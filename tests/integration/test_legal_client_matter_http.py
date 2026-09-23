"""Direct ASGI certificate for the LEGAL_CLIENT matter projection API.

TITLE: WILSY OS Legal Client Matter Read API Certificate
VERSION: v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-CERT
AUTHORITY: Direct HTTP certification of the D6 client-only projection boundary.
EPITOME: Prove the authenticated /legal-operations/client/matters route derives
         tenant/principal from authorized context, owns one read-only snapshot
         transaction, re-enters D5 with the same session and canonical reader
         dependencies, returns the D5 safe payload unchanged, and translates
         revocation races/evidence outages fail closed.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_http.py
COLLABORATION / OWNERSHIP: D4 owns IAM, D5 owns sanitized projection, kernel DB
                            owns configured Mongo handles; this certificate owns
                            only D6 HTTP/session composition.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-CERT establishes
           exact route/dependency binding, authenticated scope derivation,
           snapshot start/commit/abort, same-session D5 delegation, exact safe
           response, current-IAM race denial, evidence-unavailable mapping and
           database-unavailable failure before projection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque tenant/principal/matter data only.
TENANT BOUNDARY: Browser supplies no client/matter authority; context owns scope.
AUTHORITY BOUNDARY: HTTP projection certificate only; no legal/financial mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Fake API-owned snapshot transaction; D5 remains caller-owned.
FAIL-CLOSED DECLARATION: Missing DB, denied D5 IAM or projection evidence failure
                         aborts/denies without fallback.
"""
from __future__ import annotations

from datetime import datetime, timezone
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
from tools.eos.legal_operations.domain.legal_client_matter_projection import (
    VERSION as D5_VERSION,
    LegalClientMatterProjection,
    LegalClientMatterProjectionError,
    LegalClientMatterProjectionSet,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatterState,
)


VERSION = "v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-CERT"
TENANT = "tenant-d6"
PRINCIPAL = "principal-client"
NOW = datetime(2026, 9, 23, 22, 0, tzinfo=timezone.utc)


class FakeSession:
    """API-owned transaction double with explicit snapshot lifecycle evidence."""

    def __init__(self) -> None:
        self.in_transaction = False
        self.started_level: str | None = None
        self.committed = False
        self.aborted = False

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(
        self,
        _exc_type: object,
        _exc: object,
        _tb: object,
    ) -> None:
        return None

    def start_transaction(self, *, read_concern: Any = None) -> None:
        self.started_level = getattr(read_concern, "level", None)
        self.in_transaction = True

    def commit_transaction(self) -> None:
        assert self.in_transaction is True
        self.committed = True
        self.in_transaction = False

    def abort_transaction(self) -> None:
        assert self.in_transaction is True
        self.aborted = True
        self.in_transaction = False


class FakeClient:
    """Configured Mongo client double returning one known session."""

    def __init__(self, session: FakeSession) -> None:
        self.session = session
        self.calls = 0

    def start_session(self) -> FakeSession:
        self.calls += 1
        return self.session


class FakeDatabase:
    """Configured database double exposing only named collection markers."""

    def __init__(self) -> None:
        self.requested: list[str] = []

    def get_collection(self, name: str) -> tuple[str, str]:
        self.requested.append(name)
        return ("collection", name)


def _context() -> TenantAuthorizationContext:
    """Build one exact already-admitted LEGAL_CLIENT request context."""
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="client",
        email="client@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=TENANT,
        decision=TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_legal_client",
            "LEGAL_CLIENT",
        ),
    )


def _safe_projection() -> LegalClientMatterProjectionSet:
    """Build one exact D5-safe response object."""
    return LegalClientMatterProjectionSet(
        tenant_id=TENANT,
        matters=(
            LegalClientMatterProjection(
                case_matter_id="matter-1",
                matter_reference="CLIENT-001",
                opened_at=NOW,
                state=CaseMatterState.OPEN,
            ),
        ),
    )


def _app(
    *,
    context: TenantAuthorizationContext,
    principal_repository: object,
    membership_repository: object,
    role_repository: object,
) -> FastAPI:
    """Mount the real router while overriding only external authority providers."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[legal_router._CLIENT_MATTER_READ] = lambda: context
    app.dependency_overrides[
        legal_router.get_principal_authority_repository
    ] = lambda: principal_repository
    app.dependency_overrides[
        legal_router.get_tenant_membership_repository
    ] = lambda: membership_repository
    app.dependency_overrides[
        legal_router.get_role_assignment_repository
    ] = lambda: role_repository
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_route_binding_and_successful_snapshot_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exact route commits one snapshot and returns D5 bytes without enrichment."""
    session = FakeSession()
    client = FakeClient(session)
    database = FakeDatabase()
    principal_repository = object()
    membership_repository = object()
    role_repository = object()
    calls: list[dict[str, object]] = []

    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (client, database),
    )

    def project(**kwargs: object) -> LegalClientMatterProjectionSet:
        calls.append(dict(kwargs))
        return _safe_projection()

    monkeypatch.setattr(
        legal_router,
        "get_legal_client_matter_projection",
        project,
    )

    with TestClient(
        _app(
            context=_context(),
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            role_repository=role_repository,
        )
    ) as http:
        response = http.get("/api/legal-operations/client/matters")

    assert response.status_code == 200
    assert response.json() == _safe_projection().to_dict()
    assert client.calls == 1
    assert session.started_level == "snapshot"
    assert session.committed is True
    assert session.aborted is False
    assert len(calls) == 1
    call = calls[0]
    assert call["tenant_id"] == TENANT
    assert call["principal_id"] == PRINCIPAL
    assert call["principal_repository"] is principal_repository
    assert call["membership_repository"] is membership_repository
    assert call["business_role_repository"] is role_repository
    assert call["role_assignment_repository"] is role_repository
    assert call["session"] is session
    assert call["visibility_collection"] == (
        "collection",
        legal_router.CLIENT_VISIBILITY_COLLECTION,
    )
    assert call["lifecycle_collection"] == (
        "collection",
        legal_router.LIFECYCLE_COLLECTION,
    )
    assert database.requested == [
        legal_router.CLIENT_VISIBILITY_COLLECTION,
        legal_router.LIFECYCLE_COLLECTION,
    ]


