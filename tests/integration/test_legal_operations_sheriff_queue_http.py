"""Direct ASGI certificate for sheriff operational queue reads.

TITLE: WILSY OS Sheriff Operational Queue HTTP Certificate
VERSION: v1.0.0-L8-6A-SHERIFF-OPERATIONAL-QUEUE-HTTP-CERT
AUTHORITY: Direct ASGI certificate for authenticated sheriff queue projection.
EPITOME: Prove the L8-6A route admits only already-authorized sheriff context,
         delegates exact tenant scope to L8-5C, exposes only three certified
         current-state queues, strips transport/secret fields, and translates
         queue/persistence failures without inventing deputy, urgency, billing,
         geospatial, client, AI, or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_sheriff_queue_http.py
COLLABORATION / OWNERSHIP: Certificate for L8-6A HTTP composition only. IAM
                            authority remains in tenant authorization; L8-5C
                            remains canonical queue-membership authority.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6A-SHERIFF-OPERATIONAL-QUEUE-HTTP-CERT
           establishes authentication denial, exact sheriff tenant delegation,
           bounded three-queue output, projection filtering, L8-5C error
           translation, infrastructure error translation, and router-version
           binding without a deputy personal-queue fiction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no provider, client,
                             credential, geospatial, payment, or AI data.
TENANT BOUNDARY: Successful projection receives the exact already-authorized
                 tenant context; no cross-tenant composition exists here.
AUTHORITY BOUNDARY: Certificate and read projection only; no receipt,
                    allocation, attempt, service, return, billing, payment,
                    execution, settlement, or deputy impersonation authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Authentication gaps, queue evidence errors, unexpected
                         persistence errors, and projection leakage deny.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_operations_operational_queues import (
    LegalOperationsOperationalQueueError,
)


VERSION = "v1.0.0-L8-6A-SHERIFF-OPERATIONAL-QUEUE-HTTP-CERT"
TENANT = "tenant-sheriff"


class _Collection:
    """Opaque collection marker proving exact forwarding only."""


class _Current:
    """Current-value double proving response filtering and no invented fields."""

    def __init__(self, entity_id: str, state: str) -> None:
        self.entity_id = entity_id
        self.state = state

    def to_dict(self) -> dict[str, object]:
        return {
            "entity_id": self.entity_id,
            "tenant_id": TENANT,
            "state": self.state,
            "_id": "mongo-internal",
            "credentials": "must-not-leak",
            "token": "must-not-leak",
        }


@dataclass(frozen=True, slots=True)
class _Model:
    current: _Current


@dataclass(frozen=True, slots=True)
class _Queues:
    tenant_id: str
    office_receipt: tuple[_Model, ...]
    deputy_assignment: tuple[_Model, ...]
    active_attempts: tuple[_Model, ...]


class _QueueSpy:
    """Record exact L8-5C calls and return one governed queue projection."""

    def __init__(
        self,
        queues: _Queues | None = None,
        *,
        error: Exception | None = None,
    ) -> None:
        self.queues = queues
        self.error = error
        self.calls: list[tuple[str, object]] = []

    def read(
        self,
        *,
        tenant_id: str,
        lifecycle_collection: object,
        session: object = None,
    ) -> _Queues:
        assert session is None
        self.calls.append((tenant_id, lifecycle_collection))
        if self.error is not None:
            raise self.error
        assert self.queues is not None
        return self.queues


def _context() -> TenantAuthorizationContext:
    """Build one already-authorized sheriff context for route-seam testing."""
    identity = SovereignIdentity(
        identity_id="principal-sheriff",
        tenant_id=TENANT,
        username="sheriff",
        email="sheriff@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=TENANT,
        decision=TenantAuthorizationDecision(
            authorized=True,
            reason=TenantAuthorizationReason.AUTHORIZED,
            business_role="tenant_sheriff",
            authorization_role="SHERIFF",
        ),
    )


def _app(
    collection: _Collection,
    *,
    context: TenantAuthorizationContext | None = None,
) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if context is not None:
        app.dependency_overrides[legal_router._QUEUE_READ] = lambda: context
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: collection
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_missing_authentication_is_denied_before_queue_projection() -> None:
    """The real queue authorization dependency denies unauthenticated callers."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(legal_router.router, prefix="/api")
    with TestClient(app) as client:
        response = client.get("/api/legal-operations/operational-queues")
    assert response.status_code == 401


