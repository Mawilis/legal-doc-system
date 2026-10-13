"""FastAPI runtime composition for the WILSY AI Legal Tool Gateway.

TITLE: WILSY OS WILSY AI Legal Tool Gateway Router
VERSION: v1.4.0-CX18-PRE-READ-ADMISSION
AUTHORITY: Authenticated tenant-scoped projection of allowlisted canonical reads.
EPITOME: Recompose current durable authority and complete final AI admission
         before any legal resource materialization, then persist post-read evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/wilsy_ai_legal_gateway_router.py
COLLABORATION / OWNERSHIP: Canonical IAM owns principal, membership, business-role,
                            and granting-role truth; Legal Operations owns domain
                            truth; this router owns only request transaction composition.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: 2026-10-13 v1.4.0-CX18 places final pure AI admission before the
           domain adapter read and post-read evidence construction after it;
           listing uses admission without creating invocation evidence.
           2026-09-23 v1.2.0-L8-0 introduced canonical split-role IAM wiring.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Caller JSON cannot assert tenant, role, permission,
                             provider, entitlement, or capacity; denied requests
                             materialize no domain data and persist no evidence.
TENANT BOUNDARY: Current ACTIVE principal, membership, eligible tenant business
                 role, and ACTIVE granting role are recomposed for every request.
AUTHORITY BOUNDARY: Read composition and invocation evidence only; no legal,
                    IAM, entitlement, capacity, or billing lifecycle mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: This router alone starts, commits, aborts, and ends the
                      request-scoped Mongo session; lower layers receive it.
FAIL-CLOSED DECLARATION: Unknown tools, revoked IAM, commercial denial, invalid
                         input, read failure, persistence failure, or replay
                         conflict returns bounded denial/unavailability.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
    get_role_assignment_repository,
)
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, authorize_tenant_operation
from tools.eos.intelligence.domain.legal_ai_gateway import (
    GATEWAY_PERMISSION,
    TOOL_CONTRACTS,
    LegalAIToolGatewayError,
    build_legal_ai_tool_invocation_evidence,
    require_legal_ai_tool_admission,
)
from tools.eos.intelligence.domain.legal_ai_read_adapter import LegalAIReadAdapter
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import (
    COLLECTION as INVOCATION_COLLECTION,
    LegalAIToolInvocationRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import COLLECTION as LIFECYCLE_COLLECTION
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import COLLECTION as ELIGIBILITY_COLLECTION
from tools.eos.legal_operations.registry.process_service_tariff_registry import ASSESSMENT_COLLECTION
from tools.eos.saas.billing.wilsy_ai_entitlement_provisioning import MODULE_ID as REASONING_MODULE_ID
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import COLLECTION as ENTITLEMENT_COLLECTION, WilsyAIEntitlementRegistry
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import WilsyAIUsageCapacityOrchestrator
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import COLLECTION as OBSERVATION_COLLECTION

VERSION: Final[str] = "v1.4.0-CX18-PRE-READ-ADMISSION"
MODULE_ID: Final[str] = REASONING_MODULE_ID
_GATEWAY_READ = RequireTenantAuthorization(GATEWAY_PERMISSION, "wilsy_ai_legal_tool_read")


class LegalToolInvokeRequest(BaseModel):
    """Strict bounded selection envelope carrying no tenant or authority truth."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    resource_identity: str
    correlation_id: str


def _bounded_contract(contract: Any) -> dict[str, object]:
    """Project one public allowlisted contract without granting authority."""
    return {
        "identity": contract.identity,
        "version": contract.version,
        "capability": contract.capability,
        "entity_type": contract.entity_type,
        "pii_class": contract.pii_class,
        "allowed_fields": list(contract.allowed_fields),
    }


router = APIRouter(prefix="/wilsy-ai", tags=["WILSY AI Legal Tools"])


def _database() -> Any:
    """Resolve configured persistence or fail with bounded unavailability."""
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="WILSY_AI_LEGAL_TOOL_PERSISTENCE_UNAVAILABLE")
    return database


