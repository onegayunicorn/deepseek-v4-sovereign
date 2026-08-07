"""SOVEREIGN — AES-256-GCM encryption helpers.

Uses ``cryptography`` when installed; otherwise raises :class:`SecurityError`
with a clear install hint (encryption is a hard requirement in production).
"""

from __future__ import annotations

import base64
import hashlib
import os
from typing import Any

from sovereign.utils.errors import SecurityError

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    _HAS_CRYPTO = True
except ImportError:  # pragma: no cover
    AESGCM = None  # type: ignore[assignment,misc]
    _HAS_CRYPTO = False

_KEY_LEN = 32  # AES-256
_NONCE_LEN = 12
_PBKDF2_ITERATIONS = 600_000


class EncryptionService:
    """Encrypt / decrypt payloads with AES-256-GCM.

    Keys are either a base64 32-byte value (``AES_KEY_B64``) or derived from
    a passphrase via PBKDF2-HMAC-SHA256.
    """

    def __init__(self, key: bytes | str | None = None, passphrase: str | None = None):
        if not _HAS_CRYPTO:
            raise SecurityError("cryptography package required: pip install cryptography")
        if key is not None:
            raw = base64.b64decode(key) if isinstance(key, str) else key
        elif passphrase:
            raw = hashlib.pbkdf2_hmac(
                "sha256", passphrase.encode(), b"sovereign.salt", _PBKDF2_ITERATIONS
            )
        else:
            raw = os.environ.get("AES_KEY_B64")
            if raw:
                raw = base64.b64decode(raw)
            else:
                raise SecurityError("no encryption key configured (AES_KEY_B64)")
        if len(raw) != _KEY_LEN:
            raise SecurityError(f"AES key must be {_KEY_LEN} bytes, got {len(raw)}")
        self._cipher = AESGCM(raw)  # type: ignore[union-attr]

    def encrypt(self, data: bytes | str) -> str:
        """Return base64(nonce || ciphertext || tag)."""
        plaintext = data.encode() if isinstance(data, str) else data
        nonce = os.urandom(_NONCE_LEN)
        sealed = self._cipher.encrypt(nonce, plaintext, None)  # type: ignore[union-attr]
        return base64.b64encode(nonce + sealed).decode()

    def decrypt(self, token: str) -> str:
        try:
            blob = base64.b64decode(token)
            nonce, sealed = blob[:_NONCE_LEN], blob[_NONCE_LEN:]
            return self._cipher.decrypt(nonce, sealed, None).decode()  # type: ignore[union-attr]
        except Exception as exc:  # noqa: BLE001
            raise SecurityError(f"decryption failed: {exc}")

    def encrypt_json(self, value: Any) -> str:
        import json

        return self.encrypt(json.dumps(value, ensure_ascii=False))

    def decrypt_json(self, token: str) -> Any:
        import json

        return json.loads(self.decrypt(token))
