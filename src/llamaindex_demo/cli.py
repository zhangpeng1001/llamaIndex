"""统一命令行入口。运行 ``python -m llamaindex_demo.cli --help`` 查看用法。"""

from __future__ import annotations

import argparse
import asyncio
import json

from llama_index.core.memory import Memory

from .config import load_config
from .agent import make_knowledge_agent
from .models import configure_models
from .evaluation import evaluate_retriever
from .rag import (
    build_and_persist_index,
    format_sources,
    load_documents,
    make_query_engine,
    make_summary_engine,
    parse_documents,
    retrieve,
)
from .router import deterministic_route, make_llm_router
from .structured import create_knowledge_card
from .workflow import RagWorkflow


def _runtime(args: argparse.Namespace):
    """所有子命令共享的初始化：配置模型，并构建或加载索引。"""

    config = load_config(args.provider)
    llm, embed_model = configure_models(config)
    index = build_and_persist_index(
        config.data_dir, config.storage_dir, embed_model, rebuild=args.rebuild
    )
    return config, llm, embed_model, index


def command_quickstart(args: argparse.Namespace) -> None:
    config, llm, _, index = _runtime(args)
    engine = make_query_engine(index, llm, top_k=args.top_k)
    response = engine.query(args.question)
    print(f"模型模式：{config.provider}\n\n回答：\n{response}\n\n来源：")
    print(format_sources(response.source_nodes))


def command_retrieve(args: argparse.Namespace) -> None:
    _, _, _, index = _runtime(args)
    nodes = retrieve(
        index, args.question, top_k=args.top_k, file_name=args.file_name
    )
    print("检索结果（本命令不会调用 LLM）：")
    print(format_sources(nodes))


def command_chat(args: argparse.Namespace) -> None:
    _, llm, _, index = _runtime(args)
    # v0.14 推荐 Memory；session_id 便于以后接数据库区分不同用户会话。
    memory = Memory.from_defaults(session_id="terminal-demo", token_limit=3000)
    chat_engine = index.as_chat_engine(
        chat_mode="context",
        llm=llm,
        memory=memory,
        system_prompt="你是中文知识库助教。回答必须优先依据检索到的文档。",
    )
    print("进入多轮对话；输入 exit 或 quit 退出。")
    while True:
        question = input("\n你：").strip()
        if question.lower() in {"exit", "quit"}:
            break
        response = chat_engine.chat(question)
        print(f"助教：{response}")


def command_summary(args: argparse.Namespace) -> None:
    config, llm, embed_model, _ = _runtime(args)
    nodes = parse_documents(load_documents(config.data_dir), embed_model)
    response = make_summary_engine(nodes, llm).query(args.question)
    print(f"总结：\n{response}")


def command_router(args: argparse.Namespace) -> None:
    config, llm, embed_model, index = _runtime(args)
    nodes = parse_documents(load_documents(config.data_dir), embed_model)
    vector_engine = make_query_engine(index, llm)
    summary_engine = make_summary_engine(nodes, llm)
    if config.uses_openai:
        response = make_llm_router(vector_engine, summary_engine, llm).query(args.question)
        print(f"内置 LLM Router 回答：\n{response}")
    else:
        route_name, response = deterministic_route(
            args.question, vector_engine, summary_engine
        )
        print(f"离线路由选择：{route_name}\n回答：\n{response}")


def command_structured(args: argparse.Namespace) -> None:
    _, llm, _, _ = _runtime(args)
    card = create_knowledge_card(llm, args.material)
    print(card.model_dump_json(indent=2))


def command_stream(args: argparse.Namespace) -> None:
    _, llm, _, index = _runtime(args)
    engine = index.as_query_engine(llm=llm, similarity_top_k=args.top_k, streaming=True)
    response = engine.query(args.question)
    print("流式回答：")
    response.print_response_stream()
    print()


def command_async(args: argparse.Namespace) -> None:
    """演示异步查询；Web 服务中应优先使用 aquery，避免阻塞事件循环。"""

    _, llm, _, index = _runtime(args)
    engine = make_query_engine(index, llm, top_k=args.top_k)

    async def run() -> None:
        response = await engine.aquery(args.question)
        print(f"异步回答：\n{response}")

    asyncio.run(run())


