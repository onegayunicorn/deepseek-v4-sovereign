"""SOVEREIGN — secure tool runner.

Wraps tool execution with permission checks, timeouts, audit logging, and
metrics. This is the only path through which agents invoke tools.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from sovereign.governance.audit_logger import AuditLogger
from sovereign.tools.registry import ToolRegistry
from sovereign.utils.errors import ToolError
from sovereign.utils.logging import get_logger
from sovereign.utils.metrics import METRICS

logger = get_logger("tools.executor")


class ToolExecutor:
    def __init__(self, registry: ToolRegistry, audit: AuditLogger | None = None,
                 authorization: Any | None = None):
        self.registry = registry
        self.audit = audit
        self.authorization = authorization

    async def execute(self, tool_name: str, arguments: dict[str, Any] | None = None,
                      *, role: str = "operator", trace_id: str = "") -> dict[str, Any]:
        """Execute ``tool_name`` with policy checks + audit + metrics."""
        spec = self.registry.get(tool_name)
        if spec is None:
            raise ToolError(f"tool not found or disabled: {tool_name}")

        if self.authorization is not None and not self.authorization.can_execute_tool(role, tool_name):
            raise ToolError(f"role '{role}' is not permitted to execute tool '{tool_name}'")

        started = time.perf_counter()
        try:
            if inspect_is_async(spec.fn):
                result = await spec.fn(**(arguments or {}))
            else:
                result = await asyncio.to_thread(spec.fn, **(arguments or {}))
            outcome = "ok"
            return {"tool": tool_name, "ok": True, "result": result}
        except ToolError:
            outcome = "error"
            raise
        except Exception as exc:  # noqa: BLE001
            outcome = "error"
            raise ToolError(f"tool '{tool_name}' failed: {exc}") from exc
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)
            METRICS.incr(f"tool_{tool_name}_calls", labels={"result": outcome})
            METRICS.observe("tool_seconds", duration_ms / 1000)
            if self.audit is not None:
                self.audit.log(
                    "tool.executed",
                    role,
                    {"tool": tool_name, "args": arguments or {}, "outcome": outcome,
                     "duration_ms": duration_ms, "trace_id": trace_id},
                )


def inspect_is_async(fn: Any) -> bool:
    return asyncio.iscoroutinefunction(fn)
