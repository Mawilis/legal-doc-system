"""TITLE: WILSY OS Tenant Business Authority Policy Canon.
VERSION: v1.0.0-TENANT-AUTHORITY-POLICY-CANON
AUTHORITY: Canonical business eligibility facts only; this module does not authorize.
EPITOME: Defines bounded tenant-role eligibility and field boundaries for future composition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authority_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 establishes immutable tenant business-role eligibility, profile boundaries, and fail-closed policy APIs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure deterministic metadata; no persistence, credentials, network, or implicit authority.
TENANT BOUNDARY: Eligibility is own-tenant only; membership and target scope require separate composition.
AUTHORITY BOUNDARY: Does not authenticate, authorize, grant permissions, mutate memberships, assign roles, or provision tenants.
FINANCIAL AUTHORITY BOUNDARY: Every tenant role denies financial execution; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from types import MappingProxyType
from typing import Final, FrozenSet

VERSION = "v1.0.0-TENANT-AUTHORITY-POLICY-CANON"
ELIGIBLE, DENY = "ELIGIBLE", "DENY"
TENANT_ROLES: Final[FrozenSet[str]] = frozenset({"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor"})
OPERATIONS: Final[FrozenSet[str]] = frozenset({"profile_read", "profile_update", "lifecycle_create", "lifecycle_archive", "membership_read", "membership_invite", "membership_deactivate", "role_assignment_read", "role_grant", "role_revoke", "audit_read", "artifact_read", "cross_tenant", "financial_execution"})
_OWNER = {"profile_read": ELIGIBLE, "profile_update": ELIGIBLE, "lifecycle_create": DENY, "lifecycle_archive": ELIGIBLE, "membership_read": ELIGIBLE, "membership_invite": ELIGIBLE, "membership_deactivate": ELIGIBLE, "role_assignment_read": ELIGIBLE, "role_grant": DENY, "role_revoke": DENY, "audit_read": ELIGIBLE, "artifact_read": DENY, "cross_tenant": DENY, "financial_execution": DENY}
_ADMIN = {**_OWNER, "lifecycle_archive": DENY, "role_grant": ELIGIBLE, "role_revoke": ELIGIBLE}
_MANAGER = {operation: DENY for operation in OPERATIONS} | {"profile_read": ELIGIBLE}
_AUDITOR = {operation: DENY for operation in OPERATIONS} | {"profile_read": ELIGIBLE, "membership_read": ELIGIBLE, "role_assignment_read": ELIGIBLE, "audit_read": ELIGIBLE}
ELIGIBILITY: Final = MappingProxyType({"tenant_owner": MappingProxyType(_OWNER), "tenant_admin": MappingProxyType(_ADMIN), "tenant_manager": MappingProxyType(_MANAGER), "tenant_auditor": MappingProxyType(_AUDITOR)})
PROFILE_READABLE_FIELDS: Final[FrozenSet[str]] = frozenset({"name", "alias", "industry", "region", "sector", "legal_name", "tax_id", "contact_email", "plan", "status", "verified", "checksum", "proof_hash", "compliance_flags", "created_at", "updated_at"})
PROFILE_MUTABLE_FIELDS_V1: Final[FrozenSet[str]] = frozenset({"name", "alias", "industry", "region", "sector", "legal_name"})
LIFECYCLE_FIELDS: Final[FrozenSet[str]] = frozenset({"status"})
VERIFICATION_FIELDS: Final[FrozenSet[str]] = frozenset({"verified"})
BILLING_METADATA_FIELDS: Final[FrozenSet[str]] = frozenset({"plan"})
EVIDENCE_FIELDS: Final[FrozenSet[str]] = frozenset({"checksum", "proof_hash"})
SECURITY_SENSITIVE_FIELDS: Final[FrozenSet[str]] = frozenset({"tax_id", "contact_email", "compliance_flags"})
SYSTEM_MANAGED_FIELDS: Final[FrozenSet[str]] = frozenset({"created_at", "updated_at"})
FUTURE_PERMISSION_CANDIDATES: Final[FrozenSet[str]] = frozenset({"tenant:profile:read", "tenant:profile:write", "tenant:lifecycle:archive", "tenant:membership:read", "tenant:membership:write", "tenant:role_assignment:read", "tenant:role_assignment:write"})

def normalize_tenant_business_role(role: object) -> str | None:
    """Return an exact canonical tenant role, otherwise fail closed."""
    return role if isinstance(role, str) and role in TENANT_ROLES else None

def tenant_role_operation_eligibility(role: object, operation: object) -> str:
    """Return business eligibility only; ELIGIBLE is never an authorization grant."""
    if not isinstance(role, str) or not isinstance(operation, str): return DENY
    return ELIGIBILITY.get(role, {}).get(operation, DENY)

def allowed_profile_mutation_fields(role: object) -> FrozenSet[str]:
    """Return the bounded v1 field set for owner/admin, else empty."""
    return PROFILE_MUTABLE_FIELDS_V1 if role in {"tenant_owner", "tenant_admin"} else frozenset()

def is_hard_delete_allowed(_: object = None) -> bool:
    """Hard deletion is prohibited; future DELETE semantics are archive-only."""
    return False

def requires_system_authority(operation: object) -> bool:
    """Identify operations requiring a future explicit SYSTEM capability."""
    return operation in {"lifecycle_create", "cross_tenant", "lifecycle_archive"}

__all__ = ["VERSION", "ELIGIBLE", "DENY", "TENANT_ROLES", "OPERATIONS", "ELIGIBILITY", "PROFILE_READABLE_FIELDS", "PROFILE_MUTABLE_FIELDS_V1", "LIFECYCLE_FIELDS", "VERIFICATION_FIELDS", "BILLING_METADATA_FIELDS", "EVIDENCE_FIELDS", "SECURITY_SENSITIVE_FIELDS", "SYSTEM_MANAGED_FIELDS", "FUTURE_PERMISSION_CANDIDATES", "normalize_tenant_business_role", "tenant_role_operation_eligibility", "allowed_profile_mutation_fields", "is_hard_delete_allowed", "requires_system_authority"]

# ARTIFACT: tenant_authority_policy.py
# VERSION: v1.0.0-TENANT-AUTHORITY-POLICY-CANON
# AUTHORITY BOUNDARY: business eligibility facts only; no authorization or mutation
# TENANT POSTURE: own-tenant eligibility requires separate ACTIVE membership and scope checks
# FAIL-CLOSED POSTURE: unknown roles and operations deny; ELIGIBLE never grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
