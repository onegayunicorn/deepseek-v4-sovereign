"""SOVEREIGN — long-running job manager (train, index, tts, migrate, build).

Jobs are named, state-tracked async tasks with progress reporting. A job
registry maps ``kind`` → async callable.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from sovereign.utils.id_generator import new_id
from sovereign.utils.logging import get_logger

logger = get_logger("jobs")

JobHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]

_HANDLERS: dict[str, JobHandler] = {}


def register_job(kind: str) -> Callable[[JobHandler], JobHandler]:
    def deco(fn: JobHandler) -> JobHandler:
        _HANDLERS[kind] = fn
        return fn

    return deco


@register_job("echo")
async def _echo(params: dict[str, Any]) -> dict[str, Any]:
    return {"echo": params.get("text", "")}


class JobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    async def submit(self, name: str, kind: str, params: dict[str, Any] | None = None) -> str:
        handler = _HANDLERS.get(kind)
        if handler is None:
            raise ValueError(f"unknown job kind: {kind} (registered: {sorted(_HANDLERS)})")
        job_id = new_id("job")
        self._jobs[job_id] = {
            "id": job_id, "name": name, "kind": kind, "params": params or {},
            "status": "pending", "progress": 0.0, "result": None, "error": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._tasks[job_id] = asyncio.create_task(self._run(job_id, handler, params or {}))
        return job_id

    async def _run(self, job_id: str, handler: JobHandler, params: dict[str, Any]) -> None:
        job = self._jobs[job_id]
        job["status"] = "running"
        try:
            result = await handler(params)
            job["status"] = "completed"
            job["progress"] = 1.0
            job["result"] = result
        except Exception as exc:  # noqa: BLE001
            job["status"] = "failed"
            job["error"] = str(exc)
            logger.exception("job %s failed", job_id)

    async def get(self, job_id: str) -> dict[str, Any] | None:
        return self._jobs.get(job_id)

    async def list(self) -> list[dict[str, Any]]:
        return list(self._jobs.values())

    async def cancel(self, job_id: str) -> bool:
        task = self._tasks.get(job_id)
        if task is None:
            return False
        task.cancel()
        job = self._jobs.get(job_id)
        if job and job["status"] == "running":
            job["status"] = "cancelled"
        return True

    async def set_progress(self, job_id: str, progress: float, note: str = "") -> None:
        job = self._jobs.get(job_id)
        if job:
            job["progress"] = max(0.0, min(1.0, progress))
            if note:
                job["note"] = note
