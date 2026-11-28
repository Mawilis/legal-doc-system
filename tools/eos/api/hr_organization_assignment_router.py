"""TITLE: WILSY OS Governed Employee Organization Assignment Authority
VERSION: v1.0.0-M03-HR03-GOVERNED-ASSIGNMENTS
AUTHORITY: Python EOS HR employee-relation and organization source owners.
EPITOME: Establish exact-tenant, effective-dated employee→position→department
         assignment proposals with independent review, source CAS and history.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/hr_organization_assignment_router.py
COLLABORATION / OWNERSHIP: HR employee relation and organization IAM; canonical
         legacy employee employment.department remains separate and unmodified.
CERTIFICATION / UPDATE DATE: 2026-11-28
CHANGELOG: v1.0.0 creates source-owned HR graph assignment registry and commands.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque employee IDs and position references only.
TENANT BOUNDARY: Current authorized tenant, never selector or Owner fallback.
AUTHORITY BOUNDARY: Distinct create and decision, conjunctive HR relation IAM.
TRANSACTION BOUNDARY: Snapshot Mongo transactions and majority durability.
FINANCIAL AUTHORITY BOUNDARY: No payroll, budget or employment admission.
FAIL-CLOSED POSTURE: No orphaned or cross-tenant assignments; no name-only match.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal
from uuid import uuid4
import re

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

from .hr_workforce_directory_router import _ORG_COLLECTION, _ORG_READ, _ORG_DECIDE
from .tenant_authorization_http import RequireTenantAuthorization, TenantAuthorizationContext
from .hr_workforce_directory_router import _org_fingerprint
from tools.eos.kernel.db import get_client, get_database

router = APIRouter(prefix="/api/hr/workforce/assignments", tags=["hr-organization-assignments"])
_MAKER = RequireTenantAuthorization("hr:employee_relation:write", "hr_employee_relation_write")
_PROPOSALS = "hr_organization_assignment_proposals"
_ASSIGNMENTS = "hr_organization_assignments"
_VERSIONS = "hr_organization_assignment_versions"
_EVENTS = "hr_organization_assignment_events"
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,179}\Z")
_MAX = 200


class AssignmentDraft(BaseModel):
    """A proposed change, never a directly admitted or modified employee."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    employee_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,179}$")
    position_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
    effective_from: date
    reason: str = Field(min_length=5, max_length=2000)


class AssignmentRevision(BaseModel):
    """Optimistic source revision supplied for an exact proposal."""
    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(strict=True, ge=1)


class AssignmentDecision(AssignmentRevision):
    """Independent reasoned checker disposition."""
    decision: Literal["APPROVE", "REJECT"]
    reason: str = Field(min_length=5, max_length=2000)


