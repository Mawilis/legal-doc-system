"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
APPLICATION SERVICE: POLICY ENGINE
===============================================================================

File Path:
    tools/eos/autonomous/application/policy_engine.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Implements the PolicyEngine application service responsible for evaluating 
    autonomous actions against active governance policies and calculating dynamic 
    risk metrics. Generates deterministic, cryptographic AutonomousDecision entities 
    that enforce non-negotiable operational boundaries across Wilsy OS.

Biblical Worth Billions:
    "By wisdom a house is built, and through understanding it is established;
    through knowledge its rooms are filled with rare and beautiful treasures."
    — Proverbs 24:3-4

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
from tools.eos.autonomous.domain.autonomous_policy import (
    AutonomousPolicy,
    PolicyEffect,
    ApprovalLevel,
)
from tools.eos.autonomous.domain.autonomous_decision import (
    AutonomousDecision,
    DecisionOutcome,
)


class PolicyEngine:
    """
    Sovereign Application Service governing policy evaluation and decision generation.
    """

    def __init__(self) -> None:
        """Initializes the Policy Engine registry."""
        self._policies: Dict[str, AutonomousPolicy] = {}

    def register_policy(self, policy: AutonomousPolicy) -> Tuple[bool, str]:
        """
        Registers a governing AutonomousPolicy in the engine memory registry.

        Args:
            policy (AutonomousPolicy): Policy domain entity to register.

        Returns:
            Tuple[bool, str]: Success flag and confirmation message.
        """
        valid, err = policy.validate()
        if not valid:
            return False, f"Policy validation failed: {err}"

        self._policies[policy.policy_id] = policy
        return True, f"Policy '{policy.policy_id}' ({policy.name}) successfully registered."

    def deregister_policy(self, policy_id: str) -> bool:
        """Removes a policy from active evaluation registry."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False

    def get_policy(self, policy_id: str) -> Optional[AutonomousPolicy]:
        """Retrieves registered policy by ID."""
        return self._policies.get(policy_id)

    def list_policies(self, category: Optional[ActionCategory] = None) -> List[AutonomousPolicy]:
        """Lists active policies, optionally filtered by ActionCategory."""
        policies = list(self._policies.values())
        if category:
            return [p for p in policies if p.category == category or p.category == ActionCategory.GENERAL]
        return policies

    def calculate_action_risk(self, action: AutonomousAction) -> float:
        """
        Calculates baseline risk score for an action based on priority, 
        subsystem critical score, and execution parameter constraints.

        Returns:
            float: Risk score bounded in range [0.0, 100.0].
        """
        base_risk = 5.0

        # Priority Weighting safely mapped via string representation
        priority_weights = {
            "LOW": 2.0,
            "MEDIUM": 10.0,
            "HIGH": 25.0,
            "CRITICAL": 50.0,
            "URGENT": 80.0,
            "EMERGENCY": 80.0,
        }
        
        priority_key = action.priority.value if hasattr(action.priority, "value") else str(action.priority)
        base_risk += priority_weights.get(priority_key, 10.0)

        # Subsystem Sensitivity Heuristic
        sensitive_subsystems = ["core", "database", "security", "vault", "auth", "billing"]
        if any(sub in action.target_subsystem.lower() for sub in sensitive_subsystems):
            base_risk += 15.0

        # Parameter Payload Mass / Complexity Adjustment
        if len(action.parameters) > 10:
            base_risk += 5.0

        return min(max(base_risk, 0.0), 100.0)

    def evaluate(self, action: AutonomousAction, override_risk_score: Optional[float] = None) -> AutonomousDecision:
        """
        Evaluates an AutonomousAction against all relevant registered policies.

        Args:
            action (AutonomousAction): The operational intent to evaluate.
            override_risk_score (Optional[float]): Explicit risk score if pre-computed.

        Returns:
            AutonomousDecision: Governed, explainable outcome entity with evidence digest.
        """
        valid_action, action_err = action.validate()
        if not valid_action:
            return AutonomousDecision(
                action_id=action.action_id,
                action_type=action.action_type,
                outcome=DecisionOutcome.DENIED,
                reason=f"Invalid action entity structure: {action_err}",
                risk_score=100.0,
                approval_level_required=ApprovalLevel.CHIEF_ARCHITECT
            )

        calculated_risk = override_risk_score if override_risk_score is not None else self.calculate_action_risk(action)
        relevant_policies = self.list_policies(action.category)

        # Default fallback if no category policies are registered
        if not relevant_policies:
            return AutonomousDecision(
                action_id=action.action_id,
                action_type=action.action_type,
                outcome=DecisionOutcome.DEFERRED,
                reason=f"No governing policy found for category '{action.category.value}'. Deferred for Chief Architect review.",
                risk_score=calculated_risk,
                approval_level_required=ApprovalLevel.CHIEF_ARCHITECT
            )

        # Evaluate against matching policies
        strictest_effect = PolicyEffect.ALLOW
        governing_policy = relevant_policies[0]
        evaluation_reasons = []

        for policy in relevant_policies:
            effect, reason = policy.evaluate_action(action, calculated_risk)
            evaluation_reasons.append(f"[{policy.policy_id}]: {reason}")

            # DENY overrides all other effects
            if effect == PolicyEffect.DENY:
                strictest_effect = PolicyEffect.DENY
                governing_policy = policy
                break
            elif effect == PolicyEffect.REQUIRES_EXECUTIVE_APPROVAL and strictest_effect != PolicyEffect.DENY:
                strictest_effect = PolicyEffect.REQUIRES_EXECUTIVE_APPROVAL
                governing_policy = policy
            elif effect == PolicyEffect.REQUIRES_ROLLBACK_PLAN and strictest_effect not in (PolicyEffect.DENY, PolicyEffect.REQUIRES_EXECUTIVE_APPROVAL):
                strictest_effect = PolicyEffect.REQUIRES_ROLLBACK_PLAN
                governing_policy = policy

        combined_reason = " | ".join(evaluation_reasons)
        evidence = {
            "policies_evaluated_count": len(relevant_policies),
            "governing_policy_id": governing_policy.policy_id,
            "calculated_risk_score": calculated_risk,
            "evaluation_trail": evaluation_reasons
        }

        return AutonomousDecision.from_action_and_policy(
            action=action,
            policy=governing_policy,
            risk_score=calculated_risk,
            effect=strictest_effect,
            reason=combined_reason,
            evidence=evidence
        )


if __name__ == "__main__":
    # Institutional self-verification test block
    engine = PolicyEngine()

    # Register default repository policy
    repo_policy = AutonomousPolicy(
        policy_id="POL-REPO-001",
        name="Repository Automation Governance",
        description="Governs automated code generation and refactoring operations",
        category=ActionCategory.REPOSITORY,
        effect=PolicyEffect.ALLOW,
        required_approval_level=ApprovalLevel.CHIEF_ARCHITECT,
        max_allowed_risk_score=30.0,
        requires_rollback=True,
        rules={"allowed_action_types": ["FORMAT_CODE", "RUN_TESTS", "SCAN_SECURITY"]}
    )

    reg_ok, reg_msg = engine.register_policy(repo_policy)
    print(f"✅ Policy Registration: {reg_msg}")

    # Test allowed action
    valid_action = AutonomousAction(
        action_type="SCAN_SECURITY",
        category=ActionCategory.REPOSITORY,
        target_subsystem="tools/eos/autonomous",
        priority=ActionPriority.LOW
    )

    decision = engine.evaluate(valid_action)

    print(f"✅ PolicyEngine Self-Check Evaluation Result:")
    print(f"  - Action ID: {valid_action.action_id}")
    print(f"  - Decision ID: {decision.decision_id}")
    print(f"  - Outcome: {decision.outcome.value}")
    print(f"  - Risk Score: {decision.risk_score}")
    print(f"  - Reason: {decision.reason}")
    print(f"  - Digest: {decision.compute_digest()[:24]}...")

    assert reg_ok, "Policy registration failed!"
    assert decision.outcome in (DecisionOutcome.APPROVED, DecisionOutcome.REQUIRES_APPROVAL), "Unexpected decision outcome!"
    assert decision.compute_digest().startswith("0x"), "Decision digest invalid!"
    print("  - Status: GOLD_PRODUCTION_READY")
