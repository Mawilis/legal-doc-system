"""Direct certificate for object-backed canonical Legal Evidence metadata.

TITLE: Legal Evidence Object Metadata Certificate
VERSION: v1.0.0-L10A2R-C1-LEGAL-EVIDENCE-OBJECT-METADATA-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Freeze the metadata-only domain contract that binds one canonical
    LegalEvidenceContent value to one exact provider-neutral binary write intent
    and one verified provider object-version evidence value.

EPITOME:
    CANONICAL LEGAL EVIDENCE CONTENT
    + EXACT BINARY WRITE INTENT
    + VERIFIED PROVIDER OBJECT EVIDENCE
    -> OBJECT-BACKED CANONICAL METADATA
    != MONGO RAW-BYTE STORAGE
    != PROVIDER EXECUTION
    != RESERVATION CONSUMPTION
    != AUTHORIZED AVAILABILITY

INTEGRITY:
    WILSY SHA3-512 content identity remains canonical. Provider-native integrity
    strengthens storage evidence but never replaces WILSY content identity.

CONTROL / OBJECT PLANE:
    The resulting value may be persisted later by the Mongo control plane but
    contains no binary body. Provider object/version coordinates remain evidence
    only and do not become tenant, Legal lifecycle, IAM, retention or financial
    authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    LegalEvidenceObjectMetadata,
    LegalEvidenceObjectMetadataError,
    bind_legal_evidence_object_metadata,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)


AT = datetime(
    2026,
    9,
    30,
    8,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)
SOURCE_FP = "a" * 128


def _content(
    *,
    tenant_id: str = "tenant-r-c1",
    case_matter_id: str = "matter-r-c1",
    document_id: str = "document-r-c1",
    media_type: str = "application/pdf",
    original_filename: str = "evidence.pdf",
    body: bytes = b"canonical evidence",
) -> LegalEvidenceContent:
    return register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        document_id=document_id,
        media_type=media_type,
        original_filename=original_filename,
        content=body,
        source_evidence_reference="source-r-c1",
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=AT,
    )


def _intent(
    content: LegalEvidenceContent,
    *,
    tenant_id: str | None = None,
    case_matter_id: str | None = None,
    document_id: str | None = None,
    media_type: str | None = None,
    original_filename: str | None = None,
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id or content.tenant_id,
        case_matter_id=case_matter_id or content.case_matter_id,
        document_id=document_id or content.document_id,
        ingestion_reference="ingestion-r-c1",
        media_type=media_type or content.media_type,
        original_filename=(
            original_filename or content.original_filename
        ),
        admitted_max_content_length=content.content_length + 100,
    )


def _object_evidence(
    content: LegalEvidenceContent,
    intent: LegalEvidenceBinaryWriteIntent,
    *,
    content_length: int | None = None,
    content_fingerprint: str | None = None,
) -> LegalEvidenceBinaryObjectEvidence:
    return LegalEvidenceBinaryObjectEvidence(
        provider_name="aws-s3",
        storage_reference="legal-evidence/v1/object-r-c1",
        object_version_reference="version-r-c1",
        provider_integrity_reference='"etag-r-c1"',
        write_intent_fingerprint=intent.fingerprint,
        content_length=(
            content.content_length
            if content_length is None
            else content_length
        ),
        content_fingerprint=(
            content.content_fingerprint
            if content_fingerprint is None
            else content_fingerprint
        ),
    )


def _bound() -> LegalEvidenceObjectMetadata:
    content = _content()
    intent = _intent(content)
    evidence = _object_evidence(
        content,
        intent,
    )
    return bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=evidence,
    )


def test_exact_binding_preserves_canonical_content_and_provider_coordinates() -> None:
    content = _content()
    intent = _intent(content)
    evidence = _object_evidence(
        content,
        intent,
    )

    result = bind_legal_evidence_object_metadata(
        content=content,
        intent=intent,
        object_evidence=evidence,
    )

    assert result.tenant_id == content.tenant_id
    assert result.case_matter_id == content.case_matter_id
    assert result.document_id == content.document_id
    assert result.content_reference == content.content_reference
    assert result.content_length == content.content_length
    assert result.content_fingerprint == content.content_fingerprint
    assert result.content_metadata_fingerprint == content.fingerprint

    assert result.provider_name == evidence.provider_name
    assert result.storage_reference == evidence.storage_reference
    assert (
        result.object_version_reference
        == evidence.object_version_reference
    )
    assert (
        result.provider_integrity_reference
        == evidence.provider_integrity_reference
    )
    assert (
        result.write_intent_fingerprint
        == intent.fingerprint
    )


def test_result_contains_no_raw_binary_body() -> None:
    payload = _bound().to_dict()

    forbidden = {
        "content",
        "content_bytes",
        "bytes",
        "body",
        "binary_body",
    }

    assert forbidden.isdisjoint(payload)
    assert all(
        not isinstance(value, (bytes, bytearray))
        for value in payload.values()
    )


@pytest.mark.parametrize(
    ("coordinate", "kwargs", "code"),
    [
        (
            "tenant",
            {"tenant_id": "tenant-neighbor"},
            "L10A2R_C1_INTENT_SCOPE_MISMATCH",
        ),
        (
            "matter",
            {"case_matter_id": "matter-neighbor"},
            "L10A2R_C1_INTENT_SCOPE_MISMATCH",
        ),
        (
            "document",
            {"document_id": "document-neighbor"},
            "L10A2R_C1_INTENT_SCOPE_MISMATCH",
        ),
    ],
)
def test_write_intent_must_bind_exact_content_scope(
    coordinate: str,
    kwargs: dict[str, str],
    code: str,
) -> None:
    del coordinate
    content = _content()
    intent = _intent(
        content,
        **kwargs,
    )
    evidence = _object_evidence(
        content,
        intent,
    )

    with pytest.raises(
        LegalEvidenceObjectMetadataError,
        match=code,
    ):
        bind_legal_evidence_object_metadata(
            content=content,
            intent=intent,
            object_evidence=evidence,
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "media_type": "text/plain",
        },
        {
            "original_filename": "other.pdf",
        },
    ],
)
def test_write_intent_must_bind_exact_content_presentation(
    kwargs: dict[str, str],
) -> None:
    content = _content()
    intent = _intent(
        content,
        **kwargs,
    )
    evidence = _object_evidence(
        content,
        intent,
    )

    with pytest.raises(
        LegalEvidenceObjectMetadataError,
        match="L10A2R_C1_INTENT_CONTENT_MISMATCH",
    ):
        bind_legal_evidence_object_metadata(
            content=content,
            intent=intent,
            object_evidence=evidence,
        )


def test_object_evidence_must_belong_to_exact_write_intent() -> None:
    content = _content()
    intent = _intent(content)

    foreign_intent = LegalEvidenceBinaryWriteIntent(
        tenant_id=content.tenant_id,
        case_matter_id=content.case_matter_id,
        document_id=content.document_id,
        ingestion_reference="different-ingestion-r-c1",
        media_type=content.media_type,
        original_filename=content.original_filename,
        admitted_max_content_length=content.content_length + 100,
    )

    evidence = _object_evidence(
        content,
        foreign_intent,
    )

    with pytest.raises(
        LegalEvidenceObjectMetadataError,
        match="L10A2R_C1_OBJECT_SCOPE_MISMATCH",
    ):
        bind_legal_evidence_object_metadata(
            content=content,
            intent=intent,
            object_evidence=evidence,
        )


@pytest.mark.parametrize(
    ("length_delta", "fingerprint", "code"),
    [
        (
            1,
            None,
            "L10A2R_C1_OBJECT_CONTENT_MISMATCH",
        ),
        (
            0,
            "b" * 128,
            "L10A2R_C1_OBJECT_CONTENT_MISMATCH",
        ),
    ],
)
def test_provider_object_must_prove_exact_wilsy_stream(
    length_delta: int,
    fingerprint: str | None,
    code: str,
) -> None:
    content = _content()
    intent = _intent(content)

    evidence = _object_evidence(
        content,
        intent,
        content_length=(
            content.content_length + length_delta
        ),
        content_fingerprint=(
            content.content_fingerprint
            if fingerprint is None
            else fingerprint
        ),
    )

    with pytest.raises(
        LegalEvidenceObjectMetadataError,
        match=code,
    ):
        bind_legal_evidence_object_metadata(
            content=content,
            intent=intent,
            object_evidence=evidence,
        )


def test_result_is_immutable_and_deterministic() -> None:
    first = _bound()
    second = _bound()

    assert first == second
    assert first.fingerprint == second.fingerprint

    with pytest.raises(FrozenInstanceError):
        first.storage_reference = "changed"  # type: ignore[misc]


def test_round_trip_preserves_exact_fingerprint() -> None:
    value = _bound()

    hydrated = LegalEvidenceObjectMetadata.from_dict(
        value.to_dict()
    )

    assert hydrated == value
    assert hydrated.fingerprint == value.fingerprint


def test_fingerprint_corruption_rejects() -> None:
    payload = _bound().to_dict()
    payload["fingerprint"] = "f" * 128

    with pytest.raises(
        LegalEvidenceObjectMetadataError,
        match="L10A2R_C1_FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceObjectMetadata.from_dict(
            payload
        )


def test_caller_cannot_replace_canonical_wilsy_sha3_with_provider_integrity() -> None:
    value = _bound()

    assert (
        value.content_fingerprint
        != value.provider_integrity_reference
    )
    assert len(value.content_fingerprint) == 128


def test_serialized_surface_has_no_later_authority() -> None:
    keys = {
        key.lower()
        for key in _bound().to_dict()
    }

    forbidden = {
        "authorized_availability",
        "available",
        "reservation_consumed",
        "usage_committed",
        "iam_authorized",
        "retention_authorized",
        "legal_hold",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(keys)


# ARTIFACT: test_legal_evidence_object_metadata.py
# VERSION: v1.0.0-L10A2R-C1-LEGAL-EVIDENCE-OBJECT-METADATA-CERT
# AUTHORITY BOUNDARY: canonical metadata/object-evidence binding only
# CONTROL-PLANE POSTURE: no raw bytes exist on serialized surface
# OBJECT-PLANE POSTURE: provider evidence is evidence, not canonical Legal truth
# INTEGRITY POSTURE: WILSY SHA3-512 content identity remains canonical
# AVAILABILITY POSTURE: metadata binding does not authorize availability
# RESERVATION POSTURE: no capacity reservation lifecycle mutation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
