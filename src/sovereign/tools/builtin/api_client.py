"""SOVEREIGN — outbound API client (allow-listed destinations only).

Uses httpx when available; falls back to urllib. Only hosts matching the
configured allow-list patterns are reachable — everything else is refused.
"""

from __future__ import annotations

import fnmatch
import json
from typing import Any
from urllib.parse import urlparse

from sovereign.utils.errors import ToolError

try:
    import httpx

    _HAS_HTTPX = True
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore[assignment]
    _HAS_HTTPX = False

_ALLOWLIST = ["https://router.huggingface.co/v1/**", "https://api.github.com/**"]


def _allowed(url: str) -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    return any(fnmatch.fnmatch(url, pattern) or base == pattern.replace("/**", "") for pattern in _ALLOWLIST)


def request(method: str = "GET", url: str = "", *, headers: dict[str, str] | None = None,
            body: Any = None, timeout: int = 30) -> dict[str, Any]:
    """Perform an allow-listed HTTP request."""
    if not _allowed(url):
        raise ToolError(f"URL not in allow-list: {url}")

    if _HAS_HTTPX:
        response = httpx.request(
            method.upper(), url, headers=headers or {}, json=body if body is not None else None,
            timeout=timeout,
        )
        return {"status": response.status_code, "headers": dict(response.headers),
                "body": response.text}
    # urllib fallback (GET only)
    import urllib.request

    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return {"status": resp.status, "body": resp.read().decode(errors="replace")}
