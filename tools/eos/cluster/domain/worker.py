"""
===============================================================================
WILSY OS — FG221 WORKER DOMAIN ENTITY
===============================================================================

File Path:
    tools/eos/cluster/domain/worker.py

Epitome:
    Represents an individual compute worker node within the FG221 cluster, 
    managing its status transitions, current load, heartbeat timestamps, 
    capacity checks, health scoring, and capability tags.

Biblical Worth Billions:
    "Whatever your hand finds to do, do it with your might."
    — Ecclesiastes 9:10

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import time
from datetime import datetime, timezone
from typing import Set, Optional, Dict, Any

from tools.eos.cluster.domain.worker_status import WorkerStatus


class Worker:
    """
    Domain entity encapsulating worker state, capability matching, 
    load tracking, load increment/decrement methods, health scoring, and heartbeat monitoring.
    """

    def __init__(
        self,
        worker_id: str,
        node_id: Optional[str] = None,
        status: WorkerStatus = WorkerStatus.REGISTERED,
        capabilities: Optional[Set[str]] = None,
        max_capacity: int = 10,
        current_load: int = 0
    ) -> None:
        self.worker_id = worker_id
        self.node_id = node_id
        self.status = status
        self.capabilities: Set[str] = capabilities or set()
        self.max_capacity = max_capacity
        self.current_load = current_load
        
        self.last_heartbeat = datetime.now(timezone.utc)
        self.latency_ms: float = 0.0

    def transition_to(self, new_status: WorkerStatus) -> None:
        """Transitions worker to a new operational status."""
        self.status = new_status

    def increment_load(self) -> bool:
        """Increments current worker load if capacity allows. Returns True on success."""
        if self.current_load < self.max_capacity:
            self.current_load += 1
            if self.status == WorkerStatus.READY:
                self.status = WorkerStatus.BUSY
            return True
        return False

    def decrement_load(self) -> None:
        """Decrements current worker load and restores READY status if load drops to zero."""
        if self.current_load > 0:
            self.current_load -= 1
        if self.current_load == 0 and self.status in (WorkerStatus.BUSY, WorkerStatus.EXECUTING):
            self.status = WorkerStatus.READY

    def record_heartbeat(
        self,
        current_load: Optional[int] = None,
        latency_ms: Optional[float] = None
    ) -> None:
        """Records a fresh heartbeat from the worker, updating load and telemetry."""
        self.last_heartbeat = datetime.now(timezone.utc)
        if current_load is not None:
            self.current_load = current_load
        if latency_ms is not None:
            self.latency_ms = latency_ms

    @property
    def health_score(self) -> float:
        """Calculates numerical health score (0.0 to 100.0) based on status and load."""
        if self.status == WorkerStatus.OFFLINE:
            return 0.0
        load_ratio = float(self.current_load) / float(max(1, self.max_capacity))
        load_penalty = load_ratio * 20.0
        return max(0.0, 100.0 - load_penalty)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes worker state to a dictionary for telemetry and logging."""
        return {
            "worker_id": self.worker_id,
            "node_id": self.node_id,
            "status": self.status.value if isinstance(self.status, WorkerStatus) else str(self.status),
            "capabilities": list(self.capabilities),
            "max_capacity": self.max_capacity,
            "current_load": self.current_load,
            "health_score": round(self.health_score, 2),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "latency_ms": self.latency_ms
        }
