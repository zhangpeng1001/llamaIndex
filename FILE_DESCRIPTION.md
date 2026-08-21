# 项目文件说明文档

本文档说明 `E:\project\agent\llamaIndex` 目录下所有文件与目录的用途、保留原因，便于后续维护。

---

## 一、核心业务（质检方案生成）⭐

> 这是项目的**主营业务代码**，基于 `standard/` 中的 7 份时空数据规范 PDF，
> 在 Milvus 中构建向量知识库，并根据用户自然语言需求生成**质检方案**。

### 1.1 业务数据源

| 文件/目录 | 用途 | 保留原因 |
|---|---|---|
| `standard/` | 7 份原始**时空数据规范 PDF**（第1~7部分）：数据分类、检测点、检测线、标志性地物、重要要素、高精度栅格、资源数据 | PDF 是业务权威来源；当规范更新时，需要重新用 PDF → Markdown 提取脚本刷新 `qualityScheme/data/`。**不能删除**。 |
| `qualityScheme/data/` | 从 `standard/` 的 7 份 PDF 中提取出的 Markdown 文本（`part1_*.md` ~ `part7_*.md`），共 337+ 切块 | 是业务 RAG 的**实际输入**，被 `document_loader.py` 直接加载。删除后系统无法构建索引。 |

### 1.2 业务代码（qualityScheme/ 下的 .py 文件）

每个模块一个文件，对应 8 个 API 端点的功能链路：

| 文件名 | 职责 | 说明 |
|---|---|---|
| `__init__.py` | 包初始化 | 使 `qualityScheme` 成为可导入的 Python 包。 |
| `config.py` | 业务配置读取 | 从 `.env` 加载模型、Milvus 连接、数据/存储路径等。**Milvus URI 必须通过 `.env` 显式配置，无硬编码默认值。** |
| `models.py` | LLM / Embedding 模型创建 | - `openai` 模式：走 OpenAI 兼容接口（推荐）<br>- `local` 模式：自动连接本地 Ollama（需安装 Ollama + 拉取 `qwen2.5:7b`、`nomic-embed-text`），失败时给出明确指引，不再使用旧版无效的 LocalHashEmbedding。 |
| `enhanced_extractor.py` | **增强版 PDF 提取器**（P0 新增） | 替换原 `_extract_pdfs.py` 的薄弱实现。功能：去噪（目录/页眉页脚/表格残片）、识别章节结构、注入 `part_number` / `knowledge_type` / `data_name` 等丰富元数据。**规范更新时优先使用此脚本重新提取。** |
| `_extract_pdfs.py` | 旧版 PDF 提取脚本（薄封装） | **保留作向后兼容**，但推荐改用 `enhanced_extractor.py` 获得更高质量的 Markdown。 |
| `smart_chunker.py` | **结构感知切块器**（P0 新增） | 按章节路径分组切块，不切断章节边界；表格作为整块保留；建立父子 chunk 关系。解决旧版切块把章节切碎导致上下文丢失的问题。 |
| `document_loader.py` | 文档加载 | 用 `SimpleDirectoryReader` 从 `qualityScheme/data/` 读取 Markdown 文档。 |
| `document_parser.py` | 文档切块与摄取管线 | 调用 `smart_chunker.py` 对 Document 做结构感知切块。 |
| `check_items.py` | 28 项质检检查项定义（含参数别名映射） | 定义 `CheckItem` Pydantic 模型及 28 条内置检查项清单。**已新增 camelCase / snake_case 参数别名映射**，解决 `posAccuracy` vs `pos_accuracy` 命名混乱导致的空值问题。 |
| `check_items_indexer.py` | **检查项语义索引**（P0 新增） | 把 28 个检查项嵌入到 Milvus 的独立分区或独立索引，支持"检查项名称 → 语义检索"匹配。替代旧版 LLM 读大表选 28 选 N 的低准确率方案。 |
| `milvus_store.py` | Milvus 向量存储封装 | 创建 Milvus 连接、探测嵌入维度、确保 DB 存在、构建 `MilvusVectorStore`。 |
| `vector_index.py` | 构建 `VectorStoreIndex` | 把切块后的 Node 写入 Milvus，形成可检索的向量索引。 |
| `index_persistence.py` | 索引构建与持久化入口 | 首次启动构建索引并写 Milvus；后续启动从 Milvus 加载。配合 `--rebuild` 强制重建。 |
| `metadata_filter.py` | **增强版元数据过滤 + Hybrid Search**（P1 重写） | - 支持 8+ 业务字段过滤：`part_number` / `knowledge_type` / `data_name` / `chapter_path` / `file_name` 等<br>- 修正旧版 `retrieve_by_part` 在 Python 端过滤的错误，改为 Milvus 原生 Expr 过滤<br>- 默认启用 **Hybrid Search**（Dense 向量 + BM25 稀疏检索），提升编号/阈值类查询召回率 |
| `query_decomposer.py` | **用户需求多意图分解**（P1 新增） | 把"生成一套包含地物匹配、高程精度检查、航空照片匹配的方案"这类复合需求，拆成多个子意图分别检索，避免漏项。 |
| `query_engine.py` | 查询引擎构造 | 默认 `top_k=5`（原 3 太低），默认 Hybrid Search 模式。 |
| `source_tracker.py` | 检索来源格式化 | 把 `source_nodes` 转成可读的字典/字符串，前端用于展示来源章节与分数。 |
| `summary_engine.py` | 全文总结引擎构造 | 基于 `SummaryIndex` + `tree_summarize` 遍历全部材料做归纳。 |
| `scheme_intent.py` | 质检方案意图识别 | 识别用户需求属于"生成方案/仅查检查项/仅查参数阈值"等哪种意图。 |
| `scheme_generator.py` | **质检方案生成核心**（P1 重写） | 串联 Query 分解 → 子意图检索 → 检查项语义匹配 → 参数别名规范化 → Pydantic 结构化输出。是方案生成准确率提升的关键模块。 |
| `scheme_api.py` | 方案相关 HTTP 路由注册 | 在 `web.py` 中被调用，注册 `/api/scheme/*` 的路由。 |
| `web.py` | **FastAPI 主服务**（P1 增加缓存） | 启动入口，8 个 API：`/health`、`/rebuild`、`/quickstart`、`/retrieve`、`/retrieve/part`、`/summary`、`/stream`、`/async`。**`/api/summary` 已新增两级缓存（answer 缓存 + nodes 缓存，TTL 1 小时）**，避免每次重新切块+总结。默认端口 8001。 |
| `static/` | 前端页面（index.html/app.js/style.css） | 6 个功能面板：问答、按部分检索、总结、流式对话、异步问答、质检方案生成。由 FastAPI 直接挂载到 `/` 路由。 |

