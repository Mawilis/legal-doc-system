"""TITLE: WILSY OS Authority Namespace Canon.
VERSION: v1.0.1-AUTHORITY-NAMESPACE-CANON
AUTHORITY: Canonical Python classification of authority namespaces only.
EPITOME: Separates system, tenant, service, domain, and profile concepts before authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/authority_namespace.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.1 preserves immutable namespace metadata and migration-only legacy classification while repairing sovereign version coherence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Unknown and ambiguous values fail closed; no credentials, claims, tenant sentinels, or financial data are accepted.
TENANT BOUNDARY: Namespace metadata never proves membership or tenant authority.
AUTHORITY BOUNDARY: Owns namespace classification only; it does not authenticate, authorize, assign roles, grant permissions, parse JWTs, or transport requests.
FINANCIAL AUTHORITY BOUNDARY: No namespace grants financial execution; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from json import dumps
from types import MappingProxyType
from typing import Final

VERSION = "v1.0.1-AUTHORITY-NAMESPACE-CANON"


class AuthorityNamespace(StrEnum):
    """Closed namespace vocabulary; membership is not authorization or permission."""

    SYSTEM = "SYSTEM"
    TENANT = "TENANT"
    DOMAIN = "DOMAIN"
    PROFILE = "PROFILE"
    SERVICE = "SERVICE"


class PrincipalKind(StrEnum):
    """Human/service distinction; this metadata is not identity proof or authorization."""

    HUMAN = "HUMAN"
    SERVICE = "SERVICE"
    NON_PRINCIPAL_CLASSIFICATION = "NON_PRINCIPAL_CLASSIFICATION"


@dataclass(frozen=True, slots=True)
class NamespaceMetadata:
    """Immutable metadata; capability does not equal permission, admission, or authorization."""

    namespace: AuthorityNamespace
    authority_capable: bool
    principal_kind: PrincipalKind
    system_scope: bool = False
    service_scope: bool = False
    tenant_membership_required: bool = False
    explicit_target_scope_required_for_cross_tenant: bool = False


_METADATA: Final = MappingProxyType({
    AuthorityNamespace.SYSTEM: NamespaceMetadata(AuthorityNamespace.SYSTEM, True, PrincipalKind.HUMAN, system_scope=True, explicit_target_scope_required_for_cross_tenant=True),
    AuthorityNamespace.TENANT: NamespaceMetadata(AuthorityNamespace.TENANT, True, PrincipalKind.HUMAN, tenant_membership_required=True),
    AuthorityNamespace.DOMAIN: NamespaceMetadata(AuthorityNamespace.DOMAIN, False, PrincipalKind.NON_PRINCIPAL_CLASSIFICATION),
    AuthorityNamespace.PROFILE: NamespaceMetadata(AuthorityNamespace.PROFILE, False, PrincipalKind.NON_PRINCIPAL_CLASSIFICATION),
    AuthorityNamespace.SERVICE: NamespaceMetadata(AuthorityNamespace.SERVICE, True, PrincipalKind.SERVICE, service_scope=True),
})

_LEGACY: Final = MappingProxyType({
    "FOUNDER": AuthorityNamespace.SYSTEM, "founder": AuthorityNamespace.SYSTEM,
    "SOVEREIGN": AuthorityNamespace.SYSTEM, "sovereign": AuthorityNamespace.SYSTEM,
    "OMEGA": AuthorityNamespace.SYSTEM, "omega": AuthorityNamespace.SYSTEM,
    "SUPER_ADMIN": AuthorityNamespace.SYSTEM, "super_admin": AuthorityNamespace.SYSTEM,
    "PLATFORM_ADMIN": AuthorityNamespace.SYSTEM, "superadmin": AuthorityNamespace.SYSTEM,
    "tenant_owner": AuthorityNamespace.TENANT, "tenant_admin": AuthorityNamespace.TENANT,
    "tenant_manager": AuthorityNamespace.TENANT, "tenant_auditor": AuthorityNamespace.TENANT,
    "user_admin": AuthorityNamespace.TENANT, "user_manager": AuthorityNamespace.TENANT,
    "user_editor": AuthorityNamespace.TENANT, "user_viewer": AuthorityNamespace.TENANT,
    "OWNER": AuthorityNamespace.TENANT, "MANAGER": AuthorityNamespace.TENANT,
    "VIEWER": AuthorityNamespace.TENANT, "client": AuthorityNamespace.TENANT,
    "guest": AuthorityNamespace.TENANT,
    "lawyer": AuthorityNamespace.DOMAIN, "LAWYER": AuthorityNamespace.DOMAIN,
    "paralegal": AuthorityNamespace.DOMAIN, "arbitrator": AuthorityNamespace.DOMAIN,
    "sheriff": AuthorityNamespace.DOMAIN, "ops": AuthorityNamespace.DOMAIN,
    "staff": AuthorityNamespace.DOMAIN, "STAFF": AuthorityNamespace.DOMAIN,
    "investor": AuthorityNamespace.PROFILE, "investor_relations": AuthorityNamespace.PROFILE,
    "executive": AuthorityNamespace.PROFILE,
})
_AMBIGUOUS: Final[frozenset[str]] = frozenset({"admin", "ADMIN", "ROOT", "SYSTEM", "GLOBAL_ROOT", "WILSY_ROOT", "MASTER", "WILSY_SOVEREIGN_ROOT", "WILSY_GLOBAL_ROOT", "compliance_officer", "TENANT_ADMIN"})


def metadata(namespace: AuthorityNamespace | str) -> NamespaceMetadata:
    """Return metadata for an exact namespace; reject unknown input.

    Parameters: canonical ``AuthorityNamespace`` or exact string. Returns no
    permission or authorization decision and does not prove membership.
    """
    try:
        key = namespace if isinstance(namespace, AuthorityNamespace) else AuthorityNamespace(namespace)
    except (TypeError, ValueError) as exc:
        raise ValueError("UNKNOWN_AUTHORITY_NAMESPACE") from exc
    return _METADATA[key]


def classify_legacy(value: object) -> AuthorityNamespace | None:
    """Classify a legacy value as migration metadata only.

    The result never authorizes, grants permission, creates membership, or proves identity.
    Ambiguous, sentinel, non-string, and unknown values fail closed with ``None``.
    """
    if not isinstance(value, str) or not value or value != value.strip() or value in _AMBIGUOUS:
        return None
    return _LEGACY.get(value)


def canonical_metadata() -> bytes:
    """Return deterministic UTF-8 JSON bytes; never grants permission or authorization."""
    rows = [{"namespace": item.namespace.value, "authority_capable": item.authority_capable, "principal_kind": item.principal_kind.value, "system_scope": item.system_scope, "service_scope": item.service_scope, "tenant_membership_required": item.tenant_membership_required, "explicit_target_scope_required_for_cross_tenant": item.explicit_target_scope_required_for_cross_tenant} for item in _METADATA.values()]
    return dumps(rows, ensure_ascii=True, separators=(",", ":")).encode("utf-8")


__all__ = ["AuthorityNamespace", "PrincipalKind", "NamespaceMetadata", "VERSION", "metadata", "classify_legacy", "canonical_metadata"]

# ARTIFACT: authority_namespace.py
# VERSION: v1.0.1-AUTHORITY-NAMESPACE-CANON
# AUTHORITY BOUNDARY: immutable namespace classification only; no authentication or authorization
# TENANT POSTURE: namespace metadata never proves membership or tenant authority
# FAIL-CLOSED POSTURE: unknown, ambiguous, sentinel, and malformed inputs are non-authoritative
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
