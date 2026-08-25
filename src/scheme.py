"""质检方案服务的稳定兼容入口。

``server.py`` 与既有调用方继续使用本模块的两个公开函数。实际业务实现位于
``scheme_simple.py``，从而让方案生成不再依赖 ``qualityScheme`` 中的复杂链路。
"""

from __future__ import annotations

from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM

from .scheme_simple import generate_scheme, list_check_items


def run_scheme_generate(
    index: VectorStoreIndex,
    llm: LLM,
    requirement: str,
    context_top_k: int = 5,
) -> dict[str, Any]:
    """生成结构化质检方案，保持原有签名以避免修改 FastAPI 路由和调用方。"""

    return generate_scheme(
        index,
        llm,
        requirement,
        context_top_k=context_top_k,
    )


def get_check_items() -> list[dict[str, Any]]:
    """返回独立 JSON 配置中的检查项，保持既有前端接口字段不变。"""

    return list_check_items()
