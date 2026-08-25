"""FastAPI Web 服务入口(端口 8082)。

学习要点:
    - 启动简化:startup 只加载 config + models,不自动构建索引。
      若 Milvus 已有数据则自动加载 index(用户无需等),否则等用户点按钮触发各阶段。
    - 阶段化 API:loading/indexing/storing/querying 四个端点,用户可分步执行并验证。
    - 保留原 qualityScheme 所有功能端点(quickstart/async/stream/summary/retrieve-part/scheme),
      前端兼容,用户可继续使用 RAG问答/总结/流式/异步/方案等所有功能。
    - 异步处理:索引构建涉及 IO(嵌入会请求网络),用 asyncio.to_thread 放到线程池,
      避免阻塞 FastAPI 事件循环。
    - 静态文件 mount 在最后,避免覆盖 /api/* 路径。

业务背景:
    质检规范 RAG 系统的 Web 入口,提供:
        1. 分阶段操作(Loading/Indexing/Storing)+ 一键重建
        2. 纯检索(Querying)与 RAG 问答(quickstart/async/stream)
        3. 全文总结(summary)
        4. 质检方案生成(scheme)
        5. 按部分检索(retrieve/part)
    启动方式:python -m src.server(默认端口 8082)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 兼容直接运行(python src/server.py)与模块运行(python -m src.server)。
# 直接以脚本运行时 __package__ 为空,相对导入会失败,这里补齐包上下文。
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    __package__ = "src"

from .config import load_config
from .loading import run_loading
from .indexing import run_indexing
from .storing import load_existing_index, run_storing
from .querying import (
    format_sources_text,
    make_engine,
    run_querying,
    serialize_sources,
)
from .summary import run_summary
from .scheme import get_check_items, run_scheme_generate
from .state import state as runtime_state
from .models import configure_quality_models
from qualityScheme.milvus_store import collection_has_data

# 配置根 logger,让 src.* 的日志能输出到控制台
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 请求 / 响应模型
# ---------------------------------------------------------------------------


class QuestionRequest(BaseModel):
    """带问题的通用请求(quickstart/async/stream/summary 共用)。"""

    question: str
    top_k: int = 5


class LoadingRequest(BaseModel):
    """Loading 阶段请求。"""

    re_extract_pdf: bool = False


class StoringRequest(BaseModel):
    """Storing 阶段请求。"""

    rebuild: bool = False


class QueryingRequest(BaseModel):
    """纯检索请求(支持 file_name 和 part_number 过滤)。"""

    question: str
    top_k: int = 5
    file_name: str | None = None
    part_number: int | None = None


class RetrieveByPartRequest(BaseModel):
    """按规范部分编号检索的请求。"""

    question: str
    part_number: int
    top_k: int = 5


class SchemeRequest(BaseModel):
    """方案生成请求。"""

    requirement: str
    context_top_k: int = 5


# ---------------------------------------------------------------------------
# 启动初始化
# ---------------------------------------------------------------------------


async def init_startup() -> None:
    """startup 事件:加载 config + models,若 Milvus 有数据则加载 index。

    流程:
        1. load_config() → state.config
        2. configure_quality_models(config) → state.llm / state.embed_model
        3. collection_has_data(config) → 若 True 则 load_existing_index → state.index
        4. 不构建索引(用户按需点按钮触发各阶段)

    日志:
        - 启动开始、各步骤进度、完成。
    """

    logger.info("===== 启动初始化开始 =====")
    # 1. 加载配置
    cfg = load_config()
    runtime_state.config = cfg
    logger.info("  配置加载完成: provider=%s", cfg.provider)

    # 2. 配置模型(LLM + Embedding)
    llm, embed_model = configure_quality_models(cfg)
    runtime_state.llm = llm
    runtime_state.embed_model = embed_model
    logger.info("  模型配置完成: llm=%s, embed=%s",
                type(llm).__name__, type(embed_model).__name__)

    # 3. 若 Milvus 已有数据,自动加载 index(用户无需点按钮即可查询)
    try:
        has_data = await asyncio.to_thread(collection_has_data, cfg)
        if has_data:
            logger.info("  Milvus 已有数据,自动加载 index...")
            index = await asyncio.to_thread(load_existing_index, cfg, embed_model)
            if index is not None:
                runtime_state.index = index
                runtime_state.storing_done = True
                logger.info("  index 自动加载完成,storing_done=True")
            else:
                logger.warning("  collection_has_data=True 但 load_existing_index 返回 None")
        else:
            logger.info("  Milvus 无数据,等待用户通过流程面板触发各阶段")
    except Exception as exc:
        logger.warning("  Milvus 连接检查失败(不影响启动,后续可手动触发): %s", exc)

    logger.info("===== 启动初始化完成: ready=%s, index_ready=%s =====",
                runtime_state.ready, runtime_state.index_ready)


def require_runtime() -> tuple[Any, Any, Any, Any]:
    """获取已初始化的运行时对象(config/llm/embed_model/index)。

    返回:
        tuple (config, llm, embed_model, index)

    异常:
        HTTPException 503:运行时尚未初始化。
    """

    if not runtime_state.ready:
        raise HTTPException(status_code=503, detail="运行时尚未初始化,请稍候重试")
    return runtime_state.config, runtime_state.llm, runtime_state.embed_model, runtime_state.index


def require_index() -> Any:
    """获取已就绪的 index,未就绪时抛 503。

    用于查询类端点(quickstart/querying/scheme 等),要求 Storing 阶段已完成。
    """

    if not runtime_state.index_ready:
        raise HTTPException(
            status_code=503,
            detail="索引未就绪,请先在流程面板完成 Loading→Indexing→Storing 三阶段,或点击一键重建索引",
        )
    return runtime_state.index


# ---------------------------------------------------------------------------
# FastAPI 应用
# ---------------------------------------------------------------------------


def create_app() -> FastAPI:
    """构造 FastAPI 实例。"""

    app = FastAPI(
        title="质检规范知识库 API(src 版)",
        version="1.0.0",
        description="基于 LlamaIndex 的实景三维质检时空数据规范 RAG 服务(分阶段版,端口 8082)",
    )

    @app.on_event("startup")
    async def _startup() -> None:
        await init_startup()

    # ==================================================================
    # 健康检查 + 阶段状态
    # ==================================================================

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        """健康检查:返回模型、数据目录、Milvus 连接、各阶段完成标志。"""

        cfg, _, embed_model, _ = require_runtime()
        # 查询 Milvus collection 是否含数据
        try:
            has_data = await asyncio.to_thread(collection_has_data, cfg)
        except Exception as exc:
            logger.warning("健康检查 Milvus 连接失败: %s", exc)
            has_data = False

        return {
            "service": "src",
            "provider": cfg.provider,
            "llm_model": cfg.llm_model,
            "embed_model": cfg.embed_model,
            "uses_openai": cfg.uses_openai,
            "data_dir": str(cfg.data_dir),
            "storage_dir": str(cfg.storage_dir),
            "milvus_uri": cfg.milvus_uri,
            "milvus_db": cfg.milvus_db,
            "milvus_collection": cfg.milvus_collection,
            "collection_has_data": has_data,
            **runtime_state.get_state_dict(),
        }

    @app.get("/api/state")
    async def get_state() -> dict[str, Any]:
        """返回当前阶段状态(loading_done/indexing_done/storing_done)。"""

        return runtime_state.get_state_dict()

    # ==================================================================
    # 阶段操作:Loading / Indexing / Storing
    # ==================================================================

    @app.post("/api/loading")
    async def loading(req: LoadingRequest) -> dict[str, Any]:
        """执行 Loading 阶段:PDF→MD→Document(富 metadata)。"""

        cfg, _, _, _ = require_runtime()
        logger.info("/api/loading: re_extract_pdf=%s", req.re_extract_pdf)
        # Loading 涉及 PDF 提取(若 re_extract=True),放到线程池
        documents = await asyncio.to_thread(run_loading, cfg, re_extract_pdf=req.re_extract_pdf)
        runtime_state.documents = documents
        runtime_state.loading_done = True
        # Loading 重做后,后续阶段产物失效
        runtime_state.indexing_done = False
        runtime_state.storing_done = False
        runtime_state.nodes = None
        runtime_state.index = None
        logger.info("Loading 完成: documents=%d", len(documents))

        # 统计返回
        ktype_cnt: dict[str, int] = {}
        part_cnt: dict[str, int] = {}
        for d in documents:
            kt = d.metadata.get("knowledge_type", "?")
            ktype_cnt[kt] = ktype_cnt.get(kt, 0) + 1
            pn = f"part{d.metadata.get('part_number', '?')}"
            part_cnt[pn] = part_cnt.get(pn, 0) + 1

        return {
            "status": "ok",
            "documents_count": len(documents),
            "knowledge_type_distribution": ktype_cnt,
            "part_distribution": part_cnt,
            "loading_done": True,
        }

    @app.post("/api/indexing")
    async def indexing() -> dict[str, Any]:
        """执行 Indexing 阶段:Document→规范 Nodes(切块+嵌入+落盘)。"""

        _, _, embed_model, _ = require_runtime()
        if not runtime_state.loading_done or not runtime_state.documents:
            raise HTTPException(
                status_code=400,
                detail="Loading 阶段未完成,请先执行 Loading",
            )
        logger.info("/api/indexing: documents=%d", len(runtime_state.documents))
        spec_nodes = await asyncio.to_thread(
            run_indexing, runtime_state.documents, embed_model
        )
        runtime_state.nodes = spec_nodes
        runtime_state.indexing_done = True
        # Indexing 重做后,Storing 产物失效
        runtime_state.storing_done = False
        runtime_state.index = None
        logger.info(
            "Indexing 完成: spec_nodes=%d",
            len(spec_nodes),
        )

        # 统计返回
        lens = [len(n.get_content()) for n in spec_nodes] if spec_nodes else []
        avg_len = sum(lens) / len(lens) if lens else 0
        return {
            "status": "ok",
            "spec_nodes_count": len(spec_nodes),
            "total_nodes_count": len(spec_nodes),
            "avg_chunk_length": round(avg_len, 1),
            "min_chunk_length": min(lens) if lens else 0,
            "max_chunk_length": max(lens) if lens else 0,
            "indexing_done": True,
        }

    @app.post("/api/storing")
    async def storing(req: StoringRequest) -> dict[str, Any]:
        """执行 Storing 阶段:Milvus 写入 + manifest。"""

        cfg, _, embed_model, _ = require_runtime()
        if not runtime_state.indexing_done or not runtime_state.nodes:
            raise HTTPException(
                status_code=400,
                detail="Indexing 阶段未完成,请先执行 Indexing",
            )
        logger.info(
            "/api/storing: rebuild=%s, spec_nodes=%d",
            req.rebuild,
            len(runtime_state.nodes),
        )
        # Storing 前,清空 summary 缓存(保证新旧数据不混杂)
        runtime_state.invalidate_summary_cache()
        index = await asyncio.to_thread(
            run_storing,
            cfg,
            embed_model,
            runtime_state.nodes,
            rebuild=req.rebuild,
        )
        runtime_state.index = index
        runtime_state.storing_done = True
        logger.info("Storing 完成: storing_done=True")

        # 查询 collection 行数
        try:
            has_data = await asyncio.to_thread(collection_has_data, cfg)
        except Exception:
            has_data = True  # 写入成功,默认 True

        return {
            "status": "ok",
            "storing_done": True,
            "collection_has_data": has_data,
            "total_nodes_written": len(runtime_state.nodes),
        }

    # ==================================================================
    # Querying:纯检索 + RAG 问答
    # ==================================================================

    @app.post("/api/querying")
    async def querying(req: QueryingRequest) -> dict[str, Any]:
        """纯检索(不调 LLM):Hybrid Top-K,支持 file_name/part_number 过滤。"""

        index = require_index()
        logger.info(
            "/api/querying: question=%s, top_k=%d, file_name=%s, part_number=%s",
            req.question[:80],
            req.top_k,
            req.file_name,
            req.part_number,
        )
        nodes = await asyncio.to_thread(
            run_querying,
            index,
            req.question,
            top_k=req.top_k,
            file_name=req.file_name,
            part_number=req.part_number,
        )
        return {
            "sources": serialize_sources(nodes),
            "raw_sources": format_sources_text(nodes),
        }

    @app.post("/api/retrieve/part")
    async def retrieve_by_part(req: RetrieveByPartRequest) -> dict[str, Any]:
        """按规范部分编号(1~7)检索。"""

        from .querying import retrieve_by_part as _rbp

        index = require_index()
        logger.info(
            "/api/retrieve/part: part=%d, question=%s",
            req.part_number,
            req.question[:80],
        )
        nodes = await asyncio.to_thread(
            _rbp,
            index,
            req.question,
            req.part_number,
            top_k=req.top_k,
        )
        return {
            "part_number": req.part_number,
            "sources": serialize_sources(nodes),
            "raw_sources": format_sources_text(nodes),
        }

    @app.post("/api/quickstart")
    async def quickstart(req: QuestionRequest) -> dict[str, Any]:
        """完整 RAG 问答:检索→合成→输出来源。"""

        _, llm, _, index = require_runtime()
        require_index()
        logger.info("/api/quickstart: question=%s, top_k=%d", req.question[:80], req.top_k)
        engine = make_engine(index, llm, top_k=req.top_k)
        response = await asyncio.to_thread(engine.query, req.question)
        return {
            "answer": str(response),
            "sources": serialize_sources(getattr(response, "source_nodes", []) or []),
        }

    @app.post("/api/async")
    async def async_query(req: QuestionRequest) -> dict[str, Any]:
        """异步 QueryEngine 查询(Web 服务推荐使用避免阻塞)。"""

        _, llm, _, index = require_runtime()
        require_index()
        logger.info("/api/async: question=%s, top_k=%d", req.question[:80], req.top_k)
        engine = make_engine(index, llm, top_k=req.top_k)
        response = await engine.aquery(req.question)
        return {
            "answer": str(response),
            "sources": serialize_sources(getattr(response, "source_nodes", []) or []),
        }

    @app.post("/api/stream")
    async def stream(req: QuestionRequest):
        """通过 SSE 逐 token 推送生成结果。"""

        _, llm, _, index = require_runtime()
        require_index()
        logger.info("/api/stream: question=%s", req.question[:80])
        engine = make_engine(index, llm, top_k=req.top_k, streaming=True)

        async def event_generator():
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

    # ==================================================================
    # 全文总结
    # ==================================================================

    @app.post("/api/summary")
    async def summary(req: QuestionRequest) -> dict[str, Any]:
        """全文总结:SummaryIndex + tree_summarize,带两级缓存。"""

        require_runtime()
        logger.info("/api/summary: question=%s", req.question[:80])
        result = await asyncio.to_thread(run_summary, runtime_state, req.question)
        return result

    # ==================================================================
    # 质检方案生成
    # ==================================================================

    @app.get("/api/scheme/check-items")
    async def scheme_check_items() -> dict[str, Any]:
        """返回预定义检查项清单(27 项)。"""

        logger.info("/api/scheme/check-items: 返回检查项清单")
        return {"data": get_check_items()}

    @app.post("/api/scheme/generate")
    async def scheme_generate(req: SchemeRequest) -> dict[str, Any]:
        """根据自然语言需求生成质检方案。"""

        _, llm, _, index = require_runtime()
        require_index()
        if not req.requirement.strip():
            raise HTTPException(status_code=400, detail="需求描述不能为空")
        logger.info(
            "/api/scheme/generate: requirement=%s, context_top_k=%d",
            req.requirement[:100],
            req.context_top_k,
        )
        result = await asyncio.to_thread(
            run_scheme_generate,
            index,
            llm,
            req.requirement,
            req.context_top_k,
        )
        return result

    # ==================================================================
    # 一键重建(全流程)
    # ==================================================================

    @app.post("/api/rebuild")
    async def rebuild() -> dict[str, Any]:
        """一键全流程:Loading(re_extract=True)→Indexing→Storing(rebuild=True)。"""

        cfg, _, embed_model, _ = require_runtime()
        logger.info("/api/rebuild: 一键重建开始")
        # 重置状态
        runtime_state.reset_pipeline()

        # 阶段1: Loading(从 PDF 重新提取)
        logger.info("  [1/3] Loading 开始(re_extract_pdf=True)")
        documents = await asyncio.to_thread(run_loading, cfg, re_extract_pdf=True)
        runtime_state.documents = documents
        runtime_state.loading_done = True
        logger.info("  [1/3] Loading 完成: documents=%d", len(documents))

        # 阶段2: Indexing
        logger.info("  [2/3] Indexing 开始")
        spec_nodes = await asyncio.to_thread(
            run_indexing, documents, embed_model
        )
        runtime_state.nodes = spec_nodes
        runtime_state.indexing_done = True
        logger.info(
            "  [2/3] Indexing 完成: spec=%d",
            len(spec_nodes),
        )

        # 阶段3: Storing(rebuild=True,overwrite collection)
        logger.info("  [3/3] Storing 开始(rebuild=True)")
        index = await asyncio.to_thread(
            run_storing,
            cfg,
            embed_model,
            spec_nodes,
            rebuild=True,
        )
        runtime_state.index = index
        runtime_state.storing_done = True
        logger.info("  [3/3] Storing 完成")

        logger.info("/api/rebuild: 一键重建完成")
        return {
            "status": "ok",
            "message": "索引重建完成(Loading→Indexing→Storing 全流程)",
            "documents_count": len(documents),
            "spec_nodes_count": len(spec_nodes),
            "storing_done": True,
        }

    # ==================================================================
    # 静态前端(mount 在最后,避免覆盖 /api/* 路径)
    # ==================================================================

    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    else:
        logger.warning("静态前端目录不存在: %s(请先创建 src/static/)", static_dir)

    return app


# 方便 uvicorn src.server:app 直接启动
app = create_app()


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------


def main() -> None:
    """命令行启动入口。

    用法::

        python -m src.server                 # 默认端口 8082
        python -m src.server --port 8082      # 显式指定端口
        python -m src.server --provider openai  # 覆盖 .env 的 provider
    """

    import uvicorn

    parser = argparse.ArgumentParser(description="质检规范知识库 Web 服务(src 版,端口 8082)")
    parser.add_argument(
        "--provider",
        choices=["local", "openai"],
        help="覆盖 .env 中的模型提供方",
    )
    parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    parser.add_argument("--port", type=int, default=8082, help="监听端口(默认 8082)")
    parser.add_argument(
        "--log-level",
        default="debug",
        choices=["debug", "info", "warning", "error"],
        help="uvicorn 日志级别",
    )
    args = parser.parse_args()

    # 若指定 provider,提前覆盖环境变量(在 init_startup 读取 .env 之前)
    if args.provider:
        import os
        os.environ["LLAMAINDEX_MODEL_PROVIDER"] = args.provider

    print(
        f"启动质检规范 Web 服务(src 版): provider={args.provider or '(from .env)'}, "
        f"http://{args.host}:{args.port}"
    )
    print("提示: 首次启动后,请在流程面板点击各阶段按钮触发索引构建,或点击一键重建索引")
    print("      local 模式需先启动 Ollama;openai 模式请确保已配置 API Key")
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level)


if __name__ == "__main__":
    main()
