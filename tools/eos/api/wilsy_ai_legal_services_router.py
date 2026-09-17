"""WILSY OS C1C authenticated legal-services AI route.

TITLE: WILSY AI Legal Services Orchestration HTTP Boundary
VERSION: v1.1.0-C1C-R1A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Accepts only a prompt and replay key, then delegates to the
         server-owned bounded C1C orchestrator.  Caller JSON never supplies
         tenant, principal, model, entitlement, tool, or legal authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/wilsy_ai_legal_services_router.py
COLLABORATION / OWNERSHIP: FastAPI transport only; C1C orchestrator owns
                            policy, tool membership and evidence composition.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: 2026-09-17 v1.1.0-C1C-R1A binds the route to the dedicated
wilsy_ai:legal_services:execute permission and operation.
2026-09-16 v1.0.0-C1C-R1 adds POST /api/wilsy-ai/legal-services.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw prompts or provider output in responses/logs.
TENANT BOUNDARY: X-Tenant-ID and authenticated identity are dependency-owned.
AUTHORITY BOUNDARY: Bounded legal-read orchestration; no command or finance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing orchestrator, key, auth, parser or policy denies.
"""
from __future__ import annotations

import re
from typing import Any
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict

from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.intelligence.wilsy_ai_tool_orchestrator import WilsyAIToolOrchestrator, C1COrchestrationError

VERSION = "v1.1.0-C1C-R1A"
# C1C owns a dedicated capability so legal-services execution cannot inherit
# the narrower C1B reasoning permission by accident.
LEGAL_SERVICES_PERMISSION = "wilsy_ai:legal_services:execute"
_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")
_AUTH = RequireTenantAuthorization(LEGAL_SERVICES_PERMISSION, "wilsy_ai_legal_services_execute")


class WilsyAILegalServicesRequest(BaseModel):
    """Strict body: prompt only; all authority fields are forbidden."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    prompt: str


router = APIRouter(prefix="/wilsy-ai", tags=["WILSY AI Legal Services"])


def _key(value: str | None) -> str:
    if not isinstance(value, str) or _KEY.fullmatch(value) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="C1C_IDEMPOTENCY_KEY_REQUIRED")
    return value


@router.post("/legal-services", response_model=dict[str, object])
def execute_legal_services(request: Request, body: WilsyAILegalServicesRequest, context: TenantAuthorizationContext = Depends(_AUTH), idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")) -> dict[str, object]:
    """Execute one bounded C1C request with no authority-bearing response fields."""
    key = _key(idempotency_key)
    orchestrator = getattr(request.app.state, "wilsy_ai_legal_services_orchestrator", None)
    if not isinstance(orchestrator, WilsyAIToolOrchestrator):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="C1C_ORCHESTRATOR_UNAVAILABLE")
    try:
        result = orchestrator.run(tenant_id=context.tenant_id, principal_id=context.identity.identity_id, idempotency_key=key, prompt=body.prompt, context=context, collections=getattr(request.app.state, "wilsy_ai_legal_tool_collections", {}))
        return result.to_dict()
    except C1COrchestrationError as error:
        code = getattr(error, "code", "C1C_UNAVAILABLE")
        if "DENIED" in code or "UNKNOWN" in code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="C1C_LEGAL_SERVICE_DENIED") from error
        if "REPLAY" in code:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="C1C_REPLAY_CONFLICT") from error
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="C1C_LEGAL_SERVICE_UNAVAILABLE") from error


__all__ = ["VERSION", "LEGAL_SERVICES_PERMISSION", "WilsyAILegalServicesRequest", "execute_legal_services", "router"]

# ARTIFACT: wilsy_ai_legal_services_router.py
# VERSION: v1.1.0-C1C-R1A
# AUTHORITY BOUNDARY: authenticated bounded legal-read transport
# TENANT POSTURE: dependency-owned exact tenant and principal
# FAIL-CLOSED POSTURE: prompt-only body and required idempotency key
# END OF WILSY OS SOVEREIGN ARTIFACT
