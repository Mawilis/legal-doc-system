"""TITLE: WILSY OS HR S3 Storage Adapter Direct Certification.
VERSION: v1.0.0-P0-C12F5D-HR-S3-ADAPTER-CERT
AUTHORITY: Direct provider-execution certificate for HR S3 binary storage.
EPITOME: Certifies opaque server-derived keys, encrypted multipart writes,
exact provider evidence, scoped HEAD inspection, GET-based retrieval,
ordered read chunks and fail-closed provider/scope behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_document_s3_storage_adapter.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F5D-HR-S3-ADAPTER-CERT
establishes the first HR S3 write/read adapter direct certificate.
AUTHORITY BOUNDARY: S3 execution only; no IAM, HR business authority,
registry mutation, HTTP, billing, payment or settlement authority.
"""

from __future__ import annotations

from io import BytesIO
import hashlib
import pathlib
from typing import Any

import pytest
from botocore.exceptions import ClientError

from tools.eos.saas.hr.hr_document_read_storage import (
    HrDocumentBinaryReadIntent,
    HrDocumentBinaryReadStoragePort,
    validate_read_result_for_intent,
)
from tools.eos.saas.hr.hr_document_s3_storage_adapter import (
    PROVIDER_NAME,
    HrDocumentS3Configuration,
    HrDocumentS3ReadStorageAdapter,
    HrDocumentS3StorageAdapter,
    HrDocumentS3StorageAdapterError,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryStoragePort,
    HrDocumentBinaryWriteIntent,
    StreamingSHA3512,
    validate_completed_binary_object,
)


PAYLOAD = (
    b"%PDF-1.7\n"
    b"WILSY HR S3 DIRECT CERTIFICATE\n"
    b"\x00\x01\x02\xff"
)


