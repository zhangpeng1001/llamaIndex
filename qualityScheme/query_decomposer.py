"""用户需求 Query 分解模块（多意图拆解）。

解决原版问题：
    用户输入"检测点坐标精度不超过0.5米，编号唯一，必填字段完整" → 直接整句
    Embedding → TopK=5 → 结果被「出现次数最多的词」主导（可能3条精度、1条编号、0条必填）
    → 生成方案漏项。

改进（对应 GPT 文档第 23 节 Query Decomposition）：
    先把用户需求用 LLM + Pydantic 拆成多个独立子意图（SubQuery），
    每个子意图：intent_type + data_name + constraint + question_text（独立检索版）。
    然后每个子意图独立走检索流程，再聚合所有上下文给方案生成。

学习要点：
    - 「复杂需求」和「简单需求」的处理方式不同。简单需求（"检测点编号是什么？"）
      不需要拆分，但复合需求（多检查项、多数据层）必须拆分。
    - LLM 的结构化输出能力（Pydantic）在"分类/拆分"类任务上非常稳定，
      失败率远低于「让 LLM 自由生成一段方案」。
    - 意图类型枚举（intent_type）要和 28 项检查项的类别强对应，否则后续匹配会失败。

业务背景：
    用户的一句自然语言质检需求，往往包含「N 个独立检查要求」的并列关系。
    这些要求的集合，就是最终方案的 checkItem 数的「锚点」—— 3 个子意图 ≈ 3~4 个检查项，
    避免 LLM "画蛇添足"多加项或漏项。
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any

from llama_index.core.llms import LLM
from llama_index.core.program import LLMTextCompletionProgram
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 意图类型枚举（必须与 28 项检查项的语义匹配）
# ---------------------------------------------------------------------------

INTENT_TYPES: dict[str, dict[str, Any]] = {
    # --- 字段属性类 ---
    "field_length": {
        "desc": "字段长度检查（字符数上限、固定长度）",
        "keywords": ["长度", "字符数", "位数", "字节数"],
        "check_codes": ["qualityCheckFieldLength", "qualityCheckDecimalPlaces"],
    },
    "field_unique": {
        "desc": "字段唯一值检查（不重复）",
        "keywords": ["唯一", "不重复", "重复", "去重", "重号", "编号唯一", "不能重复"],
        "check_codes": ["QualityCheckUniqueValue"],
    },
    "field_required": {
        "desc": "必填字段非空检查",
        "keywords": ["必填", "非空", "不能为空", "必须填写", "不能为null", "缺失"],
        "check_codes": ["qualityCheckFieldRequiredValidation", "qualityCheckRequiredFieldMismatch"],
    },
    "field_range": {
        "desc": "范围/值域检查",
        "keywords": ["值域", "范围", "取值范围", "合法值", "枚举", "最大", "最小", "不超过", "不低于", "不小于"],
        "check_codes": ["QualityCheckRangeValidation"],
    },
    "field_invalid_char": {
        "desc": "字段非法字符检查",
        "keywords": ["非法字符", "特殊字符", "包含字符", "字符检查"],
        "check_codes": ["qualityCheckInvalidFieldValue"],
    },
    "code_name_match": {
        "desc": "编码名称匹配检查",
        "keywords": ["编码匹配", "代码匹配", "名称编码", "编码名称", "代码名称对应"],
        "check_codes": ["qualityCheckCodeNameMatch"],
    },
    "decimal_places": {
        "desc": "小数位数检查",
        "keywords": ["小数位数", "小数位", "保留几位", "精度位数"],
        "check_codes": ["qualityCheckDecimalPlaces"],
    },
    "field_integrity": {
        "desc": "属性字段完整性（字段名、类型、长度定义）",
        "keywords": ["字段完整", "字段定义", "字段结构", "字段类型", "字段齐全"],
        "check_codes": ["QualityCheckFieldIntegrity"],
    },
    # --- 坐标/精度类 ---
    "coordinate_accuracy": {
        "desc": "坐标精度/位置精度检查（阈值，如≤0.5米）",
        "keywords": ["坐标精度", "位置精度", "精度", "误差", "偏差", "0.5米", "米精度", "中误差"],
        "check_codes": ["layerPolygonAreaConsistencyCheck"],
    },
    "coordinate_system": {
        "desc": "平面坐标系/投影检查",
        "keywords": ["坐标系", "平面坐标", "投影", "空间参考", "高斯", "2000国家大地坐标系"],
        "check_codes": ["QualityCheckCoordinateSystem"],
    },
    # --- 几何检查类 ---
    "line_overlap": {
        "desc": "线要素重叠重合检查",
        "keywords": ["线重叠", "线重合", "重叠线", "重复线"],
        "check_codes": ["qualityCheckLineOverlap"],
    },
    "point_overlap": {
        "desc": "点要素重叠检查",
        "keywords": ["点重叠", "点重合", "重复点"],
        "check_codes": ["QualityCheckPointOverlap"],
    },
    "hanging_points": {
        "desc": "线悬挂点检查",
        "keywords": ["悬挂点", "悬挂线", "线头", "未连接"],
        "check_codes": ["QualityInspectionLayerHangingPoints"],
    },
    "broken_line": {
        "desc": "碎线检查（小于最小长度）",
        "keywords": ["碎线", "最小长度", "短线", "过短"],
        "check_codes": ["QualityCheckInnerLayerBreaks"],
    },
    "area_overlap": {
        "desc": "面内重叠检查",
        "keywords": ["面重叠", "面重合", "重叠面"],
        "check_codes": ["qualityInspectionFeatureOverlap"],
    },
    "area_gap": {
        "desc": "面缝隙检查",
        "keywords": ["面缝隙", "缝隙", "空隙", "裂口", "相邻面"],
        "check_codes": ["QualityInspectionSurfaceGapCheck"],
    },
    "area_fragments": {
        "desc": "碎面检查（小于最小面积）",
        "keywords": ["碎面", "最小面积", "小面", "面碎片"],
        "check_codes": ["QualityCheckInnerLayerFragments"],
    },
    "sharp_angle": {
        "desc": "尖锐角检查",
        "keywords": ["尖锐角", "锐角", "角度阈值", "最小角度"],
        "check_codes": ["SharpAngleCheckForQC"],
    },
    "area_self_intersection": {
        "desc": "面自相交检查",
        "keywords": ["自相交", "自交叉", "面自身重叠"],
        "check_codes": ["QualityCheckSurfaceSelfIntersection"],
    },
    "area_void": {
        "desc": "面要素空洞/孤岛检查",
        "keywords": ["空洞", "孤岛", "面空洞", "内环"],
        "check_codes": ["QualityCheckVoidInspection"],
    },
    "null_geometry": {
        "desc": "空几何检查",
        "keywords": ["空几何", "几何为空", "没有形状", "空图形", "无几何"],
        "check_codes": ["checkLayerElementEmptyGeometry"],
    },
    "layer_integrity": {
        "desc": "图层完整性检查（几何类型、数据结构）",
        "keywords": ["图层完整性", "几何类型", "图层结构", "图层完整"],
        "check_codes": ["QualityCheckLayerIntegrity"],
    },
    # --- 时间类 ---
    "time_validity": {
        "desc": "时间有效性检查（起止时间范围）",
        "keywords": ["时间", "日期", "有效期", "时间范围", "起止", "有效时间"],
        "check_codes": ["QualityCheckTimeValidity"],
    },
    # --- 跨图层一致性类 ---
    "inter_layer_attribute_consistency": {
        "desc": "图层间属性一致性检查",
        "keywords": ["跨图层属性", "属性一致", "图层间一致", "属性对应"],
        "check_codes": ["checkInterLayerAttributeConsistency"],
    },
    "polygon_contained_equal": {
        "desc": "多边形被包含且属性相等",
        "keywords": ["包含关系", "被包含", "包含且属性相同", "多边形包含"],
        "check_codes": ["CheckPolygonContainedAttrEqual"],
    },
    "inter_layer_space_attribute": {
        "desc": "图层间空间+属性一致性检查",
        "keywords": ["空间属性一致", "跨图层空间属性", "空间一致", "图层空间"],
        "check_codes": ["InterLayerFeatureConsistencyCheck"],
    },
    # --- 兜底 ---
    "general_quality": {
        "desc": "通用质量检查（无法明确分类时使用）",
        "keywords": ["质检", "质量检查", "检查", "质控"],
        "check_codes": [],  # 无特定检查项，后续由LLM自行匹配
    },
}


# ---------------------------------------------------------------------------
# Pydantic 结构化输出（LLM分解结果）
# ---------------------------------------------------------------------------


class SubQueryPydantic(BaseModel):
    """单个子查询意图。"""

    intent_type: str = Field(
        description=(
            "子意图类型，必须从给定枚举中选一个最贴切的："
            + ", ".join(f"{k}({v['desc']})" for k, v in list(INTENT_TYPES.items())[:18])
            + " 等"
        )
    )
    data_name: str = Field(
        description=(
            "该子意图涉及的数据对象中文名（如检测点、检测线、标志性地物、"
            "高精度栅格、重要要素、资源数据）。无法确定时从用户原句中提取最核心的1~2个。"
        )
    )
    constraint: str = Field(
        description=(
            "该子意图的约束/参数文本（如'≤0.5米'、'编号'、'必填'、'唯一'）。"
            "没有明确约束时填空字符串。"
        )
    )
    standalone_question: str = Field(
        description=(
            "把该子意图改写为一句独立的完整问句（便于单独检索用）。"
            "例：原句拆分后，standalone_question='检测点坐标精度要求是什么？'"
        )
    )


class DecomposedQueryPydantic(BaseModel):
    """用户需求分解的完整输出。"""

    overall_requirement_summary: str = Field(
        description="对用户原需求的一句话中文摘要，便于日志和方案名称生成。"
    )
    needs_decomposition: bool = Field(
        description="是否判定为复合需求需要拆分（≥2个独立意图为True，单个简单意图为False）。"
    )
    sub_queries: list[SubQueryPydantic] = Field(
        description=(
            "拆分出的子查询列表。即使 needs_decomposition=False，也要把单意图"
            "包装为长度1的列表，便于下游统一处理。"
        )
    )


# ---------------------------------------------------------------------------
# Prompt 模板
# ---------------------------------------------------------------------------


DECOMPOSE_PROMPT_TEMPLATE = """你是「质检需求拆解专家」。请把用户输入的自然语言质检需求，
拆分为一个或多个独立的「子查询意图」。

