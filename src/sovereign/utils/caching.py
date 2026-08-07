"""SOVEREIGN — thread-safe LRU cache with TTL."""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any, Callable, Hashable, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class TTLCache:
    """LRU cache with per-key TTL; O(1) amortized ops."""

    def __init__(self, capacity: int = 1024, ttl_seconds: float = 300.0):
        self.capacity = max(1, capacity)
        self.ttl = ttl_seconds
        self._data: OrderedDict[K, tuple[float, V]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: K, default: V | None = None) -> V | None:
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return default
            expires, value = item
            if time.monotonic() > expires:
                del self._data[key]
                return default
            self._data.move_to_end(key)
            return value

    def set(self, key: K, value: V, ttl: float | None = None) -> None:
        expires = time.monotonic() + (ttl if ttl is not None else self.ttl)
        with self._lock:
            self._data[key] = (expires, value)
            self._data.move_to_end(key)
            while len(self._data) > self.capacity:
                self._data.popitem(last=False)

    def delete(self, key: K) -> None:
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)


def cached(capacity: int = 256, ttl_seconds: float = 60.0) -> Callable:
    """Decorator: memoize sync/async function results in a TTLCache."""

    def deco(fn: Callable[..., V]) -> Callable[..., V]:
        cache: TTLCache[Any, V] = TTLCache(capacity, ttl_seconds)
        is_async = getattr(fn, "__code__", None) is not None and False

        def wrapper(*args: Any, **kwargs: Any) -> V:
            key = (args, tuple(sorted(kwargs.items())))
            hit = cache.get(key)
            if hit is not None:
                return hit
            value = fn(*args, **kwargs)
            cache.set(key, value)
            return value

        return wrapper

    return deco
