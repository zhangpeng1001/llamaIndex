"""质检方案自动编排模块。

功能:
    用户用一句自然语言描述质检需求（例如"检测点坐标精度不超过 0.5 米、编号唯一、
    必填字段完整"），本模块结合已向量化的时空数据规范，自动从预定义检查项清单中
    选择匹配的检查项，并推断参数，生成结构化的质检方案 JSON。

实现思路:
    1. 用已有的向量索引检索与用户需求相关的规范条款（提供业务上下文，例如
       "检测点编号规则"能让模型推断出 fieldNames 应包含"检测点编号"字段）。
    2. 把规范上下文 + 预定义检查项清单 + 用户需求组装成 prompt。
    3. 用 LLMTextCompletionProgram + Pydantic 获得可校验的结构化输出。
    4. 校验生成的 checkCode 必须在预定义清单中，过滤非法项并补齐缺失参数。

学习要点:
    - 结构化输出：LLMTextCompletionProgram + Pydantic，保证输出可被程序消费。
    - RAG 增强编排：检索规范文档作为上下文，让方案更贴合业务。
    - 输出校验：即使 LLM 偶发幻觉，也通过白名单过滤保证 checkCode 合法。
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
    format_check_items_for_prompt,
    get_check_item,
    is_valid_check_code,
)
from .metadata_filter import retrieve

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic 结构化输出模型
# ---------------------------------------------------------------------------


class CheckItem(BaseModel):
    """单个检查项的结构化输出。"""

    checkCode: str = Field(description="检查项编码，必须来自预定义清单")
    checkName: str = Field(description="检查项中文名称")
    params: dict[str, Any] = Field(
        description=(
            "检查项参数，键名必须匹配该检查项声明的参数名，"
            "值为具体参数取值（字段名、阈值等）"
        )
    )


class QualityScheme(BaseModel):
    """质检方案的结构化输出，最终交付给前端/下游系统。"""

    schemeName: str = Field(description="方案名称，简洁体现数据对象与检查重点")
    description: str = Field(description="方案描述，1-2 句说明检查目标与范围")
    checkItem: list[CheckItem] = Field(description="检查项列表")


# ---------------------------------------------------------------------------
# Prompt 模板
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """你是实景三维质检方案编排专家。请根据"用户需求"与"时空数据规范上下文"，从"预定义检查项清单"中选择合适的检查项，生成结构化质检方案。

## 时空数据规范上下文
以下是检索到的与用户需求相关的规范条款，供你推断字段名、阈值等参数：
{context}

## 预定义检查项清单（生成的 checkCode 必须只能来自此清单）
{check_items}

## 用户需求
{requirement}

## 输出要求
请输出符合下列规则的方案：
1. schemeName：简洁名称，体现数据对象与检查重点（如"检测点数据坐标与编号质检方案"）。
2. description：1-2 句描述方案目标与检查范围。
3. checkItem：根据用户需求选择最匹配的检查项，遵循：
   - checkCode 必须来自上述清单，且 checkName 与清单一致。
   - params 必须包含该检查项"参数名"列中声明的所有参数，键名与参数名完全一致。
   - 参数值推断依据：优先参考"时空数据规范上下文"（如规范中提到的字段名、坐标系、阈值），上下文不足时结合用户需求合理设定。
   - data_name 参数取用户需求中提到的数据对象中文名（如"检测点"、"检测线"）。
   - fieldNames 参数为字段名列表（数组）。
   - 不要添加用户未提及的检查项；若用户需求与某检查项无关，则不要选入。
4. 若用户需求中包含数值阈值（如"不超过0.5米"），请将其填入对应参数（如 threshold 或 min_length / min_area / min_angle）。

