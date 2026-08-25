"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
ANALYSIS SUBSYSTEM: FAILURE CLASSIFIER
===============================================================================

File Path:
    tools/eos/autonomous_recovery/analysis/failure_classifier.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Converts raw runtime telemetry failures into institutional incident types 
    (WORKER_FAILURE, NODE_FAILURE, REPOSITORY_FAILURE, PLUGIN_FAILURE, 
    DOCUMENTATION_FAILURE) with calculated severity ratings.

Biblical Worth Billions:
    "Wisdom is the principal thing; therefore get wisdom: and with all thy 
    getting get understanding." — Proverbs 4:7

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

from typing import Dict, Any, Tuple
from tools.eos.autonomous_recovery.domain.recovery_incident import RecoveryIncident, IncidentType, IncidentSeverity


class FailureClassifier:
    """
    Classifies raw runtime failure payloads into standardized institutional 
    RecoveryIncident objects with appropriate severity ratings.
    """

    @staticmethod
    def classify(error_payload: Dict[str, Any]) -> RecoveryIncident:
        """
        Analyzes a raw failure event and generates a classified RecoveryIncident.
        """
        message = error_payload.get("message", "").lower()
        subsystem = error_payload.get("subsystem", "unknown").lower()
        error_code = error_payload.get("error_code", "").upper()

        incident_type = IncidentType.SYSTEM_FAULT
        severity = IncidentSeverity.MEDIUM

        if "worker" in message or "worker" in subsystem or error_code == "ERR_WORKER_TIMEOUT":
            incident_type = IncidentType.WORKER_FAILURE
            severity = IncidentSeverity.MEDIUM
        elif "node" in message or "node" in subsystem or "offline" in message:
            incident_type = IncidentType.NODE_FAILURE
            severity = IncidentSeverity.HIGH
        elif "repo" in message or "corruption" in message or "git" in message:
            incident_type = IncidentType.REPOSITORY_FAILURE
            severity = IncidentSeverity.CRITICAL
        elif "plugin" in message or "marketplace" in message:
            incident_type = IncidentType.PLUGIN_FAILURE
            severity = IncidentSeverity.LOW
        elif "doc" in message or "drift" in message:
            incident_type = IncidentType.DOCUMENTATION_FAILURE
            severity = IncidentSeverity.LOW

        incident = RecoveryIncident(
            incident_type=incident_type,
            severity=severity,
            source_subsystem=error_payload.get("subsystem", "runtime"),
            description=error_payload.get("message", "Autonomous failure detected"),
            raw_payload=error_payload
        )
        return incident
