"""SOVEREIGN — webhook receivers & dispatch.

Inbound webhooks (github / huggingface / generic) are validated, mapped to
events, and dispatched to registered handlers — typically submitting tasks
(e.g. GitHub push → scout/enhance task). Signature verification is a
pluggable hook (HMAC secret per source).
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any, Awaitable, Callable

from sovereign.utils.id_generator import new_id
from sovereign.utils.logging import get_logger

logger = get_logger("webhooks")

Handler = Callable[[dict[str, Any]], Awaitable[str | None]]


class WebhookManager:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = {}
        self._secrets: dict[str, str] = {}
        self._received: list[dict[str, Any]] = []

    def register(self, source: str, handler: Handler) -> None:
        self._handlers.setdefault(source, []).append(handler)

    def set_secret(self, source: str, secret: str) -> None:
        self._secrets[source] = secret

    def verify_signature(self, source: str, body: bytes, signature: str) -> bool:
        secret = self._secrets.get(source)
        if not secret:
            return True  # no secret configured → accept (dev mode)
        expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    async def receive(self, source: str, event: str, payload: dict[str, Any]) -> dict[str, Any]:
        record = {
            "id": new_id("wh"),
            "source": source,
            "event": event,
            "payload": payload,
            "handlers_fired": 0,
        }
        self._received.append(record)
        for handler in self._handlers.get(source, []):
            try:
                task_id = await handler({"source": source, "event": event, "payload": payload})
                if task_id:
                    record["task_id"] = task_id
                    record["handlers_fired"] += 1
            except Exception:  # noqa: BLE001
                logger.exception("webhook handler failed (source=%s)", source)
        return record

    def list(self) -> list[dict[str, Any]]:
        return [
            {"source": source, "handlers": len(handlers)}
            for source, handlers in self._handlers.items()
        ]

    def received(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._received[-limit:]
