"""精简版质检方案生成器。

本模块只保留业务主链路：需求改写、规范检索、Prompt 组装、LLM 生成、结果校验。
检查项从同级 JSON 文件读取，Milvus 只保存规范条款；因此本模块不依赖
``qualityScheme`` 目录中的方案生成、查询分解、检查项检索或元数据过滤代码。
"""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.core.schema import NodeWithScore
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)

# 使用代码文件的绝对同级路径，避免通过不同工作目录启动服务时读错配置。
CHECK_ITEM_CATALOG_PATH = Path(__file__).with_name("scheme_check_items.json")


class CheckItemDefinition(BaseModel):
    """本地检查项字典的一项定义。

    ``paramNames`` 是下游质检引擎允许接收的唯一规则参数名集合。dataName 不属于
    params，因为它始终代表被检查图层，最终会统一放在检查项顶层字段。
    """

    checkCode: str = Field(min_length=1)
    checkName: str = Field(min_length=1)
    checkDesc: str = Field(min_length=1)
    paramNames: list[str] = Field(default_factory=list)

    def to_api_dict(self) -> dict[str, Any]:
        """转换为既有检查项接口的兼容格式。

        历史前端将 checkParam 作为 JSON 字符串直接展示，所以不能直接返回列表。
        同时保留 param_names 与 param_specs，尽量兼容可能已接入该接口的调用方。
        """

        return {
            "checkCode": self.checkCode,
            "checkName": self.checkName,
            "checkDesc": self.checkDesc,
            "checkParam": json.dumps(self.paramNames, ensure_ascii=False),
            "param_names": list(self.paramNames),
            "param_specs": [{"name": name} for name in self.paramNames],
        }


class GeneratedCheckItem(BaseModel):
    """LLM 在生成阶段允许返回的检查项结构。

    这里先宽松接收 checkName 和 dataName，目的是兼容模型偶尔遗漏或放错字段的情况；
    之后会完全以本地字典覆盖名称并清理参数，避免宽松解析把错误传给下游。
    """

    checkCode: str = Field(min_length=1)
    checkName: str | None = None
    dataName: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class GeneratedScheme(BaseModel):
    """LLM 返回的顶层方案结构，供本地校验前的 JSON 解析使用。"""

    schemeName: str = Field(min_length=1)
    description: str = Field(min_length=1)
    checkItem: list[GeneratedCheckItem] = Field(default_factory=list)


def load_check_item_catalog(
    catalog_path: Path | None = None,
) -> tuple[CheckItemDefinition, ...]:
    """加载并校验独立检查项 JSON 配置。

    参数:
        catalog_path: 测试或迁移时可指定配置路径；生产默认读取同级配置文件。

    返回:
        不可变元组，避免某个请求意外修改内存字典影响后续请求。

    异常:
        ValueError: 文件缺失、JSON 损坏、字段不合法、编码或参数名重复时抛出。
    """

    actual_path = catalog_path or CHECK_ITEM_CATALOG_PATH
    return _load_catalog_from_path(actual_path.resolve())


@lru_cache(maxsize=8)
def _load_catalog_from_path(catalog_path: Path) -> tuple[CheckItemDefinition, ...]:
    """读取指定路径的配置并按路径缓存，正常请求无需重复解析 JSON。"""

    if not catalog_path.is_file():
        raise ValueError(f"检查项配置文件不存在: {catalog_path}")

    try:
        raw_data = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"检查项配置不是合法 JSON: {catalog_path}: {exc}") from exc
    except OSError as exc:
        raise ValueError(f"读取检查项配置失败: {catalog_path}: {exc}") from exc

    if not isinstance(raw_data, list) or not raw_data:
        raise ValueError(f"检查项配置必须是非空 JSON 数组: {catalog_path}")

    try:
        definitions = tuple(CheckItemDefinition.model_validate(item) for item in raw_data)
    except ValidationError as exc:
        raise ValueError(f"检查项配置字段不合法: {catalog_path}: {exc}") from exc

    codes = [item.checkCode for item in definitions]
    if len(codes) != len(set(codes)):
        raise ValueError(f"检查项配置存在重复 checkCode: {catalog_path}")
    for item in definitions:
        if len(item.paramNames) != len(set(item.paramNames)) or any(
            not name.strip() for name in item.paramNames
        ):
            raise ValueError(f"检查项参数名为空或重复: {item.checkCode}")

    logger.info("已加载本地检查项配置: path=%s, count=%d", catalog_path, len(definitions))
    return definitions


