"""【Indexing 阶段】章节感知切块 + 嵌入 + Node 产物落盘。

对应 RAG 四大阶段的第二阶段:把 Loading 产出的章节级 Document 切成可检索的 Node,
并附加 embedding 向量。同时把规范 Node 按源文件导出到 src/node,便于审计切块结果。

学习要点:
    - 对结构极强的规范类文档,「先按结构粗切 → 再在章节内细切」远胜纯字符窗口切分。
    - LlamaIndex 的 SentenceSplitter 很好,但必须建立在"噪声已剔除 + 结构已分组"之上。
    - 让 Node 携带业务 Metadata(而不只是 file_name)是 RAG 质量提升的倍增器。
    - Node 落盘只保存可读的审计信息,向量仍交由 Milvus 存储,避免本地 JSON 体积过大。

业务背景:
    7 份时空数据规范都是层级编号结构(5 → 5.2 → 5.2.4 → a)b)c))。
    我们的切块必须"敬畏"这个结构,不把 5.2.4 的编号和正文切散。
    smart_chunker.smart_parse_documents 已实现:
        - 章节内 SentenceSplitter 384/64 切块(比默认 256 更适合中文)
        - 表格 Document 不切(整张表作为一个 Node)
        - 父 Document 的富 metadata 自动继承给每个 Node
    检查项清单后续由 prompt/方案生成逻辑自行优化,本阶段不再把检查项切块或写入向量库。

复用模块:
    - qualityScheme.smart_chunker.smart_parse_documents: Document→Nodes(章节感知切块+嵌入)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.schema import BaseNode, Document

from qualityScheme.smart_chunker import smart_parse_documents

logger = logging.getLogger(__name__)

# src 包目录与 Node 审计产物目录。与 src/data、src/document 保持同级,方便人工排查。
PACKAGE_DIR = Path(__file__).resolve().parent
NODE_DIR = PACKAGE_DIR / "node"


def run_indexing(
    documents: list[Document],
    embed_model: BaseEmbedding,
) -> list[BaseNode]:
    """执行 Indexing 阶段:Document → 规范 Nodes(切块+嵌入+落盘)。

    参数:
        documents: Loading 阶段产出的章节级 Document 列表(带富 metadata)。
        embed_model: 嵌入模型(用于为 Node 生成向量,写入 Milvus 时需要)。

    返回:
        spec_nodes: 规范文档切块后的 Node 列表(已嵌入,带富 metadata)。

    流程:
        1. smart_parse_documents(documents, embed_model)
           - 对 is_table=true 的 Document:不切块,整体一个 Node
           - 对正文 Document:用 SentenceSplitter 384/64 切块
           - 父 Document 的所有 metadata 自动继承给每个 Node
        2. save_nodes_to_files(spec_nodes, NODE_DIR)
           - 按 metadata.file_name 分组保存为 JSON
           - 仅保存文本和 metadata 等审计信息,不重复保存 embedding
           - 保存前清理旧 JSON,避免源文件减少或改名后留下过期 Node 产物

    日志:
        - 输入 Document 数、embed_model 名称
        - spec_nodes 数
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
    # Step 2: 将规范 Node 按源文件保存到 src/node
    # ------------------------------------------------------------------
    logger.info("Step 2: 将规范 Node 按源文件保存到 %s", NODE_DIR)
    save_nodes_to_files(spec_nodes, NODE_DIR)

    logger.info(
        "===== Indexing 阶段完成: spec_nodes=%d =====",
        len(spec_nodes),
    )
    return spec_nodes


def save_nodes_to_files(
    nodes: list[BaseNode],
    output_dir: Path,
) -> None:
    """将规范 Node 列表按源 markdown 文件分组,保存为独立 JSON 文件。

    每个源 markdown 文件对应一个 JSON 文件,文件名与源文件同名(扩展名改为 .json)。
    该产物主要用于人工查看 Indexing 阶段的切块结果,不作为向量库恢复数据源,因此默认不导出
    embedding。这样既能保留文本与 metadata 的可追溯性,又能避免每次索引后生成体积很大的
    重复向量文件。

    JSON 结构:
        {
            "source_file": "part1_数据分类与基本规定.md",
            "total_nodes": 12,
            "nodes": [
                {"node_id": "...", "text": "...", "metadata": {...}, "chunk_index": 0},
                ...
            ]
        }

    参数:
        nodes: smart_parse_documents 产出的规范文档 Node 列表。
        output_dir: 输出目录(如 src/node)。不存在会自动创建。

    日志:
        - 输出目录路径
        - 旧 JSON 清理数量
        - 每个源文件生成的 JSON 文件名与 Node 数量

    异常:
        IOError: 写入文件失败时抛出,避免调用方误以为 Indexing 产物已完整保存。
    """

    logger.info(
        "保存 Node 到文件: output_dir=%s, 总 Node 数=%d",
        output_dir,
        len(nodes),
    )

    # 创建输出目录后清理旧 JSON。src/node 是派生产物目录,清理旧文件能防止源文档删除或改名后
    # 继续残留过期 Node,从而误导人工审计结果。
    output_dir.mkdir(parents=True, exist_ok=True)
    stale_json_files = list(output_dir.glob("*.json"))
    for stale_file in stale_json_files:
        stale_file.unlink()
    if stale_json_files:
        logger.info("  已清理旧 Node JSON 文件: %d 个", len(stale_json_files))

    # 按父 Document 的 file_name 分组。Loading 阶段已经把 file_name 写入 metadata,
    # 若极端情况下缺失,使用 unknown.md 兜底,保证调试时仍能看到异常来源。
    file_groups: dict[str, list[BaseNode]] = {}
    for node in nodes:
        source_file = str((node.metadata or {}).get("file_name") or "unknown.md")
        file_groups.setdefault(source_file, []).append(node)

    logger.info("  按源文件分组: %d 个源文件", len(file_groups))

    saved_count = 0
    for source_file, grouped_nodes in file_groups.items():
        # 生成输出文件名: part1_数据分类与基本规定.md -> part1_数据分类与基本规定.json。
        output_name = Path(source_file).stem + ".json"
        output_path = output_dir / output_name

        json_data: dict[str, object] = {
            "source_file": source_file,
            "total_nodes": len(grouped_nodes),
            "nodes": [],
        }

        node_entries: list[dict[str, object]] = []
        for chunk_index, node in enumerate(grouped_nodes):
            # chunk_index 是当前源文件内的顺序编号,便于人工从 JSON 快速定位相邻切块。
            node_entries.append(
                {
                    "node_id": node.node_id,
                    "text": node.get_content(),
                    "metadata": dict(node.metadata or {}),
                    "chunk_index": chunk_index,
                }
            )
        json_data["nodes"] = node_entries

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            saved_count += 1
            logger.info(
                "  保存: %s → %s (Node 数=%d)",
                source_file,
                output_name,
                len(grouped_nodes),
            )
        except Exception as exc:
            logger.error("  保存失败: %s → %s, 错误=%s", source_file, output_name, exc)
            raise IOError(f"保存 Node 文件失败: {output_path}") from exc

    logger.info(
        "Node 保存完成: 成功保存 %d/%d 个文件, 输出目录=%s",
        saved_count,
        len(file_groups),
        output_dir,
    )
