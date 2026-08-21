"""预定义检查项清单。

数据来源：质检平台对外提供的检查项字典（共 28 项）。
方案编排时，生成的 checkCode 必须出自本清单，否则视为非法。

每项字段含义:
    - checkCode: 检查项唯一编码，方案中引用它
    - checkName: 检查项中文名称，便于人读
    - checkDesc: 检查项说明
    - checkObjType: 检查对象类型（当前均为 VECTOR 矢量数据）
    - checkParam: 该检查项需要的参数名列表（JSON 字符串形式）
    - checkRequestUrl: 实际执行检查时调用的接口路径（仅记录，本模块不调用）
"""

from __future__ import annotations

import json
from typing import Any


# 预定义检查项原始数据。字段与平台字典保持一致。
_RAW_CHECK_ITEMS: list[dict[str, Any]] = [
    {
        "checkCode": "qualityCheckFieldLength",
        "checkName": "字段长度检查",
        "checkDesc": "检查字段长度是否符合定义规范",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames","fieldLengths"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/fieldvaluelength",
    },
    {
        "checkCode": "qualityCheckRequiredFieldMismatch",
        "checkName": "必填值非空且不完全相同",
        "checkDesc": "检查必填字段非空且值不完全一致",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/notnullfieldvaldifferent",
    },
    {
        "checkCode": "QualityCheckUniqueValue",
        "checkName": "字段唯一值检查",
        "checkDesc": "检查字段值是否唯一不重复",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/uniquevalue",
    },
    {
        "checkCode": "QualityCheckTimeValidity",
        "checkName": "时间有效性检查",
        "checkDesc": "检查时间字段是否在有效时间范围内",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames","dateStart","dateEnd"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/datevalid",
    },
    {
        "checkCode": "qualityCheckLineOverlap",
        "checkName": "线重叠检查",
        "checkDesc": "检查线要素是否存在重叠重合",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/linenooverlap",
    },
    {
        "checkCode": "QualityCheckPointOverlap",
        "checkName": "点重叠检查",
        "checkDesc": "检查点要素是否存在重叠重合",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/pointnooverlap",
    },
    {
        "checkCode": "QualityInspectionLayerHangingPoints",
        "checkName": "线悬挂点检查",
        "checkDesc": "检查线要素是否存在悬挂点",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/linenodangles",
    },
    {
        "checkCode": "QualityCheckInnerLayerBreaks",
        "checkName": "碎线检查",
        "checkDesc": "检查线要素是否存在小于最小长度的碎线",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","min_length"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/brokenline",
    },
    {
        "checkCode": "qualityInspectionFeatureOverlap",
        "checkName": "面内重叠检查",
        "checkDesc": "检查面要素内部是否存在重叠",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/areanooverlap",
    },
    {
        "checkCode": "QualityInspectionSurfaceGapCheck",
        "checkName": "面缝隙检查",
        "checkDesc": "检查相邻面之间是否存在缝隙",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/areanogaps",
    },
    {
        "checkCode": "QualityCheckInnerLayerFragments",
        "checkName": "碎面检查",
        "checkDesc": "检查面要素是否存在小于最小面积的碎面",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","min_area"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/miniareapolygon",
    },
    {
        "checkCode": "SharpAngleCheckForQC",
        "checkName": "尖锐角检查",
        "checkDesc": "检查要素是否存在小于阈值的尖锐角",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","min_angle"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/acuteangle",
    },
    {
        "checkCode": "QualityCheckSurfaceSelfIntersection",
        "checkName": "面自相交检查",
        "checkDesc": "检查面要素是否存在自相交问题",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/polygonnotselfintersect",
    },
    {
        "checkCode": "QualityCheckVoidInspection",
        "checkName": "面要素空洞检查",
        "checkDesc": "检查面要素是否存在无效空洞",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/polygonmustnothaveisland",
    },
    {
        "checkCode": "layerPolygonAreaConsistencyCheck",
        "checkName": "面积与记录值一致性",
        "checkDesc": "检查图层面要素面积与记录值是否一致",
        "checkObjType": "VECTOR",
        "checkParam": '["dataName","fieldNames","threshold","unit"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/layerareasame",
    },
    {
        "checkCode": "qualityCheckDecimalPlaces",
        "checkName": "小数位数检查",
        "checkDesc": "检查数值字段小数位数是否符合要求",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames","fieldScales"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/fieldvaluescale",
    },
    {
        "checkCode": "QualityCheckRangeValidation",
        "checkName": "范围值域检查",
        "checkDesc": "检查字段值是否在规定值域范围内",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames","fieldValues"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/rangecodedomain",
    },
    {
        "checkCode": "qualityCheckInvalidFieldValue",
        "checkName": "字段非法字符检查",
        "checkDesc": "检查字段值是否包含非法字符",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/invalidvalue",
    },
    {
        "checkCode": "qualityCheckCodeNameMatch",
        "checkName": "编码名称匹配检查",
        "checkDesc": "检查字段编码与名称是否匹配一致",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames","fieldValues"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/codeandname",
    },
    {
        "checkCode": "QualityCheckCoordinateSystem",
        "checkName": "平面坐标系检查",
        "checkDesc": "检查图层是否使用平面坐标系",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/planecoordinatesystem",
    },
    {
        "checkCode": "qualityCheckFieldRequiredValidation",
        "checkName": "字段必填非空",
        "checkDesc": "检查指定字段是否必填且不为空",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/fielddefnnonnull",
    },
    {
        "checkCode": "QualityCheckFieldIntegrity",
        "checkName": "属性字段完整性",
        "checkDesc": "检查属性字段是否完整、符合规范",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","fieldNames","fieldTypes","fieldLengths"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/fielddefnintegrity",
    },
    {
        "checkCode": "checkLayerElementEmptyGeometry",
        "checkName": "空几何检查",
        "checkDesc": "检查图层要素是否存在空几何对象",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/layernullgeometry",
    },
    {
        "checkCode": "QualityCheckLayerIntegrity",
        "checkName": "图层完整性",
        "checkDesc": "检查图层数据完整性",
        "checkObjType": "VECTOR",
        "checkParam": '["data_name","geometry_type"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/layerintegrity",
    },
    {
        "checkCode": "checkInterLayerAttributeConsistency",
        "checkName": "图层间属性一致性",
        "checkDesc": "检查不同图层之间属性信息是否一致",
        "checkObjType": "VECTOR",
        "checkParam": '["dataName","dz_data_name","compare_fields_first","compare_fields_second"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/attributesame",
    },
    {
        "checkCode": "CheckPolygonContainedAttrEqual",
        "checkName": "多边形被包含且属性相等",
        "checkDesc": "检查多边形是否被包含且对应属性值相等",
        "checkObjType": "VECTOR",
        "checkParam": '["dataName","dz_data_name","compare_fields_first","compare_fields_second"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/areacoveredandsameattributes",
    },
    {
        "checkCode": "InterLayerFeatureConsistencyCheck",
        "checkName": "图层间空间属性一致性",
        "checkDesc": "检查不同图层之间空间与属性信息是否一致",
        "checkObjType": "VECTOR",
        "checkParam": '["dataName","dz_data_name","condition","key_field_first","key_field_second","compare_fields_first","compare_fields_second"]',
        "checkRequestUrl": "/gis-server-light/qualitycheck/spaceandattributesame",
    },
]


