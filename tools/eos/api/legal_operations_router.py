"""Authenticated deterministic read projections for Legal Operations.

TITLE: WILSY OS Legal Operations Read Projection Router
VERSION: v1.17.0-G68-P2-PRACTITIONER-CONFIDENTIALITY-CONTAINMENT
AUTHORITY: Authenticated, tenant-scoped projection of canonical Legal Operations evidence only.
EPITOME: Preserve exact authorized internal/sheriff/deputy/client reads while
         exposing one snapshot-consistent legal-practice workspace projection and
         a bounded conflict-screening review queue. Screening presentation remains
         read-only, tenant-scoped and data-minimized; it never creates lifecycle,
         review, clearance, billing, payment, AI, execution or settlement truth.
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
                            L8-8E owns immutable conflict-screening persistence;
                            tenant authorization owns access authority.
CERTIFICATION / UPDATE DATE: 2026-10-22
CHANGELOG: 2026-10-24 v1.17.0-G68-P2-PRACTITIONER-CONFIDENTIALITY-CONTAINMENT fails closed before any workspace collection access while certified positive practitioner confidentiality authority remains unavailable; returns a distinct non-disclosing 503 and grants no access.
CHANGELOG: 2026-10-22 v1.16.0-R67-ENTERPRISE-DAILY-WORK-EXECUTION-READ adds
           one deterministic, deduplicated and urgency-ordered daily execution
           queue to the existing authenticated productive-work response. Queue
           rows retain assignment/supervision visibility provenance and a
           SHA3-512 projection fingerprint while explicitly granting no matter
           access, assignment mutation, completion or execution authority.
           2026-10-19 v1.15.0-P7-COMPLETION-AWARE-PRODUCTIVE-WORK-HTTP composes canonical immutable
           completion history into the authenticated productive-work
           read. Completed work leaves active lists within the same
           tenant-scoped snapshot. No new permissions, collections,
           commands, IAM, workflow or financial authority are added.
           2026-10-19 v1.14.0-LEGAL-TEMPORAL-OPERATIONS-OBSERVABILITY adds one post-authorization terminal structured observation for each admitted temporal read, generated server correlation, bounded latency classification, pseudonymous tenant/principal references, and committed/aborted/unavailable transaction outcome reporting. Telemetry failure remains quiet and cannot change canonical HTTP or transaction outcomes; no evidence content, permission, persistence, workflow, AI or financial authority is added. P5-R4 aligns the sovereign end seal after real-Mongo commit/abort ordering proof.
           2026-10-18 v1.13.0-LEGAL-TEMPORAL-OPERATIONS-HTTP records authenticated GET /temporal-operations under the existing productive-work read authority. One API-owned snapshot transaction composes canonical productive-work visibility and canonical Legal Matter Deadline evidence with shared session/snapshot scope. It adds no permission, collection, index, write route, deadline arithmetic, lifecycle mutation, IAM or financial authority.
           2026-10-18 v1.12.0-LEGAL-SPECIALIST-WORKFLOW-HTTP adds authenticated GET /specialist-workflow under the existing productive-work read authority. One existing API-owned snapshot transaction composes canonical productive-work visibility first, then enriches only visible rows through LegalSpecialistWorkflowReadService. It adds no permission, collection, index, mutable current pointer, write route, workflow mutation, IAM or financial authority.
           2026-10-16 v1.11.0-LEGAL-COMMERCIAL-CONTEXT-HTTP adds authenticated GET /commercial-context using the already-canonical subscription:read permission. The route derives tenant scope only from current Python membership/permission authority, owns one read-only Mongo snapshot transaction, composes exact current Legal product entitlement with canonical subscription evidence, and exposes bounded commercial context only to commercial-read principals. It adds no Legal-role grant, subscription mutation, plan mutation, IAM assignment, payment, execution or settlement authority.
           2026-10-10 v1.10.0-D22B5-R21-LEGAL-PRODUCT-AVAILABILITY-CONJUNCTION adds the canonical D22B5 Legal Operations product-availability read as the first durable operation inside the existing workspace snapshot transaction. Unavailability denies with one non-disclosing 403; product-authority failure denies with a distinct 503; the four D15 authorities, workspace evidence reads and response contract remain unchanged.
           2026-09-25 v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API adds an authenticated exact-tenant GET /conflict-screenings review queue backed by the canonical immutable screening registry. It exposes only screening_id, source_case_matter_id, REVIEW_REQUIRED status and screened_at in a bounded deterministic projection; no review state, evidence, party identity, clearance, IAM or financial authority is created.
           2026-09-24 v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API adds canonical CaseMatter rows and matter counts to the existing practice workspace so a durably registered matter is directly discoverable after intake. CaseMatter is read from the same exact-tenant snapshot as the existing lifecycle families, exposes only case_matter_id, matter_reference, opened_at, state and opaque evidence_identity, and creates no new lifecycle, IAM, client, billing, payment, AI or settlement authority.
           2026-09-23 v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API adds GET /workspace for the exact current
           legal-practice roles tenant_legal_partner, tenant_legal_attorney,
           tenant_legal_paralegal and tenant_legal_secretary. Admission requires
           all four existing instruction/allocation/attempt/return read
           permission-operation pairs for the same tenant/principal/business
           role. One API-owned snapshot transaction enumerates deterministic
           L8-5 current models for LegalInstruction, ProcessDocument,
           ServiceAttempt, ServiceExecution and ReturnOfService, exposes only a
           bounded field whitelist plus opaque exact-snapshot evidence locators,
           and returns deterministic lifecycle counts. It creates no new IAM,
           matter, service, billing, invoice, AI, payment or settlement truth.
           2026-09-23 v1.6.0-L8-7D6-CLIENT-MATTER-READ-API adds GET /client/matters under the exact
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
                 authenticated principal to one canonical Deputy identity.
                 D15 workspace admission requires four current read authorities
                 for one exact tenant/principal/published practice role plus an
                 exact current ACTIVE Legal Operations product entitlement; all
                 workspace rows remain that tenant's current canonical evidence.
                 Foreign evidence is never admitted or disclosed.
AUTHORITY BOUNDARY: Read projection only. D15 workspace visibility is a
                    conjunction of existing instruction/allocation/attempt/
                    return read authority and D22B5 tenant product availability;
                    neither availability nor visibility grants mutation authority.
                    Queue/capability visibility grants no receipt, allocation,
                    attempt mutation, service, return, billing, invoice, payment,
                    execution, settlement, or deputy impersonation. State
                    capability is not IAM authorization.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement. Legal reads never infer paid or
                              settled truth.
TRANSACTION BOUNDARY: Existing exact internal/sheriff/deputy reads retain
                      read-only collection semantics. The D6 client-matter route
                      and D15 legal-practice workspace each own one read-only
                      Mongo snapshot transaction for their multi-read projection;
                      D22B5 product availability and all lifecycle reads share
                      the workspace transaction and exact session; both commit
                      on success and abort on failure. Command transactions
                      remain separate.
FAIL-CLOSED DECLARATION: Missing or mismatched practice authority, unavailable
                         Legal product, product-authority failure, malformed
                         identity, internal client-policy violations, snapshot/
                         session failure, D5 IAM/visibility/bound-matter failure,
                         absent exact history/locator, P2 corruption/outage,
                         divergence, queue/capability failure and invalid
                         workspace/client/internal projections deny.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import uuid
from datetime import UTC, datetime
from typing import Any, Callable, Final, TypeVar

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pymongo.read_concern import ReadConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
    get_role_assignment_repository,
)
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.authorization import RequirePermission
from tools.eos.auth.identity import SovereignIdentity
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
    list_entity_read_models,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as DEPUTY_PRINCIPAL_BINDING_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    COLLECTION as CLIENT_VISIBILITY_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)

from tools.eos.legal_operations.registry.legal_work_item_registry import (
    COLLECTION_NAME as LEGAL_WORK_ITEM_COLLECTION,
    LegalWorkItemRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_instance_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_INSTANCE_COLLECTION,
    LegalMatterWorkflowInstanceRegistry,
)
from tools.eos.legal_operations.registry.legal_matter_workflow_transition_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_TRANSITION_COLLECTION,
    LegalMatterWorkflowTransitionRegistry,
)
from tools.eos.legal_operations.registry.legal_transition_work_materialization_receipt_registry import (
    COLLECTION_NAME as LEGAL_WORK_MATERIALIZATION_RECEIPT_COLLECTION,
    LegalTransitionWorkMaterializationReceiptRegistry,
)
from tools.eos.legal_operations.registry.legal_work_completion_event_registry import (
    COLLECTION_NAME as LEGAL_WORK_COMPLETION_EVENT_COLLECTION,
    LegalWorkCompletionEventRegistry,
)
from tools.eos.legal_operations.registry.legal_work_dependency_edge_registry import (
    COLLECTION_NAME as LEGAL_WORK_DEPENDENCY_EDGE_COLLECTION,
    LegalWorkDependencyEdgeRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_definition_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_DEFINITION_COLLECTION,
    LegalWorkflowDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_gate_satisfaction_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_GATE_SATISFACTION_COLLECTION,
    LegalWorkflowGateSatisfactionRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_stage_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_STAGE_COLLECTION,
    LegalWorkflowStageRegistry,
)
from tools.eos.legal_operations.registry.legal_workflow_topology_registry import (
    COLLECTION_NAME as LEGAL_WORKFLOW_TOPOLOGY_COLLECTION,
    LegalWorkflowTopologyRegistry,
)
from tools.eos.legal_operations.registry.legal_work_assignment_registry import (
    COLLECTION_NAME as LEGAL_WORK_ASSIGNMENT_COLLECTION,
    LegalWorkAssignmentRegistry,
)
from tools.eos.legal_operations.registry.legal_work_supervision_binding_registry import (
    COLLECTION_NAME as LEGAL_WORK_SUPERVISION_COLLECTION,
    LegalWorkSupervisionBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operating_role_definition_registry import (
    COLLECTION_NAME as LEGAL_OPERATING_ROLE_DEFINITION_COLLECTION,
    LegalOperatingRoleDefinitionRegistry,
)
from tools.eos.legal_operations.registry.legal_operating_role_capability_binding_registry import (
    COLLECTION_NAME as LEGAL_OPERATING_ROLE_CAPABILITY_COLLECTION,
    LegalOperatingRoleCapabilityBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operating_role_scope_binding_registry import (
    COLLECTION_NAME as LEGAL_OPERATING_ROLE_SCOPE_COLLECTION,
    LegalOperatingRoleScopeBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_principal_operating_role_binding_registry import (
    COLLECTION_NAME as LEGAL_PRINCIPAL_OPERATING_ROLE_COLLECTION,
    LegalPrincipalOperatingRoleBindingRegistry,
)
from tools.eos.legal_operations.service.legal_productive_work_operating_context_hydrator import (
    LegalProductiveWorkOperatingContextHydrator,
    LegalProductiveWorkOperatingContextHydratorError,
)
from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadService,
    LegalProductiveWorkReadServiceError,
)
from tools.eos.legal_operations.service.legal_specialist_workflow_read_service import (
    LegalSpecialistWorkflowReadService,
    LegalSpecialistWorkflowReadServiceError,
)
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    COLLECTION as LEGAL_CONFLICT_SCREENING_COLLECTION,
    MAX_REVIEW_QUEUE,
    LegalConflictScreeningRegistry,
    LegalConflictScreeningRegistryError,
)
from tools.eos.saas.entitlement.legal_product_availability_projection import (
    LegalProductAvailabilityProjectionError,
    resolve_legal_product_availability,
)
from tools.eos.saas.entitlement.legal_commercial_context_projection import (
    LegalCommercialContextProjection,
    LegalCommercialContextProjectionError,
    resolve_legal_commercial_context,
)
import tools.eos.saas.billing.subscription_registry as subscription_registry_module
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as TENANT_PRODUCT_ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as TENANT_PRODUCT_ENTITLEMENT_HISTORY_COLLECTION,
)


VERSION: Final[str] = "v1.17.0-G68-P2-PRACTITIONER-CONFIDENTIALITY-CONTAINMENT"
logger = logging.getLogger("WilsyOS.API.LegalOperationsRouter")
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_CLIENT_ROLE = "tenant_legal_client"
_LEGAL_PRACTICE_ROLES: Final[frozenset[str]] = frozenset(
    {
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
    }
)
_WORKSPACE_SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V2"
_WORKSPACE_VERSION: Final[str] = "v1.8.0-L8-7D15-FIRST-CLASS-MATTER-WORKSPACE-API"
_WORKSPACE_VISIBILITY: Final[str] = "LEGAL_PRACTICE_WORKSPACE"
_SCREENING_SCHEMA: Final[str] = "WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1"
_SCREENING_VERSION: Final[str] = "v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API"
_SCREENING_VISIBILITY: Final[str] = "LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE"
_T = TypeVar("_T")

_COMMERCIAL_CONTEXT_SCHEMA: Final[str] = (
    "WILSY-LEGAL-OPERATIONS-COMMERCIAL-CONTEXT/V1"
)
_COMMERCIAL_CONTEXT_HTTP_VERSION: Final[str] = (
    "v1.0.0-LEGAL-COMMERCIAL-CONTEXT-HTTP"
)
_COMMERCIAL_CONTEXT_VISIBILITY: Final[str] = (
    "LEGAL_COMMERCIAL_CONTEXT_SUBSCRIPTION_READ"
)
_SUBSCRIPTION_READ_AUTHORITY = RequirePermission(
    "subscription:read"
)


def _db_handles() -> tuple[Any, Any]:
    """Resolve configured kernel client/database only when the client route runs."""
    from tools.eos.kernel.db import get_client, get_database

    return get_client(), get_database()


def _commercial_tenant_id(
    identity: SovereignIdentity,
) -> str:
    """Return only the tenant admitted by current subscription-read authority.

    ``RequirePermission("subscription:read")`` performs authentication,
    ACTIVE membership and current permission admission before this helper runs.
    Raw request headers, browser plan selectors and Legal role labels are not
    tenant or commercial authority.
    """
    tenant_id = identity.tenant_id
    if (
        not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_COMMERCIAL_AUTHORITY_UNAVAILABLE",
        )
    return tenant_id


def _commercial_projection_transaction(
    callback: Callable[[Any, Any], _T],
) -> _T:
    """Run commercial projection inside one API-owned snapshot transaction.

    The router owns session lifecycle only. It performs no write, retry,
    subscription mutation, entitlement mutation, payment execution or
    settlement operation. The exact session is propagated through subscription
    and product-entitlement reads.
    """
    client, database = _db_handles()
    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_COMMERCIAL_CONTEXT_UNAVAILABLE",
        )

    try:
        with client.start_session() as session:
            session.start_transaction(
                read_concern=ReadConcern("snapshot")
            )
            try:
                result = callback(
                    session,
                    database,
                )
                session.commit_transaction()
                return result
            except Exception:
                if bool(
                    getattr(
                        session,
                        "in_transaction",
                        False,
                    )
                ):
                    session.abort_transaction()
                raise
    except (
        HTTPException,
        LegalCommercialContextProjectionError,
    ):
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_COMMERCIAL_CONTEXT_UNAVAILABLE",
        ) from error


def _commercial_context_payload(
    projection: LegalCommercialContextProjection,
) -> dict[str, object]:
    """Serialize only bounded commercial evidence for authorized readers.

    Amounts are descriptive subscription evidence, never invoice, amount-due,
    collection, payment execution or settlement truth.
    """
    return {
        "schema": _COMMERCIAL_CONTEXT_SCHEMA,
        "version": _COMMERCIAL_CONTEXT_HTTP_VERSION,
        "tenant_id": projection.tenant_id,
        "visibility": _COMMERCIAL_CONTEXT_VISIBILITY,
        "product": {
            "product_id": projection.product_id.value,
            "workspace_key": projection.workspace_key,
            "available": projection.product_available,
            "entitlement_state": (
                projection.entitlement_state.value
                if projection.entitlement_state is not None
                else None
            ),
        },
        "subscription": {
            "subscription_id": projection.subscription_id,
            "status": (
                projection.subscription_status.value
                if projection.subscription_status is not None
                else None
            ),
            "current_period_end": (
                projection.current_period_end.isoformat()
                if projection.current_period_end is not None
                else None
            ),
        },
        "plan": {
            "plan_id": projection.plan_id,
            "tier": (
                projection.plan_tier.value
                if projection.plan_tier is not None
                else None
            ),
            "name": projection.plan_name,
            "features": list(
                projection.plan_features
            ),
            "catalogue_version":
                projection.plan_catalogue_version,
        },
        "commercial": {
            "amount": projection.amount,
            "currency": projection.currency,
            "billing_frequency": (
                projection.billing_frequency.value
                if projection.billing_frequency is not None
                else None
            ),
            "monthly_equivalent_amount":
                projection.monthly_equivalent_amount,
            "financial_execution_authority": False,
        },
    }


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


def _workspace_projection_transaction(callback: Callable[[Any, Any], _T]) -> _T:
    """Run one legal-practice workspace read in one API-owned snapshot.

    The endpoint owns only session lifecycle. It never retries, mutates durable
    evidence, or weakens the four independent current-authorization checks.
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
    except (HTTPException, LegalOperationsReadModelError):
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        ) from error


