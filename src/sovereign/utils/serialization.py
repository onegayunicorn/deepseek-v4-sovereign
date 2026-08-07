"""SOVEREIGN — JSON / YAML serialization helpers.

YAML loading degrades gracefully: if PyYAML is unavailable, a minimal
fallback raises a clear ConfigError instead of crashing opaquely.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sovereign.utils.errors import ConfigError

try:  # pragma: no cover - environment dependent
    import yaml  # type: ignore

    _HAS_YAML = True
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore
    _HAS_YAML = False


def load_json(path: str | Path) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise ConfigError(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}")


def dump_json(data: Any, path: str | Path, *, indent: int = 2) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False)


def load_yaml(path: str | Path) -> Any:
    if not _HAS_YAML:
        raise ConfigError("PyYAML is required to load YAML configs (pip install pyyaml)")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except FileNotFoundError:
        raise ConfigError(f"file not found: {path}")
    except yaml.YAMLError as exc:  # type: ignore[attr-defined]
        raise ConfigError(f"invalid YAML in {path}: {exc}")


def loads_yaml(text: str) -> Any:
    if not _HAS_YAML:
        raise ConfigError("PyYAML is required (pip install pyyaml)")
    return yaml.safe_load(text)  # type: ignore[attr-defined]
