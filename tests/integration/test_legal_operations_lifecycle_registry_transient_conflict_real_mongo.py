"""Host-backed certificate for P2 transient transaction-conflict translation.

TITLE: Wilsy OS Legal Operations Lifecycle Registry Transient-Conflict Certificate
VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-TRANSIENT-CONFLICT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove that two caller-owned Mongo transactions racing one immutable P2
         evidence identity receive one committed result and one genuine
         TransientTransactionError translated to the governed retry signal.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_lifecycle_registry_transient_conflict_real_mongo.py
COLLABORATION / OWNERSHIP: P1 owns lifecycle evidence; P2 owns persistence and
                            translation only; this certificate owns test
                            sessions, transactions, synchronization, and cleanup.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-TRANSIENT-CONFLICT-REAL-MONGO-CERT
           records direct public-path evidence for labeled transactional write
           conflict translation without accepting commit uncertainty.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated database and opaque identifiers only;
                             no customer, provider, credential, or secret data.
TENANT BOUNDARY: Both workers use one explicit tenant and one exact evidence
                 identity; all verification reads retain that tenant predicate.
AUTHORITY BOUNDARY: The certificate invokes only the public P2 create/get path;
                    P1 remains the lifecycle authority and P2 derives no state.
TRANSACTION BOUNDARY: Every session, transaction, abort, commit, and retry is
                      caller-owned. P2 receives sessions but owns none.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; legal evidence is not payment truth.
FAIL-CLOSED DECLARATION: Missing synchronization, ambiguous commit, duplicate
                         key classification, absent transient labels, extra
                         durable rows, and any unclassified outcome fail.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
import sys
import threading
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, InvalidOperation, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    LegalInstruction,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION = "v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-TRANSIENT-CONFLICT-REAL-MONGO-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any]]:
    """Yield a writable transaction-capable isolated database and clean it."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            client.close()
            pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}: {error}")
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            client.close()
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            client.close()
            pytest.skip("replica set has no writable primary")
        probe = client.start_session()
        try:
            probe.start_transaction(
                read_concern=ReadConcern("snapshot"),
                write_concern=WriteConcern(w="majority", j=True),
            )
            probe.abort_transaction()
        except PyMongoError as error:
            pytest.fail(f"transactions unavailable after verified hello: {type(error).__name__}: {error}")
        finally:
            probe.end_session()
        database = client[f"p2_transient_{uuid.uuid4().hex}"]
        collection = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(collection)
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


def _instruction(tenant_id: str) -> LegalInstruction:
    """Build one immutable initial P1 fact shared by both racing callers."""
    return LegalInstruction(
        tenant_id=tenant_id,
        instruction_id="instruction-transient-race",
        case_matter_id="matter-transient-race",
        document_id="document-transient-race",
        registered_at=BASE,
        evidence_reference="registration-transient-race",
    )


class _AbsentReadBarrierCollection:
    """Delegate real Mongo calls while coordinating the first absent lookup."""

    def __init__(
        self,
        collection: Any,
        barrier: threading.Barrier,
        arrivals: list[str],
        inserts: list[str],
        lock: threading.Lock,
        state: threading.local,
    ) -> None:
        self._collection = collection
        self._barrier = barrier
        self._arrivals = arrivals
        self._inserts = inserts
        self._lock = lock
        self._state = state

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> Any:
        row = self._collection.find_one(query, session=session)
        if set(query) == {"tenant_id", "evidence_identity"} and row is None:
            worker = str(getattr(self._state, "worker", "unknown"))
            with self._lock:
                self._arrivals.append(worker)
            self._barrier.wait(timeout=30)
        return row

    def insert_one(self, row: dict[str, Any], *, session: Any = None) -> Any:
        worker = str(getattr(self._state, "worker", "unknown"))
        with self._lock:
            self._inserts.append(worker)
        return self._collection.insert_one(row, session=session)


@dataclass(frozen=True)
class _WorkerOutcome:
    """One caller-owned result with raw conflict and lifecycle observations."""

    worker: str
    status: str
    session: Any
    result: Any = None
    error: BaseException | None = None
    raw_cause: BaseException | None = None
    labels: tuple[str, ...] = ()
    abort_called: bool = False
    abort_error: BaseException | None = None
    commit_called: bool = False


def _cause_chain(error: BaseException | None) -> Iterator[BaseException]:
    """Walk technical causes without changing the governed exception."""
    seen: set[int] = set()
    current = error
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        yield current
        current = current.__cause__ or current.__context__


def _labels(error: BaseException | None) -> tuple[str, ...]:
    """Collect actual Mongo labels present on the cause chain."""
    values: list[str] = []
    for item in _cause_chain(error):
        values.extend(str(label) for label in getattr(item, "_error_labels", ()))
    return tuple(dict.fromkeys(values))


def _mongo_code(error: BaseException | None) -> str:
    """Return the first observed driver error code from the cause chain."""
    for item in _cause_chain(error):
        code = getattr(item, "code", None)
        if code is not None:
            return str(code)
    return "NONE"


