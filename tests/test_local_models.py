from llamaindex_demo.local_models import LocalExtractiveLLM, LocalHashEmbedding


def test_local_embedding_is_deterministic_and_normalized():
    model = LocalHashEmbedding()
    first = model.get_text_embedding("LlamaIndex 向量检索")
    second = model.get_text_embedding("LlamaIndex 向量检索")
    assert first == second
    assert abs(sum(value * value for value in first) - 1.0) < 1e-6


def test_local_llm_returns_text():
    response = LocalExtractiveLLM().complete(
        "Context information is below.\n星河项目代号为 Aurora-7。\nQuery: 项目代号是什么？"
    )
    assert "Aurora-7" in response.text

