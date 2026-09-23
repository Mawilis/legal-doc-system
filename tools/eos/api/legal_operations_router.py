"""Authenticated deterministic read projections for Legal Operations.

TITLE: WILSY OS Legal Operations Read Projection Router
VERSION: v1.6.0-L8-7D6-CLIENT-MATTER-READ-API
AUTHORITY: Authenticated, tenant-scoped projection of canonical Legal Operations evidence only.
EPITOME: Preserve exact authorized internal/sheriff/deputy reads while adding
         one dedicated LEGAL_CLIENT /client/matters route that owns a snapshot
         transaction and returns only the D5 explicitly-visible sanitized
         CaseMatter projection, without opening internal entity reads or
         creating lifecycle, service, return, billing, AI, payment or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/legal_operations_router.py
COLLABORATION / OWNERSHIP: Python EOS API composition. P1 owns lifecycle truth,
                            P2 owns immutable persistence/history hydration,
                            L8-0 owns deterministic current-state projection,
                            L8-5 owns entity read-model composition, L8-5C owns
                            sheriff operational queue membership, L8-6B owns
                            principal-to-Deputy identity binding, L8-6C owns
                            deputy personal active-work membership, L8-6D
                            composes exact P2 locators with P5M state capability,
                            L8-7D5 owns sanitized client matter projection, and
                            tenant authorization owns access authority.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.6.0-L8-7D6-CLIENT-MATTER-READ-API adds GET /client/matters under the exact
           legal_operations:client_matter:read / legal_client_matter_read
           authorization dependency. The route derives tenant/principal only
           from authenticated context, owns one Mongo snapshot transaction,
           re-authorizes D5 current IAM inside that transaction, and returns
           the D5 safe payload unchanged. Existing client denial on internal
           instruction/attempt/execution/return projections remains intact.
           No caller-supplied matter/client/role/state/visibility authority and
           no lifecycle, service, return, billing, AI or financial mutation is added.
2026-09-23 v1.5.0-L8-6D-DEPUTY-FIELD-CAPABILITY-READ-API
           adds the DEPUTY-only /deputy/field-capabilities route backed by the
           L8-6D personal capability composer. The route derives tenant and
           principal scope only from authenticated authorization context,
           returns exact current P2 snapshot locators plus state-valid command
           kinds, and grants no mutation authority; existing transition/outcome
           routes independently re-authorize their command permissions.
           Also removes the obsolete sheriff-route statement that canonical
           principal-to-Deputy binding did not yet exist.
           2026-09-23 v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API
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
                 personal work and field capabilities additionally bind the
                 authenticated principal to one canonical Deputy identity and
                 exact current snapshot locators. Foreign evidence is never
                 admitted or disclosed.
AUTHORITY BOUNDARY: Read projection only. Queue/capability visibility grants no
                    receipt, allocation, attempt mutation, service, return,
                    billing, invoice, payment, execution, settlement, or deputy
                    impersonation. State capability is not IAM authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement. Legal reads never infer paid or
                              settled truth.
TRANSACTION BOUNDARY: Existing internal/sheriff/deputy reads retain read-only
                      collection semantics. The D6 client matter route alone
                      owns one read-only Mongo snapshot transaction spanning D5
                      current IAM, visibility and bound-matter reads; it commits
                      on success and aborts on failure. Command transactions remain separate.
FAIL-CLOSED DECLARATION: Missing authority, malformed identity, internal
                         client-policy violations, snapshot/session failure,
                         D5 IAM/visibility/bound-matter failure, absent exact
                         history/locator, P2 corruption/outage, divergence,
                         queue/capability failure and invalid projections deny.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Final, TypeVar

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.read_concern import ReadConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
    get_role_assignment_repository,
)
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.legal_operations.domain.deputy_personal_active_work import (
    DeputyPersonalActiveWorkError,
    get_deputy_personal_active_work,
    get_deputy_personal_field_capabilities,
)
from tools.eos.legal_operations.domain.legal_client_matter_projection import (
    LegalClientMatterProjectionError,
    get_legal_client_matter_projection,
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
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    COLLECTION as CLIENT_VISIBILITY_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
)


VERSION: Final[str] = "v1.6.0-L8-7D6-CLIENT-MATTER-READ-API"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CLIENT_ROLE = "tenant_legal_client"
_T = TypeVar("_T")


def _db_handles() -> tuple[Any, Any]:
    """Resolve configured kernel client/database only when the client route runs."""
    from tools.eos.kernel.db import get_client, get_database

    return get_client(), get_database()


def _client_projection_transaction(callback: Callable[[Any, Any], _T]) -> _T:
    """Run one client projection in one API-owned read-only snapshot transaction.

    D5 requires one active caller-owned session across current IAM, visibility,
    and bound-matter reads. This API boundary owns that session lifecycle only:
    it starts a snapshot transaction, commits a successful read, aborts on any
    projection failure, performs no retry, and creates no durable authority.
    """
    client, database = _db_handles()
    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        )
    try:
        with client.start_session() as session:
            session.start_transaction(read_concern=ReadConcern("snapshot"))
            try:
                result = callback(session, database)
                session.commit_transaction()
                return result
            except Exception:
                if bool(getattr(session, "in_transaction", False)):
                    session.abort_transaction()
                raise
    except (HTTPException, LegalClientMatterProjectionError):
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        ) from error


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
_CLIENT_MATTER_READ = RequireTenantAuthorization(
    "legal_operations:client_matter:read",
    "legal_client_matter_read",
)

router = APIRouter(prefix="/legal-operations", tags=["Legal Operations"])


@router.get("/client/matters")
async def get_legal_client_matter_projection_route(
    context: TenantAuthorizationContext = Depends(_CLIENT_MATTER_READ),
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    role_assignment_repository: Any = Depends(get_role_assignment_repository),
) -> dict[str, object]:
    """Return the authenticated LEGAL_CLIENT's explicitly visible matters only.

    HTTP admission first requires the exact D4 permission/operation pair. The
    route then owns one read-only snapshot transaction and D5 independently
    re-evaluates current IAM inside that snapshot before reading ACTIVE L8-7B
    visibility and exact current P1 CaseMatter evidence.

    Tenant and principal scope come exclusively from the authorized context.
    The request accepts no client identifier, matter identifier, role, state,
    visibility, evidence, service, return, invoice, payment, AI or settlement
    claim. Existing internal entity routes remain separately denied to the
    tenant_legal_client business role.

    D5's already-sanitized schema is returned unchanged. IAM revocation races
    fail closed as 403; visibility/matter/snapshot/persistence failures are
    bounded as 503. This route mutates no legal or financial truth.
    """

    def run(session: Any, database: Any) -> dict[str, object]:
        result = get_legal_client_matter_projection(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            visibility_collection=database.get_collection(
                CLIENT_VISIBILITY_COLLECTION
            ),
            lifecycle_collection=database.get_collection(LIFECYCLE_COLLECTION),
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=role_assignment_repository,
            role_assignment_repository=role_assignment_repository,
            session=session,
        )
        return result.to_dict()

    try:
        return _client_projection_transaction(run)
    except LegalClientMatterProjectionError as error:
        if error.code.startswith("L8_7D5_CLIENT_AUTHORIZATION_DENIED_"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="LEGAL_CLIENT_MATTER_READ_DENIED",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_CLIENT_PROJECTION_UNAVAILABLE",
        ) from error


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

    This sheriff route deliberately exposes no deputy-personal projection;
    those reads use the distinct binding-scoped deputy routes below. It also
    exposes no urgency, distance, return-generation, billing-readiness, invoice,
    payment, settlement, AI ranking, or financial truth.
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


@router.get("/deputy/field-capabilities")
async def get_deputy_field_capability_projection(
    context: TenantAuthorizationContext = Depends(_DEPUTY_QUEUE_READ),
    lifecycle_collection: Any = Depends(get_lifecycle_collection),
    binding_collection: Any = Depends(get_deputy_principal_binding_collection),
) -> dict[str, Any]:
    """Return state-valid field command descriptors for the authenticated deputy.

    Current IAM first proves legal_deputy_queue_read for the exact tenant and
    principal. L8-6D then reuses L8-6C bound personal active work, resolves the
    exact persisted P2 evidence identity for each current ALLOCATED/ATTEMPTED
    ServiceAttempt, and projects only its state-valid next command kinds.

    The response capability is not mutation authorization. Existing attempt
    transition/outcome command routes independently require their own current
    IAM permissions and validate supplied field observations. This route accepts
    no tenant_id, principal_id, deputy_id, evidence locator, lifecycle state,
    service outcome, billing, payment, settlement, location, or AI input.
    """
    try:
        personal = get_deputy_personal_field_capabilities(
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
            detail="LEGAL_OPERATIONS_DEPUTY_FIELD_CAPABILITY_UNAVAILABLE",
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        ) from error

    return {
        "tenant_id": personal.tenant_id,
        "visibility": "DEPUTY_FIELD_COMMAND_CAPABILITIES",
        "deputy_id": personal.deputy_id,
        "capabilities": [value.to_dict() for value in personal.capabilities],
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
    "get_legal_client_matter_projection_route",
    "router",
]


# ARTIFACT: legal_operations_router.py
# VERSION: v1.6.0-L8-7D6-CLIENT-MATTER-READ-API
# AUTHORITY BOUNDARY: authenticated internal/sheriff/deputy reads plus explicitly-visible LEGAL_CLIENT matter projection only; mutation IAM/commands remain separate
# TENANT POSTURE: exact authorized internal/sheriff/deputy scope plus D6 tenant/principal-bound client snapshot projection; foreign evidence is bounded
# FAIL-CLOSED POSTURE: internal policy gaps, denied client IAM, snapshot failure, visibility/matter corruption, absent history/locator, divergence and outages deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
