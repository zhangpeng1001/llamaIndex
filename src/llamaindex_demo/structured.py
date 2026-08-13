"""用 LlamaIndex Program + Pydantic 获得可校验的结构化输出。"""

from __future__ import annotations

from typing import Literal

from llama_index.core.llms import LLM
from llama_index.core.program import LLMTextCompletionProgram
from pydantic import BaseModel, Field


class KnowledgeCard(BaseModel):
    """模型输出必须满足的业务数据结构。"""

    title: str = Field(description="学习卡片标题")
    summary: str = Field(description="不超过 100 字的知识摘要")
    keywords: list[str] = Field(description="3 到 6 个关键词")
    difficulty: Literal["beginner", "intermediate", "advanced"]


def create_knowledge_card(llm: LLM, material: str) -> KnowledgeCard:
    """把非结构化学习材料转换为经过 Pydantic 校验的对象。"""

    program = LLMTextCompletionProgram.from_defaults(
        output_cls=KnowledgeCard,
        llm=llm,
        prompt_template_str=(
            "请阅读下面材料，生成一张 Knowledge_Card 学习卡片。\n"
            "材料：{material}\n"
        ),
        verbose=False,
    )
    return program(material=material)

