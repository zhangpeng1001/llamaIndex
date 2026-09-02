"""评估数据模型。

这里故意使用标准库 `dataclasses`，不把评估模块和 FastAPI、LlamaIndex 的具体对象绑死。
这样既能评估真实 RAG，也能在没有启动 Milvus 的情况下，用假的检索函数做单元测试。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EvaluationCase:
    """一条黄金问题（golden case）。

    参数说明：
        question: 发给 RAG 系统的用户问题，不能为空。
        relevant_files: 认为应该被召回的源文件名，例如 `part2_检测点.md`。
        relevant_keywords: 期望在上下文或答案中出现的业务关键词。
        reference_answer: 可选的人工参考答案；Demo 默认用关键词覆盖率，
            不强行做字符串完全相等，避免同义表达被误判。
        expected_node_ids: 可选的精确 Node ID，适合已经固定切块结果的回归测试。
        tags: 便于按业务主题筛选问题的标签。
        metadata: 预留的扩展字段，不参与默认评分。
    """

    question: str
    relevant_files: list[str] = field(default_factory=list)
    relevant_keywords: list[str] = field(default_factory=list)
    reference_answer: str | None = None
    expected_node_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """校验并规范化输入，尽早发现黄金数据配置错误。"""

        self.question = str(self.question).strip()
        if not self.question:
            raise ValueError("EvaluationCase.question 不能为空")
        # 去重但保持原顺序，避免同一关键词重复计算导致分数虚高。
        self.relevant_files = _unique_strings(self.relevant_files)
        self.relevant_keywords = _unique_strings(self.relevant_keywords)
        self.expected_node_ids = _unique_strings(self.expected_node_ids)
        self.tags = _unique_strings(self.tags)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationCase":
        """从 JSON 字典创建评估问题，并对缺省字段使用空列表。"""

        if not isinstance(data, dict):
            raise TypeError("每条评估问题必须是 JSON 对象")
        return cls(
            question=data.get("question", ""),
            relevant_files=data.get("relevant_files", []),
            relevant_keywords=data.get("relevant_keywords", []),
            reference_answer=data.get("reference_answer"),
            expected_node_ids=data.get("expected_node_ids", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为可直接写入 JSON 的字典。"""

        return {
            "question": self.question,
            "relevant_files": list(self.relevant_files),
            "relevant_keywords": list(self.relevant_keywords),
            "reference_answer": self.reference_answer,
            "expected_node_ids": list(self.expected_node_ids),
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }


def _unique_strings(values: Any) -> list[str]:
    """把用户配置的字符串列表去重并清理空白值。"""

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
