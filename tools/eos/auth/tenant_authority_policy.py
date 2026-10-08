"""TITLE: WILSY OS Tenant Business Authority Policy Canon.
VERSION: v1.36.0-CRM-P9C3-LEAD-BUSINESS-ROLE-POLICY
AUTHORITY: Canonical business eligibility facts only; this module does not authorize.
EPITOME: Defines bounded tenant-role eligibility and field boundaries, including
own-tenant WILSY AI usage-capacity and billing-intelligence evidence read eligibility and dedicated
inbound-collection, merchant-configuration, provider-policy, field-service
outcome/return roles, sheriff-only process-service directory provisioning, and
sheriff-only acceptance/office-receipt eligibility, plus an exact
tenant_legal_client-only client-matter projection read eligibility, plus the
exact Partner/Attorney-only firm-decision operation eligibility.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_authority_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
    2026-10-06 v1.36.0-CRM-P9C3-LEAD-BUSINESS-ROLE-POLICY
    introduces crm_lead_create and crm_lead_read as exact closed
    own-tenant operation vocabulary. Create is ELIGIBLE only for
    tenant_owner, tenant_admin and tenant_manager; read is ELIGIBLE
    for those roles plus tenant_auditor. Each operation maps exactly
    to its canonical crm:lead permission. Specialized Legal, HR,
    provider, finance and other tenant roles remain DENY. Eligibility
    alone proves no permission possession, assignment, subscription
    entitlement, quota, command execution or financial authority.
2026-10-04 v1.32.0-P0-C12E4B3B-HR-EMPLOYEE-RELATION-WRITE-ELIGIBILITY
admits the frozen 101-role HR catalogue into canonical tenant
business-role vocabulary and adds hr_employee_relation_write.
Exactly five formal Employee Relations business roles are ELIGIBLE;
the other 96 HR roles remain DENY. Existing non-HR eligibility is
unchanged and eligibility remains non-authorizing.
2026-10-02 v1.31.0-L10A2R-C4D6E-A3-P1C-LEGAL-EVIDENCE-CLEANUP-AUTHORITY-PARTNER-ELIGIBILITY
adds legal_evidence_cleanup_authorize as one exact own-tenant business
operation bound to legal_operations:evidence_cleanup:authorize and eligible
only to tenant_legal_partner. Eligibility remains policy-only and does not
establish ACTIVE membership, ACTIVE role assignment, A2 cleanup-authorization
binding, provider mutation, object deletion, cleanup execution, payment
execution or settlement truth.
 2026-09-29 v1.30.0-L10A3C-LEGAL-EVIDENCE-PARTNER-ELIGIBILITY
adds legal_evidence_write as one exact own-tenant business operation bound to
legal_operations:evidence:write and eligible only to tenant_legal_partner.
Eligibility remains policy-only and non-authorizing; every other tenant
business role remains denied. It does not establish ACTIVE membership, role
assignment, matter/document scope, ProcessDocument/custody mutation, Court or
Court Online filing, AI authority, billing, payment, execution or settlement.
2026-09-28 v1.29.0-L10-P2C4-D21B-BRANDING-ELIGIBILITY adds dedicated
tenant_branding read/profile/asset management operations. Read eligibility is
limited to tenant owner/admin/manager/auditor; profile and asset management is
limited to tenant owner/admin. Eligibility remains non-authorizing and does
not grant profile, asset, browser or financial execution authority.
2026-09-28 v1.28.0-L9C11-P21B-FIRM-REPRESENTATION-DECISION-ELIGIBILITY adds
legal_matter_representation_firm_decision_write as one exact own-tenant
operation eligible only to tenant_legal_partner and tenant_legal_attorney.
Eligibility remains non-authorizing and does not create a firm decision,
Representation, Court or financial authority.
2026-09-28 v1.27.0-L9C7C-ENGAGEMENT-FIRM-DECISION-ELIGIBILITY adds
legal_matter_engagement_firm_decision_write as one exact own-tenant operation
eligible only to tenant_legal_partner and tenant_legal_attorney. Eligibility
remains non-authorizing, does not bind a permission, and does not create an
Engagement, firm decision, Representation, Court or financial authority.
2026-09-27 v1.26.0-L9B10-P5-MANDATE-ACKNOWLEDGMENT-ELIGIBILITY adds
legal_matter_mandate_acknowledgment_write as one exact own-tenant operation
eligible only to tenant_legal_partner and tenant_legal_attorney. Eligibility
remains non-authorizing and does not create acknowledgment, mandate,
engagement, representation, Court or financial authority.
2026-09-26 v1.24.0-L9A3-CLIENT-ACCEPTANCE-ELIGIBILITY adds
legal_client_acceptance_write as one exact own-tenant client-acceptance
issuance operation eligible only to tenant_legal_client. Eligibility remains
non-authorizing and does not prove ACTIVE membership, role assignment,
CaseMatter/party scope, engagement, representation, Court, payment, execution
or settlement authority.
2026-09-26 v1.25.0-L9A4-P2B3-MATTER-ACCEPTANCE-APPROVAL-ELIGIBILITY adds
legal_matter_acceptance_instrument_approval_write only to tenant_legal_partner
and tenant_legal_attorney; eligibility remains non-authorizing and does not
create client acceptance, representation, Court or financial authority.
2026-09-25 v1.23.1-L8-8I-CONFLICT-REVIEW-ELIGIBILITY-REPAIR
preserves newly-added conflict-review eligibility while applying later legacy
Legal Operations eligibility augmentations by composing from the already-
updated role map rather than the pre-L8-8I snapshot. This repairs an authority-
loss defect only; approved roles, permission binding and all denial boundaries
are unchanged.
2026-09-25 v1.23.0-L8-8I-CONFLICT-REVIEW-ELIGIBILITY adds
legal_conflict_review_write as one exact own-tenant human conflict-review
operation mapped only to legal_operations:conflict_review:write and eligible
only to tenant_legal_partner and tenant_legal_attorney. Every other business
role remains denied. Eligibility remains non-authorizing and does not prove
ACTIVE membership, current authorization-role assignment, durable screening
evidence, reviewer identity, conflict finding, waiver, ethical wall, recusal,
engagement, representation, payment, execution or settlement authority.
2026-09-23 v1.22.0-L8-7D3-CLIENT-MATTER-READ-ELIGIBILITY adds legal_client_matter_read as an exact
own-tenant Legal Operations projection operation eligible only to
tenant_legal_client. Partner, attorney, paralegal, secretary, finance, sheriff,
deputy, owner/admin/manager/auditor, system and provider roles remain denied.
Eligibility remains non-authorizing and does not prove ACTIVE visibility,
matter scope, HTTP access, service/return evidence, billing, payment, execution
or settlement authority.
2026-09-23 v1.21.0-L8-7C3A-CLIENT-VISIBILITY-WRITE-ELIGIBILITY adds legal_client_visibility_write as a
dedicated own-tenant Legal Operations provisioning operation eligible exactly
to tenant_legal_partner, tenant_legal_attorney, and tenant_legal_paralegal.
LEGAL_CLIENT, secretary, finance, sheriff, deputy, owner/admin/manager/auditor,
system and provider roles remain denied. Eligibility remains non-authorizing
and grants no client read, matter visibility, service, billing, payment,
execution, or settlement authority.
2026-09-23 v1.20.0-L8-6C-DEPUTY-PERSONAL-QUEUE-IAM-ELIGIBILITY
adds legal_deputy_queue_read eligibility only to tenant_deputy for the
binding-scoped personal active-work projection. tenant_sheriff and every other
business role remain denied; this eligibility fact grants no authorization,
binding, lifecycle mutation, service, return, billing, AI, or financial truth.
2026-09-23 v1.19.0-L8-6A-SHERIFF-QUEUE-READ-IAM-ELIGIBILITY
adds legal_queue_read eligibility only to tenant_sheriff for certified
own-tenant operational-queue projection; tenant_deputy and every other
business role remain denied, and ELIGIBLE remains policy-only.
2026-09-23 v1.18.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-ELIGIBILITY
adds legal_receipt_write eligibility only to tenant_sheriff; receipt remains
distinct from allocation, attempt, service, and financial authority.
2026-09-23 v1.17.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-IAM-ELIGIBILITY
adds legal_directory_write eligibility only to tenant_sheriff; every other
business role remains denied and ELIGIBLE remains policy-only, never an
authorization grant.
2026-09-17 v1.16.0-C1E-R1 adds least-privilege legal-advisory
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
from tools.eos.auth.hr_business_role_catalog import ALL_HR_BUSINESS_ROLES

VERSION = "v1.36.0-CRM-P9C3-LEAD-BUSINESS-ROLE-POLICY"
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
    "crm_lead_create": "crm:lead:create",
    "crm_lead_read": "crm:lead:read",
    "crm_email_template_create": "crm:email_template:create",
    "crm_email_template_read": "crm:email_template:read",
    "crm_email_template_revise": "crm:email_template:revise",
    "crm_email_template_archive": "crm:email_template:archive",
    "crm_email_template_copy": "crm:email_template:copy",
    "crm_email_template_share": "crm:email_template:share",
    "legal_evidence_write": "legal_operations:evidence:write",
    "legal_evidence_cleanup_authorize": "legal_operations:evidence_cleanup:authorize",
    "hr_employee_relation_write": "hr:employee_relation:write",
    "hr_document_standard_employment_write": "hr:document:standard_employment:write",
    "hr_document_standard_employment_read": "hr:document:standard_employment:read",
    "hr_document_employee_relations_restricted_write": "hr:document:employee_relations_restricted:write",
    "hr_document_employee_relations_restricted_read": "hr:document:employee_relations_restricted:read",
    "hr_document_performance_restricted_write": "hr:document:performance_restricted:write",
    "hr_document_performance_restricted_read": "hr:document:performance_restricted:read",
    "hr_document_highly_sensitive_health_write": "hr:document:highly_sensitive_health:write",
    "hr_document_highly_sensitive_health_read": "hr:document:highly_sensitive_health:read",
    "hr_document_highly_sensitive_identity_write": "hr:document:highly_sensitive_identity:write",
    "hr_document_highly_sensitive_identity_read": "hr:document:highly_sensitive_identity:read",
    "hr_document_separation_restricted_write": "hr:document:separation_restricted:write",
    "hr_document_separation_restricted_read": "hr:document:separation_restricted:read",
    "hr_document_general_write": "hr:document:general:write",
    "hr_document_general_read": "hr:document:general:read",
    "legal_conflict_review_write": "legal_operations:conflict_review:write",
    "legal_client_acceptance_write": "legal_operations:client_acceptance:write",
    "legal_matter_acceptance_instrument_approval_write": "legal_operations:matter_acceptance_instrument_approval:write",
    "legal_matter_mandate_acknowledgment_write": "legal_operations:matter_mandate_acknowledgment:write",
    "legal_matter_representation_firm_decision_write": "legal_operations:matter_representation_firm_decision:write",
    "tenant_branding_read": "tenant_branding:read",
    "tenant_branding_profile_manage": "tenant_branding:profile:manage",
    "tenant_branding_asset_manage": "tenant_branding:asset:manage",
})
TENANT_ROLES: Final[FrozenSet[str]] = frozenset({"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor", "tenant_platform_billing_provider_policy_admin", "tenant_inbound_collection_authorization_admin", "tenant_inbound_merchant_configuration_admin", "tenant_inbound_provider_security_admin", "tenant_inbound_provider_policy_admin", "tenant_inbound_provider_policy_activation_admin", "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff", "tenant_deputy", "tenant_legal_client"}) | ALL_HR_BUSINESS_ROLES
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
OPERATIONS: FrozenSet[str] = frozenset((*OPERATIONS, "legal_directory_write", "legal_receipt_write", "legal_queue_read", "legal_deputy_queue_read", "legal_client_visibility_write", "legal_client_matter_read", "legal_conflict_review_write", "legal_client_acceptance_write", "legal_matter_acceptance_instrument_approval_write", "legal_matter_mandate_acknowledgment_write", "legal_matter_engagement_firm_decision_write", "legal_matter_representation_firm_decision_write", "legal_attempt_outcome_write", "legal_return_write", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"))
OPERATIONS: FrozenSet[str] = frozenset((*OPERATIONS, "tenant_branding_read", "tenant_branding_profile_manage", "tenant_branding_asset_manage"))
_eligibility_updates = dict(ELIGIBILITY)
_client_existing = dict(ELIGIBILITY["tenant_legal_client"])
_client_existing["legal_client_matter_read"] = ELIGIBLE
_client_existing["legal_client_acceptance_write"] = ELIGIBLE
_eligibility_updates["tenant_legal_client"] = MappingProxyType(_client_existing)
for _role in ("tenant_legal_partner", "tenant_legal_attorney"):
    _review_existing = dict(_eligibility_updates[_role])
    _review_existing["legal_conflict_review_write"] = ELIGIBLE
    _review_existing["legal_matter_acceptance_instrument_approval_write"] = ELIGIBLE
    _review_existing["legal_matter_mandate_acknowledgment_write"] = ELIGIBLE
    _review_existing["legal_matter_engagement_firm_decision_write"] = ELIGIBLE
    _review_existing["legal_matter_representation_firm_decision_write"] = ELIGIBLE
    _eligibility_updates[_role] = MappingProxyType(_review_existing)
for _role in ("tenant_sheriff", "tenant_deputy", "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary"):
    _existing = dict(_eligibility_updates[_role])
    if _role in {"tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal"}:
        _existing["legal_client_visibility_write"] = ELIGIBLE
    if _role == "tenant_sheriff":
        _existing["legal_directory_write"] = ELIGIBLE
        _existing["legal_receipt_write"] = ELIGIBLE
        _existing["legal_queue_read"] = ELIGIBLE
    if _role == "tenant_deputy":
        _existing["legal_deputy_queue_read"] = ELIGIBLE
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
_branding_updates = dict(ELIGIBILITY)
for _role in ("tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor"):
    _branding_read = dict(_branding_updates[_role])
    _branding_read["tenant_branding_read"] = ELIGIBLE
    _branding_updates[_role] = MappingProxyType(_branding_read)
for _role in ("tenant_owner", "tenant_admin"):
    _branding_manage = dict(_branding_updates[_role])
    _branding_manage["tenant_branding_profile_manage"] = ELIGIBLE
    _branding_manage["tenant_branding_asset_manage"] = ELIGIBLE
    _branding_updates[_role] = MappingProxyType(_branding_manage)
ELIGIBILITY = MappingProxyType(_branding_updates)

# L10A3C adds one exact Partner-only business operation. This extension occurs
# after prior eligibility composition so no other role can inherit it.
OPERATIONS: FrozenSet[str] = frozenset((*OPERATIONS, "legal_evidence_write"))
_evidence_updates = dict(ELIGIBILITY)
_partner_evidence = dict(_evidence_updates["tenant_legal_partner"])
_partner_evidence["legal_evidence_write"] = ELIGIBLE
_evidence_updates["tenant_legal_partner"] = MappingProxyType(_partner_evidence)
ELIGIBILITY = MappingProxyType(_evidence_updates)

# L10A2R-C4D6E-A3-P1C adds the separately authorized cleanup-command
# admission operation. ELIGIBLE remains only a business-role policy fact.
OPERATIONS: FrozenSet[str] = frozenset(
    (*OPERATIONS, "legal_evidence_cleanup_authorize")
)
_cleanup_authority_updates = dict(ELIGIBILITY)
_partner_cleanup_authority = dict(
    _cleanup_authority_updates["tenant_legal_partner"]
)
_partner_cleanup_authority[
    "legal_evidence_cleanup_authorize"
] = ELIGIBLE
_cleanup_authority_updates["tenant_legal_partner"] = MappingProxyType(
    _partner_cleanup_authority
)
ELIGIBILITY = MappingProxyType(_cleanup_authority_updates)


# P0-C12E4B3B: all 101 frozen HR roles enter the canonical
# tenant-business-role vocabulary. Exactly five are eligible
# for formal EmployeeRelation write; every other HR role denies.
OPERATIONS: FrozenSet[str] = frozenset(
    (*OPERATIONS, "hr_employee_relation_write")
)

_hr_relation_eligibility_updates = dict(ELIGIBILITY)

for _hr_business_role in (
    "tenant_hr_director",
    "tenant_hr_manager",
    "tenant_employee_relations_director",
    "tenant_employee_relations_manager",
    "tenant_employee_relations_specialist",
):
    _hr_role_eligibility = {
        operation: DENY
        for operation in OPERATIONS
    }
    _hr_role_eligibility[
        "hr_employee_relation_write"
    ] = ELIGIBLE

    _hr_relation_eligibility_updates[
        _hr_business_role
    ] = MappingProxyType(
        _hr_role_eligibility
    )

ELIGIBILITY = MappingProxyType(
    _hr_relation_eligibility_updates
)


# P0-C12F7B sensitivity-specific HR document eligibility.
_HR_DOCUMENT_OPERATION_ROLES: Final = MappingProxyType({
    "hr_document_standard_employment_write": frozenset({
        "tenant_hr_administrator",
        "tenant_hr_director",
        "tenant_hr_manager",
        "tenant_onboarding_coordinator",
        "tenant_onboarding_manager",
        "tenant_personnel_administrator",
    }),
    "hr_document_standard_employment_read": frozenset({
        "tenant_hr_administrator",
        "tenant_hr_business_partner",
        "tenant_hr_data_steward",
        "tenant_hr_director",
        "tenant_hr_generalist",
        "tenant_hr_manager",
        "tenant_hr_specialist",
        "tenant_offboarding_administrator",
        "tenant_onboarding_coordinator",
        "tenant_onboarding_manager",
        "tenant_personnel_administrator",
    }),
    "hr_document_employee_relations_restricted_write": frozenset({
        "tenant_employee_relations_director",
        "tenant_employee_relations_manager",
        "tenant_employee_relations_specialist",
        "tenant_hr_director",
        "tenant_hr_manager",
    }),
    "hr_document_employee_relations_restricted_read": frozenset({
        "tenant_disciplinary_case_manager",
        "tenant_disciplinary_outcome_approver",
        "tenant_employee_relations_director",
        "tenant_employee_relations_manager",
        "tenant_employee_relations_specialist",
        "tenant_grievance_manager",
        "tenant_hr_director",
        "tenant_hr_investigator",
        "tenant_hr_manager",
        "tenant_labour_relations_manager",
        "tenant_labour_relations_specialist",
    }),
    "hr_document_performance_restricted_write": frozenset({
        "tenant_hr_director",
        "tenant_hr_manager",
        "tenant_performance_director",
        "tenant_performance_manager",
        "tenant_performance_specialist",
    }),
    "hr_document_performance_restricted_read": frozenset({
        "tenant_hr_business_partner",
        "tenant_hr_director",
        "tenant_hr_manager",
        "tenant_performance_director",
        "tenant_performance_manager",
        "tenant_performance_specialist",
    }),
    "hr_document_highly_sensitive_health_write": frozenset({
        "tenant_health_safety_director",
        "tenant_health_safety_manager",
        "tenant_health_safety_officer",
        "tenant_occupational_health_administrator",
    }),
    "hr_document_highly_sensitive_health_read": frozenset({
        "tenant_health_safety_director",
        "tenant_health_safety_manager",
        "tenant_health_safety_officer",
        "tenant_occupational_health_administrator",
        "tenant_people_privacy_officer",
    }),
    "hr_document_highly_sensitive_identity_write": frozenset({
        "tenant_global_mobility_manager",
        "tenant_global_mobility_specialist",
        "tenant_immigration_administrator",
        "tenant_onboarding_coordinator",
        "tenant_onboarding_manager",
    }),
    "hr_document_highly_sensitive_identity_read": frozenset({
        "tenant_global_mobility_manager",
        "tenant_global_mobility_specialist",
        "tenant_immigration_administrator",
        "tenant_onboarding_coordinator",
        "tenant_onboarding_manager",
        "tenant_people_privacy_officer",
    }),
    "hr_document_separation_restricted_write": frozenset({
        "tenant_employee_relations_director",
        "tenant_employee_relations_manager",
        "tenant_employee_relations_specialist",
        "tenant_hr_director",
        "tenant_hr_manager",
        "tenant_offboarding_administrator",
    }),
    "hr_document_separation_restricted_read": frozenset({
        "tenant_employee_relations_director",
        "tenant_employee_relations_manager",
        "tenant_employee_relations_specialist",
        "tenant_hr_business_partner",
        "tenant_hr_director",
        "tenant_hr_generalist",
        "tenant_hr_manager",
        "tenant_offboarding_administrator",
    }),
    "hr_document_general_write": frozenset({
        "tenant_hr_administrator",
        "tenant_hr_director",
        "tenant_hr_manager",
        "tenant_personnel_administrator",
    }),
    "hr_document_general_read": frozenset({
        "tenant_hr_administrator",
        "tenant_hr_analyst",
        "tenant_hr_business_partner",
        "tenant_hr_director",
        "tenant_hr_generalist",
        "tenant_hr_manager",
        "tenant_hr_specialist",
        "tenant_personnel_administrator",
    }),
})

OPERATIONS: FrozenSet[str] = frozenset(
    (*OPERATIONS, *_HR_DOCUMENT_OPERATION_ROLES.keys())
)

_hr_document_eligibility_updates = dict(
    ELIGIBILITY
)

for (
    _hr_document_operation,
    _hr_document_roles,
) in _HR_DOCUMENT_OPERATION_ROLES.items():
    for _hr_document_business_role in _hr_document_roles:
        _current = dict(
            _hr_document_eligibility_updates.get(
                _hr_document_business_role,
                {},
            )
        )

        _current[
            _hr_document_operation
        ] = ELIGIBLE

        _hr_document_eligibility_updates[
            _hr_document_business_role
        ] = MappingProxyType(
            _current
        )

ELIGIBILITY = MappingProxyType(
    _hr_document_eligibility_updates
)


PROFILE_READABLE_FIELDS: Final[FrozenSet[str]] = frozenset({"name", "alias", "industry", "region", "sector", "legal_name", "tax_id", "contact_email", "plan", "status", "verified", "checksum", "proof_hash", "compliance_flags", "created_at", "updated_at"})
PROFILE_MUTABLE_FIELDS_V1: Final[FrozenSet[str]] = frozenset({"name", "alias", "industry", "region", "sector", "legal_name"})
LIFECYCLE_FIELDS: Final[FrozenSet[str]] = frozenset({"status"})
VERIFICATION_FIELDS: Final[FrozenSet[str]] = frozenset({"verified"})
BILLING_METADATA_FIELDS: Final[FrozenSet[str]] = frozenset({"plan"})
EVIDENCE_FIELDS: Final[FrozenSet[str]] = frozenset({"checksum", "proof_hash"})
SECURITY_SENSITIVE_FIELDS: Final[FrozenSet[str]] = frozenset({"tax_id", "contact_email", "compliance_flags"})
SYSTEM_MANAGED_FIELDS: Final[FrozenSet[str]] = frozenset({"created_at", "updated_at"})
FUTURE_PERMISSION_CANDIDATES: Final[FrozenSet[str]] = frozenset({"tenant:profile:read", "tenant:profile:write", "tenant:lifecycle:archive", "tenant:membership:read", "tenant:membership:write", "tenant:role_assignment:read", "tenant:role_assignment:write"})


# CRM P9C3 — canonical Lead operation/business-role policy.
#
# This policy expresses eligibility only. It does not prove permission
# possession, ACTIVE assignment, subscription entitlement, quota,
# command execution, persistence mutation, AI authority, or finance.
OPERATIONS: FrozenSet[str] = frozenset(
    (*OPERATIONS, "crm_lead_create", "crm_lead_read")
)

_crm_eligibility_updates = dict(ELIGIBILITY)

for _crm_role in (
    "tenant_owner",
    "tenant_admin",
    "tenant_manager",
):
    _crm_role_policy = dict(
        _crm_eligibility_updates[_crm_role]
    )
    _crm_role_policy["crm_lead_create"] = ELIGIBLE
    _crm_role_policy["crm_lead_read"] = ELIGIBLE
    _crm_eligibility_updates[_crm_role] = MappingProxyType(
        _crm_role_policy
    )

_crm_auditor_policy = dict(
    _crm_eligibility_updates["tenant_auditor"]
)
_crm_auditor_policy["crm_lead_read"] = ELIGIBLE
_crm_auditor_policy["crm_lead_create"] = DENY
_crm_eligibility_updates["tenant_auditor"] = MappingProxyType(
    _crm_auditor_policy
)

ELIGIBILITY = MappingProxyType(_crm_eligibility_updates)


# CRM Email Template — bounded tenant-operation eligibility only.
# These facts do not grant permissions, record access, entitlement,
# mailbox use, sending, consent, sequence execution, AI, or finance.
_EMAIL_TEMPLATE_OPERATIONS = (
    "crm_email_template_create",
    "crm_email_template_read",
    "crm_email_template_revise",
    "crm_email_template_archive",
    "crm_email_template_copy",
    "crm_email_template_share",
)

OPERATIONS = frozenset((*OPERATIONS, *_EMAIL_TEMPLATE_OPERATIONS))

_email_template_eligibility_updates = dict(ELIGIBILITY)

for _template_business_role in (
    "tenant_owner",
    "tenant_admin",
    "tenant_manager",
):
    _template_role_policy = dict(
        _email_template_eligibility_updates[_template_business_role]
    )
    for _template_operation in _EMAIL_TEMPLATE_OPERATIONS:
        _template_role_policy[_template_operation] = ELIGIBLE
    _email_template_eligibility_updates[
        _template_business_role
    ] = MappingProxyType(_template_role_policy)

_template_auditor_policy = dict(
    _email_template_eligibility_updates["tenant_auditor"]
)
for _template_operation in _EMAIL_TEMPLATE_OPERATIONS:
    _template_auditor_policy[_template_operation] = (
        ELIGIBLE
        if _template_operation == "crm_email_template_read"
        else DENY
    )
_email_template_eligibility_updates[
    "tenant_auditor"
] = MappingProxyType(_template_auditor_policy)

ELIGIBILITY = MappingProxyType(
    _email_template_eligibility_updates
)



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
# VERSION: v1.36.0-CRM-P9C3-LEAD-BUSINESS-ROLE-POLICY
# AUTHORITY BOUNDARY: business eligibility facts only; no authorization or mutation
# TENANT POSTURE: own-tenant conflict-review, client-matter and client-visibility eligibility require separate ACTIVE membership, assignment and exact permission binding; client visibility remains separately scope-bound
# FAIL-CLOSED POSTURE: unknown roles and operations deny; ELIGIBLE never grants access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
