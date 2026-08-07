"""SOVEREIGN — secrets access facade.

Uniform ``get(name)`` across environment and keyring backends. ``vault``
backend is a documented extension point (HashiCorp Vault client would plug
in here).
"""

from __future__ import annotations

import os

from sovereign.security.keyring import Keyring
from sovereign.utils.errors import SecurityError


class Secrets:
    def __init__(self, backend: str = "file"):
        self.backend = backend
        self._keyring = Keyring(backend=backend if backend != "env" else "env")

    def get(self, name: str, default: str | None = None) -> str | None:
        if self.backend == "vault":
            raise SecurityError(
                "vault backend not wired — add hvac client in security/secrets.py"
            )
        return self._keyring.get(name, default)

    def require(self, name: str) -> str:
        value = self.get(name)
        if value is None:
            raise SecurityError(f"missing secret: {name}")
        return value
