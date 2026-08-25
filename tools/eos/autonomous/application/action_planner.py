"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
APPLICATION SERVICE: ACTION PLANNER
===============================================================================

File Path:
    tools/eos/autonomous/application/action_planner.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Implements the ActionPlanner application service responsible for translating
    governed autonomous actions and policy decisions into executable step-by-step 
    AutonomousPlan entities. Synthesizes execution sequences, pre/post-conditions,
    estimated duration metrics, and automated rollback workflows.

Biblical Worth Billions:
    "For which of you, intending to build a tower, sitteth not down first, 
    and counteth the cost, whether he have sufficient to finish it?"
    — Luke 14:28

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.eos.autonomous.domain.autonomous_action import (
    AutonomousAction,
    ActionCategory,
    ActionPriority,
)
from tools.eos.autonomous.domain.autonomous_decision import (
    AutonomousDecision,
    DecisionOutcome,
)
from tools.eos.autonomous.domain.autonomous_plan import (
    AutonomousPlan,
    PlanStep,
    PlanStatus,
)


class ActionPlanner:
    """
    Sovereign Application Service for decomposing actions into deterministic execution plans.
    """

    def __init__(self, default_estimated_duration_ms: float = 1000.0) -> None:
        """
        Initializes the Action Planner service.

        Args:
            default_estimated_duration_ms (float): Baseline estimated execution time in ms.
        """
        self.default_estimated_duration_ms = default_estimated_duration_ms

    def generate_plan(
        self,
        action: AutonomousAction,
        decision: AutonomousDecision
    ) -> Tuple[Optional[AutonomousPlan], str]:
        """
        Decomposes a governed AutonomousAction into an executable AutonomousPlan.

        Args:
            action (AutonomousAction): The operational action intent.
            decision (AutonomousDecision): Policy decision authorizing or constraining action.

        Returns:
            Tuple[Optional[AutonomousPlan], str]: Generated AutonomousPlan and status message.
        """
        valid_action, err_action = action.validate()
        if not valid_action:
            return None, f"Action validation failed: {err_action}"

        valid_dec, err_dec = decision.validate()
        if not valid_dec:
            return None, f"Decision validation failed: {err_dec}"

        # Reject plan generation if action was DENIED
        if decision.outcome == DecisionOutcome.DENIED:
            return None, f"Cannot generate plan for DENIED action '{action.action_id}': {decision.reason}"

        plan = AutonomousPlan(
            plan_id=str(uuid.uuid4()),
            action_id=action.action_id,
            decision_id=decision.decision_id,
            title=f"Execution Plan: {action.action_type} on {action.target_subsystem}",
            status=PlanStatus.PLANNED,
            estimated_duration_ms=self.default_estimated_duration_ms,
            metadata={
                "target_subsystem": action.target_subsystem,
                "category": action.category.value if hasattr(action.category, "value") else str(action.category),
                "generated_at": datetime.now(timezone(timedelta(hours=2))).isoformat(),
                "governing_policy_id": getattr(decision, "governing_policy_id", getattr(decision, "policy_id", ""))
            }
        )

        # Populate steps onto the plan
        self._populate_steps(plan, action, decision)

        valid_plan, err_plan = plan.validate()
        if not valid_plan:
            return None, f"Synthesized AutonomousPlan failed validation: {err_plan}"

        return plan, f"Successfully generated AutonomousPlan containing {len(plan.steps)} steps."

    def _populate_steps(
        self,
        plan: AutonomousPlan,
        action: AutonomousAction,
        decision: AutonomousDecision
    ) -> None:
        """
        Decomposes action into concrete PlanSteps and adds them via plan.add_step().
        """
        act_type = action.action_type.upper()
        target = action.target_subsystem

        if act_type == "SCAN_SECURITY":
            plan.add_step(
                name="Validate Target Subsystem Path",
                subsystem=target,
                action="VERIFY_PATH",
                parameters={"path": target},
                rollback_action="NONE",
                is_critical=True
            )
            plan.add_step(
                name="Execute Static Security Analysis",
                subsystem=target,
                action="RUN_SECURITY_SCAN",
                parameters={"depth": "FULL", "target": target},
                rollback_action="NONE",
                is_critical=True
            )

        elif act_type == "FORMAT_CODE":
            plan.add_step(
                name="Create Temporary Snapshot",
                subsystem=target,
                action="CREATE_SNAPSHOT",
                parameters={"path": target},
                rollback_action="RESTORE_SNAPSHOT",
                is_critical=True
            )
            plan.add_step(
                name="Apply Code Formatting Standard",
                subsystem=target,
                action="FORMAT_FILES",
                parameters={"path": target, "standard": "FG224"},
                rollback_action="RESTORE_SNAPSHOT",
                is_critical=True
            )

        else:
            plan.add_step(
                name=f"Pre-Execution Inspection [{act_type}]",
                subsystem=target,
                action="INSPECT_STATE",
                parameters=action.parameters,
                rollback_action="NONE",
                is_critical=True
            )
            plan.add_step(
                name=f"Execute Primary Action Payload [{act_type}]",
                subsystem=target,
                action=act_type,
                parameters=action.parameters,
                rollback_action="REVERT_STATE" if getattr(action, "requires_rollback", False) else None,
                is_critical=True
            )
            plan.add_step(
                name=f"Post-Execution Verification [{act_type}]",
                subsystem=target,
                action="VERIFY_HEALTH",
                parameters={"target": target},
                rollback_action="NONE",
                is_critical=False
            )


if __name__ == "__main__":
    # Institutional self-verification test block
    from tools.eos.autonomous.domain.autonomous_policy import ApprovalLevel

    planner = ActionPlanner()

    action = AutonomousAction(
        action_type="SCAN_SECURITY",
        category=ActionCategory.REPOSITORY,
        target_subsystem="tools/eos/autonomous",
        priority=ActionPriority.LOW
    )

    approval_lvl = getattr(ApprovalLevel, "CHIEF_ARCHITECT", list(ApprovalLevel)[0])

    decision = AutonomousDecision(
        action_id=action.action_id,
        outcome=DecisionOutcome.APPROVED,
        reason="Action satisfies repository governance policy POL-REPO-001.",
        risk_score=7.0,
        approval_level_required=approval_lvl
    )

    plan, msg = planner.generate_plan(action, decision)

    print(f"✅ ActionPlanner Self-Check Result: {msg}")
    if plan:
        print(f"  - Plan ID: {plan.plan_id}")
        print(f"  - Action ID: {plan.action_id}")
        print(f"  - Decision ID: {plan.decision_id}")
        print(f"  - Total Steps: {len(plan.steps)}")
        print(f"  - Total Rollback Steps: {len(plan.rollback_steps)}")
        print(f"  - Status: {plan.status.value}")
        print(f"  - Digest: {plan.compute_digest()[:24]}...")

        is_valid, val_err = plan.validate()
        assert is_valid, f"Generated plan failed validation: {val_err}"
        assert len(plan.steps) >= 2, "Expected at least 2 steps in generated plan!"
        assert plan.compute_digest().startswith("0x"), "Plan digest invalid!"
        print("  - Status: GOLD_PRODUCTION_READY")
    else:
        sys.exit(1)
