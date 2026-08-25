from __future__ import annotations

"""
===============================================================================
WILSY OS RUNTIME — PIPELINE STATUS & STATE MACHINE (FG179)
===============================================================================
Epitome:
    Canonical state machine and validator governing the lifecycle states of an
    orchestrated execution pipeline across Wilsy OS kernel processes.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and
    counteth the cost, whether he have sufficient to finish it?" — Luke 14:28
    Deterministic status tracking guarantees zero dangling processes, total
    visibility, and fail-safe transactional integrity.

Collaboration & Ownership:
    - Founder & Lead Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Execution Pipeline Runtime
    - Phase / Milestone: FG179 - Execution Pipeline Manager
    - Target Directory: tools/eos/runtime/
    - File Path: tools/eos/runtime/pipeline_status.py
    - Runtime Alignment: Python 3.10+ Production Environment

Downstream Consumers:
    - PipelineManager (Drives state transitions)
    - Executive Audit Dashboards & Health Monitors
    - Kernel Scheduler & Distributed Task Dispatchers
===============================================================================
"""

import enum
from typing import Dict, Set


class PipelineStatus(str, enum.Enum):
    """
    Explicit enumeration of all valid execution states for a Wilsy OS pipeline.
    """
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PipelineStatusValidator:
    """
    Guards pipeline state transitions against illegal out-of-order jumps.
    """

    _ALLOWED_TRANSITIONS: Dict[PipelineStatus, Set[PipelineStatus]] = {
        PipelineStatus.CREATED: {PipelineStatus.READY, PipelineStatus.CANCELLED, PipelineStatus.FAILED},
        PipelineStatus.READY: {PipelineStatus.RUNNING, PipelineStatus.CANCELLED, PipelineStatus.FAILED},
        PipelineStatus.RUNNING: {
            PipelineStatus.PAUSED,
            PipelineStatus.COMPLETED,
            PipelineStatus.FAILED,
            PipelineStatus.CANCELLED,
        },
        PipelineStatus.PAUSED: {PipelineStatus.RUNNING, PipelineStatus.CANCELLED, PipelineStatus.FAILED},
        PipelineStatus.FAILED: {PipelineStatus.READY, PipelineStatus.CANCELLED, PipelineStatus.CREATED},
        PipelineStatus.COMPLETED: {PipelineStatus.READY},
        PipelineStatus.CANCELLED: {PipelineStatus.READY},
    }

    @classmethod
    def can_transition(cls, current: PipelineStatus, next_status: PipelineStatus) -> bool:
        """
        Returns True if transitioning from `current` to `next_status` is legal.
        """
        allowed = cls._ALLOWED_TRANSITIONS.get(current, set())
        return next_status in allowed


__all__ = ["PipelineStatus", "PipelineStatusValidator"]
