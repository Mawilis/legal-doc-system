"""Kennel EOS request-scoped executive evidence context boundary.

TITLE: WILSY Executive Context Evidence Engine
VERSION: v1.0.1-WILSY-EXECUTIVE-CONTEXT-EVIDENCE
AUTHORITY: Wilsy OS Core Governance; Kennel EOS / Python sovereign truth
EPITOME: Assembles explicit, already-retrieved, tenant-bound evidence without synthetic enterprise state.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/executive/intelligence/executive_context_engine.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi; Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.1 closes the direct-construction invariant bypass found during independent adversarial review; context validation is canonical for DTO and engine paths.
COMPLIANCE: POPIA section 19, GDPR Article 32, SOC 2 CC7.2; evidence provenance boundary.
SECURITY / PRIVACY POSTURE: Evidence checksums are integrity anchors only and never prove authorization.
TENANT BOUNDARY: Tenant, principal, and request scope derive solely from KernelBootstrapRequest; mixed scopes fail closed.
AUTHORITY BOUNDARY: Evidence assembly only; no authentication, authorization, recommendation, approval, or execution authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha3_512
import hmac
from typing import Iterable

from tools.eos.kernel.domain.kernel_bootstrap_request import KernelBootstrapRequest

VERSION = "v1.0.1-WILSY-EXECUTIVE-CONTEXT-EVIDENCE"
_FORBIDDEN = frozenset({"unknown", "none", "null", "tenant-default"})


class ExecutiveContextError(ValueError):
    """Raised when evidence or authority context is invalid."""


def _validate_context(
    authority: object,
    evidence: object,
    assembled_at: object,
) -> None:
    """Validate the complete immutable context boundary once for all callers."""
    if not isinstance(authority, KernelBootstrapRequest):
        raise ExecutiveContextError("INVALID_REQUEST_TYPE")
    if not isinstance(evidence, tuple):
        raise ExecutiveContextError("INVALID_EVIDENCE_TYPE")
    seen: set[str] = set()
    for item in evidence:
        if not isinstance(item, ExecutiveEvidence):
            raise ExecutiveContextError("INVALID_EVIDENCE_TYPE")
        if item.evidence_id in seen:
            raise ExecutiveContextError("DUPLICATE_EVIDENCE_ID")
        seen.add(item.evidence_id)
        if item.tenant_id != authority.tenant_id:
            raise ExecutiveContextError("TENANT_MISMATCH")
        if item.principal_id != authority.principal_id:
            raise ExecutiveContextError("PRINCIPAL_MISMATCH")
        if item.request_id != authority.request_id:
            raise ExecutiveContextError("REQUEST_MISMATCH")
    _aware(assembled_at, "ASSEMBLED_AT")


def _required(value: object, field: str, *, identity: bool = False) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExecutiveContextError(f"INVALID_EVIDENCE_FIELD:{field}")
    if identity and value.strip().casefold() in _FORBIDDEN:
        raise ExecutiveContextError(f"INVALID_EVIDENCE_FIELD:{field}")
    return value


def _aware(value: object, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ExecutiveContextError(f"INVALID_{field}")
    return value


@dataclass(frozen=True, slots=True)
class ExecutiveEvidence:
    """One caller-supplied, already-retrieved evidence excerpt."""

    evidence_id: str
    tenant_id: str
    principal_id: str
    request_id: str
    source_id: str
    source_type: str
    source_locator: str
    citation_locator: str
    content: str
    content_sha3_512: str
    authorization_receipt_ref: str
    retrieved_at: datetime
    source_version: str | None = None

    def __post_init__(self) -> None:
        for name in ("evidence_id", "tenant_id", "principal_id", "request_id", "source_id", "authorization_receipt_ref"):
            _required(getattr(self, name), name, identity=True)
        for name in ("source_type", "source_locator", "citation_locator", "content"):
            _required(getattr(self, name), name)
        if self.source_version is not None:
            _required(self.source_version, "source_version")
        _aware(self.retrieved_at, "RETRIEVED_AT")
        if not isinstance(self.content_sha3_512, str) or len(self.content_sha3_512) != 128 or any(c not in "0123456789abcdefABCDEF" for c in self.content_sha3_512):
            raise ExecutiveContextError("INVALID_CHECKSUM")
        expected = sha3_512(self.content.encode("utf-8")).hexdigest()
        if not hmac.compare_digest(expected, self.content_sha3_512.lower()):
            raise ExecutiveContextError("INVALID_CHECKSUM")


@dataclass(frozen=True, slots=True)
class ExecutiveContext:
    """Immutable request-scoped evidence context; no synthetic facts."""

    authority: KernelBootstrapRequest
    evidence: tuple[ExecutiveEvidence, ...]
    assembled_at: datetime

    def __post_init__(self) -> None:
        _validate_context(self.authority, self.evidence, self.assembled_at)

    @property
    def tenant_id(self) -> str:
        return self.authority.tenant_id

    @property
    def principal_id(self) -> str:
        return self.authority.principal_id

    @property
    def request_id(self) -> str:
        return self.authority.request_id

    @property
    def correlation_id(self) -> str | None:
        return self.authority.correlation_id

    @property
    def evidence_count(self) -> int:
        return len(self.evidence)


class ExecutiveContextEngine:
    """Stateless assembler bound exclusively to KernelBootstrapRequest."""

    def assemble_context(
        self,
        request: KernelBootstrapRequest,
        evidence: Iterable[ExecutiveEvidence],
        *,
        assembled_at: datetime | None = None,
    ) -> ExecutiveContext:
        """Assemble a tuple-owned, scope-checked evidence context."""
        if not isinstance(request, KernelBootstrapRequest):
            raise ExecutiveContextError("INVALID_REQUEST_TYPE")
        try:
            items = tuple(evidence)
        except TypeError as exc:
            raise ExecutiveContextError("INVALID_EVIDENCE_TYPE") from exc
        timestamp = datetime.now(timezone.utc) if assembled_at is None else _aware(assembled_at, "ASSEMBLED_AT")
        return ExecutiveContext(authority=request, evidence=items, assembled_at=timestamp)


executive_context_engine = ExecutiveContextEngine()


# ARTIFACT: executive_context_engine.py
# VERSION: v1.0.1-WILSY-EXECUTIVE-CONTEXT-EVIDENCE
# AUTHORITY BOUNDARY: explicit evidence assembly only; no authorization or execution.
# TENANT POSTURE: KernelBootstrapRequest-bound and mixed-scope fail closed.
# FAIL-CLOSED POSTURE: malformed evidence, checksum, authority, and scope are rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
