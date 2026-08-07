"""SOVEREIGN — task/agent lifecycle state machine.

Valid transitions enforced centrally; illegal transitions raise ValueError.
States: pending → running → completed | failed → (retry → pending) | cancelled.
"""

from __future__ import annotations

from typing import Any

_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"running", "cancelled", "failed"},
    "running": {"completed", "failed", "cancelled"},
    "failed": {"pending", "cancelled"},  # retry → pending
    "completed": set(),
    "cancelled": set(),
}


class TaskStateMachine:
    def __init__(self) -> None:
        self._states: dict[str, str] = {}

    def current(self, task_id: str) -> str:
        return self._states.get(task_id, "pending")

    def transition(self, task_id: str, to: str) -> str:
        current = self.current(task_id)
        if to not in _TRANSITIONS.get(current, set()):
            raise ValueError(f"illegal task transition: {current} -> {to}")
        self._states[task_id] = to
        return to

    def force(self, task_id: str, state: str) -> None:
        self._states[task_id] = state

    def register(self, task_id: str) -> None:
        self._states[task_id] = "pending"

    def snapshot(self) -> dict[str, str]:
        return dict(self._states)


_AGENT_STATES = {"idle", "running", "paused", "completed", "failed", "shutdown"}


class AgentStateMachine:
    def __init__(self) -> None:
        self._states: dict[str, str] = {}

    def transition(self, agent_id: str, to: str) -> str:
        if to not in _AGENT_STATES:
            raise ValueError(f"invalid agent state: {to}")
        self._states[agent_id] = to
        return to

    def current(self, agent_id: str) -> str:
        return self._states.get(agent_id, "idle")
