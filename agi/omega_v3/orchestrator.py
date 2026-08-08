"""AGI OMEGA orchestrator — deploys 42 agents + 2,650 bots.

PDF activation API::

    agi = AGIOMEGA()
    agi.initialize()

    from agi.agents.specialized import *
    agents = [ReasonerAgent(), ..., AgentFactoryAgent()]
    for agent in agents:
        agent.deploy()
    print('All 42 Agents Active')
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from agi.agents.base import SpecializedAgent
from agi.agents.specialized import ALL_AGENT_CLASSES
from agi.omega_v3.council_of_10 import COUNCIL_NAMES, CouncilOf10

BOT_COUNT = 2650  # PDF: "AGI OMEGA: 42 agents · 2,650 bots"


@dataclass
class OmegaBot:
    index: int
    role: str
    active: bool = False


class AGIOMEGA:
    """Self-contained sovereign orchestrator (zero external API)."""

    def __init__(self) -> None:
        self.initialized = False
        self.agents: List[SpecializedAgent] = []
        self.bots: List[OmegaBot] = []
        self.council = CouncilOf10()

    def initialize(self) -> "AGIOMEGA":
        """Deploy all 42 agents, spawn 2,650 bots, seat the council."""
        if self.initialized:
            return self
        self.agents = [cls() for cls in ALL_AGENT_CLASSES]
        for agent in self.agents:
            agent.deploy()
        self.bots = [OmegaBot(index=i, role="worker") for i in range(BOT_COUNT)]
        for bot in self.bots:
            bot.active = True
        for name in COUNCIL_NAMES:
            self.council.seat(name)
        self.council.convene()
        self.initialized = True
        return self

    # ── introspection ─────────────────────────────────────────────────
    def agent_count(self) -> int:
        return len(self.agents)

    def bot_count(self) -> int:
        return len(self.bots)

    def agent_names(self) -> List[str]:
        return [a.name for a in self.agents]

    def deployed_count(self) -> int:
        return sum(1 for a in self.agents if a.deployed)

    def summary(self) -> Dict[str, object]:
        return {
            "initialized": self.initialized,
            "agents": self.agent_count(),
            "agents_deployed": self.deployed_count(),
            "bots": self.bot_count(),
            "council": self.council.summary(),
        }


# Module-level singleton (PDF Phase 8.1 uses ``from agi.omega_v3.orchestrator import agi``).
agi = AGIOMEGA()

__all__ = ["AGIOMEGA", "agi", "OmegaBot"]
