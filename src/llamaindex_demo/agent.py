"""把知识库查询能力包装为工具，交给 FunctionAgent 自主调用。

Agent 与普通 RAG 的区别在于：普通 QueryEngine 的执行路径由代码固定；Agent 会由支持
function calling 的 LLM 决定是否调用工具、传什么参数，以及是否根据结果继续行动。
"""

from __future__ import annotations

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.llms import LLM
from llama_index.core.tools import QueryEngineTool


def make_knowledge_agent(
    query_engine: BaseQueryEngine, llm: LLM
) -> FunctionAgent:
    """创建只有一项知识库工具的 Agent，保持示例目标单纯且易于观察。"""

    knowledge_tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name="search_private_knowledge_base",
        description=(
            "搜索本项目的 LlamaIndex 学习资料与虚构的星河项目手册。"
            "涉及文档事实、RAG 概念或星河项目时应使用此工具。"
        ),
    )
    return FunctionAgent(
        name="KnowledgeAssistant",
        description="能使用私有知识库工具回答问题的中文助教",
        system_prompt=(
            "你是中文知识库助教。需要文档事实时先调用知识库工具，"
            "不得编造工具结果中不存在的信息，并在答案中说明依据。"
        ),
        tools=[knowledge_tool],
        llm=llm,
        verbose=True,
    )

