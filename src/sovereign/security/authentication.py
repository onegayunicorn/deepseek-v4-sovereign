"""SOVEREIGN — JWT (HS256) authentication, stdlib-only.

Compact JWT implementation (base64url header.payload.signature with
HMAC-SHA256) so the security core has zero hard dependencies.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from sovereign.utils.errors import SecurityError


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


class JWTService:
    def __init__(self, secret: str | None = None, algorithm: str = "HS256", ttl_minutes: int = 60):
        self.secret = (secret or os.environ.get("JWT_SECRET") or "").encode()
        if not self.secret:
            raise SecurityError("JWT_SECRET not configured")
        self.algorithm = algorithm
        self.ttl_minutes = ttl_minutes

    def _sign(self, header: str, payload: str) -> str:
        if self.algorithm != "HS256":
            raise SecurityError(f"unsupported algorithm: {self.algorithm}")
        signing_input = f"{header}.{payload}".encode()
        digest = hmac.new(self.secret, signing_input, hashlib.sha256).digest()
        return _b64url(digest)

    def issue(self, subject: str, claims: dict[str, Any] | None = None, ttl_minutes: int | None = None) -> str:
        now = int(time.time())
        ttl = ttl_minutes or self.ttl_minutes
        header = {"alg": self.algorithm, "typ": "JWT"}
        body = {
            "sub": subject,
            "iat": now,
            "exp": now + ttl * 60,
            **(claims or {}),
        }
        h = _b64url(json.dumps(header, separators=(",", ":")).encode())
        p = _b64url(json.dumps(body, separators=(",", ":")).encode())
        return f"{h}.{p}.{self._sign(h, p)}"

    def verify(self, token: str) -> dict[str, Any]:
        try:
            header_b64, payload_b64, signature = token.split(".")
            expected = self._sign(header_b64, payload_b64)
            if not hmac.compare_digest(signature, expected):
                raise SecurityError("invalid signature")
            payload = json.loads(_b64url_decode(payload_b64))
            if payload.get("exp", 0) < int(time.time()):
                raise SecurityError("token expired")
            return payload
        except SecurityError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise SecurityError(f"invalid token: {exc}")
