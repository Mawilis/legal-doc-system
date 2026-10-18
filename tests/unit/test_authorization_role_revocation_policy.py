"""Direct certificate for the P1-R3A pure authorization-role revocation policy.

TITLE: Authorization Role Revocation Policy Direct Certificate
VERSION: v1.0.0-P1-R3A-PURE-AUTHORIZATION-ROLE-REVOCATION-CERT
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Prove the exact two-edge allowlist and categorical denial boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_authorization_role_revocation_policy.py
COLLABORATION / OWNERSHIP: Certifies only authorization_role_revocation_policy.py.
CERTIFICATION / UPDATE DATE: 2026-10-13
CHANGELOG: v1.0.0-P1-R3A establishes direct pure-domain and dependency-boundary proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities; no credentials or PII.
TENANT BOUNDARY: Same-tenant allowlist and cross-tenant denial are explicit.
AUTHORITY BOUNDARY: Test-only verification; no authorization, persistence, mutation, or evidence authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from tools.eos.auth.authorization_role_revocation_policy import (
    AuthorizationRoleRevocationDecision,
    AuthorizationRoleRevocationDenialCode as Denial,
    evaluate_authorization_role_revocation,
)
from tools.eos.auth.role_assignment import RoleAssignmentStatus

VERSION = "v1.0.0-P1-R3A-PURE-AUTHORIZATION-ROLE-REVOCATION-CERT"
PRODUCTION = Path("tools/eos/auth/authorization_role_revocation_policy.py")


def evaluate(**changes: object) -> AuthorizationRoleRevocationDecision:
    """Evaluate canonical ACTIVE same-tenant input with explicit overrides."""
    values: dict[str, object] = {
        "operation": "role_revoke",
        "actor_principal_id": "principal-admin",
        "actor_tenant_id": "tenant-a",
        "actor_authorization_role": "ENTERPRISE_ADMIN",
        "target_principal_id": "principal-target",
        "target_tenant_id": "tenant-a",
        "target_authorization_role": "AUDITOR",
        "target_assignment_status": RoleAssignmentStatus.ACTIVE,
    }
    values.update(changes)
    return evaluate_authorization_role_revocation(**values)


@pytest.mark.parametrize(
    ("target_role", "expected_code"),
    [
        ("AUDITOR", None),
        ("SERVICE_WORKER", None),
        ("ENTERPRISE_ADMIN", Denial.ROOT_LIFECYCLE_REQUIRED),
        ("SOVEREIGN_ARCHITECT", Denial.SYSTEM_ROOT_NOT_TENANT_DELEGATION),
    ],
)
def test_enterprise_admin_exact_target_policy(target_role: str, expected_code: Denial | None) -> None:
    """Certify both allowed lower roles and both protected root targets."""
    decision = evaluate(target_authorization_role=target_role)
    assert decision.allowed is (expected_code is None)
    assert decision.denial_code is expected_code


@pytest.mark.parametrize(
    ("actor_role", "target_role"),
    [
        ("AUDITOR", "AUDITOR"),
        ("AUDITOR", "SERVICE_WORKER"),
        ("SERVICE_WORKER", "AUDITOR"),
        ("SERVICE_WORKER", "SERVICE_WORKER"),
        ("SOVEREIGN_ARCHITECT", "AUDITOR"),
        ("SOVEREIGN_ARCHITECT", "SERVICE_WORKER"),
    ],
)
def test_every_frozen_non_admin_edge_denies(actor_role: str, target_role: str) -> None:
    """Certify the six explicit non-admin graph denials without symmetry."""
    decision = evaluate(actor_authorization_role=actor_role, target_authorization_role=target_role)
    assert decision.allowed is False
    assert decision.denial_code is Denial.ACTOR_ROLE_NOT_AUTHORIZED


def test_unknown_actor_and_target_roles_deny() -> None:
    """Unknown roles cannot become wildcard or super-admin bypasses."""
    assert evaluate(actor_authorization_role="SUPER_ADMIN").denial_code is Denial.ACTOR_ROLE_NOT_AUTHORIZED
    assert evaluate(target_authorization_role="OTHER").denial_code is Denial.TARGET_ROLE_NOT_REVOCABLE


def test_unknown_operation_denies() -> None:
    """Only exact role_revoke is recognized."""
    assert evaluate(operation="role_grant").denial_code is Denial.UNKNOWN_OPERATION


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("actor_principal_id", ""),
        ("actor_principal_id", " actor "),
        ("actor_principal_id", 7),
        ("target_principal_id", ""),
        ("target_principal_id", " target "),
        ("target_principal_id", None),
        ("actor_tenant_id", ""),
        ("target_tenant_id", " tenant-a "),
    ],
)
def test_malformed_identity_and_tenant_facts_deny(field: str, value: object) -> None:
    """Malformed identity and tenant facts fail closed without coercion."""
    assert evaluate(**{field: value}).denial_code is Denial.MALFORMED_INPUT


def test_cross_tenant_denies() -> None:
    """No graph edge crosses an exact tenant boundary."""
    assert evaluate(target_tenant_id="tenant-b").denial_code is Denial.CROSS_TENANT


@pytest.mark.parametrize("status", [RoleAssignmentStatus.REVOKED, "ACTIVE", None])
def test_target_must_be_current_active_assignment(status: object) -> None:
    """Revoked targets deny and untyped status facts are malformed."""
    expected = Denial.TARGET_ASSIGNMENT_NOT_ACTIVE if status is RoleAssignmentStatus.REVOKED else Denial.MALFORMED_INPUT
    assert evaluate(target_assignment_status=status).denial_code is expected


@pytest.mark.parametrize("target_role", ["AUDITOR", "SERVICE_WORKER"])
def test_enterprise_admin_may_revoke_own_independent_lower_assignment(target_role: str) -> None:
    """Principal equality does not override an allowed independent lower edge."""
    decision = evaluate(target_principal_id="principal-admin", target_authorization_role=target_role)
    assert decision.allowed is True
    assert decision.denial_code is None


def test_self_root_and_non_admin_self_revocation_deny() -> None:
    """Root lifecycle and non-admin actor boundaries survive self targeting."""
    root = evaluate(target_principal_id="principal-admin", target_authorization_role="ENTERPRISE_ADMIN")
    assert root.denial_code is Denial.ROOT_LIFECYCLE_REQUIRED
    non_admin = evaluate(
        actor_principal_id="principal-auditor",
        target_principal_id="principal-auditor",
        actor_authorization_role="AUDITOR",
        target_authorization_role="AUDITOR",
    )
    assert non_admin.denial_code is Denial.ACTOR_ROLE_NOT_AUTHORIZED


def test_identical_input_is_deterministic_and_decision_is_immutable() -> None:
    """Identical facts yield equal immutable values."""
    first = evaluate()
    second = evaluate()
    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.allowed = False  # type: ignore[misc]


def test_complete_role_cross_product_has_only_two_allowed_edges() -> None:
    """ALL_NON_ALLOWLIST_EDGES_DENIED=YES across the frozen role vocabulary."""
    roles = ("ENTERPRISE_ADMIN", "SOVEREIGN_ARCHITECT", "AUDITOR", "SERVICE_WORKER")
    allowed = {
        (actor, target)
        for actor in roles
        for target in roles
        if evaluate(actor_authorization_role=actor, target_authorization_role=target).allowed
    }
    assert allowed == {
        ("ENTERPRISE_ADMIN", "AUDITOR"),
        ("ENTERPRISE_ADMIN", "SERVICE_WORKER"),
    }


def test_production_module_is_pure_iam_and_non_financial() -> None:
    """Certify no persistence, session, Mongo, HTTP, Legal, finance, or bypass dependency."""
    source = PRODUCTION.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert imports == {
        "__future__",
        "dataclasses",
        "enum",
        "typing",
        "tools.eos.auth.role_assignment",
    }
    forbidden_calls = {"insert_one", "update_one", "delete_one", "compare_and_swap", "start_session", "start_transaction"}
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, (ast.Attribute, ast.Name))
    }
    assert called.isdisjoint(forbidden_calls)
    lowered = source.lower()
    assert "tools.eos.legal_operations" not in lowered
    assert "super_admin" not in lowered
    assert "wildcard" not in lowered
    assert "financial execution authority: none" in lowered


# ARTIFACT: test_authorization_role_revocation_policy.py
# VERSION: v1.0.0-P1-R3A-PURE-AUTHORIZATION-ROLE-REVOCATION-CERT
# AUTHORITY BOUNDARY: direct pure-policy verification only; no production authority
# TENANT POSTURE: exact same-tenant allowlist and cross-tenant denial certified
# FAIL-CLOSED POSTURE: all non-allowlisted edges, malformed facts, inactive targets, and root targets deny
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
