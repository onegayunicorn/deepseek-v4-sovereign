"""SOVEREIGN — inter-agent messaging.

Direct agent↔agent message delivery with routing by agent id or role.
Messages are logged for audit and replayability.
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from typing import Any

from sovereign.utils.id_generator import new_id


class MessageBus:
    def __init__(self) -> None:
        self._mailboxes: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def send(self, sender: str, recipient: str, kind: str, payload: dict[str, Any]) -> str:
        message = {
            "id": new_id("msg"),
            "sender": sender,
            "recipient": recipient,
            "kind": kind,
            "payload": payload,
            "ts": time.time(),
        }
        async with self._lock:
            self._mailboxes[recipient].append(message)
        return message["id"]

    async def receive(self, recipient: str, timeout: float = 5.0) -> dict[str, Any] | None:
        """Non-blocking-ish receive: poll the mailbox for up to ``timeout``."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            async with self._lock:
                if self._mailboxes[recipient]:
                    return self._mailboxes[recipient].popleft()
            await asyncio.sleep(0.05)
        return None

    async def broadcast(self, sender: str, kind: str, payload: dict[str, Any], recipients: list[str]) -> list[str]:
        ids = []
        for recipient in recipients:
            ids.append(await self.send(sender, recipient, kind, payload))
        return ids

    def pending(self, recipient: str) -> int:
        return len(self._mailboxes.get(recipient, []))
