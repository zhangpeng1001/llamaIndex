"""RAG 问答引擎模块。

对应 demo 中 ``rag.py/make_query_engine``。

学习要点:
    - ``QueryEngine`` = Retriever + Node Postprocessors + Response Synthesizer。
    - ``similarity_top_k``：检索器返回的 Top-K 节点数。
    - ``response_mode``：响应合成策略：
        * ``compact``：把检索块尽量塞进一次 LLM 请求，适合普通短问答；
        * ``tree_summarize``：分块汇总再合并，适合长文总结；
        * ``refine``：逐块迭代精炼答案，适合需要综合多条款的场景。
    - ``streaming=True``：开启流式输出，response.response_gen 可逐 token 消费。

业务背景:
    质检规范问答以“按条款回答”为主，compact 模式足够；需要跨多部分综合时
    可切换到 refine。
"""

from __future__ import annotations

import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.llms import LLM

logger = logging.getLogger(__name__)


def make_query_engine(
    index: VectorStoreIndex,
    llm: LLM,
    *,
    top_k: int = 3,
    response_mode: str = "compact",
    streaming: bool = False,
) -> BaseQueryEngine:
    """将 Retriever 与响应合成器组合成 QueryEngine。

    参数:
        index: 已构建的向量索引。
        llm: 语言模型。
        top_k: 检索返回的节点数，默认 3。质检条款通常 1~2 条即可命中，
            过大反而引入噪声。
        response_mode: 响应合成模式，默认 ``compact``。
        streaming: 是否启用流式输出，默认 False。Web 端 SSE 场景设为 True。

    返回:
        BaseQueryEngine 实例，调用 ``query`` 或 ``aquery`` 获取响应。

    日志:
        - 引擎配置（top_k、response_mode、streaming）；
        - 模型名称，便于排查“回答质量异常”时确认实际使用的模型。
    """

    logger.info(
        "构建 QueryEngine: top_k=%d, response_mode=%s, streaming=%s, llm=%s",
        top_k,
        response_mode,
        streaming,
        getattr(llm, "model", getattr(llm, "model_name", type(llm).__name__)),
    )

    engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=top_k,
        response_mode=response_mode,
        streaming=streaming,
    )

    logger.debug("QueryEngine 构建完成: %s", type(engine).__name__)
    return engine


def query_with_engine(
    engine: BaseQueryEngine,
    question: str,
    *,
    async_mode: bool = False,
):
    """便捷调用：用已构建的引擎回答问题，并记录响应元信息。

    参数:
        engine: make_query_engine 产出的引擎。
        question: 用户问题。
        async_mode: 是否使用异步接口 ``aquery``（Web 服务推荐）。

    返回:
        Response 对象（同步）或其 await 结果（异步）。

    日志:
        - 问题文本（截断 100 字符）；
        - 响应字符数与来源节点数；
        - 来源文件清单，便于核对答案出处。
    """

    logger.info("发起查询: question=%s, async_mode=%s", question[:100], async_mode)

    if async_mode:
        # 调用方需要 await 本函数的返回值。
        async def _run():
            response = await engine.aquery(question)
            _log_response(question, response)
            return response

        return _run()

    response = engine.query(question)
    _log_response(question, response)
    return response


def _log_response(question: str, response) -> None:
    """记录响应的关键信息，便于调试与评估。"""

    answer_text = str(response)
    source_nodes = getattr(response, "source_nodes", []) or []
    source_files = [
        node.node.metadata.get("file_name", "?") for node in source_nodes
    ]

    logger.info(
        "查询完成: 答案长度=%d, 来源节点数=%d, 来源文件=%s",
        len(answer_text),
        len(source_nodes),
        source_files,
    )
    logger.debug("答案预览: %s", answer_text[:200])