def test_exact_client_authorization_dependency_is_bound() -> None:
    """D6 HTTP admission uses the same exact D4 permission-operation pair."""
    assert legal_router._CLIENT_MATTER_READ.permission_id == (
        "legal_operations:client_matter:read"
    )
    assert legal_router._CLIENT_MATTER_READ.operation == "legal_client_matter_read"
    assert legal_router.VERSION == "v1.6.0-L8-7D6-CLIENT-MATTER-READ-API"
    assert D5_VERSION == "v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION"


def test_d5_current_iam_race_denial_aborts_and_maps_to_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """HTTP admission cannot override a D5 in-snapshot authorization revocation."""
    session = FakeSession()
    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (FakeClient(session), FakeDatabase()),
    )
    monkeypatch.setattr(
        legal_router,
        "get_legal_client_matter_projection",
        lambda **_kwargs: (_ for _ in ()).throw(
            LegalClientMatterProjectionError(
                "L8_7D5_CLIENT_AUTHORIZATION_DENIED_ROLE_ASSIGNMENT_INACTIVE"
            )
        ),
    )

    marker = object()
    with TestClient(
        _app(
            context=_context(),
            principal_repository=marker,
            membership_repository=marker,
            role_repository=marker,
        )
    ) as http:
        response = http.get("/api/legal-operations/client/matters")

    assert response.status_code == 403
    assert response.json()["detail"] == "LEGAL_CLIENT_MATTER_READ_DENIED"
    assert session.committed is False
    assert session.aborted is True


@pytest.mark.parametrize(
    "code",
    (
        "L8_7D5_VISIBILITY_EVIDENCE_INVALID",
        "L8_7D5_VISIBILITY_EVIDENCE_UNAVAILABLE",
        "L8_7D5_BOUND_MATTER_NOT_FOUND",
        "L8_7D5_BOUND_MATTER_EVIDENCE_UNAVAILABLE",
    ),
)
def test_projection_evidence_failure_aborts_and_maps_to_bounded_503(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
) -> None:
    """Visibility/matter evidence failures never leak internal error detail."""
    session = FakeSession()
    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (FakeClient(session), FakeDatabase()),
    )
    monkeypatch.setattr(
        legal_router,
        "get_legal_client_matter_projection",
        lambda **_kwargs: (_ for _ in ()).throw(
            LegalClientMatterProjectionError(code)
        ),
    )
    marker = object()

    with TestClient(
        _app(
            context=_context(),
            principal_repository=marker,
            membership_repository=marker,
            role_repository=marker,
        )
    ) as http:
        response = http.get("/api/legal-operations/client/matters")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "LEGAL_OPERATIONS_CLIENT_PROJECTION_UNAVAILABLE"
    )
    assert code not in response.text
    assert session.committed is False
    assert session.aborted is True


def test_missing_database_fails_before_d5_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unavailable configured persistence returns bounded 503 before D5."""
    calls: list[str] = []
    monkeypatch.setattr(legal_router, "_db_handles", lambda: (None, None))
    monkeypatch.setattr(
        legal_router,
        "get_legal_client_matter_projection",
        lambda **_kwargs: calls.append("projection"),
    )
    marker = object()

    with TestClient(
        _app(
            context=_context(),
            principal_repository=marker,
            membership_repository=marker,
            role_repository=marker,
        )
    ) as http:
        response = http.get("/api/legal-operations/client/matters")

    assert response.status_code == 503
    assert response.json()["detail"] == "LEGAL_OPERATIONS_PERSISTENCE_UNAVAILABLE"
    assert calls == []


def test_client_response_contains_no_internal_or_financial_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """D6 adds no transport enrichment to the already-sanitized D5 payload."""
    session = FakeSession()
    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (FakeClient(session), FakeDatabase()),
    )
    monkeypatch.setattr(
        legal_router,
        "get_legal_client_matter_projection",
        lambda **_kwargs: _safe_projection(),
    )
    marker = object()

    with TestClient(
        _app(
            context=_context(),
            principal_repository=marker,
            membership_repository=marker,
            role_repository=marker,
        )
    ) as http:
        body = http.get("/api/legal-operations/client/matters").json()

    forbidden = {
        "principal_id",
        "client_principal_id",
        "evidence_reference",
        "fingerprint",
        "transition_history",
        "instruction_id",
        "document_id",
        "deputy_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
        "authorized",
        "business_role",
        "authorization_role",
    }
    assert forbidden.isdisjoint(body)
    assert len(body["matters"]) == 1
    assert forbidden.isdisjoint(body["matters"][0])


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_http.py
# VERSION: v1.0.0-L8-7D6-CLIENT-MATTER-READ-API-CERT
# AUTHORITY BOUNDARY: direct D6 authenticated client-matter HTTP/snapshot composition certificate only
# TENANT POSTURE: tenant/principal derive only from authorized context and same snapshot D5 delegation
# FAIL-CLOSED POSTURE: DB absence, D5 current-IAM denial or projection evidence failure aborts/denies
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
