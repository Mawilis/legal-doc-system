"""TITLE: WILSY authenticated workforce directory projection.
VERSION: v1.1.1-M03-SINGLE-SOURCE-AGGREGATE
AUTHORITY: Existing Python EOS tenant authorization and canonical employee directory read.
EPITOME: Projects a bounded set of directory-safe employee fields from the
         existing employees source for authenticated HR or platform-employer
         viewers, without creating employment or identity authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/hr_workforce_directory_router.py
COLLABORATION / OWNERSHIP: Mounted once by tools/eos/api/server.py at /api/hr/workforce; consumed by Headquarters and HR directory views.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG:
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
        needle = re.escape(q.strip())
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


# ARTIFACT: hr_workforce_directory_router.py
# VERSION: v1.1.1-M03-SINGLE-SOURCE-AGGREGATE
# AUTHORITY BOUNDARY: Existing EOS tenant authorization gates read-only directory projection; the route grants no employee, principal, membership, IAM, or entitlement authority.
# TENANT POSTURE: Exact authorized tenant is applied to every employee query; employer alternate pair is canonical-WILSY-only.
# FAIL-CLOSED POSTURE: Missing database, malformed authorization, or source read failure returns unavailable and never an empty-success projection.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
