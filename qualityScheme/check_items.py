"""预定义检查项清单。

数据来源：质检平台对外提供的检查项字典（共 27 项）。
方案编排时，生成的 checkCode 必须出自本清单，否则视为非法。

字段含义（对齐 Java 端 `CheckItemCatalog.CheckItemDefinition`）：
    - checkCode: 检查项唯一编码，方案中引用它
    - checkName: 检查项中文名称，便于人读
    - checkDesc: 检查项说明
    - checkParam: 该检查项需要的参数名列表（JSON 字符串形式，**不含 dataName**）
    - param_specs: 参数规格列表，每项含 name/description/example，用于 prompt 与校验

设计要点（参考 Java 版本优化）：
    1. 图层名称统一作为方案检查项的顶层 `dataName` 字段，不再混入 `checkParam`/`param_names`。
       原因：每个检查项都必然依赖一个被检查图层，而规则参数才是各检查算法之间真正不同的部分；
       把二者拆开后，prompt 更清晰，下游执行也不会同时遇到 `data_name` 与 `dataName` 两套写法。
    2. 参数名直接使用平台原始命名（`dataName`/`fieldNames`/`min_length`/`min_area` 等，不转蛇形/驼峰），
       避免 LLM 输出与下游接口期望的键名出现「同名异写」问题。
    3. 不再保留 `checkObjType`/`checkRequestUrl` 字段：前者恒为 VECTOR 无业务价值；
       后者只在下游真正执行检查时使用，不参与方案生成与 LLM 选择。
"""

from __future__ import annotations

import json
from typing import Any


