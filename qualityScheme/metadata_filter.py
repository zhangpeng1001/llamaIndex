"""增强版元数据过滤 + Hybrid 检索模块。

相对原版的改进：
    1. 支持 8+ 业务字段过滤：part_number / knowledge_type / data_name / doc_type /
       chapter_no / section_type / check_code / is_table。
       （GPT 文档第 9 节强调的「先 Metadata Filter 缩小候选，再向量检索」）
    2. 修正 retrieve_by_part：不再 TopK*5 再内存过滤，直接用 ExactMatchFilter(key="part_number")
       在 Milvus 侧完成过滤，精确且高效。
    3. 新增 Hybrid 检索开关：vector_store_query_mode="hybrid" = Dense + BM25 Sparse 混合。
       （GPT 文档第 10 节，解决编号/代号/阈值类纯向量不准的问题）
    4. 新增两个专用便捷函数：
       - retrieve_check_items：只在检查项字典（doc_type=check_item）里检索，取 TopN 候选项
       - retrieve_quality_spec：只在真实规范 part1~7 里检索，自动排除检查项字典和噪声

学习要点：
    - MetadataFilters 支持 AND/OR 组合（FilterCondition），可以同时指定 part_number
      和 knowledge_type，实现"只查第2部分质量规则"这种强约束。
    - Milvus 支持的 scalar 字段必须是字符串/整数/布尔。列表类型 metadata 需要在
      入库时序列化为 ", " 连接的字符串，再用 ExactMatchFilter（或将来用自定义
      filter）做子串匹配。
    - Hybrid 检索效果的前提是 Sparse BM25 向量也要正确入库；LlamaIndex 的
      MilvusVectorStore 在 hybrid 模式下会自动处理 sparse 向量的计算与存储。

业务背景：
    质检方案生成时，典型查询模式是「分两步检索」：
        Step A：用户需求 → 只检索 doc_type=check_item → Top3 候选检查项
        Step B：每个子意图 → 过滤 data_name=检测点 + knowledge_type=quality_rule
                 → 检索规范条款作为参数推断上下文
    如果没有精细化 Metadata Filter，两步都会混进大量无关 Chunk。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.core.vector_stores import (
    ExactMatchFilter,
    FilterCondition,
    MetadataFilters,
)

from .check_items_indexer import (
    CHECK_ITEM_DOC_TYPE,
    CHECK_ITEM_PART_NUMBER,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 检索过滤条件对象（结构化替代原始单个 file_name 参数）
# ---------------------------------------------------------------------------


@dataclass
class RetrievalFilters:
    """结构化检索过滤条件。

    所有字段均可选；None 表示不限制。
    多个字段之间默认 AND 组合。
    """

    file_name: str | None = None
    part_number: int | None = None
    knowledge_type: str | None = None
    data_name: str | None = None  # 精确匹配 part_name 子串（", "分割后包含）
    doc_type: str | None = None  # "data_spec" / "check_item" / None(全部)
    section_type: str | None = None
    chapter_no: str | None = None
    check_code: str | None = None
    exclude_noise: bool = True  # 默认排除 is_noise=true 的节点
    only_check_items: bool = False  # 便捷：只查检查项字典
    only_spec_docs: bool = False  # 便捷：只查真实规范（排除检查项）
    extra: dict[str, Any] = field(default_factory=dict)

    def build_llamaindex_filters(self) -> MetadataFilters | None:
        """构造 LlamaIndex MetadataFilters 对象。"""
        filters: list[Any] = []

        if self.only_check_items:
            filters.append(ExactMatchFilter(key="doc_type", value=CHECK_ITEM_DOC_TYPE))
            filters.append(ExactMatchFilter(key="part_number", value=CHECK_ITEM_PART_NUMBER))
        elif self.only_spec_docs:
            # 排除检查项 part_number=0
            # 注意：Milvus 的 MetadataFilters 不等于关系很复杂，这里改用手动后过滤兜底
            # + doc_type 存在且不等于 check_item 的过滤
            pass

        if self.file_name:
            filters.append(ExactMatchFilter(key="file_name", value=self.file_name))
        if self.part_number is not None and not self.only_check_items:
            filters.append(ExactMatchFilter(key="part_number", value=self.part_number))
        if self.knowledge_type:
            filters.append(ExactMatchFilter(key="knowledge_type", value=self.knowledge_type))
        if self.doc_type and not self.only_check_items:
            filters.append(ExactMatchFilter(key="doc_type", value=self.doc_type))
        if self.section_type:
            filters.append(ExactMatchFilter(key="section_type", value=self.section_type))
        if self.chapter_no:
            filters.append(ExactMatchFilter(key="chapter_no", value=self.chapter_no))
        if self.check_code:
            filters.append(ExactMatchFilter(key="check_code", value=self.check_code))

        if not filters:
            return None
        return MetadataFilters(filters=filters, condition=FilterCondition.AND)

    def post_filter(self, nodes: list[NodeWithScore]) -> list[NodeWithScore]:
        """Milvus 侧过滤后的再补充过滤（解决不支持 NOT 条件 / 字符串包含的问题）。"""
        result: list[NodeWithScore] = []
        for n in nodes:
            meta = n.node.metadata or {}

            # 1. exclude_noise: 跳过噪声行
            if self.exclude_noise and meta.get("is_noise") in (True, "true", "True"):
                continue

            # 2. only_spec_docs: 排除检查项 part_number=0
            if self.only_spec_docs:
                if meta.get("part_number") == CHECK_ITEM_PART_NUMBER or meta.get("doc_type") == CHECK_ITEM_DOC_TYPE:
                    continue

            # 3. data_name: "检测点, 检测线" 字符串包含匹配（因为序列化是逗号分隔）
            if self.data_name:
                data_name_field = str(meta.get("data_name", ""))
                if self.data_name not in data_name_field:
                    continue

            result.append(n)
        return result


# ---------------------------------------------------------------------------
# 核心检索函数
# ---------------------------------------------------------------------------


def retrieve(
    index: VectorStoreIndex,
    question: str,
    *,
    top_k: int = 5,
    file_name: str | None = None,
    filters: RetrievalFilters | None = None,
    use_hybrid: bool = True,  # 默认启用 Hybrid Search（Dense + BM25）
) -> list[NodeWithScore]:
    """执行向量检索（支持 Metadata Filter + 可选 Hybrid）。

    参数:
        index: 向量索引
        question: 查询文本
        top_k: 返回节点数（注意：Milvus侧返回top_k后，还会经过post_filter，
               最终节点数可能小于top_k；内部会自动取 top_k * 1.5 缓冲以避免不足）
        file_name: 便捷参数，等价于 filters=RetrievalFilters(file_name=...)
        filters: 结构化过滤条件（推荐用这个，比单独传 file_name 更灵活）
        use_hybrid: True 使用 Dense + BM25 Sparse 混合检索（推荐默认）

    返回:
        按相似度从高到低排序的节点（已通过 post_filter）
    """
    # 合并便捷参数和 filters 对象
    if filters is None:
        filters = RetrievalFilters()
    if file_name and not filters.file_name:
        filters.file_name = file_name

    # 构造 Milvus 侧 MetadataFilters
    mi_filters = filters.build_llamaindex_filters()

    # 为 post_filter 预留缓冲：实际取更多一点，再过滤
    raw_top_k = int(max(top_k, 1) * 2)

    # 构造 retriever 关键字参数
    retriever_kwargs: dict[str, Any] = {
        "similarity_top_k": raw_top_k,
    }
    if use_hybrid:
        # GPT文档第10节推荐：Hybrid模式
        retriever_kwargs["vector_store_query_mode"] = "hybrid"
    if mi_filters is not None:
        retriever_kwargs["filters"] = mi_filters

    logger.info(
        "检索开始: question=%s, top_k=%d(缓冲=%d), hybrid=%s, mi_filters=%s",
        question[:80],
        top_k,
        raw_top_k,
        use_hybrid,
        _summarize_filters(mi_filters),
    )

    retriever = index.as_retriever(**retriever_kwargs)
    raw_nodes = list(retriever.retrieve(question))

    logger.debug("  Milvus侧返回 %d 个节点（未post_filter）", len(raw_nodes))

    # Post 过滤（解决 NOT / 包含 / exclude_noise）
    post_nodes = filters.post_filter(raw_nodes)
    # 截断到用户要求的 top_k
    result = post_nodes[:top_k]

    logger.info(
        "检索完成: Milvus返回=%d, post过滤后=%d, 最终返回=%d",
        len(raw_nodes),
        len(post_nodes),
        len(result),
    )
    _log_result_nodes(result)
    return result


# ---------------------------------------------------------------------------
# 便捷检索函数
# ---------------------------------------------------------------------------


def retrieve_by_part(
    index: VectorStoreIndex,
    question: str,
    part_number: int,
    *,
    top_k: int = 5,
    use_hybrid: bool = True,
) -> list[NodeWithScore]:
    """按规范部分编号检索（Milvus侧过滤，不再内存过滤）。

    相对原版的改进：
        - 不再 top_k * 5 → Milvus 侧直接用 ExactMatchFilter(part_number=xxx)
        - 自动排除 part_number=0 的检查项字典（only_spec_docs=True）
        - 默认启用 Hybrid
    """
    logger.info("按部分检索: part=%d, question=%s", part_number, question[:80])
    filters = RetrievalFilters(
        part_number=part_number,
        only_spec_docs=True,
    )
    return retrieve(
        index,
        question,
        top_k=top_k,
        filters=filters,
        use_hybrid=use_hybrid,
    )


def retrieve_check_items(
    index: VectorStoreIndex,
    question: str,
    *,
    top_k: int = 5,
    use_hybrid: bool = True,
) -> list[NodeWithScore]:
    """专用：只在检查项字典（28项）中做语义检索，返回 Top-N 候选检查项。

    用于 scheme_generator 生成方案前的一步：
        "用户需求 → 检索 Top3 检查项 → 只给 LLM 看 3 项而不是 28 项"
    """
    logger.info("检查项检索: top_k=%d, question=%s", top_k, question[:80])
    filters = RetrievalFilters(only_check_items=True)
    return retrieve(
        index,
        question,
        top_k=top_k,
        filters=filters,
        use_hybrid=use_hybrid,
    )


def retrieve_quality_context(
    index: VectorStoreIndex,
    question: str,
    *,
    part_number: int | None = None,
    data_name: str | None = None,
    top_k: int = 5,
    use_hybrid: bool = True,
    prefer_quality_rules: bool = True,
) -> list[NodeWithScore]:
    """专用：检索规范条款上下文（方案生成参数推断用）。

    默认只在真实规范文档（排除检查项字典part=0）里搜，
    且优先取 knowledge_type=quality_rule / field_rule 的结果。

    参数:
        prefer_quality_rules: True 时，先尝试 knowledge_type=quality_rule 取；
            数量不足再扩大到 field_rule → 最后扩大到不限 knowledge_type。
    """
    logger.info(
        "质检规范上下文检索: part=%s, data_name=%s, prefer_quality=%s, question=%s",
        part_number,
        data_name,
        prefer_quality_rules,
        question[:80],
    )

    def _try(kt: str | None, k: int) -> list[NodeWithScore]:
        f = RetrievalFilters(
            part_number=part_number,
            knowledge_type=kt,
            data_name=data_name,
            only_spec_docs=True,
        )
        return retrieve(
            index, question, top_k=k, filters=f, use_hybrid=use_hybrid,
        )

    if not prefer_quality_rules:
        return _try(None, top_k)

    # 策略：quality_rule → field_rule → 不限制，三级渐进召回，取满top_k
    collected: list[NodeWithScore] = []
    seen_ids: set[str] = set()
    for kt_target in ("quality_rule", "field_rule", None):
        if len(collected) >= top_k:
            break
        need = top_k - len(collected)
        got = _try(kt_target, need * 2)
        for n in got:
            if n.node.node_id not in seen_ids:
                seen_ids.add(n.node.node_id)
                collected.append(n)
                if len(collected) >= top_k:
                    break
    result = collected[:top_k]
    logger.info("  渐进召回完成: 最终节点数=%d", len(result))
    return result


# ---------------------------------------------------------------------------
# 日志辅助
# ---------------------------------------------------------------------------


def _summarize_filters(filters: MetadataFilters | None) -> str:
    if filters is None or not filters.filters:
        return "None"
    parts = []
    for f in filters.filters:
        try:
            parts.append(f"{f.key}={f.value}")
        except Exception:
            parts.append(str(f))
    return f"[{'; '.join(parts)}]"


def _log_result_nodes(nodes: list[NodeWithScore]) -> None:
    for pos, n in enumerate(nodes, start=1):
        score = n.score
        meta = n.node.metadata or {}
        preview = n.node.get_content().replace("\n", " ")[:80]
        logger.debug(
            "  结果#%d: score=%.4f, part=%s, kt=%s, doc_type=%s, file=%s, preview=%s…",
            pos,
            score if score is not None else float("nan"),
            meta.get("part_number", "?"),
            meta.get("knowledge_type", "?"),
            meta.get("doc_type", "?"),
            meta.get("file_name", "?"),
            preview,
        )
