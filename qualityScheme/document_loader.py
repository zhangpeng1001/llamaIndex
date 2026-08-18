"""文档加载模块。

对应 demo 中 ``rag.py/load_documents``。

学习要点:
    - ``SimpleDirectoryReader``：LlamaIndex 提供的目录读取器，自动遍历文件并
      按扩展名分发到对应的 Reader（Markdown、PDF、TXT 等）。
    - ``Document``：LlamaIndex 的文档对象，包含 ``text`` 与 ``metadata``。
    - metadata：SimpleDirectoryReader 会自动注入 ``file_name``、``file_path``
      等字段，后面既能显示来源，也能用于元数据过滤检索。

业务背景:
    本模块读取 ``qualityScheme/data`` 目录下从 PDF 规范提取的 Markdown 文件，
    内容为《实景三维质检大数据支撑库 时空数据规范》第 1~7 部分。
"""

from __future__ import annotations

import logging
from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document

logger = logging.getLogger(__name__)


def load_documents(data_dir: Path) -> list[Document]:
    """读取目录中的 Markdown 文档，生成 Document 对象列表。

    参数:
        data_dir: 数据目录路径，通常指向 ``qualityScheme/data``。

    返回:
        Document 列表，每个文件对应一个 Document。

    异常:
        RuntimeError: 目录不存在或未读取到任何文档时抛出，避免后续流程
            在空数据上继续运行而难以定位问题。

    日志:
        - 入参目录；
        - 找到的文件数量与文件名清单（调试用）；
        - 每个 Document 的元数据关键字段（file_name、文件大小）。
    """

    logger.info("开始加载文档目录: data_dir=%s", data_dir)

    if not data_dir.exists():
        logger.error("数据目录不存在: %s", data_dir)
        raise RuntimeError(f"数据目录不存在：{data_dir}")

    # required_exts 限定扩展名，避免误读取 PDF 原文件（PDF 已被提取为 Markdown）。
    # recursive=True 以便未来按子目录组织数据时仍可加载。
    reader = SimpleDirectoryReader(
        input_dir=str(data_dir),
        recursive=True,
        required_exts=[".md", ".txt"],
    )

    documents = reader.load_data(show_progress=False)
    if not documents:
        logger.error("目录中没有可读取的 .md/.txt 文档: %s", data_dir)
        raise RuntimeError(f"目录中没有可读取的文档：{data_dir}")

    # 汇总加载结果，便于确认语料是否齐全。
    file_names = sorted({doc.metadata.get("file_name", "?") for doc in documents})
    logger.info("加载完成: 共 %d 个 Document，文件清单=%s", len(documents), file_names)

    # 逐条记录每个文档的关键信息，调试切块/检索结果时很有用。
    for index, doc in enumerate(documents, start=1):
        text_len = len(doc.get_content())
        logger.debug(
            "文档 #%d file_name=%s 字符数=%d metadata_keys=%s",
            index,
            doc.metadata.get("file_name"),
            text_len,
            list(doc.metadata.keys()),
        )

    return documents
