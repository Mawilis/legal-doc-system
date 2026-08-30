"""TITLE: WILSY OS Role Definition Policy Unit Contract.
VERSION: v1.1.0-WILSY-TENANT-PERMISSION-GRANTS-UNIT-CONTRACT
AUTHORITY: Deterministic unit verification of canonical Python role-definition policy only.
EPITOME: Proves the exact closed role vocabulary, migrated tenant permission grants, deterministic expansion, exact reverse lookup, and fail-closed non-bypass behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.1.0 certifies the bounded ENTERPRISE_ADMIN/AUDITOR tenant-permission grant migration while preserving SOVEREIGN_ARCHITECT and SERVICE_WORKER non-bypass locks.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure policy tests with no credentials, principal data, tenant records, persistence, secrets, or external IO.
TENANT BOUNDARY: Role definitions remain tenant-agnostic policy; current tenant-scoped possession still requires governed RoleAssignmentAuthority.
AUTHORITY BOUNDARY: Unit verification of role identifiers and explicit permission definitions only; no assignment, authentication, authorization, lifecycle, or transport authority.
FINANCIAL AUTHORITY BOUNDARY: No migrated grant is financial; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from typing import Any, cast

import pytest

from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_permissions_for_roles,
    get_roles_granting_permission,
)

VERSION = "v1.1.0-WILSY-TENANT-PERMISSION-GRANTS-UNIT-CONTRACT"

EXPECTED_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "SOVEREIGN_ARCHITECT": [
        "kernel:read",
        "kernel:write",
        "governance:evaluate",
        "artifacts:read",
    ],
    "ENTERPRISE_ADMIN": [
        "kernel:read",
        "governance:evaluate",
        "artifacts:read",
        "tenant:profile:read",
        "tenant:profile:write",
        "tenant:lifecycle:archive",
        "tenant:membership:read",
        "tenant:membership:write",
        "tenant:role_assignment:read",
        "tenant:role_assignment:write",
    ],
    "AUDITOR": [
        "kernel:read",
        "artifacts:read",
        "governance:read",
        "audit:read",
        "tenant:profile:read",
        "tenant:membership:read",
        "tenant:role_assignment:read",
    ],
    "SERVICE_WORKER": [
        "artifacts:write",
        "events:publish",
    ],
}

TENANT_PERMISSIONS = frozenset(
    {
        "tenant:profile:read",
        "tenant:profile:write",
        "tenant:lifecycle:archive",
        "tenant:membership:read",
        "tenant:membership:write",
        "tenant:role_assignment:read",
        "tenant:role_assignment:write",
    }
)


def test_exact_role_vocabulary_and_grant_matrix() -> None:
    """The closed four-role vocabulary and every explicit grant are exact."""

    assert ROLE_PERMISSIONS_MAP == EXPECTED_ROLE_PERMISSIONS
    for role, permissions in ROLE_PERMISSIONS_MAP.items():
        assert isinstance(role, str) and role
        assert permissions
        assert all(isinstance(permission, str) and permission == permission.strip() for permission in permissions)
        assert len(permissions) == len(set(permissions))


def test_permission_expansion_is_explicit_deterministic_and_fail_closed() -> None:
    """Expansion is an exact deterministic union; malformed/unknown roles add nothing."""

    expected = sorted(
        set(
            EXPECTED_ROLE_PERMISSIONS["AUDITOR"]
            + EXPECTED_ROLE_PERMISSIONS["SERVICE_WORKER"]
        )
    )
    assert get_permissions_for_roles(
        ["SERVICE_WORKER", "AUDITOR", "SERVICE_WORKER"]
    ) == expected
    assert get_permissions_for_roles(cast(Any, ["UNKNOWN", None, 42])) == []
    assert get_permissions_for_roles("SOVEREIGN_ARCHITECT") == []
    assert get_permissions_for_roles(
        ["SOVEREIGN_ARCHITECT", "ENTERPRISE_ADMIN"]
    ) == get_permissions_for_roles(["ENTERPRISE_ADMIN", "SOVEREIGN_ARCHITECT"])


@pytest.mark.parametrize(
    ("permission_id", "expected_roles"),
    (
        ("tenant:profile:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("tenant:profile:write", ("ENTERPRISE_ADMIN",)),
        ("tenant:lifecycle:archive", ("ENTERPRISE_ADMIN",)),
        ("tenant:membership:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("tenant:membership:write", ("ENTERPRISE_ADMIN",)),
        ("tenant:role_assignment:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("tenant:role_assignment:write", ("ENTERPRISE_ADMIN",)),
    ),
)
def test_tenant_permission_reverse_lookup_is_exact(
    permission_id: str,
    expected_roles: tuple[str, ...],
) -> None:
    """Every migrated tenant permission resolves to its exact approved grant set."""

    assert get_roles_granting_permission(permission_id) == expected_roles


@pytest.mark.parametrize(
    "permission_id",
    (
        "admin:all",
        "execution:trigger",
        "tenant:manage",
        "tenant:delete",
        "tenant:*",
        "tenant:all",
        "tenant",
        "admin",
        "unknown:permission",
        "",
        " ",
        "tenant:profile",
        "tenant:profile:read ",
        " tenant:profile:read",
    ),
)
def test_forbidden_unknown_partial_and_wildcard_like_permissions_never_grant(
    permission_id: str,
) -> None:
    """Legacy, ambiguous, malformed, partial, wildcard-like, and unknown values stay ungranted."""

    assert get_roles_granting_permission(permission_id) == ()


def test_sovereign_architect_and_service_worker_are_not_tenant_bypasses() -> None:
    """The grant migration does not turn system/service roles into tenant authority."""

    sovereign = set(get_permissions_for_roles(["SOVEREIGN_ARCHITECT"]))
    service = set(get_permissions_for_roles(["SERVICE_WORKER"]))
    assert sovereign.isdisjoint(TENANT_PERMISSIONS)
    assert service.isdisjoint(TENANT_PERMISSIONS)
    assert get_permissions_for_roles(["SERVICE_WORKER"]) == [
        "artifacts:write",
        "events:publish",
    ]


def test_no_role_has_implicit_wildcard_or_financial_grant() -> None:
    """All role grants remain explicit exact strings and non-financial."""

    for permissions in ROLE_PERMISSIONS_MAP.values():
        assert all("*" not in permission for permission in permissions)
        assert all("financial" not in permission for permission in permissions)
        assert "admin:all" not in permissions
        assert "execution:trigger" not in permissions
        assert "tenant:manage" not in permissions


# ARTIFACT: test_roles.py
# VERSION: v1.1.0-WILSY-TENANT-PERMISSION-GRANTS-UNIT-CONTRACT
# AUTHORITY BOUNDARY: deterministic unit verification of explicit role-definition policy only
# TENANT POSTURE: migrated tenant grants remain policy; current tenant-scoped possession requires governed RoleAssignmentAuthority
# FAIL-CLOSED POSTURE: unknown, malformed, implicit, wildcard, legacy, and ambiguous inputs never manufacture grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
