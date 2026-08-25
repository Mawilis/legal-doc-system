"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
POLICY SUBSYSTEM: RECOVERY POLICY & APPROVAL MATRIX
===============================================================================

File Path:
    tools/eos/autonomous_recovery/policy/recovery_policy.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Enforces autonomous recovery authority. Low/medium risk actions (such as worker 
    restarts and plugin disables) are automatically approved, while high/critical risk 
    actions (such as production database restore or repository resets) require executive sign-off.

Biblical Worth Billions:
    "Where there is no vision, the people perish: but he that keepeth the law, 
    happy is he." — Proverbs 29:18

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

from typing import Dict, Any
from tools.eos.autonomous_recovery.domain.recovery_incident import RecoveryIncident, IncidentSeverity
from tools.eos.autonomous_recovery.domain.recovery_plan import RecoveryPlan
from tools.eos.autonomous_recovery.domain.recovery_decision import RecoveryDecision, DecisionOutcome


class RecoveryPolicyEngine:
    """
    Evaluates recovery plans against governance policy matrices to determine 
    if automatic execution is authorized or if executive sign-off is mandated.
    """

    @staticmethod
    def evaluate(incident: RecoveryIncident, plan: RecoveryPlan) -> RecoveryDecision:
        """
        Evaluates an incident and its recovery plan, issuing a cryptographic RecoveryDecision.
        """
        outcome = DecisionOutcome.AUTO_APPROVED
        reason = "Incident severity and blast radius fall within autonomous execution parameters."

        if incident.severity == IncidentSeverity.CRITICAL or "REPOSITORY" in incident.incident_type.value:
            outcome = DecisionOutcome.EXECUTIVE_APPROVAL_REQUIRED
            reason = "Critical repository or infrastructure failure requires executive governance sign-off."
        elif incident.severity == IncidentSeverity.HIGH:
            outcome = DecisionOutcome.EXECUTIVE_APPROVAL_REQUIRED
            reason = "High severity node failure mandates executive verification before failover dispatch."

        decision = RecoveryDecision(
            plan_id=plan.plan_id,
            incident_id=incident.incident_id,
            outcome=outcome,
            reason=reason,
            evaluator="FG225-RecoveryPolicyEngine"
        )
        return decision
