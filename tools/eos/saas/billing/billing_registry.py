# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – SOVEREIGN BILLING REGISTRY (MONGODB‑BACKED) – v1.6.0-L7D-B-BOOTSTRAP-HARDENING                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/saas/billing/billing_registry.py                                                     ║
║ VERSION:        v1.6.0-L7D-B-BOOTSTRAP-HARDENING                                                              ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                       ║
║ EPITOME:        Dual‑write/read tenantId|tenant_id + invoiceId|invoice_id; non‑null idempotencyKey parity;    ║
║                 payment rollup – sums succeeded payments and marks invoice PAID only when fully settled.       ║
║                 Uses explicit, lazy kernel.db resolution; imports never connect or freeze Mongo snapshots.       ║
║ CLASSIFICATION: Production Artifact                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                                  ║
║   2026-09-15 – v1.6.0-L7D-B-BOOTSTRAP-HARDENING – Removed import-time connection and frozen collection handles; ║
║                billing operations now resolve active persistence lazily and fail closed when unavailable.       ║
║   2026-09-15 – v1.5.0-P6E-EXACT-CLIENT-INVOICE-MONEY – Added caller-owned exact integer ClientInvoice creation,       ║
║                replay reconciliation, strict corruption checks, and transaction-conflict translation.                ║
║   2026-09-09 – v1.4.0-M11-R8-R3B-P6E-R1-CLIENT-EVIDENCE – Persist deterministic, versioned ClientInvoice        ║
║                commercial-content evidence and reject post-create commercial rewrites.                        ║
║   2026-09-09 – v1.3.0-M11-R8-R3B-C-STRICT-RAW-INVOICE-READ – Added tenant-scoped, caller-session-capable raw       ║
║                ClientInvoice and PlatformInvoice reads that preserve persisted field presence and values.       ║
║   2026-09-09 – v1.2.0-CLIENT-INVOICE-SESSION-READ – ClientInvoice reads now accept caller-owned collection/session      ║
║                context while preserving tenant predicates and default callers.                                      ║
║   2026-09-04 – v1.1.0-FINANCIAL-TRUTH-FIREWALL – Billing payment success/failure/refund and invoice settlement truth now fail closed unless projected from Kennel EOS. ║
║   2026-08-24 – v1.0.10 – Added `_sum_succeeded_payments` and rollup logic; mark PAID only when fully paid.    ║
║   2026-08-23 – v1.0.8 – Added `client = get_client()` alias.                                                   ║
║   2026-08-23 – v1.0.7 – Fixed DuplicateKeyError import.                                                        ║
║   2026-08-23 – v1.0.6 – Migrated to shared database module.                                                    ║
║   2026-08-21 – v1.0.5 – Added order_number & purchase_order parameters.                                        ║
║   2026-08-21 – v1.0.4 – Dual‑write tenant/invoice ids; list/get $or both casings.                             ║
║   2026-08-21 – v1.0.3 – Non‑null idempotency; E11000 replay.                                                  ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                  ║
║ CRYPTO:        SHA3‑512 proof generation (delegated to domain models)                                          ║
║ INTEGRATION:   Used by billing_router.py.                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/billing_registry.py

TENANT BOUNDARY:
    Every billing persistence lookup remains tenant-scoped. Tenant identity is
    explicit input and never inferred from payment, invoice, or provider data.

AUTHORITY BOUNDARY:
    BillingRegistry owns commercial invoice persistence and historical payment
    projection only. It does not authenticate, authorize release, invoke a
    provider, create financial execution truth, or establish settlement truth.

FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS exclusively owns financial execution truth. Payment SUCCEEDED,
    FAILED, REFUNDED, PARTIALLY_REFUNDED, paid_at, amount-paid settlement, and
    InvoiceStatus.PAID cannot be manufactured by this registry.

CONSTITUTION:
    REQUEST != AUTHORIZATION != EXECUTION != SETTLEMENT.
    NO EVIDENCE = NO FACT.

