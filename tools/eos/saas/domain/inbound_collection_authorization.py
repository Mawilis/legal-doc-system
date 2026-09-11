"""WILSY OS M11 R8-R3B-P4 typed inbound collection authorization domain.
TITLE: Typed Inbound Collection Authorization Evidence
VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, provider-neutral evidence binding one canonical principal and tenant to one exact client or platform receivable collection authorization.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/inbound_collection_authorization.py
COLLABORATION / OWNERSHIP: SaaS authorization-domain owner; future issuance and registry owners consume this value contract.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE adds mandatory, fingerprinted expiry-policy provenance while preserving policy-neutral domain validation; v1.0.0-M11-R8-R3B-P4 established typed CLIENT/PLATFORM subjects, upstream tenant-authorization provenance, bounded expiry, idempotency, and complete SHA3-512 authorization evidence identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque identifiers and canonical fingerprints only; no credentials, provider transport, or invoice-model imports.
TENANT BOUNDARY: Top-level tenant and typed subject tenant must match exactly; no tenant resolution occurs here.
AUTHORITY BOUNDARY: Immutable issued authorization evidence only; construction is not current validity, persistence, consumption, payment, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns outbound financial execution and settlement evidence.
TRANSACTION BOUNDARY: Pure value objects; callers supply trusted provenance and timestamps, while future issuers own rereads and transactions.
FAIL-CLOSED DECLARATION: Invalid identity, operation, family/subject pairing, provenance, money, currency, time, schema, or digest rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, ClassVar, TypeAlias, cast

from .commercial_receivable import ReceivableFamily


VERSION = "v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE"
OPERATION = "authorize_inbound_collection"
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")


class InboundCollectionAuthorizationError(ValueError):
    """Raised when typed inbound collection authorization violates its contract."""


def _required_text(name: str, value: object) -> str:
    """Require a non-empty canonical opaque identifier without inventing it."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise InboundCollectionAuthorizationError(f"M11R8_P4_INVALID_{name.upper()}")
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require an existing lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise InboundCollectionAuthorizationError(f"M11R8_P4_INVALID_{name.upper()}")
    return value


def _amount(name: str, value: object) -> int:
    """Require a strictly positive integer minor-unit amount."""
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise InboundCollectionAuthorizationError(f"M11R8_P4_INVALID_{name.upper()}")
    return value


def _currency(value: object) -> str:
    """Canonicalize a provider-neutral three-letter currency code."""
    if not isinstance(value, str):
        raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_CURRENCY")
    canonical = value.strip().upper()
    if _CURRENCY.fullmatch(canonical) is None:
        raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_CURRENCY")
    return canonical


def _aware_utc(name: str, value: object) -> datetime:
    """Require a caller-supplied aware timestamp and canonicalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InboundCollectionAuthorizationError(f"M11R8_P4_INVALID_{name.upper()}")
    return value.astimezone(timezone.utc)


def _timestamp(value: datetime) -> str:
    """Return the stable UTC representation used by the evidence digest."""
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _canonical_bytes(value: object) -> bytes:
    """Serialize semantic evidence deterministically as compact sorted UTF-8 JSON."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True, slots=True)
class ClientInboundCollectionAuthorizationSubject:
    """Immutable CLIENT receivable subject with invoice and receivable provenance."""

    tenant_id: str
    commercial_receivable_id: str
    client_invoice_id: str
    commercial_receivable_fingerprint: str
    client_invoice_fingerprint: str
    expected_outstanding_amount_minor: int
    currency: str
    customer_id: str | None = None

    def __post_init__(self) -> None:
        _required_text("tenant_id", self.tenant_id)
        _required_text("commercial_receivable_id", self.commercial_receivable_id)
        _required_text("client_invoice_id", self.client_invoice_id)
        _fingerprint("commercial_receivable_fingerprint", self.commercial_receivable_fingerprint)
        _fingerprint("client_invoice_fingerprint", self.client_invoice_fingerprint)
        _amount("expected_outstanding_amount_minor", self.expected_outstanding_amount_minor)
        object.__setattr__(self, "currency", _currency(self.currency))
        if self.customer_id is not None:
            _required_text("customer_id", self.customer_id)

    def to_dict(self) -> dict[str, object]:
        """Return the complete typed CLIENT subject payload."""
        return {
            "tenant_id": self.tenant_id,
            "commercial_receivable_id": self.commercial_receivable_id,
            "client_invoice_id": self.client_invoice_id,
            "commercial_receivable_fingerprint": self.commercial_receivable_fingerprint,
            "client_invoice_fingerprint": self.client_invoice_fingerprint,
            "expected_outstanding_amount_minor": self.expected_outstanding_amount_minor,
            "currency": self.currency,
            "customer_id": self.customer_id,
        }


