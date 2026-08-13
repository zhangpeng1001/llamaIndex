"""项目配置。

这里有意不使用复杂的配置框架，让初学者能直接看懂环境变量如何进入程序。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# __file__ 位于 src/llamaindex_demo/config.py，parents[2] 正好是项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
STORAGE_DIR = PROJECT_ROOT / "storage"


@dataclass(frozen=True)
class AppConfig:
    """集中保存会影响示例运行的参数。"""

    provider: str
    llm_model: str
    embed_model: str
    data_dir: Path = DATA_DIR
    storage_dir: Path = STORAGE_DIR

    @property
    def uses_openai(self) -> bool:
        return self.provider == "openai"


def load_config(provider: str | None = None) -> AppConfig:
    """读取 .env 和环境变量，并返回不可变配置对象。

    命令行传入的 provider 优先级最高，便于执行 ``--provider local`` 临时覆盖。
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

    return AppConfig(
        provider=selected_provider,
        llm_model=os.getenv("LLAMAINDEX_LLM_MODEL", "gpt-4.1-mini"),
        embed_model=os.getenv(
            "LLAMAINDEX_EMBED_MODEL", "text-embedding-3-small"
        ),
    )

