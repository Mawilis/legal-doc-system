"""TITLE: WILSY authenticated workforce directory projection.
VERSION: v1.4.0-GOVERNED-ORGANIZATION-REGISTRY
AUTHORITY: Existing Python EOS tenant authorization and canonical employee directory read.
EPITOME: Projects a bounded set of directory-safe employee fields from the
         existing employees source for authenticated HR or platform-employer
         viewers, without creating employment or identity authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/hr_workforce_directory_router.py
COLLABORATION / OWNERSHIP: Mounted once by tools/eos/api/server.py at /api/hr/workforce; consumed by Headquarters and HR directory views.
CERTIFICATION / UPDATE DATE: 2026-11-28.
CHANGELOG:
  v1.4.0-GOVERNED-ORGANIZATION-REGISTRY introduces independent HR organization create/decide IAM, durable transaction-owned draft/submit/checker lifecycle, exact-tenant department and position references, majority read/write, optimistic revisions, SHA3-512 command idempotency and event evidence. No automatic grants, employee admission or staffing allocation.
  v1.4.0-GOVERNED-ORGANIZATION-REGISTRY adds a bounded exact-tenant, employee-derived department distribution, separately authorized through existing directory IAM. It never asserts approved departments, positions, reporting trees or headcount allocations and fails closed on partial or malformed aggregation.
  v1.4.0-GOVERNED-ORGANIZATION-REGISTRY rejects whitespace-only search parameters before issuing a directory-wide regex query; canonical IAM, explicit projection, bounded list and exact-tenant detail read remain unchanged.
  v1.2.0-M03-WORKFORCE-DIRECTORY-DETAIL — Adds a separately authorized, strictly exact-tenant, directory-only employee detail read with opaque not-found behavior and bounded identity selectors; reuses the canonical employee projection without employment write or protected file access.
  v1.1.1-M03-SINGLE-SOURCE-AGGREGATE — Reads employee and department measures in one exact-tenant
  Mongo aggregation instead of two unsynchronized count/distinct calls.
  v1.1.1-M03-SINGLE-SOURCE-AGGREGATE — Adds exact-tenant, current-IAM-authorized workforce Overview
  metrics from the canonical employee source. No HR access, departments,
  payroll, employee PII, or separate-source privileges are inferred.
  v1.1.1-M03-SINGLE-SOURCE-AGGREGATE — Corrects the release marker so the header, current changelog and end seal agree exactly; directory behavior is unchanged.
  v1.0.0-PLATFORM-EMPLOYER-DIRECTORY-SCOPE — Adds canonical WILSY platform-employer read authorization while preserving customer HR entitlement, exact tenant query, bounded projection and read-only behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant scope comes only from EOS authorization; directory fields are projected explicitly and sensitive identity, health and financial attributes are excluded.
TENANT BOUNDARY: Every read filters the exact authorized tenant; employer alternate permission is selected only for canonical WILSY.
AUTHORITY BOUNDARY: Customer access requires active HR entitlement and tenant IAM/currentness. WILSY employer access uses its separately assigned platform-employer permission through the same EOS resolver. This route creates no employee, membership, principal, IAM, or entitlement state.
FINANCIAL AUTHORITY BOUNDARY: No payroll execution, payment, settlement or commercial entitlement authority.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
import hashlib
import json
import uuid
from datetime import date, datetime, timezone
from typing import Literal

from fastapi import Header
from pydantic import BaseModel, ConfigDict, Field
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern
from tools.eos.kernel.db import get_client

from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.kernel.db import get_database

router = APIRouter(prefix="/api/hr/workforce", tags=["hr-workforce"])

_DIRECTORY_AUTHORITY = RequireTenantAuthorization(
    "hr:employee_directory:read",
    "hr_employee_directory_read",
    platform_employer_permission_id="platform_employer:employee_directory:read",
    platform_employer_operation="platform_employer_employee_directory_read",
)

_DIRECTORY_PROJECTION = {
    "_id": 0,
    "employeeId": 1,
    "displayName": 1,
    "preferredName": 1,
    "employment.jobTitle": 1,
    "employment.department": 1,
    "employment.managerId": 1,
    "employment.status": 1,
    "employment.workLocation": 1,
    "contact.workEmail": 1,
    "isActive": 1,
}


@router.get("")
async def list_workforce_directory(
    q: str | None = Query(default=None, min_length=2, max_length=80),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100000),
    authorization: TenantAuthorizationContext = Depends(_DIRECTORY_AUTHORITY),
) -> dict[str, Any]:
    """Return a bounded own-tenant directory page after current IAM admission."""
    tenant_id = authorization.tenant_id
    database = get_database()
    if database is None:
        raise HTTPException(
            status_code=503,
            detail="Workforce directory source is unavailable.",
        )

    criteria: dict[str, Any] = {
        "tenantId": tenant_id,
        "isActive": True,
        "deletedAt": None,
    }
    if q is not None:
        normalized_query = q.strip()
        if len(normalized_query) < 2:
            raise HTTPException(status_code=422, detail="WORKFORCE_SEARCH_QUERY_INVALID")
        needle = re.escape(normalized_query)
        criteria["$or"] = [
            {"displayName": {"$regex": needle, "$options": "i"}},
            {"preferredName": {"$regex": needle, "$options": "i"}},
            {"employeeId": {"$regex": needle, "$options": "i"}},
            {"employment.jobTitle": {"$regex": needle, "$options": "i"}},
            {"employment.department": {"$regex": needle, "$options": "i"}},
        ]

    try:
        collection = database["employees"]
        total = collection.count_documents(criteria)
        rows = list(
            collection.find(criteria, _DIRECTORY_PROJECTION)
            .sort([("displayName", 1), ("employeeId", 1)])
            .skip(offset)
            .limit(limit)
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Workforce directory source is unavailable.",
        ) from error

    items = []
    for row in rows:
        employment = row.get("employment") or {}
        contact = row.get("contact") or {}
        items.append({
            "employeeId": row.get("employeeId"),
            "displayName": row.get("displayName"),
            "preferredName": row.get("preferredName"),
            "jobTitle": employment.get("jobTitle"),
            "department": employment.get("department"),
            "managerId": employment.get("managerId"),
            "employmentStatus": employment.get("status"),
            "workLocation": employment.get("workLocation"),
            "workEmail": contact.get("workEmail"),
        })

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "hasMore": offset + len(items) < total,
        "source": "AUTHORISED_HR_EMPLOYEE_REGISTRY",
    }


@router.get("/overview")
async def read_workforce_overview(
    authorization: TenantAuthorizationContext = Depends(_DIRECTORY_AUTHORITY),
) -> dict[str, Any]:
    """Exact-tenant, permission-bound workforce measures without employee PII.

    This is one source-owned component of People Overview, not an entitlement
    to read hiring, payroll, leave or employee-case authority.
    """
    database = get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="Workforce overview source is unavailable.")
    criteria = {
        "tenantId": authorization.tenant_id,
        "isActive": True,
        "deletedAt": None,
    }
    try:
        collection = database["employees"]
        aggregation = list(collection.aggregate([
            {"$match": criteria},
            {"$group": {
                "_id": None,
                "active_employees": {"$sum": 1},
                "departments": {"$addToSet": "$employment.department"},
            }},
        ]))
        if len(aggregation) > 1:
            raise ValueError("HR_OVERVIEW_MULTIPLE_AGGREGATES")
        metrics = aggregation[0] if aggregation else {
            "active_employees": 0, "departments": [],
        }
        active_count = metrics["active_employees"]
        departments = metrics["departments"]
    except Exception as error:
        raise HTTPException(
            status_code=503, detail="Workforce overview source is unavailable."
        ) from error
    if not isinstance(active_count, int) or active_count < 0 or not isinstance(departments, list):
        raise HTTPException(status_code=503, detail="Workforce overview source is unavailable.")
    return {
        "schema": "WILSY-PEOPLE-WORKFORCE-OVERVIEW/V1",
        "tenant_id": authorization.tenant_id,
        "source": "AUTHORISED_HR_EMPLOYEE_REGISTRY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "active_employees": active_count,
            "departments": len({
                value.strip() for value in departments
                if isinstance(value, str) and value.strip()
            }),
        },
    }



@router.get("/organization")
async def read_workforce_organization(
    authorization: TenantAuthorizationContext = Depends(_DIRECTORY_AUTHORITY),
) -> dict[str, Any]:
    """Read a tenant-scoped observed departmental distribution, not an approved org chart.

    Reuses existing active-employee directory IAM. Department labels and counts
    originate exclusively from the canonical employee collection, without
    positions, invented reporting structure, HR write permission or personal data.
    The single grouped aggregation is bounded to 201 results, and oversize or
    malformed data fails closed rather than yielding a partial organizational map.
    """
    database = get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="WORKFORCE_ORGANIZATION_SOURCE_UNAVAILABLE")
    criteria = {
        "tenantId": authorization.tenant_id,
        "isActive": True,
        "deletedAt": None,
    }
    try:
        grouped = list(database["employees"].aggregate([
            {"$match": criteria},
            {"$group": {
                "_id": "$employment.department",
                "active_employees": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
            {"$limit": 201},
        ]))
    except Exception as error:
        raise HTTPException(
            status_code=503, detail="WORKFORCE_ORGANIZATION_SOURCE_UNAVAILABLE"
        ) from error
    if len(grouped) > 200:
        raise HTTPException(status_code=503, detail="WORKFORCE_ORGANIZATION_BOUND_EXCEEDED")
    departments: list[dict[str, Any]] = []
    unassigned = 0
    for entry in grouped:
        count = entry.get("active_employees")
        name = entry.get("_id")
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise HTTPException(status_code=503, detail="WORKFORCE_ORGANIZATION_SOURCE_INVALID")
        if name is None or name == "":
            unassigned += count
            continue
        if not isinstance(name, str) or not name.strip() or len(name) > 180:
            raise HTTPException(status_code=503, detail="WORKFORCE_ORGANIZATION_SOURCE_INVALID")
        departments.append({"name": name.strip(), "active_employees": count})
    if len({entry["name"] for entry in departments}) != len(departments):
        raise HTTPException(status_code=503, detail="WORKFORCE_ORGANIZATION_SOURCE_INVALID")
    departments.sort(key=lambda entry: entry["name"].casefold())
    return {
        "schema": "WILSY-HR-WORKFORCE-ORGANIZATION/V1",
        "tenant_id": authorization.tenant_id,
        "source": "AUTHORISED_HR_EMPLOYEE_REGISTRY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "OBSERVED_EMPLOYEE_DISTRIBUTION",
        "department_count": len(departments),
        "active_employees": sum(entry["active_employees"] for entry in departments) + unassigned,
        "unassigned_employees": unassigned,
        "departments": departments,
    }


@router.get("/{employee_id}")
async def read_workforce_directory_employee(
    employee_id: str,
    authorization: TenantAuthorizationContext = Depends(_DIRECTORY_AUTHORITY),
) -> dict[str, Any]:
    """Read one directory-safe employee by exact ID within current authorized tenant.

    This is not an employee file or workforce-admission read. Foreign, inactive,
    deleted and absent employee IDs all return the same opaque 404 response.
    The same current HR directory IAM and canonical employer-scope gate applies.
    """
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,179}", employee_id):
        raise HTTPException(status_code=422, detail="WORKFORCE_EMPLOYEE_ID_INVALID")
    database = get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="Workforce directory source is unavailable.")
    try:
        row = database["employees"].find_one(
            {
                "tenantId": authorization.tenant_id,
                "employeeId": employee_id,
                "isActive": True,
                "deletedAt": None,
            },
            _DIRECTORY_PROJECTION,
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Workforce directory source is unavailable.",
        ) from error
    if row is None:
        raise HTTPException(status_code=404, detail="WORKFORCE_EMPLOYEE_NOT_FOUND")
    employment = row.get("employment") or {}
    contact = row.get("contact") or {}
    if row.get("employeeId") != employee_id:
        raise HTTPException(status_code=503, detail="Workforce directory source is unavailable.")
    return {
        "schema": "WILSY-HR-WORKFORCE-DIRECTORY-DETAIL/V1",
        "source": "AUTHORISED_HR_EMPLOYEE_REGISTRY",
        "tenant_id": authorization.tenant_id,
        "employee": {
            "employeeId": employee_id,
            "displayName": row.get("displayName"),
            "preferredName": row.get("preferredName"),
            "jobTitle": employment.get("jobTitle"),
            "department": employment.get("department"),
            "managerId": employment.get("managerId"),
            "employmentStatus": employment.get("status"),
            "workLocation": employment.get("workLocation"),
            "workEmail": contact.get("workEmail"),
        },
    }



# This is a separate emerging-canonical organization authority. Observed
# employee departments above remain a read-only projection, never an approved
# department or position master.
_ORG_COLLECTION = "hr_organization_records"
_ORG_EVENTS = "hr_organization_events"
_ORG_CREATE = RequireTenantAuthorization(
    "hr:organization:create",
    "hr_organization_create",
    platform_employer_permission_id="platform_employer:organization:create",
    platform_employer_operation="platform_employer_organization_create",
)
_ORG_DECIDE = RequireTenantAuthorization(
    "hr:organization:decide",
    "hr_organization_decide",
    platform_employer_permission_id="platform_employer:organization:decide",
    platform_employer_operation="platform_employer_organization_decide",
)


class OrganizationCreateRequest(BaseModel):
    """Bounded organization proposal. IDs reference only approved same-tenant records.

    A department or position is DRAFT after creation. No staffing, IAM,
    financial execution or approved headcount is implied by a proposal.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    record_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}$")
    name: str = Field(min_length=2, max_length=180)
    parent_id: str | None = Field(default=None, min_length=1, max_length=120)
    department_id: str | None = Field(default=None, min_length=1, max_length=120)
    effective_from: date
    capacity: int | None = Field(default=None, ge=1, le=500, strict=True)


