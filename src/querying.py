"""【Querying 阶段】Hybrid 检索 + MetadataFilter + QueryEngine。

对应 RAG 四大阶段的第四阶段:从 Milvus 检索与用户问题最相关的规范条款,
支持 Hybrid Search(Dense + BM25 Sparse)和 8+ 业务字段 Metadata Filter。

学习要点:
    - Hybrid Search = Dense Vector + BM25 Sparse 混合检索。
      对质检规范这种"编码/代号/阈值多"的场景提升很大:
        * "GB/T 2260" 这类标准号:BM25 直接命中 → Top1
        * "检测点编号":Dense + BM25 共同加权 → 避免被"检测点坐标"语义盖过
        * "0.5米":BM25 数值关键词权重高 → 阈值相关条款前置
    - Metadata Filter 先缩小候选集,再向量检索,提升信噪比:
        * knowledge_type=quality_rule → 只取质量规则条款
        * part_number=2 → 只取第2部分检测点
        * data_name=检测点 → 只取检测点相关条款
    - QueryEngine = Retriever + Node Postprocessors + Response Synthesizer。
    - streaming=True 开启流式输出,response.response_gen 可逐 token 消费。

业务背景:
    质检规范问答以"按条款回答"为主,compact 模式足够;
    需要跨多部分综合时可切换到 refine。
    方案生成时,典型查询模式是「分两步检索」:
        Step A:用户需求 → 只检索 doc_type=check_item → Top3 候选检查项
        Step B:每个子意图 → 过滤 data_name + knowledge_type=quality_rule → 检索规范条款

复用模块:
    - qualityScheme.metadata_filter.retrieve / retrieve_by_part: Hybrid 检索 + 过滤
    - qualityScheme.query_engine.make_query_engine: Hybrid QueryEngine 构造
    - qualityScheme.source_tracker.format_sources / sources_to_dict: 来源节点序列化
"""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.llms import LLM
from llama_index.core.schema import NodeWithScore

from qualityScheme.metadata_filter import retrieve as _retrieve
from qualityScheme.metadata_filter import retrieve_by_part as _retrieve_by_part
from qualityScheme.query_engine import make_query_engine as _make_query_engine
from qualityScheme.source_tracker import format_sources, sources_to_dict

logger = logging.getLogger(__name__)


def run_querying(
    index: VectorStoreIndex,
    question: str,
    *,
    top_k: int = 5,
    file_name: str | None = None,
    part_number: int | None = None,
    use_hybrid: bool = True,
) -> list[NodeWithScore]:
    """执行纯检索(不调 LLM):默认 Hybrid,支持 file_name/part_number 过滤。

    参数:
        index: 已构建的 VectorStoreIndex(Storing 阶段产出)。
        question: 查询文本。
        top_k: 返回节点数(默认5)。
        file_name: 可选,按文件名过滤(如 part2_检测点.md)。
        part_number: 可选,按规范部分编号过滤(1~7)。设置时调用 retrieve_by_part。
        use_hybrid: True 使用 Dense + BM25 Sparse 混合检索(推荐默认)。

    返回:
        按相似度从高到低排序的节点列表(已通过 post_filter)。

    日志:
        - question(截断80字符)、top_k、filters、use_hybrid
        - Milvus 返回数、post 过滤后数、最终返回数
        - TopK 结果预览(file/score/metadata)

    异常:
        RuntimeError: index 未初始化时抛出。
    """

    logger.info(
        "===== Querying(纯检索)开始 =====\n"
        "  入参: question=%s, top_k=%d, file_name=%s, part_number=%s, hybrid=%s",
        question[:80],
        top_k,
        file_name,
        part_number,
        use_hybrid,
    )

    if index is None:
        logger.error("Querying 失败: index 未初始化")
        raise RuntimeError("VectorStoreIndex 未初始化,请先执行 Storing 阶段")

    # 按部分检索:走专用函数(Milvus 侧 ExactMatchFilter part_number)
    if part_number is not None:
        logger.info("  走按部分检索: part_number=%d", part_number)
        nodes = _retrieve_by_part(
            index,
            question,
            part_number,
            top_k=top_k,
            use_hybrid=use_hybrid,
        )
    else:
        # 通用检索:支持 file_name 过滤
        nodes = _retrieve(
            index,
            question,
            top_k=top_k,
            file_name=file_name,
            use_hybrid=use_hybrid,
        )

    logger.info(
        "===== Querying(纯检索)完成: 返回节点数=%d =====",
        len(nodes),
    )
    _log_result_nodes(nodes)
    return nodes


