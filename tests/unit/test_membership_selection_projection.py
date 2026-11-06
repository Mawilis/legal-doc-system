"""Unit tests for the read-only global-principal membership selection projection."""
from types import SimpleNamespace

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.membership_selection_projection import (
    MembershipSelectionProjectionError,
    build_membership_selection_page,
)


class PrincipalRepository:
    def __init__(self, status=PrincipalStatus.ACTIVE):
        self.status = status
        self.session = None

    def get(self, principal_id, *, session=None):
        self.session = session
        return SimpleNamespace(principal_id=principal_id, status=self.status)


class MembershipRepository:
    def __init__(self, rows, next_cursor=None):
        self.rows = rows
        self.next_cursor = next_cursor
        self.session = None
        self.calls = []

    def list_for_principal(self, principal_id, *, after_tenant_id=None, limit=50, session=None):
        self.calls.append((principal_id, after_tenant_id, limit))
        self.session = session
        return self.rows, self.next_cursor


class BusinessRoleRepository:
    def __init__(self, rows_by_tenant):
        self.rows_by_tenant = rows_by_tenant
        self.calls = []

    def resolve_all(self, principal_id, tenant_id, *, session=None):
        self.calls.append((principal_id, tenant_id))
        return self.rows_by_tenant.get(tenant_id, ())


def membership(tenant_id, status=TenantMembershipStatus.ACTIVE, revision=3):
    return TenantMembershipAuthority("principal-1", tenant_id, status, revision)


def capacity(tenant_id, role, revision=7, status=TenantBusinessRoleStatus.ACTIVE):
    return SimpleNamespace(
        principal_id="principal-1",
        tenant_id=tenant_id,
        business_role=role,
        status=status,
        revision=revision,
    )


def build(rows, roles, *, principal_status=PrincipalStatus.ACTIVE, next_cursor=None, session=None, tenant_resolver=None):
    return build_membership_selection_page(
        principal_id="principal-1",
        limit=25,
        principal_repository=PrincipalRepository(principal_status),
        membership_repository=MembershipRepository(rows, next_cursor),
        business_role_repository=BusinessRoleRepository(roles),
        tenant_resolver=tenant_resolver or (lambda tenant_id, session=None: SimpleNamespace(tenant_id=tenant_id)),
        session=session,
    )


def test_projects_only_active_memberships_and_active_business_capacities():
    page = build(
        [
            membership("tenant-a"),
            membership("tenant-b", TenantMembershipStatus.SUSPENDED),
        ],
        {
            "tenant-a": (
                capacity("tenant-a", "tenant_owner"),
                capacity("tenant-a", "tenant_legal_partner"),
                capacity("tenant-a", "tenant_legal_attorney", status=TenantBusinessRoleStatus.REVOKED),
            ),
        },
    )
    assert page.principal_id == "principal-1"
    assert len(page.memberships) == 1
    choice = page.memberships[0]
    assert choice.tenant_id == "tenant-a"
    assert choice.membership_revision == 3
    assert [(item.business_role, item.workspace_id) for item in choice.capacities] == [
        ("tenant_legal_partner", "LEGAL_PRACTICE"),
        ("tenant_owner", "EXECUTIVE_COMMAND_CENTRE"),
    ]


def test_active_membership_without_capacity_is_not_promoted():
    page = build([membership("tenant-a")], {})
    assert len(page.memberships) == 1
    assert page.memberships[0].capacities == ()


def test_inactive_global_principal_cannot_enumerate_memberships():
    with pytest.raises(MembershipSelectionProjectionError, match="PRINCIPAL_NOT_ACTIVE"):
        build([membership("tenant-a")], {}, principal_status=PrincipalStatus.SUSPENDED)


def test_tenant_mismatch_fails_closed():
    with pytest.raises(MembershipSelectionProjectionError, match="TENANT_MISMATCH"):
        build(
            [membership("tenant-a")],
            {"tenant-a": (capacity("tenant-a", "tenant_owner"),)},
            tenant_resolver=lambda tenant_id, session=None: SimpleNamespace(tenant_id="tenant-b"),
        )


def test_membership_page_cursor_is_preserved():
    page = build([membership("tenant-a")], {}, next_cursor="tenant-a")
    assert page.next_cursor == "tenant-a"
