from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE ENGINE: DECISION ARTIFACTS (FG177)
===============================================================================
Epitome:
    Immutable governance evaluation decision records, outcome statuses, and 
    cryptographic authorization proofs for the Wilsy OS Kernel.

Biblical Worth Billions:
    Uncompromising righteous judgments establishing structural truth and law 
    (Proverbs 21:3, Deuteronomy 16:18). Serves as an unalterable seal of 
    authorization before any execution context enters the runtime scheduler. 
    No child's place.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/
    - File Path: tools/eos/governance/governance_decision.py

Architectural Role & How It Fits:
    `governance_decision.py` provides the output artifact from `GovernanceEngine.evaluate()`.
    The decision artifact acts as a gatekeeper token:
      - APPROVED: Execution proceeds directly to the Execution Scheduler.
      - REQUIRES_REVIEW: Execution halts; report is published to the Event Bus awaiting authorization.
      - BLOCKED: Execution terminates immediately with zero resource allocation.
===============================================================================
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional


class GovernanceStatus(str, Enum):
    """
    Epitome: Final authorization disposition of a kernel execution request.
    Biblical Worth Billions: Unambiguous judgment status for system compliance.
    Collaboration Note: Evaluated by Kernel Runtime to determine execution branch.
    """
    APPROVED = "APPROVED"               # Request fully complies with active policies
    BLOCKED = "BLOCKED"                 # Request violates critical/strict policies; execution halted
    REQUIRES_REVIEW = "REQUIRES_REVIEW"# Request triggers audit/warning thresholds; human-in-the-loop required


@dataclass(frozen=True)
class GovernanceDecision:
    """
    Epitome: Immutable decision artifact recording authorization outcomes for an execution request.
    Biblical Worth Billions: Sealed judgment record with SHA-256 cryptographic auditability.
    Collaboration Note: Produced exclusively by `GovernanceEngine.evaluate()`.
    
    Attributes:
        decision_id (str): Unique identifier for this evaluation event (e.g., "DEC-20260722-001").
        execution_id (str): Reference ID of the target ExecutionContext being authorized.
        status (GovernanceStatus): Final outcome (APPROVED, BLOCKED, REQUIRES_REVIEW).
        timestamp (datetime): UTC temporal marker when evaluation was performed.
        violated_policies (List[Dict[str, Any]]): Details of policies failed during evaluation.
        warnings (List[str]): Non-blocking warning messages produced during rule checks.
        approval_reason (str): Clear justification summary explaining the status.
        metadata (Dict[str, Any]): Additional operational context or execution parameters evaluated.
    """
    decision_id: str
    execution_id: str
    status: GovernanceStatus
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    violated_policies: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    approval_reason: str = "Policy evaluation completed normally."
    metadata: Dict[str, Any] = field(default_factory=dict)

    def compute_checksum(self) -> str:
        """
        Calculates a SHA-256 cryptographic checksum locking the decision state.
        Production Ready: Ensures canonical sorting and ISO-8601 formatting for temporal attributes.
        
        Returns:
            str: 64-character hexadecimal SHA-256 string guarantee.
        """
        canonical_payload = {
            "decision_id": self.decision_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "violated_policies": self.violated_policies,
            "warnings": self.warnings,
            "approval_reason": self.approval_reason,
        }
        serialized_data = json.dumps(canonical_payload, sort_keys=True)
        return hashlib.sha256(serialized_data.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the governance decision into a standard dictionary format.
        Production Ready: Formats datetimes to ISO-8601 and includes computed checksum for transport.
        
        Returns:
            Dict[str, Any]: Standardized decision dictionary.
        """
        return {
            "decision_id": self.decision_id,
            "execution_id": self.execution_id,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "violated_policies": self.violated_policies,
            "warnings": self.warnings,
            "approval_reason": self.approval_reason,
            "metadata": self.metadata,
            "checksum": self.compute_checksum(),
        }
