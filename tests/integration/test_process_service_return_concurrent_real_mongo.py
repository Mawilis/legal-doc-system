"""Deterministic P5F duplicate-writer certificate against real MongoDB.

TITLE: Wilsy OS Process-Service Return Concurrent Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-RETURN-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: One real duplicate-writer race for canonical ReturnOfService evidence.
TENANT BOUNDARY: UUID-isolated database and exact tenant predicates.
AUTHORITY BOUNDARY: P1/P2 remain lifecycle and durable-evidence authorities;
                     P5F composes return evidence only.
TRANSACTION BOUNDARY: Workers own independent sessions and transactions; P5F/P2
                      never start, commit, abort, or retain a Mongo client.
FINANCIAL BOUNDARY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Only hello/replica availability may skip; all product, race,
             persistence, replay, provenance, or durability failures fail.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-RETURN-CONCURRENT-REAL-MONGO-CERT
           certifies one real duplicate-writer race, rollback, replay, and
           source-execution preservation.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
import threading
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
    ServiceExecutionOutcome,
)
from tools.eos.legal_operations.orchestration.process_service_return_orchestrator import (
    generate_process_service_return,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
)
from tools.eos.legal_operations.registry.process_service_return_registry import (
    ProcessServiceReturnRegistry,
    ProcessServiceReturnRegistryError,
)

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 15, 0, tzinfo=timezone.utc)
TERMINAL_FINGERPRINT = "a" * 128


class BarrierCollection:
    """Synchronize the real insert boundary while delegating every operation."""

    def __init__(self, collection: Any, barrier: threading.Barrier) -> None:
        self._collection = collection
        self._barrier = barrier

    def find_one(self, query: dict[str, Any], *, session: object = None) -> Any:
        return self._collection.find_one(query, session=session)

    def insert_one(self, row: dict[str, Any], *, session: object = None) -> Any:
        self._barrier.wait(timeout=30)
        return self._collection.insert_one(row, session=session)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield majority/journaled real collections and safely clean the database."""
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
        database = client[f"p5f_conc_{uuid.uuid4().hex}"]
        concerns = {"write_concern": WriteConcern(w="majority", j=True), "read_concern": ReadConcern("majority")}
        lifecycle = database.get_collection("legal_lifecycle", **concerns)
        returns = database.get_collection("service_returns", **concerns)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        ProcessServiceReturnRegistry.ensure_indexes(returns)
        yield client, lifecycle, returns
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _tx(client: MongoClient) -> Any:
    """Start one caller-owned transaction; production code never owns it."""
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    return session


def _terminal_attempt(tenant: str) -> tuple[ServiceAttempt, ServiceAttempt, ServiceAttempt]:
    """Build a complete immutable ALLOCATED -> ATTEMPTED -> COMPLETED chain."""
    allocated = ServiceAttempt(
        tenant_id=tenant,
        attempt_id="attempt-race",
        instruction_id="instruction-race",
        document_id="document-race",
        deputy_id="deputy-race",
        allocated_at=BASE,
        allocation_evidence_reference="allocation:race",
    )
    attempted = allocated.transition_to(ServiceAttemptState.ATTEMPTED, evidence_reference="attempt:race", occurred_at=BASE + timedelta(minutes=1))
    completed = attempted.transition_to(ServiceAttemptState.COMPLETED, evidence_reference="terminal:race", evidence_fingerprint=TERMINAL_FINGERPRINT, occurred_at=BASE + timedelta(minutes=2))
    return allocated, attempted, completed


def _seed_execution(client: MongoClient, lifecycle: Any, tenant: str) -> tuple[ServiceAttempt, ServiceExecution, str]:
    """Persist source snapshots and one factory-derived ServiceExecution."""
    allocated, attempted, terminal = _terminal_attempt(tenant)
    session = _tx(client)
    try:
        for snapshot in (allocated, attempted, terminal):
            LegalOperationsLifecycleRegistry.create(snapshot, lifecycle, session=session)
        execution = ServiceExecution.from_attempt(attempt=terminal, service_execution_id="execution-race", executed_at=BASE + timedelta(minutes=3))
        LegalOperationsLifecycleRegistry.create(execution, lifecycle, session=session, source_attempt=terminal)
        session.commit_transaction()
    finally:
        session.end_session()
    row = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ServiceExecution", "entity_identity": execution.service_execution_id})
    assert row is not None
    return terminal, execution, row["evidence_identity"]


def _worker(client: MongoClient, lifecycle: Any, return_collection: Any, tenant: str, execution_identity: str, barrier_collection: BarrierCollection, results: list[dict[str, Any]], lock: threading.Lock) -> None:
    """Run one caller-owned transaction and capture the actual losing cause."""
    session = _tx(client)
    outcome: dict[str, Any] = {}
    try:
        value = generate_process_service_return(tenant_id=tenant, execution_evidence_identity=execution_identity, lifecycle_collection=lifecycle, return_collection=barrier_collection, return_id="return-race", generated_at=BASE + timedelta(minutes=4), session=session)
        session.commit_transaction()
        outcome.update(status="COMMITTED", value=value)
    except Exception as error:
        try:
            session.abort_transaction()
        finally:
            outcome.update(status="REJECTED", error=error)
    finally:
        session.end_session()
        with lock:
            results.append(outcome)


