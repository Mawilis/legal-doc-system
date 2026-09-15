# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – SOVEREIGN BILLING DOMAIN MODEL (PYTHON) – CLIENT COMMERCIAL EVIDENCE + DUAL CASE                    ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/saas/domain/billing.py                                                             ║
║ VERSION:        v1.5.0-P6E-EXACT-CLIENT-INVOICE-MONEY                                                        ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                     ║
║ EPITOME:        LineItem accepts snake_case + camelCase. Invoice amount=subtotal, total=subtotal+tax.        ║
║                 Ledger MUST display tax-inclusive total (SA VAT / commercial invoice law).                    ║
║                 PlatformInvoice exposes deterministic, settlement-excluded commercial-release evidence.      ║
║ CLASSIFICATION: Production Artifact                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                               ║
║   2026-09-15 v1.5.0-P6E-EXACT-CLIENT-INVOICE-MONEY – Added immutable integer minor-unit ClientInvoice money  ║
║                authority, deterministic fingerprinting, and fail-closed legacy projections.                  ║
║   2026-09-09 v1.4.0-M11-R8-R3B-P6E-R1-CLIENT-EVIDENCE – Added optional, persisted, versioned deterministic     ║
║                ClientInvoice commercial-content evidence while preserving legacy proof_hash correlation.      ║
║   2026-08-24 v1.2.1-PYLANCE-METADATA – Fix ledger R0/ex-tax: from_dict reads unit_price/tax_amount;    ║
║                post_init sets amount (ex-VAT), tax_amount, total (incl VAT); dual-write total_amount.         ║
║   2026-09-04 v1.3.0-PLATFORM-INVOICE-COMMERCIAL-RELEASE-EVIDENCE – Added canonical tax-inclusive payable  ║
║                minor-unit evidence and deterministic versioned commercial-release payload/fingerprint,       ║
║                excluding settlement and execution truth.                                                     ║
║   2026-08-21 v1.1.0-ORDER-FIELDS – order_number & purchase_order.                                            ║
║   2026-08-20 v1.0.2-PROOF-GEN-FIX – Removed redundant enum .value in generate_proof.                         ║
║   2026-08-20 v1.0.0-INSTITUTIONAL – Initial creation.                                                        ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001 │ Tax invoices must show VAT-inclusive total  ║
║ CRYPTO:        SHA3‑512 proof generation                                                                     ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import Any, Dict, List, Optional, Mapping, Tuple
from .money import SUPPORTED_CURRENCY_EXPONENTS, to_minor_units


CLIENT_COMMERCIAL_EVIDENCE_VERSION = "WILSY-CLIENT-INVOICE-COMMERCIAL-EVIDENCE/V1"
_CLIENT_COMMERCIAL_EVIDENCE_SCHEMA = CLIENT_COMMERCIAL_EVIDENCE_VERSION
CLIENT_INVOICE_EXACT_MONEY_VERSION = "WILSY-CLIENT-INVOICE-EXACT-MONEY/V1"


def _canonical_rate(value: float) -> str:
    """Return a deterministic decimal representation for a line tax rate."""
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("CLIENT_INVOICE_TAX_RATE_INVALID") from exc
    if not decimal_value.is_finite():
        raise ValueError("CLIENT_INVOICE_TAX_RATE_INVALID")
    rendered = format(decimal_value, "f").rstrip("0").rstrip(".")
    return rendered or "0"


def parse_datetime(val: Any) -> Optional[datetime]:
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _f(val: Any, default: float = 0.0) -> float:
    try:
        if val is None or val == "":
            return default
        return float(val)
    except (TypeError, ValueError):
        return default


def _i(val: Any, default: int = 1) -> int:
    try:
        if val is None or val == "":
            return default
        return max(1, int(val))
    except (TypeError, ValueError):
        return default


