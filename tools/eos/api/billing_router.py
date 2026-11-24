# -*- coding: utf-8 -*-
"""
TITLE: WILSY OS Python EOS Billing HTTP Router
VERSION: v1.12.1-EOS-QR-PERSISTED-SOURCE-BOUNDARY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Composes Python-owned billing HTTP surfaces. Invoice proof reference
         verification uses canonical own-tenant authorization and persists an
         audit observation; Kennel EOS retains all financial execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/billing_router.py
COLLABORATION / OWNERSHIP: BillingRegistry, billing domain, TenantAuthorizationContext,
                           Kernel database and client billing projections.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
  2026-11-10 v1.12.1-EOS-QR-PERSISTED-SOURCE-BOUNDARY confines legacy QR
    matching to tenant-owned client invoices, rejects conflicting tenant and
    identity aliases, requires persisted currency, and uses the canonical
    invoice identity only as a deterministic trace alias when no trace is stored.
  2026-11-10 v1.12.0-EOS-QR-AUDIT-AUTHORIZATION adds authenticated tenant-bound
    legacy invoice QR issue/verify routes, authenticates persisted billing-audit
    reads, and denies integrity-control writes until a governed capability exists.
  2026-11-10 v1.11.1-MERKLE-TENANT-AUTHORIZATION scopes invoice proof lookup and
    verification audit evidence to the authenticated TenantAuthorizationContext;
    caller tenant fields cannot override that scope. Legacy compatibility routes
    remain individually bounded by their existing contracts.
  2026-09-15 v1.11.0-L7D-B-LAZY-BILLING-HANDLES resolves active kernel database
    and client handles at request time.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Verification accepts only a SHA3-512-shaped
  reference, performs tenant-scoped reads, and records no invoice content.
TENANT BOUNDARY: The proof verification route derives tenant scope only from
  RequireTenantAuthorization; body/header tenant labels never replace it.
AUTHORITY BOUNDARY: Python HTTP transport and source-owned billing evidence;
  no invoice authenticity, execution, payment, or settlement is inferred.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
  and settlement truth.

CONSTITUTION:
REQUEST != AUTHORIZATION != EXECUTION != SETTLEMENT.
NO EVIDENCE = NO FACT.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Depends, Header, Request, Query
from typing import Any, Dict, List, NoReturn, Optional
import logging
import os
import traceback
from datetime import datetime, timezone, timedelta
import uuid
import hashlib
import json
import re

from pydantic import BaseModel

from ..saas.billing.billing_registry import get_billing_registry, BillingRegistry, db, client as mongo_client
from ..kernel.db import get_database as get_kernel_database, get_client as get_kernel_client
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
from ..saas.billing.billing_intelligence_orchestrator import (
    BillingIntelligenceOrchestrator,
    BillingIntelligenceOrchestratorError,
    parse_as_of,
)
from ..saas.billing.wilsy_ai_entitlement_registry import COLLECTION as WILSY_AI_ENTITLEMENT_COLLECTION
from ..saas.billing.wilsy_ai_usage_capacity import WilsyAIUsageCapacityError
from ..saas.billing.wilsy_ai_usage_capacity_orchestrator import (
    WilsyAIUsageCapacityOrchestrator,
    WilsyAIUsageCapacityOrchestratorError,
)
from ..saas.billing.wilsy_ai_usage_observation_registry import (
    COLLECTION as WILSY_AI_USAGE_OBSERVATION_COLLECTION,
    WilsyAIUsageObservationRegistryError,
)
from ..saas.billing.wilsy_ai_entitlement_registry import WilsyAIEntitlementRegistryError
from tools.eos.api.tenant_authorization_http import (
    RequireTenantAuthorization,
    TenantAuthorizationContext,
)
from ..saas.billing.invoice_qr_legacy_contract import (
    InvoiceQrContractError,
    build_legacy_invoice_qr_payload,
    verify_legacy_invoice_qr_payload,
)

# ─── Logging ──────────────────────────────────────────────────────────────────
VERSION = "v1.12.1-EOS-QR-PERSISTED-SOURCE-BOUNDARY"

_BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION = RequireTenantAuthorization(
    "billing_intelligence:evidence:read",
    "billing_intelligence_evidence_read",
)

_WILSY_AI_CAPACITY_READ_AUTHORIZATION = RequireTenantAuthorization(
    "wilsy_ai:usage_capacity:read",
    "wilsy_ai_usage_capacity_read",
)

_BILLING_DUNNING_PROJECTION_READ_AUTHORIZATION = RequireTenantAuthorization(
    "billing_dunning:projection:read",
    "billing_dunning_projection_read",
)

_BILLING_DUNNING_PROJECTION_EVALUATE_AUTHORIZATION = RequireTenantAuthorization(
    "billing_dunning:projection:evaluate",
    "billing_dunning_projection_evaluate",
)

_BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION = RequireTenantAuthorization(
    "audit:read",
    "audit_read",
)


_LEGACY_INTELLIGENCE_UNSUPPORTED: tuple[str, ...] = (
    "arr",
    "mrr",
    "churn_rate",
    "ltv",
    "cac",
    "forecast",
    "growth_rate",
    "arpu",
    "credit_score",
    "anomaly_score",
)

logger = logging.getLogger(__name__)
DEBUG_MODE = os.getenv("WILSY_MODEL_DEBUG", "0") == "1"

def _log_error(exc: Exception, context: str, tenant_id: str = "GLOBAL_ROOT") -> None:
    if DEBUG_MODE:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}\n{traceback.format_exc()}")
    else:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}")

def _raise_financial_authority_conflict(
    code: str,
) -> None:
    """Fail closed when HTTP input attempts to create Kennel-owned truth."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=code,
    )


