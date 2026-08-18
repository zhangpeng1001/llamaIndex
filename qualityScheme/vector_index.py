"""向量索引模块。

对应 demo 中 ``rag.py/build_vector_index``。

学习要点:
    - ``VectorStoreIndex``：LlamaIndex 默认的向量索引，可基于余弦相似度检索。
    - 构建时若 Node 已带 embedding，则直接使用，不再触发模型调用。
    - ``StorageContext.from_defaults(vector_store=...)``：注入自定义向量存储
      （如 MilvusVectorStore），让向量写入外部数据库而非默认 SimpleVectorStore。
    - ``as_retriever`` / ``as_query_engine`` 都是 VectorStoreIndex 的便捷工厂方法，
      后续模块会用到。

业务背景:
    质检规范问答的核心是“按问题找条款”，向量索引能把“检测点编号”与
    “检测点数据如何整理”这类语义相近的查询匹配到同一份文档块。
    向量存储在 Milvus（collection=qualityScheme_llamaIndex）以提升检索质量。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import BaseNode

if TYPE_CHECKING:
    from llama_index.core.vector_stores.types import BasePydanticVectorStore

logger = logging.getLogger(__name__)


def build_vector_index(
    nodes: list[BaseNode],
    embed_model: BaseEmbedding,
    *,
    vector_store: "BasePydanticVectorStore | None" = None,
) -> VectorStoreIndex:
    """根据已嵌入的 Node 构建向量索引。

    参数:
        nodes: 已通过 document_parser.parse_documents 产出的 Node 列表，
            每个 Node 应已包含 embedding 字段。
        embed_model: 嵌入模型，仍需传入以便索引在“缺失向量”时能补算。
        vector_store: 可选的自定义向量存储。传入 MilvusVectorStore 时向量会
            写入 Milvus；为 None 时走默认 SimpleVectorStore（兼容旧行为）。

    返回:
        VectorStoreIndex 实例，可用于 as_retriever / as_query_engine。

    日志:
        - 入参 Node 数量与 embed_model 名称；
        - vector_store 类型与 collection 名称（便于确认向量去向）；
        - 已带向量的 Node 数 vs 缺失向量的 Node 数（若大量缺失，说明摄取
          管道配置有误）；
        - 构建完成后的索引规模。
    """

    if not nodes:
        logger.warning("Node 列表为空，将构建空索引（检索不会返回结果）")

    with_embedding = sum(1 for node in nodes if node.embedding is not None)

    # 记录向量存储去向：Milvus collection 或本地内存。
    store_desc = "默认 SimpleVectorStore(内存)"
    if vector_store is not None:
        store_desc = "%s(collection=%s)" % (
            type(vector_store).__name__,
            getattr(vector_store, "collection_name", "?"),
        )

    logger.info(
        "构建向量索引: node_count=%d, 已带向量=%d, 缺失向量=%d, embed_model=%s, vector_store=%s",
        len(nodes),
        with_embedding,
        len(nodes) - with_embedding,
        getattr(embed_model, "model_name", type(embed_model).__name__),
        store_desc,
    )

    # 注入自定义 vector_store（Milvus 等）；为 None 时 StorageContext 用默认存储。
    if vector_store is not None:
        from llama_index.core import StorageContext

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(
            nodes=nodes,
            embed_model=embed_model,
            storage_context=storage_context,
        )
    else:
        index = VectorStoreIndex(nodes=nodes, embed_model=embed_model)

    # 通过 index.ref_doc_id_set 粗略观察已索引的文档数（用于调试）。
    try:
        ref_count = len(index.ref_doc_id_set) if hasattr(index, "ref_doc_id_set") else "?"
    except Exception:  # pragma: no cover - 仅调试用
        ref_count = "?"
    logger.info("向量索引构建完成: ref_doc_count=%s", ref_count)

    return index
