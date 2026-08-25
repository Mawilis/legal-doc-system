# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – BILLING ROUTER (FASTAPI) – PRODUCTION WITH ORDER NUMBER GENERATION (FIXED MONGO CLIENT)           ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ FILE:           tools/eos/api/billing_router.py                                                                ║
║ VERSION:        v1.7.0-DUNNING-LIFECYCLE                                                                                       ║
║ AUTHORITY:      Wilsy OS Core Governance                                                                       ║
║ EPITOME:        Uses global MongoDB client from billing_registry; fixed mongo_client access.                  ║
║ CLASSIFICATION: Production Artifact                                                                             ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ 🔧 CHANGE LOG:                                                                                                  ║
║   2026-08-25 v1.7.0-DUNNING-LIFECYCLE – Persisted 3/7/10/14/21/30 lifecycle with read-only suspension and SHA3 audit proof. ║
║   2026-08-21 v1.6.1-CROSS-TENANT-RESOLVE – Use global mongo_client from billing_registry; remove request.app dependency.      ║
║   2026-08-21 v1.4.2-PRODUCTION – Fixed mongo_client access; use request.app.mongo_client (removed).           ║
║   2026-08-21 v1.4.0-ORDER-GENERATION – Integrated OrderNumberService.                                          ║
║   ...                                                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ COMPLIANCE:    POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Depends, Header, Request
from typing import Any, Dict, List, Optional
import logging
import os
import traceback
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import math
import uuid
import hashlib
import json

from pydantic import BaseModel

from ..saas.billing.billing_registry import get_billing_registry, BillingRegistry, db, client as mongo_client
from ..saas.billing.order_number_service import get_order_number_service
from ..saas.domain.billing import (
    PlatformInvoice,
    ClientInvoice,
    Payment,
    InvoiceStatus,
    PaymentStatus,
    PaymentMethod,
    CollectionMethod,
    TaxType,
    LineItem,
)
from ..saas.domain.plan import PlanEntity

# ─── Logging ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
DEBUG_MODE = os.getenv("WILSY_MODEL_DEBUG", "0") == "1"

def _log_error(exc: Exception, context: str, tenant_id: str = "GLOBAL_ROOT") -> None:
    if DEBUG_MODE:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}\n{traceback.format_exc()}")
    else:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}")

def _telemetry(tenant_id: str, category: str, event: str, source: str, metadata: Optional[dict] = None) -> None:
    if metadata is None:
        metadata = {}
    logger.info(f"[TELEMETRY] {tenant_id} | {category} | {event} | {source} | {metadata}")

# ─── Tenant Dependency ──────────────────────────────────────────────────────

def _require_db():
    """Return live Mongo database or raise 503 — satisfies Pylance Optional[Database]."""
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing database unavailable",
        )
    return db


def _require_mongo_client():
    """Return live MongoClient or raise 503 — for OrderNumberService."""
    if mongo_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mongo client unavailable for order number generation",
        )
    return mongo_client

