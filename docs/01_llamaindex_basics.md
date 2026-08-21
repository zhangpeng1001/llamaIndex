# LlamaIndex 基础概念

LlamaIndex 是一个用于构建大语言模型数据应用的框架。它擅长把私有数据接入大语言模型，常见用途包括 RAG 问答、知识库、智能体和文档分析。

一个典型 LlamaIndex 应用可以分成五个阶段：加载（Loading）、索引（Indexing）、存储（Storing）、查询（Querying）和评估（Evaluation）。加载阶段把文件或外部系统转成 Document。索引阶段把 Document 切成 Node，计算嵌入向量并组织索引。存储阶段保存索引、文档和向量。查询阶段完成检索和响应合成。评估阶段检查检索命中率、忠实度和回答相关性。

Document 表示完整的输入资料，Node 表示从资料切分出的较小语义单元。Node 会保留与原 Document 的关系及 metadata。合理的 chunk_size 和 chunk_overlap 会影响召回率、上下文完整性和成本。

QueryEngine 处理单轮问题，ChatEngine 在查询能力之上加入对话历史。Retriever 只负责找到相关节点；Response Synthesizer 负责把问题和节点交给 LLM，合成为最终回答。