def list_check_items() -> list[dict[str, Any]]:
    """返回前端可直接使用的检查项清单。"""

    return [item.to_api_dict() for item in load_check_item_catalog()]


def generate_scheme(
    index: VectorStoreIndex,
    llm: LLM,
    requirement: str,
    *,
    context_top_k: int = 5,
) -> dict[str, Any]:
    """执行精简方案生成链路并返回既有 API 兼容结果。

    与旧实现相比，这里不再拆分子查询、检索检查项候选或做意图识别。每个中间结果
    均由函数边界隔开，排查时可从日志快速判断问题发生在改写、检索还是模型生成阶段。
    """

    cleaned_requirement = requirement.strip()
    if not cleaned_requirement:
        raise ValueError("需求描述不能为空")

    # 请求参数由接口传入，至少取一条可避免 LlamaIndex 接收到非法 TopK。
    top_k = max(int(context_top_k), 1)
    catalog = load_check_item_catalog()
    logger.info(
        "===== 精简方案生成开始: requirement=%s, context_top_k=%d, catalog_count=%d =====",
        cleaned_requirement[:100],
        top_k,
        len(catalog),
    )

    retrieval_query = rewrite_requirement(llm, cleaned_requirement)
    nodes = retrieve_spec_context(index, retrieval_query, top_k=top_k)
    prompt = build_generation_prompt(
        requirement=cleaned_requirement,
        retrieval_query=retrieval_query,
        context_text=format_spec_context(nodes),
        catalog=catalog,
    )
    # 只在 DEBUG 写出完整 Prompt，避免 INFO 级生产日志被长规范条款淹没。
    logger.debug("方案生成完整 Prompt:\n%s", prompt)

    raw_response = complete_text(llm, prompt, stage="方案生成")
    logger.debug("方案生成 LLM 原始输出:\n%s", raw_response)
    result = normalize_scheme(parse_generated_scheme(raw_response), catalog)

    logger.info(
        "===== 精简方案生成完成: schemeName=%s, checkItem_count=%d =====",
        result["schemeName"],
        len(result["checkItem"]),
    )
    return result


def rewrite_requirement(llm: LLM, requirement: str) -> str:
    """将自然语言需求压缩为单条检索查询；失败时无损回退原需求。

    需求改写只是提升规范召回效果的辅助步骤，不能因为模型暂时不可用而让主流程中断，
    所以调用异常、空回答或异常长回答都会记录日志并改用原始输入检索。
    """

    prompt = f"""你是时空数据质检规范的检索查询改写助手。
请将下列需求改写为一条适合规范知识库检索的中文查询。
保留数据对象、字段名、阈值、唯一性、必填、坐标系等明确约束，不要增加新要求。
只输出改写后的查询文本，不要解释，不要 Markdown。

用户需求：{requirement}
"""
    try:
        rewritten = complete_text(llm, prompt, stage="需求改写")
    except Exception as exc:
        logger.warning("需求改写失败，使用原始需求检索: %s", exc)
        return requirement

    rewritten = rewritten.strip()
    if not rewritten or len(rewritten) > 500:
        logger.warning("需求改写结果为空或过长，使用原始需求检索: length=%d", len(rewritten))
        return requirement

    logger.info("需求改写完成: original=%s, rewritten=%s", requirement[:100], rewritten[:160])
    logger.debug("需求改写完整 Prompt:\n%s", prompt)
    return rewritten


def complete_text(llm: LLM, prompt: str, *, stage: str) -> str:
    """调用同步 LLM 接口，并将不同模型响应统一转换为非空文本。"""

    try:
        response = llm.complete(prompt)
    except Exception as exc:
        raise RuntimeError(f"{stage}调用 LLM 失败: {exc}") from exc

    text = str(response).strip()
    if not text:
        raise RuntimeError(f"{stage}调用 LLM 返回空文本")
    return text


