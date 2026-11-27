"""TITLE: WILSY OS Tenant-Scoped Legacy Employee Read Registry
VERSION: v1.1.0-M03-HR01-STRICT-TENANT-BOUNDARY
AUTHORITY: WILSY OS Python Kennel EOS employee persistence read boundary.
EPITOME: Reject every privileged legacy tenant alias and scope every legacy
         employee lookup to one explicitly supplied nonreserved tenant.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/employee/employee_registry.py
COLLABORATION / OWNERSHIP: Employee HTTP router owns authenticated tenant and
         read permission; domain EmployeeEntity owns legacy record hydration;
         kernel database owns the sole Mongo connection.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.1.0-M03-HR01-STRICT-TENANT-BOUNDARY retires MASTER and
         GLOBAL_ROOT wildcard lookups, enforces bounded exact tenant on every
         read, escapes user search regex, bounds pagination, and redacts query,
         email and employee identifiers from registry diagnostics.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No raw PII or connection details in logs.
TENANT BOUNDARY: Every query contains a validated exact tenantId equality;
         reserved aliases and malformed tenants always reject before database.
AUTHORITY BOUNDARY: This registry does not authenticate or grant IAM rights.
         Its HTTP caller MUST separately enforce current tenant authorization;
         this delivery alone does not certify the legacy public employee API.
TRANSACTION BOUNDARY: Legacy reads use the process-owned Mongo connection;
         no write, index migration, or separate connection is created.
FINANCIAL AUTHORITY BOUNDARY: No payroll, release, execution, or settlement.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Optional

from pymongo.errors import PyMongoError

from ..domain.employee import EmployeeEntity
from ...kernel.db import get_database

VERSION = "v1.1.0-M03-HR01-STRICT-TENANT-BOUNDARY"
_RESERVED = frozenset({
    "MASTER", "GLOBAL_ROOT", "WILSY_ROOT", "WILSY_MASTER",
    "WILSY_GLOBAL_ROOT", "SOVEREIGN_ROOT",
})
logger = logging.getLogger(__name__)


class EmployeeRegistryBoundaryError(ValueError):
    """Fail-closed employee source scope/input rejection without record detail."""


def _tenant(tenant_id: str) -> str:
    """Require one exact, bounded, nonprivileged tenant supplied by authorized caller."""
    if (
        not isinstance(tenant_id, str)
        or not 1 <= len(tenant_id) <= 180
        or tenant_id != tenant_id.strip()
        or any(ord(char) <= 32 for char in tenant_id)
        or tenant_id.upper() in _RESERVED
    ):
        raise EmployeeRegistryBoundaryError("EMPLOYEE_TENANT_SCOPE_INVALID")
    return tenant_id


def _pagination(limit: int, offset: int) -> tuple[int, int]:
    """Bound database cursor work and reject bools masquerading as integers."""
    if (
        type(limit) is not int or not 1 <= limit <= 100
        or type(offset) is not int or not 0 <= offset <= 100000
    ):
        raise EmployeeRegistryBoundaryError("EMPLOYEE_PAGE_INVALID")
    return limit, offset


def _identifier(value: str, kind: str) -> str:
    """Require a nonempty bounded employee selector with no control characters."""
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 254
        or value != value.strip()
        or any(ord(char) < 32 for char in value)
    ):
        raise EmployeeRegistryBoundaryError("EMPLOYEE_" + kind + "_INVALID")
    return value


class EmployeeRegistry:
    """Read-only legacy employee source; caller owns current auth/IAM and PII projection."""

    def __init__(self) -> None:
        """Construct a connection-free facade; use kernel database at request time."""

    @staticmethod
    def _collection() -> Any:
        """Read the shared kernel employee collection; fail closed on missing source."""
        database = get_database()
        if database is None:
            raise RuntimeError("EMPLOYEE_REGISTRY_DATABASE_UNAVAILABLE")
        return database["employees"]

    def search_employees(
        self, tenant_id: str, query: str, limit: int = 20, offset: int = 0,
    ) -> list[EmployeeEntity]:
        """Search bounded employees with mandatory exact-tenant query predicates.

        This is not a public IAM decision. HTTP caller must authorize the
        requested tenant before invoking this method and redact sensitive fields.
        """
        tenant = _tenant(tenant_id)
        page_size, skip = _pagination(limit, offset)
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= 180:
            return []
        safe_term = re.escape(query.strip())
        conditions: list[dict[str, Any]] = [
            {"displayName": {"$regex": safe_term, "$options": "i"}},
            {"contact.workEmail": {"$regex": safe_term, "$options": "i"}},
            {"contact.personalEmail": {"$regex": safe_term, "$options": "i"}},
            {"employeeId": {"$regex": safe_term, "$options": "i"}},
        ]
        try:
            cursor = (
                self._collection().find({"tenantId": tenant, "$or": conditions})
                .sort("displayName", 1).skip(skip).limit(page_size)
            )
            return [EmployeeEntity.from_dict(document) for document in cursor]
        except PyMongoError:
            logger.error("EMPLOYEE_SEARCH_SOURCE_UNAVAILABLE")
            raise

    def get_employee_by_id(
        self, employee_id: str, tenant_id: str,
    ) -> Optional[EmployeeEntity]:
        """Read one exact-tenant employee; do not disclose cross-tenant existence."""
        tenant = _tenant(tenant_id)
        selector = _identifier(employee_id, "ID")
        try:
            document = self._collection().find_one(
                {"tenantId": tenant, "employeeId": selector}
            )
            return EmployeeEntity.from_dict(document) if document else None
        except PyMongoError:
            logger.error("EMPLOYEE_GET_SOURCE_UNAVAILABLE")
            raise

    def get_employee_by_email(
        self, email: str, tenant_id: str,
    ) -> Optional[EmployeeEntity]:
        """Read one exact-tenant employee by exact work/personal email."""
        tenant = _tenant(tenant_id)
        selector = _identifier(email, "EMAIL")
        try:
            document = self._collection().find_one({
                "tenantId": tenant,
                "$or": [
                    {"contact.workEmail": selector},
                    {"contact.personalEmail": selector},
                ],
            })
            return EmployeeEntity.from_dict(document) if document else None
        except PyMongoError:
            logger.error("EMPLOYEE_GET_SOURCE_UNAVAILABLE")
            raise

    def list_employees(
        self, tenant_id: str, limit: int = 100, offset: int = 0,
        active_only: bool = True,
    ) -> list[EmployeeEntity]:
        """List one validated tenant; caller must have current employee-read IAM."""
        tenant = _tenant(tenant_id)
        page_size, skip = _pagination(limit, offset)
        if type(active_only) is not bool:
            raise EmployeeRegistryBoundaryError("EMPLOYEE_ACTIVE_FILTER_INVALID")
        predicate: dict[str, Any] = {"tenantId": tenant}
        if active_only:
            predicate["isActive"] = True
        try:
            cursor = (
                self._collection().find(predicate)
                .sort("displayName", 1).skip(skip).limit(page_size)
            )
            return [EmployeeEntity.from_dict(document) for document in cursor]
        except PyMongoError:
            logger.error("EMPLOYEE_LIST_SOURCE_UNAVAILABLE")
            raise


_registry: Optional[EmployeeRegistry] = None


def get_employee_registry() -> EmployeeRegistry:
    """Return connection-free singleton; no implicit tenant or authorization."""
    global _registry
    if _registry is None:
        _registry = EmployeeRegistry()
    return _registry


# ARTIFACT: tools/eos/saas/employee/employee_registry.py
# VERSION: v1.1.0-M03-HR01-STRICT-TENANT-BOUNDARY
# AUTHORITY BOUNDARY: HTTP authenticates and authorizes; registry only scopes reads.
# TENANT POSTURE: Validated exact tenantId in every database predicate.
# FAIL-CLOSED POSTURE: Reserved tenant aliases and invalid selectors denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
