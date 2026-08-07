"""SOVEREIGN — RBAC/ABAC permission engine.

Loads role→permission definitions from ``config/permissions.yaml`` (or a
passed dict). ``check(role, permission)`` supports wildcards: ``*:*`` and
``tools:execute:*``.
"""

from __future__ import annotations

import fnmatch
from typing import Any

from sovereign.utils.serialization import load_yaml

_ROLE_DEFAULTS = {
    "admin": ["*:*"],
    "operator": ["task:read", "task:create", "task:update", "task:cancel",
                 "agent:list", "agent:status", "memory:search", "tools:execute",
                 "jobs:manage", "system:status", "system:logs"],
    "user": ["task:read", "task:create", "task:status", "agent:list",
             "memory:search", "tools:execute:web_search", "tools:execute:file_ops"],
    "viewer": ["task:read", "agent:list", "agent:status", "system:status"],
    "auditor": ["audit:read", "audit:export", "system:status"],
}


class PermissionEngine:
    def __init__(self, config: dict[str, Any] | None = None):
        roles = config.get("roles") if config else None
        self.roles: dict[str, list[str]] = roles or _ROLE_DEFAULTS

    @classmethod
    def from_yaml(cls, path: str) -> "PermissionEngine":
        data = load_yaml(path)
        return cls(data or {})

    def check(self, role: str, permission: str) -> bool:
        granted = self.roles.get(role, [])
        for pattern in granted:
            if fnmatch.fnmatchcase(permission, pattern):
                return True
        return False

    def permissions_for(self, role: str) -> list[str]:
        return list(self.roles.get(role, []))

    def roles_list(self) -> list[str]:
        return sorted(self.roles)
