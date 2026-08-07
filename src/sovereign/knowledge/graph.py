"""SOVEREIGN — knowledge graph (NetworkX or pure-Python fallback).

Uses NetworkX when available (rich algorithms); otherwise a compact
pure-Python adjacency store keeps the module importable everywhere.
"""

from __future__ import annotations

from typing import Any

try:
    import networkx as nx  # type: ignore

    _HAS_NX = True
except ImportError:  # pragma: no cover
    nx = None  # type: ignore[assignment]
    _HAS_NX = False


class _AdjacencyGraph:
    def __init__(self) -> None:
        self.nodes: set[str] = set()
        self.edges: list[dict[str, Any]] = []

    def add_node(self, node: str, **attrs: Any) -> None:
        self.nodes.add(node)

    def add_edge(self, source: str, target: str, label: str = "") -> None:
        self.nodes.update([source, target])
        self.edges.append({"source": source, "target": target, "label": label})

    def neighbors(self, node: str) -> list[dict[str, Any]]:
        return [
            {"node": e["target"], "label": e["label"]}
            for e in self.edges
            if e["source"] == node
        ]

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)


class KnowledgeGraph:
    """Unified knowledge graph facade."""

    def __init__(self) -> None:
        self._impl = nx.Graph() if _HAS_NX else _AdjacencyGraph()

    def add_node(self, node: str, **attrs: Any) -> None:
        self._impl.add_node(node, **(attrs or {}))

    def add_edge(self, source: str, target: str, label: str = "") -> str:
        self._impl.add_edge(source, target, label=label)
        return f"{source}--[{label}]-->{target}"

    def neighbors(self, node: str) -> list[dict[str, Any]]:
        if _HAS_NX:
            return [
                {"node": n, "label": self._impl[n][node].get("label", "")}
                for n in self._impl.neighbors(node)
            ]
        return self._impl.neighbors(node)  # type: ignore[union-attr]

    def shortest_path(self, source: str, target: str) -> list[str]:
        if _HAS_NX:
            try:
                return list(nx.shortest_path(self._impl, source, target))
            except (nx.NetworkXNoPath, nx.NodeNotFound):  # type: ignore[attr-defined]
                return []
        return []

    def node_count(self) -> int:
        return self._impl.node_count() if not _HAS_NX else self._impl.number_of_nodes()

    def edge_count(self) -> int:
        return self._impl.edge_count() if not _HAS_NX else self._impl.number_of_edges()
