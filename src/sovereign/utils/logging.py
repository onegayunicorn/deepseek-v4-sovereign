"""SOVEREIGN — structured logging with sensitive-data redaction.

Emits JSON lines when ``format == "json"`` (see config/logging.yaml) and
redacts configured patterns (api_key, token, password, ...) before writing.
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import threading
from pathlib import Path

_REDACT = "***REDACTED***"

_DEFAULT_PATTERNS = ("api_key", "secret", "password", "token", "authorization", "hf_")


class _RedactingFormatter(logging.Formatter):
    def __init__(self, fmt: str, patterns: tuple[str, ...] = _DEFAULT_PATTERNS):
        super().__init__(fmt)
        self._exprs = [re.compile(p, re.IGNORECASE) for p in patterns]

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for expr in self._exprs:
            msg = expr.sub(_REDACT, msg)
        return msg


class _JsonFormatter(_RedactingFormatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "thread": threading.current_thread().name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        for expr in self._exprs:
            for key in list(payload):
                payload[key] = expr.sub(_REDACT, str(payload[key]))
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    fmt: str = "json",
    log_dir: str | Path | None = None,
    redaction_patterns: tuple[str, ...] = _DEFAULT_PATTERNS,
) -> logging.Logger:
    """Configure the root ``sovereign`` logger. Idempotent."""
    logger = logging.getLogger("sovereign")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False

    console = logging.StreamHandler(sys.stdout)
    if fmt == "json":
        console.setFormatter(_JsonFormatter("%(message)s", redaction_patterns))
    else:
        console.setFormatter(_RedactingFormatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s", redaction_patterns))
    logger.addHandler(console)

    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(Path(log_dir) / "orchestrator.log", encoding="utf-8")
        fh.setFormatter(_JsonFormatter("%(message)s", redaction_patterns))
        logger.addHandler(fh)

    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"sovereign.{name}")


def configure_from_env() -> logging.Logger:
    """Convenience: read LOG_LEVEL / LOG_DIR from environment."""
    return setup_logging(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        log_dir=os.environ.get("LOG_DIR"),
    )
