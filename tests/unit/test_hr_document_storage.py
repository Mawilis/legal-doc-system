"""TITLE: WILSY OS HR Document Binary Storage Port Certification.
VERSION: v1.0.0-P0-C12F2A-HR-DOCUMENT-BINARY-STORAGE-PORT-CERT
AUTHORITY: Direct certification of the provider-neutral HR binary-storage contract.
EPITOME: Proves bounded real-byte streaming, SHA3-512 identity,
exact byte accounting, opaque provider evidence and exact HR
tenant/employee/document/version scope binding without IAM authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_storage.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F2A-HR-DOCUMENT-BINARY-STORAGE-PORT-CERT
establishes the first HR binary-storage pure-contract certificate.
AUTHORITY BOUNDARY: Storage evidence only; no IAM, employment outcome,
payroll, billing, payment execution, settlement or HTTP authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from __future__ import annotations

import ast
import hashlib
import pathlib

import pytest

from tools.eos.saas.hr.hr_document_storage import (
    HR_DOCUMENT_BINARY_STORAGE_SCHEMA,
    MAX_STREAM_CHUNK_BYTES,
    HrDocumentBinaryChunkEvidence,
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryStoragePort,
    HrDocumentBinaryStoragePortError,
    HrDocumentBinaryWriteIntent,
    HrDocumentBinaryWriteSession,
    StreamingSHA3512,
    validate_completed_binary_object,
    validate_object_evidence_for_intent,
    validate_write_session_for_intent,
)


TENANT = "tenant-hr-doc"
EMPLOYEE = "employee-42"
DOCUMENT = "hrdoc-abc"
VERSION_ID = "hrdocver-001"
INGESTION = "ingest-001"


def intent() -> HrDocumentBinaryWriteIntent:
    return HrDocumentBinaryWriteIntent(
        tenant_id=TENANT,
        employee_id=EMPLOYEE,
        document_id=DOCUMENT,
        document_version_id=VERSION_ID,
        ingestion_reference=INGESTION,
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=10_000_000,
    )


def session(
    *,
    fingerprint: str | None = None,
) -> HrDocumentBinaryWriteSession:
    return HrDocumentBinaryWriteSession(
        provider_name="test-provider",
        write_session_reference="session-1",
        storage_reference="opaque/object/ref",
        write_intent_fingerprint=(
            fingerprint
            if fingerprint is not None
            else intent().fingerprint
        ),
    )


def evidence(
    *,
    fingerprint: str | None = None,
    content: bytes = b"real-hr-document-bytes",
) -> HrDocumentBinaryObjectEvidence:
    return HrDocumentBinaryObjectEvidence(
        provider_name="test-provider",
        storage_reference="opaque/object/ref",
        object_version_reference="provider-version-1",
        provider_integrity_reference="provider-integrity-1",
        write_intent_fingerprint=(
            fingerprint
            if fingerprint is not None
            else intent().fingerprint
        ),
        content_length=len(content),
        content_fingerprint=hashlib.sha3_512(
            content
        ).hexdigest(),
    )


def test_schema_and_chunk_ceiling_are_explicit() -> None:
    assert (
        HR_DOCUMENT_BINARY_STORAGE_SCHEMA
        == "WILSY-HR-DOCUMENT-BINARY-STORAGE/V1"
    )

    assert MAX_STREAM_CHUNK_BYTES == 16 * 1024 * 1024


def test_write_intent_binds_exact_hr_coordinates() -> None:
    value = intent()

    assert value.tenant_id == TENANT
    assert value.employee_id == EMPLOYEE
    assert value.document_id == DOCUMENT
    assert value.document_version_id == VERSION_ID
    assert value.ingestion_reference == INGESTION
    assert value.media_type == "application/pdf"
    assert value.original_filename == "appointment-letter.pdf"
    assert value.admitted_max_content_length == 10_000_000

    assert len(value.fingerprint) == 128

    int(
        value.fingerprint,
        16,
    )


@pytest.mark.parametrize(
    "field",
    (
        "tenant_id",
        "employee_id",
        "document_id",
        "document_version_id",
        "ingestion_reference",
    ),
)
def test_blank_identity_coordinates_fail_closed(
    field: str,
) -> None:
    kwargs = {
        "tenant_id": TENANT,
        "employee_id": EMPLOYEE,
        "document_id": DOCUMENT,
        "document_version_id": VERSION_ID,
        "ingestion_reference": INGESTION,
        "media_type": "application/pdf",
        "original_filename": "x.pdf",
        "admitted_max_content_length": 100,
    }

    kwargs[field] = ""

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        HrDocumentBinaryWriteIntent(
            **kwargs
        )


@pytest.mark.parametrize(
    "tenant",
    (
        "default",
        "global",
        "GLOBAL_ROOT",
        "master",
        "*",
    ),
)
def test_pseudo_tenants_fail_closed(
    tenant: str,
) -> None:
    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        HrDocumentBinaryWriteIntent(
            tenant_id=tenant,
            employee_id=EMPLOYEE,
            document_id=DOCUMENT,
            document_version_id=VERSION_ID,
            ingestion_reference=INGESTION,
            media_type="application/pdf",
            original_filename="x.pdf",
            admitted_max_content_length=100,
        )


def test_write_intent_fingerprint_is_deterministic() -> None:
    first = intent()
    second = intent()

    assert first.fingerprint == second.fingerprint


def test_employee_coordinate_changes_write_intent_fingerprint() -> None:
    first = intent()

    second = HrDocumentBinaryWriteIntent(
        tenant_id=TENANT,
        employee_id="employee-99",
        document_id=DOCUMENT,
        document_version_id=VERSION_ID,
        ingestion_reference=INGESTION,
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=10_000_000,
    )

    assert first.fingerprint != second.fingerprint


def test_document_version_changes_write_intent_fingerprint() -> None:
    first = intent()

    second = HrDocumentBinaryWriteIntent(
        tenant_id=TENANT,
        employee_id=EMPLOYEE,
        document_id=DOCUMENT,
        document_version_id="hrdocver-002",
        ingestion_reference=INGESTION,
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=10_000_000,
    )

    assert first.fingerprint != second.fingerprint


def test_forged_write_intent_fingerprint_rejected() -> None:
    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        HrDocumentBinaryWriteIntent(
            tenant_id=TENANT,
            employee_id=EMPLOYEE,
            document_id=DOCUMENT,
            document_version_id=VERSION_ID,
            ingestion_reference=INGESTION,
            media_type="application/pdf",
            original_filename="appointment-letter.pdf",
            admitted_max_content_length=10_000_000,
            fingerprint="0" * 128,
        )


@pytest.mark.parametrize(
    "payload",
    (
        b"%PDF-1.7\x00\x01real-pdf-body",
        b"PK\x03\x04real-docx-zip-bytes\x00\xff",
        bytes(range(1, 128)),
    ),
)
def test_streaming_real_binary_payloads_preserve_length_and_sha3(
    payload: bytes,
) -> None:
    stream = StreamingSHA3512()

    midpoint = max(
        1,
        len(payload) // 2,
    )

    stream.update(
        payload[:midpoint]
    )

    if midpoint < len(payload):
        stream.update(
            payload[midpoint:]
        )

    length, digest = stream.finalize()

    assert length == len(payload)
    assert digest == hashlib.sha3_512(
        payload
    ).hexdigest()


def test_stream_rejects_empty_chunk() -> None:
    stream = StreamingSHA3512()

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        stream.update(
            b""
        )


def test_stream_rejects_non_bytes() -> None:
    stream = StreamingSHA3512()

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        stream.update(
            bytearray(b"x")  # type: ignore[arg-type]
        )


def test_stream_rejects_chunk_over_ceiling() -> None:
    stream = StreamingSHA3512()

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        stream.update(
            b"x"
            * (
                MAX_STREAM_CHUNK_BYTES
                + 1
            )
        )


def test_stream_cannot_finalize_without_bytes() -> None:
    stream = StreamingSHA3512()

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        stream.finalize()


def test_stream_is_immutable_after_finalize() -> None:
    stream = StreamingSHA3512()

    stream.update(
        b"abc"
    )

    stream.finalize()

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        stream.update(
            b"def"
        )

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        stream.finalize()


def test_chunk_evidence_rejects_invalid_sequence() -> None:
    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        HrDocumentBinaryChunkEvidence(
            sequence=-1,
            chunk_length=1,
            provider_part_reference="part-1",
        )


def test_chunk_evidence_rejects_oversized_chunk() -> None:
    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        HrDocumentBinaryChunkEvidence(
            sequence=0,
            chunk_length=MAX_STREAM_CHUNK_BYTES + 1,
            provider_part_reference="part-1",
        )


def test_write_session_requires_exact_intent_scope() -> None:
    current = intent()

    validate_write_session_for_intent(
        intent=current,
        session=session(
            fingerprint=current.fingerprint
        ),
    )

    with pytest.raises(
        HrDocumentBinaryStoragePortError,
        match="P0_C12F2A_SCOPE_MISMATCH",
    ):
        validate_write_session_for_intent(
            intent=current,
            session=session(
                fingerprint="0" * 128
            ),
        )


def test_object_evidence_requires_exact_intent_scope() -> None:
    current = intent()

    validate_object_evidence_for_intent(
        intent=current,
        evidence=evidence(
            fingerprint=current.fingerprint
        ),
    )

    with pytest.raises(
        HrDocumentBinaryStoragePortError,
        match="P0_C12F2A_SCOPE_MISMATCH",
    ):
        validate_object_evidence_for_intent(
            intent=current,
            evidence=evidence(
                fingerprint="0" * 128
            ),
        )


def test_completed_object_accepts_exact_contiguous_stream() -> None:
    payload = b"abcdefghijklmnopqrstuvwxyz"

    chunks = (
        HrDocumentBinaryChunkEvidence(
            sequence=0,
            chunk_length=10,
            provider_part_reference="part-0",
        ),
        HrDocumentBinaryChunkEvidence(
            sequence=1,
            chunk_length=16,
            provider_part_reference="part-1",
        ),
    )

    result = validate_completed_binary_object(
        intent=intent(),
        chunks=chunks,
        evidence=evidence(
            content=payload
        ),
        observed_length=len(payload),
        observed_fingerprint=hashlib.sha3_512(
            payload
        ).hexdigest(),
    )

    assert result is None


def test_completed_object_rejects_non_contiguous_sequence() -> None:
    payload = b"abc"

    chunks = (
        HrDocumentBinaryChunkEvidence(
            sequence=1,
            chunk_length=3,
            provider_part_reference="part-1",
        ),
    )

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        validate_completed_binary_object(
            intent=intent(),
            chunks=chunks,
            evidence=evidence(
                content=payload
            ),
            observed_length=len(payload),
            observed_fingerprint=hashlib.sha3_512(
                payload
            ).hexdigest(),
        )


def test_completed_object_rejects_byte_count_divergence() -> None:
    payload = b"abc"

    chunks = (
        HrDocumentBinaryChunkEvidence(
            sequence=0,
            chunk_length=2,
            provider_part_reference="part-0",
        ),
    )

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        validate_completed_binary_object(
            intent=intent(),
            chunks=chunks,
            evidence=evidence(
                content=payload
            ),
            observed_length=len(payload),
            observed_fingerprint=hashlib.sha3_512(
                payload
            ).hexdigest(),
        )


def test_completed_object_rejects_digest_divergence() -> None:
    payload = b"abc"

    chunks = (
        HrDocumentBinaryChunkEvidence(
            sequence=0,
            chunk_length=3,
            provider_part_reference="part-0",
        ),
    )

    with pytest.raises(
        HrDocumentBinaryStoragePortError
    ):
        validate_completed_binary_object(
            intent=intent(),
            chunks=chunks,
            evidence=evidence(
                content=payload
            ),
            observed_length=len(payload),
            observed_fingerprint=hashlib.sha3_512(
                b"different"
            ).hexdigest(),
        )


def test_provider_references_are_opaque_evidence_not_content_identity() -> None:
    value = evidence()

    assert value.storage_reference
    assert value.object_version_reference
    assert value.provider_integrity_reference

    assert (
        value.provider_integrity_reference
        != value.content_fingerprint
    )


def test_storage_port_protocol_exposes_provider_operations_only() -> None:
    members = set(
        HrDocumentBinaryStoragePort.__dict__
    )

    assert {
        "begin",
        "write_chunk",
        "complete",
        "inspect",
        "abort",
    } <= members

    forbidden = {
        "authorize",
        "grant",
        "assign_role",
        "issue_warning",
        "discipline",
        "pay",
        "settle",
        "price",
        "bill",
    }

    assert members.isdisjoint(
        forbidden
    )


def test_production_module_imports_no_forbidden_authority_domains() -> None:
    import tools.eos.saas.hr.hr_document_storage as module

    path = pathlib.Path(
        module.__file__ or ""
    )

    tree = ast.parse(
        path.read_text(
            encoding="utf-8",
        )
    )

    imported = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.Import,
        ):
            imported.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imported.add(
                node.module or ""
            )

    forbidden_prefixes = (
        "tools.eos.legal_operations",
        "tools.eos.auth",
        "tools.eos.saas.billing",
        "tools.eos.billing",
        "tools.eos.kennel",
    )

    assert not any(
        name.startswith(
            forbidden_prefixes
        )
        for name in imported
    )


def test_source_contains_no_role_or_permission_decisions() -> None:
    import tools.eos.saas.hr.hr_document_storage as module

    source = pathlib.Path(
        module.__file__ or ""
    ).read_text(
        encoding="utf-8",
    )

    forbidden = (
        "ROLE_PERMISSIONS_MAP",
        "authorize_tenant_operation",
        "tenant_role_operation_eligibility",
        "permission_metadata(",
        "financial_execution",
        "payment_execution",
        "settlement_authority",
    )

    assert all(
        token not in source
        for token in forbidden
    )


# ARTIFACT: tests/unit/test_hr_document_storage.py
# VERSION: v1.0.0-P0-C12F2A-HR-DOCUMENT-BINARY-STORAGE-PORT-CERT
# AUTHORITY BOUNDARY: binary-storage contract only
# TENANT POSTURE: tenant/employee coordinates scope evidence but confer no IAM authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
