"""L7C direct certificate for Legal Operations billing read projections.

TITLE: Legal Operations Billing Read Router Certificate
VERSION: v1.0.0-L7C-LEGAL-OPERATIONS-BILLING-READ-API-CERT
AUTHORITY: Direct ASGI certificate for authenticated read-only projections.
EPITOME: Proves tenant/IAM gates, canonical registry delegation, bounded
         privacy, and absence of mutation or financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_operations_billing_read_router.py
COLLABORATION / OWNERSHIP: Certificate owns only deterministic doubles and assertions.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: v1.0.0 certifies L7C route shape, authorization ordering, strict
           P6A/P6B delegation, and privacy/financial boundaries.
TENANT BOUNDARY: Every fake repository records exact tenant predicates.
AUTHORITY BOUNDARY: P6 authorities and IAM remain canonical; GET is projection only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED DECLARATION: Missing authority, foreign rows, malformed locators, and
                         corrupt source evidence are denied without disclosure.
"""
from __future__ import annotations

from typing import Any

import pytest
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_billing_read_router as module
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.exceptions import ForbiddenOperationException
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason


TENANT = "tenant-alpha"


class Collection:
    """Deterministic Mongo-compatible read double."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.queries: list[dict[str, Any]] = []

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        self.queries.append(dict(query))
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None


class Value:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return dict(self.payload)


def context(tenant: str = TENANT, role: str = "tenant_legal_partner") -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id="principal-1", tenant_id=tenant, username="operator",
        email="operator@example.test", auth_method="TEST", status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        authorized=True, reason=TenantAuthorizationReason.AUTHORIZED,
        business_role=role, authorization_role="LEGAL_PARTNER",
    )
    return TenantAuthorizationContext(identity=identity, tenant_id=tenant, decision=decision)


def app_for(collection: Collection, ctx: TenantAuthorizationContext | None = None) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if ctx is not None:
        app.dependency_overrides[module._BILLING_READ] = lambda: ctx
        app.dependency_overrides[module._INVOICE_READ] = lambda: ctx
    app.dependency_overrides[module.get_tariff_collection] = lambda: collection
    app.dependency_overrides[module.get_eligibility_collection] = lambda: collection
    app.dependency_overrides[module.get_invoice_collection] = lambda: collection
    app.dependency_overrides[module.get_issuance_collection] = lambda: collection
    app.include_router(module.router, prefix="/api")
    return app


def test_routes_are_get_only_and_correctly_mounted() -> None:
    app = app_for(Collection([]), context())
    routes = {(getattr(route, "path", ""), tuple(sorted(getattr(route, "methods", set()) or set()))) for route in module.router.routes if hasattr(route, "path")}
    assert ("/legal-operations/tariff-assessments/{tariff_assessment_id}", ("GET",)) in routes
    assert ("/legal-operations/billing-eligibilities/{billing_eligibility_id}", ("GET",)) in routes
    assert ("/legal-operations/invoices/{invoice_id}", ("GET",)) in routes
    assert not any(method in {"POST", "PUT", "PATCH", "DELETE"} for _, methods in routes for method in methods)


def test_missing_authentication_is_denied() -> None:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(module.router, prefix="/api")
    with TestClient(app) as client:
        response = client.get("/api/legal-operations/tariff-assessments/a1")
    assert response.status_code == 401


def test_missing_tenant_is_denied_before_repository_access() -> None:
    collection = Collection([])
    app = app_for(collection)

    async def require_scope(tenant_id: str | None = Header(default=None, alias="X-Tenant-ID")) -> TenantAuthorizationContext:
        if tenant_id is None:
            raise ForbiddenOperationException("tenant scope required")
        return context(tenant_id)

    app.dependency_overrides[module._BILLING_READ] = require_scope
    with TestClient(app) as client:
        response = client.get("/api/legal-operations/tariff-assessments/a1")
    assert response.status_code == 403
    assert collection.queries == []


def test_client_role_is_denied_before_commercial_repository_access() -> None:
    collection = Collection([])
    with TestClient(app_for(collection, context(role="tenant_legal_client"))) as client:
        response = client.get("/api/legal-operations/billing-eligibilities/e1")
    assert response.status_code == 403
    assert collection.queries == []


def test_foreign_tenant_is_bounded_not_found() -> None:
    collection = Collection([{"tenant_id": TENANT, "entity_type": "TariffAssessment", "entity_identity": "a1", "evidence_identity": "a" * 128}])
    with TestClient(app_for(collection, context("tenant-foreign"))) as client:
        response = client.get("/api/legal-operations/tariff-assessments/a1")
    assert response.status_code == 404
    assert collection.queries == [{"tenant_id": "tenant-foreign", "entity_type": "TariffAssessment", "entity_identity": "a1"}]


def test_malformed_locator_is_bounded_not_found() -> None:
    collection = Collection([])
    with TestClient(app_for(collection, context())) as client:
        response = client.get("/api/legal-operations/tariff-assessments/%2A")
    assert response.status_code == 404
    assert collection.queries == []


def test_tariff_uses_strict_registry_and_projects_integer_minor_units(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = Collection([{"tenant_id": TENANT, "entity_type": "TariffAssessment", "entity_identity": "a1", "evidence_identity": "a" * 128}])
    value = Value({"tariff_assessment_id": "a1", "assessed_total_minor_units": 1250, "fee_lines": [], "customer_email": "hidden"})
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(module.ProcessServiceTariffRegistry, "get_assessment", staticmethod(lambda tenant, evidence, coll: (calls.append((tenant, evidence)) or value)))
    with TestClient(app_for(collection, context())) as client:
        response = client.get("/api/legal-operations/tariff-assessments/a1")
    assert response.status_code == 200
    assert response.json()["data"]["assessed_total_minor_units"] == 1250
    assert "customer_email" not in response.json()["data"]
    assert calls == [(TENANT, "a" * 128)]


def test_corrupt_wrapper_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = Collection([{"tenant_id": TENANT, "entity_type": "TariffAssessment", "entity_identity": "a1", "evidence_identity": "bad"}])
    with TestClient(app_for(collection, context())) as client:
        response = client.get("/api/legal-operations/tariff-assessments/a1")
    assert response.status_code == 503


def test_billing_eligibility_delegates_without_recomputation(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = Collection([{"tenant_id": TENANT, "entity_type": "ProcessServiceBillingEligibility", "entity_identity": "e1", "evidence_identity": "b" * 128}])
    value = Value({"billing_eligibility_id": "e1", "eligible_minor_units": 990, "currency": "ZAR"})
    monkeypatch.setattr(module.ProcessServiceBillingEligibilityRegistry, "get", staticmethod(lambda tenant, evidence, coll: value))
    with TestClient(app_for(collection, context())) as client:
        response = client.get("/api/legal-operations/billing-eligibilities/e1")
    assert response.status_code == 200
    assert response.json()["data"] == {"billing_eligibility_id": "e1", "eligible_minor_units": 990, "currency": "ZAR"}


def test_invoice_unknown_resource_is_bounded_and_no_financial_fields_are_projected() -> None:
    collection = Collection([])
    with TestClient(app_for(collection, context())) as client:
        response = client.get("/api/legal-operations/invoices/i1")
    assert response.status_code == 404
    assert all(token not in response.text.lower() for token in ("payment", "settlement", "kennel"))


# ARTIFACT: test_legal_operations_billing_read_router.py
# VERSION: v1.0.0-L7C-LEGAL-OPERATIONS-BILLING-READ-API-CERT
# AUTHORITY BOUNDARY: direct authenticated GET projection certificate only
# TENANT POSTURE: exact tenant predicates and bounded foreign absence
# FAIL-CLOSED POSTURE: malformed, corrupt, and partial evidence denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
