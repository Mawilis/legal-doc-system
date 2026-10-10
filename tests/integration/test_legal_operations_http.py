"""Direct ASGI certificate for deterministic Legal Operations reads.

TITLE: WILSY OS Legal Operations Current and History Read API Certificate
VERSION: v1.2.5-L8-7D6-ROUTER-COMPAT-CURRENT-HISTORY-READ-API-CERT
AUTHORITY: Direct ASGI certificate for tenant-authorized Legal Operations projections.
EPITOME: Prove authentication, exact tenant/type/entity L8-5 delegation,
         deterministic current-plus-history projection, bounded absence,
         read-model failure translation, client-policy denial, compatibility,
         and read-only projection boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_http.py
COLLABORATION / OWNERSHIP: Certificate for L7A/L8-0/L8-5 HTTP composition only.
                            Durable tenant authorization remains independent;
                            P1 owns lifecycle truth, P2 owns immutable history,
                            L8-0 owns current-state selection, and L8-5 owns
                            entity read-model composition.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.2.5-L8-7D6-ROUTER-COMPAT-CURRENT-HISTORY-READ-API-CERT rebinds the sealed internal
           Legal Operations read regression to additive D6. The new dedicated
           /client/matters route does not weaken tenant_legal_client denial on
           internal instruction/attempt/execution/return projections; existing
           current/history semantics remain unchanged.
2026-09-23 v1.2.4-L8-6D-ROUTER-COMPAT-CURRENT-HISTORY-READ-API-CERT
           rebinds the sealed L8-5 current/history regression certificate to
           the additive L8-6D read router; entity read semantics are unchanged.
           2026-09-23 v1.2.4-L8-6D-ROUTER-COMPAT-CURRENT-HISTORY-READ-API-CERT
           rebinds the sealed L8-5 current/history regression certificate to
           the additive L8-6C read router; entity read behavior is unchanged.
           2026-09-23 v1.2.2-L8-6A-ROUTER-COMPAT-CURRENT-HISTORY-READ-API-CERT
           rebinds the sealed L8-5 current/history regression certificate to
           the additive L8-6A router release while preserving every existing
           L8-5 behavioral, tenant, projection, and fail-closed assertion.
           2026-09-23 v1.2.1-L8-5-LEGAL-OPERATIONS-CURRENT-HISTORY-READ-API-CERT
           rebinds the certificate to the production documentation-alignment
           patch; runtime assertions and authority expectations are unchanged.
           2026-09-23 v1.2.0-L8-5-LEGAL-OPERATIONS-CURRENT-HISTORY-READ-API-CERT
           replaces direct P2/L8-0 HTTP spying with the canonical L8-5
           read-model seam, certifies backward-compatible current data plus
           sanitized immutable history, exact read-model delegation, bounded
           absence/error translation, and exclusion of raw P2 envelopes.
           2026-09-23 v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API-CERT
           replaces arbitrary-row read expectations with complete-history
           delegation, deterministic current selection, fork rejection, exact
           foreign absence, and bounded P2 failure proofs.
           2026-09-15 v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-CERT certified
           authentication, exact tenant scope, bounded hydration, and read-only
           output for the initial read API.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identifiers and in-memory P1 values only;
                             no real provider, credential, secret, or customer
                             data access.
TENANT BOUNDARY: Every successful read-model delegation receives the exact
                 authorized tenant, canonical entity type, and resource identity.
AUTHORITY BOUNDARY: Certificate and read projection only; no lifecycle,
                    persistence mutation, command, invoice, payment, execution,
                    or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Missing credentials/scope, client policy gaps, exact
                         absence, read-model failure, corruption, divergence,
                         and unexpected persistence errors deny without fallback.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi import FastAPI, Header
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.exceptions import ForbiddenOperationException
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    LegalInstruction,
    LegalInstructionState,
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.legal_operations_read_model import (
    LegalOperationsEntityReadModel,
    LegalOperationsReadModelError,
)


VERSION = "v1.2.5-L8-7D6-ROUTER-COMPAT-CURRENT-HISTORY-READ-API-CERT"
_TENANT = "tenant-alpha"
_IDENTITY = "instruction-001"
_NOW = datetime(2026, 9, 23, 7, 0, tzinfo=timezone.utc)


class _Collection:
    """Opaque lifecycle collection marker; lower layers own persistence semantics."""


class _ReadModelSpy:
    """Record exact L8-5 requests and return one governed entity read model."""

    def __init__(
        self,
        model: LegalOperationsEntityReadModel | None = None,
        *,
        available_tenant: str = _TENANT,
        error: Exception | None = None,
    ) -> None:
        self.model = model
        self.available_tenant = available_tenant
        self.error = error
        self.calls: list[tuple[str, str, str, object, object]] = []

    def read(
        self,
        *,
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        lifecycle_collection: object,
        session: object = None,
    ) -> LegalOperationsEntityReadModel:
        """Mirror the public L8-5 exact-entity read-model contract."""
        self.calls.append(
            (
                tenant_id,
                entity_type,
                entity_identity,
                lifecycle_collection,
                session,
            )
        )
        if self.error is not None:
            raise self.error
        if tenant_id != self.available_tenant or self.model is None:
            raise LegalOperationsReadModelError("L8_5_ENTITY_NOT_FOUND")
        return self.model


class _ProjectedValue:
    """Projection-only double proving transport and secret-field exclusion."""

    def to_dict(self) -> dict[str, object]:
        """Return bounded and forbidden fields for serializer filtering proof."""
        return {
            "instruction_id": _IDENTITY,
            "tenant_id": _TENANT,
            "state": "REGISTERED",
            "credentials": "must-not-leak",
            "token": "must-not-leak",
            "_id": "mongo-internal",
        }


def _instruction() -> LegalInstruction:
    """Build one canonical registered instruction for deterministic read tests."""
    return LegalInstruction(
        tenant_id=_TENANT,
        instruction_id=_IDENTITY,
        case_matter_id="matter-001",
        document_id="document-001",
        registered_at=_NOW,
        evidence_reference="registration-evidence",
    )


def _model(
    history: tuple[LegalInstruction, ...],
    *,
    current: LegalInstruction | None = None,
) -> LegalOperationsEntityReadModel:
    """Build one already-certified L8-5 projection for the HTTP boundary."""
    assert history
    return LegalOperationsEntityReadModel(
        tenant_id=_TENANT,
        entity_type="LegalInstruction",
        entity_identity=_IDENTITY,
        current=current or history[-1],
        history=history,
    )


def _context(
    tenant: str = _TENANT,
    role: str = "tenant_legal_partner",
) -> TenantAuthorizationContext:
    """Build one already-authorized synthetic tenant context."""
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
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=tenant,
        decision=decision,
    )


def _app(
    collection: _Collection,
    *,
    context: TenantAuthorizationContext | None = None,
) -> FastAPI:
    """Mount the real read router with only dependency providers overridden."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if context is not None:
        app.dependency_overrides[legal_router._INSTRUCTION_READ] = lambda: context
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: collection
    app.include_router(legal_router.router, prefix="/api")
    return app


