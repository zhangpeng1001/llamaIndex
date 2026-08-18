"""全文总结引擎模块。

对应 demo 中 ``rag.py/make_summary_engine``。

学习要点:
    - ``SummaryIndex``：把所有节点组织成可遍历的列表索引，不同于向量索引的
      “只取最相似几块”。适合“请总结这些文档”这类需要覆盖全部材料的任务。
    - ``tree_summarize``：响应合成策略。把节点分批送给 LLM 总结，再合并各批
      摘要，最终得到一棵“摘要树”，适合长文本归纳。
    - 与 ``compact`` 的区别：compact 尽量塞进一次请求，材料多时会被截断；
      tree_summarize 分批处理，覆盖更全。

业务背景:
    质检规范共 7 部分约 7 万字，用户常问“请总结时空数据规范的核心内容”，
    此时应遍历全部条款而非只取相似块。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core import SummaryIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.llms import LLM
from llama_index.core.schema import BaseNode

if TYPE_CHECKING:
    from pathlib import Path

    from llama_index.core.embeddings import BaseEmbedding

logger = logging.getLogger(__name__)


def make_summary_engine(
    nodes: list[BaseNode],
    llm: LLM,
) -> BaseQueryEngine:
    """基于 SummaryIndex + tree_summarize 构建全文总结引擎。

    参数:
        nodes: 已切块的 Node 列表（由 document_parser.parse_documents 产出）。
        llm: 语言模型。

    返回:
        BaseQueryEngine 实例，调用 ``query`` 进行总结。

    日志:
        - 节点数与模型名称；
        - 引擎构建完成。
    """

    if not nodes:
        logger.warning("节点列表为空，SummaryIndex 将无内容可总结")

    logger.info(
        "构建 SummaryEngine: node_count=%d, llm=%s",
        len(nodes),
        getattr(llm, "model", getattr(llm, "model_name", type(llm).__name__)),
    )

    # SummaryIndex 不需要向量，直接把节点放进列表。
    summary_index = SummaryIndex(nodes)

    # tree_summarize 适合归纳类问题；如需问答可改 compact。
    engine = summary_index.as_query_engine(llm=llm, response_mode="tree_summarize")

    logger.debug("SummaryEngine 构建完成: %s", type(engine).__name__)
    return engine


def make_summary_engine_from_dir(
    data_dir: "Path",
    embed_model: "BaseEmbedding",
    llm: LLM,
) -> BaseQueryEngine:
    """便捷封装：从目录加载、切块、构建总结引擎。

    参数:
        data_dir: 数据目录。
        embed_model: 嵌入模型（切块管道需要，SummaryIndex 本身不用向量）。
        llm: 语言模型。

    返回:
        BaseQueryEngine 实例。

    说明:
        SummaryIndex 不依赖向量，但 IngestionPipeline 会顺手为 Node 计算
        embedding——这会带来额外开销。若确认只做总结不做检索，可改用纯切块。
        这里为统一摄取流程仍走完整管道。
    """

    logger.info("从目录构建 SummaryEngine: data_dir=%s", data_dir)

    from .document_parser import parse_documents_from_dir

    nodes = parse_documents_from_dir(data_dir, embed_model)
    engine = make_summary_engine(nodes, llm)

    logger.info("SummaryEngine 从目录构建完成: 块数=%d", len(nodes))
    return engine
