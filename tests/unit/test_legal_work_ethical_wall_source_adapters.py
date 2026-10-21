"""TITLE: WILSY OS G78 Ethical-Wall Canonical Source Adapter Certificate.
VERSION: v1.0.0-G78-CANONICAL-SOURCE-ADAPTER-CERT
AUTHORITY: Transaction-bound source read verification only.
EPITOME: Certifies IAM composition and exact binding, assignment, conflict,
review and G76-B policy adapters without granting operational access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_ethical_wall_source_adapters.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 establishes G78 adapter verification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant, matter and practitioner predicates.
AUTHORITY BOUNDARY: Adapters return canonical evidence, never grants.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import LegalPractitionerMatterBinding
from tools.eos.legal_operations.domain.legal_work_assignment import LegalWorkAssignment
from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_review_decision import (
    ConfidentialityReviewDecision, ConfidentialityReviewDecisionState, EthicalWallRequirement,
)
from tools.eos.legal_operations.service import legal_work_ethical_wall_source_adapters as adapters

NOW = datetime(2026, 10, 21, 16, 0, tzinfo=UTC)


class Session:
    in_transaction = True


class Cursor(list[dict[str, object]]):
    def limit(self, maximum: int) -> "Cursor":
        return Cursor(self[:maximum])


class Collection:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        assert session.in_transaction is True  # type: ignore[union-attr]
        return Cursor([dict(row) for row in self.rows if all(row.get(k) == v for k, v in query.items())])


def binding() -> LegalPractitionerMatterBinding:
    matter = CaseMatter(
        tenant_id="tenant-a", case_matter_id="matter-a", matter_reference="MAT-A",
        opened_at=NOW - timedelta(days=2), evidence_reference="matter-evidence-a",
    )
    return LegalPractitionerMatterBinding.grant(
        binding_id="binding-a", case_matter=matter,
        practitioner_principal_id="practitioner-a", granted_by_principal_id="partner-a",
        granted_at=NOW - timedelta(days=1), evidence_reference="binding-evidence-a",
    )


def assignment() -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id="assignment-a", tenant_id="tenant-a", case_matter_id="matter-a",
        work_item_id="work-a", assignee_principal_id="practitioner-a",
        assigned_by_principal_id="partner-a", assigned_at=NOW,
        assignment_reason_reference="reason-a", authorization_evidence_reference="auth-a",
    )


def review() -> ConfidentialityReviewDecision:
    return ConfidentialityReviewDecision(
        decision_id="review-a", tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="practitioner-a", reviewer_principal_id="reviewer-a",
        predecessor_decision_id=None, decision=ConfidentialityReviewDecisionState.APPROVED,
        decided_at=NOW, expires_at=NOW + timedelta(days=1),
        reviewer_authorization_evidence_reference="reviewer-auth-a",
        reviewer_authorization_evidence_fingerprint="1" * 128,
        conflict_disposition_reference="disposition-a",
        conflict_disposition_fingerprint="2" * 128,
        screening_evidence_reference="screening-a", screening_evidence_fingerprint="3" * 128,
        ethical_wall_requirement=EthicalWallRequirement.REQUIRED,
        ethical_wall_policy_reference="wall-a", ethical_wall_policy_fingerprint="4" * 128,
        ethical_wall_satisfaction_reference="satisfaction-a",
        ethical_wall_satisfaction_fingerprint="5" * 128,
    )


@pytest.mark.parametrize("session", [None, SimpleNamespace(in_transaction=False)])
def test_every_adapter_requires_active_caller_transaction(session: object) -> None:
    source = adapters.CanonicalPractitionerBindingSource(Collection([]))
    with pytest.raises(adapters.EthicalWallSourceUnavailable, match="TRANSACTION_REQUIRED"):
        source.resolve_current(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", session=session,
        )


def test_binding_adapter_hydrates_exact_active_scope_and_rejects_revocation() -> None:
    active = binding()
    source = adapters.CanonicalPractitionerBindingSource(Collection([active.to_dict()]))
    assert source.resolve_current(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="practitioner-a", session=Session(),
    ) == active
    revoked = active.revoke(
        revoked_by_principal_id="partner-a", revoked_at=NOW,
        evidence_reference="revocation-a",
    )
    source = adapters.CanonicalPractitionerBindingSource(
        Collection([active.to_dict(), revoked.to_dict()])
    )
    with pytest.raises(adapters.EthicalWallSourceUnavailable, match="BINDING_REVOKED"):
        source.resolve_current(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", session=Session(),
        )


def test_assignment_adapter_filters_registry_currentness_to_exact_matter() -> None:
    class Registry:
        def list_current_for_assignee(self, tenant_id: str, principal_id: str, *, session: object) -> tuple[LegalWorkAssignment, ...]:
            return (assignment(),)

    source = adapters.CanonicalMatterAssignmentSource(Registry())
    assert source.resolve_current(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="practitioner-a", session=Session(),
    ) == (assignment(),)
    with pytest.raises(adapters.EthicalWallSourceUnavailable, match="ASSIGNMENT_NOT_FOUND"):
        source.resolve_current(
            tenant_id="tenant-a", case_matter_id="matter-b",
            practitioner_principal_id="practitioner-a", session=Session(),
        )


def test_review_adapter_strictly_hydrates_current_linear_history() -> None:
    value = review()
    source = adapters.CanonicalConfidentialityReviewSource(
        Collection([adapters.encode_confidentiality_review(value)]), NOW,
    )
    assert source.resolve_current(
        tenant_id="tenant-a", case_matter_id="matter-a",
        practitioner_principal_id="practitioner-a", session=Session(),
    ) == value


def test_review_adapter_rejects_forgery_and_self_review() -> None:
    document = adapters.encode_confidentiality_review(review())
    document["reviewer_principal_id"] = "practitioner-a"
    source = adapters.CanonicalConfidentialityReviewSource(Collection([document]), NOW)
    with pytest.raises(adapters.EthicalWallSourceUnavailable, match="REVIEW_INVALID"):
        source.resolve_current(
            tenant_id="tenant-a", case_matter_id="matter-a",
            practitioner_principal_id="practitioner-a", session=Session(),
        )


def test_adapters_expose_no_access_or_content_reader() -> None:
    assert adapters.SOURCE_VERIFIED_CLEARANCE is False
    assert adapters.OPERATIONAL_ACCESS_ENABLED is False
    assert not hasattr(adapters, "authorize_content")
    assert not hasattr(adapters, "read_content")


# ARTIFACT: test_legal_work_ethical_wall_source_adapters.py
# VERSION: v1.0.0-G78-CANONICAL-SOURCE-ADAPTER-CERT
# AUTHORITY BOUNDARY: canonical source reads only; no access grant
# TENANT POSTURE: exact tenant/matter/practitioner
# FAIL-CLOSED POSTURE: missing, revoked, corrupt or foreign evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
