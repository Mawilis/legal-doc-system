"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Patch Framework Package Initialization.
    Exposes patch engine, patch planner, patch validator, and patch executor modules.

Biblical Scale & Architecture:
    Production-ready automated patch governance suite. Zero child's place.
    Enforces atomic, transactional, and quantum-safe source code patching across Wilsy OS.

Collaboration & Maintenance:
    - [Architecture]: Package entrypoint for automated source patching and migration subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .patch_engine import PatchEngine
from .patch_plan import PatchPlan
from .patch_validator import PatchValidator
from .patch_executor import PatchExecutor

__all__ = [
    "PatchEngine",
    "PatchPlan",
    "PatchValidator",
    "PatchExecutor",
]
