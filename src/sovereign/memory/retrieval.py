"""SOVEREIGN — RAG retrieval pipelines.

Chunks documents, embeds them, and retrieves the top-k relevant chunks with
a similarity threshold. Works with any embedding callable (local model,
hash placeholder, or remote API).
"""

from __future__ import annotations

import re
from typing import Any, Callable

from sovereign.memory.vector_store import VectorStore


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks on paragraph/word boundaries."""
    if not text:
        return []
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    buffer = ""
    for para in paragraphs:
        if len(buffer) + len(para) <= chunk_size:
            buffer = f"{buffer}\n\n{para}" if buffer else para
            continue
        if buffer:
            chunks.append(buffer)
        words = para.split()
        buffer = ""
        for word in words:
            if len(buffer) + len(word) + 1 > chunk_size and buffer:
                chunks.append(buffer)
                buffer = " ".join(buffer.split()[-overlap:])
            buffer = f"{buffer} {word}".strip()
    if buffer:
        chunks.append(buffer)
    return [c for c in chunks if c]


class RetrievalPipeline:
    def __init__(self, vector_store: VectorStore, embedder: Callable[[str], list[float]],
                 chunk_size: int = 512, chunk_overlap: int = 50,
                 k: int = 5, threshold: float = 0.7):
        self.store = vector_store
        self.embedder = embedder
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.k = k
        self.threshold = threshold

    def index_document(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> int:
        chunks = chunk_text(text, self.chunk_size, self.chunk_overlap)
        for i, chunk in enumerate(chunks):
            self.store.upsert(
                f"{doc_id}:{i}",
                self.embedder(chunk),
                {"doc_id": doc_id, "chunk": i, "text": chunk, **(metadata or {})},
            )
        return len(chunks)

    def search(self, query: str) -> list[dict[str, Any]]:
        vector = self.embedder(query)
        return self.store.query(vector, k=self.k, threshold=self.threshold)