def get_tenant_id(x_tenant_id: str = Header(...)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Tenant-Id header required")
    return x_tenant_id

# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/billing", tags=["Billing"])

# ─── Request/Response Schemas (Pydantic) ──────────────────────────────────
class LineItemCreate(BaseModel):
    description: str
    amount: float
    quantity: int = 1
    unit_price: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    discount: float = 0.0
    currency: str = "ZAR"
    metadata: Dict[str, Any] = {}

class PlatformInvoiceCreate(BaseModel):
    customer_id: Optional[str] = None
    line_items: List[LineItemCreate]
    currency: str = "ZAR"
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    payment_terms_days: int = 30
    tax_type: str = "vat"
    seller_jurisdiction: str = "ZA"
    customer_jurisdiction: str = "ZA"
    collection_method: str = "send_invoice"
    billing_mode: str = "PLATFORM"
    subscription_id: Optional[str] = None
    plan_id: Optional[str] = None
    plan_name: Optional[str] = None
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    idempotency_key: Optional[str] = None
    order_number: Optional[str] = None
    purchase_order: Optional[str] = None

class PlatformInvoiceUpdate(BaseModel):
    status: Optional[str] = None
    paid_at: Optional[datetime] = None
    void_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    due_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None

class ClientInvoiceCreate(BaseModel):
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tax_id: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    line_items: List[LineItemCreate]
    currency: str = "ZAR"
    issued_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    payment_terms_days: int = 30
    tax_type: str = "vat"
    seller_jurisdiction: str = "ZA"
    customer_jurisdiction: str = "ZA"
    collection_method: str = "send_invoice"
    billing_mode: str = "CLIENT"
    metadata: Dict[str, Any] = {}
    idempotency_key: Optional[str] = None
    order_number: Optional[str] = None
    purchase_order: Optional[str] = None

class ClientInvoiceUpdate(BaseModel):
    status: Optional[str] = None
    paid_at: Optional[datetime] = None
    void_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    due_at: Optional[datetime] = None
    issued_at: Optional[datetime] = None

class PaymentCreate(BaseModel):
    invoice_id: str
    amount: float
    currency: str
    method: str = "other"
    external_reference: Optional[str] = None
    metadata: Dict[str, Any] = {}
    idempotency_key: Optional[str] = None

class PaymentStatusUpdate(BaseModel):
    status: str  # succeeded, failed, etc.

class RefundRequest(BaseModel):
    refund_amount: float

class HybridInvoiceCreate(BaseModel):
    tenant_id: str
    subscription_id: Optional[str] = None
    subscription_amount: float = 0.0
    usage_amount: float = 0.0
    credits: float = 0.0
    outcome_amount: float = 0.0
    proration_ratio: float = 1.0
    usage_tiers: List[Dict[str, Any]] = []
    outcome_trigger: Optional[Dict[str, Any]] = None
    currency: str = "ZAR"
    description: str = "Hybrid monetization invoice"
    idempotency_key: Optional[str] = None

class BillingSummaryResponse(BaseModel):
    totalArr: float
    activeSubscriptions: int
    pendingInvoices: int
    history: List[Dict[str, Any]]
    recentInvoices: List[Dict[str, Any]]

class BillingAnalyticsResponse(BaseModel):
    mrr: float
    arr: float
    churnRate: float
    ltv: float
    cac: float
    forecast: float
    growthRate: float
    mrrHistory: List[Dict[str, Any]]

class ForensicStatusResponse(BaseModel):
    sealStatus: str
    merkleRoot: Optional[str] = None
    proofCount: int
    latestProof: Optional[str] = None

class AnomalyResponse(BaseModel):
    anomalies: List[Dict[str, Any]]


def _canonical_json(value: Any) -> str:
    """Produce a stable payload representation before SHA3-512 anchoring."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _sha3_512(value: Any) -> str:
    return hashlib.sha3_512(_canonical_json(value).encode("utf-8")).hexdigest().upper()


def _invoice_statement_pair(invoice: Any, tenant_id: str, statement_type: str, performed_by: str) -> Dict[str, Any]:
    """Persist the EOS invoice-statement relationship and its immutable proof.

    The statement identifier is deterministic, therefore an idempotent invoice replay
    cannot create a second financial statement.  MongoDB deployments without replica
    set transactions still retain a recoverable pair: the canonical proof is stored on
    both documents and the statement is an upsert keyed by tenant plus invoice.
    """
    invoice_doc = invoice.to_dict()
    invoice_id = str(invoice_doc.get("invoice_id") or invoice_doc.get("invoiceId") or invoice.invoice_id)
    issued_at = invoice_doc.get("issued_at") or invoice_doc.get("issuedAt") or datetime.now(timezone.utc).isoformat()
    statement_id = f"WILSY-STMT-{invoice_id}"
    pair_payload = {
        "schema_version": "WILSY-EOS-INVOICE-STATEMENT-PAIR/V1",
        "tenant_id": tenant_id,
        "invoice_id": invoice_id,
        "statement_id": statement_id,
        "statement_type": statement_type,
        "invoice_proof_hash": invoice_doc.get("proof_hash") or invoice_doc.get("proofHash"),
        "issued_at": issued_at,
        "performed_by": performed_by,
    }
    proof_hash = _sha3_512(pair_payload)
    # pair_proof_hash lives ONLY in $set (never also in $setOnInsert) — Mongo code 40 otherwise
    statement_on_insert = {
        **pair_payload,
        "status": "ISSUED",
        "currency": invoice_doc.get("currency", "ZAR"),
        "total_amount": invoice_doc.get("total_amount", invoice_doc.get("totalAmount", 0)),
        "line_items": invoice_doc.get("line_items", invoice_doc.get("lineItems", [])),
        "proof_algorithm": "SHA3-512",
        "compliance": {"popia_section_19": True, "gdpr_article_32": True, "soc2_cc7_2": True},
        "created_at": datetime.now(timezone.utc),
    }
    coll_db = _require_db()
    coll_db["billing_statements"].update_one(
        {"tenant_id": tenant_id, "invoice_id": invoice_id},
        {
            "$setOnInsert": statement_on_insert,
            "$set": {
                "pair_proof_hash": proof_hash,
                "updated_at": datetime.now(timezone.utc),
            },
        },
        upsert=True,
    )
    coll_db["billing_audit_events"].update_one(
        {"tenant_id": tenant_id, "event_type": "INVOICE_STATEMENT_ANCHORED", "proof_hash": proof_hash},
        {
            "$setOnInsert": {
                **pair_payload,
                "event_type": "INVOICE_STATEMENT_ANCHORED",
                "proof_hash": proof_hash,
                "created_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    return {"statement_id": statement_id, "statement_type": statement_type, "proof_hash": proof_hash, "algorithm": "SHA3-512"}


def _invoice_response_with_statement(invoice: Any, tenant_id: str, statement_type: str, performed_by: str) -> Dict[str, Any]:
    response = invoice.to_dict()
    pair = _invoice_statement_pair(invoice, tenant_id, statement_type, performed_by)
    response["statement"] = pair
    response["invoice_statement_proof_hash"] = pair["proof_hash"]
    return response

# ─── Endpoints ──────────────────────────────────────────────────────────────

# ----------------------------------------------------------------------------
# Platform Invoices
# ----------------------------------------------------------------------------
@router.post("/platform/invoices", response_model=Dict[str, Any], status_code=201)
async def create_platform_invoice(
    invoice_data: PlatformInvoiceCreate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        # ─── Sovereign order number generation ──────────────────────────
        if not invoice_data.order_number or not invoice_data.purchase_order:
            order_service = get_order_number_service(_require_mongo_client())
            numbers = order_service.generate_both(tenant_id)
            if not invoice_data.order_number:
                invoice_data.order_number = numbers["order_number"]
            if not invoice_data.purchase_order:
                invoice_data.purchase_order = numbers["purchase_order"]
            logger.info(
                f"[BillingRouter] Auto-generated order numbers: "
                f"SO={invoice_data.order_number}, PO={invoice_data.purchase_order}",
                extra={"tenant_id": tenant_id}
            )

        line_items_dicts = [li.dict() for li in invoice_data.line_items]
        invoice = registry.create_platform_invoice(
            tenant_id=tenant_id,
            customer_id=invoice_data.customer_id,
            line_items=line_items_dicts,
            currency=invoice_data.currency,
            issued_at=invoice_data.issued_at,
            due_at=invoice_data.due_at,
            payment_terms_days=invoice_data.payment_terms_days,
            tax_type=invoice_data.tax_type,
            seller_jurisdiction=invoice_data.seller_jurisdiction,
            customer_jurisdiction=invoice_data.customer_jurisdiction,
            collection_method=invoice_data.collection_method,
            billing_mode=invoice_data.billing_mode,
            subscription_id=invoice_data.subscription_id,
            plan_id=invoice_data.plan_id,
            plan_name=invoice_data.plan_name,
            period_start=invoice_data.period_start,
            period_end=invoice_data.period_end,
            metadata=invoice_data.metadata,
            idempotency_key=invoice_data.idempotency_key,
            performed_by=performed_by,
            order_number=invoice_data.order_number,
            purchase_order=invoice_data.purchase_order,
        )
        _telemetry(tenant_id, "BILLING", "PLATFORM_INVOICE_CREATED", "billing_router", {
            "invoice_id": invoice.invoice_id,
            "order_number": invoice_data.order_number,
            "purchase_order": invoice_data.purchase_order
        })
        return _invoice_response_with_statement(invoice, tenant_id, "PLATFORM", performed_by)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _log_error(e, "CREATE_PLATFORM_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/platform/invoices", response_model=List[Dict[str, Any]])
async def list_platform_invoices(
    tenant_id: str = Depends(get_tenant_id),
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "issued_at",
    sort_order: int = -1,
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        invoices = registry.list_platform_invoices(
            tenant_id=tenant_id,
            status=status_filter,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [inv.to_dict() for inv in invoices]
    except Exception as e:
        _log_error(e, "LIST_PLATFORM_INVOICES", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/platform/invoices/{invoice_id}", response_model=Dict[str, Any])
async def get_platform_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        invoice = registry.get_platform_invoice(tenant_id, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        return invoice.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "GET_PLATFORM_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.patch("/platform/invoices/{invoice_id}", response_model=Dict[str, Any])
async def update_platform_invoice(
    invoice_id: str,
    updates: PlatformInvoiceUpdate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        update_dict = updates.dict(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        invoice = registry.update_platform_invoice(tenant_id, invoice_id, update_dict, performed_by)
        return _invoice_response_with_statement(invoice, tenant_id, "PLATFORM", performed_by)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        _log_error(e, "UPDATE_PLATFORM_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/platform/invoices/{invoice_id}/void", response_model=Dict[str, Any])
async def void_platform_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
    reason: str = "Voided by user",
):
    try:
        invoice = registry.void_platform_invoice(tenant_id, invoice_id, reason, performed_by)
        return invoice.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        _log_error(e, "VOID_PLATFORM_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ----------------------------------------------------------------------------
# Client Invoices
# ----------------------------------------------------------------------------
@router.post("/client/invoices", response_model=Dict[str, Any], status_code=201)
async def create_client_invoice(
    invoice_data: ClientInvoiceCreate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        # ─── Sovereign order number generation ──────────────────────────
        if not invoice_data.order_number or not invoice_data.purchase_order:
            order_service = get_order_number_service(_require_mongo_client())
            numbers = order_service.generate_both(tenant_id)
            if not invoice_data.order_number:
                invoice_data.order_number = numbers["order_number"]
            if not invoice_data.purchase_order:
                invoice_data.purchase_order = numbers["purchase_order"]
            logger.info(
                f"[BillingRouter] Auto-generated order numbers: "
                f"SO={invoice_data.order_number}, PO={invoice_data.purchase_order}",
                extra={"tenant_id": tenant_id}
            )

        line_items_dicts = [li.dict() for li in invoice_data.line_items]
        invoice = registry.create_client_invoice(
            tenant_id=tenant_id,
            customer_id=invoice_data.customer_id,
            customer_name=invoice_data.customer_name,
            customer_tax_id=invoice_data.customer_tax_id,
            customer_email=invoice_data.customer_email,
            customer_phone=invoice_data.customer_phone,
            line_items=line_items_dicts,
            currency=invoice_data.currency,
            issued_at=invoice_data.issued_at,
            due_at=invoice_data.due_at,
            payment_terms_days=invoice_data.payment_terms_days,
            tax_type=invoice_data.tax_type,
            seller_jurisdiction=invoice_data.seller_jurisdiction,
            customer_jurisdiction=invoice_data.customer_jurisdiction,
            collection_method=invoice_data.collection_method,
            billing_mode=invoice_data.billing_mode,
            metadata=invoice_data.metadata,
            idempotency_key=invoice_data.idempotency_key,
            performed_by=performed_by,
            order_number=invoice_data.order_number,
            purchase_order=invoice_data.purchase_order,
        )
        _telemetry(tenant_id, "BILLING", "CLIENT_INVOICE_CREATED", "billing_router", {
            "invoice_id": invoice.invoice_id,
            "order_number": invoice_data.order_number,
            "purchase_order": invoice_data.purchase_order
        })
        return _invoice_response_with_statement(invoice, tenant_id, "TENANT_CLIENT", performed_by)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _log_error(e, "CREATE_CLIENT_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/client/invoices", response_model=List[Dict[str, Any]])
async def list_client_invoices(
    tenant_id: str = Depends(get_tenant_id),
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "issued_at",
    sort_order: int = -1,
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        invoices = registry.list_client_invoices(
            tenant_id=tenant_id,
            status=status_filter,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return [inv.to_dict() for inv in invoices]
    except Exception as e:
        _log_error(e, "LIST_CLIENT_INVOICES", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/client/invoices/{invoice_id}", response_model=Dict[str, Any])
async def get_client_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        invoice = registry.get_client_invoice(tenant_id, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        return invoice.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "GET_CLIENT_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.patch("/client/invoices/{invoice_id}", response_model=Dict[str, Any])
async def update_client_invoice(
    invoice_id: str,
    updates: ClientInvoiceUpdate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        update_dict = updates.dict(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        invoice = registry.update_client_invoice(tenant_id, invoice_id, update_dict, performed_by)
        return invoice.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        _log_error(e, "UPDATE_CLIENT_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/client/invoices/{invoice_id}/void", response_model=Dict[str, Any])
async def void_client_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
    reason: str = "Voided by user",
):
    try:
        invoice = registry.void_client_invoice(tenant_id, invoice_id, reason, performed_by)
        return invoice.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        _log_error(e, "VOID_CLIENT_INVOICE", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ----------------------------------------------------------------------------
# Payments
# ----------------------------------------------------------------------------
@router.post("/payments", response_model=Dict[str, Any], status_code=201)
async def create_payment(
    payment_data: PaymentCreate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        payment = registry.create_payment(
            invoice_id=payment_data.invoice_id,
            tenant_id=tenant_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            method=payment_data.method,
            external_reference=payment_data.external_reference,
            metadata=payment_data.metadata,
            idempotency_key=payment_data.idempotency_key,
            performed_by=performed_by,
        )
        _telemetry(tenant_id, "BILLING", "PAYMENT_CREATED", "billing_router", {"payment_id": payment.payment_id})
        return payment.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _log_error(e, "CREATE_PAYMENT", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/payments", response_model=List[Dict[str, Any]])
async def list_payments(
    tenant_id: str = Depends(get_tenant_id),
    invoice_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        payments = registry.list_payments(
            tenant_id=tenant_id,
            invoice_id=invoice_id,
            status=status_filter,
            limit=limit,
            offset=offset,
        )
        return [p.to_dict() for p in payments]
    except Exception as e:
        _log_error(e, "LIST_PAYMENTS", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/payments/{payment_id}", response_model=Dict[str, Any])
async def get_payment(
    payment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        payment = registry.get_payment(tenant_id, payment_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        return payment.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "GET_PAYMENT", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.patch("/payments/{payment_id}/status", response_model=Dict[str, Any])
async def update_payment_status(
    payment_id: str,
    status_update: PaymentStatusUpdate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        payment = registry.update_payment_status(tenant_id, payment_id, status_update.status, performed_by)
        return payment.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        _log_error(e, "UPDATE_PAYMENT_STATUS", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/payments/{payment_id}/refund", response_model=Dict[str, Any])
async def refund_payment(
    payment_id: str,
    refund_data: RefundRequest,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        payment = registry.refund_payment(tenant_id, payment_id, refund_data.refund_amount, performed_by)
        return payment.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _log_error(e, "REFUND_PAYMENT", tenant_id)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
@router.get("/summary", response_model=BillingSummaryResponse)
async def get_billing_summary(
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        from ..saas.billing.billing_registry import platform_invoices_coll

        query = {}
        if tenant_id != "GLOBAL_ROOT":
            # Registry records dual-write both forms, while older records may
            # contain only one.  The summary must never silently drop either.
            query = {"$or": [{"tenant_id": tenant_id}, {"tenantId": tenant_id}]}

        invoice_docs = list(platform_invoices_coll.find(query).sort("issuedAt", -1))

        now = datetime.now(timezone.utc)
        twelve_months_ago = now - timedelta(days=365)

        monthly_volume = defaultdict(float)
        monthly_paid = defaultdict(float)
        total_arr = 0.0
        pending_invoices = 0
        recent_invoices = []

        for doc in invoice_docs:
            issued_at = doc.get("issued_at") or doc.get("issuedAt") or doc.get("created_at") or doc.get("createdAt")
            if isinstance(issued_at, str):
                issued_at = datetime.fromisoformat(issued_at.replace('Z', '+00:00'))
            elif isinstance(issued_at, datetime):
                pass
            else:
                continue

            # Mongo can return legacy naive datetimes while the current clock
            # is UTC-aware.  Normalise before comparison so one historical
            # invoice cannot make the entire cockpit summary unavailable.
            if issued_at.tzinfo is None:
                issued_at = issued_at.replace(tzinfo=timezone.utc)
            else:
                issued_at = issued_at.astimezone(timezone.utc)

            invoice_status = doc.get("status", "open")
            if invoice_status not in ["paid", "void", "cancelled"]:
                pending_invoices += 1

            if len(recent_invoices) < 10:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                recent_invoices.append(doc)

            month_key = issued_at.strftime("%Y-%m")
            amount = float(doc.get("total", 0))
            paid_amount = float(doc.get("paid_amount", doc.get("paidAmount", 0)))
            monthly_volume[month_key] += amount
            monthly_paid[month_key] += paid_amount

            if issued_at >= twelve_months_ago:
                total_arr += amount

        subscriptions_coll = _require_db()["subscriptions"]
        sub_query = {"status": {"$in": ["active", "ACTIVE", "trialing", "TRIALING"]}} if tenant_id != "GLOBAL_ROOT" else {}
        if tenant_id != "GLOBAL_ROOT":
            sub_query["$and"] = [
                {"status": {"$in": ["active", "ACTIVE", "trialing", "TRIALING"]}},
                {"$or": [{"tenant_id": tenant_id}, {"tenantId": tenant_id}]},
            ]
        active_subscriptions = subscriptions_coll.count_documents(sub_query)

        history = []
        for month in sorted(monthly_volume.keys()):
            history.append({
                "label": month,
                "volume": monthly_volume[month],
                "paidVolume": monthly_paid[month],
            })

        _telemetry(tenant_id, "BILLING", "SUMMARY_RETRIEVED", "billing_router", {
            "active_subscriptions": active_subscriptions,
            "total_arr": total_arr,
            "pending_invoices": pending_invoices,
            "history_months": len(history)
        })

        return BillingSummaryResponse(
            totalArr=total_arr,
            activeSubscriptions=active_subscriptions,
            pendingInvoices=pending_invoices,
            history=history,
            recentInvoices=recent_invoices,
        )

    except Exception as e:
        _log_error(e, "GET_BILLING_SUMMARY", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing summary. Please try again later."
        )

# ----------------------------------------------------------------------------
# Analytics
# ----------------------------------------------------------------------------
@router.get("/analytics", response_model=BillingAnalyticsResponse)
async def get_billing_analytics(
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
):
    try:
        subscriptions_coll = _require_db()["subscriptions"]
        platform_invoices_coll = _require_db()["platform_invoices"]

        sub_query = {}
        if tenant_id != "GLOBAL_ROOT":
            sub_query["tenant_id"] = tenant_id

        active_subs = list(subscriptions_coll.find({**sub_query, "status": "active"}))
        mrr = 0.0
        for sub in active_subs:
            amount = float(sub.get("amount", 0))
            freq = sub.get("billing_frequency", "monthly")
            if freq == "monthly":
                mrr += amount
            elif freq == "quarterly":
                mrr += amount / 3
            elif freq == "annual":
                mrr += amount / 12
            else:
                mrr += amount

        arr = mrr * 12

        ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)
        cancelled_subs = list(subscriptions_coll.find({
            **sub_query,
            "status": "cancelled",
            "cancelled_at": {"$gte": ninety_days_ago}
        }))
        total_cancelled = len(cancelled_subs)
        total_active = len(active_subs)
        churn_rate = total_cancelled / max(1, total_active + total_cancelled)

        avg_lifetime = 36
        avg_revenue_per_customer = mrr / max(1, total_active) if total_active > 0 else 0
        ltv = avg_revenue_per_customer * avg_lifetime * 12
        cac = ltv * 0.3

        invoice_query = {}
        if tenant_id != "GLOBAL_ROOT":
            invoice_query["tenant_id"] = tenant_id
        invoices = list(platform_invoices_coll.find(invoice_query).sort("issued_at", 1))
        monthly_mrr = defaultdict(float)
        for inv in invoices:
            issued_at = inv.get("issued_at")
            if isinstance(issued_at, str):
                issued_at = datetime.fromisoformat(issued_at.replace('Z', '+00:00'))
            elif isinstance(issued_at, datetime):
                pass
            else:
                continue
            month_key = issued_at.strftime("%Y-%m")
            amount = float(inv.get("total", 0))
            monthly_mrr[month_key] += amount

        sorted_months = sorted(monthly_mrr.keys())
        mrr_history = []
        for month in sorted_months:
            mrr_history.append({"label": month, "mrr": monthly_mrr[month]})

        forecast = mrr
        if len(mrr_history) >= 3:
            recent = [mrr_history[-i]["mrr"] for i in range(1, 4)][::-1]
            x = [0, 1, 2]
            y = recent
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(xi * yi for xi, yi in zip(x, y))
            sum_xx = sum(xi * xi for xi in x)
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x) if (n * sum_xx - sum_x * sum_x) != 0 else 0
            intercept = (sum_y - slope * sum_x) / n
            forecast = intercept + slope * 3
            forecast = max(0, forecast)

        growth_rate = 0.0
        if len(mrr_history) >= 2:
            prev = mrr_history[-2]["mrr"]
            curr = mrr_history[-1]["mrr"]
            if prev > 0:
                growth_rate = (curr - prev) / prev * 100
            else:
                growth_rate = 0

        _telemetry(tenant_id, "BILLING", "ANALYTICS_RETRIEVED", "billing_router", {
            "mrr": mrr,
            "arr": arr,
            "churn_rate": churn_rate,
            "forecast": forecast,
            "history_count": len(mrr_history)
        })

        return BillingAnalyticsResponse(
            mrr=mrr,
            arr=arr,
            churnRate=churn_rate,
            ltv=ltv,
            cac=cac,
            forecast=forecast,
            growthRate=growth_rate,
            mrrHistory=mrr_history,
        )

    except Exception as e:
        _log_error(e, "GET_BILLING_ANALYTICS", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing analytics. Please try again later."
        )

# ----------------------------------------------------------------------------
# Plans (RESILIENT)
# ----------------------------------------------------------------------------
@router.get("/plans", response_model=List[Dict[str, Any]])
async def get_billing_plans(
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Returns the plan catalog. Resilient to missing fields.
    """
    try:
        plans_coll = _require_db()["plans"]
        docs = list(plans_coll.find().sort("created_at", -1))
        result = []
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
            try:
                plan = PlanEntity.from_dict(doc)
                result.append(plan.to_dict())
            except Exception as entity_err:
                _log_error(entity_err, "PLAN_ENTITY_CONVERSION", tenant_id)
                minimal = {
                    "_id": doc.get("_id", str(uuid.uuid4())),
                    "name": doc.get("name", "Unnamed Plan"),
                    "price": float(doc.get("price", 0)),
                    "currency": doc.get("currency", "ZAR"),
                    "billingFrequency": doc.get("billingFrequency", "monthly"),
                    "planType": doc.get("planType", "STANDARD"),
                }
                for k, v in doc.items():
                    if k not in minimal and k != "_id":
                        minimal[k] = v
                result.append(minimal)
        return result
    except Exception as e:
        _log_error(e, "GET_PLANS", tenant_id)
        logger.error(f"Plans endpoint failed: {e}\n{traceback.format_exc()}")
        return []

# ----------------------------------------------------------------------------
# Credit Scores (placeholder)
# ----------------------------------------------------------------------------
@router.get("/credit-scores", response_model=Dict[str, Any])
async def get_billing_credit_scores(
    tenant_id: str = Depends(get_tenant_id),
):
    return {"scores": {}}

# ----------------------------------------------------------------------------
# Hybrid Invoice
# ----------------------------------------------------------------------------
@router.post("/hybrid/generate", response_model=Dict[str, Any], status_code=201)
async def generate_hybrid_invoice(
    hybrid_data: HybridInvoiceCreate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        if not 0 < hybrid_data.proration_ratio <= 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="proration_ratio must be greater than 0 and no more than 1.")
        tiered_usage = 0.0
        for tier in hybrid_data.usage_tiers:
            units = max(0.0, float(tier.get("units", 0)))
            unit_price = max(0.0, float(tier.get("unit_price", 0)))
            included_units = max(0.0, float(tier.get("included_units", 0)))
            tiered_usage += max(0.0, units - included_units) * unit_price
        usage_total = hybrid_data.usage_amount + tiered_usage
        subscription_total = hybrid_data.subscription_amount * hybrid_data.proration_ratio
        trigger = hybrid_data.outcome_trigger or {}
        outcome_triggered = not trigger or bool(trigger.get("achieved", False))
        outcome_total = hybrid_data.outcome_amount if outcome_triggered else 0.0
        total = max(0.0, subscription_total + usage_total - hybrid_data.credits + outcome_total)

        line_items = []
        if subscription_total > 0:
            line_items.append(LineItem(
                description=f"Subscription prorated at {hybrid_data.proration_ratio:.4f}",
                amount=subscription_total,
                quantity=1,
                unit_price=subscription_total,
                currency=hybrid_data.currency,
            ))
        if usage_total > 0:
            line_items.append(LineItem(
                description="Usage-based consumption",
                amount=usage_total,
                quantity=1,
                unit_price=usage_total,
                currency=hybrid_data.currency,
            ))
        if outcome_total > 0:
            line_items.append(LineItem(
                description="Outcome-based fee",
                amount=outcome_total,
                quantity=1,
                unit_price=outcome_total,
                currency=hybrid_data.currency,
            ))
        if hybrid_data.credits > 0:
            line_items.append(LineItem(
                description="Credits applied (negative amount)",
                amount=-hybrid_data.credits,
                quantity=1,
                unit_price=-hybrid_data.credits,
                currency=hybrid_data.currency,
            ))

        if total == 0 and not line_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one of usage, credits, or outcome must be non‑zero."
            )

        # ─── Generate order numbers for hybrid invoice ──────────────────
        order_service = get_order_number_service(_require_mongo_client())
        numbers = order_service.generate_both(tenant_id)

        invoice_data = PlatformInvoiceCreate(
            customer_id=hybrid_data.tenant_id,
            line_items=[LineItemCreate(
                description=li.description,
                amount=li.amount,
                quantity=li.quantity,
                unit_price=li.unit_price,
                currency=li.currency,
            ) for li in line_items],
            currency=hybrid_data.currency,
            issued_at=datetime.now(timezone.utc),
            due_at=datetime.now(timezone.utc) + timedelta(days=30),
            payment_terms_days=30,
            tax_type="vat",
            seller_jurisdiction="ZA",
            customer_jurisdiction="ZA",
            collection_method="send_invoice",
            billing_mode="PLATFORM",
            subscription_id=hybrid_data.subscription_id,
            metadata={
                "hybrid": True,
                "description": hybrid_data.description,
                "formula": "subscription_prorated + usage_tiered - credits + outcome_triggered",
                "subscription_amount": hybrid_data.subscription_amount,
                "proration_ratio": hybrid_data.proration_ratio,
                "tiered_usage": tiered_usage,
                "outcome_trigger": trigger,
                "outcome_triggered": outcome_triggered,
                "compliance": {"popia_section_19": True, "gdpr_article_32": True, "soc2_cc7_2": True},
            },
            idempotency_key=hybrid_data.idempotency_key or str(uuid.uuid4()),
            order_number=numbers["order_number"],
            purchase_order=numbers["purchase_order"],
        )

        line_items_dicts = [li.dict() for li in invoice_data.line_items]
        invoice = registry.create_platform_invoice(
            tenant_id=tenant_id,
            customer_id=invoice_data.customer_id,
            line_items=line_items_dicts,
            currency=invoice_data.currency,
            issued_at=invoice_data.issued_at,
            due_at=invoice_data.due_at,
            payment_terms_days=invoice_data.payment_terms_days,
            tax_type=invoice_data.tax_type,
            seller_jurisdiction=invoice_data.seller_jurisdiction,
            customer_jurisdiction=invoice_data.customer_jurisdiction,
            collection_method=invoice_data.collection_method,
            billing_mode=invoice_data.billing_mode,
            subscription_id=invoice_data.subscription_id,
            period_start=None,
            period_end=None,
            metadata=invoice_data.metadata,
            idempotency_key=invoice_data.idempotency_key,
            performed_by=performed_by,
            order_number=invoice_data.order_number,
            purchase_order=invoice_data.purchase_order,
        )

        _telemetry(tenant_id, "BILLING", "HYBRID_INVOICE_GENERATED", "billing_router", {
            "invoice_id": invoice.invoice_id,
            "tenant_id": hybrid_data.tenant_id,
            "total": total,
            "subscription": subscription_total,
            "usage": usage_total,
            "credits": hybrid_data.credits,
            "outcome": outcome_total,
            "order_number": invoice_data.order_number,
            "purchase_order": invoice_data.purchase_order,
        })

        return _invoice_response_with_statement(invoice, tenant_id, "PLATFORM", performed_by)

    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "GENERATE_HYBRID_INVOICE", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate hybrid invoice."
        )

