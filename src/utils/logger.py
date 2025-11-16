"""
Advanced Logging System for Master Orchestrator

Provides comprehensive logging with file rotation, structured logging,
and performance tracking for the viral YouTube synthesis system.

Author: AI Research Team
Date: November 2025
Version: 1.0.0
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager
import time


class StructuredLogger:
    """
    Advanced structured logger with file rotation and performance tracking.

    Features:
    - Structured JSON logging for machine parsing
    - File rotation to manage log size
    - Performance tracking for operations
    - Context-aware logging
    - Multiple log levels and handlers
    """

    def __init__(
        self,
        name: str,
        log_dir: Optional[Path] = None,
        log_level: str = "INFO",
        enable_file_logging: bool = True,
        enable_console_logging: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize the structured logger.

        Args:
            name: Logger name (typically module name)
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_file_logging: Enable logging to file
            enable_console_logging: Enable logging to console
            max_bytes: Maximum size of each log file
            backup_count: Number of backup log files to keep
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.propagate = False

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup handlers
        if enable_console_logging:
            self._add_console_handler()

        if enable_file_logging and log_dir:
            self._add_file_handler(log_dir, max_bytes, backup_count)

        self.performance_stack = []

    def _add_console_handler(self):
        """Add console handler with color formatting."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Color formatter for console
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self, log_dir: Path, max_bytes: int, backup_count: int):
        """Add rotating file handler with JSON formatting."""
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Regular text log file
        text_log_file = log_dir / f"{self.name}.log"
        text_handler = logging.handlers.RotatingFileHandler(
            text_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        text_handler.setLevel(logging.DEBUG)
        text_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        text_handler.setFormatter(text_formatter)
        self.logger.addHandler(text_handler)

        # JSON structured log file
        json_log_file = log_dir / f"{self.name}.json.log"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_formatter = JSONFormatter()
        json_handler.setFormatter(json_formatter)
        self.logger.addHandler(json_handler)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data."""
        self.logger.debug(message, extra={'data': kwargs} if kwargs else {})

    def info(self, message: str, **kwargs):
        """Log info message with optional structured data."""
        self.logger.info(message, extra={'data': kwargs} if kwargs else {})

    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data."""
        self.logger.warning(message, extra={'data': kwargs} if kwargs else {})

    def error(self, message: str, **kwargs):
        """Log error message with optional structured data."""
        self.logger.error(message, extra={'data': kwargs} if kwargs else {})

    def critical(self, message: str, **kwargs):
        """Log critical message with optional structured data."""
        self.logger.critical(message, extra={'data': kwargs} if kwargs else {})

    def exception(self, message: str, **kwargs):
        """Log exception with traceback and optional structured data."""
        self.logger.exception(message, extra={'data': kwargs} if kwargs else {})

    @contextmanager
    def performance_tracking(self, operation_name: str, **metadata):
        """
        Context manager for tracking operation performance.

        Usage:
            with logger.performance_tracking("database_query", query_type="select"):
                # perform operation
                pass
        """
        start_time = time.time()
        self.performance_stack.append({
            'operation': operation_name,
            'start_time': start_time,
            'metadata': metadata
        })

        self.debug(f"Started operation: {operation_name}", **metadata)

        try:
            yield
        except Exception as e:
            duration = time.time() - start_time
            self.error(
                f"Operation failed: {operation_name}",
                duration=duration,
                error=str(e),
                **metadata
            )
            raise
        else:
            duration = time.time() - start_time
            self.info(
                f"Completed operation: {operation_name}",
                duration=duration,
                **metadata
            )
        finally:
            self.performance_stack.pop()

    def log_workflow_stage(self, stage: str, status: str, **data):
        """
        Log workflow stage with structured data.

        Args:
            stage: Workflow stage name (e.g., "research", "viral_analysis")
            status: Status of the stage (e.g., "started", "completed", "failed")
            **data: Additional structured data
        """
        self.info(
            f"Workflow stage: {stage} - {status}",
            stage=stage,
            status=status,
            timestamp=datetime.utcnow().isoformat(),
            **data
        )

    def log_gatekeeper_decision(
        self,
        gatekeeper: str,
        decision: str,
        quality_score: float,
        threshold: float,
        **data
    ):
        """
        Log gatekeeper decision with quality metrics.

        Args:
            gatekeeper: Gatekeeper name
            decision: Decision made ("pass", "fail", "iterate")
            quality_score: Achieved quality score
            threshold: Required threshold
            **data: Additional data
        """
        log_method = self.info if decision == "pass" else self.warning
        log_method(
            f"Gatekeeper {gatekeeper}: {decision}",
            gatekeeper=gatekeeper,
            decision=decision,
            quality_score=quality_score,
            threshold=threshold,
            **data
        )

    def log_api_call(
        self,
        provider: str,
        endpoint: str,
        status: str,
        duration: Optional[float] = None,
        **data
    ):
        """
        Log API call with timing and status.

        Args:
            provider: API provider (e.g., "anthropic", "youtube")
            endpoint: API endpoint called
            status: Call status ("success", "error", "timeout")
            duration: Call duration in seconds
            **data: Additional data
        """
        self.info(
            f"API call to {provider}/{endpoint}: {status}",
            provider=provider,
            endpoint=endpoint,
            status=status,
            duration=duration,
            **data
        )


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Add color to level name
        record.levelname = f"{color}{record.levelname}{reset}"

        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record):
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'logger': record.name,
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add extra data if present
        if hasattr(record, 'data') and record.data:
            log_data['data'] = record.data

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class LoggerFactory:
    """Factory for creating loggers with consistent configuration."""

    _loggers: Dict[str, StructuredLogger] = {}
    _default_log_dir: Optional[Path] = None
    _default_log_level: str = "INFO"

    @classmethod
    def configure(cls, log_dir: Path, log_level: str = "INFO"):
        """
        Configure default settings for all loggers.

        Args:
            log_dir: Default directory for log files
            log_level: Default logging level
        """
        cls._default_log_dir = Path(log_dir)
        cls._default_log_level = log_level

    @classmethod
    def get_logger(
        cls,
        name: str,
        log_dir: Optional[Path] = None,
        log_level: Optional[str] = None
    ) -> StructuredLogger:
        """
        Get or create a logger instance.

        Args:
            name: Logger name
            log_dir: Log directory (uses default if not specified)
            log_level: Log level (uses default if not specified)

        Returns:
            StructuredLogger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = StructuredLogger(
                name=name,
                log_dir=log_dir or cls._default_log_dir,
                log_level=log_level or cls._default_log_level,
                enable_file_logging=cls._default_log_dir is not None
            )

        return cls._loggers[name]

    @classmethod
    def reset(cls):
        """Reset all loggers (mainly for testing)."""
        cls._loggers.clear()


# Convenience function for getting loggers
def get_logger(name: str) -> StructuredLogger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        StructuredLogger instance
    """
    return LoggerFactory.get_logger(name)


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    # Configure logger factory
    LoggerFactory.configure(log_dir=Path("logs"), log_level="DEBUG")

    # Get logger
    logger = get_logger("test_module")

    # Basic logging
    logger.info("System started")
    logger.warning("This is a warning", user_id=123)
    logger.error("An error occurred", error_code="ERR001")

    # Performance tracking
    with logger.performance_tracking("complex_operation", type="test"):
        time.sleep(0.1)
        logger.info("Operation in progress")

    # Workflow logging
    logger.log_workflow_stage("research", "completed", papers_found=50)

    # Gatekeeper logging
    logger.log_gatekeeper_decision(
        gatekeeper="research",
        decision="pass",
        quality_score=8.5,
        threshold=8.0
    )

    # API logging
    logger.log_api_call(
        provider="anthropic",
        endpoint="/messages",
        status="success",
        duration=1.23,
        tokens=1500
    )
