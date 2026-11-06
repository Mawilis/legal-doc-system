"""Authenticated tenant POS HTTP authority.

Every POS business operation requires exact IAM permission, active POS product
entitlement and a server-resolved active location assignment. Location IDs in
URLs are selectors only. Location assignment issuance/revocation is a separate
owner/admin command and cannot target the acting principal.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
import json
from typing import Any, Literal
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.auth.authentication import get_principal_authority_repository
from tools.eos.auth.authorization import get_role_assignment_repository
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_EVIDENCE_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError, PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError, TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.domain.pos_commercial import (
    POSLineItem, POSSale, POSTenderIntent, POSRefundIntent, POSTenderType,
)
from tools.eos.saas.domain.pos_financial_execution_authorization import POSFinancialExecutionAuthorization
from tools.eos.saas.billing.pos_financial_execution_authorization_issuance import (
    issue_pos_collection_execution_authorization,
    issue_pos_refund_execution_authorization,
)
from tools.eos.saas.billing.pos_financial_execution_authorization_registry import POSFinancialExecutionAuthorizationRegistry
from tools.eos.saas.billing.pos_financial_movement_execution import (
    execute_pos_collection, execute_pos_refund,
)
from tools.eos.kennel.registry.financial_movement_execution_registry import FinancialMovementExecutionRegistry
from tools.eos.saas.domain.pos_location_assignment import (
    POSLocationAssignment, POSLocationAssignmentStatus,
)
from tools.eos.saas.billing.pos_commercial_registry import (
    POSSaleRegistry, POSRegistryError,
)
from tools.eos.saas.billing.pos_commercial_evidence_registry import (
    POSCommercialEvidenceRegistry, POSCommercialEvidenceRegistryError,
    POSCommercialEvidenceConflict,
)
from tools.eos.saas.billing.pos_commercial_capacity_registry import (
    COLLECTION_NAME as CAPACITY_COLLECTION, POSCommercialCapacityRegistry,
    POSCommercialCapacityError, POSCommercialCapacityConflict, POSCommercialCapacityExceeded,
)
from tools.eos.saas.billing.pos_location_assignment_registry import (
    CURRENT_COLLECTION as LOCATION_CURRENT,
    HISTORY_COLLECTION as LOCATION_HISTORY,
    POSLocationAssignmentRegistry,
    POSLocationAssignmentRegistryError,
    POSLocationAssignmentConflict,
    POSLocationAssignmentNotFound,
)
from tools.eos.saas.billing.pos_workspace_service import (
    POSWorkspaceService, POSWorkspaceServiceError,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as ENTITLEMENT_CURRENT,
    HISTORY_COLLECTION as ENTITLEMENT_HISTORY,
)

def require_pos_workspace_indexes_ready(request: Request) -> None:
    if getattr(request.app.state, "pos_workspace_indexes_ready", False) is not True:
        raise HTTPException(status_code=503, detail="POS_WORKSPACE_INDEXES_NOT_READY")


router = APIRouter(prefix="/pos", tags=["Point of Sale"], dependencies=[Depends(require_pos_workspace_indexes_ready)])


class POSLocationAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    principal_id: str = Field(min_length=1, max_length=160)


class POSLocationRevocationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=0)
    reason: str = Field(min_length=3, max_length=500)


class POSLineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: str = Field(min_length=1, max_length=160)
    sku: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=500)
    quantity: int = Field(gt=0, le=100000)
    unit_price_minor: int = Field(ge=0)
    discount_minor: int = Field(ge=0)
    tax_minor: int = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)


class POSSaleCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sale_id: str = Field(min_length=1, max_length=160)
    currency: str = Field(min_length=3, max_length=3)
    lines: list[POSLineRequest] = Field(min_length=1, max_length=100)


class POSTenderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tender_type: POSTenderType
    amount_minor: int = Field(gt=0)
    evidence_id: str = Field(min_length=1, max_length=160)


class POSCashRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cash_received_minor: int = Field(gt=0)
    evidence_id: str = Field(min_length=1, max_length=160)


class POSReturnRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sku: str = Field(min_length=1, max_length=160)
    quantity: int = Field(gt=0)
    reason: str = Field(min_length=3, max_length=500)
    return_id: str = Field(min_length=1, max_length=160)


class POSRefundRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount_minor: int = Field(gt=0)
    basis: str = Field(min_length=3, max_length=500)
    refund_intent_id: str = Field(min_length=1, max_length=160)


_ASSIGN = RequireTenantAuthorization("pos:location_assignment:manage", "pos_location_assignment_manage")
_READ = RequireTenantAuthorization("pos:sale:read", "pos_sale_read")
_CREATE = RequireTenantAuthorization("pos:sale:create", "pos_sale_create")
_TENDER = RequireTenantAuthorization("pos:tender:create", "pos_tender_create")
_CASH = RequireTenantAuthorization("pos:cash:record", "pos_cash_record")
_RETURN = RequireTenantAuthorization("pos:return:create", "pos_return_create")
_REFUND = RequireTenantAuthorization("pos:refund:create", "pos_refund_create")
_EXECUTE = RequireTenantAuthorization("pos:movement:authorize", "pos_movement_authorize")


def _collection(database: Any, name: str):
    return database.get_collection(
        name,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )


def _prepare(database: Any) -> dict[str, Any]:
    sales = _collection(database, "pos_sales")
    evidence = _collection(database, "pos_commercial_evidence")
    capacity = _collection(database, CAPACITY_COLLECTION)
    execution_authorizations = _collection(database, "pos_financial_execution_authorizations")
    movement_truths = _collection(database, "financial_movement_execution_truths")
    location_history = _collection(database, LOCATION_HISTORY)
    location_current = _collection(database, LOCATION_CURRENT)
    POSSaleRegistry.ensure_indexes(sales)
    POSCommercialEvidenceRegistry.ensure_indexes(evidence)
    POSCommercialCapacityRegistry.ensure_indexes(capacity)
    POSFinancialExecutionAuthorizationRegistry.ensure_indexes(execution_authorizations)
    FinancialMovementExecutionRegistry.ensure_indexes(movement_truths)
    POSLocationAssignmentRegistry.ensure_indexes(location_history, location_current)
    TenantAuthorizationDecisionEvidenceRegistry(
        _collection(database, AUTHORIZATION_EVIDENCE_COLLECTION),
        principal_repository=get_principal_authority_repository(),
        membership_repository=get_tenant_membership_repository(),
        role_assignment_repository=get_role_assignment_repository(),
        business_role_repository=TenantBusinessRoleRepository(),
    ).ensure_indexes()
    return {
        "sales": sales, "evidence": evidence, "capacity": capacity,
        "location_history": location_history, "location_current": location_current,
        "execution_authorizations": execution_authorizations, "movement_truths": movement_truths,
        "authorization_evidence": _collection(database, AUTHORIZATION_EVIDENCE_COLLECTION),
        "entitlement_history": _collection(database, ENTITLEMENT_HISTORY),
        "entitlement_current": _collection(database, ENTITLEMENT_CURRENT),
    }


def _service(collections: dict[str, Any]) -> POSWorkspaceService:
    return POSWorkspaceService(
        sales_collection=collections["sales"],
        evidence_collection=collections["evidence"],
        capacity_collection=collections["capacity"],
        entitlement_history_collection=collections["entitlement_history"],
        entitlement_current_collection=collections["entitlement_current"],
        location_assignment_current_collection=collections["location_current"],
    )


def _transaction(callback):
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="POS_DATABASE_UNAVAILABLE")
    try:
        collections = _prepare(database)
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(collections, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern("majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except POSWorkspaceServiceError as error:
        code = error.code
        status_code = 403 if code in {"POS_PRODUCT_NOT_ENTITLED", "POS_LOCATION_ACCESS_DENIED"} else 404 if code == "POS_SALE_NOT_FOUND_OR_CORRUPT" else 409 if "CONFLICT" in code or "REPLAY" in code else 503
        raise HTTPException(status_code=status_code, detail=code) from error
    except (POSLocationAssignmentConflict, POSCommercialEvidenceConflict, POSCommercialCapacityConflict, POSCommercialCapacityExceeded) as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except (POSLocationAssignmentNotFound, POSRegistryError) as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (POSLocationAssignmentRegistryError, POSCommercialEvidenceRegistryError, POSCommercialCapacityError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="POS_TRANSACTION_UNAVAILABLE") from error


def _authority_evidence(context: TenantAuthorizationContext, *, tenant_id: str,
                        location_id: str, target_principal_id: str,
                        idempotency_key: str, command: str, occurred_at: datetime) -> tuple[str, str]:
    payload = {
        "schema": "WILSY-POS-LOCATION-AUTHORITY-COMMAND/V1",
        "command": command,
        "tenant_id": tenant_id,
        "location_id": location_id,
        "target_principal_id": target_principal_id,
        "actor_principal_id": context.identity.identity_id,
        "business_role": context.decision.business_role,
        "authorization_role": context.decision.authorization_role,
        "permission": "pos:location_assignment:manage",
        "idempotency_key": idempotency_key,
        "occurred_at": occurred_at.isoformat(),
    }
    digest = sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"pos-location-authority-command:{digest[:32]}", digest


@router.get("/locations")
async def list_assigned_locations(
    context: TenantAuthorizationContext = Depends(_READ),
):
    """List only current ACTIVE locations assigned to this authenticated principal."""
    return _transaction(lambda collections, session: {
        "tenant_id": context.tenant_id,
        "principal_id": context.identity.identity_id,
        "locations": list(_service(collections).list_locations(
            tenant_id=context.tenant_id,
            principal_id=context.identity.identity_id,
            session=session,
        )),
    })


@router.post("/locations/{location_id}/assignments", status_code=status.HTTP_201_CREATED)
async def assign_location(
    location_id: str,
    body: POSLocationAssignmentRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_ASSIGN),
    principal_repository: Any = Depends(get_principal_authority_repository),
):
    """Grant one explicit location assignment to an ACTIVE tenant principal."""
    def command(collections, session):
        if body.principal_id == context.identity.identity_id:
            raise HTTPException(status_code=403, detail="POS_SELF_LOCATION_ASSIGNMENT_FORBIDDEN")
        try:
            target_principal = principal_repository.resolve(body.principal_id, session=session)
        except PrincipalAuthorityNotFoundError as error:
            raise HTTPException(status_code=404, detail="POS_TARGET_PRINCIPAL_NOT_FOUND") from error
        except PrincipalAuthorityRepositoryError as error:
            raise HTTPException(status_code=503, detail="POS_TARGET_PRINCIPAL_AUTHORITY_UNAVAILABLE") from error
        if target_principal.status is not PrincipalStatus.ACTIVE:
            raise HTTPException(status_code=403, detail="POS_TARGET_PRINCIPAL_INACTIVE")
        try:
            membership = TenantMembershipRepository().resolve(
                body.principal_id, context.tenant_id, session=session,
            )
        except TenantMembershipNotFoundError as error:
            raise HTTPException(status_code=404, detail="POS_TARGET_MEMBERSHIP_NOT_FOUND") from error
        except TenantMembershipRepositoryError as error:
            raise HTTPException(status_code=503, detail="POS_TARGET_MEMBERSHIP_UNAVAILABLE") from error
        if membership.status is not TenantMembershipStatus.ACTIVE:
            raise HTTPException(status_code=403, detail="POS_TARGET_MEMBERSHIP_INACTIVE")
        now = datetime.now(timezone.utc)
        reference, fingerprint = _authority_evidence(
            context, tenant_id=context.tenant_id, location_id=location_id,
            target_principal_id=body.principal_id, idempotency_key=idempotency_key,
            command="ISSUE", occurred_at=now,
        )
        assignment_id = "posloc_" + sha3_512(
            f"{context.tenant_id}\0{location_id}\0{body.principal_id}\0{idempotency_key}".encode()
        ).hexdigest()[:32]
        assignment = POSLocationAssignment(
            tenant_id=context.tenant_id, location_id=location_id,
            principal_id=body.principal_id, assignment_id=assignment_id,
            revision=0, status=POSLocationAssignmentStatus.ACTIVE,
            authority_reference=reference, authority_fingerprint=fingerprint,
            idempotency_key=idempotency_key, occurred_at=now,
            changed_by_principal_id=context.identity.identity_id,
        )
        value = POSLocationAssignmentRegistry.issue(
            assignment, collections["location_history"], collections["location_current"],
            session=session,
        )
        return value.to_dict()
    return _transaction(command)


@router.post("/locations/{location_id}/assignments/{principal_id}/revoke")
async def revoke_location(
    location_id: str,
    principal_id: str,
    body: POSLocationRevocationRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_ASSIGN),
):
    """Revoke one exact current assignment through revision-guarded authority."""
    def command(collections, session):
        prior = POSLocationAssignmentRegistry.resolve(
            context.tenant_id, location_id, principal_id,
            collections["location_current"], session=session,
        )
        now = datetime.now(timezone.utc)
        reference, fingerprint = _authority_evidence(
            context, tenant_id=context.tenant_id, location_id=location_id,
            target_principal_id=principal_id, idempotency_key=idempotency_key,
            command="REVOKE", occurred_at=now,
        )
        value = POSLocationAssignmentRegistry.revoke(
            tenant_id=context.tenant_id, location_id=location_id,
            principal_id=principal_id, assignment_id=prior.assignment_id,
            expected_revision=body.expected_revision,
            authority_reference=reference, authority_fingerprint=fingerprint,
            idempotency_key=idempotency_key, occurred_at=now,
            changed_by_principal_id=context.identity.identity_id,
            reason=body.reason, history=collections["location_history"],
            current=collections["location_current"], session=session,
        )
        return value.to_dict()
    return _transaction(command)


@router.post("/locations/{location_id}/sales", status_code=status.HTTP_201_CREATED)
async def create_sale(
    location_id: str,
    body: POSSaleCreateRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CREATE),
):
    def command(collections, session):
        return _service(collections).create_sale(
            tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
            location_id=location_id, sale_id=body.sale_id, currency=body.currency,
            lines=tuple(POSLineItem(**line.model_dump()) for line in body.lines),
            idempotency_key=idempotency_key, session=session,
        ).to_dict()
    return _transaction(command)


@router.get("/locations/{location_id}/sales/{sale_id}")
async def read_sale(
    location_id: str, sale_id: str,
    context: TenantAuthorizationContext = Depends(_READ),
):
    return _transaction(lambda collections, session: _service(collections).read_sale(
        tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
        location_id=location_id, sale_id=sale_id, session=session,
    ))


@router.post("/locations/{location_id}/sales/{sale_id}/tenders", status_code=status.HTTP_201_CREATED)
async def create_tender(
    location_id: str, sale_id: str, body: POSTenderRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_TENDER),
):
    return _transaction(lambda collections, session: _service(collections).record_tender(
        tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
        location_id=location_id, sale_id=sale_id, tender_type=body.tender_type,
        amount_minor=body.amount_minor, idempotency_key=idempotency_key,
        evidence_id=body.evidence_id, session=session,
    ))


@router.post("/locations/{location_id}/sales/{sale_id}/cash-tenders", status_code=status.HTTP_201_CREATED)
async def record_cash(
    location_id: str, sale_id: str, body: POSCashRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CASH),
):
    return _transaction(lambda collections, session: _service(collections).record_cash(
        tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
        location_id=location_id, sale_id=sale_id,
        cash_received_minor=body.cash_received_minor, idempotency_key=idempotency_key,
        evidence_id=body.evidence_id, session=session,
    ))


@router.post("/locations/{location_id}/sales/{sale_id}/returns", status_code=status.HTTP_201_CREATED)
async def create_return(
    location_id: str, sale_id: str, body: POSReturnRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_RETURN),
):
    return _transaction(lambda collections, session: _service(collections).create_return(
        tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
        location_id=location_id, sale_id=sale_id, sku=body.sku,
        quantity=body.quantity, reason=body.reason, return_id=body.return_id,
        idempotency_key=idempotency_key, session=session,
    ))


@router.post("/locations/{location_id}/sales/{sale_id}/refund-intents", status_code=status.HTTP_201_CREATED)
async def create_refund(
    location_id: str, sale_id: str, body: POSRefundRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_REFUND),
):
    return _transaction(lambda collections, session: _service(collections).create_refund(
        tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
        location_id=location_id, sale_id=sale_id, amount_minor=body.amount_minor,
        basis=body.basis, refund_intent_id=body.refund_intent_id,
        idempotency_key=idempotency_key, session=session,
    ))


def _issue_execution_authority(*, collections: dict[str, Any], session: Any,
                               context: TenantAuthorizationContext, sale: POSSale,
                               source: POSTenderIntent | POSRefundIntent,
                               source_row: dict[str, Any], direction: str) -> POSFinancialExecutionAuthorization:
    source_identity = source.idempotency_key if isinstance(source, POSTenderIntent) else source.refund_intent_id
    stable_key = "pos-financial-execution:" + sha3_512(
        f"{context.tenant_id}\\0{sale.location_id}\\0{sale.sale_id}\\0{direction}\\0{source_identity}".encode()
    ).hexdigest()
    authority_registry = TenantAuthorizationDecisionEvidenceRegistry(
        collections["authorization_evidence"],
        principal_repository=get_principal_authority_repository(),
        membership_repository=get_tenant_membership_repository(),
        role_assignment_repository=get_role_assignment_repository(),
        business_role_repository=TenantBusinessRoleRepository(),
    )
    source_fingerprint = sha3_512(json.dumps(
        source.to_dict(), sort_keys=True, separators=(",", ":"),
    ).encode()).hexdigest()
    authority = authority_registry.issue(
        tenant_id=context.tenant_id,
        principal_id=context.identity.identity_id,
        operation="pos_movement_authorize",
        permission="pos:movement:authorize",
        subject_reference=f"pos:{direction.lower()}:{sale.sale_id}:{source_identity}",
        subject_evidence_fingerprint=source_fingerprint,
        idempotency_key=stable_key,
        session=session,
    )
    authorization_id = "posauth_" + sha3_512(stable_key.encode()).hexdigest()[:32]
    if isinstance(source, POSTenderIntent):
        return issue_pos_collection_execution_authorization(
            sale, source, authority, collections["execution_authorizations"],
            authorization_id=authorization_id, idempotency_key=stable_key, session=session,
        )
    return issue_pos_refund_execution_authorization(
        sale, source, authority, collections["execution_authorizations"],
        authorization_id=authorization_id, idempotency_key=stable_key, session=session,
    )


@router.post("/locations/{location_id}/sales/{sale_id}/tenders/{evidence_id}/execute")
async def execute_electronic_tender(
    location_id: str, sale_id: str, evidence_id: str,
    request: Request,
    context: TenantAuthorizationContext = Depends(_EXECUTE),
):
    """Authorize and delegate one electronic collection to the Kennel bridge."""
    orchestrator = getattr(request.app.state, "pos_financial_movement_orchestrator", None)
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="KENNEL_FINANCIAL_MOVEMENT_PROVIDER_UNBOUND")
    def authorize(collections, session):
        projection = _service(collections).read_sale(
            tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
            location_id=location_id, sale_id=sale_id, session=session,
        )
        sale = POSSale.from_dict(projection["sale"])
        row = next((item for item in projection["commercial_evidence"]
                    if item.get("evidence_type") == "TENDER_INTENT" and item.get("evidence_id") == evidence_id), None)
        if row is None:
            raise HTTPException(status_code=404, detail="POS_TENDER_EVIDENCE_NOT_FOUND")
        data = row["evidence"]
        source = POSTenderIntent(
            tenant_id=data["tenant_id"], location_id=data["location_id"], sale_id=data["sale_id"],
            tender_type=POSTenderType(data["tender_type"]), requested_amount_minor=data["requested_amount_minor"],
            currency=data["currency"], idempotency_key=data["idempotency_key"],
        )
        if source.tender_type not in (POSTenderType.CARD, POSTenderType.BANK, POSTenderType.WALLET) or source.requested_amount_minor != sale.total_minor:
            raise HTTPException(status_code=409, detail="POS_ELECTRONIC_TENDER_NOT_EXECUTABLE")
        authorization = _issue_execution_authority(
            collections=collections, session=session, context=context, sale=sale,
            source=source, source_row=row, direction="COLLECTION",
        )
        return sale.to_dict(), source.to_dict(), authorization.to_dict()
    sale_data, source_data, authorization_data = _transaction(authorize)
    sale = POSSale.from_dict(sale_data)
    source = POSTenderIntent(
        tenant_id=source_data["tenant_id"], location_id=source_data["location_id"], sale_id=source_data["sale_id"],
        tender_type=POSTenderType(source_data["tender_type"]), requested_amount_minor=source_data["requested_amount_minor"],
        currency=source_data["currency"], idempotency_key=source_data["idempotency_key"],
    )
    authorization = POSFinancialExecutionAuthorization.from_dict(authorization_data)
    result = execute_pos_collection(
        sale, source, authorization,
        _collection(get_database(), "financial_movement_execution_truths"), orchestrator,
    )
    return {"provider_invoked": result.provider_invoked, "execution_truth": result.execution_truth.to_dict()}


@router.post("/locations/{location_id}/sales/{sale_id}/refund-intents/{evidence_id}/execute")
async def execute_refund_intent(
    location_id: str, sale_id: str, evidence_id: str,
    request: Request,
    context: TenantAuthorizationContext = Depends(_EXECUTE),
):
    """Authorize and delegate one refund disbursement to the Kennel bridge."""
    orchestrator = getattr(request.app.state, "pos_financial_movement_orchestrator", None)
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="KENNEL_FINANCIAL_MOVEMENT_PROVIDER_UNBOUND")
    def authorize(collections, session):
        projection = _service(collections).read_sale(
            tenant_id=context.tenant_id, principal_id=context.identity.identity_id,
            location_id=location_id, sale_id=sale_id, session=session,
        )
        sale = POSSale.from_dict(projection["sale"])
        row = next((item for item in projection["commercial_evidence"]
                    if item.get("evidence_type") == "REFUND_INTENT" and item.get("evidence_id") == evidence_id), None)
        if row is None:
            raise HTTPException(status_code=404, detail="POS_REFUND_EVIDENCE_NOT_FOUND")
        data = row["evidence"]
        source = POSRefundIntent(
            tenant_id=data["tenant_id"], location_id=data["location_id"],
            refund_intent_id=data["refund_intent_id"], sale_id=data["sale_id"],
            amount_minor=data["amount_minor"], currency=data["currency"],
            basis=data["basis"], idempotency_key=data["idempotency_key"],
        )
        authorization = _issue_execution_authority(
            collections=collections, session=session, context=context, sale=sale,
            source=source, source_row=row, direction="DISBURSEMENT",
        )
        return sale.to_dict(), source.to_dict(), authorization.to_dict()
    sale_data, source_data, authorization_data = _transaction(authorize)
    sale = POSSale.from_dict(sale_data)
    source = POSRefundIntent(
        tenant_id=source_data["tenant_id"], location_id=source_data["location_id"],
        refund_intent_id=source_data["refund_intent_id"], sale_id=source_data["sale_id"],
        amount_minor=source_data["amount_minor"], currency=source_data["currency"],
        basis=source_data["basis"], idempotency_key=source_data["idempotency_key"],
    )
    authorization = POSFinancialExecutionAuthorization.from_dict(authorization_data)
    result = execute_pos_refund(
        sale, source, authorization,
        _collection(get_database(), "financial_movement_execution_truths"), orchestrator,
    )
    return {"provider_invoked": result.provider_invoked, "execution_truth": result.execution_truth.to_dict()}


def ensure_pos_workspace_indexes(database: Any) -> None:
    """Provision POS registries and unique indexes during API startup."""
    _prepare(database)


__all__ = ["router", "require_pos_workspace_indexes_ready", "ensure_pos_workspace_indexes"]
