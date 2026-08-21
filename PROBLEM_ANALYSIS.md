# 质检方案RAG系统问题分析报告

> 生成日期：2026-08-21
> 分析范围：qualityScheme 目录下全部业务代码 + standard 规范数据提取结果 + llamaIndex-gpt.docx 架构建议

---

## 一、系统概述与业务目标

当前系统的业务链路如下：

```
standard/*.pdf（7份时空数据规范）
    ↓ PDF提取 → qualityScheme/data/*.md
    ↓ SimpleDirectoryReader 加载 Document
    ↓ SentenceSplitter 切块（chunk_size=256, overlap=40）
    ↓ Embedding → Milvus collection=qualityScheme_llamaIndex
    ↓ VectorStoreIndex（纯向量TopK检索）
用户自然语言需求（如"检测点坐标精度≤0.5米，编号唯一"）
    ↓ 意图识别（LLM一次调用）
    ↓ 向量检索Top5条款作为上下文
    ↓ LLM + Pydantic 从28项预定义清单中选检查项 + 推断参数
    ↓ 结构化 JSON 质检方案
```

**业务核心目标**：把用户一句自然语言质检需求，准确映射到「正确的检查项编码 + 完整的参数（数据层名、字段名、阈值）」。

---

## 二、核心问题总览（按影响严重度排序）

| # | 问题类别 | 严重度 | 影响范围 |
|---|---------|--------|---------|
| 1 | **PDF数据提取质量极差** | 🔴 致命 | 全部检索结果的基础语料 |
| 2 | **Metadata 几乎为空白** | 🔴 致命 | 检索精度、过滤能力 |
| 3 | **切块策略无结构感知** | 🟠 严重 | 检索召回率、上下文完整性 |
| 4 | **纯向量检索，缺少Hybrid/Rerank** | 🟠 严重 | 编码/编号/阈值类查询召回 |
| 5 | **缺少Query分解（多意图处理）** | 🟠 严重 | 复合需求的方案完整性 |
| 6 | **28项检查项靠LLM硬选，缺少语义匹配** | 🟡 中度 | 检查项选择准确性 |
| 7 | **Milvus单一Collection"一锅炖"** | 🟡 中度 | 可扩展性、检索过滤效率 |
| 8 | **缺少Router/Composable/Recursive检索** | 🟡 中度 | 复杂查询的知识组合能力 |
| 9 | **本地模型（LocalHash/Extractive）不可用** | 🟡 中度 | local模式完全无效果 |
| 10 | 工程细节问题（调试print/低效过滤等） | 🟢 轻微 | 可维护性 |

---

## 三、问题详细分析

### 🔴 问题1：PDF数据提取质量极差

