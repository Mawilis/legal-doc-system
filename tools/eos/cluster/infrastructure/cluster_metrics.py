"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/infrastructure/cluster_metrics.py

Epitome:
    Real-time performance telemetry aggregator measuring total compute capacity,
    workload load factor percentage, worker distribution, and error rate telemetry.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, and 
    counteth the cost, whether he have sufficient to finish it?"
    — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import threading
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from tools.eos.cluster.domain.worker import Worker
from tools.eos.cluster.domain.worker_status import WorkerStatus

logger = logging.getLogger("wilsy_os.cluster.cluster_metrics")


@dataclass(frozen=True)
class ClusterMetricsSnapshot:
    """Immutable data record summarizing state and load metrics at a given timestamp."""
    timestamp: str
    total_nodes: int
    total_workers: int
    active_workers: int
    total_capacity: int
    current_load: int
    load_percentage: float
    avg_latency_ms: float
    total_tasks_executed: int
    failed_tasks_count: int
    error_rate_percentage: float
    workers_by_status: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-compatible dictionary representation of snapshot."""
        return asdict(self)


class ClusterMetricsCollector:
    """
    Thread-safe counter and aggregator capturing continuous operational metrics 
    for real-time dashboarding and backpressure throttling.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._total_tasks_executed = 0
        self._failed_tasks_count = 0
        self._total_execution_ms = 0.0

    def record_task_completion(self, execution_time_ms: float, success: bool) -> None:
        """Records task outcomes for throughput and error rate telemetry."""
        with self._lock:
            self._total_tasks_executed += 1
            self._total_execution_ms += max(0.0, execution_time_ms)
            if not success:
                self._failed_tasks_count += 1

    def capture_snapshot(self, cluster_manager: Any) -> ClusterMetricsSnapshot:
        """
        Inspects the active state of the provided ClusterManager and generates an 
        auditable metrics snapshot.
        """
        with self._lock:
            workers: List[Worker] = cluster_manager.list_workers() if hasattr(cluster_manager, "list_workers") else []
            nodes_count = len(cluster_manager.list_nodes()) if hasattr(cluster_manager, "list_nodes") else 0

            total_workers = len(workers)
            active_workers = sum(
                1 for w in workers 
                if getattr(w, "status", None) and getattr(w.status, "is_active", False)
            )

            total_capacity = sum(getattr(w, "max_capacity", 0) for w in workers)
            current_load = sum(getattr(w, "current_load", 0) for w in workers)

            load_percentage = (current_load / max(1, total_capacity)) * 100.0 if total_capacity > 0 else 0.0

            status_distribution: Dict[str, int] = {}
            total_latencies = 0.0
            for w in workers:
                st = getattr(w, "status", WorkerStatus.OFFLINE)
                st_val = st.value if hasattr(st, "value") else str(st)
                status_distribution[st_val] = status_distribution.get(st_val, 0) + 1
                total_latencies += getattr(w, "latency_ms", 0.0)

            avg_latency = (total_latencies / max(1, total_workers)) if total_workers > 0 else 0.0

            error_rate = (
                (self._failed_tasks_count / max(1, self._total_tasks_executed)) * 100.0
                if self._total_tasks_executed > 0 else 0.0
            )

            return ClusterMetricsSnapshot(
                timestamp=datetime.now(timezone.utc).isoformat(),
                total_nodes=nodes_count,
                total_workers=total_workers,
                active_workers=active_workers,
                total_capacity=total_capacity,
                current_load=current_load,
                load_percentage=round(load_percentage, 2),
                avg_latency_ms=round(avg_latency, 2),
                total_tasks_executed=self._total_tasks_executed,
                failed_tasks_count=self._failed_tasks_count,
                error_rate_percentage=round(error_rate, 2),
                workers_by_status=status_distribution
            )

    def reset_counters(self) -> None:
        """Resets dynamic execution performance counters."""
        with self._lock:
            self._total_tasks_executed = 0
            self._failed_tasks_count = 0
            self._total_execution_ms = 0.0
