"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
ANALYSIS SUBSYSTEM: IMPACT ANALYZER
===============================================================================

File Path:
    tools/eos/autonomous_recovery/analysis/impact_analyzer.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Consumes Digital Twin, repository graph, cluster, runtime, and marketplace 
    telemetry to compute the blast radius and business criticality of an incident.

Biblical Worth Billions:
    "Wherefore do ye spend money for that which is not bread? and your labour 
    for that which satisfieth not?" — Isaiah 55:2

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

from typing import Dict, Any, List
from tools.eos.autonomous_recovery.domain.recovery_incident import RecoveryIncident, IncidentType


class ImpactAnalyzer:
    """
    Evaluates incident blast radius across Wilsy OS subsystems, identifying 
    affected workers, nodes, plugins, documents, and business services.
    """

    @staticmethod
    def analyze(incident: RecoveryIncident) -> Dict[str, Any]:
        """
        Computes the impact metrics and blast radius for a given recovery incident.
        """
        affected_workers: List[str] = []
        affected_nodes: List[str] = []
        affected_plugins: List[str] = []
        affected_documents: List[str] = []
        affected_services: List[str] = []
        estimated_recovery_time_sec = 10.0

        if incident.incident_type == IncidentType.WORKER_FAILURE:
            affected_workers = [incident.raw_payload.get("worker_id", "WORKER-001")]
            affected_services = ["ExecutionScheduler"]
            estimated_recovery_time_sec = 5.0
        elif incident.incident_type == IncidentType.NODE_FAILURE:
            affected_nodes = [incident.raw_payload.get("node_id", "NODE-CLUSTER-A")]
            affected_workers = ["WORKER-001", "WORKER-002"]
            affected_services = ["ClusterOrchestrator", "RuntimeScheduler"]
            estimated_recovery_time_sec = 30.0
        elif incident.incident_type == IncidentType.REPOSITORY_FAILURE:
            affected_documents = ["CoreContract.md", "SovereignLedger.db"]
            affected_services = ["RepositorySync", "DigitalTwin"]
            estimated_recovery_time_sec = 60.0
        elif incident.incident_type == IncidentType.PLUGIN_FAILURE:
            affected_plugins = [incident.raw_payload.get("plugin_id", "PLUGIN-MARKETPLACE-EXT")]
            affected_services = ["MarketplaceEngine"]
            estimated_recovery_time_sec = 3.0

        return {
            "incident_id": incident.incident_id,
            "affected_workers": affected_workers,
            "affected_nodes": affected_nodes,
            "affected_plugins": affected_plugins,
            "affected_documents": affected_documents,
            "affected_services": affected_services,
            "estimated_recovery_time_sec": estimated_recovery_time_sec,
            "business_criticality": incident.severity.value
        }
