"""黄金问题的数据模型。

LlamaIndex 的 RetrieverEvaluator 使用 `expected_ids` 判断检索结果是否命中，
因此这里不使用文件名或自定义关键词代替 Node ID。Node ID 来自 Indexing 阶段的
真实 Node JSON；如果重新切块生成了新 ID，需要重新维护黄金集。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class GoldenCase:
    """一条用于回归测试的黄金问题。

    参数：
        query: 发送给 RAG QueryEngine 的问题。
        expected_ids: 该问题预期召回的 Node ID，供 RetrieverEvaluator 使用。
        reference_answer: 人工参考答案，供 CorrectnessEvaluator 使用；只做生成评估时必填。
        tags: 业务标签，便于人工筛选问题。
        metadata: 预留扩展字段，不会被 LlamaIndex Evaluator 直接使用。
    """

    query: str
    expected_ids: list[str] = field(default_factory=list)
    reference_answer: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """清理字符串并去重，避免同一个 Node ID 重复计算。"""

        self.query = str(self.query).strip()
        if not self.query:
            raise ValueError("黄金问题 query 不能为空")
        self.expected_ids = _clean_unique(self.expected_ids)
        self.tags = _clean_unique(self.tags)
        if self.reference_answer is not None:
            self.reference_answer = str(self.reference_answer).strip() or None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GoldenCase":
        """从 JSON 对象创建黄金问题，并对关键字段做明确校验。"""

        if not isinstance(data, dict):
            raise TypeError("每条黄金问题必须是 JSON 对象")
        if not data.get("expected_ids"):
            raise ValueError(
                "黄金问题缺少 expected_ids；RetrieverEvaluator 必须知道正确 Node ID"
            )
        return cls(
            query=data.get("query", ""),
            expected_ids=data.get("expected_ids", []),
            reference_answer=data.get("reference_answer"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为可写入 JSON 的普通字典。"""

        return {
            "query": self.query,
            "expected_ids": list(self.expected_ids),
            "reference_answer": self.reference_answer,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }


def _clean_unique(values: Any) -> list[str]:
    """清理列表中的空值并保持顺序去重。"""

    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in result:
            result.append(text)
    return result
