"""WILSY OS BillingRegistry direct certificate.

TITLE: BillingRegistry Session-Aware Lookup Certificate
VERSION: v1.0.0-BILLING-REGISTRY-LOOKUP-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify tenant-scoped explicit collection and session forwarding.
EPITOME: Durable invoice lookup remains compatible while supporting trusted composition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_registry.py
COLLABORATION / OWNERSHIP: Python EOS billing certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 certifies explicit collection/session lookup semantics.
COMPLIANCE: POPIA section 19 | GDPR Article 32 | SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque invoice references.
TENANT BOUNDARY: Tenant and invoice identifiers are queried together.
AUTHORITY BOUNDARY: Evidence only; no authorization or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Caller session is forwarded unchanged.
"""
from tools.eos.saas.billing.billing_registry import BillingRegistry
import inspect
import tools.eos.saas.billing.billing_registry as billing_module

class Collection:
    def __init__(self, result=None): self.result, self.calls = result, []
    def find_one(self, query, **kwargs): self.calls.append((query, kwargs)); return self.result

def test_explicit_collection_and_session_are_forwarded():
    collection = Collection(None); session = object()
    assert BillingRegistry().get_platform_invoice("tenant-a", "invoice-a", collection=collection, session=session) is None
    assert collection.calls == [({"$and": [{"$or": [{"tenant_id": "tenant-a"}, {"tenantId": "tenant-a"}]}, {"$or": [{"invoice_id": "invoice-a"}, {"invoiceId": "invoice-a"}]}]}, {"session": session})]

def test_omitted_session_is_not_forwarded():
    collection = Collection(None)
    BillingRegistry().get_platform_invoice("tenant-a", "invoice-a", collection=collection)
    assert collection.calls[0][1] == {}

def test_missing_invoice_preserves_none_result():
    assert BillingRegistry().get_platform_invoice("tenant-a", "missing", collection=Collection(None)) is None

def test_import_and_contract_propositions():
    source = inspect.getsource(BillingRegistry.get_platform_invoice)
    assert billing_module.BillingRegistry is BillingRegistry
    assert "collection" in source and "session=session" in source
    assert "tenant_id" in source and "invoice_id" in source
    assert "PlatformInvoice.from_dict" in source
    assert "platform_invoices_coll" in source

def test_lookup_failure_is_not_swallowed():
    class Failing(Collection):
        def find_one(self, query, **kwargs): raise RuntimeError("mongo failure")
    try:
        BillingRegistry().get_platform_invoice("tenant-a", "invoice-a", collection=Failing())
    except Exception as error:
        assert "mongo failure" in str(error)
    else:
        raise AssertionError("Mongo failure was swallowed")

# ARTIFACT: test_billing_registry.py
# VERSION: v1.0.0-BILLING-REGISTRY-LOOKUP-CERT
# AUTHORITY BOUNDARY: certification only; no execution authority
# TENANT POSTURE: exact tenant and invoice scope
# FAIL-CLOSED POSTURE: lookup failures remain production-owned
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
