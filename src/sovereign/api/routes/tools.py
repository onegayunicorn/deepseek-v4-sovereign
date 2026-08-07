"""SOVEREIGN — tool registry & execution endpoints (/api/v1/tools)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from sovereign.api.dependencies import get_tool_executor, get_tool_registry
from sovereign.api.schemas import ToolExecuteRequest

router = APIRouter(prefix="/api/v1/tools", tags=["tools"])


@router.get("/")
async def list_tools(tools: Any = Depends(get_tool_registry)):
    return {"tools": tools.specs()}


@router.post("/execute")
async def execute_tool(request: ToolExecuteRequest, executor: Any = Depends(get_tool_executor)):
    try:
        return await executor.execute(request.tool, request.arguments, role=request.role)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc))
