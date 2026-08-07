"""SOVEREIGN — working (short-term) memory.

TTL-bounded in-memory store for the current context window. Values older
than ``ttl_seconds`` are dropped on access; capacity is LRU-bounded.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any

from sovereign.utils.caching import TTLCache


class WorkingMemory:
    def __init__(self, ttl_seconds: int = 3600, max_items: int = 1000):
        self._cache: TTLCache[str, Any] = TTLCache(max_items, ttl_seconds)
        self._lock = threading.Lock()

    def set(self, key: str, value: Any) -> None:
        self._cache.set(key, value)

    def get(self, key: str, default: Any = None) -> Any:
        return self._cache.get(key, default)

    def delete(self, key: str) -> None:
        self._cache.delete(key)

    def keys(self) -> list[str]:
        return list(self._cache._data.keys())  # noqa: SLF001 — introspection for stats

    def clear(self) -> None:
        self._cache.clear()

    def stats(self) -> dict[str, Any]:
        return {"type": "working", "items": len(self), "ttl_seconds": self._cache.ttl}

    def __len__(self) -> int:
        return len(self._cache)
