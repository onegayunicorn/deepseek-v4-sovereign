"""SOVEREIGN — semantic memory (facts / concepts / long-term KB).

SQLite-backed triple store (subject, predicate, object) with confidence and
source attribution — the durable long-term knowledge layer.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from sovereign.utils.id_generator import new_id

_SCHEMA = """
CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    subject TEXT,
    predicate TEXT,
    object TEXT,
    confidence REAL DEFAULT 0.5,
    source TEXT,
    created_at REAL,
    updated_at REAL
);
CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);
"""


class SemanticMemory:
    def __init__(self, db_path: str | Path = "data/memory/semantic/facts.db"):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.executescript(_SCHEMA)

    def add_fact(self, subject: str, predicate: str, object_: str, *,
                 confidence: float = 0.5, source: str = "") -> str:
        fact_id = new_id("fact")
        now = time.time()
        with self._lock:
            self._conn.execute(
                "INSERT INTO facts (id, subject, predicate, object, confidence, source, created_at, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (fact_id, subject, predicate, object_, confidence, source, now, now),
            )
            self._conn.commit()
        return fact_id

    def lookup(self, subject: str, predicate: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM facts WHERE subject = ?"
        params: list[Any] = [subject]
        if predicate:
            sql += " AND predicate = ?"
            params.append(predicate)
        sql += " ORDER BY confidence DESC"
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        cols = [d[0] for d in self._conn.execute("SELECT * FROM facts LIMIT 0").description]
        return [dict(zip(cols, row)) for row in rows]

    def delete_fact(self, fact_id: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
            self._conn.commit()

    def count(self) -> int:
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
