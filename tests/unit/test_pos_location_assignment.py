from datetime import datetime, timezone

import pytest

from tools.eos.saas.domain.pos_location_assignment import (
    POSLocationAssignment, POSLocationAssignmentStatus,
)


def assignment(**changes):
    values = dict(
        tenant_id="tenant-a", location_id="store-1", principal_id="principal-a",
        assignment_id="assignment-1", revision=0,
        status=POSLocationAssignmentStatus.ACTIVE,
        authority_reference="workforce-assignment:123",
        authority_fingerprint="a" * 128, idempotency_key="issue-1",
        occurred_at=datetime(2026, 11, 6, tzinfo=timezone.utc),
        changed_by_principal_id="principal-issuer",
    )
    values.update(changes)
    return POSLocationAssignment(**values)


def test_assignment_is_tenant_location_principal_bound_and_fingerprinted():
    value = assignment()
    assert value.to_dict()["fingerprint"] == value.fingerprint
    assert value.to_dict()["tenant_id"] == "tenant-a"
    assert value.to_dict()["location_id"] == "store-1"
    assert value.to_dict()["principal_id"] == "principal-a"


@pytest.mark.parametrize("changes", [
    {"tenant_id": ""}, {"location_id": ""}, {"principal_id": ""},
    {"authority_fingerprint": "not-a-fingerprint"},
    {"revision": -1}, {"occurred_at": datetime(2026, 11, 6)},
])
def test_assignment_rejects_invalid_authority_scope_and_evidence(changes):
    with pytest.raises(ValueError):
        assignment(**changes)


def test_revocation_requires_reason_and_active_assignment_forbids_reason():
    with pytest.raises(ValueError):
        assignment(status=POSLocationAssignmentStatus.REVOKED)
    with pytest.raises(ValueError):
        assignment(reason="unexpected")
