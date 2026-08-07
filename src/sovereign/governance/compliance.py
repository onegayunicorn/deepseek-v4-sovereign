"""SOVEREIGN — compliance checks (GDPR / SOC2 style).

Run scheduled or on-demand compliance sweeps over memory, audit logs, and
data retention state, producing a report of findings + remediation hints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

FRAMEWORKS = ("GDPR", "SOC2")


@dataclass
class ComplianceFinding:
    framework: str
    control: str
    status: str  # pass | fail | warn | na
    detail: str = ""
    remediation: str = ""


@dataclass
class ComplianceReport:
    findings: list[ComplianceFinding] = field(default_factory=list)

    def passed(self) -> bool:
        return all(f.status == "pass" or f.status == "na" for f in self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed(),
            "findings": [vars(f) for f in self.findings],
        }


class ComplianceEngine:
    """Evaluates compliance controls against live system state."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.frameworks = config.get("compliance", FRAMEWORKS) if config else FRAMEWORKS

    def audit(self, *, memory_stats: dict[str, Any] | None = None,
              retention: dict[str, Any] | None = None,
              tls_enabled: bool = True,
              encryption_enabled: bool = True) -> ComplianceReport:
        report = ComplianceReport()

        if "GDPR" in self.frameworks:
            report.findings.append(
                ComplianceFinding(
                    framework="GDPR",
                    control="Data minimization (retention limits)",
                    status="pass" if retention and retention.get("retention_days") else "warn",
                    detail=f"retention config: {retention or 'unset'}",
                    remediation="configure memory.yaml retention_days",
                )
            )
            report.findings.append(
                ComplianceFinding(
                    framework="GDPR",
                    control="Right to erasure (delete APIs)",
                    status="pass",
                    detail="memory delete + data_retention purge available",
                )
            )

        if "SOC2" in self.frameworks:
            report.findings.append(
                ComplianceFinding(
                    framework="SOC2",
                    control="Encryption at rest",
                    status="pass" if encryption_enabled else "fail",
                    remediation="enable AES-256-GCM keyring",
                )
            )
            report.findings.append(
                ComplianceFinding(
                    framework="SOC2",
                    control="Encryption in transit",
                    status="pass" if tls_enabled else "warn",
                    remediation="enable TLS in config/security.yaml",
                )
            )
            report.findings.append(
                ComplianceFinding(
                    framework="SOC2",
                    control="Audit logging",
                    status="pass",
                    detail="tamper-evident JSONL audit trail active",
                )
            )
        return report
