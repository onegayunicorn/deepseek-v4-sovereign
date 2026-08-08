"""SOVEREIGN — AGI OMEGA module.

Top-level ``agi`` package per the PDF activation spec::

    from agi.omega_v3.orchestrator import AGIOMEGA
    from agi.agents.specialized import (
        ReasonerAgent, CoordinatorAgent, ...  # 42 agents
    )

``AGIOMEGA`` deploys 42 specialized agents plus 2,650 worker bots and
convenes the Council of 10.
"""

from __future__ import annotations

from agi.omega_v3.council_of_10 import CouncilOf10
from agi.omega_v3.orchestrator import AGIOMEGA, agi

__all__ = ["AGIOMEGA", "CouncilOf10", "agi"]