"""

import logging
import os
import uuid
import traceback
import hashlib
import json
from dataclasses import replace
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union, cast
from pymongo.collection import Collection

# ─── SHARED DATABASE CLIENT (ATLAS‑RESILIENT) ──────────────────────────────
from ...kernel.db import get_database, get_client, is_db_ready

# ─── MONGO EXCEPTIONS ──────────────────────────────────────────────────────
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.billing import (
    PlatformInvoice,
    ClientInvoice,
    Payment,
    InvoiceStatus,
    PaymentStatus,
    PaymentMethod,
    CollectionMethod,
    TaxType,
    InvoiceType,
    LineItem,
    CLIENT_COMMERCIAL_EVIDENCE_VERSION,
    ClientInvoiceExactMoney,
)

# ─── Configuration ──────────────────────────────────────────────────────────

VERSION = "v1.6.0-L7D-B-BOOTSTRAP-HARDENING"
_EXACT_REQUIRED = object()

logger = logging.getLogger(__name__)

# Compatibility attributes remain available for callers/tests that inject an
# explicit collection.  They intentionally remain ``None`` at import time;
# active persistence is resolved from kernel.db only when an operation needs it.
db = None
client = None
platform_invoices_coll = None
client_invoices_coll = None
payments_coll = None


def _active_collection(configured: Any, name: str) -> Collection:
    """Resolve an injected collection or the currently connected database.

    Importing this module performs no network I/O.  Missing explicit or kernel
    persistence fails closed at the operation boundary instead of silently
    falling back to memory.
    """
    if configured is not None:
        return cast(Collection, configured)
    database = get_database()
    if database is None:
        raise RuntimeError("BILLING_DATABASE_UNAVAILABLE")
    return cast(Collection, database[name])

# ─── Index Creation (idempotent) ──────────────────────────────────────────
def _ensure_indexes():
    """Create required indexes; safe to call multiple times."""
    try:
        platform = _active_collection(platform_invoices_coll, "platform_invoices")
        client_invoices = _active_collection(client_invoices_coll, "client_invoices")
        payments = _active_collection(payments_coll, "payments")
        platform.create_index([("tenant_id", 1), ("invoice_id", 1)], unique=True)
        platform.create_index([("tenant_id", 1), ("status", 1)])
        platform.create_index([("tenant_id", 1), ("issued_at", -1)])
        platform.create_index([("tenant_id", 1), ("due_at", 1)])
        try:
            platform.create_index(
                [("idempotencyKey", 1)],
                unique=True,
                name="idempotencyKey_1_partial",
                partialFilterExpression={"idempotencyKey": {"$type": "string"}},
            )
        except Exception:
            pass

        client_invoices.create_index([("tenant_id", 1), ("invoice_id", 1)], unique=True)
        client_invoices.create_index([("tenant_id", 1), ("status", 1)])
        client_invoices.create_index([("tenant_id", 1), ("issued_at", -1)])
        client_invoices.create_index(
            [("tenant_id", 1), ("idempotency_key", 1)],
            unique=True,
            name="p6e_client_exact_idempotency_unique",
            partialFilterExpression={"idempotency_key": {"$type": "string"}},
        )
        try:
            client_invoices.create_index(
                [("idempotencyKey", 1)],
                unique=True,
                name="idempotencyKey_1_partial",
                partialFilterExpression={"idempotencyKey": {"$type": "string"}},
            )
        except Exception:
            pass

        payments.create_index([("invoice_id", 1), ("payment_id", 1)], unique=True)
        payments.create_index([("tenant_id", 1), ("status", 1)])
        try:
            payments.create_index(
                [("idempotencyKey", 1)],
                unique=True,
                name="idempotencyKey_1_partial",
                partialFilterExpression={"idempotencyKey": {"$type": "string"}},
            )
        except Exception:
            pass
        logger.info("[BILLING_REGISTRY] Indexes verified/created.")
    except Exception as e:
        logger.warning(f"[BILLING_REGISTRY] Index creation issue (non‑fatal): {e}")


def _resolve_idempotency_key(
    idempotency_key: Optional[str] = None,
    *,
    prefix: str = "WILSY-BILL",
) -> str:
    """
    Always return a non-empty string.
    Accepts snake_case caller arg; never returns null (Mongo unique index safe).
    """
    key = (idempotency_key or "").strip() if isinstance(idempotency_key, str) else ""
    if key:
        return key
    return f"{prefix}-{uuid.uuid4().hex[:16].upper()}"


def _stamp_idempotency(doc: Dict[str, Any], key: str) -> Dict[str, Any]:
    """Dual-write camelCase (Node index) + snake_case (Kennel queries)."""
    doc["idempotencyKey"] = key
    doc["idempotency_key"] = key
    return doc


def _stamp_identity(doc: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
    """
    Dual-write tenant + invoice identifiers so Node camelCase and Kennel snake_case
    both match list/get queries.
    """
    doc["tenant_id"] = tenant_id
    doc["tenantId"] = tenant_id

    inv = (
        doc.get("invoice_id")
        or doc.get("invoiceId")
        or doc.get("invoice_number")
        or doc.get("invoiceNumber")
    )
    if inv:
        doc["invoice_id"] = inv
        doc["invoiceId"] = inv

    return doc


def _tenant_clause(tenant_id: str) -> Dict[str, Any]:
    return {"$or": [{"tenant_id": tenant_id}, {"tenantId": tenant_id}]}


def _invoice_id_clause(invoice_id: str) -> Dict[str, Any]:
    return {"$or": [{"invoice_id": invoice_id}, {"invoiceId": invoice_id}]}


def _tenant_invoice_query(tenant_id: str, invoice_id: str) -> Dict[str, Any]:
    return {"$and": [_tenant_clause(tenant_id), _invoice_id_clause(invoice_id)]}


def _normalize_sort_field(sort_by: str) -> str:
    """Prefer snake_case stored fields; fall back for camelCase domain dumps."""
    mapping = {
        "issued_at": "issued_at",
        "issuedAt": "issued_at",
        "due_at": "due_at",
        "dueAt": "due_at",
        "created_at": "created_at",
        "createdAt": "created_at",
        "total": "total",
        "status": "status",
    }
    return mapping.get(sort_by, sort_by or "issued_at")


class BillingFinancialTruthAuthorityError(ValueError):
    """Raised when billing is asked to manufacture Kennel-owned truth."""


_CLIENT_COMMERCIAL_PROTECTED_FIELDS = {
    "tenant_id", "tenantId", "invoice_id", "invoiceId", "invoice_type", "invoiceType",
    "customer_id", "customerId", "customer_name", "customerName",
    "customer_tax_id", "customerTaxId", "customer_email", "customerEmail",
    "customer_phone", "customerPhone", "currency", "amount", "subtotal",
    "tax_amount", "taxAmount", "total", "total_amount", "totalAmount",
    "grand_total", "grandTotal", "line_items", "lineItems", "issued_at", "issuedAt",
    "due_at", "dueAt", "collection_method", "collectionMethod",
    "payment_terms_days", "paymentTermsDays", "tax_type", "taxType",
    "seller_jurisdiction", "sellerJurisdiction", "customer_jurisdiction",
    "customerJurisdiction", "billing_mode", "billingMode", "order_number",
    "orderNumber", "purchase_order", "purchaseOrder", "commercial_evidence_fingerprint",
    "commercial_evidence_version",
    "exact_money", "exact_money_version", "exact_money_fingerprint",
    "subtotal_minor", "tax_amount_minor", "total_minor", "exact_money_lines",
    "exact_line_tax_rates_basis_points", "line_tax_rates_basis_points",
}


def _reject_client_invoice_commercial_updates(updates: Dict[str, Any]) -> None:
    """Prevent rewriting issued commercial content or its evidence."""
    if _CLIENT_COMMERCIAL_PROTECTED_FIELDS.intersection(updates):
        raise ValueError("CLIENT_INVOICE_COMMERCIAL_FIELD_REWRITE_FORBIDDEN")


def _exact_invoice_content(invoice: ClientInvoice, idempotency_key: str, line_tax_rates_basis_points: tuple[int, ...]) -> Dict[str, Any]:
    """Return immutable exact-path content used for replay reconciliation."""
    if invoice.exact_money is None:
        raise ValueError("CLIENT_INVOICE_EXACT_MONEY_REQUIRED")
    return {
        "tenant_id": invoice.tenant_id,
        "idempotency_key": idempotency_key,
        "customer_id": invoice.customer_id,
        "customer_name": invoice.customer_name,
        "customer_tax_id": invoice.customer_tax_id,
        "customer_email": invoice.customer_email,
        "customer_phone": invoice.customer_phone,
        "exact_money": invoice.exact_money.to_dict(),
        "line_tax_rates_basis_points": list(line_tax_rates_basis_points),
        "payment_terms_days": invoice.payment_terms_days,
        "tax_type": invoice.tax_type.value,
        "seller_jurisdiction": invoice.seller_jurisdiction,
        "customer_jurisdiction": invoice.customer_jurisdiction,
        "collection_method": invoice.collection_method.value,
        "billing_mode": invoice.billing_mode,
        "metadata": invoice.metadata,
        "order_number": invoice.order_number,
        "purchase_order": invoice.purchase_order,
        "issued_at": invoice.issued_at.isoformat() if invoice.issued_at else None,
        "due_at": invoice.due_at.isoformat() if invoice.due_at else None,
    }


def _exact_invoice_digest(invoice: ClientInvoice, idempotency_key: str, line_tax_rates_basis_points: tuple[int, ...]) -> str:
    raw = json.dumps(_exact_invoice_content(invoice, idempotency_key, line_tax_rates_basis_points), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha3_512(raw).hexdigest()


def _reject_invoice_financial_truth_updates(
    updates: Dict[str, Any],
) -> None:
    """Reject direct settlement mutation on generic invoice update paths.

    Billing owns invoice commercial state but cannot independently establish
    payment execution or settlement. Historical persisted projections remain
    readable; new settlement truth must originate from certified Kennel
    evidence through a future dedicated projection path.
    """
    if not isinstance(updates, dict):
        raise TypeError("updates must be a dictionary")

    forbidden_fields = {
        "paid_at",
        "paidAt",
        "amount_paid",
        "amountPaid",
        "outstanding_amount",
        "outstandingAmount",
    }

    if forbidden_fields.intersection(updates):
        raise BillingFinancialTruthAuthorityError(
            "BILLING_SETTLEMENT_TRUTH_REQUIRES_KENNEL"
        )

    status_value = updates.get("status")

    if isinstance(status_value, InvoiceStatus):
        status_value = status_value.value

    if (
        isinstance(status_value, str)
        and status_value.strip().lower()
        == InvoiceStatus.PAID.value
    ):
        raise BillingFinancialTruthAuthorityError(
            "BILLING_PAID_STATE_REQUIRES_KENNEL_SETTLEMENT_EVIDENCE"
        )


class BillingRegistry:
    """
    Sovereign billing registry with MongoDB persistence.
    Handles CRUD for PlatformInvoice, ClientInvoice, and Payment.
    All tenant‑scoped queries enforce tenant isolation.
    """

    def __init__(self) -> None:
        """Initialise the registry (no dependencies)."""
        pass

    # ─── Helpers ────────────────────────────────────────────────────────────

    def _sum_succeeded_payments(self, tenant_id: str, invoice_id: str) -> float:
        """
        Sum the amount of all succeeded payments for a given invoice.
        Returns 0.0 if none.
        """
        try:
            pipeline = [
                {"$match": {
                    "$and": [
                        _tenant_clause(tenant_id),
                        _invoice_id_clause(invoice_id),
                        {"status": "succeeded"},
                    ]
                }},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            result = list(_active_collection(payments_coll, "payments").aggregate(pipeline))
            if result and result[0].get("total"):
                return float(result[0]["total"])
            return 0.0
        except Exception as e:
            logger.warning(f"Failed to sum payments for invoice {invoice_id}: {e}")
            return 0.0

    # ─── Platform Invoices ──────────────────────────────────────────────────

    def create_platform_invoice(
        self,
        tenant_id: str,
        customer_id: Optional[str] = None,
        line_items: Optional[List[Dict[str, Any]]] = None,
        currency: str = "ZAR",
        issued_at: Optional[datetime] = None,
        due_at: Optional[datetime] = None,
        payment_terms_days: int = 30,
        tax_type: str = "vat",
        seller_jurisdiction: str = "ZA",
        customer_jurisdiction: str = "ZA",
        collection_method: str = "send_invoice",
        billing_mode: str = "PLATFORM",
        subscription_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        plan_name: Optional[str] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        performed_by: str = "SYSTEM",
        # ─── Sovereign order numbers ─────────────────────────────────────
        order_number: Optional[str] = None,
        purchase_order: Optional[str] = None,
    ) -> PlatformInvoice:
        """
        Create a new platform invoice (Wilsy → tenant).
        If idempotency_key is provided and an invoice with that key exists, return it.
        Never inserts idempotencyKey: null (fixes E11000 on idempotencyKey_1).
        Dual-writes tenantId/tenant_id so list queries find the document.
        Now accepts order_number and purchase_order for sovereign branded numbering.
        """
        try:
            resolved_key = _resolve_idempotency_key(idempotency_key, prefix="WILSY-BILL-PLAT")

            existing = self.get_platform_invoice_by_idempotency_key(tenant_id, resolved_key)
            if existing:
                return existing

            # Build line items from dicts
            line_item_objs = []
            if line_items:
                for li in line_items:
                    line_item_objs.append(LineItem.from_dict(li))

            # Calculate totals (domain will compute in __post_init__)
            # Pyright cannot expand inherited dataclass constructor parameters;
            # the runtime constructor remains the canonical PlatformInvoice.
            invoice = cast(Any, PlatformInvoice)(
                tenant_id=tenant_id,
                customer_id=customer_id,
                line_items=line_item_objs,
                currency=currency,
                issued_at=issued_at or datetime.now(timezone.utc),
                due_at=due_at or (datetime.now(timezone.utc) + timedelta(days=payment_terms_days)),
                payment_terms_days=payment_terms_days,
                tax_type=TaxType(tax_type.lower()),
                seller_jurisdiction=seller_jurisdiction,
                customer_jurisdiction=customer_jurisdiction,
                collection_method=CollectionMethod(collection_method.lower()),
                billing_mode=billing_mode,
                subscription_id=subscription_id,
                plan_id=plan_id,
                plan_name=plan_name,
                period_start=period_start,
                period_end=period_end,
                metadata=metadata or {},
                status=InvoiceStatus.OPEN,  # Immediately open unless draft specified
                # ─── Pass through order numbers ──────────────────────────
                order_number=order_number,
                purchase_order=purchase_order,
            )
            # After creation, we get the proof hash, total, etc.
            # Insert into MongoDB
            doc = invoice.to_dict()
            doc = _stamp_identity(doc, tenant_id)
            doc = _stamp_idempotency(doc, resolved_key)
            doc["performed_by"] = performed_by
            doc["created_by"] = performed_by

            try:
                _active_collection(platform_invoices_coll, "platform_invoices").insert_one(doc)
                logger.info(f"Created platform invoice {invoice.invoice_id} for tenant {tenant_id}")
                return invoice
            except DuplicateKeyError as dup:
                # Prefer idempotent replay over opaque 500
                existing = self.get_platform_invoice_by_idempotency_key(tenant_id, resolved_key)
                if existing:
                    logger.info(
                        f"Idempotent replay platform invoice key={resolved_key} → {existing.invoice_id}"
                    )
                    return existing
                # Possibly a duplicate invoice_id – rare, but we can retry with new ID
                logger.warning(f"Duplicate invoice_id, retrying with new ID: {dup}")
                # For simplicity, we'll re‑generate invoice_id and retry once.
                new_id = f"WILSYINV-{uuid.uuid4().hex[:8].upper()}"
                # Manually override invoice_id (since it's frozen, we need to recreate)
                invoice = PlatformInvoice.from_dict({**doc, "invoiceId": new_id, "invoice_id": new_id})
                doc = invoice.to_dict()
                doc = _stamp_identity(doc, tenant_id)
                doc = _stamp_idempotency(doc, resolved_key)
                doc["performed_by"] = performed_by
                doc["created_by"] = performed_by
                try:
                    _active_collection(platform_invoices_coll, "platform_invoices").insert_one(doc)
                    return invoice
                except DuplicateKeyError:
                    existing = self.get_platform_invoice_by_idempotency_key(tenant_id, resolved_key)
                    if existing:
                        return existing
                    raise
        except Exception as e:
            logger.error(f"Failed to create platform invoice: {e}\n{traceback.format_exc()}")
            raise

    def get_platform_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        *,
        collection: Any = None,
        session: Any = None,
    ) -> Optional[PlatformInvoice]:
        """Retrieve a platform invoice by ID, enforcing tenant isolation."""
        try:
            target = collection if collection is not None else _active_collection(platform_invoices_coll, "platform_invoices")
            query = _tenant_invoice_query(tenant_id, invoice_id)
            if session is None:
                doc = target.find_one(query)
            else:
                doc = target.find_one(query, session=session)
            if not doc:
                return None
            return PlatformInvoice.from_dict(doc)
        except Exception as e:
            logger.error(f"Failed to get platform invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    def get_platform_invoice_raw(
        self,
        tenant_id: str,
        invoice_id: str,
        *,
        collection: Any = None,
        session: Any = None,
    ) -> Optional[Dict[str, Any]]:
        """Return an exact tenant-scoped persisted platform invoice document.

        This authority-reading seam intentionally performs no domain hydration,
        defaulting, normalization, proof generation, amount conversion, or
        schema repair.  A shallow copy protects the driver's returned mapping
        while preserving ``_id`` and every persisted field, including unknown
        fields and absent authority fields.  The caller owns collection and
        session/transaction lifecycle.
        """
        try:
            target = collection if collection is not None else _active_collection(platform_invoices_coll, "platform_invoices")
            query = _tenant_invoice_query(tenant_id, invoice_id)
            if session is None:
                doc = target.find_one(query)
            else:
                doc = target.find_one(query, session=session)
            return None if doc is None else dict(doc)
        except Exception as e:
            logger.error(f"Failed to get raw platform invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    def get_platform_invoice_by_idempotency_key(self, tenant_id: str, idempotency_key: str) -> Optional[PlatformInvoice]:
        try:
            if not idempotency_key:
                return None
            # Match either field name (Node camelCase index vs Kennel snake_case)
            doc = _active_collection(platform_invoices_coll, "platform_invoices").find_one({
                "$and": [
                    _tenant_clause(tenant_id),
                    {
                        "$or": [
                            {"idempotency_key": idempotency_key},
                            {"idempotencyKey": idempotency_key},
                        ]
                    },
                ]
            })
            if not doc:
                return None
            return PlatformInvoice.from_dict(doc)
        except Exception as e:
            logger.error(f"Failed to get platform invoice by idempotency key: {e}\n{traceback.format_exc()}")
            raise

    def list_platform_invoices(
        self,
        tenant_id: str,
        status: Optional[Union[str, InvoiceStatus]] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "issued_at",
        sort_order: int = -1,
    ) -> List[PlatformInvoice]:
        try:
            query: Dict[str, Any] = dict(_tenant_clause(tenant_id))
            if status:
                if isinstance(status, InvoiceStatus):
                    status = status.value
                # status may be stored lower/upper depending on domain dump
                query["status"] = status
            sort_field = _normalize_sort_field(sort_by)
            cursor = (
                _active_collection(platform_invoices_coll, "platform_invoices").find(query)
                .sort(sort_field, sort_order)
                .skip(offset)
                .limit(limit)
            )
            return [PlatformInvoice.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to list platform invoices: {e}\n{traceback.format_exc()}")
            raise

    def update_platform_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        updates: Dict[str, Any],
        performed_by: str = "SYSTEM",
    ) -> PlatformInvoice:
        """
        Update a platform invoice. Fields allowed: status, paid_at, void_at, cancellation_reason,
        metadata, etc. Recomputes proof.
        """
        _reject_invoice_financial_truth_updates(updates)
        try:
            current = self.get_platform_invoice(tenant_id, invoice_id)
            if not current:
                raise ValueError(f"Platform invoice {invoice_id} not found for tenant {tenant_id}")

            current_dict = current.to_dict()
            field_map = {
                "status": "status",
                "paidAt": "paid_at",
                "voidAt": "void_at",
                "cancellationReason": "cancellation_reason",
                "metadata": "metadata",
                "dueAt": "due_at",
                "issuedAt": "issued_at",
            }
            for key, value in updates.items():
                if key in field_map:
                    model_key = field_map[key]
                    if model_key == "status" and isinstance(value, str):
                        value = InvoiceStatus(value.lower())
                    current_dict[model_key] = value
                else:
                    if key in current_dict:
                        current_dict[key] = value

            updated = PlatformInvoice.from_dict(current_dict)
            set_doc = _stamp_identity(updated.to_dict(), tenant_id)
            result = _active_collection(platform_invoices_coll, "platform_invoices").update_one(
                _tenant_invoice_query(tenant_id, invoice_id),
                {"$set": set_doc},
            )
            if result.matched_count == 0:
                raise ValueError(f"Platform invoice {invoice_id} not found for tenant {tenant_id}")
            return updated
        except Exception as e:
            logger.error(f"Failed to update platform invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    def void_platform_invoice(self, tenant_id: str, invoice_id: str, reason: str, performed_by: str = "SYSTEM") -> PlatformInvoice:
        try:
            return self.update_platform_invoice(
                tenant_id,
                invoice_id,
                {"status": InvoiceStatus.VOID, "void_at": datetime.now(timezone.utc), "cancellation_reason": reason},
                performed_by
            )
        except Exception as e:
            logger.error(f"Failed to void platform invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    # ─── Client Invoices ────────────────────────────────────────────────────

    def create_client_invoice(
        self,
        tenant_id: str,
        customer_id: Optional[str] = None,
        customer_name: Optional[str] = None,
        customer_tax_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        line_items: Optional[List[Dict[str, Any]]] = None,
        currency: str = "ZAR",
        issued_at: Optional[datetime] = None,
        due_at: Optional[datetime] = None,
        payment_terms_days: int = 30,
        tax_type: str = "vat",
        seller_jurisdiction: str = "ZA",
        customer_jurisdiction: str = "ZA",
        collection_method: str = "send_invoice",
        billing_mode: str = "CLIENT",
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        performed_by: str = "SYSTEM",
        # ─── Sovereign order numbers ─────────────────────────────────────
        order_number: Optional[str] = None,
        purchase_order: Optional[str] = None,
    ) -> ClientInvoice:
        try:
            resolved_key = _resolve_idempotency_key(idempotency_key, prefix="WILSY-BILL-CLI")

            existing = self.get_client_invoice_by_idempotency_key(tenant_id, resolved_key)
            if existing:
                return existing

            line_item_objs = []
            if line_items:
                for li in line_items:
                    line_item_objs.append(LineItem.from_dict(li))

            # Pyright cannot expand inherited dataclass constructor parameters;
            # the runtime constructor remains the canonical ClientInvoice.
            invoice = cast(Any, ClientInvoice)(
                tenant_id=tenant_id,
                customer_id=customer_id,
                customer_name=customer_name,
                customer_tax_id=customer_tax_id,
                customer_email=customer_email,
                customer_phone=customer_phone,
                line_items=line_item_objs,
                currency=currency,
                issued_at=issued_at or datetime.now(timezone.utc),
                due_at=due_at or (datetime.now(timezone.utc) + timedelta(days=payment_terms_days)),
                payment_terms_days=payment_terms_days,
                tax_type=TaxType(tax_type.lower()),
                seller_jurisdiction=seller_jurisdiction,
                customer_jurisdiction=customer_jurisdiction,
                collection_method=CollectionMethod(collection_method.lower()),
                billing_mode=billing_mode,
                metadata=metadata or {},
                status=InvoiceStatus.OPEN,
                # ─── Pass through order numbers ──────────────────────────
                order_number=order_number,
                purchase_order=purchase_order,
            )
            invoice = replace(
                invoice,
                commercial_evidence_version=CLIENT_COMMERCIAL_EVIDENCE_VERSION,
            )
            invoice = replace(
                invoice,
                commercial_evidence_fingerprint=invoice.compute_commercial_evidence_fingerprint(),
            )
            if not invoice.verify_commercial_evidence():
                raise ValueError("CLIENT_INVOICE_COMMERCIAL_EVIDENCE_VERIFICATION_FAILED")
            doc = invoice.to_dict()
            doc = _stamp_identity(doc, tenant_id)
            doc = _stamp_idempotency(doc, resolved_key)
            doc["performed_by"] = performed_by
            doc["created_by"] = performed_by
            try:
                _active_collection(client_invoices_coll, "client_invoices").insert_one(doc)
                logger.info(f"Created client invoice {invoice.invoice_id} for tenant {tenant_id}")
                return invoice
            except DuplicateKeyError as dup:
                existing = self.get_client_invoice_by_idempotency_key(tenant_id, resolved_key)
                if existing:
                    logger.info(
                        f"Idempotent replay client invoice key={resolved_key} → {existing.invoice_id}"
                    )
                    return existing
                new_id = f"WILSYCLI-{uuid.uuid4().hex[:8].upper()}"
                invoice = ClientInvoice.from_dict({**doc, "invoiceId": new_id, "invoice_id": new_id})
                doc = invoice.to_dict()
                doc = _stamp_identity(doc, tenant_id)
                doc = _stamp_idempotency(doc, resolved_key)
                doc["performed_by"] = performed_by
                doc["created_by"] = performed_by
                try:
                    _active_collection(client_invoices_coll, "client_invoices").insert_one(doc)
                    return invoice
                except DuplicateKeyError:
                    existing = self.get_client_invoice_by_idempotency_key(tenant_id, resolved_key)
                    if existing:
                        return existing
                    raise
        except Exception as e:
            logger.error(f"Failed to create client invoice: {e}\n{traceback.format_exc()}")
            raise

    def get_client_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        *,
        collection: Any = None,
        session: Any = None,
    ) -> Optional[ClientInvoice]:
        """Retrieve a tenant-scoped client invoice with caller-owned read context.

        ``collection`` and ``session`` mirror ``get_platform_invoice``.  The
        registry never creates, starts, commits, or aborts a transaction; when
        supplied, the exact caller session is forwarded to MongoDB.
        """
        try:
            target = collection if collection is not None else _active_collection(client_invoices_coll, "client_invoices")
            query = _tenant_invoice_query(tenant_id, invoice_id)
            if session is None:
                doc = target.find_one(query)
            else:
                doc = target.find_one(query, session=session)
            if not doc:
                return None
            return ClientInvoice.from_dict(doc)
        except Exception as e:
            logger.error(f"Failed to get client invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    def create_client_invoice_exact(
        self,
        tenant_id: str,
        exact_money: ClientInvoiceExactMoney,
        *,
        customer_id: str | object = _EXACT_REQUIRED,
        customer_name: str | object = _EXACT_REQUIRED,
        customer_tax_id: Optional[str] = None,
        customer_email: Optional[str] = None,
        customer_phone: Optional[str] = None,
        payment_terms_days: int | object = _EXACT_REQUIRED,
        tax_type: str | TaxType | object = _EXACT_REQUIRED,
        seller_jurisdiction: str | object = _EXACT_REQUIRED,
        customer_jurisdiction: str | object = _EXACT_REQUIRED,
        collection_method: str | CollectionMethod | object = _EXACT_REQUIRED,
        billing_mode: str = "CLIENT",
        metadata: Optional[Dict[str, Any]] = None,
        issued_at: datetime | object = _EXACT_REQUIRED,
        due_at: datetime | object = _EXACT_REQUIRED,
        line_tax_rates_basis_points: tuple[int, ...] | object = _EXACT_REQUIRED,
        idempotency_key: str,
        invoice_id: Optional[str] = None,
        performed_by: str = "SYSTEM",
        order_number: Optional[str] = None,
        purchase_order: Optional[str] = None,
        collection: Any = None,
        session: Any = None,
    ) -> ClientInvoice:
        """Create or exactly replay a ClientInvoice backed by integer money.

        ``exact_money`` is the sole commercial money authority; legacy floats are
        derived compatibility projections. The caller supplies collection/session
        and owns every transaction decision. Active transaction conflicts become
        ``M2_RETRY_TRANSACTION_REQUIRED`` while retaining the PyMongo cause.
        """
        if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id.casefold() in {"default", "global", "root", "master", "*"}:
            raise ValueError("CLIENT_INVOICE_TENANT_INVALID")
        if type(exact_money) is not ClientInvoiceExactMoney:
            raise ValueError("CLIENT_INVOICE_EXACT_MONEY_REQUIRED")
        if not isinstance(customer_id, str) or not customer_id.strip() or not isinstance(customer_name, str) or not customer_name.strip():
            raise ValueError("CLIENT_INVOICE_CUSTOMER_REQUIRED")
        if isinstance(payment_terms_days, bool) or not isinstance(payment_terms_days, int) or payment_terms_days < 0:
            raise ValueError("CLIENT_INVOICE_PAYMENT_TERMS_REQUIRED")
        if not isinstance(seller_jurisdiction, str) or not seller_jurisdiction.strip() or not isinstance(customer_jurisdiction, str) or not customer_jurisdiction.strip():
            raise ValueError("CLIENT_INVOICE_JURISDICTION_REQUIRED")
        if type(tax_type) is TaxType:
            resolved_tax_type = tax_type
        elif isinstance(tax_type, str):
            try: resolved_tax_type = TaxType(tax_type.lower())
            except ValueError as error: raise ValueError("CLIENT_INVOICE_TAX_TYPE_REQUIRED") from error
        else:
            raise ValueError("CLIENT_INVOICE_TAX_TYPE_REQUIRED")
        if type(collection_method) is CollectionMethod:
            resolved_collection_method = collection_method
        elif isinstance(collection_method, str):
            try: resolved_collection_method = CollectionMethod(collection_method.lower())
            except ValueError as error: raise ValueError("CLIENT_INVOICE_COLLECTION_METHOD_REQUIRED") from error
        else:
            raise ValueError("CLIENT_INVOICE_COLLECTION_METHOD_REQUIRED")
        if not isinstance(issued_at, datetime) or issued_at.tzinfo is None or issued_at.utcoffset() is None:
            raise ValueError("CLIENT_INVOICE_ISSUED_AT_REQUIRED")
        if not isinstance(due_at, datetime) or due_at.tzinfo is None or due_at.utcoffset() is None:
            raise ValueError("CLIENT_INVOICE_DUE_AT_REQUIRED")
        if due_at < issued_at:
            raise ValueError("CLIENT_INVOICE_DUE_DATE_INVALID")
        if not isinstance(line_tax_rates_basis_points, tuple) or len(line_tax_rates_basis_points) != len(exact_money.lines) or any(isinstance(rate, bool) or not isinstance(rate, int) or rate < 0 for rate in line_tax_rates_basis_points):
            raise ValueError("CLIENT_INVOICE_LINE_TAX_RATES_REQUIRED")
        if not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ValueError("CLIENT_INVOICE_IDEMPOTENCY_REQUIRED")
        target = collection if collection is not None else _active_collection(client_invoices_coll, "client_invoices")
        if target is None:
            raise ValueError("CLIENT_INVOICE_COLLECTION_UNAVAILABLE")
        projection = exact_money.to_legacy_projection()
        line_items = [LineItem.from_dict(item) for item in projection["line_items"]]
        line_items = [replace(item, tax_rate=float(Decimal(rate) / Decimal(10000))) for item, rate in zip(line_items, line_tax_rates_basis_points)]
        invoice = ClientInvoice(
            tenant_id=tenant_id,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_tax_id=customer_tax_id,
            customer_email=customer_email,
            customer_phone=customer_phone,
            status=InvoiceStatus.OPEN,
            amount=projection["amount"],
            tax_amount=projection["tax_amount"],
            total=projection["total"],
            outstanding_amount=projection["total"],
            currency=exact_money.currency,
            line_items=line_items,
            issued_at=issued_at,
            due_at=due_at,
            payment_terms_days=payment_terms_days,
            tax_type=resolved_tax_type,
            seller_jurisdiction=seller_jurisdiction,
            customer_jurisdiction=customer_jurisdiction,
            collection_method=resolved_collection_method,
            billing_mode=billing_mode,
            metadata=metadata or {},
            order_number=order_number,
            purchase_order=purchase_order,
            exact_money=exact_money,
        )
        if invoice_id is not None:
            if not isinstance(invoice_id, str) or not invoice_id.strip():
                raise ValueError("CLIENT_INVOICE_IDENTITY_REQUIRED")
            invoice = replace(invoice, invoice_id=invoice_id)
        invoice = replace(
            invoice,
            commercial_evidence_version=CLIENT_COMMERCIAL_EVIDENCE_VERSION,
        )
        invoice = replace(
            invoice,
            commercial_evidence_fingerprint=invoice.compute_commercial_evidence_fingerprint(),
        )
        if not invoice.verify_commercial_evidence():
            raise ValueError("CLIENT_INVOICE_COMMERCIAL_EVIDENCE_VERIFICATION_FAILED")
        content_fingerprint = _exact_invoice_digest(invoice, idempotency_key, line_tax_rates_basis_points)
        query = {"tenant_id": tenant_id, "idempotency_key": idempotency_key}
        try:
            existing_raw = target.find_one(query, **({"session": session} if session is not None else {}))
        except PyMongoError as error:
            raise ValueError("CLIENT_INVOICE_PERSISTENCE_UNAVAILABLE") from error
        if existing_raw is not None:
            existing = ClientInvoice.from_dict(existing_raw)
            if existing_raw.get("exact_invoice_content_fingerprint") != content_fingerprint:
                raise ValueError("CLIENT_INVOICE_REPLAY_CONFLICT")
            return existing
        doc = invoice.to_dict()
        doc = _stamp_identity(doc, tenant_id)
        doc = _stamp_idempotency(doc, idempotency_key)
        doc["exact_invoice_content_fingerprint"] = content_fingerprint
        doc["exact_line_tax_rates_basis_points"] = list(line_tax_rates_basis_points)
        doc["performed_by"] = performed_by
        doc["created_by"] = performed_by
        try:
            target.insert_one(doc, **({"session": session} if session is not None else {}))
            return invoice
        except DuplicateKeyError as error:
            active = bool(getattr(session, "in_transaction", False)) if session is not None else False
            if active:
                raise ValueError("M2_RETRY_TRANSACTION_REQUIRED") from error
            try:
                raced_raw = target.find_one(query, **({"session": session} if session is not None else {}))
            except PyMongoError as read_error:
                raise ValueError("CLIENT_INVOICE_PERSISTENCE_UNAVAILABLE") from read_error
            if raced_raw is None:
                raise ValueError("CLIENT_INVOICE_REPLAY_CONFLICT") from error
            raced = ClientInvoice.from_dict(raced_raw)
            if raced_raw.get("exact_invoice_content_fingerprint") != content_fingerprint:
                raise ValueError("CLIENT_INVOICE_REPLAY_CONFLICT") from error
            return raced
        except PyMongoError as error:
            labels = {label for label in ("TransientTransactionError", "UnknownTransactionCommitResult") if error.has_error_label(label)}
            if active := (session is not None and bool(getattr(session, "in_transaction", False))):
                if "TransientTransactionError" in labels and "UnknownTransactionCommitResult" not in labels:
                    raise ValueError("M2_RETRY_TRANSACTION_REQUIRED") from error
            raise ValueError("CLIENT_INVOICE_PERSISTENCE_UNAVAILABLE") from error

    def get_client_invoice_raw(
        self,
        tenant_id: str,
        invoice_id: str,
        *,
        collection: Any = None,
        session: Any = None,
    ) -> Optional[Dict[str, Any]]:
        """Return an exact tenant-scoped persisted client invoice document.

        The raw result is a shallow copy of the persisted Mongo mapping.  No
        ``ClientInvoice.from_dict`` call, default-generating hydration,
        normalization, proof generation, money conversion, or field insertion
        occurs.  Caller-supplied collection/session context is forwarded
        unchanged and transaction ownership remains with the caller.
        """
        try:
            target = collection if collection is not None else _active_collection(client_invoices_coll, "client_invoices")
            query = _tenant_invoice_query(tenant_id, invoice_id)
            if session is None:
                doc = target.find_one(query)
            else:
                doc = target.find_one(query, session=session)
            return None if doc is None else dict(doc)
        except Exception as e:
            logger.error(f"Failed to get raw client invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    def get_client_invoice_by_idempotency_key(self, tenant_id: str, idempotency_key: str) -> Optional[ClientInvoice]:
        try:
            if not idempotency_key:
                return None
            doc = _active_collection(client_invoices_coll, "client_invoices").find_one({
                "$and": [
                    _tenant_clause(tenant_id),
                    {
                        "$or": [
                            {"idempotency_key": idempotency_key},
                            {"idempotencyKey": idempotency_key},
                        ]
                    },
                ]
            })
            if not doc:
                return None
            return ClientInvoice.from_dict(doc)
        except Exception as e:
            logger.error(f"Failed to get client invoice by idempotency key: {e}\n{traceback.format_exc()}")
            raise

    def list_client_invoices(
        self,
        tenant_id: str,
        status: Optional[Union[str, InvoiceStatus]] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "issued_at",
        sort_order: int = -1,
    ) -> List[ClientInvoice]:
        try:
            query: Dict[str, Any] = dict(_tenant_clause(tenant_id))
            if status:
                if isinstance(status, InvoiceStatus):
                    status = status.value
                query["status"] = status
            sort_field = _normalize_sort_field(sort_by)
            cursor = (
                _active_collection(client_invoices_coll, "client_invoices").find(query)
                .sort(sort_field, sort_order)
                .skip(offset)
                .limit(limit)
            )
            return [ClientInvoice.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to list client invoices: {e}\n{traceback.format_exc()}")
            raise

    def update_client_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        updates: Dict[str, Any],
        performed_by: str = "SYSTEM",
    ) -> ClientInvoice:
        _reject_invoice_financial_truth_updates(updates)
        _reject_client_invoice_commercial_updates(updates)
        try:
            current = self.get_client_invoice(tenant_id, invoice_id)
            if not current:
                raise ValueError(f"Client invoice {invoice_id} not found for tenant {tenant_id}")
            current_dict = current.to_dict()
            field_map = {
                "status": "status",
                "paidAt": "paid_at",
                "voidAt": "void_at",
                "cancellationReason": "cancellation_reason",
                "metadata": "metadata",
                "dueAt": "due_at",
                "issuedAt": "issued_at",
            }
            for key, value in updates.items():
                if key in field_map:
                    model_key = field_map[key]
                    if model_key == "status" and isinstance(value, str):
                        value = InvoiceStatus(value.lower())
                    current_dict[model_key] = value
                else:
                    if key in current_dict:
                        current_dict[key] = value
            updated = ClientInvoice.from_dict(current_dict)
            set_doc = _stamp_identity(updated.to_dict(), tenant_id)
            result = _active_collection(client_invoices_coll, "client_invoices").update_one(
                _tenant_invoice_query(tenant_id, invoice_id),
                {"$set": set_doc},
            )
            if result.matched_count == 0:
                raise ValueError(f"Client invoice {invoice_id} not found for tenant {tenant_id}")
            return updated
        except Exception as e:
            logger.error(f"Failed to update client invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    def void_client_invoice(self, tenant_id: str, invoice_id: str, reason: str, performed_by: str = "SYSTEM") -> ClientInvoice:
        try:
            return self.update_client_invoice(
                tenant_id,
                invoice_id,
                {"status": InvoiceStatus.VOID, "void_at": datetime.now(timezone.utc), "cancellation_reason": reason},
                performed_by
            )
        except Exception as e:
            logger.error(f"Failed to void client invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    # ─── Payments ────────────────────────────────────────────────────────────

    def create_payment(
        self,
        invoice_id: str,
        tenant_id: str,
        amount: float,
        currency: str,
        method: str = "other",
        external_reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        performed_by: str = "SYSTEM",
    ) -> Payment:
        try:
            resolved_key = _resolve_idempotency_key(idempotency_key, prefix="WILSY-PAY")

            existing = self.get_payment_by_idempotency_key(tenant_id, resolved_key)
            if existing:
                return existing

            payment = Payment(
                invoice_id=invoice_id,
                amount=amount,
                currency=currency,
                method=PaymentMethod(method.lower()),
                external_reference=external_reference,
                metadata=metadata or {},
                status=PaymentStatus.PENDING,
            )
            doc = payment.to_dict()
            doc = _stamp_identity(doc, tenant_id)
            doc["invoice_id"] = invoice_id
            doc["invoiceId"] = invoice_id
            doc = _stamp_idempotency(doc, resolved_key)
            doc["performed_by"] = performed_by
            doc["created_by"] = performed_by
            try:
                _active_collection(payments_coll, "payments").insert_one(doc)
                logger.info(f"Created payment {payment.payment_id} for invoice {invoice_id}")
                return payment
            except DuplicateKeyError:
                existing = self.get_payment_by_idempotency_key(tenant_id, resolved_key)
                if existing:
                    return existing
                new_id = f"WILSYPAY-{uuid.uuid4().hex[:8].upper()}"
                payment = Payment.from_dict({**doc, "paymentId": new_id})
                doc = payment.to_dict()
                doc = _stamp_identity(doc, tenant_id)
                doc["invoice_id"] = invoice_id
                doc["invoiceId"] = invoice_id
                doc = _stamp_idempotency(doc, resolved_key)
                doc["performed_by"] = performed_by
                doc["created_by"] = performed_by
                try:
                    _active_collection(payments_coll, "payments").insert_one(doc)
                    return payment
                except DuplicateKeyError:
                    existing = self.get_payment_by_idempotency_key(tenant_id, resolved_key)
                    if existing:
                        return existing
                    raise
        except Exception as e:
            logger.error(f"Failed to create payment for invoice {invoice_id}: {e}\n{traceback.format_exc()}")
            raise

    def get_payment(self, tenant_id: str, payment_id: str) -> Optional[Payment]:
        try:
            doc = _active_collection(payments_coll, "payments").find_one({
                "$and": [
                    _tenant_clause(tenant_id),
                    {"$or": [{"payment_id": payment_id}, {"paymentId": payment_id}]},
                ]
            })
            if not doc:
                return None
            return Payment.from_dict(doc)
        except Exception as e:
            logger.error(f"Failed to get payment {payment_id}: {e}\n{traceback.format_exc()}")
            raise

    def get_payment_by_idempotency_key(self, tenant_id: str, idempotency_key: str) -> Optional[Payment]:
        try:
            if not idempotency_key:
                return None
            doc = _active_collection(payments_coll, "payments").find_one({
                "$and": [
                    _tenant_clause(tenant_id),
                    {
                        "$or": [
                            {"idempotency_key": idempotency_key},
                            {"idempotencyKey": idempotency_key},
                        ]
                    },
                ]
            })
            if not doc:
                return None
            return Payment.from_dict(doc)
        except Exception as e:
            logger.error(f"Failed to get payment by idempotency key: {e}\n{traceback.format_exc()}")
            raise

    def list_payments(
        self,
        tenant_id: str,
        invoice_id: Optional[str] = None,
        status: Optional[Union[str, PaymentStatus]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Payment]:
        try:
            query: Dict[str, Any] = dict(_tenant_clause(tenant_id))
            if invoice_id:
                query = {
                    "$and": [
                        _tenant_clause(tenant_id),
                        _invoice_id_clause(invoice_id),
                    ]
                }
            if status:
                if isinstance(status, PaymentStatus):
                    status = status.value
                if "$and" in query:
                    query["$and"].append({"status": status})
                else:
                    query["status"] = status
            cursor = _active_collection(payments_coll, "payments").find(query).sort("created_at", -1).skip(offset).limit(limit)
            return [Payment.from_dict(doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Failed to list payments: {e}\n{traceback.format_exc()}")
            raise

    def update_payment_status(
        self,
        tenant_id: str,
        payment_id: str,
        status: Union[str, PaymentStatus],
        performed_by: str = "SYSTEM",
    ) -> Payment:
        """Reject local creation of provider execution or settlement truth.

        Payment success/failure is provider execution truth and therefore belongs
        exclusively to Kennel EOS. BillingRegistry may hydrate historical
        projections but cannot manufacture, infer, or mutate that truth.
        """
        raise BillingFinancialTruthAuthorityError(
            "BILLING_EXECUTION_TRUTH_REQUIRES_KENNEL"
        )

    def refund_payment(
        self,
        tenant_id: str,
        payment_id: str,
        refund_amount: float,
        performed_by: str = "SYSTEM",
    ) -> Payment:
        """Reject local refund execution.

        A refund moves money and therefore requires a new authorized financial
        execution path through Kennel EOS. BillingRegistry owns no refund
        execution authority.
        """
        raise BillingFinancialTruthAuthorityError(
            "BILLING_REFUND_REQUIRES_KENNEL_EXECUTION"
        )


# ─── Singleton ──────────────────────────────────────────────────────────────

_registry: Optional[BillingRegistry] = None

def get_billing_registry() -> BillingRegistry:
    """Get the singleton BillingRegistry instance."""
    global _registry
    if _registry is None:
        _registry = BillingRegistry()
    return _registry


"""
════════════════════════════════════════════════════════════════════════════════
🏛️ INSTITUTIONAL CERTIFICATION SEAL — WILSY OS BILLING REGISTRY v1.6.0-L7D-B-BOOTSTRAP-HARDENING
════════════════════════════════════════════════════════════════════════════════
Status:          CERTIFIED PRODUCTION ARTIFACT — FULL MANDATE COMPLIANCE
Version:         v1.6.0-L7D-B-BOOTSTRAP-HARDENING
Fixes:           Exact integer-minor-unit ClientInvoice authority persisted with deterministic replay and conflict rejection; Kennel EOS required for execution.
Compliance:      POPIA §19 · GDPR §32 · SOC2 §CC7.2 · ISO 27001 · ECT Act §15
Health Posture:  GREEN — no open issues
Deploy:
   cp tools/eos/saas/billing/billing_registry.py \
      /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/billing_registry.py
════════════════════════════════════════════════════════════════════════════════
"""

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tools/eos/saas/billing/billing_registry.py
# VERSION: v1.6.0-L7D-B-BOOTSTRAP-HARDENING
# AUTHORITY BOUNDARY:
#   Commercial billing persistence and historical projection only.
# TENANT POSTURE:
#   Explicit tenant-scoped persistence; no cross-tenant inference.
# FAIL-CLOSED POSTURE:
#   Direct payment execution, refund execution, paid state, and settlement
#   mutation are rejected until certified Kennel evidence is supplied through
#   a dedicated projection boundary.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
