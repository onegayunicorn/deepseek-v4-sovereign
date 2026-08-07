"""SOVEREIGN — realtime event stream over WebSocket.

Bridges the in-process EventBus to connected WebSocket clients at
``/ws/events``. Replays recent history on connect.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from sovereign.communication.pubsub import EventBus


class EventStreamManager:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)
        # Replay recent history so late joiners catch up.
        for event in self.event_bus.history(limit=25):
            await websocket.send_json(event)
        try:
            while True:
                await websocket.receive_text()  # keepalive / ignore input
        except WebSocketDisconnect:
            self._clients.discard(websocket)

    async def broadcast(self, event: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for client in list(self._clients):
            try:
                await client.send_json(event)
            except Exception:  # noqa: BLE001
                stale.append(client)
        for client in stale:
            self._clients.discard(client)

    async def run(self) -> None:
        """Forward every bus event to connected clients."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

        async def _subscribe(event: dict[str, Any]) -> None:
            await queue.put(event)

        self.event_bus.subscribe("*", _subscribe)
        try:
            while True:
                event = await queue.get()
                await self.broadcast(event)
        finally:
            self.event_bus.unsubscribe("*", _subscribe)
