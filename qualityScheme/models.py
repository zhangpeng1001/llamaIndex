"""质检业务的模型创建与注册。

复用 llamaindex_demo 的 LocalExtractiveLLM / LocalHashEmbedding 实现，
避免重复实现离线模型；同时注册到 LlamaIndex 全局 Settings。
"""

from __future__ import annotations

import logging

from llama_index.core import Settings
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import LLM

from llamaindex_demo.local_models import LocalExtractiveLLM, LocalHashEmbedding

from .config import QualitySchemeConfig

logger = logging.getLogger(__name__)


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
        logger.info("使用本地离线模型（仅供学习调试）")
        llm = LocalExtractiveLLM()
        embed_model = LocalHashEmbedding()

    # 写入全局 Settings，使未显式传参的组件也能拿到默认模型。
    Settings.llm = llm
    Settings.embed_model = embed_model
    return llm, embed_model
