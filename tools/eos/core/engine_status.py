"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Engine Core Framework - Engine Status Enum.
    Defines immutable runtime states for institutional engines across Wilsy OS.

Biblical Scale & Architecture:
    Production-ready enterprise status enumeration. Zero child's place.
    Provides precise telemetry tracking for engine lifecycle progression.

Collaboration & Maintenance:
    - [Architecture]: Standardized lifecycle status representation.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from enum import Enum


class EngineStatus(str, Enum):
    """
    Enumeration of possible engine execution states.
    """
    PENDING = "PENDING"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ROLLED_BACK = "ROLLED_BACK"