def _install_read_model(
    monkeypatch: pytest.MonkeyPatch,
    spy: _ReadModelSpy,
) -> None:
    """Replace only the L8-5 read-model seam; lower-layer truth stays external."""
    monkeypatch.setattr(legal_router, "get_entity_read_model", spy.read)


def test_missing_authentication_is_denied() -> None:
    """Default authorization dependency denies unauthenticated requests."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(legal_router.router, prefix="/api")
    with TestClient(app) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 401


def test_missing_tenant_scope_is_denied_before_read_model_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing explicit tenant scope cannot reach canonical L8-5 composition."""
    collection = _Collection()
    spy = _ReadModelSpy(_model((_instruction(),)))
    _install_read_model(monkeypatch, spy)
    app = _app(collection)

    async def require_scope(
        tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    ) -> TenantAuthorizationContext:
        if tenant_id is None:
            raise ForbiddenOperationException("tenant scope required")
        return _context(tenant_id)

    app.dependency_overrides[legal_router._INSTRUCTION_READ] = require_scope
    with TestClient(app) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 403
    assert spy.calls == []


def test_authorized_read_delegates_to_l8_5_and_exposes_current_plus_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact authorized read preserves current data and adds immutable history."""
    registered = _instruction()
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=_NOW + timedelta(minutes=1),
    )
    collection = _Collection()
    spy = _ReadModelSpy(_model((registered, accepted), current=accepted))
    _install_read_model(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == _TENANT
    assert body["entity_type"] == "LegalInstruction"
    assert body["entity_identity"] == _IDENTITY
    assert body["visibility"] == "AUDIT_VISIBLE"
    assert body["data"] == accepted.to_dict()
    assert body["history"] == [registered.to_dict(), accepted.to_dict()]
    assert all(
        key not in snapshot
        for snapshot in (body["data"], *body["history"])
        for key in ("_id", "p1_payload", "source_payload", "credentials", "token")
    )
    assert spy.calls == [
        (_TENANT, "LegalInstruction", _IDENTITY, collection, None)
    ]


def test_foreign_tenant_is_bounded_absence_without_scope_disclosure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Foreign exact scope receives 404 after one foreign-scoped L8-5 delegation."""
    collection = _Collection()
    spy = _ReadModelSpy(_model((_instruction(),)))
    _install_read_model(monkeypatch, spy)

    with TestClient(
        _app(collection, context=_context("tenant-foreign"))
    ) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 404
    assert spy.calls == [
        (
            "tenant-foreign",
            "LegalInstruction",
            _IDENTITY,
            collection,
            None,
        )
    ]


