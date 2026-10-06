"""WILSY OS HR Document HTTP Direct Behavior Certificate.

TITLE: HR Document HTTP Direct Behavior and Composition Certificate
VERSION: v1.0.0-P0-C12F7C-B-R2-HR-DOCUMENT-HTTP-BEHAVIOR-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify behavior not proven by structural inspection:
bounded async-to-sync ingress, fail-closed runtime configuration,
201/202 distinction, mixed-sensitivity filtering, unavailable-authority
propagation, and persisted-only provider coordinates.

No real Mongo or AWS operation is performed by this certificate.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request

import tools.eos.api.hr_document_router as subject
from tools.eos.api.exceptions import (
    ForbiddenOperationException,
)
from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
    HrDocumentSensitivity,
)
from tools.eos.saas.hr.hr_document_service import (
    HrDocumentIngestionStatus,
)


VERSION = (
    "v1.0.0-P0-C12F7C-B-R2-"
    "HR-DOCUMENT-HTTP-BEHAVIOR-CERT"
)


def _identity() -> Any:
    return SimpleNamespace(
        identity_id="principal-http-cert"
    )


def _fake_document(
    *,
    sensitivity: HrDocumentSensitivity,
    suffix: str,
) -> Any:
    return SimpleNamespace(
        tenant_id="tenant-http-cert",
        employee_id="employee-http-cert",
        document_id="document-" + suffix,
        document_version_id="version-" + suffix,
        document_class=next(
            iter(
                HrDocumentClass
            )
        ),
        sensitivity=sensitivity,
        original_filename="file-" + suffix + ".pdf",
        media_type="application/pdf",
        byte_length=7,
        content_digest_sha3_512=("a" * 128),
        storage_provider_id="aws_s3",
        storage_object_reference="opaque-storage-" + suffix,
        object_version_reference="opaque-version-" + suffix,
        provider_integrity_reference="provider-proof-" + suffix,
        created_at=datetime(
            2026,
            10,
            5,
            tzinfo=timezone.utc,
        ),
        created_by_principal_id="principal-http-cert",
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        fingerprint=("b" * 128),
    )


def _request(
    *,
    body: bytes = b"payload",
    extra_headers: dict[str, str] | None = None,
) -> Request:
    headers = {
        "x-tenant-id": "tenant-http-cert",
        "x-hr-document-id": "document-http-cert",
        "x-hr-document-version-id": "version-http-cert",
        "x-hr-ingestion-reference": "ingestion-http-cert",
        "x-hr-document-class": next(
            iter(
                HrDocumentClass
            )
        ).value,
        "x-hr-original-filename": "cert.pdf",
        "content-type": "application/pdf",
        "content-length": str(
            len(
                body
            )
        ),
    }

    if extra_headers is not None:
        headers.update(
            extra_headers
        )

    encoded = [
        (
            key.encode(
                "latin-1"
            ),
            value.encode(
                "latin-1"
            ),
        )
        for key, value in headers.items()
    ]

    sent = False

    async def receive() -> dict[str, Any]:
        nonlocal sent

        if sent:
            return {
                "type": "http.request",
                "body": b"",
                "more_body": False,
            }

        sent = True

        return {
            "type": "http.request",
            "body": body,
            "more_body": False,
        }

    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/",
            "headers": encoded,
            "query_string": b"",
            "server": (
                "testserver",
                80,
            ),
            "client": (
                "127.0.0.1",
                1234,
            ),
            "scheme": "http",
            "http_version": "1.1",
        },
        receive,
    )


def test_missing_upload_ceiling_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "WILSY_HR_DOCUMENT_MAX_UPLOAD_BYTES",
        raising=False,
    )

    with pytest.raises(
        HTTPException,
    ) as captured:
        subject._upload_maximum()

    assert captured.value.status_code == 503


def test_invalid_upload_ceiling_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "WILSY_HR_DOCUMENT_MAX_UPLOAD_BYTES",
        "not-an-integer",
    )

    with pytest.raises(
        HTTPException,
    ) as captured:
        subject._upload_maximum()

    assert captured.value.status_code == 503


def test_missing_s3_bucket_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "WILSY_HR_DOCUMENT_S3_BUCKET",
        raising=False,
    )

    with pytest.raises(
        HTTPException,
    ) as captured:
        subject._s3_configuration()

    assert captured.value.status_code == 503


@pytest.mark.anyio
async def test_bounded_queue_bridge_streams_to_one_f6f_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    consumed: list[bytes] = []
    calls = 0

    def fake_orchestrate(
        **kwargs: Any,
    ) -> object:
        nonlocal calls

        calls += 1

        for chunk in kwargs["chunks"]:
            consumed.append(
                chunk
            )

        return object()

    monkeypatch.setattr(
        subject,
        "UPLOAD_PROVIDER_CHUNK_BYTES",
        4,
    )

    monkeypatch.setattr(
        subject,
        "orchestrate_hr_document_ingestion",
        fake_orchestrate,
    )

    monkeypatch.setattr(
        subject,
        "_runtime_database",
        lambda: (
            object(),
            object(),
            object(),
        ),
    )

    monkeypatch.setattr(
        subject,
        "get_employee_registry",
        lambda: object(),
    )

    request = _request(
        body=b"abcdefghijkl",
    )

    intent = SimpleNamespace(
        admitted_max_content_length=64,
    )

    result = await subject._run_ingestion(
        request=request,
        intent=cast(
            Any,
            intent,
        ),
        document_class=next(
            iter(
                HrDocumentClass
            )
        ),
        identity=_identity(),
        storage=cast(
            Any,
            object(),
        ),
        content_length=12,
    )

    assert result is not None
    assert calls == 1
    assert consumed == [
        b"abcd",
        b"efgh",
        b"ijkl",
    ]


@pytest.mark.anyio
async def test_ingress_declared_length_mismatch_fails_422(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_orchestrate(
        **kwargs: Any,
    ) -> object:
        tuple(
            kwargs["chunks"]
        )
        return object()

    monkeypatch.setattr(
        subject,
        "orchestrate_hr_document_ingestion",
        fake_orchestrate,
    )

    monkeypatch.setattr(
        subject,
        "_runtime_database",
        lambda: (
            object(),
            object(),
            object(),
        ),
    )

    monkeypatch.setattr(
        subject,
        "get_employee_registry",
        lambda: object(),
    )

    request = _request(
        body=b"short",
    )

    intent = SimpleNamespace(
        admitted_max_content_length=64,
    )

    with pytest.raises(
        HTTPException,
    ) as captured:
        await subject._run_ingestion(
            request=request,
            intent=cast(
                Any,
                intent,
            ),
            document_class=next(
                iter(
                    HrDocumentClass
                )
            ),
            identity=_identity(),
            storage=cast(
                Any,
                object(),
            ),
            content_length=6,
        )

    assert captured.value.status_code == 422


@pytest.mark.anyio
async def test_mixed_sensitivity_projection_omits_denied_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sensitivities = list(
        HrDocumentSensitivity
    )

    assert len(
        sensitivities
    ) >= 2

    allowed = sensitivities[0]
    denied = sensitivities[1]

    async def fake_authorize(
        **kwargs: Any,
    ) -> object:
        if kwargs["sensitivity"] is denied:
            raise ForbiddenOperationException(
                "denied"
            )

        return object()

    monkeypatch.setattr(
        subject,
        "_authorize",
        fake_authorize,
    )

    projected = await subject._authorized_projection(
        identity=_identity(),
        tenant_id="tenant-http-cert",
        documents=cast(
            Any,
            (
                _fake_document(
                    sensitivity=allowed,
                    suffix="allowed",
                ),
                _fake_document(
                    sensitivity=denied,
                    suffix="denied",
                ),
            ),
        ),
    )

    assert len(
        projected
    ) == 1

    assert projected[0][
        "document_id"
    ] == "document-allowed"


@pytest.mark.anyio
async def test_projection_authority_unavailable_fails_entire_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sensitivity = next(
        iter(
            HrDocumentSensitivity
        )
    )

    async def unavailable(
        **kwargs: Any,
    ) -> object:
        del kwargs

        raise HTTPException(
            status_code=503,
            detail="authority unavailable",
        )

    monkeypatch.setattr(
        subject,
        "_authorize",
        unavailable,
    )

    document = _fake_document(
        sensitivity=sensitivity,
        suffix="unavailable",
    )

    with pytest.raises(
        HTTPException,
    ) as captured:
        await subject._authorized_projection(
            identity=_identity(),
            tenant_id="tenant-http-cert",
            documents=cast(
                Any,
                (
                    document,
                ),
            ),
        )

    assert captured.value.status_code == 503


@pytest.mark.anyio
async def test_upload_committed_maps_to_201(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document_class = next(
        iter(
            HrDocumentClass
        )
    )

    document = _fake_document(
        sensitivity=next(
            iter(
                HrDocumentSensitivity
            )
        ),
        suffix="committed",
    )

    async def authorize(
        **kwargs: Any,
    ) -> object:
        del kwargs
        return object()

    async def ingestion(
        **kwargs: Any,
    ) -> object:
        del kwargs

        return SimpleNamespace(
            status=HrDocumentIngestionStatus.COMMITTED,
            document=document,
        )

    monkeypatch.setenv(
        "WILSY_HR_DOCUMENT_MAX_UPLOAD_BYTES",
        "1024",
    )

    monkeypatch.setattr(
        subject,
        "_authorize",
        authorize,
    )

    monkeypatch.setattr(
        subject,
        "_s3_configuration",
        lambda: cast(
            Any,
            object(),
        ),
    )

    monkeypatch.setattr(
        subject,
        "HrDocumentS3StorageAdapter",
        lambda config: cast(
            Any,
            object(),
        ),
    )

    monkeypatch.setattr(
        subject,
        "_run_ingestion",
        ingestion,
    )

    response = await subject.upload_hr_document(
        employee_id="employee-http-cert",
        request=_request(
            extra_headers={
                "x-hr-document-class":
                    document_class.value,
            },
        ),
        identity=_identity(),
        tenant_id="tenant-http-cert",
    )

    assert isinstance(
        response,
        JSONResponse,
    )

    assert response.status_code == 201


@pytest.mark.anyio
async def test_upload_reconciliation_required_maps_to_202(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document_class = next(
        iter(
            HrDocumentClass
        )
    )

    document = _fake_document(
        sensitivity=next(
            iter(
                HrDocumentSensitivity
            )
        ),
        suffix="reconciliation",
    )

    async def authorize(
        **kwargs: Any,
    ) -> object:
        del kwargs
        return object()

    async def ingestion(
        **kwargs: Any,
    ) -> object:
        del kwargs

        return SimpleNamespace(
            status=(
                HrDocumentIngestionStatus
                .RECONCILIATION_REQUIRED
            ),
            document=document,
        )

    monkeypatch.setenv(
        "WILSY_HR_DOCUMENT_MAX_UPLOAD_BYTES",
        "1024",
    )

    monkeypatch.setattr(
        subject,
        "_authorize",
        authorize,
    )

    monkeypatch.setattr(
        subject,
        "_s3_configuration",
        lambda: cast(
            Any,
            object(),
        ),
    )

    monkeypatch.setattr(
        subject,
        "HrDocumentS3StorageAdapter",
        lambda config: cast(
            Any,
            object(),
        ),
    )

    monkeypatch.setattr(
        subject,
        "_run_ingestion",
        ingestion,
    )

    response = await subject.upload_hr_document(
        employee_id="employee-http-cert",
        request=_request(
            extra_headers={
                "x-hr-document-class":
                    document_class.value,
            },
        ),
        identity=_identity(),
        tenant_id="tenant-http-cert",
    )

    assert isinstance(
        response,
        JSONResponse,
    )

    assert response.status_code == 202


def test_download_read_intent_uses_persisted_coordinates_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeIntent:
        def __init__(
            self,
            **kwargs: Any,
        ) -> None:
            captured.update(
                kwargs
            )

            self.expected_byte_length = int(
                kwargs[
                    "expected_byte_length"
                ]
            )

            self.expected_sha3_512 = str(
                kwargs[
                    "expected_sha3_512"
                ]
            )

    class FakeChunk:
        def __init__(
            self,
            data: bytes,
        ) -> None:
            self.data = data
            self.byte_length = len(
                data
            )

    class FakeAdapter:
        def __init__(
            self,
            config: object,
        ) -> None:
            del config

        def begin(
            self,
            intent: object,
        ) -> object:
            del intent
            return object()

        def read_chunk(
            self,
            intent: object,
            session: object,
            *,
            sequence: int,
            max_bytes: int,
        ) -> FakeChunk:
            del intent
            del session
            del sequence
            del max_bytes

            return FakeChunk(
                b"payload"
            )

        def complete(
            self,
            intent: object,
            session: object,
            chunks: tuple[
                FakeChunk,
                ...,
            ],
        ) -> object:
            del intent
            del session
            del chunks
            return object()

        def abort(
            self,
            intent: object,
            session: object,
        ) -> None:
            del intent
            del session

    monkeypatch.setattr(
        subject,
        "HrDocumentBinaryReadIntent",
        FakeIntent,
    )

    monkeypatch.setattr(
        subject,
        "HrDocumentS3ReadStorageAdapter",
        FakeAdapter,
    )

    monkeypatch.setattr(
        subject,
        "validate_read_result_for_intent",
        lambda *args, **kwargs: None,
    )

    document = _fake_document(
        sensitivity=next(
            iter(
                HrDocumentSensitivity
            )
        ),
        suffix="download",
    )

    data = subject._read_document_bytes(
        document,
        cast(
            Any,
            object(),
        ),
    )

    assert data == b"payload"

    assert captured[
        "tenant_id"
    ] == document.tenant_id

    assert captured[
        "employee_id"
    ] == document.employee_id

    assert captured[
        "document_id"
    ] == document.document_id

    assert captured[
        "document_version_id"
    ] == document.document_version_id

    assert captured[
        "storage_provider_id"
    ] == document.storage_provider_id

    assert captured[
        "storage_object_reference"
    ] == document.storage_object_reference

    assert captured[
        "object_version_reference"
    ] == document.object_version_reference

    assert captured[
        "expected_byte_length"
    ] == document.byte_length

    assert captured[
        "expected_sha3_512"
    ] == document.content_digest_sha3_512


# ARTIFACT: tests/unit/test_hr_document_http_behavior.py
# VERSION: v1.0.0-P0-C12F7C-B-R2-HR-DOCUMENT-HTTP-BEHAVIOR-CERT
# REAL AWS: none
# REAL MONGO: none
# PROVIDER DELETE AUTHORITY: none
# PAYMENT / SETTLEMENT / FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
