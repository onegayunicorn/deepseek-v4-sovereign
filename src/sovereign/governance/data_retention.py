"""SOVEREIGN — data retention policies & purge.

Enforces per-memory-type retention (days) and capacity limits defined in
``config/memory.yaml``. ``purge_expired`` runs on the pruning interval.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

_RETENTION_DEFAULTS = {
    "working": {"ttl_seconds": 3600},
    "episodic": {"retention_days": 30, "max_items": 10_000},
    "semantic": {"retention_days": 365, "max_items": 100_000},
    "procedural": {"retention_days": None, "max_items": 1_000},
    "vector": {"retention_days": 365},
}


@dataclass
class RetentionPolicy:
    memory_type: str
    retention_days: int | None
    max_items: int | None
    ttl_seconds: int | None


class DataRetention:
    def __init__(self, config: dict[str, Any] | None = None):
        merged = {**_RETENTION_DEFAULTS, **(config or {})}
        self.policies: dict[str, RetentionPolicy] = {}
        for name, raw in merged.items():
            self.policies[name] = RetentionPolicy(
                memory_type=name,
                retention_days=raw.get("retention_days"),
                max_items=raw.get("max_items"),
                ttl_seconds=raw.get("ttl_seconds"),
            )

    def policy(self, memory_type: str) -> RetentionPolicy:
        return self.policies.get(memory_type, RetentionPolicy(memory_type, None, None, None))

    def is_expired(self, memory_type: str, timestamp: float) -> bool:
        policy = self.policy(memory_type)
        if policy.retention_days:
            return time.time() - timestamp > policy.retention_days * 86400
        if policy.ttl_seconds:
            return time.time() - timestamp > policy.ttl_seconds
        return False

    def over_capacity(self, memory_type: str, count: int) -> bool:
        policy = self.policy(memory_type)
        return policy.max_items is not None and count > policy.max_items

    def summary(self) -> dict[str, Any]:
        return {
            name: {
                "retention_days": p.retention_days,
                "max_items": p.max_items,
                "ttl_seconds": p.ttl_seconds,
            }
            for name, p in self.policies.items()
        }