@dataclass(frozen=True, slots=True)
class PlatformInboundCollectionAuthorizationSubject:
    """Immutable PLATFORM receivable subject with invoice and receivable provenance."""

    tenant_id: str
    commercial_receivable_id: str
    platform_invoice_id: str
    commercial_receivable_fingerprint: str
    platform_invoice_fingerprint: str
    expected_outstanding_amount_minor: int
    currency: str

    def __post_init__(self) -> None:
        _required_text("tenant_id", self.tenant_id)
        _required_text("commercial_receivable_id", self.commercial_receivable_id)
        _required_text("platform_invoice_id", self.platform_invoice_id)
        _fingerprint("commercial_receivable_fingerprint", self.commercial_receivable_fingerprint)
        _fingerprint("platform_invoice_fingerprint", self.platform_invoice_fingerprint)
        _amount("expected_outstanding_amount_minor", self.expected_outstanding_amount_minor)
        object.__setattr__(self, "currency", _currency(self.currency))

    def to_dict(self) -> dict[str, object]:
        """Return the complete typed PLATFORM subject payload."""
        return {
            "tenant_id": self.tenant_id,
            "commercial_receivable_id": self.commercial_receivable_id,
            "platform_invoice_id": self.platform_invoice_id,
            "commercial_receivable_fingerprint": self.commercial_receivable_fingerprint,
            "platform_invoice_fingerprint": self.platform_invoice_fingerprint,
            "expected_outstanding_amount_minor": self.expected_outstanding_amount_minor,
            "currency": self.currency,
        }


AuthorizationSubject: TypeAlias = (
    ClientInboundCollectionAuthorizationSubject | PlatformInboundCollectionAuthorizationSubject
)


