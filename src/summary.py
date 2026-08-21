"""【全文总结】SummaryIndex + tree_summarize + 两级缓存。

学习要点:
    - SummaryIndex:把所有节点组织成可遍历的列表索引,不同于向量索引的
      "只取最相似几块"。适合"请总结这些文档"这类需要覆盖全部材料的任务。
    - tree_summarize:响应合成策略。把节点分批送给 LLM 总结,再合并各批
      摘要,最终得到一棵"摘要树",适合长文本归纳。
    - 与 compact 的区别:compact 尽量塞进一次请求,材料多时会被截断;
      tree_summarize 分批处理,覆盖更全。
    - 两级缓存:
        1. answer 缓存:相同 question 直接返回上次结果(TTL 1h),省 LLM 调用。
        2. nodes 缓存:跨 question 复用切块结果(避免每次 parse_documents)。

业务背景:
    质检规范共 7 部分约 7 万字,用户常问"请总结时空数据规范的核心内容",
    此时应遍历全部条款而非只取相似块。
    summary 接口很慢(要遍历全部节点),所以必须做缓存。

复用模块:
    - qualityScheme.summary_engine.make_summary_engine: 构造 SummaryIndex + tree_summarize 引擎
    - qualityScheme.smart_chunker.smart_parse_documents: 缓存未命中时重新切块
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core.schema import BaseNode

from qualityScheme.summary_engine import make_summary_engine

if TYPE_CHECKING:
    from .state import RuntimeState

logger = logging.getLogger(__name__)


def run_summary(state: "RuntimeState", question: str) -> dict:
    """执行全文总结:SummaryIndex + tree_summarize,带两级缓存。

    参数:
        state: RuntimeState(含 config/llm/embed_model/nodes/缓存)。
        question: 总结问题(如"请总结时空数据规范的核心内容")。

    返回:
        dict: {"answer": str, "cached": bool}
            - answer: 总结文本
            - cached: True 表示命中 answer 缓存

    流程:
        1. 查 answer 缓存(命中直接返回,省掉 LLM 调用)
        2. 查 nodes 缓存(命中省掉切块时间):
           - 优先复用 state.nodes(Indexing 阶段已切块的 spec_nodes)
           - 否则查 _summary_nodes_cache(跨 question 复用)
           - 都未命中则从 state.documents 重新切块
        3. make_summary_engine(nodes, llm) → engine.query(question)
        4. 写 answer 缓存

    日志:
        - question(截断80字符)
        - 缓存命中情况(answer/nodes)
        - nodes 数量与来源
        - 答案长度

    异常:
        RuntimeError: state 未就绪或 nodes/documents 都为空时抛出。
    """

    logger.info("===== Summary 全文总结开始 =====")
    logger.info("  入参: question=%s", question[:80])

    if not state.ready:
        logger.error("Summary 失败: state 未就绪(config/llm/embed_model 缺失)")
        raise RuntimeError("RuntimeState 未就绪,请先启动服务")

    # ------------------------------------------------------------------
    # Step 1: 查 answer 缓存(命中直接返回,省掉 LLM 调用)
    # ------------------------------------------------------------------
    cached_answer = state.get_summary_answer(question)
    if cached_answer is not None:
        logger.info("  answer 缓存命中,直接返回(跳过 LLM 调用)")
        return {"answer": cached_answer, "cached": True}

    # ------------------------------------------------------------------
    # Step 2: 获取 nodes(优先复用 state.nodes,否则切块)
    # ------------------------------------------------------------------
    nodes = _get_summary_nodes(state)
    if not nodes:
        logger.error("Summary 失败: nodes 为空,请先执行 Loading+Indexing")
        raise RuntimeError("无可用节点,请先执行 Loading 和 Indexing 阶段")

    logger.info("  使用 nodes 数=%d 做全文总结", len(nodes))

    # ------------------------------------------------------------------
    # Step 3: 构造 SummaryEngine 并查询
    # ------------------------------------------------------------------
    engine = make_summary_engine(nodes, state.llm)
    logger.info("  SummaryEngine 构造完成,开始 query...")
    response = engine.query(question)
    answer_text = str(response)
    logger.info("  总结完成: 答案长度=%d", len(answer_text))
    logger.debug("  答案预览: %s", answer_text[:200])

    # ------------------------------------------------------------------
    # Step 4: 写 answer 缓存
    # ------------------------------------------------------------------
    state.set_summary_answer(question, answer_text)

    logger.info("===== Summary 全文总结完成 =====")
    return {"answer": answer_text, "cached": False}


def _get_summary_nodes(state: "RuntimeState") -> list[BaseNode]:
    """获取总结用的 nodes,优先复用已有产物。

    优先级:
        1. state.nodes(Indexing 阶段已切块的 spec_nodes,最快)
        2. _summary_nodes_cache(跨 question 复用,避免重新切块)
        3. 从 state.documents 重新切块(最慢,但兜底)

    参数:
        state: RuntimeState。

    返回:
        Node 列表(用于构造 SummaryIndex)。

    日志:
        - nodes 来源(state.nodes / 缓存 / 重新切块)。
    """

    cfg = state.config

    # 优先级1:复用 Indexing 阶段的 spec_nodes(最快,无需任何计算)
    if state.nodes:
        logger.info("  nodes 来源: state.nodes(Indexing 阶段产物), count=%d", len(state.nodes))
        return list(state.nodes)

    # 优先级2:查 nodes 缓存(跨 question 复用)
    cached_nodes = state.get_summary_nodes(cfg.data_dir)
    if cached_nodes is not None:
        logger.info("  nodes 来源: summary 缓存, count=%d", len(cached_nodes))
        return list(cached_nodes)

    # 优先级3:从 state.documents 重新切块(最慢,兜底)
    if state.documents and state.embed_model:
        logger.info("  nodes 来源: 从 state.documents 重新切块")
        from qualityScheme.smart_chunker import smart_parse_documents

        nodes = smart_parse_documents(state.documents, state.embed_model)
        state.set_summary_nodes(cfg.data_dir, nodes)
        logger.info("  重新切块完成, count=%d, 已写入缓存", len(nodes))
        return list(nodes)

    # 都没有:无法继续
    logger.error("  无可用 nodes: state.nodes 为空, 缓存为空, state.documents 也为空")
    return []
