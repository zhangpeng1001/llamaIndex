"""索引持久化模块。

对应 demo 中 ``rag.py/build_and_persist_index``。

学习要点:
    - ``StorageContext``：LlamaIndex 的存储上下文，封装 docstore、index_store、
      vector_store 三类存储。
    - ``persist``：把索引写入磁盘，下次启动可跳过摄取与嵌入步骤。
    - ``load_index_from_storage``：从磁盘加载已持久化的索引。
    - manifest 机制：不同 Embedding 模型的向量空间/维度不可混用，因此在
      持久化目录里写一个 manifest 记录模型名，加载时校验，避免维度不匹配。

业务背景:
    质检规范文档更新频率低，构建一次索引后可长期复用；首次启动会进行切块
    与嵌入（OpenAI 模式会消耗 API 额度），之后直接从 storage 加载即可。
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.embeddings import BaseEmbedding

from .document_loader import load_documents
from .document_parser import parse_documents
from .vector_index import build_vector_index

logger = logging.getLogger(__name__)

# manifest 文件名：记录索引对应的模型与切块参数版本，加载时做一致性校验。
MANIFEST_FILE_NAME = "quality_manifest.json"


def _manifest_path(storage_dir: Path) -> Path:
    return storage_dir / MANIFEST_FILE_NAME


def _write_manifest(
    storage_dir: Path,
    embed_model: BaseEmbedding,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    """写入 manifest，记录索引构建时的关键参数。"""

    manifest = {
        "embedding_model": str(
            getattr(embed_model, "model_name", type(embed_model).__name__)
        ),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "schema_version": 1,
    }
    _manifest_path(storage_dir).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.debug("已写入 manifest: %s", manifest)


def _validate_manifest(
    storage_dir: Path,
    embed_model: BaseEmbedding,
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    """校验现有 manifest 是否与当前模型/参数一致。"""

    manifest_file = _manifest_path(storage_dir)
    if not manifest_file.exists():
        logger.warning("storage 目录缺少 manifest，跳过模型一致性校验")
        return

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    current_embed_model = str(
        getattr(embed_model, "model_name", type(embed_model).__name__)
    )
    stored_embed_model = manifest.get("embedding_model")

    if stored_embed_model != current_embed_model:
        logger.error(
            "Embedding 模型不一致: 存储=%s, 当前=%s",
            stored_embed_model,
            current_embed_model,
        )
        raise RuntimeError(
            "现有索引使用的 Embedding 模型是 "
            f"{stored_embed_model!r}，当前模型是 {current_embed_model!r}。"
            "请使用 rebuild=True 重新构建索引。"
        )

    if manifest.get("chunk_size") != chunk_size or manifest.get(
        "chunk_overlap"
    ) != chunk_overlap:
        logger.warning(
            "切块参数不一致（存储 chunk_size=%s overlap=%s，当前 %s/%s），"
            "建议 rebuild 以保证检索一致性",
            manifest.get("chunk_size"),
            manifest.get("chunk_overlap"),
            chunk_size,
            chunk_overlap,
        )


def build_and_persist_index(
    data_dir: Path,
    storage_dir: Path,
    embed_model: BaseEmbedding,
    *,
    rebuild: bool = False,
    chunk_size: int = 256,
    chunk_overlap: int = 40,
) -> VectorStoreIndex:
    """构建并持久化索引，或在索引已存在时直接加载。

    参数:
        data_dir: 数据源目录。
        storage_dir: 索引持久化目录。
        embed_model: 嵌入模型。
        rebuild: 是否强制重建（删除旧索引后重新切块嵌入）。
        chunk_size: 切块最大字符数。
        chunk_overlap: 切块重叠字符数。

    返回:
        VectorStoreIndex 实例。

    日志:
        - 决策路径（加载已有 vs 重建）；
        - rebuild 时清理旧目录；
        - 持久化写入路径。
    """

    index_store_file = storage_dir / "index_store.json"
    logger.info(
        "索引构建决策: data_dir=%s, storage_dir=%s, rebuild=%s, index_store_exists=%s",
        data_dir,
        storage_dir,
        rebuild,
        index_store_file.exists(),
    )

    # 1) 已存在索引且未要求重建：先校验模型一致性，再加载。
    if index_store_file.exists() and not rebuild:
        _validate_manifest(
            storage_dir,
            embed_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        logger.info("从已有索引加载: %s", storage_dir)
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        logger.info("索引加载完成")
        return index

    # 2) rebuild 是明确请求：仅清理本业务固定 storage 目录，避免误删其他数据。
    if rebuild and storage_dir.exists():
        logger.info("rebuild=True，清理旧索引目录: %s", storage_dir)
        shutil.rmtree(storage_dir)

    storage_dir.mkdir(parents=True, exist_ok=True)

    # 3) 重新走“加载 -> 摄取 -> 构建”全流程。
    logger.info("开始全量构建索引（加载文档 -> 切块嵌入 -> 构建索引）")
    documents = load_documents(data_dir)
    nodes = parse_documents(
        documents,
        embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    index = build_vector_index(nodes, embed_model)

    # 4) 持久化并写 manifest。
    index.storage_context.persist(persist_dir=str(storage_dir))
    _write_manifest(
        storage_dir,
        embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    logger.info("索引已持久化到: %s", storage_dir)
    return index
