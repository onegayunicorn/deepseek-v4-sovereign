"""SOVEREIGN — episodic memory (past task episodes).

SQLite-backed; each episode records task context, agent, summary, success,
and a reference into artifacts. Compatible with the blueprint schema
(``episodes`` table).
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from sovereign.utils.id_generator import new_id

_SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    agent_id TEXT,
    summary TEXT,
    details TEXT,
    success BOOLEAN,
    created_at REAL
);
CREATE INDEX IF NOT EXISTS idx_episodes_created ON episodes(created_at);
"""


class EpisodicMemory:
    def __init__(self, db_path: str | Path = "data/memory/episodic/episodes.db"):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.executescript(_SCHEMA)

    def record(self, *, task_id: str, agent_id: str = "", summary: str = "",
               details: dict[str, Any] | None = None, success: bool = True) -> str:
        episode_id = new_id("ep")
        with self._lock:
            self._conn.execute(
                "INSERT INTO episodes (id, task_id, agent_id, summary, details, success, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (episode_id, task_id, agent_id, summary,
                 json.dumps(details or {}, ensure_ascii=False), int(success), time.time()),
            )
            self._conn.commit()
        return episode_id

    def query(self, *, task_id: str | None = None, agent_id: str | None = None,
              limit: int = 20) -> list[dict[str, Any]]:
        sql = "SELECT * FROM episodes WHERE 1=1"
        params: list[Any] = []
        if task_id:
            sql += " AND task_id = ?"
            params.append(task_id)
        if agent_id:
            sql += " AND agent_id = ?"
            params.append(agent_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        cols = [d[0] for d in self._conn.execute("SELECT * FROM episodes LIMIT 0").description]
        return [dict(zip(cols, row)) for row in rows]

    def count(self) -> int:
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]

    def purge_before(self, timestamp: float) -> int:
        with self._lock:
            cur = self._conn.execute("DELETE FROM episodes WHERE created_at < ?", (timestamp,))
            self._conn.commit()
            return cur.rowcount
