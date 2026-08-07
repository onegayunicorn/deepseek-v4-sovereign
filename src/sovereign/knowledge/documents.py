"""SOVEREIGN — document ingestion / parsing (plain text, JSON, CSV, Markdown)."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sovereign.utils.id_generator import new_id


@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source: str = ""


class DocumentStore:
    """In-memory + JSONL-persisted document store."""

    def __init__(self, path: str | Path | None = "data/knowledge/documents/metadata.db.jsonl"):
        self.path = Path(path) if path else None
        self._docs: dict[str, Document] = {}
        if self.path and self.path.exists():
            self._load()

    def _load(self) -> None:
        for line in self.path.read_text(encoding="utf-8").strip().splitlines():
            if not line:
                continue
            try:
                data = json.loads(line)
                self._docs[data["doc_id"]] = Document(**data)
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    def save(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None,
             title: str = "", source: str = "") -> str:
        doc = Document(doc_id=doc_id, title=title or doc_id, text=text,
                       metadata=metadata or {}, source=source)
        self._docs[doc_id] = doc
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(vars(doc), ensure_ascii=False) + "\n")
        return doc_id

    def get(self, doc_id: str) -> Document | None:
        return self._docs.get(doc_id)

    def count(self) -> int:
        return len(self._docs)

    def ingest_text_file(self, path: str | Path) -> str:
        path = Path(path)
        return self.save(new_id("doc"), path.read_text(encoding="utf-8"),
                         source=str(path), title=path.name)

    def ingest_csv(self, path: str | Path) -> int:
        count = 0
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                self.save(new_id("csv"), json.dumps(row, ensure_ascii=False),
                          source=str(path))
                count += 1
        return count
