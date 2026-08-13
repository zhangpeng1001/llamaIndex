import asyncio

from llamaindex_demo.config import DATA_DIR
from llamaindex_demo.local_models import LocalExtractiveLLM, LocalHashEmbedding
from llamaindex_demo.rag import build_vector_index, load_documents, parse_documents
from llamaindex_demo.workflow import RagWorkflow


def test_workflow_returns_answer_and_sources():
    embedding = LocalHashEmbedding()
    nodes = parse_documents(load_documents(DATA_DIR), embedding)
    index = build_vector_index(nodes, embedding)

    # Workflow.run() 创建 asyncio Task，因此也必须在已经运行的事件循环中调用。
    async def run_workflow():
        return await RagWorkflow(index, LocalExtractiveLLM()).run(
            question="星河项目的代号是什么？"
        )

    result = asyncio.run(run_workflow())
    assert "answer" in result
    assert "Aurora-7" in result["answer"]
    assert "03_project_handbook.md" in result["sources"]
