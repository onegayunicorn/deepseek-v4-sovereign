"""SOVEREIGN — authorization enforcement (RBAC).

Delegates role→permission definitions to ``governance.permissions``; this
module is the security-layer entry point used by tools and the API.
"""

from __future__ import annotations

from typing import Any

from sovereign.utils.errors import SecurityError

try:
    from sovereign.governance.permissions import PermissionEngine  # type: ignore

    _HAS_ENGINE = True
except ImportError:  # pragma: no cover
    PermissionEngine = None  # type: ignore[assignment,misc]
    _HAS_ENGINE = False


class AuthorizationService:
    def __init__(self, config: dict[str, Any] | None = None):
        self._engine = PermissionEngine(config or {}) if _HAS_ENGINE else None

    def check(self, role: str, permission: str) -> bool:
        if self._engine is not None:
            return self._engine.check(role, permission)
        # Fallback: admin passes everything, others denied.
        return role == "admin"

    def require(self, role: str, permission: str) -> None:
        if not self.check(role, permission):
            raise SecurityError(f"role '{role}' lacks permission '{permission}'")

    def can_execute_tool(self, role: str, tool_name: str) -> bool:
        return self.check(role, f"tools:execute:{tool_name}") or self.check(role, "tools:execute")
