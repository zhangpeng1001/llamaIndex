"""无外部服务的 LlamaIndex Evaluator 演示。

Demo 不声称评估真实模型质量，它只构造最小的内存 Retriever、Response 和确定性
评审 LLM，让学习者看到 LlamaIndex 原生 Evaluator 的输入输出格式以及 BatchEvalRunner
的调用方式。真实项目请使用 `cli.py` 的默认模式。
"""

from __future__ import annotations

from typing import Any, Sequence

from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.base.llms.types import CompletionResponse, LLMMetadata
from llama_index.core.base.response.schema import Response
from llama_index.core.llms import CustomLLM
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode

from .models import GoldenCase
from .runner import LlamaIndexRAGEvaluator


class DemoRetriever(BaseRetriever):
    """按简单关键词重排内存节点，模拟一个可被评估的 Retriever。"""

    def __init__(self, nodes: Sequence[TextNode]) -> None:
        super().__init__()
        self.nodes = list(nodes)

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        """根据 query 与节点正文的字符重合数排序，返回 NodeWithScore。"""

        query = query_bundle.query_str.casefold()
        scored = []
        for node in self.nodes:
            text = node.get_content().casefold()
            score = float(sum(1 for char in set(query) if char.strip() and char in text))
            scored.append(NodeWithScore(node=node, score=score))
        return sorted(scored, key=lambda item: item.score or 0.0, reverse=True)


class DemoJudgeLLM(CustomLLM):
    """返回固定合法格式的评审结果，避免 Demo 依赖网络模型。"""

    @classmethod
    def class_name(cls) -> str:
        """返回 LlamaIndex 序列化所需的类名。"""

        return "DemoJudgeLLM"

    @property
    def metadata(self) -> LLMMetadata:
        """声明一个最小 LLM 元数据对象。"""

        return LLMMetadata(num_output=64, model_name="demo-judge")

    def complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        """识别三类内置评估提示，并返回可被官方解析器读取的结果。"""

        del formatted, kwargs
        lowered = prompt.casefold()
        if "generated answer" in lowered or "reference answer" in lowered:
            text = "5.0\nDemo 评审：答案与参考答案一致。"
        else:
            # Faithfulness/Relevancy 默认要求 YES/NO；固定返回 YES 只是为了演示格式。
            text = "YES"
        return CompletionResponse(text=text)

    def stream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any):
        """Demo 不需要流式评估，使用一个简单生成器满足 CustomLLM 接口。"""

        response = self.complete(prompt, formatted=formatted, **kwargs)
        yield response


def build_demo_evaluator() -> tuple[LlamaIndexRAGEvaluator, list[GoldenCase], list[Response]]:
    """构造内存节点、黄金问题和固定 Response。"""

    nodes = [
        TextNode(
            id_="demo-node-support-repository",
            text="质检支撑库是基于统一数据架构构建的专用数据库系统，支持查询检索和数据评估。",
        ),
        TextNode(
            id_="demo-node-resource-data",
            text="资源数据由数据体及元数据组成，数据体按文件存储，元数据记录数据说明和数据集范围。",
        ),
    ]
    cases = [
        GoldenCase(
            query="什么是质检支撑库？",
            expected_ids=["demo-node-support-repository"],
            reference_answer="质检支撑库是基于统一数据架构构建的专用数据库系统，支持查询检索和数据评估。",
        ),
        GoldenCase(
            query="资源数据由什么组成？",
            expected_ids=["demo-node-resource-data"],
            reference_answer="资源数据由数据体及元数据组成。",
        ),
    ]
    responses = [
        Response(
            response=case.reference_answer or "",
            source_nodes=[NodeWithScore(node=node, score=1.0)],
        )
        for case, node in zip(cases, nodes)
    ]
    evaluator = LlamaIndexRAGEvaluator(
        DemoRetriever(nodes),
        query_engine=None,
        llm=DemoJudgeLLM(),
        top_k=2,
        workers=1,
    )
    return evaluator, cases, responses
