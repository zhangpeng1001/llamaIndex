# 质检方案RAG系统改进计划

> 配套文档：[PROBLEM_ANALYSIS.md](file:///E:/project/agent/llamaIndex/PROBLEM_ANALYSIS.md)
> 目标：基于问题分析报告的P0/P1优先级项，完成可落地的代码改造，把"效果非常不好"提升到"生产可用"。

---

## 一、改进范围与里程碑

| 阶段 | 目标 | 核心交付 | 对应问题 |
|------|------|---------|---------|
| **阶段1：数据层重构（P0）** | 解决"垃圾进垃圾出" | 新PDF提取器 + 富Metadata + 结构感知切块 | 问题1/2/3 |
| **阶段2：检索层增强（P1）** | 解决"检索找不准、找不全" | Hybrid Search + Query分解 + 检查项入库 | 问题4/5/6 |
| **阶段3：方案生成优化（P1）** | 解决"方案漏项、参数错" | 检查项语义匹配 + 参数校验增强 | 问题6/10.4 |
| **阶段4：工程化完善（P1）** | 解决"local模式不可用 + 细节问题" | Ollama兜底 + 调试代码清理 + 缓存 | 问题9/10 |
| **阶段5：文件整理** | 解决"项目目录冗余" | 删除无用文件 + 生成说明文档 | 用户要求第6项 |

---

## 二、阶段1：数据层重构（P0）——详细设计

### 2.1 重构 PDF 提取器

**原文件**：`_extract_pdfs.py`（功能太薄）
**新文件**：新建 `qualityScheme/enhanced_extractor.py`（独立文件，符合"每个功能单独文件"规范）
**保留**：`_extract_pdfs.py` 作为向后兼容脚本，但推荐用新的。

#### 核心能力：

```
PDF每一页
  ↓ pypdf + 布局分析
  ├─ 识别目录行（正则匹配"....页码"模式）→ 标记knowledge_type=toc_noise，提取但不进语料Chunk
  ├─ 识别页眉行（每页顶部重复文本："部省共建项目""第X部分XXX"）→ 排除
  ├─ 识别页码行（纯数字行）→ 排除
  ├─ 识别章节标题（正则"^\d+(\.\d+)*\s+"如5.1.1、附录A）→ 提取chapter_no, chapter_title
  ├─ 识别表格（pypdf页面布局，行对齐特征）→ 转成Markdown表格！保留表头+行
  └─ 识别正文段落 → 按章节结构归属
最终输出：partX_XXX_structure.jsonl（结构化行） + partX_XXX.md（人读Markdown）
```

#### 新增 Metadata 提取规则（每个 Document/Node 注入）：

| 字段 | 提取方式 | 示例值 |
|------|---------|-------|
| `part_number` | 文件名正则 `part(\d+)_` | `2` |
| `part_name` | 文件名 `part2_**检测点**.md` | `"检测点"` |
| `knowledge_type` | 内容正则分类 | `toc_noise`/`preface`/`references`/`term_definition`/`data_spec`/`field_rule`/`quality_rule`/`appendix_table`/`正文_其他` |
| `chapter_no` | 章节标题正则 | `"5.2.4"` |
| `chapter_title` | 章节标题文本 | `"采集数量与方式"` |
| `chapter_path` | 层级路径（用于Parent-Child） | `"5/5.2/5.2.4"` |
| `data_name` | 从part_name推断 + 正文字段表提取 | `["检测点"]` / `["检测点", "检测线"]`（跨表时） |
| `field_name` | 从表格"字段名"列提取 | `["检测点编号", "X坐标", "Y坐标"]` |
| `param_hint` | 从正文提取的阈值关键词 | `["min_length", "0.5米", "唯一", "非空"]` |
| `is_table` | 是否为表格行 | `true/false` |
| `section_type` | 文档大章节 | `"前言"/"范围"/"术语定义"/"时空基准"/"数据采集"/"数据整理"/"数据库"/"质量要求"/"附录"` |

#### 目录噪声过滤规则：
```python
TOC_PATTERN = re.compile(r"^.+[.。]{4,}.+\d+\s*$")  # 匹配 "前言 .................................. 1"
# 另外：连续多行均含引导点 → 整段标toc_noise，直接不进入切块语料
```

#### 表格提取增强（关键！）：
- 利用 `pypdf` 的 `page.extract_table()`（如存在表格布局）
- 兜底：识别空格对齐的伪表格行，解析为Markdown表格
- **表格行Node单独标记 `is_table=true`**，并把表头作为额外metadata注入
- 这解决"附录C外业代码表"完全丢失的问题

### 2.2 结构感知切块器

**原文件**：`document_parser.py`（保留基础parse_documents）
**新文件**：`qualityScheme/smart_chunker.py`

#### 切块策略（替代纯SentenceSplitter 256/40）：

```
Step 1: 预过滤 — 剔除 knowledge_type=toc_noise/preface/references 且 section_type=前言+目录 的Node（可选保留术语定义和附录）
Step 2: 按 chapter_path 层级分组 — 相同 5.2.4 的段落先聚合
Step 3: 章节级大块（Parent Chunk）— 完整5.2.4作为1个ParentNode（不切块，用于Small-to-Big检索时补上下文）
Step 4: 条款级细块（Child Chunk）— 在章节内按 a) b) c) 子条款切，每块默认size=384（增大到384因为256常切散中文条款），overlap=64
Step 5: 表格块特殊处理 — 整张表作为1个Node（不切！拆表就是丢信息），超长表才按行分，且metadata里保留表头重复注入
Step 6: 建立 Node Relationships — ChildNode 的 relationships[NodeRelationship.PARENT] = ParentNode.node_id
```

#### 关键参数调整：
| 参数 | 原值 | 新值 | 理由 |
|------|------|------|------|
| chunk_size | 256 | 384 | 中文条款含编号+列表+示例，256易切散 |
| chunk_overlap | 40 | 64 | 增大重叠减少上下文断裂 |
| 噪声过滤 | 无 | TOC/页眉/页码/前言直接排除 | 信噪比提升30%+ |

### 2.3 检查项结构化入库

**新文件**：`qualityScheme/check_items_indexer.py`

把 `check_items.py` 中 `_RAW_CHECK_ITEMS`（28项）也做成 Node 存入 Milvus：
```python
for item in _RAW_CHECK_ITEMS:
    node = TextNode(
        text=f"{item['checkName']}：{item['checkDesc']}。参数：{','.join(item['param_names'])}",
        metadata={
            "doc_type": "check_item",          # 与规范文档的 data_spec 区分！
            "knowledge_type": "check_item_catalog",
            "check_code": item["checkCode"],
            "check_name": item["checkName"],
            "check_desc": item["checkDesc"],
            "param_names": item["param_names"],
            "check_obj_type": item["checkObjType"],
        }
    )
```
→ 这样用户问"编号唯一"时，先检索 `doc_type=check_item` 就能直接命中 `QualityCheckUniqueValue`，不用让LLM读28项大表。

### 2.4 Milvus Metadata Schema 升级

**config.py 保留**，但建 Collection 时启用丰富字段。由于 MilvusVectorStore 会自动把 metadata scalar 字段建索引，我们只需在 Node 里注入字段即可。

⚠️ **注意：Milvus collection 的向量维度如果不变，metadata 字段是自由的，不需要 rebuild schema。但如果我们要新增 filter 字段，确保它们在 Node.metadata 里都有值（缺失的填 "" 或 None）。**

---

## 三、阶段2：检索层增强（P1）——详细设计

### 3.1 Hybrid Search（Dense + BM25 Sparse）

**修改文件**：`query_engine.py` / `metadata_filter.py`

LlamaIndex 的 Milvus 集成本身支持：
```python
# make_query_engine 修改：
engine = index.as_query_engine(
    vector_store_query_mode="hybrid",  # ← 原来是默认"default"=纯Dense
    similarity_top_k=top_k,
    # sparse_top_k 可额外配置，默认和dense_top_k一致
)
```

同时 `retrieve()` 函数同步启用 hybrid 模式。

**预期效果**：
- "GB/T 2260" 这类标准号查询：BM25直接命中 → Top1
- "检测点编号"：Dense + BM25 共同加权 → 避免被"检测点坐标"语义盖过
- "0.5米"：BM25数值关键词权重高 → 阈值相关条款前置

### 3.2 Query Decomposition（多意图分解）

**新文件**：`qualityScheme/query_decomposer.py`

```
用户需求（自然语言）
  ↓ LLM + Pydantic 结构化拆解
  ↓ Prompt示例：
    """你是质检需求分析器。请把用户需求拆成独立的子需求，
    每个子需求包含：intent_type(精度/唯一性/非空/长度/范围/编码/坐标系/几何检查...)、
    data_name(检测点/检测线/...)、constraint(数值阈值或关键字)。"""
  ↓
输出：DecomposedQuery = list[SubQuery]
    例：
    [
      {"intent_type": "精度检查", "data_name": "检测点", "constraint": "≤0.5米"},
      {"intent_type": "唯一性检查", "data_name": "检测点", "constraint": "编号唯一"},
      {"intent_type": "必填非空", "data_name": "检测点", "constraint": "必填字段完整"}
    ]
```

然后**每个 SubQuery 独立走一遍检索流程**：
- SubQuery1 → 检索 quality_rules 关于精度条款 + 检索 check_item_catalog 关于精度检查项
- SubQuery2 → 检索 field_rule 关于编号字段 + 检索 check_item_catalog 关于唯一检查项
- SubQuery3 → 检索 field_rule + check_item 关于必填非空
最后聚合所有检索结果作为统一上下文传给方案生成LLM。

→ **彻底解决"复合需求漏项"问题**。

### 3.3 Metadata Filter 前置检索

**修改文件**：`metadata_filter.py`

原 `retrieve()` 只有 `file_name` 过滤。新流程：

```
用户需求 / SubQuery
  ↓
1. 意图识别阶段附带产出过滤条件：
   - part_number（如果用户提到"第2部分"）
   - data_name（如果提到"检测点"）
   - knowledge_type（"找字段"→ field_rule；"找质量要求"→ quality_rule）
  ↓
2. Metadata Filter 构造：
   MetadataFilters(
       filters=[
           ExactMatchFilter(key="knowledge_type", value="quality_rule"),
           ExactMatchFilter(key="data_name", value="检测点"),
       ],
       condition=FilterCondition.AND  # 支持AND/OR
   )
  ↓
3. 先 Milvus Filter 缩小候选集 → 再 Hybrid 检索
```

→ **这就是 GPT 文档第9节强调的 Metadata Filter + Vector Search 串联**。

同时修正 `retrieve_by_part`：现在直接用 `ExactMatchFilter(key="part_number", value=part_number)` 在 Milvus 侧完成，不再需要取TopK*5内存过滤。

### 3.4 检查项语义匹配（替代读28项大表）

**修改文件**：`scheme_generator.py`

原方案：把28项检查项整表塞给Prompt → LLM读表选。
新方案：
```
1. 用户需求（或每个SubQuery）→ 先在 Milvus 中检索 doc_type=check_item 的 Top-3 候选项
2. 只把这 Top-3 候选项的详情注入 Prompt
3. LLM 在 3 项里裁决选哪 1~2 项 + 填参
```

**收益**：
- Token 减少 80%+（28项→3项）
- 选择准确率大幅提升（不会因为长表漏看最合适项）
- 与 Query Decomposition 组合：每个子意图独立匹配自己的 Top3 检查项。

---

## 四、阶段3：方案生成优化（P1）

### 4.1 参数名规范化（解决 data_name / dataName 混乱）

**修改文件**：`check_items.py`

问题：28项检查项中，有的参数叫 `data_name`，有的叫 `dataName`（驼峰），`fieldNames` 又是驼峰。LLM生成参数名时容易写错风格。

**改进**：
1. 在 `_normalize_param` 阶段，建立**参数别名映射表**：
   ```python
   PARAM_ALIASES = {
       "dataName": "data_name",
       "data_name": "data_name",
       "fieldNames": "field_names",
       "field_names": "field_names",
       "fieldLengths": "field_lengths",
       "fieldScales": "field_scales",
       "fieldValues": "field_values",
       "fieldTypes": "field_types",
       "geometry_type": "geometry_type",
       "dz_data_name": "dz_data_name",
       "compare_fields_first": "compare_fields_first",
       "compare_fields_second": "compare_fields_second",
       "key_field_first": "key_field_first",
       "key_field_second": "key_field_second",
   }
   ```
2. Prompt 里的参数名**统一使用 snake_case** 输出。
3. 校验阶段：即使 LLM 写错为驼峰，在 `generate_scheme` 最后一步自动归一化为平台实际需要的名字（通过反向映射：snake_case → 原检查项定义里的实际参数名）。

### 4.2 参数值推断增强

**修改**：`scheme_generator.py` 的 Prompt + 后处理。

新增规则：
- 从 Metadata 中命中的 `field_name` 列表优先填入 `fieldNames/field_names` 参数，而不是让LLM瞎猜
- 命中的 `param_hint`（如"0.5米"）优先填入对应 threshold 参数
- 用户需求中的显式数值（正则提取 `\d+(\.\d+)?\s*(米|厘米|度)`）优先用用户给的值，不用规范默认值

### 4.3 检查项"用户未提及不添加"规则强化

原Prompt第4条已写，但LLM仍可能"热情过度"加项。改进：
1. 在 DecomposedQuery 阶段，intent_type 的数量就是方案检查项数量的上限（3个子意图 → 最多3~4个检查项，不允许7~8个）
2. 后处理加一道校验：`if checkCode not in {s.matched_check_codes for s in sub_queries}: remove`

---

## 五、阶段4：工程化完善（P1）

### 5.1 Local 模式不可用修复

**修改文件**：`models.py`

原问题：`LocalHashEmbedding`（随机哈希向量）+ `LocalExtractiveLLM`（纯抽取不生成）= 垃圾结果。

**改进**：
```python
# configure_quality_models 修改：
# local 模式下：
# 1. 优先尝试连接 Ollama（http://localhost:11434）
#    - LLM: Ollama(model="qwen2:7b" 或 "llama3.1:8b")
#    - Embedding: OllamaEmbedding(model="nomic-embed-text")
# 2. 如果 Ollama 连不上：
#    - 抛出 RuntimeError 明确提示：
#      "local模式需要安装Ollama并拉取模型，或配置provider=openai使用在线模型"
#    - 绝不使用 LocalHashEmbedding 假向量
```

### 5.2 调试代码清理

**修改**：`scheme_generator.py` 删除 L123-L131 的 `print()`，改成：
```python
logger.debug("Milvus检索返回 %d 个节点：", len(nodes))
for i, n in enumerate(nodes, start=1):
    logger.debug(
        "节点#%d: score=%.4f, file=%s, content=%s",
        i, n.score, n.node.metadata.get("file_name"), n.node.get_content()[:120],
    )
```

### 5.3 `/api/summary` 缓存Nodes

**修改**：`web.py` 的 `/api/summary`。
把 `parse_documents(load_documents(...))` 的结果在进程启动时算一次，存到 `RuntimeState`。不要每次请求都重新切块+嵌入（切块嵌入很慢）。

### 5.4 Milvus URI 默认留空

**修改**：`config.py` 的默认值：
```python
# 原：milvus_uri: str = "http://milvus-dev1.e-tudou.com:19530"
# 改：milvus_uri: str = ""
# 且 load_quality_config 里如果 milvus_uri 为空，抛明确错误：
# "必须在.env中设置 QUALITY_MILVUS_URI，例如：http://localhost:19530"
```
避免硬编码测试环境地址误连到生产。

---

## 六、阶段5：文件整理

### 6.1 文件保留/删除判定（见最后一项任务详细清单）

### 6.2 生成 FILE_USAGE.md 说明文档

---

## 七、改造后架构图（目标态）

```
                              用户需求
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │   意图识别 + Query分解     │  ← query_decomposer.py（新增）
                    └────────────┬─────────────┘
                                 │ 1..N SubQueries
                    ┌────────────▼─────────────┐
                    │  Router + Metadata过滤    │  ← metadata_filter.py（增强）
                    │  (knowledge_type/data_name)│
                    └────────────┬─────────────┘
                                 │
             ┌───────────────────┼───────────────────┐
             ▼                   ▼                   ▼
  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
  │ Hybrid 检索      │ │ Hybrid 检索      │ │ Hybrid 检索      │
  │ data_spec +      │ │ field_rule +     │ │ check_item +     │
  │ quality_rules    │ │ appendix_table   │ │ catalog(28项)    │  ← check_items_indexer.py（新增）
  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
           │ Dense+BM25         │                    │
           ▼                    ▼                    ▼
  ┌────────────────────────────────────────────────────────────┐
  │  Small-to-Big 补全上下文（Parent章节Node）+ 结果聚合        │  ← smart_chunker.py（新增）
  └─────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │  结构化方案生成           │  ← scheme_generator.py（增强）
                    │  (仅Top-3候选检查项)      │
                    │  + 参数名规范化映射       │
                    │  + 参数值从Metadata注入   │
                    └──────────────────────────┘
                                │
                                ▼
                          质检方案 JSON
```

---

## 八、回滚与验证策略

| 改造项 | 验证方法 | 回滚方法 |
|--------|---------|---------|
| 新PDF提取器 | 比较新老 `.md` 文件的噪声行比例（TOC行占比应<2%）| 保留老 `.md` 备份，切换 data_dir 即可 |
| 新切块器 | 抽样100个Chunk，检查条款边界完整性（不应出现"5.2.4"和"a)"分在两块）| 切回 `DEFAULT_CHUNK_SIZE=256` |
| Metadata增强 | 查询 `/api/retrieve` 接口返回Node的metadata字段数≥8 | 新版Node是增量，rebuild索引回滚即可 |
| Hybrid Search | A/B测试：同一个问题的Top5召回率纯Dense vs Hybrid 提升≥20% | 改回 `vector_store_query_mode="default"` |
| Query分解 | 3个复合需求用例，分解后子意图数=用户期望检查项数，漏项率=0 | 开关参数 `decompose=false` 回退整句检索 |
| 检查项入库 | "编号唯一"查询能直接命中 QualityCheckUniqueValue 的 check_item Node | 回退28项大表Prompt |

---

## 九、本次实际落地范围（考虑时间/复杂度约束）

⚠️ 上面是完整规划，本次代码修改优先落地**P0 + P1中最核心的、立竿见影的项**：

✅ 本次必做：
1. ✅ 新 enhanced_extractor.py：TOC/页眉/页码去噪 + 章节结构解析 + Metadata注入 + 基础表格识别
2. ✅ 新 smart_chunker.py：章节感知切块 + 噪声过滤排除 + 参数调优256→384
3. ✅ check_items_indexer.py：28项检查项入库Milvus
4. ✅ metadata_filter.py：增强过滤（part_number/data_name/knowledge_type）+ 修正retrieve_by_part
5. ✅ query_engine.py：Hybrid Search开关
6. ✅ query_decomposer.py：简单版多意图分解（≥2个子意图时拆分）
7. ✅ scheme_generator.py：检查项TopN语义匹配（不读28项全表）+ 删除print调试 + 参数名映射
8. ✅ check_items.py：参数名别名规范化
9. ✅ models.py：local模式优先Ollama，连不上抛错（不用假哈希）
10. ✅ config.py：Milvus默认URI去硬编码 + web.py summary缓存

❌ 后续优化（本次不做，留给下一迭代）：
- Small-to-Big Parent-Child Node Relationships
- RouterQueryEngine（三路独立路由）
- Recursive Retrieval
- Reranker集成
- Knowledge Graph

---

*改进计划结束。下一步：按本计划逐项修改代码。*
