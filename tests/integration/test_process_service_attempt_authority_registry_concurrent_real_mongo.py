"""Deterministic real-Mongo P5B duplicate-key transaction-race certificate.

TITLE: Wilsy OS Process-Service Attempt Authority Registry Concurrent Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify that two caller-owned Mongo transactions synchronized after
         the same absent attempt lookup produce exactly one durable P5B receipt,
         with the losing duplicate-key race classified for whole-transaction
         retry and no losing evidence surviving abort.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_attempt_authority_registry_concurrent_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed P5B concurrency certificate only. P4B
                            owns allocation evidence, P5A owns attempt-
                            authorization evidence, P5B owns append-only
                            receipt persistence, and each worker owns its Mongo
                            session and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CONCURRENT-REAL-MONGO-CERT
           certifies deterministic barrier synchronization, positive duplicate-
           key retry classification, winner durability, and loser rollback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant and opaque evidence;
                             no provider, secret, customer, or external call.
TENANT BOUNDARY: Both competing immutable receipts use one explicit synthetic
                 tenant and a shared attempt identity; no cross-tenant inference
                 or disclosure is possible.
AUTHORITY BOUNDARY: This certificate proves P5B race classification only. It
                    does not construct or transition ServiceAttempt, create
                    service/return evidence, mutate P2/P4 state, or create a
                    current pointer.
TRANSACTION BOUNDARY: Two worker sessions and transactions are started,
                      committed, and aborted by the certificate caller. P5B
                      never owns, retries, or heals either transaction.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; no invoice, payment, paid-state,
                              or settlement evidence is represented here.
FAIL-CLOSED DECLARATION: A missing barrier arrival, ambiguous commit, raw or
                         misclassified loser, extra durable winner, surviving
                         loser evidence, persistence failure, or corruption is
                         a certificate failure, never a hidden skip or pass.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
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

from tools.eos.legal_operations.domain.process_service_attempt_authority import (
    authorize_process_service_attempt,
)
from tools.eos.legal_operations.registry import process_service_attempt_authority_registry as registry
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)


VERSION = "v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CONCURRENT-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
TENANT = "tenant-p5b-race"
ATTEMPT_ID = "attempt-race"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield one verified writable replica set; runtime failure is not skipped."""
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

        database = client[f"p5b_attempt_race_{uuid.uuid4().hex}"]
        collection = database.get_collection(
            registry.RECEIPT_COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(collection)
        yield client, database, collection
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


def _receipt(tenant_id: str) -> ProcessServiceAllocationReceipt:
    """Build shared valid P4 evidence so only P5A identities diverge."""
    return ProcessServiceAllocationReceipt(
        tenant_id=tenant_id,
        allocation_command_id="allocation-command-race",
        idempotency_key="allocation-idempotency-race",
        instruction_id="instruction-race",
        case_matter_id="matter-race",
        document_id="document-race",
        district_id="district-race",
        sheriff_office_id="office-race",
        deputy_id="deputy-race",
        assignment_decision_id="assignment-race",
        assignment_decision_fingerprint=HEX_A,
        source_instruction_fingerprint=HEX_B,
        source_document_fingerprint=HEX_C,
        source_district_fingerprint=HEX_D,
        source_sheriff_office_fingerprint=HEX_E,
        source_deputy_fingerprint=HEX_F,
        prior_custody_chain_fingerprint=HEX_A,
        prior_custody_head_event_id="custody-head-race",
        prior_custody_head_fingerprint=HEX_B,
        prior_custody_head_sequence_number=7,
        from_holder_reference="office-race",
        to_holder_reference="deputy-race",
        allocation_custody_event_id="custody-allocation-race",
        allocation_evidence_reference="allocation-evidence-race",
        allocated_at=BASE,
        allocated_document_fingerprint=HEX_C,
        allocation_custody_event_fingerprint=HEX_D,
        result_custody_chain_fingerprint=HEX_E,
    )


def _current(receipt: ProcessServiceAllocationReceipt) -> ProcessServiceAllocationCurrent:
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


def _decision(authority_id: str) -> Any:
    """Authorize one valid P5A decision with a race-specific authority identity."""
    receipt = _receipt(TENANT)
    return authorize_process_service_attempt(
        allocation_receipt=receipt,
        allocation_current=_current(receipt),
        attempt_authority_id=authority_id,
        attempt_id=ATTEMPT_ID,
        authorized_at=BASE + timedelta(minutes=2),
    )


class _BarrierCursor:
    """Cursor proxy that releases both workers after the absent attempt read."""

    def __init__(self, cursor: Any, barrier: threading.Barrier, arrivals: list[str], lock: threading.Lock, state: threading.local) -> None:
        self._cursor = cursor
        self._barrier = barrier
        self._arrivals = arrivals
        self._lock = lock
        self._state = state

    def __iter__(self):  # type: ignore[no-untyped-def]
        for row in self._cursor:
            yield row
        worker = str(getattr(self._state, "worker", "unknown"))
        with self._lock:
            self._arrivals.append(worker)
        self._barrier.wait(timeout=30)


class _SynchronizedCollection:
    """Real Mongo collection proxy synchronizing only the pre-insert lookup."""

    def __init__(self, collection: Any, barrier: threading.Barrier, arrivals: list[str], state: threading.local) -> None:
        self._collection = collection
        self._barrier = barrier
        self._arrivals = arrivals
        self._lock = threading.Lock()
        self._state = state

    def find(self, query: dict[str, Any], *, session: Any) -> Any:
        cursor = self._collection.find(query, session=session)
        if query.get("attempt_id") == ATTEMPT_ID:
            return _BarrierCursor(cursor, self._barrier, self._arrivals, self._lock, self._state)
        return cursor

    def find_one(self, query: dict[str, Any], *, session: Any) -> Any:
        return self._collection.find_one(query, session=session)

    def insert_one(self, row: dict[str, Any], *, session: Any) -> Any:
        return self._collection.insert_one(row, session=session)


@dataclass(frozen=True)
class _WorkerOutcome:
    """Explicit worker result; ambiguous commits are never winners."""

    worker: str
    status: str
    decision: Any
    result: Any = None
    error: BaseException | None = None
    labels: tuple[str, ...] = ()


def _run_worker(
    client: MongoClient,
    collection: Any,
    race_collection: Any,
    worker: str,
    decision: Any,
    state: threading.local,
) -> _WorkerOutcome:
    """Run one public P5B persist with caller-owned commit/abort handling."""
    state.worker = worker
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    try:
        result = registry.persist(decision, race_collection, session=session)
        try:
            session.commit_transaction()
        except BaseException as error:
            labels = tuple(str(label) for label in getattr(error, "_error_labels", ()))
            if "UnknownTransactionCommitResult" in labels:
                return _WorkerOutcome(worker, "AMBIGUOUS", decision, error=error, labels=labels)
            raise
        return _WorkerOutcome(worker, "COMMITTED", decision, result=result)
    except BaseException as error:
        labels = tuple(str(label) for label in getattr(error, "_error_labels", ()))
        try:
            if session.in_transaction:
                session.abort_transaction()
        finally:
            session.end_session()
        return _WorkerOutcome(worker, "REJECTED", decision, error=error, labels=labels)
    finally:
        if session.has_ended is False:
            session.end_session()


def test_real_mongo_deterministic_p5b_duplicate_key_race(
    mongo_context: tuple[MongoClient, Any, Any],
) -> None:
    """Prove exactly one attempt-identity winner and one governed retry loser."""
    client, database, collection = mongo_context
    decision_a = _decision("attempt-authority-race-a")
    decision_b = _decision("attempt-authority-race-b")
    barrier = threading.Barrier(2)
    arrivals: list[str] = []
    state = threading.local()
    race_collection = _SynchronizedCollection(collection, barrier, arrivals, state)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(_run_worker, client, collection, race_collection, "a", decision_a, state),
            executor.submit(_run_worker, client, collection, race_collection, "b", decision_b, state),
        ]
        outcomes = [future.result() for future in futures]

    assert sorted(arrivals) == ["a", "b"]
    assert sorted(outcome.status for outcome in outcomes) == ["COMMITTED", "REJECTED"]
    assert not any(outcome.status == "AMBIGUOUS" for outcome in outcomes)
    winners = [outcome for outcome in outcomes if outcome.status == "COMMITTED"]
    losers = [outcome for outcome in outcomes if outcome.status == "REJECTED"]
    assert len(winners) == 1
    assert len(losers) == 1
    winner = winners[0]
    loser = losers[0]
    assert loser.error is not None
    assert isinstance(loser.error, registry.ProcessServiceAttemptAuthorityRegistryRetryRequiredError)
    assert loser.error.code == "P5B_WHOLE_TRANSACTION_RETRY_REQUIRED"
    assert "UnknownTransactionCommitResult" not in loser.labels
    assert winner.result is not None
    assert winner.result.outcome is registry.ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED

    verify = client.start_session()
    verify.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    try:
        rows = list(collection.find({"tenant_id": TENANT, "attempt_id": ATTEMPT_ID}, session=verify))
        assert len(rows) == 1
        durable = registry.get_by_attempt_id(TENANT, ATTEMPT_ID, collection, session=verify)
        assert durable.to_dict() == winner.result.receipt.to_dict()
        assert durable.authority_decision_fingerprint == winner.decision.fingerprint
        verify.commit_transaction()
    finally:
        verify.end_session()

    assert collection.count_documents({"tenant_id": TENANT, "attempt_id": ATTEMPT_ID}) == 1
    assert collection.count_documents({"tenant_id": TENANT}) == 1
    loser_authority = loser.decision.attempt_authority_id
    loser_verify = client.start_session()
    loser_verify.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    try:
        with pytest.raises(registry.ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError) as caught:
            registry.get_by_attempt_authority_id(TENANT, loser_authority, collection, session=loser_verify)
        assert caught.value.code == "P5B_ATTEMPT_AUTHORITY_NOT_FOUND"
        loser_verify.commit_transaction()
    finally:
        loser_verify.end_session()

    index_names = {str(index["name"]) for index in collection.list_indexes()}
    assert {
        registry.AUTHORITY_INDEX_NAME,
        registry.ATTEMPT_INDEX_NAME,
        registry.EVIDENCE_INDEX_NAME,
    }.issubset(index_names)
    assert not any("current" in name.casefold() for name in index_names)
    assert registry.RECEIPT_COLLECTION in database.list_collection_names()
    assert not any("current" in name.casefold() for name in database.list_collection_names())


# ARTIFACT: test_process_service_attempt_authority_registry_concurrent_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CONCURRENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: deterministic P5B duplicate-key race evidence only
# TENANT POSTURE: one explicit synthetic tenant; no cross-tenant disclosure
# FAIL-CLOSED POSTURE: ambiguous or unclassified outcomes fail the certificate
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution/settlement
# END OF WILSY OS SOVEREIGN ARTIFACT
