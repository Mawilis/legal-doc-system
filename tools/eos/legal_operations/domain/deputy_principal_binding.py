"""Canonical principal-to-deputy identity binding for Legal Operations.

TITLE: WILSY OS Deputy Principal Identity Binding
VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING
AUTHORITY: Immutable Legal Operations identity-link evidence only.
EPITOME: Bind one explicit authenticated principal identifier to one canonical
         tenant-scoped Deputy value and its immutable P1 fingerprint without
         granting tenant membership, DEPUTY role, queue access, service command,
         profile, browser, AI, billing, payment, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/deputy_principal_binding.py
COLLABORATION / OWNERSHIP: P1 owns Deputy truth; IAM owns principal lifecycle,
                            membership, business role, and authorization role;
                            L8-6B owns only their proven identity relation.
                            Persistence, HTTP admission, personal queues, mobile
                            projection, and WILSY AI remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING
           establishes an immutable factory-derived principal/deputy relation
           carrying exact tenant, deputy, sheriff-office, Deputy fingerprint,
           binding timestamp/reference, and deterministic SHA3-512 fingerprint.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque principal/deputy/office identifiers only;
                             no credentials, tokens, badge expansion, profile,
                             geolocation, provider, payment, or AI content.
TENANT BOUNDARY: Tenant, deputy_id, sheriff_office_id, and deputy_fingerprint
                 are derived exclusively from one canonical P1 Deputy instance.
AUTHORITY BOUNDARY: Identity linkage only. A binding is not authentication,
                    membership, DEPUTY role assignment, authorization, queue
                    visibility, lifecycle command authority, or service proof.
FINANCIAL AUTHORITY BOUNDARY: No invoice, payment, execution, or settlement
                              semantics; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable value construction; no I/O or transaction.
FAIL-CLOSED DECLARATION: Malformed principal, non-canonical Deputy runtime type,
                         invalid timestamp/reference, tenant/deputy provenance
                         drift, or fingerprint mismatch rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy


VERSION: Final[str] = "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING"
SCHEMA: Final[str] = "WILSY-LEGAL-OPERATIONS-DEPUTY-PRINCIPAL-BINDING/V1"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class DeputyPrincipalBindingError(ValueError):
    """Stable fail-closed L8-6B identity-binding value failure."""

    def __init__(self, code: str) -> None:
        """Create one bounded identity-binding validation code."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable binding error while retaining the technical cause."""
    error = DeputyPrincipalBindingError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one canonical opaque identifier without normalization."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"L8_6B_{name.upper()}_INVALID")
    return cast(str, value)


def _timestamp(value: object) -> datetime:
    """Require one timezone-aware binding timestamp."""
    if not isinstance(value, datetime):
        _fail("L8_6B_BOUND_AT_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        _fail("L8_6B_BOUND_AT_INVALID")
    return value


def _text(value: object) -> str:
    """Require one bounded non-empty binding evidence reference."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 512
    ):
        _fail("L8_6B_EVIDENCE_REFERENCE_INVALID")
    return value


def _sha3(payload: dict[str, object]) -> str:
    """Return lowercase SHA3-512 over deterministic canonical JSON."""
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True, init=False)
class DeputyPrincipalBinding:
    """Immutable proven identity relation between one principal and one Deputy.

    Construction is factory-only from an exact canonical :class:`Deputy`.
    Tenant, deputy identity, sheriff-office identity, and Deputy fingerprint are
    derived from that P1 value. The caller may provide only the principal
    identity plus binding evidence/time. This value grants no IAM, service,
    queue, mobile, AI, billing, payment, execution, or settlement authority.
    """

    tenant_id: str
    principal_id: str
    deputy_id: str
    sheriff_office_id: str
    deputy_fingerprint: str
    bound_at: datetime
    evidence_reference: str

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Reject documentary construction; use :meth:`from_deputy`."""
        _fail("L8_6B_FACTORY_REQUIRED")

    @classmethod
    def from_deputy(
        cls,
        *,
        principal_id: str,
        deputy: Deputy,
        bound_at: datetime,
        evidence_reference: str,
    ) -> "DeputyPrincipalBinding":
        """Derive one binding from exact canonical Deputy evidence.

        This factory validates only immutable identity-link shape. It does not
        prove principal lifecycle, tenant membership, business role, DEPUTY
        assignment, or caller authorization; the L8-6B orchestration gate owns
        those independent current-authority checks before persistence.
        """
        if type(deputy) is not Deputy:
            _fail("L8_6B_DEPUTY_REQUIRED")
        try:
            deputy.__post_init__()
        except Exception as error:
            _fail("L8_6B_DEPUTY_INVALID", error)

        principal = _identity("principal_id", principal_id)
        timestamp = _timestamp(bound_at)
        reference = _text(evidence_reference)

        value = cast(Any, object.__new__(cls))
        object.__setattr__(value, "tenant_id", deputy.tenant_id)
        object.__setattr__(value, "principal_id", principal)
        object.__setattr__(value, "deputy_id", deputy.deputy_id)
        object.__setattr__(value, "sheriff_office_id", deputy.sheriff_office_id)
        object.__setattr__(value, "deputy_fingerprint", deputy.fingerprint)
        object.__setattr__(value, "bound_at", timestamp)
        object.__setattr__(value, "evidence_reference", reference)
        value._validate()
        return cast("DeputyPrincipalBinding", value)

    def _validate(self) -> None:
        """Revalidate immutable fields without deriving any external authority."""
        _identity("tenant_id", self.tenant_id)
        _identity("principal_id", self.principal_id)
        _identity("deputy_id", self.deputy_id)
        _identity("sheriff_office_id", self.sheriff_office_id)
        if (
            not isinstance(self.deputy_fingerprint, str)
            or re.fullmatch(r"[0-9a-f]{128}", self.deputy_fingerprint) is None
        ):
            _fail("L8_6B_DEPUTY_FINGERPRINT_INVALID")
        _timestamp(self.bound_at)
        _text(self.evidence_reference)

    def _payload(self) -> dict[str, object]:
        """Return exact fingerprint payload without derived fingerprint itself."""
        self._validate()
        return {
            "schema": SCHEMA,
            "version": VERSION,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "deputy_id": self.deputy_id,
            "sheriff_office_id": self.sheriff_office_id,
            "deputy_fingerprint": self.deputy_fingerprint,
            "bound_at": self.bound_at.isoformat(),
            "evidence_reference": self.evidence_reference,
        }

    @property
    def fingerprint(self) -> str:
        """Return deterministic SHA3-512 binding evidence identity."""
        return _sha3(self._payload())

    def to_dict(self) -> dict[str, object]:
        """Serialize exact binding evidence with deterministic fingerprint."""
        payload = self._payload()
        payload["fingerprint"] = self.fingerprint
        return payload


__all__ = [
    "SCHEMA",
    "VERSION",
    "DeputyPrincipalBinding",
    "DeputyPrincipalBindingError",
]


# ARTIFACT: deputy_principal_binding.py
# VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING
# AUTHORITY BOUNDARY: immutable principal-to-canonical-Deputy identity-link evidence only
# TENANT POSTURE: tenant/deputy/office/fingerprint are factory-derived from exact P1 Deputy
# FAIL-CLOSED POSTURE: direct construction, malformed identity/time/reference, or provenance drift rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
