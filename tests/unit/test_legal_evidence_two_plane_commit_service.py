"""Direct certificate for Legal Evidence two-plane commit orchestration.

TITLE: Legal Evidence Two-Plane Commit Service Certificate
VERSION: v1.0.0-L10A2R-C3-TWO-PLANE-COMMIT-SERVICE-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Freeze the orchestration boundary that composes already-certified binary
    object evidence, canonical streamed content identity, immutable C1 metadata,
    C2 metadata durability and P5D reservation/usage reconciliation.

EPITOME:
    ACTIVE RESERVATION
    + VERIFIED PROVIDER OBJECT
    + WILSY STREAM IDENTITY
    -> CANONICAL CONTENT
    -> METADATA COMMIT
    -> RESERVATION / USAGE COMMIT
    -> TWO-PLANE COMMITTED RESULT

    TWO-PLANE COMMITTED
    != AUTHORIZED AVAILABILITY
    != IAM AUTHORIZED
    != RETENTION AUTHORIZED
    != LEGAL HOLD CLEARED
    != BILLING / PAYMENT / SETTLEMENT

TRANSACTION:
    The caller owns one already-active Mongo transaction spanning C2 metadata
    persistence and P5D consume/usage reconciliation. Provider execution occurs
    outside that transaction and must already have produced verified immutable
    object evidence.

PROVIDER:
    This service does not begin, stream, complete, inspect or abort provider
    work. It accepts only already-verified LegalEvidenceBinaryObjectEvidence.

REPLAY:
    Exact C2 metadata replay and exact P5D consumed replay must reconcile.
    Divergence fails closed.

FAIL CLOSED:
    Any tenant/document/intent/content/object/reservation mismatch rejects before
    false commit success.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
from unittest.mock import MagicMock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
)
from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    LegalEvidenceObjectMetadata,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)
from tools.eos.legal_operations.service.legal_evidence_two_plane_commit_service import (
    LegalEvidenceTwoPlaneCommitError,
    LegalEvidenceTwoPlaneCommitResult,
    LegalEvidenceTwoPlaneCommitService,
    LegalEvidenceTwoPlaneCommitTransactionRequiredError,
)


AT = datetime(
    2026,
    9,
    30,
    12,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)

SOURCE_FP = hashlib.sha3_512(
    b"c3-source"
).hexdigest()
CONTENT_FP = hashlib.sha3_512(
    b"c3-streamed-content"
).hexdigest()


class Session:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


def _intent(
    *,
    tenant_id: str = "tenant-c3",
    document_id: str = "document-c3",
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id="matter-c3",
        document_id=document_id,
        ingestion_reference="ingestion-c3",
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=4096,
    )


def _object(
    intent: LegalEvidenceBinaryWriteIntent,
    *,
    content_length: int = 19,
    content_fingerprint: str = CONTENT_FP,
) -> LegalEvidenceBinaryObjectEvidence:
    return LegalEvidenceBinaryObjectEvidence(
        provider_name="aws-s3",
        storage_reference="legal-evidence/v1/c3",
        object_version_reference="version-c3",
        provider_integrity_reference='"etag-c3"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=content_length,
        content_fingerprint=content_fingerprint,
    )


def _reservation(
    *,
    tenant_id: str = "tenant-c3",
    document_id: str = "document-c3",
    storage_bytes: int = 19,
    ingress_bytes: int = 19,
    versions: int = 1,
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id="reservation-c3",
        ingestion_intent_id="ingestion-c3",
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=storage_bytes,
        reserved_ingress_bytes=ingress_bytes,
        reserved_document_versions=versions,
        reserved_at=AT.replace(minute=0),
        expires_at=AT.replace(hour=13),
    )


def _service() -> tuple[
    LegalEvidenceTwoPlaneCommitService,
    MagicMock,
    MagicMock,
]:
    metadata_registry = MagicMock()
    lifecycle_service = MagicMock()

    service = LegalEvidenceTwoPlaneCommitService(
        metadata_registry=metadata_registry,
        lifecycle_service=lifecycle_service,
    )

    return (
        service,
        metadata_registry,
        lifecycle_service,
    )


def test_requires_active_caller_transaction_before_mutation() -> None:
    service, metadata_registry, lifecycle_service = _service()
    intent = _intent()
    object_evidence = _object(intent)

    with pytest.raises(
        LegalEvidenceTwoPlaneCommitTransactionRequiredError,
        match="L10A2R_C3_TRANSACTION_REQUIRED",
    ):
        service.commit(
            reservation=_reservation(),
            intent=intent,
            object_evidence=object_evidence,
            observed_content_length=object_evidence.content_length,
            observed_content_fingerprint=object_evidence.content_fingerprint,
            source_evidence_reference="source-c3",
            source_evidence_fingerprint=SOURCE_FP,
            committed_at=AT,
            session=Session(False),
        )

    metadata_registry.create_or_replay.assert_not_called()
    lifecycle_service.consume.assert_not_called()


def test_success_commits_metadata_before_reservation_usage() -> None:
    service, metadata_registry, lifecycle_service = _service()
    intent = _intent()
    object_evidence = _object(intent)
    reservation = _reservation()

    captured_metadata: list[LegalEvidenceObjectMetadata] = []

    def persist(
        value: LegalEvidenceObjectMetadata,
        *,
        session: object,
    ) -> LegalEvidenceObjectMetadata:
        assert session is not None
        captured_metadata.append(value)
        return value

    metadata_registry.create_or_replay.side_effect = persist

    def consume(
        *,
        tenant_id: str,
        reservation_id: str,
        content: LegalEvidenceContent,
        consumed_at: datetime,
        session: object,
    ) -> LegalEvidenceCapacityReservation:
        assert tenant_id == reservation.tenant_id
        assert reservation_id == reservation.reservation_id
        assert consumed_at == AT
        assert session is not None
        assert content.content_length == object_evidence.content_length
        assert content.content_fingerprint == object_evidence.content_fingerprint
        return reservation.consume(AT)

    lifecycle_service.consume.side_effect = consume

    result = service.commit(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
        observed_content_length=object_evidence.content_length,
        observed_content_fingerprint=object_evidence.content_fingerprint,
        source_evidence_reference="source-c3",
        source_evidence_fingerprint=SOURCE_FP,
        committed_at=AT,
        session=Session(),
    )

    assert type(result) is LegalEvidenceTwoPlaneCommitResult
    assert type(result.content) is LegalEvidenceContent
    assert type(result.metadata) is LegalEvidenceObjectMetadata
    assert (
        result.reservation.status
        is LegalEvidenceCapacityReservationStatus.CONSUMED
    )
    assert result.available is False
    assert result.authorized_availability is False

    assert captured_metadata == [
        result.metadata
    ]

    assert (
        metadata_registry.create_or_replay.call_count
        == 1
    )
    assert lifecycle_service.consume.call_count == 1

    assert (
        metadata_registry.method_calls[0][0]
        == "create_or_replay"
    )


@pytest.mark.parametrize(
    ("field", "value", "code"),
    (
        (
            "tenant_id",
            "tenant-neighbor",
            "L10A2R_C3_RESERVATION_SCOPE_MISMATCH",
        ),
        (
            "document_id",
            "document-neighbor",
            "L10A2R_C3_RESERVATION_SCOPE_MISMATCH",
        ),
        (
            "ingestion_intent_id",
            "ingestion-neighbor",
            "L10A2R_C3_RESERVATION_SCOPE_MISMATCH",
        ),
    ),
)
def test_reservation_must_bind_exact_write_intent(
    field: str,
    value: str,
    code: str,
) -> None:
    service, metadata_registry, lifecycle_service = _service()
    intent = _intent()
    object_evidence = _object(intent)

    reservation = replace(
        _reservation(),
        **{
            field: value,
            "fingerprint": "",
        },
    )

    with pytest.raises(
        LegalEvidenceTwoPlaneCommitError,
        match=code,
    ):
        service.commit(
            reservation=reservation,
            intent=intent,
            object_evidence=object_evidence,
            observed_content_length=object_evidence.content_length,
            observed_content_fingerprint=object_evidence.content_fingerprint,
            source_evidence_reference="source-c3",
            source_evidence_fingerprint=SOURCE_FP,
            committed_at=AT,
            session=Session(),
        )

    metadata_registry.create_or_replay.assert_not_called()
    lifecycle_service.consume.assert_not_called()


def test_reservation_dimensions_must_match_stream() -> None:
    service, metadata_registry, lifecycle_service = _service()
    intent = _intent()
    object_evidence = _object(intent)

    with pytest.raises(
        LegalEvidenceTwoPlaneCommitError,
        match="L10A2R_C3_RESERVATION_DIMENSION_MISMATCH",
    ):
        service.commit(
            reservation=_reservation(
                storage_bytes=20,
                ingress_bytes=19,
            ),
            intent=intent,
            object_evidence=object_evidence,
            observed_content_length=19,
            observed_content_fingerprint=CONTENT_FP,
            source_evidence_reference="source-c3",
            source_evidence_fingerprint=SOURCE_FP,
            committed_at=AT,
            session=Session(),
        )

    metadata_registry.create_or_replay.assert_not_called()
    lifecycle_service.consume.assert_not_called()


def test_provider_object_must_match_observed_stream() -> None:
    service, metadata_registry, lifecycle_service = _service()
    intent = _intent()
    object_evidence = _object(
        intent,
        content_fingerprint="b" * 128,
    )

    with pytest.raises(
        LegalEvidenceTwoPlaneCommitError,
        match="L10A2R_C3_OBJECT_CONTENT_MISMATCH",
    ):
        service.commit(
            reservation=_reservation(),
            intent=intent,
            object_evidence=object_evidence,
            observed_content_length=19,
            observed_content_fingerprint=CONTENT_FP,
            source_evidence_reference="source-c3",
            source_evidence_fingerprint=SOURCE_FP,
            committed_at=AT,
            session=Session(),
        )

    metadata_registry.create_or_replay.assert_not_called()
    lifecycle_service.consume.assert_not_called()


def test_exact_metadata_and_consumed_replay_reconcile() -> None:
    service, metadata_registry, lifecycle_service = _service()
    intent = _intent()
    object_evidence = _object(intent)
    reservation = _reservation()

    persisted: list[LegalEvidenceObjectMetadata] = []

    def persist(
        value: LegalEvidenceObjectMetadata,
        *,
        session: object,
    ) -> LegalEvidenceObjectMetadata:
        del session
        if not persisted:
            persisted.append(value)
        return persisted[0]

    metadata_registry.create_or_replay.side_effect = persist
    lifecycle_service.consume.side_effect = (
        lambda **kwargs: reservation.consume(
            kwargs["consumed_at"]
        )
    )

    first = service.commit(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
        observed_content_length=19,
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c3",
        source_evidence_fingerprint=SOURCE_FP,
        committed_at=AT,
        session=Session(),
    )

    second = service.commit(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
        observed_content_length=19,
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c3",
        source_evidence_fingerprint=SOURCE_FP,
        committed_at=AT,
        session=Session(),
    )

    assert second == first
    assert metadata_registry.create_or_replay.call_count == 2
    assert lifecycle_service.consume.call_count == 2


def test_result_and_public_surface_create_no_availability_authority() -> None:
    assert "available" in LegalEvidenceTwoPlaneCommitResult.__annotations__
    assert (
        "authorized_availability"
        in LegalEvidenceTwoPlaneCommitResult.__annotations__
    )

    public = {
        name.lower()
        for name in dir(
            LegalEvidenceTwoPlaneCommitService
        )
        if not name.startswith("_")
    }

    forbidden = {
        "authorize_availability",
        "make_available",
        "publish",
        "grant_iam",
        "apply_retention",
        "apply_legal_hold",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_two_plane_commit_service.py
# VERSION: v1.0.0-L10A2R-C3-TWO-PLANE-COMMIT-SERVICE-CERT
# AUTHORITY BOUNDARY: exact two-plane commit composition only
# PROVIDER POSTURE: accepts verified object evidence; performs no provider IO
# TRANSACTION POSTURE: caller owns exact active Mongo transaction
# METADATA POSTURE: C2 metadata durability precedes P5D consume/usage
# REPLAY POSTURE: exact metadata + consumed replay only
# AVAILABILITY POSTURE: committed result remains unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
