"""查询路由：在“精确检索问答”和“全文总结”之间选择。"""

from __future__ import annotations

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.llms import LLM
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import QueryEngineTool


def deterministic_route(
    question: str,
    vector_engine: BaseQueryEngine,
    summary_engine: BaseQueryEngine,
):
    """离线可用的确定性路由，两个分支仍然都是 LlamaIndex QueryEngine。"""

    summary_words = ("总结", "概括", "全局", "全文", "整体", "summary")
    selected = summary_engine if any(word in question.lower() for word in summary_words) else vector_engine
    route_name = "summary" if selected is summary_engine else "vector"
    return route_name, selected.query(question)


def make_llm_router(
    vector_engine: BaseQueryEngine,
    summary_engine: BaseQueryEngine,
    llm: LLM,
) -> RouterQueryEngine:
    """使用 LlamaIndex 内置 RouterQueryEngine，让真实 LLM 根据描述选择工具。"""

    tools = [
        QueryEngineTool.from_defaults(
            query_engine=vector_engine,
            name="knowledge_search",
            description="回答局部事实、定义、具体做法；通过向量相似度找相关片段。",
        ),
        QueryEngineTool.from_defaults(
            query_engine=summary_engine,
            name="document_summary",
            description="总结全部文档、归纳整体主题；会遍历较多材料。",
        ),
    ]
    return RouterQueryEngine.from_defaults(
        query_engine_tools=tools, llm=llm, select_multi=False, verbose=True
    )

