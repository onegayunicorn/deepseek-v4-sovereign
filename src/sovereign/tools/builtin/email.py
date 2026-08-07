"""SOVEREIGN — email tool (disabled by default).

SMTP sending with TLS; requires a configured SMTP server in tools.yaml.
"""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Any

from sovereign.utils.errors import ToolError


def send_email(to: str, subject: str, body: str, *, smtp_server: str = "",
               smtp_port: int = 587, from_address: str = "", username: str = "",
               password: str = "") -> dict[str, Any]:
    """Send an email via SMTP (TLS)."""
    if not smtp_server or not from_address:
        raise ToolError("email tool disabled: SMTP server not configured in tools.yaml")
    if not to or not subject:
        raise ToolError("to and subject are required")

    msg = EmailMessage()
    msg["From"] = from_address
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
        server.starttls()
        if username:
            server.login(username, password)
        server.send_message(msg)
    return {"sent": True, "to": to, "subject": subject}
