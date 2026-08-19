"""质检规范业务的 FastAPI Web 服务。

对应 demo 中 ``web.py``，但完全独立：
- 端口默认 8001（避免与 demo 的 8000 冲突）；
- API 路径前缀仍为 ``/api``，但业务对象是质检规范；
- 复用 qualityScheme 包内的 8 个功能模块。

启动方式:

    python -m qualityScheme.web                         # 默认 local 模式，端口 8001
    python -m qualityScheme.web --port 8080            # 自定义端口
    python -m qualityScheme.web --provider openai --rebuild

所有业务逻辑复用 qualityScheme 内的模块，本文件只负责 HTTP 协议适配：
    - 启动时构建一次索引，跨请求复用；
    - 流式输出通过 Server-Sent Events 推送。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 兼容直接运行（python web.py / PyCharm 调试）与模块运行（python -m qualityScheme.web）。
# 直接以脚本运行时 __package__ 为空，相对导入（from .config import ...）会抛
# ImportError: attempted relative import with no known parent package。
# 这里在相对导入之前补齐包上下文，并把 qualityScheme 的父目录加入 sys.path，
# 使其作为 "qualityScheme" 包被正确识别。
if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "qualityScheme"

from .config import QualitySchemeConfig, load_quality_config
from .document_loader import load_documents
from .document_parser import parse_documents
from .index_persistence import build_and_persist_index
from .metadata_filter import retrieve
from .models import configure_quality_models
from .query_engine import make_query_engine
from .source_tracker import format_sources, sources_to_dict
from .summary_engine import make_summary_engine
from .scheme_api import register_scheme_routes
from .milvus_store import (
    collection_has_data,
    create_milvus_vector_store,
    ensure_milvus_database,
    get_embedding_dimension,
)

# 配置根 logger，让 qualityScheme.* 的日志能输出到控制台。
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 全局运行时状态：进程启动时构建一次，跨请求共享。
# ---------------------------------------------------------------------------


class RuntimeState:
    """保存配置、模型、索引等共享对象。"""

    def __init__(self) -> None:
        self.config: QualitySchemeConfig | None = None
        self.llm: Any = None
        self.embed_model: Any = None
        self.index: Any = None
        self.vector_store: Any = None
        self._lock = asyncio.Lock()

    @property
    def ready(self) -> bool:
        return self.config is not None and self.index is not None


state = RuntimeState()


def init_runtime(config: QualitySchemeConfig, *, rebuild: bool = False) -> None:
    """在应用启动时构建模型、Milvus 向量存储与索引。

    参数:
        config: 质检业务配置。
        rebuild: 是否强制重建索引（重建 Milvus collection）。

    流程:
        1. 配置 LLM 与嵌入模型。
        2. 探测嵌入维度，确保 Milvus 数据库存在。
        3. 创建 MilvusVectorStore（rebuild 时 overwrite=True）。
        4. build_and_persist_index 据此加载已有 collection 或全量摄取写入。
    """

    logger.info("初始化运行时: provider=%s, rebuild=%s", config.provider, rebuild)
    llm, embed_model = configure_quality_models(config)

    # 1. 探测嵌入维度（决定 Milvus collection 的向量维度）。
    dim = get_embedding_dimension(embed_model)

    # 2. 确保 Milvus 数据库存在（kernel_data_platform）。
    ensure_milvus_database(config.milvus_uri, config.milvus_db)

    # 3. 创建 Milvus 向量存储；rebuild 时删除并重建 collection。
    vector_store = create_milvus_vector_store(
        config, dim=dim, overwrite=rebuild
    )

    # 4. 加载或构建索引（向量写入/读取 Milvus）。
    index = build_and_persist_index(
        config.data_dir,
        config.storage_dir,
        embed_model,
        rebuild=rebuild,
        vector_store=vector_store,
    )
    state.config = config
    state.llm = llm
    state.embed_model = embed_model
    state.index = index
    state.vector_store = vector_store
    logger.info("运行时初始化完成")


def require_runtime() -> tuple[QualitySchemeConfig, Any, Any, Any]:
    """获取已初始化的运行时对象，未就绪时抛 503。"""

    if not state.ready:
        raise HTTPException(status_code=503, detail="运行时尚未初始化")
    return state.config, state.llm, state.embed_model, state.index


# ---------------------------------------------------------------------------
# 请求 / 响应模型
# ---------------------------------------------------------------------------


class QuestionRequest(BaseModel):
    """带问题的通用请求。"""

    question: str
    top_k: int = 3


class RetrieveRequest(BaseModel):
    """检索请求，支持按 file_name 过滤。"""

    question: str
    top_k: int = 3
    file_name: str | None = None


class RetrieveByPartRequest(BaseModel):
    """按规范部分编号检索的请求。"""

    question: str
    part_number: int
    top_k: int = 3


# ---------------------------------------------------------------------------
# FastAPI 应用
# ---------------------------------------------------------------------------


def create_app(
    config: QualitySchemeConfig | None = None,
    *,
    rebuild: bool = False,
) -> FastAPI:
    """构造 FastAPI 实例。

    参数:
        config: 可选的预加载配置；为 None 时延后到 startup 事件读取环境变量。
        rebuild: 是否在启动时重建索引。
    """

    app = FastAPI(
        title="质检规范知识库 API",
        version="0.1.0",
        description="基于 LlamaIndex 的实景三维质检时空数据规范 RAG 服务",
    )

    @app.on_event("startup")
    async def _startup() -> None:
        cfg = config or load_quality_config()
        # 索引构建涉及 IO（OpenAI 嵌入会请求网络），放到线程池避免阻塞事件循环。
        # 注意 rebuild 是关键字参数，asyncio.to_thread 会透传 **kwargs。
        await asyncio.to_thread(init_runtime, cfg, rebuild=rebuild)

    # ---- 元信息与管理 ----------------------------------------------------

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        """健康检查：返回模型、数据目录、Milvus 连接与已索引文件清单。"""

        cfg, _, embed_model, _ = require_runtime()
        try:
            docs = await asyncio.to_thread(load_documents, cfg.data_dir)
            indexed_files = sorted({doc.metadata.get("file_name", "") for doc in docs})
        except Exception as exc:
            logger.warning("健康检查读取文档失败: %s", exc)
            indexed_files = []

        # 查询 Milvus collection 是否含数据（用独立连接，不影响主 store）。
        try:
            has_data = await asyncio.to_thread(collection_has_data, cfg)
        except Exception as exc:
            logger.warning("健康检查 Milvus 连接失败: %s", exc)
            has_data = False

        vector_store_type = type(state.vector_store).__name__ if state.vector_store else None

        return {
            "service": "qualityScheme",
            "provider": cfg.provider,
            "llm_model": cfg.llm_model,
            "embed_model": cfg.embed_model,
            "uses_openai": cfg.uses_openai,
            "data_dir": str(cfg.data_dir),
            "storage_dir": str(cfg.storage_dir),
            "indexed_files": indexed_files,
            "milvus_uri": cfg.milvus_uri,
            "milvus_db": cfg.milvus_db,
            "milvus_collection": cfg.milvus_collection,
            "vector_store_type": vector_store_type,
            "collection_has_data": has_data,
        }

    @app.post("/api/rebuild")
    async def rebuild_index() -> dict[str, Any]:
        """删除旧 Milvus collection 并重新切块、嵌入写入。"""

        logger.info("收到重建索引请求（Milvus overwrite=True）")
        # 重新走完整 init_runtime 流程：重建 store（overwrite=True）并重新摄取。
        cfg = state.config or load_quality_config()
        await asyncio.to_thread(init_runtime, cfg, rebuild=True)
        logger.info("索引重建完成")
        return {"status": "ok", "message": "质检规范 Milvus 索引已重建"}

    # ---- RAG 问答 -------------------------------------------------------

    @app.post("/api/quickstart")
    async def quickstart(req: QuestionRequest) -> dict[str, Any]:
        """完整 RAG 问答：检索 -> 合成 -> 输出来源。"""

        _, llm, _, index = require_runtime()
        logger.info("/api/quickstart: question=%s, top_k=%d", req.question[:80], req.top_k)
        engine = make_query_engine(index, llm, top_k=req.top_k)
        response = await asyncio.to_thread(engine.query, req.question)
        return {
            "answer": str(response),
            "sources": sources_to_dict(response.source_nodes),
            "raw_sources": format_sources(response.source_nodes),
        }

    @app.post("/api/async")
    async def async_query(req: QuestionRequest) -> dict[str, Any]:
        """异步 QueryEngine 查询，Web 服务中应优先使用避免阻塞。"""

        _, llm, _, index = require_runtime()
        logger.info("/api/async: question=%s, top_k=%d", req.question[:80], req.top_k)
        engine = make_query_engine(index, llm, top_k=req.top_k)
        response = await engine.aquery(req.question)
        return {
            "answer": str(response),
            "sources": sources_to_dict(response.source_nodes),
        }

    @app.post("/api/stream")
    async def stream(req: QuestionRequest):
        """通过 SSE 逐 token 推送生成结果。"""

        _, llm, _, index = require_runtime()
        logger.info("/api/stream: question=%s", req.question[:80])
        engine = make_query_engine(
            index, llm, top_k=req.top_k, streaming=True
        )

        async def event_generator():
            # streaming=True 的 QueryEngine.query 仍同步返回，但响应自带生成器。
            response = await asyncio.to_thread(engine.query, req.question)
            for chunk in response.response_gen:
                payload = json.dumps({"token": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    # ---- 检索（不调用 LLM） ---------------------------------------------

    @app.post("/api/retrieve")
    async def retrieve_endpoint(req: RetrieveRequest) -> dict[str, Any]:
        """纯向量检索，展示 Top-K 节点与分数。"""

        _, _, _, index = require_runtime()
        logger.info(
            "/api/retrieve: question=%s, top_k=%d, file_name=%s",
            req.question[:80],
            req.top_k,
            req.file_name,
        )
        nodes = await asyncio.to_thread(
            retrieve,
            index,
            req.question,
            top_k=req.top_k,
            file_name=req.file_name,
        )
        return {
            "sources": sources_to_dict(nodes),
            "raw_sources": format_sources(nodes),
        }

    @app.post("/api/retrieve/part")
    async def retrieve_by_part(req: RetrieveByPartRequest) -> dict[str, Any]:
        """按规范部分编号（1~7）检索。"""

        from .metadata_filter import retrieve_by_part

        _, _, _, index = require_runtime()
        logger.info(
            "/api/retrieve/part: part=%d, question=%s",
            req.part_number,
            req.question[:80],
        )
        nodes = await asyncio.to_thread(
            retrieve_by_part,
            index,
            req.question,
            req.part_number,
            top_k=req.top_k,
        )
        return {
            "part_number": req.part_number,
            "sources": sources_to_dict(nodes),
            "raw_sources": format_sources(nodes),
        }

    # ---- 全文总结 --------------------------------------------------------

    @app.post("/api/summary")
    async def summary(req: QuestionRequest) -> dict[str, Any]:
        """使用 SummaryIndex + tree_summarize 遍历全部材料做归纳。"""

        cfg, llm, embed_model, _ = require_runtime()
        logger.info("/api/summary: question=%s", req.question[:80])
        # SummaryIndex 需要节点，这里每次重新切块（生产环境可缓存）。
        nodes = await asyncio.to_thread(
            parse_documents, load_documents(cfg.data_dir), embed_model
        )
        engine = make_summary_engine(nodes, llm)
        response = await asyncio.to_thread(engine.query, req.question)
        return {"answer": str(response)}

    # ---- 质检方案编排（自然语言生成方案） --------------------------------

    # 注册方案生成相关路由；get_runtime 传入 require_runtime 避免循环依赖。
    register_scheme_routes(app, require_runtime)

    # ---- 静态前端 --------------------------------------------------------

    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


# 方便 ``uvicorn qualityScheme.web:app`` 直接启动。
app = create_app()


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------


def main() -> None:
    """命令行启动入口。

    用法::

        python -m qualityScheme.web
        python -m qualityScheme.web --port 8080
        python -m qualityScheme.web --provider openai --rebuild
    """

    import uvicorn

    parser = argparse.ArgumentParser(description="质检规范知识库 Web 服务")
    parser.add_argument(
        "--provider",
        choices=["local", "openai"],
        help="覆盖 .env 中的模型提供方",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="删除旧索引后重新切块嵌入",
    )
    parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    parser.add_argument("--port", type=int, default=8001, help="监听端口")
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="uvicorn 日志级别",
    )
    args = parser.parse_args()

    config = load_quality_config(args.provider)
    application = create_app(config, rebuild=args.rebuild)
    print(
        f"启动质检规范 Web 服务: provider={config.provider}, "
        f"http://{args.host}:{args.port}"
    )
    print("提示: local 模式首次启动会构建索引；OpenAI 模式请确保已配置 API Key。")
    uvicorn.run(application, host=args.host, port=args.port, log_level=args.log_level)


if __name__ == "__main__":
    main()
