"""黄金问题集的读取、保存和 Demo 默认数据。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .models import EvaluationCase


def load_cases(path: str | Path) -> list[EvaluationCase]:
    """从 JSON 文件加载黄金问题集。

    支持两种简单格式：
        1. 直接使用数组：`[{"question": "..."}]`
        2. 使用对象包裹：`{"cases": [{"question": "..."}]}`
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"评估数据文件不存在: {file_path}")
    data = json.loads(file_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("cases")
    if not isinstance(data, list):
        raise ValueError("评估数据必须是数组，或包含 cases 数组的对象")
    return [EvaluationCase.from_dict(item) for item in data]


def save_cases(cases: Iterable[EvaluationCase], path: str | Path) -> None:
    """把黄金问题集保存为 UTF-8 JSON，方便人工维护和版本对比。"""

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [case.to_dict() for case in cases]
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def default_cases() -> list[EvaluationCase]:
    """返回针对当前七份时空数据规范的最小可运行黄金问题集。

    这些问题只使用仓库中已经存在的事实，适合第一次运行评估时直接使用。
    后续应结合真实用户问题逐步补充，黄金集越贴近业务，指标越有参考价值。
    """

    return [
        EvaluationCase(
            question="检测点数据成果的质量要求包含哪些内容？",
            relevant_files=["part2_检测点.md"],
            relevant_keywords=["时空基准", "数据采集", "数据整理", "数据库组织", "质量要求"],
            reference_answer="检测点规范涉及时空基准、数据采集、数据整理、数据库组织与建库以及质量要求。",
            tags=["检测点", "质量"],
        ),
        EvaluationCase(
            question="资源数据的数据体和元数据分别是什么？",
            relevant_files=["part7_资源数据.md"],
            relevant_keywords=["数据体", "元数据", "文件", "空间元数据", "数据集范围"],
            reference_answer="数据体按文件存储和管理；元数据说明数据来源、质量、管理等信息，并记录数据集范围。",
            tags=["资源数据", "术语"],
        ),
        EvaluationCase(
            question="什么是质检支撑库？",
            relevant_files=["part1_数据分类与基本规定.md"],
            relevant_keywords=["统一数据架构", "专用数据库系统", "存储和管理", "查询检索", "数据评估"],
            reference_answer="质检支撑库是基于统一数据架构构建的专用数据库系统，支持质检数据和标准规范的存储管理、查询检索与数据评估。",
            tags=["基本规定", "术语"],
        ),
        EvaluationCase(
            question="资源数据范围文件采用什么格式，命名有什么要求？",
            relevant_files=["part7_资源数据.md"],
            relevant_keywords=["shape files", "面文件", "数据体范围", "命名", "一致"],
            reference_answer="范围文件采用 shape files 格式的面文件，面的范围是数据体范围，命名与数据体一致。",
            tags=["资源数据", "文件规范"],
        ),
        EvaluationCase(
            question="检测点规范的适用范围是什么？",
            relevant_files=["part2_检测点.md"],
            relevant_keywords=["新型基础测绘", "实景三维中国建设", "位置精度检测点", "采集", "质检"],
            reference_answer="适用于新型基础测绘与实景三维中国建设中的实景三维位置精度检测点数据采集、整理、建库和质检。",
            tags=["检测点", "范围"],
        ),
    ]
