"""Direct certificate for C4D3B read-only cleanup classification orchestration.

VERSION: v1.0.0-L10A2R-C4D3B-PROVIDER-CLEANUP-CLASSIFICATION-SERVICE-CERT
CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from unittest.mock import MagicMock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    open_legal_evidence_commit_uncertainty,
)
from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_observed_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    bind_legal_evidence_object_metadata,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_classification import (
    LegalEvidenceProviderCleanupClassification,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    LegalEvidenceObjectMetadataRegistryError,
    LegalEvidenceObjectMetadataRegistryNotFoundError,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_classification_service import (
    LegalEvidenceProviderCleanupClassificationService,
    LegalEvidenceProviderCleanupClassificationServiceError,
    LegalEvidenceProviderCleanupClassificationTransactionRequiredError,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderDiscoveryScope,
)


AT = datetime(
    2026,
    9,
    30,
    17,
    0,
    tzinfo=timezone.utc,
)

TENANT_FP = hashlib.sha3_512(
    b"tenant-c4d3b"
).hexdigest()

CONTENT = b"c4d3b-provider-object"
CONTENT_FP = hashlib.sha3_512(
    CONTENT
).hexdigest()

SOURCE_FP = hashlib.sha3_512(
    b"c4d3b-source"
).hexdigest()


class Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


def _scope(
    tenant_id: str = "tenant-c4d3b",
) -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id=tenant_id,
        tenant_scope_fingerprint=TENANT_FP,
    )


def _intent() -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id="tenant-c4d3b",
        case_matter_id="matter-c4d3b",
        document_id="document-c4d3b",
        ingestion_reference="ingestion-c4d3b",
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=4096,
    )


def _reservation() -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id="tenant-c4d3b",
        document_id="document-c4d3b",
        reservation_id="reservation-c4d3b",
        ingestion_intent_id="ingestion-c4d3b",
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=len(CONTENT),
        reserved_ingress_bytes=len(CONTENT),
        reserved_document_versions=1,
        reserved_at=AT - timedelta(minutes=5),
        expires_at=AT + timedelta(minutes=30),
    )


def _object_evidence() -> LegalEvidenceBinaryObjectEvidence:
    intent = _intent()
    return LegalEvidenceBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d3b/object",
        object_version_reference="version-c4d3b",
        provider_integrity_reference='"etag-c4d3b"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=len(CONTENT),
        content_fingerprint=CONTENT_FP,
    )


def _uncertainty():
    return open_legal_evidence_commit_uncertainty(
        reservation=_reservation(),
        intent=_intent(),
        object_evidence=_object_evidence(),
        observed_content_length=len(CONTENT),
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c4d3b",
        source_evidence_fingerprint=SOURCE_FP,
        detected_at=AT,
    )


def _metadata():
    intent = _intent()

    content = register_observed_legal_evidence_content(
        tenant_id="tenant-c4d3b",
        case_matter_id="matter-c4d3b",
        document_id="document-c4d3b",
        media_type=intent.media_type,
        original_filename=intent.original_filename,
        observed_content_length=len(CONTENT),
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c4d3b",
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=AT,
    )

    return bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=_object_evidence(),
    )


def _completed(
    *,
    tenant_id: str = "tenant-c4d3b",
    storage_reference: str = "legal-evidence/c4d3b/object",
    object_version_reference: str = "version-c4d3b",
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name="aws_s3",
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        provider_integrity_reference='"etag-c4d3b"',
        content_length=len(CONTENT),
        last_modified_at=AT,
        observed_at=AT + timedelta(minutes=1),
    )


def _incomplete(
    *,
    tenant_id: str = "tenant-c4d3b",
) -> LegalEvidenceIncompleteWriteSessionObservation:
    return LegalEvidenceIncompleteWriteSessionObservation(
        tenant_id=tenant_id,
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d3b/incomplete",
        write_session_reference="upload-c4d3b",
        initiated_at=AT,
        observed_at=AT + timedelta(minutes=1),
    )


def _service(
    *,
    incomplete=(),
    completed=(),
    metadata=None,
    uncertainties=(),
):
    discovery = MagicMock()
    metadata_registry = MagicMock()
    uncertainty_registry = MagicMock()

    discovery.list_incomplete_write_sessions.return_value = (
        incomplete
    )
    discovery.list_completed_object_versions.return_value = (
        completed
    )
    uncertainty_registry.list_tenant_uncertainties.return_value = (
        uncertainties
    )

    if metadata is None:
        metadata_registry.get_provider_object.side_effect = (
            LegalEvidenceObjectMetadataRegistryNotFoundError(
                "L10A2R_C2_PROVIDER_OBJECT_NOT_FOUND"
            )
        )
    else:
        metadata_registry.get_provider_object.return_value = (
            metadata
        )

    service = LegalEvidenceProviderCleanupClassificationService(
        discovery=discovery,
        metadata_registry=metadata_registry,
        uncertainty_registry=uncertainty_registry,
    )

    return (
        service,
        discovery,
        metadata_registry,
        uncertainty_registry,
    )


def test_requires_active_transaction_before_any_discovery_or_read() -> None:
    service, discovery, metadata_registry, uncertainty_registry = _service(
        completed=(
            _completed(),
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupClassificationTransactionRequiredError,
        match="L10A2R_C4D3B_TRANSACTION_REQUIRED",
    ):
        service.classify_tenant_observations(
            scope=_scope(),
            observed_at=AT,
            session=Session(False),
        )

    discovery.list_incomplete_write_sessions.assert_not_called()
    discovery.list_completed_object_versions.assert_not_called()
    metadata_registry.get_provider_object.assert_not_called()
    uncertainty_registry.list_tenant_uncertainties.assert_not_called()


def test_incomplete_session_is_classified_without_metadata_lookup() -> None:
    service, _, metadata_registry, _ = _service(
        incomplete=(
            _incomplete(),
        ),
    )

    result = service.classify_tenant_observations(
        scope=_scope(),
        observed_at=AT + timedelta(minutes=1),
        session=Session(),
    )

    assert len(result) == 1
    assert result[0].classification is (
        LegalEvidenceProviderCleanupClassification
        .INCOMPLETE_WRITE_SESSION_OBSERVED
    )
    assert result[0].abort_authorized is False
    assert result[0].provider_delete_authorized is False
    assert result[0].orphan_proven is False

    metadata_registry.get_provider_object.assert_not_called()


def test_completed_object_with_exact_metadata_is_canonical() -> None:
    metadata = _metadata()

    service, _, metadata_registry, _ = _service(
        completed=(
            _completed(),
        ),
        metadata=metadata,
    )

    result = service.classify_tenant_observations(
        scope=_scope(),
        observed_at=AT + timedelta(minutes=1),
        session=Session(),
    )

    assert result[0].classification is (
        LegalEvidenceProviderCleanupClassification
        .CANONICALLY_COMMITTED_OBJECT
    )

    metadata_registry.get_provider_object.assert_called_once()


def test_completed_object_with_matching_uncertainty_is_unresolved() -> None:
    uncertainty = _uncertainty()

    service, _, _, _ = _service(
        completed=(
            _completed(),
        ),
        uncertainties=(
            uncertainty,
        ),
    )

    result = service.classify_tenant_observations(
        scope=_scope(),
        observed_at=AT + timedelta(minutes=1),
        session=Session(),
    )

    assert result[0].classification is (
        LegalEvidenceProviderCleanupClassification
        .PROVIDER_OBJECT_UNRESOLVED
    )
    assert result[0].orphan_proven is False
    assert result[0].provider_delete_authorized is False


def test_completed_object_without_canonical_evidence_is_unresolved() -> None:
    service, _, _, _ = _service(
        completed=(
            _completed(),
        ),
    )

    result = service.classify_tenant_observations(
        scope=_scope(),
        observed_at=AT + timedelta(minutes=1),
        session=Session(),
    )

    assert result[0].classification is (
        LegalEvidenceProviderCleanupClassification
        .PROVIDER_OBJECT_UNRESOLVED
    )
    assert result[0].orphan_proven is False
    assert result[0].provider_delete_authorized is False
    assert result[0].abort_authorized is False


def test_existing_metadata_takes_canonical_precedence_over_historical_uncertainty() -> None:
    service, _, _, _ = _service(
        completed=(
            _completed(),
        ),
        metadata=_metadata(),
        uncertainties=(
            _uncertainty(),
        ),
    )

    result = service.classify_tenant_observations(
        scope=_scope(),
        observed_at=AT + timedelta(minutes=1),
        session=Session(),
    )

    assert result[0].classification is (
        LegalEvidenceProviderCleanupClassification
        .CANONICALLY_COMMITTED_OBJECT
    )


def test_cross_tenant_discovery_observation_fails_closed() -> None:
    service, _, _, _ = _service(
        completed=(
            _completed(
                tenant_id="tenant-neighbor",
            ),
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupClassificationServiceError,
        match="L10A2R_C4D3B_DISCOVERY_SCOPE_MISMATCH",
    ):
        service.classify_tenant_observations(
            scope=_scope(),
            observed_at=AT + timedelta(minutes=1),
            session=Session(),
        )


def test_cross_tenant_uncertainty_fails_closed() -> None:
    uncertainty = _uncertainty()

    object.__setattr__(
        uncertainty,
        "tenant_id",
        "tenant-neighbor",
    )

    service, _, _, _ = _service(
        uncertainties=(
            uncertainty,
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupClassificationServiceError,
        match="L10A2R_C4D3B_UNCERTAINTY_SCOPE_MISMATCH",
    ):
        service.classify_tenant_observations(
            scope=_scope(),
            observed_at=AT + timedelta(minutes=1),
            session=Session(),
        )


def test_duplicate_provider_uncertainty_identity_fails_closed() -> None:
    uncertainty = _uncertainty()

    service, _, _, _ = _service(
        uncertainties=(
            uncertainty,
            uncertainty,
        ),
    )

    with pytest.raises(
        LegalEvidenceProviderCleanupClassificationServiceError,
        match="L10A2R_C4D3B_PROVIDER_UNCERTAINTY_AMBIGUOUS",
    ):
        service.classify_tenant_observations(
            scope=_scope(),
            observed_at=AT + timedelta(minutes=1),
            session=Session(),
        )


def test_metadata_registry_failure_other_than_not_found_propagates() -> None:
    service, _, metadata_registry, _ = _service(
        completed=(
            _completed(),
        ),
    )

    metadata_registry.get_provider_object.side_effect = (
        LegalEvidenceObjectMetadataRegistryError(
            "L10A2R_C2_PERSISTENCE_UNAVAILABLE"
        )
    )

    with pytest.raises(
        LegalEvidenceObjectMetadataRegistryError,
        match="L10A2R_C2_PERSISTENCE_UNAVAILABLE",
    ):
        service.classify_tenant_observations(
            scope=_scope(),
            observed_at=AT + timedelta(minutes=1),
            session=Session(),
        )


def test_result_order_is_deterministic() -> None:
    service, _, _, _ = _service(
        incomplete=(
            _incomplete(),
        ),
        completed=(
            _completed(
                storage_reference="legal-evidence/c4d3b/z",
                object_version_reference="version-z",
            ),
            _completed(
                storage_reference="legal-evidence/c4d3b/a",
                object_version_reference="version-a",
            ),
        ),
    )

    first = service.classify_tenant_observations(
        scope=_scope(),
        observed_at=AT + timedelta(minutes=1),
        session=Session(),
    )
    second = service.classify_tenant_observations(
        scope=_scope(),
        observed_at=AT + timedelta(minutes=1),
        session=Session(),
    )

    assert first == second
    assert tuple(
        item.storage_reference
        for item in first
    ) == tuple(
        sorted(
            item.storage_reference
            for item in first
        )
    )


def test_public_surface_excludes_mutation_reconciliation_and_later_authority() -> None:
    public = {
        name.lower()
        for name in dir(
            LegalEvidenceProviderCleanupClassificationService
        )
        if not name.startswith("_")
    }

    forbidden = {
        "delete",
        "delete_object",
        "abort",
        "abort_upload",
        "reconcile",
        "resolve",
        "recover",
        "write",
        "commit",
        "clear_legal_hold",
        "satisfy_retention",
        "authorize_availability",
        "make_available",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(
        public
    )


# ARTIFACT: test_legal_evidence_provider_cleanup_classification_service.py
# VERSION: v1.0.0-L10A2R-C4D3B-PROVIDER-CLEANUP-CLASSIFICATION-SERVICE-CERT
# AUTHORITY BOUNDARY: read-only provider cleanup classification orchestration
# C4C POSTURE: no reconciliation and no write-intent reconstruction
# ORPHAN POSTURE: no orphan proof
# DELETION POSTURE: no deletion authority
# RETENTION POSTURE: no retention/legal-hold authority
# PROVIDER MUTATION POSTURE: discovery reads only
# END OF WILSY OS SOVEREIGN ARTIFACT
