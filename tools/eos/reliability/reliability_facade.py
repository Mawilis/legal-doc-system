"""
===============================================================================
WILSY OS — ENTERPRISE RELIABILITY FACADE
===============================================================================

File Path:
    tools/eos/reliability/reliability_facade.py

Epitome:
    Unified integration facade connecting High Availability, Backup Engine, 
    Recovery Engine, Observability, and Reporting submodules into a single 
    cohesive enterprise runtime interface.

Biblical Worth Billions:
    "And the work shall be established in his hand."
    — Deuteronomy 33:7

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent (Gemini)
===============================================================================
"""

from typing import Dict, Any, List
from tools.eos.reliability.high_availability.node_health import NodeHealthManager, NodeState
from tools.eos.reliability.high_availability.leader_election import LeaderElectionEngine
from tools.eos.reliability.backup.backup_engine import BackupEngine
from tools.eos.reliability.recovery.recovery_engine import RecoveryEngine
from tools.eos.reliability.observability.metrics import MetricsCollector
from tools.eos.reliability.reporting.sla import SLACalculator

class ReliabilityFacade:
    """Master entry point for the FG222 Enterprise Reliability Platform."""

    def __init__(self) -> None:
        self.node_managers: Dict[str, NodeHealthManager] = {}
        self.leader_engine = LeaderElectionEngine("WILSY-CLUSTER-01")
        self.backup_engine = BackupEngine()
        self.recovery_engine = RecoveryEngine()
        self.metrics_collector = MetricsCollector()
        self.sla_calculator = SLACalculator()

    def register_node(self, node_id: str) -> NodeHealthManager:
        """Registers and initializes a cluster node for health monitoring."""
        if node_id not in self.node_managers:
            self.node_managers[node_id] = NodeHealthManager(node_id)
        return self.node_managers[node_id]

    def process_cluster_heartbeat(self, node_id: str, metrics: Dict[str, Any]) -> None:
        """Ingests node heartbeat telemetry and updates health states."""
        manager = self.register_node(node_id)
        manager.record_heartbeat(metrics)
        self.metrics_collector.increment("heartbeats_processed")

    def create_system_backup(self, cluster_state: Dict[str, Any], registry_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Initiates an immutable platform backup through the backup engine."""
        backup = self.backup_engine.create_backup(cluster_state, registry_records)
        self.metrics_collector.increment("backups_created")
        return backup

    def execute_system_recovery(self, backup_manifest: Dict[str, Any], mode: str = "HOT") -> Dict[str, Any]:
        """Executes recovery pipeline."""
        recovery = self.recovery_engine.execute_recovery(backup_manifest, mode)
        self.metrics_collector.increment("recoveries_executed")
        return recovery

    def export_cluster_reliability_status(self) -> Dict[str, Any]:
        """Exports aggregated cluster reliability telemetry across all active nodes."""
        nodes_status = {nid: mgr.export_telemetry() for nid, mgr in self.node_managers.items()}
        online_count = sum(1 for m in self.node_managers.values() if m.state == NodeState.ONLINE)
        total_nodes = len(self.node_managers)
        
        availability_pct = (online_count / total_nodes * 100.0) if total_nodes > 0 else 100.0

        return {
            "total_nodes": total_nodes,
            "online_nodes": online_count,
            "availability_percentage": round(availability_pct, 2),
            "current_leader": self.leader_engine.get_leader(),
            "nodes": nodes_status
        }
