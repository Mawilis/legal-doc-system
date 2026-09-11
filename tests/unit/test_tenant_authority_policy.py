"""TITLE: Tenant Authority Policy Certification.
VERSION: v1.5.0-M11-R8-R3B-P8-P3D-P4A-CERT
AUTHORITY: Pure policy-canon certification only.
EPITOME: Proves immutable tenant eligibility and non-authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authority_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-09.
CHANGELOG: v1.5.0-M11-R8-R3B-P8-P3D-P4A-CERT certifies four distinct
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
TENANT BOUNDARY: Policy facts do not prove membership or scope.
AUTHORITY BOUNDARY: Tests do not authorize or mutate.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from tools.eos.auth.tenant_authority_policy import *
import pytest

def test_runtime_version_source_is_canonical() -> None:
    assert VERSION == "v1.8.0-M11-R8-R3B-P8-P3D-P4A"

LEGACY = ("AUDITOR", "SOVEREIGN_ARCHITECT", "ENTERPRISE_ADMIN", "FOUNDER", "SUPER_ADMIN", "ADMIN", "admin", "GLOBAL_ROOT", "WILSY_ROOT", "MASTER", "unknown")

def test_matrix_boundaries() -> None:
    assert TENANT_ROLES == {"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor", "tenant_platform_billing_provider_policy_admin", "tenant_inbound_collection_authorization_admin", "tenant_inbound_merchant_configuration_admin", "tenant_inbound_provider_security_admin", "tenant_inbound_provider_policy_admin", "tenant_inbound_provider_policy_activation_admin"}
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
# VERSION: v1.5.0-M11-R8-R3B-P8-P3D-P4A-CERT
# AUTHORITY BOUNDARY: certification of policy facts only
# TENANT POSTURE: no membership or tenant authority is granted
# FAIL-CLOSED POSTURE: unknown values deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
