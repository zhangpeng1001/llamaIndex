"""【Indexing 阶段】章节感知切块 + 嵌入 + 检查项 Nodes。

对应 RAG 四大阶段的第二阶段:把 Loading 产出的章节级 Document 切成可检索的 Node,
并附加 embedding 向量。同时把 28 项预定义检查项也做成 Node(用于方案生成的语义匹配)。

学习要点:
    - 对结构极强的规范类文档,「先按结构粗切 → 再在章节内细切」远胜纯字符窗口切分。
    - LlamaIndex 的 SentenceSplitter 很好,但必须建立在"噪声已剔除 + 结构已分组"之上。
    - 让 Node 携带业务 Metadata(而不只是 file_name)是 RAG 质量提升的倍增器。
    - 检查项本身就是业务知识,该入库可检索,不该只存在于 Python 常量表。

业务背景:
    7 份时空数据规范都是层级编号结构(5 → 5.2 → 5.2.4 → a)b)c))。
    我们的切块必须"敬畏"这个结构,不把 5.2.4 的编号和正文切散。
    smart_chunker.smart_parse_documents 已实现:
        - 章节内 SentenceSplitter 384/64 切块(比默认 256 更适合中文)
        - 表格 Document 不切(整张表作为一个 Node)
        - 父 Document 的富 metadata 自动继承给每个 Node
    check_items_indexer.build_check_item_nodes 把 28 项检查项转成 TextNode,
    metadata 含 doc_type=check_item,与规范文档 doc_type=data_spec 区分。

复用模块:
    - qualityScheme.smart_chunker.smart_parse_documents: Document→Nodes(章节感知切块+嵌入)
    - qualityScheme.check_items_indexer.build_check_item_nodes: 28项检查项→带embedding的TextNode
"""

from __future__ import annotations

import logging

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import BaseNode, Document

from qualityScheme.check_items_indexer import build_check_item_nodes
from qualityScheme.smart_chunker import smart_parse_documents

logger = logging.getLogger(__name__)


def run_indexing(
    documents: list[Document],
    embed_model: BaseEmbedding,
) -> tuple[list[BaseNode], list[BaseNode]]:
    """执行 Indexing 阶段:Document → Nodes(切块+嵌入) + 检查项 Nodes。

    参数:
        documents: Loading 阶段产出的章节级 Document 列表(带富 metadata)。
        embed_model: 嵌入模型(用于为 Node 生成向量,写入 Milvus 时需要)。

    返回:
        tuple (spec_nodes, check_item_nodes):
            - spec_nodes: 规范文档切块后的 Node 列表(已嵌入,带富 metadata)
            - check_item_nodes: 28 项检查项的 Node 列表(已嵌入,doc_type=check_item)

    流程:
        1. smart_parse_documents(documents, embed_model)
           - 对 is_table=true 的 Document:不切块,整体一个 Node
           - 对正文 Document:用 SentenceSplitter 384/64 切块
           - 父 Document 的所有 metadata 自动继承给每个 Node
        2. build_check_item_nodes(embed_model)
           - 把 28 项 _RAW_CHECK_ITEMS 转成 TextNode
           - semantic_text = "检查项中文名 + 说明 + 参数名列表 + 关键词"
           - metadata 含 doc_type=check_item, part_number=0(与真实规范 part1~7 区分)

    日志:
        - 输入 Document 数、embed_model 名称
        - spec_nodes 数、check_item_nodes 数
        - spec_nodes 平均长度、最小/最大长度
        - 抽样 Node 预览(前 3 个)

    异常:
        ValueError: documents 为空时抛出,避免在空数据上继续运行。
    """

    logger.info("===== Indexing 阶段开始 =====")
    logger.info(
        "  入参: Document数=%d, embed_model=%s",
        len(documents),
        getattr(embed_model, "model_name", type(embed_model).__name__),
    )

    if not documents:
        logger.error("Indexing 输入为空: documents=0")
        raise ValueError("Indexing 阶段需要非空的 Document 列表,请先执行 Loading")

    # ------------------------------------------------------------------
    # Step 1: 规范文档切块 + 嵌入
    # ------------------------------------------------------------------
    logger.info("Step 1: 规范文档章节感知切块 + 嵌入(smart_parse_documents)")
    spec_nodes = smart_parse_documents(
        documents,
        embed_model,
        # chunk_size 和 chunk_overlap 用 smart_chunker 的默认值 384/64
        # (已在 smart_chunker.DEFAULT_CHUNK_SIZE / DEFAULT_CHUNK_OVERLAP 定义)
    )
    logger.info("  规范切块完成: spec_nodes=%d", len(spec_nodes))

    # 统计切块质量
    if spec_nodes:
        lens = [len(n.get_content()) for n in spec_nodes]
        avg_len = sum(lens) / len(lens)
        logger.info(
            "  切块质量统计: 平均长度=%.1f, 最小=%d, 最大=%d",
            avg_len,
            min(lens),
            max(lens),
        )
        # 抽样记录前 3 个 Node 的关键信息
        for i in range(min(3, len(spec_nodes))):
            node = spec_nodes[i]
            preview = node.get_content().replace("\n", " ")[:80]
            md = node.metadata or {}
            logger.debug(
                "    抽样Node#%d: chars=%d, part=%s, kt=%s, chapter=%s, preview=%s…",
                i + 1,
                len(node.get_content()),
                md.get("part_number"),
                md.get("knowledge_type"),
                md.get("chapter_no"),
                preview,
            )

    # ------------------------------------------------------------------
    # Step 2: 28 项预定义检查项 → 带 embedding 的 TextNode
    # ------------------------------------------------------------------
    logger.info("Step 2: 构建检查项 Nodes(28 项预定义检查项 → TextNode + embedding)")
    check_item_nodes = build_check_item_nodes(embed_model)
    logger.info("  检查项 Nodes 构建完成: check_item_nodes=%d", len(check_item_nodes))

    # 抽样记录检查项 Node
    for i in range(min(3, len(check_item_nodes))):
        node = check_item_nodes[i]
        preview = node.get_content().replace("\n", " ")[:80]
        md = node.metadata or {}
        logger.debug(
            "    抽样检查项Node#%d: code=%s, name=%s, preview=%s…",
            i + 1,
            md.get("check_code"),
            md.get("check_name"),
            preview,
        )

    logger.info(
        "===== Indexing 阶段完成: spec_nodes=%d, check_item_nodes=%d, 总Nodes=%d =====",
        len(spec_nodes),
        len(check_item_nodes),
        len(spec_nodes) + len(check_item_nodes),
    )
    return spec_nodes, check_item_nodes
