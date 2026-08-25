"""
===============================================================================
WILSY OS — KERNEL DISTRIBUTED DASHBOARD (FG195)
===============================================================================
Epitome:
    Provides Kubernetes-like real-time cluster telemetry, worker health tracking,
    queue lengths, CPU/memory consumption, latency metrics, and artifact tracking
    across the distributed Wilsy OS sovereign infrastructure.

Biblical Worth Billions:
    "And he shall be like a tree planted by the rivers of water, that bringeth 
    forth his fruit in his season; his leaf also shall not wither; and whatsoever 
    he doeth shall prosper." 
    — Psalm 1:3

Collaboration & Ownership:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - File Path: tools/eos/dashboard/cluster_dashboard.py
===============================================================================
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logger = logging.getLogger("WilsyOS.Dashboard.Cluster")


@dataclass(frozen=True)
class WorkerNodeStatus:
    """Represents real-time health and resource telemetry for a cluster worker node."""
    node_id: str
    hostname: str
    status: str  # "HEALTHY", "DEGRADED", "OFFLINE"
    cpu_usage_pct: float
    memory_usage_pct: float
    active_tasks_count: int
    uptime_seconds: int
    last_heartbeat: str


@dataclass(frozen=True)
class ClusterQueueMetrics:
    """Tracks queue lengths, latencies, and execution throughput."""
    queue_name: str
    pending_tasks: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_latency_ms: float
    p99_latency_ms: float


@dataclass(frozen=True)
class DistributedClusterSnapshot:
    """Immutable snapshot of the entire distributed cluster state for UI/API consumption."""
    cluster_id: str
    timestamp: str
    total_workers: int
    healthy_workers: int
    workers: List[WorkerNodeStatus]
    queues: List[ClusterQueueMetrics]
    total_artifacts_cataloged: int
    global_health_index: float


class ClusterDashboardEngine:
    """
    Kubernetes-Like Distributed Dashboard Engine for Wilsy OS.

    Aggregates node health, queue depth, resource utilization, and execution telemetry
    into structured, immutable snapshots adhering to the Kernel ABI.
    """

    def __init__(self, cluster_id: str = "WILSY-OS-PROD-CLUSTER-01") -> None:
        self.cluster_id = cluster_id
        self._workers: Dict[str, WorkerNodeStatus] = {}
        self._queues: Dict[str, ClusterQueueMetrics] = {}
        self._artifact_count: int = 0
        logger.info("ClusterDashboardEngine initialized for cluster: %s", self.cluster_id)

    def register_worker(self, worker: WorkerNodeStatus) -> None:
        """Register or update a worker node's telemetry status."""
        self._workers[worker.node_id] = worker
        logger.debug("Worker node telemetry updated: %s [%s]", worker.node_id, worker.status)

    def update_queue(self, metrics: ClusterQueueMetrics) -> None:
        """Update task queue and latency metrics."""
        self._queues[metrics.queue_name] = metrics
        logger.debug("Queue metrics updated: %s (Pending: %d)", metrics.queue_name, metrics.pending_tasks)

    def record_artifact_publication(self, count: int = 1) -> None:
        """Increment artifact catalog counter."""
        self._artifact_count += count

    def generate_snapshot(self) -> DistributedClusterSnapshot:
        """
        Generate a complete, Kubernetes-like cluster telemetry snapshot.

        Returns
        -------
        DistributedClusterSnapshot
            Immutable snapshot containing worker health, resource usage, and task metrics.
        """
        workers_list = list(self._workers.values())
        total_workers = len(workers_list)
        healthy_workers = sum(1 for w in workers_list if w.status == "HEALTHY")

        queues_list = list(self._queues.values())

        # Compute global health index based on worker health and queue failure rates
        if total_workers > 0:
            worker_health_ratio = healthy_workers / total_workers
        else:
            worker_health_ratio = 1.0

        total_failures = sum(q.failed_tasks for q in queues_list)
        total_completed = sum(q.completed_tasks for q in queues_list)
        total_exec = total_completed + total_failures

        failure_penalty = (total_failures / total_exec) * 20.0 if total_exec > 0 else 0.0
        global_health = max(0.0, min(100.0, (worker_health_ratio * 100.0) - failure_penalty))

        timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        return DistributedClusterSnapshot(
            cluster_id=self.cluster_id,
            timestamp=timestamp_str,
            total_workers=total_workers,
            healthy_workers=healthy_workers,
            workers=workers_list,
            queues=queues_list,
            total_artifacts_cataloged=self._artifact_count,
            global_health_index=round(global_health, 2),
        )