## 背景知识（检查项能力域 + 意图枚举）
系统支持的意图类型（intent_type）及其含义 / 关键词 / 对应检查项编码：
{intent_catalog}

## 数据对象枚举（data_name 只能从这里选，禁止自己创造）
- 检测点（对应第2部分）
- 检测线（对应第3部分）
- 标志性地物（对应第4部分）
- 重要要素（对应第5部分）
- 高精度栅格数据 / DOM / DEM / DSM（对应第6部分）
- 资源数据（对应第7部分）
- 时空数据（通用，无法明确归属时用）

## 拆分规则
1. 用户需求中每个「独立的检查要求」拆成一个 SubQuery。
   例："坐标精度≤0.5米，编号唯一，必填字段完整" → 拆成 3 个 SubQuery。
2. 单个简单要求（如"检测点编号规则是什么"）→ needs_decomposition=False，子查询数=1。
3. 子查询的 intent_type 必须从上方「意图枚举」中选择最贴切的一个（而非自创）。
4. 子查询的 data_name 从「数据对象枚举」中选 1~2 个最贴切的（用中文名称，如"检测点"）。
5. standalone_question：把该子意图改写为「一句独立的、完整的、语义自包含的问句」，
   便于后续单独走检索流程（不能只写半句话）。
6. constraint：如果有明确的数值阈值、字段名、约束词，填进去；否则留空字符串。

