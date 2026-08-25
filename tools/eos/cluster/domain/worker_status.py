"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/domain/worker_status.py

Epitome:
    Canonical state machine enumeration governing the immutable lifecycle transitions 
    of execution workers across the Wilsy OS cluster.

Biblical Worth Billions:
    "To every thing there is a season, and a time to every purpose under the heaven."
    — Ecclesiastes 3:1

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

from enum import Enum
from typing import Dict, Set


class WorkerStatus(str, Enum):
    """
    Lifecycle states for cluster execution workers.
    
    Lifecycle Sequence:
        REGISTERED -> INITIALIZING -> READY -> EXECUTING -> BUSY -> IDLE -> DRAINING -> OFFLINE
    """
    REGISTERED = "REGISTERED"
    INITIALIZING = "INITIALIZING"
    READY = "READY"
    EXECUTING = "EXECUTING"
    BUSY = "BUSY"
    IDLE = "IDLE"
    DRAINING = "DRAINING"
    OFFLINE = "OFFLINE"

    @property
    def is_active(self) -> bool:
        """Returns True if the worker is in an active operational state."""
        return self in (
            WorkerStatus.READY,
            WorkerStatus.EXECUTING,
            WorkerStatus.BUSY,
            WorkerStatus.IDLE,
        )

    @property
    def is_schedulable(self) -> bool:
        """Returns True if the worker can accept new execution tasks."""
        return self in (WorkerStatus.READY, WorkerStatus.IDLE)

    def can_transition_to(self, new_status: "WorkerStatus") -> bool:
        """
        Validates whether a lifecycle state transition is legal.
        """
        if self == new_status:
            return True

        valid_transitions: Dict[WorkerStatus, Set[WorkerStatus]] = {
            WorkerStatus.REGISTERED: {WorkerStatus.INITIALIZING, WorkerStatus.OFFLINE},
            WorkerStatus.INITIALIZING: {WorkerStatus.READY, WorkerStatus.OFFLINE},
            WorkerStatus.READY: {WorkerStatus.EXECUTING, WorkerStatus.BUSY, WorkerStatus.IDLE, WorkerStatus.DRAINING, WorkerStatus.OFFLINE},
            WorkerStatus.EXECUTING: {WorkerStatus.READY, WorkerStatus.BUSY, WorkerStatus.IDLE, WorkerStatus.DRAINING, WorkerStatus.OFFLINE},
            WorkerStatus.BUSY: {WorkerStatus.READY, WorkerStatus.EXECUTING, WorkerStatus.IDLE, WorkerStatus.DRAINING, WorkerStatus.OFFLINE},
            WorkerStatus.IDLE: {WorkerStatus.READY, WorkerStatus.EXECUTING, WorkerStatus.BUSY, WorkerStatus.DRAINING, WorkerStatus.OFFLINE},
            WorkerStatus.DRAINING: {WorkerStatus.OFFLINE, WorkerStatus.READY},
            WorkerStatus.OFFLINE: {WorkerStatus.REGISTERED, WorkerStatus.INITIALIZING},
        }

        allowed = valid_transitions.get(self, set())
        return new_status in allowed
