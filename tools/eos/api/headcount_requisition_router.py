"""TITLE: WILSY EOS tenant-scoped headcount requisition HTTP commands.
VERSION: v1.3.0-SAFE-MY-WORK-PROJECTION
AUTHORITY: Python EOS tenant authorization and headcount registry composition.
EPITOME: Exposes exact-tenant requisition read, creation, submission and independent
         decision routes over the canonical transactional headcount registry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/headcount_requisition_router.py
COLLABORATION / OWNERSHIP: Mounted once by tools/eos/api/server.py under /api.
CERTIFICATION / UPDATE DATE: 2026-11-15.
CHANGELOG:
  v1.3.0-SAFE-MY-WORK-PROJECTION — Adds an internal, read-only, source-owned
  minimal action projection for Unified My Work. It emits no position,
  department, justification, headcount, approver, or requester data and is
  callable only after the aggregate independently admits this route's current
  read and action authority.
  v1.2.1-PLATFORM-EMPLOYER-SCOPE — Corrects the release marker so the header, current changelog and end seal agree exactly; HTTP and transaction behavior are unchanged.
  v1.2.0-PLATFORM-EMPLOYER-SCOPE — Routes the same headcount operations through existing exact-WILSY platform-employer IAM pairs while preserving customer HR entitlement and tenant IAM requirements.
  v1.1.0-HEADCOUNT-DECISION-ID-FIX — Imports the decision identifier generator used by the independent approval route; supplies the required sovereign header, route contracts and end seal.
  v1.0.0-HEADCOUNT-HTTP — Adds authenticated own-tenant headcount requisition reads and maker-checker commands over majority transactions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Strict request schemas; no raw identity document or candidate PII is accepted here.
TENANT BOUNDARY: Every record lookup and transition uses the authenticated exact tenant from current EOS authorization; employer pairs are selected only for canonical WILSY.
AUTHORITY BOUNDARY: Customer HR requires active exact-tenant HR entitlement, current membership, eligible HR business role, assigned permission and applicable workforce currentness. Canonical WILSY employer commands use separately assigned platform-employer permissions through the same EOS resolver. Creation/submission and decision remain split. Offer acceptance and employee admission remain disabled pending verified candidate identity binding.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution, settlement or product entitlement grant.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import uuid
from typing import Any, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization, TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_client, get_database
from tools.eos.saas.domain.headcount_requisition import (
    HeadcountApproval, HeadcountRequisition, RequisitionDecision, RequisitionError,
    RequisitionStatus,
)
from tools.eos.saas.hr.headcount_requisition_registry import (
    COLLECTION, EVENT_COLLECTION, HeadcountRequisitionNotFound,
    HeadcountRequisitionRegistry, HeadcountRequisitionRegistryConflict,
    HeadcountRequisitionRegistryError,
)

router = APIRouter(prefix="/hr/headcount-requisitions", tags=["Headcount Requisitions"])

_READ = RequireTenantAuthorization(
    "hr:headcount_requisition:read", "hr_headcount_requisition_read",
    platform_employer_permission_id="platform_employer:headcount_requisition:read",
    platform_employer_operation="platform_employer_headcount_requisition_read",
)
_CREATE = RequireTenantAuthorization(
    "hr:headcount_requisition:create", "hr_headcount_requisition_create",
    platform_employer_permission_id="platform_employer:headcount_requisition:create",
    platform_employer_operation="platform_employer_headcount_requisition_create",
)
_DECIDE = RequireTenantAuthorization(
    "hr:headcount_requisition:decide", "hr_headcount_requisition_decide",
    platform_employer_permission_id="platform_employer:headcount_requisition:decide",
    platform_employer_operation="platform_employer_headcount_requisition_decide",
)


class RequisitionCreateRequest(BaseModel):
    """Bounded own-tenant requisition facts; no employee or IAM data is accepted."""
    model_config = ConfigDict(extra="forbid")
    department_id: str = Field(min_length=1, max_length=180)
    position_title: str = Field(min_length=1, max_length=180)
    employment_type: str = Field(min_length=1, max_length=180)
    work_location: str = Field(min_length=1, max_length=180)
    headcount: int = Field(ge=1, le=50, strict=True)
    business_justification: str = Field(min_length=1, max_length=4000)


class RequisitionSubmitRequest(BaseModel):
    """Expected aggregate revision for the authorized maker submission command."""
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1, strict=True)


class RequisitionDecisionRequest(BaseModel):
    """Independent approve/reject decision and reason for a submitted requisition."""
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1)
    decision: Literal["APPROVE", "REJECT"]
    reason: str = Field(min_length=1, max_length=2000)


def _registry(database: Any) -> HeadcountRequisitionRegistry:
    """Compose the canonical headcount registry with majority concerns."""
    current = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    events = database.get_collection(
        EVENT_COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    return HeadcountRequisitionRegistry(current, events)


def _request_fingerprint(
    *, tenant_id: str, requisition_id: str, actor_principal_id: str,
    action: str, idempotency_key: str, payload: dict[str, object],
) -> str:
    """Fingerprint the exact tenant, actor, action, replay key, and command body."""
    command = {
        "tenant_id": tenant_id,
        "requisition_id": requisition_id,
        "actor_principal_id": actor_principal_id,
        "action": action,
        "idempotency_key": idempotency_key,
        "payload": payload,
    }
    raw = json.dumps(command, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _transaction(callback):
    """Run one registry operation in the route-owned majority Mongo transaction."""
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="HEADCOUNT_DATABASE_UNAVAILABLE")
    try:
        current = database.get_collection(COLLECTION, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        events = database.get_collection(EVENT_COLLECTION, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))
        HeadcountRequisitionRegistry.ensure_indexes(current, events)
        with client.start_session() as session:
            return session.with_transaction(
                lambda current: callback(_registry(database), current),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HeadcountRequisitionNotFound as error:
        raise HTTPException(status_code=404, detail=error.code) from error
    except HeadcountRequisitionRegistryConflict as error:
        raise HTTPException(status_code=409, detail=error.code) from error
    except (HeadcountRequisitionRegistryError, RequisitionError) as error:
        code = getattr(error, "code", str(error))
        raise HTTPException(status_code=422 if isinstance(error, RequisitionError) else 503, detail=code) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code=503, detail="HEADCOUNT_TRANSACTION_UNAVAILABLE") from error


def _project_my_work(
    *,
    tenant_id: str,
    principal_id: str,
    may_submit: bool,
    may_decide: bool,
) -> dict[str, object]:
    """Return the source-owned, non-sensitive pending headcount actions.

    Unified My Work calls this internal adapter only after its independent
    dependencies have revalidated this source's read permission and the exact
    submit/decision capabilities for the current identity, membership and
    business capacity. This source function deliberately exposes neither the
    tenant-wide administrative read model nor identities, business rationale,
    position, department, location, headcount or revisions. The command routes
    remain the exclusive authority and repeat every authorization, status,
    maker-checker, revision, evidence and transaction check.

    The underlying registry has a bounded list contract. A full page is treated
    as unavailable rather than silently truncating pending work, so verified
    empty never means an incomplete administrative queue is clear.
    """
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise HTTPException(status_code=503, detail="HEADCOUNT_MY_WORK_SCOPE_INVALID")

    def read(registry: HeadcountRequisitionRegistry, session: Any) -> dict[str, object]:
        values = registry.list_for_tenant(tenant_id=tenant_id, session=session, limit=500)
        if len(values) == 500:
            raise HTTPException(status_code=503, detail="HEADCOUNT_MY_WORK_BOUND_EXCEEDED")
        items: list[dict[str, object]] = []
        for value in values:
            if (
                may_submit
                and value.status is RequisitionStatus.DRAFT
                and value.requested_by_principal_id == principal_id
            ):
                items.append({
                    "work_item_id": f"HEADCOUNT:{value.requisition_id}:SUBMIT",
                    "title": "Submit headcount requisition",
                    "status": "PENDING_ACTION",
                    "priority": "NORMAL",
                    "kind": "HR_HEADCOUNT_SUBMIT",
                })
            elif (
                may_decide
                and value.status is RequisitionStatus.SUBMITTED
                and principal_id not in {
                    value.requested_by_principal_id,
                    value.submitted_by_principal_id,
                }
            ):
                items.append({
                    "work_item_id": f"HEADCOUNT:{value.requisition_id}:DECIDE",
                    "title": "Independently decide headcount requisition",
                    "status": "PENDING_ACTION",
                    "priority": "HIGH",
                    "kind": "HR_HEADCOUNT_DECISION",
                })
        return {"tenant_id": tenant_id, "items": items}

    return _transaction(read)


@router.get("")
async def list_headcount_requisitions(
    context: TenantAuthorizationContext = Depends(_READ),
) -> dict[str, object]:
    """Read only requisitions owned by the authenticated exact tenant."""
    values = _transaction(
        lambda registry, session: registry.list_for_tenant(
            tenant_id=context.tenant_id, session=session,
        )
    )
    return {
        "schema": "WILSY-HEADCOUNT-REQUISITIONS/V1",
        "tenant_id": context.tenant_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "items": [value.to_dict() for value in values],
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_headcount_requisition(
    body: RequisitionCreateRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CREATE),
) -> dict[str, object]:
    """Create or replay one own-tenant requisition through HR or employer IAM."""
    now = datetime.now(timezone.utc)
    stable_id = hashlib.sha3_256(
        f"{context.tenant_id}:{idempotency_key}".encode("utf-8")
    ).hexdigest()[:24].upper()
    requisition = HeadcountRequisition(
        tenant_id=context.tenant_id,
        requisition_id=f"REQ-{stable_id}",
        department_id=body.department_id,
        position_title=body.position_title,
        employment_type=body.employment_type,
        work_location=body.work_location,
        headcount=body.headcount,
        business_justification=body.business_justification,
        requested_by_principal_id=context.identity.identity_id,
    )
    value = _transaction(lambda registry, session: registry.create_or_replay(
        requisition, idempotency_key=idempotency_key,
        actor_principal_id=context.identity.identity_id,
        occurred_at=now, session=session,
    ))
    return value.to_dict()


@router.post("/{requisition_id}/submit")
async def submit_headcount_requisition(
    requisition_id: str,
    body: RequisitionSubmitRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_CREATE),
) -> dict[str, object]:
    """Submit a revision-checked requisition as its authorized maker."""
    now = datetime.now(timezone.utc)
    request_fingerprint = _request_fingerprint(
        tenant_id=context.tenant_id, requisition_id=requisition_id,
        actor_principal_id=context.identity.identity_id, action="SUBMITTED",
        idempotency_key=idempotency_key, payload=body.model_dump(),
    )
    def submit(registry: HeadcountRequisitionRegistry, session: Any):
        replay = registry.replay_transition(
            tenant_id=context.tenant_id, idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint, session=session,
        )
        if replay is not None:
            return replay
        current = registry.get(
            tenant_id=context.tenant_id, requisition_id=requisition_id, session=session,
        )
        updated = current.submit(
            actor_principal_id=context.identity.identity_id,
            submitted_at=now, expected_revision=body.expected_revision,
        )
        return registry.transition(
            tenant_id=context.tenant_id, requisition_id=requisition_id,
            expected_revision=body.expected_revision, updated=updated,
            action="SUBMITTED", actor_principal_id=context.identity.identity_id,
            idempotency_key=idempotency_key, request_fingerprint=request_fingerprint,
            occurred_at=now, session=session,
        )
    return _transaction(submit).to_dict()


@router.post("/{requisition_id}/decision")
async def decide_headcount_requisition(
    requisition_id: str,
    body: RequisitionDecisionRequest,
    idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=160),
    context: TenantAuthorizationContext = Depends(_DECIDE),
) -> dict[str, object]:
    """Record an independently authorized decision; the domain rejects self-approval."""
    now = datetime.now(timezone.utc)
    request_fingerprint = _request_fingerprint(
        tenant_id=context.tenant_id, requisition_id=requisition_id,
        actor_principal_id=context.identity.identity_id, action=body.decision,
        idempotency_key=idempotency_key, payload=body.model_dump(),
    )
    def decide(registry: HeadcountRequisitionRegistry, session: Any):
        replay = registry.replay_transition(
            tenant_id=context.tenant_id, idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint, session=session,
        )
        if replay is not None:
            return replay
        current = registry.get(
            tenant_id=context.tenant_id, requisition_id=requisition_id, session=session,
        )
        approval = HeadcountApproval(
            decision_id=f"HCA-{uuid.uuid4().hex.upper()}",
            actor_principal_id=context.identity.identity_id,
            decision=RequisitionDecision(body.decision),
            reason=body.reason,
            decided_at=now,
        )
        updated = current.decide(approval, expected_revision=body.expected_revision)
        return registry.transition(
            tenant_id=context.tenant_id, requisition_id=requisition_id,
            expected_revision=body.expected_revision, updated=updated,
            action=body.decision, actor_principal_id=context.identity.identity_id,
            idempotency_key=idempotency_key, request_fingerprint=request_fingerprint,
            occurred_at=now, session=session,
        )
    return _transaction(decide).to_dict()


__all__ = [
    "router", "RequisitionCreateRequest", "RequisitionSubmitRequest",
    "RequisitionDecisionRequest",
]


# ARTIFACT: headcount_requisition_router.py
# VERSION: v1.3.0-SAFE-MY-WORK-PROJECTION
# AUTHORITY BOUNDARY: Existing exact-tenant EOS IAM; separately assigned platform-employer permissions apply only to canonical WILSY. Customer HR still requires active HR entitlement. No offer acceptance, employee admission, IAM provisioning, payroll, payment, execution, settlement, or entitlement grant.
# TENANT POSTURE: Authenticated exact tenant scope on every read, command, replay, and aggregate lookup; platform-employer pair selection is exact-WILSY only.
# FAIL-CLOSED POSTURE: Missing authority, entitlement, stale revision, duplicate replay, transaction failure, or invalid request never reports success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