def _now() -> str:
    """Return UTC audit timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _collection(db: Any, name: str) -> Any:
    """Use majority durability; every query is additionally tenant-scoped."""
    return db.get_collection(name, read_concern=ReadConcern("majority"),
                             write_concern=WriteConcern(w="majority", j=True))


def _tx(callback):
    """Execute transaction atomically, never claim partial assignments."""
    client, db = get_client(), get_database()
    if client is None or db is None:
        raise HTTPException(503, "HR_ASSIGNMENT_SOURCE_UNAVAILABLE")
    try:
        proposed = _collection(db, _PROPOSALS)
        assigned = _collection(db, _ASSIGNMENTS)
        events = _collection(db, _EVENTS)
        versions = _collection(db, _VERSIONS)
        org = _collection(db, _ORG_COLLECTION)
        employees = _collection(db, "employees")
        proposed.create_index([("tenant_id", 1), ("proposal_id", 1)], unique=True)
        assigned.create_index([("tenant_id", 1), ("employee_id", 1)], unique=True)
        events.create_index([("tenant_id", 1), ("actor_id", 1), ("key", 1)], unique=True)
        versions.create_index([("tenant_id", 1), ("employee_id", 1), ("revision", 1)], unique=True)
        with client.start_session() as session:
            return session.with_transaction(
                lambda tx: callback(proposed, assigned, events, versions, org, employees, tx),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HTTPException:
        raise
    except DuplicateKeyError as exc:
        raise HTTPException(409, "HR_ASSIGNMENT_CONCURRENT_CONFLICT") from exc
    except Exception as exc:
        raise HTTPException(503, "HR_ASSIGNMENT_TRANSACTION_UNAVAILABLE") from exc


def _public(row):
    """Project opaque, authorized organizational relationship without employee PII."""
    return {key: row.get(key) for key in (
        "proposal_id", "employee_id", "position_id", "department_id",
        "status", "revision", "effective_from", "reason", "decision_reason",
        "base_revision",
    )}


def _verify_sources(org, employees, tenant, employee_id, position_id, tx):
    """Reject absent employee, nonapproved position/department and foreign tenant."""
    employee = employees.find_one({
        "tenantId": tenant, "employeeId": employee_id,
        "isActive": True, "deletedAt": None,
    }, {"_id": 1}, session=tx)
    if employee is None:
        raise HTTPException(404, "HR_ASSIGNMENT_EMPLOYEE_UNAVAILABLE")
    position = org.find_one({
        "tenant_id": tenant, "kind": "POSITION", "record_id": position_id,
        "status": "APPROVED",
    }, session=tx)
    if position is None:
        raise HTTPException(409, "HR_ASSIGNMENT_POSITION_NOT_APPROVED")
    department_id = position.get("department_id")
    department = org.find_one({
        "tenant_id": tenant, "kind": "DEPARTMENT", "record_id": department_id,
        "status": "APPROVED",
    }, session=tx)
    if department is None:
        raise HTTPException(409, "HR_ASSIGNMENT_DEPARTMENT_NOT_APPROVED")
    if position.get("effective_from", "") > date.today().isoformat() or (
        department.get("effective_from", "") > date.today().isoformat()
    ):
        raise HTTPException(409, "HR_ASSIGNMENT_STRUCTURE_NOT_EFFECTIVE")
    return department_id


def _command(tenant, actor, key, action, payload, callback):
    """Replay actor-scoped identical request only, inside source transaction."""
    if not isinstance(actor, str) or not actor.strip():
        raise HTTPException(503, "HR_ASSIGNMENT_ACTOR_UNVERIFIED")
    fingerprint = _org_fingerprint(
        tenant=tenant, actor=actor, key=key, command="ASSIGNMENT:" + action,
        payload=payload,
    )
    def apply(proposed, assigned, events, versions, org, employees, tx):
        identity = {"tenant_id": tenant, "actor_id": actor, "key": key}
        prior = events.find_one(identity, session=tx)
        if prior:
            if prior.get("fingerprint") != fingerprint:
                raise HTTPException(409, "HR_ASSIGNMENT_IDEMPOTENCY_CONFLICT")
            return prior["response"]
        response = callback(proposed, assigned, versions, org, employees, tx)
        events.insert_one({
            **identity, "action": action, "fingerprint": fingerprint,
            "response": response, "occurred_at": _now(),
        }, session=tx)
        return response
    return _tx(apply)


@router.get("")
def list_assignments(
    organization: TenantAuthorizationContext = Depends(_ORG_READ),
    workforce: TenantAuthorizationContext = Depends(_MAKER),
):
    """Read exact-tenant organizational assignment source, without PII."""
    if organization.tenant_id != workforce.tenant_id or (
        organization.identity.identity_id != workforce.identity.identity_id
    ):
        raise HTTPException(403, "HR_ASSIGNMENT_SCOPE_MISMATCH")
    db = get_database()
    if db is None:
        raise HTTPException(503, "HR_ASSIGNMENT_SOURCE_UNAVAILABLE")
    try:
        proposals = list(_collection(db, _PROPOSALS).find(
            {"tenant_id": organization.tenant_id},
            {"_id": 0, "proposal_id": 1, "employee_id": 1, "position_id": 1,
             "department_id": 1, "status": 1, "revision": 1,
             "effective_from": 1, "reason": 1, "decision_reason": 1,
             "created_by": 1, "submitted_by": 1},
        ).limit(_MAX + 1))
        current = list(_collection(db, _ASSIGNMENTS).find(
            {"tenant_id": organization.tenant_id},
            {"_id": 0, "employee_id": 1, "position_id": 1,
             "department_id": 1, "revision": 1, "effective_from": 1},
        ).limit(_MAX + 1))
    except Exception as exc:
        raise HTTPException(503, "HR_ASSIGNMENT_SOURCE_UNAVAILABLE") from exc
    if len(proposals) > _MAX or len(current) > _MAX:
        raise HTTPException(503, "HR_ASSIGNMENT_RESULT_BOUND_EXCEEDED")
    actor = organization.identity.identity_id
    return {
        "schema": "WILSY-HR-GOVERNED-ASSIGNMENTS/V1",
        "tenant_id": organization.tenant_id, "source": "EOS_HR_ASSIGNMENT_REGISTRY",
        "proposals": [{**_public(p), "current_principal_is_maker": actor in (
            p.get("created_by"), p.get("submitted_by"),
        )} for p in proposals],
        "current": [{k: a.get(k) for k in (
            "employee_id", "position_id", "department_id",
            "revision", "effective_from",
        )} for a in current],
        "legacy_employee_fields_synchronized": False,
        "verified_operating_entity_connected": False,
    }


@router.get("/planning")
def read_position_utilization(
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0, le=100000),
    organization: TenantAuthorizationContext = Depends(_ORG_READ),
    workforce: TenantAuthorizationContext = Depends(_MAKER),
):
    """Read approved-position capacity versus governed assignment occupancy.

    This is never an employer headcount, payroll, legal entity or budget forecast.
    Directory text labels are not counted as confirmed graph assignments.
    """
    if organization.tenant_id != workforce.tenant_id or (
        organization.identity.identity_id != workforce.identity.identity_id
    ):
        raise HTTPException(403, "HR_ASSIGNMENT_SCOPE_MISMATCH")
    db = get_database()
    if db is None:
        raise HTTPException(503, "HR_ASSIGNMENT_SOURCE_UNAVAILABLE")
    tenant = organization.tenant_id
    position_filter = {"tenant_id": tenant, "kind": "POSITION", "status": "APPROVED"}
    try:
        positions = _collection(db, _ORG_COLLECTION)
        total = positions.count_documents(position_filter)
        page = list(positions.find(position_filter, {
            "_id": 0, "record_id": 1, "department_id": 1, "name": 1,
            "capacity": 1, "effective_from": 1, "revision": 1,
        }).sort("record_id", 1).skip(offset).limit(limit))
        identifiers = [position["record_id"] for position in page]
        grouped = list(_collection(db, _ASSIGNMENTS).aggregate([
            {"$match": {"tenant_id": tenant, "position_id": {"$in": identifiers}}},
            {"$group": {"_id": "$position_id", "assigned": {"$sum": 1}}},
            {"$limit": limit + 1},
        ])) if identifiers else []
    except Exception as exc:
        raise HTTPException(503, "HR_ASSIGNMENT_PLANNING_SOURCE_UNAVAILABLE") from exc
    if len(page) > limit or len(grouped) > limit or not isinstance(total, int) or total < 0:
        raise HTTPException(503, "HR_ASSIGNMENT_PLANNING_INVALID")
    counts = {}
    for group in grouped:
        count = group.get("assigned")
        if group.get("_id") not in identifiers or type(count) is not int or count < 0:
            raise HTTPException(503, "HR_ASSIGNMENT_PLANNING_INVALID")
        counts[group["_id"]] = count
    items = []
    for position in page:
        capacity = position.get("capacity")
        if type(capacity) is not int or capacity < 1:
            raise HTTPException(503, "HR_ASSIGNMENT_POSITION_CAPACITY_UNVERIFIED")
        assigned = counts.get(position["record_id"], 0)
        if assigned > capacity:
            raise HTTPException(503, "HR_ASSIGNMENT_POSITION_OVERBOOKED")
        items.append({
            "position_id": position["record_id"],
            "department_id": position["department_id"],
            "name": position["name"],
            "approved_capacity": capacity,
            "governed_assignments": assigned,
            "unfilled_graph_slots": capacity - assigned,
            "effective_from": position["effective_from"],
            "position_currently_effective": (
                position["effective_from"] <= date.today().isoformat()
            ),
        })
    return {
        "schema": "WILSY-HR-POSITION-UTILIZATION/V1",
        "source": "EOS_APPROVED_POSITION_ASSIGNMENT_GRAPH",
        "tenant_id": tenant, "items": items,
        "total": total, "offset": offset, "limit": limit,
        "has_more": offset + len(items) < total,
        "legacy_employee_fields_synchronized": False,
        "entity_authority_verified": False,
        "funded_headcount_verified": False,
    }


@router.get("/employees/{employee_id}/history")
def read_assignment_history(
    employee_id: str,
    organization: TenantAuthorizationContext = Depends(_ORG_READ),
    workforce: TenantAuthorizationContext = Depends(_MAKER),
):
    """Return persisted effective versions for one authorized employee ID."""
    if organization.tenant_id != workforce.tenant_id or (
        organization.identity.identity_id != workforce.identity.identity_id
    ):
        raise HTTPException(403, "HR_ASSIGNMENT_SCOPE_MISMATCH")
    if not _ID.fullmatch(employee_id):
        raise HTTPException(422, "HR_ASSIGNMENT_EMPLOYEE_ID_INVALID")
    db = get_database()
    if db is None:
        raise HTTPException(503, "HR_ASSIGNMENT_SOURCE_UNAVAILABLE")
    try:
        rows = list(_collection(db, _VERSIONS).find({
            "tenant_id": organization.tenant_id, "employee_id": employee_id,
        }, {"_id": 0, "revision": 1, "position_id": 1,
            "department_id": 1, "effective_from": 1,
            "recorded_at": 1, "decision_id": 1},
        ).sort("revision", 1).limit(_MAX + 1))
    except Exception as exc:
        raise HTTPException(503, "HR_ASSIGNMENT_HISTORY_UNAVAILABLE") from exc
    if len(rows) > _MAX:
        raise HTTPException(503, "HR_ASSIGNMENT_HISTORY_BOUND_EXCEEDED")
    return {
        "schema": "WILSY-HR-ASSIGNMENT-HISTORY/V1",
        "source": "EOS_HR_ASSIGNMENT_VERSION_REGISTRY",
        "tenant_id": organization.tenant_id, "employee_id": employee_id,
        "items": rows, "count": len(rows),
        "legacy_employee_fields_synchronized": False,
    }


@router.post("/proposals", status_code=201)
def propose_assignment(
    body: AssignmentDraft,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    organization: TenantAuthorizationContext = Depends(_ORG_READ),
    workforce: TenantAuthorizationContext = Depends(_MAKER),
):
    """Maker proposes a source-verified assignment without admitting an employee."""
    if organization.tenant_id != workforce.tenant_id or (
        organization.identity.identity_id != workforce.identity.identity_id
    ):
        raise HTTPException(403, "HR_ASSIGNMENT_SCOPE_MISMATCH")
    tenant, actor = organization.tenant_id, organization.identity.identity_id
    payload = body.model_dump(mode="json")
    def apply(proposed, assigned, versions, org, employees, tx):
        department_id = _verify_sources(
            org, employees, tenant, body.employee_id, body.position_id, tx,
        )
        previous = assigned.find_one({
            "tenant_id": tenant, "employee_id": body.employee_id,
        }, session=tx)
        row = {
            **payload, "department_id": department_id,
            "tenant_id": tenant, "proposal_id": uuid4().hex,
            "status": "DRAFT", "revision": 1,
            "base_revision": previous["revision"] if previous else 0,
            "created_by": actor, "submitted_by": None, "created_at": _now(),
        }
        proposed.insert_one(row, session=tx)
        return {"schema": "WILSY-HR-ASSIGNMENT-COMMAND/V1",
                "tenant_id": tenant, "proposal": _public(row)}
    return _command(tenant, actor, key, "DRAFT", payload, apply)


@router.post("/proposals/{proposal_id}/submit")
def submit_assignment(
    proposal_id: str, body: AssignmentRevision,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    organization: TenantAuthorizationContext = Depends(_ORG_READ),
    workforce: TenantAuthorizationContext = Depends(_MAKER),
):
    """Maker submits draft for a different principal's reasoned approval."""
    if organization.tenant_id != workforce.tenant_id or (
        organization.identity.identity_id != workforce.identity.identity_id
    ):
        raise HTTPException(403, "HR_ASSIGNMENT_SCOPE_MISMATCH")
    tenant, actor = organization.tenant_id, organization.identity.identity_id
    def apply(proposed, assigned, versions, org, employees, tx):
        row = proposed.find_one({"tenant_id": tenant, "proposal_id": proposal_id}, session=tx)
        if row is None:
            raise HTTPException(404, "HR_ASSIGNMENT_PROPOSAL_NOT_FOUND")
        if row["created_by"] != actor:
            raise HTTPException(403, "HR_ASSIGNMENT_MAKER_REQUIRED")
        if row["status"] != "DRAFT" or row["revision"] != body.expected_revision:
            raise HTTPException(409, "HR_ASSIGNMENT_REVISION_CONFLICT")
        updated = proposed.find_one_and_update({
            "tenant_id": tenant, "proposal_id": proposal_id,
            "status": "DRAFT", "revision": body.expected_revision,
        }, {"$set": {"status": "SUBMITTED", "submitted_by": actor},
            "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER, session=tx)
        if updated is None:
            raise HTTPException(409, "HR_ASSIGNMENT_REVISION_CONFLICT")
        return {"schema": "WILSY-HR-ASSIGNMENT-COMMAND/V1",
                "tenant_id": tenant, "proposal": _public(updated)}
    return _command(tenant, actor, key, "SUBMIT",
                    {"proposal_id": proposal_id, "revision": body.expected_revision}, apply)


@router.post("/proposals/{proposal_id}/decision")
def decide_assignment(
    proposal_id: str, body: AssignmentDecision,
    key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    organization: TenantAuthorizationContext = Depends(_ORG_DECIDE),
    workforce: TenantAuthorizationContext = Depends(_MAKER),
):
    """Independent dual-authorized checker commits a current dated graph assignment."""
    if organization.tenant_id != workforce.tenant_id or (
        organization.identity.identity_id != workforce.identity.identity_id
    ):
        raise HTTPException(403, "HR_ASSIGNMENT_SCOPE_MISMATCH")
    tenant, actor = organization.tenant_id, organization.identity.identity_id
    def apply(proposed, assigned, versions, org, employees, tx):
        row = proposed.find_one({"tenant_id": tenant, "proposal_id": proposal_id}, session=tx)
        if row is None:
            raise HTTPException(404, "HR_ASSIGNMENT_PROPOSAL_NOT_FOUND")
        if actor in (row["created_by"], row.get("submitted_by")):
            raise HTTPException(403, "HR_ASSIGNMENT_MAKER_CANNOT_APPROVE")
        if row["status"] != "SUBMITTED" or row["revision"] != body.expected_revision:
            raise HTTPException(409, "HR_ASSIGNMENT_REVISION_CONFLICT")
        existing = assigned.find_one({
            "tenant_id": tenant, "employee_id": row["employee_id"],
        }, session=tx)
        if (existing["revision"] if existing else 0) != row["base_revision"]:
            raise HTTPException(409, "HR_ASSIGNMENT_SOURCE_CHANGED")
        if body.decision == "APPROVE":
            if row["effective_from"] > date.today().isoformat():
                raise HTTPException(409, "HR_ASSIGNMENT_FUTURE_ACTIVATION_NOT_CERTIFIED")
            if existing and row["effective_from"] < existing["effective_from"]:
                raise HTTPException(409, "HR_ASSIGNMENT_BACKDATED_MOVE_NOT_CERTIFIED")
            department_id = _verify_sources(
                org, employees, tenant, row["employee_id"], row["position_id"], tx,
            )
            if department_id != row["department_id"]:
                raise HTTPException(409, "HR_ASSIGNMENT_POSITION_DEPARTMENT_CHANGED")
            position = org.find_one({
                "tenant_id": tenant, "record_id": row["position_id"],
                "kind": "POSITION", "status": "APPROVED",
            }, session=tx)
            department = org.find_one({
                "tenant_id": tenant, "record_id": department_id,
                "kind": "DEPARTMENT", "status": "APPROVED",
            }, session=tx)
            if (not position or not department or
                row["effective_from"] < position.get("effective_from", "") or
                row["effective_from"] < department.get("effective_from", "")):
                raise HTTPException(409, "HR_ASSIGNMENT_NOT_EFFECTIVE_AT_START")
            capacity = position.get("capacity")
            if type(capacity) is not int or capacity < 1:
                raise HTTPException(409, "HR_ASSIGNMENT_POSITION_CAPACITY_UNVERIFIED")
            occupied = assigned.count_documents({
                "tenant_id": tenant, "position_id": row["position_id"],
                "employee_id": {"$ne": row["employee_id"]},
            }, session=tx)
            if occupied >= capacity:
                raise HTTPException(409, "HR_ASSIGNMENT_POSITION_CAPACITY_EXCEEDED")
            # Serialize concurrent approvals against the same position document.
            # Without a common write, two snapshot transactions could each
            # observe a free seat and jointly overbook a capacity-one position.
            touched = org.update_one({
                "tenant_id": tenant, "kind": "POSITION",
                "record_id": row["position_id"], "status": "APPROVED",
                "revision": position["revision"],
            }, {"$inc": {"assignment_write_epoch": 1}}, session=tx)
            if touched.matched_count != 1:
                raise HTTPException(409, "HR_ASSIGNMENT_POSITION_CHANGED")
            if existing and existing["position_id"] != row["position_id"]:
                old_position = org.find_one({
                    "tenant_id": tenant, "kind": "POSITION",
                    "record_id": existing["position_id"], "status": "APPROVED",
                }, session=tx)
                if old_position is None:
                    raise HTTPException(409, "HR_ASSIGNMENT_PREVIOUS_POSITION_UNAVAILABLE")
                old_touched = org.update_one({
                    "tenant_id": tenant, "kind": "POSITION",
                    "record_id": existing["position_id"], "status": "APPROVED",
                    "revision": old_position["revision"],
                }, {"$inc": {"assignment_write_epoch": 1}}, session=tx)
                if old_touched.matched_count != 1:
                    raise HTTPException(409, "HR_ASSIGNMENT_PREVIOUS_POSITION_CHANGED")
            next_revision = row["base_revision"] + 1
            new_assignment = {
                "tenant_id": tenant, "employee_id": row["employee_id"],
                "position_id": row["position_id"], "department_id": department_id,
                "effective_from": row["effective_from"],
                "revision": next_revision, "decision_id": proposal_id,
            }
            if existing is None:
                assigned.insert_one(new_assignment, session=tx)
            else:
                versions.update_one({
                    "tenant_id": tenant, "employee_id": row["employee_id"],
                    "revision": existing["revision"],
                }, {"$setOnInsert": {
                    "tenant_id": tenant, "employee_id": row["employee_id"],
                    "revision": existing["revision"],
                    "position_id": existing["position_id"],
                    "department_id": existing["department_id"],
                    "effective_from": existing["effective_from"],
                    "decision_id": existing["decision_id"],
                    "recorded_at": _now(),
                }}, upsert=True, session=tx)
                result = assigned.replace_one({
                    "tenant_id": tenant, "employee_id": row["employee_id"],
                    "revision": row["base_revision"],
                }, new_assignment, session=tx)
                if result.matched_count != 1:
                    raise HTTPException(409, "HR_ASSIGNMENT_SOURCE_CHANGED")
            versions.insert_one({
                **new_assignment, "recorded_at": _now(),
            }, session=tx)
        updated = proposed.find_one_and_update({
            "tenant_id": tenant, "proposal_id": proposal_id,
            "status": "SUBMITTED", "revision": body.expected_revision,
        }, {"$set": {"status": "APPROVED" if body.decision == "APPROVE" else "REJECTED",
                    "decision_reason": body.reason, "decided_by": actor,
                    "decided_at": _now()}, "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER, session=tx)
        if updated is None:
            raise HTTPException(409, "HR_ASSIGNMENT_REVISION_CONFLICT")
        return {"schema": "WILSY-HR-ASSIGNMENT-COMMAND/V1",
                "tenant_id": tenant, "proposal": _public(updated)}
    return _command(tenant, actor, key, "DECIDE",
                    {"proposal_id": proposal_id, **body.model_dump()}, apply)


# ARTIFACT: tools/eos/api/hr_organization_assignment_router.py
# VERSION: v1.0.0-M03-HR03-GOVERNED-ASSIGNMENTS
# AUTHORITY BOUNDARY: Conjunctive employee-relation and organization permission; no grants.
# TENANT POSTURE: Exact source-checked tenant, distinct maker/checker.
# FAIL-CLOSED POSTURE: Future activation, absent entity, orphaned staffing denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
