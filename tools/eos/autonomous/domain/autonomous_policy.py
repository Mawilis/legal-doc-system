"""
===============================================================================
WILSY OS — FG224 AUTONOMOUS OPERATIONS ENGINE
DOMAIN ENTITY: AUTONOMOUS POLICY
===============================================================================

File Path:
    tools/eos/autonomous/domain/autonomous_policy.py

Version:
    v224.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Defines the AutonomousPolicy entity governing operational permissions, risk 
    thresholds, required approval levels, and rule evaluation for autonomous 
    actions within Wilsy OS. Serves as the institutional rulebook for the 
    Policy Engine.

Biblical Worth Billions:
    "To do justice and judgment is more acceptable to the Lord than sacrifice."
    — Proverbs 21:3

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

from tools.eos.autonomous.domain.autonomous_action import (
    AutonomousAction,
    ActionCategory,
    ActionPriority,
)


class PolicyEffect(str, Enum):
    """Institutional outcome effects produced by policy evaluation."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRES_EXECUTIVE_APPROVAL = "REQUIRES_EXECUTIVE_APPROVAL"
    REQUIRES_ROLLBACK_PLAN = "REQUIRES_ROLLBACK_PLAN"


class ApprovalLevel(str, Enum):
    """Required human or sovereign authority clearance levels."""
    AUTOMATIC = "AUTOMATIC"
    SYSTEM_OPERATOR = "SYSTEM_OPERATOR"
    CHIEF_ARCHITECT = "CHIEF_ARCHITECT"


