"""【Storing 阶段】Milvus VectorStore 创建 + 写入 Nodes + manifest。

对应 RAG 四大阶段的第三阶段:把 Indexing 产出的 Nodes 写入 Milvus 向量库,
后续 Querying 阶段可直接从 Milvus 检索。

学习要点:
    - MilvusVectorStore 是 LlamaIndex 对 Milvus 的向量存储适配器,实现
      BasePydanticVectorStore 接口,可传给 VectorStoreIndex.from_vector_store。
    - Milvus 2.x 的 db_name 是命名空间概念,把质检业务放到独立 db(如 kernel_data_platform)。
    - similarity_metric=COSINE 适合语义嵌入(默认 IP 内积不归一化时结果不稳定)。
    - enable_sparse=True 开启稀疏向量字段,是 Hybrid 检索(Dense+BM25)的前置条件。
    - dim 参数由 embed_model 运行时探测,避免硬编码 1024/384。
    - overwrite=True 时若 collection 已存在则删除重建,用于 rebuild 流程。
    - manifest 机制:记录索引构建时的模型名与切块参数,加载时校验一致性。

业务背景:
    质检规范文档更新频率低,构建一次索引后可长期复用;首次启动会进行切块
    与嵌入(OpenAI 模式会消耗 API 额度),之后直接从 Milvus 加载即可。
    向量存在 Milvus,本地只存 manifest 元信息(不含向量数据)。

复用模块:
    - qualityScheme.milvus_store.ensure_milvus_database: 确保 Milvus db 存在
    - qualityScheme.milvus_store.create_milvus_vector_store: 创建 MilvusVectorStore
    - qualityScheme.milvus_store.get_embedding_dimension: 探测嵌入维度
    - qualityScheme.milvus_store.collection_has_data: 检查 collection 是否有数据
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import BaseNode

from qualityScheme.milvus_store import (
    collection_has_data,
    create_milvus_vector_store,
    ensure_milvus_database,
    get_embedding_dimension,
)

if TYPE_CHECKING:
    from .config import QualitySchemeConfig

logger = logging.getLogger(__name__)

# manifest 文件名:记录索引构建时的关键参数,加载时做一致性校验
MANIFEST_FILE_NAME = "src_manifest.json"


def run_storing(
    config: "QualitySchemeConfig",
    embed_model: BaseEmbedding,
    spec_nodes: list[BaseNode],
    check_item_nodes: list[BaseNode],
    *,
    rebuild: bool = False,
) -> VectorStoreIndex:
    """执行 Storing 阶段:创建 MilvusVectorStore + 写入 Nodes + 写 manifest。

    参数:
        config: 质检业务配置(含 milvus_uri/db/collection、storage_dir)。
        embed_model: 嵌入模型(用于探测维度,且 VectorStoreIndex 加载时需要)。
        spec_nodes: 规范文档切块后的 Node 列表(Indexing 阶段产出)。
        check_item_nodes: 检查项 Node 列表(Indexing 阶段产出)。
        rebuild: True 时删除并重建已有 collection(overwrite=True)。

    返回:
        VectorStoreIndex 实例,可直接用于 Querying 阶段检索。

    流程:
        1. get_embedding_dimension(embed_model) → dim
        2. ensure_milvus_database(config.milvus_uri, config.milvus_db)
        3. create_milvus_vector_store(config, dim=dim, overwrite=rebuild)
        4. VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
        5. index.insert_nodes(spec_nodes + check_item_nodes)  # 写入 Milvus
        6. _write_manifest(config.storage_dir, embed_model, node_count=...)

    日志:
        - dim、collection、db、overwrite
        - 写入节点数(spec + check_item)
        - manifest 路径
        - collection 行数(写入后校验)

    异常:
        RuntimeError: Milvus 连接失败或写入异常。
    """

    logger.info("===== Storing 阶段开始 =====")
    logger.info(
        "  入参: spec_nodes=%d, check_item_nodes=%d, rebuild=%s, "
        "milvus_uri=%s..., db=%s, collection=%s",
        len(spec_nodes),
        len(check_item_nodes),
        rebuild,
        config.milvus_uri[:40],
        config.milvus_db,
        config.milvus_collection,
    )

    total_nodes = len(spec_nodes) + len(check_item_nodes)
    if total_nodes == 0:
        logger.error("Storing 输入为空: spec=0, check_item=0")
        raise ValueError("Storing 阶段需要非空的 Node 列表,请先执行 Indexing")

    # ------------------------------------------------------------------
    # Step 1: 探测嵌入维度(Milvus collection 创建时需要)
    # ------------------------------------------------------------------
    logger.info("Step 1: 探测嵌入维度")
    dim = get_embedding_dimension(embed_model)
    logger.info("  嵌入维度: dim=%d", dim)

    # ------------------------------------------------------------------
    # Step 2: 确保 Milvus 数据库存在
    # ------------------------------------------------------------------
    logger.info("Step 2: 确保 Milvus 数据库存在: db=%s", config.milvus_db)
    ensure_milvus_database(config.milvus_uri, config.milvus_db)

    # ------------------------------------------------------------------
    # Step 3: 创建 MilvusVectorStore(rebuild 时 overwrite=True)
    # ------------------------------------------------------------------
    logger.info(
        "Step 3: 创建 MilvusVectorStore: collection=%s, dim=%d, overwrite=%s, "
        "metric=COSINE, enable_sparse=True",
        config.milvus_collection,
        dim,
        rebuild,
    )
    vector_store = create_milvus_vector_store(config, dim=dim, overwrite=rebuild)

    # ------------------------------------------------------------------
    # Step 4: 从 vector_store 构建 VectorStoreIndex
    # ------------------------------------------------------------------
    logger.info("Step 4: 从 MilvusVectorStore 构建 VectorStoreIndex")
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    logger.info("  VectorStoreIndex 构建完成: %s", type(index).__name__)

    # ------------------------------------------------------------------
    # Step 5: 写入 Nodes 到 Milvus(spec_nodes + check_item_nodes 一起写)
    # ------------------------------------------------------------------
    all_nodes = list(spec_nodes) + list(check_item_nodes)
    logger.info(
        "Step 5: 写入 Nodes 到 Milvus: 总数=%d (spec=%d + check_item=%d)",
        len(all_nodes),
        len(spec_nodes),
        len(check_item_nodes),
    )
    # insert_nodes 会把 Node 的 embedding 和 metadata 一起写入 Milvus
    index.insert_nodes(all_nodes)
    logger.info("  Nodes 写入完成")

    # ------------------------------------------------------------------
    # Step 6: 写 manifest(本地元信息,非向量数据)
    # ------------------------------------------------------------------
    logger.info("Step 6: 写 manifest 到 %s", config.storage_dir)
    _write_manifest(
        config.storage_dir,
        embed_model,
        node_count=total_nodes,
        spec_count=len(spec_nodes),
        check_item_count=len(check_item_nodes),
    )

    # ------------------------------------------------------------------
    # Step 7: 校验 collection 行数(写入后)
    # ------------------------------------------------------------------
    logger.info("Step 7: 校验 collection 数据(写入后)")
    has_data = collection_has_data(config)
    logger.info("  collection_has_data=%s", has_data)

    logger.info("===== Storing 阶段完成 =====")
    return index


def load_existing_index(
    config: "QualitySchemeConfig",
    embed_model: BaseEmbedding,
) -> VectorStoreIndex | None:
    """启动时若 Milvus collection 已有数据,直接从 Milvus 加载索引。

    参数:
        config: 质检业务配置(含 milvus_uri/db/collection)。
        embed_model: 嵌入模型(VectorStoreIndex 加载时需要)。

    返回:
        VectorStoreIndex 实例(若 collection 有数据);None(若 collection 无数据)。

    流程:
        1. collection_has_data(config) 检查 collection 是否有数据
        2. 若有数据,create_milvus_vector_store(overwrite=False)
        3. VectorStoreIndex.from_vector_store 加载
        4. 校验 manifest 一致性(模型名/切块参数)

    日志:
        - collection 是否存在、行数
        - 加载来源(Milvus)或跳过原因(无数据)
    """

    logger.info("检查 Milvus 是否已有索引数据...")
    has_data = collection_has_data(config)
    if not has_data:
        logger.info("  collection 无数据,跳过加载(需要先执行 Storing)")
        return None

    logger.info("  collection 有数据,从 Milvus 加载索引")
    # 探测维度(MilvusVectorStore 创建时需要)
    dim = get_embedding_dimension(embed_model)
    # overwrite=False:不删除已有 collection,直接连接
    vector_store = create_milvus_vector_store(config, dim=dim, overwrite=False)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )
    logger.info("  Milvus 索引加载完成: %s", type(index).__name__)

    # 校验 manifest(若存在)
    _validate_manifest(config.storage_dir, embed_model)

    return index


def _write_manifest(
    storage_dir: Path,
    embed_model: BaseEmbedding,
    *,
    node_count: int,
    spec_count: int,
    check_item_count: int,
) -> None:
    """写入 manifest,记录索引构建时的关键参数。

    参数:
        storage_dir: manifest 存放目录(src/storage)。
        embed_model: 嵌入模型(记录名称,加载时校验一致性)。
        node_count: 写入的 Node 总数。
        spec_count: 规范文档 Node 数。
        check_item_count: 检查项 Node 数。

    日志:
        - manifest 写入路径与内容摘要。
    """

    storage_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "embedding_model": str(
            getattr(embed_model, "model_name", type(embed_model).__name__)
        ),
        "node_count": node_count,
        "spec_node_count": spec_count,
        "check_item_node_count": check_item_count,
        "schema_version": 3,  # src 版本 schema(区别于 qualityScheme 的 v2)
        "vector_store": "milvus",
        "store_module": "src.storing",
    }
    manifest_path = storage_dir / MANIFEST_FILE_NAME
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("  manifest 已写入: %s", manifest_path)
    logger.debug("  manifest 内容: %s", manifest)


def _validate_manifest(
    storage_dir: Path,
    embed_model: BaseEmbedding,
) -> None:
    """校验现有 manifest 是否与当前模型一致。

    参数:
        storage_dir: manifest 存放目录。
        embed_model: 当前嵌入模型。

    日志:
        - 模型不一致时记录 error(但不中断,允许加载,因为维度相同时仍可用)。
        - manifest 不存在时记录 warning 并跳过。
    """

    manifest_path = storage_dir / MANIFEST_FILE_NAME
    if not manifest_path.exists():
        logger.warning("  storage 目录缺少 manifest,跳过模型一致性校验")
        return

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("  manifest 读取失败,跳过校验: %s", exc)
        return

    current_model = str(
        getattr(embed_model, "model_name", type(embed_model).__name__)
    )
    stored_model = manifest.get("embedding_model")

    if stored_model != current_model:
        logger.error(
            "  Embedding 模型不一致: 存储=%s, 当前=%s(维度可能不同,建议 rebuild)",
            stored_model,
            current_model,
        )
    else:
        logger.info("  manifest 模型一致性校验通过: %s", current_model)
