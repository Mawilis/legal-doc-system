"""TITLE: WILSY OS Tenant Business Authority Policy Canon.
VERSION: v1.16.0-C1E-R1
AUTHORITY: Canonical business eligibility facts only; this module does not authorize.
EPITOME: Defines bounded tenant-role eligibility and field boundaries, including
own-tenant WILSY AI usage-capacity and billing-intelligence evidence read eligibility and dedicated
inbound-collection, merchant-configuration, provider-policy, and field-service
outcome/return roles.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authority_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-17.
CHANGELOG: 2026-09-17 v1.16.0-C1E-R1 adds least-privilege legal-advisory
generate/read eligibility for the seven approved tenant legal roles.
2026-09-17 v1.15.0-C1C-R1 adds least-privilege legal-services
execution eligibility for approved tenant legal and field-service roles.
2026-09-16 v1.14.0-C1B-R2 adds least-privilege reasoning execution
eligibility for tenant owner, admin, and manager roles.
2026-09-15 v1.13.0-L7B-WILSY-AI-LEGAL-TOOL-ELIGIBILITY adds
dedicated gateway read eligibility without broadening underlying legal roles.
2026-09-15 v1.12.0-L7B-LEGAL-OPERATIONS-IAM-ELIGIBILITY adds
explicit eligibility for authenticated field-service outcome and return
commands while preserving least privilege and denying finance/client mutation.
2026-09-15 v1.11.0-L7A-LEGAL-OPERATIONS-IAM-ELIGIBILITY adds
explicit tenant business-role eligibility for legal-practice personas.
2026-09-13 v1.10.0-M14-P3-BILLING-INTELLIGENCE-EVIDENCE-READ-ELIGIBILITY
adds billing-intelligence evidence read eligibility exactly to tenant_owner,
tenant_admin, tenant_manager, and tenant_auditor; specialized roles remain
denied and no permission binding or authorization authority is introduced.
2026-09-13 v1.9.0-M13-P6D-WILSY-AI-CAPACITY-READ-ELIGIBILITY adds
own-tenant WILSY AI usage-capacity read eligibility exactly to tenant_owner,
tenant_admin, tenant_manager, and tenant_auditor; specialized roles remain
denied and no permission or authorization authority is introduced.
v1.8.0-M11-R8-R3B-P8-P3D-P4A adds four distinct provider
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
TENANT BOUNDARY: Eligibility is own-tenant only; WILSY AI capacity-read and
billing-intelligence evidence-read eligibility, membership, and target scope
require separate composition.
AUTHORITY BOUNDARY: Does not authenticate, authorize, grant permissions, mutate memberships, assign roles, or provision tenants.
FINANCIAL AUTHORITY BOUNDARY: Every tenant role denies financial execution;
WILSY AI capacity-read and billing-intelligence evidence-read eligibility are
non-financial. Kennel EOS remains
exclusive.
"""
from __future__ import annotations
from enum import StrEnum
from types import MappingProxyType
from typing import Final, FrozenSet

