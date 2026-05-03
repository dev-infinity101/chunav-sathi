import json
import logging
import sys
from datetime import datetime, timezone


class _StructuredJSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra"):
            entry.update(record.extra)  # type: ignore[arg-type]
        return json.dumps(entry, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_StructuredJSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def configure_root_logger() -> None:
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_StructuredJSONFormatter())
        root.addHandler(handler)
        root.setLevel(logging.INFO)
