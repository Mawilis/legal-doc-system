"""TITLE: WILSY OS Tenant Business-Role Authority.
VERSION: v1.0.0-TENANT-BUSINESS-ROLE-AUTHORITY
AUTHORITY: Immutable tenant business-role fact only; no authorization.
EPITOME: Defines explicit, revisioned, scope-bound business-role evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_business_role.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-05.
CHANGELOG: v1.0.0 establishes the independent tenant business-role value contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Explicit identifiers and lifecycle provenance; no credentials or inference.
TENANT BOUNDARY: Every value binds one explicit principal_id and tenant_id.
AUTHORITY BOUNDARY: Fact evidence only; does not authenticate, authorize, execute, or persist.
FINANCIAL AUTHORITY BOUNDARY: No financial authority; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from tools.eos.auth.tenant_authority_policy import TENANT_ROLES


class TenantBusinessRoleStatus(str, Enum):
    """Lifecycle state for one tenant business-role authority record."""

    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


@dataclass(frozen=True, slots=True)
class TenantBusinessRoleAuthority:
    """Immutable business-role fact with independent revision and lifecycle evidence."""

    principal_id: str
    tenant_id: str
    business_role: str
    status: TenantBusinessRoleStatus
    revision: int
    effective_at: datetime
    revoked_at: datetime | None

    def __post_init__(self) -> None:
        """Reject malformed identifiers, roles, revisions, timestamps, and lifecycle states."""
        for name, value in (("principal_id", self.principal_id), ("tenant_id", self.tenant_id)):
            if not isinstance(value, str) or not value or value != value.strip():
                raise ValueError(f"{name} must be a non-empty trimmed string")
        if not isinstance(self.business_role, str) or self.business_role not in TENANT_ROLES:
            raise ValueError("business_role must be a canonical tenant business role")
        if not isinstance(self.status, TenantBusinessRoleStatus):
            raise TypeError("status must be a TenantBusinessRoleStatus")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 0:
            raise ValueError("revision must be a non-negative integer")
        if not isinstance(self.effective_at, datetime) or self.effective_at.tzinfo is None or self.effective_at.utcoffset() is None:
            raise ValueError("effective_at must be timezone-aware")
        if self.revoked_at is not None and (not isinstance(self.revoked_at, datetime) or self.revoked_at.tzinfo is None or self.revoked_at.utcoffset() is None):
            raise ValueError("revoked_at must be timezone-aware when present")
        if self.status is TenantBusinessRoleStatus.ACTIVE and self.revoked_at is not None:
            raise ValueError("ACTIVE business role cannot have revoked_at")
        if self.status is TenantBusinessRoleStatus.REVOKED:
            if self.revoked_at is None:
                raise ValueError("REVOKED business role requires revoked_at")
            if self.revoked_at < self.effective_at:
                raise ValueError("revoked_at cannot precede effective_at")


__all__ = ["TenantBusinessRoleStatus", "TenantBusinessRoleAuthority"]

# ARTIFACT: tenant_business_role.py
# VERSION: v1.0.0-TENANT-BUSINESS-ROLE-AUTHORITY
# AUTHORITY BOUNDARY: immutable business-role fact only; no authorization or persistence
# TENANT POSTURE: explicit principal/tenant scope; no inference or cross-tenant authority
# FAIL-CLOSED POSTURE: malformed identifiers, roles, revisions, timestamps, and lifecycle states reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
