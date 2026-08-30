"""TITLE: WILSY OS Permission Namespace Semantic Canon.
VERSION: v1.1.0-PERMISSION-NAMESPACE-CANON
AUTHORITY: Immutable permission vocabulary and scope metadata only.
EPITOME: Binds explicit permission identifiers to bounded authority namespaces without assigning or authorizing them.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/permission_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.1.0 adds seven bounded TENANT vocabulary permissions without role grants or authorization.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Metadata never authenticates, authorizes, proves membership, trusts JWT/Node input, or grants financial execution.
TENANT BOUNDARY: Tenant permissions require current governed membership; no descriptor creates membership or cross-tenant authority.
AUTHORITY BOUNDARY: Owns permission vocabulary semantics only; role assignment and final authorization remain separate authorities.
FINANCIAL AUTHORITY BOUNDARY: No permission is financial; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from json import dumps
from types import MappingProxyType
from typing import Final

VERSION = "v1.1.0-PERMISSION-NAMESPACE-CANON"


class PermissionDisposition(StrEnum):
    CANONICAL = "CANONICAL"
    LEGACY_ONLY = "LEGACY_ONLY"
    DEPRECATED = "DEPRECATED"
    BLOCKED_AMBIGUOUS = "BLOCKED_AMBIGUOUS"


@dataclass(frozen=True, slots=True)
class PermissionMetadata:
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


def _meta(permission_id: str, namespace: str, scope: str, capability: str, *, tenant: bool = False, system: bool = False, disposition: PermissionDisposition = PermissionDisposition.CANONICAL) -> PermissionMetadata:
    return PermissionMetadata(permission_id, namespace, scope, capability, tenant, system, False, False, disposition is not PermissionDisposition.CANONICAL, False, disposition)


_PERMISSIONS: Final = MappingProxyType({
    "kernel:read": _meta("kernel:read", "SYSTEM", "SYSTEM", "read kernel state", system=True),
    "kernel:write": _meta("kernel:write", "SYSTEM", "SYSTEM", "write kernel state", system=True),
    "governance:evaluate": _meta("governance:evaluate", "SYSTEM", "SYSTEM", "evaluate governance", system=True),
    "governance:read": _meta("governance:read", "SYSTEM", "SYSTEM", "read governance evidence", system=True),
    "artifacts:read": _meta("artifacts:read", "TENANT", "TENANT", "read artifacts", tenant=True),
    "artifacts:write": _meta("artifacts:write", "SERVICE", "SERVICE", "write service artifacts"),
    "events:publish": _meta("events:publish", "SERVICE", "SERVICE", "publish service events"),
    "audit:read": _meta("audit:read", "TENANT", "TENANT", "read tenant audit evidence", tenant=True),
    "tenant:profile:read": _meta("tenant:profile:read", "TENANT", "TENANT", "read bounded tenant profile", tenant=True),
    "tenant:profile:write": _meta("tenant:profile:write", "TENANT", "TENANT", "write bounded tenant profile", tenant=True),
    "tenant:lifecycle:archive": _meta("tenant:lifecycle:archive", "TENANT", "TENANT", "archive own tenant", tenant=True),
    "tenant:membership:read": _meta("tenant:membership:read", "TENANT", "TENANT", "read tenant membership", tenant=True),
    "tenant:membership:write": _meta("tenant:membership:write", "TENANT", "TENANT", "administer tenant membership", tenant=True),
    "tenant:role_assignment:read": _meta("tenant:role_assignment:read", "TENANT", "TENANT", "read tenant role assignments", tenant=True),
    "tenant:role_assignment:write": _meta("tenant:role_assignment:write", "TENANT", "TENANT", "administer tenant role assignments", tenant=True),
    "execution:trigger": _meta("execution:trigger", "SYSTEM", "UNSAFE_MULTI_NAMESPACE", "trigger non-financial execution", disposition=PermissionDisposition.BLOCKED_AMBIGUOUS),
    "tenant:manage": _meta("tenant:manage", "TENANT", "UNRESOLVED", "tenant administration (scope unresolved)", tenant=True, disposition=PermissionDisposition.BLOCKED_AMBIGUOUS),
    "admin:all": _meta("admin:all", "SYSTEM", "LEGACY", "legacy administrative label", system=True, disposition=PermissionDisposition.LEGACY_ONLY),
})


def permission_metadata(permission_id: str) -> PermissionMetadata:
    """Return exact immutable metadata; malformed or unknown identifiers deny."""
    if not isinstance(permission_id, str) or not permission_id or permission_id != permission_id.strip():
        raise ValueError("UNKNOWN_PERMISSION")
    try:
        return _PERMISSIONS[permission_id]
    except KeyError as error:
        raise ValueError("UNKNOWN_PERMISSION") from error


def canonical_permissions() -> bytes:
    """Serialize the immutable canon deterministically as UTF-8 bytes."""
    rows = [{"permission_id": value.permission_id, "namespace": value.namespace, "scope_kind": value.scope_kind, "business_capability": value.business_capability, "tenant_membership_required": value.tenant_membership_required, "system_assignment_required": value.system_assignment_required, "cross_tenant_capable": value.cross_tenant_capable, "financial_execution_capable": value.financial_execution_capable, "deprecated_or_legacy": value.deprecated_or_legacy, "authorizes_by_itself": value.authorizes_by_itself, "disposition": value.disposition.value} for value in _PERMISSIONS.values()]
    return dumps(rows, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


def classify_legacy_permission(permission_id: object) -> PermissionDisposition | None:
    """Classify known legacy/ambiguous identifiers without authorizing."""
    if not isinstance(permission_id, str) or not permission_id or permission_id != permission_id.strip():
        return None
    try:
        return permission_metadata(permission_id).disposition
    except ValueError:
        return None


__all__ = ["PermissionDisposition", "PermissionMetadata", "VERSION", "permission_metadata", "canonical_permissions", "classify_legacy_permission"]

# ARTIFACT: permission_namespace.py
# VERSION: v1.1.0-PERMISSION-NAMESPACE-CANON
# AUTHORITY BOUNDARY: permission vocabulary and scope metadata only
# TENANT POSTURE: tenant descriptors require separately proven ACTIVE membership
# FAIL-CLOSED POSTURE: unknown, malformed, ambiguous, and legacy values never authorize
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
