"""SOVEREIGN — TLS / mTLS configuration helpers."""

from __future__ import annotations

import os
import ssl
from pathlib import Path
from typing import Any


def build_ssl_context(
    cert_file: str | None = None,
    key_file: str | None = None,
    ca_file: str | None = None,
    *,
    verify_client: bool = False,
) -> ssl.SSLContext:
    """Build a server/client SSL context from PEM paths (or env defaults)."""
    cert = cert_file or os.environ.get("SOVEREIGN_TLS_CERT")
    key = key_file or os.environ.get("SOVEREIGN_TLS_KEY")
    ca = ca_file or os.environ.get("SOVEREIGN_TLS_CA")

    purpose = ssl.Purpose.CLIENT_AUTH if verify_client else ssl.Purpose.SERVER_AUTH
    context = ssl.create_default_context(purpose)

    if verify_client:
        context.verify_mode = ssl.CERT_REQUIRED
        if ca:
            context.load_verify_locations(cafile=ca)
    elif ca:
        context.load_verify_locations(cafile=ca)
    else:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    if cert and key:
        context.load_cert_chain(certfile=cert, keyfile=key)

    return context


def ssl_config_from_yaml(config: dict[str, Any]) -> dict[str, Any]:
    """Translate config/security.yaml ssl block into uvicorn kwargs."""
    block = config.get("ssl", {}) if isinstance(config, dict) else {}
    if not block.get("enabled", False):
        return {}
    return {
        "ssl_keyfile": block.get("key_file"),
        "ssl_certfile": block.get("cert_file"),
        "ssl_ca_certs": block.get("ca_file"),
    }
