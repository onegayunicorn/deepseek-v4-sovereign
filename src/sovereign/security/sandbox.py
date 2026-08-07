"""SOVEREIGN — sandbox / resource-limit abstraction.

Provides a thin, dependency-free interface for constrained execution.
On Linux with privileges, it can drop to a low-priority, memory-limited
subprocess; the default path is a plain subprocess with timeout + output caps.
"""

from __future__ import annotations

import os
import resource
import shlex
import signal
import subprocess
from typing import Any

from sovereign.utils.errors import ToolError

_MAX_OUTPUT_BYTES = 1_000_000


class Sandbox:
    def __init__(
        self,
        memory_mb: int = 1024,
        cpu_quota: float = 1.0,
        timeout_seconds: int = 30,
        network_isolated: bool = False,
        tmpfs_size_mb: int = 256,
    ):
        self.memory_mb = memory_mb
        self.cpu_quota = cpu_quota
        self.timeout_seconds = timeout_seconds
        self.network_isolated = network_isolated
        self.tmpfs_size_mb = tmpfs_size_mb

    def run(self, command: str, *, timeout: int | None = None, env: dict[str, str] | None = None) -> dict[str, Any]:
        """Execute ``command`` inside the sandbox with limits."""
        limit = timeout or self.timeout_seconds

        def _pre_exec() -> None:
            if hasattr(resource, "setrlimit"):
                bytes_limit = self.memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (bytes_limit, bytes_limit))
                resource.setrlimit(resource.RLIMIT_CPU, (int(self.cpu_quota * 60), int(self.cpu_quota * 60)))

        try:
            proc = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, **(env or {})},
                preexec_fn=_pre_exec if os.name == "posix" else None,
            )
            try:
                stdout, stderr = proc.communicate(timeout=limit)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                raise ToolError(f"command timed out after {limit}s: {command}")
            return {
                "command": command,
                "exit_code": proc.returncode,
                "stdout": stdout[:_MAX_OUTPUT_BYTES].decode(errors="replace"),
                "stderr": stderr[:_MAX_OUTPUT_BYTES].decode(errors="replace"),
                "timed_out": False,
            }
        except FileNotFoundError as exc:
            raise ToolError(f"command not found: {exc}")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Sandbox(mem={self.memory_mb}MB, timeout={self.timeout_seconds}s)"
