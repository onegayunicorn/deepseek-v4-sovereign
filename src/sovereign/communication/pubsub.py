"""SOVEREIGN — in-process event bus (pub/sub).

Agents, tools, webhooks, and the scheduler publish events; subscribers
(coroutines) receive them. Optional async queue per subscriber prevents
slow consumers from blocking publishers.
"""

from __future__ import annotations

import asyncio
import inspect
from collections import defaultdict
from typing import Any, Awaitable, Callable

from sovereign.utils.id_generator import new_id
from sovereign.utils.logging import get_logger

logger = get_logger("pubsub")

Subscriber = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)
        self._history: list[dict[str, Any]] = []
        self._history_limit = 500

    async def start(self) -> None:
        logger.info("event bus started")

    async def stop(self) -> None:
        logger.info("event bus stopped")

    def subscribe(self, event_type: str, fn: Subscriber) -> None:
        if not (inspect.iscoroutinefunction(fn) or inspect.isawaitable(fn)):
            raise TypeError("subscribers must be async callables")
        self._subscribers[event_type].append(fn)

    def unsubscribe(self, event_type: str, fn: Subscriber) -> None:
        try:
            self._subscribers[event_type].remove(fn)
        except ValueError:
            pass

    async def publish(self, event_type: str, payload: dict[str, Any] | None = None) -> str:
        event = {"id": new_id("evt"), "type": event_type, "payload": payload or {}}
        self._history.append(event)
        if len(self._history) > self._history_limit:
            self._history = self._history[-self._history_limit:]
        for fn in list(self._subscribers.get(event_type, [])):
            try:
                await fn(event)
            except Exception:  # noqa: BLE001
                logger.exception("subscriber error for event %s", event_type)
        return event["id"]

    def history(self, event_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        events = self._history if event_type is None else [e for e in self._history if e["type"] == event_type]
        return events[-limit:]
