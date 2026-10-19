"""TITLE: WILSY OS P9 Live Reassignment Authorization Conjunction Certificate.
VERSION: v1.0.0-P9-R47R2-REASSIGNMENT-LIVE-AUTHORIZATION-CERT
AUTHORITY: Read-only Python EOS current-truth authorization tests.
EPITOME: Proves reassignment authorization requires exact current principal,
    tenant membership, eligible business role, canonical permission-operation
    pairing and ACTIVE final granting-role possession.
ABSOLUTE CANONICAL PATH:
    tests/unit/test_legal_work_reassignment_live_authorization.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.0-P9-R47R2-REASSIGNMENT-LIVE-AUTHORIZATION-CERT
    exercises current-truth authorization using existing read-only
    test repositories with explicit mutation tripwires and canonical
    SUSPENDED status values. No command or persistence is introduced.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
"""

from __future__ import annotations

import pytest

import test_tenant_authorization as h
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason as Reason,
)
from tools.eos.auth.roles import get_roles_granting_permission

OPERATION = "legal_work_item_reassign"
PERMISSION = "legal_operations:work_item:reassign"


@pytest.mark.parametrize(
    ("business_role", "granting_role"),
    (
        ("tenant_legal_partner", "LEGAL_PARTNER"),
        ("tenant_legal_attorney", "LEGAL_ATTORNEY"),
        ("tenant_legal_partner", "LEGAL_ATTORNEY"),
        ("tenant_legal_attorney", "LEGAL_PARTNER"),
    ),
)
def test_active_own_tenant_full_conjunction_authorizes(
    business_role: str, granting_role: str,
) -> None:
    assert get_roles_granting_permission(PERMISSION) == (
        "LEGAL_ATTORNEY", "LEGAL_PARTNER"
    )
    decision = h._decision(
        permission_id=PERMISSION,
        operation=OPERATION,
        business_repository=h._business(business_role),
        assignment_repository=h._assignments(granting_role),
    )
    assert decision == TenantAuthorizationDecision(
        True, Reason.AUTHORIZED, business_role, granting_role
    )


@pytest.mark.parametrize(
    "business_role",
    (
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
        "tenant_legal_finance",
        "tenant_legal_client",
        "tenant_owner",
        "tenant_admin",
        "tenant_sheriff",
        "tenant_deputy",
    ),
)
def test_ineligible_business_role_denied_even_with_partner_grant(
    business_role: str,
) -> None:
    grants = h._assignments("LEGAL_PARTNER", "LEGAL_ATTORNEY")
    decision = h._decision(
        permission_id=PERMISSION,
        operation=OPERATION,
        business_repository=h._business(business_role),
        assignment_repository=grants,
    )
    assert decision.authorized is False
    assert decision.reason is Reason.BUSINESS_ROLE_INELIGIBLE
    assert grants.calls == []


@pytest.mark.parametrize(
    ("granting_roles", "revoked_roles", "reason"),
    (
        ((), (), Reason.PERMISSION_NOT_GRANTED),
        ((), ("LEGAL_PARTNER",), Reason.ROLE_ASSIGNMENT_INACTIVE),
        (("LEGAL_PARALEGAL",), (), Reason.PERMISSION_NOT_GRANTED),
    ),
)
def test_missing_revoked_or_unrelated_grant_is_denied(
    granting_roles: tuple[str, ...],
    revoked_roles: tuple[str, ...],
    reason: Reason,
) -> None:
    decision = h._decision(
        permission_id=PERMISSION,
        operation=OPERATION,
        business_repository=h._business("tenant_legal_partner"),
        assignment_repository=h._assignments(
            *granting_roles, revoked_roles=revoked_roles
        ),
    )
    assert decision.authorized is False
    assert decision.reason is reason


@pytest.mark.parametrize(
    ("permission_id", "operation", "reason"),
    (
        (
            "legal_operations:work_item:complete",
            OPERATION,
            Reason.PERMISSION_OPERATION_MISMATCH,
        ),
        (
            "legal_operations:work_item:write",
            OPERATION,
            Reason.PERMISSION_OPERATION_MISMATCH,
        ),
        (
            PERMISSION,
            "legal_work_item_complete",
            Reason.PERMISSION_OPERATION_MISMATCH,
        ),
        (
            PERMISSION,
            "legal_work_item_reassign ",
            Reason.INVALID_INPUT,
        ),
        (
            PERMISSION,
            "LEGAL_WORK_ITEM_REASSIGN",
            Reason.INVALID_INPUT,
        ),
        (
            PERMISSION,
            "legal_work_item_*",
            Reason.INVALID_INPUT,
        ),
    ),
)
def test_mismatched_or_malformed_pair_denies_before_grant_lookup(
    permission_id: str, operation: str, reason: Reason,
) -> None:
    grants = h._assignments("LEGAL_PARTNER", "LEGAL_ATTORNEY")
    decision = h._decision(
        permission_id=permission_id,
        operation=operation,
        business_repository=h._business("tenant_legal_partner"),
        assignment_repository=grants,
    )
    assert decision.authorized is False
    assert decision.reason is reason
    assert grants.calls == []


def test_suspended_principal_denied_before_grant_lookup() -> None:
    grants = h._assignments("LEGAL_PARTNER")
    decision = h._decision(
        permission_id=PERMISSION,
        operation=OPERATION,
        business_repository=h._business("tenant_legal_partner"),
        assignment_repository=grants,
        principal_repository=h._principal(
            status=h.PrincipalStatus.SUSPENDED
        ),
    )
    assert decision.authorized is False
    assert decision.reason is Reason.PRINCIPAL_INACTIVE
    assert grants.calls == []


def test_suspended_membership_denied_before_grant_lookup() -> None:
    grants = h._assignments("LEGAL_PARTNER")
    decision = h._decision(
        permission_id=PERMISSION,
        operation=OPERATION,
        business_repository=h._business("tenant_legal_partner"),
        assignment_repository=grants,
        membership_repository=h._membership(
            status=h.TenantMembershipStatus.SUSPENDED
        ),
    )
    assert decision.authorized is False
    assert decision.reason is Reason.MEMBERSHIP_INACTIVE
    assert grants.calls == []


def test_cross_tenant_membership_cannot_grant() -> None:
    grants = h._assignments("LEGAL_PARTNER")
    decision = h._decision(
        permission_id=PERMISSION,
        operation=OPERATION,
        business_repository=h._business("tenant_legal_partner"),
        assignment_repository=grants,
        tenant_id="different_tenant",
    )
    assert decision.authorized is False
    assert decision.reason is Reason.MEMBERSHIP_NOT_FOUND
    assert grants.calls == []


def test_authorization_is_read_only_with_mutation_tripwires() -> None:
    principal = h._principal()
    membership = h._membership()
    business = h._business("tenant_legal_attorney")
    grants = h._assignments("LEGAL_ATTORNEY")
    decision = h._decision(
        permission_id=PERMISSION,
        operation=OPERATION,
        business_repository=business,
        assignment_repository=grants,
        principal_repository=principal,
        membership_repository=membership,
    )
    assert decision.authorized is True
    assert all(
        repository.write_calls == 0
        for repository in (principal, membership, business, grants)
    )


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_work_reassignment_live_authorization.py
# VERSION: v1.0.0-P9-R47R2-REASSIGNMENT-LIVE-AUTHORIZATION-CERT
# AUTHORITY BOUNDARY: current-truth own-tenant authorization only
# MATTER / RECIPIENT / SUPERVISOR AUTHORITY: NOT CERTIFIED
# REASSIGNMENT COMMAND / PERSISTENCE AUTHORITY: NOT CREATED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
