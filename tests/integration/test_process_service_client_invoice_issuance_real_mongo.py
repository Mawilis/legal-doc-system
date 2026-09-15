"""P6F ordinary real-Mongo persistence certificate.

TITLE: Process-Service Client Invoice Issuance Real-Mongo Certificate
VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
SCOPE: Durable Billing ClientInvoice plus immutable issuance evidence.
TENANT BOUNDARY: UUID-isolated database and tenant predicates on every operation.
TRANSACTION BOUNDARY: The certificate owns setup sessions; P6F never does.
AUTHORITY BOUNDARY: P6F issuance only; no quotation, payment, execution, or settlement.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution/settlement.
FAIL-CLOSED: Runtime availability may skip; index, source, replay, and corruption failures fail.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0 certifies P6F durable round-trip and tenant isolation.
"""
from datetime import timedelta
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.billing.billing_registry import BillingRegistry
from tools.eos.saas.billing.process_service_client_invoice_issuance import ProcessServiceClientInvoiceIssuanceRegistry
from tools.eos.saas.domain.billing import ClientInvoiceExactMoney, ClientInvoiceExactMoneyLine
from tests.unit.test_process_service_client_invoice_issuance import _sources, BASE, HASH

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
REPLICA_SET = "wilsyVendorCertRS"


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
        database = client.get_database(
            "p6f_" + uuid4().hex[:20],
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        yield client, database
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def test_real_mongo_issuance_evidence_round_trip_and_tenant_isolation(mongo: tuple[MongoClient, Any]) -> None:
    client, database = mongo
    invoice_collection = database.get_collection("client_invoices")
    issuance_collection = database.get_collection("issuance")
    ProcessServiceClientInvoiceIssuanceRegistry.ensure_indexes(issuance_collection)
    basis, binding, profile = _sources()
    money = ClientInvoiceExactMoney("ZAR", 12500, 0, 12500, (ClientInvoiceExactMoneyLine("Service fee", 1, 12500, 12500, 0, 0, "ZAR"),))
    session = client.start_session()
    session.start_transaction(read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))
    try:
        invoice = BillingRegistry().create_client_invoice_exact("tenant-a", money, customer_id=profile.customer_id, customer_name=profile.customer_legal_name, payment_terms_days=profile.payment_terms.days_after_issue, tax_type="vat", seller_jurisdiction=profile.seller_jurisdiction, customer_jurisdiction=profile.customer_jurisdiction, collection_method=profile.collection_method.method.value, issued_at=BASE + timedelta(hours=1), due_at=BASE + timedelta(days=15), line_tax_rates_basis_points=(0,), idempotency_key="p6f-real", collection=invoice_collection, session=session)
        evidence = __import__("tools.eos.saas.billing.process_service_client_invoice_issuance", fromlist=["ProcessServiceClientInvoiceIssuanceEvidence"]).ProcessServiceClientInvoiceIssuanceEvidence.from_invoice_sources(tenant_id="tenant-a", invoice=invoice, invoice_idempotency_key="p6f-real", basis=basis, binding=binding, profile=profile, billing_eligibility_evidence_identity=HASH, binding_evidence_identity=HASH, profile_evidence_identity=HASH, issuance_id="a" * 128, line_tax_rates_basis_points=(0,))
        ProcessServiceClientInvoiceIssuanceRegistry.create(evidence, issuance_collection, session=session)
        session.commit_transaction()
    finally:
        session.end_session()
    hydrated = ProcessServiceClientInvoiceIssuanceRegistry.get("tenant-a", next(row["evidence_identity"] for row in issuance_collection.find({"tenant_id": "tenant-a"})), issuance_collection)
    assert hydrated.to_dict() == evidence.to_dict()
    with pytest.raises(Exception, match="P6F_NOT_FOUND"):
        ProcessServiceClientInvoiceIssuanceRegistry.get("tenant-b", hydrated.fingerprint, issuance_collection)


# ARTIFACT: test_process_service_client_invoice_issuance_real_mongo.py
# VERSION: v1.0.0-PROCESS-SERVICE-CLIENT-INVOICE-ISSUANCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real persistence certificate only; no payment or settlement.
# TENANT POSTURE: UUID-isolated durable records with silent foreign absence.
# FAIL-CLOSED POSTURE: unavailable runtime skips; all post-hello failures fail.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
