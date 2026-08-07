"""SOVEREIGN — sandboxed shell tool.

Only commands in the configured allow-list may run; blocked prefixes are
rejected before execution. Uses :class:`Sandbox` for resource limits.
"""

from __future__ import annotations

from typing import Any

from sovereign.security.sandbox import Sandbox
from sovereign.utils.errors import ToolError

_ALLOWED = {"ls", "cat", "grep", "find", "python", "node", "git", "echo", "pwd", "wc", "head", "tail"}
_BLOCKED_PREFIXES = ("rm -rf", "sudo", "chmod", "dd ", "mkfs", "mkfs.", "> /dev/sd", ":(){", "shutdown", "reboot")


def run_shell(command: str, *, sandbox: Sandbox | None = None, timeout: int | None = None) -> dict[str, Any]:
    """Run a shell command inside the sandbox with policy checks."""
    if not command or not command.strip():
        raise ToolError("empty command")

    first = command.strip().split()[0]
    if first not in _ALLOWED:
        raise ToolError(f"command not in allow-list: {first}")

    lowered = command.lower()
    for prefix in _BLOCKED_PREFIXES:
        if lowered.startswith(prefix):
            raise ToolError(f"blocked command prefix: {prefix}")

    box = sandbox or Sandbox(timeout_seconds=timeout or 30)
    return box.run(command, timeout=timeout)