# 预定义检查项原始数据。参数描述/示例逐项对照 Java `CheckItemCatalog.DFINITIONS`，
# 27 项 checkCode 与 Java 版本完全一致。
_RAW_CHECK_ITEMS: list[dict[str, Any]] = [
    {
        "checkCode": "qualityCheckFieldLength",
        "checkName": "字段长度检查",
        "checkDesc": "检查字段长度是否符合定义规范",
        "checkParam": '["fieldNames","fieldLengths"]',
        "param_specs": [
            {"name": "fieldNames", "description": "要检查的字段名称，多个字段用英文逗号隔开", "example": "id,name"},
            {"name": "fieldLengths", "description": "长度要求，如10表示字段长度需小于10,直接写10,不用写小于号", "example": "10"},
        ],
    },
    {
        "checkCode": "qualityCheckRequiredFieldMismatch",
        "checkName": "必填值非空且不完全相同",
        "checkDesc": "检查必填字段非空且值不完全一致",
        "checkParam": '["fieldNames"]',
        "param_specs": [
            {"name": "fieldNames", "description": "要检查的字段名称，多个字段用英文逗号隔开", "example": "id,name"},
        ],
    },
    {
        "checkCode": "QualityCheckUniqueValue",
        "checkName": "字段唯一值检查",
        "checkDesc": "检查字段值是否唯一不重复",
        "checkParam": '["fieldNames"]',
        "param_specs": [
            {"name": "fieldNames", "description": "需检查唯一性的字段名，多个字段用英文逗号隔开", "example": "id"},
        ],
    },
    {
        "checkCode": "QualityCheckTimeValidity",
        "checkName": "时间有效性检查",
        "checkDesc": "检查时间字段是否在有效时间范围内",
        "checkParam": '["fieldNames","dateStart","dateEnd"]',
        "param_specs": [
            {"name": "fieldNames", "description": "时间字段名，多个字段用英文逗号隔开", "example": "create_time"},
            {"name": "dateStart", "description": "有效起始日期", "example": "2020-01-01"},
            {"name": "dateEnd", "description": "有效结束日期", "example": "2025-12-31"},
        ],
    },
    {
        "checkCode": "qualityCheckLineOverlap",
        "checkName": "线重叠检查",
        "checkDesc": "检查线要素是否存在重叠重合",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "QualityCheckPointOverlap",
        "checkName": "点重叠检查",
        "checkDesc": "检查点要素是否存在重叠重合",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "QualityInspectionLayerHangingPoints",
        "checkName": "线悬挂点检查",
        "checkDesc": "检查线要素是否存在悬挂点",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "QualityCheckInnerLayerBreaks",
        "checkName": "碎线检查",
        "checkDesc": "检查线要素是否存在小于最小长度的碎线",
        "checkParam": '["min_length"]',
        "param_specs": [
            {"name": "min_length", "description": "最小线长度阈值（米），小于此值为碎线,不用写小于号", "example": "0.5"},
        ],
    },
    {
        "checkCode": "qualityInspectionFeatureOverlap",
        "checkName": "面内重叠检查",
        "checkDesc": "检查面要素内部是否存在重叠",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "QualityInspectionSurfaceGapCheck",
        "checkName": "面缝隙检查",
        "checkDesc": "检查相邻面之间是否存在缝隙",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "QualityCheckInnerLayerFragments",
        "checkName": "碎面检查",
        "checkDesc": "检查面要素是否存在小于最小面积的碎面",
        "checkParam": '["min_area"]',
        "param_specs": [
            {"name": "min_area", "description": "最小面面积阈值（平方米），小于此值为碎面,不用写小于号", "example": "10"},
        ],
    },
    {
        "checkCode": "SharpAngleCheckForQC",
        "checkName": "尖锐角检查",
        "checkDesc": "检查要素是否存在小于阈值的尖锐角",
        "checkParam": '["min_angle"]',
        "param_specs": [
            {"name": "min_angle", "description": "最小角度阈值（度），小于此值为尖锐角,不用写小于号", "example": "30"},
        ],
    },
    {
        "checkCode": "QualityCheckSurfaceSelfIntersection",
        "checkName": "面自相交检查",
        "checkDesc": "检查面要素是否存在自相交问题",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "QualityCheckVoidInspection",
        "checkName": "面要素空洞检查",
        "checkDesc": "检查面要素是否存在无效空洞",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "layerPolygonAreaConsistencyCheck",
        "checkName": "面积与记录值一致性",
        "checkDesc": "检查图层面要素面积与记录值是否一致",
        "checkParam": '["fieldNames","threshold","unit"]',
        "param_specs": [
            {"name": "fieldNames", "description": "面积字段名，多个字段用英文逗号隔开", "example": "area"},
            {"name": "threshold", "description": "面积误差阈值，如0.1表示误差不超过10%", "example": "0.1"},
            {"name": "unit", "description": "面积单位", "example": "平方米"},
        ],
    },
    {
        "checkCode": "qualityCheckDecimalPlaces",
        "checkName": "小数位数检查",
        "checkDesc": "检查数值字段小数位数是否符合要求",
        "checkParam": '["fieldNames","fieldScales"]',
        "param_specs": [
            {"name": "fieldNames", "description": "数值字段名，多个字段用英文逗号隔开", "example": "price"},
            {"name": "fieldScales", "description": "小数位数要求，如2表示小数不超过2位,不用写小于号", "example": "2"},
        ],
    },
    {
        "checkCode": "QualityCheckRangeValidation",
        "checkName": "范围值域检查",
        "checkDesc": "检查字段值是否在规定值域范围内，主要用于枚举值，如性别：1,2",
        "checkParam": '["fieldNames","fieldValues"]',
        "param_specs": [
            {"name": "fieldNames", "description": "字段名，多个字段用英文逗号隔开", "example": "type"},
            {"name": "fieldValues", "description": "允许的值域列表，多个用英文逗号隔开", "example": "1,2,3"},
        ],
    },
    {
        "checkCode": "qualityCheckInvalidFieldValue",
        "checkName": "字段非法字符检查",
        "checkDesc": "检查字段值是否包含非法字符",
        "checkParam": '["fieldNames"]',
        "param_specs": [
            {"name": "fieldNames", "description": "字段名，多个字段用英文逗号隔开", "example": "name"},
        ],
    },
    {
        "checkCode": "qualityCheckCodeNameMatch",
        "checkName": "编码名称匹配检查",
        "checkDesc": "检查字段编码与名称是否匹配一致",
        "checkParam": '["fieldNames","fieldValues"]',
        "param_specs": [
            {"name": "fieldNames", "description": "编码字段名，多个字段用英文逗号隔开", "example": "code"},
            {"name": "fieldValues", "description": "对应的名称值列表，多个用英文逗号隔开", "example": "居住用地,商业用地"},
        ],
    },
    {
        "checkCode": "QualityCheckCoordinateSystem",
        "checkName": "平面坐标系检查",
        "checkDesc": "检查图层是否使用平面坐标系",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "qualityCheckFieldRequiredValidation",
        "checkName": "字段必填非空",
        "checkDesc": "检查指定字段是否必填且不为空",
        "checkParam": '["fieldNames"]',
        "param_specs": [
            {"name": "fieldNames", "description": "必填字段名，多个字段用英文逗号隔开", "example": "id,name"},
        ],
    },
    {
        "checkCode": "QualityCheckFieldIntegrity",
        "checkName": "属性字段完整性",
        "checkDesc": "检查属性字段是否完整、符合规范",
        "checkParam": '["fieldNames","fieldTypes","fieldLengths"]',
        "param_specs": [
            {"name": "fieldNames", "description": "字段名，多个字段用英文逗号隔开", "example": "id,name"},
            {"name": "fieldTypes", "description": "字段类型要求，多个用英文逗号隔开", "example": "String,Integer"},
            {"name": "fieldLengths", "description": "字段长度要求，多个用英文逗号隔开", "example": "10,20"},
        ],
    },
    {
        "checkCode": "checkLayerElementEmptyGeometry",
        "checkName": "空几何检查",
        "checkDesc": "检查图层要素是否存在空几何对象",
        "checkParam": "[]",
        "param_specs": [],
    },
    {
        "checkCode": "QualityCheckLayerIntegrity",
        "checkName": "图层完整性",
        "checkDesc": "检查图层数据完整性",
        "checkParam": '["geometry_type"]',
        "param_specs": [
            {"name": "geometry_type", "description": "要求的几何类型，如Point、LineString、Polygon", "example": "Polygon"},
        ],
    },
    {
        "checkCode": "checkInterLayerAttributeConsistency",
        "checkName": "图层间属性一致性",
        "checkDesc": "检查不同图层之间属性信息是否一致",
        "checkParam": '["dz_data_name","compare_fields_first","compare_fields_second"]',
        "param_specs": [
            {"name": "dz_data_name", "description": "对照图层名称", "example": "xzq"},
            {"name": "compare_fields_first", "description": "主图层比较字段名", "example": "code"},
            {"name": "compare_fields_second", "description": "对照图层比较字段名", "example": "dm"},
        ],
    },
    {
        "checkCode": "CheckPolygonContainedAttrEqual",
        "checkName": "多边形被包含且属性相等",
        "checkDesc": "检查多边形是否被包含且对应属性值相等",
        "checkParam": '["dz_data_name","compare_fields_first","compare_fields_second"]',
        "param_specs": [
            {"name": "dz_data_name", "description": "对照图层名称", "example": "xzq"},
            {"name": "compare_fields_first", "description": "主图层比较字段名", "example": "code"},
            {"name": "compare_fields_second", "description": "对照图层比较字段名", "example": "dm"},
        ],
    },
    {
        "checkCode": "InterLayerFeatureConsistencyCheck",
        "checkName": "图层间空间属性一致性",
        "checkDesc": "检查不同图层之间空间与属性信息是否一致",
        "checkParam": '["dz_data_name","condition","key_field_first","key_field_second","compare_fields_first","compare_fields_second"]',
        "param_specs": [
            {"name": "dz_data_name", "description": "对照图层名称", "example": "xzq"},
            {"name": "condition", "description": "关联条件表达式，如code=dm", "example": "code=dm"},
            {"name": "key_field_first", "description": "主图层关联键字段", "example": "id"},
            {"name": "key_field_second", "description": "对照图层关联键字段", "example": "fid"},
            {"name": "compare_fields_first", "description": "主图层比较字段名", "example": "name"},
            {"name": "compare_fields_second", "description": "对照图层比较字段名", "example": "dzm"},
        ],
    },
]


