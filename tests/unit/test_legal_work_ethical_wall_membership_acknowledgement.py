from dataclasses import replace
from datetime import UTC, datetime, timedelta

from tools.eos.legal_operations.domain.legal_work_ethical_wall_membership_acknowledgement import (
    AcknowledgementState,
    MembershipState,
    WallAcknowledgementEvidence,
    WallEvidenceCurrentness,
    WallMembershipEvidence,
    project_wall_membership_and_acknowledgement,
)

NOW = datetime(2026, 10, 30, 10, 0, tzinfo=UTC)


def membership(**changes: object) -> WallMembershipEvidence:
    values: dict[str, object] = {
        "membership_id": "membership-a", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a", "policy_id": "wall-a",
        "policy_fingerprint": "1" * 128, "practitioner_principal_id": "practitioner-a",
        "state": MembershipState.INCLUDED, "effective_at": NOW - timedelta(hours=1),
        "expires_at": NOW + timedelta(days=3), "issuer_principal_id": "issuer-a",
        "issuer_authorization_reference": "issuer-auth-a",
        "issuer_authorization_fingerprint": "2" * 128,
        "evidence_reference": "membership-evidence-a", "evidence_fingerprint": "3" * 128,
    }
    values.update(changes)
    return WallMembershipEvidence(**values)  # type: ignore[arg-type]


def acknowledgement(member: WallMembershipEvidence, **changes: object) -> WallAcknowledgementEvidence:
    values: dict[str, object] = {
        "acknowledgement_id": "ack-a", "revision": 1, "predecessor_fingerprint": None,
        "tenant_id": "tenant-a", "case_matter_id": "matter-a", "policy_id": "wall-a",
        "policy_fingerprint": member.policy_fingerprint,
        "practitioner_principal_id": "practitioner-a",
        "membership_fingerprint": member.fingerprint,
        "state": AcknowledgementState.ACKNOWLEDGED,
        "acknowledged_by_principal_id": "practitioner-a",
        "independently_verified_by_principal_id": "verifier-a",
        "verification_authorization_reference": "verifier-auth-a",
        "verification_authorization_fingerprint": "4" * 128,
        "acknowledged_at": NOW - timedelta(minutes=30),
        "expires_at": NOW + timedelta(days=1),
        "evidence_reference": "ack-evidence-a", "evidence_fingerprint": "5" * 128,
    }
    values.update(changes)
    return WallAcknowledgementEvidence(**values)  # type: ignore[arg-type]


def project(member: WallMembershipEvidence, ack: WallAcknowledgementEvidence | None):
    return project_wall_membership_and_acknowledgement(
        tenant_id="tenant-a", case_matter_id="matter-a", policy_id="wall-a",
        practitioner_principal_id="practitioner-a", policy_fingerprint="1" * 128,
        evaluation_time=NOW, memberships=(member,),
        acknowledgements=() if ack is None else (ack,),
    )


def test_complete_membership_and_independent_acknowledgement_are_non_authorizing():
    member = membership()
    result = project(member, acknowledgement(member))
    assert result.state is WallEvidenceCurrentness.RECORDED_COMPLETE_UNVERIFIED
    assert result.permits_operational_access is False


def test_explicit_restriction_precedes_acknowledgement():
    member = membership(state=MembershipState.RESTRICTED)
    result = project(member, acknowledgement(member))
    assert result.state is WallEvidenceCurrentness.MEMBERSHIP_RESTRICTED


def test_revocation_and_expiry_deny():
    revoked = membership(state=MembershipState.REVOKED)
    assert project(revoked, acknowledgement(revoked)).state is WallEvidenceCurrentness.MEMBERSHIP_REVOKED
    expired = membership(expires_at=NOW)
    assert project(expired, acknowledgement(expired)).state is WallEvidenceCurrentness.MEMBERSHIP_EXPIRED


def test_missing_and_stale_acknowledgement_deny():
    member = membership()
    assert project(member, None).state is WallEvidenceCurrentness.ACKNOWLEDGEMENT_MISSING
    stale = acknowledgement(member, membership_fingerprint="f" * 128)
    assert project(member, stale).state is WallEvidenceCurrentness.ACKNOWLEDGEMENT_MEMBERSHIP_MISMATCH


def test_acknowledgement_must_be_self_signed_by_practitioner_and_independently_verified():
    member = membership()
    try:
        acknowledgement(member, independently_verified_by_principal_id="practitioner-a")
    except ValueError as error:
        assert "INDEPENDENCE_INVALID" in str(error)
    else:
        raise AssertionError("self-verification must be rejected")


def test_tampered_history_is_corrupt_blocked():
    member = membership()
    tampered = object.__new__(WallMembershipEvidence)
    for name in member.__dataclass_fields__:
        object.__setattr__(tampered, name, getattr(member, name))
    object.__setattr__(tampered, "fingerprint", "f" * 128)
    result = project(tampered, acknowledgement(member))
    assert result.state is WallEvidenceCurrentness.EVIDENCE_CORRUPT


def test_policy_revision_change_invalidates_prior_membership_and_acknowledgement():
    member = membership()
    result = project_wall_membership_and_acknowledgement(
        tenant_id="tenant-a", case_matter_id="matter-a", policy_id="wall-a",
        practitioner_principal_id="practitioner-a", policy_fingerprint="9" * 128,
        evaluation_time=NOW, memberships=(member,), acknowledgements=(acknowledgement(member),),
    )
    assert result.state is WallEvidenceCurrentness.MEMBERSHIP_POLICY_MISMATCH
