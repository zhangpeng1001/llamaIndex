import asyncio

from llama_index.core.memory import Memory

from llamaindex_demo.config import DATA_DIR
from llamaindex_demo.local_models import LocalExtractiveLLM, LocalHashEmbedding
from llamaindex_demo.rag import build_vector_index, load_documents, parse_documents


def test_context_chat_engine_runs_two_turns():
    embedding = LocalHashEmbedding()
    nodes = parse_documents(load_documents(DATA_DIR), embedding)
    index = build_vector_index(nodes, embedding)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=LocalExtractiveLLM(),
        memory=Memory.from_defaults(session_id="test", token_limit=3000),
    )

    # Python 3.13 不再隐式创建默认 loop；当前 ChatEngine 的同步兼容层仍会读取它。
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        first = chat_engine.chat("星河项目的代号是什么？")
        second = chat_engine.chat("负责人呢？")
        assert str(first)
        assert str(second)
    finally:
        loop.close()
        asyncio.set_event_loop(None)
