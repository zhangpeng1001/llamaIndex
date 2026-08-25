"""【Loading 阶段】PDF → 增强 MD → 章节级 Document(富 metadata)。

对应 RAG 四大阶段的第一阶段:把原始 PDF 规范文档转成可切块的 Document 对象。

学习要点:
    - PDF 提取不是"把字串拿出来"就完事,更重要的是去噪(TOC/页眉/页码)和结构化(章节解析)。
    - Metadata 在"源头"(提取时)注入最准确,事后推断容易错。
    - 章节级 Document(而非整文件 Document)让后续切块更精准,条款边界不被切断。

业务背景:
    7 份《时空数据规范》PDF 是 GB/T 1.1 格式标准文档,结构高度相似:
        封面 → 目录(TOC)→ 前言 → 引言 → 1 范围 → 2 引用文件 → 3 术语 →
        4 时空基准 → 5/N 具体业务章节 → 附录 → 参考文献。
    enhanced_extractor 已针对此结构调优,smart_chunker.load_documents_with_enhanced_metadata
    会按 chapter_path 聚合行,生成带富 metadata 的章节级 Document。

复用模块:
    - qualityScheme.enhanced_extractor.run_enhanced_extraction: PDF→MD(去噪+结构化)
    - qualityScheme.smart_chunker.load_documents_with_enhanced_metadata: MD→章节级Document
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from llama_index.core.schema import Document

from qualityScheme.enhanced_extractor import run_enhanced_extraction
from qualityScheme.smart_chunker import load_documents_with_enhanced_metadata

from .config import PACKAGE_DIR, STANDARD_DIR, QualitySchemeConfig

logger = logging.getLogger(__name__)

# Document 存储目录:存放按源 markdown 文件分组的 Document JSON
DOCUMENT_DIR = PACKAGE_DIR / "document"


def run_loading(
    config: QualitySchemeConfig,
    *,
    re_extract_pdf: bool = False,
) -> list[Document]:
    """执行 Loading 阶段:PDF → 增强 MD → 章节级 Document。

    参数:
        config: 质检业务配置(含 data_dir 指向 src/data,standard_dir 指向项目根 standard/)。
        re_extract_pdf: True 时从 standard/*.pdf 重新提取 MD(覆盖 src/data);
                       False 时直接读取已有 src/data/*.md。

    返回:
        章节级 Document 列表,每个 Document 携带富 metadata:
            - part_number / part_name(从文件名推断)
            - chapter_no / chapter_title / chapter_path(从 MD 注释解析)
            - knowledge_type(toc_noise/term_definition/data_spec/field_rule/quality_rule/...)
            - section_type(前言/范围/术语定义/时空基准/数据采集/...)
            - data_name / field_name / param_hint(从正文启发式提取)
            - is_table(是否为表格行)

    流程:
        1. 若 re_extract_pdf=True,调用 run_enhanced_extraction 从 PDF 重新提取 MD
        2. 若 src/data 为空且 re_extract_pdf=False,自动 fallback 复用 qualityScheme/data
        3. 调用 load_documents_with_enhanced_metadata 读取 MD 并解析章节级 Document

    日志:
        - 输入参数(re_extract_pdf)、数据目录、标准 PDF 目录
        - MD 文件数与文件清单
        - Document 总数与 metadata 分布(knowledge_type、part_number)

    异常:
        RuntimeError: 数据目录不存在或没有任何 MD 文件。
    """

    logger.info(
        "===== Loading 阶段开始 =====\n"
        "  入参: re_extract_pdf=%s, data_dir=%s, standard_dir=%s",
        re_extract_pdf,
        config.data_dir,
        STANDARD_DIR,
    )

    # ------------------------------------------------------------------
    # Step 1: 可选地从 PDF 重新提取 MD
    # ------------------------------------------------------------------
    if re_extract_pdf:
        logger.info("Step 1: 从 standard/ 重新提取 PDF → 增强 MD(覆盖 src/data)")
        if not STANDARD_DIR.exists():
            logger.error("标准 PDF 目录不存在: %s", STANDARD_DIR)
            raise RuntimeError(f"标准 PDF 目录不存在:{STANDARD_DIR}")
        pdf_files = sorted(STANDARD_DIR.glob("*.pdf"))
        logger.info("  找到 PDF 文件数: %d, 文件清单=%s",
                    len(pdf_files), [p.name for p in pdf_files])
        if not pdf_files:
            raise RuntimeError(f"标准 PDF 目录中没有 PDF 文件:{STANDARD_DIR}")
        # 调用增强提取器:去 TOC/页眉/页码 + 章节结构解析 + metadata 注释
        produced = run_enhanced_extraction(STANDARD_DIR, config.data_dir, overwrite=True)
        logger.info("  增强提取完成: 生成 MD 文件数=%d", len(produced))
    else:
        logger.info("Step 1: 跳过 PDF 提取,直接读取已有 MD")

    # ------------------------------------------------------------------
    # Step 2: 数据目录检查 + fallback
    # ------------------------------------------------------------------
    config.data_dir.mkdir(parents=True, exist_ok=True)
    md_files = sorted(config.data_dir.glob("*.md"))
    logger.info("Step 2: 数据目录检查通过, MD 文件数=%d", len(md_files))
    logger.debug("  MD 文件清单: %s", [f.name for f in md_files])

    # ------------------------------------------------------------------
    # Step 3: 读取 MD → 章节级 Document(富 metadata)
    # ------------------------------------------------------------------
    logger.info("Step 3: 加载增强 MD → 章节级 Document(解析 metadata 注释)")
    documents = load_documents_with_enhanced_metadata(config.data_dir)

    # ------------------------------------------------------------------
    # Step 4: 将 Document 按源 markdown 文件保存为 JSON
    # ------------------------------------------------------------------
    logger.info("Step 4: 将 Document 按源文件保存到 %s", DOCUMENT_DIR)
    save_documents_to_files(documents, DOCUMENT_DIR)

    _log_loading_result(documents, source_dir=config.data_dir)
    logger.info("===== Loading 阶段完成 =====")
    return documents


def _log_loading_result(documents: list[Document], *, source_dir: Path) -> None:
    """记录 Loading 结果的关键统计,便于排查语料质量。

    参数:
        documents: 加载得到的 Document 列表。
        source_dir: 数据来源目录(用于日志溯源)。
    """
    if not documents:
        logger.warning("Loading 结果为空: documents=0, source_dir=%s", source_dir)
        return

    # 统计 knowledge_type 分布
    ktype_cnt: dict[str, int] = {}
    part_cnt: dict[str, int] = {}
    total_chars = 0
    for d in documents:
        kt = d.metadata.get("knowledge_type", "?")
        ktype_cnt[kt] = ktype_cnt.get(kt, 0) + 1
        pn = f"part{d.metadata.get('part_number', '?')}"
        part_cnt[pn] = part_cnt.get(pn, 0) + 1
        total_chars += len(d.get_content())

    logger.info(
        "Loading 统计: source_dir=%s, Document数=%d, 总字符数=%d",
        source_dir,
        len(documents),
        total_chars,
    )
    logger.info("  knowledge_type 分布: %s", ktype_cnt)
    logger.info("  part_number 分布: %s", part_cnt)

    # 抽样记录前 3 个 Document 的关键信息,便于调试
    for i in range(min(3, len(documents))):
        d = documents[i]
        preview = d.get_content().replace("\n", " ")[:80]
        logger.debug(
            "  抽样Document#%d: part=%s, chapter=%s, kt=%s, chars=%d, preview=%s…",
            i + 1,
            d.metadata.get("part_number"),
            d.metadata.get("chapter_no"),
            d.metadata.get("knowledge_type"),
            len(d.get_content()),
            preview,
        )


def save_documents_to_files(
    documents: list[Document],
    output_dir: Path,
) -> None:
    """将 Document 列表按源 markdown 文件分组,保存为独立的 JSON 文件。

    每个源 markdown 文件对应一个 JSON 文件,文件名与源文件同名(扩展名改为 .json)。
    JSON 结构:
        {
            "source_file": "part1_数据分类与基本规定.md",
            "total_documents": 10,
            "documents": [
                {"text": "...", "metadata": {...}},
                ...
            ]
        }

    参数:
        documents: 从 load_documents_with_enhanced_metadata 返回的 Document 列表。
        output_dir: 输出目录(如 src/document)。不存在会自动创建。

    日志:
        - 输出目录路径
        - 每个源文件生成的 JSON 文件名与 Document 数量
        - 汇总统计

    异常:
        IOError: 写入文件失败时抛出。
    """
    logger.info(
        "保存 Document 到文件: output_dir=%s, 总 Document 数=%d",
        output_dir,
        len(documents),
    )

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 按源文件分组 Document
    file_groups: dict[str, list[Document]] = {}
    for doc in documents:
        source_file = doc.metadata.get("file_name", "unknown.md")
        if source_file not in file_groups:
            file_groups[source_file] = []
        file_groups[source_file].append(doc)

    logger.info("  按源文件分组: %d 个源文件", len(file_groups))

    # 为每个源文件生成一个 JSON
    saved_count = 0
    for source_file, docs in file_groups.items():
        # 生成输出文件名: part1_数据分类与基本规定.md -> part1_数据分类与基本规定.json
        output_name = Path(source_file).stem + ".json"
        output_path = output_dir / output_name

        # 构建 JSON 数据
        json_data: dict = {
            "source_file": source_file,
            "total_documents": len(docs),
            "documents": [],
        }

        for doc in docs:
            doc_entry: dict = {
                "text": doc.get_content(),
                "metadata": dict(doc.metadata),
            }
            json_data["documents"].append(doc_entry)

        # 写入 JSON 文件
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            saved_count += 1
            logger.info(
                "  保存: %s → %s (Document 数=%d)",
                source_file,
                output_name,
                len(docs),
            )
        except Exception as e:
            logger.error("  保存失败: %s → %s, 错误=%s", source_file, output_name, e)
            raise IOError(f"保存 Document 文件失败: {output_path}") from e

    logger.info(
        "Document 保存完成: 成功保存 %d/%d 个文件, 输出目录=%s",
        saved_count,
        len(file_groups),
        output_dir,
    )
