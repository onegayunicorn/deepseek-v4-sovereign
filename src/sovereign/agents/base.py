"""SOVEREIGN — BaseAgent interface.

Every agent (deepseek chat/reasoner/coder, tool, coordinator, memory,
supervisor) adheres to this lifecycle: status transitions, event emission,
result capture, and graceful shutdown.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sovereign.communication.pubsub import EventBus
from sovereign.utils.id_generator import new_id
from sovereign.utils.logging import get_logger

logger = get_logger("agents")

_STATES = ("idle", "running", "paused", "completed", "failed", "shutdown")


class BaseAgent:
    """Abstract agent with shared lifecycle machinery."""

    kind = "base"

    def __init__(self, agent_id: str | None = None, name: str = "agent",
                 event_bus: EventBus | None = None, config: dict[str, Any] | None = None):
        self.agent_id = agent_id or new_id("agt")
        self.name = name
        self.event_bus = event_bus
        self.config = config or {}
        self.state = "idle"
        self.last_active: datetime | None = None
        self.metrics: dict[str, Any] = {"tasks": 0, "errors": 0}

    # -- lifecycle ---------------------------------------------------------
    async def _transition(self, state: str) -> None:
        if state not in _STATES:
            raise ValueError(f"invalid agent state: {state}")
        self.state = state
        self.last_active = datetime.now(timezone.utc)
        if self.event_bus is not None:
            await self.event_bus.publish(
                "agent.state_changed",
                {"agent_id": self.agent_id, "state": state, "name": self.name},
            )

    async def start(self) -> None:
        await self._transition("idle")

    async def stop(self) -> None:
        await self._transition("shutdown")

    # -- execution ---------------------------------------------------------
    async def execute(self, task: Any) -> dict[str, Any]:
        """Blueprint-compatible: run a task object through :meth:`run`."""
        payload = getattr(task, "payload", {}) or {}
        return await self.run(payload)

    async def run(self, input_: dict[str, Any]) -> dict[str, Any]:
        """Run the agent on an input dict; subclasses implement _act."""
        await self._transition("running")
        self.metrics["tasks"] += 1
        try:
            result = await self._act(input_)
            await self._transition("completed")
            return result
        except Exception as exc:  # noqa: BLE001
            self.metrics["errors"] += 1
            await self._transition("failed")
            logger.exception("agent %s failed", self.agent_id)
            return {"ok": False, "error": str(exc), "agent": self.agent_id}

    async def _act(self, input_: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    # -- introspection -----------------------------------------------------
    def status(self) -> dict[str, Any]:
        return {
            "id": self.agent_id,
            "name": self.name,
            "kind": self.kind,
            "state": self.state,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "capabilities": self.capabilities(),
            "metrics": self.metrics,
        }

    def capabilities(self) -> list[str]:
        return [self.kind]