def test_real_mongo_return_duplicate_writer_has_one_winner_and_one_retry_loser(mongo_context: tuple[MongoClient, Any, Any]) -> None:
    """Prove real duplicate-writer classification and durable post-race truth."""
    client, lifecycle, returns = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    terminal, execution, execution_identity = _seed_execution(client, lifecycle, tenant)
    source_before = execution.to_dict()
    barrier = threading.Barrier(2)
    synchronized_returns = BarrierCollection(returns, barrier)
    results: list[dict[str, Any]] = []
    lock = threading.Lock()
    workers = [threading.Thread(target=_worker, args=(client, lifecycle, returns, tenant, execution_identity, synchronized_returns, results, lock)) for _ in range(2)]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join(timeout=60)
        assert not worker.is_alive()
    assert len(results) == 2
    committed = [item for item in results if item["status"] == "COMMITTED"]
    rejected = [item for item in results if item["status"] == "REJECTED"]
    assert len(committed) == 1
    assert len(rejected) == 1
    loser = rejected[0]["error"]
    assert isinstance(loser, ProcessServiceReturnRegistryError)
    assert loser.code == "P5F_RETRY_TRANSACTION_REQUIRED"
    cause = loser.__cause__
    assert isinstance(cause, PyMongoError)
    labels = tuple(sorted(label for label in ("TransientTransactionError", "UnknownTransactionCommitResult") if cause.has_error_label(label)))
    assert "UnknownTransactionCommitResult" not in labels
    assert "TransientTransactionError" in labels or cause.__class__.__name__ == "DuplicateKeyError"
    assert getattr(cause, "code", None) is None or isinstance(getattr(cause, "code", None), int)

    assert returns.count_documents({"tenant_id": tenant}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ReturnOfService"}) == 1
    assert lifecycle.count_documents({"tenant_id": tenant, "entity_type": "ServiceExecution"}) == 1
    durable_return = lifecycle.find_one({"tenant_id": tenant, "entity_type": "ReturnOfService"})
    assert durable_return is not None
    source_envelope = durable_return["source_payload"]
    assert source_envelope["service_execution"]["executed_at"] == execution.executed_at.isoformat()
    assert source_envelope["attempt"]["attempt_id"] == terminal.attempt_id
    assert source_envelope["service_execution"]["service_execution_id"] == execution.service_execution_id
    assert execution.to_dict() == source_before

    replay_session = _tx(client)
    try:
        replay = generate_process_service_return(tenant_id=tenant, execution_evidence_identity=execution_identity, lifecycle_collection=lifecycle, return_collection=returns, return_id="return-race", generated_at=BASE + timedelta(minutes=4), session=replay_session)
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()
    assert replay.to_dict() == committed[0]["value"].to_dict()
    assert returns.count_documents({"tenant_id": tenant}) == 1
    divergent = _tx(client)
    try:
        with pytest.raises(ProcessServiceReturnRegistryError, match="P5F_REPLAY_CONFLICT"):
            generate_process_service_return(tenant_id=tenant, execution_evidence_identity=execution_identity, lifecycle_collection=lifecycle, return_collection=returns, return_id="return-race", generated_at=BASE + timedelta(minutes=5), session=divergent)
    finally:
        divergent.abort_transaction()
        divergent.end_session()
    assert returns.count_documents({"tenant_id": tenant}) == 1
    assert execution.to_dict() == source_before

    assert not hasattr(ProcessServiceReturnRegistry, "start_transaction")
    assert not hasattr(ProcessServiceReturnRegistry, "commit_transaction")
    assert not hasattr(ProcessServiceReturnRegistry, "abort_transaction")
    assert not hasattr(LegalOperationsLifecycleRegistry, "start_transaction")
    assert not hasattr(LegalOperationsLifecycleRegistry, "commit_transaction")
    assert not hasattr(LegalOperationsLifecycleRegistry, "abort_transaction")
    for module_name in (
        "tools.eos.legal_operations.domain.process_service_return_authority",
        "tools.eos.legal_operations.registry.process_service_return_registry",
        "tools.eos.legal_operations.orchestration.process_service_return_orchestrator",
    ):
        module = __import__(module_name, fromlist=["*"])
        assert not hasattr(module, "invoice")
        assert not hasattr(module, "payment")
        assert not hasattr(module, "settlement")


# ARTIFACT: test_process_service_return_concurrent_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-RETURN-CONCURRENT-REAL-MONGO-CERT
# CERTIFICATION SCOPE: one deterministic real duplicate-writer race.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN TEST ARTIFACT
