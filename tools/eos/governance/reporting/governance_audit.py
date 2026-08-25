from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE AUDIT PUBLISHER (FG177)
===============================================================================
Epitome:
    Artifact Bus publisher converting GovernanceDecisions into formal
    governance_audit_v1 compliance artifacts.

Biblical Worth Billions:
    "My covenant will I not break, nor alter the thing that is gone out of my lips."
    (Psalm 89:34). Direct artifact bus publication adhering to FG150.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/reporting/
    - File Path: tools/eos/governance/reporting/governance_audit.py
===============================================================================
"""

from typing import Any, Callable, Dict, Optional
from tools.eos.governance.domain.governance_decision import GovernanceDecision


class GovernanceAuditPublisher:
    """Publishes signed compliance artifacts directly to the Artifact Bus."""

    def __init__(
        self,
        artifact_bus_publisher: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> None:
        self.artifact_publisher = artifact_bus_publisher or self._default_publisher
        self.published_history: list[Dict[str, Any]] = []

    def _default_publisher(self, artifact_type: str, payload: Dict[str, Any]) -> None:
        self.published_history.append({"artifact_type": artifact_type, "payload": payload})

    def publish_decision(self, decision: GovernanceDecision) -> Dict[str, Any]:
        artifact_payload = {
            "artifact_schema": "governance_audit_v1",
            "execution_id": decision.execution_id,
            "status": decision.status.value,
            "checksum": decision.compute_checksum(),
            "decision": decision.to_dict(),
        }
        self.artifact_publisher("governance_audit_v1", artifact_payload)
        return artifact_payload
