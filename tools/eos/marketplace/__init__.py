"""
===============================================================================
WILSY OS — FG220 PLUGIN MARKETPLACE PACKAGE INITIALIZER
===============================================================================

Epitome:
    Package initializer and centralized logging facility for the Wilsy OS
    FG220 marketplace subsystem. Establishes structured logging formats and
    exports core public APIs with strict type safety.

Biblical Worth Billions:
    "Let all your things be done with charity."
    — 1 Corinthians 16:14

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
    - File Path: tools/eos/marketplace/__init__.py
===============================================================================
"""

import sys
import logging
from typing import Any, Optional

def _setup_marketplace_logger() -> logging.Logger:
    """Configures and returns the unified Wilsy OS Marketplace logger."""
    log = logging.getLogger("WilsyMarketplace")
    if not log.handlers:
        log.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [WILSY-MARKETPLACE] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.propagate = False
    return log


class _MarketplaceLoggerProxy:
    """Proxy providing type-safe convenient log level wrappers."""
    def __init__(self) -> None:
        self._logger = _setup_marketplace_logger()

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.error(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.warning(msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self._logger.debug(msg, *args, **kwargs)


logger = _MarketplaceLoggerProxy()