## 用户输入
{requirement}

请直接输出结构化结果。"""


# ---------------------------------------------------------------------------
# 格式化枚举给 Prompt 用
# ---------------------------------------------------------------------------


def _format_intent_catalog_for_prompt() -> str:
    lines = ["| intent_type | 含义 | 关键词示例 | 对应检查项 |",
             "|---|---|---|---|"]
    for k, v in INTENT_TYPES.items():
        kw = "、".join(v["keywords"][:6])
        codes = "、".join(v["check_codes"][:3])
        lines.append(f"| {k} | {v['desc']} | {kw} | {codes} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 数据类（非Pydantic，运行时用）
# ---------------------------------------------------------------------------


@dataclass
class SubQuery:
    intent_type: str
    data_name: str
    constraint: str
    standalone_question: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_type": self.intent_type,
            "data_name": self.data_name,
            "constraint": self.constraint,
            "standalone_question": self.standalone_question,
            "intent_desc": INTENT_TYPES.get(self.intent_type, {}).get("desc", self.intent_type),
        }


@dataclass
class DecomposedQuery:
    overall_summary: str
    needs_decomposition: bool
    sub_queries: list[SubQuery] = field(default_factory=list)

    @property
    def all_data_names(self) -> list[str]:
        """提取所有子查询涉及的数据对象名（去重保序）。"""
        seen: set[str] = set()
        out: list[str] = []
        for sq in self.sub_queries:
            if sq.data_name and sq.data_name not in seen:
                seen.add(sq.data_name)
                out.append(sq.data_name)
        return out

    @property
    def all_intent_types(self) -> list[str]:
        return [sq.intent_type for sq in self.sub_queries]

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_summary": self.overall_summary,
            "needs_decomposition": self.needs_decomposition,
            "sub_queries": [sq.to_dict() for sq in self.sub_queries],
            "all_data_names": self.all_data_names,
            "all_intent_types": self.all_intent_types,
        }


# ---------------------------------------------------------------------------
# 核心分解函数
# ---------------------------------------------------------------------------


def decompose_query(
    llm: LLM,
    requirement: str,
    *,
    min_subqueries: int = 1,
) -> DecomposedQuery:
    """对用户需求做多意图分解。

    参数:
        llm: 语言模型（与方案生成共用）
        requirement: 用户自然语言质检需求
        min_subqueries: 兜底最小子查询数；LLM返回空列表时至少生成1条

    返回:
        DecomposedQuery 对象；LLM调用失败时走规则兜底。
    """
    logger.info("开始Query分解: requirement=%s", requirement[:100])
    start_ts = time.perf_counter()

    intent_catalog = _format_intent_catalog_for_prompt()
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=DecomposedQueryPydantic,
        llm=llm,
        prompt_template_str=DECOMPOSE_PROMPT_TEMPLATE,
        verbose=False,
    )

    try:
        raw: DecomposedQueryPydantic = program(
            intent_catalog=intent_catalog,
            requirement=requirement,
        )
    except Exception as exc:
        elapsed = time.perf_counter() - start_ts
        logger.warning(
            "LLM Query分解失败，走规则兜底: error=%s, 耗时=%.2fs",
            exc,
            elapsed,
        )
        return _rule_based_fallback(requirement, min_subqueries)

    # Pydantic → 运行时数据类
    sub_queries = [
        SubQuery(
            intent_type=sq.intent_type,
            data_name=sq.data_name,
            constraint=sq.constraint,
            standalone_question=sq.standalone_question,
        )
        for sq in raw.sub_queries
    ]

    # 兜底：如果LLM给了空列表，生成1条general
    if not sub_queries:
        logger.warning("LLM返回空子查询列表，规则兜底补1条")
        return _rule_based_fallback(requirement, min_subqueries)

    result = DecomposedQuery(
        overall_summary=raw.overall_requirement_summary or requirement[:50],
        needs_decomposition=raw.needs_decomposition,
        sub_queries=sub_queries,
    )
    elapsed = time.perf_counter() - start_ts
    logger.info(
        "Query分解完成: 子查询数=%d, needs_decomp=%s, summary=%s, 耗时=%.2fs",
        len(result.sub_queries),
        result.needs_decomposition,
        result.overall_summary,
        elapsed,
    )
    for i, sq in enumerate(result.sub_queries, 1):
        logger.info(
            "  子查询#%d: intent=%s, data_name=%s, constraint=%s, question=%s",
            i,
            sq.intent_type,
            sq.data_name,
            sq.constraint,
            sq.standalone_question[:60],
        )
    return result


# ---------------------------------------------------------------------------
# 规则兜底（LLM失败时，用关键词启发式生成最少1条可用SubQuery）
# ---------------------------------------------------------------------------


def _rule_based_fallback(requirement: str, min_sub: int) -> DecomposedQuery:
    """关键词匹配式兜底分解（保证不返回空）。"""
    # 1. 提取 data_name
    dname = "时空数据"
    for cand in ("检测点", "检测线", "标志性地物", "重要要素", "高精度栅格", "DEM", "DOM", "DSM", "资源数据"):
        if cand in requirement:
            dname = cand
            break

    # 2. 按 intent_type 关键词匹配，命中几个就生成几条（最多3条，避免过多）
    matched: list[tuple[str, str]] = []  # (intent_type, constraint)
    for itype, info in INTENT_TYPES.items():
        if itype == "general_quality":
            continue
        for kw in info["keywords"]:
            if kw in requirement:
                matched.append((itype, kw))
                break
        if len(matched) >= 3:
            break

    if not matched:
        matched.append(("general_quality", ""))

    sub_queries = [
        SubQuery(
            intent_type=it,
            data_name=dname,
            constraint=cons,
            standalone_question=f"{dname}的{INTENT_TYPES[it]['desc']}要求是什么？（{cons}）" if cons
            else f"{dname}的{INTENT_TYPES[it]['desc']}要求是什么？",
        )
        for it, cons in matched[: max(min_sub, 1)]
    ]
    summary = re.sub(r"\s+", "", requirement)[:40]
    return DecomposedQuery(
        overall_summary=summary,
        needs_decomposition=len(sub_queries) > 1,
        sub_queries=sub_queries,
    )
