from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE DECISION DOMAIN MODEL (FG177)
===============================================================================
Epitome:
    Immutable execution outcome domain entity sealed with cryptographic hashes.

Biblical Worth Billions:
    "A false balance is abomination to the Lord: but a just weight is his delight."
    (Proverbs 11:1). Immutable, cryptographically verifiable governance outcomes.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/domain/
    - File Path: tools/eos/governance/domain/governance_decision.py
===============================================================================
"""

import hashlib
import json

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List


class GovernanceStatus(str, Enum):
    APPROVED = "APPROVED"
    BLOCKED = "BLOCKED"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class GovernanceDecision:
    """Immutable evaluation artifact produced by the GovernanceEngine."""

    def __init__(
        self,
        execution_id: str,
        status: GovernanceStatus,
        evaluated_policies: List[str],
        violations: List[Dict[str, Any]],
        triggers: List[Dict[str, Any]],
        approval_reason: str = "",
        timestamp: str | None = None,
    ) -> None:
        self.execution_id = execution_id
        self.status = status
        self.evaluated_policies = evaluated_policies
        self.violations = violations
        self.triggers = triggers
        self.approval_reason = approval_reason
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def compute_checksum(self) -> str:
        payload = {
            "execution_id": self.execution_id,
            "status": self.status.value,
            "evaluated_policies": self.evaluated_policies,
            "violations": self.violations,
            "triggers": self.triggers,
            "approval_reason": self.approval_reason,
            "timestamp": self.timestamp,
        }
        raw_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "status": self.status.value,
            "evaluated_policies": self.evaluated_policies,
            "violations": self.violations,
            "triggers": self.triggers,
            "approval_reason": self.approval_reason,
            "timestamp": self.timestamp,
            "checksum": self.compute_checksum(),
        }
