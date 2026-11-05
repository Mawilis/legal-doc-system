from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from tools.eos.saas.billing.atomic_platform_settlement import (
    AtomicPlatformSettlementError,
    settle_platform_invoice_atomically,
)
from tools.eos.kennel.orchestration.authenticated_settlement_observation_ingestion import (
    AuthenticatedSettlementTransportEvidence,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    TransportDisposition,
)


def _evidence(tenant_id="tenant-a"):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return AuthenticatedSettlementTransportEvidence(
        tenant_id=tenant_id,
        provider_name="PAYSHAP",
        provider_execution_reference="provider-exec-1",
        settlement_reference="settlement-1",
        provider_settlement_evidence_reference="provider-settlement-1",
        settled_amount_minor=10000,
        currency="ZAR",
        payment_destination_reference="destination-1",
        observed_at=now,
        settled_at=now,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
    )


def _args(session):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    observation = SimpleNamespace(observation_id="observation-1")
    settlement = SimpleNamespace(
        settlement_evidence_id="settlement-evidence-1",
        fingerprint="f" * 128,
        platform_execution_truth_id="platform-truth-1",
        platform_invoice_id="invoice-1",
        created_at=now,
    )
    audit = Mock()
    audit.find_one.return_value = None
    outbox = Mock()
    outbox.find_one.return_value = None
    return {
        "tenant_id": "tenant-a",
        "transport_evidence": _evidence(),
        "execution_truth_id": "execution-fact-1",
        "platform_truth_id": "platform-truth-1",
        "execution_truth_collection": Mock(),
        "observation_collection": Mock(),
        "platform_truth_collection": Mock(),
        "settlement_evidence_collection": Mock(),
        "release_authorization_collection": Mock(),
        "platform_invoice_collection": Mock(),
        "commercial_projection_collection": Mock(),
        "subscription_collection": Mock(),
        "audit_collection": audit,
        "outbox_collection": outbox,
        "session": session,
        "created_at": now,
        "_observation": observation,
        "_settlement": settlement,
    }


def test_atomic_composition_forwards_one_caller_session_to_every_stage():
    session = Mock(in_transaction=True)
    args = _args(session)
    observation, settlement, projection = (
        args.pop("_observation"),
        args.pop("_settlement"),
        object(),
    )
    with (
        patch(
            "tools.eos.saas.billing.atomic_platform_settlement.ingest_authenticated_settlement_observation",
            return_value=("CREATED", observation),
        ) as ingest,
        patch(
            "tools.eos.saas.billing.atomic_platform_settlement.bridge_settlement_observation_to_platform_evidence",
            return_value=settlement,
        ) as bridge,
        patch(
            "tools.eos.saas.billing.atomic_platform_settlement.project_platform_billing_commercial_settlement",
            return_value=projection,
        ) as project,
    ):
        result = settle_platform_invoice_atomically(**args)

    assert result["observation"] is observation
    assert result["settlement_evidence"] is settlement
    assert result["commercial_projection"] is projection
    assert result["audit_event"]["event_key"] == (
        "platform-settlement:tenant-a:settlement-evidence-1"
    )
    assert result["outbox_event"]["delivery_status"] == "PENDING"
    assert args["audit_collection"].insert_one.call_args.kwargs["session"] is session
    assert args["outbox_collection"].insert_one.call_args.kwargs["session"] is session
    assert ingest.call_args.kwargs["session"] is session
    assert bridge.call_args.kwargs["session"] is session
    assert project.call_args.kwargs["session"] is session


def test_atomic_composition_rejects_missing_caller_transaction():
    args = _args(Mock(in_transaction=False))
    args.pop("_observation")
    args.pop("_settlement")
    with pytest.raises(AtomicPlatformSettlementError, match="ACTIVE_SESSION_REQUIRED"):
        settle_platform_invoice_atomically(**args)


