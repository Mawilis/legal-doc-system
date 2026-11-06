"""Allocate verified settlement observations against platform invoices atomically.

The caller owns the active Mongo transaction. This module records partial
allocations; it does not create provider evidence or mutate subscription
lifecycle state. The full-settlement evidence bridge remains unchanged.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pymongo.collection import Collection

from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.registry.financial_execution_registry import FinancialExecutionFactRegistry
from tools.eos.kennel.registry.financial_settlement_observation_registry import FinancialSettlementObservationRegistry
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.domain.billing import InvoiceStatus, PlatformInvoice
from tools.eos.saas.domain.money import SUPPORTED_CURRENCY_EXPONENTS, to_minor_units
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.platform_invoice_settlement_allocation import PlatformInvoiceSettlementAllocation
from tools.eos.saas.billing.platform_invoice_settlement_allocation_registry import (
    PlatformInvoiceSettlementAllocationNotFound,
    PlatformInvoiceSettlementAllocationRegistry,
)


class PlatformInvoiceSettlementAllocationOrchestrationError(RuntimeError):
    pass


def ensure_platform_invoice_settlement_allocation_indexes(
    allocation_collection: Collection,
    audit_collection: Collection,
    outbox_collection: Collection,
) -> None:
    """Provision tenant-scoped immutable allocation, audit, and outbox keys.

    Run as an explicit schema/index migration outside business transactions.
    """
    PlatformInvoiceSettlementAllocationRegistry.ensure_indexes(allocation_collection)
    for collection, name in (
        (audit_collection, "uq_billing_settlement_audit_event"),
        (outbox_collection, "uq_billing_settlement_outbox_event"),
    ):
        collection.create_index(
            [("tenant_id", 1), ("event_key", 1)],
            unique=True,
            name=name,
            partialFilterExpression={"event_key": {"$type": "string"}},
        )


def _major(minor: int, currency: str) -> float:
    exponent = SUPPORTED_CURRENCY_EXPONENTS[currency]
    return float(Decimal(minor) / (Decimal(10) ** exponent))


def _insert_event(collection: Collection, event: dict[str, Any], *, session, code: str) -> dict:
    existing = collection.find_one(
        {"tenant_id": event["tenant_id"], "event_key": event["event_key"]},
        session=session,
    )
    if existing is not None:
        saved = {key: value for key, value in existing.items() if key != "_id"}
        if saved != event:
            # Outbox delivery metadata is mutable; immutable audit is not.
            if code == "ALLOCATION_OUTBOX_CONFLICT":
                mutable = {"delivery_status", "delivery_attempts", "available_at", "updated_at", "delivered_at", "claimed_by", "lease_token", "lease_until", "last_error_code"}
                if {k: v for k, v in saved.items() if k not in mutable} == {k: v for k, v in event.items() if k not in mutable}:
                    return saved
            raise PlatformInvoiceSettlementAllocationOrchestrationError(code)
        return saved
    collection.insert_one(event, session=session)
    return event


def allocate_settlement_observation_to_platform_invoice(
    tenant_id: str,
    observation_id: str,
    *,
    observation_collection: Collection,
    execution_truth_collection: Collection,
    platform_truth_collection: Collection,
    release_authorization_collection: Collection,
    platform_invoice_collection: Collection,
    allocation_collection: Collection,
    audit_collection: Collection,
    outbox_collection: Collection,
    subscription_collection: Collection | None,
    session,
    allocated_at: datetime,
) -> dict[str, Any]:
    """Persist one immutable allocation and update invoice balance in one transaction."""
    if session is None or not bool(getattr(session, "in_transaction", False)):
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_ACTIVE_SESSION_REQUIRED")
    if not isinstance(allocated_at, datetime) or allocated_at.tzinfo is None:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_TIMESTAMP_INVALID")

    try:
        replay = PlatformInvoiceSettlementAllocationRegistry.get_by_observation(
            tenant_id, observation_id, allocation_collection, session=session
        )
        return {"allocation": replay, "replayed": True}
    except PlatformInvoiceSettlementAllocationNotFound:
        pass

    observation = FinancialSettlementObservationRegistry.get(
        tenant_id, observation_id, observation_collection, session=session
    )
    truth = FinancialExecutionFactRegistry.get(
        tenant_id, observation.execution_truth_id, execution_truth_collection, session=session
    )
    if (
        observation.tenant_id != tenant_id
        or truth.execution_status is not FinancialExecutionStatus.EXECUTED
        or (observation.execution_truth_id, observation.provider_name, observation.provider_execution_reference,
            observation.currency, observation.payment_destination_reference)
        != (truth.execution_fact_id, truth.provider, truth.provider_execution_reference,
            truth.currency, truth.payment_destination_reference)
        or observation.settled_amount_minor > truth.executed_amount_minor
    ):
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_EXECUTION_PROVENANCE_MISMATCH")

    platform_truth_docs = list(platform_truth_collection.find(
        {"tenant_id": tenant_id, "source_execution_fact_id": truth.execution_fact_id},
        session=session,
    ).limit(2))
    if len(platform_truth_docs) != 1:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_PLATFORM_TRUTH_NOT_UNIQUE")
    platform_truth = PlatformBillingFinancialExecutionTruthRegistry.get(
        tenant_id, platform_truth_docs[0]["execution_truth_id"], platform_truth_collection, session=session
    )
    if (
        platform_truth.execution_status is not PlatformExecutionStatus.EXECUTED
        or platform_truth.source_execution_fact_id != truth.execution_fact_id
        or platform_truth.source_execution_fact_fingerprint != truth.fingerprint
        or (platform_truth.provider, platform_truth.provider_execution_reference,
            platform_truth.currency, platform_truth.payment_destination_reference)
        != (observation.provider_name, observation.provider_execution_reference,
            observation.currency, observation.payment_destination_reference)
        or observation.settled_amount_minor > platform_truth.executed_amount_minor
    ):
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_PLATFORM_TRUTH_MISMATCH")
    authorization = PlatformBillingReleaseAuthorizationRegistry.get(
        tenant_id, platform_truth.release_authorization_id, release_authorization_collection, session=session
    )
    doc = platform_invoice_collection.find_one(
        {"tenant_id": tenant_id, "invoice_id": platform_truth.platform_invoice_id},
        session=session,
    )
    if doc is None:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_INVOICE_NOT_FOUND")
    invoice = PlatformInvoice.from_dict(dict(doc))
    if (
        invoice.tenant_id != tenant_id
        or invoice.currency != observation.currency
        or authorization.tenant_id != tenant_id
        or authorization.platform_invoice_id != invoice.invoice_id
        or authorization.currency != invoice.currency
        or authorization.authorized_amount_minor != invoice.release_amount_minor
        or authorization.platform_invoice_evidence_fingerprint != invoice.commercial_release_evidence_fingerprint
        or authorization.payment_destination_reference != platform_truth.payment_destination_reference
        or platform_truth.release_authorization_fingerprint != authorization.release_authorization_fingerprint
    ):
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_INVOICE_PROVENANCE_MISMATCH")
    if invoice.status in {InvoiceStatus.PAID, InvoiceStatus.VOID, InvoiceStatus.CANCELLED} or invoice.paid_at is not None:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_INVOICE_NOT_OPEN")

    subscription_id = doc.get("subscription_id", doc.get("subscriptionId"))
    if subscription_id is not None:
        if not isinstance(subscription_id, str) or not subscription_id.strip() or subscription_collection is None:
            raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_SUBSCRIPTION_LINK_INVALID")
        try:
            subscription = SubscriptionRegistry.get(
                subscription_id, tenant_id_header=tenant_id,
                collection=subscription_collection, session=session,
            )
        except Exception as error:
            raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_SUBSCRIPTION_TRUTH_INVALID") from error
        if subscription is None or subscription.tenant_id != tenant_id or subscription.subscription_id != subscription_id:
            raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_SUBSCRIPTION_NOT_FOUND")

    total_minor = invoice.release_amount_minor
    paid_minor = to_minor_units(invoice.amount_paid, invoice.currency)
    outstanding_minor = to_minor_units(invoice.outstanding_amount, invoice.currency)
    if total_minor <= 0 or paid_minor < 0 or outstanding_minor != total_minor - paid_minor:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_INVOICE_BALANCE_CORRUPT")
    amount_minor = observation.settled_amount_minor
    if amount_minor <= 0 or amount_minor > outstanding_minor:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_OVERPAYMENT_REJECTED")

    prior_execution_allocations = list(allocation_collection.find(
        {"tenant_id": tenant_id, "execution_truth_id": truth.execution_fact_id}, session=session
    ))
    if sum(int(item.get("amount_minor", 0)) for item in prior_execution_allocations) + amount_minor > platform_truth.executed_amount_minor:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_EXECUTION_OVERALLOCATION")
    sequence = allocation_collection.count_documents(
        {"tenant_id": tenant_id, "invoice_id": invoice.invoice_id}, session=session
    ) + 1
    remaining = outstanding_minor - amount_minor
    allocation = PlatformInvoiceSettlementAllocation(
        tenant_id=tenant_id,
        allocation_id=f"invoice-allocation-{tenant_id}-{observation.observation_id}",
        observation_id=observation.observation_id,
        observation_fingerprint=observation.fingerprint,
        execution_truth_id=observation.execution_truth_id,
        invoice_id=invoice.invoice_id,
        invoice_evidence_fingerprint=invoice.commercial_release_evidence_fingerprint,
        currency=invoice.currency,
        amount_minor=amount_minor,
        cumulative_paid_minor=paid_minor + amount_minor,
        outstanding_minor=remaining,
        allocation_sequence=sequence,
        allocated_at=allocated_at.astimezone(timezone.utc),
        allocation_status="FINAL" if remaining == 0 else "PARTIAL",
    )
    PlatformInvoiceSettlementAllocationRegistry.create(allocation, allocation_collection, session=session)

    status = InvoiceStatus.PAID.value if remaining == 0 else invoice.status.value
    update = {
        "$set": {
            "amount_paid": _major(paid_minor + amount_minor, invoice.currency),
            "amountPaid": _major(paid_minor + amount_minor, invoice.currency),
            "outstanding_amount": _major(remaining, invoice.currency),
            "outstandingAmount": _major(remaining, invoice.currency),
            "status": status,
            "settlement_state": "SETTLED" if remaining == 0 else "PARTIALLY_SETTLED",
            "settlement_allocation_revision": sequence,
            "settlement_allocation_fingerprint": allocation.fingerprint,
            "updated_at": allocated_at.astimezone(timezone.utc).isoformat(),
            "updatedAt": allocated_at.astimezone(timezone.utc).isoformat(),
        }
    }
    if remaining == 0:
        update["$set"]["paid_at"] = observation.settled_at
        update["$set"]["paidAt"] = observation.settled_at
    cas = {
        "tenant_id": tenant_id,
        "invoice_id": invoice.invoice_id,
        "status": doc.get("status"),
        "settlement_allocation_revision": doc.get("settlement_allocation_revision", 0),
    }
    # Match the exact persisted representation. Some historical invoices are
    # snake_case-only, some camelCase-only, and newer rows may carry both.
    for field in ("amount_paid", "amountPaid", "outstanding_amount", "outstandingAmount",
                  "currency", "total", "total_amount", "totalAmount", "paid_at", "paidAt"):
        if field in doc:
            cas[field] = doc[field]
    # The release fingerprint covers every field below. Bind every persisted
    # member in the invoice CAS so a concurrent commercial rewrite cannot be
    # settled against a stale snapshot.
    for field in (
        "release_amount_minor", "amount", "tax_amount", "taxAmount", "tax_type",
        "taxType", "line_items", "lineItems", "issued_at", "issuedAt", "due_at",
        "dueAt", "payment_terms_days", "paymentTermsDays", "collection_method",
        "collectionMethod", "billing_mode", "billingMode", "seller_jurisdiction",
        "sellerJurisdiction", "customer_jurisdiction", "customerJurisdiction",
        "subscription_id", "subscriptionId", "plan_id", "planId", "order_number",
        "orderNumber", "purchase_order", "purchaseOrder",
    ):
        if field in doc:
            cas[field] = doc[field]
    result = platform_invoice_collection.update_one(cas, update, session=session)
    if result.matched_count != 1:
        raise PlatformInvoiceSettlementAllocationOrchestrationError("ALLOCATION_INVOICE_REVISION_CONFLICT")

    event_key = f"platform-invoice-allocation:{tenant_id}:{allocation.allocation_id}"
    event = {
        "tenant_id": tenant_id,
        "event_key": event_key,
        "event_type": "PLATFORM_INVOICE_SETTLEMENT_ALLOCATED",
        "schema_version": "WILSY-INVOICE-SETTLEMENT-ALLOCATION/V1",
        "allocation_id": allocation.allocation_id,
        "allocation_fingerprint": allocation.fingerprint,
        "observation_id": observation.observation_id,
        "invoice_id": invoice.invoice_id,
        "amount_minor": amount_minor,
        "cumulative_paid_minor": paid_minor + amount_minor,
        "outstanding_minor": remaining,
        "currency": invoice.currency,
        "created_at": allocated_at.astimezone(timezone.utc).isoformat(),
    }
    audit = _insert_event(audit_collection, event, session=session, code="ALLOCATION_AUDIT_CONFLICT")
    outbox = _insert_event(
        outbox_collection,
        {**event, "delivery_status": "PENDING", "delivery_attempts": 0, "available_at": event["created_at"]},
        session=session,
        code="ALLOCATION_OUTBOX_CONFLICT",
    )
    return {"allocation": allocation, "audit_event": audit, "outbox_event": outbox, "replayed": False}
