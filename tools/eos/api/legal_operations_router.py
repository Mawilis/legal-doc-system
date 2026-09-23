"""Authenticated deterministic read projections for Legal Operations.

TITLE: WILSY OS Legal Operations Read Projection Router
VERSION: v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API
AUTHORITY: Authenticated, tenant-scoped projection of canonical Legal Operations evidence only.
EPITOME: Resolve complete P2 immutable entity history through the deterministic
         L8-0 current-snapshot projection before exposing bounded cockpit reads.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_operations_router.py
COLLABORATION / OWNERSHIP: Python EOS API composition. P1 owns lifecycle truth,
                            P2 owns immutable persistence/history hydration,
                            L8-0 owns deterministic current-state projection,
                            and tenant authorization owns access authority.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API replaces
           arbitrary single-row lifecycle selection with exact complete P2
           history retrieval plus deterministic current projection, preserving
           bounded foreign absence and existing client-policy denial.
           2026-09-15 v1.0.0-L7A-LEGAL-OPERATIONS-READ-API established
           authenticated conjunctive tenant authorization and bounded P2 reads.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: JWT claims and X-Tenant-ID never create authority;
                             persistence access follows successful durable
                             tenant authorization. Secrets and transport
                             internals are excluded from response projections.
TENANT BOUNDARY: Every history query binds the exact authorized tenant, exact
                 canonical entity type, and exact entity identity. Foreign
                 absence is returned as bounded 404 without disclosure.
AUTHORITY BOUNDARY: Read projection only. This router cannot create, accept,
                    receive, allocate, attempt, serve, generate a return, bill,
                    invoice, pay, execute, settle, or mutate Legal Operations.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement. Legal reads never infer paid or
                              settled truth.
TRANSACTION BOUNDARY: Read composition owns no Mongo session or transaction;
                      P2 receives the collection and performs read-only exact
                      history enumeration.
FAIL-CLOSED DECLARATION: Missing authority, malformed identity, client-policy
                         gaps, absent exact history, P2 corruption/outage,
                         history forks/divergence, and invalid projections deny.
"""
from __future__ import annotations

import re
from typing import Any, Final

from fastapi import APIRouter, Depends, HTTPException, status

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    LegalInstruction,
    ReturnOfService,
    ServiceAttempt,
    ServiceExecution,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION: Final[str] = "v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CLIENT_ROLE = "tenant_legal_client"
_ENTITY_CLASSES: Final[dict[str, type[Any]]] = {
    "LegalInstruction": LegalInstruction,
    "ServiceAttempt": ServiceAttempt,
    "ServiceExecution": ServiceExecution,
    "ReturnOfService": ReturnOfService,
}


def get_lifecycle_collection() -> Any:
    """Return the configured lifecycle collection without owning persistence lifecycle.

    The provider creates no tenant, lifecycle, transaction, billing, payment,
    execution, or settlement authority. Database unavailability fails closed
    with a bounded 503 response.
    """
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        )
    return database.get_collection(LIFECYCLE_COLLECTION)


def _project(value: Any) -> dict[str, Any]:
    """Serialize one bounded canonical P1 value without transport/secret fields.

    Projection is read-only and creates no durable fact. A malformed serializer
    result fails closed rather than manufacturing response truth.
    """
    payload = value.to_dict()
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PROJECTION_INVALID",
        )
    forbidden = {"_id", "credentials", "secret", "token", "password"}
    return {key: item for key, item in payload.items() if key not in forbidden}


def _resource(
    entity_type: str,
    entity_identity: str,
    context: TenantAuthorizationContext,
    collection: Any,
) -> dict[str, Any]:
    """Return deterministic current truth for one authorized exact entity.

    Authorization precedes persistence access. The method requests the complete
    exact tenant/type/entity history from P2, returns 404 for exact-scope
    absence, and delegates current-state selection to the L8-0 deterministic
    projection authority. P2 corruption or projection divergence becomes a
    bounded evidence-unavailable response; arbitrary historical selection is
    forbidden. The method is read-only and owns no transaction or financial
    authority.
    """
    if context.decision.business_role == _CLIENT_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CLIENT_PROJECTION_POLICY_REQUIRED",
        )
    if _IDENTITY.fullmatch(entity_identity) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LEGAL_OPERATION_NOT_FOUND",
        )

    expected_type = _ENTITY_CLASSES.get(entity_type)
    if expected_type is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PROJECTION_INVALID",
        )

    try:
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            context.tenant_id,
            entity_type,
            entity_identity,
            collection,
        )
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LEGAL_OPERATION_NOT_FOUND",
            )
        value = resolve_current_lifecycle_snapshot(
            history,
            expected_type=expected_type,
        )
    except HTTPException:
        raise
    except (
        LegalOperationsLifecycleRegistryError,
        LegalOperationsCurrentProjectionError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        ) from error

    return {
        "tenant_id": context.tenant_id,
        "entity_type": entity_type,
        "entity_identity": entity_identity,
        "visibility": "AUDIT_VISIBLE",
        "data": _project(value),
    }


_INSTRUCTION_READ = RequireTenantAuthorization(
    "legal_operations:instruction:read",
    "legal_instruction_read",
)
_ATTEMPT_READ = RequireTenantAuthorization(
    "legal_operations:attempt:read",
    "legal_attempt_read",
)
_RETURN_READ = RequireTenantAuthorization(
    "legal_operations:return:read",
    "legal_return_read",
)

router = APIRouter(prefix="/legal-operations", tags=["Legal Operations"])


@router.get("/instructions/{entity_identity}")
async def get_instruction(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_INSTRUCTION_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return deterministic current LegalInstruction truth for one authorized tenant.

    The route is read-only, applies the existing instruction-read permission,
    and cannot create or transition instruction, document, service, billing,
    payment, execution, or settlement truth.
    """
    return _resource("LegalInstruction", entity_identity, context, collection)


@router.get("/attempts/{entity_identity}")
async def get_attempt(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_ATTEMPT_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return deterministic current ServiceAttempt truth without implying service.

    Attempt state remains distinct from successful service and the route owns no
    lifecycle mutation, transaction, billing, financial execution, or settlement
    authority.
    """
    return _resource("ServiceAttempt", entity_identity, context, collection)


@router.get("/executions/{entity_identity}")
async def get_execution(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_RETURN_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return one deterministic ServiceExecution projection from canonical evidence.

    Service execution remains legal-operational evidence only and is not bank,
    payment-provider, invoice, payment, or settlement execution truth.
    """
    return _resource("ServiceExecution", entity_identity, context, collection)


@router.get("/returns/{entity_identity}")
async def get_return_of_service(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_RETURN_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return one deterministic ReturnOfService projection without creating a return.

    A return is not a tax invoice, payment execution, or settlement fact. The
    route performs authenticated read composition only.
    """
    return _resource("ReturnOfService", entity_identity, context, collection)


__all__ = ["VERSION", "get_lifecycle_collection", "router"]


# ARTIFACT: legal_operations_router.py
# VERSION: v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API
# AUTHORITY BOUNDARY: authenticated deterministic read projection only; P1/P2/L8-0 remain canonical owners
# TENANT POSTURE: exact authorized tenant/type/entity history; foreign absence is bounded
# FAIL-CLOSED POSTURE: absent history, corruption, divergence, policy gaps, and outages deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