def _worker(
    client: MongoClient,
    value: LegalInstruction,
    collection: _AbsentReadBarrierCollection,
    state: threading.local,
    worker_name: str,
) -> _WorkerOutcome:
    """Run one complete caller transaction against the real public P2 path."""
    state.worker = worker_name
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    try:
        try:
            result = LegalOperationsLifecycleRegistry.create(value, collection, session=session)
        except LegalOperationsLifecycleRegistryError as error:
            cause = error.__cause__ or error.__context__
            if str(error) != "M2_RETRY_TRANSACTION_REQUIRED":
                if session.in_transaction:
                    session.abort_transaction()
                return _WorkerOutcome(worker_name, "OTHER_ERROR", session, error=error, raw_cause=cause, labels=_labels(error))
            abort_called = False
            abort_error: BaseException | None = None
            try:
                session.abort_transaction()
                abort_called = True
            except InvalidOperation as abort_failure:
                abort_called = True
                abort_error = abort_failure
            return _WorkerOutcome(
                worker_name,
                "RETRY_REQUIRED",
                session,
                error=error,
                raw_cause=cause,
                labels=_labels(cause),
                abort_called=abort_called,
                abort_error=abort_error,
            )
        try:
            session.commit_transaction()
            return _WorkerOutcome(worker_name, "COMMITTED", session, result=result, commit_called=True)
        except BaseException as error:
            status = "AMBIGUOUS_COMMIT" if "UnknownTransactionCommitResult" in _labels(error) else "OTHER_ERROR"
            return _WorkerOutcome(worker_name, status, session, error=error, labels=_labels(error), commit_called=True)
    except BaseException as error:
        if session.in_transaction:
            session.abort_transaction()
        return _WorkerOutcome(worker_name, "OTHER_ERROR", session, error=error, labels=_labels(error))
    finally:
        session.end_session()


def test_real_mongo_transient_transaction_conflict_translation(
    mongo_context: tuple[MongoClient, Any, Any],
) -> None:
    """Prove one genuine transient loser and one durable winner per race."""
    client, database, collection = mongo_context
    tenant = f"tenant-p2-transient-{uuid.uuid4().hex}"
    value = _instruction(tenant)
    barrier = threading.Barrier(2)
    arrivals: list[str] = []
    inserts: list[str] = []
    lock = threading.Lock()
    state = threading.local()
    synchronized = _AbsentReadBarrierCollection(collection, barrier, arrivals, inserts, lock, state)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(_worker, client, value, synchronized, state, worker_name)
            for worker_name in ("A", "B")
        ]
        outcomes = [future.result() for future in futures]

    assert sorted(arrivals) == ["A", "B"]
    assert len(arrivals) == 2
    assert len(inserts) == 2
    assert len({id(item.session) for item in outcomes}) == 2
    committed = [item for item in outcomes if item.status == "COMMITTED"]
    retry_required = [item for item in outcomes if item.status == "RETRY_REQUIRED"]
    ambiguous = [item for item in outcomes if item.status == "AMBIGUOUS_COMMIT"]
    other = [item for item in outcomes if item.status == "OTHER_ERROR"]
    assert len(committed) == 1
    assert len(retry_required) == 1
    assert not ambiguous
    assert not other

    loser = retry_required[0]
    assert loser.error is not None
    assert str(loser.error) == "M2_RETRY_TRANSACTION_REQUIRED"
    assert loser.raw_cause is not None
    assert isinstance(loser.raw_cause, PyMongoError)
    assert not isinstance(loser.raw_cause, DuplicateKeyError)
    assert "TransientTransactionError" in loser.labels
    assert "UnknownTransactionCommitResult" not in loser.labels
    assert loser.abort_called is True
    assert _mongo_code(loser.raw_cause) != "NONE"
    print(f"LOSER_RAW_EXCEPTION_TYPE={type(loser.raw_cause).__name__}")
    print(f"LOSER_MONGO_ERROR_CODE={_mongo_code(loser.raw_cause)}")
    print(f"LOSER_MONGO_MESSAGE={loser.raw_cause}")
    print(f"LOSER_MONGO_LABELS={loser.labels}")
    print(f"DATABASE={database.name}")

    assert not hasattr(LegalOperationsLifecycleRegistry, "start_transaction")
    assert not hasattr(LegalOperationsLifecycleRegistry, "commit_transaction")
    assert not hasattr(LegalOperationsLifecycleRegistry, "abort_transaction")
    assert not hasattr(LegalOperationsLifecycleRegistry, "commit")
    assert not hasattr(LegalOperationsLifecycleRegistry, "abort")
    assert not hasattr(LegalOperationsLifecycleRegistry, "_client")
    assert not hasattr(LegalOperationsLifecycleRegistry, "client")
    assert not hasattr(LegalOperationsLifecycleRegistry, "mongo_client")

    winner = committed[0].result
    assert winner == value
    durable = collection.find_one({"tenant_id": tenant, "entity_type": "LegalInstruction"})
    assert durable is not None
    evidence_identity = durable["evidence_identity"]
    assert collection.count_documents({"tenant_id": tenant}) == 1
    verify_session = client.start_session()
    verify_session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    try:
        hydrated = LegalOperationsLifecycleRegistry.get(tenant, evidence_identity, collection, session=verify_session)
        assert hydrated == value
        verify_session.abort_transaction()
    finally:
        verify_session.end_session()

    replay_session = client.start_session()
    replay_session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    try:
        replay = LegalOperationsLifecycleRegistry.create(value, collection, session=replay_session)
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()
    assert replay == value
    assert collection.count_documents({"tenant_id": tenant}) == 1


# ARTIFACT: test_legal_operations_lifecycle_registry_transient_conflict_real_mongo.py
# VERSION: v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-TRANSIENT-CONFLICT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: direct P2 transient-conflict translation certificate only.
# TENANT POSTURE: exact tenant/evidence predicates; foreign evidence is absent.
# FAIL-CLOSED POSTURE: ambiguous, duplicate-key, unclassified, or extra rows reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
