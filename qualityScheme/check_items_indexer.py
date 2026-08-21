"""预定义检查项入库模块。

核心改进：
    原来的方案是「把 28 项检查项拼成 Markdown 大表格塞给 Prompt，让 LLM 读表选」。
    问题：
        1. Token 昂贵（28 项 × 每次调用）
        2. LLM 长上下文记忆力有限，长表容易漏看最合适项
        3. 用户问"编号唯一检查"时，本该先通过语义检索直接命中 QualityCheckUniqueValue，
           而不是让 LLM 读完 28 条自己匹配。

本模块把 `_RAW_CHECK_ITEMS`（28 项）也做成 TextNode，连同规范文档一起存入 Milvus：
    - Node.text = "检查项中文名 + 说明 + 参数名列表"（用于 Embedding 语义检索）
    - Node.metadata = {
        "doc_type": "check_item",  # ← 关键！和规范文档 doc_type=data_spec 区分
        "check_code": "...",
        "check_name": "...",
        "param_names_str": "data_name, fieldNames",
        "check_obj_type": "VECTOR",
        "request_url": "...",
      }
    - part_number=0 (特殊)，不与 part1~7 真实规范冲突

然后方案生成流程改为：
    用户需求 → 先 Milvus 检索 doc_type=check_item 的 Top-3 候选项
              → 只把 Top-3 的详情注入 Prompt
              → LLM 在 3 项里裁决选哪 + 填参

学习要点：
    - 「检查项」本身就是业务知识，不该只存在于 Python 常量表，应该入库可检索。
    - 通过 metadata 的 doc_type 字段区分知识类型，实现「混合知识在一个 Collection 里可分可合」
      （比拆多 Collection 更灵活，也符合 GPT 文档的方案 B）。

业务背景：
    28 项检查项是质检平台的字典表，更新频率极低（季度/年度级）。
    首次启动时构建一次即可，后续随平台字典更新时 rebuild。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.schema import BaseNode, TextNode

from .check_items import CHECK_ITEMS

logger = logging.getLogger(__name__)

# 检查项 Node 的特殊 metadata 值（用于过滤/区分）
CHECK_ITEM_DOC_TYPE = "check_item"
CHECK_ITEM_PART_NUMBER = 0
CHECK_ITEM_PART_NAME = "质检检查项字典"


def build_check_item_nodes(
    embed_model: BaseEmbedding,
    *,
    check_items: list[dict[str, Any]] | None = None,
) -> list[BaseNode]:
    """把预定义检查项列表转成带 Embedding 的 TextNode 列表，准备入库 Milvus。

    参数:
        embed_model: 嵌入模型（与规范文档使用同一个，保证向量空间一致）
        check_items: 自定义检查项列表；None 时使用 CHECK_ITEMS

    返回:
        每个检查项对应一个 Node，已嵌入；metadata 含所有字段。
    """
    items = list(check_items) if check_items is not None else list(CHECK_ITEMS)
    logger.info("构建检查项Nodes: 检查项数=%d, embed_model=%s",
                len(items),
                getattr(embed_model, "model_name", type(embed_model).__name__))

    text_nodes: list[TextNode] = []
    for item in items:
        param_names = item.get("param_names") or []
        param_names_str = ", ".join(param_names)
        # 用于 Embedding 的语义文本：自然语言描述形式，便于用户问句向量匹配
        semantic_text = (
            f"质检检查项【{item['checkName']}】（编码{item['checkCode']}）："
            f"{item['checkDesc']}。"
            f"所需参数：{param_names_str if param_names_str else '无参数'}。"
            f"检查对象类型：{item.get('checkObjType', 'VECTOR')}。"
        )
        # 另外把 "编号唯一" "非空" "必填" 等关键词作为synonyms补充（提高召回率）
        synonyms = _build_synonyms(item)
        if synonyms:
            semantic_text += f" 相关查询关键词：{', '.join(synonyms)}。"

        meta: dict[str, Any] = {
            # 业务关键过滤字段
            "doc_type": CHECK_ITEM_DOC_TYPE,
            "knowledge_type": "check_item_catalog",
            "part_number": CHECK_ITEM_PART_NUMBER,
            "part_name": CHECK_ITEM_PART_NAME,
            # 检查项自身字段
            "check_code": item["checkCode"],
            "check_name": item["checkName"],
            "check_desc": item["checkDesc"],
            "check_obj_type": item.get("checkObjType", "VECTOR"),
            "param_names_str": param_names_str,  # Milvus scalar 字符串字段，可检索
            "request_url": item.get("checkRequestUrl", ""),
            # 通用兼容字段
            "section_type": "检查项字典",
            "data_name": "质检平台检查项",
            "is_table": False,
            "is_noise": False,
        }
        node = TextNode(text=semantic_text, metadata=meta)
        text_nodes.append(node)

    logger.debug("检查项语义文本示例: Node[0]=%s", text_nodes[0].get_content()[:150] if text_nodes else "")
    # 嵌入
    pipeline = IngestionPipeline(transformations=[embed_model])
    nodes = list(pipeline.run(nodes=text_nodes, show_progress=False))
    with_emb = sum(1 for n in nodes if n.embedding is not None)
    logger.info("检查项Nodes构建完成: 总=%d, 带向量=%d", len(nodes), with_emb)
    return nodes


def _build_synonyms(item: dict[str, Any]) -> list[str]:
    """为常见检查项构造别名/关键词，提高语义召回。

    这是一个规则型小表，按业务扩展。
    思想：用户可能说"编号不能重复"，不说"字段唯一值检查"。
    """
    synonyms: list[str] = []
    code = item["checkCode"]
    name = item["checkName"]
    desc = item.get("checkDesc", "")

    # 唯一性类
    if code == "QualityCheckUniqueValue" or "唯一" in name or "不重复" in desc:
        synonyms.extend(["唯一", "不重复", "重复检查", "编号唯一", "去重", "不能重复", "重号"])
    # 必填非空类
    if code in (
        "qualityCheckFieldRequiredValidation",
        "qualityCheckRequiredFieldMismatch",
    ) or "必填" in name or "非空" in name:
        synonyms.extend(["必填", "非空", "不能为空", "必填字段", "必填非空", "不能为null", "null检查"])
    # 精度/长度/阈值类
    if "精度" in desc or "误差" in desc or "精度" in name:
        synonyms.extend(["精度", "误差", "误差范围", "位置精度", "坐标精度"])
    if "长度" in name:
        synonyms.extend(["长度", "字段长度", "字符长度", "字符数"])
    if code == "QualityCheckRangeValidation" or "值域" in name:
        synonyms.extend(["值域", "范围", "取值范围", "枚举值", "合法值"])
    # 编码匹配类
    if "编码" in name or "编码" in desc:
        synonyms.extend(["编码匹配", "编码对应", "名称编码", "代码匹配"])
    # 坐标系类
    if "坐标" in name:
        synonyms.extend(["坐标系", "平面坐标", "投影", "坐标系统", "空间参考"])
    # 几何检查类
    if "重叠" in name:
        synonyms.extend(["重叠", "重合", "不重叠"])
    if "悬挂" in name:
        synonyms.extend(["悬挂点", "悬挂线", "线头"])
    if "碎线" in name or "碎面" in name:
        synonyms.extend(["碎线", "碎面", "最小长度", "最小面积", "碎片", "细碎"])
    if "尖锐" in name or "角" in name:
        synonyms.extend(["尖锐角", "锐角", "角度阈值", "最小角度"])
    if "自相交" in name:
        synonyms.extend(["自相交", "自交叉", "面重叠自身"])
    if "空洞" in name or "面要素空洞" in name:
        synonyms.extend(["空洞", "面空洞", "内部空洞", "孤岛"])
    if "空几何" in name:
        synonyms.extend(["空几何", "几何为空", "没有形状", "空图形"])
    if "图层完整性" in name:
        synonyms.extend(["图层完整性", "几何类型", "图层结构"])
    if "图层间" in name or "InterLayer" in code or "cross" in code.lower():
        synonyms.extend(["跨图层", "图层之间", "跨图层一致性", "一致性检查"])
    if "被包含" in name:
        synonyms.extend(["包含", "被包含", "包含关系", "多边形包含"])

    # 去重保序
    seen: set[str] = set()
    result: list[str] = []
    for s in synonyms:
        if s not in seen:
            seen.add(s)
            result.append(s)
    return result[:12]  # 上限 12 个，避免过长


# ---------------------------------------------------------------------------
# 辅助：检查项候选项检索 + Prompt 格式化（给 scheme_generator 用）
# ---------------------------------------------------------------------------


def format_top_check_items_for_prompt(
    nodes: list[Any],
    *,
    max_items: int = 5,
) -> str:
    """把「通过语义检索拿到的 TopN 检查项 Node」格式化为 Prompt 里的小表格。

    替代原来「28 项全表」，只给 LLM 最相关的 3~5 项。
    """
    if not nodes:
        return "（未检索到相关检查项）"
    actual = nodes[:max_items]
    lines = [
        "| checkCode | checkName | checkDesc | 参数名 | 匹配分数 |",
        "|---|---|---|---|---|",
    ]
    for n in actual:
        try:
            meta = n.node.metadata if hasattr(n, "node") else getattr(n, "metadata", {})
            score = getattr(n, "score", None)
            score_str = f"{score:.4f}" if score is not None else "-"
            params = meta.get("param_names_str", "")
            lines.append(
                f"| {meta.get('check_code','')} | {meta.get('check_name','')} | "
                f"{meta.get('check_desc','')} | {params} | {score_str} |"
            )
        except Exception as exc:  # pragma: no cover - 调试兜底
            logger.warning("格式化候选项异常: %s", exc)
    return "\n".join(lines)


def extract_check_codes_from_nodes(nodes: list[Any]) -> list[str]:
    """从检索到的TopN检查项Nodes里提取check_code白名单。

    用于 generate_scheme 最后一步：LLM生成的checkCode如果不在这个白名单里，
    说明LLM"超出候选项范围"了，直接过滤。
    """
    codes: list[str] = []
    for n in nodes:
        try:
            meta = n.node.metadata if hasattr(n, "node") else getattr(n, "metadata", {})
            c = meta.get("check_code")
            if c and c not in codes:
                codes.append(c)
        except Exception:
            pass
    return codes
