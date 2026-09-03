"""黄金问题集的读取、保存和默认示例。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import GoldenCase


def load_cases(path: str | Path) -> list[GoldenCase]:
    """读取 JSON 黄金问题集。

    支持直接数组和 `{\"cases\": [...]}` 两种格式，方便从其他标注工具导出。
    每条记录必须包含 `query` 和至少一个 `expected_ids`。
    """

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"黄金问题文件不存在: {file_path}")
    payload = json.loads(file_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("cases")
    if not isinstance(payload, list):
        raise ValueError("黄金问题 JSON 必须是数组，或包含 cases 数组的对象")
    return [GoldenCase.from_dict(item) for item in payload]


def save_cases(cases: Iterable[GoldenCase], path: str | Path) -> None:
    """把黄金问题保存为 UTF-8 JSON，便于版本管理和人工修改。"""

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(
        json.dumps([case.to_dict() for case in cases], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def default_cases() -> list[GoldenCase]:
    """返回当前规范的五条默认黄金问题。

    Node ID 取自仓库当前 `src/node/*.json` 的真实切块产物；这些 ID 让示例能够
    直接演示 LlamaIndex RetrieverEvaluator 的标准 expected_ids 输入。
    """

    return [
        GoldenCase(
            query="什么是质检支撑库？",
            expected_ids=["00e4579d-53f3-437f-869d-54343934cd20"],
            reference_answer="质检支撑库是基于统一数据架构构建的专用数据库系统，用于存储和管理质检时空数据、标准规范，并支持查询检索和数据评估。",
            tags=["基本规定", "术语"],
        ),
        GoldenCase(
            query="检测点规范提出了哪些工作内容？",
            expected_ids=["753665a2-e7dc-4d45-88b8-d2d8f4162db6"],
            reference_answer="检测点规范提出检测点数据的采集、整理、建库和质检等工作内容。",
            tags=["检测点"],
        ),
        GoldenCase(
            query="资源数据由什么组成？",
            expected_ids=["311e811a-4639-409b-a430-17c36153a75c"],
            reference_answer="资源数据由数据体及元数据组成。数据体按文件存储和管理，元数据记录数据的说明、来源、质量、管理信息以及数据集范围。",
            tags=["资源数据", "术语"],
        ),
        GoldenCase(
            query="资源数据范围文件采用什么格式？",
            expected_ids=["c459008c-9da3-4a6c-bbf8-334032b6b0d5"],
            reference_answer="资源数据范围文件采用 shape files 格式的面文件，面范围就是数据体范围，文件命名与数据体一致。",
            tags=["资源数据", "文件规范"],
        ),
        GoldenCase(
            query="检测点规范适用于哪些工作？",
            expected_ids=["753665a2-e7dc-4d45-88b8-d2d8f4162db6"],
            reference_answer="适用于新型基础测绘与实景三维中国建设中的实景三维位置精度检测点数据采集、整理、建库和质检。",
            tags=["检测点", "范围"],
        ),
    ]
