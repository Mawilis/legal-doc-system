"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
PLANNING SUBSYSTEM: RECOVERY PLANNER
===============================================================================

File Path:
    tools/eos/autonomous_recovery/planning/recovery_planner.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Constructs deterministic RecoveryPlan instances containing sequential execution 
    steps mapped from failure incident analysis.

Biblical Worth Billions:
    "Commit thy works unto the Lord, and thy thoughts shall be established." 
    — Proverbs 16:3

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

from typing import Dict, Any
from tools.eos.autonomous_recovery.domain.recovery_incident import RecoveryIncident
from tools.eos.autonomous_recovery.domain.recovery_plan import RecoveryPlan, PlanStatus
from tools.eos.autonomous_recovery.planning.recovery_strategy import RecoveryStrategyMapper


class RecoveryPlanner:
    """
    Generates deterministic recovery plans for classified failure incidents.
    """

    @staticmethod
    def create_plan(incident: RecoveryIncident) -> RecoveryPlan:
        """
        Builds a comprehensive RecoveryPlan for an incident based on strategy mapping.
        """
        strategy = RecoveryStrategyMapper.get_strategy_for_incident(incident.incident_type)
        
        plan = RecoveryPlan(
            incident_id=incident.incident_id,
            strategy_name=strategy["strategy_name"],
            status=PlanStatus.DRAFT
        )

        for step_def in strategy["steps"]:
            plan.add_step(
                action_type=step_def["action_type"],
                target=step_def["target"],
                parameters={"source_subsystem": incident.source_subsystem}
            )

        return plan