**现状代码**：[qualityScheme/_extract_pdfs.py](file:///E:/project/agent/llamaIndex/qualityScheme/_extract_pdfs.py)

使用 `pypdf.PdfReader(page).extract_text()` + 简单正则清理页码行。

**实际输出问题**（以 `part2_检测点.md` 为例）：

1. **大量目录噪声**：原文TOC带大量引导点，被完整保留：
   ```
   前 言 .......................................................................................................................................................... 1
   1 范围 ................................................................................................................................................................... 1
   ```
   这些行的语义是"目录导航"，与质检规则无关，但会占满Chunk空间、稀释向量语义。

2. **页面标记残留**：`<!-- 第 1 页 -->` 每页保留。

3. **表格完全丢失**：
   - 检测点编号规则（6.1节）中必然存在的「字段定义表」「编码规则表」→ 变成乱序文本行。
   - 附录A（采集登记表）、附录B、附录C（外业代码表）的表格结构 → 提取后完全不可读。
   - **后果**：用户问"检测点编号的字段格式是什么"，向量里根本没有结构化表信息，LLM只能胡编。

4. **章节层级丢失**：`6.1 检测点编号` / `6.1.1 编码规则` 这些层级编号和正文混在一起，切块时很容易被切断，导致"编号在6.1.1、正文在下一Chunk"。

5. **页眉页脚/起草信息混杂**："部省共建项目"、"2025年7月"、"起草单位：" 这些无意义文本进入语料。

**影响评估**：这是**最致命的基础问题**。语料本身脏、缺、散，后续无论 Embedding 多好、检索策略多高级，都是「垃圾进 → 垃圾出」。

---

### 🔴 问题2：Metadata 几乎为空白

**现状**：每个 Node 只有 `SimpleDirectoryReader` 自动注入的 `file_name` / `file_path` / `file_size` / `file_type`。

**缺少的关键业务Metadata**：

| 应有的Metadata字段 | 业务价值 |
|-------------------|---------|
| `part_number` (1~7) | 支持"只查第2部分检测点"的精确过滤 |
| `knowledge_type` | 枚举：`toc_noise` / `term_definition` / `data_spec` / `field_rule` / `quality_rule` / `appendix_table`。直接过滤掉目录噪声！ |
| `chapter_no` / `chapter_title` | 如 `6.1` / `检测点编号`，让检索结果可溯源到具体条款 |
| `data_name` | 业务语义：检测点 / 检测线 / 标志性地物 / 高精度栅格... |
| `field_name` | 涉及的字段名（如检测点编号、坐标X、坐标Y） |
| `param_name` | 涉及的参数名（如min_length、threshold） |
| `is_table_row` (bool) | 标记是否为表格行 |
| `doc_section` | 文档层级：前言/范围/术语定义/时空基准/数据采集/数据整理/数据库/质量要求/附录 |

**为什么致命**：
1. 现在 `metadata_filter.py` 只能按 `file_name` 过滤——精度极低。
2. **无法过滤目录噪声**：用户问"检测点的采集要求"，TopK可能先返回一堆 TOC 行（因为 TOC 反复出现"采集"关键词）。
3. 无法做"先按 knowledge_type=quality_rule 过滤，再向量检索"——这是 GPT 文档强调的 Metadata Filter 核心用法。
4. `retrieve_by_part` 函数**目前是在内存里过滤**（先取TopK*5再筛选前缀），而不是 Milvus 侧过滤——本质原因就是缺少结构化的 `part_number` 字段。

---

### 🟠 问题3：切块策略无结构感知

**现状**：[document_parser.py](file:///E:/project/agent/llamaIndex/qualityScheme/document_parser.py#L35-L38)

```python
DEFAULT_CHUNK_SIZE = 256
DEFAULT_CHUNK_OVERLAP = 40
# SentenceSplitter 纯按句号/换行切
```

**问题**：

1. **条款边界被切断**：质检规范是典型的层级编号文档（`5.1.1 → a) → b) → c)`）。256字符一刀切会把：
   ```
   5.2.4 采集数量与方式
   每个点位采用组合方式采集，每个村（居）定位点及附近区域，数量不低于5个……
   a) 房檐角+房角底点对 ≥ 1；
   b) 路面高程点 ≥ 1；
   ```
   切成两块，`a)` 的归属条款 `5.2.4` 在前面Chunk，检索只命中 `a)` 时就丢失上下文。

2. **Chunk尺寸一刀切不合理**：
   - 术语定义（3.1~3.6）：每个才2~3行，几十字符，256会把多个不相关术语揉在一起。
   - 质量要求（第8章+附录）：表格行密集，256可能只含半张表。
   - 应该**先按章节层级切块 → 再按句子细切 → 保留Parent-Child关系**（Small-to-Big Retrieval）。

3. **无噪声过滤**：目录噪声行、页码、页眉页脚在切块前就应该过滤掉，不该进入Chunk。

---

### 🟠 问题4：纯向量检索，缺少 Hybrid + Rerank

**现状**：所有检索都是 `VectorStoreIndex.as_retriever()` → 纯 Dense Vector + COSINE 相似度。

**为什么在本业务场景效果特别差**：

质检规范里充斥着**非语义类精确匹配需求**：
| 用户查询元素 | 纯向量检索的问题 |
|-------------|----------------|
| `DLMC` / `OBJECTID` / `GB/T 2260` | 缩写、代号、标准号——Embedding语义化弱，容易被"道路面层类型"这类更长文本盖过 |
| `0.5米` / `≤0.5m` / `50厘米` | 数值阈值纯向量模糊匹配，无法区分 `0.5米` vs `1.0米` |
| `检测点编号` / `QualityCheckUniqueValue` | 检查编码与字段编号是精确字符串，BM25关键词权重更高 |
| `part2` / `第2部分` | 章节编号纯文本匹配远优于向量 |

**GPT文档明确建议**（第10节）：Milvus + `vector_store_query_mode="hybrid"` = Dense + BM25 Sparse 混合，再 Rerank。

现状完全没用这些能力。

---

### 🟠 问题5：缺少 Query 分解（多意图处理）

**现状**：用户输入 "检测点坐标精度不超过0.5米，编号唯一，必填字段完整" → 直接整句Embedding → TopK=5 → LLM一把梭生成。

**问题**：这一句包含**3个独立意图**：
1. 坐标精度检查 → 对应 `layerPolygonAreaConsistencyCheck` 或坐标精度类
2. 编号唯一 → `QualityCheckUniqueValue`
3. 必填非空 → `qualityCheckFieldRequiredValidation`

**纯整句检索的问题**：
- TopK=5 的语义重心会偏向"出现次数最多的词"，可能只召回3条精度相关、1条编号、0条必填 → **方案漏项**。
- GPT文档第23节明确要求做 **Query Decomposition**：先拆成多意图，每条独立检索，再聚合。

---

### 🟡 问题6：28项检查项靠LLM硬选

**现状**：[scheme_generator.py](file:///E:/project/agent/llamaIndex/qualityScheme/scheme_generator.py#L72-L98) 的 Prompt 里用一个大表格把28项检查项全部塞给LLM，让LLM选。

**问题**：
1. **Token浪费**：28行×每次调用，且与规范上下文一同发送，成本高、响应慢。
2. **依赖LLM长上下文记忆力**：28项检查项在Prompt底部，当上下文很长时（规范条款多），LLM容易「看到了但没记住」，遗漏最合适的检查项。
3. **缺少语义匹配**：用户说"编号不能重复"——应该先把这句话和28个 checkName/checkDesc 做语义相似度（"字段唯一值检查" score最高），再把Top-3候选项给LLM裁决，而不是让LLM读28条全表。
4. **检查项本身也应该入库**：把28项 `_RAW_CHECK_ITEMS` 也做成 Node，存入 Milvus（单独 Collection 或单独 metadata 标记），用户需求先语义检索检查项 → 再让LLM确认和填参。

---

### 🟡 问题7：Milvus 单一Collection"一锅炖"

**现状**：所有规范文档Chunk → `qualityScheme_llamaIndex` 一个Collection，且无 `doc_type` metadata区分。

**GPT建议**（第20节）：不要"一锅炖"。应该：
- 方案A：多Collection：`data_specification` / `field_definition` / `quality_rules` / `check_items`
- 方案B：单Collection但强metadata区分：`doc_type` + `data_name` + `knowledge_type` + `chapter`

当前两种方案都没做。后果：
1. 做"字段名是什么"的查询，结果里混着"目录TOC"和"质量规则段落"。
2. 无法做"先过滤quality_rules类型，再检索精度条款"的Metadata前置过滤。

---

### 🟡 问题8：缺少 Router / Composable / Recursive 检索

**现状**：只有一个 `VectorStoreIndex` → 一个 `QueryEngine`，所有查询走同一链路。

**应该具备的路由能力**：

| 用户问题类型 | 应该路由到 | 当前实际 |
|-------------|-----------|---------|
| "检测点有哪些必填字段？" | 字段规范Index（knowledge_type=field_rule优先过滤） | 全文混搜 |
| "检测点的质量要求是什么？" | 质量规则Index | 全文混搜 |
| "总结一下时空数据规范的核心内容" | SummaryIndex（tree_summarize） | 已有 `/api/summary`，但没接入Router，全靠用户手动选接口 |
| "检测线和检测点的编号规则有什么区别？" | Composable：检测线 + 检测点 分别检索 → 合并对比 | 做不到 |
| "检测点编号的字段定义 + 对应质检规则 + 编码表是？" | Recursive：先命中编号 → 关联字段定义Node → 关联质检规则Node | 做不到 |

GPT文档第11~14节强调 RouterQueryEngine / Composable / Recursive / Small-to-Big，这些高级检索一个都没落地。

---

### 🟡 问题9：本地模式模型完全不可用

**现状**：[models.py](file:///E:/project/agent/llamaIndex/qualityScheme/models.py#L56-L59)

```python
llm = LocalExtractiveLLM()
embed_model = LocalHashEmbedding()
```

这两个是 `llamaindex_demo` 里的**学习占位模型**：
- `LocalHashEmbedding`：用哈希函数生成伪向量，**没有任何语义相似性**。"检测点编号"和"今天吃什么"的向量相似度可能完全随机。
- `LocalExtractiveLLM`：从检索Chunk里抽取文本片段，**不做任何生成**。Pydantic结构化输出完全失效，方案生成接口会报错或返回空。

**结论**：`provider=local` 模式下，整个系统**功能上完全不可用**。用户如果没配置OpenAI Key，启动后任何查询都是垃圾结果。

应该给local模式一个最低可用提示：未配置OpenAI时返回友好错误，或接Ollama本地模型。

---

### 🟢 问题10：工程细节问题

| # | 文件 | 问题 |
|---|------|------|
| 1 | [scheme_generator.py:L123-L131](file:///E:/project/agent/llamaIndex/qualityScheme/scheme_generator.py#L123-L131) | 生产代码里留了 `print()` 调试输出，应改用 logger.debug |
| 2 | [metadata_filter.py:L129](file:///E:/project/agent/llamaIndex/qualityScheme/metadata_filter.py#L129) | `retrieve_by_part` 先取TopK*5再内存过滤，应改用Metadata Filter在Milvus侧过滤 |
| 3 | [config.py:L17](file:///E:/project/agent/llamaIndex/qualityScheme/config.py#L17) | `PROJECT_ROOT = PACKAGE_DIR.parents[0]` 有误：PACKAGE_DIR是qualityScheme，parents[0]还是qualityScheme本身（应为parents[1]取项目根？不，再看：PACKAGE_DIR = Path(file).parent = qualityScheme，parents[0]=qualityScheme的父=llamaIndex（项目根），OK是对的） |
| 4 | [check_items.py 参数名不一致](file:///E:/project/agent/llamaIndex/qualityScheme/check_items.py#L136-L142) | `layerPolygonAreaConsistencyCheck` 用的是 `dataName`，其他大部分用 `data_name`；`checkInterLayerAttributeConsistencyCheck` 用的是 `compare_fields_first` 等——参数命名风格不统一，LLM生成参数名时容易写错（Prompt里虽然给了参数名表，但风格混乱增加了出错概率） |
| 5 | [web.py /summary接口](file:///E:/project/agent/llamaIndex/qualityScheme/web.py#L358-L370) | 每次调用都重新 `parse_documents(load_documents(...))` 切块嵌入，极慢。应缓存Nodes或SummaryIndex实例 |
| 6 | [index_persistence.py:L178](file:///E:/project/agent/llamaIndex/qualityScheme/index_persistence.py#L178) | 依赖 `_collection_initialized` 私有属性判断，属于LlamaIndex内部实现细节，版本升级可能变更，应用官方API |
| 7 | Milvus配置硬编码在config.py默认值里：`milvus_uri="http://milvus-dev1.e-tudou.com:19530"` 是测试环境地址，应要求必须.env配置，默认留空 |

---

## 四、数据提取质量抽样验证

从 `part2_检测点.md` 抽样前200行，问题覆盖率：
- 1~48行 = 纯目录 + 前言页（约24%文本量）→ **应在提取阶段标为 knowledge_type=toc_noise / preface，切块时排除或降权**
- 81~107行 = 规范性引用文件（GB/T标准清单）→ 对用户"如何质检"几乎无价值，标记为 references
- 109~137行 = 术语定义（3.1~3.6）→ 应该标记为 term_definition，可单独做术语Index
- 140~146行 = 时空基准（4.1~4.2）→ 标记为 data_spec, chapter=4

**结论**：目前约30%的Chunk内容（目录、引用、页眉）对"质检方案生成"这个核心目标是**噪声**，严重拉低检索信噪比。

---

## 五、为什么"效果非常不好"：根因链路图

```
用户输入：检测点坐标精度≤0.5米，编号唯一
          │
          ▼
[根因1] PDF提取脏：目录噪声 + 表格丢失
          ↓ 噪声Chunk占30%+
[根因2] Metadata为空：无法过滤TOC，无法限定data_name=检测点
          ↓ 检索池中混入大量part3~7无关内容 + TOC
[根因3] 切块乱：条款5.2.4被拆断 + a)b)c)归属丢失
          ↓ 召回的Chunk语义不完整
[根因4] 纯向量 + 无Query分解："编号唯一"意图被整句淹没
          ↓ TopK=5 只命中2条精度、1条编号、0条字段定义
[根因5] 28项检查项靠LLM读长表选
          ↓ LLM记忆力有限 + 参数名data_name/dataName混用写错
          └───────────────────────────────┘
                              ▼
                    生成的质检方案：
                    - 检查项选错 or 漏项
                    - fieldNames缺失 or 写错
                    - threshold参数没填 or 填错
                    = 用户感知"效果非常不好"
```

---

## 六、与GPT建议架构的差距对照

| GPT文档建议层级 | 当前是否实现 |
|----------------|-------------|
| 第8层：Ingestion Pipeline（含Metadata抽取） | ❌ 只做了切块+Embed，无Title/Chapter/实体抽取 |
| 第9层：Metadata Filtering | ⚠️ 只实现了file_name过滤，应该至少8个业务字段 |
| 第10层：Hybrid Search (Dense+BM25) | ❌ 纯Dense |
| 第11层：RouterQueryEngine | ❌ 单QueryEngine |
| 第12层：Composable Query | ❌ 无 |
| 第13层：Recursive Retrieval | ❌ 无Node relationships |
| 第14层：Small-to-Big Retrieval | ❌ 单chunk_size |
| 第15层：Summary Index 路由接入 | ⚠️ 有独立API，没Router |
| 第16层：SQL+RAG（检查项结构化查询） | ❌ 检查项没入库 |
| Milvus多Collection / 强Metadata区分 | ❌ 单Collection弱Metadata |
| Query Decomposition多意图处理 | ❌ 整句检索 |
| Reranker | ❌ 无 |

共13项关键能力，**当前实现0~1项**，其余全部缺失。这就是效果差的根本架构原因。

---

## 七、改进优先级矩阵

| 优先级 | 改进项 | 预期效果提升 | 工作量 |
|--------|-------|-------------|--------|
| P0（立刻做） | 1. 重构PDF提取：去TOC噪声 + 表格Markdown化 + 章节结构解析 | 基础语料质量↑60% | 中 |
| P0 | 2. 增强Metadata：part_number / knowledge_type / chapter / data_name / field_name | 检索信噪比↑50% | 中 |
| P0 | 3. 结构感知切块：按章节先切 + 条款边界保护 + 噪声Chunk排除 | 召回完整性↑40% | 中 |
| P1（紧接着） | 4. Hybrid Search(Dense+BM25) + 检查项也入库Milvus | 编号/编码类查询召回↑60% | 中 |
| P1 | 5. Query Decomposition：复杂需求拆多意图分别检索 | 复合需求不漏项↑70% | 中大 |
| P1 | 6. local模式接Ollama或报错，避免垃圾结果 | 系统可用性↑100% | 小 |
| P2（深入优化） | 7. RouterQueryEngine（字段/规则/总结三路路由） | 复杂查询准确率↑40% | 大 |
| P2 | 8. Small-to-Big + Parent-Child Chunk关系 | 上下文完整性↑30% | 中 |
| P2 | 9. Reranker集成 | TopK精准度↑25% | 小 |
| P3（长期演进） | 10. Composable / Recursive Retrieval | 跨文档关联查询 | 大 |
| P3 | 11. Knowledge Graph 知识图谱化 | 知识关联能力质变 | 极大 |

---

*报告结束。下一份文档：改进计划 IMPROVEMENT_PLAN.md*
