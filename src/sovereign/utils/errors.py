"""SOVEREIGN — custom exception hierarchy.

Every subsystem raises a typed exception so the API layer can map them to
HTTP status codes and the governance layer can audit failures uniformly.
"""

from __future__ import annotations


class SovereignError(Exception):
    """Base class for all sovereign orchestrator errors."""

    code = "sovereign.error"

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "details": self.details}


class ConfigError(SovereignError):
    """Invalid or missing configuration."""

    code = "config.error"


class TaskError(SovereignError):
    """Task submission, execution, or lifecycle failure."""

    code = "task.error"


class AgentError(SovereignError):
    """Agent lifecycle or execution failure."""

    code = "agent.error"


class ToolError(SovereignError):
    """Tool execution failure (timeout, policy, runtime)."""

    code = "tool.error"


class MemoryError(SovereignError):
    """Memory backend failure (store, retrieve, prune)."""

    code = "memory.error"


class SecurityError(SovereignError):
    """Authentication / authorization / encryption failure."""

    code = "security.error"


class NotFoundError(SovereignError):
    """Requested resource does not exist."""

    code = "not_found"


class ValidationError(SovereignError):
    """Input validation failure."""

    code = "validation.error"
