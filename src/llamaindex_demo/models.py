"""创建并注册 LLM、Embedding 模型。"""

from __future__ import annotations

from llama_index.core import Settings
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms import LLM

from .config import AppConfig
from .local_models import LocalExtractiveLLM, LocalHashEmbedding


def configure_models(config: AppConfig) -> tuple[LLM, BaseEmbedding]:
    """根据配置创建模型，并写入 LlamaIndex 全局 Settings。

    Settings 是 LlamaIndex 的便捷默认值容器。显式向组件传入 llm/embed_model 更利于
    大型项目测试；教程中两种方式都会展示。
    """

    if config.uses_openai:
        # 集成包是按需拆分的，这也是 requirements.txt 单独声明它们的原因。
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.llms.openai import OpenAI

        # api_base 用于对接 OpenAI 兼容服务（自建网关、第三方平台等）。
        # 留空则走 OpenAI 官方地址。注意只需填到 /v1，客户端会自动补 /chat/completions。
        llm: LLM = OpenAI(
            model=config.llm_model,
            temperature=0.1,
            api_base=config.api_base,
        )
        # OpenAIEmbedding.__init__ 会把 model 强制转成 OpenAIEmbeddingModelType 枚举，
        # 该枚举只收录 OpenAI 官方模型名，第三方/兼容服务（如 Qwen3-Embedding-0.6B）
        # 会抛 ValueError。这里用一个合法枚举值通过校验，再用 model_name 指定真正
        # 发给兼容网关的模型名（model_name 会覆盖内部 query_engine/text_engine）。
        embed_model: BaseEmbedding = OpenAIEmbedding(
            model="text-embedding-ada-002",
            model_name=config.embed_model,
            api_base=config.api_base,
        )

    else:
        llm = LocalExtractiveLLM()
        embed_model = LocalHashEmbedding()

    Settings.llm = llm
    Settings.embed_model = embed_model
    return llm, embed_model

