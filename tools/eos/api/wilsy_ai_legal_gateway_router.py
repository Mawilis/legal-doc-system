"""FastAPI runtime composition for the WILSY AI Legal Tool Gateway.

VERSION: v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-API
AUTHORITY: Authenticated tenant-scoped projection only.
EPITOME: Exposes the seven allowlisted legal read tools while domain
         composition remains the authority for IAM, entitlement, capacity and evidence.
TENANT BOUNDARY: X-Tenant-ID dependency is mandatory; caller JSON cannot select tenant.
AUTHORITY BOUNDARY: No legal command, lifecycle, invoice, payment or settlement writes.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Missing canonical providers, entitlement, capacity or
                         evidence persistence returns bounded failure responses.
CHANGELOG: v1.1.0 composes canonical tenant/module entitlement, P6C capacity,
           underlying IAM, L7A/L7C read adapters and invocation evidence.
"""
from __future__ import annotations

from typing import Any, Final
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from tools.eos.api.tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from tools.eos.intelligence.domain.legal_ai_gateway import GATEWAY_PERMISSION, TOOL_CONTRACTS, LegalAIToolGatewayError
from tools.eos.intelligence.domain.legal_ai_gateway import authorize_legal_ai_tool
from tools.eos.intelligence.domain.legal_ai_read_adapter import LegalAIReadAdapter
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import COLLECTION as INVOCATION_COLLECTION, LegalAIToolInvocationRegistry
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import COLLECTION as ENTITLEMENT_COLLECTION, WilsyAIEntitlementRegistry
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import WilsyAIUsageCapacityOrchestrator
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.authorization import get_role_assignment_repository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authorization import authorize_tenant_operation, TenantAuthorizationReason
from tools.eos.auth.tenant_business_role_authority import resolve_current_tenant_business_role
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import COLLECTION as OBSERVATION_COLLECTION
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import COLLECTION as LIFECYCLE_COLLECTION
from tools.eos.legal_operations.registry.process_service_tariff_registry import ASSESSMENT_COLLECTION
from tools.eos.legal_operations.registry.process_service_billing_eligibility_registry import COLLECTION as ELIGIBILITY_COLLECTION

VERSION: Final[str] = "v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-API"
MODULE_ID: Final[str] = "WILSY_AI_LEGAL_TOOL_GATEWAY"
_GATEWAY_READ = RequireTenantAuthorization(GATEWAY_PERMISSION, "wilsy_ai_legal_tool_read")


class LegalToolInvokeRequest(BaseModel):
    """Strict request envelope; tenant and arbitrary tool payloads are excluded."""
    model_config = ConfigDict(extra="forbid", frozen=True)
    resource_identity: str
    entitlement_id: str
    correlation_id: str


def _bounded_contract(contract: Any) -> dict[str, object]:
    return {"identity": contract.identity, "version": contract.version, "capability": contract.capability, "entity_type": contract.entity_type, "pii_class": contract.pii_class, "allowed_fields": list(contract.allowed_fields)}


router = APIRouter(prefix="/wilsy-ai", tags=["WILSY AI Legal Tools"])


def _database() -> Any:
    from tools.eos.kernel.db import get_database
    database = get_database()
    if database is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="WILSY_AI_LEGAL_TOOL_PERSISTENCE_UNAVAILABLE")
    return database


def _collections() -> dict[str, Any]:
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
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="WILSY_AI_LEGAL_TOOL_CONFIGURATION_UNAVAILABLE") from error


def _canonical_underlying_context(context: TenantAuthorizationContext, contract: Any, session: Any, principal_repository: Any, membership_repository: Any, role_assignment_repository: Any) -> TenantAuthorizationContext:
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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="WILSY_AI_LEGAL_TOOL_DENIED")
    return TenantAuthorizationContext(identity=context.identity, tenant_id=context.tenant_id, decision=decision)


def _begin_transaction() -> tuple[Any, Any]:
    from tools.eos.kernel.db import get_client
    client = get_client()
    if client is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="WILSY_AI_LEGAL_TOOL_PERSISTENCE_UNAVAILABLE")
    session = client.start_session()
    session.start_transaction()
    return client, session


