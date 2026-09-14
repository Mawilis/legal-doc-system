"""Host-backed deterministic P5C composition-race certificate.

TITLE: Wilsy OS Process-Service Attempt Orchestrator Concurrent Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify one genuine two-transaction race in which identical durable
         P5B authority is composed by P5C into one initial P1 ALLOCATED
         snapshot and persisted through the P2 immutable evidence registry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_attempt_orchestrator_concurrent_real_mongo.py
COLLABORATION / OWNERSHIP: P5B remains the durable attempt-authority source;
                            P5C owns composition only; P1 owns lifecycle
                            semantics; P2 owns immutable persistence and race
                            classification; this certificate caller owns every
                            Mongo session, transaction, abort, commit, retry,
                            and isolated-database cleanup operation.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CONCURRENT-REAL-MONGO-CERT
           establishes deterministic host-backed P5C composition-race evidence
           with one committed winner and one whole-transaction retry loser.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic identifiers only; no
                             provider, credential, customer, or personal-data
                             expansion.
TENANT BOUNDARY: Both workers use one explicit synthetic tenant and the same
                 P5B authority locator. P5B and P2 retain exact tenant scope;
                 no cross-tenant lookup or disclosure is possible.
AUTHORITY BOUNDARY: P5C composition is certified only from P5B receipt to the
                    initial P1 ALLOCATED attempt. No P4/P5A reread occurs in
                    worker execution; no transition, service, return, custody,
                    current-pointer, IAM, or transport authority is created.
TRANSACTION BOUNDARY: Two independent caller-owned sessions and transactions
                      are synchronized at the real P2 absent read. P5C never
                      starts, commits, aborts, ends, retries, or stores a client.
FINANCIAL AUTHORITY BOUNDARY: No billing, invoice, payment, execution, or
                              settlement authority exists here. Kennel EOS
                              exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Ambiguous commit, an unclassified loser, a missing
                         barrier arrival, extra durable evidence, provenance
                         loss, or any persistence defect fails the certificate.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
import sys
import threading
from typing import Any, Iterator, cast
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.legal_operations.orchestration.process_service_attempt_orchestrator as p5c
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttemptState
from tools.eos.legal_operations.domain.process_service_attempt_authority import (
    authorize_process_service_attempt,
)
from tools.eos.legal_operations.registry import legal_operations_lifecycle_registry as p2
from tools.eos.legal_operations.registry import process_service_attempt_authority_registry as p5b
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)


VERSION = "v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CONCURRENT-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any]]:
    """Yield one verified writable replica-set database and clean it finally."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            client.close()
            pytest.fail(f"host Mongo unavailable during hello: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            client.close()
            pytest.fail(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            client.close()
            pytest.fail("replica set has no writable primary")
        database = client[f"p5c_attempt_race_{uuid.uuid4().hex}"]
        concerns = {
            "write_concern": WriteConcern(w="majority", j=True),
            "read_concern": ReadConcern("majority"),
        }
        authority = database.get_collection(p5b.RECEIPT_COLLECTION, **concerns)
        lifecycle = database.get_collection(p2.COLLECTION, **concerns)
        p5b.ProcessServiceAttemptAuthorityRegistry.ensure_indexes(authority)
        p2.LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield client, database, authority, lifecycle
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


def _allocation_receipt(tenant_id: str, authority_id: str, attempt_id: str) -> ProcessServiceAllocationReceipt:
    """Build valid synthetic P4 allocation evidence for setup only."""
    return ProcessServiceAllocationReceipt(
        tenant_id=tenant_id,
        allocation_command_id=f"allocation-command-{authority_id}",
        idempotency_key=f"allocation-idempotency-{authority_id}",
        instruction_id="instruction-p5c-race",
        case_matter_id="matter-p5c-race",
        document_id=f"document-{attempt_id}",
        district_id="district-p5c-race",
        sheriff_office_id="office-p5c-race",
        deputy_id="deputy-p5c-race",
        assignment_decision_id="assignment-p5c-race",
        assignment_decision_fingerprint=HEX_A,
        source_instruction_fingerprint=HEX_B,
        source_document_fingerprint=HEX_C,
        source_district_fingerprint=HEX_D,
        source_sheriff_office_fingerprint=HEX_E,
        source_deputy_fingerprint=HEX_F,
        prior_custody_chain_fingerprint=HEX_A,
        prior_custody_head_event_id=f"custody-head-{authority_id}",
        prior_custody_head_fingerprint=HEX_B,
        prior_custody_head_sequence_number=7,
        from_holder_reference="office-p5c-race",
        to_holder_reference="deputy-p5c-race",
        allocation_custody_event_id=f"custody-allocation-{authority_id}",
        allocation_evidence_reference=f"allocation-evidence-{authority_id}",
        allocated_at=BASE,
        allocated_document_fingerprint=HEX_C,
        allocation_custody_event_fingerprint=HEX_D,
        result_custody_chain_fingerprint=HEX_E,
    )


def _allocation_current(receipt: ProcessServiceAllocationReceipt) -> ProcessServiceAllocationCurrent:
    """Build the exact P4 current pointer required by P5A correlation."""
    return ProcessServiceAllocationCurrent(
        tenant_id=receipt.tenant_id,
        document_id=receipt.document_id,
        process_document_fingerprint=receipt.allocated_document_fingerprint,
        custody_chain_fingerprint=receipt.result_custody_chain_fingerprint,
        custody_head_event_id=receipt.allocation_custody_event_id,
        custody_head_fingerprint=receipt.allocation_custody_event_fingerprint,
        custody_head_sequence_number=receipt.prior_custody_head_sequence_number + 1,
        current_holder_reference=receipt.to_holder_reference,
        authority_evidence_reference=receipt.allocation_command_id,
        authority_evidence_fingerprint=receipt.fingerprint,
    )


def _decision(tenant_id: str, authority_id: str, attempt_id: str) -> Any:
    """Create P5B authority through canonical P4 and P5A setup APIs."""
    receipt = _allocation_receipt(tenant_id, authority_id, attempt_id)
    return authorize_process_service_attempt(
        allocation_receipt=receipt,
        allocation_current=_allocation_current(receipt),
        attempt_authority_id=authority_id,
        attempt_id=attempt_id,
        authorized_at=BASE + timedelta(minutes=2),
    )


def _transaction(client: MongoClient) -> Any:
    """Start one caller-owned snapshot transaction with durable concerns."""
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    return session


def _persist_authority(client: MongoClient, authority: Any, decision: Any) -> Any:
    """Persist setup authority and commit it as the caller."""
    session = _transaction(client)
    try:
        result = p5b.ProcessServiceAttemptAuthorityRegistry.persist(decision, authority, session=session)
        session.commit_transaction()
        return result
    finally:
        session.end_session()


class _SynchronizedLifecycleCollection:
    """Delegate to real P2 Mongo calls while synchronizing its first absent read."""

    def __init__(self, collection: Any, barrier: threading.Barrier, arrivals: list[str], lock: threading.Lock, state: threading.local) -> None:
        self._collection = collection
        self._barrier = barrier
        self._arrivals = arrivals
        self._lock = lock
        self._state = state

    def find_one(self, query: dict[str, Any], *, session: Any) -> Any:
        row = self._collection.find_one(query, session=session)
        if set(query) == {"tenant_id", "evidence_identity"} and row is None:
            worker = str(getattr(self._state, "worker", "unknown"))
            with self._lock:
                self._arrivals.append(worker)
            self._barrier.wait(timeout=30)
        return row

    def insert_one(self, row: dict[str, Any], *, session: Any) -> Any:
        return self._collection.insert_one(row, session=session)


@dataclass(frozen=True)
class _WorkerOutcome:
    """One explicit caller-owned worker result; uncertain commits never win."""

    worker: str
    status: str
    result: Any = None
    error: BaseException | None = None
    labels: tuple[str, ...] = ()
    session: Any = None
    aborted: bool = False


def _labels(error: BaseException) -> tuple[str, ...]:
    """Collect Mongo error labels through cause/context without rewriting errors."""
    labels: list[str] = []
    seen: set[int] = set()
    current: BaseException | None = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        labels.extend(str(label) for label in getattr(current, "_error_labels", ()))
        current = current.__cause__ or current.__context__
    return tuple(dict.fromkeys(labels))


def test_real_mongo_p5c_composition_race(
    mongo_context: tuple[MongoClient, Any, Any, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify one real P2 insert collision through two P5C callers."""
    client, _database, authority, lifecycle = mongo_context
    tenant = f"tenant-p5c-race-{uuid.uuid4().hex}"
    authority_id = f"authority-p5c-race-{uuid.uuid4().hex}"
    attempt_id = f"attempt-p5c-race-{uuid.uuid4().hex}"
    decision = _decision(tenant, authority_id, attempt_id)
    seeded = _persist_authority(client, authority, decision)
    assert seeded.receipt.tenant_id == tenant
    pristine_authority = authority.find_one({"tenant_id": tenant, "attempt_authority_id": authority_id})
    assert pristine_authority is not None

    read_session = _transaction(client)
    try:
        durable = p5b.ProcessServiceAttemptAuthorityRegistry.get_by_attempt_authority_id(
            tenant, authority_id, authority, session=read_session
        )
        assert durable.to_dict() == seeded.receipt.to_dict()
        read_session.abort_transaction()
    finally:
        read_session.end_session()

    barrier = threading.Barrier(2)
    arrivals: list[str] = []
    observations: list[tuple[str, str, Any]] = []
    lock = threading.Lock()
    state = threading.local()
    synchronized = _SynchronizedLifecycleCollection(lifecycle, barrier, arrivals, lock, state)
    original_p5b = p5c.ProcessServiceAttemptAuthorityRegistry.get_by_attempt_authority_id
    original_p2 = p5c.LegalOperationsLifecycleRegistry.create

    def observed_p5b(tenant_value: str, locator: str, collection: object, *, session: object) -> object:
        worker = str(getattr(state, "worker", "unknown"))
        with lock:
            observations.append((worker, "p5b", session))
        return original_p5b(tenant_value, locator, collection, session=session)

    def observed_p2(value: object, collection: object, *, session: object, **kwargs: object) -> object:
        worker = str(getattr(state, "worker", "unknown"))
        with lock:
            observations.append((worker, "p2", session))
        return cast(Any, original_p2)(cast(Any, value), collection, session=session, **kwargs)

    monkeypatch.setattr(
        p5c.ProcessServiceAttemptAuthorityRegistry,
        "get_by_attempt_authority_id",
        staticmethod(observed_p5b),
    )
    monkeypatch.setattr(p5c.LegalOperationsLifecycleRegistry, "create", staticmethod(observed_p2))

    def worker(worker_name: str) -> _WorkerOutcome:
        state.worker = worker_name
        session = _transaction(client)
        try:
            try:
                result = p5c.orchestrate_process_service_attempt(
                    tenant_id=tenant,
                    attempt_authority_id=authority_id,
                    attempt_authority_collection=authority,
                    lifecycle_collection=synchronized,
                    session=session,
                )
                session.commit_transaction()
                return _WorkerOutcome(worker_name, "COMMITTED", result=result, session=session)
            except p2.LegalOperationsLifecycleRegistryError as error:
                labels = _labels(error)
                if (
                    isinstance(error, p2.LegalOperationsLifecycleRegistryError)
                    and str(error) == "M2_RETRY_TRANSACTION_REQUIRED"
                ):
                    aborted = False
                    if session.in_transaction:
                        session.abort_transaction()
                        aborted = True
                    return _WorkerOutcome(worker_name, "RETRY_REQUIRED", error=error, labels=labels, session=session, aborted=aborted)
                if "UnknownTransactionCommitResult" in labels:
                    return _WorkerOutcome(worker_name, "AMBIGUOUS_COMMIT", error=error, labels=labels, session=session)
                if session.in_transaction:
                    session.abort_transaction()
                return _WorkerOutcome(worker_name, "OTHER_ERROR", error=error, labels=labels, session=session)
            except BaseException as error:
                labels = _labels(error)
                ambiguous = "UnknownTransactionCommitResult" in labels
                if session.in_transaction:
                    session.abort_transaction()
                return _WorkerOutcome(worker_name, "AMBIGUOUS_COMMIT" if ambiguous else "OTHER_ERROR", error=error, labels=labels, session=session)
        finally:
            session.end_session()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker, name) for name in ("A", "B")]
        outcomes = [future.result() for future in futures]

    assert sorted(arrivals) == ["A", "B"]
    assert len(arrivals) == 2
    assert len({id(outcome.session) for outcome in outcomes}) == 2
    committed = [item for item in outcomes if item.status == "COMMITTED"]
    retry_required = [item for item in outcomes if item.status == "RETRY_REQUIRED"]
    ambiguous = [item for item in outcomes if item.status == "AMBIGUOUS_COMMIT"]
    other = [item for item in outcomes if item.status == "OTHER_ERROR"]
    print("P5C_RACE_DIAGNOSTIC")
    for item in outcomes:
        error = item.error
        if item.status == "COMMITTED":
            commit_attempted, commit_result = "YES", "COMMITTED"
        elif item.status == "RETRY_REQUIRED":
            commit_attempted, commit_result = "NO", "NOT_REACHED"
        elif item.status == "AMBIGUOUS_COMMIT":
            commit_attempted, commit_result = "YES", "AMBIGUOUS"
        else:
            commit_attempted, commit_result = "UNRECORDED", "UNRECORDED"
        raw_code = "NONE"
        cause = error.__cause__ if error is not None else None
        while cause is not None:
            candidate = getattr(cause, "code", None)
            if candidate is not None:
                raw_code = str(candidate)
                break
            cause = cause.__cause__ or cause.__context__
        print(f"WORKER={item.worker}")
        print(f"CATEGORY={item.status}")
        print(f"EXCEPTION_TYPE={type(error).__name__ if error is not None else 'NONE'}")
        print(f"EXCEPTION_REPR={error!r}")
        print(f"STABLE_ERROR_CODE={getattr(error, 'code', 'NONE')}")
        print(f"MONGO_ERROR_CODE={raw_code}")
        print(f"MONGO_LABELS={item.labels or 'NONE'}")
        print(f"COMMIT_ATTEMPTED={commit_attempted}")
        print(f"COMMIT_RESULT={commit_result}")
        print(f"CALLER_ABORTED={'YES' if item.aborted else 'NO'}")
    assert len(committed) == 1
    assert len(retry_required) == 1
    assert not ambiguous
    assert not other
    assert retry_required[0].error is not None
    assert isinstance(retry_required[0].error, p2.LegalOperationsLifecycleRegistryError)
    assert str(retry_required[0].error) == "M2_RETRY_TRANSACTION_REQUIRED"
    assert retry_required[0].aborted is True
    assert all("TransientTransactionError" in item.labels for item in retry_required)
    assert all("UnknownTransactionCommitResult" not in item.labels for item in retry_required)

    assert sorted((worker, kind) for worker, kind, _ in observations) == [
        ("A", "p2"),
        ("A", "p5b"),
        ("B", "p2"),
        ("B", "p5b"),
    ]
    sessions_by_worker: dict[str, dict[str, Any]] = {"A": {}, "B": {}}
    for worker_name, kind, session in observations:
        sessions_by_worker[worker_name][kind] = session
    assert sessions_by_worker["A"]["p5b"] is not sessions_by_worker["B"]["p5b"]
    assert sessions_by_worker["A"]["p2"] is sessions_by_worker["A"]["p5b"]
    assert sessions_by_worker["B"]["p2"] is sessions_by_worker["B"]["p5b"]

    durable_count = lifecycle.count_documents(
        {"tenant_id": tenant, "entity_type": "ServiceAttempt", "entity_identity": attempt_id}
    )
    assert durable_count == 1
    winner_record = lifecycle.find_one(
        {"tenant_id": tenant, "entity_type": "ServiceAttempt", "entity_identity": attempt_id}
    )
    assert winner_record is not None
    assert winner_record["p1_payload"]["state"] == ServiceAttemptState.ALLOCATED.value
    assert winner_record["p1_payload"]["tenant_id"] == durable.tenant_id
    assert winner_record["p1_payload"]["attempt_id"] == durable.attempt_id
    assert winner_record["p1_payload"]["instruction_id"] == durable.instruction_id
    assert winner_record["p1_payload"]["document_id"] == durable.document_id
    assert winner_record["p1_payload"]["deputy_id"] == durable.deputy_id
    assert winner_record["p1_payload"]["allocated_at"] == durable.allocated_at.isoformat()
    assert winner_record["p1_payload"]["allocation_evidence_reference"] == durable.allocation_evidence_reference

    verify_session = _transaction(client)
    try:
        winner = p2.LegalOperationsLifecycleRegistry.get(
            tenant, winner_record["evidence_identity"], lifecycle, session=verify_session
        )
        assert winner.to_dict() == committed[0].result.to_dict()
        verify_session.abort_transaction()
    finally:
        verify_session.end_session()

    assert authority.find_one({"tenant_id": tenant, "attempt_authority_id": authority_id}) == pristine_authority
    replay_session = _transaction(client)
    try:
        replay = p5c.orchestrate_process_service_attempt(
            tenant_id=tenant,
            attempt_authority_id=authority_id,
            attempt_authority_collection=authority,
            lifecycle_collection=lifecycle,
            session=replay_session,
        )
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()
    assert replay.to_dict() == committed[0].result.to_dict()
    assert lifecycle.count_documents(
        {"tenant_id": tenant, "entity_type": "ServiceAttempt", "entity_identity": attempt_id}
    ) == 1
    assert not hasattr(p5c, "authorize_process_service_attempt")
    assert not hasattr(p5c, "ServiceExecution")
    assert not hasattr(p5c, "ReturnOfService")


# ARTIFACT: test_process_service_attempt_orchestrator_concurrent_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-ORCHESTRATOR-CONCURRENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: deterministic P5C composition-race certificate only.
# TENANT POSTURE: one explicit synthetic tenant with tenant-scoped P5B/P2 evidence.
# FAIL-CLOSED POSTURE: ambiguous, divergent, unclassified, or extra durable outcomes fail.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
