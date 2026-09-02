"""RAG 评估指标。

指标分为两类：

* 检索指标：Hit Rate、MRR、Precision@K、Recall@K；
* 生成指标：关键词覆盖率、上下文支撑率、答案非空率。

这里不调用另一个 LLM 充当裁判，因此结果可重复、成本低，也不会把“评估模型的
主观判断”误认为客观事实。关键词指标是 Demo 级的可解释启发式指标，生产环境可
在此基础上接入人工标注或独立评估模型。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


def node_text(item: Any) -> str:
    """提取 LlamaIndex NodeWithScore、Node、字典或字符串中的正文。"""

    node = getattr(item, "node", item)
    get_content = getattr(node, "get_content", None)
    if callable(get_content):
        return str(get_content() or "")
    if isinstance(node, Mapping):
        for key in ("text", "content", "node_text"):
            if node.get(key) is not None:
                return str(node[key])
    return str(node or "")


def node_metadata(item: Any) -> dict[str, Any]:
    """提取节点 metadata；缺失时返回空字典，保证评估不中断。"""

    node = getattr(item, "node", item)
    metadata = getattr(node, "metadata", None)
    if metadata is None and isinstance(node, Mapping):
        metadata = node.get("metadata")
    return dict(metadata or {})


def node_id(item: Any) -> str | None:
    """提取节点 ID，用于需要精确回归的黄金集。"""

    node = getattr(item, "node", item)
    value = getattr(node, "node_id", None)
    if value is None and isinstance(node, Mapping):
        value = node.get("node_id") or node.get("id")
    return str(value) if value is not None else None


def source_file(item: Any) -> str:
    """提取源文件名，并统一为 basename，兼容 file_path 的绝对路径。"""

    metadata = node_metadata(item)
    value = metadata.get("file_name") or metadata.get("source_file") or metadata.get("file_path")
    if not value:
        return ""
    return str(value).replace("\\", "/").rsplit("/", 1)[-1]


def is_relevant(item: Any, case: Any) -> bool:
    """判断一个召回节点是否与黄金问题相关。

    优先使用 node_id 和源文件精确匹配；如果黄金集没有文件标注，则用关键词命中
    作为可解释兜底。这样既能做严格回归，也能快速构造 Demo 黄金集。
    """

    expected_ids = set(getattr(case, "expected_node_ids", []) or [])
    current_id = node_id(item)
    if expected_ids and current_id in expected_ids:
        return True

    expected_files = {
        str(name).replace("\\", "/").rsplit("/", 1)[-1].casefold()
        for name in (getattr(case, "relevant_files", []) or [])
    }
    current_file = source_file(item)
    if expected_files:
        # 黄金集明确标注了源文件时，优先采用严格文件匹配；否则一个“质量要求”等
        # 通用词出现在其他规范中，也会把噪声节点误判为相关节点，导致 Precision 虚高。
        # 只有节点没有任何来源信息时，才允许继续使用关键词兜底。
        if current_file:
            return current_file.casefold() in expected_files

    keywords = getattr(case, "relevant_keywords", []) or []
    text = node_text(item).casefold()
    return bool(keywords) and any(str(keyword).casefold() in text for keyword in keywords)


def retrieval_metrics(nodes: Iterable[Any], case: Any, top_k: int | None = None) -> dict[str, float | int | None]:
    """计算单题检索质量指标。

    `recall_at_k` 在黄金集标注了多个 relevant_files 时按文件数计算；只有关键词或
    单文件标注时，它退化为 0/1 命中值，避免凭空猜测“应该召回多少个节点”。
    """

    items = list(nodes)
    k = max(1, int(top_k or len(items) or 1))
    ranked = items[:k]
    flags = [is_relevant(item, case) for item in ranked]
    ranks = [index + 1 for index, flag in enumerate(flags) if flag]
    first_rank = ranks[0] if ranks else None

    expected_files = {
        str(name).replace("\\", "/").rsplit("/", 1)[-1].casefold()
        for name in (getattr(case, "relevant_files", []) or [])
    }
    found_files = {source_file(item).casefold() for item, flag in zip(ranked, flags) if flag and source_file(item)}
    if len(expected_files) > 1:
        recall = len(expected_files & found_files) / len(expected_files)
    else:
        recall = 1.0 if first_rank is not None else 0.0

    return {
        "hit_rate_at_k": 1.0 if first_rank is not None else 0.0,
        "mrr_at_k": 1.0 / first_rank if first_rank is not None else 0.0,
        "precision_at_k": sum(flags) / k,
        "recall_at_k": recall,
        "first_relevant_rank": first_rank,
        "retrieved_count": len(ranked),
        "relevant_count": sum(flags),
    }


def keyword_coverage(text: str, keywords: Iterable[str]) -> float:
    """计算关键词覆盖率：命中的关键词数 / 标注关键词总数。"""

    values = [str(keyword).strip() for keyword in keywords if str(keyword).strip()]
    if not values:
        return 0.0
    normalized = str(text or "").casefold()
    return sum(1 for keyword in values if keyword.casefold() in normalized) / len(values)


def generation_metrics(answer: str | None, context: str, case: Any) -> dict[str, float | int]:
    """计算单题答案的可解释启发式指标。"""

    answer_text = str(answer or "").strip()
    keywords = getattr(case, "relevant_keywords", []) or []
    expected = [str(keyword) for keyword in keywords if str(keyword).strip()]
    answer_hits = [keyword for keyword in expected if keyword.casefold() in answer_text.casefold()]
    context_hits = [keyword for keyword in expected if keyword.casefold() in str(context or "").casefold()]
    answer_set = set(answer_hits)
    supported = sum(1 for keyword in answer_set if keyword in context_hits)

    return {
        "answer_non_empty": 1 if answer_text else 0,
        "answer_keyword_coverage": len(answer_hits) / len(expected) if expected else 0.0,
        "context_keyword_coverage": len(context_hits) / len(expected) if expected else 0.0,
        # 只在答案确实提到标注关键词时计算支撑率；答案没有关键词时记 0，避免空答案得高分。
        "answer_grounded_keyword_rate": supported / len(answer_set) if answer_set else 0.0,
        "answer_char_count": len(answer_text),
    }


def aggregate_metric_dicts(metric_dicts: Iterable[Mapping[str, Any]]) -> dict[str, float | int]:
    """对多道题的数值指标求平均；rank/count 等字段也保留平均值便于观察。"""

    rows = list(metric_dicts)
    if not rows:
        return {"case_count": 0}
    keys = sorted({key for row in rows for key, value in row.items() if isinstance(value, (int, float))})
    result: dict[str, float | int] = {"case_count": len(rows)}
    for key in keys:
        result[key] = round(sum(float(row.get(key, 0) or 0) for row in rows) / len(rows), 6)
    return result


def join_context(nodes: Iterable[Any]) -> str:
    """把召回节点拼接为生成评估使用的上下文文本。"""

    return "\n\n".join(node_text(item) for item in nodes if node_text(item).strip())
