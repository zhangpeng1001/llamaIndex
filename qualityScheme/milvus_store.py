"""Milvus 向量存储工厂模块。

把 Milvus 相关操作集中在一处：连接/建库、维度探测、VectorStore 创建、
collection 数据检查。qualityScheme 的向量不再写本地 JSON，而是存入 Milvus
指定 collection（默认 ``qualityScheme_llamaIndex``，库 ``kernel_data_platform``）。

学习要点:
    - ``MilvusVectorStore``：LlamaIndex 对 Milvus 的向量存储适配器，实现
      ``BasePydanticVectorStore`` 接口；可传给 ``StorageContext`` 或
      ``VectorStoreIndex.from_vector_store``。
    - ``db_name``：Milvus 2.x 的数据库（命名空间）概念。MilvusVectorStore 1.1.0
      的 ``__init__`` 不直接暴露 ``db_name``，但其 ``**kwargs`` 会透传给底层
      ``MilvusClient(uri, token, db_name=...)``，因此通过 ``db_name=`` 关键字
      参数传入即可让连接指向 ``kernel_data_platform``。
    - ``similarity_metric``：默认 ``IP``（内积）；语义嵌入用 ``COSINE`` 更合适，
      与原相似度检索语义一致。
    - ``dim``：Milvus collection 需要确定向量维度。这里运行时探测 embed_model
      的输出维度，避免硬编码 1024/384，兼容 local 与 openai 两种 provider。
    - ``overwrite``：True 时若 collection 已存在则删除重建，用于 rebuild 流程。
    - ``MilvusClient``（new-style API）：本模块建库/检查 collection 时统一使用
      ``pymilvus.MilvusClient``，替代弃用的 ``connections.connect`` /
      ``utility.*`` / ``Collection``（ORM-style API），避免运行时警告。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.vector_stores.milvus import MilvusVectorStore

if TYPE_CHECKING:
    from llama_index.core.embeddings import BaseEmbedding

    from .config import QualitySchemeConfig

logger = logging.getLogger(__name__)


def get_embedding_dimension(embed_model: "BaseEmbedding") -> int:
    """探测嵌入模型的输出维度。

    参数:
        embed_model: 嵌入模型实例（local 或 OpenAI 兼容）。

    返回:
        向量维度（int）。Milvus collection 创建时需要该值。

    日志:
        - 模型名称与探测到的维度。
    """

    # 用一段短文本做探测；get_text_embedding 对两种 provider 都可用。
    probe = embed_model.get_text_embedding("dimension probe")
    dim = len(probe)
    model_name = getattr(embed_model, "model_name", type(embed_model).__name__)
    logger.info("探测嵌入维度: model=%s, dim=%d", model_name, dim)
    return dim


def ensure_milvus_database(uri: str, db_name: str) -> None:
    """确保目标数据库存在，不存在则创建。

    用户指定的 ``kernel_data_platform`` 一般已存在；这里做幂等保护：若不存在
    则用 MilvusClient 创建。MilvusVectorStore 内部的 MilvusClient 不会自动
    建库，因此必须先保证库存在，否则后续连接会失败。

    学习要点:
        - 使用 ``MilvusClient``（new-style API）替代弃用的
          ``connections.connect`` / ``utility.create_database``（ORM-style API）。
        - 创建数据库必须先连到 ``default`` 库（Milvus 元数据所在），
          再 ``create_database(db_name)``。
        - ``MilvusClient`` 通过 ``ConnectionManager`` 内部托管连接，
          ``client.close()`` 释放连接，无需手动 ``disconnect``。

    参数:
        uri: Milvus 连接地址。
        db_name: 数据库名。

    日志:
        - 数据库是否存在、是否触发创建。
    """

    # 延迟导入：pymilvus 体积较大，且本函数仅在建库时需要。
    from pymilvus import MilvusClient

    logger.info("检查 Milvus 数据库: uri=%s, db_name=%s", uri, db_name)
    # 先连 default 库：创建数据库属管理操作，必须在 default 下进行。
    client = MilvusClient(uri=uri, db_name="default")
    try:
        existing = client.list_databases()
        logger.info("现有数据库列表: %s", existing)
        if db_name in existing:
            logger.info("数据库已存在: %s", db_name)
            return
        client.create_database(db_name)
        logger.info("数据库不存在，已创建: %s", db_name)
    except Exception as exc:
        # 老版本 Milvus 可能不支持 list_databases；此时若库已存在则后续
        # 连接会成功，否则报错。这里仅记录警告，不中断流程。
        logger.warning("数据库检查/创建异常（若库已存在可忽略）: %s", exc)
    finally:
        try:
            client.close()
        except Exception:  # pragma: no cover - 清理用
            pass


def create_milvus_vector_store(
    config: "QualitySchemeConfig",
    *,
    dim: int,
    overwrite: bool = False,
) -> MilvusVectorStore:
    """创建指向固定 collection 的 MilvusVectorStore。

    参数:
        config: 质检业务配置（含 milvus_uri/db/collection）。
        dim: 向量维度（由 get_embedding_dimension 探测）。
        overwrite: 是否删除并重建已有 collection（rebuild 时为 True）。

    返回:
        MilvusVectorStore 实例，可直接用于 StorageContext 或 from_vector_store。

    日志:
        - 创建参数（collection、db、dim、overwrite、metric）。
    """

    logger.info(
        "创建 MilvusVectorStore: uri=%s, db=%s, collection=%s, dim=%d, "
        "overwrite=%s, similarity_metric=COSINE",
        config.milvus_uri,
        config.milvus_db,
        config.milvus_collection,
        dim,
        overwrite,
    )
    # db_name 经 MilvusVectorStore 的 **kwargs 透传给 MilvusClient / AsyncMilvusClient，
    # 使连接指向 kernel_data_platform 数据库。
    store = MilvusVectorStore(
        uri=config.milvus_uri,
        collection_name=config.milvus_collection,
        dim=dim,
        overwrite=overwrite,
        similarity_metric="COSINE",
        db_name=config.milvus_db,
    )
    return store


def collection_has_data(config: "QualitySchemeConfig") -> bool:
    """判断指定 collection 是否已存在且含向量数据。

    用于 ``build_and_persist_index`` 的加载/重建决策：已有数据且未要求重建时
    直接从 Milvus 加载，避免重复摄取与嵌入。

    学习要点:
        - 使用 ``MilvusClient``（new-style API）替代弃用的
          ``connections.connect`` / ``utility.has_collection`` / ``Collection``
          （ORM-style API），消除运行时弃用警告。
        - ``has_collection`` 判断存在性；``get_collection_stats`` 返回
          ``{"row_count": int}``，行数 > 0 视为已初始化。
        - Milvus 写入后 stats 的 row_count 可能滞后；这里调用前由
          MilvusVectorStore 内部 flush，或接受统计延迟（判断数据存在即可）。

    参数:
        config: 质检业务配置。

    返回:
        True 表示 collection 存在且行数 > 0。

    日志:
        - collection 是否存在、行数。
    """

    from pymilvus import MilvusClient

    logger.info(
        "检查 collection 数据: uri=%s, db=%s, collection=%s",
        config.milvus_uri,
        config.milvus_db,
        config.milvus_collection,
    )
    # 直接连目标数据库：has_collection / get_collection_stats 都在该库下查询。
    client = MilvusClient(uri=config.milvus_uri, db_name=config.milvus_db)
    try:
        exists = client.has_collection(config.milvus_collection)
        if not exists:
            logger.info("collection 不存在: %s", config.milvus_collection)
            return False
        # flush 让已插入但仍在内存的记录落盘，row_count 才会立即更新；
        # 否则新建/刚写入后 stats 可能滞后返回 0，导致健康检查误判为空。
        try:
            client.flush(config.milvus_collection)
        except Exception as exc:  # pragma: no cover - flush 在某些版本可能不必要
            logger.debug("flush 跳过（无影响）: %s", exc)
        stats = client.get_collection_stats(config.milvus_collection)
        # get_collection_stats 内部已把 row_count 转为 int。
        count = int(stats.get("row_count", 0))
        logger.info(
            "collection 存在: %s, 行数=%d", config.milvus_collection, count
        )
        return count > 0
    except Exception as exc:
        logger.warning("collection 数据检查异常: %s", exc)
        return False
    finally:
        try:
            client.close()
        except Exception:  # pragma: no cover
            pass
