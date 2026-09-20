"""WILSY OS server-owned workspace bootstrap projection.

TITLE: Workspace Bootstrap Projection
VERSION: v1.0.0-WILSY-WORKSPACE-BOOTSTRAP-PROJECTION
AUTHORITY: Read-only composition of current workspace authority facts.
PURPOSE: Compose one bounded browser-safe workspace projection from existing
         sovereign authorities without treating JWT/browser projections as truth.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/workspace_bootstrap_projection.py

AUTHORITY BOUNDARY:
    This artifact owns composition only. Authentication/current principal truth,
    tenant membership, tenant business-role persistence, and canonical tenant
    identity remain owned by their existing authorities.

TENANT BOUNDARY:
    The authenticated identity tenant claim is candidate scope only. It becomes
    workspace scope only after exact ACTIVE membership, exact ACTIVE dedicated
    tenant-business-role evidence, and exact canonical tenant resolution.

SECURITY POSTURE:
    JWT roles, JWT permissions, browser storage, caller role assertions,
    directory scans, and authorization RoleAssignment compatibility projections
    are never workspace-bootstrap authority.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authority_policy import TENANT_ROLES
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


VERSION = "v1.0.0-WILSY-WORKSPACE-BOOTSTRAP-PROJECTION"


class WorkspaceBootstrapProjectionError(RuntimeError):
    """Bounded fail-closed workspace bootstrap composition failure."""


@dataclass(frozen=True, slots=True)
class WorkspaceBootstrapProjection:
    """Browser-safe projection of current server-owned workspace authority."""

    principal_id: str
    email: str | None
    tenant_id: str
    business_role: str
    membership_revision: int
    business_role_revision: int
    tenant: Any


def _exact_text(value: object) -> str | None:
    """Return a non-empty exact string without normalizing caller authority."""
    if not isinstance(value, str) or not value or value != value.strip():
        return None
    return value


def build_workspace_bootstrap_projection(
    *,
    identity: Any,
    membership_repository: Any = None,
    business_role_repository: Any = None,
    tenant_resolver: Any = None,
    session: Any = None,
) -> WorkspaceBootstrapProjection:
    """Compose current workspace truth from existing durable authorities only."""

    principal_id = _exact_text(getattr(identity, "identity_id", None))
    tenant_id = _exact_text(getattr(identity, "tenant_id", None))

    if principal_id is None or tenant_id is None:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_IDENTITY_INVALID"
        )

    if getattr(identity, "status", None) is not PrincipalStatus.ACTIVE:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_PRINCIPAL_INACTIVE"
        )

    membership_source = (
        membership_repository
        if membership_repository is not None
        else TenantMembershipRepository()
    )

    try:
        membership = membership_source.resolve(
            principal_id,
            tenant_id,
            session=session,
        )
    except TenantMembershipNotFoundError as error:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_MEMBERSHIP_REQUIRED"
        ) from error
    except TenantMembershipRepositoryError as error:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_UNAVAILABLE"
        ) from error

    if (
        getattr(membership, "principal_id", None) != principal_id
        or getattr(membership, "tenant_id", None) != tenant_id
    ):
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_INVALID"
        )

    if getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_MEMBERSHIP_INACTIVE"
        )

    membership_revision = getattr(membership, "revision", None)
    if (
        not isinstance(membership_revision, int)
        or isinstance(membership_revision, bool)
        or membership_revision < 0
    ):
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_INVALID"
        )

    business_role_source = (
        business_role_repository
        if business_role_repository is not None
        else TenantBusinessRoleRepository()
    )

    try:
        business_role_authority = business_role_source.resolve(
            principal_id,
            tenant_id,
            session=session,
        )
    except TenantBusinessRoleNotFoundError as error:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_REQUIRED"
        ) from error
    except TenantBusinessRoleRepositoryError as error:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE"
        ) from error

    business_role = getattr(
        business_role_authority,
        "business_role",
        None,
    )

    if (
        getattr(business_role_authority, "principal_id", None) != principal_id
        or getattr(business_role_authority, "tenant_id", None) != tenant_id
        or not isinstance(business_role, str)
        or business_role not in TENANT_ROLES
    ):
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_INVALID"
        )

    if (
        getattr(business_role_authority, "status", None)
        is not TenantBusinessRoleStatus.ACTIVE
    ):
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_INACTIVE"
        )

    business_role_revision = getattr(
        business_role_authority,
        "revision",
        None,
    )
    if (
        not isinstance(business_role_revision, int)
        or isinstance(business_role_revision, bool)
        or business_role_revision < 0
    ):
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_INVALID"
        )

    resolver = (
        tenant_resolver
        if tenant_resolver is not None
        else TenantRegistry.resolve_canonical_tenant
    )

    try:
        tenant = resolver(tenant_id, session=session)
    except Exception as error:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_TENANT_UNAVAILABLE"
        ) from error

    if getattr(tenant, "tenant_id", None) != tenant_id:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_TENANT_MISMATCH"
        )

    email = getattr(identity, "email", None)
    if email is not None and not isinstance(email, str):
        email = None

    return WorkspaceBootstrapProjection(
        principal_id=principal_id,
        email=email,
        tenant_id=tenant_id,
        business_role=business_role,
        membership_revision=membership_revision,
        business_role_revision=business_role_revision,
        tenant=tenant,
    )


__all__ = [
    "VERSION",
    "WorkspaceBootstrapProjection",
    "WorkspaceBootstrapProjectionError",
    "build_workspace_bootstrap_projection",
]


# ARTIFACT: workspace_bootstrap_projection.py
# VERSION: v1.0.0-WILSY-WORKSPACE-BOOTSTRAP-PROJECTION
# AUTHORITY BOUNDARY: read-only composition; underlying authorities remain sovereign
# TENANT POSTURE: JWT tenant is candidate scope until durable workspace revalidation
# FAIL-CLOSED POSTURE: absent, inactive, malformed, mismatched, or unavailable truth denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
