"""TITLE: WILSY OS Permission Policy Unit Contract.
VERSION: v1.0.0-WILSY-PERMISSION-POLICY-UNIT-CONTRACT
AUTHORITY: Deterministic unit verification of exact Python permission-policy evaluation only.
EPITOME: Proves explicit permission grants, bypass removal, malformed/unknown fail-closed behavior, and deterministic policy evaluation without establishing current role possession or final authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_permissions.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG: v1.0.0-WILSY-PERMISSION-POLICY-UNIT-CONTRACT establishes deterministic unit-contract evidence for exact permission-policy semantics and legacy bypass removal.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure policy tests only; no credentials, principal data, tenant records, persistence, secrets, network, or external IO.
TENANT BOUNDARY: Tenant-agnostic permission policy only; current tenant-scoped role possession remains outside this artifact.
AUTHORITY BOUNDARY: Unit verification of exact permission-policy evaluation only; no role possession, principal lifecycle, membership, authentication, final authorization, or financial execution authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""
from typing import Any, cast
from tools.eos.auth.permissions import has_permission

VERSION = "v1.0.0-WILSY-PERMISSION-POLICY-UNIT-CONTRACT"

def test_explicit_permission_allow_and_deny():
    """Prove explicit grants allow and absent grants deny."""
    assert has_permission(["AUDITOR"], "audit:read") is True
    assert has_permission(["AUDITOR"], "tenant:manage") is False

def test_sovereign_architect_and_admin_all_are_literal():
    """Prove neither role nor admin:all creates implicit bypass authority."""
    assert has_permission(["SOVEREIGN_ARCHITECT"], "kernel:read") is True
    assert has_permission(["SOVEREIGN_ARCHITECT"], "tenant:delete") is False
    assert has_permission(["SOVEREIGN_ARCHITECT"], "admin:all") is False
    assert has_permission(["SOVEREIGN_ARCHITECT"], "admin:manage") is False

def test_unknown_and_malformed_inputs_fail_closed():
    """Prove unknown, malformed, empty, and whitespace inputs never grant."""
    for roles, permission in [
        (["UNKNOWN"], "kernel:read"),
        (["AUDITOR"], ""),
        (["AUDITOR"], "   "),
        (cast(Any, [None, " "]), "audit:read"),
        (cast(Any, None), "audit:read"),
        (["AUDITOR"], cast(Any, None)),
    ]:
        assert has_permission(roles, permission) is False

def test_multi_role_union_is_exact_and_deterministic():
    """Prove explicit multi-role union, exact matching, and repeatability."""
    roles = ["AUDITOR", "SERVICE_WORKER"]
    assert has_permission(roles, "events:publish") is True
    assert has_permission(roles, "audit:read") is True
    for partial in ("audit", "audit:read:extra", "*", "admin:"):
        assert has_permission(roles, partial) is False
    assert [has_permission(roles, "execution:trigger") for _ in range(5)] == [False] * 5

# ARTIFACT: test_permissions.py
# VERSION: v1.0.0-WILSY-PERMISSION-POLICY-UNIT-CONTRACT
# AUTHORITY BOUNDARY: deterministic unit verification of exact permission-policy evaluation only
# TENANT POSTURE: tenant-agnostic policy only; current role possession remains external
# FAIL-CLOSED POSTURE: unknown, malformed, implicit, wildcard, and non-explicit permissions never grant authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
