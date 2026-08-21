"""模型配置模块(LLM + Embedding)。

学习要点:
    - 复用 qualityScheme.models.configure_quality_models,不重新实现模型创建逻辑。
    - 该函数支持两种模式:
        1. openai:通过 OpenAI 兼容接口调用 LLM + Embedding(推荐生产使用)
        2. local:连接本地 Ollama 服务(需先安装 Ollama 并拉取模型)
    - 创建好的模型会注册到 LlamaIndex 全局 Settings,后续组件可隐式使用。

业务背景:
    质检规范 RAG 系统的模型选择直接影响检索和生成质量:
        - Embedding 模型决定向量空间,Milvus collection 的维度由它探测
        - LLM 模型决定方案生成的质量和响应速度
    local 模式下必须用 Ollama(不能用 LocalHashEmbedding/ExtractiveLLM 等伪模型,
    否则向量无语义相似性,检索质量极差)。
"""

from __future__ import annotations

# 直接 re-export qualityScheme.models 的配置函数
# 该函数内部会:
#   1. 根据 config.provider 选择 OpenAI 或 Ollama
#   2. 创建 LLM 和 Embedding 实例
#   3. 注册到 LlamaIndex Settings 全局
#   4. 返回 (llm, embed_model) 元组供显式注入
from qualityScheme.models import configure_quality_models

__all__ = ["configure_quality_models"]
