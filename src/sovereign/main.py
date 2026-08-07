"""SOVEREIGN orchestrator entry point: FastAPI application + CLI.

Run the API server::

    uvicorn sovereign.main:app --host 0.0.0.0 --port 8000

or via the CLI::

    python -m sovereign.main dashboard
    python -m sovereign.main status

This module is the PyInstaller entry script referenced by
``builds/exe/sovereign.spec``.
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

import typer
from fastapi import FastAPI, WebSocket

from sovereign import __brand__, __version__
from sovereign.api.dependencies import init_container
from sovereign.api.middleware import (
    AuthMiddleware,
    request_logging_middleware,
    sovereign_error_handler,
)
from sovereign.api.routes import agent, governance, knowledge, memory, system, task, tools
from sovereign.api.websocket import EventStreamManager
from sovereign.config import Config
from sovereign.governance.audit_logger import AuditLogger
from sovereign.hardware import HardwareManager
from sovereign.jobs import JobManager
from sovereign.knowledge.knowledge_base import KnowledgeBase
from sovereign.memory.memory_manager import MemoryManager
from sovereign.orchestrator.core import SovereignOrchestrator
from sovereign.security.authentication import JWTService
from sovereign.tools.executor import ToolExecutor
from sovereign.tools.registry import ToolRegistry
from sovereign.utils.errors import SovereignError
from sovereign.utils.logging import get_logger
from sovereign.webhooks import WebhookManager

logger = get_logger("main")

# ── Application wiring ───────────────────────────────────────────────────
try:
    CONFIG = Config.load()
except Exception as exc:  # noqa: BLE001
    logger.warning("config load failed (%s) — using empty config", exc)
    CONFIG = Config({})

AUDIT = AuditLogger(path="logs/audits/audit.jsonl")
MEMORY = MemoryManager()
TOOLS = ToolRegistry(config=CONFIG.section("tools"))
EXECUTOR = ToolExecutor(TOOLS, audit=AUDIT)
JOBS = JobManager()
WEBHOOKS = WebhookManager()
HARDWARE = HardwareManager()
KNOWLEDGE = KnowledgeBase()
ORCHESTRATOR = SovereignOrchestrator(
    config={
        **CONFIG.section("orchestrator"),
        "routing": CONFIG.section("routing") if CONFIG.get("routing") else {},
    },
    event_bus=None,
    memory_manager=MEMORY,
    tool_registry=TOOLS,
    audit_logger=AUDIT,
)
JWT = JWTService(ttl_minutes=60)

init_container(
    orchestrator=ORCHESTRATOR,
    memory=MEMORY,
    executor=EXECUTOR,
    tools=TOOLS,
    knowledge=KNOWLEDGE,
    jobs=JOBS,
    webhooks=WEBHOOKS,
    hardware=HARDWARE,
)

# ── FastAPI app ──────────────────────────────────────────────────────────
app = FastAPI(
    title="Sovereign Orchestrator",
    version=__version__,
    description="SOVEREIGN — self-sovereign AI orchestration API",
    lifespan=None,
)
app.add_exception_handler(SovereignError, sovereign_error_handler)  # type: ignore[arg-type]
app.middleware("http")(request_logging_middleware)

for router in (task.router, agent.router, memory.router, system.router,
               tools.router, knowledge.router, governance.router):
    app.include_router(router)

WS_MANAGER = EventStreamManager(ORCHESTRATOR.event_bus)


@app.on_event("startup")
async def _startup() -> None:
    await ORCHESTRATOR.start()
    asyncio.create_task(WS_MANAGER.run())


@app.on_event("shutdown")
async def _shutdown() -> None:
    await ORCHESTRATOR.stop()


@app.get("/")
def index() -> dict[str, Any]:
    """Service banner exposing the brand and palette."""
    return {
        "service": "sovereign",
        "brand": __brand__,
        "version": __version__,
        "palette": {"background": "#0A0A10", "cyan": "#00E5FF", "mint": "#00FFCC"},
    }


@app.get("/health")
async def health() -> dict[str, Any]:
    """Liveness probe used by load balancers and smoke tests."""
    return await ORCHESTRATOR.health()


@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket) -> None:
    await WS_MANAGER.connect(websocket)


# ── Auxiliary endpoints (jobs / webhooks / hardware / integrations) ──────
from fastapi import Request  # noqa: E402
from pydantic import BaseModel  # noqa: E402


class JobIn(BaseModel):
    name: str
    kind: str
    params: dict[str, Any] | None = None


class WebhookIn(BaseModel):
    source: str
    event: str = ""
    payload: dict[str, Any] = {}


@app.get("/api/v1/jobs")
async def list_jobs() -> dict[str, Any]:
    return {"jobs": await JOBS.list()}


@app.post("/api/v1/jobs")
async def create_job(body: JobIn) -> dict[str, Any]:
    job_id = await JOBS.submit(body.name, body.kind, body.params)
    return {"job_id": job_id, "status": "submitted"}


@app.post("/api/v1/webhooks/{source}")
async def receive_webhook(source: str, body: WebhookIn) -> dict[str, Any]:
    return await WEBHOOKS.receive(source, body.event, body.payload)


@app.get("/api/v1/webhooks")
async def list_webhooks() -> dict[str, Any]:
    return {"webhooks": WEBHOOKS.list()}


@app.get("/api/v1/hardware")
async def hardware_status() -> dict[str, Any]:
    return await HARDWARE.status()


@app.get("/api/v1/integrations")
async def integrations() -> dict[str, Any]:
    import subprocess

    result = subprocess.run(
        [sys.executable, "integrations/connector.py", "--json"],
        capture_output=True, text=True, timeout=30,
    )
    try:
        import json as _json

        return _json.loads(result.stdout)
    except Exception:  # noqa: BLE001
        return {"error": result.stderr or "connector unavailable"}


# ── CLI ──────────────────────────────────────────────────────────────────
cli = typer.Typer(
    name="sovereign",
    help="SOVEREIGN — self-sovereign AI orchestration CLI.",
    no_args_is_help=True,
)


@cli.command()
def dashboard(
    host: str = typer.Option("0.0.0.0", help="Bind host for the dashboard."),
    port: int = typer.Option(8000, help="Bind port for the dashboard."),
) -> None:
    """Serve the Sovereign orchestrator dashboard (FastAPI + uvicorn)."""
    import uvicorn

    uvicorn.run(app, host=host, port=port)


@cli.command()
def status() -> None:
    """Print orchestrator + hardware + integration status."""
    import json

    async def _status() -> None:
        health = await ORCHESTRATOR.health()
        print(json.dumps({
            "brand": __brand__,
            "version": __version__,
            "orchestrator": health,
            "hardware": await HARDWARE.status(),
            "jobs": await JOBS.list(),
            "webhooks": WEBHOOKS.list(),
        }, indent=2, default=str))

    asyncio.run(_status())


@cli.command()
def submit(
    task_type: str = typer.Argument(..., help="Task type: reason|code|search|plan|execute|coordinate"),
    input_text: str = typer.Argument(..., help="Task input text"),
) -> None:
    """Submit a task to the orchestrator and print its id."""

    async def _submit() -> None:
        await ORCHESTRATOR.start()
        task_id = await ORCHESTRATOR.submit_task(
            task_type, {"input": input_text}, priority=5
        )
        print(f"task_id: {task_id}")
        await ORCHESTRATOR.stop()

    asyncio.run(_submit())


@cli.command()
def mcp() -> None:
    """Serve the sovereign tools over MCP stdio transport."""
    from sovereign.communication.protocols.mcp import MCPStdioServer

    MCPStdioServer(TOOLS).serve_forever()


if __name__ == "__main__":
    cli()
