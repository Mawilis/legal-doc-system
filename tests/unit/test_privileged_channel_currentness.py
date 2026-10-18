from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, cast

from tools.eos.auth.privileged_channel_currentness import (
    ChannelCurrentnessError,
    FactorVerificationStatus,
    InteractiveFactorVerificationEvent,
    WorkloadTrustFact,
    WorkloadTrustStatus,
    derive_interactive_currentness,
    derive_workload_proof_currentness,
)
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.domain.auth import Session


NOW = datetime(2026, 10, 14, 5, 0, tzinfo=timezone.utc)


def interactive(
    *,
    status: FactorVerificationStatus = FactorVerificationStatus.VERIFIED,
    authenticated_at: datetime = NOW,
) -> InteractiveFactorVerificationEvent:
    return InteractiveFactorVerificationEvent(
        factor_verification_reference="factor-1",
        principal_id="principal-1",
        session_reference="WILSYSESSION-1",
        credential_revision=7,
        authenticated_at=authenticated_at,
        status=status,
    )


def test_session_reference_remains_backward_compatible() -> None:
    value = Session(
        userId="principal-1",
        token="secret",
        expiresAt=NOW,
        tenantId="tenant-1",
        role="role",
        permissions=[],
    )
    assert value.sessionReference is None


def test_session_reference_can_be_exposed_without_bearer_reuse() -> None:
    value = Session(
        userId="principal-1",
        token="secret",
        expiresAt=NOW,
        tenantId="tenant-1",
        role="role",
        permissions=[],
        sessionReference="WILSYSESSION-1",
    )
    assert value.sessionReference == "WILSYSESSION-1"
    assert value.sessionReference != value.token


class Collection:
    def __init__(self, row: object) -> None:
        self.row = row
        self.query: object = None
        self.session: object = None

    def find_one(
        self,
        query: object,
        *,
        session: object = None,
    ) -> object:
        self.query = query
        self.session = session
        return self.row


def registry_for(row: object) -> tuple[AuthRegistry, Collection]:
    registry = AuthRegistry.__new__(AuthRegistry)
    dynamic = cast(Any, registry)
    collection = Collection(row)

    dynamic._require_canonical_tenant = (
        lambda tenant_reference, **kwargs:
            SimpleNamespace(tenant_id=tenant_reference)
    )

    dynamic._resolve_exact_credential_identity = (
        lambda tenant_id, user_id, **kwargs:
            (
                {},
                {},
                SimpleNamespace(
                    id=user_id,
                    tenantId=tenant_id,
                ),
                7,
            )
    )

    dynamic._collection = (
        lambda collection_name: collection
    )

    dynamic._call_collection = (
        lambda collection_arg,
        method_name,
        *args,
        **kwargs:
            getattr(collection_arg, method_name)(
                *args,
                **kwargs,
            )
    )

    return registry, collection


def test_exact_session_currentness() -> None:
    registry, collection = registry_for(
        {
            "tenant_id": "tenant-1",
            "user_id": "principal-1",
            "session_reference": "WILSYSESSION-1",
            "expires_at": datetime(2026, 10, 14, 6, 0),
        }
    )

    assert registry.is_session_current(
        "tenant-1",
        "principal-1",
        "WILSYSESSION-1",
        at=datetime(2026, 10, 14, 5, 0),
        session="caller",
    )

    assert collection.query == {
        "tenant_id": "tenant-1",
        "user_id": "principal-1",
        "session_reference": "WILSYSESSION-1",
    }
    assert collection.session == "caller"


def test_session_currentness_normalizes_default_bson_and_aware_utc_equally() -> None:
    naive_registry, _ = registry_for(
        {
            "tenant_id": "tenant-1", "user_id": "principal-1",
            "session_reference": "WILSYSESSION-1", "expires_at": datetime(2026, 10, 14, 6),
        }
    )
    aware_registry, _ = registry_for(
        {
            "tenant_id": "tenant-1", "user_id": "principal-1",
            "session_reference": "WILSYSESSION-1", "expires_at": datetime(2026, 10, 14, 6, tzinfo=timezone.utc),
        }
    )
    observed = datetime(2026, 10, 14, 5, tzinfo=timezone.utc)
    assert naive_registry.is_session_current("tenant-1", "principal-1", "WILSYSESSION-1", at=observed)
    assert aware_registry.is_session_current("tenant-1", "principal-1", "WILSYSESSION-1", at=observed)


def test_session_currentness_rejects_non_datetime_expiry() -> None:
    registry, _ = registry_for(
        {
            "tenant_id": "tenant-1", "user_id": "principal-1",
            "session_reference": "WILSYSESSION-1", "expires_at": "2026-10-14T06:00:00Z",
        }
    )
    assert not registry.is_session_current(
        "tenant-1", "principal-1", "WILSYSESSION-1", at=NOW,
    )


