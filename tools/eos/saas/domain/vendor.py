# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – TENANT-LOCAL VENDOR IDENTITY DOMAIN                                                                   ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION:        v1.0.0-AP-DOMAIN-FREEZE                                                                         ║
║ EPITOME:        Immutable, tenant-isolated counterparty identity for future Accounts Payable obligations.       ║
║                 It identifies a vendor; it never stores a payment destination or executes settlement.           ║
║ BIBLICAL ANCHOR: Psalm 1:3 — "And he shall be like a tree planted by the rivers of water..."                  ║
║ ABSOLUTE PATH:  /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/vendor.py                         ║
║ COLLABORATION:  Wilson Khanyezi (Founder/Chief Architect) mandated a Kennel-owned AP foundation.                ║
║                 AI Engineering (Codex) implemented the first isolated artifact after domain freeze.             ║
║ CHANGE RECORD:  2026-08-25 — Initial vendor identity; no payable, route, registry, or payment mutation added. ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from .billing import generate_entity_proof


class VendorDomainError(ValueError):
    """Raised when a vendor identity violates tenant isolation or immutable-identity invariants."""


def _utc_now() -> datetime:
    """Returns the canonical UTC timestamp used by the vendor identity evidence envelope."""
    return datetime.now(timezone.utc)


def _required_text(value: Any, field_name: str, maximum: int = 240) -> str:
    """Normalizes a required identity field and rejects empty or overlong values deterministically."""
    normalized = str(value or "").strip()
    if not normalized:
        raise VendorDomainError(f"{field_name} is required")
    if len(normalized) > maximum:
        raise VendorDomainError(f"{field_name} exceeds {maximum} characters")
    return normalized


def _optional_text(value: Any, field_name: str, maximum: int = 240) -> Optional[str]:
    """Normalizes optional vendor metadata while rejecting oversized identity values."""
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if len(normalized) > maximum:
        raise VendorDomainError(f"{field_name} exceeds {maximum} characters")
    return normalized


@dataclass(frozen=True)
class VendorIdentity:
    """Represents one tenant-local legal counterparty without banking or settlement credentials.

    @property vendor_id: Immutable opaque system identity, not a display-number convention.
    @property tenant_id: Tenant authority boundary; records cannot be read or mutated across it.
    @property legal_name: Counterparty legal/business identity captured for future payable evidence.
    @property payment_destination_ref: Explicitly absent by design; payment destination belongs to Kennel execution.
    @collaboration: Future AP obligations reference this identity but must snapshot relevant counterparty fields.
    """

    tenant_id: str
    legal_name: str
    vendor_id: str = field(default_factory=lambda: str(uuid4()))
    trading_name: Optional[str] = None
    tax_identifier: Optional[str] = None
    registration_identifier: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    country_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    revision: int = 1
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)
    proof_hash: str = ""

    def __post_init__(self) -> None:
        """Enforces immutable tenant-local identity and seals its canonical public state."""
        object.__setattr__(self, "tenant_id", _required_text(self.tenant_id, "tenant_id", 128))
        object.__setattr__(self, "vendor_id", _required_text(self.vendor_id, "vendor_id", 80))
        object.__setattr__(self, "legal_name", _required_text(self.legal_name, "legal_name"))
        object.__setattr__(self, "trading_name", _optional_text(self.trading_name, "trading_name"))
        object.__setattr__(self, "tax_identifier", _optional_text(self.tax_identifier, "tax_identifier", 128))
        object.__setattr__(self, "registration_identifier", _optional_text(self.registration_identifier, "registration_identifier", 128))
        object.__setattr__(self, "email", _optional_text(self.email, "email", 320))
        object.__setattr__(self, "phone", _optional_text(self.phone, "phone", 64))
        country_code = _optional_text(self.country_code, "country_code", 3)
        object.__setattr__(self, "country_code", country_code.upper() if country_code else None)
        if self.country_code and len(self.country_code) != 2:
            raise VendorDomainError("country_code must be ISO-3166 alpha-2 when supplied")
        if not isinstance(self.metadata, dict):
            raise VendorDomainError("metadata must be an object")
        if int(self.revision) < 1:
            raise VendorDomainError("revision must be at least 1")
        object.__setattr__(self, "revision", int(self.revision))
        object.__setattr__(self, "metadata", dict(self.metadata))
        if not self.proof_hash:
            object.__setattr__(self, "proof_hash", generate_entity_proof(self.evidence_payload(), action="vendor_identity_create"))

    def evidence_payload(self) -> Dict[str, Any]:
        """Returns material vendor identity fields for the existing SHA3-512 evidence generator."""
        return {
            "schema": "WILSY-VENDOR-IDENTITY/V1",
            "tenant_id": self.tenant_id,
            "vendor_id": self.vendor_id,
            "legal_name": self.legal_name,
            "trading_name": self.trading_name,
            "tax_identifier": self.tax_identifier,
            "registration_identifier": self.registration_identifier,
            "country_code": self.country_code,
            "revision": self.revision,
        }

    def assert_tenant_access(self, tenant_id: str) -> None:
        """Rejects cross-tenant access before a future registry or API can expose vendor identity."""
        if _required_text(tenant_id, "tenant_id", 128) != self.tenant_id:
            raise VendorDomainError("vendor identity is outside the requesting tenant boundary")

    def revise(self, tenant_id: str, expected_revision: int, **changes: Any) -> "VendorIdentity":
        """Returns a new evidence-sealed revision after optimistic-concurrency and immutability checks.

        The immutable vendor and tenant identifiers cannot change. Payment-destination-like keys are refused,
        ensuring this counterparty record cannot become a secret-bearing settlement store.
        """
        self.assert_tenant_access(tenant_id)
        if int(expected_revision) != self.revision:
            raise VendorDomainError("vendor revision conflict")
        forbidden = {"vendor_id", "tenant_id", "payment_destination_ref", "bank_account", "account_number", "card_number", "secret", "token"}
        illegal = forbidden.intersection(changes)
        if illegal:
            raise VendorDomainError(f"immutable or sensitive vendor fields cannot be revised: {', '.join(sorted(illegal))}")
        allowed = {"legal_name", "trading_name", "tax_identifier", "registration_identifier", "email", "phone", "country_code", "metadata"}
        unknown = set(changes).difference(allowed)
        if unknown:
            raise VendorDomainError(f"unsupported vendor fields: {', '.join(sorted(unknown))}")
        revised = replace(self, **changes, revision=self.revision + 1, updated_at=_utc_now(), proof_hash="")
        return revised

    def to_dict(self) -> Dict[str, Any]:
        """Serializes a vendor identity without payment credentials or mutable execution state."""
        return {
            "vendor_id": self.vendor_id,
            "vendorId": self.vendor_id,
            "tenant_id": self.tenant_id,
            "tenantId": self.tenant_id,
            "legal_name": self.legal_name,
            "legalName": self.legal_name,
            "trading_name": self.trading_name,
            "tradingName": self.trading_name,
            "tax_identifier": self.tax_identifier,
            "registration_identifier": self.registration_identifier,
            "email": self.email,
            "phone": self.phone,
            "country_code": self.country_code,
            "metadata": dict(self.metadata),
            "revision": self.revision,
            "proof_hash": self.proof_hash,
            "proofHash": self.proof_hash,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

