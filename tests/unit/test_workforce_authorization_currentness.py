"""Direct certificate for tenant-principal workforce currentness."""

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.auth.workforce_authorization_currentness import (
    WorkforceAuthorizationCurrentnessError,
    derive_tenant_principal_workforce_currentness,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)


AT = datetime(
    2026,
    10,
    13,
    6,
    0,
    tzinfo=timezone.utc,
)

TENANT = "tenant-w3d"
PRINCIPAL = "principal-w3d"


def _relationship(
    *,
    relationship_id: str,
    revision: int,
    status: WorkforceRelationshipStatus,
    status_at: datetime,
    supersedes: str | None = None,
    tenant: str = TENANT,
    principal: str = PRINCIPAL,
    scope: WorkforceScopeKind = WorkforceScopeKind.TENANT,
) -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id=relationship_id,
        revision=revision,
        scope_kind=scope,
        scope_id=tenant,
        principal_id=principal,
        relationship_type=WorkforceRelationshipType.EMPLOYEE,
        status=status,
        effective_from=AT,
        effective_until=None,
        status_effective_at=status_at,
        reason_reference=f"reason-{relationship_id}-{revision}",
        supersedes_fingerprint=supersedes,
    )


def test_empty_history_is_lawful_non_authorizing_absence() -> None:
    result = derive_tenant_principal_workforce_currentness(
        (),
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        observed_at=AT,
    )

    assert result.has_active_relationship is False
    assert result.active_relationship_ids == ()
    assert dict(result.relationship_currentness) == {}


def test_one_active_relationship_is_projected_as_active_fact() -> None:
    relationship = _relationship(
        relationship_id="employment-a",
        revision=1,
        status=WorkforceRelationshipStatus.ACTIVE,
        status_at=AT,
    )

    result = derive_tenant_principal_workforce_currentness(
        (relationship,),
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        observed_at=AT,
    )

    assert result.has_active_relationship is True
    assert result.active_relationship_ids == ("employment-a",)


def test_ended_relationship_is_not_active() -> None:
    first = _relationship(
        relationship_id="employment-a",
        revision=1,
        status=WorkforceRelationshipStatus.ACTIVE,
        status_at=AT,
    )

    ended = _relationship(
        relationship_id="employment-a",
        revision=2,
        status=WorkforceRelationshipStatus.ENDED,
        status_at=AT + timedelta(hours=1),
        supersedes=first.fingerprint,
    )

    result = derive_tenant_principal_workforce_currentness(
        (first, ended),
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        observed_at=AT + timedelta(hours=2),
    )

    assert result.has_active_relationship is False
    assert result.active_relationship_ids == ()


def test_future_suspension_does_not_apply_early() -> None:
    first = _relationship(
        relationship_id="employment-a",
        revision=1,
        status=WorkforceRelationshipStatus.ACTIVE,
        status_at=AT,
    )

    future = _relationship(
        relationship_id="employment-a",
        revision=2,
        status=WorkforceRelationshipStatus.SUSPENDED,
        status_at=AT + timedelta(days=1),
        supersedes=first.fingerprint,
    )

    result = derive_tenant_principal_workforce_currentness(
        (future, first),
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        observed_at=AT + timedelta(hours=1),
    )

    assert result.active_relationship_ids == ("employment-a",)


def test_multiple_relationship_histories_are_derived_independently() -> None:
    a = _relationship(
        relationship_id="employment-a",
        revision=1,
        status=WorkforceRelationshipStatus.ACTIVE,
        status_at=AT,
    )

    b = _relationship(
        relationship_id="contract-b",
        revision=1,
        status=WorkforceRelationshipStatus.ACTIVE,
        status_at=AT,
    )

    b_end = _relationship(
        relationship_id="contract-b",
        revision=2,
        status=WorkforceRelationshipStatus.ENDED,
        status_at=AT + timedelta(hours=1),
        supersedes=b.fingerprint,
    )

    result = derive_tenant_principal_workforce_currentness(
        (b_end, a, b),
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        observed_at=AT + timedelta(hours=2),
    )

    assert result.active_relationship_ids == ("employment-a",)
    assert set(result.relationship_currentness) == {
        "employment-a",
        "contract-b",
    }


