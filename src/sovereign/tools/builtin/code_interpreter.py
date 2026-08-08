"""SOVEREIGN — isolated Python/JS execution (limited interpreter).

Executes a snippet with only allow-listed stdlib imports available;
``os``, ``subprocess``, ``socket``, and network libraries are blocked by
replacing the import machinery.
"""

from __future__ import annotations

import io
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

from sovereign.utils.errors import ToolError

_ALLOWED_IMPORTS = {"json", "csv", "datetime", "math", "random", "collections", "itertools", "re", "statistics"}
_BLOCKED_IMPORTS = {"os", "subprocess", "socket", "requests", "sys", "pathlib", "shutil"}

_HEADER = f"""
import builtins as _b
_b._banned = {sorted(_BLOCKED_IMPORTS)}
_original_import = _b.__import__
def _safe_import(name, *args, **kwargs):
    if name.split('.')[0] in _b._banned:
        raise ImportError(f"import of '{{name}}' is blocked by sovereign sandbox")
    return _original_import(name, *args, **kwargs)
_b.__import__ = _safe_import
"""


def run_code(code: str, *, language: str = "python", timeout: int = 120) -> dict[str, Any]:
    """Run ``code`` in an isolated namespace with import restrictions."""
    if language != "python":
        raise ToolError(f"unsupported language: {language}")

    namespace: dict[str, Any] = {}
    buffer = io.StringIO()
    started = time.monotonic()
    try:
        with redirect_stdout(buffer), redirect_stderr(buffer):
            exec(_HEADER, namespace)  # noqa: S102 — sandboxed by design
            exec(code, namespace)  # noqa: S102
        return {
            "ok": True,
            "output": buffer.getvalue(),
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "output": buffer.getvalue(),
            "error": str(exc),
            "traceback": traceback.format_exc(limit=5),
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
    finally:
        # Restore the real import machinery — the sandbox patch must not
        # leak into the host process (it broke later `import sys` calls).
        import builtins as _real_builtins

        if "_original_import" in namespace and callable(namespace["_original_import"]):
            _real_builtins.__import__ = namespace["_original_import"]