请直接输出结构化结果。
"""


# ---------------------------------------------------------------------------
# 核心生成函数
# ---------------------------------------------------------------------------


def _build_context_from_retrieval(
    index: VectorStoreIndex, requirement: str, *, top_k: int = 5
) -> str:
    """用向量索引检索与需求相关的规范条款，拼装成上下文文本。

    参数:
        index: 已构建的向量索引。
        requirement: 用户的自然语言需求。
        top_k: 检索返回的条款数。

    返回:
        多行文本，每行格式：``[文件名] 条款内容``。无结果时返回提示文本。
    """

    logger.info("检索规范上下文: requirement=%s, top_k=%d", requirement[:80], top_k)
    nodes = retrieve(index, requirement, top_k=top_k)
    if not nodes:
        logger.warning("未检索到相关规范条款，方案生成将缺少业务上下文")
        return "（未检索到相关规范条款）"

    lines = []
    for node in nodes:
        file_name = node.node.metadata.get("file_name", "未知文件")
        content = node.node.get_content().replace("\n", " ").strip()
        lines.append(f"[{file_name}] {content}")
    context = "\n".join(lines)
    logger.debug("规范上下文长度=%d", len(context))
    return context


def generate_scheme(
    index: VectorStoreIndex,
    llm: LLM,
    requirement: str,
    *,
    context_top_k: int = 5,
) -> QualityScheme:
    """根据自然语言需求生成质检方案。

    参数:
        index: 已构建的向量索引（用于检索规范上下文）。
        llm: 语言模型。
        requirement: 用户的自然语言质检需求。
        context_top_k: 检索规范上下文的条款数，默认 5。

    返回:
        QualityScheme 对象，已通过 checkCode 白名单校验与参数补齐。

    日志:
        - 入参需求摘要；
        - 检索到的上下文条款数；
        - LLM 原始生成的检查项数；
        - 校验后保留的合法检查项数与被过滤的非法项。
    """

    logger.info("开始生成质检方案: requirement=%s", requirement[:100])

    # 1. 检索规范上下文，让 LLM 能推断字段名/阈值等。
    context = _build_context_from_retrieval(
        index, requirement, top_k=context_top_k
    )

    # 2. 组装 prompt 并调用 LLM 生成结构化输出。
    check_items_text = format_check_items_for_prompt()
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=QualityScheme,
        llm=llm,
        prompt_template_str=PROMPT_TEMPLATE,
        verbose=False,
    )

    logger.info("调用 LLM 生成结构化方案: llm=%s", getattr(llm, "model", getattr(llm, "model_name", type(llm).__name__)))
    raw_scheme: QualityScheme = program(
        context=context,
        check_items=check_items_text,
        requirement=requirement,
    )

    logger.info(
        "LLM 原始生成: schemeName=%s, 检查项数=%d",
        raw_scheme.schemeName,
        len(raw_scheme.checkItem),
    )

    # 3. 校验 checkCode 合法性，过滤非法项并补齐缺失参数。
    valid_items: list[CheckItem] = []
    invalid_codes: list[str] = []
    for item in raw_scheme.checkItem:
        if not is_valid_check_code(item.checkCode):
            logger.warning("非法 checkCode 被过滤: %s", item.checkCode)
            invalid_codes.append(item.checkCode)
            continue
        # 用清单中的标准 checkName 覆盖，避免 LLM 写错名称。
        canonical = get_check_item(item.checkCode)
        corrected = item.model_copy(update={"checkName": canonical["checkName"]})
        # 补齐缺失的参数（值为 None），保证下游执行时不缺键。
        required_params = canonical["param_names"]
        filled_params = dict(corrected.params)
        for param_name in required_params:
            if param_name not in filled_params:
                logger.debug(
                    "补齐缺失参数: checkCode=%s, param=%s",
                    corrected.checkCode,
                    param_name,
                )
                filled_params[param_name] = None
        corrected = corrected.model_copy(update={"params": filled_params})
        valid_items.append(corrected)

    if invalid_codes:
        logger.warning("被过滤的非法 checkCode: %s", invalid_codes)

    # 4. 组装最终方案。
    scheme = raw_scheme.model_copy(update={"checkItem": valid_items})
    logger.info(
        "方案生成完成: schemeName=%s, 合法检查项=%d, 被过滤=%d",
        scheme.schemeName,
        len(scheme.checkItem),
        len(invalid_codes),
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
