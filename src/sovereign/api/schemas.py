"""SOVEREIGN — Pydantic schemas for the API layer."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    type: str = Field(..., description="Task type: reason|code|search|plan|execute|coordinate|tts|memory")
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(5, ge=1, le=10)
    max_retries: int = Field(3, ge=0, le=10)


class TaskOut(BaseModel):
    id: str
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    priority: int
    status: str
    retry_count: int
    max_retries: int
    created_at: datetime
    completed_at: datetime | None = None
    error: str | None = None
    result: Any = None


class AgentStatus(BaseModel):
    id: str
    name: str
    kind: str
    state: str
    last_active: datetime | None = None
    capabilities: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)


class MemoryStoreRequest(BaseModel):
    memory_type: str
    key: str
    value: Any
    metadata: dict[str, Any] | None = None


class MemorySearchRequest(BaseModel):
    query: str
    memory_types: list[str] | None = None
    k: int = Field(10, ge=1, le=100)


class ToolExecuteRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    role: str = Field("operator", description="role for permission checks")


class WebhookIn(BaseModel):
    source: str = Field(..., description="github | huggingface | generic")
    event: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class JobCreate(BaseModel):
    name: str
    kind: str = Field(..., description="train | index | tts | migrate | build")
    params: dict[str, Any] = Field(default_factory=dict)
