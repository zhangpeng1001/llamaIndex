from llamaindex_demo.config import DATA_DIR
from llamaindex_demo.local_models import LocalExtractiveLLM, LocalHashEmbedding
from llamaindex_demo.rag import (
    build_vector_index,
    load_documents,
    make_query_engine,
    parse_documents,
    retrieve,
)


def _index():
    embedding = LocalHashEmbedding()
    documents = load_documents(DATA_DIR)
    nodes = parse_documents(documents, embedding)
    return build_vector_index(nodes, embedding)


def test_load_parse_and_retrieve():
    index = _index()
    results = retrieve(index, "星河项目的代号和负责人", top_k=2)
    assert results
    assert any("Aurora-7" in item.node.get_content() for item in results)


def test_metadata_filter():
    index = _index()
    results = retrieve(
        index, "RAG", top_k=5, file_name="02_rag_practice.md"
    )
    assert results
    assert all(
        item.node.metadata["file_name"] == "02_rag_practice.md" for item in results
    )


def test_query_engine_has_sources():
    index = _index()
    response = make_query_engine(index, LocalExtractiveLLM()).query(
        "LlamaIndex 有哪些主要阶段？"
    )
    assert response.source_nodes
