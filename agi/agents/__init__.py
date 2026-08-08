"""AGI OMEGA specialized agents."""

from __future__ import annotations

from agi.agents.base import SpecializedAgent
from agi.agents.specialized import ALL_AGENT_CLASSES, __all__ as _agent_names

__all__ = ["SpecializedAgent", "ALL_AGENT_CLASSES", *_agent_names]
