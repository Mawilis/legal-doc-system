"""TITLE: WILSY OS HR Document Binary Read Port Certification.
VERSION: v1.0.0-P0-C12F5C-HR-DOCUMENT-READ-PORT-CERT
AUTHORITY: Direct certificate for authority-stateless HR binary retrieval.
EPITOME: Proves exact document/version/provider binding, ordered bounded
streaming chunks, incremental SHA3-512 readback, exact byte-length
verification, corruption rejection and a provider-neutral read protocol.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_read_storage.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F5C-HR-DOCUMENT-READ-PORT-CERT
establishes the first sovereign HR document binary read contract.
AUTHORITY BOUNDARY: provider execution contract only; no IAM, Legal,
registry mutation, HTTP, payroll, billing or financial authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import pathlib

import pytest

from tools.eos.saas.hr.hr_document_read_storage import (
    HR_DOCUMENT_BINARY_READ_SCHEMA,
    MAX_READ_CHUNK_BYTES,
    HrDocumentBinaryReadChunk,
    HrDocumentBinaryReadIntent,
    HrDocumentBinaryReadResult,
    HrDocumentBinaryReadSession,
    HrDocumentBinaryReadStoragePort,
    HrDocumentBinaryReadStoragePortError,
    StreamingReadSHA3512,
    validate_read_chunk_sequence,
    validate_read_result_for_intent,
    validate_read_session_for_intent,
)


PAYLOAD = (
    b"%PDF-1.7\n"
    b"WILSY HR READBACK CERTIFICATE\n"
    b"\x00\x01\xff"
)

DIGEST = hashlib.sha3_512(
    PAYLOAD
).hexdigest()


def intent() -> HrDocumentBinaryReadIntent:
    return HrDocumentBinaryReadIntent(
        tenant_id="tenant-hr-read",
        employee_id="employee-001",
        document_id="hrdoc-001",
        document_version_id="hrdocver-001",
        storage_provider_id="hr-s3",
        storage_object_reference="opaque/hr/object/1",
        object_version_reference="provider-version-1",
        expected_byte_length=len(PAYLOAD),
        expected_sha3_512=DIGEST,
    )


def session() -> HrDocumentBinaryReadSession:
    current = intent()

    return HrDocumentBinaryReadSession(
        provider_name="hr-s3",
        storage_reference="opaque/hr/object/1",
        object_version_reference="provider-version-1",
        read_reference="read-session-001",
        read_intent_fingerprint=current.fingerprint,
    )


def chunks() -> tuple[
    HrDocumentBinaryReadChunk,
    ...,
]:
    return (
        HrDocumentBinaryReadChunk(
            sequence=0,
            data=PAYLOAD[:12],
        ),
        HrDocumentBinaryReadChunk(
            sequence=1,
            data=PAYLOAD[12:],
        ),
    )


def result() -> HrDocumentBinaryReadResult:
    current = intent()

    return HrDocumentBinaryReadResult(
        provider_name=current.storage_provider_id,
        storage_reference=current.storage_object_reference,
        object_version_reference=current.object_version_reference,
        read_reference="read-session-001",
        read_intent_fingerprint=current.fingerprint,
        content_length=len(PAYLOAD),
        content_fingerprint=DIGEST,
        chunk_count=2,
    )


def test_schema_and_chunk_limit_are_explicit() -> None:
    assert (
        HR_DOCUMENT_BINARY_READ_SCHEMA
        == "WILSY-HR-DOCUMENT-BINARY-READ/V1"
    )

    assert MAX_READ_CHUNK_BYTES == 16 * 1024 * 1024


def test_read_intent_binds_exact_business_and_provider_coordinates() -> None:
    value = intent()

    assert value.tenant_id == "tenant-hr-read"
    assert value.employee_id == "employee-001"
    assert value.document_id == "hrdoc-001"
    assert value.document_version_id == "hrdocver-001"
    assert value.storage_provider_id == "hr-s3"
    assert value.storage_object_reference == "opaque/hr/object/1"
    assert value.object_version_reference == "provider-version-1"
    assert value.expected_byte_length == len(PAYLOAD)
    assert value.expected_sha3_512 == DIGEST


def test_read_intent_is_frozen() -> None:
    value = intent()

    with pytest.raises(
        FrozenInstanceError
    ):
        value.tenant_id = "forged"  # type: ignore[misc]


def test_intent_fingerprint_is_lowercase_sha3_512() -> None:
    value = intent()

    assert len(value.fingerprint) == 128
    assert value.fingerprint == value.fingerprint.lower()

    int(
        value.fingerprint,
        16,
    )


def test_intent_fingerprint_is_deterministic() -> None:
    assert (
        intent().fingerprint
        == intent().fingerprint
    )


@pytest.mark.parametrize(
    "field,value",
    (
        ("tenant_id", ""),
        ("tenant_id", "GLOBAL_ROOT"),
        ("employee_id", ""),
        ("document_id", ""),
        ("document_version_id", ""),
        ("storage_provider_id", ""),
        ("storage_object_reference", ""),
        ("object_version_reference", ""),
    ),
)
def test_invalid_identity_or_provider_coordinates_reject(
    field: str,
    value: str,
) -> None:
    kwargs = {
        "tenant_id": "tenant-hr-read",
        "employee_id": "employee-001",
        "document_id": "hrdoc-001",
        "document_version_id": "hrdocver-001",
        "storage_provider_id": "hr-s3",
        "storage_object_reference": "opaque/hr/object/1",
        "object_version_reference": "provider-version-1",
        "expected_byte_length": len(PAYLOAD),
        "expected_sha3_512": DIGEST,
    }

    kwargs[field] = value

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        HrDocumentBinaryReadIntent(
            **kwargs
        )


def test_invalid_digest_rejects() -> None:
    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        HrDocumentBinaryReadIntent(
            tenant_id="tenant-hr-read",
            employee_id="employee-001",
            document_id="hrdoc-001",
            document_version_id="hrdocver-001",
            storage_provider_id="hr-s3",
            storage_object_reference="opaque/hr/object/1",
            object_version_reference="provider-version-1",
            expected_byte_length=len(PAYLOAD),
            expected_sha3_512="0" * 127,
        )


@pytest.mark.parametrize(
    "length",
    (-1, 0, True),
)
def test_invalid_expected_length_rejects(
    length: object,
) -> None:
    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        HrDocumentBinaryReadIntent(
            tenant_id="tenant-hr-read",
            employee_id="employee-001",
            document_id="hrdoc-001",
            document_version_id="hrdocver-001",
            storage_provider_id="hr-s3",
            storage_object_reference="opaque/hr/object/1",
            object_version_reference="provider-version-1",
            expected_byte_length=length,  # type: ignore[arg-type]
            expected_sha3_512=DIGEST,
        )


def test_session_exactly_correlates_to_intent() -> None:
    validate_read_session_for_intent(
        intent(),
        session(),
    )


def test_forged_session_intent_fingerprint_rejects() -> None:
    current = session()

    forged = HrDocumentBinaryReadSession(
        provider_name=current.provider_name,
        storage_reference=current.storage_reference,
        object_version_reference=current.object_version_reference,
        read_reference=current.read_reference,
        read_intent_fingerprint="0" * 128,
    )

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError,
        match="READ_SESSION_SCOPE_MISMATCH",
    ):
        validate_read_session_for_intent(
            intent(),
            forged,
        )


def test_wrong_provider_version_session_rejects() -> None:
    current = session()

    forged = HrDocumentBinaryReadSession(
        provider_name=current.provider_name,
        storage_reference=current.storage_reference,
        object_version_reference="wrong-version",
        read_reference=current.read_reference,
        read_intent_fingerprint=intent().fingerprint,
    )

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError,
        match="READ_SESSION_SCOPE_MISMATCH",
    ):
        validate_read_session_for_intent(
            intent(),
            forged,
        )


def test_read_chunk_preserves_real_bytes() -> None:
    value = HrDocumentBinaryReadChunk(
        sequence=0,
        data=PAYLOAD,
    )

    assert value.data == PAYLOAD
    assert value.byte_length == len(PAYLOAD)

    assert (
        value.chunk_sha3_512
        == hashlib.sha3_512(
            PAYLOAD
        ).hexdigest()
    )


def test_empty_chunk_rejects() -> None:
    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        HrDocumentBinaryReadChunk(
            sequence=0,
            data=b"",
        )


def test_non_bytes_chunk_rejects() -> None:
    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        HrDocumentBinaryReadChunk(
            sequence=0,
            data="bytes",  # type: ignore[arg-type]
        )


def test_oversized_chunk_rejects() -> None:
    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        HrDocumentBinaryReadChunk(
            sequence=0,
            data=b"x" * (
                MAX_READ_CHUNK_BYTES
                + 1
            ),
        )


def test_chunk_sequence_requires_contiguous_zero_based_order() -> None:
    assert (
        validate_read_chunk_sequence(
            chunks()
        )
        == chunks()
    )

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        validate_read_chunk_sequence(
            (
                HrDocumentBinaryReadChunk(
                    sequence=1,
                    data=b"a",
                ),
            )
        )


def test_streaming_read_hasher_recomputes_length_and_sha3() -> None:
    stream = StreamingReadSHA3512()

    stream.update(
        PAYLOAD[:8]
    )

    stream.update(
        PAYLOAD[8:]
    )

    length, digest = stream.finalize()

    assert length == len(PAYLOAD)
    assert digest == DIGEST


def test_streaming_read_hasher_rejects_update_after_finalize() -> None:
    stream = StreamingReadSHA3512()

    stream.update(
        PAYLOAD
    )

    stream.finalize()

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        stream.update(
            b"later"
        )


def test_result_exactly_correlates_to_intent() -> None:
    validate_read_result_for_intent(
        intent(),
        result(),
        chunks(),
    )


def test_result_digest_mismatch_fails_closed() -> None:
    current = result()

    forged = HrDocumentBinaryReadResult(
        provider_name=current.provider_name,
        storage_reference=current.storage_reference,
        object_version_reference=current.object_version_reference,
        read_reference=current.read_reference,
        read_intent_fingerprint=current.read_intent_fingerprint,
        content_length=current.content_length,
        content_fingerprint="0" * 128,
        chunk_count=current.chunk_count,
    )

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError,
        match="READBACK_DIGEST_MISMATCH",
    ):
        validate_read_result_for_intent(
            intent(),
            forged,
            chunks(),
        )


def test_result_length_mismatch_fails_closed() -> None:
    current = result()

    forged = HrDocumentBinaryReadResult(
        provider_name=current.provider_name,
        storage_reference=current.storage_reference,
        object_version_reference=current.object_version_reference,
        read_reference=current.read_reference,
        read_intent_fingerprint=current.read_intent_fingerprint,
        content_length=current.content_length + 1,
        content_fingerprint=current.content_fingerprint,
        chunk_count=current.chunk_count,
    )

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError,
        match="READBACK_LENGTH_MISMATCH",
    ):
        validate_read_result_for_intent(
            intent(),
            forged,
            chunks(),
        )


def test_actual_chunk_bytes_are_independently_reverified() -> None:
    current = result()

    altered = (
        HrDocumentBinaryReadChunk(
            sequence=0,
            data=b"forged",
        ),
    )

    with pytest.raises(
        HrDocumentBinaryReadStoragePortError
    ):
        validate_read_result_for_intent(
            intent(),
            current,
            altered,
        )


def test_read_protocol_surface_is_exact() -> None:
    expected = {
        "begin",
        "read_chunk",
        "complete",
        "abort",
    }

    actual = {
        name
        for name in dir(
            HrDocumentBinaryReadStoragePort
        )
        if not name.startswith("_")
    }

    assert actual == expected


def test_read_port_is_runtime_checkable_protocol() -> None:
    class Adapter:
        def begin(self, request):
            raise NotImplementedError

        def read_chunk(
            self,
            request,
            session,
            *,
            sequence,
            max_bytes,
        ):
            raise NotImplementedError

        def complete(
            self,
            request,
            session,
            chunks,
        ):
            raise NotImplementedError

        def abort(
            self,
            request,
            session,
        ):
            return None

    assert isinstance(
        Adapter(),
        HrDocumentBinaryReadStoragePort,
    )


def test_source_has_no_legal_iam_billing_http_or_provider_imports() -> None:
    import tools.eos.saas.hr.hr_document_read_storage as module

    source = pathlib.Path(
        module.__file__ or ""
    ).read_text(
        encoding="utf-8",
    )

    forbidden = (
        "tools.eos.legal_operations",
        "tools.eos.auth",
        "tools.eos.saas.billing",
        "fastapi",
        "starlette",
        "boto3",
        "botocore",
        "pymongo",
        "payment_execution",
        "settlement_authority",
    )

    assert all(
        token not in source
        for token in forbidden
    )


def test_provider_reference_is_not_authority_surface() -> None:
    value = intent()

    assert value.storage_object_reference

    assert not hasattr(
        value,
        "authorize"
    )

    assert not hasattr(
        value,
        "permission"
    )


# ARTIFACT: tests/unit/test_hr_document_read_storage.py
# VERSION: v1.0.0-P0-C12F5C-HR-DOCUMENT-READ-PORT-CERT
# AUTHORITY BOUNDARY: authority-stateless binary retrieval contract only
# READBACK BOUNDARY: exact length + incremental SHA3-512 re-verification
# PROVIDER BOUNDARY: provider-neutral; no boto/S3 execution here
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
