"""SOVEREIGN — headless browser automation (disabled by default).

Optional integration point: wire a Playwright / Selenium controller here.
The default implementation refuses to run until a browser controller is
registered, keeping the surface explicit.
"""

from __future__ import annotations

from typing import Any, Callable

from sovereign.utils.errors import ToolError

_controller: Callable[..., Any] | None = None


def register_controller(fn: Callable[..., Any]) -> None:
    global _controller  # noqa: PLW0603
    _controller = fn


def browse(url: str, *, timeout: int = 60) -> dict[str, Any]:
    """Navigate to ``url`` with the registered headless controller."""
    if _controller is None:
        raise ToolError("browser tool disabled: no controller registered (see tools/builtin/browser.py)")
    return _controller(url=url, timeout=timeout)
