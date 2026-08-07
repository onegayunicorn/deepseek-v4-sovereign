"""SOVEREIGN — coordinator agent (decomposes high-level tasks).

Splits a goal into subtasks and dispatches each to the appropriate agent
via the orchestrator's task submission path.
"""

from __future__ import annotations

from typing import Any

from sovereign.agents.base import BaseAgent

_SUBTASK_PLAN = {
    "reason": {"agent_kind": "deepseek.reasoner", "priority": 5},
    "code": {"agent_kind": "deepseek.coder", "priority": 6},
    "search": {"agent_kind": "tool", "priority": 4},
    "plan": {"agent_kind": "deepseek.chat", "priority": 5},
    "execute": {"agent_kind": "tool", "priority": 7},
    "coordinate": {"agent_kind": "deepseek.chat", "priority": 5},
}


class CoordinatorAgent(BaseAgent):
    kind = "coordinator"

    def __init__(self, submit_fn: Any = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.submit_fn = submit_fn  # async (task_type, payload, priority) -> task_id

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        goal = str(input_.get("input", ""))
        plan = input_.get("plan") or self._default_plan(goal)

        dispatched: list[dict[str, Any]] = []
        for step in plan:
            task_type = step.get("type", "reason")
            spec = _SUBTASK_PLAN.get(task_type, _SUBTASK_PLAN["reason"])
            payload = {"input": step.get("prompt", goal), "expected": step.get("expected", "")}
            if self.submit_fn is not None:
                task_id = await self.submit_fn(task_type, payload, priority=spec["priority"])
            else:
                task_id = f"dry-run:{task_type}:{len(dispatched)}"
            dispatched.append({"task_type": task_type, "task_id": task_id, "status": "dispatched"})

        return {"ok": True, "goal": goal, "plan": plan, "dispatched": dispatched}

    def _default_plan(self, goal: str) -> list[dict[str, Any]]:
        return [
            {"type": "reason", "prompt": f"Analyze the goal: {goal}", "expected": "breakdown"},
            {"type": "plan", "prompt": f"Produce an execution plan for: {goal}", "expected": "plan"},
            {"type": "execute", "prompt": f"Execute the plan for: {goal}", "expected": "result"},
            {"type": "coordinate", "prompt": f"Verify and summarize: {goal}", "expected": "summary"},
        ]