def _workspace_context(
    *contexts: TenantAuthorizationContext,
) -> TenantAuthorizationContext:
    """Require one exact legal-practice principal/tenant/business-role scope."""
    if not contexts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="LEGAL_OPERATIONS_WORKSPACE_DENIED",
        )
    first = contexts[0]
    principal_id = first.identity.identity_id
    role = first.decision.business_role
    if role not in _LEGAL_PRACTICE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="LEGAL_OPERATIONS_WORKSPACE_DENIED",
        )
    for context in contexts[1:]:
        if (
            context.tenant_id != first.tenant_id
            or context.identity.identity_id != principal_id
            or context.decision.business_role != role
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="LEGAL_OPERATIONS_WORKSPACE_SCOPE_MISMATCH",
            )
    return first


_WORKSPACE_FIELDS: Final[dict[str, tuple[str, ...]]] = {
    "CaseMatter": (
        "case_matter_id",
        "matter_reference",
        "opened_at",
        "state",
    ),
    "LegalInstruction": (
        "instruction_id",
        "case_matter_id",
        "document_id",
        "registered_at",
        "state",
    ),
    "ProcessDocument": (
        "document_id",
        "case_matter_id",
        "document_type",
        "registered_at",
        "state",
    ),
    "ServiceAttempt": (
        "attempt_id",
        "instruction_id",
        "document_id",
        "deputy_id",
        "allocated_at",
        "state",
    ),
    "ServiceExecution": (
        "service_execution_id",
        "attempt_id",
        "instruction_id",
        "document_id",
        "outcome",
        "executed_at",
    ),
    "ReturnOfService": (
        "return_id",
        "instruction_id",
        "document_id",
        "attempt_id",
        "service_execution_id",
        "service_outcome",
        "generated_at",
        "state",
    ),
}


