"""SOVEREIGN — agent factory (spawns agents from config).

Maps ``agent_kind`` strings to concrete agent classes; raises on unknown
kinds so configuration mistakes surface loudly.
"""

from __future__ import annotations

from typing import Any

from sovereign.agents.base import BaseAgent
from sovereign.utils.errors import AgentError


class AgentFactory:
    def __init__(self, deps: dict[str, Any] | None = None):
        self.deps = deps or {}

    def create(self, kind: str, name: str = "", **kwargs: Any) -> BaseAgent:
        kind = kind.lower()
        if kind in ("deepseek.chat", "chat", "deepseek_chat"):
            from sovereign.agents.deepseek_chat import DeepSeekChatAgent

            return DeepSeekChatAgent(name=name or "deepseek-chat", **kwargs)
        if kind in ("deepseek.reasoner", "reasoner"):
            from sovereign.agents.deepseek_reasoner import DeepSeekReasonerAgent

            return DeepSeekReasonerAgent(name=name or "deepseek-reasoner", **kwargs)
        if kind in ("deepseek.coder", "coder"):
            from sovereign.agents.deepseek_coder import DeepSeekCoderAgent

            return DeepSeekCoderAgent(name=name or "deepseek-coder", **kwargs)
        if kind in ("tool", "tool_agent"):
            from sovereign.agents.tool_agent import ToolAgent

            return ToolAgent(name=name or "tool-agent",
                             executor=self.deps["executor"],
                             model_agent=self.deps.get("model_agent"),
                             allowed_tools=kwargs.pop("allowed_tools", None), **kwargs)
        if kind in ("coordinator", "coordinator_agent"):
            from sovereign.agents.coordinator_agent import CoordinatorAgent

            return CoordinatorAgent(name=name or "coordinator",
                                    submit_fn=self.deps.get("submit_fn"), **kwargs)
        if kind in ("memory", "memory_agent"):
            from sovereign.agents.memory_agent import MemoryAgent

            return MemoryAgent(name=name or "memory-agent",
                               memory=self.deps["memory"], **kwargs)
        if kind in ("supervisor", "supervisor_agent"):
            from sovereign.agents.supervisor_agent import SupervisorAgent

            return SupervisorAgent(name=name or "supervisor",
                                   registry=self.deps.get("agent_registry"), **kwargs)
        raise AgentError(f"unknown agent kind: {kind}")

    def create_all(self, definitions: list[dict[str, Any]]) -> list[BaseAgent]:
        agents: list[BaseAgent] = []
        for definition in definitions:
            agents.append(self.create(definition["kind"], **definition.get("config", {})))
        return agents
