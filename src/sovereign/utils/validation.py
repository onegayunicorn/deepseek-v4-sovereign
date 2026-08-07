"""SOVEREIGN — input validation helpers (lightweight, dependency-free)."""

from __future__ import annotations

import re
from typing import Any

from sovereign.utils.errors import ValidationError

_ID_RE = re.compile(r"^[a-zA-Z0-9_\-./:]{1,128}$")


def require_str(value: Any, field: str, *, min_len: int = 1, max_len: int = 512) -> str:
    if not isinstance(value, str) or not (min_len <= len(value) <= max_len):
        raise ValidationError(f"{field} must be a string of length {min_len}-{max_len}")
    return value


def require_id(value: Any, field: str = "id") -> str:
    value = require_str(value, field, max_len=128)
    if not _ID_RE.match(value):
        raise ValidationError(f"{field} contains disallowed characters")
    return value


def require_int(value: Any, field: str, *, lo: int | None = None, hi: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{field} must be an integer")
    if lo is not None and value < lo:
        raise ValidationError(f"{field} must be >= {lo}")
    if hi is not None and value > hi:
        raise ValidationError(f"{field} must be <= {hi}")
    return value


def require_dict(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise ValidationError(f"{field} must be an object")
    return value


def require_in(value: Any, choices: set[str], field: str) -> str:
    if value not in choices:
        raise ValidationError(f"{field} must be one of {sorted(choices)}")
    return value