def _workspace_rows(
    *,
    tenant_id: str,
    entity_type: str,
    collection: Any,
    session: Any,
) -> list[dict[str, Any]]:
    """Project deterministic current rows plus opaque exact-snapshot locators."""
    fields = _WORKSPACE_FIELDS[entity_type]
    models = list_entity_read_models(
        tenant_id=tenant_id,
        entity_type=entity_type,
        lifecycle_collection=collection,
        session=session,
    )
    rows: list[dict[str, Any]] = []
    for model in models:
        payload = _project(model.current)
        row = {field: payload[field] for field in fields if field in payload}
        if set(row) != set(fields):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LEGAL_OPERATIONS_WORKSPACE_PROJECTION_INVALID",
            )
        row["evidence_identity"] = (
            LegalOperationsLifecycleRegistry.get_snapshot_evidence_identity(
                model.current,
                collection,
                session=session,
            )
        )
        rows.append(row)
    return rows



def _require_workspace_disclosure_clearance(
    *,
    matters: list[dict[str, Any]],
    instructions: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    executions: list[dict[str, Any]],
    returns: list[dict[str, Any]],
) -> None:
    """Deny unverified matter-dependent workspace disclosure.

    This is an interim fail-closed boundary, NOT a positive wall grant.
    Remove the restriction only when current transaction-bound
    matter-by-matter admission is independently certified.
    """
    if any((
        matters, instructions, documents,
        attempts, executions, returns,
    )):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_WORKSPACE_MATTER_CLEARANCE_UNAVAILABLE",
        )