def _legacy_intelligence_unavailable(route: str) -> NoReturn:
    """Fail closed for uncertified legacy intelligence routes.

    The route remains mounted for compatibility with existing callers, but it
    cannot return unsupported ARR/MRR/churn/LTV/CAC/forecast/growth values.
    Canonical evidence is available only from the P1/P2-owned endpoint.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail={
            "code": "BILLING_LEGACY_INTELLIGENCE_UNAVAILABLE",
            "message": f"{route} has no certified intelligence contract",
            "canonical_endpoint": "/billing/intelligence/evidence",
            "unsupported_outputs": list(_LEGACY_INTELLIGENCE_UNSUPPORTED),
        },
    )


def _reject_http_invoice_financial_truth(
    updates: Dict[str, Any],
) -> None:
    """Reject caller-authored settlement fields before registry invocation."""
    forbidden_fields = {
        "paid_at",
        "paidAt",
        "amount_paid",
        "amountPaid",
        "outstanding_amount",
        "outstandingAmount",
    }

    if forbidden_fields.intersection(updates):
        _raise_financial_authority_conflict(
            "BILLING_SETTLEMENT_TRUTH_REQUIRES_KENNEL"
        )

    value = updates.get("status")

    if isinstance(value, InvoiceStatus):
        value = value.value

    if (
        isinstance(value, str)
        and value.strip().lower()
        == InvoiceStatus.PAID.value
    ):
        _raise_financial_authority_conflict(
            "BILLING_PAID_STATE_REQUIRES_KENNEL_SETTLEMENT_EVIDENCE"
        )


async def _reject_http_invoice_financial_truth_request(
    request: Request,
) -> None:
    """Reject forbidden settlement keys before Pydantic projects the DTO.

    Presence of a forbidden financial-truth key is itself an authority
    violation. The caller cannot evade the 409 boundary through an unknown
    snake/camel alias that Pydantic would otherwise discard.
    """
    try:
        payload: Any = await request.json()
    except ValueError:
        return

    if isinstance(payload, dict):
        _reject_http_invoice_financial_truth(payload)


def _telemetry(tenant_id: str, category: str, event: str, source: str, metadata: Optional[dict] = None) -> None:
    if metadata is None:
        metadata = {}
    logger.info(f"[TELEMETRY] {tenant_id} | {category} | {event} | {source} | {metadata}")

# ─── Tenant Dependency ──────────────────────────────────────────────────────

def _require_db():
    """Return the live kernel database or raise 503 without stale snapshots."""
    database = db if db is not None else get_kernel_database()
    if database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing database unavailable",
        )
    return database


def _require_mongo_client():
    """Return the live kernel client or raise 503 for order generation."""
    active_client = mongo_client if mongo_client is not None else get_kernel_client()
    if active_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mongo client unavailable for order number generation",
        )
    return active_client

def get_tenant_id(x_tenant_id: str = Header(...)) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="X-Tenant-Id header required")
    return x_tenant_id


def _parse_wilsy_ai_capacity_as_of(value: object) -> datetime:
    """Parse one explicit aware UTC snapshot for the P6D transport seam."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value and value == value.strip():
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise WilsyAIUsageCapacityOrchestratorError(
                "M13P6C_AS_OF_INVALID"
            ) from error
    else:
        raise WilsyAIUsageCapacityOrchestratorError("M13P6C_AS_OF_INVALID")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise WilsyAIUsageCapacityOrchestratorError("M13P6C_AS_OF_INVALID")
    return parsed.astimezone(timezone.utc)


def _raise_wilsy_ai_capacity_http_failure(
    error: Exception,
    tenant_id: str,
) -> NoReturn:
    """Translate governed P4/P6B/P6A/P6C failures without fabricating success."""
    code = str(error)
    if code in {
        "M13P6C_AS_OF_INVALID",
        "M13P6C_ENTITLEMENT_ID_REQUIRED",
        "M13P6C_TENANT_REQUIRED",
        "M13P6C_TENANT_FORBIDDEN",
        "M13P6B_INPUT_INVALID",
        "M13P6A_AS_OF_INVALID",
    }:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code) from error
    if code == "M13P4_ENTITLEMENT_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=code) from error
    if "PERSISTENCE_UNAVAILABLE" in code or "TRANSACTION_REQUIRED" in code:
        _log_error(error, "GET_WILSY_AI_USAGE_CAPACITY_EVIDENCE", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WILSY AI usage-capacity evidence unavailable",
        ) from error
    if (
        "CORRUPT" in code
        or "CONFLICT" in code
        or "DUPLICATE" in code
        or "EVIDENCE_REQUIRED" in code
        or "NOT_ACTIVE" in code
        or "BINDING" in code
        or "INVALID" in code
    ):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=code) from error
    _log_error(error, "GET_WILSY_AI_USAGE_CAPACITY_EVIDENCE", tenant_id)
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="WILSY AI usage-capacity evidence unavailable",
    ) from error

# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/billing", tags=["Billing"])
qr_router = APIRouter(prefix="/qr", tags=["Billing QR"])


def _invoice_field(document: Dict[str, Any], *names: str) -> Any:
    """Return the first non-null persisted invoice field without synthesizing truth."""
    for name in names:
        value = document.get(name)
        if value is not None:
            return value
    return None


