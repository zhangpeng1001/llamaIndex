"""质检方案编排 API 路由注册。

为了"不影响原有 web.py 代码"，本模块提供一个 ``register_scheme_routes`` 函数，
在 FastAPI app 上挂载方案生成相关接口。web.py 只需调用一次该函数即可。

接口:
    - GET  /api/scheme/check-items : 返回预定义检查项清单
    - POST /api/scheme/generate     : 根据自然语言需求生成质检方案
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .check_items import list_check_items
from .scheme_generator import generate_scheme, scheme_to_dict

logger = logging.getLogger(__name__)


class SchemeRequest(BaseModel):
    """方案生成请求。"""

    requirement: str = Field(
        default="",
        description="自然语言描述的质检需求，例如：检测点坐标精度不超过0.5米，编号唯一",
    )
    context_top_k: int = Field(default=5, description="检索规范上下文的条款数")


def register_scheme_routes(app: FastAPI, get_runtime) -> None:
    """在 FastAPI app 上注册质检方案相关路由。

    参数:
        app: FastAPI 实例。
        get_runtime: 一个可调用对象，返回 (config, llm, embed_model, index)。
                     这里传入 web 模块的 ``require_runtime``，避免循环依赖。
    """

    @app.get("/api/scheme/check-items")
    async def get_check_items() -> dict[str, Any]:
        """返回预定义检查项清单，供前端展示与选择。"""

        logger.info("/api/scheme/check-items: 返回检查项清单")
        return {"data": list_check_items()}

    @app.post("/api/scheme/generate")
    async def generate_scheme_endpoint(req: SchemeRequest) -> dict[str, Any]:
        """根据自然语言需求生成质检方案。

        流程:
            1. 用向量索引检索相关规范条款作为上下文。
            2. 调用 LLM 生成结构化方案（Pydantic 校验）。
            3. 过滤非法 checkCode，补齐缺失参数。
        """

        _, llm, _, index = get_runtime()
        if not req.requirement.strip():
            raise HTTPException(status_code=400, detail="需求描述不能为空")

        logger.info(
            "/api/scheme/generate: requirement=%s, context_top_k=%d",
            req.requirement[:100],
            req.context_top_k,
        )

        # 方案生成涉及检索+LLM调用，放到线程池避免阻塞事件循环。
        scheme = await asyncio.to_thread(
            generate_scheme,
            index,
            llm,
            req.requirement,
            context_top_k=req.context_top_k,
        )

        result = scheme_to_dict(scheme)
        logger.info(
            "方案生成接口返回: schemeName=%s, 检查项数=%d",
            result["schemeName"],
            len(result["checkItem"]),
        )
        return result

    logger.info("已注册质检方案路由: /api/scheme/check-items, /api/scheme/generate")