@dataclass
class AutonomousPolicy:
    """
    Sovereign domain entity defining operational boundaries and rules.

    Attributes:
        policy_id (str): Unique policy identification key.
        name (str): Human-readable policy name.
        description (str): Detailed institutional purpose.
        category (ActionCategory): Target subsystem category.
        effect (PolicyEffect): Outcome effect when conditions match.
        required_approval_level (ApprovalLevel): Clearance level required.
        max_allowed_risk_score (float): Maximum risk score (0.0 to 100.0) before triggering DENY/APPROVAL.
        requires_rollback (bool): Whether a deterministic rollback plan is mandatory.
        rules (Dict[str, Any]): Structural rule conditions (e.g., allowed actions, param limits).
        is_active (bool): Operational status flag.
        version (str): Semantic versioning tag.
        created_at (str): ISO 8601 SAST timestamp.
    """
    policy_id: str
    name: str
    description: str
    category: ActionCategory
    effect: PolicyEffect = PolicyEffect.ALLOW
    required_approval_level: ApprovalLevel = ApprovalLevel.AUTOMATIC
    max_allowed_risk_score: float = 30.0
    requires_rollback: bool = True
    rules: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now(timezone(timedelta(hours=2))).isoformat())

    def validate(self) -> Tuple[bool, str]:
        """Validates domain policy structure and invariant rules."""
        try:
            if not self.policy_id or not isinstance(self.policy_id, str):
                return False, "Invalid or missing 'policy_id'."
            if not self.name or not isinstance(self.name, str):
                return False, "Invalid or missing 'name'."
            if not isinstance(self.category, ActionCategory):
                return False, f"Invalid category '{self.category}'."
            if not isinstance(self.effect, PolicyEffect):
                return False, f"Invalid effect '{self.effect}'."
            if not (0.0 <= self.max_allowed_risk_score <= 100.0):
                return False, f"max_allowed_risk_score ({self.max_allowed_risk_score}) must be between 0.0 and 100.0."
            return True, "VALID"
        except Exception as err:
            return False, f"Validation error in policy: {str(err)}"

    def evaluate_action(self, action: AutonomousAction, risk_score: float = 0.0) -> Tuple[PolicyEffect, str]:
        """
        Evaluates a target AutonomousAction against this policy rule set.

        Args:
            action (AutonomousAction): The operational intent.
            risk_score (float): Current calculated risk score.

        Returns:
            Tuple[PolicyEffect, str]: Evaluated effect and institutional justification.
        """
        if not self.is_active:
            return PolicyEffect.ALLOW, f"Policy '{self.policy_id}' is inactive. Evaluation bypassed."

        # Check Category Matching
        if action.category != self.category and self.category != ActionCategory.GENERAL:
            return PolicyEffect.ALLOW, f"Action category '{action.category.value}' does not match policy target '{self.category.value}'."

        # Check Allowed Action Types list if defined in rules
        allowed_types = self.rules.get("allowed_action_types")
        if allowed_types and action.action_type not in allowed_types:
            return PolicyEffect.DENY, f"Action type '{action.action_type}' is not in allowed list for policy '{self.name}'."

        # Check Disallowed Action Types list if defined in rules
        disallowed_types = self.rules.get("disallowed_action_types")
        if disallowed_types and action.action_type in disallowed_types:
            return PolicyEffect.DENY, f"Action type '{action.action_type}' is explicitly prohibited by policy '{self.name}'."

        # Risk Score Threshold Evaluation
        if risk_score > self.max_allowed_risk_score:
            if self.required_approval_level == ApprovalLevel.CHIEF_ARCHITECT:
                return PolicyEffect.REQUIRES_EXECUTIVE_APPROVAL, f"Risk score ({risk_score:.2f}) exceeds threshold ({self.max_allowed_risk_score:.2f}). Chief Architect approval required."
            elif self.required_approval_level == ApprovalLevel.SYSTEM_OPERATOR:
                return PolicyEffect.REQUIRES_EXECUTIVE_APPROVAL, f"Risk score ({risk_score:.2f}) exceeds threshold ({self.max_allowed_risk_score:.2f}). System Operator approval required."
            else:
                return PolicyEffect.DENY, f"Risk score ({risk_score:.2f}) exceeds policy maximum ({self.max_allowed_risk_score:.2f}). Action denied."

        # Mandatory Rollback Plan check
        if self.requires_rollback and self.effect == PolicyEffect.ALLOW:
            return PolicyEffect.REQUIRES_ROLLBACK_PLAN, f"Policy '{self.name}' mandates a verifiable rollback plan prior to execution."

        return self.effect, f"Action '{action.action_type}' passed evaluation under policy '{self.name}'."

    def compute_digest(self) -> str:
        """Computes SHA-256 cryptographic digest of the policy specification."""
        payload = {
            "policy_id": self.policy_id,
            "name": self.name,
            "category": self.category.value,
            "effect": self.effect.value,
            "required_approval_level": self.required_approval_level.value,
            "max_allowed_risk_score": self.max_allowed_risk_score,
            "requires_rollback": self.requires_rollback,
            "rules": self.rules,
            "version": self.version
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        return f"0x{digest}"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes policy entity to dictionary."""
        data = asdict(self)
        data["category"] = self.category.value
        data["effect"] = self.effect.value
        data["required_approval_level"] = self.required_approval_level.value
        data["digest"] = self.compute_digest()
        return data


if __name__ == "__main__":
    # Institutional self-verification test
    test_policy = AutonomousPolicy(
        policy_id="POL-REPO-001",
        name="Repository Governance Standard",
        description="Enforces verification and rollback on repository operations",
        category=ActionCategory.REPOSITORY,
        effect=PolicyEffect.ALLOW,
        required_approval_level=ApprovalLevel.CHIEF_ARCHITECT,
        max_allowed_risk_score=25.0,
        requires_rollback=True,
        rules={"allowed_action_types": ["REPOSITORY_SCAN", "GENERATE_DOCS"]}
    )

    is_valid, msg = test_policy.validate()
    digest = test_policy.compute_digest()

    action = AutonomousAction(
        action_type="REPOSITORY_SCAN",
        category=ActionCategory.REPOSITORY,
        target_subsystem="tools/eos/repository",
        priority=ActionPriority.MEDIUM
    )

    effect, reason = test_policy.evaluate_action(action, risk_score=10.0)

    print(f"✅ AutonomousPolicy Entity Self-Check: {msg}")
    print(f"  - Policy ID: {test_policy.policy_id}")
    print(f"  - Evaluated Effect: {effect.value}")
    print(f"  - Reason: {reason}")
    print(f"  - Digest: {digest[:24]}...")
    assert is_valid, "Policy validation failed!"
    assert digest.startswith("0x"), "Digest format invalid!"
    print("  - Status: GOLD_PRODUCTION_READY")
