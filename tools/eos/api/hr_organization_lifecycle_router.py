"""TITLE: WILSY OS Governed Department Lifecycle HTTP Authority
VERSION: v1.0.0-M03-HR03-GOVERNED-DEPARTMENT-LIFECYCLE
AUTHORITY: WILSY OS Core Governance
EPITOME: Exact-tenant amendment, reorganization, retirement, impact, historical versions and source-owned productivity with independent checker decisions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/hr_organization_lifecycle_router.py
COLLABORATION / OWNERSHIP: WILSY OS HR Organization / Python EOS engineering
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0-M03-HR03-GOVERNED-DEPARTMENT-LIFECYCLE adds governed source, consumer and evidence contracts without expanding IAM grants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Bounded readback and event labels; no personnel/financial secrets, no fabricated external entity verification.
TENANT BOUNDARY: Exact authenticated EOS tenant; no root or Owner fallback.
AUTHORITY BOUNDARY: EOS source grants are separately required; maker and checker cannot be the same principal.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS exclusively.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from . import hr_workforce_directory_router as org
from .tenant_authorization_http import TenantAuthorizationContext
from tools.eos.kernel.db import get_client, get_database

router = APIRouter(prefix="/api/hr/workforce/structure", tags=["hr-organization-lifecycle"])
_CHANGES = "hr_organization_change_proposals"
_VERSIONS = "hr_organization_versions"
_CHANGE_EVENTS = "hr_organization_change_events"
_OBSERVATIONS = "hr_organization_productivity_observations"
_LIMIT = 200


class ChangeDraft(BaseModel):
    """Bounded change request; never mutates approved organization directly."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    change_type: Literal["AMEND", "RETIRE"]
    name: str | None = Field(default=None, min_length=2, max_length=180)
    parent_id: str | None = Field(default=None, min_length=1, max_length=120)
    clear_parent: bool = False
    effective_from: date
    reason: str = Field(min_length=5, max_length=2000)


class ProductivityObservation(BaseModel):
    """Bounded, identifier-free client experience evidence; not an audit result."""
    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(min_length=12, max_length=100,
                            pattern=r"^[A-Za-z0-9_-]+$")
    event: Literal[
        "FORM_OPENED", "CATALOG_SELECTED", "MANUAL_FIELD_EDITED",
        "VALIDATION_FAILED", "DRAFT_VERIFIED",
    ]
    count: int = Field(default=1, ge=1, le=20, strict=True)
    elapsed_ms: int | None = Field(default=None, ge=0, le=3600000, strict=True)


