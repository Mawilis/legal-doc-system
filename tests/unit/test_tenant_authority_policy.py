"""TITLE: Tenant Authority Policy Certification.
VERSION: v1.14.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-ELIGIBILITY-CERT
AUTHORITY: Pure policy-canon certification only.
EPITOME: Proves immutable tenant eligibility, WILSY AI usage-capacity and
billing-intelligence evidence-read eligibility, and non-authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authority_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-23.
CHANGELOG: 2026-09-23 v1.14.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-ELIGIBILITY-CERT
certifies legal_receipt_write eligibility only for tenant_sheriff and explicit
denial for every other tenant business role.
2026-09-23 v1.13.0-L8-1-LEGAL-OPERATIONS-DIRECTORY-IAM-ELIGIBILITY-CERT
certifies legal_directory_write eligibility only for tenant_sheriff and explicit
denial for every other tenant business role; policy remains non-authorizing.
2026-09-17 v1.12.0-C1E-R1 certifies exact seven-role legal-advisory
eligibility for generate/read operations.
2026-09-15 v1.9.0-L7B-WILSY-AI-LEGAL-TOOL-ELIGIBILITY-CERT certifies
the bounded WILSY AI Legal Tool Gateway eligibility for seven legal personas,
with tenant clients and administrative roles denied and no financial authority.
2026-09-15 v1.8.0-L7A-LEGAL-OPERATIONS-IAM-ELIGIBILITY-CERT
certifies the explicit legal-practice role vocabulary and least-authority matrix.
2026-09-13 v1.7.0-M14-P3-BILLING-INTELLIGENCE-EVIDENCE-READ-ELIGIBILITY-CERT
certifies billing-intelligence evidence-read eligibility for exactly the four
general tenant business roles while preserving specialized-role denial.
2026-09-13 v1.6.0-M13-P6D-WILSY-AI-CAPACITY-READ-ELIGIBILITY-CERT
certifies own-tenant WILSY AI usage-capacity read eligibility for exactly the
four general tenant business roles and preserves specialized-role denial.
v1.5.0-M11-R8-R3B-P8-P3D-P4A-CERT certifies four distinct
credential-security operations on the existing security-admin business role.
v1.4.0-M11-R8-R3B-P8-P3B-I2-R3-CERT certifies the dedicated
merchant-configuration remediation operation on the existing security role.
v1.3.0-M11-R8-R3B-P8-P3A-CERT certifies eight dedicated inbound
merchant-configuration/provider-policy operations and four least-privilege
business-role eligibility mappings.
v1.2.0-M11-R8-R3B-P6A-CERT certifies the explicit inbound
collection authorization operation and dedicated tenant business-role eligibility.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: No network, persistence, or sensitive data.
TENANT BOUNDARY: Policy facts do not prove membership or scope; WILSY AI
capacity-read and billing-intelligence evidence-read eligibility remain
own-tenant and separately composed.
AUTHORITY BOUNDARY: Tests do not authorize or mutate.
FINANCIAL AUTHORITY BOUNDARY: Capacity-read and billing-intelligence
evidence-read eligibility are non-financial; Kennel EOS remains exclusive.
"""
from tools.eos.auth.tenant_authority_policy import *
import pytest

def test_runtime_version_source_is_canonical() -> None:
    assert VERSION == "v1.18.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-ELIGIBILITY"

LEGACY = ("AUDITOR", "SOVEREIGN_ARCHITECT", "ENTERPRISE_ADMIN", "FOUNDER", "SUPER_ADMIN", "ADMIN", "admin", "GLOBAL_ROOT", "WILSY_ROOT", "MASTER", "unknown")

