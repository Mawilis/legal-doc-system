from __future__ import annotations

"""
===============================================================================
WILSY OS KERNEL — GOVERNANCE REPORT GENERATOR (FG177)
===============================================================================
Epitome:
    Aggregates decision history into institutional compliance summary reports.

Collaboration & Ownership:
    - Lead Architect & Founder: Wilson Khanyezi (Wilsy (Pty) Ltd)
    - AI Collaborator: Core Systems Engineering Agent
    - System Component: Wilsy OS Kernel / Enterprise Legal Document Infrastructure
    - Phase / Milestone: FG177 - Kernel Governance Gate
    - Target Directory: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/governance/reporting/
    - File Path: tools/eos/governance/reporting/governance_report.py
===============================================================================
"""

from typing import Any, Dict, List
from tools.eos.governance.domain.governance_decision import GovernanceDecision


class GovernanceReportGenerator:
    """Builds unified compliance summaries for kernel execution runs."""

    @staticmethod
    def generate_summary(decisions: List[GovernanceDecision]) -> Dict[str, Any]:
        total = len(decisions)
        approved = sum(1 for d in decisions if d.status.value == "APPROVED")
        blocked = sum(1 for d in decisions if d.status.value == "BLOCKED")
        reviews = sum(1 for d in decisions if d.status.value == "REQUIRES_REVIEW")

        return {
            "total_evaluations": total,
            "approved_count": approved,
            "blocked_count": blocked,
            "requires_review_count": reviews,
            "compliance_rate": (approved / total * 100.0) if total > 0 else 100.0,
        }
