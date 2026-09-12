"""Host-backed certificate for execution reconciliation and finalization."""
from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Barrier
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
)
from tools.eos.kennel.domain.financial_execution_execution_time_evidence import (
    ExecutionTimeAuthorityKind,
    FinancialExecutionTimeEvidence,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
)
from tools.eos.kennel.orchestration.financial_execution_attempt_issuance import (
    FinancialExecutionAttemptIssuance,
    issue_financial_execution_attempt,
)
from tools.eos.kennel.orchestration.financial_execution_reconciliation import (
    reconcile_and_finalize_execution,
)
from tools.eos.kennel.registry.financial_execution_attempt_registry import (
    FinancialExecutionAttemptRegistry,
    FinancialExecutionAttemptTransitionConflictError,
)
from tools.eos.kennel.registry.financial_execution_command_registry import (
    FinancialExecutionCommandRegistry,
)
from tools.eos.kennel.registry.financial_execution_provider_observation_registry import (
    FinancialExecutionProviderObservationRegistry,
)
from tools.eos.kennel.registry.financial_execution_registry import (
    FACT_COLLECTION,
    FinancialExecutionFactRegistry,
    FinancialExecutionTruthRegistry,
)

URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
NOW = datetime(2026, 9, 12, 10, tzinfo=timezone.utc)


