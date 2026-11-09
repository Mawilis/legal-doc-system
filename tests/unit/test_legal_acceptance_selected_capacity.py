"""WILSY OS selected-capacity platform-use acceptance authority certificate.

TITLE: WILSY OS Selected-Capacity Legal Acceptance Forensic Certificate
VERSION: v1.0.0-GLOBAL-ROLE-REVISION-LOCK
AUTHORITY: Wilsy OS Core Governance
EPITOME: Selected Owner/Partner business-role currentness and exact principal
         scope are re-read from durable registries before legal obligations.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_acceptance_selected_capacity.py
COLLABORATION / OWNERSHIP: LegalAcceptanceService, IAM identity and role registry.
CERTIFICATION / UPDATE DATE: 2026-11-09
CHANGELOG: v1.0.0-GLOBAL-ROLE-REVISION-LOCK verifies GLOBAL selected-capacity
           currentness, ownership obligations, revocations and legacy isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Fully synthetic principal, no live tenant data.
TENANT BOUNDARY: Every repository lookup includes exact principal and tenant.
AUTHORITY BOUNDARY: Tests membership and capacity, never grants IAM authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from dataclasses import dataclass

import pytest

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_acceptance import LegalAgreementType
from tools.eos.legal_operations.service.legal_acceptance_service import (
    AcceptancePrincipal,
    LegalAcceptanceService,
    LegalAcceptanceServiceError,
)

TENANT = "WILSYTENANT-GLOBAL-ACCEPTANCE-CERT"
PRINCIPAL = "WILSYAUTH-GLOBAL-ACCEPTANCE-CERT"


@dataclass
class Membership:
    principal_id: str = PRINCIPAL
    tenant_id: str = TENANT
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE
    revision: int = 6


@dataclass
class BusinessRole:
    business_role: str
    principal_id: str = PRINCIPAL
    tenant_id: str = TENANT
    status: TenantBusinessRoleStatus = TenantBusinessRoleStatus.ACTIVE
    revision: int = 11


class MembershipRepository:
    def __init__(self, current: Membership | None = None):
        self.current = current or Membership()
        self.calls = []

    def resolve(self, principal_id, tenant_id, *, session=None):
        self.calls.append((principal_id, tenant_id, session))
        return self.current


class CapacityRepository:
    def __init__(self):
        self.current = {
            "tenant_owner": BusinessRole("tenant_owner"),
            "tenant_legal_partner": BusinessRole("tenant_legal_partner"),
        }
        self.selected_calls = []
        self.legacy_calls = []

    def resolve_business_role(self, principal_id, tenant_id, business_role, *, session=None):
        self.selected_calls.append((principal_id, tenant_id, business_role, session))
        return self.current[business_role]

    def resolve(self, principal_id, tenant_id, *, session=None):
        self.legacy_calls.append((principal_id, tenant_id, session))
        return BusinessRole("tenant_auditor")


def test_service(repositories=None):
    membership = MembershipRepository()
    capacities = CapacityRepository()
    service = LegalAcceptanceService(
        document_collection=object(),
        acceptance_collection=object(),
        tenant_resolver=lambda tenant_id, session=None: type("Tenant", (), {"tenant_id": tenant_id})(),
        membership_repository=membership,
        business_role_repository=capacities,
    )
    return service, membership, capacities


def identity(role: str, *, membership_revision: int = 6, capacity_revision: int = 11):
    return SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        roles=[role],
        permissions=[],
        auth_method="JWT",
        status=PrincipalStatus.ACTIVE,
        principal_scope="GLOBAL",
        session_reference="verified-global-session-reference",
        workspace_id="WILSY_HEADQUARTERS" if role == "tenant_owner" else "LEGAL_PRACTICE",
        membership_revision=membership_revision,
        capacity_revision=capacity_revision,
    )


def principal():
    return AcceptancePrincipal(TENANT, PRINCIPAL, "verified-session-reference")


def test_selected_owner_and_legal_partner_are_independent_durable_capacities():
    service, membership, capacities = test_service()
    owner = service._resolve_business_role(principal(), identity=identity("tenant_owner"))
    partner = service._resolve_business_role(principal(), identity=identity("tenant_legal_partner"))
    assert owner == "tenant_owner"
    assert partner == "tenant_legal_partner"
    assert capacities.legacy_calls == []
    assert [call[2] for call in capacities.selected_calls] == [
        "tenant_owner", "tenant_legal_partner"
    ]
    assert all(call[:2] == (PRINCIPAL, TENANT) for call in capacities.selected_calls)
    assert all(call[:2] == (PRINCIPAL, TENANT) for call in membership.calls)
    assert LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE in service._required_types(owner)
    assert LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE not in service._required_types(partner)


@pytest.mark.parametrize(
    ("membership_revision", "capacity_revision", "expected"),
    [
        (7, 11, "LEGAL_ACCEPTANCE_MEMBERSHIP_REVISION_MISMATCH"),
        (6, 12, "LEGAL_ACCEPTANCE_CAPACITY_REVISION_MISMATCH"),
    ],
)
def test_stale_global_session_revisions_fail_closed(membership_revision, capacity_revision, expected):
    service, _, _ = test_service()
    with pytest.raises(LegalAcceptanceServiceError, match=expected):
        service._resolve_business_role(
            principal(),
            identity=identity(
                "tenant_owner",
                membership_revision=membership_revision,
                capacity_revision=capacity_revision,
            ),
        )


def test_revoked_exact_selected_capacity_cannot_reuse_active_other_capacity():
    service, _, capacities = test_service()
    capacities.current["tenant_owner"].status = TenantBusinessRoleStatus.REVOKED
    with pytest.raises(LegalAcceptanceServiceError, match="LEGAL_ACCEPTANCE_BUSINESS_ROLE_INACTIVE"):
        service._resolve_business_role(principal(), identity=identity("tenant_owner"))
    assert capacities.selected_calls[0][2] == "tenant_owner"
    assert capacities.legacy_calls == []


def test_wrong_tenant_or_principal_fails_even_on_selected_role_read():
    service, _, capacities = test_service()
    capacities.current["tenant_owner"].tenant_id = "OTHER-TENANT"
    with pytest.raises(LegalAcceptanceServiceError, match="LEGAL_ACCEPTANCE_BUSINESS_ROLE_AUTHORITY_INVALID"):
        service._resolve_business_role(principal(), identity=identity("tenant_owner"))


def test_multiple_signed_roles_are_not_a_valid_selected_global_capacity():
    service, _, capacities = test_service()
    selected = identity("tenant_owner")
    selected.roles = ["tenant_owner", "tenant_legal_partner"]
    with pytest.raises(LegalAcceptanceServiceError, match="LEGAL_ACCEPTANCE_SELECTED_CAPACITY_INVALID"):
        service._resolve_business_role(principal(), identity=selected)
    assert capacities.selected_calls == []


def test_legacy_signed_admin_claim_does_not_expand_durable_tenant_role():
    service, _, capacities = test_service()
    legacy = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        roles=["SUPER_ADMIN"],
        permissions=[],
        auth_method="JWT",
        status=PrincipalStatus.ACTIVE,
        principal_scope="TENANT",
    )
    assert service._resolve_business_role(principal(), identity=legacy) == "tenant_auditor"
    assert len(capacities.legacy_calls) == 1
    assert capacities.selected_calls == []


# ARTIFACT: test_legal_acceptance_selected_capacity.py
# VERSION: v1.0.0-GLOBAL-ROLE-REVISION-LOCK
# AUTHORITY BOUNDARY: Synthetic currentness verification only.
# TENANT POSTURE: Exact tenant scope and current revisions required.
# FAIL-CLOSED POSTURE: Revoked, stale or ambiguous capacities never pass.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
