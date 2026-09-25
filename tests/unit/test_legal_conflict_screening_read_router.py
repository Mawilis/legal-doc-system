"""Direct ASGI certificate for the L8-8N screening review-queue projection.

TITLE: WILSY OS Legal Conflict Screening Read Router Certificate
VERSION: v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-CERT
AUTHORITY: Direct authenticated read-projection certificate only.
EPITOME: Prove exact tenant scope, canonical screening identity, bounded
         deterministic review-queue presentation and complete authority-field
         exclusion without mutating screening, review or authorization truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_screening_read_router.py
COLLABORATION / OWNERSHIP: Certificate for tools/eos/api/legal_operations_router.py
                            L8-8E remains the immutable screening registry;
                            LegalDashboard is intentionally not changed here.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: 2026-09-25 v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-CERT
           establishes the authenticated bounded screening queue certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no raw party PII,
                             fingerprints, authorization evidence or Mongo data.
TENANT BOUNDARY: Tenant comes only from the authorized context and is forwarded
                 exactly to the canonical registry.
AUTHORITY BOUNDARY: Read projection only; no review, clearance or IAM mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Authentication, scope, schema and persistence failures
                         deny without browser-side reconstruction or fallback.
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
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictScreeningStatus,
)


TENANT = "tenant-law"
VERSION = "v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-CERT"
SCREENED_AT = datetime(2026, 9, 25, 4, 0, tzinfo=timezone.utc)


def _context(tenant: str = TENANT) -> TenantAuthorizationContext:
    """Build one already-authorized synthetic legal-practice context."""
    return TenantAuthorizationContext(
        identity=SovereignIdentity(
            identity_id="principal-law",
            tenant_id=tenant,
            username="operator",
            email="operator@example.test",
            auth_method="TEST",
            status=PrincipalStatus.ACTIVE,
        ),
        tenant_id=tenant,
        decision=TenantAuthorizationDecision(
            authorized=True,
            reason=TenantAuthorizationReason.AUTHORIZED,
            business_role="tenant_legal_partner",
            authorization_role="LEGAL_PARTNER",
        ),
    )


def _screening(
    screening_id: str,
    *,
    matter_id: str,
    screened_at: datetime = SCREENED_AT,
) -> Any:
    """Return the minimal canonical result shape consumed by the route."""
    return SimpleNamespace(
        screening_id=screening_id,
        source_case_matter_id=matter_id,
        status=LegalConflictScreeningStatus.REVIEW_REQUIRED,
        screened_at=screened_at,
    )


class _Database:
    """Record the exact screening collection requested by the route."""

    def __init__(self) -> None:
        self.collection_names: list[str] = []

    def get_collection(self, name: str) -> object:
        self.collection_names.append(name)
        return object()


def _app(context: TenantAuthorizationContext) -> FastAPI:
    """Mount the production router with only the auth dependency overridden."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[legal_router._INSTRUCTION_READ] = (
        lambda context=context: context
    )
    app.include_router(legal_router.router, prefix="/api")
    return app


def _install_read_seams(
    monkeypatch: pytest.MonkeyPatch,
    values: tuple[Any, ...],
) -> tuple[_Database, list[tuple[str, object, object]]]:
    """Replace only the transaction and registry read seams; writes are absent."""
    database = _Database()
    calls: list[tuple[str, object, object]] = []

    def list_review_required(
        tenant_id: str,
        collection: object,
        *,
        session: object,
    ) -> tuple[Any, ...]:
        calls.append((tenant_id, collection, session))
        return values

    monkeypatch.setattr(
        legal_router.LegalConflictScreeningRegistry,
        "list_review_required",
        staticmethod(list_review_required),
    )
    monkeypatch.setattr(
        legal_router,
        "_workspace_projection_transaction",
        lambda callback: callback("snapshot-session", database),
    )
    return database, calls


def test_authenticated_tenant_gets_exact_bounded_projection_and_no_authority_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The response is exact, ordered, minimized and registry-backed."""
    database, calls = _install_read_seams(
        monkeypatch,
        (
            _screening("screening-new", matter_id="matter-new"),
            _screening(
                "screening-old",
                matter_id="matter-old",
                screened_at=datetime(2026, 9, 24, 4, 0, tzinfo=timezone.utc),
            ),
        ),
    )
    with TestClient(_app(_context())) as client:
        response = client.get(
            "/api/legal-operations/conflict-screenings?limit=1"
            "&tenant_id=tenant-forged"
        )

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"schema", "version", "tenant_id", "visibility", "screenings"}
    assert body["schema"] == "WILSY-LEGAL-CONFLICT-SCREENING-PRESENTATION/V1"
    assert body["version"] == legal_router.VERSION
    assert body["tenant_id"] == TENANT
    assert body["visibility"] == "LEGAL_CONFLICT_SCREENING_REVIEW_QUEUE"
    assert body["screenings"] == [
        {
            "screening_id": "screening-new",
            "source_case_matter_id": "matter-new",
            "status": "REVIEW_REQUIRED",
            "screened_at": "2026-09-25T04:00:00+00:00",
        }
    ]
    assert calls and calls[0][0] == TENANT
    assert database.collection_names == ["legal_conflict_screenings"]
    serialized = str(body).lower()
    for forbidden in (
        "fingerprint",
        "authorization",
        "reviewer",
        "party",
        "subject",
        "token",
        "pii",
    ):
        assert forbidden not in serialized


def test_empty_authenticated_tenant_is_canonical_empty_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An authorized tenant with no queue rows is a successful empty read."""
    _install_read_seams(monkeypatch, ())
    with TestClient(_app(_context())) as client:
        response = client.get("/api/legal-operations/conflict-screenings")
    assert response.status_code == 200
    assert response.json()["screenings"] == []


def test_limit_is_bounded_and_malformed_limit_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Presentation limit is bounded without changing registry query scope."""
    _install_read_seams(
        monkeypatch,
        tuple(_screening(f"screening-{index}", matter_id=f"matter-{index}") for index in range(3)),
    )
    with TestClient(_app(_context())) as client:
        too_large = client.get(
            "/api/legal-operations/conflict-screenings?limit=2001"
        )
        malformed = client.get(
            "/api/legal-operations/conflict-screenings?limit=not-a-number"
        )
    assert too_large.status_code == 422
    assert malformed.status_code == 422


def test_authentication_failure_is_denied_before_registry_read() -> None:
    """The canonical authorization dependency remains fail-closed."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(legal_router.router, prefix="/api")
    with TestClient(app) as client:
        response = client.get("/api/legal-operations/conflict-screenings")
    assert response.status_code == 401


def test_read_certificate_surface_is_frozen() -> None:
    """The route is the new read version and exposes no mutation primitives."""
    assert legal_router.VERSION == "v1.9.0-L8-8N-CONFLICT-SCREENING-READ-API"
    assert not hasattr(legal_router, "insert_one")
    assert not hasattr(legal_router, "update_one")
    assert not hasattr(legal_router, "delete_one")


"""
ARTIFACT: test_legal_conflict_screening_read_router.py
VERSION: v1.0.0-L8-8N-CONFLICT-SCREENING-READ-ROUTER-CERT
AUTHORITY BOUNDARY: authenticated screening read projection certificate only
TENANT POSTURE: exact server-authorized tenant; caller tenant query is ignored
FAIL-CLOSED POSTURE: auth, bounds, persistence and projection drift deny
FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
