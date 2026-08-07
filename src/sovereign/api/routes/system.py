"""SOVEREIGN — system API endpoints (/api/v1/system + /health)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from sovereign.api.dependencies import get_orchestrator
from sovereign.utils.metrics import METRICS

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/health")
async def health(orchestrator: Any = Depends(get_orchestrator)):
    return await orchestrator.health()


@router.get("/metrics")
async def metrics():
    return METRICS.snapshot()


@router.get("/metrics/prometheus")
async def metrics_prometheus():
    from fastapi.responses import PlainTextResponse

    return PlainTextResponse(METRICS.export_prometheus())


@router.get("/info")
async def info():
    from sovereign import __brand__, __version__

    return {
        "service": "sovereign",
        "brand": __brand__,
        "version": __version__,
        "palette": {"background": "#0A0A10", "cyan": "#00E5FF", "mint": "#00FFCC"},
    }
