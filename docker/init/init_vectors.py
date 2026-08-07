#!/usr/bin/env python3
"""SOVEREIGN — initialize the vector store collection (container entry)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from sovereign.memory.vector_store import VectorStore  # noqa: E402

store = VectorStore(backend="memory", dimension=64, collection="memories")
print(f"[init] vector store ready: backend={store._backend_name} collection={store.collection}")
