"""
===============================================================================
WILSY OS — FG221 CLUSTER ORCHESTRATOR SUBSYSTEM
===============================================================================

File Path:
    tools/eos/cluster/infrastructure/cluster_report.py

Epitome:
    Human-readable and machine-parsable audit reporter delivering real-time cluster 
    topology, worker health, capacity distribution, and metric snapshots.

Biblical Worth Billions:
    "Write the vision, and make it plain upon tables, that he may run that readeth it."
    — Habakkuk 2:2

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from tools.eos.cluster.infrastructure.cluster_metrics import ClusterMetricsCollector, ClusterMetricsSnapshot

class ClusterReportGenerator:
    """
    Utility producing formatted textual summaries, ASCII topology structures, 
    and structured JSON reports for system monitoring.
    """

    def __init__(self, metrics_collector: ClusterMetricsCollector) -> None:
        self.metrics_collector = metrics_collector

    def generate_ascii_summary(self, cluster_manager: Any) -> str:
        """Generates a plain-text ASCII dashboard table representing cluster health."""
        snapshot: ClusterMetricsSnapshot = self.metrics_collector.capture_snapshot(cluster_manager)

        lines = [
            "=" * 78,
            "               WILSY OS — CLUSTER ORCHESTRATOR AUDIT REPORT",
            "=" * 78,
            f" Timestamp          : {snapshot.timestamp}",
            f" Registered Nodes   : {snapshot.total_nodes}",
            f" Total Workers      : {snapshot.total_workers} (Active: {snapshot.active_workers})",
            f" Capacity Utilization: {snapshot.current_load} / {snapshot.total_capacity} ({snapshot.load_percentage}% Load)",
            f" Cluster Latency    : {snapshot.avg_latency_ms:.2f} ms avg",
            f" Tasks Executed     : {snapshot.total_tasks_executed} (Failures: {snapshot.failed_tasks_count} | Error Rate: {snapshot.error_rate_percentage}%)",
            "-" * 78,
            " WORKER STATUS BREAKDOWN:",
        ]

        for status_str, count in snapshot.workers_by_status.items():
            lines.append(f"   • {status_str:<18}: {count}")

        lines.append("-" * 78)
        lines.append(" REGISTERED COMPUTE NODES:")

        nodes = cluster_manager.list_nodes() if hasattr(cluster_manager, "list_nodes") else []
        if not nodes:
            lines.append("   (No active compute nodes registered)")
        else:
            for node in nodes:
                attached_cnt = len(node.attached_workers) if hasattr(node, "attached_workers") else 0
                lines.append(
                    f"   [Node: {node.node_id:<12}] Host: {node.hostname:<15} IP: {node.ip_address:<15} "
                    f"Cores: {node.cpu_cores:<2} RAM: {node.memory_gb}GB Workers: {attached_cnt}"
                )

        lines.append("=" * 78)
        return "\n".join(lines)

    def generate_json_report(self, cluster_manager: Any) -> Dict[str, Any]:
        """Generates a structured dictionary representation suitable for API serialization."""
        snapshot = self.metrics_collector.capture_snapshot(cluster_manager)

        nodes_data = []
        if hasattr(cluster_manager, "list_nodes"):
            for n in cluster_manager.list_nodes():
                if hasattr(n, "to_dict"):
                    nodes_data.append(n.to_dict())

        workers_data = []
        if hasattr(cluster_manager, "list_workers"):
            for w in cluster_manager.list_workers():
                if hasattr(w, "to_dict"):
                    workers_data.append(w.to_dict())

        return {
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "system": "Wilsy OS FG221 Cluster Orchestrator"
            },
            "metrics": {
                "total_nodes": snapshot.total_nodes,
                "total_workers": snapshot.total_workers,
                "active_workers": snapshot.active_workers,
                "total_capacity": snapshot.total_capacity,
                "current_load": snapshot.current_load,
                "load_percentage": snapshot.load_percentage,
                "avg_latency_ms": snapshot.avg_latency_ms,
                "total_tasks_executed": snapshot.total_tasks_executed,
                "failed_tasks_count": snapshot.failed_tasks_count,
                "error_rate_percentage": snapshot.error_rate_percentage,
                "workers_by_status": snapshot.workers_by_status
            },
            "nodes": nodes_data,
            "workers": workers_data
        }
