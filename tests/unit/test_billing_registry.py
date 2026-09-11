"""WILSY OS BillingRegistry direct certificate.

TITLE: BillingRegistry Session-Aware Lookup Certificate
VERSION: v1.3.0-M11-R8-R3B-P6E-R1-CLIENT-EVIDENCE
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify tenant-scoped explicit collection and session forwarding.
EPITOME: Durable invoice lookup remains compatible while supporting trusted composition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_registry.py
COLLABORATION / OWNERSHIP: Python EOS billing certification.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.0.0 certifies explicit collection/session lookup semantics.
           v1.1.0 certifies ClientInvoice parity with the PlatformInvoice read context.
           v1.2.0 certifies strict raw ClientInvoice/PlatformInvoice reads.
           v1.3.0-M11-R8-R3B-P6E-R1 certifies deterministic ClientInvoice evidence persistence.
COMPLIANCE: POPIA section 19 | GDPR Article 32 | SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped opaque invoice references.
TENANT BOUNDARY: Tenant and invoice identifiers are queried together.
AUTHORITY BOUNDARY: Evidence only; no authorization or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
TRANSACTION BOUNDARY: Caller session is forwarded unchanged.
"""
from tools.eos.saas.billing.billing_registry import BillingRegistry
from tools.eos.saas.domain.billing import ClientInvoice, InvoiceStatus
import inspect
import tools.eos.saas.billing.billing_registry as billing_module

class Collection:
    def __init__(self, result=None): self.result, self.calls = result, []
    def find_one(self, query, **kwargs): self.calls.append((query, kwargs)); return self.result

    def insert_one(self, document):
        self.result = dict(document)
        return type("InsertResult", (), {"inserted_id": document.get("invoice_id")})()

    def update_one(self, query, update, **kwargs):
        return type("UpdateResult", (), {"matched_count": 1})()

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


def test_platform_raw_read_preserves_exact_document_and_session():
    raw = {
        "_id": "storage-platform",
        "tenant_id": "tenant-a",
        "invoice_id": "invoice-a",
        "status": "BROKEN",
        "currency": "zar",
        "unexpected": {"preserve": True},
    }
    collection = Collection(raw)
    session = object()
    assert BillingRegistry().get_platform_invoice_raw(
        "tenant-a", "invoice-a", collection=collection, session=session
    ) == raw
    assert collection.calls[0][0]["$and"][0]["$or"][0]["tenant_id"] == "tenant-a"
    assert collection.calls[0][0]["$and"][1]["$or"][0]["invoice_id"] == "invoice-a"
    assert collection.calls[0][1] == {"session": session}


def test_platform_raw_read_does_not_hydrate_or_generate(monkeypatch):
    raw = {"tenant_id": "tenant-a", "invoice_id": "invoice-a", "amount": "7.125"}
    collection = Collection(raw)
    monkeypatch.setattr(
        billing_module.PlatformInvoice,
        "from_dict",
        staticmethod(lambda _: (_ for _ in ()).throw(AssertionError("hydrated"))),
    )
    result = BillingRegistry().get_platform_invoice_raw(
        "tenant-a", "invoice-a", collection=collection
    )
    assert result is not None
    assert result == raw
    assert "status" not in result
    assert result["amount"] == "7.125"


def test_platform_raw_read_default_collection_and_not_found(monkeypatch):
    collection = Collection(None)
    monkeypatch.setattr(billing_module, "platform_invoices_coll", collection)
    assert BillingRegistry().get_platform_invoice_raw("tenant-a", "missing") is None
    assert collection.calls

def test_lookup_failure_is_not_swallowed():
    class Failing(Collection):
        def find_one(self, query, **kwargs): raise RuntimeError("mongo failure")
    try:
        BillingRegistry().get_platform_invoice("tenant-a", "invoice-a", collection=Failing())
    except Exception as error:
        assert "mongo failure" in str(error)
    else:
        raise AssertionError("Mongo failure was swallowed")

def test_client_explicit_collection_and_session_are_forwarded_unchanged():
    collection = Collection(None); session = object()
    assert BillingRegistry().get_client_invoice("tenant-a", "invoice-a", collection=collection, session=session) is None
    assert collection.calls == [({"$and": [{"$or": [{"tenant_id": "tenant-a"}, {"tenantId": "tenant-a"}]}, {"$or": [{"invoice_id": "invoice-a"}, {"invoiceId": "invoice-a"}]}]}, {"session": session})]

def test_client_omitted_session_preserves_default_call_shape():
    collection = Collection(None)
    BillingRegistry().get_client_invoice("tenant-a", "invoice-a", collection=collection)
    assert collection.calls[0][1] == {}

def test_client_lookup_is_tenant_scoped_and_hydrates_as_before():
    invoice = ClientInvoice.from_dict({
        "tenant_id": "tenant-a",
        "invoice_id": "invoice-a",
        "status": "open",
        "total": 10.0,
        "amount": 10.0,
        "outstanding_amount": 10.0,
    })
    collection = Collection(invoice.to_dict())
    hydrated = BillingRegistry().get_client_invoice("tenant-a", "invoice-a", collection=collection, session=object())
    assert hydrated == invoice
    assert collection.calls[0][0]["$and"][0]["$or"][0]["tenant_id"] == "tenant-a"
    assert collection.calls[0][0]["$and"][1]["$or"][0]["invoice_id"] == "invoice-a"

