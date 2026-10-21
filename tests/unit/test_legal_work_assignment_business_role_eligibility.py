"""TITLE: P47-R93 Legal Work Assignment Business-Role Eligibility Certificate.
VERSION: v1.0.0-P47-R93-WORK-ASSIGNMENT-ELIGIBILITY
AUTHORITY: Canonical tenant business-role eligibility facts only.
EPITOME: Proves that Partner and Attorney are the only business-role candidates
for assignment-command admission while eligibility remains non-authorizing.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_work_assignment_business_role_eligibility.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-21
CHANGELOG: v1.0.0 establishes exact positive, negative, malformed-alias and
non-authority evidence for legal_work_assignment_write.
TENANT BOUNDARY: Own-tenant eligibility metadata only; no cross-tenant scope.
AUTHORITY BOUNDARY: Eligibility is not IAM authorization, matter access,
assignment, reassignment, supervision, completion or workflow authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from __future__ import annotations

import pytest

from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    OPERATIONS,
    TENANT_ROLES,
    permission_for_business_role_operation,
    requires_system_authority,
    tenant_role_operation_eligibility,
    SystemAuthorityClassification,
)


OPERATION = "legal_work_assignment_write"
ELIGIBLE_ROLES = frozenset({
    "tenant_legal_partner",
    "tenant_legal_attorney",
})


def test_assignment_operation_is_canonical_and_non_system() -> None:
    assert OPERATION in OPERATIONS
    assert (
        requires_system_authority(OPERATION)
        is SystemAuthorityClassification.SYSTEM_NOT_INHERENTLY_REQUIRED
    )


def test_assignment_eligibility_is_exactly_partner_and_attorney() -> None:
    assert {
        role
        for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, OPERATION) == ELIGIBLE
    } == ELIGIBLE_ROLES


@pytest.mark.parametrize("role", sorted(ELIGIBLE_ROLES))
def test_each_evidence_supported_legal_role_is_eligible(role: str) -> None:
    assert tenant_role_operation_eligibility(role, OPERATION) == ELIGIBLE


@pytest.mark.parametrize(
    "role",
    (
        "tenant_legal_client",
        "tenant_legal_finance",
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
        "tenant_sheriff",
        "tenant_deputy",
        "tenant_owner",
        "tenant_admin",
        "tenant_manager",
        "tenant_auditor",
    ),
)
def test_unrelated_and_non_assigning_roles_deny(role: str) -> None:
    assert tenant_role_operation_eligibility(role, OPERATION) == DENY


@pytest.mark.parametrize(
    "role",
    (
        "LEGAL_PARTNER",
        "LEGAL_ATTORNEY",
        "tenant_legal_partner ",
        " tenant_legal_attorney",
        "tenant-legal-partner",
        "*",
        "",
        None,
        7,
    ),
)
def test_malformed_and_authorization_role_aliases_deny(role: object) -> None:
    assert tenant_role_operation_eligibility(role, OPERATION) == DENY


@pytest.mark.parametrize(
    "operation",
    (
        "legal_work_assignment_write ",
        " legal_work_assignment_write",
        "LEGAL_WORK_ASSIGNMENT_WRITE",
        "legal_work_assignment:*",
        "legal_work_reassignment_write",
        "",
        None,
    ),
)
def test_alias_wildcard_and_cross_operation_values_fail_closed(
    operation: object,
) -> None:
    for role in ELIGIBLE_ROLES:
        assert tenant_role_operation_eligibility(role, operation) == DENY


def test_assignment_operation_is_distinct_from_work_item_and_completion() -> None:
    assert OPERATION not in {
        "legal_work_item_write",
        "legal_work_item_complete",
    }


def test_r93_does_not_bind_permission_or_grant_execution_authority() -> None:
    import tools.eos.auth.tenant_authority_policy as policy

    assert permission_for_business_role_operation(OPERATION) is None
    for forbidden in (
        "assign_work",
        "reassign_work",
        "authorize_assignment",
        "complete_work",
    ):
        assert not hasattr(policy, forbidden)


# ARTIFACT: test_legal_work_assignment_business_role_eligibility.py
# VERSION: v1.0.0-P47-R93-WORK-ASSIGNMENT-ELIGIBILITY
# AUTHORITY BOUNDARY: non-authorizing business-role eligibility evidence only
# TENANT POSTURE: own-tenant metadata; no cross-tenant authority
# FAIL-CLOSED POSTURE: every unlisted or malformed role and operation denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
