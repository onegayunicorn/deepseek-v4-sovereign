"""SOVEREIGN — dedicated memory agent.

Handles memory store / retrieve / search / prune operations on behalf of
other agents — the single entry point into the memory subsystem.
"""

from __future__ import annotations

from typing import Any

from sovereign.agents.base import BaseAgent
from sovereign.memory.memory_manager import MemoryManager


class MemoryAgent(BaseAgent):
    kind = "memory"

    def __init__(self, memory: MemoryManager, **kwargs: Any):
        super().__init__(**kwargs)
        self.memory = memory

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        op = input_.get("op", "search")
        if op == "store":
            await self.memory.store(input_["memory_type"], input_["key"], input_["value"])
            return {"ok": True, "op": "store", "key": input_.get("key")}
        if op == "retrieve":
            value = await self.memory.retrieve(input_["memory_type"], input_["key"])
            return {"ok": True, "op": "retrieve", "value": value}
        if op == "search":
            results = await self.memory.search(input_.get("query", ""), k=input_.get("k", 10))
            return {"ok": True, "op": "search", "results": results}
        if op == "stats":
            return {"ok": True, "op": "stats", "stats": await self.memory.get_stats()}
        if op == "prune":
            return {"ok": True, "op": "prune", **await self.memory.prune()}
        return {"ok": False, "error": f"unknown memory op: {op}"}

    def capabilities(self) -> list[str]:
        return [self.kind, "memory:store", "memory:retrieve", "memory:search", "memory:prune"]
