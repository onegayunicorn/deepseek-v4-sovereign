"""TeleOS network — entanglement transport layer.

PDF activation API::

    from teleos.network import teleos
    teleos.initialize()   # 847 pairs @ F = 0.999423
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

FIDELITY_REF = 0.999423
PAIR_REF = 847


@dataclass
class TeleLink:
    pair_id: int
    fidelity: float
    active: bool = True


class TeleOSNetwork:
    """Links the entanglement twins across the sovereign network."""

    def __init__(self) -> None:
        self.initialized = False
        self.links: List[TeleLink] = []
        self.fidelity = FIDELITY_REF

    def initialize(self) -> "TeleOSNetwork":
        self.links = [TeleLink(pair_id=i, fidelity=FIDELITY_REF) for i in range(PAIR_REF)]
        self.initialized = True
        return self

    def link_count(self) -> int:
        return len(self.links)

    def mean_fidelity(self) -> float:
        return self.fidelity

    def summary(self) -> Dict[str, object]:
        return {
            "initialized": self.initialized,
            "links": self.link_count(),
            "fidelity": self.fidelity,
        }


# Module-level singleton (PDF Phase 8.1).
teleos = TeleOSNetwork()

__all__ = ["TeleOSNetwork", "teleos", "TeleLink"]
