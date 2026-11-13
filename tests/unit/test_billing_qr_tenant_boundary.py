"""WILSY OS authenticated invoice QR and audit boundary certificate.

TITLE: Billing QR Tenant Boundary Tests
VERSION: v1.0.3-EXACT-CLIENT-INVOICE-SOURCE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies legacy QR signing and validation are authenticated, tenant
         scoped, read-only, and compatible with the historical signed payload.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_qr_tenant_boundary.py
COLLABORATION / OWNERSHIP: Billing router, legacy QR contract, audit reads, and proof UI.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.3-EXACT-CLIENT-INVOICE-SOURCE-CERT covers conflicting ownership
           aliases, required persisted currency, stable trace fallback, and
           persisted identity mismatch.
           v1.0.2-AUTHENTICATION-DENIAL-CERT imports pytest and certifies the
           unauthenticated route raises before either invoice collection is queried.
           v1.0.1-UNAUTHENTICATED-DENIAL-EVIDENCE certifies issue/verify routing,
           exact tenant selectors, tamper denial, hidden cross-tenant absence,
           audit reads, and deny-only integrity-control writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ECT Act section 15.
SECURITY / PRIVACY POSTURE: Synthetic invoice records and non-production key only.
TENANT BOUNDARY: Every invoice/audit read uses injected canonical authorization scope.
AUTHORITY BOUNDARY: Test dependency injection supplies evidence context only; no IAM grant is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
"""
from __future__ import annotations

import time
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tools.eos.api.exceptions import UnauthorizedAccessException

from tools.eos.api import billing_router as module
from tools.eos.saas.billing.invoice_qr_legacy_contract import build_legacy_invoice_qr_payload


_TEST_SECRET = "billing-router-qr-test-secret-with-32-bytes"
_TENANT = "TENANT-OWNER"
_FOREIGN = "TENANT-FOREIGN"


def _matches_query(document: dict[str, Any], query: dict[str, Any]) -> bool:
    """Evaluate the bounded Mongo selector subset used by the QR route tests."""
    for field, expected in query.items():
        if field == "$and":
            if not all(_matches_query(document, clause) for clause in expected):
                return False
            continue
        if field == "$or":
            if not any(_matches_query(document, clause) for clause in expected):
                return False
            continue
        if isinstance(expected, dict) and "$exists" in expected:
            if (field in document) is not expected["$exists"]:
                return False
        elif expected is None:
            if field in document and document[field] is not None:
                return False
        elif document.get(field) != expected:
            return False
    return True


class _Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, *_args: Any, **_kwargs: Any) -> "_Cursor":
        return self

    def limit(self, _limit: int) -> "_Cursor":
        return self

    def __iter__(self):
        return iter(self.rows)


class _Collection:
    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = documents or []
        self.queries: list[dict[str, Any]] = []
        self.projections: list[dict[str, Any] | None] = []
        self.updates = 0
        self.inserts = 0

    def find_one(self, query: dict[str, Any], projection: dict[str, Any] | None = None):
        self.queries.append(query)
        self.projections.append(projection)
        for document in self.documents:
            if _matches_query(document, query):
                return document
        return None

    def find(self, query: dict[str, Any], projection: dict[str, Any] | None = None):
        self.queries.append(query)
        self.projections.append(projection)
        tenant_id = query.get("tenant_id")
        return _Cursor([row for row in self.documents if row.get("tenant_id") == tenant_id])

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.updates += 1

    def insert_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.inserts += 1


class _Database:
    def __init__(self, invoice: dict[str, Any] | None = None) -> None:
        self.collections = {
            "platform_invoices": _Collection(),
            "client_invoices": _Collection([invoice] if invoice else []),
            "billing_audit_events": _Collection(
                [{"tenant_id": _TENANT, "event_type": "BILLING_PROOF_REFERENCE_CHECKED"}]
            ),
            "billing_integrity_controls": _Collection(),
        }

    def __getitem__(self, name: str) -> _Collection:
        return self.collections[name]


def _invoice(tenant_id: str = _TENANT) -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "invoice_id": "INV-QR-001",
        "trace_id": "INV-QR-001",
        "total_amount": 1250.5,
        "currency": "ZAR",
        "proof_hash": "A" * 128,
    }


