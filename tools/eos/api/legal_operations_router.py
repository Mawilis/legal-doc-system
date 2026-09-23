"""Authenticated deterministic read projections for Legal Operations.

TITLE: WILSY OS Legal Operations Read Projection Router
VERSION: v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API
AUTHORITY: Authenticated, tenant-scoped projection of canonical Legal Operations evidence only.
EPITOME: Preserve exact authorized L8-5 entity reads and expose the certified
         L8-5C operational queues through a sheriff-only tenant-scoped read
         route without creating deputy identity, queue, billing, urgency,
         geospatial, client, AI, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_operations_router.py
COLLABORATION / OWNERSHIP: Python EOS API composition. P1 owns lifecycle truth,
                            P2 owns immutable persistence/history hydration,
                            L8-0 owns deterministic current-state projection,
                            L8-5 owns entity read-model composition, L8-5C owns
                            sheriff operational queue membership, L8-6B owns
                            principal-to-Deputy identity binding, L8-6C owns
                            deputy personal active-work membership, and tenant
                            authorization owns access authority.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API
           adds the DEPUTY-only /deputy/active-work route. The route derives
           principal identity from the authenticated context, resolves the
           immutable L8-6B binding, and exposes only that bound deputy's
           ALLOCATED/ATTEMPTED current ServiceAttempt work. Missing binding,
           corrupt evidence, or projection failure denies without falling back
           to the sheriff tenant-wide queue.
           2026-09-23 v1.3.0-L8-6A-SHERIFF-OPERATIONAL-QUEUE-READ-API
           adds the sheriff-only operational-queue read route backed exclusively
           by certified L8-5C queue membership and returns only current canonical
           queue items; DEPUTY receives no tenant-wide queue access and no
           unsupported dashboard truth is synthesized.
           2026-09-23 v1.2.1-L8-5-LEGAL-OPERATIONS-CURRENT-HISTORY-READ-API
           aligns every public route docstring with the current-plus-history
           response contract; runtime behavior, IAM, and authority are unchanged.
           2026-09-23 v1.2.0-L8-5-LEGAL-OPERATIONS-CURRENT-HISTORY-READ-API
           wires authenticated exact reads through the certified L8-5 entity
           read model, preserves the existing current projection in data, and
           adds sanitized immutable history without exposing P2 envelopes or
           creating new IAM vocabulary.
           2026-09-23 v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API replaces
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
TENANT BOUNDARY: Entity reads bind the exact authorized tenant/type/identity;
                 sheriff queues bind the exact authorized sheriff tenant; deputy
                 personal work additionally binds the authenticated principal
                 to one canonical Deputy identity. Foreign evidence is never
                 admitted or disclosed.
AUTHORITY BOUNDARY: Read projection only. Queue visibility grants no receipt,
                    allocation, attempt, service, return, billing, invoice,
                    payment, execution, settlement, or deputy impersonation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement. Legal reads never infer paid or
                              settled truth.
TRANSACTION BOUNDARY: HTTP composition owns no Mongo session or transaction;
                      L8-5/L8-5C/L8-6B/L8-6C use read-only collection semantics.
FAIL-CLOSED DECLARATION: Missing authority, malformed identity, client-policy
                         gaps, absent exact history, P2 corruption/outage,
                         history forks/divergence, queue projection failure,
                         and invalid projections deny.
"""
from __future__ import annotations

import re
from typing import Any, Final

from fastapi import APIRouter, Depends, HTTPException, status

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.legal_operations.domain.deputy_personal_active_work import (
    DeputyPersonalActiveWorkError,
    get_deputy_personal_active_work,
)
from tools.eos.legal_operations.domain.legal_operations_operational_queues import (
    LegalOperationsOperationalQueueError,
    get_operational_queues,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsReadModelError,
    get_entity_read_model,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as DEPUTY_PRINCIPAL_BINDING_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
)


VERSION: Final[str] = "v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CLIENT_ROLE = "tenant_legal_client"


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


