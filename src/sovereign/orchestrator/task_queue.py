"""SOVEREIGN — persistent task queue.

Priority-ordered asyncio queue with optional SQLite durability. Tasks are
dataclasses: id, type, payload, priority, status, retries, timestamps.
"""

from __future__ import annotations

import asyncio
import heapq
import json
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sovereign.utils.id_generator import new_id

_SCHEMA = """
CREATE TABLE IF NOT EXISTS queue_tasks (
    id TEXT PRIMARY KEY,
    type TEXT,
    payload TEXT,
    priority INTEGER,
    status TEXT,
    retry_count INTEGER,
    max_retries INTEGER,
    created_at REAL,
    updated_at REAL
);
"""


@dataclass
class QueueTask:
    id: str
    type: str
    payload: dict[str, Any]
    priority: int = 5
    status: str = "pending"
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: str | None = None
    result: Any = None


class TaskQueue:
    """Heap-based priority queue with optional SQLite persistence."""

    def __init__(self, backend: str = "memory", db_path: str = "data/state/orchestration_state.sqlite"):
        self.backend = backend
        self._heap: list[tuple[int, int, QueueTask]] = []
        self._counter = 0
        self._lock = asyncio.Lock()
        self._conn: sqlite3.Connection | None = None
        if backend == "sqlite":
            import sqlite3 as _s

            import pathlib

            pathlib.Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = _s.connect(db_path, check_same_thread=False)
            self._conn.executescript(_SCHEMA)
            self._restore()

    def _restore(self) -> None:
        assert self._conn is not None
        for row in self._conn.execute(
            "SELECT id, type, payload, priority, status, retry_count, max_retries, created_at "
            "FROM queue_tasks WHERE status IN ('pending','running')"
        ).fetchall():
            task = QueueTask(
                id=row[0], type=row[1], payload=json.loads(row[2] or "{}"),
                priority=row[3], status=row[4], retry_count=row[5], max_retries=row[6],
            )
            self._push(task)

    def _push(self, task: QueueTask) -> None:
        self._counter += 1
        heapq.heappush(self._heap, (-task.priority, self._counter, task))

    async def put(self, task: QueueTask) -> None:
        async with self._lock:
            self._push(task)
            if self._conn is not None:
                self._conn.execute(
                    "INSERT OR REPLACE INTO queue_tasks VALUES (?,?,?,?,?,?,?,?,?)",
                    (task.id, task.type, json.dumps(task.payload), task.priority,
                     task.status, task.retry_count, task.max_retries,
                     task.created_at.timestamp(), task.updated_at.timestamp()),
                )
                self._conn.commit()

    async def get(self) -> QueueTask:
        while True:
            async with self._lock:
                if self._heap:
                    _, _, task = heapq.heappop(self._heap)
                    if self._conn is not None:
                        self._conn.execute(
                            "UPDATE queue_tasks SET status='running', updated_at=? WHERE id=?",
                            (datetime.now(timezone.utc).timestamp(), task.id),
                        )
                        self._conn.commit()
                    return task
            await asyncio.sleep(0.05)

    async def put_back(self, task: QueueTask) -> None:
        """Requeue a task (e.g. after transient failure)."""
        await self.put(task)

    def size(self) -> int:
        return len(self._heap)

    async def drain(self) -> int:
        async with self._lock:
            count = len(self._heap)
            self._heap.clear()
            return count
