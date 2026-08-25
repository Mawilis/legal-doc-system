# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – CANONICAL VENDORBILL ACCOUNTS PAYABLE DOMAIN                                                         ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION:        v1.1.0-APPROVAL-PROJECTION-DOMAIN                                                               ║
║ EPITOME:        Tenant-local AP obligation contract; execution and settlement authority remain Kennel EOS-only. ║
║ BIBLICAL ANCHOR: Psalm 1:3 — "And he shall be like a tree planted by the rivers of water..."                  ║
║ ABSOLUTE PATH:  /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/vendor_bill.py                    ║
║ COLLABORATION:  Wilson Khanyezi (Founder/Chief Architect) mandated distinct payable semantics.                 ║
║                 AI Engineering (Codex) established the frozen AP obligation boundary.                           ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Optional
from uuid import uuid4

from .billing import generate_entity_proof


class VendorBillDomainError(ValueError):
    """Raised when a VendorBill violates an immutable AP obligation or state-boundary invariant."""


class VendorBillObligationState(StrEnum):
    """Represents the obligation only; approval, release, execution, and settlement evidence are separate."""
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PARTIALLY_SETTLED = "PARTIALLY_SETTLED"
    SETTLED = "SETTLED"
    VOIDED = "VOIDED"


class VendorBillApprovalState(StrEnum):
    """Represents approval policy truth without implying release, execution, or settlement."""
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def _utc_now() -> datetime:
    """Returns a timezone-aware UTC audit timestamp."""
    return datetime.now(timezone.utc)


def _required_text(value: Any, name: str, maximum: int = 240) -> str:
    """Normalizes an immutable non-sensitive identifier or reference."""
    normalized = str(value or "").strip()
    if not normalized:
        raise VendorBillDomainError(f"{name} is required")
    if len(normalized) > maximum:
        raise VendorBillDomainError(f"{name} exceeds {maximum} characters")
    return normalized


def _optional_text(value: Any, name: str, maximum: int = 240) -> Optional[str]:
    """Normalizes optional evidence references without accepting oversized content."""
    if value is None:
        return None
    normalized = str(value).strip()
    if not normalized:
        return None
    if len(normalized) > maximum:
        raise VendorBillDomainError(f"{name} exceeds {maximum} characters")
    return normalized


def _money(value: Any, name: str, minimum: int = 0) -> int:
    """Accepts only integer minor units and explicitly rejects bools and floating-point money."""
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise VendorBillDomainError(f"{name} must be an integer minor-unit amount of at least {minimum}")
    return value


def _accounting_date(value: Any, name: str) -> date:
    """Requires date-only accounting semantics and refuses timezone-sensitive datetime substitution."""
    if not isinstance(value, date) or isinstance(value, datetime):
        raise VendorBillDomainError(f"{name} must be a date")
    return value