def get_deputy_principal_binding_collection() -> Any:
    """Return the configured immutable deputy-principal binding collection.

    The provider creates no binding, membership, role, queue, lifecycle,
    service, billing, payment, execution, or settlement authority. Database
    unavailability fails closed with the same bounded persistence response as
    other Legal Operations read providers.
    """
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        )
    return database.get_collection(DEPUTY_PRINCIPAL_BINDING_COLLECTION)


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
    """Return deterministic current-plus-history truth for one authorized entity.

    Authorization precedes read-model access. L8-5 composes the complete exact
    P2 history with L8-0 deterministic current selection. Exact-scope absence is
    a bounded 404; corrupt, divergent, or otherwise invalid canonical evidence
    is bounded as evidence unavailable. The HTTP projection preserves the
    existing current snapshot in data for compatibility and adds sanitized
    canonical P1 snapshots in history. Raw P2 envelopes are never exposed.

    This method is read-only and owns no lifecycle, transaction, billing,
    payment, financial execution, or settlement authority.
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

    try:
        model = get_entity_read_model(
            tenant_id=context.tenant_id,
            entity_type=entity_type,
            entity_identity=entity_identity,
            lifecycle_collection=collection,
        )
    except LegalOperationsReadModelError as error:
        if error.code == "L8_5_ENTITY_NOT_FOUND":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LEGAL_OPERATION_NOT_FOUND",
            ) from error
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
        "tenant_id": model.tenant_id,
        "entity_type": model.entity_type,
        "entity_identity": model.entity_identity,
        "visibility": "AUDIT_VISIBLE",
        "data": _project(model.current),
        "history": [_project(value) for value in model.history],
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
_QUEUE_READ = RequireTenantAuthorization(
    "legal_operations:queue:read",
    "legal_queue_read",
)
_DEPUTY_QUEUE_READ = RequireTenantAuthorization(
    "legal_operations:deputy_queue:read",
    "legal_deputy_queue_read",
)

router = APIRouter(prefix="/legal-operations", tags=["Legal Operations"])


@router.get("/operational-queues")
async def get_operational_queue_projection(
    context: TenantAuthorizationContext = Depends(_QUEUE_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return certified sheriff operational queues for the authorized tenant.

    Authentication and conjunctive tenant authorization occur before L8-5C
    reads. Membership is derived only from canonical current lifecycle state:
    REGISTERED ProcessDocument -> office_receipt, RECEIVED ProcessDocument ->
    deputy_assignment, and ALLOCATED/ATTEMPTED ServiceAttempt ->
    active_attempts. The response projects current P1 values only.

    This route deliberately exposes no personal deputy queue because no
    principal-to-deputy identity binding is canonical yet. It also exposes no
    urgency, distance, return-generation, billing-readiness, invoice, payment,
    settlement, AI ranking, or financial truth.
    """
    try:
        queues = get_operational_queues(
            tenant_id=context.tenant_id,
            lifecycle_collection=collection,
        )
    except LegalOperationsOperationalQueueError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_QUEUE_EVIDENCE_UNAVAILABLE",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        ) from error

    return {
        "tenant_id": queues.tenant_id,
        "visibility": "SHERIFF_OPERATIONAL_QUEUE",
        "office_receipt": [_project(model.current) for model in queues.office_receipt],
        "deputy_assignment": [
            _project(model.current) for model in queues.deputy_assignment
        ],
        "active_attempts": [_project(model.current) for model in queues.active_attempts],
    }


@router.get("/deputy/active-work")
async def get_deputy_personal_active_work_projection(
    context: TenantAuthorizationContext = Depends(_DEPUTY_QUEUE_READ),
    lifecycle_collection: Any = Depends(get_lifecycle_collection),
    binding_collection: Any = Depends(get_deputy_principal_binding_collection),
) -> dict[str, Any]:
    """Return the authenticated deputy's binding-scoped active service work.

    Current IAM must authorize the exact legal_deputy_queue_read operation
    before either collection is accessed. The immutable L8-6B binding is then
    resolved by the authenticated principal identity and exact authorized
    tenant. L8-6C returns only current ALLOCATED/ATTEMPTED ServiceAttempt
    models whose canonical deputy_id equals the bound deputy identity.

    The route accepts no deputy_id, principal_id, tenant_id, urgency, location,
    billing, client, AI, service-outcome, return, payment, or settlement input.
    The response is read-only and grants no lifecycle command authority.
    """
    try:
        personal = get_deputy_personal_active_work(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            binding_collection=binding_collection,
            lifecycle_collection=lifecycle_collection,
        )
    except DeputyPersonalActiveWorkError as error:
        if error.code == "L8_6C_BINDING_REQUIRED":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="DEPUTY_IDENTITY_BINDING_REQUIRED",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_DEPUTY_QUEUE_EVIDENCE_UNAVAILABLE",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        ) from error

    return {
        "tenant_id": personal.tenant_id,
        "visibility": "DEPUTY_PERSONAL_ACTIVE_WORK",
        "deputy_id": personal.deputy_id,
        "active_attempts": [
            _project(model.current) for model in personal.active_attempts
        ],
    }


@router.get("/instructions/{entity_identity}")
async def get_instruction(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_INSTRUCTION_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return deterministic current-plus-history LegalInstruction truth.

    The route is read-only, applies the existing instruction-read permission,
    preserves current truth in data, exposes sanitized immutable P1 history,
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
    """Return current-plus-history ServiceAttempt truth without implying service.

    Attempt history remains distinct from certified service evidence and the
    route owns no lifecycle mutation, transaction, billing, financial execution,
    or settlement authority.
    """
    return _resource("ServiceAttempt", entity_identity, context, collection)


@router.get("/executions/{entity_identity}")
async def get_execution(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_RETURN_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return current-plus-history ServiceExecution canonical projections.

    Service execution history remains legal-operational evidence only and is not
    bank, payment-provider, invoice, payment, or settlement execution truth.
    """
    return _resource("ServiceExecution", entity_identity, context, collection)


@router.get("/returns/{entity_identity}")
async def get_return_of_service(
    entity_identity: str,
    context: TenantAuthorizationContext = Depends(_RETURN_READ),
    collection: Any = Depends(get_lifecycle_collection),
) -> dict[str, Any]:
    """Return current-plus-history ReturnOfService projections without mutation.

    A return or its immutable history is not a tax invoice, payment execution,
    or settlement fact. The route performs authenticated read composition only.
    """
    return _resource("ReturnOfService", entity_identity, context, collection)


__all__ = [
    "VERSION",
    "get_deputy_principal_binding_collection",
    "get_lifecycle_collection",
    "router",
]


# ARTIFACT: legal_operations_router.py
# VERSION: v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API
# AUTHORITY BOUNDARY: authenticated entity, sheriff queue, and bound-deputy personal active-work projections only; P1/P2/L8-0/L8-5/L8-5C/L8-6B/L8-6C retain canonical ownership
# TENANT POSTURE: exact authorized entity/sheriff tenant scope plus authenticated-principal-to-Deputy personal work binding; foreign evidence is bounded
# FAIL-CLOSED POSTURE: absent history, corruption, divergence, policy gaps, queue failures, and outages deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
