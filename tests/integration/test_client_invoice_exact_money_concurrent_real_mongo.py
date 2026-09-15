"""P6E deterministic exact-invoice writer-race certificate.
TITLE: Exact ClientInvoice Concurrent Immutable Writer Certification
VERSION: v1.0.0-P6E-EXACT-CLIENT-INVOICE-MONEY-CONCURRENT-CERT
AUTHORITY: Wilsy OS Core Governance
TENANT BOUNDARY: Both callers share one explicit tenant/idempotency identity.
TRANSACTION BOUNDARY: Two caller-owned sessions; no internal retry or commit.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED: Exactly one winner and one governed retry loser are required.
"""
from datetime import datetime, timezone
import os
from threading import Barrier, Thread
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.billing_registry import BillingRegistry
from tools.eos.saas.domain.billing import ClientInvoiceExactMoney, ClientInvoiceExactMoneyLine

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"


class _InsertBoundary:
    def __init__(self, collection, barrier): self.collection, self.barrier = collection, barrier
    def find_one(self, *args, **kwargs): return self.collection.find_one(*args, **kwargs)
    def insert_one(self, *args, **kwargs):
        self.barrier.wait(timeout=20)
        return self.collection.insert_one(*args, **kwargs)


@pytest.fixture()
def mongo():
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET)
    try: hello = client.admin.command("hello")
    except Exception as error: client.close(); pytest.skip(str(error))
    if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
        client.close(); pytest.skip("writable replica unavailable")
    name = "p6e_c_" + uuid4().hex[:18]
    db = client.get_database(name, read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority", j=True))
    try:
        yield client, db
    finally:
        client.drop_database(name); client.close()


def test_two_caller_transactions_have_one_winner_and_retry_loser(mongo):
    client, db = mongo
    collection = db["client_invoices"]
    collection.create_index([("tenant_id", 1), ("idempotency_key", 1)], unique=True)
    value = ClientInvoiceExactMoney("ZAR", 100, 15, 115, (ClientInvoiceExactMoneyLine("x", 1, 100, 100, 15, 0, "ZAR"),))
    barrier = Barrier(2); outcomes = []; causes = []
    kwargs: dict[str, Any] = dict(customer_id="customer-a", customer_name="Customer A", payment_terms_days=30, tax_type="vat", seller_jurisdiction="ZA", customer_jurisdiction="ZA", collection_method="send_invoice", issued_at=datetime(2026, 9, 15, tzinfo=timezone.utc), due_at=datetime(2026, 10, 15, tzinfo=timezone.utc), line_tax_rates_basis_points=(1500,))

    def worker():
        session = client.start_session(); session.start_transaction()
        try:
            BillingRegistry().create_client_invoice_exact("tenant-a", value, idempotency_key="race", collection=_InsertBoundary(collection, barrier), session=session, **kwargs)
            session.commit_transaction(); outcomes.append("WINNER")
        except Exception as error:
            try: session.abort_transaction()
            except Exception: pass
            outcomes.append("RETRY" if "M2_RETRY_TRANSACTION_REQUIRED" in str(error) else "OTHER")
            causes.append(error.__cause__)
        finally: session.end_session()

    threads = [Thread(target=worker) for _ in range(2)]
    for thread in threads: thread.start()
    for thread in threads: thread.join(timeout=30)
    assert sorted(outcomes) == ["RETRY", "WINNER"]
    assert all(cause is None or isinstance(cause, PyMongoError) for cause in causes)
    assert collection.count_documents({"tenant_id": "tenant-a"}) == 1


# ARTIFACT: test_client_invoice_exact_money_concurrent_real_mongo.py
# VERSION: v1.0.0-P6E-EXACT-CLIENT-INVOICE-MONEY-CONCURRENT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
