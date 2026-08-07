"""SOVEREIGN — procedural memory (learned procedures / recipes).

Stores named procedures (how-to recipes) discovered or authored by agents —
e.g. "deploy a Space", "run the lineage ETL". SQLite-backed.
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
CREATE TABLE IF NOT EXISTS procedures (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT,
    steps TEXT,
    tags TEXT,
    created_at REAL,
    updated_at REAL
);
"""


class ProceduralMemory:
    def __init__(self, db_path: str | Path = "data/memory/procedural.db"):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self._conn.executescript(_SCHEMA)

    def save(self, name: str, description: str, steps: list[dict[str, Any]], tags: list[str] | None = None) -> str:
        now = time.time()
        with self._lock:
            existing = self._conn.execute(
                "SELECT id FROM procedures WHERE name = ?", (name,)
            ).fetchone()
            proc_id = existing[0] if existing else new_id("proc")
            if existing:
                self._conn.execute(
                    "UPDATE procedures SET description=?, steps=?, tags=?, updated_at=? WHERE id=?",
                    (description, json.dumps(steps), json.dumps(tags or []), now, proc_id),
                )
            else:
                self._conn.execute(
                    "INSERT INTO procedures (id, name, description, steps, tags, created_at, updated_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (proc_id, name, description, json.dumps(steps), json.dumps(tags or []), now, now),
                )
            self._conn.commit()
        return proc_id

    def get(self, name: str) -> dict[str, Any] | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM procedures WHERE name = ?", (name,)
            ).fetchone()
        if not row:
            return None
        cols = [d[0] for d in self._conn.execute("SELECT * FROM procedures LIMIT 0").description]
        record = dict(zip(cols, row))
        record["steps"] = json.loads(record["steps"])
        record["tags"] = json.loads(record["tags"])
        return record

    def list(self) -> list[str]:
        with self._lock:
            rows = self._conn.execute("SELECT name FROM procedures ORDER BY name").fetchall()
        return [r[0] for r in rows]
