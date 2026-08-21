"""增强版质检方案自动编排模块。

相对原版的 5 大改进（对应问题报告核心问题）：
    1. ✅ 先做 Query Decomposition：复合需求 → 拆多个子意图 → 每个子意图独立检索
       （解决「复合需求漏项」，如"精度+编号+必填"只命中精度的问题）
    2. ✅ 检查项 TopN 语义匹配：先在 Milvus 检索 Top-3 候选检查项，再给 LLM 看 3 项
       （解决「28项大表浪费Token + LLM长上下文记忆力不足漏选」）
    3. ✅ 规范上下文：优先检索 knowledge_type=quality_rule/field_rule，过滤 TOC 噪声
       （解决「检索结果30%是目录，信噪比低」）
    4. ✅ 参数名规范化：Prompt 引导蛇形名，最后通过别名映射回平台要求的驼峰/蛇形混合
       （解决「data_name / dataName 写错，下游执行报找不到参数」）
    5. ✅ 删除 print 调试输出 → 用 logger.debug；且子查询数=方案检查项数上限（防画蛇添足）

完整链路：
    用户自然语言需求
      ↓
    [query_decomposer] → DecomposedQuery (N 个子查询)
      ↓ 对每个 SubQuery 并行：
          A. [metadata_filter.retrieve_check_items] → Top-3 检查项候选
          B. [metadata_filter.retrieve_quality_context] → 规范条款上下文（参数推断用）
      ↓
    汇总：所有 SubQuery 的检查项候选项并集 + 所有规范上下文
      ↓
    [LLM + Pydantic] → 生成 QualityScheme（检查项只从候选项并集里选）
      ↓
    后处理：checkCode 白名单校验 + canonicalize_params 参数名规范化 + 缺失参数补齐
      ↓
    最终结构化方案 JSON

学习要点：
    - 「复杂业务方案生成」不是一个 LLM 调用能解决的，要做「检索前置 + 结构分解 + 校验后置」。
    - LLM 擅长「裁决和填充」，不擅长「在 28 项长列表中记忆+匹配」。
    - 检查项选择的「白名单」必须是「语义检索命中的候选项」，不是全量 28 项。

业务背景：
    用户需求的「结构复杂度」和「子查询数量」直接决定最终方案的检查项数量。
    系统应该"宁少勿滥"（用户没提的不添加），所以子查询数是硬性上限。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.core.program import LLMTextCompletionProgram
from pydantic import BaseModel, Field

from .check_items import (
    canonicalize_params,
    format_param_names_snake_case,
    get_check_item,
    is_valid_check_code,
)
from .check_items_indexer import (
    extract_check_codes_from_nodes,
    format_top_check_items_for_prompt,
)
from .metadata_filter import retrieve_check_items, retrieve_quality_context
from .query_decomposer import DecomposedQuery, SubQuery, decompose_query

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic 结构化输出模型
# ---------------------------------------------------------------------------


class CheckItem(BaseModel):
    """单个检查项的结构化输出。"""

    checkCode: str = Field(description="检查项编码，必须从「候选项检查项清单」中选择")
    checkName: str = Field(description="检查项中文名称（必须和清单保持一致）")
    params: dict[str, Any] = Field(
        description=(
            "检查项参数，键名请尽量使用蛇形（如 data_name, field_names, min_length），"
            "系统最后会自动映射回平台实际需要的参数名（dataName/fieldNames等）。"
            "必须包含该检查项声明的所有参数，值为具体取值（字段名数组、阈值、坐标系等）"
        )
    )


class QualityScheme(BaseModel):
    """质检方案的结构化输出，最终交付给前端/下游系统。"""

    schemeName: str = Field(description="方案名称，简洁体现数据对象与检查重点")
    description: str = Field(description="方案描述，1-2 句说明检查目标与范围")
    checkItem: list[CheckItem] = Field(description="检查项列表（请严格从候选项里选，不要自创）")


# ---------------------------------------------------------------------------
# Prompt 模板（改进版：只给候选项，不给 28 项全表）
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """你是实景三维质检方案编排专家。请根据：
    ① 用户需求摘要
    ② 拆分出的子意图详情
    ③ 从知识库语义检索到的「规范条款上下文」（用于推断字段名、阈值等）
    ④ 从「28项检查项字典」语义匹配到的「候选项检查项清单」（注意：checkCode 必须只能从此清单里来，严禁自创！）
生成一份结构化质检方案 JSON。

## ① 用户需求摘要
{overall_summary}

## ② 拆分后的子意图（{sub_query_count}条，每条对应至少1个检查项；**禁止超出子意图数+1的检查项总数**）
{sub_queries_details}

## ③ 时空数据规范上下文（推断字段名/阈值/坐标系用）
以下是从 Milvus 知识库通过「quality_rule/field_rule 优先过滤 + Hybrid 检索」取到的相关条款：
{context}

