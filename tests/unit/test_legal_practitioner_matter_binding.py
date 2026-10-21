"""P9-R105-P4G-P6-R7B-P1 practitioner matter binding domain tests."""
from datetime import datetime, timedelta, timezone
from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter, CaseMatterState,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import (
    LegalPractitionerMatterBinding as Binding,
    PractitionerMatterBindingError as Invalid,
    PractitionerMatterBindingStatus as Status,
)

AT = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)


def matter() -> CaseMatter:
    return CaseMatter(
        tenant_id="tenant-1",
        case_matter_id="matter-1",
        matter_reference="CASE-1",
        opened_at=AT - timedelta(days=1),
        evidence_reference="matter-open-evidence",
    )


def make(**changes: Any) -> Binding:
    args: dict[str, Any] = {
        "binding_id": "binding-1",
        "case_matter": matter(),
        "practitioner_principal_id": "practitioner-1",
        "granted_by_principal_id": "partner-1",
        "granted_at": AT,
        "evidence_reference": "approved-engagement-evidence",
    }
    args.update(changes)
    return Binding.grant(**args)


def test_canonical_matter_provenance_and_immutable_identity():
    value = make()
    assert value.tenant_id == "tenant-1"
    assert value.case_matter_id == "matter-1"
    assert value.source_case_matter_fingerprint == matter().fingerprint
    assert value.status is Status.ACTIVE
    assert len(value.fingerprint) == 128
    with pytest.raises(FrozenInstanceError):
        setattr(value, "tenant_id", "foreign-tenant")


def test_exact_replay_deterministic_fingerprint():
    assert make().to_dict() == make().to_dict()


def test_round_trip_and_strict_payload():
    value = make()
    assert Binding.from_dict(value.to_dict()) == value
    corrupted = value.to_dict()
    corrupted["practitioner_principal_id"] = "another-practitioner"
    with pytest.raises(Invalid):
        Binding.from_dict(corrupted)


def test_revocation_is_distinct_immutable_snapshot():
    original = make()
    revoked = original.revoke(
        revoked_by_principal_id="partner-2",
        revoked_at=AT + timedelta(hours=1),
        evidence_reference="revocation-evidence",
    )
    assert original.status is Status.ACTIVE
    assert revoked.status is Status.REVOKED
    assert revoked.binding_id == original.binding_id
    assert revoked.fingerprint != original.fingerprint
    assert Binding.from_dict(revoked.to_dict()) == revoked
    with pytest.raises(Invalid):
        revoked.revoke(
            revoked_by_principal_id="partner-2",
            revoked_at=AT + timedelta(hours=2),
            evidence_reference="second-revocation",
        )


def test_revocation_cannot_precede_grant():
    with pytest.raises(Invalid):
        make().revoke(
            revoked_by_principal_id="partner-2",
            revoked_at=AT - timedelta(seconds=1),
            evidence_reference="backdated-revocation",
        )


def test_naive_timestamp_rejected():
    with pytest.raises(Invalid):
        make(granted_at=datetime(2026, 10, 19))


@pytest.mark.parametrize("identity", [
    "", " ", "wrong principal", "principal\nother",
])
def test_invalid_practitioner_identity_denied(identity):
    with pytest.raises(Invalid):
        make(practitioner_principal_id=identity)


def test_direct_construction_forbidden():
    with pytest.raises(Invalid):
        Binding()


def test_closed_matter_cannot_create_binding():
    closed = matter().transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="closure",
        occurred_at=AT,
    )
    with pytest.raises(Invalid):
        make(case_matter=closed, granted_at=AT + timedelta(days=1))


def test_binding_is_not_access_authorization():
    assert make().authorizes_matter_access is False
    for name in (
        "grant_document_access", "clear_ethics_wall",
        "waive_conflict", "issue_permission", "read_matter",
    ):
        assert not hasattr(make(), name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P1
# END OF WILSY OS SOVEREIGN ARTIFACT
