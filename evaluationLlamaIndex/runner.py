"""LlamaIndex 原生 RAG 评估执行器。

本文件不重新实现 Hit Rate、MRR 或答案评分算法，而是把当前项目的 Retriever、
QueryEngine 接到 LlamaIndex 自带的 Evaluator 上：

* 检索：`RetrieverEvaluator` + `HitRate` + `MRR`；
* 生成：`CorrectnessEvaluator` + `FaithfulnessEvaluator` + `RelevancyEvaluator`；
* 批量：`BatchEvalRunner`。
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.response.schema import Response
from llama_index.core.evaluation import (
    BatchEvalRunner,
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    RetrieverEvaluator,
)
from llama_index.core.evaluation.base import EvaluationResult
from llama_index.core.evaluation.retrieval.base import RetrievalEvalResult
from llama_index.core.llms import LLM
from llama_index.core.retrievers import BaseRetriever

from .models import GoldenCase

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CaseResult:
    """单条问题的检索结果和生成评估结果。"""

    query: str
    expected_ids: list[str]
    retrieval: dict[str, Any] = field(default_factory=dict)
    generation: dict[str, Any] = field(default_factory=dict)
    response: str | None = None
    contexts: list[str] = field(default_factory=list)
    error: str | None = None
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """转换为 JSON 可序列化字典。"""

        return asdict(self)


@dataclass(slots=True)
class EvaluationReport:
    """完整评估报告，保留 LlamaIndex 原生结果的关键字段。"""

    created_at: str
    mode: str
    top_k: int
    workers: int
    case_count: int
    summary: dict[str, Any]
    cases: list[CaseResult]

    def to_dict(self) -> dict[str, Any]:
        """转换为字典，方便写文件或继续被其他程序消费。"""

        return {
            "created_at": self.created_at,
            "mode": self.mode,
            "top_k": self.top_k,
            "workers": self.workers,
            "case_count": self.case_count,
            "summary": self.summary,
            "cases": [case.to_dict() for case in self.cases],
        }

    def save(self, path: str | Path) -> None:
        """把报告保存为 UTF-8 JSON。"""

        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class LlamaIndexRAGEvaluator:
    """把一个 LlamaIndex Retriever/QueryEngine 接入内置评估能力。"""

    def __init__(
        self,
        retriever: BaseRetriever,
        *,
        query_engine: BaseQueryEngine | None = None,
        llm: LLM | None = None,
        top_k: int = 5,
        workers: int = 2,
    ) -> None:
        """初始化评估器。

        `retriever` 必须是 LlamaIndex BaseRetriever；`query_engine` 和 `llm` 在只做
        检索评估时可以省略。workers 只影响 BatchEvalRunner 的评审并发数。
        """

        if not isinstance(retriever, BaseRetriever):
            raise TypeError("retriever 必须是 LlamaIndex BaseRetriever")
        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")
        if workers <= 0:
            raise ValueError("workers 必须大于 0")
        # 真实生成模式需要两者；Demo 传入固定 Response 时只需要评审 LLM，
        # 因此允许 query_engine=None、llm 非空这一种特殊组合。
        if query_engine is not None and llm is None:
            raise ValueError("提供 query_engine 时必须同时提供 llm")
        self.retriever = retriever
        self.query_engine = query_engine
        self.llm = llm
        self.top_k = top_k
        self.workers = workers

    @classmethod
    def from_src(
        cls,
        index: Any,
        llm: LLM,
        *,
        top_k: int = 5,
        workers: int = 2,
        use_hybrid: bool = True,
    ) -> "LlamaIndexRAGEvaluator":
        """复用当前项目 src 的索引、QueryEngine 和模型构造真实评估器。"""

        from src.querying import make_engine

        retriever = index.as_retriever(similarity_top_k=top_k)
        query_engine = make_engine(
            index,
            llm,
            top_k=top_k,
            use_hybrid=use_hybrid,
        )
        return cls(
            retriever,
            query_engine=query_engine,
            llm=llm,
            top_k=top_k,
            workers=workers,
        )

    def evaluate(
        self,
        cases: Sequence[GoldenCase],
        *,
        retrieval_only: bool = False,
        responses: Sequence[Response] | None = None,
        mode: str = "real",
    ) -> EvaluationReport:
        """执行整批评估。

        正常真实模式使用 `BatchEvalRunner.evaluate_queries()` 自动调用 QueryEngine；
        本地 Demo 则传入固定 `responses`，改用 `evaluate_responses()`，仍然走同一套
        LlamaIndex Evaluator。批量失败时会自动退化为逐题执行，以保证单题异常不会
        让整批结果全部丢失。
        """

        case_list = list(cases)
        if not case_list:
            raise ValueError("评估问题集不能为空")
        if not retrieval_only and responses is None and self.query_engine is None:
            raise RuntimeError("生成评估需要 query_engine 和 llm；请使用真实模式或 --demo")
        if responses is not None and len(responses) != len(case_list):
            raise ValueError("responses 数量必须与黄金问题数量一致")

        results = [self._evaluate_retrieval(case) for case in case_list]
        if retrieval_only:
            return self._build_report(case_list, results, mode=mode)

        generation_results = self._evaluate_generation_batch(case_list, responses)
        for result, generation in zip(results, generation_results):
            if generation.get("error"):
                result.error = _merge_error(result.error, generation["error"])
            else:
                result.generation = generation.get("evaluations", {})
                result.response = generation.get("response")
                result.contexts = generation.get("contexts", [])
        return self._build_report(case_list, results, mode=mode)

    def _evaluate_retrieval(self, case: GoldenCase) -> CaseResult:
        """调用 LlamaIndex RetrieverEvaluator 计算 Hit Rate 和 MRR。"""

        started = time.perf_counter()
        result = CaseResult(query=case.query, expected_ids=list(case.expected_ids))
        try:
            if not case.expected_ids:
                raise ValueError(
                    "expected_ids 不能为空；请从 src/node JSON 中填写正确 Node ID"
                )
            evaluator = RetrieverEvaluator.from_metric_names(
                ["hit_rate", "mrr"],
                retriever=self.retriever,
            )
            retrieval_result: RetrievalEvalResult = evaluator.evaluate(
                query=case.query,
                expected_ids=case.expected_ids,
            )
            result.retrieval = {
                "metric_values": retrieval_result.metric_vals_dict,
                "retrieved_ids": retrieval_result.retrieved_ids,
                "retrieved_texts": retrieval_result.retrieved_texts,
            }
        except Exception as exc:  # noqa: BLE001 - 批量评估需要记录单题错误
            result.error = f"检索评估失败: {type(exc).__name__}: {exc}"
            logger.exception("检索评估失败: %s", case.query)
        result.latency_ms = round((time.perf_counter() - started) * 1000, 3)
        return result

    def _evaluate_generation_batch(
        self,
        cases: Sequence[GoldenCase],
        responses: Sequence[Response] | None,
    ) -> list[dict[str, Any]]:
        """用 BatchEvalRunner 批量执行三个原生生成评估器。"""

        evaluators = {
            "correctness": CorrectnessEvaluator(llm=self.llm),
            "faithfulness": FaithfulnessEvaluator(llm=self.llm),
            "relevancy": RelevancyEvaluator(llm=self.llm),
        }
        runner = BatchEvalRunner(
            evaluators=evaluators,
            workers=self.workers,
            show_progress=False,
        )
        queries = [case.query for case in cases]
        references = [case.reference_answer for case in cases]
        try:
            if responses is None:
                raw_results = runner.evaluate_queries(
                    self.query_engine,
                    queries=queries,
                    correctness={"reference": references},
                )
            else:
                raw_results = runner.evaluate_responses(
                    queries=queries,
                    responses=list(responses),
                    correctness={"reference": references},
                )
            return _format_generation_results(raw_results)
        except Exception as exc:  # noqa: BLE001 - 下面逐题重试以保留其他结果
            logger.warning("批量生成评估失败，将逐题重试: %s", exc)
            return self._evaluate_generation_one_by_one(cases, responses, runner)

    def _evaluate_generation_one_by_one(
        self,
        cases: Sequence[GoldenCase],
        responses: Sequence[Response] | None,
        runner: BatchEvalRunner,
    ) -> list[dict[str, Any]]:
        """批量异常时逐题调用 BatchEvalRunner，隔离单题网络或解析错误。"""

        output: list[dict[str, Any]] = []
        for index, case in enumerate(cases):
            try:
                if responses is None:
                    raw = runner.evaluate_queries(
                        self.query_engine,
                        queries=[case.query],
                        correctness={"reference": [case.reference_answer]},
                    )
                else:
                    raw = runner.evaluate_responses(
                        queries=[case.query],
                        responses=[responses[index]],
                        correctness={"reference": [case.reference_answer]},
                    )
                output.append(_format_generation_results(raw)[0])
            except Exception as exc:  # noqa: BLE001 - 保留其他问题结果
                output.append({"error": f"生成评估失败: {type(exc).__name__}: {exc}"})
                logger.exception("逐题生成评估失败: %s", case.query)
        return output

    def _build_report(
        self,
        cases: Sequence[GoldenCase],
        results: list[CaseResult],
        *,
        mode: str,
    ) -> EvaluationReport:
        """汇总原生 Evaluator 的 score/passing，并生成最终报告。"""

        valid = [result for result in results if not result.error]
        retrieval_values: dict[str, list[float]] = {}
        generation_values: dict[str, list[float]] = {}
        generation_passes: dict[str, list[float]] = {}
        for result in valid:
            for name, value in result.retrieval.get("metric_values", {}).items():
                if value is not None:
                    retrieval_values.setdefault(name, []).append(float(value))
            for name, evaluation in result.generation.items():
                score = evaluation.get("score")
                if score is not None:
                    generation_values.setdefault(name, []).append(float(score))
                passing = evaluation.get("passing")
                if passing is not None:
                    generation_passes.setdefault(name, []).append(1.0 if passing else 0.0)

        generation_summary: dict[str, Any] = {}
        for name, values in generation_values.items():
            generation_summary[name] = {
                "average_score": round(sum(values) / len(values), 6),
                "evaluated_count": len(values),
                "passing_rate": round(
                    sum(generation_passes.get(name, [])) / len(generation_passes[name]),
                    6,
                )
                if generation_passes.get(name)
                else None,
            }

        summary = {
            "successful_case_count": len(valid),
            "failed_case_count": len(results) - len(valid),
            "retrieval": {
                name: round(sum(values) / len(values), 6)
                for name, values in retrieval_values.items()
            },
            "generation": generation_summary,
        }
        return EvaluationReport(
            created_at=datetime.now(timezone.utc).isoformat(),
            mode=mode,
            top_k=self.top_k,
            workers=self.workers,
            case_count=len(cases),
            summary=summary,
            cases=results,
        )


def _format_generation_results(raw_results: dict[str, list[EvaluationResult]]) -> list[dict[str, Any]]:
    """把 BatchEvalRunner 的按评估器分组结果还原为按问题分组。"""

    names = list(raw_results)
    count = max((len(values) for values in raw_results.values()), default=0)
    formatted: list[dict[str, Any]] = []
    for index in range(count):
        evaluations: dict[str, Any] = {}
        response: str | None = None
        contexts: list[str] = []
        for name in names:
            values = raw_results.get(name, [])
            if index >= len(values):
                continue
            evaluation = values[index]
            evaluations[name] = _evaluation_to_dict(evaluation)
            response = response or evaluation.response
            if not contexts and evaluation.contexts:
                contexts = [str(context) for context in evaluation.contexts]
        formatted.append(
            {
                "evaluations": evaluations,
                "response": response,
                "contexts": contexts,
            }
        )
    return formatted


def _evaluation_to_dict(result: EvaluationResult) -> dict[str, Any]:
    """仅保留 EvaluationResult 的稳定公开字段，避免写入 Pydantic 内部状态。"""

    return {
        "query": result.query,
        "response": result.response,
        "contexts": list(result.contexts) if result.contexts else None,
        "score": result.score,
        "passing": result.passing,
        "feedback": result.feedback,
        "invalid_result": result.invalid_result,
        "invalid_reason": result.invalid_reason,
    }


def _merge_error(old: str | None, new: str) -> str:
    """合并同一问题的检索和生成错误，避免丢失首个失败原因。"""

    return f"{old}; {new}" if old else new