def _workspace_summary(
    *,
    matters: list[dict[str, Any]],
    instructions: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    executions: list[dict[str, Any]],
    returns: list[dict[str, Any]],
) -> dict[str, int]:
    """Return deterministic counts only; counts create no lifecycle inference."""
    def count(rows: list[dict[str, Any]], field: str, value: str) -> int:
        return sum(1 for row in rows if row.get(field) == value)

    return {
        "matters_total": len(matters),
        "matters_open": count(matters, "state", "OPEN"),
        "matters_closed": count(matters, "state", "CLOSED"),
        "instructions_total": len(instructions),
        "instructions_registered": count(instructions, "state", "REGISTERED"),
        "instructions_accepted": count(instructions, "state", "ACCEPTED"),
        "instructions_closed": count(instructions, "state", "CLOSED"),
        "instructions_cancelled": count(instructions, "state", "CANCELLED"),
        "documents_total": len(documents),
        "documents_registered": count(documents, "state", "REGISTERED"),
        "documents_received": count(documents, "state", "RECEIVED"),
        "documents_allocated": count(
            documents,
            "state",
            "ALLOCATED_TO_DEPUTY",
        ),
        "documents_returned": count(
            documents,
            "state",
            "RETURNED_TO_CLIENT",
        ),
        "attempts_total": len(attempts),
        "attempts_allocated": count(attempts, "state", "ALLOCATED"),
        "attempts_attempted": count(attempts, "state", "ATTEMPTED"),
        "attempts_completed": count(attempts, "state", "COMPLETED"),
        "attempts_not_completed": count(
            attempts,
            "state",
            "NOT_COMPLETED",
        ),
        "attempts_cancelled": count(attempts, "state", "CANCELLED"),
        "executions_total": len(executions),
        "executions_completed": count(executions, "outcome", "COMPLETED"),
        "executions_not_completed": count(
            executions,
            "outcome",
            "NOT_COMPLETED",
        ),
        "returns_total": len(returns),
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


_PRODUCTIVE_WORK_READ = RequireTenantAuthorization(
    "legal_operations:productive_work:read",
    "legal_productive_work_read",
)

_PRODUCTIVE_WORK_HTTP_VERSION: Final[str] = (
    "v1.1.0-R67-ENTERPRISE-DAILY-WORK-EXECUTION-READ-API"
)

_SPECIALIST_WORKFLOW_READ = _PRODUCTIVE_WORK_READ

_SPECIALIST_WORKFLOW_HTTP_VERSION: Final[str] = (
    "v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP"
)



from tools.eos.legal_operations.registry import (
    legal_matter_deadline_registry as _temporal_deadline_registry,
)
from tools.eos.legal_operations.service.legal_temporal_operations_read_service import (
    LegalTemporalOperationsReadService,
    LegalTemporalOperationsReadServiceError,
)
from tools.eos.legal_operations.service.legal_practice_workspace_matter_lineage import MatterLineageError, resolve_workspace_canonical_parents


def _productive_work_service(
    database: Any,
) -> LegalProductiveWorkReadService:
    """Compose existing durable PW-P4/P7B readers for one request database."""

    context_hydrator = LegalProductiveWorkOperatingContextHydrator(
        principal_operating_role_registry=(
            LegalPrincipalOperatingRoleBindingRegistry(
                database.get_collection(
                    LEGAL_PRINCIPAL_OPERATING_ROLE_COLLECTION
                )
            )
        ),
        operating_role_definition_registry=(
            LegalOperatingRoleDefinitionRegistry(
                database.get_collection(
                    LEGAL_OPERATING_ROLE_DEFINITION_COLLECTION
                )
            )
        ),
        operating_role_capability_registry=(
            LegalOperatingRoleCapabilityBindingRegistry(
                database.get_collection(
                    LEGAL_OPERATING_ROLE_CAPABILITY_COLLECTION
                )
            )
        ),
        operating_role_scope_registry=(
            LegalOperatingRoleScopeBindingRegistry(
                database.get_collection(
                    LEGAL_OPERATING_ROLE_SCOPE_COLLECTION
                )
            )
        ),
    )

    return LegalProductiveWorkReadService(
        work_item_registry=LegalWorkItemRegistry(
            database.get_collection(
                LEGAL_WORK_ITEM_COLLECTION
            )
        ),
        assignment_registry=LegalWorkAssignmentRegistry(
            database.get_collection(
                LEGAL_WORK_ASSIGNMENT_COLLECTION
            )
        ),
        supervision_registry=LegalWorkSupervisionBindingRegistry(
            database.get_collection(
                LEGAL_WORK_SUPERVISION_COLLECTION
            )
        ),
        operating_context_hydrator=context_hydrator,
        completion_registry=LegalWorkCompletionEventRegistry(
            database.get_collection(
                LEGAL_WORK_COMPLETION_EVENT_COLLECTION
            )
        ),
    )


def _specialist_workflow_services(
    database: Any,
) -> tuple[
    LegalProductiveWorkReadService,
    LegalSpecialistWorkflowReadService,
]:
    """Compose canonical productive-work and specialist readers for one request.

    Registry objects are request-local facades over the existing canonical
    collections. This factory creates no collection or index and grants no
    authority. The route propagates one caller-owned active snapshot session
    through both services.
    """
    definitions = LegalWorkflowDefinitionRegistry(
        database.get_collection(
            LEGAL_WORKFLOW_DEFINITION_COLLECTION
        )
    )
    topologies = LegalWorkflowTopologyRegistry(
        database.get_collection(
            LEGAL_WORKFLOW_TOPOLOGY_COLLECTION
        ),
        definition_registry=definitions,
    )
    stages = LegalWorkflowStageRegistry(
        database.get_collection(
            LEGAL_WORKFLOW_STAGE_COLLECTION
        ),
        definition_registry=definitions,
        topology_registry=topologies,
    )
    instances = LegalMatterWorkflowInstanceRegistry(
        database.get_collection(
            LEGAL_WORKFLOW_INSTANCE_COLLECTION
        )
    )

    specialist = LegalSpecialistWorkflowReadService(
        work_item_registry=LegalWorkItemRegistry(
            database.get_collection(
                LEGAL_WORK_ITEM_COLLECTION
            )
        ),
        receipt_registry=(
            LegalTransitionWorkMaterializationReceiptRegistry(
                database.get_collection(
                    LEGAL_WORK_MATERIALIZATION_RECEIPT_COLLECTION
                )
            )
        ),
        workflow_instance_registry=instances,
        workflow_transition_registry=(
            LegalMatterWorkflowTransitionRegistry(
                database.get_collection(
                    LEGAL_WORKFLOW_TRANSITION_COLLECTION
                )
            )
        ),
        workflow_stage_registry=stages,
        dependency_registry=LegalWorkDependencyEdgeRegistry(
            database.get_collection(
                LEGAL_WORK_DEPENDENCY_EDGE_COLLECTION
            )
        ),
        completion_registry=LegalWorkCompletionEventRegistry(
            database.get_collection(
                LEGAL_WORK_COMPLETION_EVENT_COLLECTION
            )
        ),
        gate_satisfaction_registry=(
            LegalWorkflowGateSatisfactionRegistry(
                database.get_collection(
                    LEGAL_WORKFLOW_GATE_SATISFACTION_COLLECTION
                ),
                instance_registry=instances,
                topology_registry=topologies,
                stage_registry=stages,
            )
        ),
    )

    return _productive_work_service(database), specialist


def _productive_work_projection_transaction(
    callback: Callable[[Any, Any], _T],
) -> _T:
    """Run productive-work reconstruction in one API-owned snapshot transaction."""

    client, database = _db_handles()

    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        )

    try:
        with client.start_session() as session:
            session.start_transaction(
                read_concern=ReadConcern("snapshot")
            )

            try:
                result = callback(
                    session,
                    database,
                )
                session.commit_transaction()
                return result
            except Exception:
                if bool(
                    getattr(
                        session,
                        "in_transaction",
                        False,
                    )
                ):
                    session.abort_transaction()
                raise
    except (
        HTTPException,
        LegalProductiveWorkReadServiceError,
        LegalProductiveWorkOperatingContextHydratorError,
        LegalSpecialistWorkflowReadServiceError,
    ):
        raise
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE",
        ) from error