def _invoice_trace_id(document: Dict[str, Any], canonical_invoice_id: Any) -> str | None:
    """Resolve persisted trace identity or its stable invoice-ID compatibility alias."""
    values = [
        document[name]
        for name in ("trace_id", "traceId")
        if document.get(name) is not None
    ]
    normalized = {str(value).strip() for value in values}
    if len(normalized) > 1 or "" in normalized:
        return None
    if normalized:
        return next(iter(normalized))
    fallback = str(canonical_invoice_id).strip() if canonical_invoice_id is not None else ""
    return fallback or None


def _tenant_invoice_lookup_query(
    tenant_id: str,
    *,
    invoice_id: str | None = None,
    trace_id: str | None = None,
) -> Dict[str, Any]:
    """Build one exact tenant-bounded legacy/current invoice selector."""
    tenant_fields = (
        "tenant_id",
        "tenantId",
        "recipient_tenant_id",
        "recipientTenantId",
    )
    invoice_fields = (
        "invoice_id",
        "invoiceId",
        "invoice_number",
        "invoiceNumber",
    )
    trace_fields = (
        "trace_id",
        "traceId",
    )
    identity_clauses = (
        [{field: invoice_id} for field in invoice_fields]
        if isinstance(invoice_id, str) and invoice_id
        else []
    ) + (
        [{field: trace_id} for field in trace_fields]
        if isinstance(trace_id, str) and trace_id
        else []
    )
    tenant_consistency = [
        {"$or": [{field: tenant_id}, {field: None}]}
        for field in tenant_fields
    ]
    return {
        "$and": [
            {"$or": [{field: tenant_id} for field in tenant_fields]},
            *tenant_consistency,
            {"$or": identity_clauses},
        ]
    }


def _find_tenant_invoice(
    database: Any,
    tenant_id: str,
    *,
    invoice_id: str | None = None,
    trace_id: str | None = None,
) -> Dict[str, Any] | None:
    """Read one client invoice using consistent exact-tenant ownership fields."""
    query = _tenant_invoice_lookup_query(
        tenant_id,
        invoice_id=invoice_id,
        trace_id=trace_id,
    )
    document = database["client_invoices"].find_one(query)
    if document is None:
        return None
    if not isinstance(document, dict):
        raise TypeError("BILLING_QR_PERSISTED_INVOICE_INVALID")
    owner_fields = (
        "tenant_id",
        "tenantId",
        "recipient_tenant_id",
        "recipientTenantId",
    )
    owners = [document[field] for field in owner_fields if document.get(field) is not None]
    if not owners or any(str(owner) != tenant_id for owner in owners):
        return None
    return document


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

@router.patch(
    "/platform/invoices/{invoice_id}",
    response_model=Dict[str, Any],
    dependencies=[
        Depends(_reject_http_invoice_financial_truth_request)
    ],
)
async def update_platform_invoice(
    invoice_id: str,
    updates: PlatformInvoiceUpdate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        update_dict = updates.dict(exclude_unset=True)
        _reject_http_invoice_financial_truth(update_dict)
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        invoice = registry.update_platform_invoice(tenant_id, invoice_id, update_dict, performed_by)
        return _invoice_response_with_statement(invoice, tenant_id, "PLATFORM", performed_by)
    except HTTPException:
        raise
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

@router.patch(
    "/client/invoices/{invoice_id}",
    response_model=Dict[str, Any],
    dependencies=[
        Depends(_reject_http_invoice_financial_truth_request)
    ],
)
async def update_client_invoice(
    invoice_id: str,
    updates: ClientInvoiceUpdate,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    try:
        update_dict = updates.dict(exclude_unset=True)
        _reject_http_invoice_financial_truth(update_dict)
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
        invoice = registry.update_client_invoice(tenant_id, invoice_id, update_dict, performed_by)
        return invoice.to_dict()
    except HTTPException:
        raise
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
    """Payment execution truth is Kennel-owned; caller status mutation is prohibited."""
    _raise_financial_authority_conflict(
        "BILLING_EXECUTION_TRUTH_REQUIRES_KENNEL"
    )

@router.post("/payments/{payment_id}/refund", response_model=Dict[str, Any])
async def refund_payment(
    payment_id: str,
    refund_data: RefundRequest,
    tenant_id: str = Depends(get_tenant_id),
    registry: BillingRegistry = Depends(get_billing_registry),
    performed_by: str = "SYSTEM",
):
    """Refund execution requires a new Kennel-owned financial execution path."""
    _raise_financial_authority_conflict(
        "BILLING_REFUND_REQUIRES_KENNEL_EXECUTION"
    )

# ----------------------------------------------------------------------------
# Legacy intelligence compatibility boundaries
# ----------------------------------------------------------------------------
@router.get("/summary", response_model=None)
async def get_billing_summary(
    tenant_id: str = Depends(get_tenant_id),
) -> Any:
    """Reject the uncertified legacy summary without fabricating intelligence."""
    _legacy_intelligence_unavailable("/billing/summary")


@router.get("/analytics", response_model=None)
async def get_billing_analytics(
    tenant_id: str = Depends(get_tenant_id),
) -> Any:
    """Reject uncertified legacy analytics without fabricating intelligence."""
    _legacy_intelligence_unavailable("/billing/analytics")


@router.get("/intelligence/evidence", response_model=Dict[str, Any])
async def get_billing_intelligence_evidence(
    as_of: str = Query(..., description="Explicit aware ISO-8601 evidence snapshot time"),
    prior_evidence_identity: str | None = Query(
        None,
        description="Optional exact tenant-scoped prior evidence identity for growth",
    ),
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION
    ),
) -> Dict[str, Any]:
    """Return canonical M12-P1 evidence composed and persisted through P2.

    This endpoint is deliberately separate from the legacy summary/analytics
    projections. It supplies explicit tenant scope and snapshot time, loads
    only canonical Python evidence collections, and delegates derivation and
    persistence to their certified owners. It creates no execution or
    settlement truth.
    """
    tenant_id = authorization.tenant_id
    try:
        snapshot = parse_as_of(as_of)
        database = _require_db()
        orchestrator = BillingIntelligenceOrchestrator(
            receivable_collection=database["commercial_receivables"],
            aging_collection=database["commercial_receivable_aging"],
            dunning_collection=database["commercial_receivable_dunning"],
            evidence_collection=database["billing_intelligence_evidence"],
            subscription_collection=database["subscriptions"],
        )
        collect_kwargs: dict[str, Any] = {"as_of": snapshot}
        if prior_evidence_identity is not None:
            collect_kwargs["prior_evidence_identity"] = prior_evidence_identity
        evidence = orchestrator.collect_and_persist(tenant_id, **collect_kwargs)
        return orchestrator.response_payload(evidence)
    except BillingIntelligenceOrchestratorError as error:
        code = str(error)
        if code in {
            "M12P3_TENANT_REQUIRED",
            "M12P3_GLOBAL_TENANT_FORBIDDEN",
            "M12P3_AS_OF_REQUIRED",
            "M12P3_AS_OF_INVALID",
        }:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=code) from error
        if "CONFLICT" in code or "CORRUPT" in code or "UNSUPPORTED" in code:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=code) from error
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=code) from error
    except HTTPException:
        raise
    except Exception as error:
        _log_error(error, "GET_BILLING_INTELLIGENCE_EVIDENCE", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Canonical billing intelligence evidence unavailable",
        ) from error


