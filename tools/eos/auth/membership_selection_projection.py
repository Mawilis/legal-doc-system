"""Read-only, principal-scoped projection of eligible tenant memberships.

This projection is intended for the post-credential, pre-session membership
selection stage. It does not authenticate a principal, create membership,
assign a business capacity, issue a token, or authorize tenant operations.
Every returned tenant and capacity is re-resolved from current EOS authorities.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.workspace_bootstrap_projection import resolve_workspace_id
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

VERSION = "v1.0.0-PRINCIPAL-MEMBERSHIP-SELECTION-PROJECTION"
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


class MembershipSelectionProjectionError(RuntimeError):
    """Fail-closed membership directory or current-authority failure."""


@dataclass(frozen=True, slots=True)
class MembershipCapacityChoice:
    """One current tenant business capacity, not an authorization grant."""

    business_role: str
    workspace_id: str
    business_role_revision: int


@dataclass(frozen=True, slots=True)
class MembershipChoice:
    """One active principal/tenant membership and its eligible capacities."""

    tenant_id: str
    membership_revision: int
    capacities: tuple[MembershipCapacityChoice, ...]


@dataclass(frozen=True, slots=True)
class MembershipSelectionPage:
    """Bounded, deterministic choices for one already-authenticated principal."""

    principal_id: str
    memberships: tuple[MembershipChoice, ...]
    next_cursor: str | None


def build_membership_selection_page(
    *,
    principal_id: str,
    after_tenant_id: str | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
    principal_repository: Any = None,
    membership_repository: Any = None,
    business_role_repository: Any = None,
    tenant_resolver: Any = None,
    session: Any = None,
) -> MembershipSelectionPage:
    """Project current eligible memberships for one ACTIVE global principal.

    The principal must already have been authenticated by a separate credential
    authority. A discovered tenant alias is deliberately not accepted here:
    tenant discovery is a routing hint, never proof of membership. Pagination
    is keyed by canonical tenant_id and remains bounded for large installations.
    """
    if not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip():
        raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_PRINCIPAL_INVALID")
    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= MAX_PAGE_SIZE:
        raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_PAGE_LIMIT_INVALID")

    principals = principal_repository or PrincipalAuthorityRepository()
    memberships_source = membership_repository or TenantMembershipRepository()
    business_roles = business_role_repository or TenantBusinessRoleRepository()
    resolve_tenant = tenant_resolver or TenantRegistry.resolve_canonical_tenant

    try:
        principal = principals.get(principal_id, session=session)
    except PrincipalAuthorityNotFoundError as error:
        raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_PRINCIPAL_REQUIRED") from error
    except PrincipalAuthorityRepositoryError as error:
        raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_PRINCIPAL_UNAVAILABLE") from error

    if getattr(principal, "principal_id", None) != principal_id or getattr(principal, "status", None) is not PrincipalStatus.ACTIVE:
        raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_PRINCIPAL_NOT_ACTIVE")

    try:
        membership_rows, next_cursor = memberships_source.list_for_principal(
            principal_id,
            after_tenant_id=after_tenant_id,
            limit=limit,
            session=session,
        )
    except TenantMembershipRepositoryError as error:
        raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_MEMBERSHIPS_UNAVAILABLE") from error

    choices: list[MembershipChoice] = []
    for membership in membership_rows:
        if membership.principal_id != principal_id:
            raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_MEMBERSHIP_MISMATCH")
        if membership.status is not TenantMembershipStatus.ACTIVE:
            continue
        try:
            tenant = resolve_tenant(membership.tenant_id, session=session)
        except Exception as error:
            raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_TENANT_UNAVAILABLE") from error
        if getattr(tenant, "tenant_id", None) != membership.tenant_id:
            raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_TENANT_MISMATCH")

        try:
            role_rows = business_roles.resolve_all(
                principal_id,
                membership.tenant_id,
                session=session,
            )
        except TenantBusinessRoleRepositoryError as error:
            raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_CAPACITIES_UNAVAILABLE") from error

        capacities: list[MembershipCapacityChoice] = []
        seen_roles: set[str] = set()
        for role in role_rows:
            if role.principal_id != principal_id or role.tenant_id != membership.tenant_id:
                raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_CAPACITY_MISMATCH")
            if role.status is not TenantBusinessRoleStatus.ACTIVE:
                continue
            if role.business_role in seen_roles:
                raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_CAPACITY_AMBIGUOUS")
            seen_roles.add(role.business_role)
            try:
                workspace_id = resolve_workspace_id(role.business_role)
            except Exception as error:
                raise MembershipSelectionProjectionError("MEMBERSHIP_SELECTION_WORKSPACE_UNMAPPED") from error
            capacities.append(
                MembershipCapacityChoice(
                    business_role=role.business_role,
                    workspace_id=workspace_id,
                    business_role_revision=role.revision,
                )
            )
        choices.append(
            MembershipChoice(
                tenant_id=membership.tenant_id,
                membership_revision=membership.revision,
                capacities=tuple(sorted(capacities, key=lambda item: item.business_role)),
            )
        )

    return MembershipSelectionPage(
        principal_id=principal_id,
        memberships=tuple(choices),
        next_cursor=next_cursor,
    )


__all__ = [
    "VERSION",
    "DEFAULT_PAGE_SIZE",
    "MAX_PAGE_SIZE",
    "MembershipSelectionProjectionError",
    "MembershipCapacityChoice",
    "MembershipChoice",
    "MembershipSelectionPage",
    "build_membership_selection_page",
]
