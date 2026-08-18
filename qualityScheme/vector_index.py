"""向量索引模块。

对应 demo 中 ``rag.py/build_vector_index``。

学习要点:
    - ``VectorStoreIndex``：LlamaIndex 默认的向量索引，基于余弦相似度检索。
    - 构建时若 Node 已带 embedding，则直接使用，不再触发模型调用。
    - ``as_retriever`` / ``as_query_engine`` 都是 VectorStoreIndex 的便捷工厂方法，
      后续模块会用到。

业务背景:
    质检规范问答的核心是“按问题找条款”，向量索引能把“检测点编号”与
    “检测点数据如何整理”这类语义相近的查询匹配到同一份文档块。
"""

from __future__ import annotations

import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import BaseNode

logger = logging.getLogger(__name__)


def build_vector_index(
    nodes: list[BaseNode],
    embed_model: BaseEmbedding,
) -> VectorStoreIndex:
    """根据已嵌入的 Node 构建内存向量索引。

    参数:
        nodes: 已通过 document_parser.parse_documents 产出的 Node 列表，
            每个 Node 应已包含 embedding 字段。
        embed_model: 嵌入模型，仍需传入以便索引在“缺失向量”时能补算。

    返回:
        VectorStoreIndex 实例，可用于 as_retriever / as_query_engine。

    日志:
        - 入参 Node 数量与 embed_model 名称；
        - 已带向量的 Node 数 vs 缺失向量的 Node 数（若大量缺失，说明摄取
          管道配置有误）；
        - 构建完成后的索引规模。
    """

    if not nodes:
        logger.warning("Node 列表为空，将构建空索引（检索不会返回结果）")

    with_embedding = sum(1 for node in nodes if node.embedding is not None)
    logger.info(
        "构建向量索引: node_count=%d, 已带向量=%d, 缺失向量=%d, embed_model=%s",
        len(nodes),
        with_embedding,
        len(nodes) - with_embedding,
        getattr(embed_model, "model_name", type(embed_model).__name__),
    )

    # VectorStoreIndex 会遍历 nodes 注册到内部 docstore 与向量存储。
    # 若 Node 已有 embedding，不会再次调用 embed_model，节省 API 调用。
    index = VectorStoreIndex(nodes=nodes, embed_model=embed_model)

    # 通过 index.ref_doc_id_set 粗略观察已索引的文档数（用于调试）。
    try:
        ref_count = len(index.ref_doc_id_set) if hasattr(index, "ref_doc_id_set") else "?"
    except Exception:  # pragma: no cover - 仅调试用
        ref_count = "?"
    logger.info("向量索引构建完成: ref_doc_count=%s", ref_count)

    return index
