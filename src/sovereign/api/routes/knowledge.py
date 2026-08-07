"""SOVEREIGN — knowledge base & graph endpoints (/api/v1/knowledge)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from sovereign.api.dependencies import get_knowledge_base

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])


class IngestRequest(BaseModel):
    doc_id: str
    text: str
    metadata: dict[str, Any] | None = None


class TripleRequest(BaseModel):
    subject: str
    predicate: str
    object: str


@router.post("/ingest")
async def ingest(request: IngestRequest, kb: Any = Depends(get_knowledge_base)):
    chunks = kb.ingest(request.doc_id, request.text, request.metadata)
    return {"status": "ingested", "doc_id": request.doc_id, "chunks": chunks}


@router.post("/search")
async def search(query: str, k: int = 5, kb: Any = Depends(get_knowledge_base)):
    return {"query": query, "results": kb.search(query, k=k)}


@router.post("/graph")
async def add_triple(request: TripleRequest, kb: Any = Depends(get_knowledge_base)):
    return {"edge": kb.add_triple(request.subject, request.predicate, request.object)}


@router.get("/stats")
async def stats(kb: Any = Depends(get_knowledge_base)):
    return kb.stats()
