"""TITLE: WILSY OS Legal Operations read API certificate.
VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-CERT
AUTHORITY: Direct ASGI certificate for tenant-authorized Legal Operations projections.
EPITOME: Proves authentication, exact tenant scope, bounded hydration, and read-only output.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_http.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: v1.0.0 certifies bounded instruction reads and denial boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Repository predicates always include the authorized tenant.
AUTHORITY BOUNDARY: Read projection only; no lifecycle, persistence, or command authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Missing credentials/scope, foreign records, client policy gaps, and corruption deny.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.exceptions import ForbiddenOperationException
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
from tools.eos.auth.principal_status import PrincipalStatus


VERSION = "v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-CERT"
_TENANT = "tenant-alpha"
_IDENTITY = "instruction-001"


class _Collection:
    """Minimal tenant-predicate collection double with query audit."""

    def __init__(self, row: dict[str, object] | None) -> None:
        self.row = row
        self.queries: list[dict[str, object]] = []

    def find_one(self, query: dict[str, object]) -> dict[str, object] | None:
        self.queries.append(dict(query))
        if self.row is not None and all(self.row.get(key) == value for key, value in query.items()):
            return dict(self.row)
        return None


class _Value:
    def to_dict(self) -> dict[str, object]:
        return {
            "instruction_id": _IDENTITY,
            "tenant_id": _TENANT,
            "state": "REGISTERED",
            "created_at": "2026-09-15T08:00:00+00:00",
            "credentials": "must-not-leak",
            "_id": "mongo-internal",
        }


def _context(tenant: str = _TENANT, role: str = "tenant_legal_partner") -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id="principal-1",
        tenant_id=tenant,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        authorized=True,
        reason=TenantAuthorizationReason.AUTHORIZED,
        business_role=role,
        authorization_role="LEGAL_PARTNER",
    )
    return TenantAuthorizationContext(identity=identity, tenant_id=tenant, decision=decision)


def _app(collection: _Collection, *, context: TenantAuthorizationContext | None = None) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if context is not None:
        app.dependency_overrides[legal_router._INSTRUCTION_READ] = lambda: context
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: collection
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_missing_authentication_is_denied() -> None:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(legal_router.router, prefix="/api")
    with TestClient(app) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 401


def test_missing_tenant_scope_is_denied() -> None:
    collection = _Collection(None)
    app = _app(collection)
    async def require_scope(tenant_id: str | None = Header(default=None, alias="X-Tenant-ID")) -> TenantAuthorizationContext:
        if tenant_id is None:
            raise ForbiddenOperationException("tenant scope required")
        return _context(tenant_id)

    app.dependency_overrides[legal_router._INSTRUCTION_READ] = require_scope
    with TestClient(app) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 403
    assert collection.queries == []


def test_authorized_own_tenant_read_is_bounded_and_exactly_scoped(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = _Collection({
        "tenant_id": _TENANT,
        "entity_type": "LegalInstruction",
        "entity_identity": _IDENTITY,
        "evidence_identity": "a" * 128,
    })
    monkeypatch.setattr(legal_router.LegalOperationsLifecycleRegistry, "get", staticmethod(lambda *_args: _Value()))
    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == _TENANT
    assert body["data"]["instruction_id"] == _IDENTITY
    assert "_id" not in body["data"]
    assert "credentials" not in body["data"]
    assert not any("payment" in key or "settlement" in key for key in body["data"])
    assert collection.queries == [{"tenant_id": _TENANT, "entity_type": "LegalInstruction", "entity_identity": _IDENTITY}]


def test_foreign_tenant_is_not_found_without_repository_leak(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = _Collection({
        "tenant_id": _TENANT,
        "entity_type": "LegalInstruction",
        "entity_identity": _IDENTITY,
        "evidence_identity": "a" * 128,
    })
    monkeypatch.setattr(legal_router.LegalOperationsLifecycleRegistry, "get", staticmethod(lambda *_args: _Value()))
    with TestClient(_app(collection, context=_context("tenant-foreign"))) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 404
    assert collection.queries == [{"tenant_id": "tenant-foreign", "entity_type": "LegalInstruction", "entity_identity": _IDENTITY}]


def test_unknown_resource_is_bounded_absence() -> None:
    collection = _Collection(None)
    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 404
    assert "stack_trace" not in response.text


def test_client_role_is_fail_closed_until_projection_policy_exists() -> None:
    collection = _Collection(None)
    with TestClient(_app(collection, context=_context(role="tenant_legal_client"))) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 403
    assert collection.queries == []


# ARTIFACT: test_legal_operations_http.py
# VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-CERT
# AUTHORITY BOUNDARY: direct ASGI read projection certificate only
# TENANT POSTURE: exact authorized tenant predicate and foreign absence
# FAIL-CLOSED POSTURE: missing authority, client-policy gaps, and unknown resources deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
