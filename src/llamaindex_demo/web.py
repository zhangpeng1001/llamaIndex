"""FastAPI Web 服务：把 CLI 功能暴露为 HTTP / SSE 接口，配合前端页面便于测试。

启动方式：

    llama-demo web                # 默认 local 模式
    llama-demo web --port 8080    # 自定义端口
    llama-demo --provider openai web --rebuild

所有业务逻辑都复用 ``rag.py`` / ``router.py`` 等模块，本文件只负责协议适配：
    - 启动时构建一次索引，跨请求复用；
    - 多轮对话的 ChatEngine 按会话 ID 缓存在内存；
    - 流式输出通过 Server-Sent Events 推送。
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from llama_index.core.memory import Memory

from .agent import make_knowledge_agent
from .config import AppConfig, load_config
from .evaluation import evaluate_retriever
from .models import configure_models
from .rag import (
    build_and_persist_index,
    format_sources,
    load_documents,
    make_query_engine,
    make_summary_engine,
    parse_documents,
    retrieve,
)
from .router import deterministic_route, make_llm_router
from .structured import create_knowledge_card
from .workflow import RagWorkflow


# ---------------------------------------------------------------------------
# 全局运行时状态：进程启动时构建一次，跨请求共享。
# ---------------------------------------------------------------------------


class RuntimeState:
    """保存配置、模型、索引等共享对象。"""

    def __init__(self) -> None:
        self.config: AppConfig | None = None
        self.llm: Any = None
        self.embed_model: Any = None
        self.index: Any = None
        # session_id -> ChatEngine；多轮对话依赖它保持历史。
        self.chat_sessions: dict[str, Any] = {}
        self._lock = asyncio.Lock()


state = RuntimeState()


def init_runtime(config: AppConfig, *, rebuild: bool = False) -> None:
    """在应用启动时构建模型与索引。"""

    llm, embed_model = configure_models(config)
    index = build_and_persist_index(
        config.data_dir, config.storage_dir, embed_model, rebuild=rebuild
    )
    state.config = config
    state.llm = llm
    state.embed_model = embed_model
    state.index = index


def require_runtime() -> tuple[AppConfig, Any, Any, Any]:
    if state.config is None or state.index is None:
        raise HTTPException(status_code=503, detail="运行时尚未初始化")
    return state.config, state.llm, state.embed_model, state.index


# ---------------------------------------------------------------------------
# 请求 / 响应模型
# ---------------------------------------------------------------------------


class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3


class RetrieveRequest(BaseModel):
    question: str
    top_k: int = 3
    file_name: str | None = None


class MaterialRequest(BaseModel):
    material: str


class RebuildRequest(BaseModel):
    rebuild: bool = True


class ChatMessage(BaseModel):
    message: str


def _sources_to_dict(source_nodes: list[Any]) -> list[dict[str, Any]]:
    """把 source_nodes 序列化成前端可消费的 JSON。"""

    items: list[dict[str, Any]] = []
    for position, item in enumerate(source_nodes, start=1):
        items.append(
            {
                "position": position,
                "file_name": item.node.metadata.get("file_name", "未知文件"),
                "score": round(item.score, 4) if item.score is not None else None,
                "preview": item.node.get_content().replace("\n", " ")[:200],
            }
        )
    return items


# ---------------------------------------------------------------------------
# FastAPI 应用
# ---------------------------------------------------------------------------


def create_app(
    config: AppConfig | None = None, *, rebuild: bool = False
) -> FastAPI:
    """构造 FastAPI 实例。

    ``config`` 为 None 时延后在启动事件里读取环境变量；这样既支持
    ``llama-demo web`` 显式传参，也支持 ``uvicorn llamaindex_demo.web:app``。
    """

    app = FastAPI(title="LlamaIndex Demo API", version="0.1.0")

    @app.on_event("startup")
    async def _startup() -> None:
        cfg = config or load_config()
        init_runtime(cfg, rebuild=rebuild)

    # ---- 元信息与管理 ----------------------------------------------------

    @app.get("/api/health")
    async def health() -> dict[str, Any]:
        cfg, _, _, index = require_runtime()
        try:
            indexed_files = sorted(
                {doc.metadata.get("file_name", "") for doc in load_documents(cfg.data_dir)}
            )
        except Exception:
            indexed_files = []
        return {
            "provider": cfg.provider,
            "llm_model": cfg.llm_model,
            "embed_model": cfg.embed_model,
            "uses_openai": cfg.uses_openai,
            "data_dir": str(cfg.data_dir),
            "storage_dir": str(cfg.storage_dir),
            "indexed_files": indexed_files,
            "active_chat_sessions": len(state.chat_sessions),
        }

    @app.post("/api/rebuild")
    async def rebuild_index() -> dict[str, Any]:
        cfg, _, embed_model, _ = require_runtime()
        # 重建是耗时 IO 操作，放到线程池避免阻塞事件循环。
        new_index = await asyncio.to_thread(
            build_and_persist_index,
            cfg.data_dir,
            cfg.storage_dir,
            embed_model,
            rebuild=True,
        )
        state.index = new_index
        # 旧会话绑定的索引已失效，清空防止串用。
        state.chat_sessions.clear()
        return {"status": "ok", "message": "索引已重建，对话会话已重置"}

    # ---- 单轮问答与检索 --------------------------------------------------

    @app.post("/api/quickstart")
    async def quickstart(req: QuestionRequest) -> dict[str, Any]:
        _, llm, _, index = require_runtime()
        engine = make_query_engine(index, llm, top_k=req.top_k)
        response = await asyncio.to_thread(engine.query, req.question)
        return {
            "answer": str(response),
            "sources": _sources_to_dict(response.source_nodes),
            "raw_sources": format_sources(response.source_nodes),
        }

    @app.post("/api/retrieve")
    async def retrieve_endpoint(req: RetrieveRequest) -> dict[str, Any]:
        _, _, _, index = require_runtime()
        nodes = retrieve(
            index, req.question, top_k=req.top_k, file_name=req.file_name
        )
        return {
            "sources": _sources_to_dict(nodes),
            "raw_sources": format_sources(nodes),
        }

    @app.post("/api/summary")
    async def summary_endpoint(req: QuestionRequest) -> dict[str, Any]:
        cfg, llm, embed_model, _ = require_runtime()
        nodes = await asyncio.to_thread(
            parse_documents, load_documents(cfg.data_dir), embed_model
        )
        engine = make_summary_engine(nodes, llm)
        response = await asyncio.to_thread(engine.query, req.question)
        return {"answer": str(response)}

    @app.post("/api/router")
    async def router_endpoint(req: QuestionRequest) -> dict[str, Any]:
        cfg, llm, embed_model, index = require_runtime()
        nodes = await asyncio.to_thread(
            parse_documents, load_documents(cfg.data_dir), embed_model
        )
        vector_engine = make_query_engine(index, llm, top_k=req.top_k)
        summary_engine = make_summary_engine(nodes, llm)
        if cfg.uses_openai:
            router_engine = make_llm_router(vector_engine, summary_engine, llm)
            response = await asyncio.to_thread(router_engine.query, req.question)
            return {"route": "llm_router", "answer": str(response)}
        route_name, response = await asyncio.to_thread(
            deterministic_route, req.question, vector_engine, summary_engine
        )
        return {"route": route_name, "answer": str(response)}

    @app.post("/api/structured")
    async def structured_endpoint(req: MaterialRequest) -> dict[str, Any]:
        _, llm, _, _ = require_runtime()
        card = await asyncio.to_thread(create_knowledge_card, llm, req.material)
        return {"card": card.model_dump()}

    @app.post("/api/async")
    async def async_endpoint(req: QuestionRequest) -> dict[str, Any]:
        _, llm, _, index = require_runtime()
        engine = make_query_engine(index, llm, top_k=req.top_k)
        response = await engine.aquery(req.question)
        return {
            "answer": str(response),
            "sources": _sources_to_dict(response.source_nodes),
        }

    @app.post("/api/stream")
    async def stream_endpoint(req: QuestionRequest):
        """通过 SSE 逐字符推送生成结果。"""

        _, llm, _, index = require_runtime()
        engine = index.as_query_engine(
            llm=llm, similarity_top_k=req.top_k, streaming=True
        )

        async def event_generator():
            # streaming=True 的 QueryEngine.query 仍然同步返回，但响应自带生成器。
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

    @app.post("/api/workflow")
    async def workflow_endpoint(req: QuestionRequest) -> dict[str, Any]:
        _, llm, _, index = require_runtime()
        result = await RagWorkflow(index, llm, top_k=req.top_k).run(
            question=req.question
        )
        return result

    @app.post("/api/agent")
    async def agent_endpoint(req: QuestionRequest) -> dict[str, Any]:
        cfg, llm, _, index = require_runtime()
        if not cfg.uses_openai:
            raise HTTPException(
                status_code=400,
                detail="agent 需要支持 function calling 的真实模型，请切换 --provider openai。",
            )
        query_engine = make_query_engine(index, llm)
        agent = make_knowledge_agent(query_engine, llm)
        result = await agent.run(user_msg=req.question)
        return {"answer": str(result)}

    # ---- 检索评估 --------------------------------------------------------

    @app.get("/api/evaluate")
    async def evaluate_endpoint(top_k: int = 3) -> dict[str, Any]:
        _, _, _, index = require_runtime()
        report = await asyncio.to_thread(evaluate_retriever, index, None, top_k=top_k)
        return report

    # ---- 多轮对话（按 session_id 保存 Memory） ---------------------------

    @app.post("/api/chat/sessions")
    async def create_chat_session() -> dict[str, str]:
        _, llm, _, index = require_runtime()
        session_id = uuid.uuid4().hex[:12]
        memory = Memory.from_defaults(session_id=session_id, token_limit=3000)
        chat_engine = index.as_chat_engine(
            chat_mode="context",
            llm=llm,
            memory=memory,
            system_prompt="你是中文知识库助教。回答必须优先依据检索到的文档。",
        )
        state.chat_sessions[session_id] = chat_engine
        return {"session_id": session_id}

    @app.post("/api/chat/{session_id}/message")
    async def chat_message(session_id: str, req: ChatMessage) -> dict[str, Any]:
        _, _, _, _ = require_runtime()
        chat_engine = state.chat_sessions.get(session_id)
        if chat_engine is None:
            raise HTTPException(
                status_code=404, detail=f"会话不存在或已失效：{session_id}"
            )
        reply = await chat_engine.achat(req.message)
        return {"reply": str(reply)}

    @app.delete("/api/chat/{session_id}")
    async def reset_chat(session_id: str) -> dict[str, str]:
        state.chat_sessions.pop(session_id, None)
        return {"status": "ok", "message": f"会话 {session_id} 已重置"}

    # ---- 静态前端 --------------------------------------------------------

    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

    return app


# 方便 ``uvicorn llamaindex_demo.web:app`` 直接启动。
app = create_app()