def test_authorized_sheriff_delegates_exact_tenant_and_projects_only_three_queues(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Already-authorized sheriff context reaches L8-5C and nothing broader."""
    collection = _Collection()
    spy = _QueueSpy(
        _Queues(
            tenant_id=TENANT,
            office_receipt=(_Model(_Current("document-1", "REGISTERED")),),
            deputy_assignment=(_Model(_Current("document-2", "RECEIVED")),),
            active_attempts=(_Model(_Current("attempt-1", "ALLOCATED")),),
        )
    )
    monkeypatch.setattr(legal_router, "get_operational_queues", spy.read)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get("/api/legal-operations/operational-queues")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == TENANT
    assert body["visibility"] == "SHERIFF_OPERATIONAL_QUEUE"
    assert set(body) == {
        "tenant_id",
        "visibility",
        "office_receipt",
        "deputy_assignment",
        "active_attempts",
    }
    assert body["office_receipt"] == [
        {"entity_id": "document-1", "tenant_id": TENANT, "state": "REGISTERED"}
    ]
    assert body["deputy_assignment"] == [
        {"entity_id": "document-2", "tenant_id": TENANT, "state": "RECEIVED"}
    ]
    assert body["active_attempts"] == [
        {"entity_id": "attempt-1", "tenant_id": TENANT, "state": "ALLOCATED"}
    ]
    assert spy.calls == [(TENANT, collection)]

    serialized = str(body).casefold()
    for forbidden in (
        "_id",
        "credentials",
        "token",
        "urgent",
        "distance",
        "billing",
        "invoice",
        "payment",
        "settlement",
        "revenue",
        "gps",
        "ai_score",
        "client_name",
    ):
        assert forbidden not in serialized


def test_l8_5c_queue_failure_is_bounded_evidence_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _Collection()
    spy = _QueueSpy(error=LegalOperationsOperationalQueueError("L8_5C_READ_MODEL_UNAVAILABLE"))
    monkeypatch.setattr(legal_router, "get_operational_queues", spy.read)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get("/api/legal-operations/operational-queues")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_QUEUE_EVIDENCE_UNAVAILABLE"
    assert spy.calls == [(TENANT, collection)]


def test_unexpected_queue_failure_is_bounded_persistence_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _Collection()
    spy = _QueueSpy(error=RuntimeError("synthetic persistence outage"))
    monkeypatch.setattr(legal_router, "get_operational_queues", spy.read)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get("/api/legal-operations/operational-queues")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE"
    assert spy.calls == [(TENANT, collection)]


def test_router_binding_is_exact_l8_6a_release() -> None:
    """Certificate remains bound to the intended sheriff queue API release."""
    assert legal_router.VERSION == "v1.3.0-L8-6A-SHERIFF-OPERATIONAL-QUEUE-READ-API"
    assert legal_router._QUEUE_READ.permission_id == "legal_operations:queue:read"
    assert legal_router._QUEUE_READ.operation == "legal_queue_read"


# ARTIFACT: test_legal_operations_sheriff_queue_http.py
# VERSION: v1.0.0-L8-6A-SHERIFF-OPERATIONAL-QUEUE-HTTP-CERT
# AUTHORITY BOUNDARY: direct ASGI sheriff operational-queue projection certificate only
# TENANT POSTURE: exact already-authorized sheriff tenant forwarded to L8-5C
# FAIL-CLOSED POSTURE: auth gaps, queue evidence failure, leakage, and outages deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