---

## 二、LlamaIndex 学习 Demo（参考资料用）

> 这部分是项目**最初的学习目标**——一个从空目录搭建的、带详细中文注释的 LlamaIndex
> 教学 Demo。当前核心业务 `qualityScheme/` 是独立开发的，**代码层面已不再引用此 Demo**，
> 但作为 LlamaIndex 框架学习与组件理解的参考资料，仍有保留价值。

### 2.1 Demo 代码

| 文件/目录 | 用途 | 保留原因 |
|---|---|---|
| `src/llamaindex_demo/` | 14 个 LlamaIndex 教学模块：`rag.py` / `router.py` / `structured.py` / `workflow.py` / `agent.py` / `evaluation.py` / `local_models.py` 等 + CLI 入口 + Web 服务 | 每个模块对应 LlamaIndex 一个核心概念，注释非常详细。后续若需要扩展 `qualityScheme/` 的高级能力（如 Agent 工具调用、事件工作流、检索评估），可参考此处实现。 |
| `data/` | Demo 的 3 份学习资料：LlamaIndex 基础概念、RAG 实践、项目手册 | Demo 的知识库样例数据，与 qualityScheme 业务无关。仅用于 Demo 跑通 RAG 流程。 |
| `docs/` | 4 份中文学习文档：架构导览、学习指南、官方资源、问题排查 | 指导初学者按顺序掌握 LlamaIndex。 |
| `README.md` | Demo 的使用说明（安装、启动、CLI 命令、切换 OpenAI） | 对应 Demo 的完整文档；**qualityScheme 业务的启动方式见下文第五节**。 |
| `pyproject.toml` | 项目包配置与依赖 | 当前仍是项目**唯一的依赖清单入口**（`llama-index==0.14.23` + Milvus/FastAPI 等），`pip install -e ".[dev]"` 从此读取。后续若新增 Ollama 依赖（`llama-index-llms-ollama` 等）也需在此补充。 |
| `requirements.txt` / `requirements-dev.txt` | 依赖的 requirements 风格备份 | 与 `pyproject.toml` 依赖基本一致，方便不习惯用 `pip install -e` 的用户直接 `pip install -r requirements.txt`。 |

---

## 三、项目配置与元数据

| 文件/目录 | 用途 | 保留原因 |
|---|---|---|
| `.env.example` | 环境变量模板 | 包含 `OPENAI_API_KEY`、模型名、**`QUALITY_MILVUS_*` 连接信息** 等模板。**新项目必须复制为 `.env` 并填写实际值**（Milvus 相关变量是必填，无默认值）。 |
| `.gitignore` | Git 忽略规则 | 忽略 `.venv/`、`.env`、`__pycache__/`、`storage/` 等本地运行产物，避免提交敏感信息与大文件。 |
| `.idea/` | PyCharm / IntelliJ IDEA 的项目配置（`.iml`、inspection、VCS 等） | 如果团队使用 JetBrains IDE 开发，可共享运行配置与代码风格；即便不使用，通常也**不删除**（由个人 IDE 管理，`.gitignore` 也未排除）。 |
| `.venv/` | Python 虚拟环境（已安装依赖） | 运行时必需；已在 `.gitignore` 中，不会被提交。删除后需要重新 `python -m venv .venv && pip install -e ".[dev]"` 重建，**不建议删除**。 |

