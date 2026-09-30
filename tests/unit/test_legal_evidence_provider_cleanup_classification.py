"""Direct certificate for C4D3A provider cleanup classification."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib

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
from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_classification import (
    LegalEvidenceProviderCleanupClassification,
    LegalEvidenceProviderCleanupClassificationError,
    classify_legal_evidence_provider_observation,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)
from tools.eos.legal_operations.service.legal_evidence_commit_reconciliation_service import (
    LegalEvidenceCommitReconciliationOutcome,
    LegalEvidenceCommitReconciliationResult,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
)


AT = datetime(2026, 9, 30, 15, 0, tzinfo=timezone.utc)
CONTENT = b"c4d3a-provider-object"
CONTENT_FP = hashlib.sha3_512(CONTENT).hexdigest()
SOURCE_FP = hashlib.sha3_512(b"c4d3a-source").hexdigest()


def _intent() -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id="tenant-c4d3a",
        case_matter_id="matter-c4d3a",
        document_id="document-c4d3a",
        ingestion_reference="ingestion-c4d3a",
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
    expired_at: datetime | None = None,
):
    return LegalEvidenceCapacityReservation(
        tenant_id="tenant-c4d3a",
        document_id="document-c4d3a",
        reservation_id="reservation-c4d3a",
        ingestion_intent_id="ingestion-c4d3a",
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=len(CONTENT),
        reserved_ingress_bytes=len(CONTENT),
        reserved_document_versions=1,
        reserved_at=AT - timedelta(minutes=10),
        expires_at=AT + timedelta(minutes=30),
        status=status,
        consumed_at=consumed_at,
        expired_at=expired_at,
    )


def _object_evidence():
    intent = _intent()
    return LegalEvidenceBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d3a/object",
        object_version_reference="version-c4d3a",
        provider_integrity_reference='"etag-c4d3a"',
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
        source_evidence_reference="source-c4d3a",
        source_evidence_fingerprint=SOURCE_FP,
        detected_at=AT,
    )


def _observation():
    return LegalEvidenceCompletedObjectObservation(
        tenant_id="tenant-c4d3a",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d3a/object",
        object_version_reference="version-c4d3a",
        provider_integrity_reference='"etag-c4d3a"',
        content_length=len(CONTENT),
        last_modified_at=AT,
        observed_at=AT + timedelta(minutes=1),
    )


def _metadata_and_content():
    intent = _intent()
    content = register_observed_legal_evidence_content(
        tenant_id="tenant-c4d3a",
        case_matter_id="matter-c4d3a",
        document_id="document-c4d3a",
        media_type=intent.media_type,
        original_filename=intent.original_filename,
        observed_content_length=len(CONTENT),
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c4d3a",
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=AT + timedelta(minutes=2),
    )
    metadata = bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=_object_evidence(),
    )
    return metadata, content


def test_closed_vocabulary() -> None:
    assert {
        item.value
        for item in LegalEvidenceProviderCleanupClassification
    } == {
        "INCOMPLETE_WRITE_SESSION_OBSERVED",
        "CANONICALLY_COMMITTED_OBJECT",
        "PROVIDER_OBJECT_UNRESOLVED",
        "CLEANUP_CANDIDATE",
    }


def test_incomplete_session_is_observation_only() -> None:
    observation = LegalEvidenceIncompleteWriteSessionObservation(
        tenant_id="tenant-c4d3a",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d3a/object",
        write_session_reference="upload-c4d3a",
        initiated_at=AT,
        observed_at=AT + timedelta(minutes=1),
    )
    result = classify_legal_evidence_provider_observation(observation)

    assert result.classification is (
        LegalEvidenceProviderCleanupClassification
        .INCOMPLETE_WRITE_SESSION_OBSERVED
    )
    assert result.abort_authorized is False
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_exact_metadata_is_canonically_committed() -> None:
    metadata, _ = _metadata_and_content()
    result = classify_legal_evidence_provider_observation(
        _observation(),
        metadata=metadata,
    )
    assert result.classification is (
        LegalEvidenceProviderCleanupClassification
        .CANONICALLY_COMMITTED_OBJECT
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", "tenant-wrong"),
        ("provider_name", "provider-wrong"),
        ("storage_reference", "wrong/object"),
        ("object_version_reference", "wrong-version"),
        ("provider_integrity_reference", '"wrong-etag"'),
        ("content_length", len(CONTENT) + 1),
    ],
)
def test_metadata_identity_mismatch_fails_closed(field, value) -> None:
    metadata, _ = _metadata_and_content()
    wrong = replace(metadata, **{field: value}, fingerprint="")

    with pytest.raises(
        LegalEvidenceProviderCleanupClassificationError,
        match="L10A2R_C4D3A_METADATA_OBSERVATION_MISMATCH",
    ):
        classify_legal_evidence_provider_observation(
            _observation(),
            metadata=wrong,
        )


def test_matching_uncertainty_is_unresolved() -> None:
    result = classify_legal_evidence_provider_observation(
        _observation(),
        uncertainty=_uncertainty(),
    )
    assert result.classification is (
        LegalEvidenceProviderCleanupClassification
        .PROVIDER_OBJECT_UNRESOLVED
    )
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


@pytest.mark.parametrize(
    ("state", "fingerprint"),
    [
        (
            LegalEvidenceCompletedObjectIntentMetadataState.NOT_OBSERVED,
            None,
        ),
        (
            LegalEvidenceCompletedObjectIntentMetadataState.ABSENT,
            None,
        ),
        (
            LegalEvidenceCompletedObjectIntentMetadataState.PRESENT,
            "a" * 128,
        ),
    ],
)
def test_no_stronger_canonical_evidence_is_always_unresolved(
    state: LegalEvidenceCompletedObjectIntentMetadataState,
    fingerprint: str | None,
) -> None:
    observation = replace(
        _observation(),
        write_intent_metadata_state=state,
        write_intent_fingerprint=fingerprint,
    )

    result = classify_legal_evidence_provider_observation(
        observation
    )

    assert result.classification is (
        LegalEvidenceProviderCleanupClassification
        .PROVIDER_OBJECT_UNRESOLVED
    )
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False
    assert result.abort_authorized is False


@pytest.mark.parametrize(
    "outcome",
    [
        LegalEvidenceCommitReconciliationOutcome.COMMITTED_CONFIRMED,
        LegalEvidenceCommitReconciliationOutcome.COMMIT_RECOVERED,
    ],
)
def test_committed_reconciliation_is_canonical(outcome) -> None:
    uncertainty = _uncertainty()
    metadata, content = _metadata_and_content()
    consumed_at = content.registered_at
    consumed = _reservation(
        LegalEvidenceCapacityReservationStatus.CONSUMED,
        consumed_at=consumed_at,
    )
    reconciliation = LegalEvidenceCommitReconciliationResult(
        outcome=outcome,
        uncertainty=uncertainty,
        reservation=consumed,
        content=content,
        metadata=metadata,
    )

    result = classify_legal_evidence_provider_observation(
        _observation(),
        uncertainty=uncertainty,
        reconciliation=reconciliation,
    )
    assert result.classification is (
        LegalEvidenceProviderCleanupClassification
        .CANONICALLY_COMMITTED_OBJECT
    )


def test_unresolved_reconciliation_stays_unresolved() -> None:
    uncertainty = _uncertainty()
    active = _reservation()
    expired = _reservation(
        LegalEvidenceCapacityReservationStatus.EXPIRED,
        expired_at=active.expires_at,
    )
    reconciliation = LegalEvidenceCommitReconciliationResult(
        outcome=(
            LegalEvidenceCommitReconciliationOutcome
            .PROVIDER_OBJECT_UNRESOLVED
        ),
        uncertainty=uncertainty,
        reservation=expired,
    )

    result = classify_legal_evidence_provider_observation(
        _observation(),
        uncertainty=uncertainty,
        reconciliation=reconciliation,
    )

    assert result.classification is (
        LegalEvidenceProviderCleanupClassification
        .PROVIDER_OBJECT_UNRESOLVED
    )
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False


def test_incomplete_session_rejects_completed_object_evidence() -> None:
    observation = LegalEvidenceIncompleteWriteSessionObservation(
        tenant_id="tenant-c4d3a",
        provider_name="aws_s3",
        storage_reference="legal-evidence/c4d3a/object",
        write_session_reference="upload-c4d3a",
        initiated_at=AT,
        observed_at=AT + timedelta(minutes=1),
    )
    metadata, _ = _metadata_and_content()

    with pytest.raises(
        LegalEvidenceProviderCleanupClassificationError,
        match="L10A2R_C4D3A_INCOMPLETE_SESSION_EVIDENCE_CONFLICT",
    ):
        classify_legal_evidence_provider_observation(
            observation,
            metadata=metadata,
        )


def test_classification_evidence_is_immutable_and_deterministic() -> None:
    first = classify_legal_evidence_provider_observation(_observation())
    second = classify_legal_evidence_provider_observation(_observation())

    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 128

    with pytest.raises(FrozenInstanceError):
        first.tenant_id = "tenant-mutated"  # type: ignore[misc]


def test_public_surface_has_no_later_authority_commands() -> None:
    public = {
        name.lower()
        for name in dir(
            __import__(
                "tools.eos.legal_operations.domain."
                "legal_evidence_provider_cleanup_classification",
                fromlist=["*"],
            )
        )
        if not name.startswith("_")
    }

    forbidden = {
        "delete",
        "delete_object",
        "abort",
        "abort_upload",
        "clear_legal_hold",
        "satisfy_retention",
        "authorize_availability",
        "make_available",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_provider_cleanup_classification.py
# VERSION: v1.0.0-L10A2R-C4D3A-PROVIDER-CLEANUP-CLASSIFICATION-CERT
# AUTHORITY BOUNDARY: pure provider observation classification only
# ORPHAN POSTURE: no classification proves orphan status
# DELETION POSTURE: no deletion authority
# RETENTION POSTURE: no retention/legal-hold authority
# PROVIDER MUTATION POSTURE: none
# END OF WILSY OS SOVEREIGN ARTIFACT
