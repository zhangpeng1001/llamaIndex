"""RAG 评估模块。

本包提供一套不依赖额外评估平台的轻量评估工具，直接复用项目现有的
`src.querying.run_querying` 和 `src.querying.make_engine`，便于 Demo 学习和后续扩展。
"""

from .dataset import default_cases, load_cases, save_cases
from .evaluator import EvaluationReport, RAGEvaluator
from .models import EvaluationCase

__all__ = [
    "EvaluationCase",
    "EvaluationReport",
    "RAGEvaluator",
    "default_cases",
    "load_cases",
    "save_cases",
]