def test_matrix_boundaries() -> None:
    assert TENANT_ROLES == {"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor", "tenant_platform_billing_provider_policy_admin", "tenant_inbound_collection_authorization_admin", "tenant_inbound_merchant_configuration_admin", "tenant_inbound_provider_security_admin", "tenant_inbound_provider_policy_admin", "tenant_inbound_provider_policy_activation_admin", "tenant_legal_partner", "tenant_legal_attorney", "tenant_legal_paralegal", "tenant_legal_secretary", "tenant_legal_finance", "tenant_sheriff", "tenant_deputy", "tenant_legal_client"}
    assert all(tenant_role_operation_eligibility(role, "financial_execution") == DENY for role in TENANT_ROLES)
    assert all(tenant_role_operation_eligibility(role, "cross_tenant") == DENY for role in TENANT_ROLES)
    assert tenant_role_operation_eligibility("tenant_manager", "profile_update") == DENY
    assert tenant_role_operation_eligibility("tenant_auditor", "artifact_read") == DENY
    assert tenant_role_operation_eligibility("tenant_owner", "role_grant") == DENY
    assert tenant_role_operation_eligibility("tenant_admin", "lifecycle_archive") == DENY
    assert tenant_role_operation_eligibility("tenant_owner", "lifecycle_create") == DENY
    assert normalize_tenant_business_role("SUPER_ADMIN") is None
    assert normalize_tenant_business_role("AUDITOR") is None
    assert tenant_role_operation_eligibility("unknown", "profile_read") == DENY
    assert is_hard_delete_allowed() is False
    assert all(normalize_tenant_business_role(value) is None for value in LEGACY)
    assert tenant_role_operation_eligibility("unknown", "unknown_operation") == DENY
    assert tenant_role_operation_eligibility("tenant_auditor", "profile_update") == DENY
    assert tenant_role_operation_eligibility("tenant_auditor", "membership_invite") == DENY
    assert tenant_role_operation_eligibility("tenant_auditor", "role_grant") == DENY
    assert tenant_role_operation_eligibility("tenant_auditor", "role_revoke") == DENY
    assert tenant_role_operation_eligibility("tenant_owner", "role_revoke") == DENY
    assert tenant_role_operation_eligibility("tenant_admin", "lifecycle_create") == DENY
    assert tenant_role_operation_eligibility("tenant_manager", "membership_read") == DENY
    assert tenant_role_operation_eligibility("tenant_manager", "role_assignment_read") == DENY


def test_legal_business_role_matrix_is_explicit_and_least_authority() -> None:
    """Each legal persona has bounded eligibility and no financial execution."""
    expected = {
        "tenant_legal_partner": {"legal_instruction_read", "legal_instruction_write", "legal_allocation_read", "legal_allocation_write", "legal_attempt_read", "legal_return_read", "legal_return_write", "legal_billing_read", "legal_invoice_read", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_services_execute", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"},
        "tenant_legal_attorney": {"legal_instruction_read", "legal_instruction_write", "legal_allocation_read", "legal_allocation_write", "legal_attempt_read", "legal_return_read", "legal_return_write", "legal_billing_read", "legal_invoice_read", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_services_execute", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"},
        "tenant_legal_paralegal": {"legal_instruction_read", "legal_instruction_write", "legal_allocation_read", "legal_allocation_write", "legal_attempt_read", "legal_return_read", "legal_return_write", "legal_invoice_read", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_services_execute", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"},
        "tenant_legal_secretary": {"legal_instruction_read", "legal_allocation_read", "legal_attempt_read", "legal_return_read", "legal_return_write", "legal_invoice_read", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_services_execute", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"},
        "tenant_legal_finance": {"legal_billing_read", "legal_invoice_read", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_services_execute", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"},
        "tenant_sheriff": {"legal_directory_write", "legal_receipt_write", "legal_allocation_read", "legal_allocation_write", "legal_attempt_read", "legal_attempt_write", "legal_attempt_outcome_write", "legal_return_read", "legal_return_write", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_services_execute", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"},
        "tenant_deputy": {"legal_attempt_read", "legal_attempt_write", "legal_attempt_outcome_write", "legal_return_read", "legal_return_write", "wilsy_ai_legal_tool_read", "wilsy_ai_legal_services_execute", "wilsy_ai_legal_advisory_generate", "wilsy_ai_legal_advisory_read"},
        "tenant_legal_client": {"legal_invoice_read"},
    }
    assert set(expected) <= TENANT_ROLES
    for role, allowed in expected.items():
        assert {operation for operation in OPERATIONS if tenant_role_operation_eligibility(role, operation) == ELIGIBLE} == allowed
        assert tenant_role_operation_eligibility(role, "financial_execution") == DENY
    assert tenant_role_operation_eligibility("tenant_legal_client", "legal_instruction_read") == DENY
    assert tenant_role_operation_eligibility("tenant_deputy", "legal_instruction_read") == DENY


