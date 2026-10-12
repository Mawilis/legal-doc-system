"""WILSY OS authenticated Legal Evidence multipart HTTP boundary.

TITLE: Authenticated Legal Evidence Upload HTTP Router
VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-HTTP
AUTHORITY: Wilsy OS Core Governance / Python EOS API
EPITOME: Admit one bounded Partner-authorized multipart file, derive all legal
         scope server-side, and project only canonical commit/reconciliation truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_evidence_upload_router.py
COLLABORATION / OWNERSHIP: Canonical tenant authorization owns IAM; the L10A4
                            orchestrator owns composition; this module owns only
                            multipart validation and HTTP translation.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L10A4 establishes the authenticated upload route.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: One file field only; request size is bounded before
                             parsing; provider details and authority fields reject.
TENANT BOUNDARY: Tenant and principal derive solely from authenticated IAM context.
AUTHORITY BOUNDARY: Transport only; no document, storage, provider, availability,
                    lifecycle, retention, deletion or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

import os
from typing import Any, Final

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from starlette.datastructures import UploadFile

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database
from tools.eos.legal_operations.service.legal_evidence_s3_storage_adapter import LegalEvidenceS3Configuration, LegalEvidenceS3StorageAdapter
from tools.eos.legal_operations.service.legal_evidence_upload_orchestrator import MAX_UPLOAD_BYTES, LegalEvidenceUploadError, LegalEvidenceUploadOrchestrator


VERSION: Final[str] = "v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-HTTP"
PERMISSION: Final[str] = "legal_operations:evidence:write"
OPERATION: Final[str] = "legal_evidence_write"
MAX_MULTIPART_BYTES: Final[int] = MAX_UPLOAD_BYTES + (1024 * 1024)
SAFE_MEDIA_TYPES: Final[frozenset[str]] = frozenset(
    {"application/pdf", "image/jpeg", "image/png", "image/tiff", "text/plain"}
)

router = APIRouter(prefix="/legal-operations/evidence", tags=["Legal Evidence"])
_WRITE = RequireTenantAuthorization(PERMISSION, OPERATION)


def get_legal_evidence_upload_orchestrator() -> LegalEvidenceUploadOrchestrator:
    """Compose server-only persistence and provider dependencies fail closed."""
    client = get_client()
    database = get_database()
    bucket = os.getenv("WILSY_LEGAL_EVIDENCE_S3_BUCKET", "").strip()
    region = os.getenv("WILSY_LEGAL_EVIDENCE_S3_REGION", "af-south-1").strip()
    kms_key = os.getenv("WILSY_LEGAL_EVIDENCE_S3_KMS_KEY_ID", "").strip() or None
    if client is None or database is None or not bucket:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "LEGAL_EVIDENCE_UPLOAD_UNAVAILABLE"})
    try:
        storage = LegalEvidenceS3StorageAdapter(LegalEvidenceS3Configuration(bucket=bucket, region=region, kms_key_id=kms_key))
        return LegalEvidenceUploadOrchestrator(client=client, database=database, storage=storage)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "LEGAL_EVIDENCE_UPLOAD_UNAVAILABLE"}) from error


def _http_error(error: BaseException) -> HTTPException:
    """Translate stable domain failures without disclosing foreign/provider truth."""
    code = str(getattr(error, "code", "LEGAL_EVIDENCE_UPLOAD_FAILED"))
    if "DOCUMENT_UNAVAILABLE" in code or "NOT_FOUND" in code:
        return HTTPException(status_code=404, detail={"code": "LEGAL_EVIDENCE_DOCUMENT_UNAVAILABLE"})
    if "CAPACITY" in code or "CONFLICT" in code or "RETRY" in code:
        return HTTPException(status_code=409, detail={"code": code})
    if any(token in code for token in ("INVALID", "REQUIRED", "UNSUPPORTED", "LENGTH")):
        return HTTPException(status_code=422, detail={"code": code})
    return HTTPException(status_code=503, detail={"code": "LEGAL_EVIDENCE_UPLOAD_UNAVAILABLE"})


@router.post("/documents/{document_id}")
async def upload_legal_evidence(
    document_id: str,
    request: Request,
    content_length: int | None = Header(default=None, alias="Content-Length"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    context: TenantAuthorizationContext = Depends(_WRITE),
    orchestrator: LegalEvidenceUploadOrchestrator = Depends(get_legal_evidence_upload_orchestrator),
) -> dict[str, Any]:
    """Admit one bounded file for one server-resolved canonical ProcessDocument.

    Only ``file`` is accepted in multipart data. Tenant, principal, matter,
    fingerprints, provider coordinates, and storage references cannot be
    nominated by the browser. A COMMITTED response proves the existing
    two-plane commit; RECONCILIATION_REQUIRED is explicit non-canonical state.
    """
    if content_length is None or content_length <= 0 or content_length > MAX_MULTIPART_BYTES:
        raise HTTPException(status_code=413, detail={"code": "LEGAL_EVIDENCE_MULTIPART_SIZE_INVALID"})
    if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip() or len(idempotency_key) > 160:
        raise HTTPException(status_code=422, detail={"code": "LEGAL_EVIDENCE_IDEMPOTENCY_KEY_INVALID"})
    try:
        form = await request.form(max_files=1, max_fields=0, max_part_size=MAX_UPLOAD_BYTES)
    except Exception as error:
        raise HTTPException(status_code=422, detail={"code": "LEGAL_EVIDENCE_MULTIPART_INVALID"}) from error
    if list(form.keys()) != ["file"]:
        raise HTTPException(status_code=422, detail={"code": "LEGAL_EVIDENCE_MULTIPART_FIELDS_INVALID"})
    file = form.get("file")
    if not isinstance(file, UploadFile):
        raise HTTPException(status_code=422, detail={"code": "LEGAL_EVIDENCE_FILE_REQUIRED"})
    filename = file.filename or ""
    media_type = (file.content_type or "").split(";", 1)[0].strip().lower()
    if not filename or filename != filename.strip() or len(filename) > 255 or any(ord(character) < 32 for character in filename):
        raise HTTPException(status_code=422, detail={"code": "LEGAL_EVIDENCE_FILENAME_INVALID"})
    if media_type not in SAFE_MEDIA_TYPES:
        raise HTTPException(status_code=422, detail={"code": "LEGAL_EVIDENCE_MEDIA_TYPE_UNSUPPORTED"})
    try:
        file.file.seek(0, 2)
        measured = file.file.tell()
        file.file.seek(0)
        if measured <= 0 or measured > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail={"code": "LEGAL_EVIDENCE_FILE_SIZE_INVALID"})
        result = orchestrator.upload(
            tenant_id=context.tenant_id, document_id=document_id, filename=filename,
            media_type=media_type, content_length=measured, stream=file.file,
            idempotency_key=idempotency_key,
        )
    except HTTPException:
        raise
    except Exception as error:
        raise _http_error(error) from error
    finally:
        await file.close()
    return {
        "schema": "WILSY-LEGAL-EVIDENCE-UPLOAD-RESULT/V1",
        "version": VERSION,
        "ingestion_reference": result.ingestion_reference,
        "document_id": result.document_id,
        "case_matter_id": result.case_matter_id,
        "state": result.state,
        "content_reference": result.content_reference,
        "content_fingerprint": result.content_fingerprint,
        "content_length": result.content_length,
        "uncertainty_id": result.uncertainty_id,
    }


__all__ = ["MAX_MULTIPART_BYTES", "OPERATION", "PERMISSION", "SAFE_MEDIA_TYPES", "VERSION", "get_legal_evidence_upload_orchestrator", "router", "upload_legal_evidence"]

# ARTIFACT: legal_evidence_upload_router.py
# VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-HTTP
# AUTHORITY BOUNDARY: authenticated bounded multipart transport only
# TENANT POSTURE: canonical IAM context exclusively supplies tenant/principal scope
# FAIL-CLOSED POSTURE: extra fields, invalid media/size, authority drift and unavailable dependencies reject
# PROVIDER POSTURE: credentials and provider coordinates remain server-private
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