def _collections() -> dict[str, Any]:
    """Resolve the canonical collections used by one gateway composition."""
    database = _database()
    return {
        "entitlement": database[ENTITLEMENT_COLLECTION],
        "observation": database[OBSERVATION_COLLECTION],
        "lifecycle": database[LIFECYCLE_COLLECTION],
        "tariff": database[ASSESSMENT_COLLECTION],
        "eligibility": database[ELIGIBILITY_COLLECTION],
        "invoice": database["client_invoices"],
        "issuance": database["issuance"],
        "invocation": database[INVOCATION_COLLECTION],
    }


def _underlying_operation(contract: Any) -> tuple[str, str]:
    """Map one allowlisted permission to its canonical tenant operation."""
    mapping = {
        "legal_operations:instruction:read": ("legal_instruction_read", "legal_operations:instruction:read"),
        "legal_operations:attempt:read": ("legal_attempt_read", "legal_operations:attempt:read"),
        "legal_operations:return:read": ("legal_return_read", "legal_operations:return:read"),
        "legal_operations:billing:read": ("legal_billing_read", "legal_operations:billing:read"),
        "legal_operations:invoice:read": ("legal_invoice_read", "legal_operations:invoice:read"),
    }
    try:
        return mapping[contract.underlying_permission]
    except KeyError as error:
        raise HTTPException(status_code=503, detail="WILSY_AI_LEGAL_TOOL_CONFIGURATION_UNAVAILABLE") from error


def _canonical_underlying_context(
    context: TenantAuthorizationContext,
    contract: Any,
    session: Any,
    principal_repository: Any,
    membership_repository: Any,
    role_assignment_repository: Any,
) -> TenantAuthorizationContext:
    """Reauthorize underlying permission from current canonical durable truth."""
    operation, permission = _underlying_operation(contract)
    decision = authorize_tenant_operation(
        principal_id=context.identity.identity_id,
        tenant_id=context.tenant_id,
        permission_id=permission,
        operation=operation,
        principal_repository=principal_repository,
        membership_repository=membership_repository,
        role_assignment_repository=role_assignment_repository,
        business_role_repository=role_assignment_repository,
        session=session,
    )
    if not decision.authorized or decision.reason is not TenantAuthorizationReason.AUTHORIZED:
        raise HTTPException(status_code=403, detail="WILSY_AI_LEGAL_TOOL_DENIED")
    return TenantAuthorizationContext(identity=context.identity, tenant_id=context.tenant_id, decision=decision)


def _begin_transaction() -> tuple[Any, Any]:
    """Begin one caller-owned request transaction or fail closed."""
    from tools.eos.kernel.db import get_client

    client = get_client()
    if client is None:
        raise HTTPException(status_code=503, detail="WILSY_AI_LEGAL_TOOL_PERSISTENCE_UNAVAILABLE")
    session = client.start_session()
    session.start_transaction()
    return client, session


def _commercial_facts(collections: dict[str, Any], tenant_id: str, session: Any) -> tuple[Any, Any]:
    """Load current entitlement then derive current capacity in caller session."""
    entitlement = WilsyAIEntitlementRegistry(collections["entitlement"]).get_by_module(
        tenant_id=tenant_id, module_id=MODULE_ID, session=session,
    )
    capacity = WilsyAIUsageCapacityOrchestrator.from_collections(
        entitlement_collection=collections["entitlement"],
        observation_collection=collections["observation"],
    ).derive_capacity(
        tenant_id=tenant_id,
        entitlement_id=entitlement.entitlement_id,
        as_of=datetime.now(timezone.utc),
        session=session,
    )
    return entitlement, capacity


