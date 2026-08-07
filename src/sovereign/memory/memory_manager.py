"""SOVEREIGN — unified memory access & pruning.

Facade over working / episodic / semantic / procedural / vector memory.
``store``/``retrieve``/``search`` dispatch on memory_type; ``prune`` enforces
the retention policies.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from sovereign.governance.data_retention import DataRetention
from sovereign.memory.episodic_memory import EpisodicMemory
from sovereign.memory.procedural_memory import ProceduralMemory
from sovereign.memory.semantic_memory import SemanticMemory
from sovereign.memory.vector_store import VectorStore
from sovereign.memory.working_memory import WorkingMemory
from sovereign.utils.logging import get_logger

logger = get_logger("memory")


class MemoryManager:
    def __init__(
        self,
        working: WorkingMemory | None = None,
        episodic: EpisodicMemory | None = None,
        semantic: SemanticMemory | None = None,
        procedural: ProceduralMemory | None = None,
        vector: VectorStore | None = None,
        retention: DataRetention | None = None,
    ):
        self.working = working or WorkingMemory()
        self.episodic = episodic or EpisodicMemory()
        self.semantic = semantic or SemanticMemory()
        self.procedural = procedural or ProceduralMemory()
        self.vector = vector or VectorStore(backend="memory")
        self.retention = retention or DataRetention()

    # -- store -------------------------------------------------------------
    async def store(self, memory_type: str, key: str, value: Any, metadata: dict[str, Any] | None = None) -> None:
        memory_type = memory_type.lower()
        if memory_type == "working":
            self.working.set(key, value)
        elif memory_type == "episodic":
            self.episodic.record(task_id=str(value.get("task_id", key)), details=value)
        elif memory_type == "semantic":
            self.semantic.add_fact(str(value.get("subject", key)), str(value.get("predicate", "")),
                                   str(value.get("object", "")), confidence=float(value.get("confidence", 0.5)))
        elif memory_type == "procedural":
            self.procedural.save(str(value.get("name", key)), str(value.get("description", "")),
                                 value.get("steps", []))
        elif memory_type in ("vector", "vectors"):
            if "vector" not in value:
                raise ValueError("vector memory requires {'vector': [...]}")
            self.vector.upsert(key, value["vector"], metadata)
        else:
            raise ValueError(f"unknown memory type: {memory_type}")

    async def store_task_result(self, task: Any) -> None:
        """Blueprint-compatible hook: persist completed task into episodic memory."""
        await self.store(
            "episodic",
            task.id,
            {"task_id": task.id, "summary": f"task {task.type} completed",
             "success": task.status == "completed"},
        )

    # -- retrieve ----------------------------------------------------------
    async def retrieve(self, memory_type: str, key: str) -> Any:
        memory_type = memory_type.lower()
        if memory_type == "working":
            return self.working.get(key)
        if memory_type == "episodic":
            rows = self.episodic.query(task_id=key, limit=1)
            return rows[0] if rows else None
        if memory_type == "semantic":
            return self.semantic.lookup(key)
        if memory_type == "procedural":
            return self.procedural.get(key)
        raise ValueError(f"unknown memory type: {memory_type}")

    # -- search ------------------------------------------------------------
    async def search(self, query: str, memory_types: list[str] | None = None, k: int = 10) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        types = memory_types or ["vector", "semantic"]
        if "vector" in types:
            hits = self.vector.query(self.vector.hash_placeholder(query, 64), k=k)
            results.extend({"memory_type": "vector", **h} for h in hits)
        if "semantic" in types:
            facts = self.semantic.lookup(query)
            results.extend({"memory_type": "semantic", "key": f["id"], "value": f} for f in facts[:k])
        return results

    # -- stats / prune -----------------------------------------------------
    async def get_stats(self) -> dict[str, Any]:
        return {
            "working": self.working.stats(),
            "episodic": {"type": "episodic", "items": self.episodic.count()},
            "semantic": {"type": "semantic", "items": self.semantic.count()},
            "procedural": {"type": "procedural", "items": len(self.procedural.list())},
            "vector": {"type": "vector", "items": self.vector.count(), "backend": getattr(self.vector, "_backend_name", "?")},
            "retention": self.retention.summary(),
        }

    async def prune(self) -> dict[str, int]:
        """Purge expired episodic records per retention policy."""
        policy = self.retention.policy("episodic")
        cutoff = time.time() - (policy.retention_days or 30) * 86400
        purged = await asyncio.to_thread(self.episodic.purge_before, cutoff)
        logger.info("pruned %s expired episodic records", purged)
        return {"episodic_purged": purged}