@pytest.fixture()
def runtime() -> Any:
    configured = os.environ.get("TEST_VENDOR_MONGO_URI")
    assert configured == URI, "TEST_VENDOR_MONGO_URI must select the certified replica set"
    client = MongoClient(configured, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database = client[f"fer_{uuid4().hex}"]
    command_collection = database["kennel_financial_execution_commands"]
    attempt_collection = database["kennel_financial_execution_attempts"]
    observation_collection = database["kennel_financial_execution_provider_observations"]
    fact_collection = database[FACT_COLLECTION]
    ap_truth_collection = database["kennel_financial_execution_truth"]
    platform_truth_collection = database["kennel_platform_billing_financial_execution_truth"]
    FinancialExecutionCommandRegistry.ensure_indexes(command_collection)
    FinancialExecutionAttemptRegistry.ensure_indexes(attempt_collection)
    FinancialExecutionProviderObservationRegistry.ensure_indexes(observation_collection)
    FinancialExecutionFactRegistry.ensure_indexes(fact_collection)
    FinancialExecutionTruthRegistry.ensure_indexes(ap_truth_collection)
    try:
        yield {
            "client": client,
            "database": database,
            "command_collection": command_collection,
            "attempt_collection": attempt_collection,
            "observation_collection": observation_collection,
            "fact_collection": fact_collection,
            "ap_truth_collection": ap_truth_collection,
            "platform_truth_collection": platform_truth_collection,
        }
    finally:
        client.drop_database(database.name)
        client.close()


def _command(suffix: str) -> FinancialExecutionCommand:
    source = AccountsPayableCommandSource(
        execution_request_id=f"request-{suffix}",
        execution_request_fingerprint="a" * 128,
        selection_decision_id=f"selection-{suffix}",
        selection_decision_fingerprint="b" * 128,
        payable_id=f"payable-{suffix}",
        release_authorization_id=f"release-{suffix}",
        authorized_provider_name="PAYSHAP",
    )
    return FinancialExecutionCommand(
        tenant_id="tenant-reconciliation",
        execution_command_id=f"command-{suffix}",
        idempotency_key=f"key-{suffix}",
        amount_minor=1000,
        currency="ZAR",
        payment_destination_reference=f"destination-{suffix}",
        source_authority=source,
        provider_name="PAYSHAP",
        created_at=NOW,
    )


def _seed(data: dict[str, Any], suffix: str) -> tuple[str, FinancialExecutionTimeEvidence]:
    command = _command(suffix)
    attempt_id = f"attempt-{suffix}"
    client = data["client"]
    with client.start_session() as session:
        session.start_transaction()
        FinancialExecutionCommandRegistry.create(command, data["command_collection"], session=session)
        attempt = issue_financial_execution_attempt(
            command,
            FinancialExecutionAttemptIssuance(
                execution_attempt_id=attempt_id,
                provider_name="PAYSHAP",
                created_at=NOW,
                request_evidence_reference=f"request-evidence-{suffix}",
            ),
            command_collection=data["command_collection"],
            session=session,
        )
        FinancialExecutionAttemptRegistry.create(attempt, data["attempt_collection"], session=session)
        current = FinancialExecutionAttemptRegistry.get("tenant-reconciliation", attempt_id, data["attempt_collection"], session=session)
        for target_state in (FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.ACCEPTED):
            target = current.transition_to(target_state)
            current = FinancialExecutionAttemptRegistry.transition(
                "tenant-reconciliation", attempt_id, current.state, current.fingerprint,
                target, data["attempt_collection"], session=session,
            )
        session.commit_transaction()
    execution_time = FinancialExecutionTimeEvidence(
        tenant_id="tenant-reconciliation",
        execution_attempt_id=attempt_id,
        provider_name="PAYSHAP",
        provider_execution_reference=f"execution-{suffix}",
        evidence_reference=f"evidence-{suffix}",
        executed_at=NOW,
        authority_kind=ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
    )
    observation = FinancialExecutionProviderObservation(
        observation_id=f"observation-{suffix}",
        tenant_id="tenant-reconciliation",
        execution_attempt_id=attempt_id,
        provider_name="PAYSHAP",
        observation_status=ObservationStatus.EXECUTED,
        observed_at=NOW,
        provider_execution_reference=execution_time.provider_execution_reference,
        provider_evidence_reference=execution_time.evidence_reference,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
    )
    with client.start_session() as session:
        session.start_transaction()
        FinancialExecutionProviderObservationRegistry.create(
            observation, data["observation_collection"], session=session
        )
        session.commit_transaction()
    return attempt_id, execution_time


def _reconcile(data: dict[str, Any], attempt_id: str, execution_time: FinancialExecutionTimeEvidence) -> Any:
    with data["client"].start_session() as session:
        session.start_transaction()
        result = reconcile_and_finalize_execution(
            "tenant-reconciliation", attempt_id,
            command_collection=data["command_collection"],
            attempt_collection=data["attempt_collection"],
            observation_collection=data["observation_collection"],
            fact_collection=data["fact_collection"],
            ap_truth_collection=data["ap_truth_collection"],
            platform_truth_collection=data["platform_truth_collection"],
            execution_time_evidence=execution_time,
            session=session,
        )
        session.commit_transaction()
        return result


def test_reconciliation_confirms_attempt_persists_fact_and_exact_replay(runtime: dict[str, Any]) -> None:
    attempt_id, execution_time = _seed(runtime, "commit")
    first = _reconcile(runtime, attempt_id, execution_time)
    assert first.tenant_id == "tenant-reconciliation"
    assert runtime["attempt_collection"].find_one({"execution_attempt_id": attempt_id})["state"] == "CONFIRMED_EXECUTED"
    assert runtime["fact_collection"].count_documents({}) == 1
    assert runtime["ap_truth_collection"].count_documents({}) == 1
    _reconcile(runtime, attempt_id, execution_time)
    assert runtime["fact_collection"].count_documents({}) == 1
    assert runtime["ap_truth_collection"].count_documents({}) == 1


def test_caller_abort_rolls_back_reconciliation_and_downstream_truth(runtime: dict[str, Any]) -> None:
    attempt_id, execution_time = _seed(runtime, "abort")
    with runtime["client"].start_session() as session:
        session.start_transaction()
        reconcile_and_finalize_execution(
            "tenant-reconciliation", attempt_id,
            command_collection=runtime["command_collection"],
            attempt_collection=runtime["attempt_collection"],
            observation_collection=runtime["observation_collection"],
            fact_collection=runtime["fact_collection"],
            ap_truth_collection=runtime["ap_truth_collection"],
            platform_truth_collection=runtime["platform_truth_collection"],
            execution_time_evidence=execution_time,
            session=session,
        )
        session.abort_transaction()
    row = runtime["attempt_collection"].find_one({"execution_attempt_id": attempt_id})
    assert row is not None and row["state"] == "ACCEPTED"
    assert runtime["fact_collection"].count_documents({}) == 0
    assert runtime["ap_truth_collection"].count_documents({}) == 0


def test_concurrent_reconciliation_cas_has_one_durable_terminal_result(runtime: dict[str, Any]) -> None:
    attempt_id, execution_time = _seed(runtime, "race")
    barrier = Barrier(2)

    def worker() -> str:
        with runtime["client"].start_session() as session:
            barrier.wait(timeout=10)
            session.start_transaction()
            try:
                reconcile_and_finalize_execution(
                    "tenant-reconciliation", attempt_id,
                    command_collection=runtime["command_collection"],
                    attempt_collection=runtime["attempt_collection"],
                    observation_collection=runtime["observation_collection"],
                    fact_collection=runtime["fact_collection"],
                    ap_truth_collection=runtime["ap_truth_collection"],
                    platform_truth_collection=runtime["platform_truth_collection"],
                    execution_time_evidence=execution_time,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"
            except (PyMongoError, FinancialExecutionAttemptTransitionConflictError):
                if session.in_transaction:
                    session.abort_transaction()
                return "REJECTED_OR_RETRIABLE"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(pool.map(lambda _: worker(), range(2)))
    assert all(outcome in {"COMMITTED", "REJECTED_OR_RETRIABLE"} for outcome in outcomes)
    assert runtime["attempt_collection"].find_one({"execution_attempt_id": attempt_id})["state"] == "CONFIRMED_EXECUTED"
    assert runtime["fact_collection"].count_documents({}) == 1
    assert runtime["ap_truth_collection"].count_documents({}) == 1


# ARTIFACT: test_financial_execution_reconciliation_mongo.py
# VERSION: v1.0.0-M11-HOST-EXECUTION-RECONCILIATION
# AUTHORITY BOUNDARY: host certificate for evidence reconciliation only; no settlement.
# TENANT POSTURE: isolated UUID database and exact tenant-scoped registries.
# FAIL-CLOSED POSTURE: replica-set and transaction preconditions are asserted.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
