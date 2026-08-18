"""元数据过滤检索模块。

对应 demo 中 ``rag.py/retrieve``。

学习要点:
    - ``MetadataFilters``：组合多个过滤条件的容器。
    - ``ExactMatchFilter``：精确匹配某条 metadata 字段，例如 file_name。
    - 过滤发生在向量检索之前，能显著缩小检索范围、提升精度与速度。
    - ``as_retriever``：把索引转换为 Retriever，``retrieve`` 只返回节点不调用 LLM，
      适合调试“检索找到了什么”。

业务背景:
    质检规范分 7 部分，用户常希望“只在《第2部分 检测点》里查找检测点编号规则”，
    此时通过 file_name 过滤即可限定范围。
"""

from __future__ import annotations

import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import (
    ExactMatchFilter,
    MetadataFilters,
)

logger = logging.getLogger(__name__)


def retrieve(
    index: VectorStoreIndex,
    question: str,
    *,
    top_k: int = 3,
    file_name: str | None = None,
) -> list[NodeWithScore]:
    """执行纯向量检索（不调用 LLM），返回 Top-K 节点。

    参数:
        index: 向量索引。
        question: 检索问题文本。
        top_k: 返回节点数，默认 3。
        file_name: 可选的文件名过滤值，精确匹配 metadata.file_name。
            例如传入 ``part2_检测点.md`` 只在该文件内检索。

    返回:
        NodeWithScore 列表，按相似度从高到低排序。

    日志:
        - 问题与过滤条件；
        - 检索结果数与每个结果的文件名、分数、预览；
        - 若过滤后结果为空，提示检查 file_name 是否正确。
    """

    filters = None
    if file_name:
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="file_name", value=file_name)]
        )
        logger.info(
            "启用元数据过滤: key=file_name, value=%s, question=%s",
            file_name,
            question[:80],
        )
    else:
        logger.info("无过滤检索: question=%s, top_k=%d", question[:80], top_k)

    retriever = index.as_retriever(
        similarity_top_k=top_k,
        filters=filters,
    )
    nodes = list(retriever.retrieve(question))

    logger.info("检索完成: 返回节点数=%d", len(nodes))
    if not nodes:
        if file_name:
            logger.warning(
                "过滤后无结果，请检查 file_name=%s 是否存在于索引中", file_name
            )
        else:
            logger.warning("检索无结果，请检查索引是否已构建")
        return []

    # 逐条记录检索结果，调试检索质量的核心日志。
    for position, node_with_score in enumerate(nodes, start=1):
        score = node_with_score.score
        preview = node_with_score.node.get_content().replace("\n", " ")[:80]
        logger.debug(
            "检索结果 #%d: file=%s, score=%.4f, 预览=%s…",
            position,
            node_with_score.node.metadata.get("file_name"),
            score if score is not None else float("nan"),
            preview,
        )

    return nodes


def retrieve_by_part(
    index: VectorStoreIndex,
    question: str,
    part_number: int,
    *,
    top_k: int = 3,
) -> list[NodeWithScore]:
    """便捷封装：按规范部分编号检索。

    参数:
        index: 向量索引。
        question: 检索问题。
        part_number: 规范部分编号（1~7）。
        top_k: 返回节点数。

    返回:
        NodeWithScore 列表。

    说明:
        规范文件名形如 ``part2_检测点.md``，此处用前缀 ``partN_`` 过滤。
        若未来文件命名规则变化，需同步调整此函数。
    """

    file_name_prefix = f"part{part_number}_"
    logger.info("按部分检索: part=%d, 前缀=%s", part_number, file_name_prefix)

    # ExactMatchFilter 是精确匹配，无法直接用前缀。这里取所有节点中文件名
    # 以 partN_ 开头的那批 file_name，再构造过滤。
    # 简化做法：直接 retrieve 后在内存过滤，适合小规模语料。
    all_nodes = retrieve(index, question, top_k=top_k * 5)
    filtered = [
        node
        for node in all_nodes
        if str(node.node.metadata.get("file_name", "")).startswith(file_name_prefix)
    ]
    result = filtered[:top_k]
    logger.info(
        "部分过滤: 候选=%d, 命中=%d, 截断=%d",
        len(all_nodes),
        len(filtered),
        len(result),
    )
    return result
