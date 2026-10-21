"""TITLE: WILSY OS Practitioner Confidentiality Review Decision Certificate.
VERSION: v1.0.0-P47-R95-G58-DOMAIN-CERT
AUTHORITY: Pure-domain verification only.
EPITOME: Freezes practitioner-specific review evidence without granting access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_practitioner_confidentiality_review_decision.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 establishes the G58 domain certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references only; no privileged narrative.
TENANT BOUNDARY: Exact tenant, matter and practitioner scope.
AUTHORITY BOUNDARY: Recorded review evidence never grants operational access.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_review_decision import (
    ConfidentialityReviewDecision,
    ConfidentialityReviewDecisionError,
    ConfidentialityReviewDecisionState,
    ConfidentialityReviewCurrentnessState,
    EthicalWallRequirement,
    project_confidentiality_review_currentness,
)

NOW = datetime(2026, 10, 21, 12, 0, tzinfo=UTC)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128


def make(**changes: object) -> ConfidentialityReviewDecision:
    values: dict[str, object] = {
        "decision_id": "decision-1", "tenant_id": "tenant-a",
        "case_matter_id": "matter-a", "practitioner_principal_id": "p-target",
        "reviewer_principal_id": "p-reviewer", "predecessor_decision_id": None,
        "decision": ConfidentialityReviewDecisionState.APPROVED,
        "decided_at": NOW, "expires_at": NOW + timedelta(days=30),
        "reviewer_authorization_evidence_reference": "iam-evidence-1",
        "reviewer_authorization_evidence_fingerprint": HEX_A,
        "conflict_disposition_reference": "disposition-1",
        "conflict_disposition_fingerprint": HEX_B,
        "screening_evidence_reference": "screening-1",
        "screening_evidence_fingerprint": HEX_C,
        "ethical_wall_requirement": EthicalWallRequirement.REQUIRED,
        "ethical_wall_policy_reference": "wall-policy-1",
        "ethical_wall_policy_fingerprint": HEX_D,
        "ethical_wall_satisfaction_reference": "wall-satisfaction-1",
        "ethical_wall_satisfaction_fingerprint": "e" * 128,
    }
    values.update(changes)
    return ConfidentialityReviewDecision(**values)  # type: ignore[arg-type]


def test_approved_record_is_deterministic_but_never_authorizing() -> None:
    left = make()
    right = make()
    assert left == right
    assert len(left.fingerprint) == 128
    assert left.permits_operational_access is False


def test_self_review_and_unverified_wall_inputs_fail_closed() -> None:
    with pytest.raises(ConfidentialityReviewDecisionError, match="SELF_REVIEW"):
        make(reviewer_principal_id="p-target")
    with pytest.raises(ConfidentialityReviewDecisionError, match="WALL_SATISFACTION_REQUIRED"):
        make(ethical_wall_satisfaction_reference=None,
             ethical_wall_satisfaction_fingerprint=None)


def test_not_required_wall_still_needs_independent_policy_provenance() -> None:
    value = make(
        ethical_wall_requirement=EthicalWallRequirement.NOT_REQUIRED,
        ethical_wall_satisfaction_reference=None,
        ethical_wall_satisfaction_fingerprint=None,
    )
    assert value.ethical_wall_policy_reference == "wall-policy-1"
    with pytest.raises(ConfidentialityReviewDecisionError, match="WALL_POLICY_REQUIRED"):
        make(ethical_wall_requirement=EthicalWallRequirement.NOT_REQUIRED,
             ethical_wall_policy_reference=None,
             ethical_wall_policy_fingerprint=None,
             ethical_wall_satisfaction_reference=None,
             ethical_wall_satisfaction_fingerprint=None)


def test_denial_and_revocation_are_terminal_successors() -> None:
    approved = make()
    revoked = make(
        decision_id="decision-2", predecessor_decision_id=approved.decision_id,
        decision=ConfidentialityReviewDecisionState.REVOKED,
        decided_at=NOW + timedelta(days=1), expires_at=NOW + timedelta(days=30),
    )
    projected = project_confidentiality_review_currentness(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="p-target", evaluation_time=NOW + timedelta(days=2),
        decisions=(approved, revoked),
    )
    assert projected.state is ConfidentialityReviewCurrentnessState.REVOKED_BLOCKED
    assert projected.permits_operational_access is False


def test_recorded_approval_is_explicitly_unverified_and_expires() -> None:
    approved = make()
    current = project_confidentiality_review_currentness(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="p-target", evaluation_time=NOW,
        decisions=(approved,),
    )
    expired = project_confidentiality_review_currentness(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="p-target", evaluation_time=NOW + timedelta(days=31),
        decisions=(approved,),
    )
    assert current.state is ConfidentialityReviewCurrentnessState.APPROVED_RECORDED_UNVERIFIED
    assert expired.state is ConfidentialityReviewCurrentnessState.EXPIRED_BLOCKED


def test_cross_scope_fork_and_tampering_corrupt_block() -> None:
    approved = make()
    cross_scope = make(decision_id="decision-2", tenant_id="tenant-b")
    fork = make(decision_id="decision-3", predecessor_decision_id=approved.decision_id,
                decision=ConfidentialityReviewDecisionState.DENIED,
                decided_at=NOW + timedelta(days=1))
    other_fork = replace(fork, decision_id="decision-4")
    tampered = object.__new__(ConfidentialityReviewDecision)
    for field in approved.__dataclass_fields__:
        object.__setattr__(tampered, field, getattr(approved, field))
    object.__setattr__(tampered, "fingerprint", "f" * 128)
    for history in ((approved, cross_scope), (approved, fork, other_fork), (tampered,)):
        result = project_confidentiality_review_currentness(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="p-target", evaluation_time=NOW + timedelta(days=2),
            decisions=history,
        )
        assert result.state is ConfidentialityReviewCurrentnessState.CORRUPT_BLOCKED


# ARTIFACT: test_legal_work_practitioner_confidentiality_review_decision.py
# VERSION: v1.0.0-P47-R95-G58-DOMAIN-CERT
# AUTHORITY BOUNDARY: pure non-authorizing domain verification only
# TENANT POSTURE: exact tenant, matter and practitioner scope
# FAIL-CLOSED POSTURE: missing provenance, self-review, forks and tampering reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
