"""Direct certificate for caller-owned execution reconciliation.

TITLE: Financial Execution Reconciliation Unit Certificate
VERSION: v1.0.0-M11-HOST-EXECUTION-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Prove durable authenticated EXECUTED evidence is the only path to
         lifecycle confirmation and post-terminalization runtime dispatch.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_reconciliation.py
COLLABORATION / OWNERSHIP: Kennel EOS reconciliation owner certificate.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0 certifies strict evidence correlation, lifecycle CAS,
           exact replay, conflict rejection, and transaction ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no providers or secrets.
TENANT BOUNDARY: Every fixture and assertion is tenant and attempt scoped.
AUTHORITY BOUNDARY: Reconciliation only; no settlement or provider transport.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS owns execution truth; EXECUTION != SETTLEMENT.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock, patch

import pytest

from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
)
from tools.eos.kennel.domain.financial_execution_execution_time_evidence import (
    ExecutionTimeAuthorityKind,
    FinancialExecutionTimeEvidence,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
)
from tools.eos.kennel.orchestration.financial_execution_reconciliation import (
    FinancialExecutionReconciliationError,
    reconcile_and_finalize_execution,
)

NOW = datetime(2026, 9, 12, 10, tzinfo=timezone.utc)


def _command() -> FinancialExecutionCommand:
    source = AccountsPayableCommandSource(
        execution_request_id="request-1",
        execution_request_fingerprint="a" * 128,
        selection_decision_id="selection-1",
        selection_decision_fingerprint="b" * 128,
        payable_id="payable-1",
        release_authorization_id="release-1",
        authorized_provider_name="PAYSHAP",
    )
    return FinancialExecutionCommand(
        tenant_id="tenant-1",
        execution_command_id="command-1",
        idempotency_key="key-1",
        amount_minor=1000,
        currency="ZAR",
        payment_destination_reference="destination-1",
        source_authority=source,
        provider_name="PAYSHAP",
        created_at=NOW,
    )


def _attempt(command: FinancialExecutionCommand, state: FinancialExecutionAttemptState) -> FinancialExecutionAttempt:
    return FinancialExecutionAttempt(
        execution_attempt_id="attempt-1",
        tenant_id="tenant-1",
        execution_command_id=command.execution_command_id,
        provider_name=command.provider_name,
        state=state,
        payment_destination_reference=command.payment_destination_reference,
        request_fingerprint=command.fingerprint,
        created_at=NOW,
        confirmed_at=NOW if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None,
        reconciliation_evidence_reference="evidence-1" if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None,
        latest_provider_evidence_reference="evidence-1" if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None,
    )


def _observation(**changes: object) -> FinancialExecutionProviderObservation:
    values: dict[str, object] = {
        "observation_id": "observation-1",
        "tenant_id": "tenant-1",
        "execution_attempt_id": "attempt-1",
        "provider_name": "PAYSHAP",
        "observation_status": ObservationStatus.EXECUTED,
        "observed_at": NOW,
        "provider_execution_reference": "execution-1",
        "provider_evidence_reference": "evidence-1",
        "evidence_strength": EvidenceStrength.AUTHENTICATED,
        "transport_disposition": TransportDisposition.RESPONSE_RECEIVED,
    }
    values.update(changes)
    return FinancialExecutionProviderObservation(**cast(Any, values))


def _time(**changes: object) -> FinancialExecutionTimeEvidence:
    values: dict[str, object] = {
        "tenant_id": "tenant-1",
        "execution_attempt_id": "attempt-1",
        "provider_name": "PAYSHAP",
        "provider_execution_reference": "execution-1",
        "evidence_reference": "evidence-1",
        "executed_at": NOW,
        "authority_kind": ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
        "evidence_strength": EvidenceStrength.AUTHENTICATED,
    }
    values.update(changes)
    return FinancialExecutionTimeEvidence(**cast(Any, values))


def _collections() -> dict[str, Mock]:
    return {
        "command_collection": Mock(),
        "attempt_collection": Mock(),
        "observation_collection": Mock(),
        "fact_collection": Mock(),
        "ap_truth_collection": Mock(),
        "platform_truth_collection": Mock(),
    }


def test_authenticated_executed_evidence_confirms_attempt_and_dispatches_runtime() -> None:
    command = _command()
    attempt = _attempt(command, FinancialExecutionAttemptState.PENDING)
    target = attempt.transition_to(
        FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
        evidence_reference="evidence-1",
        confirmed_at=NOW,
    )
    runtime_result = object()
    collections = _collections()
    session = SimpleNamespace(in_transaction=True)
    with (
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.get",
            return_value=attempt,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionCommandRegistry.get",
            return_value=command,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionProviderObservationRegistry.list_for_attempt",
            return_value=(_observation(),),
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.transition",
            return_value=target,
        ) as transition,
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.orchestrate_terminal_execution_fact_and_projection",
            return_value=runtime_result,
        ) as runtime,
    ):
        result = reconcile_and_finalize_execution(
            "tenant-1",
            "attempt-1",
            **collections,
            execution_time_evidence=_time(),
            session=cast(Any, session),
        )
    assert result is runtime_result
    transition.assert_called_once()
    runtime.assert_called_once()
    assert transition.call_args.kwargs["session"] is session
    assert runtime.call_args.kwargs["session"] is session


def test_exact_replay_does_not_transition_again_but_dispatches_runtime() -> None:
    command = _command()
    attempt = _attempt(command, FinancialExecutionAttemptState.CONFIRMED_EXECUTED)
    collections = _collections()
    session = SimpleNamespace(in_transaction=True)
    with (
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.get",
            return_value=attempt,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionCommandRegistry.get",
            return_value=command,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionProviderObservationRegistry.list_for_attempt",
            return_value=(_observation(),),
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.transition"
        ) as transition,
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.orchestrate_terminal_execution_fact_and_projection",
            return_value=object(),
        ),
    ):
        reconcile_and_finalize_execution(
            "tenant-1",
            "attempt-1",
            **collections,
            execution_time_evidence=_time(),
            session=cast(Any, session),
        )
    transition.assert_not_called()


@pytest.mark.parametrize(
    "changes, time_changes, expected",
    [
        ({"provider_occurred_at": NOW}, {"evidence_reference": "wrong"}, "EXECUTION_TIME_EVIDENCE_CORRELATION_MISMATCH"),
        ({"evidence_strength": EvidenceStrength.UNAUTHENTICATED}, {}, "EXECUTED_EVIDENCE_INSUFFICIENT"),
        ({"transport_disposition": TransportDisposition.AMBIGUOUS}, {}, "EXECUTED_EVIDENCE_INSUFFICIENT"),
        ({"tenant_id": "tenant-2"}, {}, "OBSERVATION_IDENTITY_MISMATCH"),
        ({"execution_attempt_id": "attempt-2"}, {}, "OBSERVATION_IDENTITY_MISMATCH"),
        ({"provider_execution_reference": "other"}, {}, "EXECUTION_TIME_EVIDENCE_CORRELATION_MISMATCH"),
    ],
)
def test_invalid_or_divergent_evidence_fails_closed(
    changes: dict[str, object], time_changes: dict[str, object], expected: str
) -> None:
    command = _command()
    attempt = _attempt(command, FinancialExecutionAttemptState.PENDING)
    collections = _collections()
    session = SimpleNamespace(in_transaction=True)
    items = (_observation(**changes),)
    with (
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.get",
            return_value=attempt,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionCommandRegistry.get",
            return_value=command,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionProviderObservationRegistry.list_for_attempt",
            return_value=items,
        ),
        pytest.raises(FinancialExecutionReconciliationError, match=expected),
    ):
        reconcile_and_finalize_execution(
            "tenant-1",
            "attempt-1",
            **collections,
            execution_time_evidence=_time(**time_changes),
            session=cast(Any, session),
        )


@pytest.mark.parametrize("status", [ObservationStatus.FAILED, ObservationStatus.CANCELLED])
def test_conflicting_terminal_observation_fails_closed(status: ObservationStatus) -> None:
    command = _command()
    attempt = _attempt(command, FinancialExecutionAttemptState.PENDING)
    conflicting = _observation(
        observation_id="observation-2", observation_status=status, provider_evidence_reference="evidence-2"
    )
    collections = _collections()
    session = SimpleNamespace(in_transaction=True)
    with (
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.get",
            return_value=attempt,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionCommandRegistry.get",
            return_value=command,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionProviderObservationRegistry.list_for_attempt",
            return_value=(_observation(), conflicting),
        ),
        pytest.raises(FinancialExecutionReconciliationError, match="CONFLICTING_TERMINAL_EVIDENCE"),
    ):
        reconcile_and_finalize_execution(
            "tenant-1",
            "attempt-1",
            **collections,
            execution_time_evidence=_time(),
            session=cast(Any, session),
        )


def test_missing_explicit_time_evidence_fails_closed() -> None:
    command = _command()
    attempt = _attempt(command, FinancialExecutionAttemptState.PENDING)
    collections = _collections()
    session = SimpleNamespace(in_transaction=True)
    with (
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.get",
            return_value=attempt,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionCommandRegistry.get",
            return_value=command,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionProviderObservationRegistry.list_for_attempt",
            return_value=(_observation(provider_occurred_at=NOW),),
        ),
        pytest.raises(FinancialExecutionReconciliationError, match="EXECUTION_TIME_EVIDENCE_REQUIRED"),
    ):
        reconcile_and_finalize_execution(
            "tenant-1",
            "attempt-1",
            **collections,
            execution_time_evidence=cast(Any, None),
            session=cast(Any, session),
        )


def test_inactive_transaction_fails_before_reads() -> None:
    with pytest.raises(FinancialExecutionReconciliationError, match="ACTIVE_TRANSACTION_REQUIRED"):
        reconcile_and_finalize_execution(
            "tenant-1",
            "attempt-1",
            **_collections(),
            execution_time_evidence=_time(),
            session=cast(Any, SimpleNamespace(in_transaction=False)),
        )


def test_runtime_failure_propagates_for_caller_abort() -> None:
    command = _command()
    attempt = _attempt(command, FinancialExecutionAttemptState.PENDING)
    target = attempt.transition_to(
        FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
        evidence_reference="evidence-1",
        confirmed_at=NOW,
    )
    session = SimpleNamespace(in_transaction=True)
    with (
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.get",
            return_value=attempt,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionCommandRegistry.get",
            return_value=command,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionProviderObservationRegistry.list_for_attempt",
            return_value=(_observation(),),
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.FinancialExecutionAttemptRegistry.transition",
            return_value=target,
        ),
        patch(
            "tools.eos.kennel.orchestration.financial_execution_reconciliation.orchestrate_terminal_execution_fact_and_projection",
            side_effect=RuntimeError("downstream failure"),
        ),
        pytest.raises(RuntimeError, match="downstream failure"),
    ):
        reconcile_and_finalize_execution(
            "tenant-1",
            "attempt-1",
            **_collections(),
            execution_time_evidence=_time(),
            session=cast(Any, session),
        )


# ARTIFACT: test_financial_execution_reconciliation.py
# VERSION: v1.0.0-M11-HOST-EXECUTION-RECONCILIATION
# AUTHORITY BOUNDARY: direct reconciliation certificate only; no settlement authority.
# TENANT POSTURE: exact tenant/attempt/provider evidence correlation.
# FAIL-CLOSED POSTURE: weak, conflicting, stale, and divergent evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
