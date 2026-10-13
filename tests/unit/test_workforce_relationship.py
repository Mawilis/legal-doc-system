"""Direct certificate for WILSY-W3A WorkforceRelationship."""

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.workforce.domain.workforce_relationship import (
    SCHEMA,
    VERSION,
    WorkforceRelationship,
    WorkforceRelationshipError,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)


AT = datetime(
    2026,
    10,
    13,
    4,
    30,
    0,
    123456,
    tzinfo=timezone.utc,
)


def relationship(
    *,
    revision: int = 1,
    scope_kind: WorkforceScopeKind = (
        WorkforceScopeKind.PLATFORM
    ),
    scope_id: str = "wilsy-platform",
    principal_id: str = "principal-001",
    relationship_type: WorkforceRelationshipType = (
        WorkforceRelationshipType.EMPLOYEE
    ),
    status: WorkforceRelationshipStatus = (
        WorkforceRelationshipStatus.ACTIVE
    ),
    effective_from: datetime = AT,
    effective_until: datetime | None = None,
    status_effective_at: datetime = AT,
    reason_reference: str = "workforce-evidence-001",
    supersedes_fingerprint: str | None = None,
) -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id="workforce-rel-001",
        revision=revision,
        scope_kind=scope_kind,
        scope_id=scope_id,
        principal_id=principal_id,
        relationship_type=relationship_type,
        status=status,
        effective_from=effective_from,
        effective_until=effective_until,
        status_effective_at=status_effective_at,
        reason_reference=reason_reference,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def test_identity_is_exact() -> None:
    assert (
        VERSION
        == "v1.0.0-WILSY-W3A-WORKFORCE-RELATIONSHIP"
    )
    assert (
        SCHEMA
        == "WILSY-WORKFORCE-RELATIONSHIP/V1"
    )


def test_platform_employee_is_exact_and_immutable() -> None:
    value = relationship()

    assert (
        value.scope_kind
        is WorkforceScopeKind.PLATFORM
    )
    assert value.scope_id == "wilsy-platform"
    assert value.principal_id == "principal-001"
    assert (
        value.relationship_type
        is WorkforceRelationshipType.EMPLOYEE
    )
    assert (
        value.status
        is WorkforceRelationshipStatus.ACTIVE
    )
    assert value.effective_from == AT
    assert value.status_effective_at == AT
    assert len(value.fingerprint) == 128

    with pytest.raises(FrozenInstanceError):
        value.status = (  # type: ignore[misc]
            WorkforceRelationshipStatus.ENDED
        )


def test_tenant_workforce_is_supported_without_platform_authority() -> None:
    value = relationship(
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id="tenant-acme",
    )

    assert (
        value.scope_kind
        is WorkforceScopeKind.TENANT
    )
    assert value.scope_id == "tenant-acme"


@pytest.mark.parametrize(
    "relationship_type",
    tuple(WorkforceRelationshipType),
)
def test_all_frozen_relationship_types_are_supported(
    relationship_type: WorkforceRelationshipType,
) -> None:
    value = relationship(
        relationship_type=relationship_type,
    )

    assert (
        value.relationship_type
        is relationship_type
    )


@pytest.mark.parametrize(
    "status",
    tuple(WorkforceRelationshipStatus),
)
def test_all_frozen_statuses_are_supported(
    status: WorkforceRelationshipStatus,
) -> None:
    value = relationship(
        status=status,
    )

    assert value.status is status


def test_bounded_contract_expiry_is_preserved() -> None:
    end = AT + timedelta(days=90)

    value = relationship(
        relationship_type=(
            WorkforceRelationshipType.CONTRACTOR
        ),
        effective_until=end,
    )

    assert value.effective_until == end


def test_invalid_effective_period_rejects() -> None:
    with pytest.raises(
        WorkforceRelationshipError,
        match="EFFECTIVE_PERIOD_INVALID",
    ):
        relationship(
            effective_until=AT,
        )


def test_status_cannot_predate_relationship() -> None:
    with pytest.raises(
        WorkforceRelationshipError,
        match="STATUS_EFFECTIVE_AT_INVALID",
    ):
        relationship(
            status_effective_at=(
                AT - timedelta(seconds=1)
            ),
        )


