"""TITLE: WILSY OS Workspace Bootstrap Projection Certification.
VERSION: v1.1.0-WILSY-HEADQUARTERS-WORKSPACE-RESOLUTION-TESTS
AUTHORITY: Unit-level verification of read-only EOS workspace projection.
EPITOME: Certifies tenant-aware WILSY Headquarters selection, ordinary customer
         tenant owner routing, current membership/capacity validation and
         fail-closed canonical tenant resolution.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_workspace_bootstrap_projection.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-08.
CHANGELOG:
    2026-11-08 v1.1.0-WILSY-HEADQUARTERS-WORKSPACE-RESOLUTION-TESTS certifies exact canonical WILSY tenant routing to
    WILSY_HEADQUARTERS without changing customer tenant owner routing.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Exercises forged transport claims and exact durable
    principal, membership, business-capacity and tenant authority boundaries.
TENANT BOUNDARY: WILSY Headquarters selection requires exact canonical company
    tenant scope; ordinary tenant owners retain their own customer workspace.
AUTHORITY BOUNDARY: Tests read-only presentation projection only; no permissions
    or domain authority are created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

"""Direct certificate for the server-owned WorkspaceBootstrapProjection.

The projection must compose existing sovereign authorities only:
- authenticated/current ACTIVE principal supplied by get_current_identity;
- exact ACTIVE TenantMembership authority;
- exact dedicated ACTIVE TenantBusinessRole authority;
- exact canonical ACTIVE TenantEntity resolution.