def _daily_execution_queue(
    projection: Any,
) -> dict[str, object]:
    """Derive one deterministic non-authorizing daily execution queue.

    Assignment and supervision remain visibility provenance only. The queue
    never decides confidential matter access or command authority. Its ordering
    is operational: overdue, due soon, blocked, scheduled, then unscheduled,
    with due instant and opaque work identity providing deterministic ties.

    Args:
        projection: Existing exact-tenant productive-work projection composed
            inside the API-owned snapshot transaction.

    Returns:
        A bounded derived projection with unique rows and SHA3-512 identity.

    Raises:
        LegalProductiveWorkReadServiceError: If visible lists contain malformed
            or divergent representations of the same work-item identity.
    """
    by_id: dict[str, dict[str, object]] = {}
    visibility: dict[str, set[str]] = {}

    for source, values in (
        ("ASSIGNMENT", projection.assigned_work_items),
        ("SUPERVISION", projection.supervised_work_items),
    ):
        for value in values:
            projected = value.to_dict()
            if not isinstance(projected, dict):
                raise LegalProductiveWorkReadServiceError(
                    "R67_WORK_ITEM_PROJECTION_INVALID"
                )
            work_item_id = projected.get("work_item_id")
            if not isinstance(work_item_id, str) or not work_item_id:
                raise LegalProductiveWorkReadServiceError(
                    "R67_WORK_ITEM_ID_INVALID"
                )
            existing = by_id.get(work_item_id)
            if existing is not None and existing != projected:
                raise LegalProductiveWorkReadServiceError(
                    "R67_WORK_ITEM_PROJECTION_DIVERGENT"
                )
            by_id[work_item_id] = projected
            visibility.setdefault(work_item_id, set()).add(source)

    priority_ids: dict[str, set[str]] = {
        "OVERDUE": set(),
        "DUE_SOON": set(),
    }
    for priority, values in (
        ("OVERDUE", projection.overdue_work_items),
        ("DUE_SOON", projection.due_soon_work_items),
    ):
        for value in values:
            projected = value.to_dict()
            if not isinstance(projected, dict):
                raise LegalProductiveWorkReadServiceError(
                    "R67_PRIORITY_WORK_PROJECTION_INVALID"
                )
            work_item_id = projected.get("work_item_id")
            if not isinstance(work_item_id, str) or not work_item_id:
                raise LegalProductiveWorkReadServiceError(
                    "R67_PRIORITY_WORK_ITEM_ID_INVALID"
                )
            existing = by_id.get(work_item_id)
            if existing is not None and existing != projected:
                raise LegalProductiveWorkReadServiceError(
                    "R67_WORK_ITEM_PROJECTION_DIVERGENT"
                )
            if existing is None:
                by_id[work_item_id] = projected
                visibility[work_item_id] = {"PRODUCTIVE_WORK_PRIORITY"}
            priority_ids[priority].add(work_item_id)

    overdue_ids = priority_ids["OVERDUE"]
    due_soon_ids = priority_ids["DUE_SOON"]

    urgency_order = {
        "OVERDUE": 0,
        "DUE_SOON": 1,
        "BLOCKED": 2,
        "SCHEDULED": 3,
        "UNSCHEDULED": 4,
    }
    rows: list[dict[str, object]] = []
    for work_item_id, value in by_id.items():
        status_value = value.get("status")
        status_token = getattr(status_value, "value", status_value)
        due_at = value.get("due_at")
        if work_item_id in overdue_ids:
            urgency = "OVERDUE"
        elif work_item_id in due_soon_ids:
            urgency = "DUE_SOON"
        elif status_token == "BLOCKED":
            urgency = "BLOCKED"
        elif due_at is not None:
            urgency = "SCHEDULED"
        else:
            urgency = "UNSCHEDULED"

        rows.append(
            {
                "work_item_id": work_item_id,
                "case_matter_id": value.get("case_matter_id"),
                "status": status_token,
                "due_at": due_at,
                "urgency": urgency,
                "visibility_sources": sorted(visibility[work_item_id]),
                "work_evidence_fingerprint": value.get("fingerprint"),
            }
        )

    rows.sort(
        key=lambda row: (
            urgency_order[str(row["urgency"])],
            row["due_at"] is None,
            str(row["due_at"] or ""),
            str(row["work_item_id"]),
        )
    )
    positioned = [
        {"queue_position": index, **row}
        for index, row in enumerate(rows, start=1)
    ]
    semantic = {
        "tenant_id": projection.tenant_id,
        "principal_id": projection.principal_id,
        "as_of": projection.as_of.isoformat(),
        "items": positioned,
    }
    fingerprint = hashlib.sha3_512(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
    ).hexdigest()

    return {
        "fact_classification": "DERIVED_OPERATIONAL_PROJECTION",
        "as_of": projection.as_of.isoformat(),
        "unique_active_count": len(positioned),
        "assignment_supervision_overlap_count": sum(
            1 for sources in visibility.values() if len(sources) == 2
        ),
        "items": positioned,
        "projection_fingerprint": fingerprint,
        "execution_authority": "NOT_EVALUATED",
        "permits_execution": False,
        "permits_assignment_mutation": False,
        "permits_confidential_matter_access": False,
    }


