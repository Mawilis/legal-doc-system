"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Logging Framework - Institutional Log Formatter.
    Provides structured, timestamped, and color-coded formatting for all
    runtime telemetry across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise log formatter. Zero child's place.
    Ensures precise trace correlation and audit-ready log formatting.

Collaboration & Maintenance:
    - [Architecture]: Custom logging.Formatter implementation with severity coloring.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional


class WilsyFormatter(logging.Formatter):
    """
    Institutional log formatter generating structured, readable log entries with precise timestamps.
    """

    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s" + reset,
        logging.INFO: blue + "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s" + reset,
        logging.WARNING: yellow + "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s" + reset,
        logging.ERROR: red + "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s" + reset,
        logging.CRITICAL: bold_red + "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s" + reset,
    }

    def __init__(self, use_colors: bool = True) -> None:
        super().__init__(datefmt="%Y-%m-%d %H:%M:%S")
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record with conditional ANSI coloring and timestamp injection.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: Formatted log string.
        """
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        if not self.use_colors:
            # Strip ANSI escape sequences for plain file logging
            log_fmt = "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"

        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
