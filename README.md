# LlamaIndex 中文学习 Demo

这是一个从空目录搭建的、可直接运行的 LlamaIndex 教学项目。代码包含详细中文注释，并同时支持：

- `local`：默认模式，无 API Key、无网络调用也能走通完整框架流程；
- `openai`：使用真实 LLM 与 Embedding，体验有语义理解能力的 RAG。

项目基于 `llama-index 0.14.23`。离线模型只是教学替身，目的是让你观察框架组件怎样协作，回答质量不能代表真实模型。

## 已实现功能

| 功能 | 对应代码 | 你会学到什么 |
|---|---|---|
| 文档加载 | `rag.py/load_documents` | `SimpleDirectoryReader`、`Document`、metadata |
| 数据摄取 | `rag.py/parse_documents` | `IngestionPipeline`、切块、Embedding、Node |
| 向量索引 | `rag.py/build_vector_index` | `VectorStoreIndex`、相似度检索 |
| 索引持久化 | `rag.py/build_and_persist_index` | `StorageContext`、加载已有索引 |
| RAG 问答 | `rag.py/make_query_engine` | Retriever、Response Synthesizer、QueryEngine |
| 来源追踪 | `rag.py/format_sources` | `source_nodes`、score、metadata |
| 元数据过滤 | `rag.py/retrieve` | `MetadataFilters`、`ExactMatchFilter` |
| 全文总结 | `rag.py/make_summary_engine` | `SummaryIndex`、`tree_summarize` |
| 多轮对话 | `cli.py/command_chat` | `ChatEngine`、`Memory`、上下文模式 |
| 查询路由 | `router.py` | 确定性路由、`RouterQueryEngine`、QueryEngineTool |
| 结构化输出 | `structured.py` | Program、Pydantic schema、输出校验 |
| 流式/异步 | `cli.py` | streaming、`aquery` |
| 检索评估 | `evaluation.py` | 黄金问题集、Hit Rate、MRR |
| 事件工作流 | `workflow.py` | `Workflow`、Event、step、Start/StopEvent |
| 工具调用 Agent | `agent.py` | `FunctionAgent`、QueryEngineTool（OpenAI 可选） |
| 自定义模型 | `local_models.py` | `CustomLLM`、`BaseEmbedding` 扩展接口 |

## 1. 安装

推荐 Python 3.10～3.13。本目录已经创建过 `.venv` 时可以直接激活；在新机器上执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

macOS/Linux 的激活命令为：

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## 2. 启动方式

本项目有两种启动方式：**CLI 命令行**和 **Web 服务**，二者复用同一套业务代码，区别只在交互形式。

> 注意：`llama-demo` 后面跟的是**子命令**（如 `web`、`quickstart`、`chat`），**没有 `llama-demo main` 这种用法**。`main` 只是 Python 入口函数名（见 `src/llamaindex_demo/cli.py` 的 `main()`），不是 CLI 命令。完整子命令列表执行 `llama-demo --help` 查看。

| 子命令 | 作用 | 是否启动 HTTP 服务 |
|---|---|---|
| `quickstart` | 一次 RAG 问答 | 否 |
| `retrieve` | 只检索不生成 | 否 |
| `chat` | 多轮命令行对话 | 否 |
| `summary` / `router` / `structured` / `stream` / `async` / `workflow` / `evaluate` | 各功能实验 | 否 |
| `agent` | 工具调用 Agent（需 OpenAI） | 否 |
| `web` | 启动 FastAPI 服务 | ✅ 是 |

### 2.1 启动 Web 服务（后端 API + 前端页面一条命令同时起）

本项目**没有独立的前端工程**，前端是 `src/llamaindex_demo/static/` 下的静态文件，由 FastAPI 直接托管（见 `web.py` 末尾 `app.mount("/", StaticFiles(...))`）。因此 `llama-demo web` 一条命令会同时启动后端 API 和前端页面，**无需单独启动前端**。

```powershell
llama-demo web                       # 默认 127.0.0.1:8000
llama-demo web --port 8080           # 自定义端口
llama-demo web --host 0.0.0.0        # 允许局域网访问
llama-demo --provider openai --rebuild web   # OpenAI 模式并重建索引
```

启动成功后：

- 前端页面：浏览器打开 `http://127.0.0.1:8000`
- API 文档（Swagger UI）：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/api/health`

### 2.2 CLI 方式启动（不开 HTTP 服务）

适合在终端里快速实验单个功能：

```powershell
llama-demo quickstart                # 五分钟跑通
llama-demo chat                      # 多轮对话
llama-demo retrieve "你的问题"        # 只检索
```

### 2.3 不使用 `llama-demo` 命令的原始启动方式

如果没执行 `pip install -e .`，或找不到 `llama-demo` 命令，可用 `python -m` 等价启动（需先设 PYTHONPATH）：

```powershell
$env:PYTHONPATH = "src"

