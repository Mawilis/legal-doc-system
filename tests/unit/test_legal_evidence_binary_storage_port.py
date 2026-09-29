"""Direct certificate for the Legal Evidence binary-storage port.

VERSION: v1.0.0-L10A2R-A3-LEGAL-EVIDENCE-BINARY-STORAGE-PORT-CERT
AUTHORITY: Wilsy OS Core Governance
CERTIFICATION / UPDATE DATE: 2026-09-29
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from hashlib import sha3_512

import pytest

from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    MAX_STREAM_CHUNK_BYTES,
    SCHEMA,
    LegalEvidenceBinaryChunkEvidence,
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryStoragePort,
    LegalEvidenceBinaryStoragePortError,
    LegalEvidenceBinaryWriteIntent,
    LegalEvidenceBinaryWriteSession,
    StreamingSHA3512,
    validate_completed_binary_object,
)


def intent(**overrides: object) -> LegalEvidenceBinaryWriteIntent:
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-a",
        "document_id": "document-a",
        "ingestion_reference": "ingest-a",
        "media_type": "application/pdf",
        "original_filename": "evidence.pdf",
        "admitted_max_content_length": 10_000,
    }
    values.update(overrides)
    return LegalEvidenceBinaryWriteIntent(**values)  # type: ignore[arg-type]


def completed_for(
    value: LegalEvidenceBinaryWriteIntent,
    *,
    raw: bytes = b"abc",
) -> LegalEvidenceBinaryObjectEvidence:
    return LegalEvidenceBinaryObjectEvidence(
        provider_name="synthetic",
        storage_reference="object-a",
        object_version_reference="version-1",
        provider_integrity_reference="provider-integrity",
        write_intent_fingerprint=value.fingerprint,
        content_length=len(raw),
        content_fingerprint=sha3_512(raw).hexdigest(),
    )


def test_write_intent_is_deterministic_sha3_512_and_tenant_bound() -> None:
    first = intent()
    second = intent()
    other = intent(tenant_id="tenant-b")

    assert first.fingerprint == second.fingerprint
    assert first.fingerprint != other.fingerprint
    assert len(first.fingerprint) == 128
    assert first.fingerprint == first.fingerprint.lower()


def test_write_intent_normalizes_media_type_and_rejects_pseudo_tenant() -> None:
    assert intent(media_type="APPLICATION/PDF").media_type == "application/pdf"

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="TENANT_REQUIRED",
    ):
        intent(tenant_id="global")


@pytest.mark.parametrize(
    "field,value",
    [
        ("case_matter_id", ""),
        ("document_id", " bad"),
        ("ingestion_reference", "*"),
        ("original_filename", ""),
        ("admitted_max_content_length", 0),
        ("admitted_max_content_length", True),
    ],
)
def test_write_intent_rejects_malformed_coordinates(
    field: str,
    value: object,
) -> None:
    with pytest.raises(LegalEvidenceBinaryStoragePortError):
        intent(**{field: value})


def test_write_intent_rejects_fingerprint_tampering() -> None:
    value = intent()

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="WRITE_INTENT_FINGERPRINT_MISMATCH",
    ):
        intent(fingerprint="0" * 128)


def test_write_session_binds_exact_intent_fingerprint() -> None:
    value = intent()
    session = LegalEvidenceBinaryWriteSession(
        provider_name="synthetic",
        write_session_reference="session-a",
        storage_reference="object-a",
        write_intent_fingerprint=value.fingerprint,
    )

    assert session.write_intent_fingerprint == value.fingerprint


def test_write_session_rejects_malformed_digest() -> None:
    with pytest.raises(LegalEvidenceBinaryStoragePortError):
        LegalEvidenceBinaryWriteSession(
            provider_name="synthetic",
            write_session_reference="session-a",
            storage_reference="object-a",
            write_intent_fingerprint="bad",
        )


def test_streaming_sha3_matches_one_shot_hash_without_whole_object_contract() -> None:
    chunks = [b"a" * 1024, b"b" * 2048, b"c" * 4096]
    raw = b"".join(chunks)

    stream = StreamingSHA3512()
    for chunk in chunks:
        stream.update(chunk)

    length, digest = stream.finalize()

    assert length == len(raw)
    assert digest == sha3_512(raw).hexdigest()


def test_stream_rejects_empty_nonbytes_oversize_and_post_finalize_updates() -> None:
    stream = StreamingSHA3512()

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="STREAM_CHUNK_EMPTY",
    ):
        stream.update(b"")

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="STREAM_CHUNK_BYTES_REQUIRED",
    ):
        stream.update("x")  # type: ignore[arg-type]

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="CHUNK_TOO_LARGE",
    ):
        stream.update(b"x" * (MAX_STREAM_CHUNK_BYTES + 1))

    stream.update(b"x")
    stream.finalize()

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="STREAM_ALREADY_FINALIZED",
    ):
        stream.update(b"y")


def test_empty_stream_cannot_finalize() -> None:
    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="STREAM_EMPTY",
    ):
        StreamingSHA3512().finalize()


def test_chunk_evidence_requires_orderable_bounded_positive_chunks() -> None:
    value = LegalEvidenceBinaryChunkEvidence(
        sequence=0,
        chunk_length=1,
        provider_part_reference="part-0",
    )
    assert value.sequence == 0

    with pytest.raises(LegalEvidenceBinaryStoragePortError):
        LegalEvidenceBinaryChunkEvidence(
            sequence=-1,
            chunk_length=1,
            provider_part_reference="part",
        )

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="CHUNK_TOO_LARGE",
    ):
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=MAX_STREAM_CHUNK_BYTES + 1,
            provider_part_reference="part",
        )


def test_completed_object_matches_stream_and_intent() -> None:
    raw = b"payload"
    value = intent(admitted_max_content_length=len(raw))
    digest = sha3_512(raw).hexdigest()

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=len(raw),
            provider_part_reference="part-0",
        ),
    )

    completed = completed_for(value, raw=raw)

    validate_completed_binary_object(
        intent=value,
        chunks=chunks,
        observed_length=len(raw),
        observed_fingerprint=digest,
        completed=completed,
    )

    assert completed.proves_stream(
        observed_length=len(raw),
        observed_fingerprint=digest,
    )


def test_cross_tenant_identical_bytes_fail_closed() -> None:
    raw = b"same-bytes"
    tenant_a = intent(tenant_id="tenant-a", ingestion_reference="ingest-a")
    tenant_b = intent(tenant_id="tenant-b", ingestion_reference="ingest-b")

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=len(raw),
            provider_part_reference="part-0",
        ),
    )

    wrong = completed_for(tenant_b, raw=raw)

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="BINARY_CORRELATION_INVALID",
    ):
        validate_completed_binary_object(
            intent=tenant_a,
            chunks=chunks,
            observed_length=len(raw),
            observed_fingerprint=sha3_512(raw).hexdigest(),
            completed=wrong,
        )


def test_cross_document_identical_bytes_fail_closed() -> None:
    raw = b"same-bytes"
    document_a = intent(document_id="document-a")
    document_b = intent(document_id="document-b")

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=len(raw),
            provider_part_reference="part-0",
        ),
    )

    wrong = completed_for(document_b, raw=raw)

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="BINARY_CORRELATION_INVALID",
    ):
        validate_completed_binary_object(
            intent=document_a,
            chunks=chunks,
            observed_length=len(raw),
            observed_fingerprint=sha3_512(raw).hexdigest(),
            completed=wrong,
        )


def test_noncontiguous_chunk_sequence_rejects() -> None:
    raw = b"abcd"
    value = intent(admitted_max_content_length=len(raw))

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=2,
            provider_part_reference="part-0",
        ),
        LegalEvidenceBinaryChunkEvidence(
            sequence=2,
            chunk_length=2,
            provider_part_reference="part-2",
        ),
    )

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="CHUNK_SEQUENCE_INVALID",
    ):
        validate_completed_binary_object(
            intent=value,
            chunks=chunks,
            observed_length=len(raw),
            observed_fingerprint=sha3_512(raw).hexdigest(),
            completed=completed_for(value, raw=raw),
        )


def test_chunk_total_must_equal_observed_length() -> None:
    raw = b"abcd"
    value = intent(admitted_max_content_length=len(raw))

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=3,
            provider_part_reference="part-0",
        ),
    )

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="BINARY_CORRELATION_INVALID",
    ):
        validate_completed_binary_object(
            intent=value,
            chunks=chunks,
            observed_length=len(raw),
            observed_fingerprint=sha3_512(raw).hexdigest(),
            completed=completed_for(value, raw=raw),
        )


def test_admitted_ceiling_is_enforced_after_stream_observation() -> None:
    raw = b"abcd"
    value = intent(admitted_max_content_length=3)

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=len(raw),
            provider_part_reference="part-0",
        ),
    )

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="BINARY_CORRELATION_INVALID",
    ):
        validate_completed_binary_object(
            intent=value,
            chunks=chunks,
            observed_length=len(raw),
            observed_fingerprint=sha3_512(raw).hexdigest(),
            completed=completed_for(value, raw=raw),
        )


def test_provider_content_fingerprint_must_match_wilsy_stream() -> None:
    raw = b"abcd"
    value = intent(admitted_max_content_length=len(raw))

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=len(raw),
            provider_part_reference="part-0",
        ),
    )

    wrong = LegalEvidenceBinaryObjectEvidence(
        provider_name="synthetic",
        storage_reference="object-a",
        object_version_reference="version-1",
        provider_integrity_reference="provider-integrity",
        write_intent_fingerprint=value.fingerprint,
        content_length=len(raw),
        content_fingerprint=sha3_512(b"different").hexdigest(),
    )

    with pytest.raises(
        LegalEvidenceBinaryStoragePortError,
        match="BINARY_CORRELATION_INVALID",
    ):
        validate_completed_binary_object(
            intent=value,
            chunks=chunks,
            observed_length=len(raw),
            observed_fingerprint=sha3_512(raw).hexdigest(),
            completed=wrong,
        )


def test_values_are_frozen() -> None:
    value = intent()

    with pytest.raises(FrozenInstanceError):
        value.tenant_id = "tenant-b"  # type: ignore[misc]


def test_protocol_shape_requires_all_provider_operations() -> None:
    class CompleteAdapter:
        def begin(self, value: LegalEvidenceBinaryWriteIntent):
            raise NotImplementedError

        def write_chunk(
            self,
            session: LegalEvidenceBinaryWriteSession,
            *,
            sequence: int,
            chunk: bytes,
        ):
            raise NotImplementedError

        def complete(
            self,
            session: LegalEvidenceBinaryWriteSession,
            *,
            chunks: tuple[LegalEvidenceBinaryChunkEvidence, ...],
            content_length: int,
            content_fingerprint: str,
        ):
            raise NotImplementedError

        def inspect(self, evidence: LegalEvidenceBinaryObjectEvidence):
            raise NotImplementedError

        def abort(self, session: LegalEvidenceBinaryWriteSession):
            raise NotImplementedError

    class IncompleteAdapter:
        pass

    assert isinstance(CompleteAdapter(), LegalEvidenceBinaryStoragePort)
    assert not isinstance(IncompleteAdapter(), LegalEvidenceBinaryStoragePort)


def test_schema_and_contract_exclude_provider_and_business_authority() -> None:
    value = intent()
    assert value.schema == SCHEMA

    forbidden = {
        "bucket",
        "region",
        "aws_access_key",
        "secret",
        "plan_id",
        "subscription_id",
        "price",
        "amount",
        "currency",
        "permission",
        "court_status",
        "service_status",
        "invoice",
        "payment",
        "settlement",
    }

    assert forbidden.isdisjoint(value.__dataclass_fields__)


# ARTIFACT: test_legal_evidence_binary_storage_port.py
# VERSION: v1.0.0-L10A2R-A3-LEGAL-EVIDENCE-BINARY-STORAGE-PORT-CERT
# AUTHORITY BOUNDARY: direct provider-neutral binary-storage contract evidence only
# TENANT POSTURE: exact tenant/matter/document/ingestion intent and stream correlation
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