def test_client_missing_invoice_remains_none():
    assert BillingRegistry().get_client_invoice("tenant-a", "missing", collection=Collection(None)) is None

def test_client_default_collection_path_remains_compatible(monkeypatch):
    collection = Collection(None)
    monkeypatch.setattr(billing_module, "client_invoices_coll", collection)
    assert BillingRegistry().get_client_invoice("tenant-a", "invoice-a") is None
    assert collection.calls

def test_client_lookup_does_not_create_transaction_or_authority():
    class SessionGuard(Collection):
        def find_one(self, query, **kwargs):
            assert kwargs["session"] is session
            assert not any(name in kwargs for name in ("transaction", "commit", "abort"))
            return None
    session = object()
    assert BillingRegistry().get_client_invoice("tenant-a", "invoice-a", collection=SessionGuard(), session=session) is None


def test_client_raw_read_preserves_absent_and_malformed_fields():
    raw = {
        "_id": "storage-client",
        "tenantId": "tenant-a",
        "invoiceId": "invoice-a",
        "status": "not-a-status",
        "currency": "zar",
        "proof_hash": "malformed-proof",
        "amount": 7.125,
        "unknown_field": "observable",
    }
    collection = Collection(raw)
    result = BillingRegistry().get_client_invoice_raw(
        "tenant-a", "invoice-a", collection=collection, session=object()
    )
    assert result is not None
    assert result == raw
    assert "outstanding_amount" not in result
    assert result["status"] == "not-a-status"
    assert result["currency"] == "zar"
    assert result["amount"] == 7.125
    assert result["unknown_field"] == "observable"


def test_client_raw_read_does_not_call_from_dict(monkeypatch):
    raw = {"tenant_id": "tenant-a", "invoice_id": "invoice-a"}
    collection = Collection(raw)
    monkeypatch.setattr(
        billing_module.ClientInvoice,
        "from_dict",
        staticmethod(lambda _: (_ for _ in ()).throw(AssertionError("hydrated"))),
    )
    assert BillingRegistry().get_client_invoice_raw(
        "tenant-a", "invoice-a", collection=collection
    ) == raw


def test_client_raw_read_default_collection_and_not_found(monkeypatch):
    collection = Collection(None)
    monkeypatch.setattr(billing_module, "client_invoices_coll", collection)
    assert BillingRegistry().get_client_invoice_raw("tenant-a", "missing") is None
    assert collection.calls


def test_raw_reads_return_copies_and_forward_session_without_transactions():
    raw = {"tenant_id": "tenant-a", "invoice_id": "invoice-a"}
    client_collection = Collection(raw)
    platform_collection = Collection(raw)
    session = object()
    client_result = BillingRegistry().get_client_invoice_raw(
        "tenant-a", "invoice-a", collection=client_collection, session=session
    )
    platform_result = BillingRegistry().get_platform_invoice_raw(
        "tenant-a", "invoice-a", collection=platform_collection, session=session
    )
    assert client_result is not raw
    assert platform_result is not raw
    assert client_collection.calls[0][1] == {"session": session}
    assert platform_collection.calls[0][1] == {"session": session}


def test_client_create_persists_and_verifies_model_c_evidence(monkeypatch):
    collection = Collection(None)
    monkeypatch.setattr(billing_module, "client_invoices_coll", collection)
    invoice = BillingRegistry().create_client_invoice(
        "tenant-a", customer_id="customer-a", line_items=[{"description": "Service", "amount": 10.0}]
    )
    assert invoice.commercial_evidence_version == "WILSY-CLIENT-INVOICE-COMMERCIAL-EVIDENCE/V1"
    assert invoice.verify_commercial_evidence() is True
    assert collection.result is not None
    assert collection.result["commercial_evidence_fingerprint"] == invoice.commercial_evidence_fingerprint
    assert collection.result["commercial_evidence_version"] == invoice.commercial_evidence_version


def test_client_commercial_rewrite_is_fail_closed(monkeypatch):
    registry = BillingRegistry()
    for field, value in (("amount", 11.0), ("line_items", []), ("issued_at", "2026-09-02T00:00:00+00:00"), ("commercial_evidence_version", "V2")):
        try:
            registry.update_client_invoice("tenant-a", "invoice-a", {field: value})
        except ValueError as error:
            assert "CLIENT_INVOICE_COMMERCIAL_FIELD_REWRITE_FORBIDDEN" in str(error)
        else:
            raise AssertionError("commercial rewrite was accepted")

# ARTIFACT: test_billing_registry.py
# VERSION: v1.3.0-M11-R8-R3B-P6E-R1-CLIENT-EVIDENCE
# AUTHORITY BOUNDARY: certification only; no execution authority
# TENANT POSTURE: exact tenant and invoice scope
# FAIL-CLOSED POSTURE: lookup failures remain production-owned
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
