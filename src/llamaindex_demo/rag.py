"""RAG 主流程：加载、切分、索引、持久化、检索和生成。"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    SummaryIndex,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.llms import LLM
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import BaseNode, Document, NodeWithScore
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters


def load_documents(data_dir: Path) -> list[Document]:
    """读取目录中的 Markdown/TXT 文件，并生成 Document 对象。

    SimpleDirectoryReader 会自动把 ``file_name``、``file_path`` 等信息放入 metadata，
    后面既可以显示来源，也可以用于过滤检索。
    """

    documents = SimpleDirectoryReader(
        input_dir=str(data_dir),
        recursive=True,
        required_exts=[".md", ".txt"],
    ).load_data()
    if not documents:
        raise RuntimeError(f"目录中没有可读取的文档：{data_dir}")
    return documents


def parse_documents(
    documents: list[Document], embed_model: BaseEmbedding
) -> list[BaseNode]:
    """通过 IngestionPipeline 把 Document 转换成带向量的 Node。

    SentenceSplitter 负责分块；Embedding 负责把块变成向量。真实项目还可加入标题提取、
    脱敏、去重等 Transformation。较小块便于在样例文档中观察多个检索结果。
    """

    splitter = SentenceSplitter(chunk_size=256, chunk_overlap=40)
    pipeline = IngestionPipeline(transformations=[splitter, embed_model])
    return list(pipeline.run(documents=documents, show_progress=False))


def build_vector_index(
    nodes: list[BaseNode], embed_model: BaseEmbedding
) -> VectorStoreIndex:
    """创建内存向量索引；节点已有向量，因此不会重复计算。"""

    return VectorStoreIndex(nodes=nodes, embed_model=embed_model)


def build_and_persist_index(
    data_dir: Path, storage_dir: Path, embed_model: BaseEmbedding, *, rebuild: bool = False
) -> VectorStoreIndex:
    """构建索引并持久化，或直接加载已有索引。"""

    index_store_file = storage_dir / "index_store.json"
    manifest_file = storage_dir / "demo_manifest.json"
    current_embed_model = str(
        getattr(embed_model, "model_name", type(embed_model).__name__)
    )
    if index_store_file.exists() and not rebuild:
        # 不同 Embedding 模型的向量空间/维度不可混用。自有 manifest 比等待底层
        # 抛出“向量维度不匹配”更容易理解，也方便以后加入 chunk 参数版本检查。
        if manifest_file.exists():
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            stored_embed_model = manifest.get("embedding_model")
            if stored_embed_model != current_embed_model:
                raise RuntimeError(
                    "现有索引使用的 Embedding 模型是 "
                    f"{stored_embed_model!r}，当前模型是 {current_embed_model!r}。"
                    "请增加 --rebuild 重新构建索引。"
                )
        storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
        return load_index_from_storage(
            storage_context, embed_model=embed_model
        )

    # rebuild 是明确的用户请求；只清理项目内固定 storage 目录中的旧索引。
    if rebuild and storage_dir.exists():
        shutil.rmtree(storage_dir)
    nodes = parse_documents(load_documents(data_dir), embed_model)
    index = build_vector_index(nodes, embed_model)
    index.storage_context.persist(persist_dir=str(storage_dir))
    manifest_file.write_text(
        json.dumps(
            {"embedding_model": current_embed_model, "schema_version": 1},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return index


def retrieve(
    index: VectorStoreIndex,
    question: str,
    *,
    top_k: int = 3,
    file_name: str | None = None,
) -> list[NodeWithScore]:
    """执行纯检索，不调用 LLM；适合调试“找到了什么”。"""

    filters = None
    if file_name:
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="file_name", value=file_name)]
        )
    retriever = index.as_retriever(similarity_top_k=top_k, filters=filters)
    return list(retriever.retrieve(question))


def make_query_engine(
    index: VectorStoreIndex, llm: LLM, *, top_k: int = 3
) -> BaseQueryEngine:
    """将 Retriever 与响应合成器组合成 QueryEngine。"""

    return index.as_query_engine(
        llm=llm,
        similarity_top_k=top_k,
        # compact 会尽量把检索块放进一次 LLM 请求，适合普通短问答。
        response_mode="compact",
    )


def make_summary_engine(nodes: list[BaseNode], llm: LLM) -> BaseQueryEngine:
    """SummaryIndex 会遍历材料，适合全局总结，而非只取最相似的几个块。"""

    summary_index = SummaryIndex(nodes)
    return summary_index.as_query_engine(llm=llm, response_mode="tree_summarize")


def format_sources(source_nodes: list[NodeWithScore]) -> str:
    """把响应中的溯源节点格式化为适合终端阅读的文本。"""

    lines: list[str] = []
    for position, item in enumerate(source_nodes, start=1):
        file_name = item.node.metadata.get("file_name", "未知文件")
        score = f"{item.score:.4f}" if item.score is not None else "N/A"
        preview = item.node.get_content().replace("\n", " ")[:100]
        lines.append(f"  {position}. {file_name} | score={score} | {preview}…")
    return "\n".join(lines) if lines else "  （无来源节点）"
