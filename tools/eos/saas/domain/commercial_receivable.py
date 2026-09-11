"""WILSY OS M11A canonical commercial receivable domain.
TITLE: Typed Platform and Client Commercial Receivable
VERSION: v1.0.0-M11A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable Python-owned commercial obligation and outstanding balance.
ABSOLUTE CANONICAL PATH: tools/eos/saas/domain/commercial_receivable.py
COLLABORATION / OWNERSHIP: SaaS commercial-receivable domain owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11A establishes explicit platform/client receivable truth.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque identifiers; no credentials.
TENANT BOUNDARY: Every receivable is bound to one tenant and invoice family.
AUTHORITY BOUNDARY: Commercial obligation only; no execution or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel owns execution/settlement evidence.
TRANSACTION BOUNDARY: Pure value object; persistence is outside M11A.
FAIL-CLOSED DECLARATION: Invalid money, identity, schema, or fingerprint rejects.
"""
from __future__ import annotations
from typing import Any, cast
from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re

class CommercialReceivableError(ValueError):
    """Raised when a commercial receivable violates its canonical contract."""

class ReceivableFamily(str, Enum):
    """Explicit commercial ledger family; platform and client are distinct."""
    PLATFORM = "PLATFORM"
    CLIENT = "CLIENT"

class ReceivableStatus(str, Enum):
    """Commercial lifecycle status, deliberately excluding paid/settled/executed."""
    OPEN = "OPEN"
    CLOSED_COMMERCIAL = "CLOSED_COMMERCIAL"

_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FIELDS = frozenset({"tenant_id", "receivable_family", "receivable_id", "source_invoice_id", "currency", "original_amount_minor", "adjustment_amount_minor", "outstanding_amount_minor", "source_invoice_fingerprint", "status", "receivable_fingerprint"})

def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise CommercialReceivableError(f"M11A_INVALID_{name.upper()}")
    return value

def _money(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CommercialReceivableError(f"M11A_INVALID_{name.upper()}")
    return value

@dataclass(frozen=True, slots=True)
class CommercialReceivable:
    """Immutable tenant-scoped commercial balance independent of future persistence."""
    tenant_id: str
    receivable_family: ReceivableFamily
    receivable_id: str
    source_invoice_id: str
    currency: str
    original_amount_minor: int
    adjustment_amount_minor: int
    outstanding_amount_minor: int
    source_invoice_fingerprint: str
    status: ReceivableStatus

    def __post_init__(self) -> None:
        _text("tenant_id", self.tenant_id); _text("receivable_id", self.receivable_id); _text("source_invoice_id", self.source_invoice_id)
        if not isinstance(self.receivable_family, ReceivableFamily): raise CommercialReceivableError("M11A_INVALID_FAMILY")
        if not isinstance(self.status, ReceivableStatus): raise CommercialReceivableError("M11A_INVALID_STATUS")
        if not isinstance(self.currency, str) or not re.fullmatch(r"[A-Z]{3}", self.currency): raise CommercialReceivableError("M11A_INVALID_CURRENCY")
        original = _money("original_amount_minor", self.original_amount_minor); adjustment = _money("adjustment_amount_minor", self.adjustment_amount_minor); outstanding = _money("outstanding_amount_minor", self.outstanding_amount_minor)
        lawful = original + adjustment
        if outstanding > lawful: raise CommercialReceivableError("M11A_OUTSTANDING_EXCEEDS_OBLIGATION")
        if self.status is ReceivableStatus.CLOSED_COMMERCIAL and outstanding != 0: raise CommercialReceivableError("M11A_CLOSED_WITH_OUTSTANDING_BALANCE")
        if not isinstance(self.source_invoice_fingerprint, str) or not _SHA3.fullmatch(self.source_invoice_fingerprint): raise CommercialReceivableError("M11A_INVALID_SOURCE_FINGERPRINT")

    @property
    def receivable_fingerprint(self) -> str:
        """Return deterministic SHA3-512 over all economically material fields."""
        return hashlib.sha3_512(self._canonical_bytes(include_fingerprint=False)).hexdigest()

    def _canonical_bytes(self, *, include_fingerprint: bool) -> bytes:
        value = {"tenant_id": self.tenant_id, "receivable_family": self.receivable_family.value, "receivable_id": self.receivable_id, "source_invoice_id": self.source_invoice_id, "currency": self.currency, "original_amount_minor": self.original_amount_minor, "adjustment_amount_minor": self.adjustment_amount_minor, "outstanding_amount_minor": self.outstanding_amount_minor, "source_invoice_fingerprint": self.source_invoice_fingerprint, "status": self.status.value}
        if include_fingerprint: value["receivable_fingerprint"] = self.receivable_fingerprint
        return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact canonical domain schema without transport metadata."""
        return json.loads(self._canonical_bytes(include_fingerprint=True))

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "CommercialReceivable":
        """Hydrate strictly; Mongo `_id`, unknown fields, and bad fingerprints reject."""
        if not isinstance(payload, dict) or set(payload) != _FIELDS or "_id" in payload: raise CommercialReceivableError("M11A_INVALID_SCHEMA")
        try:
            data = cast(dict[str, Any], payload)
            value = cls(tenant_id=data["tenant_id"], receivable_family=ReceivableFamily(data["receivable_family"]), receivable_id=data["receivable_id"], source_invoice_id=data["source_invoice_id"], currency=data["currency"], original_amount_minor=data["original_amount_minor"], adjustment_amount_minor=data["adjustment_amount_minor"], outstanding_amount_minor=data["outstanding_amount_minor"], source_invoice_fingerprint=data["source_invoice_fingerprint"], status=ReceivableStatus(data["status"]))
        except (KeyError, TypeError, ValueError) as error: raise CommercialReceivableError("M11A_INVALID_SCHEMA") from error
        if payload["receivable_fingerprint"] != value.receivable_fingerprint: raise CommercialReceivableError("M11A_FINGERPRINT_MISMATCH")
        return value

# ARTIFACT: commercial_receivable.py
# VERSION: v1.0.0-M11A
# AUTHORITY BOUNDARY: Commercial obligation only; no execution or settlement.
# TENANT POSTURE: Explicit tenant and platform/client family binding.
# FAIL-CLOSED POSTURE: Strict schema, money, and fingerprint validation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
