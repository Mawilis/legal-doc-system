"""TITLE: WILSY OS Legal Work Assignment Static Grant Contract.
VERSION: v1.0.0-P47-R94-WORK-ASSIGNMENT-STATIC-GRANTS-CERT
AUTHORITY: Deterministic verification of static authorization-role policy.
EPITOME: Proves that assignment mutation is granted only to the two approved
legal authorization roles and remains distinct from work-item mutation and
completion.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_assignment_static_role_grants.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-21.
CHANGELOG: 2026-10-21 v1.0.0 creates the closed R94 static-grant certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure policy test; no credentials, PII, or IO.
TENANT BOUNDARY: Static grants never prove tenant membership or possession.
AUTHORITY BOUNDARY: No assignment, reassignment, HTTP, or persistence mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from tools.eos.auth.roles import (
    ROLE_PERMISSIONS_MAP,
    get_permissions_for_roles,
    get_roles_granting_permission,
)

PERMISSION = "legal_operations:work_assignment:write"
EXPECTED_ROLES = ("LEGAL_ATTORNEY", "LEGAL_PARTNER")


def test_assignment_write_grant_is_exact_and_unique() -> None:
    """Only Partner and Attorney definitions contain one exact grant."""
    assert get_roles_granting_permission(PERMISSION) == EXPECTED_ROLES
    for role, grants in ROLE_PERMISSIONS_MAP.items():
        assert grants.count(PERMISSION) == (1 if role in EXPECTED_ROLES else 0)


def test_assignment_grant_is_distinct_from_work_item_write_and_completion() -> None:
    """Neighboring work-item permissions cannot substitute for assignment."""
    for neighboring in (
        "legal_operations:work_item:write",
        "legal_operations:work_item:complete",
    ):
        assert neighboring != PERMISSION
        assert get_roles_granting_permission(neighboring) != ()
    for role in ("LEGAL_PARALEGAL", "LEGAL_SECRETARY"):
        assert "legal_operations:work_item:complete" in ROLE_PERMISSIONS_MAP[role]
        assert PERMISSION not in ROLE_PERMISSIONS_MAP[role]


def test_expansion_and_malformed_aliases_fail_closed() -> None:
    """Exact expansion succeeds while aliases and wildcards grant nothing."""
    assert PERMISSION in get_permissions_for_roles(["LEGAL_PARTNER"])
    assert PERMISSION in get_permissions_for_roles(["LEGAL_ATTORNEY"])
    for malformed in (
        "legal_operations:work_assignment",
        "legal_operations:work_assignment:*",
        "legal_operations:work_assignment:read",
        " legal_operations:work_assignment:write",
        "legal_operations:work_assignment:write ",
        "LEGAL_OPERATIONS:WORK_ASSIGNMENT:WRITE",
    ):
        assert get_roles_granting_permission(malformed) == ()


# ARTIFACT: test_legal_work_assignment_static_role_grants.py
# VERSION: v1.0.0-P47-R94-WORK-ASSIGNMENT-STATIC-GRANTS-CERT
# AUTHORITY BOUNDARY: static authorization-role policy verification only
# TENANT POSTURE: current membership, eligibility, and possession remain separate
# FAIL-CLOSED POSTURE: all unlisted roles and malformed permissions deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
