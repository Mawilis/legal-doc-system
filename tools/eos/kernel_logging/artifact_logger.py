"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Logging Framework - Artifact Logger.
    Specialized logger for recording institutional artifact creation, cryptographic
    hashing, and disk persistence across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise artifact logger. Zero child's place.
    Provides structured audit tracking for generated reports and code assets.

Collaboration & Maintenance:
    - [Architecture]: Contextual artifact logger for sealing compliance records.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
from .logger import get_logger

logger = get_logger("Artifact")


class ArtifactLogger:
    """
    Specialized logger for tracking institutional artifact generation and sealing.
    """

    def __init__(self, execution_id: str) -> None:
        self.execution_id = execution_id

    def log_creation(self, artifact_name: str, destination: Path | str) -> None:
        """Log the generation of a new artifact."""
        logger.info(f"[{self.execution_id}] Artifact Created: '{artifact_name}' -> {destination}")

    def log_sealing(self, artifact_name: str, checksum: str) -> None:
        """Log the cryptographic sealing of an artifact."""
        logger.info(f"[{self.execution_id}] Artifact Sealed: '{artifact_name}' [Checksum: {checksum[:12]}...] ")

    def log_failure(self, artifact_name: str, error: str) -> None:
        """Log artifact generation or sealing failure."""
        logger.error(f"[{self.execution_id}] Artifact Failed: '{artifact_name}' -> {error}")
