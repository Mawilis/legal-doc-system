"""Direct certificate for Legal Evidence commit-uncertainty reconciliation.

TITLE: Legal Evidence Commit Reconciliation Service Certificate
VERSION: v1.0.0-L10A2R-C4C-COMMIT-RECONCILIATION-SERVICE-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Freeze C4C reconciliation across committed confirmation, recoverable C3
    replay, expiry/unresolved classification and fail-closed partial state.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from unittest.mock import MagicMock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
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
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    LegalEvidenceObjectMetadataRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    LegalEvidenceUsageObservationNotFoundError,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)
from tools.eos.legal_operations.service.legal_evidence_commit_reconciliation_service import (
    LegalEvidenceCommitReconciliationError,
    LegalEvidenceCommitReconciliationOutcome,
    LegalEvidenceCommitReconciliationService,
    LegalEvidenceCommitReconciliationTransactionRequiredError,
)
from tools.eos.legal_operations.service.legal_evidence_two_plane_commit_service import (
    LegalEvidenceTwoPlaneCommitResult,
)


AT = datetime(
    2026,
    9,
    30,
    14,
    30,
    0,
    tzinfo=timezone.utc,
)

CONTENT = b"c4c-content"
CONTENT_FP = hashlib.sha3_512(
    CONTENT
).hexdigest()
SOURCE_FP = hashlib.sha3_512(
    b"c4c-source"
).hexdigest()


class Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


def _intent() -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id="tenant-c4c",
        case_matter_id="matter-c4c",
        document_id="document-c4c",
        ingestion_reference="ingestion-c4c",
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=4096,
    )


def _reservation(
    status: LegalEvidenceCapacityReservationStatus = (
        LegalEvidenceCapacityReservationStatus.ACTIVE
    ),
    *,
    consumed_at: datetime | None = None,
    released_at: datetime | None = None,
    expired_at: datetime | None = None,
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id="tenant-c4c",
        document_id="document-c4c",
        reservation_id="reservation-c4c",
        ingestion_intent_id="ingestion-c4c",
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=len(CONTENT),
        reserved_ingress_bytes=len(CONTENT),
        reserved_document_versions=1,
        reserved_at=AT - timedelta(minutes=10),
        expires_at=AT + timedelta(minutes=30),
        status=status,
        consumed_at=consumed_at,
        released_at=released_at,
        expired_at=expired_at,
    )


def _uncertainty():
    intent = _intent()
    reservation = _reservation()

    evidence = LegalEvidenceBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4c",
        object_version_reference="version-c4c",
        provider_integrity_reference='"etag-c4c"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=len(CONTENT),
        content_fingerprint=CONTENT_FP,
    )

    return open_legal_evidence_commit_uncertainty(
        reservation=reservation,
        intent=intent,
        object_evidence=evidence,
        observed_content_length=len(CONTENT),
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c4c",
        source_evidence_fingerprint=SOURCE_FP,
        detected_at=AT,
    )


def _service(
    *,
    uncertainty,
    reservation,
    metadata=None,
    usage=None,
    recovered=None,
    expired=None,
):
    uncertainty_registry = MagicMock()
    metadata_registry = MagicMock()
    reservation_registry = MagicMock()
    usage_registry = MagicMock()
    lifecycle_service = MagicMock()
    two_plane = MagicMock()

    uncertainty_registry.get.return_value = (
        uncertainty
    )
    reservation_registry.get.return_value = (
        reservation
    )

    if metadata is None:
        metadata_registry.get.side_effect = (
            LegalEvidenceObjectMetadataRegistryNotFoundError()
        )
    else:
        metadata_registry.get.return_value = (
            metadata
        )

    if usage is None:
        usage_registry.get.side_effect = (
            LegalEvidenceUsageObservationNotFoundError(
                "L10A2Q_P3B_OBSERVATION_NOT_FOUND"
            )
        )
    else:
        usage_registry.get.return_value = usage

    if recovered is not None:
        two_plane.commit.return_value = (
            recovered
        )

    if expired is not None:
        lifecycle_service.expire.return_value = (
            expired
        )

    service = LegalEvidenceCommitReconciliationService(
        uncertainty_registry=uncertainty_registry,
        metadata_registry=metadata_registry,
        reservation_registry=reservation_registry,
        usage_registry=usage_registry,
        lifecycle_service=lifecycle_service,
        two_plane_commit_service=two_plane,
    )

    return (
        service,
        uncertainty_registry,
        metadata_registry,
        reservation_registry,
        usage_registry,
        lifecycle_service,
        two_plane,
    )


def _committed_bundle():
    uncertainty = _uncertainty()
    intent = _intent()

    committed_at = AT + timedelta(
        minutes=1
    )

    content = register_observed_legal_evidence_content(
        tenant_id=uncertainty.tenant_id,
        case_matter_id=uncertainty.case_matter_id,
        document_id=uncertainty.document_id,
        media_type=intent.media_type,
        original_filename=intent.original_filename,
        observed_content_length=uncertainty.content_length,
        observed_content_fingerprint=uncertainty.content_fingerprint,
        source_evidence_reference=(
            uncertainty.source_evidence_reference
        ),
        source_evidence_fingerprint=(
            uncertainty.source_evidence_fingerprint
        ),
        registered_at=committed_at,
    )

    evidence = LegalEvidenceBinaryObjectEvidence(
        provider_name=uncertainty.provider_name,
        storage_reference=uncertainty.storage_reference,
        object_version_reference=(
            uncertainty.object_version_reference
        ),
        provider_integrity_reference=(
            uncertainty.provider_integrity_reference
        ),
        write_intent_fingerprint=(
            uncertainty.write_intent_fingerprint
        ),
        content_length=uncertainty.content_length,
        content_fingerprint=(
            uncertainty.content_fingerprint
        ),
    )

    metadata = bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=evidence,
    )

    consumed = _reservation(
        LegalEvidenceCapacityReservationStatus.CONSUMED,
        consumed_at=committed_at,
    )

    usage = observe_legal_evidence_usage(
        content=content
    )

    return (
        uncertainty,
        intent,
        content,
        metadata,
        consumed,
        usage,
        committed_at,
    )


def test_requires_active_transaction_before_reads() -> None:
    uncertainty = _uncertainty()
    service, uncertainty_registry, *_ = _service(
        uncertainty=uncertainty,
        reservation=_reservation(),
    )

    with pytest.raises(
        LegalEvidenceCommitReconciliationTransactionRequiredError,
        match="L10A2R_C4C_TRANSACTION_REQUIRED",
    ):
        service.reconcile(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            intent=_intent(),
            reconciled_at=AT,
            session=Session(False),
        )

    uncertainty_registry.get.assert_not_called()


def test_committed_state_is_confirmed_without_c3_replay() -> None:
    (
        uncertainty,
        intent,
        content,
        metadata,
        consumed,
        usage,
        committed_at,
    ) = _committed_bundle()

    service, _, _, _, _, lifecycle, two_plane = _service(
        uncertainty=uncertainty,
        reservation=consumed,
        metadata=metadata,
        usage=usage,
    )

    result = service.reconcile(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=uncertainty.uncertainty_id,
        intent=intent,
        reconciled_at=committed_at + timedelta(minutes=1),
        session=Session(),
    )

    assert result.outcome is (
        LegalEvidenceCommitReconciliationOutcome.COMMITTED_CONFIRMED
    )
    assert result.content == content
    assert result.metadata == metadata
    assert result.reservation == consumed
    assert result.available is False
    assert result.authorized_availability is False
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False

    two_plane.commit.assert_not_called()
    lifecycle.expire.assert_not_called()


def test_missing_metadata_with_consumed_reservation_fails_closed() -> None:
    uncertainty = _uncertainty()
    consumed = _reservation(
        LegalEvidenceCapacityReservationStatus.CONSUMED,
        consumed_at=AT + timedelta(minutes=1),
    )

    service, *_ = _service(
        uncertainty=uncertainty,
        reservation=consumed,
    )

    with pytest.raises(
        LegalEvidenceCommitReconciliationError,
        match="L10A2R_C4C_CONTROL_PLANE_DIVERGENCE",
    ):
        service.reconcile(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            intent=_intent(),
            reconciled_at=AT + timedelta(minutes=2),
            session=Session(),
        )


def test_metadata_with_active_reservation_fails_closed() -> None:
    (
        uncertainty,
        intent,
        _,
        metadata,
        _,
        usage,
        _,
    ) = _committed_bundle()

    service, *_ = _service(
        uncertainty=uncertainty,
        reservation=_reservation(),
        metadata=metadata,
        usage=usage,
    )

    with pytest.raises(
        LegalEvidenceCommitReconciliationError,
        match="L10A2R_C4C_CONTROL_PLANE_DIVERGENCE",
    ):
        service.reconcile(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            intent=intent,
            reconciled_at=AT + timedelta(minutes=2),
            session=Session(),
        )


def test_committed_metadata_without_usage_fails_closed_not_healed() -> None:
    (
        uncertainty,
        intent,
        _,
        metadata,
        consumed,
        _,
        committed_at,
    ) = _committed_bundle()

    service, _, _, _, _, lifecycle, two_plane = _service(
        uncertainty=uncertainty,
        reservation=consumed,
        metadata=metadata,
        usage=None,
    )

    with pytest.raises(
        LegalEvidenceCommitReconciliationError,
        match="L10A2R_C4C_CONTROL_PLANE_DIVERGENCE",
    ):
        service.reconcile(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            intent=intent,
            reconciled_at=committed_at + timedelta(minutes=1),
            session=Session(),
        )

    two_plane.commit.assert_not_called()
    lifecycle.expire.assert_not_called()


def test_active_unexpired_missing_metadata_uses_exact_c3_recovery() -> None:
    uncertainty = _uncertainty()
    intent = _intent()
    active = _reservation()
    recovered_at = AT + timedelta(minutes=5)

    content = register_observed_legal_evidence_content(
        tenant_id=uncertainty.tenant_id,
        case_matter_id=uncertainty.case_matter_id,
        document_id=uncertainty.document_id,
        media_type=intent.media_type,
        original_filename=intent.original_filename,
        observed_content_length=uncertainty.content_length,
        observed_content_fingerprint=uncertainty.content_fingerprint,
        source_evidence_reference=(
            uncertainty.source_evidence_reference
        ),
        source_evidence_fingerprint=(
            uncertainty.source_evidence_fingerprint
        ),
        registered_at=recovered_at,
    )

    evidence = LegalEvidenceBinaryObjectEvidence(
        provider_name=uncertainty.provider_name,
        storage_reference=uncertainty.storage_reference,
        object_version_reference=(
            uncertainty.object_version_reference
        ),
        provider_integrity_reference=(
            uncertainty.provider_integrity_reference
        ),
        write_intent_fingerprint=(
            uncertainty.write_intent_fingerprint
        ),
        content_length=uncertainty.content_length,
        content_fingerprint=uncertainty.content_fingerprint,
    )

    metadata = bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=evidence,
    )

    consumed = _reservation(
        LegalEvidenceCapacityReservationStatus.CONSUMED,
        consumed_at=recovered_at,
    )

    recovered = LegalEvidenceTwoPlaneCommitResult(
        content=content,
        metadata=metadata,
        reservation=consumed,
    )

    service, _, _, _, _, lifecycle, two_plane = _service(
        uncertainty=uncertainty,
        reservation=active,
        recovered=recovered,
    )

    result = service.reconcile(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=uncertainty.uncertainty_id,
        intent=intent,
        reconciled_at=recovered_at,
        session=Session(),
    )

    assert result.outcome is (
        LegalEvidenceCommitReconciliationOutcome.COMMIT_RECOVERED
    )
    assert result.reservation == consumed
    assert result.content == content
    assert result.metadata == metadata

    two_plane.commit.assert_called_once()
    lifecycle.expire.assert_not_called()


def test_active_at_expiry_expires_and_remains_unresolved() -> None:
    uncertainty = _uncertainty()
    active = _reservation()

    expired = _reservation(
        LegalEvidenceCapacityReservationStatus.EXPIRED,
        expired_at=active.expires_at,
    )

    service, _, _, _, _, lifecycle, two_plane = _service(
        uncertainty=uncertainty,
        reservation=active,
        expired=expired,
    )

    result = service.reconcile(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=uncertainty.uncertainty_id,
        intent=_intent(),
        reconciled_at=active.expires_at,
        session=Session(),
    )

    assert result.outcome is (
        LegalEvidenceCommitReconciliationOutcome.PROVIDER_OBJECT_UNRESOLVED
    )
    assert result.reservation == expired
    assert result.content is None
    assert result.metadata is None
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False

    lifecycle.expire.assert_called_once()
    two_plane.commit.assert_not_called()


@pytest.mark.parametrize(
    "status,time_field",
    [
        (
            LegalEvidenceCapacityReservationStatus.RELEASED,
            "released_at",
        ),
        (
            LegalEvidenceCapacityReservationStatus.EXPIRED,
            "expired_at",
        ),
    ],
)
def test_terminal_nonconsumed_missing_metadata_is_unresolved_not_orphan(
    status,
    time_field,
) -> None:
    uncertainty = _uncertainty()
    kwargs = {
        time_field: (
            AT + timedelta(minutes=31)
            if status
            is LegalEvidenceCapacityReservationStatus.EXPIRED
            else AT + timedelta(minutes=2)
        )
    }

    reservation = _reservation(
        status,
        **kwargs,
    )

    service, _, _, _, _, lifecycle, two_plane = _service(
        uncertainty=uncertainty,
        reservation=reservation,
    )

    result = service.reconcile(
        tenant_id=uncertainty.tenant_id,
        uncertainty_id=uncertainty.uncertainty_id,
        intent=_intent(),
        reconciled_at=AT + timedelta(minutes=3),
        session=Session(),
    )

    assert result.outcome is (
        LegalEvidenceCommitReconciliationOutcome.PROVIDER_OBJECT_UNRESOLVED
    )
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False

    lifecycle.expire.assert_not_called()
    two_plane.commit.assert_not_called()


def test_write_intent_fingerprint_mismatch_rejects_before_state_reads() -> None:
    uncertainty = _uncertainty()

    wrong_intent = LegalEvidenceBinaryWriteIntent(
        tenant_id="tenant-c4c",
        case_matter_id="matter-c4c",
        document_id="document-c4c",
        ingestion_reference="ingestion-c4c",
        media_type="text/plain",
        original_filename="evidence.txt",
        admitted_max_content_length=4096,
    )

    service, _, _, reservation_registry, *_ = _service(
        uncertainty=uncertainty,
        reservation=_reservation(),
    )

    with pytest.raises(
        LegalEvidenceCommitReconciliationError,
        match="L10A2R_C4C_WRITE_INTENT_MISMATCH",
    ):
        service.reconcile(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            intent=wrong_intent,
            reconciled_at=AT,
            session=Session(),
        )

    reservation_registry.get.assert_not_called()


def test_reconciliation_time_cannot_precede_uncertainty() -> None:
    uncertainty = _uncertainty()
    service, *_ = _service(
        uncertainty=uncertainty,
        reservation=_reservation(),
    )

    with pytest.raises(
        LegalEvidenceCommitReconciliationError,
        match="L10A2R_C4C_RECONCILED_AT_PRECEDES_UNCERTAINTY",
    ):
        service.reconcile(
            tenant_id=uncertainty.tenant_id,
            uncertainty_id=uncertainty.uncertainty_id,
            intent=_intent(),
            reconciled_at=AT - timedelta(microseconds=1),
            session=Session(),
        )


def test_outcome_vocabulary_is_closed_and_non_authorizing() -> None:
    assert {
        member.value
        for member in LegalEvidenceCommitReconciliationOutcome
    } == {
        "COMMITTED_CONFIRMED",
        "COMMIT_RECOVERED",
        "PROVIDER_OBJECT_UNRESOLVED",
    }


def test_public_surface_excludes_provider_deletion_and_availability() -> None:
    public = {
        name.lower()
        for name in dir(
            LegalEvidenceCommitReconciliationService
        )
        if not name.startswith("_")
    }

    forbidden = {
        "delete",
        "delete_object",
        "abort",
        "begin",
        "write_chunk",
        "complete",
        "authorize_availability",
        "make_available",
        "publish",
        "clear_legal_hold",
        "satisfy_retention",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(
        public
    )


# ARTIFACT: test_legal_evidence_commit_reconciliation_service.py
# VERSION: v1.0.0-L10A2R-C4C-COMMIT-RECONCILIATION-SERVICE-CERT
# AUTHORITY BOUNDARY: control-plane commit reconciliation only
# PARTIAL STATE POSTURE: contradictory control-plane state fails closed
# C3 POSTURE: only missing-metadata ACTIVE/unexpired state invokes recovery
# P5D POSTURE: ACTIVE at/after expiry reconciles to EXPIRED only
# ORPHAN POSTURE: unresolved provider object is not orphan proof
# PROVIDER POSTURE: no provider IO or deletion
# AVAILABILITY POSTURE: no availability authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
