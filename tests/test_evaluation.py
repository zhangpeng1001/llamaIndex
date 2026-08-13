from llamaindex_demo.config import DATA_DIR
from llamaindex_demo.evaluation import evaluate_retriever
from llamaindex_demo.local_models import LocalHashEmbedding
from llamaindex_demo.rag import build_vector_index, load_documents, parse_documents


def test_evaluation_report_shape():
    embedding = LocalHashEmbedding()
    nodes = parse_documents(load_documents(DATA_DIR), embedding)
    report = evaluate_retriever(build_vector_index(nodes, embedding), top_k=3)
    assert 0 <= report["hit_rate"] <= 1
    assert 0 <= report["mrr"] <= 1
    assert len(report["details"]) == 4

