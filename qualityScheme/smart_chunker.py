"""结构感知切块器（Smart Chunker）。

解决原 document_parser.py 的 SentenceSplitter 纯按字符切块的问题：
    1. 章节边界（5.2.4 编号 + 标题）被切断，a)b)c) 子条款归属丢失
    2. 噪声行（TOC/页眉/页码）没过滤，占用 Chunk 空间稀释语义
    3. 256 字符一刀切对中文规范太短，384 更合适
    4. 表格行被切散导致整张表语义破碎

切块策略：
    Step 1: 预过滤 — 剔除 metadata 标记为 is_noise 的行（TOC/页眉/页码/前言推荐项可选）
    Step 2: 按 chapter_path 分组 — 相同章节路径下的行先聚合为「章节块」
    Step 3: 章节内细切 — 在章节内按条款（a)b)c)、句号、换行）使用 SentenceSplitter 384/64 切
    Step 4: 表格特殊处理 — 标记 is_table=true 的连续行合并为整块，不切
    Step 5: 继承富 Metadata — 每个 Node 携带 10+ 业务字段（part_number/chapter/knowledge_type 等）

学习要点：
    - 对结构极强的规范类文档，「先按结构粗切 → 再在章节内细切」远胜纯字符窗口切分。
    - LlamaIndex 的 SentenceSplitter 很好，但必须建立在"噪声已剔除 + 结构已分组"之上。
    - 让 Node 携带业务 Metadata（而不只是 file_name）是 RAG 质量提升的倍增器。

业务背景：
    7 份时空数据规范都是层级编号结构（5 → 5.2 → 5.2.4 → a)b)c)）。
    我们的切块必须"敬畏"这个结构，不把 5.2.4 的编号和正文切散。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode, Document, TextNode

from .enhanced_extractor import EnhancedPdfExtractor, ExtractedLine, run_enhanced_extraction

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# 优化后的切块参数（在原256/40基础上调整，更适合中文规范）
DEFAULT_CHUNK_SIZE = 384
DEFAULT_CHUNK_OVERLAP = 64

# 建议过滤的噪声 knowledge_type（会被直接排除，不进入Chunk）
DEFAULT_NOISE_KTYPES: frozenset[str] = frozenset(
    {"toc_noise", "preface", "references", "scope_intro"}
)
# 可选过滤：也可以把 term_definition 单独保留做术语索引
DEFAULT_LOW_VALUE_SECTIONS: frozenset[str] = frozenset(
    {"前言/引言", "范围", "引用文件", "参考文献"}
)


# ---------------------------------------------------------------------------
# 1. 从 Enhanced MD 文件中提取带 Metadata 的 Document 列表
# ---------------------------------------------------------------------------


MD_META_RE = re.compile(r"<!--\s*(.+?)\s*-->")


def _parse_md_meta_comment(line: str) -> dict[str, str] | None:
    """解析 Markdown 行开头的 <!-- chapter_no=5.2.4; ... --> 注释。"""
    m = MD_META_RE.match(line.strip())
    if not m:
        return None
    body = m.group(1)
    out: dict[str, str] = {}
    for part in body.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out or None


def _extract_doc_meta_from_filename(file_name: str) -> dict[str, Any]:
    """从文件名 part2_检测点.md 推断 part_number 和 part_name。"""
    m = re.match(r"^part(\d+)_(.+)\.md$", file_name)
    if m:
        return {
            "part_number": int(m.group(1)),
            "part_name": m.group(2).replace("_", " "),
        }
    return {"part_number": None, "part_name": file_name}


def load_documents_with_enhanced_metadata(
    data_dir: Path,
    *,
    exclude_low_value_sections: bool = True,
    exclude_noise_knowledge: bool = True,
) -> list[Document]:
    """加载 data_dir 下的 MD 文件，解析每个 section 的富 Metadata，生成 Document 列表。

    与 document_loader.load_documents 的区别：
        - 读取 enhanced_extractor 输出的 MD，解析每一行注释里的 chapter_no / knowledge_type 等
        - 把相邻相同 chapter_path 的行聚合，生成「一段正文一个 Document」（Document 比整文件粒度更细）
        - 每个 Document 注入富 metadata：part_number、chapter_no、knowledge_type、data_name 等
        - 可选项：直接剔除前言/目录/引用等低价值段落，不进入语料

    参数:
        exclude_low_value_sections: True 时排除 section_type ∈ {前言/引言, 范围, 引用文件, 参考文献}
        exclude_noise_knowledge: True 时排除 knowledge_type ∈ toc_noise/preface/references
    """
    logger.info(
        "加载增强MD: dir=%s, exclude_low_value=%s, exclude_noise_know=%s",
        data_dir,
        exclude_low_value_sections,
        exclude_noise_knowledge,
    )
    md_files = sorted(data_dir.glob("*.md"))
    if not md_files:
        raise RuntimeError(f"增强MD目录为空: {data_dir}")

    documents: list[Document] = []
    skip_low_value = DEFAULT_LOW_VALUE_SECTIONS if exclude_low_value_sections else frozenset()
    skip_noise_kt = DEFAULT_NOISE_KTYPES if exclude_noise_knowledge else frozenset()

    for md_path in md_files:
        logger.debug("  处理文件: %s", md_path.name)
        file_meta = _extract_doc_meta_from_filename(md_path.name)
        raw_text = md_path.read_text(encoding="utf-8")
        lines = raw_text.splitlines()

        # 按 chapter_path 分组：相同章节路径的行聚合成一个 Document
        # Key = (chapter_no or "document_level", chapter_path or "root")
        current_chapter_no: str | None = None
        current_chapter_title: str | None = None
        current_chapter_path: str | None = None
        current_section_type = "正文_其他"
        current_knowledge_type = "正文_其他"
        current_is_table = False
        current_data_names: list[str] = file_meta.get("part_name") and [file_meta["part_name"]] or []
        current_field_names: list[str] = []
        current_param_hints: list[str] = []
        buffer: list[str] = []
        chapter_doc_count = 0

        def flush() -> None:
            nonlocal buffer, chapter_doc_count
            if not buffer:
                return
            text = "\n".join(buffer).strip()
            if not text:
                buffer = []
                return
            # 低价值过滤
            if current_section_type in skip_low_value:
                buffer = []
                return
            if current_knowledge_type in skip_noise_kt:
                buffer = []
                return
            chapter_doc_count += 1
            doc_meta: dict[str, Any] = {
                "file_name": md_path.name,
                "file_path": str(md_path),
                **file_meta,
                "section_type": current_section_type,
                "knowledge_type": current_knowledge_type,
                "is_table": current_is_table,
            }
            if current_chapter_no:
                doc_meta["chapter_no"] = current_chapter_no
            if current_chapter_title:
                doc_meta["chapter_title"] = current_chapter_title
            if current_chapter_path:
                doc_meta["chapter_path"] = current_chapter_path
            if current_data_names:
                # 序列化为 JSON 字符串（metadata scalar 兼容 Milvus 字符串字段）
                doc_meta["data_name"] = ", ".join(current_data_names)
            if current_field_names:
                doc_meta["field_name"] = ", ".join(current_field_names)
            if current_param_hints:
                doc_meta["param_hint"] = ", ".join(current_param_hints)
            doc = Document(text=text, metadata=doc_meta)
            documents.append(doc)
            buffer = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                # 空行：作为段落分隔，但若章节没变就保留在buffer
                buffer.append("")
                continue

            # 解析章节元数据注释
            meta_map = _parse_md_meta_comment(stripped)
            if meta_map:
                # 如果章节变了 → 先flush上一节
                new_chapter_no = meta_map.get("chapter_no") or current_chapter_no
                new_section = meta_map.get("section_type") or current_section_type
                new_ktype = meta_map.get("knowledge_type") or current_knowledge_type
                new_title = meta_map.get("chapter_title") or current_chapter_title
                if (
                    new_chapter_no != current_chapter_no
                    or new_section != current_section_type
                    or new_ktype != current_knowledge_type
                ):
                    flush()
                    current_chapter_no = new_chapter_no
                    current_section_type = new_section
                    current_knowledge_type = new_ktype
                    current_chapter_title = new_title
                    if new_chapter_no:
                        # 简单重建 chapter_path（增强MD只注释了当前号，路径靠栈）
                        if not current_chapter_path or current_chapter_no is None:
                            current_chapter_path = new_chapter_no
                        else:
                            # 对比层级，如果新编号层级更深则拼接
                            cur_depth = (current_chapter_path or "").count("/") + 1
                            new_depth = new_chapter_no.count(".") + 1
                            if new_depth > cur_depth and current_chapter_path:
                                current_chapter_path = f"{current_chapter_path}/{new_chapter_no}"
                            else:
                                current_chapter_path = new_chapter_no
                # 去掉注释后内容
                rest = stripped
                if stripped.startswith("<!--"):
                    end = stripped.find("-->")
                    if end != -1:
                        rest = stripped[end + 3 :].strip()
                if rest:
                    # 是否是 MD 标题行（# 开头），如果是，作为正文也加入buffer
                    if rest.startswith("#"):
                        buffer.append(rest.lstrip("#").strip())
                    else:
                        buffer.append(rest)
                continue

            # 表格启发式：含 | 分隔符且不是注释
            if stripped.count("|") >= 2:
                current_is_table = True

            buffer.append(stripped)

        # 文件结束 flush 最后一段
        flush()
        logger.debug(
            "    文件 %s → 生成 %d 个Document(章节粒度)",
            md_path.name,
            chapter_doc_count,
        )

    logger.info(
        "增强加载完成: 文件数=%d, 文档(章节级)数=%d",
        len(md_files),
        len(documents),
    )
    # 统计分布日志
    _log_doc_distribution(documents)
    return documents


def _log_doc_distribution(docs: list[Document]) -> None:
    ktype_cnt: dict[str, int] = {}
    part_cnt: dict[str, int] = {}
    for d in docs:
        kt = d.metadata.get("knowledge_type", "?")
        ktype_cnt[kt] = ktype_cnt.get(kt, 0) + 1
        pn = f"part{d.metadata.get('part_number', '?')}"
        part_cnt[pn] = part_cnt.get(pn, 0) + 1
    logger.info("  knowledge_type分布: %s", ktype_cnt)
    logger.info("  part分布: %s", part_cnt)


# ---------------------------------------------------------------------------
# 2. Smart Chunker：章节感知 → 章节内 SentenceSplitter
# ---------------------------------------------------------------------------


def smart_parse_documents(
    documents: list[Document],
    embed_model: BaseEmbedding,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    keep_tables_whole: bool = True,
) -> list[BaseNode]:
    """结构感知切块：对章节级Document列表切块，输出带富Metadata的Node。

    策略：
        - 对 is_table=true 的 Document：不切块，整体一个 Node（或当超长时按行切）
        - 对正文 Document：用 SentenceSplitter 384/64 切块（比默认256更适合中文）
        - 切块后，父 Document 的所有 metadata 自动继承给每个 Node

    参数:
        documents: load_documents_with_enhanced_metadata 返回的章节级Document列表
        embed_model: 嵌入模型
        chunk_size: 非表格Chunk的目标字符数
        chunk_overlap: 重叠字符数
        keep_tables_whole: True 表格Document不切
    """
    logger.info(
        "Smart切块开始: 章节Document数=%d, chunk_size=%d, overlap=%d, keep_tables_whole=%s",
        len(documents),
        chunk_size,
        chunk_overlap,
        keep_tables_whole,
    )

    # 分开处理 表格Document 和 正文Document
    table_docs: list[Document] = []
    normal_docs: list[Document] = []
    for d in documents:
        if d.metadata.get("is_table") and keep_tables_whole:
            table_docs.append(d)
        else:
            normal_docs.append(d)
    logger.info("  分类: 表格Document=%d, 正文Document=%d", len(table_docs), len(normal_docs))

    all_nodes: list[BaseNode] = []

    # --- 正文：用 IngestionPipeline 切块 + 嵌入 ---
    if normal_docs:
        splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        pipeline = IngestionPipeline(transformations=[splitter, embed_model])
        normal_nodes = list(pipeline.run(documents=normal_docs, show_progress=False))
        all_nodes.extend(normal_nodes)
        logger.info("  正文切块完成: Nodes=%d", len(normal_nodes))

    # --- 表格Document：不切，直接整文档→TextNode，再单独嵌入 ---
    if table_docs:
        table_nodes: list[BaseNode] = []
        for doc in table_docs:
            text = doc.get_content()
            if len(text) > chunk_size * 4 and keep_tables_whole:
                # 超长表：还是简单切一下（按行切，保持每行完整）
                tbl_splitter = SentenceSplitter(
                    chunk_size=chunk_size * 2, chunk_overlap=chunk_overlap,
                    paragraph_separator="\n",
                )
                sub_nodes = tbl_splitter.get_nodes_from_documents([doc])
                for sn in sub_nodes:
                    # 显式标记 is_table=true
                    sn.metadata["is_table"] = True
                table_nodes.extend(sub_nodes)
            else:
                node = TextNode(text=text, metadata=dict(doc.metadata))
                # 表头重复：作为独立字段保存（Milvus可搜索）
                table_nodes.append(node)
        # 嵌入表格Nodes
        if table_nodes:
            # IngestionPipeline 只嵌入不重切（用 identity splitter 等价）
            pipeline_only_embed = IngestionPipeline(transformations=[embed_model])
            table_nodes_embedded = list(
                pipeline_only_embed.run(nodes=table_nodes, show_progress=False)
            )
            all_nodes.extend(table_nodes_embedded)
            logger.info("  表格处理完成: Nodes=%d (已嵌入)", len(table_nodes_embedded))

    # 统计质量
    if all_nodes:
        lens = [len(n.get_content()) for n in all_nodes]
        avg_len = sum(lens) / len(lens)
        logger.info(
            "Smart切块全部完成: 总Nodes=%d, 平均长度=%.1f, 最小=%d, 最大=%d",
            len(all_nodes),
            avg_len,
            min(lens),
            max(lens),
        )
        _sample_nodes_log(all_nodes)
    return all_nodes


def _sample_nodes_log(nodes: list[BaseNode], n: int = 3) -> None:
    for i in range(min(n, len(nodes))):
        node = nodes[i]
        preview = node.get_content().replace("\n", " ")[:100]
        md_keys = sorted(node.metadata.keys()) if node.metadata else []
        logger.debug(
            "  抽样Node#%d: content_len=%d, md_keys=%s, preview=%s…",
            i + 1,
            len(node.get_content()),
            md_keys,
            preview,
        )


# ---------------------------------------------------------------------------
# 3. 便捷封装：从 standard PDF 一键到 Nodes（含重新提取）
# ---------------------------------------------------------------------------


def rebuild_from_standard_to_nodes(
    standard_dir: Path,
    output_data_dir: Path,
    embed_model: BaseEmbedding,
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    re_extract_pdf: bool = True,
) -> list[BaseNode]:
    """一键链路：standard/PDF → 增强提取MD → 章节级Document → Smart切块 → Nodes。

    用于 `/api/rebuild` 或首次启动时的全量重建。
    """
    logger.info("===== 一键重建 standard→Nodes 开始 =====")
    if re_extract_pdf:
        run_enhanced_extraction(standard_dir, output_data_dir, overwrite=True)
    docs = load_documents_with_enhanced_metadata(output_data_dir)
    nodes = smart_parse_documents(docs, embed_model, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    logger.info("===== 一键重建 standard→Nodes 完成: Nodes=%d =====", len(nodes))
    return nodes
