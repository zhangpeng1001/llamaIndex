"""一次性脚本：把 standard 目录下的 PDF 规范文档提取为 Markdown 数据源。

提取结果写入 qualityScheme/data/，作为 RAG 流程的语料。
脚本本身不属于业务代码，可重复运行覆盖输出。
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pypdf

STANDARD_DIR = Path(__file__).resolve().parent.parent / "standard"
OUTPUT_DIR = Path(__file__).resolve().parent / "data"


def clean_text(text: str) -> str:
    """清理 PDF 抽取出的文本：去除多余空白行、页眉页脚噪声。"""

    lines = []
    prev_blank = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        # 去除孤立页码行
        if re.fullmatch(r"\s*\d+\s*", line):
            continue
        if not line.strip():
            if prev_blank:
                continue
            prev_blank = True
        else:
            prev_blank = False
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def extract_pdf(pdf_path: Path) -> str:
    """读取 PDF 全部页面文本。"""

    reader = pypdf.PdfReader(str(pdf_path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        content = page.extract_text() or ""
        pages.append(f"<!-- 第 {index} 页 -->\n{content}")
    return clean_text("\n".join(pages))


def build_markdown(pdf_path: Path, body: str) -> str:
    """为正文添加 Markdown 标题与元数据，便于检索时显示来源。"""

    # 文件名形如 "实景三维质检大数据支撑库 时空数据规范 第1部分 数据分类与基本规定.pdf"
    stem = pdf_path.stem
    return f"# {stem}\n\n> 来源：{pdf_path.name}\n\n{body}"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(STANDARD_DIR.glob("*.pdf"))
    print(f"发现 {len(pdf_files)} 个 PDF 文件")
    for pdf_path in pdf_files:
        body = extract_pdf(pdf_path)
        # 生成简短且稳定的输出文件名：part1_classification.md 之类
        match = re.search(r"第\s*(\d+)\s*部分\s*(.+?)\.pdf$", pdf_path.name)
        if match:
            part_num = match.group(1)
            part_name = re.sub(r"[\\/:*?\"<>|\s]+", "_", match.group(2).strip())
            out_name = f"part{part_num}_{part_name}.md"
        else:
            out_name = re.sub(r"[\\/:*?\"<>|\s]+", "_", pdf_path.stem) + ".md"
        out_path = OUTPUT_DIR / out_name
        out_path.write_text(
            build_markdown(pdf_path, body), encoding="utf-8"
        )
        print(f"  -> {out_name}  ({len(body)} 字符)")


if __name__ == "__main__":
    main()
