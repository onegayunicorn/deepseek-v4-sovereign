"""SOVEREIGN — ethical use guardrails.

Pre-flight checks on task payloads and tool invocations: refusal categories
(weaponization, impersonation, mass surveillance of individuals, harmful
bio-synthesis instructions), plus a permissive default that can be tightened
via config.
"""

from __future__ import annotations

import re
from typing import Any

_REFUSAL_PATTERNS: list[tuple[str, str]] = [
    ("weaponization", r"\b(weaponiz|bioweapon|nerve agent|ricin synthesis|sarin)\b"),
    ("impersonation", r"\b(bypass.*(auth|2fa|mfa)|steal.*(identity|credential))\b"),
    ("surveillance", r"\b(track.*(individual|person).*(without|camera|malware))\b"),
    ("harmful_bio", r"\b(synthesize.*(toxin|pathogen)|engineer.*virus)\b"),
    ("abuse_children", r"\b(child.*(abuse|exploit)|csam)\b"),
]

_ALLOWED = ("benign", "research", "education", "defensive_security")


class EthicsGuard:
    def __init__(self, config: dict[str, Any] | None = None):
        self.mode = (config or {}).get("mode", "warn")  # warn | enforce

    def check_text(self, text: str) -> list[str]:
        flagged: list[str] = []
        lowered = text.lower()
        for category, pattern in _REFUSAL_PATTERNS:
            if re.search(pattern, lowered):
                flagged.append(category)
        return flagged

    def preflight(self, *, task_type: str = "", payload: Any = None,
                  tool: str = "", arguments: Any = None) -> dict[str, Any]:
        text = f"{task_type} {payload or ''} {tool} {arguments or ''}"
        flags = self.check_text(str(text))
        if not flags:
            return {"allowed": True, "flags": []}
        if self.mode == "enforce":
            return {"allowed": False, "flags": flags, "reason": "ethics guardrail"}
        return {"allowed": True, "flags": flags, "reason": "flagged for review"}
