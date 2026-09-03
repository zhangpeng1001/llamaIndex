"""LlamaIndex 内置 Evaluator 的离线测试。

测试只使用 evaluationLlamaIndex.demo 中的内存节点和确定性评审 LLM，
不会连接 Milvus，也不会调用 OpenAI/Ollama。
"""

from __future__ import annotations

import json

import pytest

from evaluationLlamaIndex.dataset import load_cases, save_cases
from evaluationLlamaIndex.demo import build_demo_evaluator
from evaluationLlamaIndex.models import GoldenCase
from evaluationLlamaIndex.runner import LlamaIndexRAGEvaluator


def test_dataset_round_trip(tmp_path):
    """黄金集可以保存并再次加载，且关键字段保持不变。"""

    path = tmp_path / "cases.json"
    cases = [
        GoldenCase(
            query="测试问题",
            expected_ids=["node-1"],
            reference_answer="测试答案",
        )
    ]
    save_cases(cases, path)
    loaded = load_cases(path)
    assert loaded[0].query == "测试问题"
    assert loaded[0].expected_ids == ["node-1"]
    assert loaded[0].reference_answer == "测试答案"


def test_missing_expected_ids_is_explicit_error(tmp_path):
    """缺少 expected_ids 时必须给出面向学习者的明确错误。"""

    path = tmp_path / "bad.json"
    path.write_text(json.dumps([{"query": "没有标注"}], ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError, match="expected_ids"):
        load_cases(path)


def test_demo_uses_builtin_retrieval_and_generation_evaluators(tmp_path):
    """Demo 能完成 RetrieverEvaluator + BatchEvalRunner 的完整流程。"""

    evaluator, cases, responses = build_demo_evaluator()
    report = evaluator.evaluate(cases, responses=responses, mode="demo")
    assert report.summary["failed_case_count"] == 0
    assert report.summary["retrieval"]["hit_rate"] == 1.0
    assert report.summary["retrieval"]["mrr"] == 1.0
    assert report.summary["generation"]["correctness"]["average_score"] == 5.0
    assert report.summary["generation"]["faithfulness"]["passing_rate"] == 1.0
    report_path = tmp_path / "report.json"
    report.save(report_path)
    assert json.loads(report_path.read_text(encoding="utf-8"))["mode"] == "demo"


def test_retrieval_only_keeps_going_after_one_bad_case():
    """单条 expected_ids 错误只影响当前问题，不阻断其他问题。"""

    evaluator, cases, _ = build_demo_evaluator()
    bad_case = GoldenCase(query="错误标注", expected_ids=[])
    report = evaluator.evaluate([cases[0], bad_case], retrieval_only=True)
    assert report.summary["successful_case_count"] == 1
    assert report.summary["failed_case_count"] == 1
    assert "expected_ids" in report.cases[1].error
