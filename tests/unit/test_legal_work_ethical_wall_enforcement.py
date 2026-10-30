"""TITLE: WILSY OS G77 Source-Verified Ethical-Wall Enforcement Certificate.
VERSION: v1.0.1-G77-DENIAL-ADVERSARIAL-EXPANSION
AUTHORITY: Negative enforcement and canonical-source validation only.
EPITOME: Certifies transaction, IAM, binding, assignment, conflict, review and
wall-source verification while institutional authority remains unavailable.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_ethical_wall_enforcement.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering / Legal Operations.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-26 v1.0.1 expands expiry, separation-of-duties, cross-scope, revocation and history-pointer denial cases; no positive authorization.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant, matter and authenticated principal.
AUTHORITY BOUNDARY: No positive content or operational access result exists.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    LegalClientMatterConflictDispositionCurrentness,
    LegalClientMatterConflictDispositionCurrentnessReason,
    LegalClientMatterConflictDispositionCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import (
    LegalPractitionerMatterBinding,
)
from tools.eos.legal_operations.domain.legal_work_assignment import LegalWorkAssignment
from tools.eos.legal_operations.domain.legal_work_ethical_wall_policy import (
    EthicalWallPolicyRevision,
    EthicalWallPolicyStatus,
    InstitutionalRatificationState,
)
from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_review_decision import (
    ConfidentialityReviewDecision,
    ConfidentialityReviewDecisionState,
    EthicalWallRequirement,
)
from tools.eos.legal_operations.domain.legal_work_ethical_wall_membership_acknowledgement import (
    WallMembershipEvidence, WallAcknowledgementEvidence,
    MembershipState, AcknowledgementState,
)
from tools.eos.legal_operations.service import legal_work_ethical_wall_enforcement as service

NOW = datetime(2026, 10, 21, 15, 0, tzinfo=UTC)


class Session:
    in_transaction = True


class Source:
    def __init__(self, value: object) -> None:
        self.value = value
        self.calls = 0

    def resolve_current(self, **kwargs: object) -> object:
        assert kwargs["session"].in_transaction is True  # type: ignore[union-attr]
        self.calls += 1
        return self.value


def matter() -> CaseMatter:
    return CaseMatter(
        case_matter_id="matter-a", tenant_id="tenant-a",
        matter_reference="matter-ref-a", opened_at=NOW - timedelta(days=2),
        evidence_reference="matter-open-evidence-a", state=CaseMatterState.OPEN,
    )


def binding() -> LegalPractitionerMatterBinding:
    return LegalPractitionerMatterBinding.grant(
        binding_id="binding-a", case_matter=matter(),
        practitioner_principal_id="practitioner-a",
        granted_by_principal_id="partner-a", granted_at=NOW - timedelta(days=1),
        evidence_reference="binding-evidence-a",
    )


def assignment() -> LegalWorkAssignment:
    return LegalWorkAssignment(
        assignment_id="assignment-a", tenant_id="tenant-a",
        case_matter_id="matter-a", work_item_id="work-a",
        assignee_principal_id="practitioner-a", assigned_by_principal_id="partner-a",
        assigned_at=NOW - timedelta(hours=12), assignment_reason_reference="reason-a",
        authorization_evidence_reference="assignment-auth-a",
    )


def conflict() -> LegalClientMatterConflictDispositionCurrentness:
    return LegalClientMatterConflictDispositionCurrentness(
        currentness_id="conflict-current-a", tenant_id="tenant-a",
        case_matter_id="matter-a", matter_fingerprint=matter().fingerprint,
        client_party_id="client-a", subject_identity_fingerprint="1" * 128,
        evaluation_time=NOW, decisive_effective_from=NOW - timedelta(days=1),
        decisive_disposition_ids=("disposition-a",),
        decisive_disposition_fingerprints=("2" * 128,),
        decisive_dispositions=("ENGAGEMENT_PERMITTED",),
        decisive_screening_ids=("screening-a",),
        decisive_screening_fingerprints=("3" * 128,),
        decisive_conflict_review_ids=("conflict-review-a",),
        decisive_conflict_review_fingerprints=("4" * 128,),
        decisive_review_outcomes=("NO_CONFLICT_IDENTIFIED",),
        corruption_evidence_fingerprints=(),
        state=LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED,
        reason=LegalClientMatterConflictDispositionCurrentnessReason.ENGAGEMENT_PERMITTED,
    )


def policy(**changes: object) -> EthicalWallPolicyRevision:
    values: dict[str, object] = {
        "policy_id": "wall-1", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a",
        "protected_subject_fingerprints": ("1" * 128,),
        "restricted_principal_ids": ("principal-denied",),
        "permitted_principal_ids": ("practitioner-a",),
        "status": EthicalWallPolicyStatus.ACTIVE,
        "effective_from": NOW - timedelta(days=1),
        "effective_until": NOW + timedelta(days=30),
        "source_evidence_reference": "source-a", "source_evidence_fingerprint": "5" * 128,
        "administrator_principal_id": "admin-a",
        "administrator_authorization_reference": "admin-auth-a",
        "administrator_authorization_fingerprint": "6" * 128,
        "ratification_state": InstitutionalRatificationState.APPROVED,
        "ratification_reference": "ratification-a", "ratification_fingerprint": "7" * 128,
    }
    values.update(changes)
    return EthicalWallPolicyRevision(**values)  # type: ignore[arg-type]


def review(wall: EthicalWallPolicyRevision, **changes: object) -> ConfidentialityReviewDecision:
    values: dict[str, object] = {
        "decision_id": "review-a", "tenant_id": "tenant-a",
        "case_matter_id": "matter-a", "practitioner_principal_id": "practitioner-a",
        "reviewer_principal_id": "reviewer-a", "predecessor_decision_id": None,
        "decision": ConfidentialityReviewDecisionState.APPROVED,
        "decided_at": NOW - timedelta(hours=1), "expires_at": NOW + timedelta(days=2),
        "reviewer_authorization_evidence_reference": "reviewer-auth-a",
        "reviewer_authorization_evidence_fingerprint": "8" * 128,
        "conflict_disposition_reference": "disposition-a",
        "conflict_disposition_fingerprint": "2" * 128,
        "screening_evidence_reference": "screening-a",
        "screening_evidence_fingerprint": "3" * 128,
        "ethical_wall_requirement": EthicalWallRequirement.REQUIRED,
        "ethical_wall_policy_reference": wall.policy_id,
        "ethical_wall_policy_fingerprint": wall.fingerprint,
        "ethical_wall_satisfaction_reference": "wall-satisfaction-a",
        "ethical_wall_satisfaction_fingerprint": "9" * 128,
    }
    values.update(changes)
    return ConfidentialityReviewDecision(**values)  # type: ignore[arg-type]


class WallSource:
    def __init__(self, wall: EthicalWallPolicyRevision) -> None:
        self.wall = wall

    def get_current(self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object) -> EthicalWallPolicyRevision:
        return self.wall

    def list_history(self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object) -> tuple[EthicalWallPolicyRevision, ...]:
        return (self.wall,)


def sources(**changes: object) -> dict[str, object]:
    wall = policy()
    membership = WallMembershipEvidence(
        membership_id="membership-a", revision=1, predecessor_fingerprint=None,
        tenant_id="tenant-a", case_matter_id="matter-a", policy_id=wall.policy_id,
        policy_fingerprint=wall.fingerprint, practitioner_principal_id="practitioner-a",
        state=MembershipState.INCLUDED, effective_at=NOW - timedelta(hours=1),
        expires_at=NOW + timedelta(days=10), issuer_principal_id="wall-admin-a",
        issuer_authorization_reference="wall-issuer-auth-a",
        issuer_authorization_fingerprint="a" * 128,
        evidence_reference="membership-evidence-a", evidence_fingerprint="b" * 128,
    )
    acknowledgement = WallAcknowledgementEvidence(
        acknowledgement_id="ack-a", revision=1, predecessor_fingerprint=None,
        tenant_id="tenant-a", case_matter_id="matter-a", policy_id=wall.policy_id,
        policy_fingerprint=wall.fingerprint, practitioner_principal_id="practitioner-a",
        membership_fingerprint=membership.fingerprint,
        state=AcknowledgementState.ACKNOWLEDGED,
        acknowledged_by_principal_id="practitioner-a",
        independently_verified_by_principal_id="independent-verifier-a",
        verification_authorization_reference="ack-verifier-auth-a",
        verification_authorization_fingerprint="c" * 128,
        acknowledged_at=NOW - timedelta(minutes=30), expires_at=NOW + timedelta(days=2),
        evidence_reference="ack-evidence-a", evidence_fingerprint="d" * 128,
    )
    values: dict[str, object] = {
        "iam_source": Source(TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, "tenant_legal_attorney", "LEGAL_ATTORNEY")),
        "binding_source": Source(binding()),
        "assignment_source": Source((assignment(),)),
        "conflict_source": Source(conflict()),
        "review_source": Source(review(wall)),
        "wall_source": WallSource(wall),
        "membership_source": Source((membership,)),
        "acknowledgement_source": Source((acknowledgement,)),
    }
    values.update(changes)
    return values


def enforce(**changes: object) -> None:
    values: dict[str, object] = {
        "authenticated_principal_id": "practitioner-a", "tenant_id": "tenant-a",
        "case_matter_id": "matter-a", "policy_id": "wall-1",
        "evaluation_time": NOW, "session": Session(), **sources(),
    }
    values.update(changes)
    service.require_source_verified_ethical_wall_access(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("session", [None, SimpleNamespace(in_transaction=False)])
def test_active_caller_transaction_required(session: object) -> None:
    with pytest.raises(service.EthicalWallEnforcementDenied, match="TRANSACTION_REQUIRED"):
        enforce(session=session)


def test_boolean_or_noncanonical_iam_assertion_rejects() -> None:
    with pytest.raises(service.EthicalWallEnforcementDenied, match="IAM_INVALID"):
        enforce(iam_source=Source(True))


def test_denied_iam_stops_before_binding() -> None:
    binding_source = Source(binding())
    denied = TenantAuthorizationDecision(
        False, TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    )
    with pytest.raises(service.EthicalWallEnforcementDenied, match="IAM_DENIED"):
        enforce(iam_source=Source(denied), binding_source=binding_source)
    assert binding_source.calls == 0


def test_binding_and_assignment_must_be_exact_current_scope() -> None:
    foreign = binding().revoke(
        revoked_by_principal_id="partner-a", revoked_at=NOW,
        evidence_reference="revoked-a",
    )
    with pytest.raises(service.EthicalWallEnforcementDenied, match="BINDING_INVALID"):
        enforce(binding_source=Source(foreign))
    with pytest.raises(service.EthicalWallEnforcementDenied, match="ASSIGNMENT_REQUIRED"):
        enforce(assignment_source=Source(()))


def test_conflict_and_review_sources_are_canonical_and_exact() -> None:
    with pytest.raises(service.EthicalWallEnforcementDenied, match="CONFLICT_INVALID"):
        enforce(conflict_source=Source(SimpleNamespace(state="ENGAGEMENT_PERMITTED")))
    wall = policy()
    with pytest.raises(service.EthicalWallEnforcementDenied, match="REVIEW_INVALID"):
        enforce(review_source=Source(review(wall, case_matter_id="matter-b")))


def test_explicit_restriction_and_policy_pointer_mismatch_deny() -> None:
    wall = policy(restricted_principal_ids=("practitioner-a",))
    with pytest.raises(service.EthicalWallEnforcementDenied, match="EXPLICITLY_RESTRICTED"):
        enforce(wall_source=WallSource(wall), review_source=Source(review(wall)))
    wrong = policy(source_evidence_reference="other")
    with pytest.raises(service.EthicalWallEnforcementDenied, match="REVIEW_POLICY_MISMATCH"):
        enforce(wall_source=WallSource(wrong))


def test_recorded_approval_still_denies_unratified_institutional_authority() -> None:
    with pytest.raises(service.EthicalWallEnforcementDenied, match="INSTITUTIONAL_AUTHORITY_UNRATIFIED"):
        enforce()



def test_wall_membership_restriction_precedes_acknowledgement() -> None:
    values = sources()
    source = values["membership_source"]
    acknowledgement_source = values["acknowledgement_source"]
    member = source.value[0]  # type: ignore[union-attr]
    restricted = replace(member, state="RESTRICTED")
    values["membership_source"] = Source((restricted,))
    with pytest.raises(service.EthicalWallEnforcementDenied, match="WALL_MEMBERSHIP_RESTRICTED"):
        enforce(**values)
    assert acknowledgement_source.calls == 0  # type: ignore[union-attr]


def test_wall_acknowledgement_must_bind_current_membership() -> None:
    values = sources()
    ack_source = values["acknowledgement_source"]
    acknowledgement = ack_source.value[0]  # type: ignore[union-attr]
    mismatched = replace(acknowledgement, membership_fingerprint="f" * 128)
    with pytest.raises(
        service.EthicalWallEnforcementDenied,
        match="WALL_ACKNOWLEDGEMENT_MEMBERSHIP_MISMATCH",
    ):
        enforce(acknowledgement_source=Source((mismatched,)))


def test_missing_wall_acknowledgement_denies() -> None:
    with pytest.raises(
        service.EthicalWallEnforcementDenied,
        match="WALL_ACKNOWLEDGEMENT_REQUIRED",
    ):
        enforce(acknowledgement_source=Source(()))


def test_membership_source_unavailable_denies_before_acknowledgement_read() -> None:
    acknowledgement_source = Source(())
    with pytest.raises(
        service.EthicalWallEnforcementDenied,
        match="WALL_MEMBERSHIP_SOURCE_UNAVAILABLE",
    ):
        enforce(membership_source=object(), acknowledgement_source=acknowledgement_source)
    assert acknowledgement_source.calls == 0


def test_service_has_no_positive_or_content_delivery_surface() -> None:
    assert not hasattr(service, "authorize_content")
    assert not hasattr(service, "read_content")
    assert service.SOURCE_VERIFIED_CLEARANCE is False
    assert service.OPERATIONAL_ACCESS_ENABLED is False



@pytest.mark.parametrize(
    ("review_changes", "expected"),
    [
        ({"expires_at": NOW}, "REVIEW_EXPIRED"),
        ({"reviewer_principal_id": "practitioner-a"}, "REVIEW_INVALID"),
    ],
)
def test_expired_or_self_review_denies(review_changes: dict[str, object], expected: str) -> None:
    wall = policy()
    with pytest.raises(service.EthicalWallEnforcementDenied, match=expected):
        enforce(review_source=Source(review(wall, **review_changes)))


def test_cross_tenant_conflict_evidence_denies() -> None:
    with pytest.raises(service.EthicalWallEnforcementDenied, match="CONFLICT_BLOCKED"):
        enforce(conflict_source=Source(replace(conflict(), tenant_id="tenant-b")))


def test_cross_tenant_binding_and_cross_matter_assignment_deny() -> None:
    with pytest.raises(service.EthicalWallEnforcementDenied, match="BINDING_INVALID"):
        enforce(binding_source=Source(binding()), tenant_id="tenant-b")
    with pytest.raises(service.EthicalWallEnforcementDenied, match="ASSIGNMENT_SCOPE_INVALID"):
        enforce(assignment_source=Source((replace(assignment(), case_matter_id="matter-b"),)))


def test_revoked_wall_policy_denies_even_with_matching_review_fingerprint() -> None:
    revoked = policy(status=EthicalWallPolicyStatus.REVOKED)
    with pytest.raises(service.EthicalWallEnforcementDenied, match="WALL_REVOKED_OR_SCOPE_INVALID"):
        enforce(wall_source=WallSource(revoked), review_source=Source(review(revoked)))


def test_wall_current_pointer_must_match_history_tail() -> None:
    current = policy()
    previous = policy(effective_until=NOW - timedelta(seconds=1))

    class StaleHistorySource:
        def get_current(self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object) -> EthicalWallPolicyRevision:
            return current

        def list_history(self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object) -> tuple[EthicalWallPolicyRevision, ...]:
            return (previous,)

    with pytest.raises(service.EthicalWallEnforcementDenied, match="WALL_POINTER_INVALID"):
        enforce(wall_source=StaleHistorySource(), review_source=Source(review(current)))


def test_foreign_wall_scope_denies_before_unratified_terminal_denial() -> None:
    foreign = policy(tenant_id="tenant-b")
    with pytest.raises(service.EthicalWallEnforcementDenied, match="WALL_REVOKED_OR_SCOPE_INVALID"):
        enforce(wall_source=WallSource(foreign), review_source=Source(review(foreign)))


def test_expired_wall_policy_denies_at_exact_expiry_boundary() -> None:
    expired = policy(effective_until=NOW)
    with pytest.raises(service.EthicalWallEnforcementDenied, match="WALL_NOT_SATISFIED"):
        enforce(wall_source=WallSource(expired), review_source=Source(review(expired)))


def test_unavailable_wall_source_fails_closed() -> None:
    class UnavailableWallSource:
        def get_current(self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object) -> EthicalWallPolicyRevision:
            raise RuntimeError("source unavailable")

        def list_history(self, tenant_id: str, case_matter_id: str, policy_id: str, *, session: object) -> tuple[EthicalWallPolicyRevision, ...]:
            raise AssertionError("history must not be read after current lookup fails")

    with pytest.raises(service.EthicalWallEnforcementDenied, match="WALL_SOURCE_UNAVAILABLE"):
        enforce(wall_source=UnavailableWallSource())


def test_wall_administrator_cannot_review_practitioner_decision() -> None:
    wall = policy(administrator_principal_id="reviewer-a")
    conflicting_review = review(wall, reviewer_principal_id="reviewer-a")
    with pytest.raises(
        service.EthicalWallEnforcementDenied,
        match="G77_REVIEW_ADMIN_SEPARATION_INVALID",
    ):
        enforce(wall_source=WallSource(wall), review_source=Source(conflicting_review))


def test_review_conflicting_with_current_conflict_evidence_denies() -> None:
    wall = policy()
    contradictory = review(wall, conflict_disposition_fingerprint="f" * 128)
    with pytest.raises(
        service.EthicalWallEnforcementDenied,
        match="G77_REVIEW_CONFLICT_MISMATCH",
    ):
        enforce(review_source=Source(contradictory))


# ARTIFACT: test_legal_work_ethical_wall_enforcement.py
# VERSION: v1.0.1-G77-DENIAL-ADVERSARIAL-EXPANSION
# AUTHORITY BOUNDARY: canonical negative verification only; no access grant
# TENANT POSTURE: exact tenant/matter/principal, foreign scope denied
# FAIL-CLOSED POSTURE: unavailable, malformed, revoked or unratified denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