@router.get("/legal-tools")
async def list_legal_tools(context: TenantAuthorizationContext = Depends(_GATEWAY_READ), principal_repository: Any = Depends(get_principal_authority_repository), membership_repository: Any = Depends(get_tenant_membership_repository), role_assignment_repository: Any = Depends(get_role_assignment_repository)) -> dict[str, object]:
    """List only tools usable by the authenticated tenant at this instant."""
    client, session = _begin_transaction()
    try:
        collections = _collections()
        entitlement = WilsyAIEntitlementRegistry(collections["entitlement"]).get_by_module(tenant_id=context.tenant_id, module_id=MODULE_ID, session=session)
        capacity = WilsyAIUsageCapacityOrchestrator.from_collections(entitlement_collection=collections["entitlement"], observation_collection=collections["observation"]).derive_capacity(tenant_id=context.tenant_id, entitlement_id=entitlement.entitlement_id, as_of=datetime.now(timezone.utc), session=session)
        usable: list[dict[str, object]] = []
        for contract in TOOL_CONTRACTS.values():
            try:
                underlying = _canonical_underlying_context(context, contract, session, principal_repository, membership_repository, role_assignment_repository)
                authorize_legal_ai_tool(gateway_context=context, underlying_context=underlying, entitlement=entitlement, capacity=capacity, tool_identity=contract.identity, input_payload={"resource_identity": "list", "entitlement_id": entitlement.entitlement_id, "correlation_id": "list"}, occurred_at=datetime.now(timezone.utc), result_reference="list")
            except (LegalAIToolGatewayError, HTTPException):
                continue
            usable.append(_bounded_contract(contract))
        session.commit_transaction()
        return {"tenant_id": context.tenant_id, "tools": usable}
    except HTTPException:
        session.abort_transaction(); raise
    except Exception as error:
        session.abort_transaction(); raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="WILSY_AI_LEGAL_TOOL_UNAVAILABLE") from error
    finally:
        session.end_session()


@router.post("/legal-tools/{tool_identity}/invoke")
async def invoke_legal_tool(tool_identity: str, request: LegalToolInvokeRequest, context: TenantAuthorizationContext = Depends(_GATEWAY_READ), principal_repository: Any = Depends(get_principal_authority_repository), membership_repository: Any = Depends(get_tenant_membership_repository), role_assignment_repository: Any = Depends(get_role_assignment_repository)) -> dict[str, object]:
    """Compose canonical entitlement, capacity, IAM, legal read and evidence."""
    if tool_identity not in TOOL_CONTRACTS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WILSY_AI_LEGAL_TOOL_NOT_FOUND")
    contract = TOOL_CONTRACTS[tool_identity]
    if context.tenant_id != getattr(context.identity, "tenant_id", context.tenant_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="WILSY_AI_LEGAL_TOOL_DENIED")
    client, session = _begin_transaction()
    try:
        collections = _collections()
        entitlement = WilsyAIEntitlementRegistry(collections["entitlement"]).get_by_module(tenant_id=context.tenant_id, module_id=MODULE_ID, session=session)
        if entitlement.entitlement_id != request.entitlement_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="WILSY_AI_LEGAL_TOOL_DENIED")
        capacity = WilsyAIUsageCapacityOrchestrator.from_collections(entitlement_collection=collections["entitlement"], observation_collection=collections["observation"]).derive_capacity(tenant_id=context.tenant_id, entitlement_id=entitlement.entitlement_id, as_of=datetime.now(timezone.utc), session=session)
        underlying = _canonical_underlying_context(context, contract, session, principal_repository, membership_repository, role_assignment_repository)
        result = await LegalAIReadAdapter().read(contract=contract, resource_identity=request.resource_identity, context=underlying, collections=collections)
        result_reference = f"{contract.entity_type}:{request.resource_identity}"
        evidence = authorize_legal_ai_tool(gateway_context=context, underlying_context=underlying, entitlement=entitlement, capacity=capacity, tool_identity=tool_identity, input_payload=request.model_dump(), occurred_at=datetime.now(timezone.utc), result_reference=result_reference)
        persisted = LegalAIToolInvocationRegistry(collections["invocation"]).create_or_replay(evidence, session=session)
        session.commit_transaction()
        return {"tool": contract.identity, "data": result, "evidence": persisted.to_dict()}
    except HTTPException:
        session.abort_transaction(); raise
    except LegalAIToolGatewayError as error:
        session.abort_transaction(); raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="WILSY_AI_LEGAL_TOOL_DENIED") from error
    except Exception as error:
        session.abort_transaction(); raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="WILSY_AI_LEGAL_TOOL_UNAVAILABLE") from error
    finally:
        session.end_session()


__all__ = ["VERSION", "MODULE_ID", "LegalToolInvokeRequest", "list_legal_tools", "invoke_legal_tool", "router"]
# ARTIFACT: wilsy_ai_legal_gateway_router.py
# VERSION: v1.1.0-L7B-WILSY-AI-LEGAL-TOOL-API
# AUTHORITY BOUNDARY: authenticated allowlist projection; no command authority
# TENANT POSTURE: explicit exact tenant dependency
# FAIL-CLOSED POSTURE: unsupported, incomplete or divergent invocation denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
