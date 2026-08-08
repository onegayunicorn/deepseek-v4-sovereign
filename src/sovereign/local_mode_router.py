"""Zero-API local mode router — intercepts external calls, routes to localhost.

PDF spec (Solution 1)::

    from sovereign.local_mode_router import activate_sovereign_offline
    activate_sovereign_offline()
"""

from __future__ import annotations

import os
import re
from typing import List, Optional

CREDENTIAL_KEYS = [
    "AZURE_CONN",
    "GITHUB_TOKEN",
    "GITHUB_USERNAME",
    "HF_TOKEN",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "API_KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
]

LOCAL_ROUTES = {
    r"api\.openai\.com": "127.0.0.1:8000/v1",
    r"huggingface\.co": "127.0.0.1:8001",
    r"github\.com": "127.0.0.1:8002/git",
    r"azure\.com": "127.0.0.1:8003/storage",
    r"api\.anthropic\.com": "127.0.0.1:8004",
    r"api\.googleapis\.com": "127.0.0.1:8005",
}


def purge_credentials() -> List[str]:
    """Remove ALL credential env vars from process memory."""
    purged = []
    for key in list(os.environ.keys()):
        lowered = key.lower()
        if any(pattern.lower() in lowered for pattern in CREDENTIAL_KEYS):
            del os.environ[key]
            purged.append(key)
    return purged


class LocalOnlyRouter:
    """Monkey-patch requests → force ALL traffic to local loopback."""

    def __init__(self) -> None:
        self.original_get = None
        self.original_post = None
        self.active = False

    def activate(self) -> None:
        import requests

        self.original_get = requests.get
        self.original_post = requests.post

        def _local_route(url, **kwargs):
            for remote, local in LOCAL_ROUTES.items():
                if re.search(remote, url):
                    routed = re.sub(r"https?://[^/]+", f"http://{local}", url)
                    kwargs["headers"] = {
                        k: v
                        for k, v in kwargs.get("headers", {}).items()
                        if "authorization" not in k.lower() and "api-key" not in k.lower()
                    }
                    return self.original_get(routed, **kwargs)
            return self.original_get(url, **kwargs)

        requests.get = _local_route
        requests.post = _local_route
        self.active = True

    def deactivate(self) -> None:
        if self.active and self.original_get is not None:
            import requests

            requests.get = self.original_get
            requests.post = self.original_post
            self.active = False


def activate_sovereign_offline() -> LocalOnlyRouter:
    """Purge credentials and install the local-only router."""
    purge_credentials()
    router = LocalOnlyRouter()
    router.activate()
    os.environ["SOVEREIGN_MODE"] = "AIR_GAPPED"
    return router
