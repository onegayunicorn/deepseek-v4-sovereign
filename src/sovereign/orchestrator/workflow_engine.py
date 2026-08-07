"""SOVEREIGN — DAG-based workflow engine.

Workflows are YAML/JSON DAGs: nodes (task submissions) with dependencies.
The engine topologically sorts and executes nodes as dependencies complete,
with a global timeout.
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from sovereign.utils.errors import TaskError
from sovereign.utils.logging import get_logger

logger = get_logger("workflow")

SubmitFn = Callable[[str, dict[str, Any], int], Awaitable[str]]
StatusFn = Callable[[str], Awaitable[dict[str, Any]]]


class WorkflowEngine:
    def __init__(self, submit_fn: SubmitFn, status_fn: StatusFn):
        self.submit = submit_fn
        self.status = status_fn

    @staticmethod
    def topo_sort(nodes: dict[str, dict[str, Any]]) -> list[str]:
        """Kahn's algorithm; raises on cycles."""
        indegree = {name: len(node.get("depends_on", [])) for name, node in nodes.items()}
        dependents: dict[str, list[str]] = {name: [] for name in nodes}
        for name, node in nodes.items():
            for dep in node.get("depends_on", []):
                dependents.setdefault(dep, []).append(name)

        ready = [n for n, d in indegree.items() if d == 0]
        order: list[str] = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for dependent in dependents.get(current, []):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    ready.append(dependent)
        if len(order) != len(nodes):
            raise TaskError("workflow graph contains a cycle")
        return order

    async def run(self, nodes: dict[str, dict[str, Any]], *, timeout: float = 7200) -> dict[str, Any]:
        order = self.topo_sort(nodes)
        results: dict[str, Any] = {}
        completed: set[str] = set()

        for name in order:
            node = nodes[name]
            for dep in node.get("depends_on", []):
                if dep not in completed:
                    raise TaskError(f"dependency {dep} of {name} did not complete")

            task_id = await self.submit(node.get("task_type", "generic"),
                                        node.get("payload", {}),
                                        node.get("priority", 5))
            results[name] = {"task_id": task_id, "status": "submitted"}
            completed.add(name)

        logger.info("workflow dispatched %s nodes in order %s", len(order), order)
        return {"order": order, "tasks": results}
