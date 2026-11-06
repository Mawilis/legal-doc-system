"""Immutable partial and cumulative platform-invoice settlement allocation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import re


class PlatformInvoiceSettlementAllocationError(ValueError):
    """Invalid or divergent allocation evidence."""


@dataclass(frozen=True, slots=True)
class PlatformInvoiceSettlementAllocation:
    tenant_id: str
    allocation_id: str
    observation_id: str
    observation_fingerprint: str
    execution_truth_id: str
    invoice_id: str
    invoice_evidence_fingerprint: str
    currency: str
    amount_minor: int
    cumulative_paid_minor: int
    outstanding_minor: int
    allocation_sequence: int
    allocated_at: datetime
    allocation_status: str

    def __post_init__(self) -> None:
        for name in ("tenant_id", "allocation_id", "observation_id", "execution_truth_id", "invoice_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise PlatformInvoiceSettlementAllocationError("ALLOCATION_IDENTITY_INVALID")
        for name in ("observation_fingerprint", "invoice_evidence_fingerprint"):
            if re.fullmatch(r"[0-9a-f]{128}", getattr(self, name) or "") is None:
                raise PlatformInvoiceSettlementAllocationError("ALLOCATION_FINGERPRINT_INVALID")
        if not isinstance(self.currency, str) or re.fullmatch(r"[A-Z]{3}", self.currency) is None:
            raise PlatformInvoiceSettlementAllocationError("ALLOCATION_CURRENCY_INVALID")
        for name in ("amount_minor", "cumulative_paid_minor", "outstanding_minor", "allocation_sequence"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise PlatformInvoiceSettlementAllocationError("ALLOCATION_AMOUNT_INVALID")
        if self.amount_minor <= 0 or self.allocation_sequence <= 0:
            raise PlatformInvoiceSettlementAllocationError("ALLOCATION_AMOUNT_INVALID")
        if self.cumulative_paid_minor < self.amount_minor:
            raise PlatformInvoiceSettlementAllocationError("ALLOCATION_CUMULATIVE_INVALID")
        if self.outstanding_minor < 0 or self.allocation_status not in {"PARTIAL", "FINAL"}:
            raise PlatformInvoiceSettlementAllocationError("ALLOCATION_STATE_INVALID")
        if (self.allocation_status == "FINAL") != (self.outstanding_minor == 0):
            raise PlatformInvoiceSettlementAllocationError("ALLOCATION_FINALITY_INVALID")
        if not isinstance(self.allocated_at, datetime) or self.allocated_at.tzinfo is None:
            raise PlatformInvoiceSettlementAllocationError("ALLOCATION_TIMESTAMP_INVALID")

    @property
    def fingerprint(self) -> str:
        payload = asdict(self)
        payload["allocated_at"] = self.allocated_at.astimezone(timezone.utc).isoformat()
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["allocated_at"] = self.allocated_at.astimezone(timezone.utc).isoformat()
        payload["allocation_fingerprint"] = self.fingerprint
        return payload

    @classmethod
    def from_dict(cls, payload: dict) -> "PlatformInvoiceSettlementAllocation":
        data = {key: value for key, value in payload.items() if key not in {"_id", "allocation_fingerprint"}}
        if isinstance(data.get("allocated_at"), str):
            data["allocated_at"] = datetime.fromisoformat(data["allocated_at"])
        value = cls(**data)
        if payload.get("allocation_fingerprint") != value.fingerprint:
            raise PlatformInvoiceSettlementAllocationError("ALLOCATION_FINGERPRINT_MISMATCH")
        return value
