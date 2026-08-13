"""仅供教学和测试使用的离线模型。

真实 RAG 通常需要在线 LLM 和语义嵌入模型。为了让读者没有 API Key 也能运行项目，
本模块实现 LlamaIndex 的两个扩展接口：CustomLLM 与 BaseEmbedding。

它们的价值是展示“模型可插拔”，并不追求回答质量，切勿直接用于生产环境。
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Generator

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.llms import CompletionResponse, CustomLLM, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback


class LocalHashEmbedding(BaseEmbedding):
    """把字符和相邻字符映射为固定维度向量的本地嵌入。

    相同/相近字词会落入相似的向量方向，因此足以演示向量索引与 Top-K 检索。
    它不理解真正语义，例如“汽车”和“轿车”不一定相近。
    """

    dimension: int = 384
    model_name: str = "local-hash-demo-v1"

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        normalized = re.sub(r"\s+", "", text.lower())

        # 同时使用单字符、双字符和空格分词，兼顾中文与英文。
        features = list(normalized)
        features += [normalized[i : i + 2] for i in range(len(normalized) - 1)]
        features += re.findall(r"[a-z0-9_]+", text.lower())
        for feature in features:
            digest = hashlib.sha256(feature.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimension
            # 使用另一位决定正负，可减少哈希碰撞带来的单向偏差。
            vector[bucket] += 1.0 if digest[4] % 2 == 0 else -1.0

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def _get_query_embedding(self, query: str) -> list[float]:
        return self._embed(query)

    async def _aget_query_embedding(self, query: str) -> list[float]:
        return self._embed(query)

    def _get_text_embedding(self, text: str) -> list[float]:
        return self._embed(text)


class LocalExtractiveLLM(CustomLLM):
    """从提示词上下文中抽取句子的极简 LLM 替身。

    QueryEngine 仍会正常完成“检索 -> 构造 Prompt -> 调用 LLM -> 封装响应”，
    只是最后一步由确定性规则代替生成式模型，因而非常适合单元测试。
    """

    context_window: int = 8192
    num_output: int = 512
    model_name: str = "local-extractive-demo"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
            is_chat_model=False,
        )

    @staticmethod
    def _answer(prompt: str) -> str:
        lower_prompt = prompt.lower()

        # 结构化输出示例需要合法 JSON。离线模式返回确定结果，以展示 Pydantic 解析链路。
        if "knowledge_card" in lower_prompt or "学习卡片" in prompt:
            return json.dumps(
                {
                    "title": "LlamaIndex RAG 学习卡片",
                    "summary": "RAG 先检索相关上下文，再由模型基于上下文生成回答。",
                    "keywords": ["LlamaIndex", "RAG", "检索", "索引"],
                    "difficulty": "beginner",
                },
                ensure_ascii=False,
            )

        # LlamaIndex 的不同响应合成器会使用略有差异的模板。这里尽量抽取 Context，
        # 未匹配时退回整个提示词尾部，保证示例仍可运行。
        context_match = re.search(
            r"context information is below\.(.*?)(?:query:|question:|given the context)",
            prompt,
            flags=re.IGNORECASE | re.DOTALL,
        ) or re.search(r"上下文[：:](.*?)问题[：:]", prompt, flags=re.DOTALL)
        context = context_match.group(1) if context_match else prompt[-5000:]

        question_matches = re.findall(
            r"(?:query|question|user|问题)\s*[：:]\s*(.+)",
            prompt,
            flags=re.IGNORECASE,
        )
        question = question_matches[-1] if question_matches else prompt[-300:]

        # “总结”问题应该覆盖更多上下文；普通问答按问题字符重合度选句。
        sentences = [
            item.strip(" -\n#")
            for item in re.split(r"(?<=[。！？.!?])\s+|\n+", context)
            if len(item.strip()) >= 8
        ]
        if not sentences:
            return "离线模型没有找到可抽取的上下文。"

        if any(word in question for word in ("总结", "概括", "summary")):
            selected = sentences[:4]
        else:
            query_chars = set(re.sub(r"[\W_]", "", question.lower()))
            ranked = sorted(
                sentences,
                key=lambda sentence: len(
                    query_chars & set(re.sub(r"[\W_]", "", sentence.lower()))
                ),
                reverse=True,
            )
            selected = ranked[:3]
        return "【离线抽取式回答】" + " ".join(selected)

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: object
    ) -> CompletionResponse:
        del formatted, kwargs
        return CompletionResponse(text=self._answer(prompt))

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: object
    ) -> Generator[CompletionResponse, None, None]:
        del formatted, kwargs
        answer = self._answer(prompt)
        accumulated = ""
        # 按字符流式返回，便于理解真实模型 Token 流的消费方式。
        for char in answer:
            accumulated += char
            yield CompletionResponse(text=accumulated, delta=char)