@router.get("/wilsy-ai/usage-capacity/evidence", response_model=Dict[str, Any])
async def get_wilsy_ai_usage_capacity_evidence(
    entitlement_id: str = Query(
        ...,
        description="Explicit tenant-scoped entitlement locator",
    ),
    as_of: str = Query(
        ...,
        description="Explicit aware ISO-8601 capacity snapshot time",
    ),
    authorization: TenantAuthorizationContext = Depends(
        _WILSY_AI_CAPACITY_READ_AUTHORIZATION
    ),
) -> Dict[str, Any]:
    """Return canonical P6A capacity evidence for the authorized own tenant.

    Tenant scope is taken exclusively from ``TenantAuthorizationContext``.
    The router composes P6C from the exact P4 and P6B collections, owns one
    caller-created session and transaction, and returns P6A's serialization
    unchanged.  It performs no entitlement, usage, quota, commercial, or
    financial derivation of its own.
    """
    tenant_id = authorization.tenant_id
    try:
        if (
            not isinstance(entitlement_id, str)
            or not entitlement_id
            or entitlement_id != entitlement_id.strip()
        ):
            raise WilsyAIUsageCapacityOrchestratorError(
                "M13P6C_ENTITLEMENT_ID_REQUIRED"
            )
        snapshot = _parse_wilsy_ai_capacity_as_of(as_of)
        database = _require_db()
        live_client = _require_mongo_client()
        orchestrator = WilsyAIUsageCapacityOrchestrator.from_collections(
            entitlement_collection=database[WILSY_AI_ENTITLEMENT_COLLECTION],
            observation_collection=database[WILSY_AI_USAGE_OBSERVATION_COLLECTION],
        )
        with live_client.start_session() as session:
            session.start_transaction()
            try:
                capacity = orchestrator.derive_capacity(
                    tenant_id=tenant_id,
                    entitlement_id=entitlement_id,
                    as_of=snapshot,
                    session=session,
                )
                session.commit_transaction()
            except BaseException:
                active = getattr(session, "in_transaction", False)
                if callable(active):
                    active = active()
                if active is True:
                    session.abort_transaction()
                raise
        return capacity.to_dict()
    except HTTPException:
        raise
    except (
        WilsyAIUsageCapacityOrchestratorError,
        WilsyAIEntitlementRegistryError,
        WilsyAIUsageObservationRegistryError,
        WilsyAIUsageCapacityError,
    ) as error:
        _raise_wilsy_ai_capacity_http_failure(error, tenant_id)
    except Exception as error:
        _log_error(error, "GET_WILSY_AI_USAGE_CAPACITY_EVIDENCE", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WILSY AI usage-capacity evidence unavailable",
        ) from error

