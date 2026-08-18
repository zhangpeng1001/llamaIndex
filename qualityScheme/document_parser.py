"""数据摄取模块（IngestionPipeline）。

对应 demo 中 ``rag.py/parse_documents``。

学习要点:
    - ``IngestionPipeline``：LlamaIndex 的数据摄取管道，把若干 Transformation
      串联起来依次应用到 Document。
    - ``SentenceSplitter``：基于句子边界的切块器，参数 ``chunk_size`` 控制块
      最大字符数，``chunk_overlap`` 控制块间重叠以保留上下文连贯。
    - ``BaseNode`` / ``TextNode``：Document 被切块后的最小检索单元，携带向量、
      文本、以及从父 Document 继承的 metadata。
    - Embedding：把文本块映射为向量；切块后注入 embed_model 即可让每个 Node
      自带向量，避免后续索引阶段重复计算。

业务背景:
    规范文档多为层级编号（如 5.1.1 空间基准），较小的块可以让检索更精确命中
    某一条规定，而不是返回整章内容。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode, Document

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


# 默认切块参数：质检规范条款较短，256 字符兼顾完整性与精度。
DEFAULT_CHUNK_SIZE = 256
DEFAULT_CHUNK_OVERLAP = 40


def parse_documents(
    documents: list[Document],
    embed_model: BaseEmbedding,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[BaseNode]:
    """通过 IngestionPipeline 把 Document 切块并嵌入，返回带向量的 Node 列表。

    参数:
        documents: 已加载的 Document 列表（由 document_loader.load_documents 产出）。
        embed_model: 嵌入模型，local 或 OpenAI 兼容。
        chunk_size: 每块最大字符数，默认 256。
        chunk_overlap: 相邻块重叠字符数，默认 40。

    返回:
        BaseNode 列表，每个 Node 已计算 embedding。

    日志:
        - 入参文档数与切块参数；
        - 管道执行耗时（便于评估 OpenAI 嵌入的网络开销）；
        - 切块结果统计：总块数、平均块长度、最大/最小块长度；
        - 抽样记录前 3 个块的内容预览，方便确认切块是否符合预期。
    """

    logger.info(
        "开始数据摄取: 文档数=%d, chunk_size=%d, chunk_overlap=%d, embed_model=%s",
        len(documents),
        chunk_size,
        chunk_overlap,
        getattr(embed_model, "model_name", type(embed_model).__name__),
    )

    # 1) 切块器：SentenceSplitter 兼顾中英文标点，按句号/换行切分再归并到目标长度。
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    # 2) 管道：按顺序应用 transformations，最后一步 embed_model 为每个块计算向量。
    pipeline = IngestionPipeline(transformations=[splitter, embed_model])

    # run 默认会显示 tqdm 进度条；show_progress=False 关闭以保持日志整洁。
    nodes = list(pipeline.run(documents=documents, show_progress=False))

    if not nodes:
        logger.warning("摄取管道未产出任何 Node，请检查文档内容是否为空")
        return []

    # 统计切块质量：块长度差异过大可能意味着切块参数需要调整。
    lengths = [len(node.get_content()) for node in nodes]
    avg_len = sum(lengths) / len(lengths)
    logger.info(
        "摄取完成: 总块数=%d, 平均长度=%.1f, 最小=%d, 最大=%d",
        len(nodes),
        avg_len,
        min(lengths),
        max(lengths),
    )

    # 抽样前 3 个块，确认切块边界合理（例如没有把条款编号与正文切散）。
    for sample_index in range(min(3, len(nodes))):
        node = nodes[sample_index]
        preview = node.get_content().replace("\n", " ")[:80]
        logger.debug(
            "块 #%d file=%s 长度=%d 预览=%s…",
            sample_index + 1,
            node.metadata.get("file_name"),
            lengths[sample_index],
            preview,
        )

    return nodes


def parse_documents_from_dir(
    data_dir: "Path",
    embed_model: BaseEmbedding,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[BaseNode]:
    """便捷封装：直接从目录加载并切块。

    供 summary_engine 等需要 Node 但又不想显式分步调用的场景使用。
    """

    # 延迟导入避免循环依赖：document_loader 不依赖本模块。
    from .document_loader import load_documents

    documents = load_documents(data_dir)
    return parse_documents(
        documents,
        embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
