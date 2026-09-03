"""TITLE: WILSY OS Role Definition Policy Unit Contract.
VERSION: v1.2.0-PLAN-PERMISSION-GRANTS-UNIT-CONTRACT
AUTHORITY: Deterministic unit verification of canonical Python role-definition policy only.
EPITOME: Proves the exact closed role vocabulary, tenant/subscription/plan
permission grants, deterministic expansion, reverse lookup, and fail-closed
non-bypass behavior.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_roles.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-03.
CHANGELOG:
    2026-09-03 v1.2.0-PLAN-PERMISSION-GRANTS-UNIT-CONTRACT certifies
    plan:read for ENTERPRISE_ADMIN/AUDITOR and plan:manage only for
    ENTERPRISE_ADMIN while retaining subscription grants and preserving
    SOVEREIGN_ARCHITECT/SERVICE_WORKER non-bypass locks.
    2026-08-30 v1.1.0-WILSY-TENANT-PERMISSION-GRANTS-UNIT-CONTRACT
    certified the bounded ENTERPRISE_ADMIN/AUDITOR tenant-permission migration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Pure policy tests with no credentials, principal
data, tenant records, persistence, secrets, or external IO.
TENANT BOUNDARY: Role definitions remain tenant-agnostic policy; current
tenant-scoped possession still requires governed RoleAssignmentAuthority.
AUTHORITY BOUNDARY: Unit verification of role identifiers and explicit
permission definitions only; no assignment, authentication, authorization,
lifecycle, or transport authority.
FINANCIAL AUTHORITY BOUNDARY: No tenant/subscription/plan grant is financial;
Kennel EOS remains exclusive.
"""

from __future__ import annotations

from typing import Any, cast

import pytest

from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_permissions_for_roles,
    get_roles_granting_permission,
)

VERSION = "v1.2.0-PLAN-PERMISSION-GRANTS-UNIT-CONTRACT"

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

TENANT_PERMISSIONS = {
    "audit:read",
    "tenant:profile:read",
    "tenant:profile:write",
    "tenant:lifecycle:archive",
    "tenant:membership:read",
    "tenant:membership:write",
    "tenant:role_assignment:read",
    "tenant:role_assignment:write",
    "subscription:read",
    "subscription:manage",
    "plan:read",
    "plan:manage",
}


def test_exact_role_vocabulary_and_grant_matrix() -> None:
    """The closed role map grants only the explicitly approved capabilities."""
    assert ROLE_PERMISSIONS_MAP == {
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
            "subscription:read",
            "subscription:manage",
            "plan:read",
            "plan:manage",
        ],
        "AUDITOR": [
            "kernel:read",
            "artifacts:read",
            "governance:read",
            "audit:read",
            "tenant:profile:read",
            "tenant:membership:read",
            "tenant:role_assignment:read",
            "subscription:read",
            "plan:read",
        ],
        "SERVICE_WORKER": [
            "artifacts:write",
            "events:publish",
        ],
    }



def test_permission_expansion_is_explicit_deterministic_and_fail_closed() -> None:
    """Role expansion remains exact, deterministic and non-authoritative."""
    assert get_permissions_for_roles(
        ["ENTERPRISE_ADMIN"]
    ) == sorted(
        ROLE_PERMISSIONS_MAP[
            "ENTERPRISE_ADMIN"
        ]
    )

    assert get_permissions_for_roles(
        ["AUDITOR"]
    ) == sorted(
        ROLE_PERMISSIONS_MAP[
            "AUDITOR"
        ]
    )

    assert get_permissions_for_roles(
        [
            "ENTERPRISE_ADMIN",
            "AUDITOR",
            "ENTERPRISE_ADMIN",
        ]
    ) == sorted(
        set(
            ROLE_PERMISSIONS_MAP[
                "ENTERPRISE_ADMIN"
            ]
        )
        | set(
            ROLE_PERMISSIONS_MAP[
                "AUDITOR"
            ]
        )
    )

    assert get_permissions_for_roles(
        ["UNKNOWN_ROLE"]
    ) == []

    assert get_permissions_for_roles(
        "ENTERPRISE_ADMIN"
    ) == []



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
        ("subscription:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("subscription:manage", ("ENTERPRISE_ADMIN",)),
        ("plan:read", ("AUDITOR", "ENTERPRISE_ADMIN")),
        ("plan:manage", ("ENTERPRISE_ADMIN",)),
    ),
)
def test_tenant_permission_reverse_lookup_is_exact(
    permission_id: str,
    expected_roles: tuple[str, ...],
) -> None:
    """Every tenant commercial permission resolves to its exact approved grants."""
    assert (
        get_roles_granting_permission(
            permission_id
        )
        == expected_roles
    )



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
        "subscription:*",
        "subscription",
        "plan:*",
        "plan:all",
        "plan",
        "PLAN:READ",
        " plan:read",
        "plan:read ",
    ),
)
def test_forbidden_unknown_partial_and_wildcard_like_permissions_never_grant(
    permission_id: str,
) -> None:
    """Malformed, wildcard-like and unknown values never manufacture grants."""
    assert (
        get_roles_granting_permission(
            permission_id
        )
        == ()
    )



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
# VERSION: v1.2.0-PLAN-PERMISSION-GRANTS-UNIT-CONTRACT
# AUTHORITY BOUNDARY: deterministic unit verification of explicit role-definition policy only
# TENANT POSTURE: tenant/subscription/plan grants remain policy; current tenant-scoped possession requires governed RoleAssignmentAuthority
# FAIL-CLOSED POSTURE: unknown, malformed, implicit, wildcard, legacy, and ambiguous inputs never manufacture grants
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