def retrieve_spec_context(
    index: VectorStoreIndex,
    query: str,
    *,
    top_k: int,
) -> list[NodeWithScore]:
    """从 Milvus 检索规范条款，并在 Hybrid 不可用时自动降级。

    当前 collection 已移除检查项节点，故不再需要旧实现中繁杂的 doc_type 或
    knowledge_type 过滤。优先 Hybrid 是为了保留编号、阈值等关键词的召回能力；
    对未建稀疏向量字段的旧 collection 则退回普通向量检索，保持服务可用。
    """

    try:
        retriever = index.as_retriever(
            similarity_top_k=top_k,
            vector_store_query_mode="hybrid",
        )
        nodes = list(retriever.retrieve(query))
        mode = "hybrid"
    except Exception as hybrid_error:
        logger.warning("Hybrid 规范检索失败，回退普通向量检索: %s", hybrid_error)
        try:
            retriever = index.as_retriever(similarity_top_k=top_k)
            nodes = list(retriever.retrieve(query))
            mode = "default"
        except Exception as fallback_error:
            raise RuntimeError(f"规范检索失败: {fallback_error}") from fallback_error

    logger.info(
        "规范检索完成: mode=%s, query=%s, requested_top_k=%d, result_count=%d",
        mode,
        query[:160],
        top_k,
        len(nodes),
    )
    for position, scored_node in enumerate(nodes, start=1):
        metadata = scored_node.node.metadata or {}
        logger.info(
            "  命中#%d: score=%s, file=%s, chapter=%s, preview=%s",
            position,
            format_score(scored_node.score),
            metadata.get("file_name", "未知文件"),
            metadata.get("chapter_no", "未知章节"),
            scored_node.node.get_content().replace("\n", " ").strip()[:180],
        )
    return nodes


def format_spec_context(nodes: list[NodeWithScore]) -> str:
    """将命中的规范节点格式化为带来源的 Prompt 上下文，便于模型引用与人工追查。"""

    if not nodes:
        logger.warning("未命中规范条款，生成阶段仅可依据用户需求和本地检查项字典")
        return "（未检索到相关规范条款；不得据此编造字段名、阈值或数据编码。）"

    sections: list[str] = []
    for position, scored_node in enumerate(nodes, start=1):
        metadata = scored_node.node.metadata or {}
        source = (
            f"来源={metadata.get('file_name', '未知文件')}；"
            f"章节={metadata.get('chapter_no', '未知章节')}；"
            f"类别={metadata.get('knowledge_type', '未知')}；"
            f"相似度={format_score(scored_node.score)}"
        )
        sections.append(
            f"### 规范条款 {position}\n{source}\n{scored_node.node.get_content().strip()}"
        )

    context = "\n\n".join(sections)
    logger.debug("格式化后的规范上下文:\n%s", context)
    return context


def build_generation_prompt(
    *,
    requirement: str,
    retrieval_query: str,
    context_text: str,
    catalog: tuple[CheckItemDefinition, ...],
) -> str:
    """组装唯一一次方案生成 Prompt，将本地字典作为 checkCode 的唯一白名单。"""

    return f"""你是实景三维时空数据质检方案编排专家。请基于用户需求和规范条款，输出可由质检引擎执行的 JSON 方案。

## 用户原始需求
{requirement}

## 用于检索规范的改写查询
{retrieval_query}

## Milvus 命中的规范条款
{context_text}

## 允许使用的检查项字典
{format_catalog_for_prompt(catalog)}

## 严格输出规则
1. 只能输出一个合法 JSON 对象，不要 Markdown 代码块或解释文字。
2. 顶层必须包含 schemeName、description、checkItem。
3. checkItem 每项必须包含 checkCode、checkName、dataName、params。
4. checkCode 只能从上述字典选择；checkName 必须使用字典标准名称。
5. dataName 填被检查图层，无法确认时填 null；不得把 dataName 写入 params,填写被检查的图层名称，如'检测点'、'电杆检测线'，如果在时空数据规范上下文中能匹配到对应的英文名称，则使用其英文名称，如'检测点'的英文名称为'JCD','电杆检测线'的英文名称为'DG_CZTZX'。
6. params 只能使用字典列出的参数名；无法从需求或规范确定的值填 null。
7. fieldNames 字段名称，多个字段用英文逗号隔开（如：id,name）,使用字段在文档中的英文名称，如果没有英文名称的字段，则使用其中文名称。

输出结构示例：
{{"schemeName":"检测点质检方案","description":"检查检测点编号唯一性。","checkItem":[{{"checkCode":"QualityCheckUniqueValue","checkName":"字段唯一值检查","dataName":"JCD","params":{{"fieldNames":"id"}}}}]}}
"""