def _productive_work_payload(
    projection: Any,
) -> dict[str, object]:
    """Project only the certified daily-work read model; create no authority."""

    return {
        "schema": projection.schema,
        "version": projection.version,
        "http_version": _PRODUCTIVE_WORK_HTTP_VERSION,
        "workday_summary": {
            "assigned_count": len(projection.assigned_work_items),
            "supervised_count": len(projection.supervised_work_items),
            "overdue_count": len(projection.overdue_work_items),
            "due_soon_count": len(projection.due_soon_work_items),
            "execution_authority": "NOT_EVALUATED",
            "permits_execution": False,
            "permits_confidential_matter_access": False,
        },
        "daily_execution_queue": _daily_execution_queue(projection),
        "tenant_id": projection.tenant_id,
        "principal_id": projection.principal_id,
        "as_of": projection.as_of.isoformat(),
        "operating_contexts": [
            {
                "operating_role_id": value.operating_role_id,
                "operating_role_revision": value.operating_role_revision,
                "display_name": value.display_name,
                "capability_ids": list(
                    value.capability_ids
                ),
                "office_references": list(
                    value.office_references
                ),
                "practice_references": list(
                    value.practice_references
                ),
                "business_unit_references": list(
                    value.business_unit_references
                ),
                "jurisdiction_references": list(
                    value.jurisdiction_references
                ),
            }
            for value in projection.operating_contexts
        ],
        "capability_ids": list(
            projection.capability_ids
        ),
        "assigned_work_items": [
            value.to_dict()
            for value in projection.assigned_work_items
        ],
        "supervised_work_items": [
            value.to_dict()
            for value in projection.supervised_work_items
        ],
        "overdue_work_items": [
            value.to_dict()
            for value in projection.overdue_work_items
        ],
        "due_soon_work_items": [
            value.to_dict()
            for value in projection.due_soon_work_items
        ],
    }


def _specialist_workflow_payload(
    projection: Any,
) -> dict[str, object]:
    """Serialize bounded deterministic workflow explanation only."""
    return {
        "schema": projection.schema,
        "version": projection.version,
        "http_version": _SPECIALIST_WORKFLOW_HTTP_VERSION,
        "tenant_id": projection.tenant_id,
        "principal_id": projection.principal_id,
        "as_of": projection.as_of.isoformat(),
        "rows": [
            {
                "work_item_id": row.work_item_id,
                "case_matter_id": row.case_matter_id,
                "workflow_instance_id": row.workflow_instance_id,
                "workflow_definition_id": row.workflow_definition_id,
                "stage_definition_id": row.stage_definition_id,
                "readiness": row.readiness,
                "blocking_dependency_work_item_ids": list(
                    row.blocking_dependency_work_item_ids
                ),
                "unsatisfied_gate_references": list(
                    row.unsatisfied_gate_references
                ),
                "materialization_transition_id": (
                    row.materialization_transition_id
                ),
                "materialization_receipt_id": (
                    row.materialization_receipt_id
                ),
            }
            for row in projection.rows
        ],
    }


_INSTRUCTION_READ = RequireTenantAuthorization(
    "legal_operations:instruction:read",
    "legal_instruction_read",
)
_ATTEMPT_READ = RequireTenantAuthorization(
    "legal_operations:attempt:read",
    "legal_attempt_read",
)
_ALLOCATION_READ = RequireTenantAuthorization(
    "legal_operations:allocation:read",
    "legal_allocation_read",
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


@router.get("/commercial-context")
async def get_legal_commercial_context_projection(
    identity: SovereignIdentity = Depends(
        _SUBSCRIPTION_READ_AUTHORITY
    ),
) -> dict[str, object]:
    """Return exact tenant Legal product/subscription commercial context.

    Admission reuses the existing canonical ``subscription:read`` authority.
    The authenticated identity's membership-admitted tenant is the only tenant
    selector. Legal role labels, browser state, product selectors, plan
    selectors, subscription identifiers, prices, currencies and billing
    frequencies are not accepted from the request.

    One API-owned Mongo snapshot transaction joins the exact current
    LEGAL_OPERATIONS product entitlement with canonical ACTIVE subscription
    evidence. Entitlement/subscription disagreement fails closed.

    The response is descriptive commercial truth only. It grants no Legal
    lifecycle mutation, business role, IAM assignment, plan/subscription
    mutation, invoice, collection, payment execution or settlement authority.
    Kennel EOS remains exclusive financial execution authority.
    """
    tenant_id = _commercial_tenant_id(
        identity
    )

    def run(
        session: Any,
        database: Any,
    ) -> dict[str, object]:
        projection = resolve_legal_commercial_context(
            tenant_id,
            database.get_collection(
                subscription_registry_module
                .subscriptions_collection.name
            ),
            database.get_collection(
                TENANT_PRODUCT_ENTITLEMENT_HISTORY_COLLECTION
            ),
            database.get_collection(
                TENANT_PRODUCT_ENTITLEMENT_CURRENT_COLLECTION
            ),
            session=session,
        )

        return _commercial_context_payload(
            projection
        )

    try:
        return _commercial_projection_transaction(
            run
        )
    except LegalCommercialContextProjectionError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_COMMERCIAL_CONTEXT_UNAVAILABLE",
        ) from error


@router.get("/productive-work")
async def get_legal_productive_work_projection(
    context: TenantAuthorizationContext = Depends(
        _PRODUCTIVE_WORK_READ
    ),
) -> dict[str, object]:
    """Return the authenticated principal's durable own-tenant productive work.

    Admission is the exact PW-P11A permission/operation conjunction. Tenant and
    principal scope come only from the authenticated TenantAuthorizationContext;
    the route accepts no alternate principal, tenant, role, assignment,
    supervision, workflow, approval, billing, payment, execution or settlement
    authority.

    One API-owned snapshot transaction is propagated unchanged through the
    canonical PW-P4 read service and PW-P7B CX27 operating-context hydrator.
    Operating-role, capability and scope metadata remain descriptive and
    non-authorizing. Sheriff and Deputy specialized queue surfaces are separate.
    """

    def run(
        session: Any,
        database: Any,
    ) -> dict[str, object]:
        projection = _productive_work_service(
            database
        ).project(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            as_of=datetime.now(UTC),
            session=session,
        )

        return _productive_work_payload(
            projection
        )

    try:
        return _productive_work_projection_transaction(
            run
        )
    except (
        LegalProductiveWorkReadServiceError,
        LegalProductiveWorkOperatingContextHydratorError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_PRODUCTIVE_WORK_EVIDENCE_UNAVAILABLE",
        ) from error

_TEMPORAL_OBSERVATION_SCHEMA: Final[str] = (
    "WILSY-LEGAL-TEMPORAL-OPERATIONS-OBSERVATION/V1"
)
_TEMPORAL_OBSERVATION_VERSION: Final[str] = (
    "v1.0.0-P5-A-TEMPORAL-OPERATIONS-OBSERVABILITY"
)


def _new_temporal_correlation_id() -> str:
    """Generate one server-owned correlation identifier for an admitted read."""
    return f"temporal-{uuid.uuid4().hex}"


