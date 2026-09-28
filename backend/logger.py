"""
Structured logging module for Jarvis 2 Assistant.
Provides standardized formatting and log levels across all components.
"""

import logging
import sys
from typing import Optional
from backend.config import config


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retrieve a configured logger instance with formatted console output.
    """
    logger_name = f"Jarvis.{name}" if name else "Jarvis"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        log_level = logging.DEBUG if config.debug else logging.INFO
        logger.setLevel(log_level)

    return logger


logger = get_logger("Core")