def test_absent_or_expired_session_fails_closed() -> None:
    registry, _ = registry_for(None)

    assert not registry.is_session_current(
        "tenant-1",
        "principal-1",
        "WILSYSESSION-1",
        at=datetime(2026, 10, 14, 5, 0),
    )

    registry, _ = registry_for(
        {
            "tenant_id": "tenant-1",
            "user_id": "principal-1",
            "session_reference": "WILSYSESSION-1",
            "expires_at": datetime(2026, 10, 14, 4, 59),
        }
    )

    assert not registry.is_session_current(
        "tenant-1",
        "principal-1",
        "WILSYSESSION-1",
        at=datetime(2026, 10, 14, 5, 0),
    )


def test_session_binding_mismatch_fails_closed() -> None:
    for row in (
        {
            "tenant_id": "other",
            "user_id": "principal-1",
            "session_reference": "WILSYSESSION-1",
            "expires_at": datetime(2026, 10, 14, 6),
        },
        {
            "tenant_id": "tenant-1",
            "user_id": "other",
            "session_reference": "WILSYSESSION-1",
            "expires_at": datetime(2026, 10, 14, 6),
        },
        {
            "tenant_id": "tenant-1",
            "user_id": "principal-1",
            "session_reference": "different",
            "expires_at": datetime(2026, 10, 14, 6),
        },
    ):
        registry, _ = registry_for(row)

        assert not registry.is_session_current(
            "tenant-1",
            "principal-1",
            "WILSYSESSION-1",
            at=datetime(2026, 10, 14, 5),
        )


def test_interactive_currentness_requires_exact_bindings() -> None:
    value = derive_interactive_currentness(
        interactive(),
        principal_id="principal-1",
        session_reference="WILSYSESSION-1",
        credential_revision=7,
        session_current=True,
        evaluated_at=NOW + timedelta(minutes=5),
        maximum_age_seconds=600,
    )

    assert value.factor_verification_current
    assert value.authentication_recency_current


def test_revoked_factor_fails_closed() -> None:
    value = derive_interactive_currentness(
        interactive(status=FactorVerificationStatus.REVOKED),
        principal_id="principal-1",
        session_reference="WILSYSESSION-1",
        credential_revision=7,
        session_current=True,
        evaluated_at=NOW,
        maximum_age_seconds=600,
    )

    assert not value.factor_verification_current
    assert not value.authentication_recency_current


def test_old_factor_can_be_current_but_not_recent() -> None:
    value = derive_interactive_currentness(
        interactive(
            authenticated_at=NOW - timedelta(minutes=20)
        ),
        principal_id="principal-1",
        session_reference="WILSYSESSION-1",
        credential_revision=7,
        session_current=True,
        evaluated_at=NOW,
        maximum_age_seconds=600,
    )

    assert value.factor_verification_current
    assert not value.authentication_recency_current


def test_session_current_does_not_imply_factor_current() -> None:
    value = derive_interactive_currentness(
        interactive(),
        principal_id="different",
        session_reference="WILSYSESSION-1",
        credential_revision=7,
        session_current=True,
        evaluated_at=NOW,
        maximum_age_seconds=600,
    )

    assert not value.factor_verification_current


def test_workload_currentness_requires_exact_trusted_bindings() -> None:
    fact = WorkloadTrustFact(
        proof_reference="proof-1",
        principal_id="machine-1",
        credential_or_attestation_reference="attestation-1",
        observed_at=NOW,
        status=WorkloadTrustStatus.CURRENT,
    )

    assert derive_workload_proof_currentness(
        fact,
        principal_id="machine-1",
        proof_reference="proof-1",
        credential_or_attestation_reference="attestation-1",
    )

    assert not derive_workload_proof_currentness(
        fact,
        principal_id="different",
        proof_reference="proof-1",
        credential_or_attestation_reference="attestation-1",
    )


def test_revoked_workload_trust_fails_closed() -> None:
    fact = WorkloadTrustFact(
        proof_reference="proof-1",
        principal_id="machine-1",
        credential_or_attestation_reference="attestation-1",
        observed_at=NOW,
        status=WorkloadTrustStatus.REVOKED,
    )

    assert not derive_workload_proof_currentness(
        fact,
        principal_id="machine-1",
        proof_reference="proof-1",
        credential_or_attestation_reference="attestation-1",
    )


def test_invalid_domain_input_rejected() -> None:
    try:
        interactive(
            authenticated_at=datetime(2026, 10, 14, 5)
        )
    except ChannelCurrentnessError:
        pass
    else:
        raise AssertionError(
            "naive verification time accepted"
        )
