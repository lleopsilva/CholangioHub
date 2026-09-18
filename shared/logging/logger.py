import logging
import sys
from datetime import UTC, datetime
from typing import Any, cast

_json: Any = None
try:
    import json as _json
except ImportError:  # pragma: no cover - json is stdlib, always available
    _json = None


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON.

    Keeps a small, fixed set of fields so logs are easy to grep/parse in
    aggregation tools (CloudWatch, Loki, etc.) without extra config.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(extra)

        return cast(str, _json.dumps(payload, default=str))


def get_logger(name: str, *, level: int = logging.INFO) -> logging.Logger:
    """Return a logger configured to emit structured JSON to stdout.

    Safe to call repeatedly (e.g. once per module) — handlers are only
    attached once per logger name.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger


def log_with_fields(logger: logging.Logger, level: int, message: str, **fields: Any) -> None:
    """Log a message with extra structured fields, e.g.

    log_with_fields(logger, logging.INFO, "ingestion finished", records=42, source="pubmed")
    """
    logger.log(level, message, extra={"extra_fields": fields})
