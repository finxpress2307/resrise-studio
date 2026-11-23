"""Structured logging for Resrise Studio automation scripts."""
import sys
from pathlib import Path
from typing import Optional
import structlog
from structlog.types import Processor

from .config import get_settings


def configure_logging(
    log_file: Optional[Path] = None,
    level: str = "INFO",
    json_output: bool = False,
) -> None:
    """Configure structlog with console and optional file output."""
    settings = get_settings()

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())
        )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to route through structlog
    import logging

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(
            logging.Formatter("%(message)s")
        )
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class ActivityLogger:
    """High-level activity logger for Instagram automation scripts."""

    def __init__(self, account: str, log_file: Optional[Path] = None):
        self.account = account
        self.logger = get_logger(f"resrise.{account}")
        self._log_file = log_file

        if log_file:
            self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Ensure log file exists and is writable."""
        self._log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, **kwargs) -> None:
        """Log an activity message with account context."""
        self.logger.info(message, account=self.account, **kwargs)
        if self._log_file:
            self._write_to_file(message)

    def _write_to_file(self, message: str) -> None:
        """Write to activity log file."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [@{self.account}] {message}\n"
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(log_msg)
        except Exception as e:
            self.logger.error("Failed to write activity log", error=str(e))

    def debug(self, message: str, **kwargs) -> None:
        self.logger.debug(message, account=self.account, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self.logger.warning(message, account=self.account, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self.logger.error(message, account=self.account, **kwargs)

    def success(self, message: str, **kwargs) -> None:
        self.logger.info(message, account=self.account, status="success", **kwargs)