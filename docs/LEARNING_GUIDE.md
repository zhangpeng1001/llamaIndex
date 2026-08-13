# LlamaIndex 核心概念学习指南

## 1. LlamaIndex 解决什么问题

LLM 的参数知识不包含你的实时私有资料。把整套知识直接塞进 Prompt 又会遇到上下文长度、成本和噪声问题。LlamaIndex 的核心工作是把数据预处理成可查询结构，在问题到来时选出少量相关证据，再让 LLM 基于证据回答。

这就是最常见的 RAG，但 LlamaIndex 还提供数据连接器、索引、检索器、查询引擎、聊天引擎、路由、结构化输出、工作流、智能体和评估组件。本项目聚焦所有数据应用都会用到的核心部分。

## 2. Loading：从文件到 Document

打开 `rag.py` 的 `load_documents`。`SimpleDirectoryReader` 将 `data/` 中每份文件读成一个或多个 `Document`，同时生成文件名、路径等 metadata。

练习：打印 `documents[0].text` 和 `documents[0].metadata`。然后新增一个 `.md` 文件，重新构建索引。

真实项目可以使用数据库、Notion、Google Drive、网页等 Reader。无论数据来自哪里，后续阶段通常面对统一的 Document/Node 抽象。

## 3. Ingestion：切块、变换与嵌入

`IngestionPipeline` 接受一串 transformations。本项目按顺序执行：

1. `SentenceSplitter(chunk_size=256, chunk_overlap=40)`；
2. Embedding 模型。

切块是 RAG 中最值得实验的参数之一。`chunk_size` 不是“字符数”的简单同义词，默认 splitter 通常基于 tokenizer 估算 token。重叠区用于保留跨边界语义，但也会增加存储和重复召回。

可以进一步加入 metadata 提取、隐私脱敏、内容清洗、自定义 Node ID 和去重策略。增量数据管道还需要正确处理文档更新和删除，否则旧 Node 会继续被召回。

## 4. Indexing 与 Storing

`VectorStoreIndex` 为每个 Node 保存向量。查询向量与节点向量通常按余弦相似度或等价距离排序。

本项目通过 `StorageContext.persist()` 把内存状态写到 `storage/`，通过 `load_index_from_storage()` 恢复。修改 Embedding 模型后必须重建索引，因为不同模型的向量空间与维度往往不同。

`SummaryIndex` 与向量索引目标不同：前者更适合遍历材料做整体汇总，后者更适合从大量材料里取少量相关块。没有一种索引适合所有问题，这也是 Router 存在的原因。

## 5. Retrieval：先看证据，再看答案

调试 RAG 时，第一步应该运行 `retrieve`，而不是直接评价最终回答。它返回 `NodeWithScore`：

- `node`：命中的内容与 metadata；
- `score`：相似程度；绝对阈值因模型和数据而异；
- 排名：通常比跨模型比较绝对分数更有意义。

如果正确证据没有被找到，再强的 LLM 也难以忠实回答。可改善切块、查询改写、Embedding、Top-K、metadata、reranker 或混合检索。

`MetadataFilters` 适合限定部门、租户、时间或文件类型。但安全系统不能只依赖 Prompt 告诉模型“不要看”，必须在检索之前执行访问控制。

## 6. QueryEngine：检索 + 响应合成

`index.as_query_engine()` 是高层便利接口，内部把 Retriever 与 Response Synthesizer 组合起来。`response_mode="compact"` 会尽量减少 LLM 调用次数。

常见响应模式思路包括：

- compact：合并上下文后回答，适合普通问答；
- refine：逐块修订答案，调用更多但能处理较长材料；
- tree_summarize：层级总结，适合大量材料归纳；
- no_text：只运行检索，便于检查节点。

最终响应的 `source_nodes` 是可解释性入口。本项目展示文件名、分数和片段；生产 UI 通常还会提供页码、链接、引用定位和权限检查。

## 7. ChatEngine 与 Memory

单轮 QueryEngine 不自动理解“它”“刚才那个项目”等指代。ChatEngine 加入历史，让后续问题可依赖前文。本项目使用 `chat_mode="context"`，每一轮仍从知识库检索上下文。

Memory 不应无限增长。达到上下文限制时要截断或总结旧消息。生产系统还应隔离 session/user，防止会话信息串用，并谨慎持久化包含个人数据的历史。

## 8. Router 与组合能力

同一个知识库可能同时需要精确事实检索与全局总结。Router 把多个 QueryEngine 包装为工具，根据问题选择一个分支。

local 模式使用关键词确定性路由，方便测试。OpenAI 模式使用 `RouterQueryEngine`，由 LLM 阅读工具描述并选择。工具 description 应写清“什么时候使用”，否则路由选择会不稳定。

## 9. 结构化输出

普通 LLM 返回字符串，业务系统往往需要字段明确的数据。`LLMTextCompletionProgram` 把 Prompt、LLM、Pydantic 模型连起来：模型输出经过解析和类型校验后成为 `KnowledgeCard`。

结构化输出能降低下游解析成本，但不能证明事实正确。字段校验、业务规则校验和证据核验仍不可少。

## 10. Streaming 与 Async

Streaming 改善“首字延迟”的主观体验，完整总耗时未必下降。客户端要正确处理增量 Token、取消、网络中断和最终来源信息。

异步接口适合 FastAPI 等并发服务。应从 Web handler 一直异步到 `aquery`/模型客户端，避免用同步网络请求阻塞事件循环。

## 11. Evaluation：用问题集驱动改进

`evaluation.py` 先评估检索：

- Hit Rate@K：正确资料是否进入前 K；
- MRR：第一份正确资料的排名质量。

完整 RAG 还应评价回答相关性、忠实度、引用正确性、拒答能力、延迟和成本。评估集必须来自真实业务问题，并包含无答案、模糊、越权和对抗样例。每次修改切块、Prompt 或模型都应回归比较，而不是只看几个演示问题。

## 12. Workflow：复杂流程的事件编排

`workflow.py` 把检索结果包装为 `RetrievedEvent`，再由下一个异步 step 消费，最终通过 `StopEvent` 返回答案和来源。类型签名同时描述了步骤的输入输出，框架据此构建事件图。

对于标准问答，QueryEngine 更简洁；Workflow 更适合审核、重试、分支、并行与人工介入。

## 13. Agent 与工具调用

`agent.py` 把 QueryEngine 包装成 `QueryEngineTool`，再交给 `FunctionAgent`。Agent 的 LLM 会读取工具名称、参数和 description，决定何时调用。工具描述必须具体，工具输出必须当作不可信输入防范提示注入，高风险写操作还需要权限检查和人工确认。

本项目只在 OpenAI 模式运行 Agent。`LocalExtractiveLLM` 不支持 function calling；强行让它模拟选择会掩盖 Agent 的真实机制。对于路径固定的知识库问答，QueryEngine 通常比 Agent 更便宜、更稳定、更容易评估。

## 14. 后续扩展清单

完成本项目后，可以按顺序扩展：

1. 接入真实中文 Embedding，并比较离线评估；
2. 换用持久化向量数据库；
3. 增加 BM25 + 向量的混合检索和 reranker；
4. 为摄取管道实现稳定 doc_id、增量更新和删除；
5. 接入 Web API 与前端引用展示；
6. 增加 tracing、Token/费用统计和线上反馈；
7. 在确实需要外部工具调用时学习 LlamaIndex Workflows/Agents。
