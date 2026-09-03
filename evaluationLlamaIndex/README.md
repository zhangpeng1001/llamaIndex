# LlamaIndex 内置 Evaluator RAG 评估 Demo

本目录专门演示如何使用 LlamaIndex 自带的评估能力，不重新实现评分算法。
当前项目版本为 `llama-index==0.14.23`。

## 1. 评估什么

### 检索质量

使用：

```python
from llama_index.core.evaluation import RetrieverEvaluator

evaluator = RetrieverEvaluator.from_metric_names(
    ["hit_rate", "mrr"],
    retriever=retriever,
)
result = evaluator.evaluate(query=query, expected_ids=expected_ids)
```

- `hit_rate`：Top-K 中是否命中了至少一个正确 Node。
- `mrr`：第一个正确 Node 排名越靠前，分数越高。

`expected_ids` 必须是人工标注的正确 Node ID。示例 ID 来自当前 `src/node/*.json`。
重新执行 Indexing 后 Node ID 可能变化，需要同步更新黄金问题集。

### 生成质量

本模块使用三个 LlamaIndex 原生 Evaluator：

- `CorrectnessEvaluator`：答案与参考答案是否正确、完整，返回 1～5 分。
- `FaithfulnessEvaluator`：答案是否能被召回上下文支持，返回 YES/NO。
- `RelevancyEvaluator`：问题、上下文和答案是否相关，返回 YES/NO。

它们都使用 LLM 作为评审者，因此真实模式会产生额外模型请求和费用。

### 批量评估

三个生成评估器通过 `BatchEvalRunner` 批量运行：

```python
runner = BatchEvalRunner(
    evaluators={
        "correctness": CorrectnessEvaluator(llm=llm),
        "faithfulness": FaithfulnessEvaluator(llm=llm),
        "relevancy": RelevancyEvaluator(llm=llm),
    },
    workers=2,
)
results = runner.evaluate_queries(
    query_engine,
    queries=queries,
    correctness={"reference": reference_answers},
)
```

本目录的 `runner.py` 对上述原生结果做了轻量整理，保留每题的 `score`、`passing`、
`feedback`、`response` 和 `contexts`，并额外保存检索结果 ID。

## 2. 运行

在项目根目录执行：

```powershell
cd E:\project\agent\llamaIndex

# 无 Milvus、无 OpenAI/Ollama 的教学演示
python -m evaluationLlamaIndex.cli --demo

# 只评估真实索引的检索质量
python -m evaluationLlamaIndex.cli --retrieval-only --top-k 5

# 评估真实检索 + 答案生成质量
python -m evaluationLlamaIndex.cli --top-k 5 --workers 2

# 使用自定义黄金集
python -m evaluationLlamaIndex.cli `
  --dataset evaluationLlamaIndex/examples/golden_questions.json `
  --output evaluationLlamaIndex/report.json
```

默认报告路径是 `evaluationLlamaIndex/report.json`。真实模式要求 Milvus 中已经存在
索引；没有索引时程序会直接提示先完成 `Loading→Indexing→Storing`，不会自动重建。

导出默认黄金集：

```powershell
python -m evaluationLlamaIndex.cli `
  --write-default-dataset evaluationLlamaIndex/examples/my_questions.json
```

## 3. 黄金问题格式

```json
{
  "query": "资源数据由什么组成？",
  "expected_ids": ["真实 Node ID"],
  "reference_answer": "资源数据由数据体及元数据组成。",
  "tags": ["资源数据", "术语"]
}
```

- `query`：发送给 RAG 的问题。
- `expected_ids`：检索评估必填；应填写一个或多个正确 Node ID。
- `reference_answer`：CorrectnessEvaluator 的参考答案；只做检索评估时可以省略。
- `tags`：仅用于人工管理，不参与评分。

## 4. 两种模式的差异

### 真实模式

`cli.py` 调用现有 `src.config`、`src.models`、`src.storing` 和 `src.querying`，连接真实
Embedding、Milvus、Retriever、QueryEngine 和 LLM。它衡量的是当前系统实际运行质量。

### Demo 模式

`demo.py` 使用两个内存 TextNode、一个简单 BaseRetriever、固定 Response 和一个返回
合法 YES/NO/分数格式的 `CustomLLM`。它的目的只是展示 LlamaIndex Evaluator 的输入输出，
结果不代表真实模型质量，也不会产生网络请求。

## 5. 如何阅读报告

```json
{
  "retrieval": {"hit_rate": 1.0, "mrr": 1.0},
  "generation": {
    "correctness": {"average_score": 4.5, "passing_rate": 1.0},
    "faithfulness": {"average_score": 1.0, "passing_rate": 1.0},
    "relevancy": {"average_score": 1.0, "passing_rate": 1.0}
  }
}
```

- `score`：LlamaIndex Evaluator 返回的数值分数。
- `passing`：是否达到该 Evaluator 的通过阈值。
- `feedback`：评审 LLM 给出的理由或 YES/NO 原文。
- `contexts`：本题生成答案使用的召回上下文。
- `failed_case_count`：执行或评审异常的问题数。

评估分数不能完全替代人工审核。尤其是 Faithfulness/Relevancy 的判断仍取决于评审
模型，建议把高频真实问题加入黄金集，并结合人工抽查观察长期趋势。

## 6. 代码入口

- `models.py`：黄金问题数据模型。
- `dataset.py`：黄金集 JSON 读写和默认问题。
- `runner.py`：RetrieverEvaluator、三个生成 Evaluator、BatchEvalRunner 的适配。
- `demo.py`：无外部依赖的内存演示。
- `cli.py`：命令行入口和真实模式初始化。

所有新增函数、异常处理、批量失败降级和 API 关键参数均带有中文注释。
