"""Unit tests for the AGI OMEGA module."""

from __future__ import annotations

import unittest

from agi.agents.specialized import ALL_AGENT_CLASSES
from agi.omega_v3.council_of_10 import CouncilOf10
from agi.omega_v3.orchestrator import AGIOMEGA


class TestAGIOMEGA(unittest.TestCase):
    def test_orchestrator_deploys_42_agents(self) -> None:
        agi = AGIOMEGA()
        agi.initialize()
        self.assertEqual(agi.agent_count(), 42)
        self.assertEqual(agi.deployed_count(), 42)

    def test_2650_bots(self) -> None:
        agi = AGIOMEGA()
        agi.initialize()
        self.assertEqual(agi.bot_count(), 2650)

    def test_council_of_10(self) -> None:
        council = CouncilOf10()
        names = [
            "Nexus", "Sage", "Chronos", "Aurora", "Ember",
            "Sol", "Tide", "Veil", "Verdant", "Forge",
        ]
        for name in names:
            council.seat(name)
        result = council.convene()
        self.assertTrue(result["all_aligned"])
        self.assertEqual(len(result["names"]), 10)

    def test_agent_classes_enumerable(self) -> None:
        self.assertEqual(len(ALL_AGENT_CLASSES), 42)


if __name__ == "__main__":
    unittest.main()
