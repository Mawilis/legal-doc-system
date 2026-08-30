"""TITLE: WILSY OS Role Definition Policy Unit Contract.
VERSION: v1.0.0-WILSY-ROLE-DEFINITION-POLICY-UNIT-CONTRACT
AUTHORITY: Deterministic unit verification of canonical Python role-definition policy only.
EPITOME: Proves exact role vocabulary, deterministic permission expansion, exact reverse permission lookup, and fail-closed unknown/malformed policy inputs without establishing current role possession or authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG: v1.0.0-WILSY-ROLE-DEFINITION-POLICY-UNIT-CONTRACT establishes deterministic unit-contract evidence for governed Python role-definition policy.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure policy tests with no credentials, principal data, tenant records, persistence, secrets, or external IO.
TENANT BOUNDARY: Role definitions are tenant-agnostic policy only; these tests never establish tenant-scoped possession.
AUTHORITY BOUNDARY: Unit verification of role identifiers and explicit permission definitions only; no assignment, authentication, authorization, or lifecycle authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from typing import Any, cast
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_permissions_for_roles, get_roles_granting_permission

VERSION = "v1.0.0-WILSY-ROLE-DEFINITION-POLICY-UNIT-CONTRACT"
EXPECTED_ROLES = {"SOVEREIGN_ARCHITECT", "ENTERPRISE_ADMIN", "AUDITOR", "SERVICE_WORKER"}

def test_exact_role_vocabulary_and_definition_quality():
    """Prove the closed role vocabulary and non-empty duplicate-free definitions."""
    assert set(ROLE_PERMISSIONS_MAP) == EXPECTED_ROLES
    for role, permissions in ROLE_PERMISSIONS_MAP.items():
        assert isinstance(role, str) and role
        assert permissions and all(isinstance(p, str) and p.strip() for p in permissions)
        assert len(permissions) == len(set(permissions))

def test_permission_expansion_is_explicit_deterministic_and_fail_closed():
    """Prove deterministic deduplication, unknown-role denial, and no malformed broadening."""
    expected = sorted(set(ROLE_PERMISSIONS_MAP["AUDITOR"] + ROLE_PERMISSIONS_MAP["SERVICE_WORKER"]))
    assert get_permissions_for_roles(["SERVICE_WORKER", "AUDITOR", "SERVICE_WORKER"]) == expected
    assert get_permissions_for_roles(cast(Any, ["UNKNOWN", None, 42])) == []
    assert get_permissions_for_roles("SOVEREIGN_ARCHITECT") == []
    assert get_permissions_for_roles(["SOVEREIGN_ARCHITECT"])[-1] == "kernel:write"

def test_reverse_lookup_is_exact_and_deterministic():
    """Prove exact reverse lookup rejects unknown and partial permission strings."""
    assert get_roles_granting_permission("admin:all") == ()
    assert get_roles_granting_permission("execution:trigger") == ()
    assert get_roles_granting_permission("admin") == ()
    assert get_roles_granting_permission("unknown:permission") == ()
    assert get_roles_granting_permission(cast(Any, None)) == ()

def test_admin_all_and_sovereign_architect_are_not_implicit_bypasses():
    """Prove admin:all and SOVEREIGN_ARCHITECT grant only explicit definitions."""
    grants = get_permissions_for_roles(["SOVEREIGN_ARCHITECT"])
    assert "admin:all" not in grants
    assert get_permissions_for_roles(["ENTERPRISE_ADMIN"]) == ["artifacts:read", "governance:evaluate", "kernel:read"]
    assert get_permissions_for_roles(["SERVICE_WORKER"]) == ["artifacts:write", "events:publish"]
    assert get_roles_granting_permission("tenant:manage") == ()
    assert get_permissions_for_roles(["AUDITOR"]) == ["artifacts:read", "audit:read", "governance:read", "kernel:read"]
    assert get_permissions_for_roles(["SOVEREIGN_ARCHITECT", "ENTERPRISE_ADMIN"]) == get_permissions_for_roles(["ENTERPRISE_ADMIN", "SOVEREIGN_ARCHITECT"])
    assert "tenant:delete" not in grants
    assert get_roles_granting_permission("tenant:delete") == ()

# ARTIFACT: test_roles.py
# VERSION: v1.0.0-WILSY-ROLE-DEFINITION-POLICY-UNIT-CONTRACT
# AUTHORITY BOUNDARY: deterministic unit verification of explicit role-definition policy only
# TENANT POSTURE: role definitions are tenant-agnostic; current possession is outside this artifact
# FAIL-CLOSED POSTURE: unknown and malformed role or permission inputs never manufacture grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
