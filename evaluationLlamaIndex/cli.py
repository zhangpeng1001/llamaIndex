"""命令行入口：真实 RAG 评估和离线 Demo。"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .dataset import default_cases, load_cases, save_cases
from .demo import build_demo_evaluator
from .runner import LlamaIndexRAGEvaluator


def build_real_evaluator(provider: str | None, top_k: int, workers: int) -> LlamaIndexRAGEvaluator:
    """加载当前项目的配置、模型和已有 Milvus 索引。"""

    from src.config import load_config
    from src.models import configure_quality_models
    from src.storing import load_existing_index

    config = load_config(provider)
    llm, embed_model = configure_quality_models(config)
    index = load_existing_index(config, embed_model)
    if index is None:
        raise RuntimeError(
            "没有可用 Milvus 索引，请先完成 src 的 Loading→Indexing→Storing 流程"
        )
    return LlamaIndexRAGEvaluator.from_src(
        index,
        llm,
        top_k=top_k,
        workers=workers,
    )


def build_parser() -> argparse.ArgumentParser:
    """创建 CLI 参数解析器。"""

    parser = argparse.ArgumentParser(description="使用 LlamaIndex 内置 Evaluator 评估 RAG")
    parser.add_argument("--dataset", type=Path, help="黄金问题 JSON；不传则使用内置问题集")
    parser.add_argument("--output", type=Path, default=Path("evaluationLlamaIndex/report.json"))
    parser.add_argument("--top-k", type=int, default=5, help="Retriever 返回节点数，默认 5")
    parser.add_argument("--workers", type=int, default=2, help="BatchEvalRunner 并发数，默认 2")
    parser.add_argument("--provider", choices=["local", "openai"], help="覆盖 src 模型提供方")
    parser.add_argument("--retrieval-only", action="store_true", help="只运行 RetrieverEvaluator")
    parser.add_argument("--demo", action="store_true", help="运行无外部服务的内存演示")
    parser.add_argument("--write-default-dataset", type=Path, help="导出内置黄金集后退出")
    return parser


def main() -> None:
    """解析参数、执行评估、保存 JSON 并打印汇总。"""

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    args = build_parser().parse_args()
    if args.write_default_dataset:
        save_cases(default_cases(), args.write_default_dataset)
        print(f"已写入默认黄金集：{args.write_default_dataset.resolve()}")
        return

    if args.top_k <= 0 or args.workers <= 0:
        raise SystemExit("--top-k 和 --workers 必须大于 0")

    if args.demo:
        evaluator, cases, responses = build_demo_evaluator()
        report = evaluator.evaluate(
            cases,
            retrieval_only=args.retrieval_only,
            responses=None if args.retrieval_only else responses,
            mode="demo",
        )
    else:
        cases = load_cases(args.dataset) if args.dataset else default_cases()
        evaluator = build_real_evaluator(args.provider, args.top_k, args.workers)
        report = evaluator.evaluate(
            cases,
            retrieval_only=args.retrieval_only,
            mode="real",
        )

    report.save(args.output)
    print(json.dumps(report.summary, ensure_ascii=False, indent=2))
    print(f"完整报告已写入：{args.output.resolve()}")


if __name__ == "__main__":
    main()