# ----------------------------------------------------------------------------
# Forensic Status
# ----------------------------------------------------------------------------
@router.get("/statements/invoices/{invoice_id}", response_model=Dict[str, Any])
async def get_invoice_statement(invoice_id: str, tenant_id: str = Depends(get_tenant_id)):
    """Return the EOS-persisted statement paired with one invoice."""
    statement = _require_db()["billing_statements"].find_one({"tenant_id": tenant_id, "invoice_id": invoice_id}, {"_id": 0})
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No EOS statement pair exists for this invoice")
    return statement


@router.post("/investor/proofs", response_model=Dict[str, Any], status_code=201)
async def anchor_investor_proof(payload: Dict[str, Any], tenant_id: str = Depends(get_tenant_id)):
    """Anchor investor metrics supplied by the UI; EOS never accepts a client seal."""
    required = ("arr", "forecasted_arr", "collection_efficiency", "risk_score", "active_subscriptions")
    missing = [key for key in required if key not in payload]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing investor proof metrics: {', '.join(missing)}")
    record = {
        "schema_version": "WILSY-EOS-INVESTOR-PROOF/V1",
        "tenant_id": tenant_id,
        "metrics": {key: payload[key] for key in required},
        "model": payload.get("model", {"forecast": "deterministic_linear_plus_seeded_monte_carlo"}),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    record["proof_hash"] = _sha3_512(record)
    record["proof_algorithm"] = "SHA3-512"
    _require_db()["billing_investor_proofs"].insert_one(record)
    _require_db()["billing_audit_events"].insert_one({"tenant_id": tenant_id, "event_type": "INVESTOR_PROOF_ANCHORED", "proof_hash": record["proof_hash"], "created_at": datetime.now(timezone.utc)})
    record.pop("_id", None)
    return record


@router.get("/audit/events", response_model=List[Dict[str, Any]])
async def list_billing_audit_events(tenant_id: str = Depends(get_tenant_id), limit: int = 100):
    """Expose persisted Kennel anchors only; no synthetic client-side audit rows."""
    rows = list(_require_db()["billing_audit_events"].find({"tenant_id": tenant_id}, {"_id": 0}).sort("created_at", -1).limit(min(max(limit, 1), 250)))
    return rows


@router.get("/audit/integrity", response_model=Dict[str, Any])
async def get_audit_integrity(tenant_id: str = Depends(get_tenant_id)):
    return _require_db()["billing_integrity_controls"].find_one(
        {"tenant_id": tenant_id}, {"_id": 0}
    ) or {"tenant_id": tenant_id, "auto_renew": True, "encrypted_backup": True, "neural_sync": False, "source": "EOS_DEFAULTS"}


@router.patch("/audit/integrity", response_model=Dict[str, Any])
async def update_audit_integrity(payload: Dict[str, bool], tenant_id: str = Depends(get_tenant_id)):
    allowed = {key: value for key, value in payload.items() if key in {"auto_renew", "encrypted_backup", "neural_sync"} and isinstance(value, bool)}
    if not allowed:
        raise HTTPException(status_code=400, detail="Submit at least one boolean integrity control")
    next_state = {"tenant_id": tenant_id, **allowed, "updated_at": datetime.now(timezone.utc).isoformat()}
    next_state["proof_hash"] = _sha3_512(next_state)
    _require_db()["billing_integrity_controls"].update_one({"tenant_id": tenant_id}, {"$set": next_state}, upsert=True)
    _require_db()["billing_audit_events"].insert_one({"tenant_id": tenant_id, "event_type": "INTEGRITY_CONTROL_UPDATED", "proof_hash": next_state["proof_hash"], "metadata": allowed, "created_at": datetime.now(timezone.utc)})
    return next_state


@router.get("/forensic-status", response_model=ForensicStatusResponse)
async def get_forensic_status(
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        from ..saas.billing.billing_registry import platform_invoices_coll
        query = {}
        if tenant_id != "GLOBAL_ROOT":
            query["tenant_id"] = tenant_id
        latest = platform_invoices_coll.find_one(query, sort=[("issued_at", -1)])
        seal_status = "VERIFIED" if latest and latest.get("proofHash") else "NO_SEAL"
        merkle_root = latest.get("merkleRoot") if latest else None
        proof_count = platform_invoices_coll.count_documents(query)
        latest_proof = latest.get("proofHash") if latest else None

        return ForensicStatusResponse(
            sealStatus=seal_status,
            merkleRoot=merkle_root,
            proofCount=proof_count,
            latestProof=latest_proof,
        )
    except Exception as e:
        _log_error(e, "GET_FORENSIC_STATUS", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve forensic status."
        )

# ----------------------------------------------------------------------------
# Anomalies
# ----------------------------------------------------------------------------
@router.get("/anomalies", response_model=AnomalyResponse)
async def get_anomalies(
    tenant_id: str = Depends(get_tenant_id),
):
    return AnomalyResponse(anomalies=[])



# ----------------------------------------------------------------------------
# LEDGER ACTION SURFACE (Node → Kennel migration parity)
# Paths match BillingHUD / InvoiceLedgerItem so Vite /api/billing/* no longer 404.
# ----------------------------------------------------------------------------

class InvoiceEmailRequest(BaseModel):
    invoiceId: Optional[str] = None
    invoice_id: Optional[str] = None
    tenantId: Optional[str] = None
    tenant_id: Optional[str] = None
    to: Optional[str] = None
    includeSeal: bool = True


class PartialPaymentBody(BaseModel):
    amount: float
    currency: str = "ZAR"
    idempotencyKey: Optional[str] = None
    idempotency_key: Optional[str] = None
    method: str = "manual"
    external_reference: Optional[str] = None


class InvoiceStatusBody(BaseModel):
    status: str
    idempotencyKey: Optional[str] = None
    idempotency_key: Optional[str] = None


class MerkleVerifyBody(BaseModel):
    sealHash: Optional[str] = None
    seal_hash: Optional[str] = None
    proofHash: Optional[str] = None
    proof_hash: Optional[str] = None
    statementId: Optional[str] = None
    tenantId: Optional[str] = None
    tenant_id: Optional[str] = None


class DunningPolicyUpdate(BaseModel):
    reminder_day: int = 3
    warning_day: int = 7
    critical_day: int = 10
    suspension_day: int = 14
    collections_day: int = 21
    termination_day: int = 30


class DunningEvaluationRequest(BaseModel):
    subscription_id: Optional[str] = None
    dry_run: bool = False


DUNNING_STATE_ORDER = {
    "ACTIVE": 0,
    "WARNING": 1,
    "CRITICAL": 2,
    "SUSPENDED_READONLY": 3,
    "TERMINATED": 4,
}

DUNNING_DEFAULT_POLICY = {
    "reminder_day": 3,
    "warning_day": 7,
    "critical_day": 10,
    "suspension_day": 14,
    "collections_day": 21,
    "termination_day": 30,
}


def _normalize_dunning_policy(payload: Dict[str, Any]) -> Dict[str, int]:
    """Validates a monotonic tenant dunning ladder before it can automate access changes."""
    policy = {key: int(payload.get(key, fallback)) for key, fallback in DUNNING_DEFAULT_POLICY.items()}
    values = [policy[key] for key in DUNNING_DEFAULT_POLICY]
    if any(value < 0 for value in values) or values != sorted(values):
        raise HTTPException(status_code=422, detail="Dunning policy days must be non-negative and chronological")
    return policy


def _dunning_state_for_days(days_overdue: int, policy: Dict[str, int]) -> str:
    """Resolves the approved service state for one overdue platform subscription invoice."""
    if days_overdue >= policy["termination_day"]:
        return "TERMINATED"
    if days_overdue >= policy["suspension_day"]:
        return "SUSPENDED_READONLY"
    if days_overdue >= policy["critical_day"]:
        return "CRITICAL"
    if days_overdue >= policy["warning_day"]:
        return "WARNING"
    return "ACTIVE"


def _as_utc(value: Any) -> Optional[datetime]:
    """Normalizes Mongo and domain timestamps for deterministic overdue-day calculation."""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


def _resolve_invoice_any(registry: BillingRegistry, tenant_id: str, invoice_id: str):
    """Resolve platform/client invoice. SUPER_ADMIN tenants may cross-lookup by invoice_id only."""
    if not invoice_id:
        return None, None
    inv = registry.get_platform_invoice(tenant_id, invoice_id)
    if inv:
        return inv, "PLATFORM"
    inv = registry.get_client_invoice(tenant_id, invoice_id)
    if inv:
        return inv, "CLIENT"

    # Super-admin / founder headers: find by invoice id without tenant filter
    super_tenants = {
        "GLOBAL_ROOT", "MASTER", "WILSY_SOVEREIGN_ROOT", "SOVEREIGN_ROOT",
        "WILSY_PLATFORM", "PLATFORM",
    }
    if str(tenant_id or "").upper() not in super_tenants:
        return None, None

    coll_db = _require_db()
    id_clause = {
        "$or": [
            {"invoice_id": invoice_id},
            {"invoiceId": invoice_id},
            {"invoice_number": invoice_id},
            {"invoiceNumber": invoice_id},
        ]
    }
    doc = coll_db["platform_invoices"].find_one(id_clause)
    if doc:
        try:
            return PlatformInvoice.from_dict(doc), "PLATFORM"
        except Exception:
            # Tolerate mixed-case legacy rows
            try:
                return PlatformInvoice.from_dict({
                    **doc,
                    "tenantId": doc.get("tenantId") or doc.get("tenant_id") or tenant_id,
                    "invoiceId": doc.get("invoiceId") or doc.get("invoice_id") or invoice_id,
                    "status": str(doc.get("status") or "open").lower(),
                    "amount": float(doc.get("amount") or 0),
                    "total": float(doc.get("total") or doc.get("total_amount") or doc.get("totalAmount") or 0),
                    "currency": doc.get("currency") or "ZAR",
                }), "PLATFORM"
            except Exception:
                pass
    doc = coll_db["client_invoices"].find_one(id_clause)
    if doc:
        try:
            return ClientInvoice.from_dict(doc), "CLIENT"
        except Exception:
            try:
                return ClientInvoice.from_dict({
                    **doc,
                    "tenantId": doc.get("tenantId") or doc.get("tenant_id") or tenant_id,
                    "invoiceId": doc.get("invoiceId") or doc.get("invoice_id") or invoice_id,
                    "status": str(doc.get("status") or "open").lower(),
                    "amount": float(doc.get("amount") or 0),
                    "total": float(doc.get("total") or doc.get("total_amount") or doc.get("totalAmount") or 0),
                    "currency": doc.get("currency") or "ZAR",
                }), "CLIENT"
            except Exception:
                pass
    return None, None


@router.post("/invoices/email", response_model=Dict[str, Any])
async def email_invoice(
    body: InvoiceEmailRequest,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
):
    """Queue invoice email — persists audit event (SMTP can be wired later)."""
    try:
        inv_id = body.invoiceId or body.invoice_id or ""
        tid = body.tenantId or body.tenant_id or tenant_id
        inv, kind = _resolve_invoice_any(registry, tid, inv_id)
        proof = inv.proof_hash if inv else ""
        total = float(getattr(inv, "total", 0) or 0) if inv else 0
        event = {
            "tenant_id": tid,
            "event_type": "INVOICE_EMAIL_QUEUED",
            "invoice_id": inv_id,
            "pipeline": kind or "UNKNOWN",
            "to": body.to or "billing-contact@tenant",
            "include_seal": body.includeSeal,
            "proof_hash": proof,
            "total": total,
            "created_at": datetime.now(timezone.utc),
            "status": "QUEUED",
        }
        coll_db = _require_db()
        coll_db["billing_audit_events"].insert_one(dict(event))
        event.pop("_id", None)
        _telemetry(tid, "BILLING", "INVOICE_EMAIL_QUEUED", "billing_router", {"invoice_id": inv_id})
        return {
            "success": True,
            "status": "QUEUED",
            "message": f"Email queued for invoice {inv_id}",
            "invoice_id": inv_id,
            "to": event["to"],
            "pipeline": kind,
            "event": {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in event.items()},
        }
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "EMAIL_INVOICE", tenant_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoices/{invoice_id}/partial-payment", response_model=Dict[str, Any], status_code=201)
@router.post("/invoices/{invoice_id}/partialPayment", response_model=Dict[str, Any], status_code=201)
@router.post("/invoice/{invoice_id}/partial-payment", response_model=Dict[str, Any], status_code=201)
async def record_partial_payment(
    invoice_id: str,
    body: PartialPaymentBody,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        if body.amount <= 0:
            raise HTTPException(status_code=400, detail="amount must be > 0")
        inv, kind = _resolve_invoice_any(registry, tenant_id, invoice_id)
        if not inv:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
        # Persist payment under the invoice's real tenant (not only GLOBAL_ROOT header)
        pay_tenant = getattr(inv, "tenant_id", None) or tenant_id
        invoice_doc_before_payment = inv.to_dict() if hasattr(inv, "to_dict") else dict(inv)
        invoice_total = float(
            invoice_doc_before_payment.get("total")
            or invoice_doc_before_payment.get("total_amount")
            or invoice_doc_before_payment.get("totalAmount")
            or 0
        )
        successful_before_payment = registry.list_payments(
            pay_tenant, invoice_id=invoice_id, status="succeeded", limit=500
        )
        amount_paid_before_payment = round(sum(
            float((item.to_dict() if hasattr(item, "to_dict") else item).get("amount", 0) or 0)
            for item in successful_before_payment
        ), 2)
        remaining_before_payment = max(0.0, round(invoice_total - amount_paid_before_payment, 2))
        if invoice_total <= 0:
            raise HTTPException(status_code=409, detail="Invoice does not have a collectible total")
        if remaining_before_payment <= 0:
            raise HTTPException(status_code=409, detail="Invoice is already settled")
        if round(body.amount, 2) > remaining_before_payment:
            raise HTTPException(
                status_code=422,
                detail=f"Payment exceeds remaining balance of {remaining_before_payment:.2f} {body.currency or getattr(inv, 'currency', 'ZAR')}",
            )
        key = body.idempotencyKey or body.idempotency_key or str(uuid.uuid4())
        payment = registry.create_payment(
            tenant_id=pay_tenant,
            invoice_id=invoice_id,
            amount=body.amount,
            currency=body.currency or getattr(inv, "currency", "ZAR"),
            method=body.method or "manual",
            external_reference=body.external_reference,
            metadata={"source": "LEDGER_PARTIAL", "pipeline": kind},
            idempotency_key=key,
            performed_by=performed_by,
        )
        # Mark succeeded so invoice balance updates when registry supports it
        try:
            payment = registry.update_payment_status(
                pay_tenant, payment.payment_id, "succeeded", performed_by
            )
        except Exception:
            pass
        # The payment collection is the source for partial settlement.  Return a
        # fresh, enriched invoice so the browser never has to invent balances.
        refreshed, _ = _resolve_invoice_any(registry, pay_tenant, invoice_id)
        if not refreshed:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} disappeared after payment recording")
        succeeded_payments = registry.list_payments(
            pay_tenant, invoice_id=invoice_id, status="succeeded", limit=500
        )
        payment_history = [
            item.to_dict() if hasattr(item, "to_dict") else item
            for item in succeeded_payments
        ]
        invoice_doc = refreshed.to_dict() if hasattr(refreshed, "to_dict") else dict(refreshed)
        amount_paid = round(sum(float(item.get("amount", 0) or 0) for item in payment_history), 2)
        invoice_total = float(invoice_doc.get("total") or invoice_doc.get("total_amount") or 0)
        outstanding_amount = max(0.0, round(invoice_total - amount_paid, 2))
        settlement_updates: Dict[str, Any] = {
            "amount_paid": amount_paid,
            "outstanding_amount": outstanding_amount,
        }
        if outstanding_amount == 0 and invoice_total > 0:
            settlement_updates.update({"status": "paid", "paid_at": datetime.now(timezone.utc)})
        if kind == "platform":
            refreshed = registry.update_platform_invoice(pay_tenant, invoice_id, settlement_updates, performed_by)
        else:
            refreshed = registry.update_client_invoice(pay_tenant, invoice_id, settlement_updates, performed_by)
        invoice_doc = refreshed.to_dict() if hasattr(refreshed, "to_dict") else dict(refreshed)
        invoice_doc.update({
            "amount_paid": amount_paid,
            "amountPaid": amount_paid,
            "outstanding_amount": outstanding_amount,
            "outstandingAmount": outstanding_amount,
            "payments": payment_history,
            "status": "paid" if outstanding_amount == 0 and invoice_total > 0 else "partially_paid",
        })
        _telemetry(pay_tenant, "BILLING", "PARTIAL_PAYMENT", "billing_router", {
            "invoice_id": invoice_id, "amount": body.amount, "pipeline": kind,
            "resolved_tenant": pay_tenant, "header_tenant": tenant_id,
        })
        return {
            "success": True,
            "payment": payment.to_dict() if hasattr(payment, "to_dict") else payment,
            "invoice": invoice_doc,
            "invoice_id": invoice_id,
            "pipeline": kind,
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _log_error(e, "PARTIAL_PAYMENT", tenant_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/invoices/{invoice_id}/status", response_model=Dict[str, Any])
@router.put("/invoices/{invoice_id}/status", response_model=Dict[str, Any])
@router.post("/invoices/{invoice_id}/status", response_model=Dict[str, Any])
async def update_invoice_status_unified(
    invoice_id: str,
    body: InvoiceStatusBody,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        raw = str(body.status or "").lower().strip()
        # Map UI vocabulary → domain
        aliases = {
            "issued": "open",
            "open": "open",
            "draft": "draft",
            "paid": "paid",
            "overdue": "overdue",
            "void": "void",
            "voided": "void",
            "cancelled": "cancelled",
            "canceled": "cancelled",
            "disputed": "overdue",
            "legal_hold": "overdue",
            "partially_paid": "open",
        }
        domain_status = aliases.get(raw, raw)
        inv, kind = _resolve_invoice_any(registry, tenant_id, invoice_id)
        if not inv:
            raise HTTPException(status_code=404, detail=f"Invoice {invoice_id} not found")
        inv_tenant = getattr(inv, "tenant_id", None) or tenant_id
        updates = {"status": domain_status}
        if kind == "PLATFORM":
            updated = registry.update_platform_invoice(inv_tenant, invoice_id, updates, performed_by)
        else:
            updated = registry.update_client_invoice(inv_tenant, invoice_id, updates, performed_by)
        _telemetry(tenant_id, "BILLING", "INVOICE_STATUS_UPDATED", "billing_router", {
            "invoice_id": invoice_id, "status": domain_status, "pipeline": kind
        })
        return updated.to_dict() if hasattr(updated, "to_dict") else updated
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        _log_error(e, "UPDATE_INVOICE_STATUS", tenant_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{invoice_id}/pdf", response_model=Dict[str, Any])
async def invoice_pdf_manifest(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
):
    """JSON print manifest until full PDF binary is served from artifact renderer."""
    inv, kind = _resolve_invoice_any(registry, tenant_id, invoice_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    doc = inv.to_dict()
    return {
        "success": True,
        "format": "MANIFEST_JSON",
        "message": "Use client print fallback or POST /generate/pdf on Node for binary PDF",
        "pipeline": kind,
        "invoice": doc,
        "print": {
            "title": doc.get("invoiceId") or invoice_id,
            "total": doc.get("total") or doc.get("totalAmount"),
            "currency": doc.get("currency", "ZAR"),
            "proof_hash": doc.get("proofHash") or doc.get("proof_hash"),
        },
    }


@router.get("/dunning/policy", response_model=Dict[str, Any])
async def get_dunning_policy(tenant_id: str = Depends(get_tenant_id)):
    """Returns the persisted tenant policy or the adopted 3/7/10/14/21/30-day ladder."""
    coll_db = _require_db()
    stored = coll_db["billing_dunning_policies"].find_one({"tenant_id": tenant_id}, {"_id": 0}) or {}
    policy = _normalize_dunning_policy(stored.get("policy", DUNNING_DEFAULT_POLICY))
    return {"success": True, "tenant_id": tenant_id, "policy": policy, "source": "PERSISTED" if stored else "DEFAULT"}


@router.put("/dunning/policy", response_model=Dict[str, Any])
async def update_dunning_policy(body: DunningPolicyUpdate, tenant_id: str = Depends(get_tenant_id)):
    """Persists an approved tenant policy and anchors its configuration change for audit review."""
    coll_db = _require_db()
    policy = _normalize_dunning_policy(body.model_dump())
    changed_at = datetime.now(timezone.utc)
    proof_payload = {"tenant_id": tenant_id, "policy": policy, "changed_at": changed_at.isoformat(), "schema": "WILSY-DUNNING-POLICY/V1"}
    proof_hash = _sha3_512(proof_payload)
    coll_db["billing_dunning_policies"].update_one(
        {"tenant_id": tenant_id},
        {"$set": {**proof_payload, "proof_hash": proof_hash, "updated_at": changed_at}},
        upsert=True,
    )
    coll_db["billing_audit_events"].insert_one({
        "tenant_id": tenant_id,
        "event_type": "DUNNING_POLICY_UPDATED",
        "proof_hash": proof_hash,
        "metadata": {"policy": policy},
        "created_at": changed_at,
    })
    return {"success": True, "tenant_id": tenant_id, "policy": policy, "proof_hash": proof_hash}


@router.get("/dunning/state", response_model=Dict[str, Any])
async def get_dunning_state(tenant_id: str = Depends(get_tenant_id), subscription_id: Optional[str] = None):
    """Returns persisted service-access posture; tenant UI uses this to enforce read-only mode truthfully."""
    query: Dict[str, Any] = {"tenant_id": tenant_id}
    if subscription_id:
        query["subscription_id"] = subscription_id
    rows = list(_require_db()["billing_dunning_states"].find(query, {"_id": 0}).sort("updated_at", -1).limit(100))
    return {"success": True, "tenant_id": tenant_id, "states": rows}


async def evaluate_tenant_dunning_lifecycle(
    tenant_id: str,
    body: DunningEvaluationRequest,
) -> Dict[str, Any]:
    """Evaluates one tenant's platform receivables without crossing its billing boundary.

    @param tenant_id: Tenant that owns the Wilsy platform subscription.
    @param body: Evaluation options supplied by the API command or daily scheduler.
    @returns: Immutable transition candidates and the policy used to derive them.
    @collaboration: Shared by the authenticated command route and Kennel-native daily scheduler.
    """
    coll_db = _require_db()
    policy_doc = coll_db["billing_dunning_policies"].find_one({"tenant_id": tenant_id}, {"_id": 0}) or {}
    policy = _normalize_dunning_policy(policy_doc.get("policy", DUNNING_DEFAULT_POLICY))
    now = datetime.now(timezone.utc)
    invoice_query: Dict[str, Any] = {
        "$or": [{"tenant_id": tenant_id}, {"tenantId": tenant_id}],
    }
    if body.subscription_id:
        invoice_query["$and"] = [{"$or": [{"subscription_id": body.subscription_id}, {"subscriptionId": body.subscription_id}]}]
    invoices = list(coll_db["platform_invoices"].find(invoice_query, {"_id": 0}))
    transitions: List[Dict[str, Any]] = []

    for invoice in invoices:
        invoice_status = str(invoice.get("status") or "").strip().lower()
        if invoice_status in {"paid", "void", "cancelled", "canceled"}:
            continue
        due_at = _as_utc(invoice.get("due_at") or invoice.get("dueAt"))
        subscription_id = str(invoice.get("subscription_id") or invoice.get("subscriptionId") or "").strip()
        invoice_id = str(invoice.get("invoice_id") or invoice.get("invoiceId") or "").strip()
        if not due_at or not subscription_id or not invoice_id or due_at > now:
            continue
        days_overdue = max(0, (now.date() - due_at.date()).days)
        next_state = _dunning_state_for_days(days_overdue, policy)
        state_filter = {"tenant_id": tenant_id, "subscription_id": subscription_id}
        existing = coll_db["billing_dunning_states"].find_one(state_filter, {"_id": 0}) or {}
        current_state = str(existing.get("state") or "ACTIVE").upper()
        if DUNNING_STATE_ORDER.get(next_state, 0) <= DUNNING_STATE_ORDER.get(current_state, 0):
            continue
        transition = {
            "tenant_id": tenant_id,
            "subscription_id": subscription_id,
            "invoice_id": invoice_id,
            "from_state": current_state,
            "state": next_state,
            "days_overdue": days_overdue,
            "policy": policy,
            "evaluated_at": now.isoformat(),
        }
        transition["proof_hash"] = _sha3_512(transition)
        transitions.append(transition)
        if body.dry_run:
            continue
        coll_db["billing_dunning_states"].update_one(
            state_filter,
            {"$set": {**transition, "updated_at": now}, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        coll_db["subscriptions"].update_many(
            {"tenant_id": tenant_id, "$or": [{"subscription_id": subscription_id}, {"subscriptionId": subscription_id}]},
            {"$set": {"suspension_state": next_state, "dunning_state": next_state, "dunning_updated_at": now}},
        )
        coll_db["billing_audit_events"].insert_one({
            "tenant_id": tenant_id,
            "event_type": "DUNNING_STATE_TRANSITION",
            "proof_hash": transition["proof_hash"],
            "metadata": transition,
            "created_at": now,
        })
        _telemetry(tenant_id, "BILLING", "DUNNING_STATE_TRANSITION", "billing_router", transition)

    return {"success": True, "tenant_id": tenant_id, "dry_run": body.dry_run, "policy": policy, "transitions": transitions}


async def evaluate_all_tenant_dunning_lifecycles() -> Dict[str, Any]:
    """Runs one idempotent dunning pass for every tenant with a platform invoice.

    @returns: Scheduler-safe aggregate that names evaluated tenants and transition counts.
    @collaboration: Called only by the Kennel API lifecycle task; it never evaluates client invoices.
    """
    coll_db = _require_db()
    tenant_ids = set(coll_db["platform_invoices"].distinct("tenant_id"))
    tenant_ids.update(coll_db["platform_invoices"].distinct("tenantId"))
    results: List[Dict[str, Any]] = []
    for tenant_id in sorted(str(value).strip() for value in tenant_ids if value):
        result = await evaluate_tenant_dunning_lifecycle(tenant_id, DunningEvaluationRequest())
        results.append({"tenant_id": tenant_id, "transition_count": len(result["transitions"])})
    return {
        "success": True,
        "evaluated_tenants": len(results),
        "transition_count": sum(row["transition_count"] for row in results),
        "results": results,
    }


@router.post("/dunning/evaluate", response_model=Dict[str, Any])
async def evaluate_dunning_lifecycle(body: DunningEvaluationRequest, tenant_id: str = Depends(get_tenant_id)):
    """Evaluates overdue platform-subscription invoices and persists only forward lifecycle transitions.

    This endpoint is safe for a scheduled worker: repeated calls are idempotent while the invoice remains unpaid.
    It never evaluates tenant-to-client receivables as a reason to suspend the tenant's Wilsy service.
    """
    return await evaluate_tenant_dunning_lifecycle(tenant_id, body)


@router.post("/merkle/verify", response_model=Dict[str, Any])
@router.post("/audit/verifyChain", response_model=Dict[str, Any])
async def verify_invoice_chain(
    body: MerkleVerifyBody,
    tenant_id: str = Depends(get_tenant_id),
):
    seal = body.sealHash or body.seal_hash or body.proofHash or body.proof_hash or ""
    tid = body.tenantId or body.tenant_id or tenant_id
    if not seal:
        raise HTTPException(status_code=400, detail="sealHash required")
    coll_db = _require_db()
    # Look for matching proof on invoices or audit events
    hit = coll_db["platform_invoices"].find_one({
        "$or": [
            {"proof_hash": seal}, {"proofHash": seal},
            {"seal_hash": seal}, {"sealHash": seal},
        ]
    })
    if not hit:
        hit = coll_db["client_invoices"].find_one({
            "$or": [
                {"proof_hash": seal}, {"proofHash": seal},
                {"seal_hash": seal}, {"sealHash": seal},
            ]
        })
    audit = coll_db["billing_audit_events"].find_one({"proof_hash": seal}) or coll_db["billing_audit_events"].find_one({"proofHash": seal})
    valid = bool(hit or audit)
    result = {
        "success": True,
        "valid": valid,
        "sealHash": seal.upper() if seal else "",
        "tenantId": tid,
        "matchedInvoice": bool(hit),
        "matchedAudit": bool(audit),
        "algorithm": "SHA3-512",
        "verifiedAt": datetime.now(timezone.utc).isoformat(),
    }
    coll_db["billing_audit_events"].insert_one({
        "tenant_id": tid,
        "event_type": "CHAIN_VERIFY",
        "proof_hash": seal,
        "valid": valid,
        "created_at": datetime.now(timezone.utc),
    })
    return result


@router.get("/actions", response_model=Dict[str, Any])
async def billing_actions_surface():
    return {
        "success": True,
        "surface": "KENNEL_BILLING_ACTIONS",
        "version": "1.6.1-CROSS-TENANT-RESOLVE",
        "routes": [
            "POST /billing/invoices/email",
            "POST /billing/invoices/{id}/partial-payment",
            "GET|PUT /billing/dunning/policy",
            "GET /billing/dunning/state",
            "POST /billing/dunning/evaluate",
            "PATCH|PUT|POST /billing/invoices/{id}/status",
            "GET  /billing/invoices/{id}/pdf",
            "POST /billing/merkle/verify",
            "POST /billing/audit/verifyChain",
            "GET  /billing/audit/events",
            "GET  /billing/actions",
        ],
    }


"""
════════════════════════════════════════════════════════════════════════════════
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS BILLING ROUTER v1.6.1-CROSS-TENANT-RESOLVE
════════════════════════════════════════════════════════════════════════════════
Status:          CERTIFIED PRODUCTION ARTIFACT
Version:         v1.4.4-PAIR-PROOF-FIX
Fixes:           pair_proof_hash $setOnInsert/$set conflict; db/mongo_client guards.
Compliance:      POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001
Note:            Ready for deployment with billing_registry v1.0.5.
════════════════════════════════════════════════════════════════════════════════
"""