def test_active_at_expiry_rejects() -> None:
    end = AT + timedelta(days=1)

    with pytest.raises(
        WorkforceRelationshipError,
        match="ACTIVE_AT_OR_AFTER_EXPIRY",
    ):
        relationship(
            effective_until=end,
            status_effective_at=end,
        )


def test_first_revision_cannot_supersede() -> None:
    with pytest.raises(
        WorkforceRelationshipError,
        match="FIRST_REVISION_SUPERSEDES_FORBIDDEN",
    ):
        relationship(
            supersedes_fingerprint="a" * 128,
        )


def test_later_revision_requires_exact_previous_fingerprint() -> None:
    previous = relationship()

    value = relationship(
        revision=2,
        status=(
            WorkforceRelationshipStatus.SUSPENDED
        ),
        status_effective_at=(
            AT + timedelta(hours=1)
        ),
        supersedes_fingerprint=(
            previous.fingerprint
        ),
    )

    assert value.revision == 2
    assert (
        value.supersedes_fingerprint
        == previous.fingerprint
    )

    with pytest.raises(
        WorkforceRelationshipError,
        match="LATER_REVISION_SUPERSEDES_REQUIRED",
    ):
        relationship(
            revision=2,
        )


def test_invalid_supersedes_fingerprint_rejects() -> None:
    with pytest.raises(
        WorkforceRelationshipError,
        match="SUPERSEDES_FINGERPRINT_INVALID",
    ):
        relationship(
            revision=2,
            supersedes_fingerprint="not-a-fingerprint",
        )


def test_round_trip_preserves_exact_truth() -> None:
    value = relationship(
        relationship_type=(
            WorkforceRelationshipType.CONTRACTOR
        ),
        effective_until=(
            AT + timedelta(days=30)
        ),
    )

    hydrated = (
        WorkforceRelationship.from_dict(
            value.to_dict()
        )
    )

    assert hydrated == value
    assert (
        hydrated.fingerprint
        == value.fingerprint
    )


def test_extra_and_missing_fields_reject() -> None:
    value = relationship()
    payload = value.to_dict()

    extra = dict(payload)
    extra["permission"] = "admin"

    with pytest.raises(
        WorkforceRelationshipError,
        match="PAYLOAD_FIELDS_INVALID",
    ):
        WorkforceRelationship.from_dict(
            extra
        )

    missing = dict(payload)
    missing.pop("scope_id")

    with pytest.raises(
        WorkforceRelationshipError,
        match="PAYLOAD_FIELDS_INVALID",
    ):
        WorkforceRelationship.from_dict(
            missing
        )


def test_corrupt_fingerprint_rejects() -> None:
    value = relationship()
    payload = value.to_dict()
    payload["fingerprint"] = "0" * 128

    with pytest.raises(
        WorkforceRelationshipError,
        match="FINGERPRINT_INVALID",
    ):
        WorkforceRelationship.from_dict(
            payload
        )


def test_naive_time_rejects() -> None:
    with pytest.raises(
        WorkforceRelationshipError,
        match="EFFECTIVE_FROM_INVALID",
    ):
        relationship(
            effective_from=(
                datetime(
                    2026,
                    10,
                    13,
                    4,
                    30,
                )
            ),
        )


def test_microseconds_are_preserved() -> None:
    value = relationship()

    hydrated = (
        WorkforceRelationship.from_dict(
            value.to_dict()
        )
    )

    assert (
        hydrated.effective_from.microsecond
        == 123456
    )


def test_domain_contains_no_iam_or_commercial_authority() -> None:
    fields = set(
        relationship().to_dict()
    )

    forbidden = {
        "role",
        "roles",
        "role_id",
        "permission",
        "permissions",
        "entitlement",
        "subscription",
        "plan",
        "authorized",
        "is_authorized",
        "financial_execution",
        "current_stage",
    }

    assert fields.isdisjoint(
        forbidden
    )


def test_relationship_does_not_self_declare_current_authorization() -> None:
    value = relationship()

    assert not hasattr(
        value,
        "is_authorized",
    )
    assert not hasattr(
        value,
        "permission",
    )
    assert not hasattr(
        value,
        "membership",
    )


# ARTIFACT:
# tests/unit/test_workforce_relationship.py
#
# AUTHORITY:
# direct pure-domain certificate only
#
# FINANCIAL EXECUTION AUTHORITY:
# NONE
