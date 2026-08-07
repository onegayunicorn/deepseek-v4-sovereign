"""SOVEREIGN — supervisor agent (monitors other agents).

Polls agent status, restarts failed agents, and publishes health events.
"""

from __future__ import annotations

from typing import Any

from sovereign.agents.base import BaseAgent
from sovereign.utils.logging import get_logger

logger = get_logger("agents.supervisor")


class SupervisorAgent(BaseAgent):
    kind = "supervisor"

    def __init__(self, registry: dict[str, BaseAgent] | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.registry = registry or {}

    def register_agent(self, agent: BaseAgent) -> None:
        self.registry[agent.agent_id] = agent

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        op = input_.get("op", "status")
        if op == "status":
            return {
                "ok": True,
                "op": "status",
                "agents": [a.status() for a in self.registry.values()],
            }
        if op == "restart":
            agent_id = input_.get("agent_id")
            agent = self.registry.get(agent_id)
            if agent is None:
                return {"ok": False, "error": f"unknown agent: {agent_id}"}
            await agent.stop()
            await agent.start()
            return {"ok": True, "op": "restart", "agent_id": agent_id}
        if op == "health":
            failed = [a.agent_id for a in self.registry.values() if a.state == "failed"]
            return {"ok": True, "op": "health", "healthy": not failed, "failed": failed}
        return {"ok": False, "error": f"unknown supervisor op: {op}"}

    def capabilities(self) -> list[str]:
        return [self.kind, "supervisor:status", "supervisor:restart", "supervisor:health"]
