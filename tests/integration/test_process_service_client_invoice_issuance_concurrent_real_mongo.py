"""P6F deterministic concurrent duplicate-key certificate.

TITLE: Process-Service Client Invoice Issuance Concurrent Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-CONCURRENT-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Caller-owned transaction race handling for immutable P6F evidence.
TENANT BOUNDARY: One UUID-isolated tenant/database per fixture.
TRANSACTION BOUNDARY: Workers own sessions, begin/commit/abort; P6F owns none.
AUTHORITY BOUNDARY: Persistence/replay only; no invoice payment or settlement.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Exactly one durable winner and one governed retry loser are required.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0 certifies deterministic P6F duplicate-key race handling.
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

from tools.eos.saas.billing.process_service_client_invoice_issuance import ProcessServiceClientInvoiceIssuanceEvidence, ProcessServiceClientInvoiceIssuanceRegistry
from tools.eos.saas.billing.billing_registry import BillingRegistry
from tools.eos.saas.domain.billing import ClientInvoiceExactMoney, ClientInvoiceExactMoneyLine
from tests.unit.test_process_service_client_invoice_issuance import _sources, BASE, HASH

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"


class _InitialReadBarrier:
    """Synchronize only the two pre-insert reads; no sleeps or retries."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection
        self.barrier = threading.Barrier(2)
        self.calls = 0
        self.lock = threading.Lock()

    def find_one(self, query: dict[str, Any], *, session: Any = None) -> Any:
        with self.lock:
            first_read = self.calls < 2
            self.calls += 1
        result = self.collection.find_one(query, session=session)
        if first_read:
            self.barrier.wait(timeout=10)
        return result

    def insert_one(self, record: dict[str, Any], *, session: Any = None) -> Any:
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


def test_real_mongo_one_winner_one_retry_loser(mongo: tuple[MongoClient, Any]) -> None:
    client, database = mongo
    invoices = database.get_collection("client_invoices")
    issuance = database.get_collection("issuance")
    ProcessServiceClientInvoiceIssuanceRegistry.ensure_indexes(issuance)
    basis, binding, profile = _sources()
    money = ClientInvoiceExactMoney("ZAR", 12500, 0, 12500, (ClientInvoiceExactMoneyLine("Service fee", 1, 12500, 12500, 0, 0, "ZAR"),))
    setup = client.start_session()
    setup.start_transaction(write_concern=WriteConcern(w="majority", j=True))
    try:
        invoice = BillingRegistry().create_client_invoice_exact("tenant-a", money, customer_id=profile.customer_id, customer_name=profile.customer_legal_name, payment_terms_days=profile.payment_terms.days_after_issue, tax_type="vat", seller_jurisdiction=profile.seller_jurisdiction, customer_jurisdiction=profile.customer_jurisdiction, collection_method=profile.collection_method.method.value, issued_at=BASE + timedelta(hours=1), due_at=BASE + timedelta(days=15), line_tax_rates_basis_points=(0,), idempotency_key="p6f-race", collection=invoices, session=setup)
        setup.commit_transaction()
    finally:
        setup.end_session()
    evidence = ProcessServiceClientInvoiceIssuanceEvidence.from_invoice_sources(tenant_id="tenant-a", invoice=invoice, invoice_idempotency_key="p6f-race", basis=basis, binding=binding, profile=profile, billing_eligibility_evidence_identity=HASH, binding_evidence_identity=HASH, profile_evidence_identity=HASH, issuance_id="b" * 128, line_tax_rates_basis_points=(0,))
    raced_issuance = _InitialReadBarrier(issuance)
    outcomes: list[str] = []
    lock = threading.Lock()

    def worker() -> None:
        session = client.start_session()
        try:
            session.start_transaction(write_concern=WriteConcern(w="majority", j=True))
            ProcessServiceClientInvoiceIssuanceRegistry.create(evidence, raced_issuance, session=session)
            session.commit_transaction()
            result = "WINNER"
        except Exception as error:
            try:
                if session.in_transaction:
                    session.abort_transaction()
            except Exception:
                pass
            result = getattr(error, "code", type(error).__name__)
            if result in {11000, 112, "DuplicateKeyError"} or "TransientTransactionError" in str(error):
                result = "P6F_RETRY_TRANSACTION_REQUIRED"
        finally:
            session.end_session()
        with lock:
            outcomes.append(result)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads: thread.start()
    for thread in threads: thread.join(timeout=30)
    assert len(outcomes) == 2
    assert outcomes.count("WINNER") == 1
    assert outcomes.count("P6F_RETRY_TRANSACTION_REQUIRED") == 1
    assert issuance.count_documents({"tenant_id": "tenant-a"}) == 1


# ARTIFACT: test_process_service_client_invoice_issuance_concurrent_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-CONCURRENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: race certificate only; no financial execution.
# TENANT POSTURE: isolated tenant and unique immutable issuance evidence.
# FAIL-CLOSED POSTURE: ambiguous outcomes fail the certificate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
