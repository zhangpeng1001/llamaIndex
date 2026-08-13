"""一个容易读懂的检索评估示例。

生产环境可以使用 LlamaIndex 的评估器或专门平台；这里手写 Hit Rate 与 MRR，
帮助初学者先理解指标在衡量什么，再学习自动化评估框架。
"""

from __future__ import annotations

from dataclasses import dataclass

from llama_index.core import VectorStoreIndex

from .rag import retrieve


@dataclass(frozen=True)
class EvaluationCase:
    question: str
    expected_file: str


# 小型“黄金问题集”：每个问题预先标记应该命中的文档。
DEFAULT_CASES = [
    EvaluationCase("Document 和 Node 有什么关系？", "01_llamaindex_basics.md"),
    EvaluationCase("Top-K 太大会有什么问题？", "02_rag_practice.md"),
    EvaluationCase("星河项目代号是什么？", "03_project_handbook.md"),
    EvaluationCase("知识库什么时候做全量同步？", "03_project_handbook.md"),
]


def evaluate_retriever(
    index: VectorStoreIndex,
    cases: list[EvaluationCase] | None = None,
    *,
    top_k: int = 3,
) -> dict[str, object]:
    """计算 Hit Rate 与 Mean Reciprocal Rank。

    Hit Rate：正确文档是否出现在 Top-K 中。
    MRR：正确文档排名越靠前得分越高；第一名为 1，第二名为 1/2。
    """

    selected_cases = cases or DEFAULT_CASES
    details: list[dict[str, object]] = []
    hits = 0
    reciprocal_rank_sum = 0.0

    for case in selected_cases:
        results = retrieve(index, case.question, top_k=top_k)
        retrieved_files = [
            str(item.node.metadata.get("file_name", "")) for item in results
        ]
        try:
            # list.index 从 0 开始，指标中的排名从 1 开始。
            rank = retrieved_files.index(case.expected_file) + 1
        except ValueError:
            rank = None
        if rank is not None:
            hits += 1
            reciprocal_rank_sum += 1.0 / rank
        details.append(
            {
                "question": case.question,
                "expected": case.expected_file,
                "retrieved": retrieved_files,
                "rank": rank,
            }
        )

    count = len(selected_cases)
    return {
        "hit_rate": hits / count if count else 0.0,
        "mrr": reciprocal_rank_sum / count if count else 0.0,
        "top_k": top_k,
        "details": details,
    }

