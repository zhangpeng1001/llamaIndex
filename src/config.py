"""配置加载模块(Loading/Indexing/Storing/Querying 共用)。

学习要点:
    - 复用 qualityScheme.config 的 QualitySchemeConfig 与 load_quality_config,
      不重新实现 .env 解析逻辑,避免重复维护配置项。
    - 用 dataclasses.replace 覆盖 data_dir/storage_dir 默认值,指向 src/data 和 src/storage,
      使新版与 qualityScheme 的数据目录隔离,互不干扰。
    - Milvus 连接配置仍走 .env 的 QUALITY_MILVUS_* 变量(无默认值,强制显式配置)。

业务背景:
    质检规范 RAG 系统的配置分为三类:
        1. 模型配置:provider(openai/local)、llm_model、embed_model、api_base
        2. Milvus 配置:uri、db、collection(必须显式配置,避免硬编码内部地址)
        3. 路径配置:data_dir(MD语料)、storage_dir(manifest 元信息)
    新版 src 把路径配置指向 src/data 和 src/storage,与 qualityScheme 隔离。
"""

from __future__ import annotations

import logging
from dataclasses import replace
from pathlib import Path

from qualityScheme.config import QualitySchemeConfig, load_quality_config as _load_base

logger = logging.getLogger(__name__)

# src 目录:本文件所在目录
PACKAGE_DIR = Path(__file__).resolve().parent
# 数据目录:存放从 PDF 增强提取的 Markdown 语料
DATA_DIR = PACKAGE_DIR / "data"
# 存储目录:存放 manifest 元信息(向量本身存 Milvus,这里只是元信息)
STORAGE_DIR = PACKAGE_DIR / "storage"
# 标准 PDF 目录:项目根的 standard/(7份时空数据规范 PDF)
STANDARD_DIR = PACKAGE_DIR.parents[0] / "standard"


def load_config(provider: str | None = None) -> QualitySchemeConfig:
    """读取 .env 与环境变量,返回质检业务配置(路径指向 src 下)。

    参数:
        provider: 可选的模型提供方覆盖(local/openai),优先级高于 .env。

    返回:
        QualitySchemeConfig 实例,data_dir 和 storage_dir 指向 src/data 和 src/storage。

    日志:
        - 记录 provider、llm_model、embed_model、data_dir、storage_dir、milvus 连接信息。
        - 路径覆盖前后的对比,便于排查路径问题。

    异常:
        RuntimeError: 缺少 QUALITY_MILVUS_URI/DB/COLLECTION 等必需环境变量(由 _load_base 抛出)。
        ValueError: provider 不在 {local, openai} 列表中(由 _load_base 抛出)。
    """

    logger.info("加载 src 配置: provider=%s", provider)
    # 先用 qualityScheme 的加载逻辑读取 .env,得到基础配置
    base_cfg = _load_base(provider)
    logger.info(
        "基础配置加载完成: provider=%s, llm=%s, embed=%s",
        base_cfg.provider,
        base_cfg.llm_model,
        base_cfg.embed_model,
    )

    # 覆盖 data_dir 和 storage_dir,指向 src 下
    # dataclasses.replace 会保留其他字段不变,只替换指定字段
    cfg = replace(
        base_cfg,
        data_dir=DATA_DIR,
        storage_dir=STORAGE_DIR,
    )

    logger.info(
        "src 配置最终生效: data_dir=%s, storage_dir=%s, standard_dir=%s, "
        "milvus_uri=%s..., milvus_db=%s, milvus_collection=%s",
        cfg.data_dir,
        cfg.storage_dir,
        STANDARD_DIR,
        cfg.milvus_uri[:40],
        cfg.milvus_db,
        cfg.milvus_collection,
    )
    return cfg
