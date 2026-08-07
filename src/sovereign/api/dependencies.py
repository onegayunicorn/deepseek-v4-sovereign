"""SOVEREIGN — FastAPI dependency injection.

Holds the application container (orchestrator, memory, executor, ...) so
route modules can request singletons via Depends.
"""

from __future__ import annotations

from typing import Any

_container: dict[str, Any] = {}


def init_container(orchestrator: Any, memory: Any, executor: Any, tools: Any,
                   knowledge: Any, jobs: Any, webhooks: Any, hardware: Any) -> None:
    _container.update(
        orchestrator=orchestrator,
        memory=memory,
        executor=executor,
        tools=tools,
        knowledge=knowledge,
        jobs=jobs,
        webhooks=webhooks,
        hardware=hardware,
    )


def get_orchestrator() -> Any:
    return _container["orchestrator"]


def get_memory_manager() -> Any:
    return _container["memory"]


def get_tool_executor() -> Any:
    return _container["executor"]


def get_tool_registry() -> Any:
    return _container["tools"]


def get_knowledge_base() -> Any:
    return _container["knowledge"]


def get_job_manager() -> Any:
    return _container["jobs"]


def get_webhook_manager() -> Any:
    return _container["webhooks"]


def get_hardware_manager() -> Any:
    return _container["hardware"]
