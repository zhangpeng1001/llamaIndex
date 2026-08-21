"""qualityScheme 业务配置。

独立于 demo 的 config.py，但复用项目根目录的 .env，便于在同一个进程里
分别加载 demo 与业务两套索引。
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# qualityScheme 目录位于项目根下；parents[1] 即项目根。
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parents[0]

# 业务数据源：从 standard 提取出的 Markdown 规范文本。
DATA_DIR = PACKAGE_DIR / "data"
# 索引持久化目录：与 demo 的 storage 隔离，避免互相覆盖。
STORAGE_DIR = PACKAGE_DIR / "storage"

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class QualitySchemeConfig:
    """质检规范业务的不可变配置。

    与 demo 的 AppConfig 字段保持一致，便于复用 models.configure_models。
    新增 Milvus 向量库连接配置：向量不再写本地 JSON，而是存入 Milvus。

    安全约束（GPT文档第7节）：
      - Milvus URI 不允许硬编码，必须通过 .env 的 QUALITY_MILVUS_URI 显式配置。
        这样避免把内部服务地址泄漏到开源代码中，也方便不同环境（dev/staging/prod）
        指向不同的 Milvus 实例。
    """

    provider: str
    llm_model: str
    embed_model: str
    # Milvus 连接配置：全部必须通过 .env 显式配置，无默认值。
    # 注意：dataclass 要求无默认值字段必须排在有默认值字段之前，
    # 因此把这三个字段放在 api_base/data_dir/storage_dir 之前。
    milvus_uri: str
    milvus_db: str
    milvus_collection: str
    api_base: str | None = None
    data_dir: Path = DATA_DIR
    storage_dir: Path = STORAGE_DIR

    @property
    def uses_openai(self) -> bool:
        """是否使用 OpenAI 兼容模型。"""

        return self.provider == "openai"


def load_quality_config(provider: str | None = None) -> QualitySchemeConfig:
    """读取 .env 与环境变量，返回质检业务配置。

    参数:
        provider: 可选的模型提供方覆盖，优先级高于 .env。

    日志:
        - 记录最终选择的 provider、数据目录、存储目录，便于排查路径问题。

    异常:
        RuntimeError: 缺少必需的环境变量（OPENAI_API_KEY 或 QUALITY_MILVUS_URI）。
        ValueError: provider 不在允许列表中。
    """

    load_dotenv(PROJECT_ROOT / ".env")
    selected_provider = (
        provider or os.getenv("LLAMAINDEX_MODEL_PROVIDER", "local")
    ).lower()
    if selected_provider not in {"local", "openai"}:
        raise ValueError("provider 只能是 'local' 或 'openai'")

    if selected_provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "选择 openai 模式时必须设置 OPENAI_API_KEY；"
            "请复制 .env.example 为 .env 并填写密钥。"
        )

    # Milvus URI 必须显式配置，不提供默认值（避免硬编码内部服务地址）。
    milvus_uri = os.getenv("QUALITY_MILVUS_URI")
    if not milvus_uri:
        raise RuntimeError(
            "缺少必需的环境变量 QUALITY_MILVUS_URI；\n"
            "请在项目根目录的 .env 文件中添加：\n"
            "  QUALITY_MILVUS_URI=http://your-milvus-host:19530\n"
            "例如：\n"
            "  QUALITY_MILVUS_URI=http://milvus-dev1.e-tudou.com:19530"
        )

    milvus_db = os.getenv("QUALITY_MILVUS_DB")
    if not milvus_db:
        raise RuntimeError(
            "缺少必需的环境变量 QUALITY_MILVUS_DB；\n"
            "请在项目根目录的 .env 文件中添加，例如：\n"
            "  QUALITY_MILVUS_DB=kernel_data_platform"
        )

    milvus_collection = os.getenv("QUALITY_MILVUS_COLLECTION")
    if not milvus_collection:
        raise RuntimeError(
            "缺少必需的环境变量 QUALITY_MILVUS_COLLECTION；\n"
            "请在项目根目录的 .env 文件中添加，例如：\n"
            "  QUALITY_MILVUS_COLLECTION=qualityScheme_llamaIndex"
        )

    config = QualitySchemeConfig(
        provider=selected_provider,
        llm_model=os.getenv("LLAMAINDEX_LLM_MODEL", "gpt-4.1-mini"),
        embed_model=os.getenv(
            "LLAMAINDEX_EMBED_MODEL", "text-embedding-3-small"
        ),
        api_base=os.getenv("OPENAI_API_BASE") or None,
        milvus_uri=milvus_uri,
        milvus_db=milvus_db,
        milvus_collection=milvus_collection,
    )

    logger.info(
        "加载质检业务配置: provider=%s, llm=%s, embed=%s, data_dir=%s, storage_dir=%s, "
        "milvus_uri=%s, milvus_db=%s, milvus_collection=%s",
        config.provider,
        config.llm_model,
        config.embed_model,
        config.data_dir,
        config.storage_dir,
        # 日志中只显示 URI 前半段，避免完整地址泄漏到日志聚合系统。
        milvus_uri.split("@")[-1][:40] + "..." if len(milvus_uri) > 40 else milvus_uri,
        config.milvus_db,
        config.milvus_collection,
    )
    return config
