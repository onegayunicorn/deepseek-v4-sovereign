"""The 42 specialized AGI OMEGA agents (PDF activation list).

Exact classes required by the PDF spec activation sequence::

    from agi.agents.specialized import *

    agents = [ReasonerAgent(), CoordinatorAgent(), ..., AgentFactoryAgent()]
    for agent in agents:
        agent.deploy()
"""

from __future__ import annotations

from typing import List, Type

from agi.agents.base import SpecializedAgent

# ── Core cognition ────────────────────────────────────────────────────
class ReasonerAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="reasoner", role="deep reasoning", capabilities=["reasoning", "logic"])


class CoordinatorAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="coordinator", role="task coordination", capabilities=["coordination"])


class SupervisorAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="supervisor", role="supervision", capabilities=["oversight"])


class ToolAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="tool", role="tool dispatch", capabilities=["tools"])


class MemoryAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="memory", role="memory management", capabilities=["memory"])


class KnowledgeAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="knowledge", role="knowledge base", capabilities=["knowledge"])


class SecurityAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="security", role="security", capabilities=["security", "sandbox"])


class GovernanceAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="governance", role="governance", capabilities=["governance"])


class AuditAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="audit", role="audit logging", capabilities=["audit"])


class ComplianceAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="compliance", role="compliance", capabilities=["compliance"])


# ── Domain agents ─────────────────────────────────────────────────────
class QuantumAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="quantum", role="quantum entanglement", capabilities=["quantum"])


class NeuralAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="neural", role="neural interface", capabilities=["neural", "bci"])


class GenomicAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="genomic", role="genomics", capabilities=["genomics"])


class ForensicAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="forensic", role="forensics", capabilities=["forensics"])


class MedicalAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="medical", role="medical", capabilities=["medical"])


class IoTAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="iot", role="iot devices", capabilities=["iot"])


class MobileAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="mobile", role="mobile", capabilities=["mobile"])


class WebAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="web", role="web", capabilities=["web"])


class SearchAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="search", role="search", capabilities=["search"])


class DatabaseAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="database", role="database", capabilities=["database"])


class FileAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="file", role="file ops", capabilities=["file_ops"])


class EmailAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="email", role="email", capabilities=["email"])


class DNAAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="dna", role="dna resonance", capabilities=["dna", "bio"])


class UniversalDriverAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="universal_driver", role="hardware abstraction", capabilities=["hardware"])


class PlasmaAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="plasma", role="plasma interface", capabilities=["plasma"])


class SimAIAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="sim_ai", role="simulation", capabilities=["simulation"])


class BrowserRelayAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="browser_relay", role="browser relay", capabilities=["browser"])


class A17Agent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="a17", role="samsung a17", capabilities=["mobile", "hardware"])


class TeslaAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="tesla", role="tesla nexus", capabilities=["tesla"])


class AnsysAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="ansys", role="engineering simulation", capabilities=["ansys"])


class HealthAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="health", role="health monitoring", capabilities=["health"])


class MetricsAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="metrics", role="metrics", capabilities=["metrics"])


class AlertAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="alert", role="alerting", capabilities=["alerting"])


class LoggerAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="logger", role="logging", capabilities=["logging"])


class TelemetryAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="telemetry", role="telemetry", capabilities=["telemetry"])


class BackupAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="backup", role="backup", capabilities=["backup"])


# ── Orchestration agents ──────────────────────────────────────────────
class OrchestratorAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="orchestrator", role="orchestration", capabilities=["orchestration"])


class SchedulerAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="scheduler", role="scheduling", capabilities=["scheduling"])


class StateMachineAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="state_machine", role="state machine", capabilities=["state_machine"])


class TaskQueueAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="task_queue", role="task queue", capabilities=["task_queue"])


class AgentFactoryAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(name="agent_factory", role="agent factory", capabilities=["factory"])


# ── Junction bridge (42nd agent, ecosystem-native) ────────────────────
class JunctionAgent(SpecializedAgent):
    def __init__(self) -> None:
        super().__init__(
            name="junction",
            role="cross-system bridge",
            capabilities=["bridge", "route", "translate"],
        )


# The full activation order from the PDF (41) + Junction (1) = 42.
ALL_AGENT_CLASSES: List[Type[SpecializedAgent]] = [
    ReasonerAgent,
    CoordinatorAgent,
    SupervisorAgent,
    ToolAgent,
    MemoryAgent,
    KnowledgeAgent,
    SecurityAgent,
    GovernanceAgent,
    AuditAgent,
    ComplianceAgent,
    QuantumAgent,
    NeuralAgent,
    GenomicAgent,
    ForensicAgent,
    MedicalAgent,
    IoTAgent,
    MobileAgent,
    WebAgent,
    SearchAgent,
    DatabaseAgent,
    FileAgent,
    EmailAgent,
    DNAAgent,
    UniversalDriverAgent,
    PlasmaAgent,
    SimAIAgent,
    BrowserRelayAgent,
    A17Agent,
    TeslaAgent,
    AnsysAgent,
    HealthAgent,
    MetricsAgent,
    AlertAgent,
    LoggerAgent,
    TelemetryAgent,
    BackupAgent,
    OrchestratorAgent,
    SchedulerAgent,
    StateMachineAgent,
    TaskQueueAgent,
    AgentFactoryAgent,
    JunctionAgent,
]

__all__ = [cls.__name__ for cls in ALL_AGENT_CLASSES] + ["ALL_AGENT_CLASSES"]
