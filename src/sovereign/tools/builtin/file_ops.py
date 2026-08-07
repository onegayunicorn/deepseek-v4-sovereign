"""SOVEREIGN — file operations tool (read/write/list) with path policy."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sovereign.utils.errors import ToolError


def run_file_ops(op: str, path: str, *, content: str | None = None,
                 max_size_mb: int = 100) -> dict[str, Any]:
    """Perform a file operation: read | write | list | delete.

    ``path`` is resolved relative to the monorepo root; absolute paths
    outside are rejected.
    """
    target = Path(path)
    if target.is_absolute():
        raise ToolError("absolute paths not allowed; use workspace-relative paths")

    if op == "read":
        if not target.is_file():
            raise ToolError(f"file not found: {path}")
        if target.stat().st_size > max_size_mb * 1024 * 1024:
            raise ToolError(f"file exceeds {max_size_mb}MB limit")
        return {"op": "read", "path": path, "content": target.read_text(encoding="utf-8")}

    if op == "write":
        if content is None:
            raise ToolError("write requires content")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"op": "write", "path": path, "bytes": len(content.encode())}

    if op == "list":
        root = target if target.is_dir() else target.parent
        entries = [str(p.relative_to(Path("."))) for p in sorted(root.rglob("*"))][:500]
        return {"op": "list", "path": str(root), "entries": entries}

    if op == "delete":
        if target.is_dir():
            raise ToolError("directory delete not allowed via tool")
        target.unlink(missing_ok=True)
        return {"op": "delete", "path": path}

    raise ToolError(f"unknown file op: {op}")
