"""SOVEREIGN — tool agent (agent that can invoke tools).

Wraps an underlying model agent and gives it safe access to the tool
registry through the :class:`ToolExecutor` (policy + audit + metrics).
"""

from __future__ import annotations

from typing import Any

from sovereign.agents.base import BaseAgent
from sovereign.tools.executor import ToolExecutor
from sovereign.utils.logging import get_logger

logger = get_logger("agents.tool")


class ToolAgent(BaseAgent):
    kind = "tool"

    def __init__(self, executor: ToolExecutor, model_agent: BaseAgent | None = None,
                 allowed_tools: list[str] | None = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.executor = executor
        self.model_agent = model_agent
        self.allowed_tools = allowed_tools

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None,
                        *, role: str = "operator") -> dict[str, Any]:
        if self.allowed_tools is not None and name not in self.allowed_tools:
            return {"ok": False, "error": f"tool '{name}' not allowed for this agent"}
        return await self.executor.execute(name, arguments, role=role)

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        if "tool" in input_:
            return await self.call_tool(input_["tool"], input_.get("arguments"))
        if self.model_agent is not None:
            return await self.model_agent.run(input_)
        return {"ok": False, "error": "tool agent requires 'tool' or a model_agent"}

    def capabilities(self) -> list[str]:
        tools = self.allowed_tools or (self.executor.registry.names() if self.executor else [])
        return [self.kind, *[f"tool:{t}" for t in tools]]
