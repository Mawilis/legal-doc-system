"""
TITLE: WILSY OS Billing Proof Reference Tenant Boundary Certificate
VERSION: v1.0.0-AUTHORIZED-SEAL-REFERENCE-VERIFY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies billing proof lookup and its audit event stay within the
         canonical TenantAuthorizationContext, ignoring caller tenant labels.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_invoice_proof_tenant_boundary.py
COLLABORATION / OWNERSHIP: Billing HTTP router, tenant authorization dependency,
                           Kernel database seam and proof display client.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.0-AUTHORIZED-SEAL-REFERENCE-VERIFY adds bounded route tests for
           valid, missing and malformed persisted SHA3-512 references.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: In-memory synthetic records only; no live DB.
TENANT BOUNDARY: Every lookup and audit event derives scope from the authorized
                 context, never from body tenant fields.
AUTHORITY BOUNDARY: Repository regression evidence only; no evidence is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api import billing_router as module


class _Collection:
    def __init__(self, match: dict[str, Any] | None = None) -> None:
        self.match = match
        self.queries: list[dict[str, Any]] = []
        self.inserted: list[dict[str, Any]] = []

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        self.queries.append(query)
        return self.match

    def insert_one(self, record: dict[str, Any]) -> None:
        self.inserted.append(record)


class _Database:
    def __init__(
        self,
        *,
        invoice_match: dict[str, Any] | None = None,
        audit_match: dict[str, Any] | None = None,
    ) -> None:
        self.collections = {
            "platform_invoices": _Collection(invoice_match),
            "client_invoices": _Collection(),
            "billing_audit_events": _Collection(audit_match),
        }

    def __getitem__(self, name: str) -> _Collection:
        return self.collections[name]


def _client(monkeypatch, database: _Database) -> TestClient:
    context = SimpleNamespace(tenant_id="TENANT-CANONICAL")
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[
        module._BILLING_FORENSIC_REFERENCE_VERIFY_AUTHORIZATION
    ] = lambda: context
    monkeypatch.setattr(module, "db", database)
    return TestClient(app)


def test_proof_reference_lookup_and_audit_ignore_caller_tenant(monkeypatch) -> None:
    database = _Database(invoice_match={"proof_hash": "a" * 128})
    client = _client(monkeypatch, database)

    response = client.post(
        "/billing/merkle/verify",
        json={
            "seal_hash": "a" * 128,
            "tenant_id": "TENANT-ATTACKER",
            "tenantId": "TENANT-ATTACKER",
        },
    )

    assert response.status_code == 200
    result = response.json()
    assert result["valid"] is True
    assert result["tenantId"] == "TENANT-CANONICAL"
    assert result["verificationMode"] == "PERSISTED_REFERENCE_MATCH"
    query = database.collections["platform_invoices"].queries[0]
    assert "TENANT-CANONICAL" in repr(query)
    assert "TENANT-ATTACKER" not in repr(query)
    event = database.collections["billing_audit_events"].inserted[0]
    assert event["tenant_id"] == "TENANT-CANONICAL"
    assert event["event_type"] == "BILLING_PROOF_REFERENCE_CHECKED"


def test_missing_reference_is_audited_only_in_the_authorized_tenant(monkeypatch) -> None:
    database = _Database()
    client = _client(monkeypatch, database)

    response = client.post(
        "/billing/merkle/verify",
        json={"proof_hash": "b" * 128, "tenantId": "TENANT-ATTACKER"},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["tenantId"] == "TENANT-CANONICAL"
    for collection in (
        database.collections["platform_invoices"],
        database.collections["client_invoices"],
        database.collections["billing_audit_events"],
    ):
        assert collection.queries
        assert all("TENANT-ATTACKER" not in repr(query) for query in collection.queries)
    assert database.collections["billing_audit_events"].inserted[0]["valid"] is False


def test_malformed_hash_fails_before_database_access(monkeypatch) -> None:
    database = _Database()
    client = _client(monkeypatch, database)

    response = client.post(
        "/billing/merkle/verify",
        json={"seal_hash": "not-a-sha3-512-reference"},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "BILLING_PROOF_HASH_INVALID"
    assert all(not collection.queries for collection in database.collections.values())
    assert all(not collection.inserted for collection in database.collections.values())


# ARTIFACT: WILSY OS Billing Proof Reference Tenant Boundary Certificate
# VERSION: v1.0.0-AUTHORIZED-SEAL-REFERENCE-VERIFY
# AUTHORITY BOUNDARY: deterministic repository regression evidence only
# TENANT POSTURE: caller-provided tenant labels are never accepted as scope
# FAIL-CLOSED POSTURE: malformed references fail before persistence
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