def _client(monkeypatch, database: _Database, *, authorize: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(module.router, prefix="/api")
    app.include_router(module.qr_router, prefix="/api")
    monkeypatch.setattr(module, "_require_db", lambda: database)
    if authorize:
        app.dependency_overrides[
            module._BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
        ] = lambda: SimpleNamespace(tenant_id=_TENANT)
    return TestClient(app)


def test_issue_and_verify_legacy_qr_use_authenticated_persisted_invoice(monkeypatch) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    monkeypatch.setenv("QR_VERIFICATION_BASE_URL", "https://wilsy.example/api/qr/verify")
    database = _Database(_invoice())
    client = _client(monkeypatch, database)

    issued = client.get("/api/billing/invoices/INV-QR-001/qr")
    assert issued.status_code == 200
    issued_body = issued.json()
    assert issued_body["persisted"] is False
    assert issued_body["payload"]["tenantId"] == _TENANT
    assert issued_body["verificationUrl"].startswith("https://wilsy.example/api/qr/verify/")
    assert database.collections["client_invoices"].updates == 0
    assert database.collections["client_invoices"].inserts == 0
    assert not database.collections["platform_invoices"].queries

    verified = client.get(f"/api/qr/verify/{issued_body['encodedPayload']}")
    assert verified.status_code == 200
    result = verified.json()
    assert result["valid"] is True
    assert result["verificationMode"] == "LEGACY_SIGNED_QR_PERSISTED_INVOICE_MATCH"
    assert result["tenantId"] == _TENANT
    query = database.collections["client_invoices"].queries[-1]
    assert _TENANT in repr(query)
    assert _FOREIGN not in repr(query)


def test_qr_source_rejects_conflicting_tenant_ownership_aliases(monkeypatch) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    monkeypatch.setenv("QR_VERIFICATION_BASE_URL", "https://wilsy.example/api/qr/verify")
    invoice = _invoice()
    invoice["recipientTenantId"] = _FOREIGN
    database = _Database(invoice)
    client = _client(monkeypatch, database)

    response = client.get("/api/billing/invoices/INV-QR-001/qr")

    assert response.status_code == 404
    assert response.json()["detail"] == "BILLING_QR_INVOICE_NOT_FOUND"
    assert not database.collections["platform_invoices"].queries


def test_qr_issuer_fails_closed_when_persisted_currency_is_missing(monkeypatch) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    monkeypatch.setenv("QR_VERIFICATION_BASE_URL", "https://wilsy.example/api/qr/verify")
    invoice = _invoice()
    del invoice["currency"]
    client = _client(monkeypatch, _Database(invoice))

    response = client.get("/api/billing/invoices/INV-QR-001/qr")

    assert response.status_code == 409
    assert response.json()["detail"] == "QR_SOURCE_FIELDS_UNAVAILABLE"


def test_qr_issuer_uses_stable_invoice_identity_when_legacy_trace_is_absent(
    monkeypatch,
) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    monkeypatch.setenv("QR_VERIFICATION_BASE_URL", "https://wilsy.example/api/qr/verify")
    invoice = _invoice()
    del invoice["trace_id"]
    client = _client(monkeypatch, _Database(invoice))

    response = client.get("/api/billing/invoices/INV-QR-001/qr")

    assert response.status_code == 200
    assert response.json()["payload"]["traceId"] == "INV-QR-001"


def test_qr_issuer_rejects_conflicting_persisted_trace_aliases(monkeypatch) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    monkeypatch.setenv("QR_VERIFICATION_BASE_URL", "https://wilsy.example/api/qr/verify")
    invoice = _invoice()
    invoice["traceId"] = "TRACE-CONFLICT"
    client = _client(monkeypatch, _Database(invoice))

    response = client.get("/api/billing/invoices/INV-QR-001/qr")

    assert response.status_code == 409
    assert response.json()["detail"] == "QR_SOURCE_FIELDS_UNAVAILABLE"


def test_signed_qr_requires_persisted_trace_identity_and_currency_match(monkeypatch) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    database = _Database(_invoice())
    client = _client(monkeypatch, database)
    now_ms = time.time_ns() // 1_000_000
    wrong_trace = build_legacy_invoice_qr_payload(
        {
            "invoiceId": "INV-QR-001",
            "tenantId": _TENANT,
            "amount": 1250.5,
            "currency": "ZAR",
            "traceId": "TRACE-OTHER",
        },
        secret=_TEST_SECRET,
        base_url="https://wilsy.example/api/qr/verify",
        now_ms=now_ms,
    )

    trace_response = client.get(f"/api/qr/verify/{wrong_trace.encoded_payload}")

    assert trace_response.status_code == 400
    assert trace_response.json()["detail"] == "BILLING_QR_PERSISTED_IDENTITY_MISMATCH"

    wrong_currency = build_legacy_invoice_qr_payload(
        {
            "invoiceId": "INV-QR-001",
            "tenantId": _TENANT,
            "amount": 1250.5,
            "currency": "GBP",
            "traceId": "INV-QR-001",
        },
        secret=_TEST_SECRET,
        base_url="https://wilsy.example/api/qr/verify",
        now_ms=now_ms,
    )
    currency_response = client.get(
        f"/api/qr/verify/{wrong_currency.encoded_payload}"
    )

    assert currency_response.status_code == 400
    assert currency_response.json()["detail"] == "BILLING_QR_CURRENCY_MISMATCH"


def test_historical_payload_with_foreign_tenant_is_hidden_before_database_lookup(monkeypatch) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    database = _Database(_invoice(_FOREIGN))
    client = _client(monkeypatch, database)
    now_ms = time.time_ns() // 1_000_000
    foreign = build_legacy_invoice_qr_payload(
        {
            "invoiceId": "INV-QR-001",
            "tenantId": _FOREIGN,
            "amount": 1250.5,
            "currency": "ZAR",
            "traceId": "INV-QR-001",
            "sealHash": "A" * 128,
        },
        secret=_TEST_SECRET,
        base_url="https://wilsy.example/api/qr/verify",
        now_ms=now_ms,
    )

    response = client.get(f"/api/qr/verify/{foreign.encoded_payload}")

    assert response.status_code == 404
    assert response.json()["detail"] == "BILLING_QR_INVOICE_NOT_FOUND"
    assert not database.collections["platform_invoices"].queries
    assert not database.collections["client_invoices"].queries


def test_tampered_signed_qr_fails_before_invoice_lookup(monkeypatch) -> None:
    monkeypatch.setenv("QR_SIGNING_SECRET", _TEST_SECRET)
    database = _Database(_invoice())
    client = _client(monkeypatch, database)
    now_ms = time.time_ns() // 1_000_000
    qr = build_legacy_invoice_qr_payload(
        {
            "invoiceId": "INV-QR-001",
            "tenantId": _TENANT,
            "amount": 1250.5,
            "currency": "ZAR",
            "traceId": "INV-QR-001",
            "sealHash": "A" * 128,
        },
        secret=_TEST_SECRET,
        base_url="https://wilsy.example/api/qr/verify",
        now_ms=now_ms,
    )
    payload_part, signature = qr.encoded_payload.split(".", 1)
    replacement = "0" if signature[-1] != "0" else "1"

    response = client.get(f"/api/qr/verify/{payload_part}.{signature[:-1]}{replacement}")

    assert response.status_code == 400
    assert response.json()["detail"] == "QR_SIGNATURE_MISMATCH"
    assert not database.collections["platform_invoices"].queries
    assert not database.collections["client_invoices"].queries


def test_audit_reads_are_authenticated_tenant_scoped_and_integrity_is_read_only(monkeypatch) -> None:
    database = _Database()
    client = _client(monkeypatch, database)

    events = client.get("/api/billing/audit/events?limit=25")
    integrity = client.get("/api/billing/audit/integrity")
    denied_write = client.patch(
        "/api/billing/audit/integrity",
        json={"auto_renew": False},
    )

    assert events.status_code == 200
    assert events.json()[0]["tenant_id"] == _TENANT
    assert database.collections["billing_audit_events"].queries == [{"tenant_id": _TENANT}]
    assert integrity.status_code == 200
    assert integrity.json()["source"] == "EOS_DEFAULTS"
    assert database.collections["billing_integrity_controls"].queries == [
        {"tenant_id": _TENANT}
    ]
    assert denied_write.status_code == 403
    assert denied_write.json()["detail"] == "AUDIT_INTEGRITY_WRITE_AUTHORITY_UNAVAILABLE"
    assert database.collections["billing_integrity_controls"].updates == 0
    assert database.collections["billing_integrity_controls"].inserts == 0


def test_qr_route_requires_authentication_before_database_access(monkeypatch) -> None:
    database = _Database(_invoice())
    client = _client(monkeypatch, database, authorize=False)

    with pytest.raises(UnauthorizedAccessException, match="Missing authentication credentials"):
        client.get("/api/billing/invoices/INV-QR-001/qr")

    assert not database.collections["platform_invoices"].queries
    assert not database.collections["client_invoices"].queries


# ARTIFACT: Billing QR Tenant Boundary Tests
# VERSION: v1.0.3-EXACT-CLIENT-INVOICE-SOURCE-CERT
# AUTHORITY BOUNDARY: Synthetic authorization contexts and invoices only.
# TENANT POSTURE: Foreign tenant invoice absence is non-disclosing.
# FAIL-CLOSED POSTURE: Missing authentication, invalid signatures, and denied writes fail before mutation.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
