"""SOVEREIGN — queryable knowledge base.

Facade combining document store, vector index (via RetrievalPipeline), and
the knowledge graph. The default embedder is the sovereign hash-placeholder
(no network required); swap in a real embedding model for semantic quality.
"""

from __future__ import annotations

from typing import Any

from sovereign.knowledge.documents import DocumentStore
from sovereign.knowledge.graph import KnowledgeGraph
from sovereign.memory.retrieval import RetrievalPipeline
from sovereign.memory.vector_store import VectorStore


class KnowledgeBase:
    def __init__(self, vector_store: VectorStore | None = None,
                 graph: KnowledgeGraph | None = None,
                 documents: DocumentStore | None = None,
                 embedder: Any | None = None):
        self.documents = documents or DocumentStore()
        self.graph = graph or KnowledgeGraph()
        self.embedder = embedder or (lambda text: VectorStore.hash_placeholder(text, 64))
        self.retrieval = RetrievalPipeline(
            vector_store or VectorStore(backend="memory", dimension=64),
            self.embedder,
            k=5,
            threshold=0.0,
        )

    def ingest(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> int:
        self.documents.save(doc_id, text, metadata)
        return self.retrieval.index_document(doc_id, text, metadata)

    def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        return self.retrieval.search(query)[:k]

    def add_triple(self, subject: str, predicate: str, object_: str) -> str:
        return self.graph.add_edge(subject, object_, label=predicate)

    def neighbors(self, node: str) -> list[dict[str, Any]]:
        return self.graph.neighbors(node)

    def stats(self) -> dict[str, Any]:
        return {
            "documents": self.documents.count(),
            "graph_nodes": self.graph.node_count(),
            "graph_edges": self.graph.edge_count(),
        }
