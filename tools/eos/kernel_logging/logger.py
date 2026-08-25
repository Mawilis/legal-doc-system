"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Logging Framework - Central Logger Factory.
    Configures and provisions standardized enterprise loggers with console and
    file handlers across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise logger factory. Zero child's place.
    Ensures centralized stream and file output governance.

Collaboration & Maintenance:
    - [Architecture]: Factory pattern for provisioning WilsyLogger instances.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from .formatter import WilsyFormatter


class WilsyLogger:
    """
    Factory and configurator for institutional logging instances.
    """

    _configured: bool = False

    @classmethod
    def configure_root(
        cls,
        log_level: int = logging.INFO,
        log_file: Optional[Path | str] = None,
    ) -> None:
        """
        Configure the root Wilsy logging environment.
        """
        if cls._configured:
            return

        root_logger = logging.getLogger("Wilsy")
        root_logger.setLevel(log_level)
        root_logger.handlers.clear()

        # Console Handler with Color Formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(WilsyFormatter(use_colors=True))
        root_logger.addHandler(console_handler)

        # Optional File Handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(WilsyFormatter(use_colors=False))
            root_logger.addHandler(file_handler)

        cls._configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Retrieve a pre-configured institutional logger instance.

    Args:
        name (str): The name/subsystem identifier for the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    if not WilsyLogger._configured:
        WilsyLogger.configure_root()

    return logging.getLogger(f"Wilsy.{name}")
