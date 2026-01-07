import logging
import sys
import structlog
from typing import Any
from src.config import settings

def setup_logger():
    """
    Configures structlog for JSON output (production-ready)
    and standard logging compatibility.
    """
    
    # Validation: Basic Config
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    # JSON Renderer for Production (or if forced)
    # ConsoleRenderer for local dev (optional, but requested commercial grade = likely JSON for machines)
    # We will stick to JSON for consistency as per request "Usage of structlog with JSON format"
    processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Return a proxy that mimics standard logger but uses structlog
    return structlog.get_logger()
