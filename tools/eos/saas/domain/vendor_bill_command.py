"""Immutable committed VendorBill mutation identity for the durable command ledger."""
from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Optional

SCHEMA = "WILSY-VENDOR-BILL-COMMAND/V1"
VERSION = "v1.0.0-VENDORBILL-COMMAND-LEDGER-DOMAIN"
class VendorBillCommandDomainError(ValueError): pass
class VendorBillCommandType(StrEnum):
    OPEN_BILL = "OPEN_BILL"
    PROJECT_FINANCIAL_APPROVAL_RESULT = "PROJECT_FINANCIAL_APPROVAL_RESULT"
class VendorBillCommandOutcome(StrEnum): COMMITTED = "COMMITTED"
def _text(v: Any, n: str, max_len: int = 128) -> str:
    if not isinstance(v, str) or not v.strip() or len(v.strip()) > max_len: raise VendorBillCommandDomainError(f"{n} is invalid")
    return v.strip()
def _revision(v: Any, n: str, minimum: int) -> int:
    if not isinstance(v, int) or isinstance(v, bool) or v < minimum: raise VendorBillCommandDomainError(f"{n} is invalid")
    return v
@dataclass(frozen=True)
class VendorBillCommand:
    tenant_id: str; payable_id: str; idempotency_key: str; command_sequence: int; command_type: VendorBillCommandType; command_fingerprint: str; committed_outcome: VendorBillCommandOutcome; committed_at: datetime; obligation_revision_before: int; obligation_revision_after: int; approval_projection_revision_before: int; approval_projection_revision_after: int; effective_result_id: Optional[str] = None
    def __post_init__(self) -> None:
        for n in ("tenant_id", "payable_id", "idempotency_key"): object.__setattr__(self, n, _text(getattr(self, n), n))
        object.__setattr__(self, "command_sequence", _revision(self.command_sequence, "command_sequence", 1)); object.__setattr__(self, "obligation_revision_before", _revision(self.obligation_revision_before, "obligation_revision_before", 1)); object.__setattr__(self, "obligation_revision_after", _revision(self.obligation_revision_after, "obligation_revision_after", 1)); object.__setattr__(self, "approval_projection_revision_before", _revision(self.approval_projection_revision_before, "approval_projection_revision_before", 0)); object.__setattr__(self, "approval_projection_revision_after", _revision(self.approval_projection_revision_after, "approval_projection_revision_after", 0))
        if not isinstance(self.command_type, VendorBillCommandType) or not isinstance(self.committed_outcome, VendorBillCommandOutcome) or not isinstance(self.committed_at, datetime) or self.committed_at.tzinfo is None: raise VendorBillCommandDomainError("command enums/timestamp are invalid")
        object.__setattr__(self, "committed_at", self.committed_at.astimezone(timezone.utc))
        if not isinstance(self.command_fingerprint, str) or re.fullmatch(r"[0-9a-f]{128}", self.command_fingerprint) is None: raise VendorBillCommandDomainError("command_fingerprint is invalid")
        result = None if self.effective_result_id is None else _text(self.effective_result_id, "effective_result_id", 80); object.__setattr__(self, "effective_result_id", result)
        if self.command_type is VendorBillCommandType.OPEN_BILL and (self.obligation_revision_after != self.obligation_revision_before + 1 or self.approval_projection_revision_after != self.approval_projection_revision_before or result is not None): raise VendorBillCommandDomainError("OPEN_BILL invariants are invalid")
        if self.command_type is VendorBillCommandType.PROJECT_FINANCIAL_APPROVAL_RESULT and (self.obligation_revision_after != self.obligation_revision_before or self.approval_projection_revision_after != self.approval_projection_revision_before + 1 or result is None): raise VendorBillCommandDomainError("projection invariants are invalid")
    def to_persistence_dict(self) -> dict[str, Any]:
        return {"schema": SCHEMA, "tenant_id": self.tenant_id, "payable_id": self.payable_id, "idempotency_key": self.idempotency_key, "command_sequence": self.command_sequence, "command_type": self.command_type.value, "command_fingerprint": self.command_fingerprint, "committed_outcome": self.committed_outcome.value, "committed_at": self.committed_at.isoformat(), "obligation_revision_before": self.obligation_revision_before, "obligation_revision_after": self.obligation_revision_after, "approval_projection_revision_before": self.approval_projection_revision_before, "approval_projection_revision_after": self.approval_projection_revision_after, "effective_result_id": self.effective_result_id}
    @classmethod
    def from_persistence_dict(cls, payload: Mapping[str, Any]) -> "VendorBillCommand":
        required = {"schema", "tenant_id", "payable_id", "idempotency_key", "command_sequence", "command_type", "command_fingerprint", "committed_outcome", "committed_at", "obligation_revision_before", "obligation_revision_after", "approval_projection_revision_before", "approval_projection_revision_after", "effective_result_id"}
        if not isinstance(payload, Mapping) or set(payload) != required or payload.get("schema") != SCHEMA: raise VendorBillCommandDomainError("invalid persisted VendorBill command")
        try: return cls(tenant_id=payload["tenant_id"], payable_id=payload["payable_id"], idempotency_key=payload["idempotency_key"], command_sequence=payload["command_sequence"], command_type=VendorBillCommandType(payload["command_type"]), command_fingerprint=payload["command_fingerprint"], committed_outcome=VendorBillCommandOutcome(payload["committed_outcome"]), committed_at=datetime.fromisoformat(payload["committed_at"]), obligation_revision_before=payload["obligation_revision_before"], obligation_revision_after=payload["obligation_revision_after"], approval_projection_revision_before=payload["approval_projection_revision_before"], approval_projection_revision_after=payload["approval_projection_revision_after"], effective_result_id=payload["effective_result_id"])
        except (KeyError, TypeError, ValueError) as error: raise VendorBillCommandDomainError("invalid persisted VendorBill command") from error