def retrieve_by_part(
    index: VectorStoreIndex,
    question: str,
    part_number: int,
    *,
    top_k: int = 5,
    use_hybrid: bool = True,
) -> list[NodeWithScore]:
    """按规范部分编号检索(Milvus 侧过滤,排除检查项字典)。

    参数:
        index: VectorStoreIndex。
        question: 查询文本。
        part_number: 规范部分编号(1~7)。
        top_k: 返回节点数。
        use_hybrid: True 使用 Hybrid 检索。

    返回:
        节点列表(只含指定部分的规范条款,排除 part_number=0 的检查项)。

    日志:
        - part_number、question、返回节点数。
    """

    logger.info(
        "按部分检索: part=%d, top_k=%d, question=%s",
        part_number,
        top_k,
        question[:80],
    )
    nodes = _retrieve_by_part(
        index,
        question,
        part_number,
        top_k=top_k,
        use_hybrid=use_hybrid,
    )
    _log_result_nodes(nodes)
    return nodes


def make_engine(
    index: VectorStoreIndex,
    llm: LLM,
    *,
    top_k: int = 5,
    response_mode: str = "compact",
    streaming: bool = False,
    use_hybrid: bool = True,
) -> BaseQueryEngine:
    """构造 Hybrid QueryEngine(RAG 问答/异步/流式共用)。

    参数:
        index: VectorStoreIndex。
        llm: 语言模型。
        top_k: 检索返回的节点数,默认5。
        response_mode: 响应合成模式(compact/tree_summarize/refine),默认 compact。
        streaming: 是否启用流式输出,默认 False(SSE 场景设 True)。
        use_hybrid: True 开启 Hybrid 检索(Dense + BM25 Sparse)。

    返回:
        BaseQueryEngine 实例,调用 query 或 aquery 获取响应。

    日志:
        - 引擎配置(top_k、response_mode、streaming、hybrid、llm)。
    """

    logger.info(
        "构造 QueryEngine: top_k=%d, response_mode=%s, streaming=%s, hybrid=%s, llm=%s",
        top_k,
        response_mode,
        streaming,
        use_hybrid,
        getattr(llm, "model", getattr(llm, "model_name", type(llm).__name__)),
    )
    engine = _make_query_engine(
        index,
        llm,
        top_k=top_k,
        response_mode=response_mode,
        streaming=streaming,
        use_hybrid=use_hybrid,
    )
    logger.debug("  QueryEngine 构建完成: %s", type(engine).__name__)
    return engine


def serialize_sources(nodes: list[NodeWithScore]) -> list[dict[str, Any]]:
    """把检索结果节点序列化为前端可消费的 JSON 结构。

    参数:
        nodes: 检索返回的节点列表。

    返回:
        字典列表,每项含 position/file_name/file_path/score/preview/node_id。
    """

    return sources_to_dict(nodes)


def format_sources_text(nodes: list[NodeWithScore]) -> str:
    """把检索结果节点格式化为多行文本(终端阅读用)。

    参数:
        nodes: 检索返回的节点列表。

    返回:
        多行字符串,每行格式: `  1. 文件名 | score=0.8421 | 内容预览…`
    """

    return format_sources(nodes)


def _log_result_nodes(nodes: list[NodeWithScore]) -> None:
    """记录检索结果的关键信息,便于调试与评估。

    参数:
        nodes: 检索返回的节点列表。
    """

    for pos, n in enumerate(nodes, start=1):
        score = n.score
        meta = n.node.metadata or {}
        preview = n.node.get_content().replace("\n", " ")[:80]
        logger.debug(
            "  结果#%d: score=%.4f, part=%s, kt=%s, doc_type=%s, file=%s, preview=%s…",
            pos,
            score if score is not None else float("nan"),
            meta.get("part_number", "?"),
            meta.get("knowledge_type", "?"),
            meta.get("doc_type", "?"),
            meta.get("file_name", "?"),
            preview,
        )
