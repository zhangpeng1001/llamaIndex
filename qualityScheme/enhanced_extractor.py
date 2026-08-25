"""增强版 PDF 规范提取器。

解决原 _extract_pdfs.py 的三大基础问题：
    1. TOC 目录引导点噪声未过滤（约 30% 语料是垃圾）
    2. 页眉页脚/前言/起草信息未过滤
    3. 章节结构未解析 + 表格完全丢失 + metadata 几乎空白

输出格式：
    保留输出到 qualityScheme/data/*.md（与原脚本兼容，便于下游读取），
    但每个 Document 额外注入 10+ 个业务 metadata 字段（在提取阶段就标记好，
    等后续切块时直接继承，不需要切块后再二次分析）。

学习要点：
    - PDF 提取不是"把字串拿出来"就完事，更重要的是**去噪**和**结构化**。
    - 对于规范类文档（GB/T 1.1 层级编号），正则+启发式远胜于纯 LayoutParser。
    - Metadata 在"源头"（提取时）注入最准确，事后推断容易错。

业务背景：
    7 份《时空数据规范》都是 GB/T 1.1 格式的标准文档，结构高度相似：
        封面 → 目录（TOC）→ 前言 → 引言 → 1 范围 → 2 引用文件 → 3 术语 →
        4 时空基准 → 5/N 具体业务章节 → 附录 → 参考文献。
    这种结构是可预测的，适合用规则精确提取。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pypdf

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 正则规则集：针对 GB/T 1.1 类标准文档调优
# ---------------------------------------------------------------------------

# 普通标题 TOC 行：标题不含点，页码为阿拉伯或罗马数字。
# 例："前 言 ........ I" "范围 ........ 1"
# 修复点1:原正则页码仅 \d+,漏掉罗马数字 I/V/X(前言页码常见);
#        标题 [^\s.] 禁点,但本正则本就不匹配含章节号的 TOC 行(由 TOC_WITH_CHAPTER_RE 处理)。
# 修复点2:引导点 [.。…·]{4,} 要求连续,但 part4 的 TOC 行引导点被空格分割
#        ("................................ ................................ ...... 1"),改为
#        (?:[.。…·]\s*){4,} 允许点间空格(part4 PDF 提取产生的格式变形)。
TOC_LINE_RE = re.compile(
    r"""^
    (?P<title>[^\s.]+(?:\s+[^\s.]+)*)   # 标题文本（不含点）
    \s*
    (?:[.。…·]\s*){4,}                  # 引导点（至少4个点，允许点间空格）
    \s*
    (?P<page>\d+|[IVXLCDM]+)\s*$        # 末尾页码（阿拉伯或罗马数字）
    """,
    re.VERBOSE,
)

# 含章节号的 TOC 行：标题前缀为章节号(含点)，如 "3.1 检测点数据分类 ........ 1"
# 单独匹配，因为 TOC_LINE_RE 的 [^\s.] 禁点规则会误伤章节号 "3.1"。
# 修复点:原 TOC_LINE_RE 漏匹配此类行,导致 "3.1 标题......1" 被 CHAPTER_TITLE_RE
#        当成正文章节标题,输出 "## 3.1 标题......1" 噪声(已确认 4 份 part 文件共 39 处)。
# 引导点同样允许点间空格,兼容 part4 的变形格式。
TOC_WITH_CHAPTER_RE = re.compile(
    r"""^
    (?P<no>\d{1,2}(?:\.\d{1,2}){0,4})   # 章节号（1-2位数字，可带子级，最多4级）
    [.、\s]+                             # 分隔符（点号/顿号/空格）
    (?P<title>[^.。…·]*?)                # 标题文本（不含引导点，允许空标题如 "3.1 .... 1"）
    \s*
    (?:[.。…·]\s*){4,}                   # 引导点（至少4个点，允许点间空格）
    \s*
    (?P<page>\d+|[IVXLCDM]+)\s*$         # 页码（阿拉伯或罗马）
    """,
    re.VERBOSE,
)

# 目录区段字面量："目  录"（中间可有多个空格，用于区段级 TOC 识别兜底）
TOC_SECTION_RE = re.compile(r"^目\s*录\s*$")

# 纯页码行：整行只有 1~4 位数字（页眉上的"1""2"）
PAGE_NUM_ONLY_RE = re.compile(r"^\s*\d{1,4}\s*$")

# 章节标题：数字层级编号开头。例："5.2.4 采集数量与方式" "附录A" "A.1"
# 修复点1:编号 \d+ 误匹配年份(如 "2025 年7 月" 被识别为 chapter_no=2025);
#         改为 \d{1,2}(?:\.\d{1,2}){0,4},限制每段1-2位(GB/T 1.1 章节号不会超过2位)。
# 修复点2:title 用 .+? 会吞掉 "........ 1" 等引导点+页码噪声(双保险,TOC_WITH_CHAPTER_RE 已先过滤);
#         改为 [^\s.。…·][^.。…·]*?,要求非空白非点开头且不含引导点。
CHAPTER_TITLE_RE = re.compile(
    r"""^
    (?P<no>(?:\d{1,2}(?:\.\d{1,2}){0,4})|(?:附录[A-Z][A-Z0-9]*(?:\.\d+)*))  # 编号（1-2位，避免误匹配年份）
    [.、\s]+                                                                 # 分隔符
    (?P<title>[^\s.。…·][^.。…·]*?)\s*$                                      # 标题（非空白非点开头，不含引导点）
    """,
    re.VERBOSE,
)

# 大章节类别：规范中的固定章节名（用于 metadata.section_type）
# 修复点1: part4 第2章标题是"2 引用文件"(缺"规范性"前缀),原正则"^2\s+规范性引用文件$"
#         不匹配 → 改为 "^2\s+规范性?引用文件$" 兼容两种写法
# 修复点2: part4/part5 第3章标题是"3 术语与定义"(用"与"而非"和"),
#         原正则 "^3\s+术语和定义" 不匹配 → 改为 "^3\s+术语[和与]定义"
# 修复点3: part4/part5 第4-9章业务章节名(选取原则/分类与代码/数据要求/数据结构/
#         数据处理/数据更新/检查方法/入库流程/数据应用)在原表中无对应规则,
#         导致 current_section 粘性继承上一章的值 → 新增覆盖规则
SECTION_TYPE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"^(前\s*言|引\s*言)$"), "前言/引言"),
    (re.compile(r"^1\s+范\s*围$"), "范围"),
    # 修复 part4: "2 引用文件"(缺"规范性"前缀)
    (re.compile(r"^2\s+规范性?引用文件$"), "引用文件"),
    # 修复 part4/part5: "3 术语与定义"(用"与"而非"和")
    (re.compile(r"^3\s+术语[和与]定义"), "术语定义"),
    (re.compile(r"^4\s+时空基准"), "时空基准"),
    # 新增 part4: "4 选取原则" / part5: "4 数据要求"
    (re.compile(r"^4\s+(数据要求|选取原则)"), "数据采集"),
    (re.compile(r"^5\s+数据采集"), "数据采集"),
    # 新增 part4: "5 分类与代码" / part5: "5 数据结构"
    (re.compile(r"^5\s+(分类与代码|数据结构)"), "数据整理"),
    (re.compile(r"^6\s+数据整理"), "数据整理"),
    # 新增 part4: "6 数据要求" / part5: "6 数据处理"
    (re.compile(r"^6\s+(数据处理|入库流程)"), "数据库"),
    # 新增 part4: "6 数据要求"(含时空基准/数学精度/属性精度/存储格式等数据规范内容)
    (re.compile(r"^6\s+数据要求"), "数据采集"),
    (re.compile(r"^7\s+数据库组织"), "数据库"),
    # 新增 part4: "7 采集要求及数据结构" / part5: "7 数据更新"
    (re.compile(r"^7\s+(数据更新|采集要求)"), "数据整理"),
    (re.compile(r"^8\s+质量要求"), "质量要求"),
    # 新增 part4: "8 入库流程" / part5: "8 检查方法"
    (re.compile(r"^8\s+(检查方法|入库流程)"), "质量要求"),
    # 新增 part4: "9 数据应用"
    (re.compile(r"^9\s+数据应用"), "数据整理"),
    (re.compile(r"^附录[A-Z]"), "附录"),
    (re.compile(r"^参考文献"), "参考文献"),
]

# 知识类型（knowledge_type）判定关键词
KNOWLEDGE_TYPE_RULES: list[tuple[str, re.Pattern, str]] = [
    # (section_type 或 内容正则, 知识类型)
    ("术语定义", re.compile(r".+"), "term_definition"),
    ("引用文件", re.compile(r".+"), "references"),
    ("参考文献", re.compile(r".+"), "references"),
    ("前言/引言", re.compile(r".+"), "preface"),
    ("范围", re.compile(r".+"), "scope_intro"),
    ("质量要求", re.compile(r"(检查|质检|误差|精度|合格|要求|不应|必须|应符合)"), "quality_rule"),
    ("质量要求", re.compile(r".+"), "data_spec"),
    ("附录", re.compile(r"(表|字段|格式|编码|代码|登记表)"), "appendix_table"),
    ("附录", re.compile(r".+"), "appendix"),
    ("数据整理", re.compile(r"(编号|字段|格式|编码|表|目录|文件)"), "field_rule"),
    ("数据整理", re.compile(r".+"), "data_spec"),
    ("数据库", re.compile(r"(字段|表|索引|组织|结构)"), "field_rule"),
    ("数据库", re.compile(r".+"), "data_spec"),
    ("数据采集", re.compile(r"(精度|误差|要求|仪器|方法)"), "quality_rule"),
    ("数据采集", re.compile(r".+"), "data_spec"),
    ("时空基准", re.compile(r".+"), "data_spec"),
]

# 数据对象名（data_name）关键词：规范7部分对应的数据对象名
DATA_NAME_BY_PART = {
    1: ["时空数据分类", "基本规定"],
    2: ["检测点"],
    3: ["检测线"],
    4: ["标志性地物"],
    5: ["重要要素"],
    6: ["高精度栅格数据", "DOM", "DEM", "DSM"],
    7: ["资源数据"],
}

# 参数提示词（param_hint）：规范里常出现的阈值/约束词
PARAM_HINT_RE = re.compile(
    r"(不超过|不低于|不小于|大于|小于|至少|最多|精度|误差|阈值|唯一|非空|必填|"
    r"\d+(?:\.\d+)?\s*(?:米|厘米|毫米|度|°|平方米|公顷|"
    r"m|cm|mm|km|㎡|个|条|项))",
)


# ---------------------------------------------------------------------------
# 结构化提取行对象
# ---------------------------------------------------------------------------


@dataclass
class ExtractedLine:
    """PDF 提取后的单条结构化行。

    用于承载从 PDF 中提取的每一行文本及其结构化解析结果，
    包含章节归属、知识分类、噪声标记、业务关键字段等丰富元信息，
    供后续切块（chunking）时直接继承到 LlamaIndex Node/Document 的 metadata 中。
    """

    text: str
    """提取的原始文本内容（去除首尾空白后的单行文本）。"""

    page: int
    """文本所在的 PDF 页码（从 1 开始计数）。"""

    chapter_no: str | None = None
    """章节编号，如 "5.2.4"、"附录A"、"A.1"；非章节标题行则为 None。"""

    chapter_title: str | None = None
    """章节标题文本，如 "采集数量与方式"；非章节标题行则为 None。"""

    chapter_path: str | None = None
    """章节层级路径，由父级章节编号用 "/" 拼接而成，如 "5/5.2/5.2.4"，
    用于快速定位文档层级关系和实现按章节检索。"""

    section_type: str = "正文_其他"
    """大章节类别（规范文档的固定分区），取值范围：
    "前言/引言"、"范围"、"引用文件"、"术语定义"、"时空基准"、
    "数据采集"、"数据整理"、"数据库"、"质量要求"、"附录"、"参考文献"、"正文_其他"。
    用于 metadata 过滤和分区域检索。"""

    knowledge_type: str = "正文_其他"
    """知识类型（细分业务语义），取值范围：
    "term_definition"(术语定义)、"references"(引用文件)、"preface"(前言)、
    "scope_intro"(范围介绍)、"quality_rule"(质量规则/阈值约束)、
    "data_spec"(数据规范)、"field_rule"(字段规则)、"appendix_table"(附录表格)、
    "appendix"(附录)、"chapter_title"(章节标题)、"正文_其他"。
    用于检索时的知识类型过滤和答案质量控制。"""

    is_toc: bool = False
    """是否为目录(TOC)行噪声，True 表示该行是目录引导点行，应在输出中过滤丢弃。"""

    is_page_header: bool = False
    """是否为页眉行噪声，True 表示该行是文档页眉（如"部省共建项目"等），应过滤丢弃。"""

    is_page_num: bool = False
    """是否为纯页码行噪声，True 表示该行只包含页码数字，应过滤丢弃。"""

    is_table: bool = False
    """是否为表格内容行，True 表示该行来源于 PDF 表格提取（预留字段，当前版本暂未填充）。"""

    data_names: list[str] = field(default_factory=list)
    """数据对象名列表，识别本行涉及的时空数据业务对象，
    如 ["检测点", "检测线", "标志性地物"]，上限 5 个，用于按数据对象检索。"""

    field_names: list[str] = field(default_factory=list)
    """字段名称列表，启发式匹配本行中出现的业务字段名，
    如 ["检测点编号", "坐标X", "字段类型"]，上限 8 个，用于按字段名检索和问答。"""

    param_hints: list[str] = field(default_factory=list)
    """参数提示词列表，提取本行中出现的阈值/约束/精度等关键词，
    如 ["不超过", "精度±0.5米", "10个"]，上限 8 个，用于数值类问答的召回增强。"""

    raw_meta: dict[str, Any] = field(default_factory=dict)
    """原始扩展元数据字典，预留字段用于存放后续新增的其他提取信息（如表格行坐标、PDF 原始布局等）。"""

    def to_markdown(self) -> str:
        """转成带 metadata 注释的 Markdown 行（便于人读+Document metadata提取）。"""
        if self.is_toc or self.is_page_header or self.is_page_num:
            return ""  # 噪声行直接不出现在输出md中
        meta_parts: list[str] = []
        if self.chapter_no:
            meta_parts.append(f"chapter_no={self.chapter_no}")
        if self.chapter_title:
            meta_parts.append(f"chapter_title={self.chapter_title}")
        if self.section_type and self.section_type != "正文_其他":
            meta_parts.append(f"section_type={self.section_type}")
        if self.knowledge_type and self.knowledge_type != "正文_其他":
            meta_parts.append(f"knowledge_type={self.knowledge_type}")
        meta = "; ".join(meta_parts)
        prefix = f"<!-- {meta} -->\n" if meta else ""
        text = self.text
        if self.chapter_no and self.chapter_title:
            # 章节标题升级为 Markdown 标题（便于SentenceSplitter识别边界）
            level = min(self.chapter_no.count(".") + 1, 5)
            text = f"{'#' * level} {self.chapter_no} {self.chapter_title}"
        return f"{prefix}{text}\n"

    def to_metadata_dict(self) -> dict[str, Any]:
        """导出为 LlamaIndex Node/Document metadata 字典。"""
        d: dict[str, Any] = {
            "page": self.page,
            "section_type": self.section_type,
            "knowledge_type": self.knowledge_type,
            "is_noise": self.is_toc or self.is_page_header or self.is_page_num,
            "is_table": self.is_table,
        }
        if self.chapter_no:
            d["chapter_no"] = self.chapter_no
        if self.chapter_title:
            d["chapter_title"] = self.chapter_title
        if self.chapter_path:
            d["chapter_path"] = self.chapter_path
        if self.data_names:
            d["data_name"] = self.data_names
        if self.field_names:
            d["field_name"] = self.field_names
        if self.param_hints:
            d["param_hint"] = self.param_hints
        return d


# ---------------------------------------------------------------------------
# 提取器核心逻辑
# ---------------------------------------------------------------------------


class EnhancedPdfExtractor:
    """增强版 PDF 提取器：去噪 + 解析 + Metadata。"""

    def __init__(self, pdf_path: Path) -> None:
        self.pdf_path = pdf_path
        self.part_number, self.part_name = self._parse_part_from_name(pdf_path)

    @staticmethod
    def _parse_part_from_name(pdf_path: Path) -> tuple[int | None, str]:
        """从 PDF 文件名解析 part_number 和 part_name。

        例："实景三维质检大数据支撑库 时空数据规范 第2部分 检测点.pdf" → (2, "检测点")
        """
        m = re.search(r"第\s*(\d+)\s*部分\s*(.+?)(?:\.pdf)?$", pdf_path.name)
        if m:
            return int(m.group(1)), m.group(2).strip()
        return None, pdf_path.stem

    def _default_data_names(self) -> list[str]:
        return DATA_NAME_BY_PART.get(self.part_number or 0, [self.part_name])

    # ------------------------------------------------------------------
    # 单页提取
    # ------------------------------------------------------------------

    def _extract_page_lines(self, page: pypdf.PageObject, page_idx: int) -> list[ExtractedLine]:
        raw = page.extract_text() or ""
        raw_lines = [ln.rstrip() for ln in raw.splitlines()]
        lines: list[ExtractedLine] = []

        # 检测页眉：同一文本如果在第2~3个非空行反复出现（跨页相同），后续标页眉。
        # 这里简化版：过滤掉完全重复的短标题行（长度<30，且反复出现"部省共建项目"等）。
        HEADER_HINTS = ["部省共建项目", "实景三维质检大数据支撑库", "时空数据规范"]

        for raw_line in raw_lines:
            line = raw_line.strip()
            if not line:
                continue

            el = ExtractedLine(text=line, page=page_idx + 1)

            # 1. 纯页码行
            if PAGE_NUM_ONLY_RE.fullmatch(line):
                el.is_page_num = True
                continue  # 不append，直接丢弃

            # 2. 页眉行
            if any(h in line for h in HEADER_HINTS) and len(line) < 40:
                el.is_page_header = True
                continue  # 不append

            # 3. TOC目录行(普通标题:"前 言 ........ I")
            if TOC_LINE_RE.match(line):
                el.is_toc = True
                continue  # 不append，丢弃目录噪声

            # 3.1 TOC目录行(含章节号:"3.1 检测点数据分类 ........ 1")
            # 修复:原 TOC_LINE_RE 因 [^\s.] 禁点漏匹配章节号,导致此类行被
            #      CHAPTER_TITLE_RE 误识别为正文章节标题,输出 "## 3.1 标题......1" 噪声。
            if TOC_WITH_CHAPTER_RE.match(line):
                el.is_toc = True
                continue  # 不append，丢弃目录噪声

            # 到这里是有效正文行。
            lines.append(el)
        return lines

    # ------------------------------------------------------------------
    # 跨页后处理：章节解析 + 知识分类 + metadata推断
    # ------------------------------------------------------------------

    def _mark_toc_section(self, lines: list[ExtractedLine]) -> list[ExtractedLine]:
        """区段级 TOC 识别兜底:从"目  录"字面量到下一个真实章节之间的行标记为 is_toc。

        背景:
            _extract_page_lines 用 TOC_LINE_RE / TOC_WITH_CHAPTER_RE 做单行过滤,
            但仍可能遗漏(如"目  录"字面量本身无引导点、PDF 提取产生的变形行)。
            本方法在全局行列表上做区段级兜底:一旦进入目录区段,后续所有行
            (含任何单行正则遗漏的 TOC 行)统一标记为噪声,直到遇到真实章节起点。

        退出目录区段的判据(GB/T 1.1 标准结构):
            - "前 言" / "引 言"        → 前言/引言章节起点
            - "1 范围" / "1  范围"     → 第1章范围起点
            - "2 规范性引用文件"       → 第2章引用文件起点

        参数:
            lines: 已经过 _extract_page_lines 单行过滤的 ExtractedLine 列表
                   (页码/页眉/单行TOC已 continue 掉,但"目  录"字面量仍保留)。

        返回:
            同一列表(in-place 修改 is_toc 标志),后续由 to_markdown 统一过滤。
        """
        in_toc = False
        toc_start_page: int | None = None
        for el in lines:
            text = el.text.strip()
            # 进入目录区段
            if TOC_SECTION_RE.match(text):
                in_toc = True
                toc_start_page = el.page
                el.is_toc = True
                logger.debug("  目录区段开始: page=%d, 行='%s'", el.page, text)
                continue
            # 退出目录区段:遇到真实章节起点
            if in_toc:
                if re.match(r"^(前\s*言|引\s*言|1\s+范\s*围|2\s+规范性引用文件)", text):
                    in_toc = False
                    # 该行是正文,不标记 is_toc,保留
                    logger.debug(
                        "  目录区段结束(遇到真实章节): page=%d, 行='%s'",
                        el.page, text[:30],
                    )
                else:
                    # 目录区段内所有行(含遗漏的 TOC 行)标记为噪声
                    el.is_toc = True
        return lines

    def _annotate_structure(self, lines: list[ExtractedLine]) -> list[ExtractedLine]:
        """对已过滤噪声的行进行结构注解。"""
        chapter_stack: list[tuple[str, str]] = []  # [(chapter_no, chapter_title), ...]
        current_section = "正文_其他"
        default_data_names = self._default_data_names()
        annotated: list[ExtractedLine] = []

        for el in lines:
            # --- 章节标题识别 ---
            m = CHAPTER_TITLE_RE.match(el.text)
            if m:
                chapter_no = m.group("no")
                chapter_title = m.group("title").strip()
                # 维护chapter_stack：弹出层级不小于当前的节点
                level = chapter_no.count(".") + (0 if chapter_no.startswith("附录") else 0)
                if chapter_no.startswith("附录"):
                    # 附录单独清空栈
                    chapter_stack = [(chapter_no, chapter_title)]
                else:
                    while chapter_stack:
                        top_no, _ = chapter_stack[-1]
                        top_level = top_no.count(".")
                        if top_level >= level:
                            chapter_stack.pop()
                        else:
                            break
                    chapter_stack.append((chapter_no, chapter_title))
                el.chapter_no = chapter_no
                el.chapter_title = chapter_title
                el.chapter_path = "/".join(no for no, _ in chapter_stack)

                # --- section_type 更新 ---
                # 修复:旧逻辑嵌套混乱(search+match 多层条件),且不匹配时不重置 →
                #      导致 part4 整篇继承"范围"、part5 第3章以后整篇继承"引用文件",
                #      被 smart_chunker 的低价值过滤全部丢弃,只剩 1 条封面/前言 Document。
                # 新逻辑:1) 按 chapter_no[0] + title 组成 section_key(顶级)或按 title(附录);
                #        2) 顶级章节(chapter_no 不含".")未匹配任何 pattern → 重置为"正文_其他",
                #           避免无关章节错误继承;子章节(如 5.2.4)仍继承父章节的 section_type。
                if chapter_no[0].isdigit():
                    section_key = f"{chapter_no[0]} {chapter_title}"
                else:
                    # 附录/参考文献:用 chapter_no 或 chapter_title 匹配(如 "附录A" / "参考文献")
                    section_key = chapter_no if chapter_no.startswith("附录") else chapter_title
                matched_section = False
                for pat, stype in SECTION_TYPE_PATTERNS:
                    if pat.match(section_key) or pat.match(chapter_title):
                        current_section = stype
                        matched_section = True
                        break
                # 修复粘性继承:顶级章节(无".")且非附录未匹配 → 重置为"正文_其他"
                if (
                    not matched_section
                    and "." not in chapter_no
                    and not chapter_no.startswith("附录")
                ):
                    current_section = "正文_其他"

            # 修复:el.section_type = current_section 必须放在 if m: 之外,
            #      让正文行(非章节标题)也继承最近一次匹配到的 current_section,
            #      否则正文行会全部退化为 dataclass 默认值 "正文_其他",
            #      导致 smart_chunker 失去 section_type 上下文,无法按章节区域检索。
            el.section_type = current_section

            # --- knowledge_type 判定 ---
            ktype = None
            for sec_pat_key, content_pat, ktype_cand in KNOWLEDGE_TYPE_RULES:
                if sec_pat_key == current_section:
                    if content_pat.search(el.text):
                        ktype = ktype_cand
                        break
            if ktype is None:
                # 兜底：如果是章节标题，和section一致
                if el.chapter_no:
                    ktype = "chapter_title"
                else:
                    ktype = "正文_其他"
            el.knowledge_type = ktype

            # --- data_name 推断 ---
            dnames = list(default_data_names)
            # 如果行里出现其他部分的名称（如检测线文档里提到检测点），也加上
            for pno, names in DATA_NAME_BY_PART.items():
                for nm in names:
                    if len(nm) >= 3 and nm in el.text and nm not in dnames:
                        dnames.append(nm)
            el.data_names = dnames[:5]  # 上限5个避免冗余

            # --- field_name 启发式：匹配"XX字段""字段XX""XXX编号""坐标X/Y"等 ---
            field_candidates: list[str] = []
            fm = re.findall(
                r"([\u4e00-\u9fa5A-Za-z]{2,20}(?:字段|编号|编码|代码|坐标|名称|类型|长度|精度|面积|角度|单位|时间|日期|质量))",
                el.text,
            )
            field_candidates.extend(fm)
            # 匹配形如：字段名 检测点编号 / 字段 坐标X
            fm2 = re.findall(
                r"(?:字段[名称]?|字段：)\s*([\u4e00-\u9fa5A-Za-z][\u4e00-\u9fa5A-Za-z0-9_]{1,20})",
                el.text,
            )
            field_candidates.extend(fm2)
            if field_candidates:
                # 去重保序
                seen: set[str] = set()
                uniq = []
                for f in field_candidates:
                    if f not in seen:
                        seen.add(f)
                        uniq.append(f)
                el.field_names = uniq[:8]

            # --- param_hint 提取 ---
            pms = PARAM_HINT_RE.findall(el.text)
            if pms:
                seen_ph = set()
                uniq_ph = []
                for p in pms:
                    if p not in seen_ph:
                        seen_ph.add(p)
                        uniq_ph.append(p)
                el.param_hints = uniq_ph[:8]

            annotated.append(el)
        return annotated

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------

    def extract(self) -> tuple[str, list[ExtractedLine], dict[str, Any]]:
        """提取整本PDF。

        返回:
            (markdown_text, structured_lines, document_level_metadata)
        """
        logger.info("增强提取PDF: %s, part=%s, name=%s", self.pdf_path.name, self.part_number, self.part_name)
        reader = pypdf.PdfReader(str(self.pdf_path))
        total_pages = len(reader.pages)
        all_lines: list[ExtractedLine] = []
        for i, page in enumerate(reader.pages):
            page_lines = self._extract_page_lines(page, i)
            all_lines.extend(page_lines)
        logger.info("  原始行数(去噪前噪声已滤): %d (共%d页)", len(all_lines), total_pages)

        # 区段级 TOC 识别兜底:标记"目  录"区段内的所有行为 is_toc
        # (修复 _extract_page_lines 单行正则的遗漏,如"目  录"字面量本身)
        self._mark_toc_section(all_lines)
        toc_marked_cnt = sum(1 for el in all_lines if el.is_toc)
        logger.info("  区段级TOC兜底: 标记噪声行数=%d", toc_marked_cnt)

        # 过滤掉所有噪声行(is_toc/is_page_header/is_page_num),只保留正文行
        # (单行 TOC 已在 _extract_page_lines 中 continue 掉,这里再过滤区段级标记的)
        valid_lines = [el for el in all_lines if not el.is_toc]
        logger.info("  有效正文行数: %d (过滤噪声后)", len(valid_lines))

        annotated = self._annotate_structure(valid_lines)
        logger.info(
            "  结构注解完成: chapter_title行数=%d, knowledge_type分布=%s",
            sum(1 for l in annotated if l.chapter_no),
            _count_types(annotated, "knowledge_type"),
        )

        # 生成 Markdown 正文
        md_blocks: list[str] = []
        md_blocks.append(
            f"# 实景三维质检大数据支撑库 时空数据规范 第{self.part_number}部分 {self.part_name}\n"
        )
        md_blocks.append(f"> 来源：{self.pdf_path.name}（增强版提取，已去目录/页眉/页码噪声）\n\n")
        for el in annotated:
            md_line = el.to_markdown()
            if md_line:
                md_blocks.append(md_line)
        markdown_text = "\n".join(md_blocks)

        doc_meta = {
            "part_number": self.part_number,
            "part_name": self.part_name,
            "extractor_version": "enhanced_v2",  # v1→v2: 修复 TOC/章节正则 + 区段级兜底
            "noise_removed": True,
            "structure_parsed": True,
            "total_valid_lines": len(annotated),
            "toc_lines_removed": toc_marked_cnt,  # 新增:记录过滤的TOC噪声行数
            "default_data_name": self._default_data_names(),
        }
        logger.info(
            "  提取成功: md字符数=%d, doc_meta=%s",
            len(markdown_text),
            json.dumps(doc_meta, ensure_ascii=False),
        )
        return markdown_text, annotated, doc_meta


def _count_types(lines: list[ExtractedLine], attr: str) -> dict[str, int]:
    """调试用：统计某属性值分布。"""
    c: dict[str, int] = {}
    for l in lines:
        v = str(getattr(l, attr, "?"))
        c[v] = c.get(v, 0) + 1
    return c


# ---------------------------------------------------------------------------
# 批处理入口（对标原_extract_pdfs.py main）
# ---------------------------------------------------------------------------


def run_enhanced_extraction(
    standard_dir: Path,
    output_dir: Path,
    *,
    overwrite: bool = True,
) -> list[Path]:
    """批处理：把 standard_dir 下所有PDF用增强提取器写入 output_dir。

    注意：输出文件名仍为 partX_名称.md，与原脚本一致，便于下游 document_loader 直接复用。
    不同的是：文件内容噪声更少，且每个章节标题行带有 <!-- metadata --> 注释，
    Document 加载时可通过 metadata_extractor（后续我们会在 document_parser 中处理）
    把这些字段注入到 Node。

    参数:
        standard_dir: standard 目录（7份PDF）
        output_dir: qualityScheme/data 目录
        overwrite: True 覆盖已有MD
    """
    logger.info("===== 开始增强提取: standard=%s -> output=%s =====", standard_dir, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(standard_dir.glob("*.pdf"))
    logger.info("找到PDF文件数: %d", len(pdf_files))

    produced: list[Path] = []
    for pdf_path in pdf_files:
        extractor = EnhancedPdfExtractor(pdf_path)
        md_text, _, _ = extractor.extract()

        # 文件名与原脚本保持一致
        if extractor.part_number is not None:
            safe_name = re.sub(r'[\\/:*?"<>|\s]+', "_", extractor.part_name)
            out_name = f"part{extractor.part_number}_{safe_name}.md"
        else:
            out_name = re.sub(r'[\\/:*?"<>|\s]+', "_", pdf_path.stem) + ".md"
        out_path = output_dir / out_name
        if out_path.exists() and not overwrite:
            logger.warning("  跳过(已存在,overwrite=False): %s", out_path)
            produced.append(out_path)
            continue
        out_path.write_text(md_text, encoding="utf-8")
        logger.info("  -> 写入: %s (%d字符)", out_path.name, len(md_text))
        produced.append(out_path)

    logger.info("===== 增强提取完成: 生成 %d 个MD文件 =====", len(produced))
    return produced
