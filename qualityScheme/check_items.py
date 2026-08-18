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
