"""SOVEREIGN — retry decorators (sync + async) with exponential backoff."""

from __future__ import annotations

import asyncio
import functools
import logging
import random
import time
from typing import Any, Callable, TypeVar

from sovereign.utils.logging import get_logger

T = TypeVar("T")
logger = get_logger("retry")


def _sleep(seconds: float) -> None:
    time.sleep(seconds)


async def _asleep(seconds: float) -> None:
    await asyncio.sleep(seconds)


def retry(
    attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Callable[[int, Exception], None] | None = None,
) -> Callable:
    """Retry a sync or async callable with exponential backoff."""

    def deco(fn: Callable[..., T]) -> Callable[..., T]:
        is_async = asyncio.iscoroutinefunction(fn)

        @functools.wraps(fn)
        async def _async_wrapper(*args: Any, **kwargs: Any) -> T:
            last: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return await fn(*args, **kwargs)  # type: ignore[misc]
                except exceptions as exc:  # noqa: PERF203
                    last = exc
                    if attempt >= attempts:
                        break
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    if jitter:
                        delay *= random.uniform(0.5, 1.5)
                    if on_retry:
                        on_retry(attempt, exc)
                    logger.warning("retry %s/%s in %.1fs: %s", attempt, attempts, delay, exc)
                    await _asleep(delay)
            assert last is not None
            raise last

        @functools.wraps(fn)
        def _sync_wrapper(*args: Any, **kwargs: Any) -> T:
            last: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:  # noqa: PERF203
                    last = exc
                    if attempt >= attempts:
                        break
                    delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                    if jitter:
                        delay *= random.uniform(0.5, 1.5)
                    if on_retry:
                        on_retry(attempt, exc)
                    logger.warning("retry %s/%s in %.1fs: %s", attempt, attempts, delay, exc)
                    _sleep(delay)
            assert last is not None
            raise last

        return _async_wrapper if is_async else _sync_wrapper  # type: ignore[return-value]

    return deco