def _pick(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return default

def _as_dict(val: Any) -> Dict[str, Any]:
    """Always return a plain dict — never None (Pylance / dataclass safe)."""
    if isinstance(val, dict):
        return dict(val)
    return {}



def generate_entity_proof(entity_dict: Dict[str, Any], action: str = "save", metadata: Optional[Dict[str, Any]] = None) -> str:
    payload = {
        "action": action,
        "entity": entity_dict,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }
    sorted_payload = {k: payload[k] for k in sorted(payload.keys())}
    data = hashlib.sha3_512()
    data.update(json.dumps(sorted_payload, sort_keys=True, default=str).encode("utf-8"))
    return data.hexdigest().upper()


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    UNPAID = "unpaid"
    OVERDUE = "overdue"
    VOID = "void"
    CANCELLED = "cancelled"
    PENDING = "pending"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    CRYPTO = "crypto"
    MANUAL = "manual"
    OTHER = "other"


class InvoiceType(str, Enum):
    PLATFORM = "platform"
    CLIENT = "client"


class TaxType(str, Enum):
    VAT = "vat"
    GST = "gst"
    NONE = "none"


class CollectionMethod(str, Enum):
    CHARGE_AUTOMATICALLY = "charge_automatically"
    SEND_INVOICE = "send_invoice"


@dataclass(frozen=True)
class LineItem:
    description: str
    amount: float
    quantity: int = 1
    unit_price: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    discount: float = 0.0
    currency: str = "ZAR"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # Dual-case for Node + Kennel consumers
        return {
            "description": self.description,
            "amount": float(self.amount),
            "quantity": int(self.quantity),
            "unit_price": float(self.unit_price),
            "unitPrice": float(self.unit_price),
            "tax_rate": float(self.tax_rate),
            "taxRate": float(self.tax_rate),
            "tax_amount": float(self.tax_amount),
            "taxAmount": float(self.tax_amount),
            "discount": float(self.discount),
            "currency": self.currency,
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineItem":
        if not isinstance(data, dict):
            data = {}
        qty = _i(_pick(data, "quantity", "qty"), 1)
        unit = _f(_pick(data, "unit_price", "unitPrice"), 0.0)
        # amount is tax-exclusive line total (qty × unit − discount)
        raw_amount = _pick(data, "amount", "line_total", "lineTotal")
        if raw_amount is not None:
            amount = _f(raw_amount, 0.0)
        else:
            amount = round(qty * unit, 2)
        if unit <= 0 and amount > 0 and qty > 0:
            unit = round(amount / qty, 2)
        tax_rate = _f(_pick(data, "tax_rate", "taxRate"), 0.0)
        tax_amount = _f(_pick(data, "tax_amount", "taxAmount"), 0.0)
        # Derive tax if rate present but tax_amount missing (client snake_case was dropped before)
        if tax_amount <= 0 and tax_rate > 0 and amount > 0:
            tax_amount = round(amount * tax_rate, 2)
        discount = _f(_pick(data, "discount"), 0.0)
        return cls(
            description=str(_pick(data, "description", "desc") or "Service"),
            amount=float(amount),
            quantity=qty,
            unit_price=float(unit),
            tax_rate=float(tax_rate),
            tax_amount=float(tax_amount),
            discount=float(discount),
            currency=str(_pick(data, "currency") or "ZAR"),
            metadata=_as_dict(data.get("metadata")),
        )


@dataclass(frozen=True)
class ClientInvoiceExactMoneyLine:
    """Immutable exact-money line; all monetary authority is integer minor units."""

    description: str
    quantity: int
    unit_price_minor: int
    amount_minor: int
    tax_amount_minor: int
    discount_minor: int
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("CLIENT_INVOICE_EXACT_LINE_DESCRIPTION_REQUIRED")
        if not isinstance(self.currency, str) or self.currency not in SUPPORTED_CURRENCY_EXPONENTS:
            raise ValueError("CLIENT_INVOICE_EXACT_LINE_CURRENCY_INVALID")
        for name in ("quantity", "unit_price_minor", "amount_minor", "tax_amount_minor", "discount_minor"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"CLIENT_INVOICE_EXACT_{name.upper()}_INVALID")
        if self.quantity <= 0:
            raise ValueError("CLIENT_INVOICE_EXACT_QUANTITY_INVALID")
        expected = self.quantity * self.unit_price_minor - self.discount_minor
        if expected < 0 or expected != self.amount_minor:
            raise ValueError("CLIENT_INVOICE_EXACT_LINE_ARITHMETIC_INVALID")

    def to_dict(self) -> Dict[str, Any]:
        """Return deterministic canonical line evidence."""
        return {
            "description": self.description,
            "quantity": self.quantity,
            "unit_price_minor": self.unit_price_minor,
            "amount_minor": self.amount_minor,
            "tax_amount_minor": self.tax_amount_minor,
            "discount_minor": self.discount_minor,
            "currency": self.currency,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ClientInvoiceExactMoneyLine":
        """Hydrate one line with an exact key set; extra or missing fields reject."""
        if not isinstance(data, Mapping):
            raise ValueError("CLIENT_INVOICE_EXACT_LINE_INVALID")
        required = {"description", "quantity", "unit_price_minor", "amount_minor", "tax_amount_minor", "discount_minor", "currency"}
        if set(data) != required:
            raise ValueError("CLIENT_INVOICE_EXACT_LINE_SCHEMA_INVALID")
        return cls(**{key: data[key] for key in required})


@dataclass(frozen=True)
class ClientInvoiceExactMoney:
    """Canonical immutable ClientInvoice money authority independent of legacy floats."""

    currency: str
    subtotal_minor: int
    tax_amount_minor: int
    total_minor: int
    lines: Tuple[ClientInvoiceExactMoneyLine, ...]
    exact_money_version: str = CLIENT_INVOICE_EXACT_MONEY_VERSION
    exact_money_fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.exact_money_version != CLIENT_INVOICE_EXACT_MONEY_VERSION:
            raise ValueError("CLIENT_INVOICE_EXACT_MONEY_VERSION_UNSUPPORTED")
        if not isinstance(self.currency, str) or self.currency not in SUPPORTED_CURRENCY_EXPONENTS:
            raise ValueError("CLIENT_INVOICE_EXACT_CURRENCY_INVALID")
        if not isinstance(self.lines, tuple) or not self.lines:
            raise ValueError("CLIENT_INVOICE_EXACT_LINES_REQUIRED")
        for name in ("subtotal_minor", "tax_amount_minor", "total_minor"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"CLIENT_INVOICE_EXACT_{name.upper()}_INVALID")
        if any(line.currency != self.currency for line in self.lines):
            raise ValueError("CLIENT_INVOICE_EXACT_LINE_CURRENCY_MISMATCH")
        if sum(line.amount_minor for line in self.lines) != self.subtotal_minor:
            raise ValueError("CLIENT_INVOICE_EXACT_SUBTOTAL_ARITHMETIC_INVALID")
        if sum(line.tax_amount_minor for line in self.lines) != self.tax_amount_minor:
            raise ValueError("CLIENT_INVOICE_EXACT_TAX_ARITHMETIC_INVALID")
        if self.subtotal_minor + self.tax_amount_minor != self.total_minor:
            raise ValueError("CLIENT_INVOICE_EXACT_TOTAL_ARITHMETIC_INVALID")
        expected = self.compute_fingerprint()
        if self.exact_money_fingerprint:
            if not isinstance(self.exact_money_fingerprint, str) or len(self.exact_money_fingerprint) != 128 or self.exact_money_fingerprint != expected:
                raise ValueError("CLIENT_INVOICE_EXACT_FINGERPRINT_INVALID")
        else:
            object.__setattr__(self, "exact_money_fingerprint", expected)

    def _fingerprint_payload(self) -> Dict[str, Any]:
        return {
            "exact_money_version": self.exact_money_version,
            "currency": self.currency,
            "subtotal_minor": self.subtotal_minor,
            "tax_amount_minor": self.tax_amount_minor,
            "total_minor": self.total_minor,
            "lines": [line.to_dict() for line in self.lines],
        }

    def compute_fingerprint(self) -> str:
        """Return deterministic lowercase SHA3-512 exact-money evidence."""
        raw = json.dumps(self._fingerprint_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha3_512(raw).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the complete durable exact-money envelope."""
        return {**self._fingerprint_payload(), "exact_money_fingerprint": self.exact_money_fingerprint}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ClientInvoiceExactMoney":
        """Strictly hydrate persisted exact-money evidence."""
        if not isinstance(data, Mapping):
            raise ValueError("CLIENT_INVOICE_EXACT_MONEY_SCHEMA_INVALID")
        required = {"exact_money_version", "currency", "subtotal_minor", "tax_amount_minor", "total_minor", "lines", "exact_money_fingerprint"}
        if set(data) != required or not isinstance(data["lines"], list):
            raise ValueError("CLIENT_INVOICE_EXACT_MONEY_SCHEMA_INVALID")
        lines = tuple(ClientInvoiceExactMoneyLine.from_dict(item) for item in data["lines"])
        return cls(
            currency=data["currency"],
            subtotal_minor=data["subtotal_minor"],
            tax_amount_minor=data["tax_amount_minor"],
            total_minor=data["total_minor"],
            lines=lines,
            exact_money_version=data["exact_money_version"],
            exact_money_fingerprint=data["exact_money_fingerprint"],
        )

    def to_legacy_projection(self) -> Dict[str, Any]:
        """Project exact integers to legacy floats; projection is never authority."""
        exponent = SUPPORTED_CURRENCY_EXPONENTS[self.currency]
        scale = Decimal(10) ** exponent
        def major(value: int) -> float:
            return float(Decimal(value) / scale)
        return {
            "amount": major(self.subtotal_minor),
            "tax_amount": major(self.tax_amount_minor),
            "total": major(self.total_minor),
            "line_items": [
                {
                    "description": line.description,
                    "quantity": line.quantity,
                    "unit_price": major(line.unit_price_minor),
                    "amount": major(line.amount_minor),
                    "tax_amount": major(line.tax_amount_minor),
                    "discount": major(line.discount_minor),
                    "currency": line.currency,
                }
                for line in self.lines
            ],
        }


@dataclass(frozen=True)
class Payment:
    invoice_id: str
    amount: float
    currency: str
    payment_id: str = field(default_factory=lambda: f"WILSYPAY-{uuid.uuid4().hex[:8].upper()}")
    status: PaymentStatus = PaymentStatus.PENDING
    method: PaymentMethod = PaymentMethod.OTHER
    external_reference: Optional[str] = None
    paid_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    refund_amount: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    proof_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.proof_hash:
            object.__setattr__(self, "proof_hash", self.generate_proof())

    def generate_proof(self, action: str = "save", metadata: Optional[Dict[str, Any]] = None) -> str:
        state = self.to_dict()
        return generate_entity_proof(state, action=action, metadata=metadata)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "paymentId": self.payment_id,
            "payment_id": self.payment_id,
            "invoiceId": self.invoice_id,
            "invoice_id": self.invoice_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status.value,
            "method": self.method.value,
            "externalReference": self.external_reference,
            "paidAt": self.paid_at.isoformat() if self.paid_at else None,
            "refundedAt": self.refunded_at.isoformat() if self.refunded_at else None,
            "refundAmount": self.refund_amount,
            "metadata": self.metadata,
            "proofHash": self.proof_hash,
            "proof_hash": self.proof_hash,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payment":
        inv = _pick(data, "invoiceId", "invoice_id")
        return cls(
            invoice_id=str(inv),
            amount=_f(data.get("amount")),
            currency=str(data.get("currency") or "ZAR"),
            payment_id=str(_pick(data, "paymentId", "payment_id") or f"WILSYPAY-{uuid.uuid4().hex[:8].upper()}"),
            status=PaymentStatus(str(data.get("status", "pending")).lower()),
            method=PaymentMethod(str(data.get("method", "other")).lower()),
            external_reference=data.get("externalReference") or data.get("external_reference"),
            paid_at=parse_datetime(data.get("paidAt") or data.get("paid_at")),
            refunded_at=parse_datetime(data.get("refundedAt") or data.get("refunded_at")),
            refund_amount=_f(data.get("refundAmount") or data.get("refund_amount")),
            metadata=_as_dict(data.get("metadata")),
            proof_hash=str(data.get("proofHash") or data.get("proof_hash") or ""),
            created_at=parse_datetime(data.get("createdAt") or data.get("created_at")) or datetime.now(timezone.utc),
            updated_at=parse_datetime(data.get("updatedAt") or data.get("updated_at")) or datetime.now(timezone.utc),
        )


@dataclass(frozen=True)
class BaseInvoice:
    tenant_id: str
    invoice_id: str = field(default_factory=lambda: f"WILSYINV-{uuid.uuid4().hex[:8].upper()}")
    customer_id: Optional[str] = None
    status: InvoiceStatus = InvoiceStatus.DRAFT
    amount: float = 0.0          # subtotal EXCLUDING tax
    tax_amount: float = 0.0      # VAT/GST total
    total: float = 0.0           # TAX-INCLUSIVE payable (legal invoice total)
    amount_paid: float = 0.0     # Settled total sourced from succeeded payment records
    outstanding_amount: float = 0.0  # Remaining tax-inclusive balance
    currency: str = "ZAR"
    line_items: List[LineItem] = field(default_factory=list)
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    void_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    collection_method: CollectionMethod = CollectionMethod.SEND_INVOICE
    payment_terms_days: int = 30
    tax_type: TaxType = TaxType.VAT
    seller_jurisdiction: str = "ZA"
    customer_jurisdiction: str = "ZA"
    billing_mode: str = "PLATFORM"
    metadata: Dict[str, Any] = field(default_factory=dict)
    proof_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    order_number: Optional[str] = None
    purchase_order: Optional[str] = None

    def __post_init__(self) -> None:
        """
        Canonical math (South African tax invoice posture):
          amount     = sum(line.amount)           # exclusive of tax
          tax_amount = sum(line.tax_amount)       # VAT on exclusive lines
          total      = amount + tax_amount        # inclusive — ledger MUST show this
        Always recompute when line_items present so snake_case tax never silently zeros.
        """
        if self.line_items:
            subtotal = round(sum(float(item.amount) for item in self.line_items), 2)
            tax = round(sum(float(item.tax_amount) for item in self.line_items), 2)
            # If lines have rate but zero tax_amount, derive (belt-and-braces)
            if tax <= 0:
                derived = 0.0
                for item in self.line_items:
                    if item.tax_rate and item.tax_rate > 0 and item.amount > 0:
                        derived += round(item.amount * item.tax_rate, 2)
                tax = round(derived, 2)
            object.__setattr__(self, "amount", subtotal)
            object.__setattr__(self, "tax_amount", tax)
            object.__setattr__(self, "total", round(subtotal + tax, 2))
        elif self.total == 0 and self.amount > 0:
            object.__setattr__(self, "total", round(float(self.amount) + float(self.tax_amount or 0), 2))
        if not self.proof_hash:
            object.__setattr__(self, "proof_hash", self.generate_proof())

    def generate_proof(self, action: str = "save", metadata: Optional[Dict[str, Any]] = None) -> str:
        state = self.to_dict()
        for f in ["issued_at", "due_at", "paid_at", "void_at", "created_at", "updated_at"]:
            if state.get(f) and isinstance(state[f], datetime):
                state[f] = state[f].isoformat()
        return generate_entity_proof(state, action=action, metadata=metadata)

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseInvoice":
        raise NotImplementedError


def _base_financial_dict(inv: BaseInvoice) -> Dict[str, Any]:
    """Shared dual-case financial fields — ledger reads total / total_amount / totalAmount."""
    return {
        "amount": float(inv.amount),
        "subtotal": float(inv.amount),
        "tax_amount": float(inv.tax_amount),
        "taxAmount": float(inv.tax_amount),
        "total": float(inv.total),
        "total_amount": float(inv.total),
        "totalAmount": float(inv.total),
        "grand_total": float(inv.total),
        "grandTotal": float(inv.total),
        "amount_paid": float(inv.amount_paid),
        "amountPaid": float(inv.amount_paid),
        "outstanding_amount": float(inv.outstanding_amount),
        "outstandingAmount": float(inv.outstanding_amount),
    }


def _parse_line_items(data: Dict[str, Any]) -> List[LineItem]:
    raw = data.get("lineItems") or data.get("line_items") or data.get("items") or []
    if not isinstance(raw, list):
        return []
    return [LineItem.from_dict(li) for li in raw if isinstance(li, dict)]


def _parse_status(data: Dict[str, Any]) -> InvoiceStatus:
    raw = str(_pick(data, "status", "invoice_status", "invoiceStatus") or "draft").lower()
    try:
        return InvoiceStatus(raw)
    except ValueError:
        # tolerate OPEN-style already lower
        aliases = {"issued": InvoiceStatus.OPEN, "sent": InvoiceStatus.OPEN, "active": InvoiceStatus.OPEN}
        return aliases.get(raw, InvoiceStatus.DRAFT)


@dataclass(frozen=True)
class PlatformInvoice(BaseInvoice):
    invoice_type: InvoiceType = InvoiceType.PLATFORM
    subscription_id: Optional[str] = None
    plan_id: Optional[str] = None
    plan_name: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "invoiceId": self.invoice_id,
            "invoice_id": self.invoice_id,
            "tenantId": self.tenant_id,
            "tenant_id": self.tenant_id,
            "customerId": self.customer_id,
            "customer_id": self.customer_id,
            "status": self.status.value,
            **_base_financial_dict(self),
            "currency": self.currency,
            "lineItems": [li.to_dict() for li in self.line_items],
            "line_items": [li.to_dict() for li in self.line_items],
            "issuedAt": self.issued_at.isoformat() if self.issued_at else None,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "dueAt": self.due_at.isoformat() if self.due_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "paidAt": self.paid_at.isoformat() if self.paid_at else None,
            "voidAt": self.void_at.isoformat() if self.void_at else None,
            "cancellationReason": self.cancellation_reason,
            "collectionMethod": self.collection_method.value,
            "paymentTermsDays": self.payment_terms_days,
            "taxType": self.tax_type.value,
            "sellerJurisdiction": self.seller_jurisdiction,
            "customerJurisdiction": self.customer_jurisdiction,
            "billingMode": self.billing_mode,
            "metadata": self.metadata,
            "proofHash": self.proof_hash,
            "proof_hash": self.proof_hash,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "invoiceType": self.invoice_type.value,
            "subscriptionId": self.subscription_id,
            "planId": self.plan_id,
            "planName": self.plan_name,
            "periodStart": self.period_start.isoformat() if self.period_start else None,
            "periodEnd": self.period_end.isoformat() if self.period_end else None,
            "orderNumber": self.order_number,
            "order_number": self.order_number,
            "purchaseOrder": self.purchase_order,
            "purchase_order": self.purchase_order,
        }
        return base

    def commercial_release_evidence_payload(self) -> Dict[str, Any]:
        """Return deterministic payable-liability evidence, excluding settlement state."""
        return {
            "schema": "WILSY-PLATFORM-INVOICE-COMMERCIAL-RELEASE-EVIDENCE/V1",
            "tenant_id": self.tenant_id,
            "invoice_id": self.invoice_id,
            "release_amount_minor": self.release_amount_minor,
            "currency": self.currency,
            "amount": self.amount,
            "tax_amount": self.tax_amount,
            "tax_type": self.tax_type.value,
            "line_items": [item.to_dict() for item in self.line_items],
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "payment_terms_days": self.payment_terms_days,
            "collection_method": self.collection_method.value,
            "billing_mode": self.billing_mode,
            "seller_jurisdiction": self.seller_jurisdiction,
            "customer_jurisdiction": self.customer_jurisdiction,
            "subscription_id": self.subscription_id,
            "plan_id": self.plan_id,
            "order_number": self.order_number,
            "purchase_order": self.purchase_order,
        }

    @property
    def release_amount_minor(self) -> int:
        """Convert the tax-inclusive payable total using canonical money precision."""
        return to_minor_units(self.total, self.currency)

    @property
    def commercial_release_evidence_fingerprint(self) -> str:
        """Return deterministic lowercase SHA3-512 over canonical evidence payload."""
        raw = json.dumps(self.commercial_release_evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        return hashlib.sha3_512(raw).hexdigest()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlatformInvoice":
        if not isinstance(data, dict):
            raise ValueError("PlatformInvoice.from_dict requires a dict")
        line_items = _parse_line_items(data)
        tenant = str(_pick(data, "tenantId", "tenant_id") or "")
        if not tenant:
            raise ValueError("tenantId required")
        amount = _f(_pick(data, "amount", "subtotal"), 0.0)
        tax_amount = _f(_pick(data, "taxAmount", "tax_amount"), 0.0)
        total = _f(_pick(data, "total", "total_amount", "totalAmount", "grand_total", "grandTotal"), 0.0)
        inv = cls(
            tenant_id=tenant,
            invoice_id=str(_pick(data, "invoiceId", "invoice_id") or f"WILSYINV-{uuid.uuid4().hex[:8].upper()}"),
            customer_id=_pick(data, "customerId", "customer_id"),
            status=_parse_status(data),
            amount=amount,
            tax_amount=tax_amount,
            total=total,
            amount_paid=_f(_pick(data, "amountPaid", "amount_paid"), 0.0),
            outstanding_amount=_f(_pick(data, "outstandingAmount", "outstanding_amount"), max(0.0, total)),
            currency=str(data.get("currency") or "ZAR"),
            line_items=line_items,
            issued_at=parse_datetime(_pick(data, "issuedAt", "issued_at")),
            due_at=parse_datetime(_pick(data, "dueAt", "due_at")),
            paid_at=parse_datetime(_pick(data, "paidAt", "paid_at")),
            void_at=parse_datetime(_pick(data, "voidAt", "void_at")),
            cancellation_reason=_pick(data, "cancellationReason", "cancellation_reason"),
            collection_method=CollectionMethod(str(_pick(data, "collectionMethod", "collection_method") or "send_invoice").lower()),
            payment_terms_days=_i(_pick(data, "paymentTermsDays", "payment_terms_days"), 30),
            tax_type=TaxType(str(_pick(data, "taxType", "tax_type") or "vat").lower()),
            seller_jurisdiction=str(_pick(data, "sellerJurisdiction", "seller_jurisdiction") or "ZA"),
            customer_jurisdiction=str(_pick(data, "customerJurisdiction", "customer_jurisdiction") or "ZA"),
            billing_mode=str(_pick(data, "billingMode", "billing_mode") or "PLATFORM"),
            metadata=_as_dict(data.get("metadata")),
            proof_hash=str(_pick(data, "proofHash", "proof_hash") or ""),
            created_at=parse_datetime(_pick(data, "createdAt", "created_at")) or datetime.now(timezone.utc),
            updated_at=parse_datetime(_pick(data, "updatedAt", "updated_at")) or datetime.now(timezone.utc),
            invoice_type=InvoiceType(str(_pick(data, "invoiceType", "invoice_type") or "platform").lower()),
            subscription_id=_pick(data, "subscriptionId", "subscription_id"),
            plan_id=_pick(data, "planId", "plan_id"),
            plan_name=_pick(data, "planName", "plan_name"),
            period_start=parse_datetime(_pick(data, "periodStart", "period_start")),
            period_end=parse_datetime(_pick(data, "periodEnd", "period_end")),
            order_number=_pick(data, "orderNumber", "order_number"),
            purchase_order=_pick(data, "purchaseOrder", "purchase_order"),
        )
        return inv


@dataclass(frozen=True)
class ClientInvoice(BaseInvoice):
    invoice_type: InvoiceType = InvoiceType.CLIENT
    customer_name: Optional[str] = None
    customer_tax_id: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    commercial_evidence_fingerprint: Optional[str] = None
    commercial_evidence_version: Optional[str] = None
    exact_money: Optional[ClientInvoiceExactMoney] = None

    def __post_init__(self) -> None:
        """Validate optional exact-money authority without changing legacy math."""
        if self.exact_money is not None and not self.line_items:
            projection = self.exact_money.to_legacy_projection()
            object.__setattr__(self, "line_items", [LineItem.from_dict(item) for item in projection["line_items"]])
            object.__setattr__(self, "amount", projection["amount"])
            object.__setattr__(self, "tax_amount", projection["tax_amount"])
            object.__setattr__(self, "total", projection["total"])
        BaseInvoice.__post_init__(self)
        if self.exact_money is not None:
            _validate_exact_money_projection(self, self.exact_money)

    def generate_proof(self, action: str = "save", metadata: Optional[Dict[str, Any]] = None) -> str:
        """Generate the unchanged legacy correlation proof without Model-C fields."""
        state = self.to_dict()
        state.pop("commercial_evidence_fingerprint", None)
        state.pop("commercial_evidence_version", None)
        return generate_entity_proof(state, action=action, metadata=metadata)

    def commercial_evidence_payload(
        self,
        *,
        version: str = CLIENT_COMMERCIAL_EVIDENCE_VERSION,
    ) -> Dict[str, Any]:
        """Build the exact deterministic V1 commercial-content payload.

        The payload deliberately excludes lifecycle, collection, audit metadata,
        legacy proof, and persistence timestamps that are not issuance facts.
        """
        if version != CLIENT_COMMERCIAL_EVIDENCE_VERSION:
            raise ValueError("CLIENT_INVOICE_COMMERCIAL_EVIDENCE_VERSION_UNSUPPORTED")
        return {
            "schema_version": version,
            "tenant_id": self.tenant_id,
            "invoice_id": self.invoice_id,
            "invoice_type": self.invoice_type.value,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "customer_tax_id": self.customer_tax_id,
            "customer_email": self.customer_email,
            "customer_phone": self.customer_phone,
            "currency": self.currency,
            "amount_minor": to_minor_units(self.amount, self.currency),
            "tax_amount_minor": to_minor_units(self.tax_amount, self.currency),
            "total_minor": to_minor_units(self.total, self.currency),
            "line_items": [
                {
                    "description": item.description,
                    "quantity": item.quantity,
                    "amount_minor": to_minor_units(item.amount, item.currency),
                    "unit_price_minor": to_minor_units(item.unit_price, item.currency),
                    "tax_rate": _canonical_rate(item.tax_rate),
                    "tax_amount_minor": to_minor_units(item.tax_amount, item.currency),
                    "discount_minor": to_minor_units(item.discount, item.currency),
                    "currency": item.currency,
                }
                for item in self.line_items
            ],
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "collection_method": self.collection_method.value,
            "payment_terms_days": self.payment_terms_days,
            "tax_type": self.tax_type.value,
            "seller_jurisdiction": self.seller_jurisdiction,
            "customer_jurisdiction": self.customer_jurisdiction,
            "billing_mode": self.billing_mode,
            "order_number": self.order_number,
            "purchase_order": self.purchase_order,
        }

    def compute_commercial_evidence_fingerprint(
        self,
        *,
        version: str = CLIENT_COMMERCIAL_EVIDENCE_VERSION,
    ) -> str:
        """Compute deterministic lowercase SHA3-512 commercial evidence."""
        payload = self.commercial_evidence_payload(version=version)
        raw = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha3_512(raw).hexdigest()

    def verify_commercial_evidence(self) -> bool:
        """Verify persisted Model-C evidence without clocks or defaulting."""
        stored = self.commercial_evidence_fingerprint
        version = self.commercial_evidence_version
        if not stored or not version or version != CLIENT_COMMERCIAL_EVIDENCE_VERSION:
            return False
        if len(stored) != 128 or any(char not in "0123456789abcdef" for char in stored):
            return False
        try:
            expected = self.compute_commercial_evidence_fingerprint(version=version)
        except (TypeError, ValueError):
            return False
        return hmac.compare_digest(stored, expected)

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "invoiceId": self.invoice_id,
            "invoice_id": self.invoice_id,
            "tenantId": self.tenant_id,
            "tenant_id": self.tenant_id,
            "customerId": self.customer_id,
            "customer_id": self.customer_id,
            "customerName": self.customer_name,
            "customer_name": self.customer_name,
            "customerTaxId": self.customer_tax_id,
            "customerEmail": self.customer_email,
            "customerPhone": self.customer_phone,
            "status": self.status.value,
            **_base_financial_dict(self),
            "currency": self.currency,
            "lineItems": [li.to_dict() for li in self.line_items],
            "line_items": [li.to_dict() for li in self.line_items],
            "issuedAt": self.issued_at.isoformat() if self.issued_at else None,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "dueAt": self.due_at.isoformat() if self.due_at else None,
            "due_at": self.due_at.isoformat() if self.due_at else None,
            "paidAt": self.paid_at.isoformat() if self.paid_at else None,
            "voidAt": self.void_at.isoformat() if self.void_at else None,
            "cancellationReason": self.cancellation_reason,
            "collectionMethod": self.collection_method.value,
            "paymentTermsDays": self.payment_terms_days,
            "taxType": self.tax_type.value,
            "sellerJurisdiction": self.seller_jurisdiction,
            "customerJurisdiction": self.customer_jurisdiction,
            "billingMode": self.billing_mode,
            "metadata": self.metadata,
            "proofHash": self.proof_hash,
            "proof_hash": self.proof_hash,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "invoiceType": self.invoice_type.value,
            "orderNumber": self.order_number,
            "order_number": self.order_number,
            "purchaseOrder": self.purchase_order,
            "purchase_order": self.purchase_order,
        }
        if self.commercial_evidence_fingerprint is not None:
            base["commercial_evidence_fingerprint"] = self.commercial_evidence_fingerprint
        if self.commercial_evidence_version is not None:
            base["commercial_evidence_version"] = self.commercial_evidence_version
        if self.exact_money is not None:
            exact = self.exact_money.to_dict()
            base["exact_money_version"] = exact["exact_money_version"]
            base["exact_money_fingerprint"] = exact["exact_money_fingerprint"]
            base["subtotal_minor"] = exact["subtotal_minor"]
            base["tax_amount_minor"] = exact["tax_amount_minor"]
            base["total_minor"] = exact["total_minor"]
            base["exact_money_lines"] = exact["lines"]
            base["exact_money"] = exact
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientInvoice":
        if not isinstance(data, dict):
            raise ValueError("ClientInvoice.from_dict requires a dict")
        line_items = _parse_line_items(data)
        exact: Optional[ClientInvoiceExactMoney] = None
        exact_keys = {"exact_money_version", "exact_money_fingerprint", "subtotal_minor", "tax_amount_minor", "total_minor", "exact_money_lines", "exact_money"}
        present_exact = exact_keys.intersection(data)
        if present_exact:
            envelope = data.get("exact_money")
            if envelope is None:
                envelope = {"exact_money_version": data.get("exact_money_version"), "exact_money_fingerprint": data.get("exact_money_fingerprint"), "currency": data.get("currency"), "subtotal_minor": data.get("subtotal_minor"), "tax_amount_minor": data.get("tax_amount_minor"), "total_minor": data.get("total_minor"), "lines": data.get("exact_money_lines")}
            exact = ClientInvoiceExactMoney.from_dict(envelope)
            if not line_items:
                projection = exact.to_legacy_projection()
                line_items = [LineItem.from_dict(item) for item in projection["line_items"]]
        tenant = str(_pick(data, "tenantId", "tenant_id") or "")
        if not tenant:
            raise ValueError("tenantId required")
        amount = _f(_pick(data, "amount", "subtotal"), 0.0)
        tax_amount = _f(_pick(data, "taxAmount", "tax_amount"), 0.0)
        total = _f(_pick(data, "total", "total_amount", "totalAmount", "grand_total", "grandTotal"), 0.0)
        invoice = cls(
            tenant_id=tenant,
            invoice_id=str(_pick(data, "invoiceId", "invoice_id") or f"WILSYCLI-{uuid.uuid4().hex[:8].upper()}"),
            customer_id=_pick(data, "customerId", "customer_id"),
            customer_name=_pick(data, "customerName", "customer_name"),
            customer_tax_id=_pick(data, "customerTaxId", "customer_tax_id"),
            customer_email=_pick(data, "customerEmail", "customer_email"),
            customer_phone=_pick(data, "customerPhone", "customer_phone"),
            status=_parse_status(data),
            amount=amount,
            tax_amount=tax_amount,
            total=total,
            amount_paid=_f(_pick(data, "amountPaid", "amount_paid"), 0.0),
            outstanding_amount=_f(_pick(data, "outstandingAmount", "outstanding_amount"), max(0.0, total)),
            currency=str(data.get("currency") or "ZAR"),
            line_items=line_items,
            issued_at=parse_datetime(_pick(data, "issuedAt", "issued_at")),
            due_at=parse_datetime(_pick(data, "dueAt", "due_at")),
            paid_at=parse_datetime(_pick(data, "paidAt", "paid_at")),
            void_at=parse_datetime(_pick(data, "voidAt", "void_at")),
            cancellation_reason=_pick(data, "cancellationReason", "cancellation_reason"),
            collection_method=CollectionMethod(str(_pick(data, "collectionMethod", "collection_method") or "send_invoice").lower()),
            payment_terms_days=_i(_pick(data, "paymentTermsDays", "payment_terms_days"), 30),
            tax_type=TaxType(str(_pick(data, "taxType", "tax_type") or "vat").lower()),
            seller_jurisdiction=str(_pick(data, "sellerJurisdiction", "seller_jurisdiction") or "ZA"),
            customer_jurisdiction=str(_pick(data, "customerJurisdiction", "customer_jurisdiction") or "ZA"),
            billing_mode=str(_pick(data, "billingMode", "billing_mode") or "CLIENT"),
            metadata=_as_dict(data.get("metadata")),
            proof_hash=str(_pick(data, "proofHash", "proof_hash") or ""),
            created_at=parse_datetime(_pick(data, "createdAt", "created_at")) or datetime.now(timezone.utc),
            updated_at=parse_datetime(_pick(data, "updatedAt", "updated_at")) or datetime.now(timezone.utc),
            invoice_type=InvoiceType(str(_pick(data, "invoiceType", "invoice_type") or "client").lower()),
            order_number=_pick(data, "orderNumber", "order_number"),
            purchase_order=_pick(data, "purchaseOrder", "purchase_order"),
            commercial_evidence_fingerprint=data.get("commercial_evidence_fingerprint"),
            commercial_evidence_version=data.get("commercial_evidence_version"),
            exact_money=exact,
        )
        return invoice


def _validate_exact_money_projection(invoice: ClientInvoice, exact: ClientInvoiceExactMoney) -> None:
    """Require every legacy float projection to round-trip to exact authority."""
    if invoice.currency != exact.currency:
        raise ValueError("CLIENT_INVOICE_EXACT_CURRENCY_MISMATCH")
    for projected, authoritative in (
        (invoice.amount, exact.subtotal_minor),
        (invoice.tax_amount, exact.tax_amount_minor),
        (invoice.total, exact.total_minor),
    ):
        if to_minor_units(projected, exact.currency) != authoritative:
            raise ValueError("CLIENT_INVOICE_EXACT_PROJECTION_MISMATCH")
    if len(invoice.line_items) != len(exact.lines):
        raise ValueError("CLIENT_INVOICE_EXACT_LINE_COUNT_MISMATCH")
    for item, line in zip(invoice.line_items, exact.lines):
        if item.currency != exact.currency or item.quantity != line.quantity:
            raise ValueError("CLIENT_INVOICE_EXACT_LINE_BINDING_MISMATCH")
        for projected, authoritative in (
            (item.unit_price, line.unit_price_minor),
            (item.amount, line.amount_minor),
            (item.tax_amount, line.tax_amount_minor),
            (item.discount, line.discount_minor),
        ):
            if to_minor_units(projected, exact.currency) != authoritative:
                raise ValueError("CLIENT_INVOICE_EXACT_LINE_PROJECTION_MISMATCH")


"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS BILLING DOMAIN v1.5.0-P6E-EXACT-CLIENT-INVOICE-MONEY
════════════════════════════════════════════════════════════════════════════════
Math:            amount = Σ line.amount (ex-VAT); tax_amount = Σ line.tax; total = amount + tax
Ledger:          MUST display total / total_amount / totalAmount (tax-inclusive)
Dual-case:       snake_case + camelCase on all money + id fields
Compliance:      POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001 │ SA VAT invoice total
Deploy:
  cp artifacts/tools/eos/saas/domain/billing.py \\
     /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/billing.py
  # restart Kennel (9095)
════════════════════════════════════════════════════════════════════════════════
"""
# ARTIFACT: tools/eos/saas/domain/billing.py
# VERSION: v1.5.0-P6E-EXACT-CLIENT-INVOICE-MONEY
# AUTHORITY BOUNDARY: ClientInvoice commercial and exact-money evidence only.
# TENANT POSTURE: Explicit tenant identity; legacy hydration remains compatible.
# FAIL-CLOSED POSTURE: Exact money requires integer arithmetic and verified SHA3-512.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