def _normalize_param(raw: str) -> list[str]:
    """把 checkParam 字符串解析为参数名列表。

    平台字典中 checkParam 形如 ``'["fieldNames","fieldLengths"]'``，
    这里解析为 ``["fieldNames", "fieldLengths"]``，便于校验生成参数是否齐全。
    """

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (json.JSONDecodeError, TypeError):
        pass
    return []


# 规范化后的检查项列表：每项包含解析后的 param_names 与原始 param_specs。
CHECK_ITEMS: list[dict[str, Any]] = []
# checkCode -> 检查项详情，便于 O(1) 校验。
CHECK_ITEM_BY_CODE: dict[str, dict[str, Any]] = {}

for _item in _RAW_CHECK_ITEMS:
    _normalized = dict(_item)
    _normalized["param_names"] = _normalize_param(_item["checkParam"])
    # param_specs 已在 _RAW_CHECK_ITEMS 中显式声明，直接保留，供 prompt 使用。
    CHECK_ITEMS.append(_normalized)
    CHECK_ITEM_BY_CODE[_item["checkCode"]] = _normalized


def list_check_items() -> list[dict[str, Any]]:
    """返回全部检查项（含解析后的 param_names 与原始 param_specs）。"""

    return CHECK_ITEMS


def get_check_item(check_code: str) -> dict[str, Any] | None:
    """按 checkCode 查询检查项详情。"""

    return CHECK_ITEM_BY_CODE.get(check_code)


