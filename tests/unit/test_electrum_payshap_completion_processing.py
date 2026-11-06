from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.orchestration.electrum_payshap_completion_processing import (
    process_electrum_payshap_completion_event,
)
from tools.eos.kennel.registry.electrum_payshap_completion_inbox_registry import (
    ElectrumPayShapCompletionInboxEvent,
)


NOW = datetime(2026, 11, 5, 8, 0, tzinfo=timezone.utc)


def _event(outcome="APPROVED"):
    return ElectrumPayShapCompletionInboxEvent(
        provider_name="ELECTRUM",
        message_id="message-1",
        message_created_at=NOW,
        uetr="8f14e45f-ea5e-4f5f-9c5d-8f14e45fea5e",
        transaction_reference="transaction-1",
        outcome=outcome,
        payment_scheme="ZA_RPP",
        payment_method="CreditTransfer",
        amount_minor=4000,
        currency="ZAR",
        settlement_date="2026-11-05",
        creditor_account_fingerprint="a" * 64,
        content_digest="b" * 64,
        signature_key_id="electrum-key-1",
        received_at=NOW,
    )


def _args():
    return dict(
        inbox_collection=Mock(),
        binding_collection=Mock(),
        observation_collection=Mock(),
        execution_truth_collection=Mock(),
        platform_truth_collection=Mock(),
        release_authorization_collection=Mock(),
        platform_invoice_collection=Mock(),
        allocation_collection=Mock(),
        audit_collection=Mock(),
        outbox_collection=Mock(),
        subscription_collection=None,
        session=Mock(in_transaction=True),
        processed_at=NOW,
    )


def test_non_approved_completion_is_durably_ignored_without_allocation():
    event = _event("REJECTED")
    raw = {"processing_status": "PENDING", "processing_revision": 0}
    args = _args()
    with patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.ElectrumPayShapCompletionInboxRegistry.get",
        return_value=(event, raw),
    ), patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.ElectrumPayShapCompletionInboxRegistry.mark_processed"
    ) as mark, patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.allocate_settlement_observation_to_platform_invoice"
    ) as allocate:
        result = process_electrum_payshap_completion_event("message-1", **args)
    assert result["processing_status"] == "IGNORED"
    mark.assert_called_once()
    assert mark.call_args.kwargs["ignored"] is True
    allocate.assert_not_called()


def test_approved_completion_allocates_and_marks_inbox_in_same_session():
    event = _event()
    raw = {"processing_status": "PENDING", "processing_revision": 0}
    args = _args()
    args["platform_truth_collection"].find.return_value.limit.return_value = [
        {"tenant_id": "tenant-a", "execution_truth_id": "platform-truth-1"}
    ]
    platform_truth = SimpleNamespace(
        execution_status=PlatformExecutionStatus.EXECUTED,
        provider_execution_reference=event.uetr,
        currency="ZAR",
        payment_destination_reference="destination-1",
        source_execution_fact_id="fact-1",
        provider="PAYSHAP",
    )
    observation = SimpleNamespace(observation_id="settlement-observation-fact-1-transaction-1")
    allocation = SimpleNamespace(allocation_id="allocation-1", allocation_status="PARTIAL")
    with patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.ElectrumPayShapCompletionInboxRegistry.get",
        return_value=(event, raw),
    ), patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.ElectrumProviderAccountBindingRegistry.get_by_creditor_account_fingerprint",
        return_value={"payment_destination_reference": "destination-1"},
    ), patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.PlatformBillingFinancialExecutionTruthRegistry.get",
        return_value=platform_truth,
    ), patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.ingest_authenticated_settlement_observation",
        return_value=observation,
    ) as ingest, patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.allocate_settlement_observation_to_platform_invoice",
        return_value={"allocation": allocation, "replayed": False},
    ) as allocate, patch(
        "tools.eos.kennel.orchestration.electrum_payshap_completion_processing.ElectrumPayShapCompletionInboxRegistry.mark_processed"
    ) as mark:
        result = process_electrum_payshap_completion_event("message-1", **args)
    assert result["processing_status"] == "PROCESSED"
    assert result["allocation_id"] == "allocation-1"
    assert ingest.call_args.kwargs["session"] is args["session"]
    assert allocate.call_args.kwargs["session"] is args["session"]
    assert mark.call_args.kwargs["session"] is args["session"]
    assert mark.call_args.kwargs["allocation_id"] == "allocation-1"
