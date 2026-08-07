"""SOVEREIGN — core orchestrator.

Manages the complete lifecycle of tasks, agents, and workflows:

    submit_task → queue → _process_tasks → _execute_task → agent → result
                                                                    │
                                        retry (status=failed) ◀────┘
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from sovereign.agents.base import BaseAgent
from sovereign.communication.pubsub import EventBus
from sovereign.governance.audit_logger import AuditLogger
from sovereign.memory.memory_manager import MemoryManager
from sovereign.orchestrator.agent_factory import AgentFactory
from sovereign.orchestrator.scheduler import Scheduler
from sovereign.orchestrator.state_machine import TaskStateMachine
from sovereign.orchestrator.task_queue import QueueTask, TaskQueue
from sovereign.tools.registry import ToolRegistry
from sovereign.utils.id_generator import new_id
from sovereign.utils.logging import get_logger
from sovereign.utils.metrics import METRICS

logger = get_logger("orchestrator.core")

VALID_STATUSES = {"pending", "running", "completed", "failed", "cancelled"}


@dataclass
class Task:
    """Orchestrator task (persisted via QueueTask when queued)."""

    id: str
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    max_retries: int = 3
    status: str = "pending"
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    error: str | None = None
    result: Any = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "payload": self.payload,
            "priority": self.priority,
            "max_retries": self.max_retries,
            "status": self.status,
            "retry_count": self.retry_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "result": self.result,
        }

    def to_queue_task(self) -> QueueTask:
        return QueueTask(
            id=self.id, type=self.type, payload=self.payload, priority=self.priority,
            status=self.status, retry_count=self.retry_count, max_retries=self.max_retries,
        )


class SovereignOrchestrator:
    """Main orchestrator: coordinates agents, tasks, memory, tools, governance."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        event_bus: EventBus | None = None,
        memory_manager: MemoryManager | None = None,
        tool_registry: ToolRegistry | None = None,
        audit_logger: AuditLogger | None = None,
        agent_factory: AgentFactory | None = None,
    ):
        self.config = config or {}
        self.event_bus = event_bus or EventBus()
        self.memory_manager = memory_manager or MemoryManager()
        self.tool_registry = tool_registry or ToolRegistry()
        self.audit_logger = audit_logger or AuditLogger()
        self.agent_factory = agent_factory or AgentFactory()
        self.state_machine = TaskStateMachine()

        self.tasks: dict[str, Task] = {}
        self.agents: dict[str, BaseAgent] = {}
        self.active_tasks: dict[str, asyncio.Task] = {}
        self.is_running = False
        self.started_at: datetime | None = None

        self.task_queue = TaskQueue(
            backend=(config or {}).get("task_queue", {}).get("backend", "memory"),
            db_path=(config or {}).get("task_queue", {}).get("db_path", "data/state/orchestration_state.sqlite"),
        )
        self.scheduler = Scheduler(submit_fn=self.submit_task)

    # -- lifecycle ---------------------------------------------------------
    async def start(self) -> None:
        self.is_running = True
        self.started_at = datetime.now(timezone.utc)
        await self.event_bus.start()
        await self.audit_logger.log_event("system.startup", "system",
                                          {"version": self.config.get("version", "1.0.0")})
        asyncio.create_task(self._process_tasks())
        asyncio.create_task(self._health_check())
        logger.info("SOVEREIGN orchestrator started")

    async def stop(self) -> None:
        self.is_running = False
        for task_id in list(self.active_tasks):
            await self.cancel_task(task_id)
        await self.event_bus.stop()
        await self.audit_logger.log_event("system.shutdown", "system",
                                          {"uptime": self._get_uptime()})
        logger.info("SOVEREIGN orchestrator stopped")

    def _get_uptime(self) -> float:
        if self.started_at is None:
            return 0.0
        return (datetime.now(timezone.utc) - self.started_at).total_seconds()

    # -- task submission ---------------------------------------------------
    async def submit_task(self, task_type: str, payload: dict[str, Any],
                          priority: int = 5, max_retries: int = 3) -> str:
        task_id = new_id("task")
        task = Task(id=task_id, type=task_type, payload=payload,
                    priority=max(1, min(10, priority)),
                    max_retries=max_retries, status="pending")
        self.tasks[task_id] = task
        self.state_machine.register(task_id)
        await self.task_queue.put(task.to_queue_task())
        await self.audit_logger.log_event("task.submitted", "user",
                                          {"task_id": task_id, "type": task_type})
        METRICS.incr("tasks_submitted", labels={"type": task_type})
        return task_id

    # -- processing loop ---------------------------------------------------
    async def _process_tasks(self) -> None:
        while self.is_running:
            try:
                qtask = await self.task_queue.get()
                task = self.tasks.get(qtask.id)
                if task is None:
                    continue
                self.state_machine.transition(task.id, "running")
                task.status = "running"
                task.updated_at = datetime.now(timezone.utc)
                self.active_tasks[task.id] = asyncio.create_task(self._execute_task(task))
            except asyncio.CancelledError:
                break
            except Exception:  # noqa: BLE001
                logger.exception("task processor error")

    async def _execute_task(self, task: Task) -> None:
        try:
            agent = await self._get_agent_for_task(task)
            result = await agent.execute(task)
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now(timezone.utc)
            self.state_machine.transition(task.id, "completed")
            await self.memory_manager.store_task_result(task)
            await self.audit_logger.log_event(
                "task.completed", "system",
                {"task_id": task.id,
                 "duration": (task.completed_at - task.created_at).total_seconds()},
            )
            METRICS.incr("tasks_completed")
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.error = str(exc)
            task.retry_count += 1
            if task.retry_count < task.max_retries:
                task.status = "pending"
                await self.task_queue.put_back(task.to_queue_task())
                await self.audit_logger.log_event("task.retried", "system",
                                                  {"task_id": task.id, "retry": task.retry_count})
            else:
                self.state_machine.transition(task.id, "failed")
                await self.audit_logger.log_event("task.failed", "system",
                                                  {"task_id": task.id, "error": str(exc)})
                METRICS.incr("tasks_failed")
        finally:
            self.active_tasks.pop(task.id, None)

    async def _get_agent_for_task(self, task: Task) -> BaseAgent:
        """Route task type → agent kind via config/models routing."""
        routing = self.config.get("routing", {})
        agent_kind = {
            "reason": "deepseek.reasoner",
            "code": "deepseek.coder",
            "search": "tool",
            "plan": "deepseek.chat",
            "coordinate": "coordinator",
            "memory": "memory",
            "tts": "tts",
        }.get(task.type, routing.get("default", "deepseek.chat"))

        agent_id = f"{agent_kind}:{task.id}"
        if agent_id not in self.agents:
            agent = self.agent_factory.create(
                agent_kind,
                event_bus=self.event_bus,
                config={"model": self.config.get("default_model", "deepseek-v4-sovereign")},
            )
            self.agents[agent_id] = agent
        return self.agents[agent_id]

    def _generate_task_id(self) -> str:
        return new_id("task")

    # -- task queries ------------------------------------------------------
    async def get_task(self, task_id: str) -> Task | None:
        return self.tasks.get(task_id)

    async def list_tasks(self, status: str | None = None, limit: int = 50, offset: int = 0) -> list[Task]:
        tasks = list(self.tasks.values())
        if status and status in VALID_STATUSES:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks[offset:offset + limit]

    async def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task is None or task.status in ("completed", "cancelled"):
            return False
        runner = self.active_tasks.pop(task_id, None)
        if runner is not None:
            runner.cancel()
        task.status = "cancelled"
        self.state_machine.transition(task_id, "cancelled")
        await self.audit_logger.log_event("task.cancelled", "user", {"task_id": task_id})
        return True

    async def retry_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if task is None or task.status != "failed":
            return False
        task.status = "pending"
        task.retry_count = 0
        task.error = None
        await self.task_queue.put(task.to_queue_task())
        return True

    async def get_task_result(self, task_id: str) -> Any:
        task = self.tasks.get(task_id)
        if task is None or task.status != "completed":
            return None
        return task.result

    # -- agent queries -----------------------------------------------------
    async def list_agents(self) -> list[dict[str, Any]]:
        return [agent.status() for agent in self.agents.values()]

    async def get_agent(self, agent_id: str) -> dict[str, Any] | None:
        agent = self.agents.get(agent_id)
        return agent.status() if agent else None

    async def restart_agent(self, agent_id: str) -> bool:
        agent = self.agents.get(agent_id)
        if agent is None:
            return False
        await agent.stop()
        await agent.start()
        return True

    # -- health ------------------------------------------------------------
    async def _health_check(self) -> None:
        while self.is_running:
            await asyncio.sleep((self.config.get("health_check") or {}).get("interval_seconds", 30))
            METRICS.set_gauge("tasks_active", len(self.active_tasks))
            METRICS.set_gauge("agents_active", len(self.agents))
            METRICS.set_gauge("uptime_seconds", self._get_uptime())

    async def health(self) -> dict[str, Any]:
        return {
            "status": "ok" if self.is_running else "stopped",
            "uptime_seconds": self._get_uptime(),
            "tasks": len(self.tasks),
            "active_tasks": len(self.active_tasks),
            "agents": len(self.agents),
            "queue_depth": self.task_queue.size(),
        }

    def to_json(self, path: str = "data/state/task_state.json") -> None:
        import pathlib

        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }
        pathlib.Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False))