def command_evaluate(args: argparse.Namespace) -> None:
    """运行不调用 LLM 的可重复检索评估。"""

    _, _, _, index = _runtime(args)
    report = evaluate_retriever(index, top_k=args.top_k)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def command_workflow(args: argparse.Namespace) -> None:
    """通过 Workflow 的类型化事件执行两步 RAG。"""

    _, llm, _, index = _runtime(args)

    async def run() -> None:
        result = await RagWorkflow(index, llm, top_k=args.top_k).run(
            question=args.question
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    asyncio.run(run())


def command_agent(args: argparse.Namespace) -> None:
    """运行支持工具调用的 Agent；当前示例要求 OpenAI function calling。"""

    config, llm, _, index = _runtime(args)
    if not config.uses_openai:
        raise SystemExit(
            "agent 子命令需要支持 function calling 的真实模型。"
            "请配置 OPENAI_API_KEY 后使用 --provider openai；"
            "默认 local 模型仅用于演示确定性 RAG，不会伪造工具调用。"
        )
    query_engine = make_query_engine(index, llm)
    agent = make_knowledge_agent(query_engine, llm)

    async def run() -> None:
        result = await agent.run(user_msg=args.question)
        print(f"Agent 回答：\n{result}")

    asyncio.run(run())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LlamaIndex 中文核心功能 Demo")
    parser.add_argument(
        "--provider", choices=["local", "openai"], help="覆盖 .env 中的模型提供方"
    )
    parser.add_argument(
        "--rebuild", action="store_true", help="删除旧 storage 后重新解析并构建索引"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def question_command(name: str, help_text: str, default: str):
        child = subparsers.add_parser(name, help=help_text)
        child.add_argument("question", nargs="?", default=default)
        child.add_argument("--top-k", type=int, default=3)
        return child

    quickstart = question_command(
        "quickstart", "完成一次带来源的 RAG 问答", "LlamaIndex 的五个主要阶段是什么？"
    )
    quickstart.set_defaults(func=command_quickstart)

    raw_retrieve = question_command(
        "retrieve", "只执行向量检索并显示分数", "持久化索引有什么好处？"
    )
    raw_retrieve.add_argument("--file-name", help="按 metadata 中的 file_name 精确过滤")
    raw_retrieve.set_defaults(func=command_retrieve)

    chat = subparsers.add_parser("chat", help="进入带记忆的多轮知识库对话")
    chat.set_defaults(func=command_chat)

    summary = subparsers.add_parser("summary", help="使用 SummaryIndex 总结所有文档")
    summary.add_argument("question", nargs="?", default="请总结这些文档的核心内容")
    summary.set_defaults(func=command_summary)

    router = subparsers.add_parser("router", help="在向量问答与全文总结之间路由")
    router.add_argument("question", nargs="?", default="请整体总结项目知识库")
    router.set_defaults(func=command_router)

    structured = subparsers.add_parser("structured", help="生成 Pydantic 结构化输出")
    structured.add_argument(
        "material", nargs="?", default="LlamaIndex 使用索引和检索器构建 RAG 应用。"
    )
    structured.set_defaults(func=command_structured)

    stream = question_command(
        "stream", "逐 Token/字符打印生成结果", "为什么 RAG 回答需要显示来源？"
    )
    stream.set_defaults(func=command_stream)

    async_query = question_command(
        "async", "使用异步 QueryEngine", "Document 和 Node 有什么区别？"
    )
    async_query.set_defaults(func=command_async)

    evaluate = subparsers.add_parser("evaluate", help="计算检索 Hit Rate 与 MRR")
    evaluate.add_argument("--top-k", type=int, default=3)
    evaluate.set_defaults(func=command_evaluate)

    workflow = question_command(
        "workflow", "用事件和 step 显式编排检索与生成", "星河项目的代号是什么？"
    )
    workflow.set_defaults(func=command_workflow)

    agent = subparsers.add_parser(
        "agent", help="让支持 function calling 的模型自主调用知识库工具（OpenAI）"
    )
    agent.add_argument("question", nargs="?", default="星河项目的代号是什么？")
    agent.set_defaults(func=command_agent)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
