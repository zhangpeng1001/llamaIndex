"""src 包:质检规范 RAG 系统的精简重写版。

按 RAG 四大阶段组织:
    - loading.py   加载(Loading): PDF→MD增强 + MD→Document
    - indexing.py   索引(Indexing): 章节切块 + 嵌入 + Node JSON 导出
    - storing.py   存储(Storing): Milvus VectorStore + 写入 + manifest
    - querying.py  查询(Querying): Hybrid检索 + MetadataFilter + QueryEngine

附加能力:
    - summary.py   全文总结(SummaryIndex + tree_summarize)
    - scheme.py    质检方案生成(查询分解+TopN候选+Pydantic)
    - server.py    FastAPI 入口(端口 8082)

设计原则:
    1. 复用 qualityScheme 中已优化的核心函数,不重新实现已优化逻辑
    2. 每个阶段独立可执行,产物存入 RuntimeState 跨请求复用
    3. 启动只加载 config + models,不自动构建索引,用户按需触发各阶段
    4. 每个文件包含详细中文注释和结构化日志
"""
