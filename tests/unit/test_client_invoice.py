"""WILSY OS ClientInvoice Model-C commercial-evidence certificate.
TITLE: ClientInvoice Deterministic Commercial Evidence
VERSION: v1.1.0-M11-R8-R3B-P6E-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify deterministic ClientInvoice content evidence while preserving legacy proof correlation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_client_invoice.py
COLLABORATION / OWNERSHIP: ClientInvoice domain certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P6E-R1 adds the frozen Model-C evidence certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped invoice evidence; no provider or credential state.
TENANT BOUNDARY: Client invoice identity is tenant scoped.
AUTHORITY BOUNDARY: Commercial content integrity only; legacy proof remains correlation evidence.
FINANCIAL AUTHORITY BOUNDARY: No collection, execution, payment, or settlement authority.
TRANSACTION BOUNDARY: Unit-only deterministic domain certificate.
FAIL-CLOSED DECLARATION: Missing, malformed, or unsupported deterministic evidence never verifies.
"""
from dataclasses import replace
from datetime import datetime, timezone

import tools.eos.saas.domain.billing as billing_module
from tools.eos.saas.domain.billing import (
    ClientInvoice,
    InvoiceStatus,
    InvoiceType,
    LineItem,
    CLIENT_COMMERCIAL_EVIDENCE_VERSION,
)


def _invoice(**changes):
    value = ClientInvoice(
        tenant_id="tenant-a",
        invoice_id="client-a",
        customer_id="customer-a",
        customer_name="Customer A",
        customer_tax_id="TAX-A",
        customer_email="a@example.test",
        customer_phone="+27110000000",
        status=InvoiceStatus.OPEN,
        line_items=[LineItem("Service", 100.0, 2, 50.0, 0.15, 15.0, 0.0, "ZAR")],
        currency="ZAR",
        issued_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        due_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        payment_terms_days=30,
        billing_mode="CLIENT",
        order_number="ORDER-A",
        purchase_order="PO-A",
    )
    return replace(value, **changes) if changes else value


def test_client_invoice_type_is_distinct():
    assert ClientInvoice.invoice_type is InvoiceType.CLIENT


def test_legacy_objects_keep_evidence_fields_absent_on_construction_and_hydration():
    invoice = _invoice()
    assert invoice.commercial_evidence_fingerprint is None
    assert invoice.commercial_evidence_version is None
    hydrated = ClientInvoice.from_dict(invoice.to_dict())
    assert hydrated.commercial_evidence_fingerprint is None
    assert hydrated.commercial_evidence_version is None


def test_compute_is_deterministic_lowercase_sha3_512_without_clock(monkeypatch):
    invoice = _invoice()

    class ClockBomb:
        @classmethod
        def now(cls, *args, **kwargs):
            raise AssertionError("fresh clock used")

    monkeypatch.setattr(billing_module, "datetime", ClockBomb)
    first = invoice.compute_commercial_evidence_fingerprint()
    assert first == invoice.compute_commercial_evidence_fingerprint()
    assert len(first) == 128 and first == first.lower()


def test_version_is_committed_and_unknown_version_fails_closed():
    invoice = _invoice(commercial_evidence_version=CLIENT_COMMERCIAL_EVIDENCE_VERSION)
    valid = replace(invoice, commercial_evidence_fingerprint=invoice.compute_commercial_evidence_fingerprint())
    assert valid.verify_commercial_evidence() is True
    assert replace(valid, commercial_evidence_version="WILSY-CLIENT-INVOICE-COMMERCIAL-EVIDENCE/V2").verify_commercial_evidence() is False


