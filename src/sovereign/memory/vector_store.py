"""SOVEREIGN — local vector store interface.

Backends: ``memory`` (pure-Python cosine, zero deps) and ``chromadb``
(optional). The memory backend keeps the orchestrator fully sovereign —
embeddings can be computed locally or skipped with hashed placeholders.
"""

from __future__ import annotations

import hashlib
import math
import threading
from typing import Any

from sovereign.utils.errors import MemoryError

try:
    import chromadb  # type: ignore

    _HAS_CHROMA = True
except ImportError:  # pragma: no cover
    chromadb = None  # type: ignore[assignment]
    _HAS_CHROMA = False


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class _MemoryVectorStore:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self._lock = threading.Lock()
        self._vectors: dict[str, list[float]] = {}
        self._meta: dict[str, dict[str, Any]] = {}

    def upsert(self, key: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        if len(vector) != self.dimension:
            raise MemoryError(f"vector dimension {len(vector)} != {self.dimension}")
        with self._lock:
            self._vectors[key] = vector
            self._meta[key] = metadata or {}

    def query(self, vector: list[float], k: int = 5, threshold: float = 0.0) -> list[dict[str, Any]]:
        with self._lock:
            scored = [(key, _cosine(vector, vec)) for key, vec in self._vectors.items()]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [
            {"key": key, "score": round(score, 4), "metadata": self._meta.get(key, {})}
            for key, score in scored[:k]
            if score >= threshold
        ]

    def count(self) -> int:
        with self._lock:
            return len(self._vectors)


class VectorStore:
    """Unified vector store facade."""

    def __init__(self, backend: str = "memory", dimension: int = 1536,
                 path: str = "data/memory/vectors", collection: str = "memories"):
        self.backend = backend
        self.dimension = dimension
        self.collection = collection
        if backend == "chromadb" and _HAS_CHROMA:
            client = chromadb.PersistentClient(path=path)  # type: ignore[union-attr]
            self._impl = client.get_or_create_collection(collection)
        else:
            self._impl = _MemoryVectorStore(dimension)
        self._backend_name = "chromadb" if (backend == "chromadb" and _HAS_CHROMA) else "memory"

    def upsert(self, key: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        if self._backend_name == "chromadb":
            self._impl.upsert(  # type: ignore[union-attr]
                ids=[key], embeddings=[vector], metadatas=[metadata or {}]
            )
        else:
            self._impl.upsert(key, vector, metadata)  # type: ignore[union-attr]

    def query(self, vector: list[float], k: int = 5, threshold: float = 0.0) -> list[dict[str, Any]]:
        if self._backend_name == "chromadb":
            result = self._impl.query(query_embeddings=[vector], n_results=k)  # type: ignore[union-attr]
            return [
                {"key": key, "score": score, "metadata": meta or {}}
                for key, score, meta in zip(
                    result["ids"][0], result["distances"][0], result["metadatas"][0]
                )
            ]
        return self._impl.query(vector, k, threshold)  # type: ignore[union-attr]

    def count(self) -> int:
        return self._impl.count()  # type: ignore[union-attr]

    @staticmethod
    def hash_placeholder(text: str, dimension: int = 64) -> list[float]:
        """Deterministic pseudo-embedding for sovereign/no-network mode."""
        seed = hashlib.sha256(text.encode()).digest()
        return [((seed[i % len(seed)] + (i * 31) % 256) / 255.0) - 0.5 for i in range(dimension)]
