import logging
import json
import time
from datetime import datetime, timezone
from typing import Any, Dict


class StructuredJSONFormatter(logging.Formatter):
    """
    Production-safe JSON log formatter with sensitive data redaction.
    """

    SENSITIVE_KEYS = {
        "password", "token", "access_token", "secret", "secret_key",
        "api_key", "gemini_api_key", "authorization", "cookie"
    }

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for k, v in data.items():
            if isinstance(k, str) and k.lower() in self.SENSITIVE_KEYS:
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include custom extra fields if attached to log record
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_entry["extra"] = self._sanitize_dict(record.extra)

        if hasattr(record, "request_id"):
            log_entry["request_id"] = getattr(record, "request_id")

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


def setup_logging(level: int = logging.INFO):
    """Setup root logger with StructuredJSONFormatter."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredJSONFormatter())
        root_logger.addHandler(handler)
