"""WILSY OS M11E2 inbound collection authority domain.
TITLE: Provider-Neutral Inbound Collection Authority
VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable, tenant-scoped authority for one inbound collection against one commercial receivable.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/inbound_collection_authority.py
COLLABORATION / OWNERSHIP: SaaS commercial-collection domain owner; issuance and persistence remain outside this value object.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE adds the exact durable authorization-evidence fingerprint to the immutable semantic authority contract; v1.0.0-M11-R8-R2 established closed CLIENT/PLATFORM source variants and derived SHA3-512 authority identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque identifiers; no credentials or external transport facts.
TENANT BOUNDARY: Authority tenant and source tenant must be identical and are included in the semantic fingerprint.
AUTHORITY BOUNDARY: Immutable inbound collection authorization only; no invoice, receivable, execution, payment, or closure mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns outbound financial execution and settlement evidence.
TRANSACTION BOUNDARY: Pure value object; trusted times and canonical provenance are supplied by the caller.
FAIL-CLOSED DECLARATION: Invalid schema, family pairing, tenant, money, time, or fingerprint data rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, ClassVar, TypeAlias, cast

from .commercial_receivable import ReceivableFamily


VERSION = "v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE"


_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")
_CURRENCY = re.compile(r"^[A-Z]{3}$")


class InboundCollectionAuthorityError(ValueError):
    """Raised when inbound collection authority data violates its contract."""


def _required_text(name: str, value: object) -> str:
    """Validate a required opaque text primitive without inventing a value."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise InboundCollectionAuthorityError(f"M11R8_INVALID_{name.upper()}")
    return value


def _fingerprint_text(name: str, value: object) -> str:
    """Validate an existing lowercase SHA3-512 hexadecimal fingerprint."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise InboundCollectionAuthorityError(f"M11R8_INVALID_{name.upper()}")
    return value


def _aware_utc(name: str, value: object) -> datetime:
    """Require a caller-supplied aware time and canonicalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InboundCollectionAuthorityError(f"M11R8_INVALID_{name.upper()}")
    return value.astimezone(timezone.utc)


