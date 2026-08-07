"""SOVEREIGN — tool-level permission enforcement.

Checks ``config/permissions.yaml`` tool_permissions: which roles may invoke
each tool, plus optional path-pattern allow-lists for file_ops.
"""

from __future__ import annotations

import fnmatch
from typing import Any

from sovereign.utils.errors import ToolError

_DEFAULTS: dict[str, dict[str, Any]] = {
    "shell": {"roles": ["admin", "operator"]},
    "web_search": {"roles": ["admin", "operator", "user"]},
    "file_ops": {"roles": ["admin", "operator", "user"], "allowed_patterns": ["*.txt", "*.md", "*.json", "*.yaml"]},
    "code_interpreter": {"roles": ["admin", "operator"]},
    "database": {"roles": ["admin", "operator"]},
    "api_client": {"roles": ["admin", "operator"]},
    "browser": {"roles": ["admin"]},
    "email": {"roles": ["admin"]},
}


class ToolAuthorization:
    def __init__(self, config: dict[str, Any] | None = None):
        self.rules = {**_DEFAULTS, **(config or {})}

    def can_execute(self, role: str, tool_name: str) -> bool:
        rule = self.rules.get(tool_name)
        if rule is None:
            return False
        return role in rule.get("roles", [])

    def check_path(self, tool_name: str, path: str) -> bool:
        rule = self.rules.get(tool_name, {})
        patterns = rule.get("allowed_patterns", [])
        if not patterns:
            return True
        return any(fnmatch.fnmatch(path, p) for p in patterns)

    def require(self, role: str, tool_name: str, path: str | None = None) -> None:
        if not self.can_execute(role, tool_name):
            raise ToolError(f"role '{role}' cannot execute tool '{tool_name}'")
        if path and not self.check_path(tool_name, path):
            raise ToolError(f"path '{path}' not allowed for tool '{tool_name}'")