## ④ 候选项检查项清单（checkCode 必须只能从此表中选！总共 {candidate_count} 项，请从中挑选最合适的）
{check_items_candidates}

## 输出要求（严格遵守）
1. schemeName：简洁，体现数据对象+检查重点，如"检测点坐标+编号+必填质检方案"。
2. description：1-2 句描述方案目标与检查范围，可引用需求摘要。
3. checkItem：
   a) 数量控制：检查项数 ≤ 子意图数 + 1（一般 == 子意图数，极个别子意图需拆2项检查时才超过），**严禁添加用户未提及的任何检查项**。
   b) checkCode：必须来自上方④候选项清单（候选项是从28项字典中语义匹配的结果，若不在里面说明不是本次需求需要的）。
   c) checkName：必须与候选项清单中的名称完全一致（系统后处理会再次强制覆盖）。
   d) params：
      - 键名推荐用「蛇形」：如 data_name(或dataName), field_names, min_length, threshold, date_start, min_area。系统会自动映射到平台需要的实际参数名。
      - 必须包含候选项清单中「参数名」列声明的**全部参数**，不得缺键。
      - data_name：对应用户需求提到的数据对象中文名（如"检测点"、"检测线"）。
      - field_names：优先参考③规范上下文中出现过的字段名（检测点编号、坐标X/Y、地物代码、采集日期等）；若无明确上下文，对应用户需求里的关键词。
      - 数值阈值：如果②子意图中有"≤0.5米"、"唯一"、"必填"、"不小于"等明确约束，优先使用用户给的数值。
      - 无法确定的值，可以填 null，但不要编造不存在的字段名和数值。
4. 禁止：
   - 从④之外的检查项挑（会被系统过滤丢弃，白名单校验失败）
   - 添加用户未提及的检查项
   - 参数值瞎编（真不知道填 null）