def _temporal_observation_ref(value: str) -> str:
    """Pseudonymize an already-authorized identifier for diagnostics only."""
    return hashlib.sha3_512(value.encode("utf-8")).hexdigest()


def _temporal_latency_bucket(started_ns: int) -> str:
    """Return one bounded latency class without high-cardinality measurements."""
    elapsed_ms = max(0, time.perf_counter_ns() - started_ns) / 1_000_000
    if elapsed_ms < 10:
        return "LT_10_MS"
    if elapsed_ms < 50:
        return "LT_50_MS"
    if elapsed_ms < 250:
        return "LT_250_MS"
    if elapsed_ms < 1000:
        return "LT_1000_MS"
    return "GTE_1000_MS"


def _observe_temporal_operations(
    *,
    outcome: str,
    transaction_outcome: str,
    dependency_class: str,
    tenant_id: str,
    principal_id: str,
    correlation_id: str,
    http_status: int,
    started_ns: int,
    visible_matter_count: int | None = None,
    deadline_count: int | None = None,
    error_code: str | None = None,
) -> None:
    """Emit one bounded terminal event after the canonical transaction outcome.

    Identifiers are SHA3-512 pseudonyms and never metric labels. Legal evidence,
    headers, query values, role names, exception text and credentials are
    intentionally excluded. Logging failure cannot alter the HTTP result.
    """
    payload: dict[str, object] = {
        "schema": _TEMPORAL_OBSERVATION_SCHEMA,
        "version": _TEMPORAL_OBSERVATION_VERSION,
        "event": "LEGAL_TEMPORAL_OPERATIONS_HTTP",
        "operation": "READ",
        "outcome": outcome,
        "transaction_outcome": transaction_outcome,
        "dependency_class": dependency_class,
        "tenant_ref": _temporal_observation_ref(tenant_id),
        "principal_ref": _temporal_observation_ref(principal_id),
        "correlation_ref": _temporal_observation_ref(correlation_id),
        "http_status": http_status,
        "latency_bucket": _temporal_latency_bucket(started_ns),
    }
    if visible_matter_count is not None:
        payload["visible_matter_count"] = max(0, visible_matter_count)
    if deadline_count is not None:
        payload["deadline_count"] = max(0, deadline_count)
    if error_code is not None:
        payload["error_code"] = error_code

    try:
        logger.log(
            logging.INFO if outcome == "SUCCESS" else logging.WARNING,
            "LEGAL_TEMPORAL_OPERATIONS_HTTP",
            extra={"wilsy_observation": payload},
        )
    except Exception:
        return


def _temporal_operations_services(
    database: Any,
) -> tuple[
    LegalProductiveWorkReadService,
    LegalTemporalOperationsReadService,
]:
    """Reuse certified productive visibility and canonical deadline storage."""
    return (
        _productive_work_service(database),
        LegalTemporalOperationsReadService(
            deadline_collection=database.get_collection(
                _temporal_deadline_registry.COLLECTION
            )
        ),
    )


def _temporal_operations_payload(
    projection: Any,
) -> dict[str, object]:
    """Serialize evidenced temporal facts without deriving new authority."""
    return {
        "schema": projection.schema,
        "version": projection.version,
        "tenant_id": projection.tenant_id,
        "principal_id": projection.principal_id,
        "as_of": projection.as_of.isoformat(),
        "visible_matter_ids": list(projection.visible_matter_ids),
        "rows": [
            {
                "case_matter_id": row.case_matter_id,
                "deadline_id": row.deadline_id,
                "deadline_kind": getattr(
                    row.deadline_kind, "value", row.deadline_kind
                ),
                "title": row.title,
                "due_at": row.due_at.isoformat(),
                "source_type": getattr(
                    row.source_type, "value", row.source_type
                ),
                "source_reference": row.source_reference,
                "source_evidence_fingerprint": (
                    row.source_evidence_fingerprint
                ),
                "jurisdiction_reference": row.jurisdiction_reference,
                "status": getattr(row.status, "value", row.status),
            }
            for row in projection.rows
        ],
    }


@router.get("/temporal-operations")
async def get_legal_temporal_operations_projection(
    response: Response,
    context: TenantAuthorizationContext = Depends(
        _PRODUCTIVE_WORK_READ
    ),
) -> dict[str, object]:
    """Read canonical temporal facts for authenticated productive visibility.

    Tenant and principal are obtained exclusively from authorization context.
    One API-owned snapshot session covers productive and deadline reads.
    This endpoint grants no separate calendar, matter or execution authority.
    """
    correlation_id = _new_temporal_correlation_id()
    started_ns = time.perf_counter_ns()

    def run(
        session: Any,
        database: Any,
    ) -> dict[str, object]:
        productive_service, temporal_service = (
            _temporal_operations_services(database)
        )
        as_of = datetime.now(UTC)

        try:
            productive_work = productive_service.project(
                tenant_id=context.tenant_id,
                principal_id=context.identity.identity_id,
                as_of=as_of,
                session=session,
            )
            temporal_projection = temporal_service.project(
                productive_work=productive_work,
                session=session,
            )
            return _temporal_operations_payload(
                temporal_projection
            )
        except (
            LegalProductiveWorkReadServiceError,
            LegalProductiveWorkOperatingContextHydratorError,
            LegalTemporalOperationsReadServiceError,
        ) as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LEGAL_OPERATIONS_TEMPORAL_EVIDENCE_UNAVAILABLE",
            ) from error

    try:
        payload = _productive_work_projection_transaction(run)
        response.headers["X-Correlation-ID"] = correlation_id
        _observe_temporal_operations(
            outcome="SUCCESS",
            transaction_outcome="COMMITTED",
            dependency_class="NONE",
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            correlation_id=correlation_id,
            http_status=status.HTTP_200_OK,
            started_ns=started_ns,
            visible_matter_count=len(
                payload["visible_matter_ids"]  # type: ignore[arg-type]
            ),
            deadline_count=len(
                payload["rows"]  # type: ignore[arg-type]
            ),
        )
        return payload
    except HTTPException as error:
        detail = str(error.detail)
        temporal_failure = (
            detail
            == "LEGAL_OPERATIONS_TEMPORAL_EVIDENCE_UNAVAILABLE"
        )
        headers = dict(error.headers or {})
        headers["X-Correlation-ID"] = correlation_id
        error.headers = headers
        _observe_temporal_operations(
            outcome="ERROR",
            transaction_outcome=(
                "ABORTED" if temporal_failure else "UNAVAILABLE"
            ),
            dependency_class=(
                "TEMPORAL_EVIDENCE"
                if temporal_failure
                else "PERSISTENCE"
            ),
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            correlation_id=correlation_id,
            http_status=error.status_code,
            started_ns=started_ns,
            error_code=(
                "TEMPORAL_EVIDENCE_UNAVAILABLE"
                if temporal_failure
                else "PERSISTENCE_UNAVAILABLE"
            ),
        )
        raise


