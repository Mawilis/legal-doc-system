"""WILSY OS BillingRegistry real-Mongo certificate.

TITLE: BillingRegistry Explicit Collection and Session Certificate
VERSION: v1.0.0-BILLING-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify durable tenant-scoped invoice reads on governed MongoDB.
EPITOME: Explicit collections and caller sessions preserve canonical hydration and rollback semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_billing_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Python EOS billing integration certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes four operational Mongo scenarios.
COMPLIANCE: POPIA section 19 | GDPR Article 32 | SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic identifiers and bounded cleanup.
TENANT BOUNDARY: Every query includes tenant and invoice identity.
AUTHORITY BOUNDARY: Persistence evidence only; no execution authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Caller-owned sessions are forwarded unchanged.
"""
import os, uuid
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.collection import Collection
from tools.eos.saas.billing.billing_registry import BillingRegistry

URI = os.environ["TEST_VENDOR_MONGO_URI"]

def _document(tenant: str, invoice_id: str) -> dict[str, object]:
    return {"tenant_id": tenant, "invoice_id": invoice_id, "status": "open", "amount": 100.0, "total": 100.0, "tax_amount": 0.0, "currency": "ZAR", "line_items": [], "issued_at": datetime.now(timezone.utc), "proof_hash": "a" * 128}

def _run_billing_registry_matrix(case: int) -> None:
    """Execute one distinct durable BillingRegistry scenario."""
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    client.admin.command("ping")
    collection: Collection = client["wilsy_billing_registry_cert"]["platform_invoices"]
    tenant, other, invoice_id = f"cert-{uuid.uuid4().hex}", f"cert-{uuid.uuid4().hex}", f"INV-{uuid.uuid4().hex}"
    document = _document(tenant, invoice_id)
    try:
        if case == 1:
            collection.insert_one(document)
            result = BillingRegistry().get_platform_invoice(tenant, invoice_id, collection=collection)
            assert result is not None and result.tenant_id == tenant and result.invoice_id == invoice_id and result.currency == "ZAR"
        elif case in (2, 3):
            with client.start_session() as session:
                with session.start_transaction():
                    collection.insert_one(document, session=session)
                    local = BillingRegistry().get_platform_invoice(tenant, invoice_id, collection=collection, session=session)
                    assert local is not None and local.invoice_id == invoice_id
                    if case == 3:
                        session.abort_transaction()
            if case == 3:
                assert BillingRegistry().get_platform_invoice(tenant, invoice_id, collection=collection) is None
        else:
            collection.insert_one(document)
            assert BillingRegistry().get_platform_invoice(other, invoice_id, collection=collection) is None
            assert BillingRegistry().get_platform_invoice(tenant, invoice_id, collection=collection) is not None
    finally:
        collection.delete_one({"tenant_id": tenant, "invoice_id": invoice_id})
        client.close()

def test_rm_billing_registry_1_explicit_collection() -> None: _run_billing_registry_matrix(1)
def test_rm_billing_registry_2_transaction_local_visibility() -> None: _run_billing_registry_matrix(2)
def test_rm_billing_registry_3_transaction_abort() -> None: _run_billing_registry_matrix(3)
def test_rm_billing_registry_4_tenant_isolation() -> None: _run_billing_registry_matrix(4)

# ARTIFACT: test_billing_registry_real_mongo.py
# VERSION: v1.0.0-BILLING-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: persistence evidence only
# TENANT POSTURE: UUID-isolated bounded cleanup
# FAIL-CLOSED POSTURE: unavailable governed Mongo fails the certificate
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
