"""来源追踪模块。

对应 demo 中 ``rag.py/format_sources``。

学习要点:
    - ``response.source_nodes``：QueryEngine 响应中携带的检索来源节点列表。
    - ``NodeWithScore``：包装了 ``node``（文本块）与 ``score``（相似度分数）。
    - ``score``：余弦相似度等度量值，范围通常在 0~1（越高越相似）。
    - metadata 来源：每个 Node 继承自父 Document 的 metadata，包含 file_name、
      file_path 等，可用于显示“这段内容出自哪份规范”。

业务背景:
    质检问答必须可溯源——回答“检测点编号规则”时应能定位到《第2部分 检测点》
    的具体条款，避免凭空生成。
"""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core.schema import NodeWithScore

logger = logging.getLogger(__name__)


def format_sources(source_nodes: list[NodeWithScore]) -> str:
    """把溯源节点格式化为适合终端阅读的多行文本。

    参数:
        source_nodes: 响应中的 source_nodes，或 retrieve 返回的节点列表。

    返回:
        多行字符串，每行格式：
            ``  1. 文件名 | score=0.8421 | 内容预览…``
        无来源时返回 ``  （无来源节点）``。

    日志:
        - 节点数量；
        - 每个节点的分数与文件名，便于在日志里快速核对检索质量。
    """

    logger.info("格式化来源: 节点数=%d", len(source_nodes))

    if not source_nodes:
        logger.info("无来源节点")
        return "  （无来源节点）"

    lines: list[str] = []
    for position, item in enumerate(source_nodes, start=1):
        file_name = item.node.metadata.get("file_name", "未知文件")
        score = f"{item.score:.4f}" if item.score is not None else "N/A"
        preview = item.node.get_content().replace("\n", " ")[:100]
        lines.append(f"  {position}. {file_name} | score={score} | {preview}…")
        logger.debug("来源 #%d: file=%s, score=%s", position, file_name, score)

    return "\n".join(lines)


def sources_to_dict(source_nodes: list[NodeWithScore]) -> list[dict[str, Any]]:
    """把溯源节点序列化为前端可消费的 JSON 结构。

    参数:
        source_nodes: 响应中的 source_nodes。

    返回:
        字典列表，每项包含:
            - ``position``: 排名序号（从 1 开始）
            - ``file_name``: 来源文件名
            - ``file_path``: 来源文件完整路径（若有）
            - ``score``: 相似度分数（保留 4 位小数）
            - ``preview``: 内容预览（前 200 字符）
            - ``node_id``: 节点 ID，便于前端定位

    日志:
        - 序列化节点数；
        - 是否存在分数缺失的节点（分数缺失会影响排序展示）。
    """

    logger.info("序列化来源为 dict: 节点数=%d", len(source_nodes))

    missing_score = 0
    items: list[dict[str, Any]] = []
    for position, item in enumerate(source_nodes, start=1):
        score = item.score
        if score is None:
            missing_score += 1
        items.append(
            {
                "position": position,
                "file_name": item.node.metadata.get("file_name", "未知文件"),
                "file_path": item.node.metadata.get("file_path"),
                "score": round(score, 4) if score is not None else None,
                "preview": item.node.get_content().replace("\n", " ")[:200],
                "node_id": item.node.node_id,
            }
        )

    if missing_score:
        logger.warning("有 %d 个来源节点缺少 score，排序展示可能异常", missing_score)

    return items
