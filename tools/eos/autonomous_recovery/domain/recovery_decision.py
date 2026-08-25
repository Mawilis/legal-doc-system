"""
===============================================================================
WILSY OS — FG225 AUTONOMOUS RECOVERY ENGINE
DOMAIN SUBSYSTEM: RECOVERY DECISION
===============================================================================

File Path:
    tools/eos/autonomous_recovery/domain/recovery_decision.py

Version:
    v225.0.0-GOLD | Sovereign Production Artifact

Authority:
    Wilsy (Pty) Ltd — Enterprise Operating System Architecture

Epitome:
    Captures autonomous policy evaluation outcomes and approval matrix decisions 
    determining whether an incident recovery plan is automatically approved or 
    requires executive governance sign-off.

Biblical Worth Billions:
    "Where no counsel is, the people fall: but in the multitude of counsellors 
    there is safety." — Proverbs 11:14

Collaboration & Sovereign Sign-Off:
    - Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Lead Systems Engineering Agent
===============================================================================
"""

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any


class DecisionOutcome(str, Enum):
    """Outcomes of the autonomous recovery policy decision engine."""
    AUTO_APPROVED = "AUTO_APPROVED"
    EXECUTIVE_APPROVAL_REQUIRED = "EXECUTIVE_APPROVAL_REQUIRED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


@dataclass
class RecoveryDecision:
    """
    Represents the governance and policy evaluation decision governing 
    whether a recovery plan may proceed autonomously or demands escalation.
    """
    decision_id: str = field(default_factory=lambda: f"DEC-{uuid.uuid4().hex[:8].upper()}")
    plan_id: str = ""
    incident_id: str = ""
    outcome: DecisionOutcome = DecisionOutcome.DEFERRED
    reason: str = ""
    evaluator: str = "FG225-RecoveryPolicyEngine"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checksum: str = field(init=False)

    def __post_init__(self) -> None:
        """Computes cryptographic integrity checksum upon decision creation."""
        self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Generates a SHA-256 cryptographic hash of the decision attributes."""
        raw_data = f"{self.decision_id}:{self.plan_id}:{self.incident_id}:{self.outcome}:{self.created_at}"
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the recovery decision into a dictionary representation."""
        return {
            "decision_id": self.decision_id,
            "plan_id": self.plan_id,
            "incident_id": self.incident_id,
            "outcome": self.outcome.value,
            "reason": self.reason,
            "evaluator": self.evaluator,
            "created_at": self.created_at,
            "checksum": self.checksum
        }
