"""Council of 10 — the seated advisory council.

PDF activation API::

    council = CouncilOf10()
    members = ['Nexus', 'Sage', 'Chronos', 'Aurora', 'Ember',
               'Sol', 'Tide', 'Veil', 'Verdant', 'Forge']
    for member in members:
        council.seat(member)
    council.convene()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

COUNCIL_NAMES = [
    "Nexus",
    "Sage",
    "Chronos",
    "Aurora",
    "Ember",
    "Sol",
    "Tide",
    "Veil",
    "Verdant",
    "Forge",
]


@dataclass
class CouncilMember:
    name: str
    seated: bool = False
    aligned: bool = False
    vote: str = ""

    def seat(self) -> None:
        self.seated = True
        self.aligned = True


class CouncilOf10:
    """Seats and convenes the ten-member advisory council."""

    def __init__(self) -> None:
        self.members: List[CouncilMember] = []
        self.convened = False

    def seat(self, name: str) -> CouncilMember:
        member = CouncilMember(name=name)
        member.seat()
        self.members.append(member)
        return member

    def convene(self) -> Dict[str, object]:
        """Convene the council; returns the alignment summary."""
        if len(self.members) != 10:
            raise RuntimeError(f"Council requires 10 members, has {len(self.members)}")
        self.convened = True
        for member in self.members:
            member.vote = "aligned"
        return {
            "seated": len(self.members),
            "names": [m.name for m in self.members],
            "all_aligned": all(m.aligned for m in self.members),
            "convened": self.convened,
        }

    def summary(self) -> Dict[str, object]:
        return {
            "members": len(self.members),
            "names": [m.name for m in self.members],
            "convened": self.convened,
            "aligned": sum(1 for m in self.members if m.aligned),
        }