class OrganizationRevisionRequest(BaseModel):
    """Expected revision for a single authorized draft submission."""

    model_config = ConfigDict(extra="forbid")
    expected_revision: int = Field(ge=1, strict=True)


class OrganizationDecisionRequest(OrganizationRevisionRequest):
    """Independent organization decision with a bounded audited explanation."""

    decision: Literal["APPROVE", "REJECT"]
    reason: str = Field(min_length=5, max_length=2000)


def _org_collection(database: Any, name: str) -> Any:
    """Compose a majority-consistent organization collection for one transaction."""
    return database.get_collection(
        name,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )


def _org_transaction(callback: Any) -> Any:
    """Commit source state and immutable command evidence in one Mongo transaction.

    A unique event key provides durable idempotency for a tenant, actor and
    request key. No read failure, transient error or write conflict is treated
    as accepted business truth.
    """
    client, database = get_client(), get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="ORGANIZATION_DATABASE_UNAVAILABLE")
    try:
        records = _org_collection(database, _ORG_COLLECTION)
        events = _org_collection(database, _ORG_EVENTS)
        records.create_index([("tenant_id", 1), ("kind", 1), ("record_id", 1)], unique=True)
        events.create_index([("tenant_id", 1), ("actor_id", 1), ("key", 1)], unique=True)
        with client.start_session() as session:
            return session.with_transaction(
                lambda current: callback(records, events, current),
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
                read_preference=ReadPreference.PRIMARY,
            )
    except HTTPException:
        raise
    except DuplicateKeyError as error:
        raise HTTPException(status_code=409, detail="ORGANIZATION_CONCURRENT_CONFLICT") from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="ORGANIZATION_TRANSACTION_UNAVAILABLE") from error


