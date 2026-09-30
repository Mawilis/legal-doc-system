"""Direct certificate for the Legal Evidence S3 storage adapter.

VERSION: v1.0.0-L10A2R-B3-LEGAL-EVIDENCE-S3-STORAGE-ADAPTER-CERT
AUTHORITY: Wilsy OS Core Governance
CERTIFICATION / UPDATE DATE: 2026-09-29
"""
from __future__ import annotations

from hashlib import sha3_512
from typing import Any, cast

import pytest
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryChunkEvidence,
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryStoragePort,
    LegalEvidenceBinaryWriteIntent,
    LegalEvidenceBinaryWriteSession,
)
from tools.eos.legal_operations.service.legal_evidence_s3_storage_adapter import (
    PROVIDER_NAME,
    S3_MIN_NONFINAL_PART_BYTES,
    LegalEvidenceS3Configuration,
    LegalEvidenceS3StorageAdapter,
    LegalEvidenceS3StorageAdapterError,
    _storage_key,
)


class FakeS3Client:
    """Deterministic in-process S3 capability recorder."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.begin_response: dict[str, Any] = {"UploadId": "upload-1"}
        self.upload_response: dict[str, Any] = {"ETag": "part-etag"}
        self.complete_response: dict[str, Any] = {
            "VersionId": "version-1",
            "ETag": "object-etag",
        }
        self.head_response: dict[str, Any] | None = None
        self.list_multipart_uploads_response: dict[str, Any] = {
            "Uploads": [],
            "IsTruncated": False,
        }
        self.list_object_versions_response: dict[str, Any] = {
            "Versions": [],
            "IsTruncated": False,
        }
        self.raise_on: str | None = None

    def _record(self, name: str, kwargs: dict[str, Any]) -> None:
        self.calls.append((name, kwargs))
        if self.raise_on == name:
            raise ClientError(
                {
                    "Error": {
                        "Code": "SyntheticProviderFailure",
                        "Message": "sensitive-provider-message",
                    }
                },
                name,
            )

    def create_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        self._record("create_multipart_upload", kwargs)
        return dict(self.begin_response)

    def upload_part(self, **kwargs: Any) -> dict[str, Any]:
        self._record("upload_part", kwargs)
        return dict(self.upload_response)

    def complete_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        self._record("complete_multipart_upload", kwargs)
        return dict(self.complete_response)

    def head_object(self, **kwargs: Any) -> dict[str, Any]:
        self._record("head_object", kwargs)
        if self.head_response is None:
            raise AssertionError("head_response must be configured")
        return dict(self.head_response)

    def list_multipart_uploads(self, **kwargs: Any) -> dict[str, Any]:
        self._record(
            "list_multipart_uploads",
            kwargs,
        )
        return dict(
            self.list_multipart_uploads_response
        )

    def list_object_versions(self, **kwargs: Any) -> dict[str, Any]:
        self._record(
            "list_object_versions",
            kwargs,
        )
        return dict(
            self.list_object_versions_response
        )

    def abort_multipart_upload(self, **kwargs: Any) -> dict[str, Any]:
        self._record("abort_multipart_upload", kwargs)
        return {}


def intent(
    *,
    tenant: str = "tenant-a",
    matter: str = "matter-a",
    document: str = "document-a",
    ingestion: str = "ingest-a",
    maximum: int = 64 * 1024 * 1024,
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant,
        case_matter_id=matter,
        document_id=document,
        ingestion_reference=ingestion,
        media_type="application/pdf",
        original_filename="confidential.pdf",
        admitted_max_content_length=maximum,
    )


def adapter(
    client: FakeS3Client,
    *,
    kms: str | None = None,
) -> LegalEvidenceS3StorageAdapter:
    return LegalEvidenceS3StorageAdapter(
        LegalEvidenceS3Configuration(
            bucket="wilsy-legal-evidence-test",
            region="af-south-1",
            kms_key_id=kms,
        ),
        client=cast(BaseClient, client),
    )


def session_for(value: LegalEvidenceBinaryWriteIntent) -> LegalEvidenceBinaryWriteSession:
    return LegalEvidenceBinaryWriteSession(
        provider_name=PROVIDER_NAME,
        write_session_reference="upload-1",
        storage_reference=_storage_key(value),
        write_intent_fingerprint=value.fingerprint,
    )


def evidence_for(
    value: LegalEvidenceBinaryWriteIntent,
    *,
    length: int = 3,
    fingerprint: str | None = None,
) -> LegalEvidenceBinaryObjectEvidence:
    digest = fingerprint or sha3_512(b"abc").hexdigest()
    return LegalEvidenceBinaryObjectEvidence(
        provider_name=PROVIDER_NAME,
        storage_reference=_storage_key(value),
        object_version_reference="version-1",
        provider_integrity_reference="object-etag",
        write_intent_fingerprint=value.fingerprint,
        content_length=length,
        content_fingerprint=digest,
    )


def test_adapter_implements_certified_storage_port() -> None:
    client = FakeS3Client()
    assert isinstance(adapter(client), LegalEvidenceBinaryStoragePort)


def test_provider_key_contains_no_raw_business_coordinates() -> None:
    value = intent(
        tenant="tenant-secret",
        matter="matter-secret",
        document="document-secret",
        ingestion="ingestion-secret",
    )

    key = _storage_key(value)

    assert key.startswith("legal-evidence/v1/t/")
    for forbidden in (
        value.tenant_id,
        value.case_matter_id,
        value.document_id,
        value.ingestion_reference,
    ):
        assert forbidden not in key


def test_begin_uses_server_derived_key_and_no_raw_tenant_metadata() -> None:
    client = FakeS3Client()
    value = intent()

    result = adapter(client).begin(value)

    assert result.storage_reference == _storage_key(value)
    assert len(client.calls) == 1
    name, kwargs = client.calls[0]
    assert name == "create_multipart_upload"
    assert kwargs["Key"] == _storage_key(value)
    assert kwargs["ServerSideEncryption"] == "AES256"

    metadata = kwargs["Metadata"]
    assert metadata["wilsy-intent-sha3-512"] == value.fingerprint
    joined = repr(kwargs)
    assert value.tenant_id not in joined
    assert value.case_matter_id not in joined
    assert value.document_id not in joined
    assert value.ingestion_reference not in joined


def test_kms_configuration_uses_sse_kms_without_credentials() -> None:
    client = FakeS3Client()
    value = intent()

    adapter(client, kms="kms-key-reference").begin(value)

    _, kwargs = client.calls[0]
    assert kwargs["ServerSideEncryption"] == "aws:kms"
    assert kwargs["SSEKMSKeyId"] == "kms-key-reference"
    assert "AWS_ACCESS_KEY_ID" not in repr(kwargs)
    assert "AWS_SECRET_ACCESS_KEY" not in repr(kwargs)


def test_cross_tenant_write_chunk_causes_zero_aws_calls() -> None:
    client = FakeS3Client()
    tenant_a = intent(tenant="tenant-a", ingestion="ingest-a")
    tenant_b = intent(tenant="tenant-b", ingestion="ingest-b")
    foreign_session = session_for(tenant_b)

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_SCOPE_MISMATCH$",
    ):
        adapter(client).write_chunk(
            tenant_a,
            foreign_session,
            sequence=0,
            chunk=b"abc",
        )

    assert client.calls == []


def test_wrong_document_complete_causes_zero_aws_calls() -> None:
    client = FakeS3Client()
    document_a = intent(document="document-a")
    document_b = intent(document="document-b")
    foreign_session = session_for(document_b)

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=3,
            provider_part_reference="part-etag",
        ),
    )

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_SCOPE_MISMATCH$",
    ):
        adapter(client).complete(
            document_a,
            foreign_session,
            chunks=chunks,
            content_length=3,
            content_fingerprint=sha3_512(b"abc").hexdigest(),
        )

    assert client.calls == []


def test_cross_tenant_inspect_causes_zero_aws_calls() -> None:
    client = FakeS3Client()
    tenant_a = intent(tenant="tenant-a", ingestion="ingest-a")
    tenant_b = intent(tenant="tenant-b", ingestion="ingest-b")
    foreign_evidence = evidence_for(tenant_b)

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_SCOPE_MISMATCH$",
    ):
        adapter(client).inspect(tenant_a, foreign_evidence)

    assert client.calls == []


def test_cross_tenant_abort_causes_zero_aws_calls() -> None:
    client = FakeS3Client()
    tenant_a = intent(tenant="tenant-a", ingestion="ingest-a")
    tenant_b = intent(tenant="tenant-b", ingestion="ingest-b")
    foreign_session = session_for(tenant_b)

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_SCOPE_MISMATCH$",
    ):
        adapter(client).abort(tenant_a, foreign_session)

    assert client.calls == []


def test_forged_storage_reference_causes_zero_aws_calls() -> None:
    client = FakeS3Client()
    value = intent()

    forged = LegalEvidenceBinaryWriteSession(
        provider_name=PROVIDER_NAME,
        write_session_reference="upload-1",
        storage_reference="legal-evidence/v1/forged",
        write_intent_fingerprint=value.fingerprint,
    )

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_SCOPE_MISMATCH$",
    ):
        adapter(client).write_chunk(
            value,
            forged,
            sequence=0,
            chunk=b"abc",
        )

    assert client.calls == []


def test_wrong_provider_session_causes_zero_aws_calls() -> None:
    client = FakeS3Client()
    value = intent()

    forged = LegalEvidenceBinaryWriteSession(
        provider_name="other_provider",
        write_session_reference="upload-1",
        storage_reference=_storage_key(value),
        write_intent_fingerprint=value.fingerprint,
    )

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_SCOPE_MISMATCH$",
    ):
        adapter(client).write_chunk(
            value,
            forged,
            sequence=0,
            chunk=b"abc",
        )

    assert client.calls == []


def test_upload_part_maps_zero_based_sequence_to_s3_part_number() -> None:
    client = FakeS3Client()
    value = intent()
    result = adapter(client).write_chunk(
        value,
        session_for(value),
        sequence=0,
        chunk=b"abc",
    )

    assert result.sequence == 0
    assert result.chunk_length == 3
    assert result.provider_part_reference == "part-etag"

    assert len(client.calls) == 1
    name, kwargs = client.calls[0]
    assert name == "upload_part"
    assert kwargs["PartNumber"] == 1
    assert kwargs["Body"] == b"abc"


def test_nonfinal_part_below_s3_minimum_rejects_before_completion_call() -> None:
    client = FakeS3Client()
    value = intent()
    storage = adapter(client)

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=S3_MIN_NONFINAL_PART_BYTES - 1,
            provider_part_reference="part-1",
        ),
        LegalEvidenceBinaryChunkEvidence(
            sequence=1,
            chunk_length=1,
            provider_part_reference="part-2",
        ),
    )

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_NONFINAL_PART_TOO_SMALL$",
    ):
        storage.complete(
            value,
            session_for(value),
            chunks=chunks,
            content_length=S3_MIN_NONFINAL_PART_BYTES,
            content_fingerprint="0" * 128,
        )

    assert client.calls == []


def test_chunk_total_divergence_rejects_before_completion_call() -> None:
    client = FakeS3Client()
    value = intent()
    storage = adapter(client)

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=3,
            provider_part_reference="part-1",
        ),
    )

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_CONTENT_LENGTH_INVALID$",
    ):
        storage.complete(
            value,
            session_for(value),
            chunks=chunks,
            content_length=4,
            content_fingerprint="0" * 128,
        )

    assert client.calls == []


def test_complete_then_head_returns_correlated_object_evidence() -> None:
    client = FakeS3Client()
    value = intent()
    digest = sha3_512(b"abc").hexdigest()

    client.head_response = {
        "ContentLength": 3,
        "Metadata": {"wilsy-intent-sha3-512": value.fingerprint},
        "ETag": "head-etag",
        "VersionId": "version-1",
    }

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=3,
            provider_part_reference="part-etag",
        ),
    )

    result = adapter(client).complete(
        value,
        session_for(value),
        chunks=chunks,
        content_length=3,
        content_fingerprint=digest,
    )

    assert result.content_length == 3
    assert result.content_fingerprint == digest
    assert result.write_intent_fingerprint == value.fingerprint

    assert [name for name, _ in client.calls] == [
        "complete_multipart_upload",
        "head_object",
    ]


def test_provider_metadata_mismatch_fails_closed() -> None:
    client = FakeS3Client()
    value = intent()

    client.head_response = {
        "ContentLength": 3,
        "Metadata": {"wilsy-intent-sha3-512": "0" * 128},
        "ETag": "head-etag",
        "VersionId": "version-1",
    }

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_PROVIDER_METADATA_MISMATCH$",
    ):
        adapter(client).inspect(
            value,
            evidence_for(value),
        )


def test_wrong_object_version_fails_closed() -> None:
    client = FakeS3Client()
    value = intent()

    client.head_response = {
        "ContentLength": 3,
        "Metadata": {"wilsy-intent-sha3-512": value.fingerprint},
        "ETag": "head-etag",
        "VersionId": "different-version",
    }

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_PROVIDER_METADATA_MISMATCH$",
    ):
        adapter(client).inspect(value, evidence_for(value))


def test_missing_version_id_from_completion_fails_closed() -> None:
    client = FakeS3Client()
    value = intent()
    client.complete_response = {"ETag": "object-etag"}

    chunks = (
        LegalEvidenceBinaryChunkEvidence(
            sequence=0,
            chunk_length=3,
            provider_part_reference="part-etag",
        ),
    )

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_PROVIDER_RESPONSE_INVALID$",
    ):
        adapter(client).complete(
            value,
            session_for(value),
            chunks=chunks,
            content_length=3,
            content_fingerprint=sha3_512(b"abc").hexdigest(),
        )

    assert [name for name, _ in client.calls] == [
        "complete_multipart_upload",
    ]


def test_provider_failure_is_bounded_and_does_not_echo_sensitive_message() -> None:
    client = FakeS3Client()
    client.raise_on = "create_multipart_upload"

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_B2_BEGIN_FAILED$",
    ) as captured:
        adapter(client).begin(intent())

    assert str(captured.value) == "L10A2R_B2_BEGIN_FAILED"
    assert "sensitive-provider-message" not in str(captured.value)


def test_abort_calls_only_exact_scoped_upload() -> None:
    client = FakeS3Client()
    value = intent()

    adapter(client).abort(value, session_for(value))

    assert len(client.calls) == 1
    name, kwargs = client.calls[0]
    assert name == "abort_multipart_upload"
    assert kwargs["Key"] == _storage_key(value)
    assert kwargs["UploadId"] == "upload-1"


@pytest.mark.parametrize(
    "bucket",
    (
        "",
        "UPPERCASE-BUCKET",
        "bad..bucket",
        "a",
    ),
)
def test_invalid_bucket_configuration_fails_closed(bucket: str) -> None:
    with pytest.raises(LegalEvidenceS3StorageAdapterError):
        LegalEvidenceS3Configuration(bucket=bucket)


def test_configuration_never_accepts_credentials() -> None:
    assert set(LegalEvidenceS3Configuration.__dataclass_fields__) == {
        "bucket",
        "region",
        "kms_key_id",
    }


# ARTIFACT: test_legal_evidence_s3_storage_adapter.py
# VERSION: v1.0.0-L10A2R-B3-LEGAL-EVIDENCE-S3-STORAGE-ADAPTER-CERT
# AUTHORITY BOUNDARY: direct fake-provider S3 adapter evidence only
# TENANT POSTURE: cross-tenant/document/session/evidence substitution must make zero provider calls
# OPERATIONAL POSTURE: fake-client certificate only; real AWS not yet certified
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT


def test_c4d2r2_exact_head_without_intent_metadata_emits_absent() -> None:
    client = FakeS3Client()

    key = (
        _c4d2_tenant_prefix()
        + "m/opaque-matter/"
        "d/opaque-document/"
        "i/opaque-ingestion/content"
    )

    client.list_object_versions_response = {
        "Versions": [
            {
                "Key": key,
                "VersionId": "version-legacy",
                "ETag": '"etag-legacy"',
                "Size": 77,
                "LastModified": C4D2_AT,
            }
        ],
        "IsTruncated": False,
    }

    client.head_response = {
        "VersionId": "version-legacy",
        "ETag": '"etag-legacy"',
        "ContentLength": 77,
        "Metadata": {},
    }

    result = adapter(
        client
    ).list_completed_object_versions(
        _c4d2_scope(),
        observed_at=C4D2_AT,
    )

    assert len(result) == 1
    assert (
        result[0].write_intent_metadata_state
        is LegalEvidenceCompletedObjectIntentMetadataState.ABSENT
    )
    assert result[0].write_intent_fingerprint is None


@pytest.mark.parametrize(
    "fingerprint",
    [
        "",
        "a" * 127,
        "a" * 129,
        "A" * 128,
        "g" * 128,
    ],
)
def test_c4d2r2_malformed_provider_intent_metadata_fails_closed(
    fingerprint: str,
) -> None:
    client = FakeS3Client()

    key = (
        _c4d2_tenant_prefix()
        + "m/opaque-matter/"
        "d/opaque-document/"
        "i/opaque-ingestion/content"
    )

    client.list_object_versions_response = {
        "Versions": [
            {
                "Key": key,
                "VersionId": "version-bad",
                "ETag": '"etag-bad"',
                "Size": 88,
                "LastModified": C4D2_AT,
            }
        ],
        "IsTruncated": False,
    }

    client.head_response = {
        "VersionId": "version-bad",
        "ETag": '"etag-bad"',
        "ContentLength": 88,
        "Metadata": {
            "wilsy-intent-sha3-512": fingerprint,
        },
    }

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_C4D2R2_PROVIDER_METADATA_INVALID$",
    ):
        adapter(
            client
        ).list_completed_object_versions(
            _c4d2_scope(),
            observed_at=C4D2_AT,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("VersionId", "wrong-version"),
        ("ETag", '"wrong-etag"'),
        ("ContentLength", 90),
        ("Metadata", None),
    ],
)
def test_c4d2r2_head_identity_or_shape_mismatch_fails_closed(
    field: str,
    value: object,
) -> None:
    client = FakeS3Client()

    key = (
        _c4d2_tenant_prefix()
        + "m/opaque-matter/"
        "d/opaque-document/"
        "i/opaque-ingestion/content"
    )

    client.list_object_versions_response = {
        "Versions": [
            {
                "Key": key,
                "VersionId": "version-head",
                "ETag": '"etag-head"',
                "Size": 89,
                "LastModified": C4D2_AT,
            }
        ],
        "IsTruncated": False,
    }

    client.head_response = {
        "VersionId": "version-head",
        "ETag": '"etag-head"',
        "ContentLength": 89,
        "Metadata": {},
    }
    client.head_response[field] = value

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_C4D2R2_HEAD_RESPONSE_MISMATCH$",
    ):
        adapter(
            client
        ).list_completed_object_versions(
            _c4d2_scope(),
            observed_at=C4D2_AT,
        )


def test_c4d2r2_head_provider_failure_is_bounded_and_fails_closed() -> None:
    client = FakeS3Client()

    key = (
        _c4d2_tenant_prefix()
        + "m/opaque-matter/"
        "d/opaque-document/"
        "i/opaque-ingestion/content"
    )

    client.list_object_versions_response = {
        "Versions": [
            {
                "Key": key,
                "VersionId": "version-failure",
                "ETag": '"etag-failure"',
                "Size": 55,
                "LastModified": C4D2_AT,
            }
        ],
        "IsTruncated": False,
    }

    client.raise_on = "head_object"

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
        match="^L10A2R_C4D2R2_HEAD_OBJECT_FAILED$",
    ) as captured:
        adapter(
            client
        ).list_completed_object_versions(
            _c4d2_scope(),
            observed_at=C4D2_AT,
        )

    assert "sensitive-provider-message" not in str(
        captured.value
    )


def test_c4d2r2_empty_completed_listing_performs_no_head_calls() -> None:
    client = FakeS3Client()

    result = adapter(
        client
    ).list_completed_object_versions(
        _c4d2_scope(),
        observed_at=C4D2_AT,
    )

    assert result == ()
    assert [name for name, _ in client.calls] == [
        "list_object_versions",
    ]

# --- L10A2R-C4D2 S3 provider cleanup discovery certificate ---

from datetime import datetime, timezone
import hashlib

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceProviderCleanupDiscoveryPort,
    LegalEvidenceProviderDiscoveryScope,
)


C4D2_AT = datetime(
    2026,
    9,
    30,
    15,
    45,
    0,
    123456,
    tzinfo=timezone.utc,
)


def _c4d2_scope() -> LegalEvidenceProviderDiscoveryScope:
    return LegalEvidenceProviderDiscoveryScope(
        tenant_id="tenant-c4d2",
        tenant_scope_fingerprint=hashlib.sha3_512(
            b"tenant-c4d2"
        ).hexdigest(),
    )


def _c4d2_tenant_prefix() -> str:
    tenant_digest = hashlib.sha3_256(
        b"tenant-c4d2"
    ).hexdigest()

    return (
        "legal-evidence/v1/t/"
        f"{tenant_digest}/"
    )


def test_c4d2_adapter_implements_cleanup_discovery_port() -> None:
    client = FakeS3Client()
    adapter = LegalEvidenceS3StorageAdapter(
        LegalEvidenceS3Configuration(
            bucket="wilsy-c4d2-cert"
        ),
        client=cast(BaseClient, client),
    )

    assert isinstance(
        adapter,
        LegalEvidenceProviderCleanupDiscoveryPort,
    )


def test_c4d2_incomplete_session_discovery_uses_tenant_opaque_prefix_only() -> None:
    client = FakeS3Client()

    client.list_multipart_uploads_response = {
        "Uploads": [
            {
                "Key": (
                    _c4d2_tenant_prefix()
                    + "m/opaque-matter/"
                    "d/opaque-document/"
                    "i/opaque-ingestion/content"
                ),
                "UploadId": "upload-c4d2",
                "Initiated": C4D2_AT,
            }
        ],
        "IsTruncated": False,
    }

    adapter = LegalEvidenceS3StorageAdapter(
        LegalEvidenceS3Configuration(
            bucket="wilsy-c4d2-cert"
        ),
        client=cast(BaseClient, client),
    )

    result = adapter.list_incomplete_write_sessions(
        _c4d2_scope(),
        observed_at=C4D2_AT,
    )

    assert len(result) == 1
    assert result[0].tenant_id == "tenant-c4d2"
    assert result[0].provider_name == "aws_s3"
    assert result[0].write_session_reference == "upload-c4d2"
    assert result[0].observed_at == C4D2_AT

    calls = [
        call
        for call in client.calls
        if call[0] == "list_multipart_uploads"
    ]
    assert len(calls) == 1

    kwargs = calls[0][1]
    assert kwargs["Bucket"] == "wilsy-c4d2-cert"
    assert "Prefix" in kwargs

    prefix = kwargs["Prefix"]

    assert "tenant-c4d2" not in prefix
    assert prefix.startswith(
        "legal-evidence/v1/t/"
    )


def test_c4d2_completed_object_discovery_recovers_exact_version_intent_metadata() -> None:
    client = FakeS3Client()

    key = (
        _c4d2_tenant_prefix()
        + "m/opaque-matter/"
        "d/opaque-document/"
        "i/opaque-ingestion/content"
    )

    client.list_object_versions_response = {
        "Versions": [
            {
                "Key": key,
                "VersionId": "version-c4d2",
                "ETag": '"etag-c4d2"',
                "Size": 123,
                "LastModified": C4D2_AT,
                "IsLatest": True,
            }
        ],
        "IsTruncated": False,
    }

    fingerprint = "a" * 128

    client.head_response = {
        "VersionId": "version-c4d2",
        "ETag": '"etag-c4d2"',
        "ContentLength": 123,
        "Metadata": {
            "wilsy-intent-sha3-512": fingerprint,
        },
    }

    storage = LegalEvidenceS3StorageAdapter(
        LegalEvidenceS3Configuration(
            bucket="wilsy-c4d2-cert"
        ),
        client=cast(BaseClient, client),
    )

    result = storage.list_completed_object_versions(
        _c4d2_scope(),
        observed_at=C4D2_AT,
    )

    assert len(result) == 1
    observation = result[0]

    assert observation.tenant_id == "tenant-c4d2"
    assert observation.provider_name == "aws_s3"
    assert observation.object_version_reference == "version-c4d2"
    assert observation.content_length == 123
    assert (
        observation.write_intent_metadata_state
        is LegalEvidenceCompletedObjectIntentMetadataState.PRESENT
    )
    assert observation.write_intent_fingerprint == fingerprint

    assert [name for name, _ in client.calls] == [
        "list_object_versions",
        "head_object",
    ]

    _, head_kwargs = client.calls[1]
    assert head_kwargs == {
        "Bucket": "wilsy-c4d2-cert",
        "Key": key,
        "VersionId": "version-c4d2",
    }


def test_c4d2_discovery_surface_performs_no_abort_or_delete() -> None:
    client = FakeS3Client()

    client.list_multipart_uploads_response = {
        "Uploads": [],
        "IsTruncated": False,
    }
    client.list_object_versions_response = {
        "Versions": [],
        "IsTruncated": False,
    }

    adapter = LegalEvidenceS3StorageAdapter(
        LegalEvidenceS3Configuration(
            bucket="wilsy-c4d2-cert"
        ),
        client=cast(BaseClient, client),
    )

    scope = _c4d2_scope()

    assert (
        adapter.list_incomplete_write_sessions(
            scope,
            observed_at=C4D2_AT,
        )
        == ()
    )

    assert (
        adapter.list_completed_object_versions(
            scope,
            observed_at=C4D2_AT,
        )
        == ()
    )

    names = {
        name
        for name, _ in client.calls
    }

    assert "abort_multipart_upload" not in names
    assert "delete_object" not in names
    assert "delete_objects" not in names


def test_c4d2_provider_pagination_is_required_not_silently_truncated() -> None:
    client = FakeS3Client()

    client.list_multipart_uploads_response = {
        "Uploads": [],
        "IsTruncated": True,
    }

    adapter = LegalEvidenceS3StorageAdapter(
        LegalEvidenceS3Configuration(
            bucket="wilsy-c4d2-cert"
        ),
        client=cast(BaseClient, client),
    )

    with pytest.raises(
        LegalEvidenceS3StorageAdapterError,
    ):
        adapter.list_incomplete_write_sessions(
            _c4d2_scope(),
            observed_at=C4D2_AT,
        )
