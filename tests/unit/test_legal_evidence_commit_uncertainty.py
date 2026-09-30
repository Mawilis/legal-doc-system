"""Certificate for immutable Legal Evidence commit-uncertainty evidence.

TITLE: Legal Evidence Commit Uncertainty Domain Certificate
VERSION: v1.0.0-L10A2R-C4A-COMMIT-UNCERTAINTY-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Freeze immutable evidence that a provider object has been verified for one
    exact Legal Evidence ingestion while durable C3 Mongo commitment has not yet
    been proven to the caller.

EPITOME:
    VERIFIED PROVIDER OBJECT
    + ACTIVE CAPACITY RESERVATION
    + EXACT WRITE INTENT
    + WILSY STREAM IDENTITY
    + C3 COMMIT OUTCOME NOT PROVEN
    -> RECONCILIATION REQUIRED

    RECONCILIATION REQUIRED
    != ORPHAN PROVEN
    != MONGO COMMIT FAILED
    != RESERVATION RELEASED
    != OBJECT DELETION AUTHORIZED
    != AUTHORIZED AVAILABILITY

AUTHORITY:
    This domain records uncertainty only. It performs no provider IO, Mongo IO,
    reservation mutation, usage mutation, deletion, retention, legal-hold,
    availability, IAM, billing, payment or settlement action.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
    LegalEvidenceCommitUncertaintyError,
    open_legal_evidence_commit_uncertainty,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)


AT = datetime(
    2026,
    9,
    30,
    13,
    15,
    0,
    123456,
    tzinfo=timezone.utc,
)

CONTENT = b"c4a-provider-completed-content"

CONTENT_FP = hashlib.sha3_512(
    CONTENT
).hexdigest()

SOURCE_FP = hashlib.sha3_512(
    b"c4a-source-evidence"
).hexdigest()


def _intent(
    *,
    tenant_id: str = "tenant-c4a",
    document_id: str = "document-c4a",
    ingestion_reference: str = "ingestion-c4a",
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id="matter-c4a",
        document_id=document_id,
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=4096,
    )


def _reservation(
    *,
    tenant_id: str = "tenant-c4a",
    document_id: str = "document-c4a",
    ingestion_intent_id: str = "ingestion-c4a",
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id="reservation-c4a",
        ingestion_intent_id=ingestion_intent_id,
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=len(CONTENT),
        reserved_ingress_bytes=len(CONTENT),
        reserved_document_versions=1,
        reserved_at=AT - timedelta(minutes=5),
        expires_at=AT + timedelta(minutes=20),
    )


def _object(
    intent: LegalEvidenceBinaryWriteIntent,
    *,
    content_length: int = len(CONTENT),
    content_fingerprint: str = CONTENT_FP,
) -> LegalEvidenceBinaryObjectEvidence:
    return LegalEvidenceBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference="legal-evidence/v1/c4a",
        object_version_reference="version-c4a",
        provider_integrity_reference='"etag-c4a"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=content_length,
        content_fingerprint=content_fingerprint,
    )


def _open() -> LegalEvidenceCommitUncertainty:
    intent = _intent()

    return open_legal_evidence_commit_uncertainty(
        reservation=_reservation(),
        intent=intent,
        object_evidence=_object(intent),
        observed_content_length=len(CONTENT),
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c4a",
        source_evidence_fingerprint=SOURCE_FP,
        detected_at=AT,
    )


def test_exact_provider_and_ingestion_evidence_is_preserved() -> None:
    value = _open()

    assert value.tenant_id == "tenant-c4a"
    assert value.case_matter_id == "matter-c4a"
    assert value.document_id == "document-c4a"
    assert value.ingestion_intent_id == "ingestion-c4a"
    assert value.reservation_id == "reservation-c4a"

    assert value.provider_name == "aws_s3"
    assert value.storage_reference == "legal-evidence/v1/c4a"
    assert value.object_version_reference == "version-c4a"
    assert value.provider_integrity_reference == '"etag-c4a"'

    assert value.content_length == len(CONTENT)
    assert value.content_fingerprint == CONTENT_FP
    assert value.write_intent_fingerprint == _intent().fingerprint

    assert value.source_evidence_reference == "source-c4a"
    assert value.source_evidence_fingerprint == SOURCE_FP


def test_uncertainty_identity_is_server_derived_and_deterministic() -> None:
    first = _open()
    second = _open()

    assert first == second
    assert first.uncertainty_id == second.uncertainty_id
    assert first.fingerprint == second.fingerprint
    assert first.uncertainty_id.startswith(
        "legal-evidence-commit-uncertainty:"
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("tenant_id", "tenant-neighbor"),
        ("document_id", "document-neighbor"),
        ("ingestion_intent_id", "ingestion-neighbor"),
    ),
)
def test_reservation_must_bind_exact_write_intent(
    field: str,
    value: str,
) -> None:
    intent = _intent()

    reservation = replace(
        _reservation(),
        **{
            field: value,
            "fingerprint": "",
        },
    )

    with pytest.raises(
        LegalEvidenceCommitUncertaintyError,
        match="L10A2R_C4A_RESERVATION_SCOPE_MISMATCH",
    ):
        open_legal_evidence_commit_uncertainty(
            reservation=reservation,
            intent=intent,
            object_evidence=_object(intent),
            observed_content_length=len(CONTENT),
            observed_content_fingerprint=CONTENT_FP,
            source_evidence_reference="source-c4a",
            source_evidence_fingerprint=SOURCE_FP,
            detected_at=AT,
        )


def test_reservation_dimensions_must_match_observed_stream() -> None:
    intent = _intent()

    reservation = replace(
        _reservation(),
        reserved_storage_bytes=len(CONTENT) + 1,
        fingerprint="",
    )

    with pytest.raises(
        LegalEvidenceCommitUncertaintyError,
        match="L10A2R_C4A_RESERVATION_DIMENSION_MISMATCH",
    ):
        open_legal_evidence_commit_uncertainty(
            reservation=reservation,
            intent=intent,
            object_evidence=_object(intent),
            observed_content_length=len(CONTENT),
            observed_content_fingerprint=CONTENT_FP,
            source_evidence_reference="source-c4a",
            source_evidence_fingerprint=SOURCE_FP,
            detected_at=AT,
        )


def test_provider_object_must_prove_exact_observed_stream() -> None:
    intent = _intent()

    with pytest.raises(
        LegalEvidenceCommitUncertaintyError,
        match="L10A2R_C4A_OBJECT_CONTENT_MISMATCH",
    ):
        open_legal_evidence_commit_uncertainty(
            reservation=_reservation(),
            intent=intent,
            object_evidence=_object(
                intent,
                content_fingerprint="b" * 128,
            ),
            observed_content_length=len(CONTENT),
            observed_content_fingerprint=CONTENT_FP,
            source_evidence_reference="source-c4a",
            source_evidence_fingerprint=SOURCE_FP,
            detected_at=AT,
        )


def test_uncertainty_round_trip_preserves_exact_fingerprint() -> None:
    value = _open()

    restored = LegalEvidenceCommitUncertainty.from_dict(
        value.to_dict()
    )

    assert restored == value
    assert restored.fingerprint == value.fingerprint


def test_serialized_surface_contains_no_raw_bytes() -> None:
    serialized = _open().to_dict()

    forbidden = {
        "content",
        "content_bytes",
        "body",
        "binary_body",
        "raw_bytes",
    }

    assert forbidden.isdisjoint(serialized)

    assert all(
        not isinstance(
            value,
            (
                bytes,
                bytearray,
            ),
        )
        for value in serialized.values()
    )


def test_uncertainty_does_not_claim_orphan_commit_failure_or_deletion() -> None:
    serialized = _open().to_dict()

    forbidden = {
        "orphan",
        "mongo_commit_failed",
        "metadata_missing",
        "reservation_released",
        "object_deletion_authorized",
        "deleted",
        "available",
        "authorized_availability",
        "retention_satisfied",
        "legal_hold_cleared",
    }

    assert forbidden.isdisjoint(serialized)


def test_public_surface_has_no_execution_or_later_authority() -> None:
    public = {
        name.lower()
        for name in dir(
            LegalEvidenceCommitUncertainty
        )
        if not name.startswith("_")
    }

    forbidden = {
        "inspect",
        "abort",
        "delete",
        "reconcile",
        "consume",
        "release",
        "authorize_availability",
        "make_available",
        "publish",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_commit_uncertainty.py
# VERSION: v1.0.0-L10A2R-C4A-COMMIT-UNCERTAINTY-CERT
# AUTHORITY BOUNDARY: immutable commit-uncertainty evidence only
# PROVIDER POSTURE: verified object evidence accepted; no provider execution
# MONGO POSTURE: no persistence or commit outcome claimed
# ORPHAN POSTURE: uncertainty does not prove orphan status
# DELETION POSTURE: no deletion authority
# AVAILABILITY POSTURE: no availability authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
