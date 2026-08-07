"""Unit tests — tool sandbox and policy enforcement."""

from __future__ import annotations

import asyncio

from sovereign.tools.authorization import ToolAuthorization
from sovereign.tools.builtin.code_interpreter import run_code
from sovereign.tools.builtin.shell import run_shell
from sovereign.utils.errors import ToolError


def test_shell_allowlist():
    result = run_shell("echo hello")
    assert result["exit_code"] == 0
    assert "hello" in result["stdout"]

    try:
        run_shell("sudo rm -rf /")
        assert False, "blocked command ran"
    except ToolError:
        pass


def test_code_interpreter_blocked_import():
    result = run_code("import os\nprint('x')")
    assert result["ok"] is False
    assert "blocked" in result["error"]


def test_tool_authorization():
    auth = ToolAuthorization()
    assert auth.can_execute("admin", "shell")
    assert not auth.can_execute("viewer", "shell")


def test_ethics_guard():
    from sovereign.governance.ethics import EthicsGuard

    guard = EthicsGuard()
    assert guard.preflight(task_type="research")["allowed"]
