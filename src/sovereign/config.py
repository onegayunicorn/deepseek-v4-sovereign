"""SOVEREIGN — configuration loader.

Loads every ``config/*.yaml`` file into a single :class:`Config` namespace,
layered as:

    defaults < file values < environment overrides (``SOVEREIGN_*``)

Environment overrides are ``SOVEREIGN_MODE``, ``SOVEREIGN_PORT`` and any
``SECTION_KEY`` mapping for nested scalar leaves (e.g. ``RUNTIME_RETRY_ATTEMPTS``).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from sovereign.utils.errors import ConfigError
from sovereign.utils.serialization import load_yaml

_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"

_ENV_PREFIX = "SOVEREIGN_"


class Config:
    """Namespaced configuration accessor: ``cfg.get("orchestrator.name")``."""

    def __init__(self, data: dict[str, Any], config_dir: Path | None = None):
        self._data = data
        self.config_dir = config_dir or _CONFIG_DIR

    # -- loading -----------------------------------------------------------
    @classmethod
    def load(cls, config_dir: str | Path | None = None) -> "Config":
        base = Path(config_dir) if config_dir else _CONFIG_DIR
        if not base.is_dir():
            raise ConfigError(f"config directory not found: {base}")

        merged: dict[str, Any] = {}
        for path in sorted(base.glob("*.yaml")):
            section = path.stem
            merged[section] = load_yaml(path) or {}

        cfg = cls(merged, base)
        cfg._apply_env()
        return cfg

    def _apply_env(self) -> None:
        for key, value in os.environ.items():
            if key.startswith(_ENV_PREFIX):
                leaf = key[len(_ENV_PREFIX):].lower()
                self._set_leaf(leaf, value)

    def _set_leaf(self, dotted: str, value: str) -> None:
        parts = dotted.split("_")
        node: dict[str, Any] = self._data
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = value

    # -- access ------------------------------------------------------------
    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self._data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def section(self, name: str) -> dict[str, Any]:
        value = self.get(name, {})
        return value if isinstance(value, dict) else {}

    def __getitem__(self, dotted: str) -> Any:
        value = self.get(dotted)
        if value is None:
            raise KeyError(dotted)
        return value

    def as_dict(self) -> dict[str, Any]:
        return self._data

    def __repr__(self) -> str:  # pragma: no cover
        return f"Config(sections={sorted(self._data)})"
