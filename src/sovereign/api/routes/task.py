"""SOVEREIGN — task management API endpoints (/api/v1/tasks)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from sovereign.api.dependencies import get_orchestrator
from sovereign.api.schemas import TaskCreate, TaskOut

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
async def create_task(task_data: TaskCreate, orchestrator: Any = Depends(get_orchestrator)):
    task_id = await orchestrator.submit_task(
        task_type=task_data.type,
        payload=task_data.payload,
        priority=task_data.priority,
        max_retries=task_data.max_retries,
    )
    task = await orchestrator.get_task(task_id)
    return task


@router.get("/", response_model=list[TaskOut])
async def list_tasks(status: str | None = Query(None), limit: int = Query(50, ge=1, le=100),
                     offset: int = Query(0, ge=0), orchestrator: Any = Depends(get_orchestrator)):
    return await orchestrator.list_tasks(status=status, limit=limit, offset=offset)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: str, orchestrator: Any = Depends(get_orchestrator)):
    task = await orchestrator.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def cancel_task(task_id: str, orchestrator: Any = Depends(get_orchestrator)):
    success = await orchestrator.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
    return {"status": "cancelled", "task_id": task_id}


@router.post("/{task_id}/retry")
async def retry_task(task_id: str, orchestrator: Any = Depends(get_orchestrator)):
    success = await orchestrator.retry_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or not retryable")
    return {"status": "retried", "task_id": task_id}


@router.get("/{task_id}/result")
async def get_task_result(task_id: str, orchestrator: Any = Depends(get_orchestrator)):
    result = await orchestrator.get_task_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found or not completed")
    return {"task_id": task_id, "result": result}
