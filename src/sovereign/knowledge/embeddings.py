"""SOVEREIGN — text embedding pipelines.

Default ``HashEmbedder`` is deterministic and fully local (sovereign).
``OpenAIEmbedder`` and ``HuggingFaceEmbedder`` are optional network-backed
implementations enabled when credentials/models are configured.
"""

from __future__ import annotations

import os
from typing import Any

from sovereign.memory.vector_store import VectorStore


class HashEmbedder:
    """Deterministic local embedder — zero network, zero dependencies."""

    def __init__(self, dimension: int = 64):
        self.dimension = dimension

    def __call__(self, text: str) -> list[float]:
        return VectorStore.hash_placeholder(text, self.dimension)


class OpenAIEmbedder:
    """OpenAI-compatible embeddings via httpx (optional)."""

    def __init__(self, model: str = "text-embedding-3-small", dimension: int = 1536,
                 base_url: str | None = None, api_key: str | None = None):
        self.model = model
        self.dimension = dimension
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    def __call__(self, text: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not configured for OpenAIEmbedder")
        import httpx

        response = httpx.post(
            f"{self.base_url}/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": text},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


class HuggingFaceEmbedder:
    """HuggingFace inference router embeddings (optional)."""

    def __init__(self, model: str = "BAAI/bge-large-en-v1.5", dimension: int = 1024,
                 api_key: str | None = None):
        self.model = model
        self.dimension = dimension
        self.api_key = api_key or os.environ.get("HF_TOKEN", "")

    def __call__(self, text: str) -> list[float]:
        if not self.api_key:
            raise RuntimeError("HF_TOKEN not configured for HuggingFaceEmbedder")
        import httpx

        response = httpx.post(
            "https://router.huggingface.co/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "input": text},
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def embedder_from_config(config: dict[str, Any]) -> Any:
    """Build an embedder from config (sovereign by default)."""
    kind = (config or {}).get("kind", "hash")
    if kind == "openai":
        return OpenAIEmbedder(dimension=(config or {}).get("dimension", 1536))
    if kind == "huggingface":
        return HuggingFaceEmbedder(dimension=(config or {}).get("dimension", 1024))
    return HashEmbedder(dimension=(config or {}).get("dimension", 64))
