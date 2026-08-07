"""SOVEREIGN — web search connector (private / local by default).

The default ``local`` provider performs no network I/O and returns an empty
result set with a hint — keeping the orchestrator sovereign. A provider
implementation (e.g. DuckDuckGo/Google) can be plugged in via
``providers`` without changing the tool contract.
"""

from __future__ import annotations

from typing import Any


def _local_search(query: str, max_results: int) -> list[dict[str, Any]]:
    # No phone-home: sovereign mode returns nothing until a provider is wired.
    return []


_PROVIDERS: dict[str, Any] = {"local": _local_search}


def search(query: str, *, max_results: int = 10, provider: str = "local") -> dict[str, Any]:
    """Search the web via the configured provider (sovereign by default)."""
    impl = _PROVIDERS.get(provider, _local_search)
    results = impl(query, max_results)
    return {"query": query, "provider": provider, "results": results, "count": len(results)}


def register_provider(name: str, fn: Any) -> None:
    _PROVIDERS[name] = fn
