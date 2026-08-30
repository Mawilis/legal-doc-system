"""TITLE: Tenant Authority Policy Certification.
VERSION: v1.0.2-TENANT-AUTHORITY-POLICY-CERT
AUTHORITY: Pure policy-canon certification only.
EPITOME: Proves immutable tenant eligibility and non-authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authority_policy.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.2 certifies explicit fail-closed unknown SYSTEM-authority classification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: No network, persistence, or sensitive data.
TENANT BOUNDARY: Policy facts do not prove membership or scope.
AUTHORITY BOUNDARY: Tests do not authorize or mutate.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""
from tools.eos.auth.tenant_authority_policy import *
import pytest

LEGACY = ("AUDITOR", "SOVEREIGN_ARCHITECT", "ENTERPRISE_ADMIN", "FOUNDER", "SUPER_ADMIN", "ADMIN", "admin", "GLOBAL_ROOT", "WILSY_ROOT", "MASTER", "unknown")

def test_matrix_boundaries() -> None:
    assert TENANT_ROLES == {"tenant_owner", "tenant_admin", "tenant_manager", "tenant_auditor"}
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
# VERSION: v1.0.2-TENANT-AUTHORITY-POLICY-CERT
# AUTHORITY BOUNDARY: certification of policy facts only
# TENANT POSTURE: no membership or tenant authority is granted
# FAIL-CLOSED POSTURE: unknown values deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
