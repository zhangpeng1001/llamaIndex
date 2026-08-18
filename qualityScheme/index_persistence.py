"""索引持久化模块（Milvus 向量存储版）。

对应 demo 中 ``rag.py/build_and_persist_index``，但向量不再写本地 JSON，
而是存入 Milvus 指定 collection（``qualityScheme_llamaIndex``）。

学习要点:
    - ``MilvusVectorStore``：LlamaIndex 的 Milvus 适配器，向量持久化由 Milvus
      负责，进程重启后无需重新嵌入即可加载。
    - ``VectorStoreIndex.from_vector_store``：从已有 vector store 构建索引，
      不依赖本地 ``persist_dir``；检索时直接查 Milvus。
    - ``StorageContext``：当传入 vector_store 时，``VectorStoreIndex`` 会把节点
      写入该 store（Milvus）；Milvus 自带 docstore/text 字段，故无需额外磁盘持久化。
    - manifest 机制：Milvus collection 的向量维度由 embed_model 决定，切换模型
      后维度不匹配会导致写入失败。因此保留一个本地 manifest 记录模型名与切块
      参数，加载时校验，提示是否需要 rebuild。

业务背景:
    质检规范文档更新频率低，构建一次索引后可长期复用；首次启动会进行切块
    与嵌入（OpenAI 模式会消耗 API 额度），之后直接从 Milvus 加载即可。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding

from .document_loader import load_documents
from .document_parser import parse_documents
from .vector_index import build_vector_index

if TYPE_CHECKING:
    from llama_index.core.vector_stores.types import BasePydanticVectorStore

    from .config import QualitySchemeConfig

logger = logging.getLogger(__name__)

# manifest 文件名：记录索引构建时的关键参数，加载时做一致性校验。
# 注意：这只是一个小元信息文件，不是向量数据；向量本身存在 Milvus。
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

    storage_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "embedding_model": str(
            getattr(embed_model, "model_name", type(embed_model).__name__)
        ),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "schema_version": 2,
        "vector_store": "milvus",
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
            "向量维度不同，Milvus 无法复用。请使用 rebuild=True 重新构建索引。"
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
    vector_store: "BasePydanticVectorStore | None" = None,
) -> VectorStoreIndex:
    """构建并持久化索引（向量存 Milvus），或从 Milvus 直接加载。

    参数:
        data_dir: 数据源目录。
        storage_dir: 本地 manifest 存放目录（仅元信息，非向量）。
        embed_model: 嵌入模型。
        rebuild: 是否强制重建（重建 Milvus collection 并重新切块嵌入）。
        chunk_size: 切块最大字符数。
        chunk_overlap: 切块重叠字符数。
        vector_store: 自定义向量存储（MilvusVectorStore）。为 None 时回退到
            旧的本地磁盘逻辑（向后兼容，但业务路径会传入 Milvus store）。

    返回:
        VectorStoreIndex 实例。

    决策逻辑:
        1. 传入 vector_store（Milvus 路径）：
           - rebuild=True → 用 overwrite=True 重建 collection，全量摄取写入；
           - collection 已有数据 → 校验 manifest → from_vector_store 加载；
           - collection 无数据 → 全量摄取写入。
        2. 未传入 vector_store → 沿用原本地磁盘逻辑（兼容）。
    """

    # ------------------------------------------------------------------
    # 兼容路径：未接入 Milvus 时走原磁盘逻辑。
    # ------------------------------------------------------------------
    if vector_store is None:
        logger.warning(
            "未传入 vector_store，回退本地磁盘存储逻辑（向量不会进 Milvus）"
        )
        return _build_local_disk_index(
            data_dir,
            storage_dir,
            embed_model,
            rebuild=rebuild,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    # ------------------------------------------------------------------
    # Milvus 路径
    # ------------------------------------------------------------------
    # 注意：vector_store 在创建时已根据 rebuild 决定 overwrite，collection
    # 是否已有数据由 collection_has_data 在 web 层判断。这里基于“当前
    # collection 是否已初始化”决定加载还是摄取。
    is_initialized = bool(getattr(vector_store, "_collection_initialized", False))

    logger.info(
        "Milvus 索引构建决策: rebuild=%s, collection_initialized=%s, store=%s",
        rebuild,
        is_initialized,
        type(vector_store).__name__,
    )

    # 已初始化且未要求重建：从 Milvus 加载，跳过摄取与嵌入。
    if is_initialized and not rebuild:
        _validate_manifest(
            storage_dir,
            embed_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        logger.info("从 Milvus 加载索引（不重新嵌入）")
        index = VectorStoreIndex.from_vector_store(
            vector_store, embed_model=embed_model
        )
        logger.info("Milvus 索引加载完成")
        return index

    # 否则：全量摄取写入 Milvus。
    # rebuild 时 collection 已被 overwrite 删除；无数据时 collection 尚未创建，
    # build_vector_index 写入时由 MilvusVectorStore 自动创建。
    logger.info("开始全量摄取并写入 Milvus（加载文档 -> 切块嵌入 -> 写入 collection）")
    documents = load_documents(data_dir)
    nodes = parse_documents(
        documents,
        embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    index = build_vector_index(nodes, embed_model, vector_store=vector_store)

    # 向量已写入 Milvus（Milvus 即持久化），本地只写 manifest 元信息。
    _write_manifest(
        storage_dir,
        embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    logger.info("向量已写入 Milvus，manifest 已记录: %s", storage_dir)
    return index


def _build_local_disk_index(
    data_dir: Path,
    storage_dir: Path,
    embed_model: BaseEmbedding,
    *,
    rebuild: bool,
    chunk_size: int,
    chunk_overlap: int,
) -> VectorStoreIndex:
    """旧版本地磁盘索引逻辑（未接入 Milvus 时的兼容回退）。

    保留原 StorageContext + persist + load_index_from_storage 链路，便于在
    Milvus 不可用时临时使用。业务正常路径不走这里。
    """

    import shutil

    from llama_index.core import StorageContext, load_index_from_storage

    index_store_file = storage_dir / "index_store.json"
    logger.info(
        "[本地磁盘回退] 索引构建决策: data_dir=%s, storage_dir=%s, rebuild=%s, "
        "index_store_exists=%s",
        data_dir,
        storage_dir,
        rebuild,
        index_store_file.exists(),
    )

    if index_store_file.exists() and not rebuild:
        _validate_manifest(
            storage_dir,
            embed_model,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        logger.info("[本地磁盘回退] 从已有索引加载: %s", storage_dir)
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        logger.info("[本地磁盘回退] 索引加载完成")
        return index

    if rebuild and storage_dir.exists():
        logger.info("[本地磁盘回退] rebuild=True，清理旧索引目录: %s", storage_dir)
        shutil.rmtree(storage_dir)

    storage_dir.mkdir(parents=True, exist_ok=True)

    logger.info("[本地磁盘回退] 全量构建索引")
    documents = load_documents(data_dir)
    nodes = parse_documents(
        documents,
        embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    index = build_vector_index(nodes, embed_model)

    index.storage_context.persist(persist_dir=str(storage_dir))
    _write_manifest(
        storage_dir,
        embed_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    logger.info("[本地磁盘回退] 索引已持久化到: %s", storage_dir)
    return index
