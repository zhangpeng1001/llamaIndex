"""评估命令行入口。

默认连接当前项目的 `src` RAG 链路。若只想验证检索质量，可增加 `--retrieval-only`，
这样不会调用 LLM；但仍需要已有的 Milvus 索引。没有 Milvus 时，建议直接在 Python
中注入一个测试 retriever，或先完成 src 的 Loading→Indexing→Storing 流程。
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .dataset import default_cases, load_cases, save_cases
from .evaluator import RAGEvaluator


def build_src_evaluator(provider: str | None, retrieval_only: bool) -> RAGEvaluator:
    """加载当前项目配置、模型和 Milvus 索引，构造真实 RAG 评估器。"""

    from src.config import load_config
    from src.models import configure_quality_models
    from src.storing import load_existing_index

    config = load_config(provider)
    llm, embed_model = configure_quality_models(config)
    index = load_existing_index(config, embed_model)
    if index is None:
        raise RuntimeError("没有可用索引，请先运行 src 的 Loading→Indexing→Storing 流程")
    return RAGEvaluator.from_src(index, None if retrieval_only else llm)


def build_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器。"""

    parser = argparse.ArgumentParser(description="简单、可解释的 RAG 质量评估工具")
    parser.add_argument("--dataset", type=Path, help="黄金问题 JSON；不传则使用内置问题集")
    parser.add_argument("--output", type=Path, default=Path("evaluation/report.json"), help="报告输出路径")
    parser.add_argument("--top-k", type=int, default=5, help="每题检索节点数，默认 5")
    parser.add_argument("--provider", choices=["local", "openai"], help="覆盖 src 的模型提供方")
    parser.add_argument("--retrieval-only", action="store_true", help="只评估检索，不调用 LLM")
    parser.add_argument("--write-default-dataset", type=Path, help="把内置黄金集写到指定 JSON 后退出")
    return parser


def main() -> None:
    """命令行主函数，打印简明汇总并保存完整 JSON 报告。"""

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = build_parser().parse_args()
    if args.write_default_dataset:
        save_cases(default_cases(), args.write_default_dataset)
        print(f"已写入默认黄金集: {args.write_default_dataset}")
        return

    cases = load_cases(args.dataset) if args.dataset else default_cases()
    evaluator = build_src_evaluator(args.provider, args.retrieval_only)
    report = evaluator.evaluate(cases, top_k=args.top_k, retrieval_only=args.retrieval_only)
    report.save(args.output)
    print(json.dumps(report.summary, ensure_ascii=False, indent=2))
    print(f"完整报告已写入: {args.output.resolve()}")


if __name__ == "__main__":
    main()
