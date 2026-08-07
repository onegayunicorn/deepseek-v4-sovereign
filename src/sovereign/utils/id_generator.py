"""SOVEREIGN — unique ID generation (task / agent / job / audit IDs)."""

from __future__ import annotations

import secrets
import time
import uuid

_EPOCH = 1_700_000_000  # 2023-11-14


def new_id(prefix: str = "sov") -> str:
    """Time-ordered, collision-resistant ID: ``{prefix}_{ts36}_{rand}``.

    Sortable by creation time within the same prefix — useful for task
    queues and audit logs.
    """
    ts = int(time.time() * 1000) - _EPOCH * 1000
    return f"{prefix}_{ts:012x}{secrets.token_hex(4)}"


def short_id(length: int = 8) -> str:
    """Cryptographically random short ID (for keys, sessions)."""
    return secrets.token_hex(length // 2 + 1)[:length]


def uuid4() -> str:
    """Standard UUID4 string."""
    return str(uuid.uuid4())
