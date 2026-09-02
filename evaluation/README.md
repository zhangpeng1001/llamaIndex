# RAG 评估模块

这个目录提供一个适合 Demo 学习的、可重复运行的 RAG 评估模块。它不改变 `src` 的索引和问答逻辑，而是复用现有的：

- `src.querying.run_querying`：真实 Hybrid 检索；
- `src.querying.make_engine`：真实检索后生成答案；
- `src.storing.load_existing_index`：加载已经存在的 Milvus 索引。

## 目录结构

| 文件 | 作用 |
|---|---|
| `models.py` | 定义黄金问题 `EvaluationCase` |
| `dataset.py` | 读取/保存问题集，提供当前规范的默认问题 |
| `metrics.py` | 检索和答案的可解释指标 |
| `evaluator.py` | 批量执行评估，输出每题明细和汇总 |
| `cli.py` | 命令行入口 |
| `examples/golden_questions.json` | 可直接编辑的示例黄金集 |

## 快速开始

先确保项目已经完成索引构建，且 `.env` 中的 Milvus 和模型配置可用：

```powershell
cd E:\project\agent\llamaIndex
python -m evaluation.cli --retrieval-only --top-k 5 --output evaluation\retrieval_report.json
```

评估检索和生成：

```powershell
python -m evaluation.cli --top-k 5 --output evaluation\rag_report.json
```

如果想把内置黄金集复制出来再编辑：

```powershell
python -m evaluation.cli --write-default-dataset evaluation\my_questions.json
python -m evaluation.cli --dataset evaluation\my_questions.json
```

## 指标解释

### 检索指标

- `hit_rate_at_k`：Top-K 中是否至少有一个相关节点；最直观地回答“有没有找对”。
- `mrr_at_k`：第一个相关节点排名越靠前分数越高；能区分 Top1 命中和 Top5 命中。
- `precision_at_k`：Top-K 中相关节点比例；反映召回结果是否混入很多噪声。
- `recall_at_k`：黄金集标注多个源文件时，找回了多少个源文件；单文件问题退化为命中值。
- `first_relevant_rank`：第一个相关节点的 1-based 排名，未命中为 `null`。

### 答案指标

- `answer_keyword_coverage`：答案覆盖了多少个黄金关键词。
- `context_keyword_coverage`：召回上下文覆盖了多少个黄金关键词，用于区分“答案没说”与“检索没找到”。
- `answer_grounded_keyword_rate`：答案中出现的黄金关键词有多少也出现在召回上下文中，是一个简单的上下文支撑度指标。
- `answer_non_empty`：答案是否为空。

这些答案指标是启发式指标，不等同于事实正确率。真实项目应持续增加人工审核结果，或接入独立评估模型交叉验证。

## 在 Python 中接入真实 RAG

```python
from evaluation.dataset import load_cases
from evaluation.evaluator import RAGEvaluator
from src.config import load_config
from src.models import configure_quality_models
from src.storing import load_existing_index

config = load_config()
llm, embed_model = configure_quality_models(config)
index = load_existing_index(config, embed_model)
if index is None:
    raise RuntimeError("请先构建索引")

evaluator = RAGEvaluator.from_src(index, llm)
report = evaluator.evaluate(load_cases("evaluation/examples/golden_questions.json"), top_k=5)
report.save("evaluation/report.json")
print(report.summary)
```

## 接入自己的检索函数

只要返回节点序列即可，节点可以是 LlamaIndex `NodeWithScore`、普通字典或字符串：

```python
def my_retriever(question: str, top_k: int):
    return my_index.search(question, limit=top_k)

evaluator = RAGEvaluator(my_retriever)
```

黄金集中的 `relevant_files`、`relevant_keywords` 越准确，评估结果越有意义。建议先用 10～30 条真实用户问题建立小规模回归集，再逐步扩充。