# ----------------------------------------------------------------------------
# Plans (RESILIENT)
# ----------------------------------------------------------------------------
@router.get("/plans", response_model=List[Dict[str, Any]])
async def get_billing_plans(
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Return the complete canonical PlanRegistry catalogue projection.

    ``GLOBAL_ROOT`` receives the complete catalogue. A tenant receives its
    tenant-scoped plus global catalogue entries under PlanRegistry semantics.
    Persistence, index or hydration failure becomes HTTP 503 and can never
    masquerade as an empty catalogue.
    """

    try:
        # PlanRegistry opens its configured catalogue client at import time;
        # defer that unrelated catalogue dependency so billing composition can
        # mount the canonical intelligence seam without network side effects.
        from ..saas.billing.plan_registry import PlanRegistry

        registry_tenant = (
            None
            if tenant_id
            == "GLOBAL_ROOT"
            else tenant_id
        )

        probe = (
            PlanRegistry.list(
                tenant_id=
                    registry_tenant,
                page=1,
                limit=1,
            )
        )

        expected_total = int(
            probe[
                "total"
            ]
        )

        result = (
            PlanRegistry.list(
                tenant_id=
                    registry_tenant,
                page=1,
                limit=max(
                    1,
                    expected_total,
                ),
            )
        )

        items = result[
            "items"
        ]

        if (
            int(
                result[
                    "total"
                ]
            )
            != expected_total
            or len(
                items
            )
            != expected_total
        ):
            raise RuntimeError(
                "PLAN_CATALOGUE_CHANGED_DURING_READ"
            )

        return [
            plan.to_dict()
            for plan in items
        ]

    except Exception as exc:
        _log_error(
            exc,
            "GET_PLANS",
            tenant_id,
        )

        raise HTTPException(
            status_code=
                status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=
                "Plan catalogue unavailable",
        ) from exc

# ----------------------------------------------------------------------------
# Credit Scores (legacy compatibility boundary)
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


@router.get("/invoices/{invoice_id}/qr", response_model=Dict[str, Any])
async def issue_invoice_qr_reference(
    invoice_id: str,
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
    ),
) -> Dict[str, Any]:
    """Issue a non-persisted legacy-compatible QR only for an authorized invoice.

    Authority: Requires canonical audit:read tenant authorization.
    Tenant scope: Both invoice lookup and signed tenant derive from the same
        TenantAuthorizationContext; foreign absence is indistinguishable.
    Mutation: No invoice or QR state is persisted.
    Financial boundary: Does not establish invoice payment, execution, or settlement.
    """
    tenant_id = authorization.tenant_id
    try:
        document = _find_tenant_invoice(
            _require_db(),
            tenant_id,
            invoice_id=invoice_id,
        )
    except HTTPException:
        raise
    except Exception as error:
        _log_error(error, "ISSUE_INVOICE_QR", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_QR_INVOICE_LOOKUP_UNAVAILABLE",
        ) from error
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BILLING_QR_INVOICE_NOT_FOUND",
        )

    canonical_invoice_id = _invoice_field(
        document, "invoice_number", "invoiceNumber", "invoice_id", "invoiceId"
    )
    total = _invoice_field(
        document, "total_amount", "totalAmount", "total", "grand_total", "grandTotal"
    )
    trace_id = _invoice_trace_id(document, canonical_invoice_id)
    currency = _invoice_field(document, "currency")
    if (
        canonical_invoice_id is None
        or str(canonical_invoice_id) != invoice_id
        or total is None
        or trace_id is None
        or currency is None
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="QR_SOURCE_FIELDS_UNAVAILABLE",
        )

    try:
        qr = build_legacy_invoice_qr_payload(
            {
                "invoiceId": str(canonical_invoice_id),
                "tenantId": tenant_id,
                "amount": total,
                "currency": currency,
                "traceId": str(trace_id),
                "sealHash": _invoice_field(
                    document, "seal_hash", "sealHash", "proof_hash", "proofHash"
                ) or "",
                "merkleRoot": _invoice_field(
                    document, "merkle_root", "merkleRoot"
                ) or "",
                "documentType": "INVOICE",
            }
        )
    except InvoiceQrContractError as error:
        if error.code.startswith("QR_SIGNING_CONFIGURATION") or error.code.startswith(
            "QR_VERIFICATION_BASE_URL"
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error.code,
            ) from error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error.code,
        ) from error

    return {
        "verificationUrl": qr.verification_url,
        "encodedPayload": qr.encoded_payload,
        "payload": dict(qr.payload),
        "signatureAlgorithm": "SHA3-512-LEGACY-SECRET-SUFFIX",
        "verificationMode": "LEGACY_INVOICE_QR_COMPATIBILITY",
        "persisted": False,
    }


@qr_router.get("/verify/{encoded_payload}", response_model=Dict[str, Any])
async def verify_signed_invoice_qr(
    encoded_payload: str,
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
    ),
) -> Dict[str, Any]:
    """Validate historical QR bytes and match the persisted invoice in own tenant.

    Authority: Requires canonical audit:read tenant authorization.
    Tenant scope: The signed tenant must exactly equal the authorized tenant before
        any invoice lookup; database selectors include tenant ownership fields.
    Mutation: Read-only. No qrVerified flag, invoice, or audit control is changed.
    Financial boundary: A valid result is not payment, execution, or settlement.
    """
    tenant_id = authorization.tenant_id
    try:
        verified = verify_legacy_invoice_qr_payload(encoded_payload)
    except InvoiceQrContractError as error:
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if error.code == "QR_SIGNING_CONFIGURATION_UNAVAILABLE"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=error.code) from error

    payload = verified.payload
    if payload["tenantId"] != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BILLING_QR_INVOICE_NOT_FOUND",
        )
    if payload["documentType"] != "INVOICE":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="BILLING_QR_DOCUMENT_TYPE_UNSUPPORTED",
        )

    try:
        document = _find_tenant_invoice(
            _require_db(),
            tenant_id,
            invoice_id=payload["documentId"],
            trace_id=payload["traceId"],
        )
    except HTTPException:
        raise
    except Exception as error:
        _log_error(error, "VERIFY_SIGNED_INVOICE_QR", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_QR_INVOICE_LOOKUP_UNAVAILABLE",
        ) from error
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BILLING_QR_INVOICE_NOT_FOUND",
        )

    canonical_invoice_id = _invoice_field(
        document, "invoice_number", "invoiceNumber", "invoice_id", "invoiceId"
    )
    persisted_trace_id = _invoice_trace_id(document, canonical_invoice_id)
    if (
        canonical_invoice_id is None
        or str(canonical_invoice_id) != payload["documentId"]
        or persisted_trace_id is None
        or str(persisted_trace_id) != payload["traceId"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BILLING_QR_PERSISTED_IDENTITY_MISMATCH",
        )

    persisted_amount = _invoice_field(
        document, "total_amount", "totalAmount", "total", "grand_total", "grandTotal"
    )
    if persisted_amount is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_QR_PERSISTED_AMOUNT_UNAVAILABLE",
        )
    try:
        amount_matches = float(persisted_amount) == float(payload["amount"])
    except (TypeError, ValueError, OverflowError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_QR_PERSISTED_AMOUNT_INVALID",
        ) from error
    if not amount_matches:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BILLING_QR_AMOUNT_MISMATCH",
        )

    persisted_currency = _invoice_field(document, "currency")
    if persisted_currency is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_QR_PERSISTED_CURRENCY_UNAVAILABLE",
        )
    if str(persisted_currency).upper() != payload["currency"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BILLING_QR_CURRENCY_MISMATCH",
        )

    persisted_seal = _invoice_field(
        document, "seal_hash", "sealHash", "proof_hash", "proofHash"
    )
    seal_reference_matches = (
        not payload["sealHash"]
        or (
            persisted_seal is not None
            and str(persisted_seal).upper() == payload["sealHash"].upper()
        )
    )
    if not seal_reference_matches:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BILLING_QR_SEAL_REFERENCE_MISMATCH",
        )

    return {
        "valid": True,
        "signatureValid": True,
        "tenantScopedInvoiceFound": True,
        "amountMatches": True,
        "sealReferenceMatches": bool(payload["sealHash"]),
        "verificationMode": "LEGACY_SIGNED_QR_PERSISTED_INVOICE_MATCH",
        "tenantId": tenant_id,
        "documentId": payload["documentId"],
        "traceId": payload["traceId"],
        "documentType": payload["documentType"],
        "amount": payload["amount"],
        "currency": payload["currency"],
        "sealHash": payload["sealHash"],
        "merkleRoot": payload["merkleRoot"],
        "pkiVerification": "NOT_PERFORMED",
        "paymentExecution": "NOT_EVALUATED",
        "settlement": "NOT_EVALUATED",
    }


@router.get("/audit/events", response_model=List[Dict[str, Any]])
async def list_billing_audit_events(
    limit: int = Query(default=100, ge=1, le=250),
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
    ),
) -> List[Dict[str, Any]]:
    """Expose persisted billing events only inside the authorized tenant.

    Authority: Requires canonical audit:read authorization.
    Tenant scope: Query derives from TenantAuthorizationContext only.
    Mutation: Read-only; no synthetic audit event is created.
    """
    tenant_id = authorization.tenant_id
    try:
        rows = list(
            _require_db()["billing_audit_events"]
            .find({"tenant_id": tenant_id}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
    except Exception as error:
        _log_error(error, "LIST_BILLING_AUDIT_EVENTS", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_AUDIT_EVENTS_UNAVAILABLE",
        ) from error
    return rows


@router.get("/audit/integrity", response_model=Dict[str, Any])
async def get_audit_integrity(
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
    ),
) -> Dict[str, Any]:
    """Read source-provided integrity controls for the authorized tenant.

    The explicit EOS_DEFAULTS source is a configured default posture, not proof
    that the values were persisted or independently executed.
    """
    tenant_id = authorization.tenant_id
    try:
        value = _require_db()["billing_integrity_controls"].find_one(
            {"tenant_id": tenant_id}, {"_id": 0}
        )
    except Exception as error:
        _log_error(error, "GET_BILLING_AUDIT_INTEGRITY", tenant_id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_AUDIT_INTEGRITY_UNAVAILABLE",
        ) from error
    return value or {
        "tenant_id": tenant_id,
        "auto_renew": True,
        "encrypted_backup": True,
        "neural_sync": False,
        "source": "EOS_DEFAULTS",
    }


@router.patch("/audit/integrity", response_model=Dict[str, Any])
async def update_audit_integrity(
    payload: Dict[str, bool],
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
    ),
) -> Dict[str, Any]:
    """Deny integrity-control mutation until a governed Python EOS write exists."""
    del payload, authorization
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="AUDIT_INTEGRITY_WRITE_AUTHORITY_UNAVAILABLE",
    )


@router.get("/forensic-status", response_model=ForensicStatusResponse)
async def get_forensic_status(
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        platform_invoices_coll = _require_db()["platform_invoices"]
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


DUNNING_DEFAULT_POLICY = {
    "reminder_day": 3,
    "warning_day": 7,
    "critical_day": 10,
    "suspension_day": 14,
    "collections_day": 21,
    "termination_day": 30,
}


def _normalize_dunning_policy(payload: Dict[str, Any]) -> Dict[str, int]:
    """Use the canonical deterministic dunning policy validator."""
    from tools.eos.saas.billing.platform_dunning_evaluator import (
        PlatformDunningEvaluationError,
        normalize_policy,
    )
    try:
        return normalize_policy(payload)
    except PlatformDunningEvaluationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


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
    """Partial settlement requires governed Kennel execution and settlement evidence."""
    _raise_financial_authority_conflict(
        "BILLING_PARTIAL_SETTLEMENT_REQUIRES_KENNEL"
    )


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
        if raw == "paid":
            _raise_financial_authority_conflict(
                "BILLING_PAID_STATE_REQUIRES_KENNEL_SETTLEMENT_EVIDENCE"
            )
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
async def get_dunning_state(
    subscription_id: Optional[str] = None,
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_DUNNING_PROJECTION_READ_AUTHORIZATION
    ),
):
    """Return collection projections separately from authoritative subscription lifecycle.

    A dunning projection is never an entitlement, suspension, termination, or
    access-control decision. Lifecycle enforcement must resolve SubscriptionRegistry.
    """
    tenant_id = authorization.tenant_id
    from tools.eos.saas.billing.platform_dunning_registry import COLLECTION as DUNNING_PROJECTION_COLLECTION
    query: Dict[str, Any] = {"tenant_id": tenant_id}
    if subscription_id:
        query["subscription_id"] = subscription_id
    rows = list(
        _require_db()[DUNNING_PROJECTION_COLLECTION]
        .find(query, {"_id": 0})
        .sort("updated_at", -1)
        .limit(100)
    )
    return {
        "success": True,
        "tenant_id": tenant_id,
        "states": [],
        "dunning_projections": rows,
        "access_posture_source": "SUBSCRIPTION_REGISTRY_REQUIRED",
    }

async def evaluate_tenant_dunning_lifecycle(
    tenant_id: str,
    body: DunningEvaluationRequest,
) -> Dict[str, Any]:
    """Aggregate tenant platform invoices into an atomic dunning projection.

    Subscription lifecycle, access, entitlements, and financial execution are
    not mutated by this collection-workflow evaluator.
    """
    from tools.eos.saas.billing.platform_dunning_registry import (
        PlatformDunningRegistry,
        PlatformDunningRegistryError,
        PlatformDunningRevisionConflict,
        COLLECTION as DUNNING_PROJECTION_COLLECTION,
    )
    from tools.eos.saas.billing.platform_dunning_evaluator import (
        PlatformDunningEvaluationError,
        evaluate_platform_dunning,
    )

    coll_db = _require_db()
    now = datetime.now(timezone.utc)
    invoice_query: Dict[str, Any] = {
        "$or": [{"tenant_id": tenant_id}, {"tenantId": tenant_id}],
    }
    if body.subscription_id:
        invoice_query["$and"] = [{
            "$or": [
                {"subscription_id": body.subscription_id},
                {"subscriptionId": body.subscription_id},
            ]
        }]
    projection_collection = coll_db[DUNNING_PROJECTION_COLLECTION]
    audit_collection = coll_db["billing_audit_events"]
    PlatformDunningRegistry.ensure_indexes(projection_collection)
    audit_collection.create_index(
        [
            ("tenant_id", 1),
            ("event_type", 1),
            ("subscription_id", 1),
            ("revision", 1),
        ],
        unique=True,
        partialFilterExpression={"event_type": "DUNNING_PROJECTION_TRANSITION"},
        name="dunning_projection_transition_audit_unique",
    )

    def evaluate(session: Any = None) -> Dict[str, Any]:
        policy_doc = coll_db["billing_dunning_policies"].find_one(
            {"tenant_id": tenant_id}, {"_id": 0}, session=session
        ) or {}
        policy = _normalize_dunning_policy(
            policy_doc.get("policy", DUNNING_DEFAULT_POLICY)
        )
        invoices = list(
            coll_db["platform_invoices"].find(
                invoice_query, {"_id": 0}, session=session
            )
        )
        result = evaluate_platform_dunning(
            tenant_id=tenant_id,
            invoices=invoices,
            policy=policy,
            projection_collection=projection_collection,
            now=now,
            dry_run=body.dry_run,
            subscription_id=body.subscription_id,
            session=session,
        )
        if not body.dry_run:
            for transition in result["transitions"]:
                audit = {
                    "tenant_id": tenant_id,
                    "event_type": "DUNNING_PROJECTION_TRANSITION",
                    "subscription_id": transition["subscription_id"],
                    "revision": transition["revision"],
                    "proof_hash": transition["transition_fingerprint"],
                    "metadata": transition,
                    "created_at": now,
                }
                audit_collection.update_one(
                    {
                        "tenant_id": tenant_id,
                        "event_type": "DUNNING_PROJECTION_TRANSITION",
                        "subscription_id": transition["subscription_id"],
                        "revision": transition["revision"],
                    },
                    {"$setOnInsert": audit},
                    upsert=True,
                    session=session,
                )
        return {**result, "policy": policy}

    try:
        if body.dry_run:
            result = evaluate()
        else:
            # The route owns the transaction; registries receive its session.
            with coll_db.client.start_session() as session:
                with session.start_transaction():
                    result = evaluate(session)
    except PlatformDunningRevisionConflict:
        raise HTTPException(
            status_code=409,
            detail="DUNNING_PROJECTION_REVISION_CONFLICT; retry from current projection",
        )
    except HTTPException:
        raise
    except (PlatformDunningRegistryError, PlatformDunningEvaluationError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except Exception as error:
        # Includes transient and unknown-commit outcomes; a failed response
        # must never be interpreted as proof that the transaction rolled back.
        raise HTTPException(
            status_code=503,
            detail="DUNNING_TRANSACTION_OUTCOME_UNCERTAIN",
        ) from error

    if not body.dry_run:
        for transition in result["transitions"]:
            _telemetry(
                tenant_id,
                "BILLING",
                "DUNNING_PROJECTION_TRANSITION",
                "billing_router",
                transition,
            )
    return {
        **result,
        "subscription_lifecycle_mutated": False,
    }

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
async def evaluate_dunning_lifecycle(
    body: DunningEvaluationRequest,
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_DUNNING_PROJECTION_EVALUATE_AUTHORIZATION
    ),
):
    """Evaluates overdue platform invoices and persists collection workflow projections only.

    Repeated calls are idempotent while source evidence is unchanged. Projection
    stages do not suspend, terminate, or grant/revoke subscription access.
    Subscription lifecycle remains exclusively owned by SubscriptionRegistry.
    """
    return await evaluate_tenant_dunning_lifecycle(authorization.tenant_id, body)


@router.post("/merkle/verify", response_model=Dict[str, Any])
@router.post("/audit/verifyChain", response_model=Dict[str, Any])
async def verify_invoice_chain(
    body: MerkleVerifyBody,
    authorization: TenantAuthorizationContext = Depends(
        _BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
    ),
) -> Dict[str, Any]:
    """Check a persisted invoice proof reference inside the authorized tenant.

    A valid result means a matching SHA3-512-shaped reference exists in a
    tenant-owned invoice or billing audit record. This lookup does not replay a
    Merkle chain, verify a QR signature, validate document content, or establish
    payment or settlement truth. A caller-supplied tenant field is accepted for
    wire compatibility only and is never used for lookup or audit scope.
    """
    tenant_id = authorization.tenant_id
    candidate = next(
        (
            value.strip()
            for value in (body.sealHash, body.seal_hash, body.proofHash, body.proof_hash)
            if isinstance(value, str) and value.strip()
        ),
        "",
    )
    if not re.fullmatch(r"[A-Fa-f0-9]{128}", candidate):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="BILLING_PROOF_HASH_INVALID",
        )

    seal = candidate.upper()
    hash_values = [seal, seal.lower()]
    tenant_query = {
        "$or": [
            {"tenant_id": tenant_id},
            {"tenantId": tenant_id},
        ]
    }
    hash_query = {
        "$or": [
            {field: {"$in": hash_values}}
            for field in ("proof_hash", "proofHash", "seal_hash", "sealHash")
        ]
    }
    scoped_query = {"$and": [tenant_query, hash_query]}

    try:
        coll_db = _require_db()
        invoice_hit = coll_db["platform_invoices"].find_one(scoped_query)
        if not invoice_hit:
            invoice_hit = coll_db["client_invoices"].find_one(scoped_query)

        audit_hit = coll_db["billing_audit_events"].find_one(
            {
                "$and": [
                    tenant_query,
                    {
                        "$or": [
                            {"proof_hash": {"$in": hash_values}},
                            {"proofHash": {"$in": hash_values}},
                        ]
                    },
                ]
            }
        )
        valid = bool(invoice_hit or audit_hit)
        coll_db["billing_audit_events"].insert_one(
            {
                "tenant_id": tenant_id,
                "event_type": "BILLING_PROOF_REFERENCE_CHECKED",
                "proof_hash": seal,
                "valid": valid,
                "verification_scope": "AUTHORIZED_TENANT",
                "created_at": datetime.now(timezone.utc),
            }
        )
    except HTTPException:
        raise
    except Exception as error:
        _log_error(
            error,
            "BILLING_PROOF_REFERENCE_VERIFICATION_FAILED",
            tenant_id=tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="BILLING_PROOF_REFERENCE_VERIFICATION_UNAVAILABLE",
        ) from error

    return {
        "success": True,
        "valid": valid,
        "sealHash": seal,
        "tenantId": tenant_id,
        "matchedInvoice": bool(invoice_hit),
        "matchedAudit": bool(audit_hit),
        "algorithm": "SHA3-512",
        "verificationMode": "PERSISTED_REFERENCE_MATCH",
        "verificationScope": "AUTHORIZED_TENANT",
        "verifiedAt": datetime.now(timezone.utc).isoformat(),
    }


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
INSTITUTIONAL CERTIFICATION SEAL — WILSY OS BILLING ROUTER v1.12.1-EOS-QR-PERSISTED-SOURCE-BOUNDARY
════════════════════════════════════════════════════════════════════════════════
Status:          ENGINEERING ARTIFACT — PRODUCTION ACTIVATION NOT CERTIFIED
Version:         v1.12.1-EOS-QR-PERSISTED-SOURCE-BOUNDARY
Fixes:           Financial-truth HTTP firewall; canonical billing-intelligence authorization seam and P4/P6B/P6A/P6C WILSY AI capacity seams preserved.
Compliance:      POPIA §19 │ GDPR §32 │ SOC2 §CC7.2 │ ISO 27001
Note:            Plan catalogue authority is PlanRegistry; Kennel remains exclusive financial execution authority. Dunning is a separate collection projection and cannot mutate subscription lifecycle or access.
════════════════════════════════════════════════════════════════════════════════
"""

# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tools/eos/api/billing_router.py
# VERSION: v1.12.1-EOS-QR-PERSISTED-SOURCE-BOUNDARY
# AUTHORITY BOUNDARY:
#   Python HTTP transport/composition only; no provider execution or settlement.
# TENANT POSTURE:
#   Audit reads and QR issue/verify use TenantAuthorizationContext. Integrity
#   controls are read-only until governed write authority is established.
# FAIL-CLOSED POSTURE:
#   Payment status, refund, partial settlement, paid state, and paid-at caller
#   mutation are rejected before billing-registry mutation. QR validation is
#   read-only and requires the signed tenant and invoice to match current IAM.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
