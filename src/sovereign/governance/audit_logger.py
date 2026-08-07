"""SOVEREIGN — tamper-evident audit logger.

Appends JSON lines to ``logs/audits/audit.jsonl``; every record carries a
``prev_hash`` (SHA-256 of the previous record) so the chain is
tamper-evident. In-memory mode is used when no path is configured.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sovereign.utils.id_generator import new_id


class AuditLogger:
    def __init__(self, path: str | Path | None = "logs/audits/audit.jsonl", tamper_evident: bool = True):
        self.path = Path(path) if path else None
        self.tamper_evident = tamper_evident
        self._lock = threading.Lock()
        self._prev_hash = "0" * 64
        self._records: list[dict[str, Any]] = []
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            if self.path.exists():
                try:
                    line = self.path.read_text(encoding="utf-8").strip().splitlines()[-1]
                    self._prev_hash = json.loads(line).get("hash", self._prev_hash)
                except Exception:  # noqa: BLE001
                    pass

    def log(self, event_type: str, actor: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        with self._lock:
            record: dict[str, Any] = {
                "id": new_id("aud"),
                "ts": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "actor": actor,
                "details": details or {},
            }
            if self.tamper_evident:
                record["prev_hash"] = self._prev_hash
                record["hash"] = hashlib.sha256(
                    json.dumps(record, sort_keys=True, default=str).encode()
                ).hexdigest()
                self._prev_hash = record["hash"]
            self._records.append(record)
            if self.path:
                with open(self.path, "a", encoding="utf-8") as fh:
                    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            return record

    async def log_event(self, event_type: str, actor: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
        """Async wrapper (kept for blueprint API compatibility)."""
        return await asyncio.to_thread(self.log, event_type, actor, details)

    def tail(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._records[-limit:])

    def export(self, fmt: str = "jsonl") -> str:
        if fmt == "jsonl":
            return "\n".join(json.dumps(r, ensure_ascii=False) for r in self._records)
        import csv
        import io

        buffer = io.StringIO()
        if self._records:
            writer = csv.DictWriter(buffer, fieldnames=sorted(self._records[0]))
            writer.writeheader()
            writer.writerows(self._records)
        return buffer.getvalue()
