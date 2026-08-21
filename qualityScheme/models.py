"""质检业务的模型创建与注册。

支持两种模型模式：
1. openai：通过 OpenAI 兼容接口（或自建网关）调用 LLM + Embedding，推荐生产使用。
2. local：尝试连接本地 Ollama 服务（需用户自行启动 Ollama 并拉取模型）。
   若未安装 Ollama 或模型不可用，则抛出明确错误，避免使用无效的伪模型（旧版
   LocalHashEmbedding/ExtractiveLLM 会生成无意义向量，导致检索质量极差）。

同时把创建好的模型注册到 LlamaIndex 全局 Settings。
"""

from __future__ import annotations

import logging
import os

from llama_index.core import Settings
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import LLM

from .config import QualitySchemeConfig

logger = logging.getLogger(__name__)


def _try_configure_ollama(
    config: QualitySchemeConfig,
) -> tuple[LLM, BaseEmbedding]:
    """尝试配置本地 Ollama 模型。

    优先读取环境变量：
      - OLLAMA_BASE_URL: Ollama 服务地址，默认 http://localhost:11434
      - OLLAMA_LLM_MODEL: 对话模型名，默认 qwen2.5:7b
      - OLLAMA_EMBED_MODEL: 嵌入模型名，默认 nomic-embed-text

    若 llama-index-llms-ollama / llama-index-embeddings-ollama 未安装，
    或 Ollama 服务不可达，则抛出 RuntimeError，提示用户正确配置。
    """
    import importlib.util

    ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_llm = os.getenv("OLLAMA_LLM_MODEL", "qwen2.5:7b")
    ollama_embed = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    logger.info(
        "尝试配置 Ollama 本地模型: base=%s, llm=%s, embed=%s",
        ollama_base, ollama_llm, ollama_embed,
    )

    # 1. 检查依赖是否安装
    llm_ok = importlib.util.find_spec("llama_index.llms.ollama") is not None
    embed_ok = importlib.util.find_spec("llama_index.embeddings.ollama") is not None
    if not llm_ok or not embed_ok:
        raise RuntimeError(
            "local 模式需要 Ollama 支持：请先安装依赖\n"
            "  pip install llama-index-llms-ollama llama-index-embeddings-ollama\n"
            "然后启动 Ollama 并拉取模型：\n"
            f"  ollama pull {ollama_llm}\n"
            f"  ollama pull {ollama_embed}\n"
            "如无本地 GPU，建议改用 provider=openai 模式（在 .env 中配置）。"
        )

    # 2. 尝试连接 Ollama（简单心跳检测）
    import urllib.request
    try:
        with urllib.request.urlopen(ollama_base, timeout=3) as resp:
            if resp.status != 200:
                raise ConnectionError(f"Ollama 返回状态 {resp.status}")
    except Exception as exc:
        raise RuntimeError(
            f"无法连接到 Ollama 服务 ({ollama_base})：{exc}\n"
            "请先启动 Ollama：\n"
            "  Windows: 在开始菜单中启动 Ollama\n"
            "  或访问 https://ollama.com/download 安装后执行 ollama serve\n"
            "如无本地 GPU，建议改用 provider=openai 模式（在 .env 中配置）。"
        ) from exc

    # 3. 创建模型实例
    from llama_index.llms.ollama import Ollama as OllamaLLM
    from llama_index.embeddings.ollama import OllamaEmbedding

    llm: LLM = OllamaLLM(
        model=ollama_llm,
        base_url=ollama_base,
        temperature=0.1,
        request_timeout=120,
    )
    embed_model: BaseEmbedding = OllamaEmbedding(
        model_name=ollama_embed,
        base_url=ollama_base,
    )
    logger.info("Ollama 模型配置成功")
    return llm, embed_model


def configure_quality_models(
    config: QualitySchemeConfig,
) -> tuple[LLM, BaseEmbedding]:
    """根据配置创建 LLM 与 Embedding 模型，并写入全局 Settings。

    参数:
        config: 质检业务配置。

    返回:
        (llm, embed_model) 元组，供后续索引、查询引擎等组件显式注入。

    日志:
        - 记录模型类型与名称，方便确认实际使用的是 local 还是 openai。

    异常:
        RuntimeError: local 模式下 Ollama 不可用，或 openai 模式缺少必要配置。
    """

    if config.uses_openai:
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.llms.openai import OpenAI

        logger.info("使用 OpenAI 兼容模型: llm=%s, embed=%s", config.llm_model, config.embed_model)
        # api_base 用于对接 OpenAI 兼容服务（自建网关、第三方平台等）。
        llm: LLM = OpenAI(
            model=config.llm_model,
            temperature=0.1,
            api_base=config.api_base,
        )
        # OpenAIEmbedding.__init__ 会把 model 强制转成枚举校验，第三方模型名
        # 会抛错。这里用一个合法枚举值通过校验，再用 model_name 指定真正
        # 发给兼容网关的模型名。
        embed_model: BaseEmbedding = OpenAIEmbedding(
            model="text-embedding-ada-002",
            model_name=config.embed_model,
            api_base=config.api_base,
        )
    else:
        # local 模式：优先使用 Ollama；失败时给出明确指引，不再使用无效伪模型。
        try:
            llm, embed_model = _try_configure_ollama(config)
        except RuntimeError as exc:
            logger.error("local 模式初始化失败: %s", exc)
            raise

    # 写入全局 Settings，使未显式传参的组件也能拿到默认模型。
    Settings.llm = llm
    Settings.embed_model = embed_model
    logger.info("全局模型注册完成: Settings.llm=%s, Settings.embed_model=%s",
                type(llm).__name__, type(embed_model).__name__)
    return llm, embed_model
