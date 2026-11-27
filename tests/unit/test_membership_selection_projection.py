"""TITLE: WILSY OS Membership Selection Tenant Workspace Regression Certificate.
VERSION: v1.1.0-FOUNDER-OWNER-MEMBERSHIP-CERT
AUTHORITY: Python EOS Global Principal selection read-only certification.
EPITOME: Verify Founder Owner, customer Owner and HR selection resolve the
    same exact tenant/workspace authority as the MFA challenge and bootstrap.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_membership_selection_projection.py
COLLABORATION / OWNERSHIP: Membership selection projection and workspace bootstrap.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.1.0-FOUNDER-OWNER-MEMBERSHIP-CERT establishes exact canonical
    Founder Owner workspace selection without granting roles or changing MFA.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic principal/tenant fixtures only.
TENANT BOUNDARY: Canonical Founder mapping is exact-tenant-only.
AUTHORITY BOUNDARY: Tests are read-only, no IAM role/session changes.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS owns all funds.
"""
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


def test_founder_owner_appears_as_exact_headquarters_capacity_alongside_hr():
    """Membership options must match canonical EOS MFA/bootstrap workspace resolution."""
    from tools.eos.auth.workspace_bootstrap_projection import resolve_workspace_id

    founder_tenant = "WILSYTENANT-4CD2FZ4O"
    page = build(
        [membership(founder_tenant)],
        {founder_tenant: (
            capacity(founder_tenant, "tenant_owner"),
            capacity(founder_tenant, "tenant_hr_director"),
            capacity(founder_tenant, "tenant_hr_manager"),
        )},
    )
    assert len(page.memberships) == 1
    choices = {item.business_role: item.workspace_id for item in page.memberships[0].capacities}
    assert choices == {
        "tenant_owner": "WILSY_HEADQUARTERS",
        "tenant_hr_director": "PEOPLE_OPERATIONS",
        "tenant_hr_manager": "PEOPLE_OPERATIONS",
    }
    for role, workspace in choices.items():
        assert resolve_workspace_id(role, tenant_id=founder_tenant) == workspace
    assert resolve_workspace_id("tenant_owner", tenant_id="customer-tenant") == "EXECUTIVE_COMMAND_CENTRE"


# ARTIFACT: tests/unit/test_membership_selection_projection.py
# VERSION: v1.1.0-FOUNDER-OWNER-MEMBERSHIP-CERT
# AUTHORITY BOUNDARY: Read-only synthetic EOS membership selection tests only.
# TENANT POSTURE: The Founder tenant cannot authorize a foreign tenant Owner.
# FAIL-CLOSED POSTURE: No selected-capacity fallback when evidence is absent.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns payments.
# END OF WILSY OS SOVEREIGN ARTIFACT
