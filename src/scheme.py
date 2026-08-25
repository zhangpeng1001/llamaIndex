"""【方案生成】自然语言需求 → 结构化质检方案。

学习要点:
    - 复杂业务方案生成不是一个 LLM 调用能解决的,要做「检索前置 + 结构分解 + 校验后置」。
    - LLM 擅长「裁决和填充」,不擅长「在 27 项长列表中记忆+匹配」。
    - 检查项选择的「白名单」必须是「语义检索命中的候选项」,不是全量 27 项。
    - 意图识别:非质检要求时友好拒绝,避免对闲聊/无关问题浪费 RAG 流程。

业务背景:
    用户需求的「结构复杂度」和「子查询数量」直接决定最终方案的检查项数量。
    系统应该"宁少勿滥"(用户没提的不添加),所以子查询数是硬性上限。

完整链路:
    用户自然语言需求
      ↓
    [scheme_intent.recognize_scheme_intent] → 意图识别(非质检要求则友好拒绝)
      ↓
    [scheme_generator.generate_scheme] → 查询分解 + TopN候选 + Pydantic 结构化
      ↓
    [scheme_generator.scheme_to_dict] → 序列化为前端可消费的 dict
      ↓
    结构化方案 JSON(schemeName/description/checkItem[])

复用模块:
    - qualityScheme.scheme_generator.generate_scheme / scheme_to_dict
    - qualityScheme.scheme_intent.recognize_scheme_intent
    - qualityScheme.check_items.list_check_items
"""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM

from qualityScheme.check_items import list_check_items
from qualityScheme.scheme_generator import generate_scheme, scheme_to_dict
from qualityScheme.scheme_intent import recognize_scheme_intent

logger = logging.getLogger(__name__)


def run_scheme_generate(
    index: VectorStoreIndex,
    llm: LLM,
    requirement: str,
    context_top_k: int = 5,
) -> dict[str, Any]:
    """执行质检方案生成:意图识别 + 查询分解 + TopN候选 + Pydantic。

    参数:
        index: VectorStoreIndex(Storing 阶段产出,用于检索规范上下文 + 检查项候选)。
        llm: 语言模型(用于意图识别 + 方案生成)。
        requirement: 自然语言质检需求(如"检测点坐标精度不超过0.5米,编号唯一")。
        context_top_k: 检索规范上下文的条款数(默认5)。

    返回:
        dict: 两种情况
            1. 质检要求 → {"schemeName":..., "description":..., "checkItem":[...]}
            2. 非质检要求 → {"status":"rejected", "message":..., "suggestion":...}

    流程:
        1. recognize_scheme_intent(llm, requirement) → 意图识别
           - 判断用户输入是否为真实的质检方案要求
           - 非质检要求(如闲聊)→ 返回 {"status":"rejected", ...}
        2. generate_scheme(index, llm, requirement, context_top_k) → 结构化方案
           - 查询分解:复合需求 → 拆多个子意图
           - 每个子意图独立检索规范上下文 + Top3 候选检查项
           - LLM 在候选项里裁决选哪 + 填参(Pydantic 校验)
           - 后处理:checkCode 白名单校验 + 参数名规范化
        3. scheme_to_dict(scheme) → 序列化为 dict

    日志:
        - requirement(截断100字符)、context_top_k
        - 意图识别结果(is_quality_requirement、reason)
        - 方案生成结果(schemeName、检查项数)
    """

    logger.info(
        "===== 方案生成开始 =====\n"
        "  入参: requirement=%s, context_top_k=%d",
        requirement[:100],
        context_top_k,
    )

    if not requirement.strip():
        logger.error("方案生成失败: requirement 为空")
        return {
            "status": "rejected",
            "message": "需求描述不能为空",
            "suggestion": "请输入具体的质检需求,例如:检测点坐标精度不超过0.5米,编号唯一。",
        }

    # ------------------------------------------------------------------
    # Step 1: 意图识别(判断是否为质检方案要求)
    # ------------------------------------------------------------------
    logger.info("Step 1: 意图识别")
    intent = recognize_scheme_intent(llm, requirement)
    logger.info(
        "  意图识别结果: is_quality=%s, reason=%s",
        intent.is_quality_requirement,
        intent.reason,
    )

    if not intent.is_quality_requirement:
        # 非质检要求:返回 200 + status 标志,前端友好展示引导信息
        logger.info("  非质检要求,返回 rejected")
        return {
            "status": "rejected",
            "message": "未识别到质检方案要求,请输入具体的质检需求。",
            "suggestion": intent.suggestion,
        }

    # ------------------------------------------------------------------
    # Step 2: 方案生成(查询分解 + TopN候选 + Pydantic)
    # ------------------------------------------------------------------
    logger.info("Step 2: 调用 generate_scheme 生成结构化方案")
    scheme = generate_scheme(
        index,
        llm,
        requirement,
        context_top_k=context_top_k,
    )

    # ------------------------------------------------------------------
    # Step 3: 序列化为前端可消费的 dict
    # ------------------------------------------------------------------
    result = scheme_to_dict(scheme)
    logger.info(
        "  方案生成完成: schemeName=%s, 检查项数=%d",
        result.get("schemeName"),
        len(result.get("checkItem", [])),
    )

    logger.info("===== 方案生成完成 =====")
    return result


def get_check_items() -> list[dict[str, Any]]:
    """返回预定义检查项清单(27 项)。

    用于前端展示与选择参考。复用 qualityScheme.check_items.list_check_items。

    返回:
        list[dict]: 每项含 checkCode/checkName/checkDesc/checkParam/param_specs
        （param_names 在加载阶段由 checkParam 解析得到）。
    """

    logger.info("返回预定义检查项清单")
    items = list_check_items()
    logger.info("  检查项数=%d", len(items))
    return items
