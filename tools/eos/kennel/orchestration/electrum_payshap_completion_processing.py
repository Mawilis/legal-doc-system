"""Process durable Electrum PayShap completion inbox events atomically.

HTTP ingress only verifies, stores and acknowledges provider messages. This
worker composes canonical tenant/payment correlation, settlement observation,
partial invoice allocation, audit/outbox and inbox completion in one
caller-owned Mongo transaction.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    TransportDisposition,
)
from tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion import (
    AuthenticatedSettlementTransportEvidence,
    ingest_authenticated_settlement_observation,
)
from tools.eos.kennel.registry.electrum_payshap_completion_inbox_registry import (
    ElectrumCompletionInboxError,
    ElectrumPayShapCompletionInboxEvent,
    ElectrumPayShapCompletionInboxRegistry,
)
from tools.eos.kennel.registry.electrum_provider_tenant_binding_registry import (
    ElectrumProviderTenantBindingRegistry,
)
from tools.eos.kennel.registry.financial_settlement_observation_registry import (
    FinancialSettlementObservationRegistry,
)
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import (
    PlatformBillingFinancialExecutionTruthRegistry,
)
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.saas.billing.platform_invoice_settlement_allocation import (
    allocate_settlement_observation_to_platform_invoice,
)


class ElectrumPayShapCompletionProcessingError(RuntimeError):
    pass


def ensure_electrum_payshap_completion_indexes(
    *,
    inbox_collection: Collection,
    binding_collection: Collection,
    observation_collection: Collection,
    platform_truth_collection: Collection,
    allocation_collection: Collection,
    audit_collection: Collection,
    outbox_collection: Collection,
) -> None:
    """Provision provider inbox/binding and allocation indexes outside transactions."""
    ElectrumPayShapCompletionInboxRegistry.ensure_indexes(inbox_collection)
    ElectrumProviderTenantBindingRegistry.ensure_indexes(binding_collection)
    FinancialSettlementObservationRegistry.ensure_indexes(observation_collection)
    platform_truth_collection.create_index(
        [("tenant_id", 1), ("provider_execution_reference", 1)],
        name="ix_platform_truth_provider_execution_reference",
    )
    from tools.eos.saas.billing.platform_invoice_settlement_allocation import (
        ensure_platform_invoice_settlement_allocation_indexes,
    )
    ensure_platform_invoice_settlement_allocation_indexes(
        allocation_collection, audit_collection, outbox_collection
    )


def process_electrum_payshap_completion_event(
    message_id: str,
    *,
    inbox_collection: Collection,
    binding_collection: Collection,
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
    processed_at: datetime,
) -> dict[str, Any]:
    """Apply one inbox completion; the caller owns commit, retry and recovery."""
    if session is None or not bool(getattr(session, "in_transaction", False)):
        raise ElectrumPayShapCompletionProcessingError("ELECTRUM_PROCESSING_CALLER_TRANSACTION_REQUIRED")
    if not isinstance(processed_at, datetime) or processed_at.tzinfo is None:
        raise ElectrumPayShapCompletionProcessingError("ELECTRUM_PROCESSING_TIMESTAMP_INVALID")

    event, raw = ElectrumPayShapCompletionInboxRegistry.get(
        "ELECTRUM", message_id, inbox_collection, session=session
    )
    state = raw.get("processing_status")
    if state in {"PROCESSED", "IGNORED"}:
        return {
            "message_id": message_id,
            "processing_status": state,
            "allocation_id": raw.get("allocation_id"),
            "replayed": True,
        }
    revision = raw.get("processing_revision")
    if (
        state != "PENDING"
        or isinstance(revision, bool)
        or not isinstance(revision, int)
        or revision < 0
    ):
        raise ElectrumCompletionInboxError("ELECTRUM_INBOX_PROCESSING_STATE_INVALID")

    if event.outcome != "APPROVED":
        ElectrumPayShapCompletionInboxRegistry.mark_processed(
            event,
            collection=inbox_collection,
            session=session,
            processed_at=processed_at,
            allocation_id=None,
            ignored=True,
            expected_revision=revision,
        )
        return {
            "message_id": message_id,
            "processing_status": "IGNORED",
            "allocation_id": None,
            "replayed": False,
        }

    binding = ElectrumProviderTenantBindingRegistry.get_by_creditor_account_fingerprint(
        event.creditor_account_fingerprint, binding_collection, session=session
    )
    tenant_id = binding["tenant_id"]
    truth_docs = list(platform_truth_collection.find(
        {
            "tenant_id": tenant_id,
            "provider_execution_reference": event.uetr,
        },
        session=session,
    ).limit(2))
    if len(truth_docs) != 1:
        raise ElectrumPayShapCompletionProcessingError("ELECTRUM_EXECUTION_TRUTH_NOT_UNIQUE")
    platform_truth = PlatformBillingFinancialExecutionTruthRegistry.get(
        tenant_id,
        truth_docs[0]["execution_truth_id"],
        platform_truth_collection,
        session=session,
    )
    if (
        platform_truth.execution_status is not PlatformExecutionStatus.EXECUTED
        or platform_truth.provider_execution_reference != event.uetr
        or platform_truth.currency != event.currency
        or platform_truth.payment_destination_reference != binding["payment_destination_reference"]
    ):
        raise ElectrumPayShapCompletionProcessingError("ELECTRUM_EXECUTION_CORRELATION_MISMATCH")

    observation_id = f"electrum-payshap-completion-{event.message_id}"
    evidence = AuthenticatedSettlementTransportEvidence(
        tenant_id=tenant_id,
        provider_name=platform_truth.provider,
        provider_execution_reference=event.uetr,
        settlement_reference=event.transaction_reference,
        provider_settlement_evidence_reference=event.message_id,
        settled_amount_minor=event.amount_minor,
        currency=event.currency,
        payment_destination_reference=binding["payment_destination_reference"],
        observed_at=event.received_at,
        settled_at=event.message_created_at,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
    )
    observation = ingest_authenticated_settlement_observation(
        tenant_id,
        evidence,
        execution_truth_id=platform_truth.source_execution_fact_id,
        execution_truth_collection=execution_truth_collection,
        observation_collection=observation_collection,
        session=session,
    )
    if observation.observation_id != observation_id:
        # The canonical ingestion owns its observation identity. The event id
        # must still be traceable to the resulting durable observation.
        observation_id = observation.observation_id

    allocation_result = allocate_settlement_observation_to_platform_invoice(
        tenant_id,
        observation_id,
        observation_collection=observation_collection,
        execution_truth_collection=execution_truth_collection,
        platform_truth_collection=platform_truth_collection,
        release_authorization_collection=release_authorization_collection,
        platform_invoice_collection=platform_invoice_collection,
        allocation_collection=allocation_collection,
        audit_collection=audit_collection,
        outbox_collection=outbox_collection,
        subscription_collection=subscription_collection,
        session=session,
        allocated_at=processed_at,
    )
    allocation = allocation_result["allocation"]
    ElectrumPayShapCompletionInboxRegistry.mark_processed(
        event,
        collection=inbox_collection,
        session=session,
        processed_at=processed_at,
        allocation_id=allocation.allocation_id,
        expected_revision=revision,
    )
    return {
        "message_id": message_id,
        "processing_status": "PROCESSED",
        "allocation_id": allocation.allocation_id,
        "allocation_status": allocation.allocation_status,
        "replayed": bool(allocation_result.get("replayed", False)),
    }


__all__ = [
    "ElectrumPayShapCompletionProcessingError",
    "ensure_electrum_payshap_completion_indexes",
    "process_electrum_payshap_completion_event",
]
