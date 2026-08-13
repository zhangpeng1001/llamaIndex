"""使用 LlamaIndex Workflow 显式编排“检索 -> 生成”事件流。

QueryEngine 适合标准 RAG；当业务出现审核、分支、重试、人工介入等复杂逻辑时，
Workflow 能把每个阶段建模为带类型的事件与异步 step。
"""

from __future__ import annotations

from llama_index.core import VectorStoreIndex
from llama_index.core.llms import LLM
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step

from .rag import retrieve


class RetrievedEvent(Event):
    """第一步产生的事件，也是第二步的类型安全输入。"""

    question: str
    context: str
    sources: list[str]


class RagWorkflow(Workflow):
    """两步式 RAG 工作流；实例可以通过 ``await workflow.run(...)`` 执行。"""

    def __init__(self, index: VectorStoreIndex, llm: LLM, top_k: int = 3) -> None:
        super().__init__(timeout=60, verbose=False)
        self.index = index
        self.llm = llm
        self.top_k = top_k

    @step
    async def retrieve_step(self, ev: StartEvent) -> RetrievedEvent:
        """把 StartEvent 中的 question 转为检索上下文事件。"""

        question = str(ev.get("question", ""))
        if not question:
            raise ValueError("Workflow 必须传入非空 question")
        nodes = retrieve(self.index, question, top_k=self.top_k)
        context = "\n\n".join(item.node.get_content() for item in nodes)
        sources = [
            str(item.node.metadata.get("file_name", "未知文件")) for item in nodes
        ]
        return RetrievedEvent(
            question=question, context=context, sources=sources
        )

    @step
    async def synthesize_step(self, ev: RetrievedEvent) -> StopEvent:
        """消费 RetrievedEvent，用 LLM 生成答案并结束工作流。"""

        prompt = (
            "请只根据下面的知识库上下文回答问题；证据不足时明确说不知道。\n\n"
            f"上下文：\n{ev.context}\n\n问题：{ev.question}\n回答："
        )
        completion = await self.llm.acomplete(prompt)
        # StopEvent.result 可以是字符串、字典或业务对象；这里返回字典以保留来源。
        return StopEvent(
            result={"answer": completion.text, "sources": ev.sources}
        )

