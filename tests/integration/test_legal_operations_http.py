"""Direct ASGI certificate for deterministic Legal Operations reads.

TITLE: WILSY OS Legal Operations Deterministic Current Read API Certificate
VERSION: v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API-CERT
AUTHORITY: Direct ASGI certificate for tenant-authorized Legal Operations projections.
EPITOME: Prove authentication, exact tenant/type/entity history delegation,
         deterministic current-state selection, bounded absence, divergence
         rejection, client-policy denial, and read-only projection boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_http.py
COLLABORATION / OWNERSHIP: Certificate for L7A/L8-0 read composition only.
                            Durable tenant authorization remains independent;
                            P1 owns lifecycle truth, P2 owns immutable history,
                            and L8-0 owns current-state selection.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API-CERT
           replaces arbitrary-row read expectations with complete-history
           delegation, deterministic current selection, fork rejection, exact
           foreign absence, and bounded P2 failure proofs.
           2026-09-15 v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-CERT certified
           authentication, exact tenant scope, bounded hydration, and read-only
           output for the initial read API.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers and in-memory P1 values only;
                             no real provider, credential, secret, or customer
                             data access.
TENANT BOUNDARY: Every successful repository delegation receives the exact
                 authorized tenant, canonical entity type, and resource identity.
AUTHORITY BOUNDARY: Certificate and read projection only; no lifecycle,
                    persistence mutation, command, invoice, payment, execution,
                    or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement.
FAIL-CLOSED DECLARATION: Missing credentials/scope, client policy gaps, exact
                         absence, P2 failure, corruption, and history divergence
                         deny without arbitrary fallback selection.
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
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistryError,
)


VERSION = "v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API-CERT"
_TENANT = "tenant-alpha"
_IDENTITY = "instruction-001"
_NOW = datetime(2026, 9, 23, 7, 0, tzinfo=timezone.utc)


class _Collection:
    """Opaque lifecycle collection marker; P2 owns all persistence semantics."""


class _HistorySpy:
    """Record exact P2 history requests and return governed synthetic history."""

    def __init__(
        self,
        history: tuple[object, ...] = (),
        *,
        available_tenant: str = _TENANT,
        error: LegalOperationsLifecycleRegistryError | None = None,
    ) -> None:
        self.history = history
        self.available_tenant = available_tenant
        self.error = error
        self.calls: list[tuple[str, str, str, object, object]] = []

    def read(
        self,
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        collection: object,
        *,
        session: object = None,
    ) -> tuple[object, ...]:
        """Mirror P2's public history contract without selecting current truth."""
        self.calls.append(
            (tenant_id, entity_type, entity_identity, collection, session)
        )
        if self.error is not None:
            raise self.error
        if tenant_id != self.available_tenant:
            return ()
        return self.history


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
    """Mount the real L7A router with only dependency providers overridden."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if context is not None:
        app.dependency_overrides[legal_router._INSTRUCTION_READ] = lambda: context
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: collection
    app.include_router(legal_router.router, prefix="/api")
    return app


def _install_history(
    monkeypatch: pytest.MonkeyPatch,
    spy: _HistorySpy,
) -> None:
    """Replace only the P2 history I/O seam; keep the real L8-0 resolver active."""
    monkeypatch.setattr(
        legal_router.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(spy.read),
    )


def test_missing_authentication_is_denied() -> None:
    """Default authorization dependency denies unauthenticated requests."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(legal_router.router, prefix="/api")
    with TestClient(app) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")
    assert response.status_code == 401


def test_missing_tenant_scope_is_denied_before_history_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing explicit tenant scope cannot reach canonical lifecycle history."""
    collection = _Collection()
    spy = _HistorySpy()
    _install_history(monkeypatch, spy)
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


def test_authorized_read_resolves_unique_current_snapshot_from_complete_history(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unordered exact history resolves the longest canonical linear lineage."""
    registered = _instruction()
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=_NOW + timedelta(minutes=1),
    )
    collection = _Collection()
    spy = _HistorySpy((accepted, registered))
    _install_history(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == _TENANT
    assert body["entity_type"] == "LegalInstruction"
    assert body["entity_identity"] == _IDENTITY
    assert body["visibility"] == "AUDIT_VISIBLE"
    assert body["data"] == accepted.to_dict()
    assert spy.calls == [
        (_TENANT, "LegalInstruction", _IDENTITY, collection, None)
    ]


def test_foreign_tenant_is_bounded_absence_without_scope_disclosure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Foreign exact scope receives 404 after one foreign-scoped P2 delegation."""
    collection = _Collection()
    spy = _HistorySpy((_instruction(),))
    _install_history(monkeypatch, spy)

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
    """Empty exact P2 history is 404 and never becomes invented current truth."""
    collection = _Collection()
    spy = _HistorySpy(())
    _install_history(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 404
    assert "stack_trace" not in response.text
    assert spy.calls == [
        (_TENANT, "LegalInstruction", _IDENTITY, collection, None)
    ]


def test_client_role_is_fail_closed_before_history_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Internal lifecycle projections remain denied to client role until policy exists."""
    collection = _Collection()
    spy = _HistorySpy((_instruction(),))
    _install_history(monkeypatch, spy)

    with TestClient(
        _app(collection, context=_context(role="tenant_legal_client"))
    ) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 403
    assert response.json()["detail"] == "CLIENT_PROJECTION_POLICY_REQUIRED"
    assert spy.calls == []


def test_forked_history_fails_closed_instead_of_selecting_arbitrary_row(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two sibling current candidates become bounded evidence-unavailable."""
    registered = _instruction()
    accepted = registered.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted",
        occurred_at=_NOW + timedelta(minutes=1),
    )
    cancelled = registered.transition_to(
        LegalInstructionState.CANCELLED,
        evidence_reference="cancelled",
        occurred_at=_NOW + timedelta(minutes=1),
    )
    collection = _Collection()
    spy = _HistorySpy((registered, accepted, cancelled))
    _install_history(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE"


def test_p2_failure_is_bounded_and_never_falls_back_to_local_selection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P2 corruption/outage remains bounded evidence-unavailable."""
    collection = _Collection()
    spy = _HistorySpy(
        error=LegalOperationsLifecycleRegistryError("M2_P1_FINGERPRINT_MISMATCH")
    )
    _install_history(monkeypatch, spy)

    with TestClient(_app(collection, context=_context())) as client:
        response = client.get(f"/api/legal-operations/instructions/{_IDENTITY}")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_EVIDENCE_UNAVAILABLE"


def test_projection_excludes_transport_and_secret_fields() -> None:
    """Projection filtering cannot expose transport identifiers or common secrets."""
    payload = legal_router._project(_ProjectedValue())
    assert payload == {
        "instruction_id": _IDENTITY,
        "tenant_id": _TENANT,
        "state": "REGISTERED",
    }


def test_router_version_is_deterministic_current_read_release() -> None:
    """Certificate remains bound to the intended production router release."""
    assert legal_router.VERSION == "v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API"


# ARTIFACT: test_legal_operations_http.py
# VERSION: v1.1.0-L8-0-LEGAL-OPERATIONS-CURRENT-READ-API-CERT
# AUTHORITY BOUNDARY: direct ASGI deterministic read projection certificate only
# TENANT POSTURE: exact authorized tenant/type/entity delegation and foreign absence
# FAIL-CLOSED POSTURE: auth gaps, absence, P2 failures, and history divergence deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
