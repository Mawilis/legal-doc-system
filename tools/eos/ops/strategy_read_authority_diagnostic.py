"""Read-only local EOS Strategy IAM reconciliation.

TITLE: WILSY OS Strategy Owner Access Readback
VERSION: v1.0.1-STRATEGY-OWNER-STATIC-POLICY-CHECK
AUTHORITY: Existing canonical tenant IAM composer; no writes, grants or session issuance.
EPITOME: Compare Owner Projects vs Strategy under one explicit principal/tenant and print exact static capacity eligibility.
COMPLIANCE: Do not disclose credentials, email, role revision or raw document content.
TENANT BOUNDARY: Canonical WILSY tenant only; no alias or root fallback.
FINANCIAL AUTHORITY BOUNDARY: No execution.
"""
from __future__ import annotations

import os
import sys
from typing import Final

from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_authority_policy import tenant_role_operation_eligibility
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.api.tenant_authorization_http import get_role_assignment_repository
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID
from tools.eos.kernel.db import connect_db, get_database

VERSION: Final = "v1.0.1-STRATEGY-OWNER-STATIC-POLICY-CHECK"
CAPACITY: Final = "tenant_owner"
ASSIGNMENTS: Final = (
    "PROJECTS_PLATFORM_OWNER",
    "COMPANY_DOCUMENT_READER",
    "COMPANY_DOCUMENT_AUTHOR",
    "COMPANY_DOCUMENT_PUBLISHER",
    "ENTERPRISE_ADMIN",
)


def _status(value: object) -> str:
    state = getattr(getattr(value, "status", None), "value", None)
    return state if state in {"ACTIVE", "REVOKED", "INACTIVE"} else "OTHER"


def inspect(principal_id: str) -> dict[str, str]:
    """Inspect only explicit current authority; no IAM writes or DDL."""
    if not isinstance(principal_id, str) or not principal_id.strip() or principal_id != principal_id.strip():
        raise ValueError("EXPLICIT_PRINCIPAL_REQUIRED")
    connected, _ = connect_db()
    if not connected or get_database() is None:
        raise RuntimeError("EOS_DATABASE_UNAVAILABLE")

    tenant_id = WILSY_COMPANY_TENANT_ID
    result: dict[str, str] = {
        "STATIC_OWNER_PROJECT_POLICY": tenant_role_operation_eligibility(CAPACITY, "project_detail"),
        "STATIC_OWNER_STRATEGY_POLICY": tenant_role_operation_eligibility(CAPACITY, "company_operating_document_read"),
    }
    role_reader = get_role_assignment_repository()

    for label, permission, operation in (
        ("PROJECTS", "project:read", "project_detail"),
        ("STRATEGY", "company_operating_document:read", "company_operating_document_read"),
    ):
        decision = authorize_tenant_operation(
            principal_id=principal_id,
            tenant_id=tenant_id,
            permission_id=permission,
            operation=operation,
            principal_repository=PrincipalAuthorityRepository(),
            membership_repository=TenantMembershipRepository(),
            business_role_repository=role_reader,
            role_assignment_repository=role_reader,
            selected_business_role=CAPACITY,
        )
        result[label] = (
            "AUTHORIZED" if decision.authorized else decision.reason.value
        )

    try:
        capacity = TenantBusinessRoleRepository.resolve_business_role(
            principal_id, tenant_id, CAPACITY,
        )
        result["OWNER_CAPACITY"] = _status(capacity)
    except Exception as error:
        result["OWNER_CAPACITY"] = (
            "NOT_FOUND" if "NotFound" in type(error).__name__ else "SOURCE_UNAVAILABLE"
        )

    for role in ASSIGNMENTS:
        try:
            assignment = RoleAssignmentRepository.resolve(principal_id, tenant_id, role)
            result["ASSIGNMENT_" + role] = _status(assignment)
        except RoleAssignmentNotFoundError:
            result["ASSIGNMENT_" + role] = "NOT_FOUND"
        except Exception:
            result["ASSIGNMENT_" + role] = "SOURCE_UNAVAILABLE"

    return result


def main() -> int:
    principal_id = os.environ.get("WILSY_DIAGNOSTIC_PRINCIPAL_ID", "")
    if not principal_id:
        print("DIAGNOSTIC=PRINCIPAL_ID_REQUIRED")
        return 2
    try:
        results = inspect(principal_id)
    except Exception as error:
        code = str(error) if isinstance(error, (ValueError, RuntimeError)) else "DIAGNOSTIC_SOURCE_UNAVAILABLE"
        print("DIAGNOSTIC=" + code)
        return 2
    print("DIAGNOSTIC=READ_ONLY")
    print("CAPACITY=tenant_owner")
    for key, value in results.items():
        print(key + "=" + value)
    # A missing read permission or capacity is NOT repaired by this command.
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ARTIFACT: tools/eos/ops/strategy_read_authority_diagnostic.py
# VERSION: v1.0.1-STRATEGY-OWNER-STATIC-POLICY-CHECK
# AUTHORITY BOUNDARY: pure source inspection; no assignment or grant changes.
# END OF WILSY OS SOVEREIGN ARTIFACT