class ChangeDecision(BaseModel):
    """Independent checker decision bound to one expected proposal revision."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    expected_revision: int = Field(ge=1, strict=True)
    decision: Literal["APPROVE", "REJECT"]
    reason: str = Field(min_length=5, max_length=2000)


class ExpectedRevision(BaseModel):
    """Revision precondition required for maker submission."""
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1, strict=True)


def _now() -> str:
    """Return a timezone-aware UTC audit timestamp; no business mutation."""
    return datetime.now(timezone.utc).isoformat()


def _coll(db: Any, name: str):
    """Return a majority-consistent collection; callers must apply exact tenant filters."""
    return db.get_collection(
        name, read_concern=ReadConcern("majority"),
        write_concern=WriteConcern(w="majority", j=True),
    )


def _transaction(callback):
    """Own a majority Mongo transaction over proposals, versions and audit events; fail closed."""
    client, db = get_client(), get_database()
    if client is None or db is None:
        raise HTTPException(503, "ORGANIZATION_DATABASE_UNAVAILABLE")
    try:
        records = org._org_collection(db, org._ORG_COLLECTION)
        changes = _coll(db, _CHANGES)
        versions = _coll(db, _VERSIONS)
        events = _coll(db, _CHANGE_EVENTS)
        changes.create_index([("tenant_id", 1), ("change_id", 1)], unique=True)
        versions.create_index([("tenant_id", 1), ("record_id", 1), ("revision", 1)], unique=True)
        events.create_index([("tenant_id", 1), ("actor_id", 1), ("key", 1)], unique=True)
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(records, changes, versions, events, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HTTPException:
        raise
    except DuplicateKeyError as error:
        raise HTTPException(409, "ORGANIZATION_CONCURRENT_CONFLICT") from error
    except Exception as error:
        raise HTTPException(503, "ORGANIZATION_CHANGE_TRANSACTION_UNAVAILABLE") from error


def _run_command(callback, *, tenant, actor, key, operation, payload):
    """Transactional replay of an identical actor-scoped command key."""
    fingerprint = org._org_fingerprint(
        tenant=tenant, actor=actor, key=key, command=operation, payload=payload,
    )

    def run(records, changes, versions, events, tx):
        identity = {"tenant_id": tenant, "actor_id": actor, "key": key}
        prior = events.find_one(identity, session=tx)
        if prior is not None:
            if prior.get("fingerprint") != fingerprint or "response" not in prior:
                raise HTTPException(409, "ORGANIZATION_IDEMPOTENCY_CONFLICT")
            return prior["response"]
        response = callback(records, changes, versions, events, tx)
        updated = events.update_one(identity, {
            "$set": {"fingerprint": fingerprint, "response": response},
        }, session=tx)
        if updated.matched_count != 1:
            raise HTTPException(503, "ORGANIZATION_COMMAND_EVIDENCE_MISSING")
        return response

    return _transaction(run)


def _record(records, tenant: str, record_id: str, tx):
    """Resolve an exact-tenant department in a source transaction or deny opaque absence."""
    row = records.find_one({"tenant_id": tenant, "kind": "DEPARTMENT",
                            "record_id": record_id}, session=tx)
    if row is None:
        raise HTTPException(404, "ORGANIZATION_NOT_FOUND")
    return row


def _impact(records, tenant: str, record_id: str, tx=None):
    """Inspect bounded approved child departments and positions; block unverified staffing retirement."""
    cursor = records.find({
        "tenant_id": tenant, "status": "APPROVED",
        "$or": [{"parent_id": record_id, "kind": "DEPARTMENT"},
                {"department_id": record_id, "kind": "POSITION"}],
    }, {"_id": 0, "kind": 1, "record_id": 1, "name": 1}).limit(_LIMIT + 1)
    if tx is not None:
        cursor = records.find({
            "tenant_id": tenant, "status": "APPROVED",
            "$or": [{"parent_id": record_id, "kind": "DEPARTMENT"},
                    {"department_id": record_id, "kind": "POSITION"}],
        }, {"_id": 0, "kind": 1, "record_id": 1, "name": 1}, session=tx).limit(_LIMIT + 1)
    rows = list(cursor)
    if len(rows) > _LIMIT:
        raise HTTPException(503, "ORGANIZATION_IMPACT_BOUND_EXCEEDED")
    return {
        "schema": "WILSY-HR-ORGANIZATION-IMPACT/V1",
        "dependent_departments": [r["record_id"] for r in rows if r["kind"] == "DEPARTMENT"],
        "dependent_positions": [r["record_id"] for r in rows if r["kind"] == "POSITION"],
        # Current workforce employee assignments are not yet established as
        # canonical department-ID references. No "zero employees" inference.
        "staffing_dependency_status": "NOT_CERTIFIED",
        "retirement_blocker_reasons": (
            ["APPROVED_DEPENDENT_STRUCTURE"] if rows else []
        ) + ["EMPLOYEE_ASSIGNMENT_LINKAGE_NOT_CERTIFIED"],
        "retirement_blocked": True,
    }


def _safe_change(row):
    """Project non-sensitive change data for authorized same-tenant consumers only."""
    return {k: row.get(k) for k in (
        "change_id", "record_id", "change_type", "status", "revision",
        "effective_from", "name", "parent_id", "reason", "decision_reason",
    )}


def _event(events, tenant, actor, key, action, change, tx):
    """Persist an actor-scoped immutable change event in the transaction."""
    events.insert_one({
        "tenant_id": tenant, "actor_id": actor, "key": key,
        "action": action, "change_id": change["change_id"],
        "record_id": change["record_id"], "occurred_at": _now(),
        "revision": change["revision"],
    }, session=tx)


@router.get("/changes")
def list_department_changes(
    auth: TenantAuthorizationContext = Depends(org._ORG_READ),
):
    """Read bounded exact-tenant change queue with maker flags, never other actor identities."""
    db = get_database()
    if db is None:
        raise HTTPException(503, "ORGANIZATION_DATABASE_UNAVAILABLE")
    rows = list(_coll(db, _CHANGES).find(
        {"tenant_id": auth.tenant_id},
        {"_id": 0, "change_id": 1, "record_id": 1, "change_type": 1,
         "status": 1, "revision": 1, "effective_from": 1,
         "name": 1, "parent_id": 1, "reason": 1, "decision_reason": 1,
         "created_by": 1, "submitted_by": 1},
    ).sort("created_at", -1).limit(_LIMIT + 1))
    if len(rows) > _LIMIT:
        raise HTTPException(503, "ORGANIZATION_CHANGE_RESULT_BOUND_EXCEEDED")
    return {
        "schema": "WILSY-HR-ORGANIZATION-CHANGES/V1",
        "tenant_id": auth.tenant_id, "source": "EOS_HR_ORGANIZATION_CHANGES",
        "count": len(rows),
        "items": [
            {**_safe_change(row), "current_principal_is_maker":
             auth.identity.identity_id in (row.get("created_by"), row.get("submitted_by"))}
            for row in rows
        ],
    }


@router.get("/departments/{record_id}/impact")
def read_department_impact(
    record_id: str,
    auth: TenantAuthorizationContext = Depends(org._ORG_READ),
):
    """Authorize and inspect source-related dependents without leaking employee PII."""
    db = get_database()
    if db is None:
        raise HTTPException(503, "ORGANIZATION_DATABASE_UNAVAILABLE")
    records = org._org_collection(db, org._ORG_COLLECTION)
    if records.find_one({"tenant_id": auth.tenant_id, "kind": "DEPARTMENT",
                         "record_id": record_id}, {"_id": 1}) is None:
        raise HTTPException(404, "ORGANIZATION_NOT_FOUND")
    return {"tenant_id": auth.tenant_id, "record_id": record_id,
            **_impact(records, auth.tenant_id, record_id)}


@router.get("/departments/{record_id}/history")
def read_department_history(
    record_id: str, auth: TenantAuthorizationContext = Depends(org._ORG_READ),
):
    """Return bounded effective-version evidence for an authorized tenant department."""
    db = get_database()
    if db is None:
        raise HTTPException(503, "ORGANIZATION_DATABASE_UNAVAILABLE")
    records = org._org_collection(db, org._ORG_COLLECTION)
    if records.find_one({"tenant_id": auth.tenant_id, "kind": "DEPARTMENT",
                         "record_id": record_id}, {"_id": 1}) is None:
        raise HTTPException(404, "ORGANIZATION_NOT_FOUND")
    rows = list(_coll(db, _VERSIONS).find(
        {"tenant_id": auth.tenant_id, "record_id": record_id},
        {"_id": 0, "revision": 1, "name": 1, "parent_id": 1,
         "effective_from": 1, "status": 1, "recorded_at": 1},
    ).sort("revision", 1).limit(_LIMIT + 1))
    if len(rows) > _LIMIT:
        raise HTTPException(503, "ORGANIZATION_HISTORY_BOUND_EXCEEDED")
    return {"schema": "WILSY-HR-ORGANIZATION-HISTORY/V1", "tenant_id": auth.tenant_id,
            "record_id": record_id, "items": rows, "count": len(rows)}


@router.get("/departments/{record_id}/as-of")
def read_department_at_date(
    record_id: str, on: date = Query(...),
    auth: TenantAuthorizationContext = Depends(org._ORG_READ),
):
    """Bounded historical snapshot; never imply a missing older version exists."""
    db = get_database()
    if db is None:
        raise HTTPException(503, "ORGANIZATION_DATABASE_UNAVAILABLE")
    record = org._org_collection(db, org._ORG_COLLECTION).find_one(
        {"tenant_id": auth.tenant_id, "kind": "DEPARTMENT",
         "record_id": record_id}, {"_id": 0},
    )
    if record is None:
        raise HTTPException(404, "ORGANIZATION_NOT_FOUND")
    rows = list(_coll(db, _VERSIONS).find(
        {"tenant_id": auth.tenant_id, "record_id": record_id},
        {"_id": 0, "revision": 1, "name": 1, "parent_id": 1,
         "status": 1, "effective_from": 1},
    ).limit(_LIMIT + 1))
    if len(rows) > _LIMIT:
        raise HTTPException(503, "ORGANIZATION_HISTORY_BOUND_EXCEEDED")
    if not rows:
        rows = [{k: record.get(k) for k in (
            "revision", "name", "parent_id", "status", "effective_from",
        )}]
    applicable = [row for row in rows
                  if str(row.get("effective_from") or "") <= on.isoformat()]
    if not applicable:
        raise HTTPException(404, "ORGANIZATION_NO_VERIFIED_VERSION_FOR_DATE")
    chosen = max(applicable, key=lambda row: (
        str(row.get("effective_from") or ""), row["revision"],
    ))
    return {"schema": "WILSY-HR-ORGANIZATION-AS-OF/V1",
            "tenant_id": auth.tenant_id, "record_id": record_id,
            "as_of": on.isoformat(), "record": chosen}


@router.post("/departments/{record_id}/changes", status_code=201)
def propose_department_change(
    record_id: str, body: ChangeDraft,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_CREATE),
):
    """Create idempotent audited draft against an approved source revision; no approval."""
    if body.clear_parent and body.parent_id is not None:
        raise HTTPException(422, "ORGANIZATION_PARENT_CONFLICT")
    if body.change_type == "RETIRE" and (body.name is not None
                                        or body.parent_id is not None or body.clear_parent):
        raise HTTPException(422, "ORGANIZATION_RETIREMENT_FIELDS_INVALID")
    if body.change_type == "AMEND" and body.name is None and body.parent_id is None and not body.clear_parent:
        raise HTTPException(422, "ORGANIZATION_CHANGE_FIELDS_REQUIRED")
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    payload = body.model_dump(mode="json")
    fingerprint = org._org_fingerprint(tenant=tenant, actor=actor, key=key,
                                     command="CHANGE_DRAFT", payload={"record_id": record_id, **payload})
    def apply(records, changes, versions, events, tx):
        prior = changes.find_one({"tenant_id": tenant, "actor_id": actor,
                                  "idempotency_key": key}, session=tx)
        if prior is not None:
            if prior.get("fingerprint") != fingerprint:
                raise HTTPException(409, "ORGANIZATION_IDEMPOTENCY_CONFLICT")
            return {"schema": "WILSY-HR-ORGANIZATION-CHANGE/V1",
                    "tenant_id": tenant, "change": _safe_change(prior)}
        current = _record(records, tenant, record_id, tx)
        if current["status"] != "APPROVED":
            raise HTTPException(409, "ORGANIZATION_APPROVED_RECORD_REQUIRED")
        if payload["effective_from"] < str(current.get("effective_from") or ""):
            raise HTTPException(409, "ORGANIZATION_BACKDATED_CHANGE_NOT_SUPPORTED")
        change = {
            **payload, "tenant_id": tenant, "record_id": record_id,
            "change_id": uuid4().hex, "status": "DRAFT", "revision": 1,
            "base_revision": current["revision"], "created_by": actor,
            "submitted_by": None, "decided_by": None,
            "idempotency_key": key, "fingerprint": fingerprint,
            "created_at": _now(),
        }
        changes.insert_one(change, session=tx)
        _event(events, tenant, actor, key, "CHANGE_DRAFT", change, tx)
        return {"schema": "WILSY-HR-ORGANIZATION-CHANGE/V1",
                "tenant_id": tenant, "change": _safe_change(change)}
    return _run_command(apply, tenant=tenant, actor=actor, key=key,
        operation="CHANGE_DRAFT", payload={"record_id": record_id, **payload})


@router.post("/departments/{record_id}/changes/{change_id}/submit")
def submit_department_change(
    record_id: str, change_id: str, body: ExpectedRevision,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_CREATE),
):
    """Allow the original maker to submit a proposal with optimistic concurrency."""
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    def apply(records, changes, versions, events, tx):
        change = changes.find_one({"tenant_id": tenant, "record_id": record_id,
                                   "change_id": change_id}, session=tx)
        if change is None:
            raise HTTPException(404, "ORGANIZATION_CHANGE_NOT_FOUND")
        if change["created_by"] != actor:
            raise HTTPException(403, "ORGANIZATION_MAKER_REQUIRED")
        if change["status"] != "DRAFT" or change["revision"] != body.expected_revision:
            raise HTTPException(409, "ORGANIZATION_REVISION_CONFLICT")
        updated = changes.find_one_and_update({
            "tenant_id": tenant, "change_id": change_id,
            "status": "DRAFT", "revision": body.expected_revision,
        }, {"$set": {"status": "SUBMITTED", "submitted_by": actor,
                     "submitted_at": _now()}, "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER, session=tx)
        if updated is None:
            raise HTTPException(409, "ORGANIZATION_REVISION_CONFLICT")
        _event(events, tenant, actor, key, "CHANGE_SUBMIT", updated, tx)
        return {"schema": "WILSY-HR-ORGANIZATION-CHANGE/V1",
                "tenant_id": tenant, "change": _safe_change(updated)}
    return _run_command(apply, tenant=tenant, actor=actor, key=key,
        operation="CHANGE_SUBMIT", payload={"record_id": record_id, "change_id": change_id,
                                            "expected_revision": body.expected_revision})


@router.post("/departments/{record_id}/changes/{change_id}/decision")
def decide_department_change(
    record_id: str, change_id: str, body: ChangeDecision,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_DECIDE),
):
    """Require a distinct checker; apply or schedule change atomically after impact checks."""
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    def apply(records, changes, versions, events, tx):
        change = changes.find_one({"tenant_id": tenant, "record_id": record_id,
                                   "change_id": change_id}, session=tx)
        if change is None:
            raise HTTPException(404, "ORGANIZATION_CHANGE_NOT_FOUND")
        if actor in (change["created_by"], change.get("submitted_by")):
            raise HTTPException(403, "ORGANIZATION_MAKER_CANNOT_APPROVE")
        if change["status"] != "SUBMITTED" or change["revision"] != body.expected_revision:
            raise HTTPException(409, "ORGANIZATION_REVISION_CONFLICT")
        current = _record(records, tenant, record_id, tx)
        if current["status"] != "APPROVED" or current["revision"] != change["base_revision"]:
            raise HTTPException(409, "ORGANIZATION_SOURCE_CHANGED")
        if change["effective_from"] < str(current.get("effective_from") or ""):
            raise HTTPException(409, "ORGANIZATION_BACKDATED_CHANGE_NOT_SUPPORTED")
        if body.decision == "APPROVE":
            if change["change_type"] == "RETIRE" and _impact(records, tenant, record_id, tx)["retirement_blocked"]:
                raise HTTPException(409, "ORGANIZATION_RETIREMENT_HAS_DEPENDENCIES")
            if change["change_type"] == "AMEND":
                _check_hierarchy(records, current, change, tenant, tx)
        scheduled = body.decision == "APPROVE" and change["effective_from"] > date.today().isoformat()
        decision_status = ("APPROVED_SCHEDULED" if scheduled else "APPROVED") if body.decision == "APPROVE" else "REJECTED"
        if body.decision == "APPROVE" and not scheduled:
            _apply_change(records, versions, current, change, tenant, tx)
        updated = changes.find_one_and_update({
            "tenant_id": tenant, "change_id": change_id,
            "status": "SUBMITTED", "revision": body.expected_revision,
        }, {"$set": {"status": decision_status, "decided_by": actor,
                     "decision_reason": body.reason, "decided_at": _now()},
            "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER, session=tx)
        if updated is None:
            raise HTTPException(409, "ORGANIZATION_REVISION_CONFLICT")
        _event(events, tenant, actor, key, "CHANGE_DECIDE_" + body.decision, updated, tx)
        return {"schema": "WILSY-HR-ORGANIZATION-CHANGE/V1",
                "tenant_id": tenant, "change": _safe_change(updated)}
    return _run_command(apply, tenant=tenant, actor=actor, key=key,
        operation="CHANGE_DECIDE", payload={"record_id": record_id, "change_id": change_id,
                                            **body.model_dump()})


def _check_hierarchy(records, current, change, tenant, tx):
    """Reject cycles and nonapproved parents on decision AND activation."""
    target = change.get("parent_id")
    if change.get("clear_parent") or not target:
        return
    if target == current["record_id"]:
        raise HTTPException(422, "ORGANIZATION_SELF_REFERENCE")
    ancestor = target
    for _ in range(64):
        row = records.find_one({
            "tenant_id": tenant, "kind": "DEPARTMENT",
            "record_id": ancestor, "status": "APPROVED",
        }, session=tx)
        if row is None:
            raise HTTPException(409, "ORGANIZATION_PARENT_NOT_APPROVED")
        ancestor = row.get("parent_id")
        if ancestor == current["record_id"]:
            raise HTTPException(409, "ORGANIZATION_PARENT_CYCLE")
        if not ancestor:
            return
    raise HTTPException(409, "ORGANIZATION_HIERARCHY_DEPTH_EXCEEDED")


def _apply_change(records, versions, current, change, tenant, tx):
    """Persist previous and new effective versions with a compare-and-set source update."""
    snapshot = {k: current.get(k) for k in ("name", "parent_id", "effective_from", "status")}
    if change["change_type"] == "AMEND":
        fields = {"name": change.get("name") or current["name"],
                  "parent_id": None if change.get("clear_parent") else (
                    change.get("parent_id") if change.get("parent_id") is not None
                    else current.get("parent_id")),
                  "effective_from": change["effective_from"]}
    else:
        fields = {"status": "RETIRED", "effective_from": change["effective_from"]}
    next_revision = current["revision"] + 1
    versions.update_one({"tenant_id": tenant, "record_id": current["record_id"],
                         "revision": current["revision"]},
                        {"$setOnInsert": {"tenant_id": tenant, "record_id": current["record_id"],
                          "revision": current["revision"], **snapshot, "recorded_at": _now()}},
                        upsert=True, session=tx)
    updated = records.find_one_and_update({
        "tenant_id": tenant, "kind": "DEPARTMENT",
        "record_id": current["record_id"], "revision": current["revision"],
        "status": "APPROVED",
    }, {"$set": fields, "$inc": {"revision": 1}},
        return_document=ReturnDocument.AFTER, session=tx)
    if updated is None:
        raise HTTPException(409, "ORGANIZATION_SOURCE_CHANGED")
    versions.insert_one({
        "tenant_id": tenant, "record_id": current["record_id"],
        "revision": next_revision, "name": updated["name"],
        "parent_id": updated.get("parent_id"), "status": updated["status"],
        "effective_from": updated["effective_from"], "recorded_at": _now(),
    }, session=tx)


@router.post("/departments/{record_id}/changes/{change_id}/activate")
def activate_due_department_change(
    record_id: str, change_id: str,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_DECIDE),
):
    """Explicit guarded activation for approved future-dated changes; no early mutations."""
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    def apply(records, changes, versions, events, tx):
        change = changes.find_one({"tenant_id": tenant, "record_id": record_id,
                                   "change_id": change_id}, session=tx)
        if change is None:
            raise HTTPException(404, "ORGANIZATION_CHANGE_NOT_FOUND")
        if actor in (change["created_by"], change.get("submitted_by")):
            raise HTTPException(403, "ORGANIZATION_MAKER_CANNOT_APPROVE")
        if change["status"] != "APPROVED_SCHEDULED":
            raise HTTPException(409, "ORGANIZATION_CHANGE_NOT_SCHEDULED")
        if change["effective_from"] > date.today().isoformat():
            raise HTTPException(409, "ORGANIZATION_EFFECTIVE_DATE_NOT_DUE")
        current = _record(records, tenant, record_id, tx)
        if current["revision"] != change["base_revision"] or current["status"] != "APPROVED":
            raise HTTPException(409, "ORGANIZATION_SOURCE_CHANGED")
        if change["effective_from"] < str(current.get("effective_from") or ""):
            raise HTTPException(409, "ORGANIZATION_BACKDATED_CHANGE_NOT_SUPPORTED")
        if change["change_type"] == "RETIRE" and _impact(records, tenant, record_id, tx)["retirement_blocked"]:
            raise HTTPException(409, "ORGANIZATION_RETIREMENT_HAS_DEPENDENCIES")
        if change["change_type"] == "AMEND":
            _check_hierarchy(records, current, change, tenant, tx)
        _apply_change(records, versions, current, change, tenant, tx)
        updated = changes.find_one_and_update({
            "tenant_id": tenant, "change_id": change_id, "status": "APPROVED_SCHEDULED",
        }, {"$set": {"status": "ACTIVATED", "activated_at": _now()},
            "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER, session=tx)
        if updated is None:
            raise HTTPException(409, "ORGANIZATION_SOURCE_CHANGED")
        _event(events, tenant, actor, key, "CHANGE_ACTIVATE", updated, tx)
        return {"schema": "WILSY-HR-ORGANIZATION-CHANGE/V1",
                "tenant_id": tenant, "change": _safe_change(updated)}
    return _run_command(apply, tenant=tenant, actor=actor, key=key,
        operation="CHANGE_ACTIVATE", payload={"record_id": record_id, "change_id": change_id})


@router.post("/productivity/observations", status_code=201)
def report_organization_experience(
    body: ProductivityObservation,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    auth: TenantAuthorizationContext = Depends(org._ORG_CREATE),
):
    """Record opt-in product usage counts only; never collect values or identities."""
    db = get_database()
    if db is None:
        raise HTTPException(503, "ORGANIZATION_DATABASE_UNAVAILABLE")
    tenant, actor = auth.tenant_id, auth.identity.identity_id
    fingerprint = org._org_fingerprint(
        tenant=tenant, actor=actor, key=key, command="UX_OBSERVATION",
        payload=body.model_dump(),
    )
    try:
        observations = _coll(db, _OBSERVATIONS)
        observations.create_index([("tenant_id", 1), ("actor_id", 1), ("key", 1)],
                                  unique=True)
        previous = observations.find_one(
            {"tenant_id": tenant, "actor_id": actor, "key": key},
        )
        if previous is not None:
            if previous.get("fingerprint") != fingerprint:
                raise HTTPException(409, "ORGANIZATION_PRODUCTIVITY_CONFLICT")
            return {"schema": "WILSY-HR-ORGANIZATION-OBSERVATION/V1",
                    "tenant_id": tenant, "accepted": True}
        observations.insert_one({
            "tenant_id": tenant, "actor_id": actor, "key": key,
            "fingerprint": fingerprint, "session_id": body.session_id,
            "event": body.event, "count": body.count,
            "elapsed_ms": body.elapsed_ms, "recorded_at": _now(),
            "source": "CLIENT_REPORTED",
        })
        return {"schema": "WILSY-HR-ORGANIZATION-OBSERVATION/V1",
                "tenant_id": tenant, "accepted": True}
    except HTTPException:
        raise
    except DuplicateKeyError as error:
        raise HTTPException(409, "ORGANIZATION_PRODUCTIVITY_CONFLICT") from error
    except Exception as error:
        raise HTTPException(503, "ORGANIZATION_PRODUCTIVITY_UNAVAILABLE") from error


@router.get("/productivity")
def read_organization_productivity(
    auth: TenantAuthorizationContext = Depends(org._ORG_READ),
):
    """Source event timing, not inferred business outcomes or client-reported accuracy."""
    db = get_database()
    if db is None:
        raise HTTPException(503, "ORGANIZATION_DATABASE_UNAVAILABLE")
    rows = list(_coll(db, _CHANGE_EVENTS).find(
        {"tenant_id": auth.tenant_id},
        {"_id": 0, "change_id": 1, "action": 1, "occurred_at": 1},
    ).sort("occurred_at", -1).limit(_LIMIT + 1))
    recent_events_truncated = len(rows) > _LIMIT
    rows = rows[:_LIMIT]
    drafts = {r["change_id"]: r["occurred_at"] for r in rows if r["action"] == "CHANGE_DRAFT"}
    elapsed = []
    for item in rows:
        if item["action"] == "CHANGE_DECIDE_APPROVE" and item["change_id"] in drafts:
            seconds = (datetime.fromisoformat(item["occurred_at"])
                       - datetime.fromisoformat(drafts[item["change_id"]])).total_seconds()
            if seconds >= 0:
                elapsed.append(seconds)
    try:
        summary_rows = list(_coll(db, _OBSERVATIONS).aggregate([
            {"$match": {"tenant_id": auth.tenant_id}},
            {"$group": {
                "_id": "$event", "count": {"$sum": "$count"},
                "samples": {"$sum": 1}, "mean_elapsed_ms": {"$avg": "$elapsed_ms"},
            }},
            {"$limit": 6},
        ]))
    except Exception as error:
        raise HTTPException(503, "ORGANIZATION_PRODUCTIVITY_UNAVAILABLE") from error
    allowed_events = {
        "FORM_OPENED", "CATALOG_SELECTED", "MANUAL_FIELD_EDITED",
        "VALIDATION_FAILED", "DRAFT_VERIFIED",
    }
    if len(summary_rows) > len(allowed_events) or any(
        row["_id"] not in allowed_events for row in summary_rows
    ):
        raise HTTPException(503, "ORGANIZATION_PRODUCTIVITY_INVALID_AGGREGATE")
    observed = {name: 0 for name in allowed_events}
    sample_count = 0
    mean_form_duration = None
    for row in summary_rows:
        observed[row["_id"]] = int(row["count"])
        sample_count += int(row["samples"])
        if row["_id"] == "DRAFT_VERIFIED" and row.get("mean_elapsed_ms") is not None:
            mean_form_duration = round(row["mean_elapsed_ms"] / 1000, 2)
    return {
        "client_report_source": "CLIENT_REPORTED",
        "client_observation_sample": sample_count,
        "client_observed": observed,
        "client_mean_form_to_verified_seconds": mean_form_duration,
        "schema": "WILSY-HR-ORGANIZATION-PRODUCTIVITY/V1",
        "tenant_id": auth.tenant_id, "source": "EOS_ORGANIZATION_CHANGE_EVENTS",
        "bounded_events": len(rows),
        "recent_events_truncated": recent_events_truncated,
        "change_drafts": sum(r["action"] == "CHANGE_DRAFT" for r in rows),
        "approved_changes": sum(r["action"] == "CHANGE_DECIDE_APPROVE" for r in rows),
        "rejected_changes": sum(r["action"] == "CHANGE_DECIDE_REJECT" for r in rows),
        "mean_draft_to_decision_seconds": round(sum(elapsed) / len(elapsed), 2) if elapsed else None,
        "measured_decision_sample": len(elapsed),
        "client_completion_time": None, "manual_field_count": None,
        "validation_failure_rate": None, "accessibility_certified": False,
    }

# ARTIFACT: tools/eos/api/hr_organization_lifecycle_router.py
# VERSION: v1.0.0-M03-HR03-GOVERNED-DEPARTMENT-LIFECYCLE
# AUTHORITY BOUNDARY: Exact-tenant EOS authority and regression evidence; no grants or financial execution.
# TENANT POSTURE: Exact authorized tenant only; no cross-tenant records, Owner or root fallback.
# FAIL-CLOSED POSTURE: Missing or contradictory evidence is denied/unavailable, never approved.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
