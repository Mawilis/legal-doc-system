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
