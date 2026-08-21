"""RuntimeState 跨阶段共享状态 + Summary 两级缓存。

学习要点:
    - 进程级共享状态:FastAPI 单进程多请求下,config/llm/embed_model/index 等重对象
      在 startup 时构建一次,跨请求复用,避免每次请求重新加载。
    - 阶段产物链路:Loading→documents, Indexing→nodes, Storing→index。
      下一阶段直接复用上一阶段产物,无需重复计算。
    - Summary 两级缓存:
        1. answer 缓存:相同 question 直接返回上次结果(TTL 1h),省 LLM 调用。
        2. nodes 缓存:跨 question 复用切块结果(避免每次 parse_documents)。
    - rebuild 时清空所有产物 + summary 缓存,保证新旧数据不混杂。

业务背景:
    质检规范 RAG 四大阶段产物需要跨请求共享:
        - Loading 产出的 documents 可被 Indexing 复用
        - Indexing 产出的 nodes 可被 Storing 写入 + Summary 缓存复用
        - Storing 产出的 index 可被 Querying 检索 + 方案生成复用
    阶段完成标志用于前端按钮依赖检查(Indexing 依赖 Loading,Storing 依赖 Indexing)。
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Summary 缓存的 TTL(秒)。默认 1 小时,足以覆盖日常使用且不会因规范更新而太陈旧。
_SUMMARY_CACHE_TTL = 3600
# Summary 缓存最大条目数(按 question 维度),避免无边界内存增长。
_SUMMARY_CACHE_MAX = 32


class RuntimeState:
    """跨请求共享的运行时状态。

    属性:
        config: 质检业务配置(startup 时加载)。
        llm: 语言模型(startup 时配置)。
        embed_model: 嵌入模型(startup 时配置)。
        vector_store: MilvusVectorStore(Storing 时创建)。
        documents: Loading 阶段产出的章节级 Document 列表。
        nodes: Indexing 阶段产出的规范文档 Node 列表(spec_nodes)。
        check_item_nodes: Indexing 阶段产出的检查项 Node 列表。
        index: Storing 阶段产出的 VectorStoreIndex(可查询)。
        loading_done: Loading 阶段完成标志。
        indexing_done: Indexing 阶段完成标志。
        storing_done: Storing 阶段完成标志。

    Summary 缓存(私有):
        _summary_nodes_cache: key=data_dir, value=(ts, nodes)。
        _summary_answer_cache: key=question_hash, value=(ts, answer)。
    """

    def __init__(self) -> None:
        # startup 时加载的基础对象
        self.config: Any = None
        self.llm: Any = None
        self.embed_model: Any = None
        self.vector_store: Any = None

        # 四阶段产物
        self.documents: list[Any] | None = None
        self.nodes: list[Any] | None = None  # spec_nodes
        self.check_item_nodes: list[Any] | None = None
        self.index: Any = None  # VectorStoreIndex

        # 阶段完成标志
        self.loading_done: bool = False
        self.indexing_done: bool = False
        self.storing_done: bool = False

        # 异步锁(防止并发 rebuild 竞态)
        self._lock = asyncio.Lock()

        # Summary 两级缓存
        self._summary_nodes_cache: dict[str, tuple[float, Any]] = {}
        self._summary_answer_cache: dict[str, tuple[float, str]] = {}

    @property
    def ready(self) -> bool:
        """基础就绪:config 和 models 已加载(不含 index)。"""
        return self.config is not None and self.llm is not None and self.embed_model is not None

    @property
    def index_ready(self) -> bool:
        """索引就绪:Storing 阶段已完成,index 可用于查询。"""
        return self.ready and self.index is not None and self.storing_done

    def reset_pipeline(self) -> None:
        """rebuild 时重置四阶段产物 + 阶段标志 + summary 缓存。

        保留 config/llm/embed_model(这些 startup 时加载,无需重建)。
        清空 documents/nodes/index 等阶段产物,保证 rebuild 后数据一致。
        """

        logger.info("重置 RuntimeState: 清空阶段产物 + summary 缓存")
        self.documents = None
        self.nodes = None
        self.check_item_nodes = None
        self.index = None
        self.vector_store = None
        self.loading_done = False
        self.indexing_done = False
        self.storing_done = False
        self.invalidate_summary_cache()

    def get_state_dict(self) -> dict[str, Any]:
        """返回当前阶段状态(给 /api/state 端点用)。"""

        return {
            "loading_done": self.loading_done,
            "indexing_done": self.indexing_done,
            "storing_done": self.storing_done,
            "index_ready": self.index_ready,
            "documents_count": len(self.documents) if self.documents else 0,
            "nodes_count": len(self.nodes) if self.nodes else 0,
            "check_item_nodes_count": len(self.check_item_nodes) if self.check_item_nodes else 0,
        }

    # ------------------------------------------------------------------
    # Summary 缓存方法(复用原 qualityScheme/web.py 的设计)
    # ------------------------------------------------------------------

    def _evict_expired(self) -> None:
        """清理过期缓存(懒清理:每次读写时调用一次)。"""

        now = time.time()
        for cache in (self._summary_nodes_cache, self._summary_answer_cache):
            expired_keys = [k for k, (ts, _) in cache.items() if now - ts > _SUMMARY_CACHE_TTL]
            for k in expired_keys:
                cache.pop(k, None)

    def get_summary_nodes(self, data_dir: Path) -> Any | None:
        """读取已缓存的 summary 节点;不存在或过期返回 None。"""

        self._evict_expired()
        entry = self._summary_nodes_cache.get(str(data_dir))
        if entry is None:
            return None
        logger.info("Summary 节点缓存命中: data_dir=%s", data_dir)
        return entry[1]

    def set_summary_nodes(self, data_dir: Path, nodes: Any) -> None:
        """写入 summary 节点缓存。"""

        self._evict_expired()
        if len(self._summary_nodes_cache) >= _SUMMARY_CACHE_MAX:
            # 淘汰最早的一条
            oldest_key = min(self._summary_nodes_cache, key=lambda k: self._summary_nodes_cache[k][0])
            self._summary_nodes_cache.pop(oldest_key, None)
        self._summary_nodes_cache[str(data_dir)] = (time.time(), nodes)
        logger.info(
            "Summary 节点已缓存: data_dir=%s, 条目数=%d",
            data_dir,
            len(self._summary_nodes_cache),
        )

    def get_summary_answer(self, question: str) -> str | None:
        """读取已缓存的 summary 回答;不存在或过期返回 None。"""

        self._evict_expired()
        key = hashlib.md5(question.encode("utf-8")).hexdigest()
        entry = self._summary_answer_cache.get(key)
        if entry is None:
            return None
        logger.info("Summary 回答命中缓存: question=%s", question[:50])
        return entry[1]

    def set_summary_answer(self, question: str, answer: str) -> None:
        """写入 summary 回答缓存。"""

        self._evict_expired()
        if len(self._summary_answer_cache) >= _SUMMARY_CACHE_MAX:
            oldest_key = min(self._summary_answer_cache, key=lambda k: self._summary_answer_cache[k][0])
            self._summary_answer_cache.pop(oldest_key, None)
        key = hashlib.md5(question.encode("utf-8")).hexdigest()
        self._summary_answer_cache[key] = (time.time(), answer)
        logger.info(
            "Summary 回答已缓存: question=%s, 缓存条目=%d",
            question[:50],
            len(self._summary_answer_cache),
        )

    def invalidate_summary_cache(self) -> None:
        """在 rebuild 索引时清空 summary 缓存,保证新旧数据不混杂。"""

        self._summary_nodes_cache.clear()
        self._summary_answer_cache.clear()
        logger.info("Summary 缓存已清空(rebuild 触发)")


# 全局单例:整个进程共享一个 RuntimeState
state = RuntimeState()
