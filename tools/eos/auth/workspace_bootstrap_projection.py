"""WILSY OS server-owned workspace bootstrap projection.

TITLE: Workspace Bootstrap Projection
VERSION: v1.2.0-WILSY-CANONICAL-HEADQUARTERS-WORKSPACE-RESOLUTION
AUTHORITY: Read-only composition of current workspace authority facts.
CHANGELOG:
    2026-11-08 v1.2.0-WILSY-CANONICAL-HEADQUARTERS-WORKSPACE-RESOLUTION scopes tenant_owner presentation to
    WILSY_HEADQUARTERS only for the exact canonical WILSY company tenant.
    Customer tenant owners retain EXECUTIVE_COMMAND_CENTRE. No IAM permission,
    tenant membership, legal practice capacity, or domain authority is granted.
    v1.0.0-WILSY-WORKSPACE-BOOTSTRAP-PROJECTION established the original
    server-owned projection contract.
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
from types import MappingProxyType
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
from tools.eos.auth.hr_business_role_catalog import ALL_HR_BUSINESS_ROLES
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


VERSION = "v1.2.0-WILSY-CANONICAL-HEADQUARTERS-WORKSPACE-RESOLUTION"
WILSY_COMPANY_TENANT_ID = "WILSYTENANT-4CD2FZ4O"
WORKSPACE_CONTRACT_VERSION = "v1.0.0-WILSY-EOS-WORKSPACE-RESOLUTION"

# Canonical workspace selection is an EOS projection of an already-verified
# durable tenant business role. This mapping selects presentation scope only;
# every workspace API independently enforces its own IAM and resource policy.
_WORKSPACE_BY_BUSINESS_ROLE = MappingProxyType({
    "tenant_owner": "EXECUTIVE_COMMAND_CENTRE",
    "tenant_admin": "TENANT_ADMINISTRATION",
    "tenant_manager": "TENANT_ADMINISTRATION",
    "tenant_auditor": "AUDIT_REPORTING",
    "tenant_platform_billing_provider_policy_admin": "TENANT_OPERATIONS",
    "tenant_inbound_collection_authorization_admin": "TENANT_OPERATIONS",
    "tenant_inbound_merchant_configuration_admin": "TENANT_OPERATIONS",
    "tenant_inbound_provider_security_admin": "TENANT_OPERATIONS",
    "tenant_inbound_provider_policy_admin": "TENANT_OPERATIONS",
    "tenant_inbound_provider_policy_activation_admin": "TENANT_OPERATIONS",
    "tenant_legal_partner": "LEGAL_PRACTICE",
    "tenant_legal_attorney": "LEGAL_PRACTICE",
    "tenant_legal_paralegal": "LEGAL_PRACTICE",
    "tenant_legal_secretary": "LEGAL_PRACTICE",
    "tenant_legal_finance": "LEGAL_FINANCE",
    "tenant_legal_client": "CLIENT_PORTAL",
    "tenant_sheriff": "PROCESS_SERVICE",
    "tenant_deputy": "PROCESS_SERVICE",
    "tenant_pos_operator": "POINT_OF_SALE",
})


def resolve_workspace_id(
    business_role: str,
    *,
    tenant_id: str | None = None,
) -> str:
    """Resolve a presentation workspace from exact tenant and durable capacity.

    The WILSY company Headquarters is selected only for the exact canonical
    company tenant and its already-persisted tenant_owner business capacity.
    Customer tenant owners retain the customer Executive Command Centre.
    This mapping grants no permission or access; each destination independently
    authorizes the current principal, tenant, capacity and resource.
    """
    if business_role == "tenant_owner" and tenant_id == WILSY_COMPANY_TENANT_ID:
        return "WILSY_HEADQUARTERS"
    workspace_id = _WORKSPACE_BY_BUSINESS_ROLE.get(business_role)
    if workspace_id is not None:
        return workspace_id
    if business_role in ALL_HR_BUSINESS_ROLES:
        return "PEOPLE_OPERATIONS"
    raise WorkspaceBootstrapProjectionError(
        "WORKSPACE_BOOTSTRAP_WORKSPACE_UNMAPPED"
    )




class WorkspaceBootstrapProjectionError(RuntimeError):
    """Bounded fail-closed workspace bootstrap composition failure."""


@dataclass(frozen=True, slots=True)
class WorkspaceBootstrapProjection:
    """Browser-safe projection of current server-owned workspace authority."""

    principal_id: str
    email: str | None
    tenant_id: str
    business_role: str
    workspace_id: str
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

    principal_scope = getattr(identity, "principal_scope", None)
    selected_business_role: str | None = None
    selected_workspace_id: str | None = None
    selected_capacity_revision: int | None = None
    selected_membership_revision: int | None = None

    if principal_scope == "GLOBAL":
        roles = getattr(identity, "roles", None)
        selected_business_role = (
            roles[0]
            if isinstance(roles, list)
            and len(roles) == 1
            and isinstance(roles[0], str)
            and roles[0]
            and roles[0] == roles[0].strip()
            else None
        )
        selected_workspace_id = _exact_text(getattr(identity, "workspace_id", None))
        selected_capacity_revision = getattr(identity, "capacity_revision", None)
        selected_membership_revision = getattr(identity, "membership_revision", None)
        if (
            selected_business_role is None
            or selected_workspace_id is None
            or not isinstance(selected_capacity_revision, int)
            or isinstance(selected_capacity_revision, bool)
            or selected_capacity_revision < 0
            or not isinstance(selected_membership_revision, int)
            or isinstance(selected_membership_revision, bool)
            or selected_membership_revision < 0
        ):
            raise WorkspaceBootstrapProjectionError(
                "WORKSPACE_BOOTSTRAP_SELECTED_CAPACITY_INVALID"
            )
        if selected_membership_revision != membership_revision:
            raise WorkspaceBootstrapProjectionError(
                "WORKSPACE_BOOTSTRAP_MEMBERSHIP_REVISION_STALE"
            )

    try:
        if principal_scope == "GLOBAL":
            resolver = getattr(business_role_source, "resolve_business_role", None)
            if not callable(resolver):
                raise TenantBusinessRoleRepositoryError(
                    "TENANT_BUSINESS_ROLE_EXACT_RESOLVER_REQUIRED"
                )
            business_role_authority = resolver(
                principal_id,
                tenant_id,
                selected_business_role,
                session=session,
            )
        elif principal_scope in (None, "TENANT"):
            business_role_authority = business_role_source.resolve(
                principal_id,
                tenant_id,
                session=session,
            )
        else:
            raise WorkspaceBootstrapProjectionError(
                "WORKSPACE_BOOTSTRAP_PRINCIPAL_SCOPE_INVALID"
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
    if principal_scope == "GLOBAL":
        if (
            business_role != selected_business_role
            or business_role_revision != selected_capacity_revision
            or resolve_workspace_id(business_role, tenant_id=tenant_id) != selected_workspace_id
        ):
            raise WorkspaceBootstrapProjectionError(
                "WORKSPACE_BOOTSTRAP_SELECTED_CAPACITY_STALE"
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

    workspace_id = resolve_workspace_id(business_role, tenant_id=tenant_id)

    return WorkspaceBootstrapProjection(
        principal_id=principal_id,
        email=email,
        tenant_id=tenant_id,
        business_role=business_role,
        workspace_id=workspace_id,
        membership_revision=membership_revision,
        business_role_revision=business_role_revision,
        tenant=tenant,
    )


__all__ = [
    "VERSION",
    "WORKSPACE_CONTRACT_VERSION",
    "resolve_workspace_id",
    "WorkspaceBootstrapProjection",
    "WorkspaceBootstrapProjectionError",
    "build_workspace_bootstrap_projection",
]


# ARTIFACT: workspace_bootstrap_projection.py
# VERSION: v1.2.0-WILSY-CANONICAL-HEADQUARTERS-WORKSPACE-RESOLUTION
# AUTHORITY BOUNDARY: read-only composition; underlying authorities remain sovereign
# TENANT POSTURE: JWT tenant is candidate scope until durable workspace revalidation
# FAIL-CLOSED POSTURE: absent, inactive, malformed, mismatched, or unavailable truth denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
