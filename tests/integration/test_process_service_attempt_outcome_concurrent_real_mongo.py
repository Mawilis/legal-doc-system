"""Deterministic concurrent real-Mongo certificate for P5E outcome authority.

TITLE: Wilsy OS Process-Service Attempt Outcome Concurrent Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove two caller-owned transactions racing for one immutable terminal
         outcome yield exactly one durable winner and one governed retry loser.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_attempt_outcome_concurrent_real_mongo.py
TENANT BOUNDARY: UUID-isolated tenant/database; foreign evidence is never disclosed.
AUTHORITY BOUNDARY: P5E outcome evidence plus P1-derived ServiceExecution only;
                     no ReturnOfService, invoice, payment, or settlement truth.
TRANSACTION BOUNDARY: Workers own independent sessions, transactions, aborts,
                      commits, and cleanup. Production code owns none of these.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Ambiguous outcomes, duplicate durable facts, unknown
                         conflicts, and unclassified errors fail certification.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-CONCURRENT-REAL-MONGO-CERT
           establishes deterministic two-worker uniqueness and rollback evidence.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from threading import Barrier, Thread
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt, ServiceAttemptState, ServiceExecutionOutcome
from tools.eos.legal_operations.orchestration.process_service_attempt_outcome_orchestrator import transition_process_service_attempt_outcome
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.registry.process_service_attempt_outcome_registry import ProcessServiceAttemptOutcomeRegistry

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 14, 0, tzinfo=timezone.utc)
EVIDENCE_HASH = "e" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield isolated majority/journaled collections and clean them safely."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"MONGO_RUNTIME_UNAVAILABLE: {type(error).__name__}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"MONGO_REPLICA_SET_UNAVAILABLE: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        database = client[f"p5e_outcome_cas_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("legal_lifecycle", **concerns)
        outcomes = database.get_collection("attempt_outcomes", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceAttemptOutcomeRegistry.ensure_indexes(outcomes)
        yield client, lifecycle, outcomes
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def _tx(client: MongoClient) -> Any:
    """Start one worker-owned transaction."""
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    return session


def _seed(client: MongoClient, lifecycle: Any, tenant: str) -> str:
    """Persist the canonical ALLOCATED and ATTEMPTED source snapshots."""
    allocated = ServiceAttempt(tenant_id=tenant, attempt_id="attempt-cas", instruction_id="instruction-cas", document_id="document-cas", deputy_id="deputy-cas", allocated_at=BASE, allocation_evidence_reference="p5b:allocation-cas")
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="field:attempt-cas", occurred_at=BASE + timedelta(minutes=1))
    session = _tx(client)
    try:
        LegalOperationsLifecycleRegistry.create(allocated, lifecycle, session=session)
        LegalOperationsLifecycleRegistry.create(attempted, lifecycle, session=session)
        session.commit_transaction()
    finally:
        session.end_session()
    row = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ServiceAttempt", "entity_identity": attempted.attempt_id, "p1_fingerprint": attempted.fingerprint})
    assert row is not None
    return row["evidence_identity"]


def test_real_mongo_two_workers_one_terminal_outcome_winner_and_retry_loser(mongo_context: tuple[MongoClient, Any, Any]) -> None:
    """Race two real transactions and prove one winner, one governed loser, and exact replay."""
    client, lifecycle, outcomes = mongo_context
    tenant = f"tenant-cas-{uuid.uuid4().hex}"
    source_identity = _seed(client, lifecycle, tenant)
    barrier = Barrier(2)
    results: list[ServiceExecutionOutcome] = []
    errors: list[BaseException] = []

    def worker() -> None:
        session = _tx(client)
        try:
            barrier.wait(timeout=15)
            result = transition_process_service_attempt_outcome(tenant_id=tenant, current_evidence_identity=source_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.COMPLETED, evidence_reference="field:cas-completed", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-cas", executed_at=BASE + timedelta(minutes=3), session=session)
            session.commit_transaction()
            results.append(result.outcome)
        except BaseException as error:
            errors.append(error)
            try:
                if session.in_transaction:
                    session.abort_transaction()
            except PyMongoError:
                pass
        finally:
            session.end_session()

    threads = [Thread(target=worker), Thread(target=worker)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert not any(thread.is_alive() for thread in threads)
    assert len(results) == 1
    assert results == [ServiceExecutionOutcome.COMPLETED]
    assert len(errors) == 1
    loser = errors[0]
    governed_code = getattr(loser, "code", None)
    assert governed_code == "P5E_RETRY_TRANSACTION_REQUIRED"
    cause: BaseException | None = loser
    while cause is not None and not isinstance(cause, PyMongoError):
        cause = cause.__cause__ or cause.__context__
    assert isinstance(cause, PyMongoError)
    labels = sorted(getattr(cause, "_error_labels", ()))
    print(
        "LOSER_DIAGNOSTIC "
        f"exception_type={type(loser).__name__} governed_code={governed_code} "
        f"raw_cause_type={type(cause).__name__} raw_mongo_code={getattr(cause, 'code', None)!r} "
        f"mongo_labels={labels}"
    )
    assert not cause.has_error_label("UnknownTransactionCommitResult")

    assert outcomes.count_documents({"tenant_id": tenant}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ServiceAttempt", "p1_payload.state": "COMPLETED"}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ServiceExecution"}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ReturnOfService"}) == 0
    terminal = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ServiceAttempt", "p1_payload.state": "COMPLETED"})
    execution = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ServiceExecution"})
    assert terminal is not None and execution is not None
    terminal_payload = terminal["p1_payload"]
    transition_history = terminal_payload["transition_history"]
    assert isinstance(transition_history, list) and transition_history
    terminal_event = transition_history[-1]
    assert terminal_event["resulting_state"] == terminal_payload["state"] == "COMPLETED"
    assert terminal_event["evidence_reference"] == "field:cas-completed"
    assert terminal_event["evidence_fingerprint"] == EVIDENCE_HASH
    assert execution["p1_payload"]["outcome"] == ServiceExecutionOutcome.COMPLETED.value
    assert execution["source_payload"]["attempt"]["attempt_id"] == "attempt-cas"

    replay_session = _tx(client)
    try:
        replay = transition_process_service_attempt_outcome(tenant_id=tenant, current_evidence_identity=source_identity, lifecycle_collection=lifecycle, outcome_collection=outcomes, outcome=ServiceAttemptState.COMPLETED, evidence_reference="field:cas-completed", evidence_fingerprint=EVIDENCE_HASH, occurred_at=BASE + timedelta(minutes=2), service_execution_id="execution-cas", executed_at=BASE + timedelta(minutes=3), session=replay_session)
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()
    assert replay.outcome is ServiceExecutionOutcome.COMPLETED
    assert outcomes.count_documents({"tenant_id": tenant}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ServiceExecution"}) == 1


# ARTIFACT: test_process_service_attempt_outcome_concurrent_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-OUTCOME-CONCURRENT-REAL-MONGO-CERT
# CERTIFICATION SCOPE: real concurrent terminal-outcome uniqueness and rollback.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
