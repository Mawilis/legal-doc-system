"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
DOMAIN ENTITY: AUTONOMOUS DECISION
===============================================================================

File Path:
    tools/eos/autonomous/domain/autonomous_decision.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines the AutonomousDecision domain entity encapsulating the explainable,
    governed outcome of an autonomous policy and risk evaluation. Every decision
    contains cryptographic evidence, risk scoring, governing policy context,
    and institutional justification.

Biblical Worth Billions:
    "A wise man hearth, and will increase learning; and a man of understanding
    shall attain unto wise counsels."
    — Proverbs 1:5

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
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# --- ABSOLUTE PATH BOOTSTRAP GUARANTEE ---
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.eos.autonomous.domain.autonomous_action import AutonomousAction, ActionCategory, ActionPriority
from tools.eos.autonomous.domain.autonomous_policy import AutonomousPolicy, PolicyEffect, ApprovalLevel


class DecisionOutcome(str, Enum):
    """Institutional outcome states for an autonomous action decision."""
    APPROVED = "APPROVED"
    DENIED = "DENY"
    DEFERRED = "DEFERRED"
    REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
    ROLLBACK = "ROLLBACK"


@dataclass
class AutonomousDecision:
    """
    Sovereign domain entity capturing the outcome of an autonomous evaluation.

    Attributes:
        decision_id (str): Unique decision UUID v4 identifier.
        action_id (str): Target AutonomousAction identifier.
        action_type (str): Operational category name.
        outcome (DecisionOutcome): Sovereign outcome status.
        reason (str): Human-readable institutional rationale.
        evidence (Dict[str, Any]): Telemetry and evaluation proof vectors.
        policy_id (str): Identifier of the governing AutonomousPolicy.
        risk_score (float): Calculated risk score (0.0 to 100.0).
        approval_level_required (ApprovalLevel): Clearance level required.
        evaluated_by (str): Engine component identifier.
        created_at (str): ISO 8601 SAST timestamp.
        metadata (Dict[str, Any]): Auxiliary attributes.
    """
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    action_id: str = ""
    action_type: str = ""
    outcome: DecisionOutcome = DecisionOutcome.DEFERRED
    reason: str = "Decision pending evaluation."
    evidence: Dict[str, Any] = field(default_factory=dict)
    policy_id: str = "POL-DEFAULT-000"
    risk_score: float = 0.0
    approval_level_required: ApprovalLevel = ApprovalLevel.AUTOMATIC
    evaluated_by: str = "WilsyOS.AutonomousDecisionEngine"
    created_at: str = field(default_factory=lambda: datetime.now(timezone(timedelta(hours=2))).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> Tuple[bool, str]:
        """Validates decision structural integrity and value constraints."""
        try:
            if not self.decision_id or not isinstance(self.decision_id, str):
                return False, "Invalid or missing 'decision_id'."
            if not self.action_id or not isinstance(self.action_id, str):
                return False, "Invalid or missing 'action_id'."
            if not isinstance(self.outcome, DecisionOutcome):
                return False, f"Invalid outcome '{self.outcome}'."
            if not isinstance(self.approval_level_required, ApprovalLevel):
                return False, f"Invalid approval level '{self.approval_level_required}'."
            if not (0.0 <= self.risk_score <= 100.0):
                return False, f"risk_score ({self.risk_score}) out of range [0.0, 100.0]."
            return True, "VALID"
        except Exception as err:
            return False, f"Decision validation exception: {str(err)}"

    def compute_digest(self) -> str:
        """Computes SHA-256 cryptographic digest of the decision record."""
        payload = {
            "decision_id": self.decision_id,
            "action_id": self.action_id,
            "action_type": self.action_type,
            "outcome": self.outcome.value,
            "policy_id": self.policy_id,
            "risk_score": self.risk_score,
            "approval_level_required": self.approval_level_required.value,
            "reason": self.reason,
            "evidence": self.evidence,
            "created_at": self.created_at
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        return f"0x{digest}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes domain entity to a dictionary with cryptographic digest."""
        data = asdict(self)
        data["outcome"] = self.outcome.value
        data["approval_level_required"] = self.approval_level_required.value
        data["digest"] = self.compute_digest()
        return data

    @classmethod
    def from_action_and_policy(
        cls,
        action: AutonomousAction,
        policy: AutonomousPolicy,
        risk_score: float,
        effect: PolicyEffect,
        reason: str,
        evidence: Optional[Dict[str, Any]] = None
    ) -> "AutonomousDecision":
        """
        Factory method constructing an AutonomousDecision from an action and policy evaluation.
        """
        outcome_map = {
            PolicyEffect.ALLOW: DecisionOutcome.APPROVED,
            PolicyEffect.DENY: DecisionOutcome.DENIED,
            PolicyEffect.REQUIRES_EXECUTIVE_APPROVAL: DecisionOutcome.REQUIRES_APPROVAL,
            PolicyEffect.REQUIRES_ROLLBACK_PLAN: DecisionOutcome.APPROVED  # Requires plan before execution
        }
        
        outcome = outcome_map.get(effect, DecisionOutcome.DEFERRED)
        
        return cls(
            action_id=action.action_id,
            action_type=action.action_type,
            outcome=outcome,
            reason=reason,
            evidence=evidence or {"policy_name": policy.name, "effect": effect.value},
            policy_id=policy.policy_id,
            risk_score=risk_score,
            approval_level_required=policy.required_approval_level
        )


if __name__ == "__main__":
    # Institutional self-verification test block
    test_action = AutonomousAction(
        action_type="GENERATE_DOCS",
        category=ActionCategory.DOCUMENTATION,
        target_subsystem="tools/eos/documentation",
        priority=ActionPriority.HIGH
    )

    test_policy = AutonomousPolicy(
        policy_id="POL-DOC-001",
        name="Documentation Autonomous Policy",
        description="Governs automated doc generation",
        category=ActionCategory.DOCUMENTATION,
        effect=PolicyEffect.ALLOW,
        required_approval_level=ApprovalLevel.AUTOMATIC,
        max_allowed_risk_score=15.0
    )

    decision = AutonomousDecision.from_action_and_policy(
        action=test_action,
        policy=test_policy,
        risk_score=5.2,
        effect=PolicyEffect.ALLOW,
        reason="Documentation auto generation approved under policy POL-DOC-001."
    )

    is_valid, msg = decision.validate()
    digest = decision.compute_digest()

    print(f"✅ AutonomousDecision Entity Self-Check: {msg}")
    print(f"  - Decision ID: {decision.decision_id}")
    print(f"  - Target Action ID: {decision.action_id}")
    print(f"  - Outcome: {decision.outcome.value}")
    print(f"  - Risk Score: {decision.risk_score}")
    print(f"  - Digest: {digest[:24]}...")
    assert is_valid, "Decision validation failed!"
    assert digest.startswith("0x"), "Digest format invalid!"
    print("  - Status: GOLD_PRODUCTION_READY")