def test_directory_provisioning_eligibility_is_sheriff_only() -> None:
    """Directory provisioning eligibility is exact, own-tenant policy only."""
    operation = "legal_directory_write"
    assert operation in OPERATIONS
    assert tenant_role_operation_eligibility("tenant_sheriff", operation) == ELIGIBLE
    assert {
        role
        for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, operation) == ELIGIBLE
    } == {"tenant_sheriff"}
    assert tenant_role_operation_eligibility("tenant_deputy", operation) == DENY
    assert tenant_role_operation_eligibility("tenant_legal_partner", operation) == DENY
    assert tenant_role_operation_eligibility("tenant_owner", operation) == DENY
    assert tenant_role_operation_eligibility("tenant_admin", operation) == DENY
    assert tenant_role_operation_eligibility("tenant_legal_client", operation) == DENY
    assert requires_system_authority(
        operation
    ) is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    assert permission_for_business_role_operation(operation) is None

def test_acceptance_receipt_eligibility_is_sheriff_only() -> None:
    """Office receipt is sheriff-only and distinct from allocation/service."""
    operation = "legal_receipt_write"
    assert operation in OPERATIONS
    assert {
        role
        for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, operation) == ELIGIBLE
    } == {"tenant_sheriff"}
    for role in (
        "tenant_deputy",
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
        "tenant_legal_finance",
        "tenant_legal_client",
        "tenant_owner",
        "tenant_admin",
    ):
        assert tenant_role_operation_eligibility(role, operation) == DENY
    assert requires_system_authority(
        operation
    ) is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    assert permission_for_business_role_operation(operation) is None


def test_platform_billing_release_is_tenant_owner_only() -> None:
    assert "platform_billing_release" in OPERATIONS
    assert tenant_role_operation_eligibility("tenant_owner", "platform_billing_release") == ELIGIBLE
    assert all(tenant_role_operation_eligibility(role, "platform_billing_release") == DENY for role in TENANT_ROLES if role != "tenant_owner")

def test_inbound_collection_eligibility_is_explicit_and_least_privilege() -> None:
    """Only the dedicated tenant business role is eligible for the operation."""
    assert "inbound_collection_authorization_create" in OPERATIONS
    assert tenant_role_operation_eligibility(
        "tenant_inbound_collection_authorization_admin",
        "inbound_collection_authorization_create",
    ) == ELIGIBLE
    assert all(
        tenant_role_operation_eligibility(role, "inbound_collection_authorization_create") == DENY
        for role in TENANT_ROLES
        if role != "tenant_inbound_collection_authorization_admin"
    )

def test_inbound_provider_vocabulary_is_explicit_and_separated() -> None:
    expected = {
        "tenant_inbound_merchant_configuration_admin": {
            "tenant_inbound_merchant_configuration_register",
            "tenant_inbound_merchant_configuration_lifecycle_transition",
        },
        "tenant_inbound_provider_security_admin": {
            "tenant_inbound_merchant_configuration_compromise",
            "tenant_inbound_merchant_configuration_remediate",
            "tenant_inbound_provider_policy_emergency_disable",
            "tenant_inbound_provider_credential_security_eligibility_issue",
            "tenant_inbound_provider_credential_security_revoke",
            "tenant_inbound_provider_credential_security_compromise",
            "tenant_inbound_provider_credential_security_rotate",
        },
        "tenant_inbound_provider_policy_admin": {
            "tenant_inbound_provider_policy_create",
            "tenant_inbound_provider_policy_revise",
        },
        "tenant_inbound_provider_policy_activation_admin": {
            "tenant_inbound_provider_policy_activate",
            "tenant_inbound_provider_policy_deactivate",
        },
    }
    for role, allowed in expected.items():
        assert role in TENANT_ROLES
        assert {operation for operation in OPERATIONS if tenant_role_operation_eligibility(role, operation) == ELIGIBLE} == allowed
    assert tenant_role_operation_eligibility("tenant_owner", "tenant_inbound_provider_policy_activate") == DENY
    assert tenant_role_operation_eligibility("tenant_admin", "tenant_inbound_provider_policy_create") == DENY
    assert tenant_role_operation_eligibility("tenant_inbound_provider_policy_admin", "tenant_inbound_provider_policy_activate") == DENY
    assert tenant_role_operation_eligibility("tenant_inbound_provider_security_admin", "tenant_inbound_provider_policy_activate") == DENY


