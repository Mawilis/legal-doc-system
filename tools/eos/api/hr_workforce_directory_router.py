"""Authenticated, least-privilege WILSY workforce directory projection.

This endpoint is read-only. Tenant scope comes exclusively from the canonical
RequireTenantAuthorization dependency; caller query/body tenant identifiers
are not accepted. Only directory-safe fields are projected from the existing
employee registry. Restricted HR, identity, health and financial attributes
are never returned.
"""
from __future__ import annotations

import re
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
