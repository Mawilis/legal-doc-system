"""Direct certificate for Legal Evidence provider cleanup authorization.

VERSION: v1.1.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Certify the pure C4D6E-A1 cleanup-authorization domain against the exact
    existing C4D6D-B orphan-proof and C4D4C preservation contracts.

AUTHORITY BOUNDARY:
    Test evidence only. No provider mutation, deletion execution, IAM binding,
    persistence, HTTP/API routing, billing, payment, execution or settlement.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldState,
)
from tools.eos.legal_operations.domain.legal_evidence_preservation_assessment import (
    LegalEvidencePreservationState,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_authorization import (
    VERSION,
    LegalEvidenceProviderCleanupAuthorization,
    LegalEvidenceProviderCleanupAuthorizationError,
    authorize_legal_evidence_provider_cleanup,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_disownership import (
    LegalEvidenceProviderObjectDisownership,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_object_orphan_proof import (
    LegalEvidenceProviderObjectOrphanProof,
    prove_legal_evidence_provider_object_orphan,
)
from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionConstraint,
)
from tools.eos.legal_operations.orchestration.legal_evidence_preservation_composer import (
    LegalEvidencePreservationComposer,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerificationService,
)


AT = datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)
AUTHORIZED_AT = AT + timedelta(minutes=10)

TENANT = "tenant-a1-cert"
PROVIDER = "aws_s3"
STORAGE = "opaque/storage/a1-cert"
OBJECT_VERSION = "version-a1-cert"

SHA_A = "a" * 128
SHA_B = "b" * 128
SHA_C = "c" * 128


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class _RetentionRegistry:
    def __init__(self, value: LegalEvidenceRetentionConstraint) -> None:
        self.value = value

    def get_by_provider_object(
        self,
        **_: Any,
    ) -> LegalEvidenceRetentionConstraint:
        return self.value


class _HoldRegistry:
    def __init__(
        self,
        values: tuple[LegalEvidenceLegalHoldConstraint, ...],
    ) -> None:
        self.values = values

    def list_provider_object_history(
        self,
        **_: Any,
    ) -> tuple[LegalEvidenceLegalHoldConstraint, ...]:
        return self.values


class _Provider:
    def __init__(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        completed: tuple[LegalEvidenceCompletedObjectObservation, ...],
    ) -> None:
        self.scope = scope
        self.completed = completed

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return LegalEvidenceProviderEnumerationPage(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=PROVIDER,
            enumeration_kind=(
                LegalEvidenceProviderEnumerationKind.INCOMPLETE_WRITE_SESSIONS
            ),
            observed_at=AT,
            observations=(),
            next_page_reference=None,
        )

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        assert scope == self.scope
        assert observed_at == AT
        assert page_reference is None

        return LegalEvidenceProviderEnumerationPage(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=PROVIDER,
            enumeration_kind=(
                LegalEvidenceProviderEnumerationKind.COMPLETED_OBJECT_VERSIONS
            ),
            observed_at=AT,
            observations=cast(
                tuple[Any, ...],
                self.completed,
            ),
            next_page_reference=None,
        )


def _orphan_proof() -> LegalEvidenceProviderObjectOrphanProof:
    scope = LegalEvidenceProviderDiscoveryScope(
        tenant_id=TENANT,
        tenant_scope_fingerprint=SHA_A,
    )

    observation = LegalEvidenceCompletedObjectObservation(
        tenant_id=TENANT,
        provider_name=PROVIDER,
        storage_reference=STORAGE,
        object_version_reference=OBJECT_VERSION,
        provider_integrity_reference='"etag-a1-cert"',
        content_length=19,
        last_modified_at=AT,
        observed_at=AT,
        write_intent_metadata_state=(
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
        ),
        write_intent_fingerprint=None,
    )

    provider = _Provider(
        scope=scope,
        completed=(observation,),
    )

    assert isinstance(
        provider,
        LegalEvidenceProviderCoverageEnumerationPort,
    )

    coverage_service = LegalEvidenceProviderCoverageVerificationService(
        provider=provider,
    )

    verification = coverage_service.verify_coverage(
        scope=scope,
        provider_name=PROVIDER,
        observed_at=AT,
    )

    disownership = LegalEvidenceProviderObjectDisownership(
        tenant_id=TENANT,
        provider_name=PROVIDER,
        storage_reference=STORAGE,
        object_version_reference=OBJECT_VERSION,
        disownership_reference="disownership-a1-cert",
        reason_reference="reason-a1-cert",
        source_evidence_reference="source-a1-cert",
        source_evidence_fingerprint=SHA_A,
        authorization_evidence_reference="authorization-a1-cert",
        authorization_evidence_fingerprint=SHA_B,
        decided_at=AT - timedelta(minutes=5),
    )

    return prove_legal_evidence_provider_object_orphan(
        coverage_service=coverage_service,
        verification=verification,
        observation=observation,
        disownership=disownership,
        orphan_proof_reference="orphan-proof-a1-cert",
        proved_at=AT + timedelta(minutes=1),
    )


def _preservation(
    *,
    tenant_id: str = TENANT,
    provider_name: str = PROVIDER,
    storage_reference: str = STORAGE,
    object_version_reference: str = OBJECT_VERSION,
    retain_until: datetime = AT,
    hold_history: tuple[LegalEvidenceLegalHoldConstraint, ...] = (),
    assessed_at: datetime = AT,
):
    retention = LegalEvidenceRetentionConstraint(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        source_evidence_reference="retention-source-a1-cert",
        source_evidence_fingerprint=SHA_C,
        imposed_at=AT - timedelta(days=10),
        retain_until=retain_until,
    )

    composer = LegalEvidencePreservationComposer(
        _RetentionRegistry(retention),
        _HoldRegistry(hold_history),
    )

    return composer.compose_preservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        assessed_at=assessed_at,
        session=_Session(),
    )


def _authorize(
    *,
    orphan_proof: LegalEvidenceProviderObjectOrphanProof | None = None,
    preservation: Any | None = None,
    authorization_id: str = "cleanup-authorization-a1-cert",
    authorized_at: datetime = AUTHORIZED_AT,
    reason_reference: str = "cleanup-reason-a1-cert",
) -> LegalEvidenceProviderCleanupAuthorization:
    return authorize_legal_evidence_provider_cleanup(
        orphan_proof=(
            orphan_proof
            if orphan_proof is not None
            else _orphan_proof()
        ),
        preservation=(
            preservation
            if preservation is not None
            else _preservation()
        ),
        authorization_id=authorization_id,
        authorized_at=authorized_at,
        reason_reference=reason_reference,
    )


def test_shape_is_frozen_slots_factory_only_and_exact() -> None:
    assert VERSION == (
        "v1.1.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION"
    )

    assert [
        field.name
        for field in fields(
            LegalEvidenceProviderCleanupAuthorization
        )
    ] == [
        "authorization_id",
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "orphan_proof_fingerprint",
        "disownership_fingerprint",
        "preservation_fingerprint",
        "preservation_assessed_at",
        "authorized_at",
        "reason_reference",
        "schema",
        "authorization_version",
        "_construction_proof",
    ]

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match="L10A2R_C4D6E_A1_FACTORY_REQUIRED",
    ):
        LegalEvidenceProviderCleanupAuthorization(
            authorization_id="direct-a1-cert",
            tenant_id=TENANT,
            provider_name=PROVIDER,
            storage_reference=STORAGE,
            object_version_reference=OBJECT_VERSION,
            orphan_proof_fingerprint="1" * 128,
            disownership_fingerprint="2" * 128,
            preservation_fingerprint="3" * 128,
            preservation_assessed_at=AT,
            authorized_at=AUTHORIZED_AT,
            reason_reference="direct-forbidden",
        )


def test_positive_authorization_is_exact_and_deterministic() -> None:
    orphan = _orphan_proof()
    preservation = _preservation()

    first = _authorize(
        orphan_proof=orphan,
        preservation=preservation,
    )
    second = _authorize(
        orphan_proof=orphan,
        preservation=preservation,
    )

    assert first == second
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128
    assert set(first.fingerprint) <= set("0123456789abcdef")

    assert first.tenant_id == orphan.tenant_id
    assert first.provider_name == orphan.provider_name
    assert first.storage_reference == orphan.storage_reference
    assert (
        first.object_version_reference
        == orphan.object_version_reference
    )
    assert first.orphan_proof_fingerprint == orphan.fingerprint
    assert (
        first.disownership_fingerprint
        == orphan.disownership_fingerprint
    )
    assert first.preservation_assessed_at == AT
    assert first.authorized_at == AUTHORIZED_AT


@pytest.mark.parametrize(
    (
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
    ),
    [
        ("tenant-other", PROVIDER, STORAGE, OBJECT_VERSION),
        (TENANT, "other_provider", STORAGE, OBJECT_VERSION),
        (TENANT, PROVIDER, "other/storage", OBJECT_VERSION),
        (TENANT, PROVIDER, STORAGE, "other-version"),
    ],
)
def test_cross_scope_preservation_rejects(
    tenant_id: str,
    provider_name: str,
    storage_reference: str,
    object_version_reference: str,
) -> None:
    preservation = _preservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match="L10A2R_C4D6E_A1_SOURCE_SCOPE_MISMATCH",
    ):
        _authorize(
            preservation=preservation,
        )


def test_active_retention_rejects_cleanup_authorization() -> None:
    preservation = _preservation(
        retain_until=AT + timedelta(days=1),
    )

    assert preservation.preservation_required is True
    assert preservation.retention.retention_elapsed is False

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match="L10A2R_C4D6E_A1_PRESERVATION_CLEARANCE_REQUIRED",
    ):
        _authorize(
            preservation=preservation,
        )


def test_active_legal_hold_rejects_cleanup_authorization() -> None:
    hold = LegalEvidenceLegalHoldConstraint(
        tenant_id=TENANT,
        provider_name=PROVIDER,
        storage_reference=STORAGE,
        object_version_reference=OBJECT_VERSION,
        hold_reference="hold-a1-cert",
        source_evidence_reference="hold-source-a1-cert",
        source_evidence_fingerprint=SHA_B,
        imposed_at=AT - timedelta(days=2),
        state=LegalEvidenceLegalHoldState.ACTIVE,
        released_at=None,
    )

    preservation = _preservation(
        hold_history=(hold,),
    )

    assert preservation.preservation_required is True
    assert preservation.legal_hold_currentness.preservation_blocking is True
    assert preservation.state is (
        LegalEvidencePreservationState.LEGAL_HOLD_REQUIRED
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match="L10A2R_C4D6E_A1_PRESERVATION_CLEARANCE_REQUIRED",
    ):
        _authorize(
            preservation=preservation,
        )


def test_authorization_chronology_inversion_rejects() -> None:
    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match="L10A2R_C4D6E_A1_AUTHORIZATION_CHRONOLOGY_INVALID",
    ):
        _authorize(
            authorized_at=AT - timedelta(seconds=1),
        )


def test_authorization_is_frozen_and_payload_bound() -> None:
    value = _authorize()

    with pytest.raises(FrozenInstanceError):
        value.tenant_id = "mutated"  # type: ignore[misc]

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match="L10A2R_C4D6E_A1_SOURCE_BINDING_INVALID",
    ):
        replace(
            value,
            reason_reference="tampered-reason",
        )


def test_source_later_authority_remains_false() -> None:
    preservation = _preservation()
    value = _authorize(
        preservation=preservation,
    )

    assert preservation.orphan_proven is False
    assert preservation.deletion_authorized is False
    assert preservation.provider_delete_authorized is False
    assert preservation.retention.orphan_proven is False
    assert preservation.retention.provider_delete_authorized is False

    # A1 is evidence for a later cleanup workflow, not provider execution.
    assert not hasattr(value, "delete")
    assert not hasattr(value, "delete_object")
    assert not hasattr(value, "delete_objects")
    assert not hasattr(value, "execute")



def test_exact_document_round_trip_preserves_integrity() -> None:
    value = _authorize()

    document = value.to_document()

    assert set(document) == {
        "schema",
        "authorization_version",
        "authorization_id",
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "orphan_proof_fingerprint",
        "disownership_fingerprint",
        "preservation_fingerprint",
        "preservation_assessed_at",
        "authorized_at",
        "reason_reference",
        "fingerprint",
    }

    assert document["authorization_version"] == VERSION
    assert document["fingerprint"] == value.fingerprint

    hydrated = (
        LegalEvidenceProviderCleanupAuthorization
        .from_dict(
            deepcopy(document)
        )
    )

    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint
    assert hydrated.to_document() == document


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda document: document.update(
                {"unexpected_field": "forbidden"}
            ),
            "L10A2R_C4D6E_A1_DOCUMENT_FIELDS_INVALID",
        ),
        (
            lambda document: document.pop(
                "reason_reference"
            ),
            "L10A2R_C4D6E_A1_DOCUMENT_FIELDS_INVALID",
        ),
        (
            lambda document: document.update(
                {"fingerprint": "0" * 128}
            ),
            "L10A2R_C4D6E_A1_FINGERPRINT_MISMATCH",
        ),
        (
            lambda document: document.update(
                {"reason_reference": "tampered-reason"}
            ),
            "L10A2R_C4D6E_A1_FINGERPRINT_MISMATCH",
        ),
        (
            lambda document: document.update(
                {"schema": "wilsy.invalid.cleanup.v1"}
            ),
            "L10A2R_C4D6E_A1_SCHEMA_INVALID",
        ),
        (
            lambda document: document.update(
                {"authorization_version": "v0.0.0-invalid"}
            ),
            "L10A2R_C4D6E_A1_VERSION_INVALID",
        ),
        (
            lambda document: document.update(
                {"provider_delete_authorized": True}
            ),
            "L10A2R_C4D6E_A1_DOCUMENT_FIELDS_INVALID",
        ),
    ],
)
def test_persisted_document_corruption_rejects(
    mutation: Any,
    expected: str,
) -> None:
    document = _authorize().to_document()
    mutation(document)

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match=expected,
    ):
        LegalEvidenceProviderCleanupAuthorization.from_dict(
            document
        )


def test_noncanonical_persisted_timestamp_rejects() -> None:
    document = _authorize().to_document()

    document["authorized_at"] = (
        str(document["authorized_at"])
        .replace("+00:00", "Z")
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match=(
            "L10A2R_C4D6E_A1_"
            "DOCUMENT_TIMESTAMP_INVALID"
        ),
    ):
        LegalEvidenceProviderCleanupAuthorization.from_dict(
            document
        )


def test_non_string_persisted_field_rejects() -> None:
    document = _authorize().to_document()
    document["reason_reference"] = 123

    with pytest.raises(
        LegalEvidenceProviderCleanupAuthorizationError,
        match="L10A2R_C4D6E_A1_DOCUMENT_INVALID",
    ):
        LegalEvidenceProviderCleanupAuthorization.from_dict(
            document
        )


def test_hydration_grants_no_later_authority() -> None:
    hydrated = (
        LegalEvidenceProviderCleanupAuthorization
        .from_dict(
            _authorize().to_document()
        )
    )

    assert not hasattr(
        hydrated,
        "provider_delete_authorized",
    )
    assert not hasattr(
        hydrated,
        "delete",
    )
    assert not hasattr(
        hydrated,
        "delete_object",
    )
    assert not hasattr(
        hydrated,
        "execute",
    )


# ARTIFACT: test_legal_evidence_provider_cleanup_authorization.py
# VERSION: v1.1.0-L10A2R-C4D6E-A1-PROVIDER-CLEANUP-AUTHORIZATION-CERT
# AUTHORITY BOUNDARY: direct pure-domain certificate only
# PROVIDER MUTATION POSTURE: none
# DELETION EXECUTION POSTURE: none
# IAM POSTURE: none
# PERSISTENCE POSTURE: none
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
