"""WILSY OS HR Document HTTP Boundary.

TITLE: HR Document HTTP Router
VERSION: v1.0.0-P0-C12F7C-HR-DOCUMENT-HTTP
AUTHORITY: Python EOS HTTP admission and projection only.

PURPOSE:
Expose four canonical tenant-scoped HR document operations while composing the
already-certified F3 domain, F4 registry, F5 read/write provider adapters, F6F
ingestion orchestration and F7B tenant authorization.

UPLOAD:
The request body is consumed with Request.stream() and passed through a
bounded queue to one synchronous F6F worker. The complete upload is never
materialized as one body buffer.

READ:
Persisted HrDocument metadata determines sensitivity, provider coordinates,
expected length and expected SHA3-512. Caller input never supplies those
authority-bearing persisted coordinates.

LIST / HISTORY:
Each persisted row is evaluated against its own sensitivity-specific read
operation. A denied row is omitted without disclosure. Unavailable authority
fails the request closed.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/hr_document_router.py

CERTIFICATION / UPDATE DATE: 2026-10-05
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import os
import queue
import threading
from typing import Any, Final

from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Request,
)
from fastapi.responses import (
    JSONResponse,
    Response,
)

from tools.eos.api.exceptions import (
    ForbiddenOperationException,
)
from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
    get_role_assignment_repository,
)
from tools.eos.auth.authentication import (
    get_current_identity,
    get_principal_authority_repository,
)
from tools.eos.auth.identity import (
    SovereignIdentity,
)
from tools.eos.auth.tenant_access import (
    get_tenant_membership_repository,
)
from tools.eos.auth.tenant_authority_policy import (
    permission_for_business_role_operation,
)
from tools.eos.kernel.db import (
    get_client,
    get_database,
)
from tools.eos.saas.domain.hr_document import (
    HrDocument,
    HrDocumentClass,
    HrDocumentSensitivity,
    sensitivity_for_document_class,
)
from tools.eos.saas.employee.employee_registry import (
    get_employee_registry,
)
from tools.eos.saas.hr.hr_document_commit_uncertainty_registry import (
    COLLECTION as HR_DOCUMENT_UNCERTAINTY_COLLECTION,
)
from tools.eos.saas.hr.hr_document_read_storage import (
    MAX_READ_CHUNK_BYTES,
    HrDocumentBinaryReadIntent,
    validate_read_result_for_intent,
)
from tools.eos.saas.hr.hr_document_registry import (
    COLLECTION as HR_DOCUMENT_COLLECTION,
    HrDocumentRegistryError,
    HrDocumentRegistryNotFoundError,
    get_document_version,
    list_document_versions,
    list_employee_documents,
)
from tools.eos.saas.hr.hr_document_s3_storage_adapter import (
    DEFAULT_REGION,
    HrDocumentS3Configuration,
    HrDocumentS3ReadStorageAdapter,
    HrDocumentS3StorageAdapter,
    HrDocumentS3StorageAdapterError,
)
from tools.eos.saas.hr.hr_document_service import (
    HrDocumentIngestionStatus,
    HrDocumentServiceError,
    HrDocumentServiceInputError,
    HrDocumentServiceScopeError,
    orchestrate_hr_document_ingestion,
)
from tools.eos.saas.hr.hr_document_storage import (
    MAX_STREAM_CHUNK_BYTES,
    HrDocumentBinaryWriteIntent,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F7C-"
    "HR-DOCUMENT-HTTP"
)

ROUTER_PREFIX: Final[str] = (
    "/api/hr/documents"
)

UPLOAD_QUEUE_CAPACITY: Final[int] = 2

# Provider-facing parts remain below F2's certified 16 MiB ceiling and above
# the multipart provider's non-final small-part threshold.
UPLOAD_PROVIDER_CHUNK_BYTES: Final[int] = (
    8 * 1024 * 1024
)

if (
    UPLOAD_PROVIDER_CHUNK_BYTES
    > MAX_STREAM_CHUNK_BYTES
):
    raise RuntimeError(
        "P0_C12F7C_PROVIDER_CHUNK_CONFIGURATION_INVALID"
    )


router = APIRouter(
    prefix=ROUTER_PREFIX,
    tags=["hr-documents"],
)


class _IngressAbort(
    RuntimeError
):
    pass


_STOP: Final[object] = object()


def _unprocessable(
    detail: str,
) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail=detail,
    )


def _unavailable(
    detail: str,
) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail=detail,
    )


def _required_header(
    request: Request,
    name: str,
) -> str:
    value = request.headers.get(
        name
    )

    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
    ):
        raise _unprocessable(
            "Required HR document metadata is invalid."
        )

    return value


def _positive_content_length(
    request: Request,
    maximum: int,
) -> int:
    raw = request.headers.get(
        "content-length"
    )

    try:
        value = int(
            raw
            if raw is not None
            else ""
        )
    except ValueError:
        raise _unprocessable(
            "Content-Length is required."
        ) from None

    if (
        value <= 0
        or value > maximum
    ):
        raise _unprocessable(
            "Document content length is outside the admitted bound."
        )

    return value


def _upload_maximum() -> int:
    raw = os.getenv(
        "WILSY_HR_DOCUMENT_MAX_UPLOAD_BYTES"
    )

    if (
        not isinstance(
            raw,
            str,
        )
        or not raw
        or raw != raw.strip()
        or not raw.isdecimal()
    ):
        raise _unavailable(
            "HR document upload policy is unavailable."
        )

    value = int(
        raw
    )

    if value <= 0:
        raise _unavailable(
            "HR document upload policy is unavailable."
        )

    return value


def _s3_configuration() -> HrDocumentS3Configuration:
    bucket = os.getenv(
        "WILSY_HR_DOCUMENT_S3_BUCKET"
    )

    if (
        not isinstance(
            bucket,
            str,
        )
        or not bucket
        or bucket != bucket.strip()
    ):
        raise _unavailable(
            "HR document storage configuration is unavailable."
        )

    region_raw = os.getenv(
        "WILSY_HR_DOCUMENT_S3_REGION"
    )

    region = (
        DEFAULT_REGION
        if not isinstance(
            region_raw,
            str,
        )
        or not region_raw.strip()
        else region_raw.strip()
    )

    kms_raw = os.getenv(
        "WILSY_HR_DOCUMENT_S3_KMS_KEY_ID"
    )

    kms = (
        None
        if not isinstance(
            kms_raw,
            str,
        )
        or not kms_raw.strip()
        else kms_raw.strip()
    )

    try:
        return HrDocumentS3Configuration(
            bucket=bucket,
            region=region,
            kms_key_id=kms,
        )
    except HrDocumentS3StorageAdapterError as error:
        raise _unavailable(
            "HR document storage configuration is unavailable."
        ) from error


def _iam_coordinates(
    sensitivity: HrDocumentSensitivity,
    access: str,
) -> tuple[str, str]:
    if access not in {
        "read",
        "write",
    }:
        raise _unavailable(
            "HR document authorization policy is unavailable."
        )

    token = sensitivity.value.casefold()

    operation = (
        "hr_document_"
        + token
        + "_"
        + access
    )

    permission = (
        permission_for_business_role_operation(
            operation
        )
    )

    if (
        not isinstance(
            permission,
            str,
        )
        or not permission
    ):
        raise _unavailable(
            "HR document authorization policy is unavailable."
        )

    return (
        operation,
        permission,
    )


async def _authorize(
    *,
    identity: SovereignIdentity,
    tenant_id: str,
    sensitivity: HrDocumentSensitivity,
    access: str,
) -> TenantAuthorizationContext:
    operation, permission = (
        _iam_coordinates(
            sensitivity,
            access,
        )
    )

    dependency = RequireTenantAuthorization(
        permission,
        operation,
    )

    return await dependency(
        identity=identity,
        tenant_id=tenant_id,
        principal_repository=(
            get_principal_authority_repository()
        ),
        membership_repository=(
            get_tenant_membership_repository()
        ),
        role_assignment_repository=(
            get_role_assignment_repository()
        ),
    )


def _runtime_database() -> tuple[
    Any,
    Any,
    Any,
]:
    client = get_client()
    database = get_database()

    if (
        client is None
        or database is None
    ):
        raise _unavailable(
            "HR document persistence is unavailable."
        )

    return (
        client,
        database[
            HR_DOCUMENT_COLLECTION
        ],
        database[
            HR_DOCUMENT_UNCERTAINTY_COLLECTION
        ],
    )


def _public_metadata(
    document: HrDocument,
) -> dict[str, object]:
    return {
        "tenant_id":
            document.tenant_id,
        "employee_id":
            document.employee_id,
        "document_id":
            document.document_id,
        "document_version_id":
            document.document_version_id,
        "document_class":
            document.document_class.value,
        "sensitivity":
            document.sensitivity.value,
        "original_filename":
            document.original_filename,
        "media_type":
            document.media_type,
        "byte_length":
            document.byte_length,
        "content_digest_sha3_512":
            document.content_digest_sha3_512,
        "created_at":
            document.created_at.isoformat(),
        "created_by_principal_id":
            document.created_by_principal_id,
        "retention_until":
            (
                document.retention_until.isoformat()
                if document.retention_until is not None
                else None
            ),
        "legal_hold":
            document.legal_hold,
        "supersedes_version_id":
            document.supersedes_version_id,
        "fingerprint":
            document.fingerprint,
    }


def _load_employee_documents(
    *,
    tenant_id: str,
    employee_id: str,
) -> tuple[
    HrDocument,
    ...,
]:
    client, collection, _ = (
        _runtime_database()
    )

    try:
        with client.start_session() as session:
            with session.start_transaction():
                return list_employee_documents(
                    tenant_id,
                    employee_id,
                    collection,
                    session=session,
                )
    except HrDocumentRegistryError as error:
        raise _unavailable(
            "HR document metadata is unavailable."
        ) from error
    except Exception as error:
        raise _unavailable(
            "HR document metadata is unavailable."
        ) from error


def _load_document_history(
    *,
    tenant_id: str,
    employee_id: str,
    document_id: str,
) -> tuple[
    HrDocument,
    ...,
]:
    client, collection, _ = (
        _runtime_database()
    )

    try:
        with client.start_session() as session:
            with session.start_transaction():
                return list_document_versions(
                    tenant_id,
                    employee_id,
                    document_id,
                    collection,
                    session=session,
                )
    except HrDocumentRegistryError as error:
        raise _unavailable(
            "HR document metadata is unavailable."
        ) from error
    except Exception as error:
        raise _unavailable(
            "HR document metadata is unavailable."
        ) from error


def _load_exact_document(
    *,
    tenant_id: str,
    employee_id: str,
    document_version_id: str,
) -> HrDocument:
    client, collection, _ = (
        _runtime_database()
    )

    try:
        with client.start_session() as session:
            with session.start_transaction():
                document = get_document_version(
                    tenant_id,
                    document_version_id,
                    collection,
                    session=session,
                )
    except HrDocumentRegistryNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail="HR document not found.",
        ) from error
    except HrDocumentRegistryError as error:
        raise _unavailable(
            "HR document metadata is unavailable."
        ) from error
    except Exception as error:
        raise _unavailable(
            "HR document metadata is unavailable."
        ) from error

    if document.employee_id != employee_id:
        raise HTTPException(
            status_code=404,
            detail="HR document not found.",
        )

    return document


async def _authorized_projection(
    *,
    identity: SovereignIdentity,
    tenant_id: str,
    documents: tuple[
        HrDocument,
        ...,
    ],
) -> list[
    dict[str, object]
]:
    decisions: dict[
        HrDocumentSensitivity,
        bool,
    ] = {}

    projected: list[
        dict[str, object]
    ] = []

    for document in documents:
        sensitivity = document.sensitivity

        if sensitivity not in decisions:
            try:
                await _authorize(
                    identity=identity,
                    tenant_id=tenant_id,
                    sensitivity=sensitivity,
                    access="read",
                )
                decisions[
                    sensitivity
                ] = True

            except ForbiddenOperationException:
                decisions[
                    sensitivity
                ] = False

        if decisions[
            sensitivity
        ]:
            projected.append(
                _public_metadata(
                    document
                )
            )

    return projected


def _map_ingestion_error(
    error: BaseException,
) -> HTTPException:
    if isinstance(
        error,
        HrDocumentServiceInputError,
    ):
        return _unprocessable(
            "HR document ingestion input is invalid."
        )

    if isinstance(
        error,
        HrDocumentServiceScopeError,
    ):
        return HTTPException(
            status_code=404,
            detail="Employee scope was not found.",
        )

    if isinstance(
        error,
        HrDocumentServiceError,
    ):
        return _unavailable(
            "HR document ingestion is unavailable."
        )

    return _unavailable(
        "HR document ingestion is unavailable."
    )


async def _run_ingestion(
    *,
    request: Request,
    intent: HrDocumentBinaryWriteIntent,
    document_class: HrDocumentClass,
    identity: SovereignIdentity,
    storage: HrDocumentS3StorageAdapter,
    content_length: int,
) -> Any:
    client, document_collection, uncertainty_collection = (
        _runtime_database()
    )

    q: queue.Queue[
        object
    ] = queue.Queue(
        maxsize=UPLOAD_QUEUE_CAPACITY
    )

    done = threading.Event()

    result_box: dict[
        str,
        Any,
    ] = {}

    errors: list[
        BaseException
    ] = []

    def source() -> Any:
        while True:
            item = q.get()

            if item is _STOP:
                return

            if isinstance(
                item,
                BaseException,
            ):
                raise item

            if not isinstance(
                item,
                bytes,
            ):
                raise _IngressAbort(
                    "P0_C12F7C_INGRESS_CHUNK_INVALID"
                )

            yield item

    def worker() -> None:
        try:
            result_box[
                "result"
            ] = (
                orchestrate_hr_document_ingestion(
                    intent=intent,
                    chunks=source(),
                    document_class=document_class,
                    created_at=datetime.now(
                        timezone.utc
                    ),
                    created_by_principal_id=(
                        identity.identity_id
                    ),
                    retention_until=None,
                    legal_hold=False,
                    supersedes_version_id=None,
                    storage=storage,
                    employee_registry=(
                        get_employee_registry()
                    ),
                    mongo_client=client,
                    document_collection=(
                        document_collection
                    ),
                    uncertainty_collection=(
                        uncertainty_collection
                    ),
                )
            )
        except BaseException as error:
            errors.append(
                error
            )
        finally:
            done.set()

    thread = threading.Thread(
        target=worker,
        name="wilsy-hr-document-f6f",
        daemon=True,
    )

    thread.start()

    def put_item(
        item: object,
    ) -> None:
        while True:
            if done.is_set():
                if errors:
                    raise errors[
                        0
                    ]

                raise RuntimeError(
                    "P0_C12F7C_F6F_WORKER_STOPPED"
                )

            try:
                q.put(
                    item,
                    timeout=0.1,
                )
                return
            except queue.Full:
                continue

    observed = 0
    buffer = bytearray()
    producer_error: HTTPException | None = None

    try:
        async for incoming in request.stream():
            if not incoming:
                continue

            observed += len(
                incoming
            )

            if (
                observed > content_length
                or observed
                > intent.admitted_max_content_length
            ):
                raise _unprocessable(
                    "Document content length does not match admission."
                )

            buffer.extend(
                incoming
            )

            while (
                len(
                    buffer
                )
                >= UPLOAD_PROVIDER_CHUNK_BYTES
            ):
                chunk = bytes(
                    buffer[
                        :UPLOAD_PROVIDER_CHUNK_BYTES
                    ]
                )

                del buffer[
                    :UPLOAD_PROVIDER_CHUNK_BYTES
                ]

                await asyncio.to_thread(
                    put_item,
                    chunk,
                )

        if observed != content_length:
            raise _unprocessable(
                "Document content length does not match admission."
            )

        if buffer:
            await asyncio.to_thread(
                put_item,
                bytes(
                    buffer
                ),
            )

        await asyncio.to_thread(
            put_item,
            _STOP,
        )

    except HTTPException as error:
        producer_error = error

        try:
            await asyncio.to_thread(
                put_item,
                _IngressAbort(
                    "P0_C12F7C_INGRESS_ABORTED"
                ),
            )
        except BaseException:
            pass

    except BaseException as error:
        producer_error = _unavailable(
            "HR document ingress is unavailable."
        )

        try:
            await asyncio.to_thread(
                put_item,
                _IngressAbort(
                    "P0_C12F7C_INGRESS_ABORTED"
                ),
            )
        except BaseException:
            pass

    await asyncio.to_thread(
        thread.join
    )

    if producer_error is not None:
        raise producer_error

    if errors:
        raise _map_ingestion_error(
            errors[
                0
            ]
        )

    result = result_box.get(
        "result"
    )

    if result is None:
        raise _unavailable(
            "HR document ingestion did not produce a result."
        )

    return result


def _read_document_bytes(
    document: HrDocument,
    config: HrDocumentS3Configuration,
) -> bytes:
    adapter = (
        HrDocumentS3ReadStorageAdapter(
            config
        )
    )

    intent = HrDocumentBinaryReadIntent(
        tenant_id=document.tenant_id,
        employee_id=document.employee_id,
        document_id=document.document_id,
        document_version_id=(
            document.document_version_id
        ),
        storage_provider_id=(
            document.storage_provider_id
        ),
        storage_object_reference=(
            document.storage_object_reference
        ),
        object_version_reference=(
            document.object_version_reference
        ),
        expected_byte_length=(
            document.byte_length
        ),
        expected_sha3_512=(
            document.content_digest_sha3_512
        ),
    )

    session = None

    try:
        session = adapter.begin(
            intent
        )

        chunks = []

        remaining = (
            intent.expected_byte_length
        )

        sequence = 0

        while remaining > 0:
            chunk = adapter.read_chunk(
                intent,
                session,
                sequence=sequence,
                max_bytes=min(
                    MAX_READ_CHUNK_BYTES,
                    remaining,
                ),
            )

            chunks.append(
                chunk
            )

            remaining -= (
                chunk.byte_length
            )

            sequence += 1

        frozen_chunks = tuple(
            chunks
        )

        result = adapter.complete(
            intent,
            session,
            frozen_chunks,
        )

        validate_read_result_for_intent(
            intent,
            result,
            frozen_chunks,
        )

        return b"".join(
            chunk.data
            for chunk in frozen_chunks
        )

    except Exception:
        if session is not None:
            try:
                adapter.abort(
                    intent,
                    session,
                )
            except Exception:
                pass

        raise


@router.post(
    "/employees/{employee_id}",
    status_code=201,
)
async def upload_hr_document(
    employee_id: str,
    request: Request,
    identity: SovereignIdentity = Depends(
        get_current_identity
    ),
    tenant_id: str | None = Header(
        default=None,
        alias="X-Tenant-ID",
    ),
) -> Response:
    if (
        not isinstance(
            tenant_id,
            str,
        )
        or not tenant_id
        or tenant_id != tenant_id.strip()
    ):
        raise HTTPException(
            status_code=403,
            detail="Tenant scope is required.",
        )

    document_id = _required_header(
        request,
        "x-hr-document-id",
    )

    document_version_id = (
        _required_header(
            request,
            "x-hr-document-version-id",
        )
    )

    ingestion_reference = (
        _required_header(
            request,
            "x-hr-ingestion-reference",
        )
    )

    class_raw = _required_header(
        request,
        "x-hr-document-class",
    )

    original_filename = (
        _required_header(
            request,
            "x-hr-original-filename",
        )
    )

    media_type = _required_header(
        request,
        "content-type",
    )

    try:
        document_class = (
            HrDocumentClass(
                class_raw
            )
        )
    except ValueError:
        raise _unprocessable(
            "HR document class is invalid."
        ) from None

    sensitivity = (
        sensitivity_for_document_class(
            document_class
        )
    )

    await _authorize(
        identity=identity,
        tenant_id=tenant_id,
        sensitivity=sensitivity,
        access="write",
    )

    maximum = _upload_maximum()

    content_length = (
        _positive_content_length(
            request,
            maximum,
        )
    )

    config = _s3_configuration()

    try:
        intent = HrDocumentBinaryWriteIntent(
            tenant_id=tenant_id,
            employee_id=employee_id,
            document_id=document_id,
            document_version_id=(
                document_version_id
            ),
            ingestion_reference=(
                ingestion_reference
            ),
            media_type=media_type,
            original_filename=(
                original_filename
            ),
            admitted_max_content_length=(
                maximum
            ),
        )

        storage = HrDocumentS3StorageAdapter(
            config
        )

    except Exception as error:
        raise _unprocessable(
            "HR document ingestion metadata is invalid."
        ) from error

    result = await _run_ingestion(
        request=request,
        intent=intent,
        document_class=document_class,
        identity=identity,
        storage=storage,
        content_length=content_length,
    )

    payload = {
        "status":
            result.status.value,
        "document":
            _public_metadata(
                result.document
            ),
    }

    if (
        result.status
        is HrDocumentIngestionStatus
        .RECONCILIATION_REQUIRED
    ):
        return JSONResponse(
            status_code=202,
            content=payload,
        )

    if (
        result.status
        is not HrDocumentIngestionStatus
        .COMMITTED
    ):
        raise _unavailable(
            "HR document ingestion status is unavailable."
        )

    return JSONResponse(
        status_code=201,
        content=payload,
    )


@router.get(
    "/employees/{employee_id}",
)
async def list_hr_documents(
    employee_id: str,
    identity: SovereignIdentity = Depends(
        get_current_identity
    ),
    tenant_id: str | None = Header(
        default=None,
        alias="X-Tenant-ID",
    ),
) -> list[
    dict[str, object]
]:
    if (
        not isinstance(
            tenant_id,
            str,
        )
        or not tenant_id
        or tenant_id != tenant_id.strip()
    ):
        raise HTTPException(
            status_code=403,
            detail="Tenant scope is required.",
        )

    documents = await asyncio.to_thread(
        _load_employee_documents,
        tenant_id=tenant_id,
        employee_id=employee_id,
    )

    return await _authorized_projection(
        identity=identity,
        tenant_id=tenant_id,
        documents=documents,
    )


@router.get(
    (
        "/employees/{employee_id}"
        "/documents/{document_id}/versions"
    ),
)
async def list_hr_document_versions(
    employee_id: str,
    document_id: str,
    identity: SovereignIdentity = Depends(
        get_current_identity
    ),
    tenant_id: str | None = Header(
        default=None,
        alias="X-Tenant-ID",
    ),
) -> list[
    dict[str, object]
]:
    if (
        not isinstance(
            tenant_id,
            str,
        )
        or not tenant_id
        or tenant_id != tenant_id.strip()
    ):
        raise HTTPException(
            status_code=403,
            detail="Tenant scope is required.",
        )

    documents = await asyncio.to_thread(
        _load_document_history,
        tenant_id=tenant_id,
        employee_id=employee_id,
        document_id=document_id,
    )

    return await _authorized_projection(
        identity=identity,
        tenant_id=tenant_id,
        documents=documents,
    )


@router.get(
    (
        "/employees/{employee_id}"
        "/versions/{document_version_id}/content"
    ),
)
async def download_hr_document(
    employee_id: str,
    document_version_id: str,
    identity: SovereignIdentity = Depends(
        get_current_identity
    ),
    tenant_id: str | None = Header(
        default=None,
        alias="X-Tenant-ID",
    ),
) -> Response:
    if (
        not isinstance(
            tenant_id,
            str,
        )
        or not tenant_id
        or tenant_id != tenant_id.strip()
    ):
        raise HTTPException(
            status_code=403,
            detail="Tenant scope is required.",
        )

    document = await asyncio.to_thread(
        _load_exact_document,
        tenant_id=tenant_id,
        employee_id=employee_id,
        document_version_id=(
            document_version_id
        ),
    )

    await _authorize(
        identity=identity,
        tenant_id=tenant_id,
        sensitivity=document.sensitivity,
        access="read",
    )

    config = _s3_configuration()

    try:
        payload = await asyncio.to_thread(
            _read_document_bytes,
            document,
            config,
        )
    except HrDocumentS3StorageAdapterError as error:
        raise _unavailable(
            "HR document provider is unavailable."
        ) from error
    except Exception as error:
        raise _unavailable(
            "HR document integrity verification failed."
        ) from error

    return Response(
        content=payload,
        media_type=document.media_type,
        status_code=200,
    )


__all__ = [
    "VERSION",
    "ROUTER_PREFIX",
    "router",
]


# ARTIFACT: tools/eos/api/hr_document_router.py
# VERSION: v1.0.0-P0-C12F7C-HR-DOCUMENT-HTTP
# ROUTES: exactly four canonical HR document operations
# UPLOAD: bounded raw-stream ingress to one F6F worker
# WRITE AUTHORITY: canonical class -> persisted sensitivity policy
# READ AUTHORITY: persisted sensitivity only
# PROVIDER COORDINATES: server/persisted metadata only
# PROVIDER MUTATION SURFACE: write orchestration only
# END OF WILSY OS SOVEREIGN ARTIFACT