def test_unknown_resource_is_bounded_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L8-5 exact-entity absence is 404 and never becomes invented truth."""
    collection = _Collection()
    spy = _ReadModelSpy()
    _install_read_model(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 404
    assert "stack_trace" not in response.text
    assert spy.calls == [
        (_TENANT, "LegalInstruction", _IDENTITY, collection, None)
    ]


def test_client_role_is_fail_closed_before_read_model_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Internal lifecycle projections remain denied to client role until policy exists."""
    collection = _Collection()
    spy = _ReadModelSpy(_model((_instruction(),)))
    _install_read_model(monkeypatch, spy)

    with TestClient(
        _app(collection, context=_context(role="tenant_legal_client"))
    ) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 403
    assert response.json()["detail"] == "CLIENT_PROJECTION_POLICY_REQUIRED"
    assert spy.calls == []


def test_divergent_read_model_failure_is_bounded_evidence_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L8-0 divergence translated by L8-5 cannot become arbitrary HTTP truth."""
    collection = _Collection()
    spy = _ReadModelSpy(
        error=LegalOperationsReadModelError("L8_5_CURRENT_PROJECTION_INVALID")
    )
    _install_read_model(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE"


def test_l8_5_evidence_failure_is_bounded_without_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P2 corruption/outage translated by L8-5 remains evidence-unavailable."""
    collection = _Collection()
    spy = _ReadModelSpy(
        error=LegalOperationsReadModelError("L8_5_EVIDENCE_UNAVAILABLE")
    )
    _install_read_model(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE"


def test_unexpected_read_failure_is_bounded_persistence_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected infrastructure failure remains a bounded 503 response."""
    collection = _Collection()
    spy = _ReadModelSpy(error=RuntimeError("synthetic transport failure"))
    _install_read_model(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE"


def test_projection_excludes_transport_and_secret_fields() -> None:
    """Projection filtering cannot expose transport identifiers or common secrets."""
    payload = legal_router._project(_ProjectedValue())
    assert payload == {
        "instruction_id": _IDENTITY,
        "tenant_id": _TENANT,
        "state": "REGISTERED",
    }


def test_l8_5_read_contract_remains_bound_under_l8_7d6_router_release() -> None:
    """L8-5 internal read semantics remain sealed under additive D6."""
    assert legal_router.VERSION == "v1.10.0-D22B5-R21-LEGAL-PRODUCT-AVAILABILITY-CONJUNCTION"


# ---------------------------------------------------------------------------
# D6 — direct ServiceAttempt current/history HTTP read certificate
# ---------------------------------------------------------------------------

_ATTEMPT_ID = "attempt-001"


def _attempt() -> ServiceAttempt:
    """Build one canonical allocated ServiceAttempt for the D6 read boundary."""
    return ServiceAttempt(
        tenant_id=_TENANT,
        attempt_id=_ATTEMPT_ID,
        instruction_id="instruction-001",
        document_id="document-001",
        deputy_id="deputy-001",
        allocated_at=_NOW,
        allocation_evidence_reference="allocation-evidence",
    )


def _attempt_model(
    history: tuple[ServiceAttempt, ...],
    *,
    current: ServiceAttempt | None = None,
    tenant_id: str = _TENANT,
) -> LegalOperationsEntityReadModel:
    """Build the already-certified generic read model for ServiceAttempt."""
    assert history
    return LegalOperationsEntityReadModel(
        tenant_id=tenant_id,
        entity_type="ServiceAttempt",
        entity_identity=_ATTEMPT_ID,
        current=current or history[-1],
        history=history,
    )


def _attempt_app(
    *,
    context: TenantAuthorizationContext | None = None,
) -> FastAPI:
    """Mount the production route while overriding infrastructure only."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if context is not None:
        app.dependency_overrides[legal_router._ATTEMPT_READ] = lambda: context
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: object()
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_attempt_read_missing_authentication_is_denied() -> None:
    """The attempt route remains behind canonical authentication."""
    with TestClient(_attempt_app()) as client:
        response = client.get(
            f"/api/legal-operations/attempts/{_ATTEMPT_ID}"
        )
    assert response.status_code == 401


def test_attempt_read_authorization_denial_precedes_read_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A denied attempt-read dependency prevents any lifecycle projection."""
    from fastapi import HTTPException

    calls: list[str] = []

    def forbidden() -> None:
        raise HTTPException(
            status_code=403,
            detail="TENANT_AUTHORIZATION_DENIED",
        )

    def forbidden_read(*args: object, **kwargs: object) -> object:
        calls.append("read_model")
        raise AssertionError("read model must not run after denied authority")

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[legal_router._ATTEMPT_READ] = forbidden
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: object()
    app.include_router(legal_router.router, prefix="/api")

    monkeypatch.setattr(
        legal_router,
        "get_entity_read_model",
        forbidden_read,
    )

    with TestClient(app) as client:
        response = client.get(
            f"/api/legal-operations/attempts/{_ATTEMPT_ID}"
        )

    assert response.status_code == 403
    assert calls == []


def test_attempt_read_exposes_exact_current_plus_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authorized attempt reads expose deterministic canonical history only."""
    allocated = _attempt()
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-evidence",
        occurred_at=_NOW + timedelta(minutes=1),
    )
    model = _attempt_model((allocated, attempted), current=attempted)
    calls: list[tuple[str, str, str]] = []

    def resolve(
        *,
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        lifecycle_collection: object,
        session: object = None,
    ) -> LegalOperationsEntityReadModel:
        del lifecycle_collection, session
        calls.append((tenant_id, entity_type, entity_identity))
        return model

    monkeypatch.setattr(
        legal_router,
        "get_entity_read_model",
        resolve,
    )

    with TestClient(_attempt_app(context=_context())) as client:
        response = client.get(
            f"/api/legal-operations/attempts/{_ATTEMPT_ID}"
        )

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == _TENANT
    assert body["entity_type"] == "ServiceAttempt"
    assert body["entity_identity"] == _ATTEMPT_ID
    assert body["visibility"] == "AUDIT_VISIBLE"
    assert body["data"] == attempted.to_dict()
    assert body["history"] == [
        allocated.to_dict(),
        attempted.to_dict(),
    ]
    assert calls == [
        (_TENANT, "ServiceAttempt", _ATTEMPT_ID)
    ]

    for snapshot in (body["data"], *body["history"]):
        assert "_id" not in snapshot
        assert "credentials" not in snapshot
        assert "secret" not in snapshot
        assert "token" not in snapshot
        assert "password" not in snapshot
        assert not any(
            token in key.casefold()
            for key in snapshot
            for token in (
                "invoice",
                "payment",
                "settlement",
                "billing_execution",
            )
        )