@router.get("/legal-tools")
async def list_legal_tools(
    context: TenantAuthorizationContext = Depends(_GATEWAY_READ),
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    role_assignment_repository: Any = Depends(get_role_assignment_repository),
) -> dict[str, object]:
    """List tools passing current IAM and pure admission without persistence."""
    _client, session = _begin_transaction()
    try:
        collections = _collections()
        entitlement, capacity = _commercial_facts(collections, context.tenant_id, session)
        usable: list[dict[str, object]] = []
        for contract in TOOL_CONTRACTS.values():
            try:
                underlying = _canonical_underlying_context(
                    context, contract, session, principal_repository,
                    membership_repository, role_assignment_repository,
                )
                require_legal_ai_tool_admission(
                    gateway_context=context,
                    underlying_context=underlying,
                    entitlement=entitlement,
                    capacity=capacity,
                    tool_identity=contract.identity,
                    input_payload={"resource_identity": "list", "correlation_id": "list"},
                )
            except (LegalAIToolGatewayError, HTTPException):
                continue
            usable.append(_bounded_contract(contract))
        session.commit_transaction()
        return {"tenant_id": context.tenant_id, "tools": usable}
    except HTTPException:
        session.abort_transaction()
        raise
    except Exception as error:
        session.abort_transaction()
        raise HTTPException(status_code=503, detail="WILSY_AI_LEGAL_TOOL_UNAVAILABLE") from error
    finally:
        session.end_session()


@router.post("/legal-tools/{tool_identity}/invoke")
async def invoke_legal_tool(
    tool_identity: str,
    request: LegalToolInvokeRequest,
    context: TenantAuthorizationContext = Depends(_GATEWAY_READ),
    principal_repository: Any = Depends(get_principal_authority_repository),
    membership_repository: Any = Depends(get_tenant_membership_repository),
    role_assignment_repository: Any = Depends(get_role_assignment_repository),
) -> dict[str, object]:
    """Admit before read, then construct and persist post-read evidence."""
    contract = TOOL_CONTRACTS.get(tool_identity)
    if contract is None:
        raise HTTPException(status_code=404, detail="WILSY_AI_LEGAL_TOOL_NOT_FOUND")
    if context.tenant_id != getattr(context.identity, "tenant_id", context.tenant_id):
        raise HTTPException(status_code=403, detail="WILSY_AI_LEGAL_TOOL_DENIED")
    _client, session = _begin_transaction()
    try:
        collections = _collections()
        entitlement, capacity = _commercial_facts(collections, context.tenant_id, session)
        underlying = _canonical_underlying_context(
            context, contract, session, principal_repository,
            membership_repository, role_assignment_repository,
        )
        admission = require_legal_ai_tool_admission(
            gateway_context=context,
            underlying_context=underlying,
            entitlement=entitlement,
            capacity=capacity,
            tool_identity=tool_identity,
            input_payload=request.model_dump(),
        )
        result = await LegalAIReadAdapter().read(
            contract=contract,
            resource_identity=request.resource_identity,
            context=underlying,
            collections=collections,
        )
        evidence = build_legal_ai_tool_invocation_evidence(
            admission=admission,
            occurred_at=datetime.now(timezone.utc),
            result_reference=f"{contract.entity_type}:{request.resource_identity}",
        )
        persisted = LegalAIToolInvocationRegistry(collections["invocation"]).create_or_replay(
            evidence, session=session,
        )
        session.commit_transaction()
        return {"tool": contract.identity, "data": result, "evidence": persisted.to_dict()}
    except HTTPException:
        session.abort_transaction()
        raise
    except LegalAIToolGatewayError as error:
        session.abort_transaction()
        raise HTTPException(status_code=403, detail="WILSY_AI_LEGAL_TOOL_DENIED") from error
    except Exception as error:
        session.abort_transaction()
        raise HTTPException(status_code=503, detail="WILSY_AI_LEGAL_TOOL_UNAVAILABLE") from error
    finally:
        session.end_session()


__all__ = ["VERSION", "MODULE_ID", "LegalToolInvokeRequest", "list_legal_tools", "invoke_legal_tool", "router"]

# ARTIFACT: wilsy_ai_legal_gateway_router.py
# VERSION: v1.4.0-CX18-PRE-READ-ADMISSION
# AUTHORITY BOUNDARY: authenticated read composition and post-read evidence only
# TENANT POSTURE: fresh canonical principal, membership, business-role, and granting-role truth
# FAIL-CLOSED POSTURE: denial precedes domain read and invocation evidence persistence
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