def test_atomic_composition_rejects_cross_tenant_transport_evidence():
    args = _args(Mock(in_transaction=True))
    args["transport_evidence"] = _evidence("tenant-b")
    args.pop("_observation")
    args.pop("_settlement")
    with pytest.raises(AtomicPlatformSettlementError, match="TENANT_MISMATCH"):
        settle_platform_invoice_atomically(**args)


def test_atomic_audit_replay_conflict_fails_closed():
    from tools.eos.saas.billing.atomic_platform_settlement import _persist_audit_and_outbox

    session = Mock(in_transaction=True)
    settlement = _args(session)["_settlement"]
    audit = Mock()
    audit.find_one.return_value = {
        "tenant_id": "tenant-a",
        "event_key": "platform-settlement:tenant-a:settlement-evidence-1",
        "event_type": "TAMPERED",
    }
    with pytest.raises(AtomicPlatformSettlementError, match="AUDIT_REPLAY_CONFLICT"):
        _persist_audit_and_outbox(
            tenant_id="tenant-a",
            settlement_evidence=settlement,
            audit_collection=audit,
            outbox_collection=Mock(),
            session=session,
        )
    audit.insert_one.assert_not_called()


def test_settlement_observation_registry_preflights_exact_replay_before_insert():
    from tools.eos.kennel.domain.financial_settlement_observation import (
        FinancialSettlementObservation,
        SettlementObservationStatus,
    )
    from tools.eos.kennel.registry.financial_settlement_observation_registry import (
        FinancialSettlementObservationRegistry,
    )

    evidence = _evidence()
    value = FinancialSettlementObservation(
        tenant_id=evidence.tenant_id,
        observation_id="observation-replay-1",
        provider_name=evidence.provider_name,
        execution_truth_id="execution-fact-1",
        provider_execution_reference=evidence.provider_execution_reference,
        settlement_reference=evidence.settlement_reference,
        provider_settlement_evidence_reference=evidence.provider_settlement_evidence_reference,
        status=SettlementObservationStatus.SETTLED,
        settled_amount_minor=evidence.settled_amount_minor,
        currency=evidence.currency,
        payment_destination_reference=evidence.payment_destination_reference,
        observed_at=evidence.observed_at,
        settled_at=evidence.settled_at,
        evidence_strength=evidence.evidence_strength,
        transport_disposition=evidence.transport_disposition,
    )
    persisted = {**value.to_dict(), "observation_fingerprint": value.fingerprint}
    collection = Mock()
    collection.find_one.side_effect = [persisted]
    outcome, replayed = FinancialSettlementObservationRegistry.create(
        value, collection, session=Mock(in_transaction=True)
    )
    assert outcome == "IDEMPOTENT_REPLAY"
    assert replayed == value
    collection.insert_one.assert_not_called()


def test_settlement_observation_registry_rejects_divergent_replay_before_insert():
    from tools.eos.kennel.domain.financial_settlement_observation import (
        FinancialSettlementObservation,
        SettlementObservationStatus,
    )
    from tools.eos.kennel.registry.financial_settlement_observation_registry import (
        FinancialSettlementObservationConflictError,
        FinancialSettlementObservationRegistry,
    )

    evidence = _evidence()
    value = FinancialSettlementObservation(
        tenant_id=evidence.tenant_id,
        observation_id="observation-replay-2",
        provider_name=evidence.provider_name,
        execution_truth_id="execution-fact-1",
        provider_execution_reference=evidence.provider_execution_reference,
        settlement_reference=evidence.settlement_reference,
        provider_settlement_evidence_reference=evidence.provider_settlement_evidence_reference,
        status=SettlementObservationStatus.SETTLED,
        settled_amount_minor=evidence.settled_amount_minor,
        currency=evidence.currency,
        payment_destination_reference=evidence.payment_destination_reference,
        observed_at=evidence.observed_at,
        settled_at=evidence.settled_at,
        evidence_strength=evidence.evidence_strength,
        transport_disposition=evidence.transport_disposition,
    )
    divergent = FinancialSettlementObservation(
        **{**value.__dict__, "provider_settlement_evidence_reference": "different-proof"}
    )
    persisted = {**value.to_dict(), "observation_fingerprint": value.fingerprint}
    collection = Mock()
    collection.find_one.side_effect = [persisted]
    with pytest.raises(FinancialSettlementObservationConflictError):
        FinancialSettlementObservationRegistry.create(
            divergent, collection, session=Mock(in_transaction=True)
        )
    collection.insert_one.assert_not_called()


