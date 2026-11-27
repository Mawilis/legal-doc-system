"""TITLE: WILSY OS Authenticated Employee Directory HTTP Boundary
VERSION: v1.1.0-M03-HR01-IAM-REDACTED-DIRECTORY
AUTHORITY: Python Kennel EOS Global Principal and tenant workforce IAM.
EPITOME: Read an exact authorized tenant workforce directory without accepting
         caller-selected tenant identity or exposing protected employee files.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/employee_router.py
COLLABORATION / OWNERSHIP: Mounted by server.py under /api/employees;
         TenantAuthorizationHTTP owns current principal/tenant/capacity/IAM;
         EmployeeRegistry owns exact tenant persistence; EmployeeEntity is a
         legacy sensitive domain record and MUST NOT be serialized directly.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.1.0-M03-HR01-IAM-REDACTED-DIRECTORY replaces caller tenant query,
         header fallback and GLOBAL_ROOT with current RequireTenantAuthorization,
         reuses existing customer directory and WILSY employer permission pairs,
         restricts responses to verified directory-only fields, and denies
         legacy tenantId query input.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Salary, identity numbers, banking, personal contacts,
         addresses, date of birth, emergency contacts and HR files never leave
         this surface. No PII or raw error logging.
TENANT BOUNDARY: Exact tenant from authenticated selected membership only,
         enforced independently by IAM and EmployeeRegistry query predicate.
AUTHORITY BOUNDARY: Current HR workforce directory read entitlement and IAM
         required; separate WILSY platform employer permission (no root bypass).
TRANSACTION BOUNDARY: Read-only existing kernel database, no writes or indexes.
FINANCIAL AUTHORITY BOUNDARY: Directory read grants no pay or release authority.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict

from .tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from ..saas.employee.employee_registry import (
    EmployeeRegistry,
    EmployeeRegistryBoundaryError,
    get_employee_registry,
)
from ..saas.domain.employee import EmployeeEntity

VERSION = "v1.1.0-M03-HR01-IAM-REDACTED-DIRECTORY"
router = APIRouter(prefix="/api/employees", tags=["Employees"])

_DIRECTORY_READ = RequireTenantAuthorization(
    "hr:employee_directory:read",
    "hr_employee_directory_read",
    platform_employer_permission_id="platform_employer:employee_directory:read",
    platform_employer_operation="platform_employer_employee_directory_read",
)


class EmployeeDirectoryRecord(BaseModel):
    """Public directory-safe employee fields for authorized workforce readers.

    No source write, salary, bank, national identity, protected HR document,
    personal contact, or arbitrary metadata fields are admitted in this model.
    """
    model_config = ConfigDict(extra="forbid")
    employeeId: str
    displayName: str
    jobTitle: str
    department: str
    managerId: str | None
    employmentStatus: str
    isActive: bool


def _directory_record(employee: EmployeeEntity) -> EmployeeDirectoryRecord:
    """Explicit minimal projection; never call EmployeeEntity.to_dict() in HTTP."""
    return EmployeeDirectoryRecord(
        employeeId=employee.employeeId,
        displayName=employee.displayName,
        jobTitle=employee.jobTitle,
        department=employee.department,
        managerId=employee.managerId,
        employmentStatus=employee.status,
        isActive=employee.isActive,
    )


@router.get("/search", response_model=list[EmployeeDirectoryRecord])
def search_employees(
    q: str = Query(min_length=2, max_length=180),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=100000),
    context: TenantAuthorizationContext = Depends(_DIRECTORY_READ),
    registry: EmployeeRegistry = Depends(get_employee_registry),
) -> list[EmployeeDirectoryRecord]:
    """Search only the selected tenant's directory through active HR read IAM.

    A deprecated caller tenantId query parameter is not used to resolve scope;
    clients must rely on the authenticated exact tenant. Invalid source or
    persistence errors fail closed without cross-tenant existence disclosure.
    """
    try:
        records = registry.search_employees(context.tenant_id, q, limit, offset)
    except EmployeeRegistryBoundaryError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.args[0],
        ) from None
    return [_directory_record(record) for record in records]


@router.get("/{employee_id}", response_model=EmployeeDirectoryRecord)
def get_employee(
    employee_id: str,
    context: TenantAuthorizationContext = Depends(_DIRECTORY_READ),
    registry: EmployeeRegistry = Depends(get_employee_registry),
) -> EmployeeDirectoryRecord:
    """Read one authorized directory record; foreign and missing remain identical."""
    try:
        employee = registry.get_employee_by_id(employee_id, context.tenant_id)
    except EmployeeRegistryBoundaryError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.args[0],
        ) from None
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="EMPLOYEE_NOT_FOUND",
        )
    return _directory_record(employee)


# ARTIFACT: tools/eos/api/employee_router.py
# VERSION: v1.1.0-M03-HR01-IAM-REDACTED-DIRECTORY
# AUTHORITY BOUNDARY: Existing exact tenant employee-directory permissions.
# TENANT POSTURE: Global Principal authenticated selected tenant only.
# FAIL-CLOSED POSTURE: Restricted PII excluded; nonadmitted request denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
