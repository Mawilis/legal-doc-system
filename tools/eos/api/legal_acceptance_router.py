"""Authenticated legal-acceptance HTTP projection and mutation boundary.

TITLE: WILSY OS Legal Acceptance Router
VERSION: v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exposes current acceptance requirements and append-only acceptance
         submission while preserving server-selected tenant, principal,
         document, and digest authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_acceptance_router.py
COLLABORATION / OWNERSHIP: Auth dependency authenticates; service composes
                            document and acceptance registries; router owns HTTP only.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0 establishes no-store status/document projections and an
           Idempotency-Key guarded acceptance mutation surface.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Request body cannot provide tenant, principal,
                            approval, version, or digest authority.
TENANT BOUNDARY: Every operation uses the authenticated canonical identity.
AUTHORITY BOUNDARY: Acknowledgement/acceptance only; no corporate execution,
                    signature pad, billing, payment, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from typing import Any, Final

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_acceptance import AcceptanceMethod
from tools.eos.legal_operations.registry.legal_acceptance_registry import COLLECTION as ACCEPTANCE_COLLECTION
from tools.eos.legal_operations.registry.legal_document_registry import COLLECTION as DOCUMENT_COLLECTION
from tools.eos.legal_operations.service.legal_acceptance_service import LegalAcceptanceService, LegalAcceptanceServiceError


VERSION: Final[str] = "v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE"
router = APIRouter(prefix="/legal-acceptance", tags=["Legal Acceptance"])


class AcceptanceSubmission(BaseModel):
    """Only server-verifiable document identity and acceptance method."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    document_id: str = Field(min_length=1, max_length=256)
    document_version: str = Field(min_length=1, max_length=64)
    document_sha3_512: str = Field(min_length=128, max_length=128, pattern=r"^[0-9a-f]{128}$")
    acceptance_method: AcceptanceMethod
    locale: str = Field(default="en-ZA", min_length=2, max_length=32)


def _service() -> LegalAcceptanceService:
    database = kernel_db.get_database()
    if database is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_ACCEPTANCE_PERSISTENCE_UNAVAILABLE")
    return LegalAcceptanceService(database[DOCUMENT_COLLECTION], database[ACCEPTANCE_COLLECTION])


def _session_id(identity: SovereignIdentity) -> str:
    # The authenticated identity is the only available durable context in this
    # router; a request correlation reference is not elevated to legal authority.
    return f"authenticated:{identity.identity_id}"


def _translate(error: LegalAcceptanceServiceError) -> HTTPException:
    code = str(error)
    client_errors = {"LEGAL_ACCEPTANCE_DOCUMENT_NOT_APPROVED", "LEGAL_ACCEPTANCE_DOCUMENT_NOT_CURRENT", "LEGAL_ACCEPTANCE_CORPORATE_EXECUTION_UNAVAILABLE", "LEGAL_ACCEPTANCE_METHOD_INVALID", "LEGAL_ACCEPTANCE_IDEMPOTENCY_REQUIRED"}
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY if code in client_errors else status.HTTP_503_SERVICE_UNAVAILABLE, detail=code)


@router.get("/status")
def acceptance_status(response: Response, identity: SovereignIdentity = Depends(get_current_identity), service: LegalAcceptanceService = Depends(_service)) -> dict[str, Any]:
    """Return the server-derived acceptance plan for the authenticated principal."""
    response.headers["Cache-Control"] = "no-store"
    try:
        return service.status(identity, session_id=_session_id(identity), locale="en-ZA")
    except LegalAcceptanceServiceError as error:
        raise _translate(error) from error


@router.get("/documents/{document_id}")
def legal_document(document_id: str, response: Response, identity: SovereignIdentity = Depends(get_current_identity), service: LegalAcceptanceService = Depends(_service)) -> dict[str, Any]:
    """Return only the server-selected current approved document for this principal."""
    response.headers["Cache-Control"] = "no-store"
    try:
        plan = service.status(identity, session_id=_session_id(identity), locale="en-ZA")
        selected = next(
            (item for item in plan.get("documents", []) if item.get("documentId") == document_id),
            None,
        )
        if selected is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LEGAL_DOCUMENT_NOT_FOUND",
            )
        document = service.document_registry.get(
            document_id,
            selected.get("version"),
            collection=service.document_collection,
        )
        if (
            document is None
            or document.status.value != "APPROVED"
            or document.sha3_512 != selected.get("sha3_512")
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LEGAL_DOCUMENT_NOT_FOUND",
            )
        return document.to_document()
    except HTTPException:
        raise
    except LegalAcceptanceServiceError as error:
        raise _translate(error) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_DOCUMENT_READ_FAILED",
        ) from error


@router.post("/accept", status_code=status.HTTP_201_CREATED)
def submit_acceptance(payload: AcceptanceSubmission, response: Response, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), identity: SovereignIdentity = Depends(get_current_identity), service: LegalAcceptanceService = Depends(_service)) -> dict[str, Any]:
    """Append one acceptance; replay is idempotent and divergence is rejected."""
    response.headers["Cache-Control"] = "no-store"
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="LEGAL_ACCEPTANCE_IDEMPOTENCY_REQUIRED")
    try:
        return service.accept(identity, document_id=payload.document_id, document_version=payload.document_version, document_sha3_512=payload.document_sha3_512, acceptance_method=payload.acceptance_method, idempotency_key=idempotency_key, session_id=_session_id(identity), locale=payload.locale)
    except LegalAcceptanceServiceError as error:
        raise _translate(error) from error


__all__ = ["AcceptanceSubmission", "VERSION", "router"]

# ARTIFACT: legal_acceptance_router.py
# VERSION: v1.0.0-R1D-B0F-B4-PRODUCTION-LEGAL-ACCEPTANCE
# AUTHORITY BOUNDARY: authenticated HTTP transport only
# TENANT POSTURE: tenant/principal derive from authenticated identity, never body
# FAIL-CLOSED POSTURE: missing auth, missing idempotency, and unavailable truth deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