VERSION = "v1.16.0-C1E-R1"
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
TENANT_ROLES: Final[FrozenSet[str]] = frozenset({"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor", "tenant_platform_billing_provider_policy_admin", "tenant_inbound_collection_authorization_admin", "tenant_inbound_merchant_configuration_admin", "tenant_inbound_provider_security_admin", "tenant_inbound_provider_policy_admin", "tenant_inbound_provider_policy_activation_admin", "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff", "tenant_deputy", "tenant_legal_client"})
OPERATIONS: FrozenSet[str] = frozenset({"profile_read", "profile_update", "lifecycle_create", "lifecycle_archive", "membership_read", "membership_invite", "membership_deactivate", "role_assignment_read", "role_grant", "role_revoke", "business_role_read", "business_role_assign", "business_role_change", "business_role_revoke", "platform_billing_provider_policy_create", "platform_billing_provider_policy_revise", "platform_billing_provider_policy_activate", "platform_billing_provider_policy_revoke", "inbound_collection_authorization_create", "tenant_inbound_merchant_configuration_register", "tenant_inbound_merchant_configuration_lifecycle_transition", "tenant_inbound_merchant_configuration_compromise", "tenant_inbound_merchant_configuration_remediate", "tenant_inbound_provider_policy_create", "tenant_inbound_provider_policy_revise", "tenant_inbound_provider_policy_activate", "tenant_inbound_provider_policy_deactivate", "tenant_inbound_provider_policy_emergency_disable", "tenant_inbound_provider_credential_security_eligibility_issue", "tenant_inbound_provider_credential_security_revoke", "tenant_inbound_provider_credential_security_compromise", "tenant_inbound_provider_credential_security_rotate", "wilsy_ai_usage_capacity_read", "wilsy_ai_reasoning_execute", "wilsy_ai_legal_services_execute", "billing_intelligence_evidence_read", "legal_instruction_read", "legal_instruction_write", "legal_allocation_read", "legal_allocation_write", "legal_attempt_read", "legal_attempt_write", "legal_return_read", "legal_billing_read", "legal_invoice_read", "audit_read", "artifact_read", "platform_billing_release", "plan_read", "plan_create", "plan_update", "plan_archive", "subscription_read", "subscription_audit_read", "subscription_metrics_read", "subscription_create", "subscription_update", "subscription_archive", "subscription_pause", "subscription_resume", "subscription_cancel", "subscription_upgrade", "subscription_downgrade", "subscription_reactivate", "cross_tenant", "financial_execution"})
ELIGIBILITY = MappingProxyType({
    "tenant_owner": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "profile_update": ELIGIBLE, "lifecycle_archive": ELIGIBLE, "membership_read": ELIGIBLE, "membership_invite": ELIGIBLE, "membership_deactivate": ELIGIBLE, "role_assignment_read": ELIGIBLE, "business_role_read": ELIGIBLE, "business_role_assign": ELIGIBLE, "business_role_change": ELIGIBLE, "business_role_revoke": ELIGIBLE, "audit_read": ELIGIBLE, "platform_billing_release": ELIGIBLE, "plan_read": ELIGIBLE, "plan_create": ELIGIBLE, "plan_update": ELIGIBLE, "plan_archive": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE, "subscription_create": ELIGIBLE, "subscription_update": ELIGIBLE, "subscription_archive": ELIGIBLE, "subscription_pause": ELIGIBLE, "subscription_resume": ELIGIBLE, "subscription_cancel": ELIGIBLE, "subscription_upgrade": ELIGIBLE, "subscription_downgrade": ELIGIBLE, "subscription_reactivate": ELIGIBLE, "wilsy_ai_usage_capacity_read": ELIGIBLE, "billing_intelligence_evidence_read": ELIGIBLE}),
    "tenant_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "profile_update": ELIGIBLE, "membership_read": ELIGIBLE, "membership_invite": ELIGIBLE, "membership_deactivate": ELIGIBLE, "role_assignment_read": ELIGIBLE, "role_grant": ELIGIBLE, "role_revoke": ELIGIBLE, "business_role_read": ELIGIBLE, "business_role_assign": ELIGIBLE, "business_role_change": ELIGIBLE, "business_role_revoke": ELIGIBLE, "audit_read": ELIGIBLE, "plan_read": ELIGIBLE, "plan_create": ELIGIBLE, "plan_update": ELIGIBLE, "plan_archive": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE, "subscription_create": ELIGIBLE, "subscription_update": ELIGIBLE, "subscription_archive": ELIGIBLE, "subscription_pause": ELIGIBLE, "subscription_resume": ELIGIBLE, "subscription_cancel": ELIGIBLE, "subscription_upgrade": ELIGIBLE, "subscription_downgrade": ELIGIBLE, "subscription_reactivate": ELIGIBLE, "wilsy_ai_usage_capacity_read": ELIGIBLE, "billing_intelligence_evidence_read": ELIGIBLE}),
    "tenant_manager": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "plan_read": ELIGIBLE, "plan_create": ELIGIBLE, "plan_update": ELIGIBLE, "plan_archive": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE, "subscription_create": ELIGIBLE, "subscription_update": ELIGIBLE, "subscription_archive": ELIGIBLE, "subscription_pause": ELIGIBLE, "subscription_resume": ELIGIBLE, "subscription_cancel": ELIGIBLE, "subscription_upgrade": ELIGIBLE, "subscription_downgrade": ELIGIBLE, "subscription_reactivate": ELIGIBLE, "wilsy_ai_usage_capacity_read": ELIGIBLE, "billing_intelligence_evidence_read": ELIGIBLE}),
    "tenant_auditor": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "profile_read": ELIGIBLE, "membership_read": ELIGIBLE, "role_assignment_read": ELIGIBLE, "business_role_read": ELIGIBLE, "audit_read": ELIGIBLE, "plan_read": ELIGIBLE, "subscription_read": ELIGIBLE, "subscription_audit_read": ELIGIBLE, "subscription_metrics_read": ELIGIBLE, "wilsy_ai_usage_capacity_read": ELIGIBLE, "billing_intelligence_evidence_read": ELIGIBLE}),
    "tenant_platform_billing_provider_policy_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "platform_billing_provider_policy_create": ELIGIBLE, "platform_billing_provider_policy_revise": ELIGIBLE, "platform_billing_provider_policy_activate": ELIGIBLE, "platform_billing_provider_policy_revoke": ELIGIBLE}),
    "tenant_accounts_payable_provider_policy_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "accounts_payable_provider_policy_create": ELIGIBLE, "accounts_payable_provider_policy_revise": ELIGIBLE, "accounts_payable_provider_policy_activate": ELIGIBLE, "accounts_payable_provider_policy_revoke": ELIGIBLE}),
    "tenant_inbound_collection_authorization_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "inbound_collection_authorization_create": ELIGIBLE}),
    "tenant_inbound_merchant_configuration_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_merchant_configuration_register": ELIGIBLE, "tenant_inbound_merchant_configuration_lifecycle_transition": ELIGIBLE}),
    "tenant_inbound_provider_security_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_merchant_configuration_compromise": ELIGIBLE, "tenant_inbound_merchant_configuration_remediate": ELIGIBLE, "tenant_inbound_provider_policy_emergency_disable": ELIGIBLE, "tenant_inbound_provider_credential_security_eligibility_issue": ELIGIBLE, "tenant_inbound_provider_credential_security_revoke": ELIGIBLE, "tenant_inbound_provider_credential_security_compromise": ELIGIBLE, "tenant_inbound_provider_credential_security_rotate": ELIGIBLE}),
    "tenant_inbound_provider_policy_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_provider_policy_create": ELIGIBLE, "tenant_inbound_provider_policy_revise": ELIGIBLE}),
    "tenant_inbound_provider_policy_activation_admin": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "tenant_inbound_provider_policy_activate": ELIGIBLE, "tenant_inbound_provider_policy_deactivate": ELIGIBLE}),
    "tenant_legal_partner": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_instruction_read": ELIGIBLE, "legal_instruction_write": ELIGIBLE, "legal_allocation_read": ELIGIBLE, "legal_allocation_write": ELIGIBLE, "legal_attempt_read": ELIGIBLE, "legal_return_read": ELIGIBLE, "legal_billing_read": ELIGIBLE, "legal_invoice_read": ELIGIBLE}),
    "tenant_legal_attorney": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_instruction_read": ELIGIBLE, "legal_instruction_write": ELIGIBLE, "legal_allocation_read": ELIGIBLE, "legal_allocation_write": ELIGIBLE, "legal_attempt_read": ELIGIBLE, "legal_return_read": ELIGIBLE, "legal_billing_read": ELIGIBLE, "legal_invoice_read": ELIGIBLE}),
    "tenant_legal_paralegal": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_instruction_read": ELIGIBLE, "legal_instruction_write": ELIGIBLE, "legal_allocation_read": ELIGIBLE, "legal_allocation_write": ELIGIBLE, "legal_attempt_read": ELIGIBLE, "legal_return_read": ELIGIBLE, "legal_invoice_read": ELIGIBLE}),
    "tenant_legal_secretary": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_instruction_read": ELIGIBLE, "legal_allocation_read": ELIGIBLE, "legal_attempt_read": ELIGIBLE, "legal_return_read": ELIGIBLE, "legal_invoice_read": ELIGIBLE}),
    "tenant_legal_finance": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_billing_read": ELIGIBLE, "legal_invoice_read": ELIGIBLE}),
    "tenant_sheriff": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_allocation_read": ELIGIBLE, "legal_allocation_write": ELIGIBLE, "legal_attempt_read": ELIGIBLE, "legal_attempt_write": ELIGIBLE, "legal_return_read": ELIGIBLE}),
    "tenant_deputy": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_attempt_read": ELIGIBLE, "legal_attempt_write": ELIGIBLE, "legal_return_read": ELIGIBLE}),
    "tenant_legal_client": MappingProxyType({**{operation: DENY for operation in OPERATIONS}, "legal_invoice_read": ELIGIBLE}),
})
OPERATIONS: FrozenSet[str] = frozenset((*OPERATIONS, "legal_attempt_outcome_write", "legal_return_write", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"))
_eligibility_updates = dict(ELIGIBILITY)
for _role in ("tenant_sheriff", "tenant_deputy", "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary"):
    _existing = dict(ELIGIBILITY[_role])
    if _role in {"tenant_sheriff", "tenant_deputy"}:
        _existing["legal_attempt_outcome_write"] = ELIGIBLE
    _existing["legal_return_write"] = ELIGIBLE
    _eligibility_updates[_role] = MappingProxyType(_existing)
ELIGIBILITY = MappingProxyType(_eligibility_updates)
_gateway_updates = dict(ELIGIBILITY)
for _role in ("tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff", "tenant_deputy"):
    _role_values = dict(_gateway_updates[_role])
    _role_values["wilsy_ai_legal_tool_read"] = ELIGIBLE
    _gateway_updates[_role] = MappingProxyType(_role_values)
ELIGIBILITY = MappingProxyType(_gateway_updates)

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
    if operation == "wilsy_ai_reasoning_execute":
        return ELIGIBLE if role in {"tenant_owner", "tenant_admin", "tenant_manager"} else DENY
    if operation == "wilsy_ai_legal_services_execute":
        return ELIGIBLE if role in {"tenant_owner", "tenant_admin", "tenant_manager", "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff", "tenant_deputy"} else DENY
    if operation in {"wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"}:
        return ELIGIBLE if role in {"tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff", "tenant_deputy"} else DENY
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
# VERSION: v1.16.0-C1E-R1
# AUTHORITY BOUNDARY: business eligibility facts only; no authorization or mutation
# TENANT POSTURE: own-tenant WILSY AI and billing-intelligence evidence eligibility requires separate ACTIVE membership and scope checks
# FAIL-CLOSED POSTURE: unknown roles and operations deny; ELIGIBLE never grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
