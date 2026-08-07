"""SOVEREIGN — API middleware (auth, request logging, error mapping)."""

from __future__ import annotations

import time
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from sovereign.utils.errors import SovereignError
from sovereign.utils.logging import get_logger
from sovereign.utils.metrics import METRICS

logger = get_logger("api.middleware")


async def sovereign_error_handler(request: Request, exc: SovereignError) -> JSONResponse:
    status_codes = {
        "not_found": 404,
        "validation.error": 422,
        "security.error": 403,
        "tool.error": 400,
        "task.error": 400,
    }
    status = status_codes.get(exc.code, 500)
    return JSONResponse(status_code=status, content=exc.to_dict())


async def request_logging_middleware(request: Request, call_next: Any) -> Any:
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = int((time.perf_counter() - started) * 1000)
    METRICS.incr("http_requests", labels={"path": request.url.path})
    logger.info("%s %s -> %s (%sms)", request.method, request.url.path,
                response.status_code, duration_ms)
    response.headers["X-Sovereign-Trace"] = f"{request.method}:{request.url.path}"
    return response


class AuthMiddleware:
    """Bearer-token guard for non-public routes (enabled when configured)."""

    def __init__(self, jwt_service: Any | None = None, enabled: bool = False):
        self.jwt = jwt_service
        self.enabled = enabled

    async def __call__(self, request: Request, call_next: Any) -> Any:
        if not self.enabled or request.url.path in ("/health", "/", "/docs", "/openapi.json"):
            return await call_next(request)
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"code": "security.error", "message": "missing bearer token"})
        try:
            payload = self.jwt.verify(auth[7:]) if self.jwt else {"sub": "anon"}
            request.state.user = payload.get("sub", "anon")
            request.state.role = payload.get("role", "user")
        except Exception as exc:  # noqa: BLE001
            return JSONResponse(status_code=401, content={"code": "security.error", "message": str(exc)})
        return await call_next(request)
