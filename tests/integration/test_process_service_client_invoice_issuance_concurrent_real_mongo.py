"""P6F full ClientInvoice-write concurrency certificate.

TITLE: Process-Service Client Invoice Issuance Concurrent Canonical E2E
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Two complete P6F issuance transactions racing at ClientInvoice insert.
TENANT BOUNDARY: One tenant and canonical source set per isolated database.
TRANSACTION BOUNDARY: Workers own sessions and commit/abort; P6F owns none.
AUTHORITY BOUNDARY: P6F invoice issuance evidence only; no payment or settlement.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Ambiguous, fabricated, or non-conflict outcomes fail.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.1 races the real ClientInvoice write and retries whole tx.
"""
from datetime import timedelta
import os
import threading
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.process_service_client_invoice_issuance import ProcessServiceClientInvoiceIssuanceError, ProcessServiceClientInvoiceIssuanceRegistry, issue_process_service_client_invoice
from tests.integration.test_process_service_client_invoice_issuance_real_mongo import BASE, REPLICA_SET, URI, _issue, _seed_sources


class _InvoiceWriteBarrier:
    """Synchronize exactly the two real ClientInvoice insert calls."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection
        self.barrier = threading.Barrier(2)
        self.participants = 0
        self.lock = threading.Lock()

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> Any:
        return self.collection.find_one(query, session=session)

    def insert_one(self, record: dict[str, Any], *, session: Any = None) -> Any:
        with self.lock:
            self.participants += 1
        self.barrier.wait(timeout=30)
        return self.collection.insert_one(record, session=session)


@pytest.fixture()
def mongo() -> Iterator[tuple[MongoClient, Any]]:
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET)
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.skip(f"MONGO_RUNTIME_UNAVAILABLE: {type(error).__name__}")
        if hello.get("setName") != REPLICA_SET:
            pytest.skip(f"MONGO_REPLICA_SET_UNAVAILABLE: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
        database = client.get_database("p6f_race_" + uuid4().hex[:20], read_concern=ReadConcern("majority"), write_concern=WriteConcern(w="majority", j=True))
        yield client, database
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def test_real_mongo_full_issuance_race_at_client_invoice_write(mongo: tuple[MongoClient, Any]) -> None:
    client, database = mongo
    sources = _seed_sources(client, database, tenant="tenant-race", prefix="race")
    invoices = database.get_collection("client_invoices")
    issuance = database.get_collection("issuance")
    ProcessServiceClientInvoiceIssuanceRegistry.ensure_indexes(issuance)
    raced_invoices = _InvoiceWriteBarrier(invoices)
    outcomes: list[str] = []
    raw_causes: list[tuple[str, Any, Any]] = []
    lock = threading.Lock()
    fixed = BASE + timedelta(hours=1)

    def worker() -> None:
        session = client.start_session()
        try:
            session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
            issue_process_service_client_invoice(tenant_id=sources["tenant"], billing_eligibility_evidence_identity=sources["eligibility_eid"], binding_evidence_identity=sources["binding_eid"], profile_evidence_identity=sources["profile_eid"], eligibility_collection=sources["eligibility"], assessment_collection=sources["assessments"], profile_collection=sources["profiles"], binding_collection=sources["bindings"], client_invoice_collection=raced_invoices, issuance_collection=issuance, session=session, clock=lambda: fixed)
            session.commit_transaction()
            result = "WINNER"
        except ProcessServiceClientInvoiceIssuanceError as error:
            if session.in_transaction:
                session.abort_transaction()
            result = error.code
            cause = error.__cause__
            with lock:
                raw_causes.append((type(cause).__name__ if cause is not None else "None", getattr(cause, "code", None), getattr(cause, "_error_labels", None)))
        except Exception as error:
            if session.in_transaction:
                session.abort_transaction()
            result = f"OTHER:{type(error).__name__}"
        finally:
            session.end_session()
        with lock:
            outcomes.append(result)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert raced_invoices.participants == 2
    assert len(outcomes) == 2
    assert outcomes.count("WINNER") == 1
    assert outcomes.count("P6F_RETRY_TRANSACTION_REQUIRED") == 1
    assert not [item for item in outcomes if item not in {"WINNER", "P6F_RETRY_TRANSACTION_REQUIRED"}]
    assert issuance.count_documents({"tenant_id": "tenant-race"}) == 1
    assert invoices.count_documents({"tenant_id": "tenant-race"}) == 1
    assert len(raw_causes) == 1
    cause_type, cause_code, labels = raw_causes[0]
    assert cause_type in {"DuplicateKeyError", "WriteConflict", "OperationFailure"}
    assert cause_code in {11000, 112, None}
    assert not (labels and "UnknownTransactionCommitResult" in labels)

    replay_clock_calls = {"count": 0}
    def replay_clock() -> Any:
        replay_clock_calls["count"] += 1
        return fixed + timedelta(hours=1)
    invoice, evidence = _issue(client, sources, invoices, issuance, clock=replay_clock)
    assert invoice.invoice_id.startswith("p6f-")
    assert evidence.invoice_id == invoice.invoice_id
    assert replay_clock_calls["count"] == 0
    assert issuance.count_documents({"tenant_id": "tenant-race"}) == 1
    assert invoices.count_documents({"tenant_id": "tenant-race"}) == 1


# ARTIFACT: test_process_service_client_invoice_issuance_concurrent_real_mongo.py
# VERSION: v1.0.1-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-CONCURRENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: canonical race certificate only; no payment or settlement.
# TENANT POSTURE: all workers share one tenant-scoped source set and database.
# FAIL-CLOSED POSTURE: only one winner and one genuine retry loser are accepted.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
