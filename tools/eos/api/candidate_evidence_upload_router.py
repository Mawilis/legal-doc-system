"""Authenticated streaming ingress for candidate and signed-offer evidence.

The request identity and tenant come only from canonical EOS authorization.
The body is streamed to the provider; Mongo transactions never span S3 I/O.
Provider verification and custody registration are separate explicit gates.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterable

import boto3
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.domain.candidate_evidence import (
    CandidateEvidenceKind,
    CandidateEvidenceObjectMetadata,
)
from tools.eos.saas.hr.candidate_evidence_registry import (
    COLLECTION as EVIDENCE_COLLECTION,
    EVENT_COLLECTION as EVIDENCE_EVENT_COLLECTION,
    CandidateEvidenceRegistry,
    CandidateEvidenceRegistryConflict,
    CandidateEvidenceRegistryError,
    CandidateEvidenceRegistryNotFound,
)
from tools.eos.saas.hr.candidate_evidence_s3_storage_adapter import (
    CandidateEvidenceS3Error,
    CandidateEvidenceS3Configuration,
    CandidateEvidenceS3StorageAdapter,
)
from tools.eos.saas.hr.candidate_evidence_storage import (
    MAX_OBJECT_BYTES,
    CandidateEvidenceWriteIntent,
)
from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    COLLECTION as ATTEMPT_COLLECTION,
    EVENT_COLLECTION as ATTEMPT_EVENT_COLLECTION,
    CandidateEvidenceUploadAttemptRegistry,
    UploadAttemptStatus,
    UploadAttemptConflict,
    UploadAttemptError,
)
from tools.eos.saas.hr.candidate_evidence_upload_orchestrator import (
    CandidateEvidenceUploadOrchestrationError,
    CandidateEvidenceUploadOrchestrator,
)
from tools.eos.saas.hr.hiring_lifecycle_registry import (
    CANDIDATE_COLLECTION,
    OFFER_COLLECTION,
    HiringLifecycleRegistry,
    HiringLifecycleNotFound,
    EVENT_COLLECTION as HIRING_EVENT_COLLECTION,
)

router = APIRouter(prefix="/hr/hiring", tags=["Candidate Evidence"])
_UPLOAD = RequireTenantAuthorization(
    "hr:hiring_candidate_evidence:upload",
    "hr_hiring_candidate_evidence_upload",
)
_READ = RequireTenantAuthorization(
    "hr:hiring_candidate_evidence:read",
    "hr_hiring_candidate_evidence_read",
)

_ALLOWED_MEDIA_PREFIXES = ("application/pdf", "image/", "application/msword",
                            "application/vnd.openxmlformats-officedocument.")


def _database():
    database = get_database()
    client = get_client()
    if database is None or client is None:
        raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_DATABASE_UNAVAILABLE")
    return client, database


def _transaction(callback):
    client, _ = _database()
    try:
        with client.start_session() as session:
            return session.with_transaction(
                callback,
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HiringLifecycleNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except UploadAttemptConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except UploadAttemptError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except CandidateEvidenceRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except CandidateEvidenceRegistryError as error:
        raise HTTPException(status_code=503, detail=error.code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_TRANSACTION_UNAVAILABLE") from error


@router.on_event("startup")
def ensure_candidate_evidence_upload_indexes() -> None:
    """Install durable upload and custody indexes before accepting commands."""
    _, database = _database()
    CandidateEvidenceUploadAttemptRegistry.ensure_indexes(
        database[ATTEMPT_COLLECTION], database[ATTEMPT_EVENT_COLLECTION],
    )
    CandidateEvidenceRegistry.ensure_indexes(
        database[EVIDENCE_COLLECTION], database[EVIDENCE_EVENT_COLLECTION],
    )


def _storage() -> CandidateEvidenceS3StorageAdapter:
    bucket = os.getenv("WILSY_HR_CANDIDATE_EVIDENCE_S3_BUCKET", "").strip()
    region = os.getenv("WILSY_HR_CANDIDATE_EVIDENCE_S3_REGION", "").strip()
    kms_key_id = os.getenv("WILSY_HR_CANDIDATE_EVIDENCE_S3_KMS_KEY_ID", "").strip()
    if not bucket or not region or not kms_key_id:
        raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_PROVIDER_NOT_CONFIGURED")
    try:
        config = CandidateEvidenceS3Configuration(bucket=bucket, region=region, kms_key_id=kms_key_id)
        return CandidateEvidenceS3StorageAdapter(
            config, client=boto3.client("s3", region_name=region),
        )
    except Exception as error:
        raise HTTPException(status_code=503, detail="CANDIDATE_EVIDENCE_PROVIDER_UNAVAILABLE") from error


def _registries(database: Any):
    hiring = HiringLifecycleRegistry(
        database[CANDIDATE_COLLECTION],
        database[OFFER_COLLECTION],
        database[HIRING_EVENT_COLLECTION],
    )
    attempts = CandidateEvidenceUploadAttemptRegistry(
        database[ATTEMPT_COLLECTION], database[ATTEMPT_EVENT_COLLECTION],
    )
    custody = CandidateEvidenceRegistry(
        database[EVIDENCE_COLLECTION], database[EVIDENCE_EVENT_COLLECTION],
    )
    return hiring, attempts, custody


async def _request_chunks(request: Request, expected_length: int) -> AsyncIterable[bytes]:
    observed = 0
    async for chunk in request.stream():
        # Starlette emits a final empty sentinel; it is not an object part.
        if chunk:
            observed += len(chunk)
            if observed > expected_length:
                raise ValueError("CANDIDATE_EVIDENCE_CONTENT_LENGTH_EXCEEDED")
            yield chunk
    if observed != expected_length:
        raise ValueError("CANDIDATE_EVIDENCE_CONTENT_LENGTH_MISMATCH")


@router.put("/candidates/{candidate_id}/evidence/{evidence_id}/{evidence_version_id}", status_code=201)
async def upload_candidate_evidence(
    candidate_id: str,
    evidence_id: str,
    evidence_version_id: str,
    request: Request,
    content_length: int = Header(alias="Content-Length", ge=1, le=MAX_OBJECT_BYTES),
    media_type: str = Header(alias="X-Evidence-Media-Type", min_length=1, max_length=128),
    original_filename: str = Header(alias="X-Evidence-Filename", min_length=1, max_length=255),
    evidence_kind: CandidateEvidenceKind = Header(alias="X-Evidence-Kind"),
    offer_id: str | None = Header(default=None, alias="X-Offer-Id", max_length=180),
    context: TenantAuthorizationContext = Depends(_UPLOAD),
):
    """Stream an admitted evidence object and atomically register verified custody."""
    if not any(media_type.lower().startswith(prefix) for prefix in _ALLOWED_MEDIA_PREFIXES):
        raise HTTPException(status_code=415, detail="CANDIDATE_EVIDENCE_MEDIA_TYPE_UNSUPPORTED")
    if evidence_kind is CandidateEvidenceKind.SIGNED_OFFER and not offer_id:
        raise HTTPException(status_code=422, detail="CANDIDATE_EVIDENCE_SIGNED_OFFER_SCOPE_REQUIRED")
    if evidence_kind is CandidateEvidenceKind.CANDIDATE_PROFILE and offer_id is not None:
        raise HTTPException(status_code=422, detail="CANDIDATE_EVIDENCE_PROFILE_OFFER_SCOPE_FORBIDDEN")

    client, database = _database()
    hiring, attempts, custody = _registries(database)
    tenant_id = context.tenant_id
    actor_id = context.identity.identity_id

    def admit(tx):
        candidate = hiring.get_candidate(tenant_id=tenant_id, candidate_id=candidate_id, session=tx)
        try:
            custody.get(
                tenant_id=tenant_id, candidate_id=candidate_id,
                evidence_id=evidence_id, evidence_version_id=evidence_version_id,
                session=tx,
            )
        except CandidateEvidenceRegistryNotFound:
            pass
        else:
            raise HTTPException(status_code=409, detail="CANDIDATE_EVIDENCE_VERSION_ALREADY_REGISTERED")
        if evidence_kind is CandidateEvidenceKind.SIGNED_OFFER:
            offer = hiring.get_offer(tenant_id=tenant_id, offer_id=offer_id, session=tx)
            if offer.candidate_id != candidate_id:
                raise HTTPException(status_code=404, detail="HIRING_OFFER_NOT_FOUND")
        return candidate

    try:
        candidate = _transaction(admit)
    except HiringLifecycleNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error

    try:
        intent = CandidateEvidenceWriteIntent(
            tenant_id=tenant_id,
            candidate_id=candidate_id,
            evidence_id=evidence_id,
            evidence_version_id=evidence_version_id,
            ingestion_reference="ING-" + uuid.uuid4().hex,
            media_type=media_type,
            original_filename=original_filename,
            admitted_max_content_length=content_length,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    storage = _storage()

    def transaction(callback):
        return _transaction(lambda tx: callback(tx))

    orchestrator = CandidateEvidenceUploadOrchestrator(
        registry=attempts,
        storage=storage,
        transaction=transaction,
    )
    try:
        attempt_id, provider_evidence = await orchestrator.upload(
            intent=intent,
            chunks=_request_chunks(request, content_length),
            actor_principal_id=actor_id,
            offer_id=offer_id,
            evidence_kind=evidence_kind.value,
        )
        # Re-inspect the exact provider object version outside Mongo. A HEAD
        # failure leaves PROVIDER_VERIFIED evidence unregistered for recovery.
        verified = await asyncio.to_thread(storage.inspect, intent, provider_evidence)
    except CandidateEvidenceUploadOrchestrationError as error:
        status = 202 if error.uncertain else 422
        raise HTTPException(status_code=status, detail=error.code) from error
    except CandidateEvidenceS3Error as error:
        status = 202 if error.uncertain else 503
        raise HTTPException(status_code=status, detail=error.code) from error

    metadata = CandidateEvidenceObjectMetadata(
        tenant_id=tenant_id,
        candidate_id=candidate_id,
        evidence_id=evidence_id,
        evidence_version_id=evidence_version_id,
        evidence_kind=evidence_kind,
        media_type=media_type,
        original_filename=original_filename,
        byte_length=verified.byte_length,
        content_digest_sha3_512=verified.content_digest_sha3_512,
        storage_provider_id="aws_s3",
        storage_object_reference=verified.storage_object_reference,
        object_version_reference=verified.object_version_reference,
        provider_integrity_reference=verified.provider_integrity_reference,
        ingestion_reference=intent.ingestion_reference,
        created_at=datetime.now(timezone.utc),
        created_by_principal_id=actor_id,
        offer_id=offer_id,
    )

    def register_custody(tx):
        custody.register(
            metadata,
            actor_principal_id=actor_id,
            idempotency_key=f"evidence-upload:{attempt_id}",
            session=tx,
        )
        current = attempts.get(
            tenant_id=tenant_id, upload_attempt_id=attempt_id, session=tx,
        )
        updated = current.advance(
            status=UploadAttemptStatus.CUSTODY_REGISTERED,
            expected_revision=current.revision,
            occurred_at=datetime.now(timezone.utc),
        )
        attempts.transition(
            current, updated, expected_revision=current.revision,
            actor_principal_id=actor_id, session=tx,
        )
        return updated

    registered = _transaction(register_custody)
    return {
        "upload_attempt_id": attempt_id,
        "status": registered.status.value,
        "candidate_id": candidate_id,
        "evidence_id": evidence_id,
        "evidence_version_id": evidence_version_id,
        "byte_length": verified.byte_length,
        "content_digest_sha3_512": verified.content_digest_sha3_512,
        "custody_registered": True,
    }


@router.get("/candidates/{candidate_id}/evidence/{evidence_id}/{evidence_version_id}")
async def read_candidate_evidence(
    candidate_id: str,
    evidence_id: str,
    evidence_version_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
):
    """Read exact-version evidence only after tenant-scoped custody and byte verification."""
    _, database = _database()
    _, _, custody = _registries(database)

    def load(tx):
        try:
            return custody.get(
                tenant_id=context.tenant_id,
                candidate_id=candidate_id,
                evidence_id=evidence_id,
                evidence_version_id=evidence_version_id,
                session=tx,
            )
        except CandidateEvidenceRegistryNotFound as error:
            raise HTTPException(status_code=404, detail="CANDIDATE_EVIDENCE_NOT_FOUND") from error

    metadata = _transaction(load)
    storage = _storage()
    try:
        verified_file = await asyncio.to_thread(storage.read_verified_object, metadata)
    except CandidateEvidenceS3Error as error:
        raise HTTPException(status_code=503, detail=error.code) from error

    return StreamingResponse(
        iter(lambda: verified_file.read(64 * 1024), b""),
        media_type=metadata.media_type,
        headers={
            "Content-Length": str(metadata.byte_length),
            "Content-Disposition": "attachment",
            "Cache-Control": "no-store",
            "X-Content-Digest-SHA3-512": metadata.content_digest_sha3_512,
        },
        background=BackgroundTask(verified_file.close),
    )


__all__ = ["router", "upload_candidate_evidence", "read_candidate_evidence"]