@dataclass(frozen=True, slots=True)
class InboundCollectionAuthorization:
    """Immutable issued authorization evidence, distinct from current lifecycle state."""

    inbound_collection_authorization_id: str
    tenant_id: str
    principal_id: str
    operation: str
    subject_authority_kind: ReceivableFamily
    subject_authority: AuthorizationSubject
    tenant_authorization_decision_id: str
    tenant_authorization_evidence_fingerprint: str
    idempotency_key: str
    authorized_at: datetime
    expires_at: datetime
    expiry_policy_version: str

    OPERATION: ClassVar[str] = OPERATION

    def __post_init__(self) -> None:
        _required_text("inbound_collection_authorization_id", self.inbound_collection_authorization_id)
        tenant_id = _required_text("tenant_id", self.tenant_id)
        _required_text("principal_id", self.principal_id)
        if self.operation != OPERATION:
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_OPERATION")
        if not isinstance(self.subject_authority_kind, ReceivableFamily):
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_SUBJECT_AUTHORITY_KIND")
        if type(self.subject_authority) not in (
            ClientInboundCollectionAuthorizationSubject,
            PlatformInboundCollectionAuthorizationSubject,
        ):
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_SUBJECT_AUTHORITY")
        subject = cast(AuthorizationSubject, self.subject_authority)
        expected_kind = (
            ReceivableFamily.CLIENT
            if type(subject) is ClientInboundCollectionAuthorizationSubject
            else ReceivableFamily.PLATFORM
        )
        if self.subject_authority_kind is not expected_kind:
            raise InboundCollectionAuthorizationError("M11R8_P4_SUBJECT_FAMILY_TYPE_MISMATCH")
        if subject.tenant_id != tenant_id:
            raise InboundCollectionAuthorizationError("M11R8_P4_SUBJECT_TENANT_MISMATCH")
        _required_text("tenant_authorization_decision_id", self.tenant_authorization_decision_id)
        _fingerprint(
            "tenant_authorization_evidence_fingerprint",
            self.tenant_authorization_evidence_fingerprint,
        )
        if not isinstance(self.idempotency_key, str):
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_IDEMPOTENCY_KEY")
        idempotency_key = self.idempotency_key.strip()
        if not idempotency_key:
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_IDEMPOTENCY_KEY")
        object.__setattr__(self, "idempotency_key", idempotency_key)
        _required_text("expiry_policy_version", self.expiry_policy_version)
        authorized_at = _aware_utc("authorized_at", self.authorized_at)
        expires_at = _aware_utc("expires_at", self.expires_at)
        if expires_at <= authorized_at:
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_EXPIRY_ORDER")
        object.__setattr__(self, "authorized_at", authorized_at)
        object.__setattr__(self, "expires_at", expires_at)

    def _semantic_payload(self) -> dict[str, object]:
        """Build every semantic authorization field except its derived digest."""
        return {
            "inbound_collection_authorization_id": self.inbound_collection_authorization_id,
            "tenant_id": self.tenant_id,
            "principal_id": self.principal_id,
            "operation": self.operation,
            "subject_authority_kind": self.subject_authority_kind.value,
            "subject_authority": self.subject_authority.to_dict(),
            "tenant_authorization_decision_id": self.tenant_authorization_decision_id,
            "tenant_authorization_evidence_fingerprint": self.tenant_authorization_evidence_fingerprint,
            "idempotency_key": self.idempotency_key,
            "authorized_at": _timestamp(self.authorized_at),
            "expires_at": _timestamp(self.expires_at),
            "expiry_policy_version": self.expiry_policy_version,
        }

    @property
    def authorization_evidence_fingerprint(self) -> str:
        """Return SHA3-512 over the complete semantic authorization payload."""
        return hashlib.sha3_512(_canonical_bytes(self._semantic_payload())).hexdigest()

    def to_dict(self) -> dict[str, object]:
        """Serialize semantic evidence plus its derived integrity fingerprint."""
        payload = self._semantic_payload()
        payload["authorization_evidence_fingerprint"] = self.authorization_evidence_fingerprint
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "InboundCollectionAuthorization":
        """Hydrate strictly and recompute the caller-supplied digest before acceptance."""
        expected = {
            "inbound_collection_authorization_id",
            "tenant_id",
            "principal_id",
            "operation",
            "subject_authority_kind",
            "subject_authority",
            "tenant_authorization_decision_id",
            "tenant_authorization_evidence_fingerprint",
            "idempotency_key",
            "authorized_at",
            "expires_at",
            "expiry_policy_version",
            "authorization_evidence_fingerprint",
        }
        if not isinstance(payload, dict) or set(payload) != expected:
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_SCHEMA")
        try:
            data = cast(dict[str, Any], payload)
            raw_subject = data["subject_authority"]
            if not isinstance(raw_subject, dict):
                raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_SUBJECT_AUTHORITY")
            subject_data = cast(dict[str, Any], raw_subject)
            if data["subject_authority_kind"] == ReceivableFamily.CLIENT.value:
                subject_fields = set(ClientInboundCollectionAuthorizationSubject.__dataclass_fields__)
                if set(subject_data) != subject_fields:
                    raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_CLIENT_SUBJECT_SCHEMA")
                subject: AuthorizationSubject = ClientInboundCollectionAuthorizationSubject(**subject_data)
            elif data["subject_authority_kind"] == ReceivableFamily.PLATFORM.value:
                subject_fields = set(PlatformInboundCollectionAuthorizationSubject.__dataclass_fields__)
                if set(subject_data) != subject_fields:
                    raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_PLATFORM_SUBJECT_SCHEMA")
                subject = PlatformInboundCollectionAuthorizationSubject(**subject_data)
            else:
                raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_SUBJECT_AUTHORITY_KIND")
            authorized_at = data["authorized_at"]
            expires_at = data["expires_at"]
            if not isinstance(authorized_at, str) or not isinstance(expires_at, str):
                raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_SCHEMA")
            value = cls(
                inbound_collection_authorization_id=data["inbound_collection_authorization_id"],
                tenant_id=data["tenant_id"],
                principal_id=data["principal_id"],
                operation=data["operation"],
                subject_authority_kind=ReceivableFamily(data["subject_authority_kind"]),
                subject_authority=subject,
                tenant_authorization_decision_id=data["tenant_authorization_decision_id"],
                tenant_authorization_evidence_fingerprint=data["tenant_authorization_evidence_fingerprint"],
                idempotency_key=data["idempotency_key"],
                authorized_at=datetime.fromisoformat(authorized_at),
                expires_at=datetime.fromisoformat(expires_at),
                expiry_policy_version=data["expiry_policy_version"],
            )
        except InboundCollectionAuthorizationError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise InboundCollectionAuthorizationError("M11R8_P4_INVALID_SCHEMA") from error
        if data["authorization_evidence_fingerprint"] != value.authorization_evidence_fingerprint:
            raise InboundCollectionAuthorizationError("M11R8_P4_FINGERPRINT_MISMATCH")
        return value


__all__ = [
    "AuthorizationSubject",
    "ClientInboundCollectionAuthorizationSubject",
    "InboundCollectionAuthorization",
    "InboundCollectionAuthorizationError",
    "OPERATION",
    "PlatformInboundCollectionAuthorizationSubject",
    "ReceivableFamily",
    "VERSION",
]


# ARTIFACT: inbound_collection_authorization.py
# VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE
# AUTHORITY BOUNDARY: Immutable typed authorization evidence only.
# TENANT POSTURE: Exact tenant/principal/subject binding; no membership resolution.
# FAIL-CLOSED POSTURE: Strict operation, family, provenance, expiry, idempotency, immutability, and SHA3-512 validation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