请直接输出结构化结果。"""


# ---------------------------------------------------------------------------
# 辅助：把 SubQuery 列表格式化为 Prompt 可读文本
# ---------------------------------------------------------------------------


def _format_sub_queries_for_prompt(decomposed: DecomposedQuery) -> str:
    lines = []
    for i, sq in enumerate(decomposed.sub_queries, 1):
        lines.append(
            f"### 子意图{i}\n"
            f"- intent_type: {sq.intent_type}\n"
            f"- 数据对象(data_name): {sq.data_name}\n"
            f"- 约束条件: {sq.constraint or '(无明确约束)'}\n"
            f"- 独立检索问句: {sq.standalone_question}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 核心：逐 SubQuery 检索规范上下文 + 检查项候选项
# ---------------------------------------------------------------------------


def _retrieve_for_scheme(
    index: VectorStoreIndex,
    decomposed: DecomposedQuery,
    *,
    spec_top_k_per_subquery: int = 3,
    checkitem_top_k_per_subquery: int = 3,
    max_total_checkitem_candidates: int = 8,
) -> tuple[str, str, list[str]]:
    """为方案生成准备检索素材：规范上下文 + 候选项表格 + 允许的checkCode白名单。

    对每个 SubQuery 独立检索，再做并集。
    """
    logger.info(
        "方案生成前置检索: SubQueries=%d, spec_top_k=%d, checkitem_top_k=%d",
        len(decomposed.sub_queries),
        spec_top_k_per_subquery,
        checkitem_top_k_per_subquery,
    )

    # 收集规范上下文
    spec_lines: list[str] = []
    seen_spec_ids: set[str] = set()
    # 收集检查项 Node（去重）
    all_checkitem_nodes: list[Any] = []
    seen_check_codes: set[str] = set()

    for i, sq in enumerate(decomposed.sub_queries, 1):
        logger.debug("  处理子查询#%d: %s", i, sq.intent_type)
        # --- A. 规范上下文（用 standalone_question 检索）
        spec_nodes = retrieve_quality_context(
            index,
            sq.standalone_question,
            data_name=sq.data_name if sq.data_name and sq.data_name != "时空数据" else None,
            top_k=spec_top_k_per_subquery,
            prefer_quality_rules=True,
        )
        for n in spec_nodes:
            nid = n.node.node_id
            if nid in seen_spec_ids:
                continue
            seen_spec_ids.add(nid)
            meta = n.node.metadata or {}
            file_name = meta.get("file_name", "未知文件")
            kt = meta.get("knowledge_type", "")
            chapter = meta.get("chapter_no", "")
            prefix_parts = [f"[{file_name}"]
            if chapter:
                prefix_parts.append(f"条款{chapter}")
            if kt:
                prefix_parts.append(f"类型{kt}")
            prefix = " ".join(prefix_parts) + "]"
            content = n.node.get_content().replace("\n", " ").strip()
            spec_lines.append(f"{prefix} {content}")

        # --- B. 检查项检索（用 intent_type + standalone_question 合成查询）
        # 意图类型 + 约束 + 数据对象，组合成更精准的检查项检索词
        ci_query = f"{sq.data_name} {sq.intent_type} {sq.constraint} {sq.standalone_question}"
        ci_nodes = retrieve_check_items(
            index,
            ci_query,
            top_k=checkitem_top_k_per_subquery,
        )
        for n in ci_nodes:
            code = (n.node.metadata or {}).get("check_code", "")
            if not code or code in seen_check_codes:
                continue
            if len(all_checkitem_nodes) >= max_total_checkitem_candidates:
                break
            seen_check_codes.add(code)
            all_checkitem_nodes.append(n)

    context_text = "\n".join(spec_lines) if spec_lines else "（未检索到相关规范条款，请主要依靠子意图描述）"
    logger.info(
        "  前置检索完成: 规范上下文节点=%d(%d字符), 检查项候选项=%d(代码=%s)",
        len(seen_spec_ids),
        len(context_text),
        len(all_checkitem_nodes),
        sorted(seen_check_codes),
    )

    # 格式化候选项表格
    candidate_table = format_top_check_items_for_prompt(
        all_checkitem_nodes,
        max_items=max_total_checkitem_candidates,
    )
    # 白名单：允许的checkCode
    allowed_codes = extract_check_codes_from_nodes(all_checkitem_nodes)
    return context_text, candidate_table, allowed_codes


# ---------------------------------------------------------------------------
# 核心生成函数（增强版：带 Query 分解）
# ---------------------------------------------------------------------------


def generate_scheme(
    index: VectorStoreIndex,
    llm: LLM,
    requirement: str,
    *,
    context_top_k: int = 5,  # 保留原签名兼容，实际用 per-subquery k
    enable_decomposition: bool = True,
) -> QualityScheme:
    """根据自然语言需求生成质检方案（增强版，带Query分解 + 检查项语义匹配）。

    参数:
        index: 已构建的向量索引（含规范文档 + 检查项字典）。
        llm: 语言模型。
        requirement: 用户自然语言质检需求。
        context_top_k: 兼容原参数，实际按每个子查询检索 context_top_k//2 + 1。
        enable_decomposition: True 先走 Query Decomposition（推荐默认）；
            False 走原版单查询路径（极端情况兜底）。

    日志:
        - 入参需求摘要；
        - Query 分解耗时与子查询数；
        - 子查询级规范检索/检查项检索结果数；
        - LLM 原始生成项数 vs 校验后合法项数 vs 白名单过滤数。
    """
    logger.info("开始生成质检方案(增强版): requirement=%s, decompose=%s",
                requirement[:100], enable_decomposition)

    # 1. Query 分解（多意图）
    if enable_decomposition:
        decomposed = decompose_query(llm, requirement)
    else:
        # 兜底：不分解时，用原流程的分解结果包装成 1 条
        from .query_decomposer import _rule_based_fallback
        decomposed = _rule_based_fallback(requirement, 1)

    # 2. 每个 SubQuery 独立检索规范上下文 + 检查项候选项
    per_sub_k = max(context_top_k // 2 + 1, 2)
    context_text, candidate_table, allowed_codes = _retrieve_for_scheme(
        index,
        decomposed,
        spec_top_k_per_subquery=per_sub_k,
        checkitem_top_k_per_subquery=3,
    )

    # 如果检索出来的候选项为空（极端场景），退回「按intent_type直接找预设检查编码+全表28项」
    # 这里做个兜底保证不会让候选为空 → LLM白名单为空会过滤掉所有 → 输出空方案
    if not allowed_codes:
        logger.warning("检查项语义检索未命中，退回: 从分解的intent_types里直接映射检查项白名单")
        from .query_decomposer import INTENT_TYPES
        extra_codes: list[str] = []
        for it in decomposed.all_intent_types:
            extra_codes.extend(INTENT_TYPES.get(it, {}).get("check_codes", []))
        allowed_codes = list(dict.fromkeys(extra_codes))[:8]  # 去重保序，上限8
        if allowed_codes:
            # 构造一个假的候选项表格文本（从CHECK_ITEMS中直接拼）
            pseudo_lines = ["| checkCode | checkName | checkDesc | 参数名 | 匹配分数 |",
                            "|---|---|---|---|---|"]
            from .check_items import CHECK_ITEM_BY_CODE
            for c in allowed_codes:
                info = CHECK_ITEM_BY_CODE.get(c)
                if not info:
                    continue
                pnames = format_param_names_snake_case(info["param_names"])
                pseudo_lines.append(f"| {c} | {info['checkName']} | {info['checkDesc']} | {pnames} | fallback |")
            candidate_table = "\n".join(pseudo_lines)
        # 真的还是空 → 只能允许全量28项（最后手段）
        if not allowed_codes:
            logger.warning("  意图映射也空，最后兜底：允许全部28项")
            from .check_items import CHECK_ITEMS
            allowed_codes = [c["checkCode"] for c in CHECK_ITEMS]

    # 3. 组装增强版 Prompt
    sub_queries_text = _format_sub_queries_for_prompt(decomposed)
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=QualityScheme,
        llm=llm,
        prompt_template_str=PROMPT_TEMPLATE,
        verbose=False,
    )

    logger.info(
        "调用LLM生成结构化方案: llm=%s, 候选检查项=%d个, 子查询数=%d",
        getattr(llm, "model", getattr(llm, "model_name", type(llm).__name__)),
        len(allowed_codes),
        len(decomposed.sub_queries),
    )

    raw_scheme: QualityScheme = program(
        overall_summary=decomposed.overall_summary,
        sub_query_count=len(decomposed.sub_queries),
        sub_queries_details=sub_queries_text,
        context=context_text,
        candidate_count=len(allowed_codes),
        check_items_candidates=candidate_table,
    )

    logger.info(
        "LLM原始生成: schemeName=%s, 检查项数=%d, 允许的候选=%s",
        raw_scheme.schemeName,
        len(raw_scheme.checkItem),
        allowed_codes,
    )

    # 4. 校验：checkCode 合法性 + 白名单（必须来自 allowed_codes）+ 名称修正 + 参数规范化 + 缺失补齐
    valid_items: list[CheckItem] = []
    filtered_not_in_dict: list[str] = []
    filtered_not_whitelist: list[str] = []
    allowed_set = set(allowed_codes)
    # 数量控制上限（子意图数 + 1，允许某意图拆2项）
    max_check_items = max(len(decomposed.sub_queries) + 1, 1)

    for item in raw_scheme.checkItem:
        # 4a. 合法性（预定义28项中是否存在）
        if not is_valid_check_code(item.checkCode):
            logger.warning("过滤非法checkCode(不在28项): %s", item.checkCode)
            filtered_not_in_dict.append(item.checkCode)
            continue
        # 4b. 白名单（不在本次需求检索的候选项里 → LLM硬从28项里编）
        if item.checkCode not in allowed_set:
            logger.warning(
                "过滤checkCode(不在候选项白名单，可能是LLM画蛇添足): %s",
                item.checkCode,
            )
            filtered_not_whitelist.append(item.checkCode)
            continue
        # 4c. 数量上限
        if len(valid_items) >= max_check_items:
            logger.warning(
                "检查项数达到上限%d, 跳过多余的: %s",
                max_check_items,
                item.checkCode,
            )
            break

        # 4d. 用标准 checkName 覆盖
        canonical = get_check_item(item.checkCode)
        corrected = item.model_copy(update={"checkName": canonical["checkName"]})

        # 4e. 参数名规范化：蛇形 → 平台实际参数名
        canonical_params = canonicalize_params(corrected.checkCode, dict(corrected.params))

        # 4f. 补齐缺失参数（值为None），保证下游不缺键
        required_params = canonical["param_names"]
        for param_name in required_params:
            if param_name not in canonical_params:
                logger.debug(
                    "补齐缺失参数: checkCode=%s, param=%s -> None",
                    corrected.checkCode,
                    param_name,
                )
                canonical_params[param_name] = None
        corrected = corrected.model_copy(update={"params": canonical_params})
        valid_items.append(corrected)

    if filtered_not_in_dict:
        logger.warning("被过滤(不在28项字典): %s", filtered_not_in_dict)
    if filtered_not_whitelist:
        logger.warning("被过滤(不在候选项白名单): %s", filtered_not_whitelist)

    # 5. 组装最终方案
    scheme = raw_scheme.model_copy(update={"checkItem": valid_items})
    logger.info(
        "方案生成完成: schemeName=%s, 合法检查项=%d, 子查询数=%d, 过滤(字典外/白名单外)=%d/%d",
        scheme.schemeName,
        len(scheme.checkItem),
        len(decomposed.sub_queries),
        len(filtered_not_in_dict),
        len(filtered_not_whitelist),
    )
    return scheme


def scheme_to_dict(scheme: QualityScheme) -> dict[str, Any]:
    """把 QualityScheme 序列化为前端/下游可消费的 JSON 结构。"""
    return {
        "schemeName": scheme.schemeName,
        "description": scheme.description,
        "checkItem": [item.model_dump() for item in scheme.checkItem],
    }


def scheme_to_json(scheme: QualityScheme, *, indent: int = 2) -> str:
    """把 QualityScheme 序列化为 JSON 字符串。"""
    return json.dumps(scheme_to_dict(scheme), ensure_ascii=False, indent=indent)