def test_credential_security_operation_vocabulary_is_four_way_and_least_authority() -> None:
    operations = {
        "tenant_inbound_provider_credential_security_eligibility_issue",
        "tenant_inbound_provider_credential_security_revoke",
        "tenant_inbound_provider_credential_security_compromise",
        "tenant_inbound_provider_credential_security_rotate",
    }
    assert operations <= OPERATIONS
    assert len(operations) == 4
    assert len({*operations}) == 4
    assert all(
        tenant_role_operation_eligibility("tenant_inbound_provider_security_admin", operation) == ELIGIBLE
        for operation in operations
    )
    for role in TENANT_ROLES - {"tenant_inbound_provider_security_admin"}:
        assert all(tenant_role_operation_eligibility(role, operation) == DENY for operation in operations)
    assert tenant_role_operation_eligibility("tenant_inbound_provider_security_admin", "unknown_operation") == DENY
    assert all(tenant_role_operation_eligibility("tenant_inbound_provider_security_admin", operation) == DENY for operation in {
        "tenant_inbound_merchant_configuration_lifecycle_transition",
        "tenant_inbound_provider_policy_activate",
        "financial_execution",
        "cross_tenant",
    })


def test_wilsy_ai_capacity_read_eligibility_is_general_roles_only() -> None:
    operation = "wilsy_ai_usage_capacity_read"
    general_roles = {"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor"}
    assert operation in OPERATIONS
    assert {role for role in TENANT_ROLES if tenant_role_operation_eligibility(role, operation) == ELIGIBLE} == general_roles
    assert all(tenant_role_operation_eligibility(role, operation) == DENY for role in TENANT_ROLES - general_roles)
    assert requires_system_authority(operation) is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    assert permission_for_business_role_operation(operation) is None
    for role in ("unknown", "TENANT_OWNER", " tenant_owner", "tenant_owner ", None, 123):
        assert tenant_role_operation_eligibility(role, operation) == DENY
    for malformed in ("wilsy_ai_usage_capacity", "wilsy_ai_usage_capacity_read ", " wilsy_ai_usage_capacity_read", "WILSY_AI_USAGE_CAPACITY_READ", "wilsy_ai:*", None, 123):
        assert all(tenant_role_operation_eligibility(role, malformed) == DENY for role in TENANT_ROLES)
    assert requires_system_authority("wilsy_ai_usage_capacity") is SystemAuthorityClassification.UNKNOWN


def test_billing_intelligence_evidence_read_eligibility_is_general_roles_only() -> None:
    operation = "billing_intelligence_evidence_read"
    general_roles = {"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor"}
    assert operation in OPERATIONS
    assert {role for role in TENANT_ROLES if tenant_role_operation_eligibility(role, operation) == ELIGIBLE} == general_roles
    assert all(tenant_role_operation_eligibility(role, operation) == DENY for role in TENANT_ROLES - general_roles)
    assert requires_system_authority(operation) is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    assert permission_for_business_role_operation(operation) is None
    for role in ("unknown", "TENANT_OWNER", " tenant_owner", "tenant_owner ", None, 123):
        assert tenant_role_operation_eligibility(role, operation) == DENY
    for malformed in (
        "billing_intelligence_evidence",
        "billing_intelligence_evidence_read ",
        " billing_intelligence_evidence_read",
        "BILLING_INTELLIGENCE_EVIDENCE_READ",
        "billing_intelligence:*",
        "billing_intelligence_evidence_*",
        None,
        123,
    ):
        assert all(tenant_role_operation_eligibility(role, malformed) == DENY for role in TENANT_ROLES)
    assert requires_system_authority("billing_intelligence_evidence") is SystemAuthorityClassification.UNKNOWN


def test_wilsy_ai_legal_tool_gateway_eligibility_is_bounded_and_nonfinancial() -> None:
    """Gateway eligibility is limited to legal personas and cannot cross-grant."""

    operation = "wilsy_ai_legal_tool_read"
    eligible_roles = {
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
        "tenant_legal_finance",
        "tenant_sheriff",
        "tenant_deputy",
    }
    assert operation in OPERATIONS
    assert {
        role
        for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, operation) == ELIGIBLE
    } == eligible_roles
    assert tenant_role_operation_eligibility("tenant_legal_client", operation) == DENY
    assert all(
        tenant_role_operation_eligibility(role, operation) == DENY
        for role in {
            "tenant_owner",
            "tenant_admin",
            "tenant_manager",
            "tenant_auditor",
            "tenant_inbound_collection_authorization_admin",
            "tenant_inbound_merchant_configuration_admin",
            "tenant_inbound_provider_security_admin",
            "tenant_inbound_provider_policy_admin",
            "tenant_inbound_provider_policy_activation_admin",
        }
    )
    assert all(
        tenant_role_operation_eligibility(role, "financial_execution") == DENY
        for role in eligible_roles
    )
    assert tenant_role_operation_eligibility("tenant_legal_finance", "legal_instruction_read") == DENY
    assert tenant_role_operation_eligibility("tenant_legal_finance", "legal_attempt_read") == DENY
    assert tenant_role_operation_eligibility("tenant_legal_finance", "legal_return_read") == DENY
    for role in ("tenant_sheriff", "tenant_deputy"):
        assert tenant_role_operation_eligibility(role, "legal_billing_read") == DENY
        assert tenant_role_operation_eligibility(role, "legal_invoice_read") == DENY
    for malformed in ("wilsy_ai_legal_tool", "wilsy_ai_legal_tool_read ", " wilsy_ai_legal_tool_read", "WILSY_AI_LEGAL_TOOL_READ", "wilsy_ai:*"):
        assert all(
            tenant_role_operation_eligibility(role, malformed) == DENY
            for role in TENANT_ROLES
        )
    assert requires_system_authority(operation) is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    assert permission_for_business_role_operation(operation) is None

