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
    """

    provider: str
    llm_model: str
    embed_model: str
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

    config = QualitySchemeConfig(
        provider=selected_provider,
        llm_model=os.getenv("LLAMAINDEX_LLM_MODEL", "gpt-4.1-mini"),
        embed_model=os.getenv(
            "LLAMAINDEX_EMBED_MODEL", "text-embedding-3-small"
        ),
        api_base=os.getenv("OPENAI_API_BASE") or None,
    )

    logger.info(
        "加载质检业务配置: provider=%s, llm=%s, embed=%s, data_dir=%s, storage_dir=%s",
        config.provider,
        config.llm_model,
        config.embed_model,
        config.data_dir,
        config.storage_dir,
    )
    return config