def _normalize_param(raw: str) -> list[str]:
    """把 checkParam 字符串解析为参数名列表。

    平台字典中 checkParam 形如 ``'["data_name","fieldNames"]'``，
    这里解析为 ``["data_name", "fieldNames"]``，便于校验生成参数是否齐全。
    """

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (json.JSONDecodeError, TypeError):
        pass
    return []


# ---------------------------------------------------------------------------
# 参数名别名映射：解决 dataName vs data_name 这种驼峰/蛇形混用问题
# 原理：
#   1. LLM 生成参数时，Prompt 里统一引导使用「蛇形」命名（更符合中文拼音直觉）
#   2. 但平台实际 checkParam 可能是驼峰（如 dataName），所以在后处理阶段
#      需要把 LLM 生成的蛇形参数名，映射回对应检查项真正声明的参数名
# ---------------------------------------------------------------------------

# 通用「蛇形 ↔ 驼峰」双向别名表（所有检查项共享的通用别名）
COMMON_PARAM_ALIASES: dict[str, str] = {
    # 数据层名相关
    "data_name": "dataName",
    "dataname": "dataName",
    "dataName": "data_name",
    # 字段相关
    "field_names": "fieldNames",
    "fieldnames": "fieldNames",
    "fieldNames": "field_names",
    "field_types": "fieldTypes",
    "fieldtypes": "fieldTypes",
    "fieldTypes": "field_types",
    "field_lengths": "fieldLengths",
    "fieldlengths": "fieldLengths",
    "fieldLengths": "field_lengths",
    "field_scales": "fieldScales",
    "fieldscales": "fieldScales",
    "fieldScales": "field_scales",
    "field_values": "fieldValues",
    "fieldvalues": "fieldValues",
    "fieldValues": "field_values",
    # 几何/阈值相关
    "geometry_type": "geometry_type",  # 本身就是蛇形
    "min_length": "min_length",
    "min_area": "min_area",
    "min_angle": "min_angle",
    "date_start": "dateStart",
    "datestart": "dateStart",
    "dateStart": "date_start",
    "date_end": "dateEnd",
    "dateend": "dateEnd",
    "dateEnd": "date_end",
    # 跨图层相关
    "dz_data_name": "dz_data_name",  # 本身蛇形
    "compare_fields_first": "compare_fields_first",
    "compare_fields_second": "compare_fields_second",
    "key_field_first": "key_field_first",
    "key_field_second": "key_field_second",
}


