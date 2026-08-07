"""SOVEREIGN — memory API endpoints (/api/v1/memory)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from sovereign.api.dependencies import get_memory_manager
from sovereign.api.schemas import MemorySearchRequest, MemoryStoreRequest

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


@router.post("/store")
async def store_memory(request: MemoryStoreRequest, memory: Any = Depends(get_memory_manager)):
    await memory.store(request.memory_type, request.key, request.value, request.metadata)
    return {"status": "stored", "key": request.key, "type": request.memory_type}


@router.get("/{memory_type}/{key}")
async def retrieve_memory(memory_type: str, key: str, memory: Any = Depends(get_memory_manager)):
    value = await memory.retrieve(memory_type, key)
    if value is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"key": key, "value": value, "type": memory_type}


@router.post("/search")
async def search_memory(request: MemorySearchRequest, memory: Any = Depends(get_memory_manager)):
    results = await memory.search(request.query, request.memory_types, request.k)
    return {"query": request.query, "results": results}


@router.get("/stats")
async def memory_stats(memory: Any = Depends(get_memory_manager)):
    return await memory.get_stats()