def test_profile_policy_is_bounded_and_disjoint() -> None:
    assert allowed_profile_mutation_fields("tenant_owner") == PROFILE_MUTABLE_FIELDS_V1
    assert allowed_profile_mutation_fields("tenant_admin") == PROFILE_MUTABLE_FIELDS_V1
    assert not (PROFILE_MUTABLE_FIELDS_V1 & (LIFECYCLE_FIELDS | VERIFICATION_FIELDS | BILLING_METADATA_FIELDS | EVIDENCE_FIELDS | SECURITY_SENSITIVE_FIELDS | SYSTEM_MANAGED_FIELDS))
    assert not {"tax_id", "contact_email", "plan", "status", "verified", "checksum", "proof_hash"} & PROFILE_MUTABLE_FIELDS_V1
    assert PROFILE_MUTABLE_FIELDS_V1 == {"name", "alias", "industry", "region", "sector", "legal_name"}
    assert PROFILE_MUTABLE_FIELDS_V1.isdisjoint(LIFECYCLE_FIELDS | VERIFICATION_FIELDS | BILLING_METADATA_FIELDS | EVIDENCE_FIELDS | SECURITY_SENSITIVE_FIELDS | SYSTEM_MANAGED_FIELDS)
    assert allowed_profile_mutation_fields("tenant_manager") == frozenset()
    assert allowed_profile_mutation_fields("tenant_auditor") == frozenset()

def test_policy_is_not_authorization_or_persistence() -> None:
    assert tenant_role_operation_eligibility("tenant_owner", "profile_read") == ELIGIBLE
    assert "pymongo" not in __import__("tools.eos.auth.tenant_authority_policy", fromlist=["x"]).__dict__
    assert requires_system_authority("lifecycle_create") is SystemAuthorityClassification.SYSTEM_REQUIRED
    assert requires_system_authority("cross_tenant") is SystemAuthorityClassification.SYSTEM_REQUIRED
    assert requires_system_authority("platform_lifecycle") is SystemAuthorityClassification.SYSTEM_REQUIRED
    assert requires_system_authority("lifecycle_archive") is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    assert all(requires_system_authority(value) is SystemAuthorityClassification.UNKNOWN for value in ("unknown", "", None, 123, object(), "ADMIN", "GLOBAL_ROOT", "lifecycle_delete", "tenant:manage"))
    assert requires_system_authority("profile_read") is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    assert "tenant:profile:read" in FUTURE_PERMISSION_CANDIDATES
    assert "tenant:lifecycle:archive" in FUTURE_PERMISSION_CANDIDATES
    assert "payment" not in FUTURE_PERMISSION_CANDIDATES

def test_policy_facts_cannot_be_mutated() -> None:
    with pytest.raises(TypeError):
        ELIGIBILITY["tenant_owner"]["profile_read"] = DENY  # type: ignore[index]
    with pytest.raises(AttributeError):
        TENANT_ROLES.add("x")  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        OPERATIONS.add("x")  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        PROFILE_MUTABLE_FIELDS_V1.add("status")  # type: ignore[attr-defined]
    assert tenant_role_operation_eligibility("tenant_owner", "profile_read") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_owner", "role_grant") == DENY
    assert tenant_role_operation_eligibility("tenant_admin", "lifecycle_archive") == DENY

# ARTIFACT: test_tenant_authority_policy.py
# VERSION: v1.14.0-L8-3-LEGAL-OPERATIONS-RECEIPT-IAM-ELIGIBILITY-CERT
# AUTHORITY BOUNDARY: certification of policy facts only
# TENANT POSTURE: directory/receipt and other tenant eligibility remains policy-only; no membership or tenant authority is granted
# FAIL-CLOSED POSTURE: unknown values deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT