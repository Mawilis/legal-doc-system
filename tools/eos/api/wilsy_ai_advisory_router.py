"""WILSY OS C1E authenticated read-only advisory HTTP product surface.

TITLE: WILSY AI Legal Next-Actions Router
VERSION: v1.0.0-C1E-R1
AUTHORITY: Wilsy OS Core Governance; transport-only product access
EPITOME: Exposes strict tenant-authenticated POST/GET routes for deterministic
         evidence-backed legal advisories while keeping orchestration,
         projection, persistence, and transaction ownership in the service.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/wilsy_ai_advisory_router.py
COLLABORATION / OWNERSHIP: FastAPI transport delegates to WilsyAIAdvisoryService.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-C1E-R1 establishes strict request/response schemas, bounded
           error translation, authenticated tenant scope, and no-store responses.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Responses exclude evidence identities, fingerprints,
                            provider/model data, prompts, and execution handles.
TENANT BOUNDARY: X-Tenant-ID and current principal/membership authorization are mandatory.
AUTHORITY BOUNDARY: Advisory review projection only; no legal or financial execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.intelligence.wilsy_ai_advisory_service import (
    GENERATE_OPERATION,
    READ_OPERATION,
    WilsyAIAdvisoryService,
    WilsyAIAdvisoryServiceError,
)

VERSION = "v1.0.0-C1E-R1"
GENERATE_PERMISSION = "wilsy_ai:legal_advisory:generate"
READ_PERMISSION = "wilsy_ai:legal_advisory:read"
_GENERATE = RequireTenantAuthorization(GENERATE_PERMISSION, GENERATE_OPERATION)
_READ = RequireTenantAuthorization(READ_PERMISSION, READ_OPERATION)


class WilsyAIAdvisoryRequest(BaseModel):
    """Strict POST body; all authority and evidence fields are forbidden."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    orchestration_id: str = Field(min_length=1, max_length=128)


router = APIRouter(prefix="/wilsy-ai", tags=["WILSY AI Legal Advisory"])


def _service(request: Request) -> WilsyAIAdvisoryService:
    value = getattr(request.app.state, "wilsy_ai_advisory_service", None)
    if isinstance(value, WilsyAIAdvisoryService):
        return value
    value = WilsyAIAdvisoryService()
    request.app.state.wilsy_ai_advisory_service = value
    return value


def _error(error: WilsyAIAdvisoryServiceError) -> HTTPException:
    code = error.code
    if code in {"C1E_ORCHESTRATION_NOT_FOUND", "C1E_ADVISORY_NOT_FOUND"}:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="C1E_RESOURCE_NOT_FOUND")
    if code == "C1E_TOOL_ASSISTED_REQUIRED":
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=code)
    if code == "C1E_SOURCE_SNAPSHOT_STALE":
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=code)
    if code == "C1E_LEGAL_AUTHORITY_DENIED":
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="C1E_LEGAL_ACCESS_DENIED")
    if code in {"C1E_SUPERSESSION_CONFLICT", "C1E_DIVERGENT_REPLAY"}:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail="C1E_ADVISORY_CONFLICT")
    if code == "C1E_ADVISORY_RECONCILIATION_REQUIRED":
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=code)
    if code.endswith("INVALID"):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=code)
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="C1E_ADVISORY_UNAVAILABLE")


@router.post("/legal-next-actions", response_model=dict[str, object], status_code=status.HTTP_201_CREATED)
async def generate_legal_next_actions(
    request: Request,
    response: Response,
    body: WilsyAIAdvisoryRequest,
    context: TenantAuthorizationContext = Depends(_GENERATE),
) -> dict[str, object]:
    """Generate one advisory or return an exact deterministic replay."""
    response.headers["Cache-Control"] = "no-store"
    try:
        result = await _service(request).generate(orchestration_id=body.orchestration_id, context=context, generated_at=datetime.now(timezone.utc))
    except WilsyAIAdvisoryServiceError as error:
        raise _error(error) from error
    if result.replay:
        response.status_code = status.HTTP_200_OK
    return result.to_public_dict()


@router.get("/legal-next-actions/{advisory_id}", response_model=dict[str, object])
async def read_legal_next_action(
    request: Request,
    response: Response,
    advisory_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read one tenant-scoped advisory with derived CURRENT/STALE status."""
    response.headers["Cache-Control"] = "no-store"
    try:
        result, disposition, superseded = await _service(request).get(advisory_id=advisory_id, context=context)
    except WilsyAIAdvisoryServiceError as error:
        raise _error(error) from error
    return result.to_public_dict(status=disposition, superseded_by=superseded)


__all__ = ["VERSION", "GENERATE_PERMISSION", "READ_PERMISSION", "WilsyAIAdvisoryRequest", "generate_legal_next_actions", "read_legal_next_action", "router"]

# ARTIFACT: wilsy_ai_advisory_router.py
# VERSION: v1.0.0-C1E-R1
# AUTHORITY BOUNDARY: authenticated advisory transport only
# TENANT POSTURE: exact X-Tenant-ID plus current IAM dependency
# FAIL-CLOSED POSTURE: strict body, bounded errors, no-store, and redacted responses
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
