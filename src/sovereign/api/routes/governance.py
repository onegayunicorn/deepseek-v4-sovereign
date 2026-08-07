"""SOVEREIGN — governance endpoints (/api/v1/governance)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from sovereign.api.dependencies import get_orchestrator
from sovereign.governance.compliance import ComplianceEngine
from sovereign.governance.permissions import PermissionEngine

router = APIRouter(prefix="/api/v1/governance", tags=["governance"])


@router.get("/audit")
async def audit_trail(limit: int = 50, orchestrator: Any = Depends(get_orchestrator)):
    return {"records": orchestrator.audit_logger.tail(limit)}


@router.get("/audit/export")
async def audit_export(fmt: str = "jsonl", orchestrator: Any = Depends(get_orchestrator)):
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(orchestrator.audit_logger.export(fmt))


@router.get("/roles")
async def roles():
    engine = PermissionEngine()
    return {"roles": engine.roles_list(),
            "permissions": {r: engine.permissions_for(r) for r in engine.roles_list()}}


@router.get("/compliance")
async def compliance(orchestrator: Any = Depends(get_orchestrator)):
    engine = ComplianceEngine()
    report = engine.audit(
        memory_stats=await orchestrator.memory_manager.get_stats(),
        retention={"retention_days": 30},
        tls_enabled=True,
        encryption_enabled=True,
    )
    return report.to_dict()
