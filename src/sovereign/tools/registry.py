"""SOVEREIGN — tool registration & discovery.

Tools are plain callables wrapped as :class:`ToolSpec`. The registry loads
builtin tools plus any custom tools under ``src/sovereign/tools/custom/``.
"""

from __future__ import annotations

import importlib
import inspect
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from sovereign.utils.logging import get_logger

logger = get_logger("tools")


@dataclass
class ToolSpec:
    name: str
    fn: Callable[..., Any]
    description: str = ""
    enabled: bool = True
    timeout_seconds: int = 30
    parameters: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self, config: dict[str, Any] | None = None):
        self._tools: dict[str, ToolSpec] = {}
        self.config = config or {}
        self._load_builtin()

    def _load_builtin(self) -> None:
        from sovereign.tools.builtin import api_client, code_interpreter, database, file_ops, shell, web_search

        registry: dict[str, Callable[..., Any]] = {
            "shell": shell.run_shell,
            "web_search": web_search.search,
            "file_ops": file_ops.run_file_ops,
            "api_client": api_client.request,
            "code_interpreter": code_interpreter.run_code,
            "database": database.query,
        }
        for name, fn in registry.items():
            enabled = True
            for tool_cfg in self.config.get("builtin", []):
                if tool_cfg.get("name") == name:
                    enabled = tool_cfg.get("enabled", True)
                    break
            self.register(ToolSpec(name=name, fn=fn, description=fn.__doc__ or "", enabled=enabled))

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec
        logger.debug("registered tool: %s", spec.name)

    def register_fn(self, name: str, fn: Callable[..., Any], description: str = "") -> ToolSpec:
        spec = ToolSpec(name=name, fn=fn, description=description or (fn.__doc__ or ""))
        self.register(spec)
        return spec

    def get(self, name: str) -> ToolSpec | None:
        spec = self._tools.get(name)
        if spec is None or not spec.enabled:
            return None
        return spec

    def names(self) -> list[str]:
        return [name for name, spec in sorted(self._tools.items()) if spec.enabled]

    def specs(self) -> list[dict[str, Any]]:
        return [
            {"name": spec.name, "description": spec.description, "enabled": spec.enabled,
             "timeout_seconds": spec.timeout_seconds}
            for spec in sorted(self._tools.values(), key=lambda s: s.name)
        ]

    def load_custom(self, module_path: str) -> int:
        """Import a custom-tools module and register its ToolSpec attrs."""
        try:
            module = importlib.import_module(module_path)
        except ImportError as exc:
            logger.warning("custom tools import failed: %s", exc)
            return 0
        count = 0
        for _, value in inspect.getmembers(module):
            if isinstance(value, ToolSpec):
                self.register(value)
                count += 1
        return count
