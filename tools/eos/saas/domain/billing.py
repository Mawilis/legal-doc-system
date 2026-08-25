# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – SOVEREIGN BILLING DOMAIN MODEL (PYTHON) – TAX-INCLUSIVE TOTALS + DUAL CASE                           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/saas/domain/billing.py                                                             ║
║ VERSION:        v1.2.1-PYLANCE-METADATA                                                               ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                     ║
║ EPITOME:        LineItem accepts snake_case + camelCase. Invoice amount=subtotal, total=subtotal+tax.        ║
║                 Ledger MUST display tax-inclusive total (SA VAT / commercial invoice law).                    ║
║ CLASSIFICATION: Production Artifact                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                               ║
║   2026-08-24 v1.2.1-PYLANCE-METADATA – Fix ledger R0/ex-tax: from_dict reads unit_price/tax_amount;    ║
║                post_init sets amount (ex-VAT), tax_amount, total (incl VAT); dual-write total_amount.         ║
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
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


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
        return base

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ClientInvoice":
        if not isinstance(data, dict):
            raise ValueError("ClientInvoice.from_dict requires a dict")
        line_items = _parse_line_items(data)
        tenant = str(_pick(data, "tenantId", "tenant_id") or "")
        if not tenant:
            raise ValueError("tenantId required")
        amount = _f(_pick(data, "amount", "subtotal"), 0.0)
        tax_amount = _f(_pick(data, "taxAmount", "tax_amount"), 0.0)
        total = _f(_pick(data, "total", "total_amount", "totalAmount", "grand_total", "grandTotal"), 0.0)
        return cls(
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
        )


"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS BILLING DOMAIN v1.2.0-TAX-INCLUSIVE
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
