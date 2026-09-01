"""WILSY OS — canonical, authority-bearing kernel bootstrap request.

TITLE: Kernel Bootstrap Request Domain Authority
VERSION: v1.0.0-WILSY-KERNEL-BOOTSTRAP-REQUEST
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable tenant, principal, and request identity boundary for kernel bootstrap.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kernel/domain/kernel_bootstrap_request.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
UPDATED: 2026-08-29
SECURITY / PRIVACY: References authenticated authority only; stores no credentials, claims, or secrets.
TENANT BOUNDARY: Tenant-scoped and fail-closed; no implicit tenant or system mode.
AUTHORITY BOUNDARY: Caller-authenticated identity and request references only.
PROVIDER / RUNTIME BOUNDARY: Provider-neutral and free of live runtime handles.
FINANCIAL AUTHORITY BOUNDARY: No financial, provider, settlement, or ledger authority.
CHANGELOG: v1.0.0 establishes the first immutable bootstrap authority contract.

WILSY OWNS BUSINESS TRUTH. EOS ALL THE WAY.
"""

from __future__ import annotations

from dataclasses import dataclass


class KernelBootstrapRequestError(ValueError):
    """Raised when bootstrap authority is absent, invalid, or a sentinel."""


_FORBIDDEN_REFERENCES = frozenset({"unknown", "none", "null", "tenant-default"})


def _required_reference(value: str, field_name: str) -> str:
    """Validate one immutable authority reference without normalizing ownership."""
    if not isinstance(value, str):
        raise KernelBootstrapRequestError(f"{field_name} must be a non-empty string")
    cleaned = value.strip()
    if not cleaned or cleaned.casefold() in _FORBIDDEN_REFERENCES:
        raise KernelBootstrapRequestError(f"{field_name} is invalid")
    return cleaned


def _optional_reference(value: str | None, field_name: str) -> str | None:
    """Validate an optional correlation reference when supplied."""
    if value is None:
        return None
    return _required_reference(value, field_name)


@dataclass(frozen=True, slots=True)
class KernelBootstrapRequest:
    """Immutable tenant-scoped authority required before kernel bootstrap.

    ``tenant_id`` and ``principal_id`` reference authenticated authority owned
    by the identity subsystem. ``request_id`` identifies caller intent. The
    optional ``correlation_id`` remains distinct from both request and runtime
    execution identities. No session or execution identity is generated here.
    """

    tenant_id: str
    principal_id: str
    request_id: str
    correlation_id: str | None = None

    def __post_init__(self) -> None:
        """Fail closed while preserving the caller's explicit references."""
        object.__setattr__(self, "tenant_id", _required_reference(self.tenant_id, "tenant_id"))
        object.__setattr__(self, "principal_id", _required_reference(self.principal_id, "principal_id"))
        object.__setattr__(self, "request_id", _required_reference(self.request_id, "request_id"))
        object.__setattr__(self, "correlation_id", _optional_reference(self.correlation_id, "correlation_id"))

    def to_dict(self) -> dict[str, str | None]:
        """Return deterministic authority material in stable field order."""
        return {
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
        }


# ARTIFACT: kernel_bootstrap_request.py
# VERSION: v1.0.0-WILSY-KERNEL-BOOTSTRAP-REQUEST
# AUTHORITY BOUNDARY: immutable tenant/principal/request references only.
# TENANT POSTURE: tenant-scoped and fail-closed; no implicit tenant or system mode.
# FAIL-CLOSED POSTURE: missing, blank, and migration-sentinel references are rejected.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel financial truth remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