def test_identity_and_commercial_changes_change_fingerprint():
    invoice = _invoice()
    baseline = invoice.compute_commercial_evidence_fingerprint()
    changes = {
        "tenant_id": "tenant-b", "invoice_id": "client-b", "invoice_type": InvoiceType.PLATFORM,
        "customer_id": "customer-b", "customer_name": "Customer B", "customer_tax_id": "TAX-B",
        "customer_email": "b@example.test", "customer_phone": "+27220000000", "currency": "USD",
        "amount": 101.0, "tax_amount": 16.0, "total": 117.0,
        "issued_at": datetime(2026, 9, 2, tzinfo=timezone.utc),
        "due_at": datetime(2026, 10, 2, tzinfo=timezone.utc), "payment_terms_days": 45,
        "seller_jurisdiction": "GB", "customer_jurisdiction": "US", "billing_mode": "CLIENT-REVISION",
        "order_number": "ORDER-B", "purchase_order": "PO-B",
    }
    for field_name, value in changes.items():
        changed = replace(invoice, **{field_name: value})
        if field_name in {"amount", "tax_amount", "total"}:
            changed = replace(invoice, line_items=[] , **{field_name: value})
        assert changed.compute_commercial_evidence_fingerprint() != baseline, field_name
    reordered = replace(invoice, line_items=invoice.line_items + [LineItem("Second", 5.0, 1, 5.0, 0.15, 0.75, 0.0, "ZAR")])
    reordered = replace(reordered, line_items=list(reversed(reordered.line_items)))
    assert reordered.compute_commercial_evidence_fingerprint() != baseline
    altered_line = replace(invoice, line_items=[LineItem("Different", 100.0, 2, 50.0, 0.15, 15.0, 0.0, "ZAR")])
    assert altered_line.compute_commercial_evidence_fingerprint() != baseline


def test_lifecycle_payment_metadata_and_legacy_proof_do_not_change_fingerprint():
    invoice = _invoice()
    baseline = invoice.compute_commercial_evidence_fingerprint()
    variants = (
        {"status": InvoiceStatus.PAID}, {"amount_paid": 20.0}, {"outstanding_amount": 95.0},
        {"paid_at": datetime(2026, 9, 3, tzinfo=timezone.utc)},
        {"void_at": datetime(2026, 9, 4, tzinfo=timezone.utc)},
        {"cancellation_reason": "administrative"}, {"updated_at": datetime(2026, 9, 5, tzinfo=timezone.utc)},
        {"metadata": {"trace": "changed"}}, {"proof_hash": "different-legacy-token"},
        {"line_items": [LineItem("Service", 100.0, 2, 50.0, 0.15, 15.0, 0.0, "ZAR", {"x": 1})]},
    )
    for changes in variants:
        assert replace(invoice, **changes).compute_commercial_evidence_fingerprint() == baseline


def test_verification_rejects_missing_malformed_or_tampered_evidence():
    invoice = _invoice(commercial_evidence_version=CLIENT_COMMERCIAL_EVIDENCE_VERSION)
    assert invoice.verify_commercial_evidence() is False
    fingerprint = invoice.compute_commercial_evidence_fingerprint()
    valid = replace(invoice, commercial_evidence_fingerprint=fingerprint)
    assert valid.verify_commercial_evidence() is True
    assert replace(valid, commercial_evidence_fingerprint="x").verify_commercial_evidence() is False
    assert replace(valid, customer_name="Tampered").verify_commercial_evidence() is False


def test_serialization_preserves_present_evidence_without_alias_fabrication():
    invoice = _invoice(commercial_evidence_version=CLIENT_COMMERCIAL_EVIDENCE_VERSION)
    value = replace(invoice, commercial_evidence_fingerprint=invoice.compute_commercial_evidence_fingerprint())
    payload = value.to_dict()
    assert payload["commercial_evidence_fingerprint"] == value.commercial_evidence_fingerprint
    assert payload["commercial_evidence_version"] == CLIENT_COMMERCIAL_EVIDENCE_VERSION
    hydrated = ClientInvoice.from_dict(payload)
    assert hydrated.commercial_evidence_fingerprint == value.commercial_evidence_fingerprint
    assert hydrated.commercial_evidence_version == CLIENT_COMMERCIAL_EVIDENCE_VERSION
    assert hydrated.verify_commercial_evidence() is True


def test_platform_invoice_semantics_remain_separate():
    from tools.eos.saas.domain.billing import PlatformInvoice
    platform = PlatformInvoice("tenant-a", "platform-a")
    assert not hasattr(platform, "commercial_evidence_fingerprint")
    assert platform.invoice_type is InvoiceType.PLATFORM


# ARTIFACT: test_client_invoice.py
# VERSION: v1.1.0-M11-R8-R3B-P6E-R1
# AUTHORITY BOUNDARY: deterministic ClientInvoice commercial evidence only.
# TENANT POSTURE: Tenant scoped.
# FAIL-CLOSED POSTURE: Missing, malformed, and unsupported evidence reject verification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