def _org_fingerprint(
    *, tenant: str, actor: str, key: str, command: str, payload: dict[str, Any],
) -> str:
    """Deterministic SHA3-512 for one scoped idempotent organization command."""
    return hashlib.sha3_512(json.dumps(
        {"tenant": tenant, "actor": actor, "key": key,
         "command": command, "payload": payload},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def _org_command(
    *, authorization: TenantAuthorizationContext, key: str, command: str,
    payload: dict[str, Any], apply: Any,
) -> dict[str, Any]:
    """Replay identical commands without making additional source mutations."""
    tenant = authorization.tenant_id
    actor = authorization.identity.identity_id
    if not actor or not actor.strip():
        raise HTTPException(status_code=503, detail="ORGANIZATION_ACTOR_INVALID")
    fingerprint = _org_fingerprint(
        tenant=tenant, actor=actor, key=key, command=command, payload=payload,
    )

    def transaction(records: Any, events: Any, session: Any) -> dict[str, Any]:
        identity = {"tenant_id": tenant, "actor_id": actor, "key": key}
        replay = events.find_one(identity, session=session)
        if replay is not None:
            if replay.get("fingerprint") != fingerprint:
                raise HTTPException(status_code=409, detail="ORGANIZATION_IDEMPOTENCY_CONFLICT")
            return replay["response"]
        response = apply(records, session, tenant, actor)
        events.insert_one({
            **identity, "fingerprint": fingerprint, "command": command,
            "response": response, "record_id": payload["record_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }, session=session)
        return response

    return _org_transaction(transaction)


def _org_public(row: dict[str, Any]) -> dict[str, Any]:
    """Project only organizational attributes; exclude actor and command evidence."""
    return {
        field: row.get(field) for field in (
            "record_id", "kind", "name", "parent_id", "department_id",
            "effective_from", "capacity", "status", "revision",
        )
    }


@router.get("/structure")
async def read_approved_workforce_structure(
    authorization: TenantAuthorizationContext = Depends(_DIRECTORY_AUTHORITY),
) -> dict[str, Any]:
    """Read bounded own-tenant organization proposals and approved records.

    The source labels draft, submitted and approved records independently.
    It is never an employee directory, headcount allocation or payroll read.
    """
    database = get_database()
    if database is None:
        raise HTTPException(status_code=503, detail="ORGANIZATION_DATABASE_UNAVAILABLE")
    try:
        collection = _org_collection(database, _ORG_COLLECTION)
        rows = list(collection.find(
            {"tenant_id": authorization.tenant_id}, {"_id": 0,
                "record_id": 1, "kind": 1, "name": 1, "parent_id": 1,
                "department_id": 1, "effective_from": 1, "capacity": 1,
                "status": 1, "revision": 1,
            },
        ).sort([("kind", 1), ("record_id", 1)]).limit(201))
    except Exception as error:
        raise HTTPException(status_code=503, detail="ORGANIZATION_SOURCE_UNAVAILABLE") from error
    if len(rows) > 200:
        raise HTTPException(status_code=503, detail="ORGANIZATION_RESULT_BOUND_EXCEEDED")
    return {
        "schema": "WILSY-HR-ORGANIZATION-REGISTRY/V1",
        "source": "EOS_HR_ORGANIZATION_REGISTRY",
        "tenant_id": authorization.tenant_id,
        "items": [_org_public(row) for row in rows],
        "count": len(rows),
    }


@router.post("/structure/{kind}", status_code=201)
async def create_workforce_structure(
    kind: Literal["departments", "positions"],
    body: OrganizationCreateRequest,
    idempotency_key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    authorization: TenantAuthorizationContext = Depends(_ORG_CREATE),
) -> dict[str, Any]:
    """Create one audited DRAFT, not an approved organization or staffing action."""
    record_kind = "DEPARTMENT" if kind == "departments" else "POSITION"
    if (record_kind == "DEPARTMENT" and
            (body.department_id is not None or body.capacity is not None)):
        raise HTTPException(status_code=422, detail="ORGANIZATION_DEPARTMENT_FIELDS_INVALID")
    if record_kind == "POSITION" and (not body.department_id or body.capacity is None):
        raise HTTPException(status_code=422, detail="ORGANIZATION_POSITION_FIELDS_REQUIRED")
    if body.parent_id == body.record_id or body.department_id == body.record_id:
        raise HTTPException(status_code=422, detail="ORGANIZATION_SELF_REFERENCE")
    data = body.model_dump(mode="json")
    def apply(records: Any, session: Any, tenant: str, actor: str) -> dict[str, Any]:
        for parent_kind, parent_id in (
            (record_kind, body.parent_id),
            ("DEPARTMENT", body.department_id),
        ):
            if parent_id and records.find_one(
                {"tenant_id": tenant, "kind": parent_kind, "record_id": parent_id,
                 "status": "APPROVED"},
                session=session,
            ) is None:
                raise HTTPException(status_code=422, detail="ORGANIZATION_PARENT_NOT_APPROVED")
        if records.find_one(
            {"tenant_id": tenant, "kind": record_kind, "record_id": body.record_id},
            session=session,
        ) is not None:
            raise HTTPException(status_code=409, detail="ORGANIZATION_RECORD_EXISTS")
        record = {
            **data, "tenant_id": tenant, "kind": record_kind,
            "status": "DRAFT", "revision": 1,
            "created_by": actor,
            "submitted_by": None, "decided_by": None,
        }
        records.insert_one(record, session=session)
        return {
            "schema": "WILSY-HR-ORGANIZATION-COMMAND/V1",
            "tenant_id": tenant, "record": _org_public(record),
        }
    return _org_command(
        authorization=authorization, key=idempotency_key,
        command="CREATE:" + record_kind,
        payload={**data, "kind": record_kind}, apply=apply,
    )


@router.post("/structure/{kind}/{record_id}/submit")
async def submit_workforce_structure(
    kind: Literal["departments", "positions"],
    record_id: str,
    body: OrganizationRevisionRequest,
    idempotency_key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    authorization: TenantAuthorizationContext = Depends(_ORG_CREATE),
) -> dict[str, Any]:
    """Submit own draft for a later independent organization decision."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}", record_id):
        raise HTTPException(status_code=422, detail="ORGANIZATION_RECORD_ID_INVALID")
    record_kind = "DEPARTMENT" if kind == "departments" else "POSITION"
    payload = {"record_id": record_id, "kind": record_kind,
               "expected_revision": body.expected_revision}
    def apply(records: Any, session: Any, tenant: str, actor: str) -> dict[str, Any]:
        current = records.find_one(
            {"tenant_id": tenant, "kind": record_kind, "record_id": record_id},
            session=session,
        )
        if current is None:
            raise HTTPException(status_code=404, detail="ORGANIZATION_NOT_FOUND")
        if current["status"] != "DRAFT" or current["revision"] != body.expected_revision:
            raise HTTPException(status_code=409, detail="ORGANIZATION_REVISION_CONFLICT")
        if current["created_by"] != actor:
            raise HTTPException(status_code=403, detail="ORGANIZATION_MAKER_REQUIRED")
        updated = records.find_one_and_update(
            {"tenant_id": tenant, "kind": record_kind, "record_id": record_id,
             "status": "DRAFT", "revision": body.expected_revision},
            {"$set": {"status": "SUBMITTED", "submitted_by": actor},
             "$inc": {"revision": 1}},
            return_document=True, session=session,
        )
        if updated is None:
            raise HTTPException(status_code=409, detail="ORGANIZATION_REVISION_CONFLICT")
        return {"schema": "WILSY-HR-ORGANIZATION-COMMAND/V1",
                "tenant_id": tenant, "record": _org_public(updated)}
    return _org_command(
        authorization=authorization, key=idempotency_key,
        command="SUBMIT:" + record_kind, payload=payload, apply=apply,
    )


@router.post("/structure/{kind}/{record_id}/decision")
async def decide_workforce_structure(
    kind: Literal["departments", "positions"],
    record_id: str,
    body: OrganizationDecisionRequest,
    idempotency_key: str = Header(min_length=12, max_length=128, alias="Idempotency-Key"),
    authorization: TenantAuthorizationContext = Depends(_ORG_DECIDE),
) -> dict[str, Any]:
    """Checker decision on a submitted proposal; maker cannot self-approve."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,119}", record_id):
        raise HTTPException(status_code=422, detail="ORGANIZATION_RECORD_ID_INVALID")
    record_kind = "DEPARTMENT" if kind == "departments" else "POSITION"
    payload = {**body.model_dump(), "record_id": record_id, "kind": record_kind}
    def apply(records: Any, session: Any, tenant: str, actor: str) -> dict[str, Any]:
        current = records.find_one(
            {"tenant_id": tenant, "kind": record_kind, "record_id": record_id},
            session=session,
        )
        if current is None:
            raise HTTPException(status_code=404, detail="ORGANIZATION_NOT_FOUND")
        if current["status"] != "SUBMITTED" or current["revision"] != body.expected_revision:
            raise HTTPException(status_code=409, detail="ORGANIZATION_REVISION_CONFLICT")
        if actor in (current["created_by"], current["submitted_by"]):
            raise HTTPException(status_code=403, detail="ORGANIZATION_MAKER_CANNOT_APPROVE")
        if record_kind == "POSITION" and body.decision == "APPROVE":
            department = records.find_one({
                "tenant_id": tenant, "kind": "DEPARTMENT",
                "record_id": current["department_id"], "status": "APPROVED",
            }, session=session)
            if department is None:
                raise HTTPException(status_code=409, detail="ORGANIZATION_PARENT_NOT_APPROVED")
        updated = records.find_one_and_update(
            {"tenant_id": tenant, "kind": record_kind, "record_id": record_id,
             "status": "SUBMITTED", "revision": body.expected_revision},
            {"$set": {"status": "APPROVED" if body.decision == "APPROVE" else "REJECTED",
                      "decided_by": actor, "decision_reason": body.reason},
             "$inc": {"revision": 1}},
            return_document=True, session=session,
        )
        if updated is None:
            raise HTTPException(status_code=409, detail="ORGANIZATION_REVISION_CONFLICT")
        return {"schema": "WILSY-HR-ORGANIZATION-COMMAND/V1",
                "tenant_id": tenant, "record": _org_public(updated)}
    return _org_command(
        authorization=authorization, key=idempotency_key,
        command="DECIDE:" + record_kind, payload=payload, apply=apply,
    )


# ARTIFACT: hr_workforce_directory_router.py
# VERSION: v1.4.0-GOVERNED-ORGANIZATION-REGISTRY
# AUTHORITY BOUNDARY: Existing directory reads remain read-only; independent hr:organization:create and hr:organization:decide permissions gate new registry commands; no permission grant or employee/IAM admission is created.
# TENANT POSTURE: Exact authorized tenant is applied to every employee query; employer alternate pair is canonical-WILSY-only.
# FAIL-CLOSED POSTURE: Missing database, malformed authorization, or source read failure returns unavailable and never an empty-success projection.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
