"""TITLE: WILSY OS Tenant Business Authority Policy Canon.
VERSION: v1.8.0-M11-R8-R3B-P8-P3D-P4A
AUTHORITY: Canonical business eligibility facts only; this module does not authorize.
EPITOME: Defines bounded tenant-role eligibility and field boundaries, including
dedicated inbound-collection, merchant-configuration, and provider-policy roles.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authority_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-09.
CHANGELOG: v1.8.0-M11-R8-R3B-P8-P3D-P4A adds four distinct provider
credential-security operation eligibilities to the existing security-admin
business role; no new role or execution authority is introduced.
v1.7.0-M11-R8-R3B-P8-P3B-I2-R3 adds the explicit
tenant_inbound_merchant_configuration_remediate eligibility for the existing
security-admin business role; only future COMPROMISED-to-DISABLED remediation
is represented.
v1.6.0-M11-R8-R3B-P8-P3A adds the explicit
tenant inbound merchant-configuration and provider-policy operation eligibility
for four dedicated business roles; no tenant-owner/admin bypass is introduced.
v1.5.0-M11-R8-R3B-P6A adds the explicit
tenant_inbound_collection_authorization_admin eligibility for exactly
inbound_collection_authorization_create; no typed authorization is issued.
v1.3.0 adds distinct business-role read/assign/change/revoke
eligibility without implementing delegation or authorization; v1.2.0 runtime
VERSION is the canonical policy provenance source;
v1.1.0 adds platform_billing_release as a high-consequence
tenant commercial-liability operation eligible only to tenant_owner; tenant_admin,
tenant_manager, and tenant_auditor remain ineligible, financial_execution remains
explicitly denied, and no financial or Kennel authority is created.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure deterministic metadata; no persistence,
credentials, network, or implicit authority.
TENANT BOUNDARY: Eligibility is own-tenant only; membership and target scope require separate composition.
AUTHORITY BOUNDARY: Does not authenticate, authorize, grant permissions, mutate memberships, assign roles, or provision tenants.
FINANCIAL AUTHORITY BOUNDARY: Every tenant role denies financial execution; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from enum import StrEnum
from types import MappingProxyType
from typing import Final, FrozenSet

VERSION = "v1.8.0-M11-R8-R3B-P8-P3D-P4A"
class SystemAuthorityClassification(StrEnum):
    SYSTEM_REQUIRED = "SYSTEM_REQUIRED"
    SYSTEM_NOT_INHERENTLY_REQUIRED = "SYSTEM_NOT_INHERENTLY_REQUIRED"
    UNKNOWN = "UNKNOWN"
ELIGIBLE, DENY = "ELIGIBLE", "DENY"
BUSINESS_ROLE_OPERATION_PERMISSIONS: Final = MappingProxyType({
    "business_role_read": "tenant:business_role:read",
    "business_role_assign": "tenant:business_role:write",
    "business_role_change": "tenant:business_role:write",
    "business_role_revoke": "tenant:business_role:write",
})
TENANT_ROLES: Final[FrozenSet[str]] = frozenset({"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor", "tenant_platform_billing_provider_policy_admin", "tenant_inbound_collection_authorization_admin", "tenant_inbound_merchant_configuration_admin", "tenant_inbound_provider_security_admin", "tenant_inbound_provider_policy_admin", "tenant_inbound_provider_policy_activation_admin"})
OPERATIONS: Final[FrozenSet[str]] = frozenset({"profile_read", "profile_update", "lifecycle_create", "lifecycle_archive", "membership_read", "membership_invite", "membership_deactivate", "role_assignment_read", "role_grant", "role_revoke", "business_role_read", "business_role_assign", "business_role_change", "business_role_revoke", "platform_billing_provider_policy_create", "platform_billing_provider_policy_revise", "platform_billing_provider_policy_activate", "platform_billing_provider_policy_revoke", "inbound_collection_authorization_create", "tenant_inbound_merchant_configuration_register", "tenant_inbound_merchant_configuration_lifecycle_transition", "tenant_inbound_merchant_configuration_compromise", "tenant_inbound_merchant_configuration_remediate", "tenant_inbound_provider_policy_create", "tenant_inbound_provider_policy_revise", "tenant_inbound_provider_policy_activate", "tenant_inbound_provider_policy_deactivate", "tenant_inbound_provider_policy_emergency_disable", "tenant_inbound_provider_credential_security_eligibility_issue", "tenant_inbound_provider_credential_security_revoke", "tenant_inbound_provider_credential_security_compromise", "tenant_inbound_provider_credential_security_rotate", "audit_read", "artifact_read", "platform_billing_release", "plan_read", "plan_create", "plan_update", "plan_archive", "subscription_read", "subscription_audit_read", "subscription_metrics_read", "subscription_create", "subscription_update", "subscription_archive", "subscription_pause", "subscription_resume", "subscription_cancel", "subscription_upgrade", "subscription_downgrade", "subscription_reactivate", "cross_tenant", "financial_execution"})
ELIGIBILITY: Final = MappingProxyType({
    "tenant_owner": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "profile_update": ELIGIBLE, "lifecycle_archive": ELIGIBLE, "membership_read": ELIGIBLE, "membership_invite": ELIGIBLE, "membership_deactivate": ELIGIBLE, "role_assignment_read": ELIGIBLE, "business_role_read": ELIGIBLE, "business_role_assign": ELIGIBLE, "business_role_change": ELIGIBLE, "business_role_revoke": ELIGIBLE, "audit_read": ELIGIBLE, "platform_billing_release": ELIGIBLE, "plan_read": ELIGIBLE, "plan_create": ELIGIBLE, "plan_update": ELIGIBLE, "plan_archive": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE, "subscription_create": ELIGIBLE, "subscription_update": ELIGIBLE, "subscription_archive": ELIGIBLE, "subscription_pause": ELIGIBLE, "subscription_resume": ELIGIBLE, "subscription_cancel": ELIGIBLE, "subscription_upgrade": ELIGIBLE, "subscription_downgrade": ELIGIBLE, "subscription_reactivate": ELIGIBLE}),
    "tenant_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "profile_update": ELIGIBLE, "membership_read": ELIGIBLE, "membership_invite": ELIGIBLE, "membership_deactivate": ELIGIBLE, "role_assignment_read": ELIGIBLE, "role_grant": ELIGIBLE, "role_revoke": ELIGIBLE, "business_role_read": ELIGIBLE, "business_role_assign": ELIGIBLE, "business_role_change": ELIGIBLE, "business_role_revoke": ELIGIBLE, "audit_read": ELIGIBLE, "plan_read": ELIGIBLE, "plan_create": ELIGIBLE, "plan_update": ELIGIBLE, "plan_archive": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE, "subscription_create": ELIGIBLE, "subscription_update": ELIGIBLE, "subscription_archive": ELIGIBLE, "subscription_pause": ELIGIBLE, "subscription_resume": ELIGIBLE, "subscription_cancel": ELIGIBLE, "subscription_upgrade": ELIGIBLE, "subscription_downgrade": ELIGIBLE, "subscription_reactivate": ELIGIBLE}),
    "tenant_manager": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "plan_read": ELIGIBLE, "plan_create": ELIGIBLE, "plan_update": ELIGIBLE, "plan_archive": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE, "subscription_create": ELIGIBLE, "subscription_update": ELIGIBLE, "subscription_archive": ELIGIBLE, "subscription_pause": ELIGIBLE, "subscription_resume": ELIGIBLE, "subscription_cancel": ELIGIBLE, "subscription_upgrade": ELIGIBLE, "subscription_downgrade": ELIGIBLE, "subscription_reactivate": ELIGIBLE}),
    "tenant_auditor": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "membership_read": ELIGIBLE, "role_assignment_read": ELIGIBLE, "business_role_read": ELIGIBLE, "audit_read": ELIGIBLE, "plan_read": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE}),
    "tenant_platform_billing_provider_policy_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "platform_billing_provider_policy_create": ELIGIBLE, "platform_billing_provider_policy_revise": ELIGIBLE, "platform_billing_provider_policy_activate": ELIGIBLE, "platform_billing_provider_policy_revoke": ELIGIBLE}),
    "tenant_accounts_payable_provider_policy_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "accounts_payable_provider_policy_create": ELIGIBLE, "accounts_payable_provider_policy_revise": ELIGIBLE, "accounts_payable_provider_policy_activate": ELIGIBLE, "accounts_payable_provider_policy_revoke": ELIGIBLE}),
    "tenant_inbound_collection_authorization_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "inbound_collection_authorization_create": ELIGIBLE}),
    "tenant_inbound_merchant_configuration_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_merchant_configuration_register": ELIGIBLE, "tenant_inbound_merchant_configuration_lifecycle_transition": ELIGIBLE}),
    "tenant_inbound_provider_security_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_merchant_configuration_compromise": ELIGIBLE, "tenant_inbound_merchant_configuration_remediate": ELIGIBLE, "tenant_inbound_provider_policy_emergency_disable": ELIGIBLE, "tenant_inbound_provider_credential_security_eligibility_issue": ELIGIBLE, "tenant_inbound_provider_credential_security_revoke": ELIGIBLE, "tenant_inbound_provider_credential_security_compromise": ELIGIBLE, "tenant_inbound_provider_credential_security_rotate": ELIGIBLE}),
    "tenant_inbound_provider_policy_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_provider_policy_create": ELIGIBLE, "tenant_inbound_provider_policy_revise": ELIGIBLE}),
    "tenant_inbound_provider_policy_activation_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_provider_policy_activate": ELIGIBLE, "tenant_inbound_provider_policy_deactivate": ELIGIBLE}),
})
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

def permission_for_business_role_operation(operation: object) -> str | None:
    """Return the canonical permission for a business-role operation."""
    return BUSINESS_ROLE_OPERATION_PERMISSIONS.get(operation) if isinstance(operation, str) else None

def allowed_profile_mutation_fields(role: object) -> FrozenSet[str]:
    """Return the bounded v1 field set for owner/admin, else empty."""
    return PROFILE_MUTABLE_FIELDS_V1 if role in {"tenant_owner", "tenant_admin"} else frozenset()

def is_hard_delete_allowed(_: object = None) -> bool:
    """Hard deletion is prohibited; future DELETE semantics are archive-only."""
    return False

def requires_system_authority(operation: object) -> SystemAuthorityClassification:
    """Classify SYSTEM scope; unknown or malformed operations return UNKNOWN."""
    if not isinstance(operation, str): return SystemAuthorityClassification.UNKNOWN
    if operation in {"lifecycle_create", "cross_tenant", "platform_lifecycle"}: return SystemAuthorityClassification.SYSTEM_REQUIRED
    if operation in OPERATIONS or operation == "lifecycle_archive": return SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    return SystemAuthorityClassification.UNKNOWN

__all__ = ["VERSION", "ELIGIBLE", "DENY", "SystemAuthorityClassification", "TENANT_ROLES", "OPERATIONS", "ELIGIBILITY", "BUSINESS_ROLE_OPERATION_PERMISSIONS", "PROFILE_READABLE_FIELDS", "PROFILE_MUTABLE_FIELDS_V1", "LIFECYCLE_FIELDS", "VERIFICATION_FIELDS", "BILLING_METADATA_FIELDS", "EVIDENCE_FIELDS", "SECURITY_SENSITIVE_FIELDS", "SYSTEM_MANAGED_FIELDS", "FUTURE_PERMISSION_CANDIDATES", "normalize_tenant_business_role", "tenant_role_operation_eligibility", "permission_for_business_role_operation", "allowed_profile_mutation_fields", "is_hard_delete_allowed", "requires_system_authority"]

# ARTIFACT: tenant_authority_policy.py
# VERSION: v1.8.0-M11-R8-R3B-P8-P3D-P4A
# AUTHORITY BOUNDARY: business eligibility facts only; no authorization or mutation
# TENANT POSTURE: own-tenant eligibility requires separate ACTIVE membership and scope checks
# FAIL-CLOSED POSTURE: unknown roles and operations deny; ELIGIBLE never grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