@router.get("/specialist-workflow")
async def get_legal_specialist_workflow_projection(
    context: TenantAuthorizationContext = Depends(
        _SPECIALIST_WORKFLOW_READ
    ),
) -> dict[str, object]:
    """Return workflow explanation for authenticated visible productive work.

    The existing productive-work permission and operation remain the sole HTTP
    admission authority. Tenant and principal come only from the authenticated
    authorization context. Within one API-owned snapshot transaction, the
    productive-work projection is composed first and becomes the absolute
    visibility ceiling for the P1 specialist read service.

    This endpoint exposes no create, assign, supervise, complete, transition,
    gate-satisfaction, IAM, billing, payment, execution or settlement command.
    Absence of materialization evidence yields no row; malformed, divergent or
    corrupt durable evidence fails closed as an unavailable projection.
    """

    def run(
        session: Any,
        database: Any,
    ) -> dict[str, object]:
        productive_service, specialist_service = (
            _specialist_workflow_services(
                database
            )
        )
        as_of = datetime.now(UTC)
        productive_work = productive_service.project(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            as_of=as_of,
            session=session,
        )
        projection = specialist_service.project(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            as_of=as_of,
            productive_work=productive_work,
            session=session,
        )
        return _specialist_workflow_payload(
            projection
        )

    try:
        return _productive_work_projection_transaction(
            run
        )
    except (
        LegalProductiveWorkReadServiceError,
        LegalProductiveWorkOperatingContextHydratorError,
        LegalSpecialistWorkflowReadServiceError,
    ) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "LEGAL_OPERATIONS_SPECIALIST_WORKFLOW_"
                "EVIDENCE_UNAVAILABLE"
            ),
        ) from error


@router.get("/workspace")
async def get_legal_practice_workspace_projection(
    instruction_context: TenantAuthorizationContext = Depends(_INSTRUCTION_READ),
    allocation_context: TenantAuthorizationContext = Depends(_ALLOCATION_READ),
    attempt_context: TenantAuthorizationContext = Depends(_ATTEMPT_READ),
    return_context: TenantAuthorizationContext = Depends(_RETURN_READ),
) -> dict[str, object]:
    """Return one snapshot-consistent current Legal Operations practice workspace.

    Admission is conjunctive: all four existing instruction, allocation,
    attempt, and return read authorities must be current for the same exact
    authenticated principal, tenant, and published legal-practice business role,
    and the tenant's canonical D22B5 Legal Operations product must be available.
    The response enumerates current canonical CaseMatter and P1 lifecycle projections and
    opaque current-snapshot evidence locators. It does not expose history,
    evidence references/fingerprints, client identity, billing, invoice,
    payment, AI, financial-execution, or settlement truth.
    """
    context = _workspace_context(
        instruction_context,
        allocation_context,
        attempt_context,
        return_context,
    )

    def run(session: Any, database: Any) -> dict[str, object]:
        try:
            product_availability = resolve_legal_product_availability(
                context.tenant_id,
                database.get_collection(
                    TENANT_PRODUCT_ENTITLEMENT_HISTORY_COLLECTION
                ),
                database.get_collection(
                    TENANT_PRODUCT_ENTITLEMENT_CURRENT_COLLECTION
                ),
                session=session,
            )
        except LegalProductAvailabilityProjectionError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LEGAL_OPERATIONS_PRODUCT_AUTHORITY_UNAVAILABLE",
            ) from error
        if product_availability.available is not True:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="LEGAL_OPERATIONS_PRODUCT_UNAVAILABLE",
            )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_WORKSPACE_CONFIDENTIALITY_AUTHORITY_UNAVAILABLE",
        )

    try:
        return _workspace_projection_transaction(run)
    except MatterLineageError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_WORKSPACE_PARENT_LINEAGE_INVALID",
        ) from error
    except LegalOperationsReadModelError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_OPERATIONS_WORKSPACE_EVIDENCE_UNAVAILABLE",
        ) from error


@router.get("/conflict-screenings")
async def get_legal_conflict_screening_review_queue(
    context: TenantAuthorizationContext = Depends(_INSTRUCTION_READ),
    limit: int = Query(default=MAX_REVIEW_QUEUE, ge=1, le=MAX_REVIEW_QUEUE),
) -> dict[str, object]:
    """Return the authorized tenant's bounded screening review queue.

    The canonical screening registry owns immutable screening truth and ordering;
    this route owns only one read-only snapshot transaction and a minimized
    presentation projection. Tenant identity is taken exclusively from the
    already-authorized context. ``limit`` bounds presentation and cannot widen
    the registry's tenant query. Multiple immutable reviews may exist, so this
    route deliberately projects no reviewed/unreviewed state and exposes only
    the canonical ``REVIEW_REQUIRED`` eligibility signal.
    """

    def run(session: Any, database: Any) -> dict[str, object]:
        values = LegalConflictScreeningRegistry.list_review_required(
            context.tenant_id,
            database.get_collection(LEGAL_CONFLICT_SCREENING_COLLECTION),
            session=session,
        )
        return {
            "schema": _SCREENING_SCHEMA,
            "version": _SCREENING_VERSION,
            "tenant_id": context.tenant_id,
            "visibility": _SCREENING_VISIBILITY,
            "screenings": [
                {
                    "screening_id": value.screening_id,
                    "source_case_matter_id": value.source_case_matter_id,
                    "status": getattr(value.status, "value", value.status),
                    "screened_at": value.screened_at.isoformat(),
                }
                for value in values[:limit]
            ],
        }

    try:
        return _workspace_projection_transaction(run)
    except LegalConflictScreeningRegistryError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LEGAL_CONFLICT_SCREENING_EVIDENCE_UNAVAILABLE",
        ) from error


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
    "get_legal_commercial_context_projection",
    "get_legal_conflict_screening_review_queue",
    "get_legal_practice_workspace_projection",
    "get_legal_productive_work_projection",
    "get_legal_specialist_workflow_projection",
    "get_legal_temporal_operations_projection",
    "router",
]


# ARTIFACT: legal_operations_router.py
# VERSION: v1.17.0-G68-P2-PRACTITIONER-CONFIDENTIALITY-CONTAINMENT
# AUTHORITY BOUNDARY: authenticated Legal reads and bounded post-authorization temporal observation only; temporal and specialist workflow projections remain bounded by productive-work visibility and grant no command, IAM assignment, plan/subscription mutation, payment execution or settlement authority
# TENANT POSTURE: every projection uses exact authenticated/current-authorized tenant context; foreign lifecycle, deadline, workflow, screening, subscription and entitlement evidence is never disclosed
# COMPLETION PROVENANCE: Canonical immutable completion history
# DAILY EXECUTION QUEUE: deterministic derived projection; no command authority
# ACTIVE WORK: Derived from completion currentness
# FAIL-CLOSED POSTURE: authority/scope mismatch, entitlement/subscription disagreement, unavailable product/commercial/deadline/workflow authority, snapshot failure, corruption, divergence and persistence outages deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
