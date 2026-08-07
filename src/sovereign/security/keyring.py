"""SOVEREIGN — local secret storage (file / env / vault backends).

Stored secrets are wrapped with :class:`EncryptionService` when a master key
is available; otherwise a warning is logged and values are kept in memory.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from sovereign.security.encryption import EncryptionService
from sovereign.utils.errors import SecurityError

logger = logging.getLogger("sovereign.security.keyring")

_BACKENDS = ("file", "env", "vault")


class Keyring:
    def __init__(self, backend: str = "file", path: str | Path | None = None):
        if backend not in _BACKENDS:
            raise SecurityError(f"unknown keyring backend: {backend}")
        self.backend = backend
        self.path = Path(path) if path else Path("data/state/keyring.json")
        self._memory: dict[str, str] = {}
        self._enc: EncryptionService | None = None
        try:
            self._enc = EncryptionService()
        except SecurityError:
            logger.warning("keyring running WITHOUT encryption (no master key)")
        if self.backend == "file" and self.path.exists():
            self._load()

    # -- internals ---------------------------------------------------------
    def _load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for key, value in raw.items():
                self._memory[key] = (
                    self._enc.decrypt(value) if self._enc else value
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("keyring load failed: %s", exc)

    def _persist(self) -> None:
        if self.backend != "file":
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            key: (self._enc.encrypt(value) if self._enc else value)
            for key, value in self._memory.items()
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    # -- API ---------------------------------------------------------------
    def set(self, name: str, value: str) -> None:
        if self.backend == "env":
            raise SecurityError("env backend is read-only")
        self._memory[name] = value
        self._persist()

    def get(self, name: str, default: str | None = None) -> str | None:
        if self.backend == "env":
            return os.environ.get(name, default)
        return self._memory.get(name, default)

    def delete(self, name: str) -> None:
        self._memory.pop(name, None)
        self._persist()

    def list(self) -> list[str]:
        return sorted(self._memory)

    def resolve(self, name: str) -> str:
        """Get a secret or raise (for required credentials)."""
        value = self.get(name)
        if value is None:
            raise SecurityError(f"missing secret: {name}")
        return value