def test_outbox_delivery_state_is_mutable_without_rewriting_immutable_audit():
    from tools.eos.saas.billing.atomic_platform_settlement import _persist_audit_and_outbox

    session = Mock(in_transaction=True)
    settlement = _args(session)["_settlement"]
    audit = Mock()
    outbox = Mock()
    audit.find_one.return_value = None
    outbox.find_one.return_value = None
    first_audit, first_outbox = _persist_audit_and_outbox(
        tenant_id="tenant-a",
        settlement_evidence=settlement,
        audit_collection=audit,
        outbox_collection=outbox,
        session=session,
    )
    audit.find_one.return_value = first_audit
    outbox.find_one.return_value = {
        **first_outbox,
        "delivery_status": "DELIVERED",
        "delivery_attempts": 1,
        "delivered_at": "2026-01-01T00:00:00+00:00",
    }
    audit.insert_one.reset_mock()
    outbox.insert_one.reset_mock()
    replayed_audit, replayed_outbox = _persist_audit_and_outbox(
        tenant_id="tenant-a",
        settlement_evidence=settlement,
        audit_collection=audit,
        outbox_collection=outbox,
        session=session,
    )
    assert replayed_audit == first_audit
    assert replayed_outbox["delivery_status"] == "DELIVERED"
    audit.insert_one.assert_not_called()
    outbox.insert_one.assert_not_called()


class _UnknownCommitResult(Exception):
    def has_error_label(self, label: str) -> bool:
        return label == "UnknownTransactionCommitResult"


def test_unknown_commit_result_retries_commit_on_same_session_without_replaying_writes():
    from tools.eos.saas.billing.atomic_platform_settlement import (
        commit_atomic_settlement_transaction,
    )

    class Session:
        def __init__(self) -> None:
            self.calls = 0
        def commit_transaction(self) -> None:
            self.calls += 1
            if self.calls == 1:
                raise _UnknownCommitResult("acknowledgement lost")

    session = Session()
    readbacks: list[bool] = []
    result = commit_atomic_settlement_transaction(
        session,
        verify_committed=lambda: readbacks.append(True) or True,
    )
    assert result == "COMMITTED"
    assert session.calls == 2
    assert readbacks == []


def test_unknown_commit_result_exhaustion_uses_independent_positive_readback():
    from tools.eos.saas.billing.atomic_platform_settlement import (
        commit_atomic_settlement_transaction,
    )

    class Session:
        def __init__(self) -> None:
            self.calls = 0
        def commit_transaction(self) -> None:
            self.calls += 1
            raise _UnknownCommitResult("acknowledgement remains unknown")

    session = Session()
    result = commit_atomic_settlement_transaction(
        session,
        verify_committed=lambda: True,
        max_commit_attempts=2,
    )
    assert result == "COMMITTED_RECONCILED"
    assert session.calls == 2


def test_unknown_commit_result_never_treats_missing_readback_as_success():
    from tools.eos.saas.billing.atomic_platform_settlement import (
        AtomicPlatformSettlementCommitUncertainError,
        commit_atomic_settlement_transaction,
    )

    class Session:
        def commit_transaction(self) -> None:
            raise _UnknownCommitResult("acknowledgement remains unknown")

    with pytest.raises(AtomicPlatformSettlementCommitUncertainError):
        commit_atomic_settlement_transaction(
            Session(),
            verify_committed=lambda: False,
            max_commit_attempts=1,
        )