def is_valid_check_code(check_code: str) -> bool:
    """判断 checkCode 是否存在于预定义清单。"""

    return check_code in CHECK_ITEM_BY_CODE


def format_check_items_for_prompt() -> str:
    """把检查项清单格式化为供 LLM prompt 使用的结构化文本。

    对齐 Java `CheckItemCatalog.formatForPrompt()`：
        - 通用说明节：dataName/fieldNames/dz_data_name 等通用字段含义
        - 每项检查项：checkCode/checkName/checkDesc + 每参数的 description 与 example

    相比原来的简单 Markdown 表格，逐项说明能让模型明确知道每个参数的业务语义，
    减少把阈值填错参数名、或把 dataName 混入 params 的情况。
    """

    builder: list[str] = []

    # 通用说明：dataName 与反复出现的参数含义固定，先统一交代，避免逐项重复。
    builder.append("## 通用说明")
    builder.append(
        "每个检查项都有一个 dataName 字段（图层名称），填写被检查的图层名称，"
        "如'检测点'、'电杆检测线'，如果在时空数据规范上下文中能匹配到对应的英文名称，"
        "则使用其英文名称，如'检测点'的英文名称为'JCD','电杆检测线'的英文名称为'DG_CZTZX'。"
    )
    builder.append("以下参数在多个检查项中反复出现，含义固定：")
    builder.append(
        "- fieldNames：字段名称，多个字段用英文逗号隔开（如：id,name）,"
        "使用字段在文档中的英文名称，如果没有英文名称的字段，则使用其中文名称"
    )
    builder.append("- dz_data_name：对照图层名称，用于图层间一致性检查（如：xzq）")
    builder.append("")

    # 预定义检查项清单主体：逐项输出 checkCode/checkName/checkDesc 与参数规格。
    builder.append(
        f"## 预定义检查项清单（共{len(CHECK_ITEMS)}项，生成的 checkCode 必须只能来自此清单）"
    )
    builder.append("每个检查项需填写 dataName（图层名称）和下列规则参数：")
    builder.append("")

    for index, item in enumerate(CHECK_ITEMS, 1):
        builder.append(f"### {index}. {item['checkCode']} — {item['checkName']}")
        builder.append(f"说明：{item['checkDesc']}")

        param_specs = item.get("param_specs") or []
        if not param_specs:
            builder.append("规则参数：无（仅需 dataName）")
        else:
            builder.append("规则参数：")
            for spec in param_specs:
                builder.append(
                    f"  - {spec['name']}：{spec['description']}。示例：{spec['example']}"
                )
        builder.append("")

    return "\n".join(builder)