@dataclass(frozen=True)
class VendorBill:
    """Canonical AP obligation; it is never a payment destination, release command, or execution authority."""
    tenant_id: str
    vendor_id: str
    gross_amount_minor: int
    currency: str
    issue_date: date
    due_date: date
    payable_id: str = field(default_factory=lambda: str(uuid4()))
    outstanding_amount_minor: Optional[int] = None
    vendor_reference: Optional[str] = None
    source_document_reference: Optional[str] = None
    received_at: datetime = field(default_factory=_utc_now)
    obligation_state: VendorBillObligationState = VendorBillObligationState.DRAFT
    approval_state: VendorBillApprovalState = VendorBillApprovalState.NOT_REQUIRED
    approval_projection_revision: int = 0
    approval_effective_result_id: Optional[str] = None
    approval_policy_reference: Optional[str] = None
    revision: int = 1
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)
    proof_hash: str = ""

    def __post_init__(self) -> None:
        """Freezes identity, minor-unit money, date semantics, and the separate obligation/approval dimensions."""
        object.__setattr__(self, "tenant_id", _required_text(self.tenant_id, "tenant_id", 128))
        object.__setattr__(self, "vendor_id", _required_text(self.vendor_id, "vendor_id", 80))
        object.__setattr__(self, "payable_id", _required_text(self.payable_id, "payable_id", 80))
        object.__setattr__(self, "currency", _required_text(self.currency, "currency", 3).upper())
        if len(self.currency) != 3 or not self.currency.isalpha():
            raise VendorBillDomainError("currency must be an ISO 4217 alphabetic code")
        gross = _money(self.gross_amount_minor, "gross_amount_minor", 1)
        outstanding = gross if self.outstanding_amount_minor is None else _money(self.outstanding_amount_minor, "outstanding_amount_minor")
        if outstanding > gross:
            raise VendorBillDomainError("outstanding_amount_minor cannot exceed gross_amount_minor")
        object.__setattr__(self, "gross_amount_minor", gross)
        object.__setattr__(self, "outstanding_amount_minor", outstanding)
        object.__setattr__(self, "issue_date", _accounting_date(self.issue_date, "issue_date"))
        object.__setattr__(self, "due_date", _accounting_date(self.due_date, "due_date"))
        if self.due_date < self.issue_date:
            raise VendorBillDomainError("due_date cannot precede issue_date")
        for name in ("received_at", "created_at", "updated_at"):
            value = getattr(self, name)
            if not isinstance(value, datetime) or value.tzinfo is None:
                raise VendorBillDomainError(f"{name} must be a timezone-aware datetime")
        object.__setattr__(self, "vendor_reference", _optional_text(self.vendor_reference, "vendor_reference"))
        object.__setattr__(self, "source_document_reference", _optional_text(self.source_document_reference, "source_document_reference"))
        object.__setattr__(self, "approval_policy_reference", _optional_text(self.approval_policy_reference, "approval_policy_reference"))
        if not isinstance(self.approval_projection_revision, int) or isinstance(self.approval_projection_revision, bool) or self.approval_projection_revision < 0:
            raise VendorBillDomainError("approval_projection_revision must be an integer of at least 0")
        object.__setattr__(self, "approval_effective_result_id", _optional_text(self.approval_effective_result_id, "approval_effective_result_id", 80))
        if self.approval_projection_revision == 0 and self.approval_effective_result_id is not None:
            raise VendorBillDomainError("approval_effective_result_id requires a positive approval_projection_revision")
        if self.approval_projection_revision > 0 and self.approval_effective_result_id is None:
            raise VendorBillDomainError("positive approval_projection_revision requires approval_effective_result_id")
        if not isinstance(self.obligation_state, VendorBillObligationState) or not isinstance(self.approval_state, VendorBillApprovalState):
            raise VendorBillDomainError("VendorBill states must use canonical enums")
        if self.obligation_state is VendorBillObligationState.PARTIALLY_SETTLED and not 0 < outstanding < gross:
            raise VendorBillDomainError("PARTIALLY_SETTLED requires a strictly partial outstanding balance")
        if self.obligation_state is VendorBillObligationState.SETTLED and outstanding != 0:
            raise VendorBillDomainError("SETTLED requires zero outstanding balance")
        if self.obligation_state in {VendorBillObligationState.DRAFT, VendorBillObligationState.OPEN} and outstanding != gross:
            raise VendorBillDomainError("DRAFT and OPEN require the full obligation to remain outstanding")
        if self.obligation_state is VendorBillObligationState.VOIDED and outstanding != 0:
            raise VendorBillDomainError("VOIDED requires zero outstanding balance")
        if not isinstance(self.revision, int) or isinstance(self.revision, bool) or self.revision < 1:
            raise VendorBillDomainError("revision must be an integer of at least 1")
        if not self.proof_hash:
            object.__setattr__(self, "proof_hash", generate_entity_proof(self.evidence_payload(), action="vendor_bill_create"))

    def evidence_payload(self) -> Dict[str, Any]:
        """Returns immutable AP obligation evidence, excluding payment destination and execution details."""
        return {"schema": "WILSY-VENDOR-BILL/V1", "tenant_id": self.tenant_id, "payable_id": self.payable_id, "vendor_id": self.vendor_id, "vendor_reference": self.vendor_reference, "source_document_reference": self.source_document_reference, "currency": self.currency, "gross_amount_minor": self.gross_amount_minor, "outstanding_amount_minor": self.outstanding_amount_minor, "issue_date": self.issue_date.isoformat(), "due_date": self.due_date.isoformat(), "obligation_state": self.obligation_state.value, "approval_state": self.approval_state.value, "revision": self.revision}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the AP obligation without inventing release, execution, payment-destination, or settlement records."""
        return {"tenant_id": self.tenant_id, "tenantId": self.tenant_id, "payable_id": self.payable_id, "payableId": self.payable_id, "vendor_id": self.vendor_id, "vendorId": self.vendor_id, "vendor_reference": self.vendor_reference, "source_document_reference": self.source_document_reference, "currency": self.currency, "gross_amount_minor": self.gross_amount_minor, "outstanding_amount_minor": self.outstanding_amount_minor, "issue_date": self.issue_date.isoformat(), "due_date": self.due_date.isoformat(), "received_at": self.received_at.isoformat(), "obligation_state": self.obligation_state.value, "approval_state": self.approval_state.value, "approval_projection_revision": self.approval_projection_revision, "approval_effective_result_id": self.approval_effective_result_id, "approval_policy_reference": self.approval_policy_reference, "revision": self.revision, "created_at": self.created_at.isoformat(), "updated_at": self.updated_at.isoformat(), "proof_hash": self.proof_hash}
