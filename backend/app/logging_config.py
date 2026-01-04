"""Structured logging configuration."""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from functools import wraps
import time


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """Structured logger with context support."""
    
    def __init__(self, name: str = "app"):
        self.logger = logging.getLogger(name)
        self._context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs):
        """Set context fields for all subsequent logs."""
        self._context.update(kwargs)
    
    def clear_context(self):
        """Clear all context fields."""
        self._context.clear()
    
    def _log(self, level: int, message: str, **extra):
        """Internal log method."""
        extra_data = {**self._context, **extra}
        record = self.logger.makeRecord(
            self.logger.name, level, "", 0, message, (), None
        )
        record.extra_data = extra_data
        self.logger.handle(record)
    
    def debug(self, message: str, **extra):
        self._log(logging.DEBUG, message, **extra)
    
    def info(self, message: str, **extra):
        self._log(logging.INFO, message, **extra)
    
    def warning(self, message: str, **extra):
        self._log(logging.WARNING, message, **extra)
    
    def error(self, message: str, **extra):
        self._log(logging.ERROR, message, **extra)
    
    def critical(self, message: str, **extra):
        self._log(logging.CRITICAL, message, **extra)


def setup_logging(debug: bool = False, json_format: bool = True):
    """Setup application logging."""
    # Set log level
    level = logging.DEBUG if debug else logging.INFO
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            )
        )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]
    
    # Configure app logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(level)
    
    # Reduce noise from libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return StructuredLogger("app")


def log_execution_time(logger: StructuredLogger):
    """Decorator to log function execution time."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"{func.__name__} completed",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2)
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2),
                    error=str(e)
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"{func.__name__} completed",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2)
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed",
                    function=func.__name__,
                    execution_time_ms=round(execution_time * 1000, 2),
                    error=str(e)
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


# Global logger instance
logger = setup_logging(debug=True, json_format=False)