@pytest.mark.parametrize(
    ("relationships", "tenant", "principal", "message"),
    [
        (
            lambda: (
                _relationship(
                    relationship_id="wrong-tenant",
                    revision=1,
                    status=WorkforceRelationshipStatus.ACTIVE,
                    status_at=AT,
                    tenant="tenant-other",
                ),
            ),
            TENANT,
            PRINCIPAL,
            "CROSS_TENANT_RELATIONSHIP_FORBIDDEN",
        ),
        (
            lambda: (
                _relationship(
                    relationship_id="wrong-principal",
                    revision=1,
                    status=WorkforceRelationshipStatus.ACTIVE,
                    status_at=AT,
                    principal="principal-other",
                ),
            ),
            TENANT,
            PRINCIPAL,
            "PRINCIPAL_RELATIONSHIP_MISMATCH",
        ),
        (
            lambda: (
                _relationship(
                    relationship_id="platform",
                    revision=1,
                    status=WorkforceRelationshipStatus.ACTIVE,
                    status_at=AT,
                    scope=WorkforceScopeKind.PLATFORM,
                    tenant="platform",
                ),
            ),
            TENANT,
            PRINCIPAL,
            "NON_TENANT_RELATIONSHIP_FORBIDDEN",
        ),
    ],
)
def test_scope_and_identity_mismatch_fail_closed(
    relationships,
    tenant,
    principal,
    message,
) -> None:
    with pytest.raises(
        WorkforceAuthorizationCurrentnessError,
        match=message,
    ):
        derive_tenant_principal_workforce_currentness(
            relationships(),
            tenant_id=tenant,
            principal_id=principal,
            observed_at=AT,
        )


def test_invalid_history_is_wrapped_fail_closed() -> None:
    rev1 = _relationship(
        relationship_id="broken",
        revision=1,
        status=WorkforceRelationshipStatus.ACTIVE,
        status_at=AT,
    )

    rev3 = _relationship(
        relationship_id="broken",
        revision=3,
        status=WorkforceRelationshipStatus.ACTIVE,
        status_at=AT + timedelta(hours=1),
        supersedes=rev1.fingerprint,
    )

    with pytest.raises(
        WorkforceAuthorizationCurrentnessError,
        match="RELATIONSHIP_CURRENTNESS_INVALID",
    ):
        derive_tenant_principal_workforce_currentness(
            (rev1, rev3),
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            observed_at=AT + timedelta(hours=2),
        )


def test_input_validation_fails_closed() -> None:
    with pytest.raises(
        WorkforceAuthorizationCurrentnessError,
        match="TENANT_ID_INVALID",
    ):
        derive_tenant_principal_workforce_currentness(
            (),
            tenant_id="",
            principal_id=PRINCIPAL,
            observed_at=AT,
        )

    with pytest.raises(
        WorkforceAuthorizationCurrentnessError,
        match="PRINCIPAL_ID_INVALID",
    ):
        derive_tenant_principal_workforce_currentness(
            (),
            tenant_id=TENANT,
            principal_id=" ",
            observed_at=AT,
        )

    with pytest.raises(
        WorkforceAuthorizationCurrentnessError,
        match="OBSERVED_AT_INVALID",
    ):
        derive_tenant_principal_workforce_currentness(
            (),
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            observed_at=datetime(2026, 10, 13, 6, 0),
        )


def test_projection_does_not_expose_authorization_api() -> None:
    import tools.eos.auth.workforce_authorization_currentness as module

    assert not hasattr(module, "authorize")
    assert not hasattr(module, "grant")
    assert not hasattr(module, "permission")
