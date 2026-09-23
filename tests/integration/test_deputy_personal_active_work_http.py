"""Direct ASGI certificate for deputy personal active-work reads.

TITLE: WILSY OS Deputy Personal Active Work HTTP Certificate
VERSION: v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-HTTP-CERT
AUTHORITY: Direct HTTP certification of the L8-6C deputy-only read route.
EPITOME: Prove authentication/authorization precede collection access, tenant
         and principal scope are server-derived, exactly one L8-6C projection
         is invoked, only bound-deputy active attempts are returned, and
         missing binding/evidence/persistence failures remain bounded.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_deputy_personal_active_work_http.py
COLLABORATION / OWNERSHIP: HTTP composition certificate only; IAM owns caller
                            admission, L8-6B owns identity binding, and L8-6C
                            owns personal queue membership.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-HTTP-CERT
           establishes authentication denial, exact tenant/principal dispatch,
           bounded response shape, binding-required 403, evidence/persistence
           503 mapping, and production-version/permission binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Scope derives only from authorized tenant and identity context.
AUTHORITY BOUNDARY: Read transport certificate only; no lifecycle mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing IAM, binding, evidence, or persistence denies
                         without sheriff-queue or fixture fallback.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
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
from tools.eos.legal_operations.domain.deputy_personal_active_work import (
    DeputyPersonalActiveWorkError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
)


VERSION = "v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-HTTP-CERT"
TENANT = "tenant-deputy"
PRINCIPAL = "principal-deputy"
DEPUTY = "deputy-1"
NOW = datetime(2026, 9, 23, 19, 30, tzinfo=timezone.utc)


class _Collection:
    """Opaque collection marker proving exact provider forwarding."""


def _context() -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="deputy",
        email="deputy@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=TENANT,
        decision=TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_deputy",
            "DEPUTY",
        ),
    )


def _attempt() -> ServiceAttempt:
    return ServiceAttempt(
        tenant_id=TENANT,
        attempt_id="attempt-1",
        instruction_id="instruction-1",
        document_id="document-1",
        deputy_id=DEPUTY,
        allocated_at=NOW,
        allocation_evidence_reference="allocation-1",
    )


def _app(
    lifecycle: _Collection,
    binding: _Collection,
    *,
    authorize: bool,
) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if authorize:
        app.dependency_overrides[legal_router._DEPUTY_QUEUE_READ] = _context
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: lifecycle
    app.dependency_overrides[
        legal_router.get_deputy_principal_binding_collection
    ] = lambda: binding
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_missing_authentication_denies_before_collection_access() -> None:
    """Real authorization dependency denies before either read collection."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(legal_router.router, prefix="/api")

    with TestClient(app) as client:
        response = client.get("/api/legal-operations/deputy/active-work")

    assert response.status_code == 401


def test_authorized_deputy_dispatches_server_derived_scope_and_projects_only_active_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lifecycle, binding = _Collection(), _Collection()
    calls: list[dict[str, Any]] = []

    def project(**kwargs: Any) -> object:
        calls.append(kwargs)
        return SimpleNamespace(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
            deputy_id=DEPUTY,
            active_attempts=(SimpleNamespace(current=_attempt()),),
        )

    monkeypatch.setattr(legal_router, "get_deputy_personal_active_work", project)

    with TestClient(_app(lifecycle, binding, authorize=True)) as client:
        response = client.get("/api/legal-operations/deputy/active-work")

    assert response.status_code == 200
    assert len(calls) == 1
    assert calls[0] == {
        "tenant_id": TENANT,
        "principal_id": PRINCIPAL,
        "binding_collection": binding,
        "lifecycle_collection": lifecycle,
    }

    body = response.json()
    assert set(body) == {
        "tenant_id",
        "visibility",
        "deputy_id",
        "active_attempts",
    }
    assert body["tenant_id"] == TENANT
    assert body["visibility"] == "DEPUTY_PERSONAL_ACTIVE_WORK"
    assert body["deputy_id"] == DEPUTY
    assert body["active_attempts"] == [_attempt().to_dict()]
    serialized = str(body).casefold()
    for forbidden in (
        "principal_id",
        "office_receipt",
        "deputy_assignment",
        "urgent",
        "distance",
        "gps",
        "billing",
        "invoice",
        "payment",
        "settlement",
        "revenue",
        "ai_score",
        "client_name",
    ):
        assert forbidden not in serialized


def test_missing_binding_is_bounded_forbidden(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reject(**_kwargs: Any) -> object:
        raise DeputyPersonalActiveWorkError("L8_6C_BINDING_REQUIRED")

    monkeypatch.setattr(legal_router, "get_deputy_personal_active_work", reject)
    with TestClient(_app(_Collection(), _Collection(), authorize=True)) as client:
        response = client.get("/api/legal-operations/deputy/active-work")

    assert response.status_code == 403
    assert response.json()["detail"] == "DEPUTY_IDENTITY_BINDING_REQUIRED"


@pytest.mark.parametrize(
    "code",
    (
        "L8_6C_BINDING_INVALID",
        "L8_6C_BINDING_UNAVAILABLE",
        "L8_6C_ATTEMPT_EVIDENCE_UNAVAILABLE",
        "L8_6C_ATTEMPT_MODEL_INVALID",
    ),
)
def test_projection_failures_are_bounded_evidence_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
) -> None:
    def reject(**_kwargs: Any) -> object:
        raise DeputyPersonalActiveWorkError(code)

    monkeypatch.setattr(legal_router, "get_deputy_personal_active_work", reject)
    with TestClient(_app(_Collection(), _Collection(), authorize=True)) as client:
        response = client.get("/api/legal-operations/deputy/active-work")

    assert response.status_code == 503
    assert (
        response.json()["detail"]
        == "LEGAL_OPERATIONS_DEPUTY_QUEUE_EVIDENCE_UNAVAILABLE"
    )


def test_unexpected_failure_is_bounded_persistence_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        legal_router,
        "get_deputy_personal_active_work",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("synthetic outage")),
    )
    with TestClient(_app(_Collection(), _Collection(), authorize=True)) as client:
        response = client.get("/api/legal-operations/deputy/active-work")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE"


def test_route_permission_and_router_version_are_exact() -> None:
    paths = {route.path for route in legal_router.router.routes}  # type: ignore[reportAttributeAccessIssue]
    assert "/legal-operations/deputy/active-work" in paths
    assert legal_router._DEPUTY_QUEUE_READ.permission_id == (
        "legal_operations:deputy_queue:read"
    )
    assert legal_router._DEPUTY_QUEUE_READ.operation == "legal_deputy_queue_read"
    assert legal_router.VERSION == (
        "v1.4.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-READ-API"
    )
    assert VERSION == "v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-HTTP-CERT"


# ARTIFACT: test_deputy_personal_active_work_http.py
# VERSION: v1.0.0-L8-6C-DEPUTY-PERSONAL-ACTIVE-WORK-HTTP-CERT
# AUTHORITY BOUNDARY: direct deputy-only personal active-work HTTP certificate only
# TENANT POSTURE: tenant/principal are server-derived from authorized identity context
# FAIL-CLOSED POSTURE: missing IAM/binding/evidence/persistence denies without fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