JWT role/permission claims, browser state, directory scans, and RoleAssignment
compatibility projections are not workspace-bootstrap authority.
"""

from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any

import pytest

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepositoryError,
)
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES


def _contract() -> Any:
    try:
        return importlib.import_module(
            "tools.eos.auth.workspace_bootstrap_projection"
        )
    except ModuleNotFoundError as error:
        pytest.fail(
            "WORKSPACE_BOOTSTRAP_PROJECTION_NOT_ESTABLISHED",
            pytrace=False,
        )
        raise AssertionError from error


def _identity(
    *,
    tenant_id: str = "TENANT-A",
    status: PrincipalStatus = PrincipalStatus.ACTIVE,
) -> SimpleNamespace:
    return SimpleNamespace(
        identity_id="principal-1",
        tenant_id=tenant_id,
        email="principal@example.com",
        status=status,
        # Deliberately forged transport projections. They must never become
        # workspace role/permission authority.
        roles=["SUPER_ADMIN"],
        permissions=["*"],
    )


def _membership(
    *,
    principal_id: str = "principal-1",
    tenant_id: str = "TENANT-A",
    status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    revision: int = 7,
) -> SimpleNamespace:
    return SimpleNamespace(
        principal_id=principal_id,
        tenant_id=tenant_id,
        status=status,
        revision=revision,
    )


def _business_role(
    *,
    principal_id: str = "principal-1",
    tenant_id: str = "TENANT-A",
    business_role: str = "tenant_auditor",
    status: TenantBusinessRoleStatus = TenantBusinessRoleStatus.ACTIVE,
    revision: int = 11,
) -> SimpleNamespace:
    return SimpleNamespace(
        principal_id=principal_id,
        tenant_id=tenant_id,
        business_role=business_role,
        status=status,
        revision=revision,
    )


def _tenant(*, tenant_id: str = "TENANT-A") -> SimpleNamespace:
    return SimpleNamespace(
        tenant_id=tenant_id,
        status="ACTIVE",
        organization=SimpleNamespace(
            organization_name="Tenant A",
            legal_name="Tenant A (Pty) Ltd",
        ),
    )


class _ExactRepository:
    def __init__(self, value: Any = None, error: Exception | None = None) -> None:
        self.value = value
        self.error = error
        self.calls: list[tuple[str, str]] = []
        self.selected_calls: list[tuple[str, str, str]] = []

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        del session
        self.calls.append((principal_id, tenant_id))
        if self.error is not None:
            raise self.error
        return self.value

    def resolve_business_role(
        self,
        principal_id: str,
        tenant_id: str,
        business_role: str,
        *,
        session: Any = None,
    ) -> Any:
        del session
        self.selected_calls.append((principal_id, tenant_id, business_role))
        if self.error is not None:
            raise self.error
        if getattr(self.value, "business_role", None) != business_role:
            raise TenantBusinessRoleNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
        return self.value


class _TenantResolver:
    def __init__(self, value: Any = None, error: Exception | None = None) -> None:
        self.value = value
        self.error = error
        self.calls: list[str] = []

    def __call__(self, tenant_id: str, *, session: Any = None) -> Any:
        del session
        self.calls.append(tenant_id)
        if self.error is not None:
            raise self.error
        return self.value


def _build(
    *,
    identity: Any | None = None,
    membership: Any | None = None,
    business_role: Any | None = None,
    tenant: Any | None = None,
    membership_error: Exception | None = None,
    business_role_error: Exception | None = None,
    tenant_error: Exception | None = None,
) -> tuple[Any, _ExactRepository, _ExactRepository, _TenantResolver]:
    contract = _contract()
    membership_repository = _ExactRepository(
        membership if membership is not None else _membership(),
        membership_error,
    )
    business_role_repository = _ExactRepository(
        business_role if business_role is not None else _business_role(),
        business_role_error,
    )
    tenant_resolver = _TenantResolver(
        tenant if tenant is not None else _tenant(),
        tenant_error,
    )

    projection = contract.build_workspace_bootstrap_projection(
        identity=identity if identity is not None else _identity(),
        membership_repository=membership_repository,
        business_role_repository=business_role_repository,
        tenant_resolver=tenant_resolver,
    )
    return (
        projection,
        membership_repository,
        business_role_repository,
        tenant_resolver,
    )


def _error_code(error: BaseException) -> str:
    return str(error)


def test_workspace_bootstrap_uses_only_current_durable_workspace_authorities() -> None:
    projection, memberships, roles, tenants = _build()

    assert projection.principal_id == "principal-1"
    assert projection.email == "principal@example.com"
    assert projection.tenant_id == "TENANT-A"
    assert projection.business_role == "tenant_auditor"
    assert projection.workspace_id == "AUDIT_REPORTING"
    assert projection.membership_revision == 7
    assert projection.business_role_revision == 11
    assert projection.tenant.tenant_id == "TENANT-A"

    # Forged JWT projections must not survive as workspace authority.
    assert not hasattr(projection, "roles")
    assert not hasattr(projection, "permissions")

    assert memberships.calls == [("principal-1", "TENANT-A")]
    assert roles.calls == [("principal-1", "TENANT-A")]
    assert tenants.calls == ["TENANT-A"]


def test_workspace_bootstrap_rejects_inactive_principal() -> None:
    contract = _contract()
    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as raised:
        _build(
            identity=_identity(status=PrincipalStatus.SUSPENDED),
        )
    assert _error_code(raised.value) == "WORKSPACE_BOOTSTRAP_PRINCIPAL_INACTIVE"


def test_workspace_bootstrap_requires_exact_active_membership() -> None:
    contract = _contract()

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as missing:
        _build(
            membership_error=TenantMembershipNotFoundError(
                "TENANT_MEMBERSHIP_NOT_FOUND"
            )
        )
    assert _error_code(missing.value) == "WORKSPACE_BOOTSTRAP_MEMBERSHIP_REQUIRED"

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as inactive:
        _build(
            membership=_membership(status=TenantMembershipStatus.SUSPENDED)
        )
    assert _error_code(inactive.value) == "WORKSPACE_BOOTSTRAP_MEMBERSHIP_INACTIVE"

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as mismatch:
        _build(
            membership=_membership(tenant_id="TENANT-B")
        )
    assert _error_code(mismatch.value) == "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_INVALID"


def test_workspace_bootstrap_fails_closed_when_membership_authority_is_unavailable() -> None:
    contract = _contract()
    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as raised:
        _build(
            membership_error=TenantMembershipRepositoryError(
                "TENANT_MEMBERSHIP_READ_FAILED"
            )
        )
    assert (
        _error_code(raised.value)
        == "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_UNAVAILABLE"
    )


def test_workspace_bootstrap_requires_exact_active_dedicated_business_role() -> None:
    contract = _contract()

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as missing:
        _build(
            business_role_error=TenantBusinessRoleNotFoundError(
                "TENANT_BUSINESS_ROLE_NOT_FOUND"
            )
        )
    assert _error_code(missing.value) == "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_REQUIRED"

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as inactive:
        _build(
            business_role=_business_role(
                status=TenantBusinessRoleStatus.REVOKED
            )
        )
    assert _error_code(inactive.value) == "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_INACTIVE"

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as mismatch:
        _build(
            business_role=_business_role(principal_id="principal-2")
        )
    assert (
        _error_code(mismatch.value)
        == "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_INVALID"
    )


def test_workspace_bootstrap_rejects_noncanonical_business_role() -> None:
    contract = _contract()
    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as raised:
        _build(
            business_role=_business_role(business_role="SUPER_ADMIN")
        )
    assert (
        _error_code(raised.value)
        == "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_INVALID"
    )


def test_workspace_bootstrap_fails_closed_when_business_role_authority_is_unavailable() -> None:
    contract = _contract()
    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as raised:
        _build(
            business_role_error=TenantBusinessRoleRepositoryError(
                "TENANT_BUSINESS_ROLE_READ_FAILED"
            )
        )
    assert (
        _error_code(raised.value)
        == "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
    )


def test_workspace_bootstrap_requires_exact_canonical_tenant() -> None:
    contract = _contract()

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as mismatch:
        _build(tenant=_tenant(tenant_id="TENANT-B"))
    assert _error_code(mismatch.value) == "WORKSPACE_BOOTSTRAP_TENANT_MISMATCH"

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as unavailable:
        _build(tenant_error=RuntimeError("TENANT_REGISTRY_UNAVAILABLE"))
    assert _error_code(unavailable.value) == "WORKSPACE_BOOTSTRAP_TENANT_UNAVAILABLE"



def test_workspace_resolution_maps_owner_and_legal_practice_to_distinct_workspaces() -> None:
    contract = _contract()

    assert contract.resolve_workspace_id("tenant_owner") == "EXECUTIVE_COMMAND_CENTRE"
    assert contract.resolve_workspace_id("tenant_legal_partner") == "LEGAL_PRACTICE"
    assert contract.resolve_workspace_id("tenant_legal_attorney") == "LEGAL_PRACTICE"
    assert contract.resolve_workspace_id("tenant_sheriff") == "PROCESS_SERVICE"


def test_every_published_tenant_business_role_has_one_workspace_mapping() -> None:
    contract = _contract()

    resolved = {
        role: contract.resolve_workspace_id(role)
        for role in TENANT_ROLES
    }

    assert resolved["tenant_owner"] == "EXECUTIVE_COMMAND_CENTRE"
    assert resolved["tenant_legal_partner"] == "LEGAL_PRACTICE"
    assert all(isinstance(workspace_id, str) and workspace_id for workspace_id in resolved.values())


def test_wilsy_company_owner_resolves_to_headquarters_only_for_canonical_tenant() -> None:
    contract = _contract()

    assert contract.resolve_workspace_id(
        "tenant_owner",
        tenant_id="WILSYTENANT-4CD2FZ4O",
    ) == "WILSY_HEADQUARTERS"
    assert contract.resolve_workspace_id(
        "tenant_owner",
        tenant_id="CUSTOMER-TENANT-1",
    ) == "EXECUTIVE_COMMAND_CENTRE"
    assert contract.resolve_workspace_id("tenant_owner") == "EXECUTIVE_COMMAND_CENTRE"
    assert contract.resolve_workspace_id(
        "tenant_legal_partner",
        tenant_id="WILSYTENANT-4CD2FZ4O",
    ) == "LEGAL_PRACTICE"


def test_unknown_workspace_role_fails_closed() -> None:
    contract = _contract()

    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as raised:
        contract.resolve_workspace_id("tenant_unpublished_role")

    assert _error_code(raised.value) == "WORKSPACE_BOOTSTRAP_WORKSPACE_UNMAPPED"


def _global_identity(
    *,
    business_role: str = "tenant_owner",
    workspace_id: str = "EXECUTIVE_COMMAND_CENTRE",
    membership_revision: int = 7,
    capacity_revision: int = 11,
) -> SimpleNamespace:
    return SimpleNamespace(
        identity_id="principal-1",
        tenant_id="TENANT-A",
        email="principal@example.com",
        status=PrincipalStatus.ACTIVE,
        roles=[business_role],
        permissions=[],
        principal_scope="GLOBAL",
        workspace_id=workspace_id,
        membership_revision=membership_revision,
        capacity_revision=capacity_revision,
    )


def test_global_workspace_bootstrap_uses_exact_session_selected_capacity() -> None:
    projection, memberships, roles, tenants = _build(
        identity=_global_identity(),
        business_role=_business_role(business_role="tenant_owner"),
    )

    assert projection.business_role == "tenant_owner"
    assert projection.workspace_id == "EXECUTIVE_COMMAND_CENTRE"
    assert projection.membership_revision == 7
    assert projection.business_role_revision == 11
    assert roles.calls == []
    assert roles.selected_calls == [
        ("principal-1", "TENANT-A", "tenant_owner")
    ]
    assert memberships.calls == [("principal-1", "TENANT-A")]
    assert tenants.calls == ["TENANT-A"]


@pytest.mark.parametrize(
    ("identity", "business_role", "expected"),
    [
        (
            _global_identity(capacity_revision=10),
            _business_role(business_role="tenant_owner"),
            "WORKSPACE_BOOTSTRAP_SELECTED_CAPACITY_STALE",
        ),
        (
            _global_identity(workspace_id="LEGAL_PRACTICE"),
            _business_role(business_role="tenant_owner"),
            "WORKSPACE_BOOTSTRAP_SELECTED_CAPACITY_STALE",
        ),
        (
            _global_identity(membership_revision=6),
            _business_role(business_role="tenant_owner"),
            "WORKSPACE_BOOTSTRAP_MEMBERSHIP_REVISION_STALE",
        ),
    ],
)
def test_global_workspace_bootstrap_rejects_stale_selected_capacity_context(
    identity: Any,
    business_role: Any,
    expected: str,
) -> None:
    contract = _contract()
    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as raised:
        _build(identity=identity, business_role=business_role)
    assert _error_code(raised.value) == expected


def test_global_workspace_bootstrap_does_not_fall_back_to_another_active_capacity() -> None:
    contract = _contract()
    with pytest.raises(contract.WorkspaceBootstrapProjectionError) as raised:
        _build(
            identity=_global_identity(business_role="tenant_legal_partner"),
            business_role=_business_role(business_role="tenant_owner"),
        )
    assert _error_code(raised.value) == "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_REQUIRED"

# ARTIFACT: test_workspace_bootstrap_projection.py
# VERSION: v1.1.0-WILSY-HEADQUARTERS-WORKSPACE-RESOLUTION-TESTS
# AUTHORITY BOUNDARY: unit certification of read-only workspace projection only
# TENANT POSTURE: canonical WILSY company tenant and customer tenant cases are isolated
# FAIL-CLOSED POSTURE: malformed, stale, inactive, mismatched and unknown authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
