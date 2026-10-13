"""Direct certificate for W3B derived workforce currentness."""

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.domain.workforce_relationship_currentness import (
    WorkforceRelationshipCurrentnessError,
    derive_workforce_relationship_currentness,
)


AT = datetime(
    2026,
    10,
    13,
    6,
    0,
    tzinfo=timezone.utc,
)


def revision(
    number: int,
    *,
    status: WorkforceRelationshipStatus,
    previous: WorkforceRelationship | None = None,
    relationship_id: str = "rel-001",
    principal_id: str = "principal-001",
) -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id=relationship_id,
        revision=number,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id="tenant-001",
        principal_id=principal_id,
        relationship_type=(
            WorkforceRelationshipType.EMPLOYEE
        ),
        status=status,
        effective_from=AT,
        effective_until=None,
        status_effective_at=(
            AT + timedelta(hours=number - 1)
        ),
        reason_reference=f"evidence-{number}",
        supersedes_fingerprint=(
            None
            if previous is None
            else previous.fingerprint
        ),
    )


def test_active_history_derives_active() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )

    value = derive_workforce_relationship_currentness(
        [first],
        AT + timedelta(minutes=1),
    )

    assert value.is_effective is True
    assert value.is_active is True
    assert value.relationship == first


def test_future_dated_suspension_does_not_apply_early() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )
    future_suspension = revision(
        2,
        status=WorkforceRelationshipStatus.SUSPENDED,
        previous=first,
    )

    before_suspension = (
        derive_workforce_relationship_currentness(
            [first, future_suspension],
            AT + timedelta(minutes=30),
        )
    )

    assert before_suspension.relationship == first
    assert before_suspension.is_effective is True
    assert before_suspension.is_active is True


def test_future_dated_first_revision_is_not_active_early() -> None:
    future = WorkforceRelationship(
        relationship_id="future-worker",
        revision=1,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id="tenant-001",
        principal_id="principal-future",
        relationship_type=(
            WorkforceRelationshipType.EMPLOYEE
        ),
        status=WorkforceRelationshipStatus.ACTIVE,
        effective_from=AT + timedelta(hours=2),
        effective_until=None,
        status_effective_at=AT + timedelta(hours=2),
        reason_reference="future-engagement",
        supersedes_fingerprint=None,
    )

    before_start = (
        derive_workforce_relationship_currentness(
            [future],
            AT + timedelta(hours=1),
        )
    )

    assert before_start.relationship == future
    assert before_start.is_effective is False
    assert before_start.is_active is False


def test_suspended_history_is_not_active() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )
    second = revision(
        2,
        status=WorkforceRelationshipStatus.SUSPENDED,
        previous=first,
    )

    value = derive_workforce_relationship_currentness(
        [first, second],
        AT + timedelta(hours=2),
    )

    assert value.is_effective is True
    assert value.is_active is False


def test_ended_history_is_not_active() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )
    ended = revision(
        2,
        status=WorkforceRelationshipStatus.ENDED,
        previous=first,
    )

    value = derive_workforce_relationship_currentness(
        [first, ended],
        AT + timedelta(hours=2),
    )

    assert value.is_active is False


def test_expired_active_relationship_is_not_effective() -> None:
    end = AT + timedelta(days=30)

    value = WorkforceRelationship(
        relationship_id="contract-001",
        revision=1,
        scope_kind=WorkforceScopeKind.PLATFORM,
        scope_id="wilsy-platform",
        principal_id="contractor-001",
        relationship_type=(
            WorkforceRelationshipType.CONTRACTOR
        ),
        status=WorkforceRelationshipStatus.ACTIVE,
        effective_from=AT,
        effective_until=end,
        status_effective_at=AT,
        reason_reference="contract-001",
        supersedes_fingerprint=None,
    )

    projection = derive_workforce_relationship_currentness(
        [value],
        end,
    )

    assert projection.is_effective is False
    assert projection.is_active is False


def test_gap_rejects() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )
    third = WorkforceRelationship(
        relationship_id=first.relationship_id,
        revision=3,
        scope_kind=first.scope_kind,
        scope_id=first.scope_id,
        principal_id=first.principal_id,
        relationship_type=first.relationship_type,
        status=WorkforceRelationshipStatus.SUSPENDED,
        effective_from=AT,
        effective_until=None,
        status_effective_at=AT + timedelta(hours=2),
        reason_reference="gap",
        supersedes_fingerprint=first.fingerprint,
    )

    with pytest.raises(
        WorkforceRelationshipCurrentnessError,
        match="REVISION_SEQUENCE_INVALID",
    ):
        derive_workforce_relationship_currentness(
            [first, third],
            AT + timedelta(hours=3),
        )


def test_broken_fingerprint_chain_rejects() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )
    other = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
        relationship_id="other",
    )

    second = revision(
        2,
        status=WorkforceRelationshipStatus.SUSPENDED,
        previous=other,
    )

    with pytest.raises(
        WorkforceRelationshipCurrentnessError,
        match="FINGERPRINT_CHAIN_INVALID",
    ):
        derive_workforce_relationship_currentness(
            [first, second],
            AT + timedelta(hours=2),
        )


def test_identity_change_rejects() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )

    changed = revision(
        2,
        status=WorkforceRelationshipStatus.SUSPENDED,
        previous=first,
        principal_id="principal-other",
    )

    with pytest.raises(
        WorkforceRelationshipCurrentnessError,
        match="HISTORY_IDENTITY_MISMATCH",
    ):
        derive_workforce_relationship_currentness(
            [first, changed],
            AT + timedelta(hours=2),
        )


def test_ended_is_terminal_for_same_relationship_id() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )
    ended = revision(
        2,
        status=WorkforceRelationshipStatus.ENDED,
        previous=first,
    )
    resurrected = revision(
        3,
        status=WorkforceRelationshipStatus.ACTIVE,
        previous=ended,
    )

    with pytest.raises(
        WorkforceRelationshipCurrentnessError,
        match="ENDED_RELATIONSHIP_TERMINAL",
    ):
        derive_workforce_relationship_currentness(
            [first, ended, resurrected],
            AT + timedelta(hours=4),
        )


def test_rehire_requires_new_relationship_identity() -> None:
    old = revision(
        1,
        status=WorkforceRelationshipStatus.ENDED,
        relationship_id="employment-old",
    )

    new = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
        relationship_id="employment-new",
    )

    assert old.relationship_id != new.relationship_id

    current = derive_workforce_relationship_currentness(
        [new],
        AT + timedelta(hours=1),
    )

    assert current.is_active is True


def test_currentness_contains_no_iam_authority() -> None:
    first = revision(
        1,
        status=WorkforceRelationshipStatus.ACTIVE,
    )

    value = derive_workforce_relationship_currentness(
        [first],
        AT + timedelta(minutes=1),
    )

    assert not hasattr(value, "permission")
    assert not hasattr(value, "role")
    assert not hasattr(value, "authorized")
