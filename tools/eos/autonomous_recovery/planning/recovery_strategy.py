"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
PLANNING SUBSYSTEM: RECOVERY STRATEGY MAPPING
===============================================================================

File Path:
    tools/eos/autonomous_recovery/planning/recovery_strategy.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Maps classified failure incidents to approved recovery strategies 
    (Worker Restart, Leader Election, Snapshot Restore, Event Replay, Plugin Disable).

Biblical Worth Billions:
    "Through wisdom is an house builded; and by understanding it is established." 
    — Proverbs 24:3

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

from typing import List, Dict, Any
from tools.eos.autonomous_recovery.domain.recovery_incident import IncidentType


class RecoveryStrategyMapper:
    """
    Maps institutional incident types to deterministic recovery strategies 
    and required action sequences.
    """

    @staticmethod
    def get_strategy_for_incident(incident_type: IncidentType) -> Dict[str, Any]:
        """
        Returns the strategy name and sequence of action steps for a given incident type.
        """
        if incident_type == IncidentType.WORKER_FAILURE:
            return {
                "strategy_name": "RESTART_WORKER_STRATEGY",
                "steps": [
                    {"action_type": "DRAIN_WORKER_QUEUES", "target": "worker"},
                    {"action_type": "RESTART_WORKER_PROCESS", "target": "worker"},
                    {"action_type": "VERIFY_WORKER_HEALTH", "target": "worker"}
                ]
            }
        elif incident_type == IncidentType.NODE_FAILURE:
            return {
                "strategy_name": "NODE_FAILOVER_AND_LEADER_ELECTION",
                "steps": [
                    {"action_type": "FREEZE_SCHEDULING", "target": "cluster"},
                    {"action_type": "INITIATE_LEADER_ELECTION", "target": "cluster"},
                    {"action_type": "MIGRATE_WORKERS", "target": "cluster"},
                    {"action_type": "VERIFY_CLUSTER_QUORUM", "target": "cluster"},
                    {"action_type": "RESUME_SCHEDULING", "target": "cluster"}
                ]
            }
        elif incident_type == IncidentType.REPOSITORY_FAILURE:
            return {
                "strategy_name": "RESTORE_SNAPSHOT_AND_REPLAY",
                "steps": [
                    {"action_type": "ISOLATE_REPOSITORY", "target": "repository"},
                    {"action_type": "RESTORE_SNAPSHOT", "target": "reliability_platform"},
                    {"action_type": "REPLAY_EVENT_LOG", "target": "event_bus"},
                    {"action_type": "VERIFY_REPOSITORY_INTEGRITY", "target": "repository"}
                ]
            }
        elif incident_type == IncidentType.PLUGIN_FAILURE:
            return {
                "strategy_name": "DISABLE_PLUGIN_AND_RESTORE",
                "steps": [
                    {"action_type": "DISABLE_MARKETPLACE_PLUGIN", "target": "marketplace"},
                    {"action_type": "RESTORE_PREVIOUS_PLUGIN_VERSION", "target": "marketplace"},
                    {"action_type": "VERIFY_MARKETPLACE_HEALTH", "target": "marketplace"}
                ]
            }
        else:
            return {
                "strategy_name": "STANDARD_SYSTEM_RECOVERY",
                "steps": [
                    {"action_type": "DIAGNOSE_SUBSYSTEM", "target": "system"},
                    {"action_type": "RESTART_SUBSYSTEM", "target": "system"}
                ]
            }
