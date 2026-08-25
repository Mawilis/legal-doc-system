"""
===============================================================================
WILSY ENGINEERING KERNEL
===============================================================================
Epitome:
    Automation Package Initialization.
    Exposes workflow scheduler, workflow definition, and pipeline executor modules.

Biblical Scale & Architecture:
    Production-ready automated institutional workflow suite. Zero child's place.
    Enforces robust orchestration, scheduling, and pipeline execution across Wilsy OS.

Collaboration & Maintenance:
    - [Architecture]: Package entrypoint for automated task scheduling and pipeline subsystems.
    - Maintained by Wilson Khanyezi & Core Engineering.
===============================================================================
"""

from __future__ import annotations

from .scheduler import WorkflowScheduler
from .workflow import Workflow
from .pipeline_executor import PipelineExecutor

__all__ = [
    "WorkflowScheduler",
    "Workflow",
    "PipelineExecutor",
]
