"""SOVEREIGN — semantic search & reasoning over the knowledge base."""

from __future__ import annotations

from typing import Any

from sovereign.knowledge.knowledge_base import KnowledgeBase


class QueryEngine:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb

    def answer(self, query: str, k: int = 5) -> dict[str, Any]:
        """Retrieve evidence + graph context for a query."""
        chunks = self.kb.search(query, k=k)

        # Extract candidate entities mentioned in the query for graph lookup.
        graph_hits: list[dict[str, Any]] = []
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            doc_id = meta.get("doc_id", "")
            graph_hits.extend(self.kb.neighbors(doc_id) if doc_id else [])

        return {
            "query": query,
            "evidence": chunks,
            "graph_context": graph_hits[:20],
            "evidence_count": len(chunks),
        }

    def summarize(self, query: str, k: int = 5, max_chars: int = 2000) -> str:
        result = self.answer(query, k)
        snippets = []
        budget = max_chars
        for chunk in result["evidence"]:
            text = chunk.get("metadata", {}).get("text", "")
            if budget <= 0:
                break
            snippets.append(text[:budget])
            budget -= len(text)
        return "\n\n".join(snippets)
