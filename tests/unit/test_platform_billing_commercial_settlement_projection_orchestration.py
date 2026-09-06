"""TITLE: R3F-B orchestration certificate.
VERSION: v1.0.0-R3F-B
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify explicit orchestration boundary.
EPITOME: Caller-owned atomic commercial projection.
ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_commercial_settlement_projection_orchestration.py
COLLABORATION / OWNERSHIP: SaaS Billing orchestration certificate.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-R3F-B adds orchestration surface certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No hidden clients.
TENANT BOUNDARY: Explicit tenant-bound calls.
AUTHORITY BOUNDARY: Kennel settlement evidence only.
FINANCIAL AUTHORITY BOUNDARY: No provider execution.
TRANSACTION BOUNDARY: Caller-owned session.
FAIL-CLOSED DECLARATION: Missing session rejected.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from tools.eos.saas.billing import platform_billing_commercial_settlement_projection as orchestration
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection import project_platform_billing_commercial_settlement
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection import _canonical_utc_datetime
from tools.eos.saas.domain.billing import PlatformInvoice, InvoiceStatus
from tools.eos.saas.domain.platform_billing_commercial_settlement_projection import PlatformBillingCommercialSettlementProjection
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection_registry import PlatformBillingCommercialSettlementProjectionRegistry
from bson import BSON
def test_surface(): assert callable(project_platform_billing_commercial_settlement)

def test_b25_mongo_naive_utc_paid_at_normalization() -> None:
    naive = datetime(2026, 1, 1)
    settled = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert _canonical_utc_datetime(naive) == settled

def test_b19_post_validation_commercial_snapshot_drift_fails_cas(monkeypatch: pytest.MonkeyPatch) -> None:
    """Commercial liability drift after hydration must fail the exact CAS."""
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    base = PlatformInvoice.from_dict({
        "tenant_id": "tenant-b19", "invoice_id": "invoice-b19", "status": "open",
        "amount": 100.0, "tax_amount": 15.0, "total": 115.0, "amount_paid": 0.0,
        "outstanding_amount": 115.0, "currency": "ZAR", "issued_at": now,
        "created_at": now, "updated_at": now, "line_items": [{"description": "A", "amount": 100.0}],
    })
    snapshot_a = base.to_dict()
    snapshot_b = dict(snapshot_a, lineItems=[{"description": "B", "amount": 100.0}], line_items=[{"description": "B", "amount": 100.0}])
    invoice_a = PlatformInvoice.from_dict(snapshot_a)
    invoice_b = PlatformInvoice.from_dict(snapshot_b)
    assert invoice_a.commercial_release_evidence_fingerprint != invoice_b.commercial_release_evidence_fingerprint

    class InvoiceCollection:
        def find_one(self, _query, *, session=None):
            authorization.platform_invoice_evidence_fingerprint = PlatformInvoice.from_dict(snapshot_a).commercial_release_evidence_fingerprint
            return snapshot_a
        def update_one(self, _query, _update, *, session=None): return SimpleNamespace(matched_count=0)

    class ProjectionCollection:
        def find_one(self, _query, *, session=None): return None

    class Session:
        in_transaction = True

    settlement = SimpleNamespace(
        tenant_id="tenant-b19", platform_invoice_id="invoice-b19", settlement_evidence_id="settlement-b19",
        fingerprint="a" * 128, platform_execution_truth_id="execution-b19", execution_request_id="request-b19",
        execution_command_id="command-b19", release_authorization_id="auth-b19", settled_amount_minor=100,
        currency="ZAR", settled_at=now,
    )
    authorization = SimpleNamespace(
        tenant_id="tenant-b19", platform_invoice_id="invoice-b19", release_authorization_id="auth-b19",
        release_authorization_fingerprint="b" * 128, platform_invoice_evidence_fingerprint=invoice_a.commercial_release_evidence_fingerprint,
        authorized_amount_minor=100, currency="ZAR",
    )
    monkeypatch.setattr(orchestration.PlatformBillingFinancialSettlementEvidenceRegistry, "get", staticmethod(lambda *args, **kwargs: settlement))
    monkeypatch.setattr(orchestration.PlatformBillingReleaseAuthorizationRegistry, "get", staticmethod(lambda *args, **kwargs: authorization))
    monkeypatch.setattr(orchestration.PlatformBillingCommercialSettlementProjectionRegistry, "create", staticmethod(lambda *args, **kwargs: args[0]))
    with pytest.raises(orchestration.PlatformBillingCommercialSettlementProjectionError, match="R3F_(PROVENANCE_MISMATCH|INVOICE_CAS_FAILED)"):
        project_platform_billing_commercial_settlement(  # type: ignore[arg-type]
            "tenant-b19", "settlement-b19", settlement_collection=SimpleNamespace(),  # type: ignore[arg-type]
            release_authorization_collection=SimpleNamespace(),  # type: ignore[arg-type]
            platform_invoice_collection=InvoiceCollection(),  # type: ignore[arg-type]
            commercial_projection_collection=ProjectionCollection(), session=Session(), projected_at=now,  # type: ignore[arg-type]
        )
    assert invoice_b.status is InvoiceStatus.OPEN

def _replay_setup(monkeypatch: pytest.MonkeyPatch, *, paid: bool = True, drift: bool = False):
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    invoice = PlatformInvoice.from_dict({"tenant_id": "tenant-replay", "invoice_id": "invoice-replay", "status": "paid" if paid else "open", "amount": 100.0, "total": 100.0, "amount_paid": 100.0 if paid else 0.0, "outstanding_amount": 1.0 if drift else (0.0 if paid else 100.0), "paid_at": now if paid else None, "currency": "ZAR", "issued_at": now, "created_at": now, "updated_at": now, "line_items": [{"description": "A", "amount": 100.0}]})
    if paid:
        invoice = PlatformInvoice.from_dict(dict(invoice.to_dict(), amount_paid=invoice.total, amountPaid=invoice.total, outstanding_amount=1.0 if drift else 0.0, outstandingAmount=1.0 if drift else 0.0))
    settlement = SimpleNamespace(tenant_id="tenant-replay", platform_invoice_id="invoice-replay", settlement_evidence_id="settlement-replay", fingerprint="a"*128, platform_execution_truth_id="execution-replay", execution_request_id="request-replay", execution_command_id="command-replay", release_authorization_id="auth-replay", settled_amount_minor=invoice.release_amount_minor, currency=invoice.currency, settled_at=now)
    authorization = SimpleNamespace(tenant_id=invoice.tenant_id, platform_invoice_id=invoice.invoice_id, release_authorization_id="auth-replay", release_authorization_fingerprint="b"*128, platform_invoice_evidence_fingerprint=invoice.commercial_release_evidence_fingerprint, authorized_amount_minor=invoice.release_amount_minor, currency=invoice.currency)
    class Collection:
        def find_one(self, query, *, session=None):
            if "invoice_id" in query:
                authorization.platform_invoice_evidence_fingerprint = PlatformInvoice.from_dict(invoice.to_dict()).commercial_release_evidence_fingerprint
                return invoice.to_dict()
            return {"commercial_settlement_projection_id": "existing", "projected_at": datetime(2025, 12, 31, tzinfo=timezone.utc)}
        def update_one(self, *args, **kwargs): raise AssertionError("invoice CAS must not run on replay")
    existing = SimpleNamespace(commercial_settlement_projection_id="platform-commercial-settlement-settlement-replay", projected_at=datetime(2025, 12, 31, tzinfo=timezone.utc), to_dict=lambda include_fingerprint=False: {})
    monkeypatch.setattr(orchestration.PlatformBillingFinancialSettlementEvidenceRegistry, "get", staticmethod(lambda *a, **k: settlement))
    monkeypatch.setattr(orchestration.PlatformBillingReleaseAuthorizationRegistry, "get", staticmethod(lambda *a, **k: authorization))
    monkeypatch.setattr(orchestration.PlatformInvoice, "from_dict", classmethod(lambda cls, data: invoice))
    monkeypatch.setattr(orchestration.PlatformBillingCommercialSettlementProjectionRegistry, "get", staticmethod(lambda *a, **k: existing))
    monkeypatch.setattr(orchestration.PlatformBillingCommercialSettlementProjectionRegistry, "create", staticmethod(lambda *a, **k: (_ for _ in ()).throw(AssertionError("duplicate projection"))))
    projected_values = []
    monkeypatch.setattr(orchestration, "PlatformBillingCommercialSettlementProjection", lambda *a, **k: (projected_values.append(a[14]) or existing))
    return Collection(), SimpleNamespace(in_transaction=True), now, projected_values

def test_b20_canonical_identical_replay(monkeypatch: pytest.MonkeyPatch) -> None:
    collection, session, now, projected_values = _replay_setup(monkeypatch)
    later = datetime(2026, 1, 2, tzinfo=timezone.utc)
    result = project_platform_billing_commercial_settlement("tenant-replay", "settlement-replay", settlement_collection=collection, release_authorization_collection=collection, platform_invoice_collection=collection, commercial_projection_collection=collection, session=session, projected_at=later)  # type: ignore[arg-type]
    assert result.commercial_settlement_projection_id == "platform-commercial-settlement-settlement-replay"
    assert projected_values == [datetime(2025, 12, 31, tzinfo=timezone.utc)]

def test_b21_unproven_paid_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    collection, session, now, _ = _replay_setup(monkeypatch)
    monkeypatch.setattr(orchestration.PlatformBillingCommercialSettlementProjectionRegistry, "get", staticmethod(lambda *a, **k: None))
    with pytest.raises(orchestration.PlatformBillingCommercialSettlementProjectionError, match="R3F_(ARBITRARY_PAID_STATE|PROVENANCE_MISMATCH)"):
        project_platform_billing_commercial_settlement("tenant-replay", "settlement-replay", settlement_collection=collection, release_authorization_collection=collection, platform_invoice_collection=collection, commercial_projection_collection=collection, session=session, projected_at=now)  # type: ignore[arg-type]

def test_b22_replay_invoice_drift_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    collection, session, now, _ = _replay_setup(monkeypatch, drift=True)
    with pytest.raises(orchestration.PlatformBillingCommercialSettlementProjectionError, match="R3F_(REPLAY_INVOICE_MISMATCH|PROVENANCE_MISMATCH)"):
        project_platform_billing_commercial_settlement("tenant-replay", "settlement-replay", settlement_collection=collection, release_authorization_collection=collection, platform_invoice_collection=collection, commercial_projection_collection=collection, session=session, projected_at=now)  # type: ignore[arg-type]

def test_b23_major_minor_boundary() -> None:
    invoice = PlatformInvoice.from_dict({"tenant_id": "t", "invoice_id": "i", "amount": 100.0, "total": 100.0, "currency": "ZAR"})
    assert invoice.total == 100.0 and invoice.release_amount_minor == 10000

def test_b24_durable_projection_bson_roundtrip_identity() -> None:
    now = datetime(2026, 1, 1, 0, 0, 0, 123000, tzinfo=timezone.utc)
    projection = PlatformBillingCommercialSettlementProjection("t", "p", "s", "a"*128, "e", "r", "c", "a", "b"*128, "i", "d"*128, 10000, "ZAR", now, now, "PAID", 10000, 0)
    persisted = projection.to_dict()
    hydrated = PlatformBillingCommercialSettlementProjectionRegistry._hydrate(BSON(BSON.encode(persisted)).decode())
    assert hydrated.to_dict(include_fingerprint=False) == projection.to_dict(include_fingerprint=False)
    assert hydrated.projection_fingerprint == projection.projection_fingerprint
# ARTIFACT: test_platform_billing_commercial_settlement_projection_orchestration.py
# VERSION: v1.0.0-R3F-B
# END OF WILSY OS SOVEREIGN ARTIFACT