def _build_param_snake_to_original(check_code: str) -> dict[str, str]:
    """为指定检查项构造「蛇形参数名 → 平台原始参数名」映射。

    例：layerPolygonAreaConsistencyCheck 的平台参数是 ["dataName","fieldNames","threshold","unit"]，
    用户/LLM可能写成 data_name / field_names。这里返回一个双向映射字典用于最后一步还原。
    """
    item = get_check_item(check_code)
    if item is None:
        return {}
    out: dict[str, str] = {}
    for orig in item["param_names"]:
        # 原始名本身就是 key
        out[orig] = orig
        # 加通用别名
        if orig in COMMON_PARAM_ALIASES:
            alias = COMMON_PARAM_ALIASES[orig]
            out[alias] = orig
        # 简单蛇形/驼峰互转兜底
        snake = _camel_to_snake(orig)
        if snake != orig:
            out[snake] = orig
        camel = _snake_to_camel(orig)
        if camel != orig:
            out[camel] = orig
    return out


def _camel_to_snake(s: str) -> str:
    import re as _re
    s1 = _re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    return _re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _snake_to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(p.title() for p in parts[1:])


def canonicalize_params(check_code: str, params: dict[str, Any]) -> dict[str, Any]:
    """把 LLM 生成的 params 字典规范化为平台检查项实际要求的参数名。

    步骤：
        1. 取该检查项的别名映射（蛇形→平台原始）
        2. 对每个 params 的 key，尝试匹配别名；若匹配则改 key
        3. 未匹配到的参数按原样保留（可能是未知的额外参数，交由下游处理）

    这解决了「平台中 data_name 和 dataName 混用，LLM 容易写错」的问题。
    """
    alias = _build_param_snake_to_original(check_code)
    if not alias:
        return dict(params)
    out: dict[str, Any] = {}
    for k, v in params.items():
        mapped_key = alias.get(k, k)  # 别名命中则替换，否则用原名
        out[mapped_key] = v
    return out


# Prompt 用的「引导LLM使用蛇形名」的参数名表。
def format_param_names_snake_case(param_names: list[str]) -> str:
    """把平台原始参数名列表，转成「蛇形（若有别名）+ 括号说明原名」的格式，
    便于 Prompt 中引导 LLM 使用统一风格。

    例：["dataName", "fieldNames"] → "data_name(即 dataName), field_names(即 fieldNames)"
    """
    parts: list[str] = []
    for orig in param_names:
        snake = _camel_to_snake(orig)
        if snake != orig:
            parts.append(f"{snake}(即 {orig})")
        else:
            parts.append(orig)
    return ", ".join(parts)


# 规范化后的检查项列表：每项包含解析后的 param_names。
CHECK_ITEMS: list[dict[str, Any]] = []
# checkCode -> 检查项详情，便于 O(1) 校验。
CHECK_ITEM_BY_CODE: dict[str, dict[str, Any]] = {}

for _item in _RAW_CHECK_ITEMS:
    _normalized = dict(_item)
    _normalized["param_names"] = _normalize_param(_item["checkParam"])
    CHECK_ITEMS.append(_normalized)
    CHECK_ITEM_BY_CODE[_item["checkCode"]] = _normalized


def list_check_items() -> list[dict[str, Any]]:
    """返回全部检查项（含解析后的 param_names）。"""

    return CHECK_ITEMS


def get_check_item(check_code: str) -> dict[str, Any] | None:
    """按 checkCode 查询检查项详情。"""

    return CHECK_ITEM_BY_CODE.get(check_code)


def is_valid_check_code(check_code: str) -> bool:
    """判断 checkCode 是否存在于预定义清单。"""

    return check_code in CHECK_ITEM_BY_CODE


def format_check_items_for_prompt() -> str:
    """把检查项清单格式化为供 LLM prompt 使用的表格文本。

    只保留 LLM 选择检查项时需要的信息：编码、名称、说明、参数名。
    """

    lines = [
        "| checkCode | checkName | checkDesc | 参数名 |",
        "|---|---|---|---|",
    ]
    for item in CHECK_ITEMS:
        param_names = ", ".join(item["param_names"])
        lines.append(
            f"| {item['checkCode']} | {item['checkName']} | {item['checkDesc']} | {param_names} |"
        )
    return "\n".join(lines)