def _canonical_json_bytes(value: object) -> bytes:
    """Serialize semantic data deterministically for the authority fingerprint."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class ClientCollectionSource:
    """Immutable CLIENT provenance for a collection authority."""

    tenant_id: str
    client_invoice_id: str
    commercial_receivable_id: str
    commercial_receivable_fingerprint: str
    client_invoice_fingerprint: str
    customer_id: str | None = None

    def __post_init__(self) -> None:
        _required_text("tenant_id", self.tenant_id)
        _required_text("client_invoice_id", self.client_invoice_id)
        _required_text("commercial_receivable_id", self.commercial_receivable_id)
        _fingerprint_text("commercial_receivable_fingerprint", self.commercial_receivable_fingerprint)
        _fingerprint_text("client_invoice_fingerprint", self.client_invoice_fingerprint)
        if self.customer_id is not None:
            _required_text("customer_id", self.customer_id)

    def to_dict(self) -> dict[str, object]:
        """Return the exact CLIENT source payload used by canonical hashing."""
        return {
            "tenant_id": self.tenant_id,
            "client_invoice_id": self.client_invoice_id,
            "commercial_receivable_id": self.commercial_receivable_id,
            "commercial_receivable_fingerprint": self.commercial_receivable_fingerprint,
            "client_invoice_fingerprint": self.client_invoice_fingerprint,
            "customer_id": self.customer_id,
        }


@dataclass(frozen=True, slots=True)
class PlatformCollectionSource:
    """Immutable PLATFORM provenance for a collection authority."""

    tenant_id: str
    platform_invoice_id: str
    commercial_receivable_id: str
    commercial_receivable_fingerprint: str
    platform_invoice_fingerprint: str

    def __post_init__(self) -> None:
        _required_text("tenant_id", self.tenant_id)
        _required_text("platform_invoice_id", self.platform_invoice_id)
        _required_text("commercial_receivable_id", self.commercial_receivable_id)
        _fingerprint_text("commercial_receivable_fingerprint", self.commercial_receivable_fingerprint)
        _fingerprint_text("platform_invoice_fingerprint", self.platform_invoice_fingerprint)

    def to_dict(self) -> dict[str, object]:
        """Return the exact PLATFORM source payload used by canonical hashing."""
        return {
            "tenant_id": self.tenant_id,
            "platform_invoice_id": self.platform_invoice_id,
            "commercial_receivable_id": self.commercial_receivable_id,
            "commercial_receivable_fingerprint": self.commercial_receivable_fingerprint,
            "platform_invoice_fingerprint": self.platform_invoice_fingerprint,
        }


CollectionSource: TypeAlias = ClientCollectionSource | PlatformCollectionSource


@dataclass(frozen=True, slots=True)
class InboundCollectionAuthority:
    """Immutable, provider-neutral authority for one complete collection subject."""

    collection_authority_id: str
    tenant_id: str
    source_authority_kind: ReceivableFamily
    source_authority: CollectionSource
    expected_amount_minor: int
    currency: str
    idempotency_key: str
    issued_by_actor_id: str
    authorization_reference: str
    authorization_evidence_fingerprint: str
    created_at: datetime
    authorized_at: datetime

    _SEMANTIC_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "collection_authority_id",
            "tenant_id",
            "source_authority_kind",
            "source_authority",
            "expected_amount_minor",
            "currency",
            "idempotency_key",
            "issued_by_actor_id",
            "authorization_reference",
            "authorization_evidence_fingerprint",
            "created_at",
            "authorized_at",
        }
    )

    def __post_init__(self) -> None:
        _required_text("collection_authority_id", self.collection_authority_id)
        tenant_id = _required_text("tenant_id", self.tenant_id)
        if not isinstance(self.source_authority_kind, ReceivableFamily):
            raise InboundCollectionAuthorityError("M11R8_INVALID_SOURCE_AUTHORITY_KIND")
        if type(self.source_authority) not in (ClientCollectionSource, PlatformCollectionSource):
            raise InboundCollectionAuthorityError("M11R8_INVALID_SOURCE_AUTHORITY")
        source = cast(CollectionSource, self.source_authority)
        expected_kind = (
            ReceivableFamily.CLIENT
            if type(source) is ClientCollectionSource
            else ReceivableFamily.PLATFORM
        )
        if self.source_authority_kind is not expected_kind:
            raise InboundCollectionAuthorityError("M11R8_SOURCE_FAMILY_TYPE_MISMATCH")
        if source.tenant_id != tenant_id:
            raise InboundCollectionAuthorityError("M11R8_SOURCE_TENANT_MISMATCH")
        if isinstance(self.expected_amount_minor, bool) or not isinstance(self.expected_amount_minor, int) or self.expected_amount_minor <= 0:
            raise InboundCollectionAuthorityError("M11R8_INVALID_EXPECTED_AMOUNT_MINOR")
        if not isinstance(self.currency, str):
            raise InboundCollectionAuthorityError("M11R8_INVALID_CURRENCY")
        currency = self.currency.strip().upper()
        if _CURRENCY.fullmatch(currency) is None:
            raise InboundCollectionAuthorityError("M11R8_INVALID_CURRENCY")
        object.__setattr__(self, "currency", currency)
        if not isinstance(self.idempotency_key, str):
            raise InboundCollectionAuthorityError("M11R8_INVALID_IDEMPOTENCY_KEY")
        idempotency_key = self.idempotency_key.strip()
        if not idempotency_key:
            raise InboundCollectionAuthorityError("M11R8_INVALID_IDEMPOTENCY_KEY")
        object.__setattr__(self, "idempotency_key", idempotency_key)
        _required_text("issued_by_actor_id", self.issued_by_actor_id)
        _required_text("authorization_reference", self.authorization_reference)
        _fingerprint_text("authorization_evidence_fingerprint", self.authorization_evidence_fingerprint)
        object.__setattr__(self, "created_at", _aware_utc("created_at", self.created_at))
        object.__setattr__(self, "authorized_at", _aware_utc("authorized_at", self.authorized_at))

    @property
    def fingerprint(self) -> str:
        """Return lowercase SHA3-512 over every semantic authority field."""
        return hashlib.sha3_512(_canonical_json_bytes(self._semantic_payload())).hexdigest()

    def _semantic_payload(self) -> dict[str, object]:
        """Build the provider-independent payload whose digest is the authority proof."""
        return {
            "collection_authority_id": self.collection_authority_id,
            "tenant_id": self.tenant_id,
            "source_authority_kind": self.source_authority_kind.value,
            "source_authority": self.source_authority.to_dict(),
            "expected_amount_minor": self.expected_amount_minor,
            "currency": self.currency,
            "idempotency_key": self.idempotency_key,
            "issued_by_actor_id": self.issued_by_actor_id,
            "authorization_reference": self.authorization_reference,
            "authorization_evidence_fingerprint": self.authorization_evidence_fingerprint,
            "created_at": self.created_at.isoformat(),
            "authorized_at": self.authorized_at.isoformat(),
        }

    def to_dict(self) -> dict[str, object]:
        """Serialize the strict canonical schema, including the derived fingerprint."""
        payload = self._semantic_payload()
        payload["fingerprint"] = self.fingerprint
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "InboundCollectionAuthority":
        """Hydrate strictly and reject unknown fields or caller-supplied digest drift."""
        expected_fields = set(cls._SEMANTIC_FIELDS) | {"fingerprint"}
        if not isinstance(payload, dict) or set(payload) != expected_fields:
            raise InboundCollectionAuthorityError("M11R8_INVALID_SCHEMA")
        try:
            data = cast(dict[str, Any], payload)
            source_payload = data["source_authority"]
            if not isinstance(source_payload, dict):
                raise InboundCollectionAuthorityError("M11R8_INVALID_SOURCE_AUTHORITY")
            source_data = cast(dict[str, Any], source_payload)
            source_fields = set(source_data)
            if data["source_authority_kind"] == ReceivableFamily.CLIENT.value:
                required_source_fields = set(ClientCollectionSource.__dataclass_fields__)
                if source_fields != required_source_fields:
                    raise InboundCollectionAuthorityError("M11R8_INVALID_SOURCE_SCHEMA")
                source: CollectionSource = ClientCollectionSource(
                    tenant_id=source_data["tenant_id"],
                    client_invoice_id=source_data["client_invoice_id"],
                    commercial_receivable_id=source_data["commercial_receivable_id"],
                    commercial_receivable_fingerprint=source_data["commercial_receivable_fingerprint"],
                    client_invoice_fingerprint=source_data["client_invoice_fingerprint"],
                    customer_id=source_data["customer_id"],
                )
            elif data["source_authority_kind"] == ReceivableFamily.PLATFORM.value:
                required_source_fields = set(PlatformCollectionSource.__dataclass_fields__)
                if source_fields != required_source_fields:
                    raise InboundCollectionAuthorityError("M11R8_INVALID_SOURCE_SCHEMA")
                source = PlatformCollectionSource(
                    tenant_id=source_data["tenant_id"],
                    platform_invoice_id=source_data["platform_invoice_id"],
                    commercial_receivable_id=source_data["commercial_receivable_id"],
                    commercial_receivable_fingerprint=source_data["commercial_receivable_fingerprint"],
                    platform_invoice_fingerprint=source_data["platform_invoice_fingerprint"],
                )
            else:
                raise InboundCollectionAuthorityError("M11R8_INVALID_SOURCE_AUTHORITY_KIND")
            value = cls(
                collection_authority_id=data["collection_authority_id"],
                tenant_id=data["tenant_id"],
                source_authority_kind=ReceivableFamily(data["source_authority_kind"]),
                source_authority=source,
                expected_amount_minor=data["expected_amount_minor"],
                currency=data["currency"],
                idempotency_key=data["idempotency_key"],
                issued_by_actor_id=data["issued_by_actor_id"],
                authorization_reference=data["authorization_reference"],
                authorization_evidence_fingerprint=data["authorization_evidence_fingerprint"],
                created_at=datetime.fromisoformat(cast(str, data["created_at"])),
                authorized_at=datetime.fromisoformat(cast(str, data["authorized_at"])),
            )
        except InboundCollectionAuthorityError:
            raise
        except (KeyError, TypeError, ValueError) as error:
            raise InboundCollectionAuthorityError("M11R8_INVALID_SCHEMA") from error
        if data["fingerprint"] != value.fingerprint:
            raise InboundCollectionAuthorityError("M11R8_FINGERPRINT_MISMATCH")
        return value


__all__ = [
    "VERSION",
    "ClientCollectionSource",
    "CollectionSource",
    "InboundCollectionAuthority",
    "InboundCollectionAuthorityError",
    "PlatformCollectionSource",
]


# ARTIFACT: inbound_collection_authority.py
# VERSION: v1.1.0-M11-R8-R3B-P3-AUTHORIZATION-PROVENANCE
# AUTHORITY BOUNDARY: Provider-neutral inbound collection authority only.
# TENANT POSTURE: Explicit tenant and CLIENT/PLATFORM source binding.
# FAIL-CLOSED POSTURE: Strict immutable schema, family, time, money, authorization provenance, and digest validation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
