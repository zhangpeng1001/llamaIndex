"""RAG 评估执行器。

执行器只约定两个非常小的函数接口：

* retriever(question, top_k) -> 节点序列；
* answerer(question, top_k) -> 字符串、LlamaIndex Response，或包含 answer/source_nodes 的字典。

因此它既可以连接真实 `src` 服务，也可以用几行代码接入其他 RAG 实现。
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from .metrics import aggregate_metric_dicts, generation_metrics, join_context, retrieval_metrics
from .models import EvaluationCase

logger = logging.getLogger(__name__)

Retriever = Callable[[str, int], Sequence[Any]]
Answerer = Callable[[str, int], Any]


@dataclass(slots=True)
class CaseResult:
    """单条评估问题的结果，保留明细便于定位失败样本。"""

    question: str
    retrieval: dict[str, Any]
    generation: dict[str, Any] = field(default_factory=dict)
    answer: str | None = None
    retrieved_sources: list[str] = field(default_factory=list)
    error: str | None = None
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """转换为可序列化字典。"""

        return asdict(self)


@dataclass(slots=True)
class EvaluationReport:
    """整批评估报告，包含汇总指标和每题明细。"""

    created_at: str
    top_k: int
    case_count: int
    summary: dict[str, Any]
    cases: list[CaseResult]
    retrieval_only: bool = False

    def to_dict(self) -> dict[str, Any]:
        """转换为 JSON 结构，并把 dataclass 明细展开。"""

        return {
            "created_at": self.created_at,
            "top_k": self.top_k,
            "case_count": self.case_count,
            "retrieval_only": self.retrieval_only,
            "summary": self.summary,
            "cases": [case.to_dict() for case in self.cases],
        }

    def save(self, path: str | Path) -> None:
        """保存评估报告到 JSON 文件。"""

        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class RAGEvaluator:
    """使用注入的检索/生成函数执行 RAG 评估。"""

    def __init__(self, retriever: Retriever, answerer: Answerer | None = None) -> None:
        """初始化执行器；retriever 是必需的，answerer 可选以支持只评估检索。"""

        if not callable(retriever):
            raise TypeError("retriever 必须是可调用对象")
        if answerer is not None and not callable(answerer):
            raise TypeError("answerer 必须是可调用对象或 None")
        self.retriever = retriever
        self.answerer = answerer

    @classmethod
    def from_src(cls, index: Any, llm: Any | None = None, *, use_hybrid: bool = True) -> "RAGEvaluator":
        """把当前项目 `src` 的 VectorStoreIndex 封装成评估器。

        导入放在函数内部，避免用户只使用离线指标时必须先安装/连接 Milvus。
        """

        from src.querying import make_engine, run_querying

        def retrieve(question: str, top_k: int) -> Sequence[Any]:
            """调用项目已有的 Hybrid 检索链路。"""

            return run_querying(index, question, top_k=top_k, use_hybrid=use_hybrid)

        answerer: Answerer | None = None
        if llm is not None:
            def answer(question: str, top_k: int) -> Any:
                """调用项目已有 QueryEngine，保留 source_nodes 用于答案支撑分析。"""

                engine = make_engine(index, llm, top_k=top_k, use_hybrid=use_hybrid)
                return engine.query(question)

            answerer = answer
        return cls(retrieve, answerer)

    def evaluate(self, cases: Iterable[EvaluationCase], *, top_k: int = 5, retrieval_only: bool = False) -> EvaluationReport:
        """逐题执行评估并生成报告。

        单题失败会记录在 `CaseResult.error` 中并继续后续题目；这样批量评估不会因为
        某道问题的网络抖动而丢失已经完成的结果。最终汇总只对成功结果求平均。
        """

        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")
        case_list = list(cases)
        results: list[CaseResult] = []
        for case in case_list:
            results.append(self.evaluate_case(case, top_k=top_k, retrieval_only=retrieval_only))

        successful = [result for result in results if not result.error]
        retrieval_rows = [result.retrieval for result in successful]
        generation_rows = [result.generation for result in successful if result.generation]
        summary: dict[str, Any] = {
            "retrieval": aggregate_metric_dicts(retrieval_rows),
            "generation": aggregate_metric_dicts(generation_rows) if generation_rows else {"case_count": 0},
            "failed_case_count": len(results) - len(successful),
        }
        return EvaluationReport(
            created_at=datetime.now(timezone.utc).isoformat(),
            top_k=top_k,
            case_count=len(case_list),
            summary=summary,
            cases=results,
            retrieval_only=retrieval_only or self.answerer is None,
        )

    def evaluate_case(self, case: EvaluationCase, *, top_k: int, retrieval_only: bool = False) -> CaseResult:
        """评估单条问题，记录检索、答案、来源和耗时。"""

        started = time.perf_counter()
        try:
            nodes = list(self.retriever(case.question, top_k))
            retrieval = retrieval_metrics(nodes, case, top_k)
            answer: str | None = None
            answer_nodes = nodes
            generation: dict[str, Any] = {}

            if self.answerer is not None and not retrieval_only:
                raw_answer = self.answerer(case.question, top_k)
                answer, answer_nodes = _parse_answer_result(raw_answer, fallback_nodes=nodes)
                generation = generation_metrics(answer, join_context(answer_nodes), case)

            sources = []
            for item in nodes[:top_k]:
                from .metrics import source_file

                source = source_file(item)
                if source and source not in sources:
                    sources.append(source)
            return CaseResult(
                question=case.question,
                retrieval=retrieval,
                generation=generation,
                answer=answer,
                retrieved_sources=sources,
                latency_ms=round((time.perf_counter() - started) * 1000, 3),
            )
        except Exception as exc:  # noqa: BLE001 - 评估批处理需要记录并继续
            logger.exception("评估问题失败: %s", case.question)
            return CaseResult(
                question=case.question,
                retrieval={},
                error=f"{type(exc).__name__}: {exc}",
                latency_ms=round((time.perf_counter() - started) * 1000, 3),
            )


def _parse_answer_result(raw: Any, *, fallback_nodes: Sequence[Any]) -> tuple[str, Sequence[Any]]:
    """兼容字符串、LlamaIndex Response 和字典三种答案返回形式。"""

    if isinstance(raw, dict):
        answer = raw.get("answer", raw.get("response", ""))
        nodes = raw.get("source_nodes") or raw.get("sources") or fallback_nodes
        return str(answer or ""), list(nodes)
    answer = getattr(raw, "response", None)
    if answer is None:
        answer = str(raw or "")
    nodes = getattr(raw, "source_nodes", None) or fallback_nodes
    return str(answer), list(nodes)
