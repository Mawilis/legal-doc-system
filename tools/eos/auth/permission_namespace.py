"""TITLE: WILSY OS Permission Namespace Semantic Canon.
VERSION: v1.3.0-PLAN-PERMISSION-CANON
AUTHORITY: Immutable permission vocabulary and scope metadata only.
EPITOME: Extends the canonical TENANT permission vocabulary with bounded
subscription and plan-catalogue read/manage capabilities without granting
possession, cross-tenant authority, entitlement, or financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/permission_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-03.
CHANGELOG:
    2026-09-03 v1.3.0-PLAN-PERMISSION-CANON adds plan:read and plan:manage
    as explicit own-tenant, membership-required, non-cross-tenant,
    non-financial canonical permissions.
    v1.2.0-SUBSCRIPTION-PERMISSION-CANON added subscription:read and
    subscription:manage as explicit own-tenant, membership-required,
    non-cross-tenant, non-financial canonical permissions.
    v1.1.0-PERMISSION-NAMESPACE-CANON added the bounded TENANT vocabulary.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Metadata never authenticates, authorizes, proves
membership, trusts transport projections, or grants execution.
TENANT BOUNDARY: Subscription and plan permissions require separately proven
ACTIVE membership in the exact selected tenant and never permit cross-tenant
access.
AUTHORITY BOUNDARY: Owns permission vocabulary semantics only. Current role
assignment and final authorization remain separate authorities.
FINANCIAL AUTHORITY BOUNDARY: Subscription and plan catalogue permissions
cannot approve, release, execute, collect, or settle funds. Kennel EOS remains
exclusive.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from json import dumps
from types import MappingProxyType
from typing import Final


VERSION = "v1.3.0-PLAN-PERMISSION-CANON"


class PermissionDisposition(StrEnum):
    """Closed permission-canon disposition vocabulary."""

    CANONICAL = "CANONICAL"
    LEGACY_ONLY = "LEGACY_ONLY"
    DEPRECATED = "DEPRECATED"
    BLOCKED_AMBIGUOUS = "BLOCKED_AMBIGUOUS"


@dataclass(frozen=True, slots=True)
class PermissionMetadata:
    """Immutable semantic metadata for one permission identifier."""

    permission_id: str
    namespace: str
    scope_kind: str
    business_capability: str
    tenant_membership_required: bool
    system_assignment_required: bool
    cross_tenant_capable: bool
    financial_execution_capable: bool
    deprecated_or_legacy: bool
    authorizes_by_itself: bool
    disposition: PermissionDisposition


def _meta(
    permission_id: str,
    namespace: str,
    scope: str,
    capability: str,
    *,
    tenant: bool = False,
    system: bool = False,
    disposition: PermissionDisposition = PermissionDisposition.CANONICAL,
) -> PermissionMetadata:
    """Construct immutable metadata without creating authority."""
    return PermissionMetadata(
        permission_id=permission_id,
        namespace=namespace,
        scope_kind=scope,
        business_capability=capability,
        tenant_membership_required=tenant,
        system_assignment_required=system,
        cross_tenant_capable=False,
        financial_execution_capable=False,
        deprecated_or_legacy=(
            disposition is not PermissionDisposition.CANONICAL
        ),
        authorizes_by_itself=False,
        disposition=disposition,
    )


_PERMISSIONS: Final = MappingProxyType(
    {
        "kernel:read": _meta(
            "kernel:read",
            "SYSTEM",
            "SYSTEM",
            "read kernel state",
            system=True,
        ),
        "kernel:write": _meta(
            "kernel:write",
            "SYSTEM",
            "SYSTEM",
            "write kernel state",
            system=True,
        ),
        "governance:evaluate": _meta(
            "governance:evaluate",
            "SYSTEM",
            "SYSTEM",
            "evaluate governance",
            system=True,
        ),
        "governance:read": _meta(
            "governance:read",
            "SYSTEM",
            "SYSTEM",
            "read governance evidence",
            system=True,
        ),
        "artifacts:read": _meta(
            "artifacts:read",
            "TENANT",
            "TENANT",
            "read artifacts",
            tenant=True,
        ),
        "artifacts:write": _meta(
            "artifacts:write",
            "SERVICE",
            "SERVICE",
            "write service artifacts",
        ),
        "events:publish": _meta(
            "events:publish",
            "SERVICE",
            "SERVICE",
            "publish service events",
        ),
        "audit:read": _meta(
            "audit:read",
            "TENANT",
            "TENANT",
            "read tenant audit evidence",
            tenant=True,
        ),
        "tenant:profile:read": _meta(
            "tenant:profile:read",
            "TENANT",
            "TENANT",
            "read bounded tenant profile",
            tenant=True,
        ),
        "tenant:profile:write": _meta(
            "tenant:profile:write",
            "TENANT",
            "TENANT",
            "write bounded tenant profile",
            tenant=True,
        ),
        "tenant:lifecycle:archive": _meta(
            "tenant:lifecycle:archive",
            "TENANT",
            "TENANT",
            "archive own tenant",
            tenant=True,
        ),
        "tenant:membership:read": _meta(
            "tenant:membership:read",
            "TENANT",
            "TENANT",
            "read tenant membership",
            tenant=True,
        ),
        "tenant:membership:write": _meta(
            "tenant:membership:write",
            "TENANT",
            "TENANT",
            "administer tenant membership",
            tenant=True,
        ),
        "tenant:role_assignment:read": _meta(
            "tenant:role_assignment:read",
            "TENANT",
            "TENANT",
            "read tenant role assignments",
            tenant=True,
        ),
        "tenant:role_assignment:write": _meta(
            "tenant:role_assignment:write",
            "TENANT",
            "TENANT",
            "administer tenant role assignments",
            tenant=True,
        ),
        "subscription:read": _meta(
            "subscription:read",
            "TENANT",
            "TENANT",
            "read own-tenant subscription commercial truth",
            tenant=True,
        ),
        "subscription:manage": _meta(
            "subscription:manage",
            "TENANT",
            "TENANT",
            "manage own-tenant subscription lifecycle truth",
            tenant=True,
        ),
        "plan:read": _meta(
            "plan:read",
            "TENANT",
            "TENANT",
            "read own-tenant plan catalogue commercial truth",
            tenant=True,
        ),
        "plan:manage": _meta(
            "plan:manage",
            "TENANT",
            "TENANT",
            "manage own-tenant plan catalogue lifecycle truth",
            tenant=True,
        ),
        "execution:trigger": _meta(
            "execution:trigger",
            "SYSTEM",
            "UNSAFE_MULTI_NAMESPACE",
            "trigger non-financial execution",
            disposition=PermissionDisposition.BLOCKED_AMBIGUOUS,
        ),
        "tenant:manage": _meta(
            "tenant:manage",
            "TENANT",
            "UNRESOLVED",
            "tenant administration (scope unresolved)",
            tenant=True,
            disposition=PermissionDisposition.BLOCKED_AMBIGUOUS,
        ),
        "admin:all": _meta(
            "admin:all",
            "SYSTEM",
            "LEGACY",
            "legacy administrative label",
            system=True,
            disposition=PermissionDisposition.LEGACY_ONLY,
        ),
    }
)


def permission_metadata(
    permission_id: str,
) -> PermissionMetadata:
    """Return exact immutable metadata; malformed and unknown values deny."""
    if (
        not isinstance(permission_id, str)
        or not permission_id
        or permission_id != permission_id.strip()
    ):
        raise ValueError("UNKNOWN_PERMISSION")

    try:
        return _PERMISSIONS[permission_id]
    except KeyError as error:
        raise ValueError(
            "UNKNOWN_PERMISSION"
        ) from error


def canonical_permissions() -> bytes:
    """Serialize the immutable permission canon deterministically."""
    rows = [
        {
            "permission_id": value.permission_id,
            "namespace": value.namespace,
            "scope_kind": value.scope_kind,
            "business_capability": value.business_capability,
            "tenant_membership_required":
                value.tenant_membership_required,
            "system_assignment_required":
                value.system_assignment_required,
            "cross_tenant_capable":
                value.cross_tenant_capable,
            "financial_execution_capable":
                value.financial_execution_capable,
            "deprecated_or_legacy":
                value.deprecated_or_legacy,
            "authorizes_by_itself":
                value.authorizes_by_itself,
            "disposition":
                value.disposition.value,
        }
        for value in _PERMISSIONS.values()
    ]

    return dumps(
        rows,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")


def classify_legacy_permission(
    permission_id: object,
) -> PermissionDisposition | None:
    """Classify known noncanonical permissions without authorizing."""
    if (
        not isinstance(permission_id, str)
        or not permission_id
        or permission_id != permission_id.strip()
    ):
        return None

    try:
        return permission_metadata(
            permission_id
        ).disposition
    except ValueError:
        return None


__all__ = [
    "PermissionDisposition",
    "PermissionMetadata",
    "VERSION",
    "permission_metadata",
    "canonical_permissions",
    "classify_legacy_permission",
]

# ARTIFACT: tools/eos/auth/permission_namespace.py
# VERSION: v1.3.0-PLAN-PERMISSION-CANON
# AUTHORITY BOUNDARY: canonical permission vocabulary semantics only; no possession or authorization authority
# TENANT POSTURE: subscription and plan permissions require separately proven exact ACTIVE tenant membership
# FAIL-CLOSED POSTURE: unknown, malformed, ambiguous and legacy values never manufacture authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
