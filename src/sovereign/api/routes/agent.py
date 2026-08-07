"""SOVEREIGN — agent management API endpoints (/api/v1/agents)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from sovereign.api.dependencies import get_orchestrator
from sovereign.api.schemas import AgentStatus

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.get("/", response_model=list[AgentStatus])
async def list_agents(orchestrator: Any = Depends(get_orchestrator)):
    return await orchestrator.list_agents()


@router.get("/{agent_id}", response_model=AgentStatus)
async def get_agent(agent_id: str, orchestrator: Any = Depends(get_orchestrator)):
    agent = await orchestrator.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/{agent_id}/restart")
async def restart_agent(agent_id: str, orchestrator: Any = Depends(get_orchestrator)):
    success = await orchestrator.restart_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "restarted", "agent_id": agent_id}