def format_catalog_for_prompt(catalog: tuple[CheckItemDefinition, ...]) -> str:
    """以紧凑文本展现全部 27 项检查项及其允许参数，避免隐藏规则散落在代码中。"""

    return "\n".join(
        f"- checkCode={item.checkCode}；checkName={item.checkName}；"
        f"说明={item.checkDesc}；params={','.join(item.paramNames) or '无'}"
        for item in catalog
    )


def parse_generated_scheme(raw_response: str) -> GeneratedScheme:
    """解析模型返回的 JSON，并兼容部分模型自动包裹的 Markdown 代码块。"""

    json_text = extract_json_object(raw_response)
    try:
        raw_data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"方案生成结果不是合法 JSON: {exc}") from exc
    try:
        return GeneratedScheme.model_validate(raw_data)
    except ValidationError as exc:
        raise RuntimeError(f"方案生成结果结构不符合约定: {exc}") from exc


def extract_json_object(raw_response: str) -> str:
    """从纯 JSON 或 fenced JSON 中提取对象，不尝试修复实际损坏的 JSON。"""

    text = raw_response.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    return text[start : end + 1] if start >= 0 and end >= start else text


def normalize_scheme(
    generated_scheme: GeneratedScheme,
    catalog: tuple[CheckItemDefinition, ...],
) -> dict[str, Any]:
    """以本地字典过滤并归一化模型输出，确保结果可被下游质检引擎执行。"""

    catalog_by_code = {item.checkCode: item for item in catalog}
    normalized_items: list[dict[str, Any]] = []
    rejected_codes: list[str] = []
    removed_param_keys: list[str] = []

    for generated_item in generated_scheme.checkItem:
        definition = catalog_by_code.get(generated_item.checkCode)
        if definition is None:
            rejected_codes.append(generated_item.checkCode)
            continue

        raw_params = dict(generated_item.params)
        # 兼容旧 Prompt 习惯：dataName/data_name 即使放进 params，也只会保留到顶层。
        data_name = clean_optional_text(generated_item.dataName)
        if data_name is None:
            data_name = clean_optional_text(raw_params.get("dataName"))
        if data_name is None:
            data_name = clean_optional_text(raw_params.get("data_name"))
        raw_params.pop("dataName", None)
        raw_params.pop("data_name", None)

        unexpected_names = sorted(set(raw_params) - set(definition.paramNames))
        removed_param_keys.extend(
            f"{definition.checkCode}.{name}" for name in unexpected_names
        )
        # 每个声明参数都保留，即便无法确定也用 null，避免下游再判断键是否存在。
        params = {
            name: normalize_param_value(raw_params.get(name))
            for name in definition.paramNames
        }
        normalized_items.append(
            {
                "checkCode": definition.checkCode,
                "checkName": definition.checkName,
                "dataName": data_name,
                "params": params,
            }
        )

    logger.info(
        "方案后处理完成: generated=%d, valid=%d, rejected_codes=%s, removed_param_keys=%s",
        len(generated_scheme.checkItem),
        len(normalized_items),
        rejected_codes,
        removed_param_keys,
    )
    if not normalized_items:
        raise RuntimeError("模型没有生成可执行检查项：所有 checkCode 均不在本地检查项字典中")

    return {
        "schemeName": generated_scheme.schemeName.strip(),
        "description": generated_scheme.description.strip(),
        "checkItem": normalized_items,
    }


def normalize_param_value(value: Any) -> Any:
    """把模型偶尔生成的参数数组转成下游约定的英文逗号字符串。"""

    if isinstance(value, list):
        return ",".join(str(item).strip() for item in value if str(item).strip())
    return value.strip() if isinstance(value, str) else value


def clean_optional_text(value: Any) -> str | None:
    """将空白或非字符串图层名视为未知，避免写入无意义数据。"""

    return value.strip() or None if isinstance(value, str) else None


def format_score(score: float | None) -> str:
    """安全格式化可能为空的检索分数，日志错误不应影响主流程。"""

    return f"{score:.4f}" if isinstance(score, (int, float)) else "未知"
