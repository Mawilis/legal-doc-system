"""TITLE: WILSY OS Legal Operations Read Projection Router.
VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-READ-API
AUTHORITY: Authenticated, tenant-scoped projection of existing Legal Operations evidence only.
EPITOME: Exposes bounded read-only cockpit projections while P1/P2/P4-P6F
         remain the canonical lifecycle, evidence, and commercial authorities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_operations_router.py
COLLABORATION / OWNERSHIP: Python EOS API composition; domain registries remain authoritative.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: v1.0.0-L7A-LEGAL-OPERATIONS-READ-API establishes authenticated,
           conjunctive tenant authorization and bounded P2 lifecycle reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: JWT claims and X-Tenant-ID are never authority;
                            repository access follows successful current-truth authorization.
TENANT BOUNDARY: Every query binds the exact authorized tenant and resource identity;
                 foreign absence is returned as 404 without disclosure.
AUTHORITY BOUNDARY: Read projection only. This router never creates, transitions,
                    derives, or mutates Legal Operations, billing, invoice, payment,
                    or settlement truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Missing authority, unknown resources, malformed records,
                         client projection policy gaps, and persistence failures deny.
"""
from __future__ import annotations

import re
from typing import Any, Final

from fastapi import APIRouter, Depends, HTTPException, status

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION: Final[str] = "v1.0.0-L7A-LEGAL-OPERATIONS-READ-API"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CLIENT_ROLE = "tenant_legal_client"


def get_lifecycle_collection() -> Any:
    """Return the configured lifecycle collection without owning its client or transaction."""
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE")
    return database.get_collection(LIFECYCLE_COLLECTION)


def _project(value: Any) -> dict[str, Any]:
    """Serialize a bounded canonical P1 projection and exclude transport internals."""
    payload = value.to_dict()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_OPERATIONS_PROJECTION_INVALID")
    forbidden = {"_id", "credentials", "secret", "token", "password"}
    return {key: item for key, item in payload.items() if key not in forbidden}


def _resource(
    entity_type: str,
    entity_identity: str,
    context: TenantAuthorizationContext,
    collection: Any,
) -> dict[str, Any]:
    """Hydrate one exact tenant-scoped P2 record after authorization."""
    if context.decision.business_role == _CLIENT_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CLIENT_PROJECTION_POLICY_REQUIRED")
    if _IDENTITY.fullmatch(entity_identity) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LEGAL_OPERATION_NOT_FOUND")
    try:
        row = collection.find_one(
            {"tenant_id": context.tenant_id, "entity_type": entity_type, "entity_identity": entity_identity}
        )
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LEGAL_OPERATION_NOT_FOUND")
        evidence_identity = row.get("evidence_identity")
        if not isinstance(evidence_identity, str):
            raise LegalOperationsLifecycleRegistryError("M2_EVIDENCE_IDENTITY_INVALID")
        value = LegalOperationsLifecycleRegistry.get(context.tenant_id, evidence_identity, collection)
    except HTTPException:
        raise
    except LegalOperationsLifecycleRegistryError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE") from error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE") from error
    return {
        "tenant_id": context.tenant_id,
        "entity_type": entity_type,
        "entity_identity": entity_identity,
        "visibility": "AUDIT_VISIBLE",
        "data": _project(value),
    }


_INSTRUCTION_READ = RequireTenantAuthorization("legal_operations:instruction:read", "legal_instruction_read")
_ATTEMPT_READ = RequireTenantAuthorization("legal_operations:attempt:read", "legal_attempt_read")
_RETURN_READ = RequireTenantAuthorization("legal_operations:return:read", "legal_return_read")

router = APIRouter(prefix="/legal-operations", tags=["Legal Operations"])


@router.get("/instructions/{entity_identity}")
async def get_instruction(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_INSTRUCTION_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return one authorized LegalInstruction projection; no lifecycle mutation occurs."""
    return _resource("LegalInstruction", entity_identity, context, collection)


@router.get("/attempts/{entity_identity}")
async def get_attempt(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_ATTEMPT_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return one authorized ServiceAttempt projection, never service completion truth."""
    return _resource("ServiceAttempt", entity_identity, context, collection)


@router.get("/executions/{entity_identity}")
async def get_execution(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_RETURN_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return one authorized ServiceExecution projection derived from P1 evidence."""
    return _resource("ServiceExecution", entity_identity, context, collection)


@router.get("/returns/{entity_identity}")
async def get_return_of_service(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_RETURN_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return one authorized ReturnOfService projection without creating a return."""
    return _resource("ReturnOfService", entity_identity, context, collection)


__all__ = ["VERSION", "get_lifecycle_collection", "router"]

# ARTIFACT: legal_operations_router.py
# VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-READ-API
# AUTHORITY BOUNDARY: authenticated read projection only; P1/P2 remain canonical
# TENANT POSTURE: exact authorized tenant predicates; foreign absence is bounded
# FAIL-CLOSED POSTURE: missing authority, client-policy gaps, corruption, and outages deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
