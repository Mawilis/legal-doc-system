"""P6E exact ClientInvoice real-Mongo certificate.
TITLE: Exact ClientInvoice Money Durable Certification
VERSION: v1.0.0-P6E-EXACT-CLIENT-INVOICE-MONEY-RM-CERT
AUTHORITY: Wilsy OS Core Governance
TENANT BOUNDARY: UUID-isolated tenant-scoped invoice evidence.
TRANSACTION BOUNDARY: Caller owns sessions and transactions.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED: Runtime corruption and divergent replay reject.
"""
from datetime import datetime, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.billing_registry import BillingRegistry
from tools.eos.saas.domain.billing import ClientInvoiceExactMoney, ClientInvoiceExactMoneyLine

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture()
def mongo():
    client = MongoClient(URI, serverSelectionTimeoutMS=3000, replicaSet=REPLICA_SET)
    try:
        hello = client.admin.command("hello")
    except Exception as error:
        client.close(); pytest.skip(f"Mongo unavailable: {error}")
    if hello.get("setName") != REPLICA_SET or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
        client.close(); pytest.skip("Expected writable replica set unavailable")
    name = "p6e_" + uuid4().hex[:20]
    database = client.get_database(name, read_concern=ReadConcern("majority"), write_concern=WriteConcern("majority", j=True))
    try:
        yield client, database
    finally:
        client.drop_database(name)
        client.close()


def _money():
    line = ClientInvoiceExactMoneyLine("Service", 3, 333, 999, 150, 0, "ZAR")
    return ClientInvoiceExactMoney("ZAR", 999, 150, 1149, (line,))


def test_exact_money_persists_replays_hydrates_and_is_tenant_scoped(mongo):
    client, db = mongo
    collection = db["client_invoices"]
    registry = BillingRegistry()
    value = _money()
    session = client.start_session()
    kwargs: dict[str, Any] = dict(customer_id="customer-a", customer_name="Customer A", payment_terms_days=30, tax_type="vat", seller_jurisdiction="ZA", customer_jurisdiction="ZA", collection_method="send_invoice", issued_at=datetime(2026, 9, 15, tzinfo=timezone.utc), due_at=datetime(2026, 10, 15, tzinfo=timezone.utc), line_tax_rates_basis_points=(1500,))
    try:
        first = registry.create_client_invoice_exact("tenant-a", value, idempotency_key="p6e-a", collection=collection, session=session, **kwargs)
        replay = registry.create_client_invoice_exact("tenant-a", value, idempotency_key="p6e-a", collection=collection, session=session, **kwargs)
        assert first == replay
        assert collection.count_documents({"tenant_id": "tenant-a"}) == 1
        raw = collection.find_one({"tenant_id": "tenant-a", "idempotency_key": "p6e-a"})
        assert raw["subtotal_minor"] == 999 and isinstance(raw["subtotal_minor"], int)
        assert raw["exact_money_fingerprint"] == value.exact_money_fingerprint
        hydrated = registry.get_client_invoice("tenant-a", first.invoice_id, collection=collection)
        assert hydrated is not None and hydrated.exact_money == value
        assert registry.get_client_invoice("tenant-b", first.invoice_id, collection=collection) is None
        divergent = ClientInvoiceExactMoney("ZAR", 1002, 150, 1152, (ClientInvoiceExactMoneyLine("Service", 3, 334, 1002, 150, 0, "ZAR"),))
        with pytest.raises(ValueError, match="CLIENT_INVOICE_REPLAY_CONFLICT"):
            registry.create_client_invoice_exact("tenant-a", divergent, idempotency_key="p6e-a", collection=collection, **kwargs)
    finally:
        session.end_session()


# ARTIFACT: test_client_invoice_exact_money_real_mongo.py
# VERSION: v1.0.0-P6E-EXACT-CLIENT-INVOICE-MONEY-RM-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