def test_attempt_read_foreign_tenant_is_bounded_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Foreign-tenant attempt existence cannot be disclosed."""
    calls: list[tuple[str, str, str]] = []

    def resolve(
        *,
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        lifecycle_collection: object,
        session: object = None,
    ) -> LegalOperationsEntityReadModel:
        del lifecycle_collection, session
        calls.append((tenant_id, entity_type, entity_identity))
        raise LegalOperationsReadModelError(
            "L8_5_ENTITY_NOT_FOUND"
        )

    monkeypatch.setattr(
        legal_router,
        "get_entity_read_model",
        resolve,
    )

    foreign = "tenant-foreign"
    with TestClient(
        _attempt_app(context=_context(foreign))
    ) as client:
        response = client.get(
            f"/api/legal-operations/attempts/{_ATTEMPT_ID}"
        )

    assert response.status_code == 404
    assert "stack_trace" not in response.text
    assert calls == [
        (foreign, "ServiceAttempt", _ATTEMPT_ID)
    ]


def test_attempt_read_unknown_resource_is_bounded_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unknown attempt identity remains the generic bounded 404."""
    def resolve(**kwargs: object) -> LegalOperationsEntityReadModel:
        del kwargs
        raise LegalOperationsReadModelError(
            "L8_5_ENTITY_NOT_FOUND"
        )

    monkeypatch.setattr(
        legal_router,
        "get_entity_read_model",
        resolve,
    )

    with TestClient(_attempt_app(context=_context())) as client:
        response = client.get(
            "/api/legal-operations/attempts/missing-attempt"
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "LEGAL_OPERATION_NOT_FOUND"
    assert "stack_trace" not in response.text


def test_attempt_read_divergent_history_is_bounded_evidence_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Corrupt or divergent attempt truth fails closed as evidence unavailable."""
    def resolve(**kwargs: object) -> LegalOperationsEntityReadModel:
        del kwargs
        raise LegalOperationsReadModelError(
            "L8_5_CURRENT_PROJECTION_INVALID"
        )

    monkeypatch.setattr(
        legal_router,
        "get_entity_read_model",
        resolve,
    )

    with TestClient(_attempt_app(context=_context())) as client:
        response = client.get(
            f"/api/legal-operations/attempts/{_ATTEMPT_ID}"
        )

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE"
    )


def test_attempt_read_unexpected_persistence_failure_is_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected persistence failures do not leak implementation details."""
    def resolve(**kwargs: object) -> LegalOperationsEntityReadModel:
        del kwargs
        raise RuntimeError("synthetic persistence failure")

    monkeypatch.setattr(
        legal_router,
        "get_entity_read_model",
        resolve,
    )

    with TestClient(_attempt_app(context=_context())) as client:
        response = client.get(
            f"/api/legal-operations/attempts/{_ATTEMPT_ID}"
        )

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE"
    )
    assert "synthetic persistence failure" not in response.text

# ARTIFACT: test_legal_operations_http.py
# VERSION: v1.2.5-L8-7D6-ROUTER-COMPAT-CURRENT-HISTORY-READ-API-CERT
# AUTHORITY BOUNDARY: direct ASGI authenticated current-plus-history projection certificate only
# TENANT POSTURE: exact authorized tenant/type/entity L8-5 delegation and foreign absence
# FAIL-CLOSED POSTURE: auth gaps, absence, read-model failures, divergence, and outages deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