python -m llamaindex_demo.cli web          # 等价于 llama-demo web
python -m llamaindex_demo.cli quickstart   # 等价于 llama-demo quickstart
```

也可以直接用 `uvicorn` 启动 Web 服务（等价效果，`--reload` 适合开发调试）：

```powershell
$env:PYTHONPATH = "src"
uvicorn llamaindex_demo.web:app --host 127.0.0.1 --port 8000 --reload
```

## 3. 五分钟跑通（CLI）

```powershell
# 默认 local 模式：构建索引并执行问答
llama-demo quickstart

# 如果没有使用可编辑安装，也可直接这样运行
python -m llamaindex_demo.cli quickstart

# 观察纯检索结果和相似度分数
llama-demo retrieve "星河项目什么时候同步知识库？"

# 强制重新切块、嵌入并构建 storage
llama-demo --rebuild quickstart "LlamaIndex 的五个阶段是什么？"
```

第一次运行会创建 `storage/`。后续运行自动加载已有索引，因此不会重复计算 Embedding。修改 `data/` 中的材料后，需要增加 `--rebuild`。

## 3. 切换真实 OpenAI 模型

复制 `.env.example` 为 `.env`，填写：

```dotenv
OPENAI_API_KEY=你的密钥
LLAMAINDEX_MODEL_PROVIDER=openai
LLAMAINDEX_LLM_MODEL=gpt-4.1-mini
LLAMAINDEX_EMBED_MODEL=text-embedding-3-small
```

然后重建索引。不同 Embedding 模型产生的向量不可混用：

```powershell
llama-demo --provider openai --rebuild quickstart "RAG 有什么优势？"
```

这会调用外部 API 并产生费用。请勿把 `.env` 提交到版本库。

### 3.1 使用公司自建 / 第三方 OpenAI 兼容服务

如果无法直连 OpenAI 官方地址，或想走公司网关、本地部署、第三方平台（如 Azure OpenAI 兼容层、one-api 等），在 `.env` 中额外配置 `OPENAI_API_BASE`：

```dotenv
OPENAI_API_KEY=你的密钥
LLAMAINDEX_MODEL_PROVIDER=openai
LLAMAINDEX_LLM_MODEL=gpt-4.1-mini
LLAMAINDEX_EMBED_MODEL=text-embedding-3-small

# 自定义服务地址：只填到 /v1 结尾，客户端会自动补 /chat/completions、/embeddings
OPENAI_API_BASE=https://ai2-api.i-tudou.com/v1
```

> ⚠️ 注意：`OPENAI_API_BASE` 只需填到 `/v1` 即可，**不要**带上 `/chat/completions`。
> 客户端会根据具体调用（对话 / 向量）自动拼接对应路径。

改完 `OPENAI_API_BASE` 后，Embedding 端点也会同步切换，因此必须加 `--rebuild` 重建索引：

```powershell
llama-demo --provider openai --rebuild quickstart "RAG 有什么优势？"
```

如果服务端使用的是自定义模型名（非 `gpt-4.1-mini` 等 OpenAI 官方模型名），同时修改 `LLAMAINDEX_LLM_MODEL` 与 `LLAMAINDEX_EMBED_MODEL` 为平台支持的模型名即可。

## 4. 逐项实验

```powershell
# 只检索，不生成；限定只查某个文件
llama-demo retrieve "Top-K 如何选择？" --file-name 02_rag_practice.md

# 多轮对话；输入 exit 退出
llama-demo chat

# 遍历材料做总结
llama-demo summary "总结全部文档并给出三个学习重点"

# 自动选择局部问答或全文总结分支
llama-demo router "星河项目代号是什么？"
llama-demo router "请整体总结这些材料"

# 把自然语言转换为经过 Pydantic 校验的 JSON
llama-demo structured "RAG 通过检索私有知识增强模型回答"

# 流式输出与异步接口
llama-demo stream "为什么回答需要来源？"
llama-demo async "Document 和 Node 有什么区别？"

# 运行检索评估
llama-demo evaluate --top-k 3

# 使用类型化事件显式编排“检索 -> 生成”
llama-demo workflow "星河项目的代号是什么？"

# 让真实模型自主决定并调用知识库工具（需要 OpenAI 配置）
llama-demo --provider openai agent "查一下星河项目负责人，然后解释信息来源"

# 单元测试
pytest -q
```

## 6. 推荐阅读顺序

1. 先读并运行 `quickstart`，在 `rag.py` 中跟踪一条问题的完整路径。
2. 修改 `data/03_project_handbook.md`，加 `--rebuild` 后验证新事实能否检索到。
3. 使用 `retrieve` 调整 `top_k`，理解“检索”和“生成”是两个阶段。
4. 依次实验 summary、chat、router、structured、workflow。
5. 配置支持 function calling 的真实模型后实验 agent。
6. 修改 `evaluation.py` 的黄金问题集，用数据比较参数效果。
7. 比较离线哈希嵌入与真正语义嵌入。

更完整的概念说明见 [docs/LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md)，架构与代码导览见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)，常见问题见 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)，继续深入时可查阅 [docs/OFFICIAL_RESOURCES.md](docs/OFFICIAL_RESOURCES.md)。
