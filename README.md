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

## 2. 五分钟跑通

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

## 5. 推荐阅读顺序

1. 先读并运行 `quickstart`，在 `rag.py` 中跟踪一条问题的完整路径。
2. 修改 `data/03_project_handbook.md`，加 `--rebuild` 后验证新事实能否检索到。
3. 使用 `retrieve` 调整 `top_k`，理解“检索”和“生成”是两个阶段。
4. 依次实验 summary、chat、router、structured、workflow。
5. 配置支持 function calling 的真实模型后实验 agent。
6. 修改 `evaluation.py` 的黄金问题集，用数据比较参数效果。
7. 比较离线哈希嵌入与真正语义嵌入。

更完整的概念说明见 [docs/LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md)，架构与代码导览见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)，常见问题见 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)，继续深入时可查阅 [docs/OFFICIAL_RESOURCES.md](docs/OFFICIAL_RESOURCES.md)。
