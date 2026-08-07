"""SOVEREIGN — task scheduler (cron / interval / event triggers).

Runs registered triggers and submits their tasks to the orchestrator.
Supports cron expressions via the ``croniter`` library when installed,
with a simple interval fallback otherwise.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

try:
    from croniter import croniter  # type: ignore

    _HAS_CRONITER = True
except ImportError:  # pragma: no cover
    croniter = None  # type: ignore[assignment]
    _HAS_CRONITER = False

logger = logging.getLogger("sovereign.orchestrator.scheduler")

TriggerFn = Callable[[], Awaitable[None]]


@dataclass
class Trigger:
    name: str
    kind: str  # cron | interval | once
    expression: str = ""
    interval_seconds: float = 60.0
    task_type: str = "generic"
    payload: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    last_fired: float = 0.0
    fn: TriggerFn | None = None


class Scheduler:
    def __init__(self, submit_fn: Callable[[str, dict[str, Any], int], Awaitable[str]] | None = None):
        self.triggers: dict[str, Trigger] = {}
        self._submit_fn = submit_fn

    def add(self, trigger: Trigger) -> None:
        self.triggers[trigger.name] = trigger

    def add_cron(self, name: str, expression: str, task_type: str, payload: dict[str, Any] | None = None) -> Trigger:
        trigger = Trigger(name=name, kind="cron", expression=expression,
                          task_type=task_type, payload=payload or {})
        self.add(trigger)
        return trigger

    def add_interval(self, name: str, seconds: float, task_type: str, payload: dict[str, Any] | None = None) -> Trigger:
        trigger = Trigger(name=name, kind="interval", interval_seconds=seconds,
                          task_type=task_type, payload=payload or {})
        self.add(trigger)
        return trigger

    def _due(self, trigger: Trigger, now: float) -> bool:
        if not trigger.enabled:
            return False
        if trigger.kind == "interval":
            return now - trigger.last_fired >= trigger.interval_seconds
        if trigger.kind == "cron" and _HAS_CRONITER and croniter is not None:
            itr = croniter(trigger.expression, trigger.last_fired or now - 1)
            return itr.get_next(float) <= now
        return False

    async def tick(self, now: float | None = None) -> list[str]:
        import time

        now = now or time.time()
        fired: list[str] = []
        for trigger in self.triggers.values():
            if not self._due(trigger, now):
                continue
            trigger.last_fired = now
            fired.append(trigger.name)
            try:
                if trigger.fn is not None:
                    await trigger.fn()
                elif self._submit_fn is not None:
                    await self._submit_fn(trigger.task_type, trigger.payload, 5)
            except Exception:  # noqa: BLE001
                logger.exception("trigger %s failed", trigger.name)
        return fired

    async def run_forever(self, interval: float = 1.0) -> None:
        while True:
            await self.tick()
            await asyncio.sleep(interval)