---

## 四、本次优化产出文档（2026-08-18 生成）

| 文件 | 内容 | 保留原因 |
|---|---|---|
| `PROBLEM_ANALYSIS.md` | **核心问题分析报告**：对照 `llamaIndex-gpt.docx`（GPT 方案总结），从 PDF 提取质量、元数据缺失、切块策略、检索方式、Query 分解、检查项选择、Milvus 单 Collection、本地伪模型 8 个维度，指出当前实现的**根本缺陷**与对应 GPT 文档章节建议 | 是本次优化的"诊断依据"，后续若效果仍不理想，可回到此文档逐项核查。 |
| `IMPROVEMENT_PLAN.md` | **改进计划**：把问题分析转成 P0（必须做）/ P1（高优先级）/ P2（锦上添花）任务清单，每项任务明确"改哪个文件、达到什么效果、对应 GPT 哪一节" | 是本次优化的"执行清单"，**已全部落地 P0+P1**；后续做 P2 时可继续跟进。 |
| `llamaIndex-gpt.docx` | 原始 GPT 方案总结（用户提供） | 是优化的"参考标准"，对比当前实现找差距的依据。保留作为历史文档。 |
| `FILE_DESCRIPTION.md` | **本文档**：全项目文件用途说明与保留理由 | 新人接手时的"导航地图"，避免误删关键文件或把 Demo 与业务代码混淆。**本文档是本次任务的产出。** |

---

## 五、如何启动核心业务（质检方案生成）

### 前置准备（一次性）

1. 复制 `.env.example` 为 `.env`，填写必填项：
   ```dotenv
   # 模型（推荐 openai 模式；local 模式需要启动 Ollama）
   LLAMAINDEX_MODEL_PROVIDER=openai
   OPENAI_API_KEY=sk-xxx
   LLAMAINDEX_LLM_MODEL=gpt-4.1-mini
   LLAMAINDEX_EMBED_MODEL=text-embedding-3-small
   
   # Milvus 连接（三个 QUALITY_MILVUS_* 变量必填，无默认值）
   QUALITY_MILVUS_URI=http://milvus-dev1.e-tudou.com:19530
   QUALITY_MILVUS_DB=kernel_data_platform
   QUALITY_MILVUS_COLLECTION=qualityScheme_llamaIndex
   ```

2. 安装依赖：
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -m pip install -e ".[dev]"
   # 如果用 local 模式，额外安装 Ollama 适配：
   python -m pip install llama-index-llms-ollama llama-index-embeddings-ollama
   ```

### 启动质检业务 Web 服务

```powershell
# 首次 / 规范更新后：加 --rebuild 重新从 qualityScheme/data/ 提取并写入 Milvus
python -m qualityScheme.web --provider openai --rebuild

# 日常启动（从 Milvus 直接加载已有索引）
python -m qualityScheme.web --provider openai
```

访问：
- 前端页面：`http://127.0.0.1:8001/`
- API 文档：`http://127.0.0.1:8001/docs`
- 健康检查：`http://127.0.0.1:8001/api/health`

### 规范 PDF 更新时的处理流程

1. 把新版 PDF 放到 `standard/`，覆盖旧文件。
2. 运行**增强版提取脚本**（推荐）：
   ```powershell
   python -m qualityScheme.enhanced_extractor
   ```
   这会用 `enhanced_extractor.py` 重新生成 `qualityScheme/data/part1_*.md` ~ `part7_*.md`，
   并自动去噪、加注结构信息与元数据。
3. 重启 Web 服务并加 `--rebuild`，重新写 Milvus 索引：
   ```powershell
   python -m qualityScheme.web --provider openai --rebuild
   ```

---

## 六、文件清理决策摘要

本次清理**未删除任何有业务或参考价值的文件**，仅做了以下运行时清理（可随时重新生成）：
- 删除 `qualityScheme/__pycache__/` 与 `src/llamaindex_demo/__pycache__/`（Python 字节码缓存）

以下常见"看似无用"的目录**刻意保留**：
- `.idea/` → IDE 共享配置
- `.venv/` → 运行时虚拟环境（删除需重装所有依赖）
- `src/llamaindex_demo/` + `data/` + `docs/` → LlamaIndex 学习参考，架构与组件导览
- `standard/` → 原始 PDF 规范源（更新时必需）
- `_extract_pdfs.py` → 旧版提取脚本，保留作向后兼容
