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

        llm: LLM = OpenAI(model=config.llm_model, temperature=0.1)
        embed_model: BaseEmbedding = OpenAIEmbedding(model=config.embed_model)
    else:
        llm = LocalExtractiveLLM()
        embed_model = LocalHashEmbedding()

    Settings.llm = llm
    Settings.embed_model = embed_model
    return llm, embed_model

