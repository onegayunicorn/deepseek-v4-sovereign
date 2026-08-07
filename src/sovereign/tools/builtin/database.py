"""SOVEREIGN — database tool (SQLite query execution).

Only SELECT / EXPLAIN / PRAGMA statements are allowed by default; DDL/DML
requires ``read_only=False`` in tools.yaml (still limited to the configured
databases).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from sovereign.utils.errors import ToolError

_ALLOWED_DBS = ["data/state/orchestration_state.sqlite"]
_READ_ONLY = True


def query(sql: str, *, db: str = "data/state/orchestration_state.sqlite",
          params: tuple | None = None, limit: int = 100) -> dict[str, Any]:
    """Execute a read-only SQL query against an allowed database."""
    if db not in _ALLOWED_DBS:
        raise ToolError(f"database not in allow-list: {db}")

    statement = sql.strip().split()[0].upper() if sql.strip() else ""
    if statement not in ("SELECT", "EXPLAIN", "PRAGMA", "WITH"):
        if _READ_ONLY:
            raise ToolError(f"read-only mode: '{statement}' statements are blocked")
        raise ToolError(f"unsupported statement: {statement}")

    path = Path(db)
    if not path.exists():
        return {"rows": [], "columns": [], "error": f"database not initialized: {db}"}

    conn = sqlite3.connect(str(path))
    try:
        cur = conn.execute(sql, params or ())
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(limit + 1)
        truncated = len(rows) > limit
        return {"rows": rows[:limit], "columns": columns, "truncated": truncated, "count": len(rows[:limit])}
    except sqlite3.Error as exc:
        raise ToolError(f"query failed: {exc}")
    finally:
        conn.close()
