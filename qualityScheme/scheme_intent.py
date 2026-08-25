"""质检方案意图识别模块。

功能:
    在 ``/api/scheme/generate`` 调用方案生成主流程之前，先对用户输入的自然语言
    做一次轻量 LLM 意图识别，判断其是否为"真实的质检方案要求"。

    背景：用户未必会显式输入"质检方案"关键字，可能直接给出要求（如"检测点坐标
    精度不超过0.5米、编号唯一"）。本模块以预定义检查项清单（源自
    ``check_items._RAW_CHECK_ITEMS``）作为"系统能识别的质检能力域"参照，让 LLM
    判断用户输入是否落在这些能力域内，从而避免对闲聊/无关问题浪费完整 RAG 流程。

实现思路:
    1. 复用 ``check_items.format_check_items_for_prompt()`` 把检查项清单格式化为
       结构化文本（含 checkCode/checkName/checkDesc + 参数描述/示例；不再保留
       对意图识别无用的 checkRequestUrl/checkObjType 等字段，更省 token）。
    2. 用 ``LLMTextCompletionProgram + Pydantic`` 获得可校验的结构化判断结果，
       与 ``scheme_generator.py`` 保持一致的范式。
    3. 异常兜底：意图识别自身 LLM 调用失败时默认放行，保证主流程可用性优先。

学习要点:
    - 轻量意图识别：独立一次 LLM 调用，不检索向量索引，保持快速。
    - 结构化输出：Pydantic 约束 LLM 返回 ``is_quality_requirement`` 布尔判断。
    - 异常兜底策略：辅助链路故障不应阻断主流程。
"""

from __future__ import annotations

import logging
import time
from typing import Any

from llama_index.core.llms import LLM
from llama_index.core.program import LLMTextCompletionProgram
from pydantic import BaseModel, Field

from .check_items import format_check_items_for_prompt

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic 结构化输出模型
# ---------------------------------------------------------------------------


class IntentResult(BaseModel):
    """意图识别的结构化输出。"""

    is_quality_requirement: bool = Field(
        description=(
            "用户输入是否为真实的质检方案要求。True 表示描述了可映射到预定义"
            "检查项能力域的质检需求；False 表示闲聊、问候或与质检无关的问题。"
        )
    )
    reason: str = Field(
        description="判定理由，简短说明依据，用于日志与调试。"
    )
    suggestion: str = Field(
        description=(
            "当判定为 False 时，给用户的引导提示，包含质检需求的示例；"
            "判定为 True 时可为空字符串。"
        )
    )


# ---------------------------------------------------------------------------
# Prompt 模板
# ---------------------------------------------------------------------------

INTENT_PROMPT_TEMPLATE = """你是实景三维质检方案的意图识别专家。请判断"用户输入"是否为真实的质检方案要求。

## 系统能识别的质检能力域（预定义检查项清单）
以下检查项覆盖了系统支持的质检能力域（字段检查、几何检查、坐标系检查、图层一致性、值域、时间有效性、编码匹配等）：
{check_items}

## 用户输入
{requirement}

## 判定规则
1. 若"用户输入"描述了可映射到上述任一检查项能力域的质检要求，即使未出现"质检方案"关键字（例如"检测点坐标精度不超过0.5米，编号唯一"、"检查图层是否使用平面坐标系"、"字段值是否唯一"），则 is_quality_requirement=True。
2. 若"用户输入"为闲聊、问候、与质检无关的问题（例如"你好"、"今天天气怎么样"、"帮我写首诗"），则 is_quality_requirement=False，并在 suggestion 中给出质检需求示例引导用户重新输入。
3. suggestion 示例："请输入具体的质检需求，例如：检测点坐标精度不超过0.5米，编号唯一；或：检查图层字段是否完整、是否使用平面坐标系。"

请直接输出结构化结果。
"""


# ---------------------------------------------------------------------------
# 核心意图识别函数
# ---------------------------------------------------------------------------


def recognize_scheme_intent(llm: LLM, requirement: str) -> IntentResult:
    """对用户输入做意图识别，判断是否为质检方案要求。

    参数:
        llm: 语言模型（来自运行时，与方案生成共用同一实例）。
        requirement: 用户的自然语言输入。

    返回:
        IntentResult 对象，包含 is_quality_requirement、reason、suggestion。

    异常兜底:
        LLM 调用失败时返回默认放行结果（is_quality_requirement=True），
        避免意图识别故障阻断方案生成主流程。

    日志:
        - 入参需求摘要；
        - LLM 调用耗时与判定结果；
        - reason 用于调试。
    """

    logger.info("开始意图识别: requirement=%s", requirement[:100])
    start_ts = time.perf_counter()

    # 组装 prompt：把检查项清单（源自 _RAW_CHECK_ITEMS 的精炼视图）注入。
    check_items_text = format_check_items_for_prompt()

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=IntentResult,
        llm=llm,
        prompt_template_str=INTENT_PROMPT_TEMPLATE,
        verbose=False,
    )

    logger.info(
        "调用 LLM 进行意图识别: llm=%s",
        getattr(llm, "model", getattr(llm, "model_name", type(llm).__name__)),
    )

    try:
        result: IntentResult = program(
            check_items=check_items_text,
            requirement=requirement,
        )
    except Exception as exc:
        # 异常兜底：意图识别失败时默认放行，保证主流程可用性优先。
        elapsed = time.perf_counter() - start_ts
        logger.warning(
            "意图识别 LLM 调用异常，默认放行: error=%s,耗时=%.2fs",
            exc,
            elapsed,
        )
        return IntentResult(
            is_quality_requirement=True,
            reason=f"意图识别异常，默认放行: {exc}",
            suggestion="",
        )

    elapsed = time.perf_counter() - start_ts
    logger.info(
        "意图识别完成: is_quality_requirement=%s, reason=%s, 耗时=%.2fs",
        result.is_quality_requirement,
        result.reason,
        elapsed,
    )
    return result


def intent_result_to_dict(result: IntentResult) -> dict[str, Any]:
    """把 IntentResult 序列化为前端/下游可消费的 JSON 结构。"""

    return {
        "is_quality_requirement": result.is_quality_requirement,
        "reason": result.reason,
        "suggestion": result.suggestion,
    }