class FakeS3Client:
    def __init__(self) -> None:
        self.calls: list[
            tuple[
                str,
                dict[str, Any],
            ]
        ] = []
        self.objects: dict[
            tuple[str, str],
            dict[str, Any],
        ] = {}
        self.parts: dict[
            tuple[str, str, str],
            list[bytes],
        ] = {}
        self.upload_counter = 0
        self.get_error: Exception | None = None
        self.head_error: Exception | None = None

    def create_multipart_upload(
        self,
        **kwargs: Any,
    ) -> dict[str, str]:
        self.calls.append(
            (
                "create_multipart_upload",
                dict(kwargs),
            )
        )

        self.upload_counter += 1
        upload_id = (
            f"upload-{self.upload_counter}"
        )

        self.parts[
            (
                kwargs["Bucket"],
                kwargs["Key"],
                upload_id,
            )
        ] = []

        return {
            "UploadId": upload_id,
        }

    def upload_part(
        self,
        **kwargs: Any,
    ) -> dict[str, str]:
        self.calls.append(
            (
                "upload_part",
                dict(kwargs),
            )
        )

        key = (
            kwargs["Bucket"],
            kwargs["Key"],
            kwargs["UploadId"],
        )

        self.parts[key].append(
            bytes(
                kwargs["Body"]
            )
        )

        return {
            "ETag":
                f"etag-{kwargs['PartNumber']}"
        }

    def complete_multipart_upload(
        self,
        **kwargs: Any,
    ) -> dict[str, str]:
        self.calls.append(
            (
                "complete_multipart_upload",
                dict(kwargs),
            )
        )

        key = (
            kwargs["Bucket"],
            kwargs["Key"],
            kwargs["UploadId"],
        )

        body = b"".join(
            self.parts[key]
        )

        version_id = "version-001"
        etag = "etag-complete"

        create = next(
            data
            for name, data in self.calls
            if (
                name
                == "create_multipart_upload"
                and data["Key"]
                == kwargs["Key"]
            )
        )

        self.objects[
            (
                kwargs["Bucket"],
                kwargs["Key"],
            )
        ] = {
            "Body": body,
            "VersionId": version_id,
            "ETag": etag,
            "ContentLength": len(body),
            "Metadata": dict(
                create["Metadata"]
            ),
        }

        return {
            "VersionId": version_id,
            "ETag": etag,
        }

    def head_object(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self.calls.append(
            (
                "head_object",
                dict(kwargs),
            )
        )

        if self.head_error is not None:
            raise self.head_error

        current = self.objects[
            (
                kwargs["Bucket"],
                kwargs["Key"],
            )
        ]

        if (
            kwargs.get("VersionId")
            != current["VersionId"]
        ):
            raise ClientError(
                {
                    "Error": {
                        "Code": "NoSuchVersion",
                        "Message": "missing",
                    }
                },
                "HeadObject",
            )

        return {
            "VersionId":
                current["VersionId"],
            "ETag":
                current["ETag"],
            "ContentLength":
                current["ContentLength"],
            "Metadata":
                dict(
                    current["Metadata"]
                ),
        }

    def get_object(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self.calls.append(
            (
                "get_object",
                dict(kwargs),
            )
        )

        if self.get_error is not None:
            raise self.get_error

        current = self.objects[
            (
                kwargs["Bucket"],
                kwargs["Key"],
            )
        ]

        if (
            kwargs.get("VersionId")
            != current["VersionId"]
        ):
            raise ClientError(
                {
                    "Error": {
                        "Code": "NoSuchVersion",
                        "Message": "missing",
                    }
                },
                "GetObject",
            )

        return {
            "Body": BytesIO(
                current["Body"]
            ),
            "VersionId":
                current["VersionId"],
            "ContentLength":
                current["ContentLength"],
            "ETag":
                current["ETag"],
            "Metadata":
                dict(
                    current["Metadata"]
                ),
        }

    def abort_multipart_upload(
        self,
        **kwargs: Any,
    ) -> dict[str, object]:
        self.calls.append(
            (
                "abort_multipart_upload",
                dict(kwargs),
            )
        )

        return {}


def write_intent() -> HrDocumentBinaryWriteIntent:
    return HrDocumentBinaryWriteIntent(
        tenant_id="tenant-hr-s3",
        employee_id="employee-001",
        document_id="document-001",
        document_version_id="document-version-001",
        ingestion_reference="ingestion-001",
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=5_000_000,
    )


def config() -> HrDocumentS3Configuration:
    return HrDocumentS3Configuration(
        bucket="wilsy-hr-documents",
        region="af-south-1",
    )


def build_adapter() -> tuple[
    HrDocumentS3StorageAdapter,
    FakeS3Client,
]:
    client = FakeS3Client()

    return (
        HrDocumentS3StorageAdapter(
            config(),
            client=client,  # type: ignore[arg-type]
        ),
        client,
    )


def build_read_adapter(
    client: FakeS3Client | None = None,
) -> tuple[
    HrDocumentS3ReadStorageAdapter,
    FakeS3Client,
]:
    actual_client = (
        client
        if client is not None
        else FakeS3Client()
    )

    return (
        HrDocumentS3ReadStorageAdapter(
            config(),
            client=actual_client,  # type: ignore[arg-type]
        ),
        actual_client,
    )

def upload(
    adapter: HrDocumentS3StorageAdapter,
):
    intent = write_intent()
    session = adapter.begin(
        intent
    )

    chunk = adapter.write_chunk(
        intent,
        session,
        sequence=0,
        chunk=PAYLOAD,
    )

    stream = StreamingSHA3512()
    stream.update(
        PAYLOAD
    )

    length, digest = (
        stream.finalize()
    )

    evidence = adapter.complete(
        intent,
        session,
        (
            chunk,
        ),
        observed_length=length,
        observed_fingerprint=digest,
    )

    validate_completed_binary_object(
        intent=intent,
        chunks=(
            chunk,
        ),
        evidence=evidence,
        observed_length=length,
        observed_fingerprint=digest,
    )

    return (
        intent,
        evidence,
    )


def test_write_adapter_implements_only_frozen_write_protocol() -> None:
    adapter, _ = build_adapter()

    write_port: HrDocumentBinaryStoragePort = adapter

    assert isinstance(
        write_port,
        HrDocumentBinaryStoragePort,
    )

    assert not isinstance(
        adapter,
        HrDocumentBinaryReadStoragePort,
    )

    assert not hasattr(
        adapter,
        "read_chunk",
    )


def test_read_adapter_implements_only_frozen_read_protocol() -> None:
    adapter, _ = build_read_adapter()

    read_port: HrDocumentBinaryReadStoragePort = adapter

    assert isinstance(
        read_port,
        HrDocumentBinaryReadStoragePort,
    )

    assert not isinstance(
        adapter,
        HrDocumentBinaryStoragePort,
    )

    assert not hasattr(
        adapter,
        "write_chunk",
    )

    assert not hasattr(
        adapter,
        "inspect",
    )



def test_configuration_defaults_to_af_south_1() -> None:
    value = HrDocumentS3Configuration(
        bucket="wilsy-hr-documents"
    )

    assert (
        value.region
        == "af-south-1"
    )


def test_invalid_bucket_rejects() -> None:
    with pytest.raises(
        HrDocumentS3StorageAdapterError
    ):
        HrDocumentS3Configuration(
            bucket="INVALID_BUCKET"
        )


def test_begin_uses_server_derived_opaque_key_and_encryption() -> None:
    adapter, client = build_adapter()
    intent = write_intent()

    session = adapter.begin(
        intent
    )

    call = client.calls[-1]

    assert (
        call[0]
        == "create_multipart_upload"
    )

    kwargs = call[1]

    assert (
        kwargs["Bucket"]
        == "wilsy-hr-documents"
    )

    assert (
        kwargs["ServerSideEncryption"]
        == "AES256"
    )

    assert (
        kwargs["ContentType"]
        == "application/pdf"
    )

    assert (
        kwargs["Metadata"][
            "wilsy-intent-sha3-512"
        ]
        == intent.fingerprint
    )

    key = kwargs["Key"]

    for raw in (
        intent.tenant_id,
        intent.employee_id,
        intent.document_id,
        intent.document_version_id,
        intent.ingestion_reference,
        intent.original_filename,
    ):
        assert raw not in key

    assert (
        session.storage_reference
        == key
    )

    assert (
        session.provider_name
        == PROVIDER_NAME
    )


def test_kms_configuration_uses_aws_kms() -> None:
    client = FakeS3Client()

    adapter = HrDocumentS3StorageAdapter(
        HrDocumentS3Configuration(
            bucket="wilsy-hr-documents",
            kms_key_id="kms-key-001",
        ),
        client=client,  # type: ignore[arg-type]
    )

    adapter.begin(
        write_intent()
    )

    kwargs = client.calls[-1][1]

    assert (
        kwargs["ServerSideEncryption"]
        == "aws:kms"
    )

    assert (
        kwargs["SSEKMSKeyId"]
        == "kms-key-001"
    )


def test_write_chunk_uses_exact_multipart_coordinates() -> None:
    adapter, client = build_adapter()
    intent = write_intent()
    session = adapter.begin(
        intent
    )

    evidence = adapter.write_chunk(
        intent,
        session,
        sequence=0,
        chunk=PAYLOAD,
    )

    name, kwargs = client.calls[-1]

    assert name == "upload_part"
    assert kwargs["PartNumber"] == 1
    assert kwargs["Body"] == PAYLOAD

    assert (
        evidence.sequence
        == 0
    )

    assert (
        evidence.chunk_length
        == len(PAYLOAD)
    )


def test_scope_substitution_rejects_before_provider_write() -> None:
    adapter, client = build_adapter()

    first = write_intent()
    session = adapter.begin(
        first
    )

    forged = HrDocumentBinaryWriteIntent(
        tenant_id="tenant-other",
        employee_id=first.employee_id,
        document_id=first.document_id,
        document_version_id=first.document_version_id,
        ingestion_reference=first.ingestion_reference,
        media_type=first.media_type,
        original_filename=first.original_filename,
        admitted_max_content_length=first.admitted_max_content_length,
    )

    before = len(
        client.calls
    )

    with pytest.raises(
        HrDocumentS3StorageAdapterError
    ):
        adapter.write_chunk(
            forged,
            session,
            sequence=0,
            chunk=PAYLOAD,
        )

    assert (
        len(client.calls)
        == before
    )


def test_complete_returns_exact_provider_evidence() -> None:
    adapter, _ = build_adapter()

    intent, evidence = upload(
        adapter
    )

    assert (
        evidence.provider_name
        == PROVIDER_NAME
    )

    assert (
        evidence.object_version_reference
        == "version-001"
    )

    assert (
        evidence.provider_integrity_reference
        == "etag-complete"
    )

    assert (
        evidence.write_intent_fingerprint
        == intent.fingerprint
    )

    assert (
        evidence.content_length
        == len(PAYLOAD)
    )

    assert (
        evidence.content_fingerprint
        == hashlib.sha3_512(
            PAYLOAD
        ).hexdigest()
    )


def test_inspect_uses_exact_version_and_validates_metadata() -> None:
    adapter, client = build_adapter()

    intent, evidence = upload(
        adapter
    )

    observed = adapter.inspect(
        intent,
        evidence,
    )

    assert observed == evidence

    name, kwargs = client.calls[-1]

    assert name == "head_object"
    assert (
        kwargs["VersionId"]
        == evidence.object_version_reference
    )


def test_abort_uses_exact_upload_session() -> None:
    adapter, client = build_adapter()
    intent = write_intent()
    session = adapter.begin(
        intent
    )

    adapter.abort(
        intent,
        session,
    )

    name, kwargs = client.calls[-1]

    assert (
        name
        == "abort_multipart_upload"
    )

    assert (
        kwargs["UploadId"]
        == session.write_session_reference
    )


def test_readback_uses_get_object_and_reverifies_bytes() -> None:
    write_adapter, client = build_adapter()

    _, evidence = upload(
        write_adapter
    )

    read_adapter, _ = build_read_adapter(
        client
    )

    request = HrDocumentBinaryReadIntent(
        tenant_id="tenant-hr-s3",
        employee_id="employee-001",
        document_id="document-001",
        document_version_id="document-version-001",
        storage_provider_id=evidence.provider_name,
        storage_object_reference=evidence.storage_reference,
        object_version_reference=evidence.object_version_reference,
        expected_byte_length=evidence.content_length,
        expected_sha3_512=evidence.content_fingerprint,
    )

    read_session = read_adapter.begin(
        request
    )

    read_chunk = read_adapter.read_chunk(
        request,
        read_session,
        sequence=0,
        max_bytes=1024 * 1024,
    )

    result = read_adapter.complete(
        request,
        read_session,
        (
            read_chunk,
        ),
    )

    validate_read_result_for_intent(
        request,
        result,
        (
            read_chunk,
        ),
    )

    assert read_chunk.data == PAYLOAD

    assert any(
        name == "get_object"
        for name, _ in client.calls
    )



def test_wrong_read_version_rejects_before_get_object() -> None:
    write_adapter, client = build_adapter()

    _, evidence = upload(
        write_adapter
    )

    read_adapter, _ = build_read_adapter(
        client
    )

    request = HrDocumentBinaryReadIntent(
        tenant_id="tenant-hr-s3",
        employee_id="employee-001",
        document_id="document-001",
        document_version_id="document-version-001",
        storage_provider_id=evidence.provider_name,
        storage_object_reference=evidence.storage_reference,
        object_version_reference="wrong-version",
        expected_byte_length=evidence.content_length,
        expected_sha3_512=evidence.content_fingerprint,
    )

    with pytest.raises(
        HrDocumentS3StorageAdapterError
    ):
        read_adapter.begin(
            request
        )

    name, kwargs = client.calls[-1]

    assert name == "get_object"

    assert (
        kwargs["VersionId"]
        == "wrong-version"
    )



def test_missing_provider_object_fails_closed() -> None:
    write_adapter, client = build_adapter()

    _, evidence = upload(
        write_adapter
    )

    read_adapter, _ = build_read_adapter(
        client
    )

    client.get_error = ClientError(
        {
            "Error": {
                "Code": "NoSuchKey",
                "Message": "missing",
            }
        },
        "GetObject",
    )

    request = HrDocumentBinaryReadIntent(
        tenant_id="tenant-hr-s3",
        employee_id="employee-001",
        document_id="document-001",
        document_version_id="document-version-001",
        storage_provider_id=evidence.provider_name,
        storage_object_reference=evidence.storage_reference,
        object_version_reference=evidence.object_version_reference,
        expected_byte_length=evidence.content_length,
        expected_sha3_512=evidence.content_fingerprint,
    )

    with pytest.raises(
        HrDocumentS3StorageAdapterError
    ):
        read_adapter.begin(
            request
        )



def test_source_has_no_hr_iam_registry_http_or_financial_authority() -> None:
    import tools.eos.saas.hr.hr_document_s3_storage_adapter as module

    source = pathlib.Path(
        module.__file__ or ""
    ).read_text(
        encoding="utf-8",
    )

    forbidden = (
        "tools.eos.auth",
        "hr_document_registry",
        "fastapi",
        "starlette",
        "payment_execution",
        "settlement_authority",
        "billing_authorized",
        "payment_authorized",
    )

    assert all(
        token not in source
        for token in forbidden
    )


# ARTIFACT: tests/unit/test_hr_document_s3_storage_adapter.py
# VERSION: v1.0.0-P0-C12F5D-HR-S3-ADAPTER-CERT
# PROVIDER: AWS S3 execution only
# AUTHORITY BOUNDARY: no IAM, HR business, registry or financial authority
# READBACK: get_object-based real-byte retrieval path
# END OF WILSY OS SOVEREIGN ARTIFACT
