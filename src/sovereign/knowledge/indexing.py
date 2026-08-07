"""SOVEREIGN — index building & updating.

Scans configured directories (documents/, docs/, integrations/) and indexes
new/changed files into the knowledge base. Idempotent: tracks a content
hash per document and skips unchanged files.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from sovereign.knowledge.documents import DocumentStore
from sovereign.memory.retrieval import RetrievalPipeline
from sovereign.utils.logging import get_logger

logger = get_logger("knowledge.indexing")

_TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".py", ".html", ".sql"}


class Indexer:
    def __init__(self, knowledge_base: Any, document_store: DocumentStore,
                 retrieval: RetrievalPipeline, index_path: str | Path = "data/knowledge/index.json"):
        self.kb = knowledge_base
        self.documents = document_store
        self.retrieval = retrieval
        self.index_path = Path(index_path)
        self._hashes: dict[str, str] = {}
        if self.index_path.exists():
            import json

            self._hashes = json.loads(self.index_path.read_text(encoding="utf-8"))

    def index_directory(self, directory: str | Path, recursive: bool = True) -> dict[str, Any]:
        root = Path(directory)
        if not root.is_dir():
            return {"indexed": 0, "skipped": 0, "error": f"not a directory: {directory}"}

        files = sorted(root.rglob("*")) if recursive else sorted(root.glob("*"))
        indexed = skipped = 0
        for path in files:
            if not path.is_file() or path.suffix.lower() not in _TEXT_SUFFIXES:
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            key = str(path)
            if self._hashes.get(key) == digest:
                skipped += 1
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                self.documents.save(key, text, source=str(path), title=path.name)
                self.retrieval.index_document(key, text, {"path": str(path)})
                self._hashes[key] = digest
                indexed += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning("index failed for %s: %s", path, exc)
        self._persist()
        return {"indexed": indexed, "skipped": skipped}

    def _persist(self) -> None:
        import json

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.write_text(json.dumps(self._hashes, indent=1), encoding="utf-8")
