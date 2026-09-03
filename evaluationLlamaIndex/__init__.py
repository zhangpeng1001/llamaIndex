"""基于 LlamaIndex 内置 Evaluator 的 RAG 评估示例包。

本包刻意保留 LlamaIndex 原生对象（EvaluationResult、RetrievalEvalResult），
让学习者可以直接对照官方 API 阅读评估流程，而不是重新实现一套指标。
"""

from .dataset import default_cases, load_cases, save_cases
from .models import GoldenCase
from .runner import EvaluationReport, LlamaIndexRAGEvaluator

__all__ = [
    "EvaluationReport",
    "GoldenCase",
    "LlamaIndexRAGEvaluator",
    "default_cases",
    "load_cases",
    "save_cases",
]
