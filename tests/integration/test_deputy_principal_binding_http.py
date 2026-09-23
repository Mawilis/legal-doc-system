"""Direct ASGI certificate for sheriff deputy-principal binding commands.

TITLE: WILSY OS Deputy Principal Binding HTTP Certificate
VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-CERT
AUTHORITY: Direct HTTP/transaction certificate for the L8-6B sheriff command.
EPITOME: Prove the existing sheriff-only directory authority gates binding
         creation, tenant scope is server-derived, exactly one L8-6B composer
         runs inside one API-owned transaction, malformed authority fields fail,
         and structured not-found/conflict/invalid/unavailable failures map
         without fabricating identity or authorization truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_deputy_principal_binding_http.py
COLLABORATION / OWNERSHIP: HTTP composition certificate only; IAM owns actor
                            admission and L8-6B owns target identity validation.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-CERT
           establishes unauthenticated denial, exact sheriff tenant dispatch,
           forbidden body tenant authority, commit/abort ownership, bounded
           error mapping, response shape, and production-version binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no credentials,
                             location, client, AI, provider, or payment data.
TENANT BOUNDARY: Body cannot supply tenant_id; authorized context is exclusive.
AUTHORITY BOUNDARY: Transport certificate only; binding is not IAM or service.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: API starts/commits/aborts exactly one session transaction.
FAIL-CLOSED DECLARATION: Missing sheriff admission, extra authority fields,
                         target/precondition failure, conflict, or persistence
                         failure rejects without a binding-success projection.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_command_router as command_api
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.orchestration.deputy_principal_binding_orchestrator import (
    DeputyPrincipalBindingOrchestrationError,
)


VERSION = "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-CERT"
TENANT = "tenant-sheriff"
NOW = datetime(2026, 9, 23, 17, 30, tzinfo=timezone.utc)


class Session:
    """API-owned session double with explicit transaction event evidence."""

    def __init__(self) -> None:
        self.in_transaction = False
        self.events: list[str] = []

    def start_transaction(self) -> None:
        self.events.append("start")
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.events.append("commit")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *_args: object) -> None:
        self.events.append("end")


class Client:
    """Return one inspectable session for the API transaction wrapper."""

    def __init__(self) -> None:
        self.session = Session()

    def start_session(self) -> Session:
        return self.session


class Database:
    """Return named collection markers without persistence semantics."""

    def get_collection(self, name: str) -> object:
        return SimpleNamespace(name=name)


def _context() -> TenantAuthorizationContext:
    """Return one already-authorized sheriff directory context."""
    identity = SovereignIdentity(
        identity_id="sheriff-principal",
        tenant_id=TENANT,
        username="sheriff",
        email="sheriff@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_sheriff",
        "SHERIFF",
    )
    return TenantAuthorizationContext(identity, TENANT, decision)


def _app(*, authorize: bool) -> FastAPI:
    """Mount the real command router with optional sheriff admission override."""
    app = FastAPI()
    register_error_handlers(app, debug=False)
    if authorize:
        app.dependency_overrides[command_api._DIRECTORY] = _context
    app.include_router(command_api.router, prefix="/api")
    return app


def _payload() -> dict[str, object]:
    return {
        "principal_id": "deputy-principal",
        "deputy_id": "deputy-1",
        "bound_at": NOW.isoformat(),
        "evidence_reference": "sheriff-binding-evidence",
    }


def _binding() -> DeputyPrincipalBinding:
    return DeputyPrincipalBinding.from_deputy(
        principal_id="deputy-principal",
        deputy=Deputy(
            tenant_id=TENANT,
            deputy_id="deputy-1",
            sheriff_office_id="office-1",
            display_name="Deputy One",
            badge_reference="badge-1",
            evidence_reference="directory-evidence",
        ),
        bound_at=NOW,
        evidence_reference="sheriff-binding-evidence",
    )


def test_missing_authentication_denies_before_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Default directory dependency denies before any DB/session composition."""
    calls: list[str] = []
    monkeypatch.setattr(
        command_api,
        "_db_handles",
        lambda: calls.append("db") or (Client(), Database()),
    )

    with TestClient(_app(authorize=False)) as client:
        response = client.post(
            "/api/legal-operations/directory/deputy-principal-bindings",
            json=_payload(),
        )

    assert response.status_code == 401
    assert calls == []


def test_sheriff_dispatches_exact_tenant_target_and_commits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Authorized sheriff reaches exactly one L8-6B composer in one transaction."""
    client = Client()
    database = Database()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, database))
    seen: list[dict[str, Any]] = []

    def fake_bind(**kwargs: Any) -> DeputyPrincipalBinding:
        seen.append(kwargs)
        return _binding()

    monkeypatch.setattr(command_api, "bind_deputy_principal_identity", fake_bind)

    with TestClient(_app(authorize=True)) as http:
        response = http.post(
            "/api/legal-operations/directory/deputy-principal-bindings",
            json=_payload(),
        )

    assert response.status_code == 200
    assert response.json() == _binding().to_dict()
    assert len(seen) == 1
    call = seen[0]
    assert call["tenant_id"] == TENANT
    assert call["principal_id"] == "deputy-principal"
    assert call["deputy_id"] == "deputy-1"
    assert call["bound_at"] == NOW
    assert call["evidence_reference"] == "sheriff-binding-evidence"
    assert call["session"] is client.session
    assert call["lifecycle_collection"].name == command_api.LIFECYCLE_COLLECTION
    assert (
        call["binding_collection"].name
        == command_api.DEPUTY_PRINCIPAL_BINDING_COLLECTION
    )
    assert call["principal_collection"].name == command_api.PRINCIPAL_AUTHORITY_COLLECTION
    assert call["membership_collection"].name == command_api.TENANT_MEMBERSHIP_COLLECTION
    assert (
        call["business_role_collection"].name
        == command_api.TENANT_BUSINESS_ROLE_COLLECTION
    )
    assert call["role_assignment_collection"].name == command_api.ROLE_ASSIGNMENT_COLLECTION
    assert client.session.events == ["start", "commit", "end"]

    keys = set(response.json())
    for forbidden in {
        "permission",
        "role_id",
        "business_role",
        "authorized",
        "queue",
        "attempt_id",
        "invoice",
        "payment",
        "settlement",
    }:
        assert forbidden not in keys


def test_body_cannot_supply_tenant_or_authorization_fields() -> None:
    """Pydantic boundary rejects caller-manufactured scope/authority."""
    for extra in (
        {"tenant_id": TENANT},
        {"role_id": "DEPUTY"},
        {"permission": "legal_operations:directory:write"},
        {"authorized": True},
    ):
        payload = {**_payload(), **extra}
        with TestClient(_app(authorize=True)) as client:
            response = client.post(
                "/api/legal-operations/directory/deputy-principal-bindings",
                json=payload,
            )
        assert response.status_code == 422


@pytest.mark.parametrize(
    ("code", "status_code", "detail"),
    (
        ("L8_6B_DEPUTY_NOT_FOUND", 404, "LEGAL_OPERATION_NOT_FOUND"),
        (
            "L8_6B_BINDING_CONFLICT",
            409,
            "LEGAL_OPERATIONS_DEPUTY_BINDING_CONFLICT",
        ),
        (
            "L8_6B_DEPUTY_BUSINESS_ROLE_REQUIRED",
            422,
            "LEGAL_OPERATIONS_COMMAND_INVALID",
        ),
        (
            "L8_6B_BINDING_PERSISTENCE_UNAVAILABLE",
            503,
            "LEGAL_OPERATIONS_UNAVAILABLE",
        ),
    ),
)
def test_structured_l8_6b_failures_abort_and_map_bounded(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
    status_code: int,
    detail: str,
) -> None:
    """Structured composer failures abort once and preserve bounded HTTP meaning."""
    client = Client()
    monkeypatch.setattr(command_api, "_db_handles", lambda: (client, Database()))

    def reject(**_kwargs: Any) -> object:
        raise DeputyPrincipalBindingOrchestrationError(code)

    monkeypatch.setattr(command_api, "bind_deputy_principal_identity", reject)

    with TestClient(_app(authorize=True)) as http:
        response = http.post(
            "/api/legal-operations/directory/deputy-principal-bindings",
            json=_payload(),
        )

    assert response.status_code == status_code
    assert response.json()["detail"] == detail
    assert client.session.events == ["start", "abort", "end"]


def test_command_route_and_version_binding_are_exact() -> None:
    """Certificate remains bound to the intended route and sheriff dependency."""
    paths = {route.path for route in command_api.router.routes}  # type: ignore[reportAttributeAccessIssue]
    assert "/legal-operations/directory/deputy-principal-bindings" in paths
    assert command_api._DIRECTORY.permission_id == "legal_operations:directory:write"
    assert command_api._DIRECTORY.operation == "legal_directory_write"
    assert command_api.VERSION == (
        "v1.4.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-COMMAND-API"
    )
    assert VERSION == "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-CERT"


# ARTIFACT: test_deputy_principal_binding_http.py
# VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-HTTP-CERT
# AUTHORITY BOUNDARY: direct sheriff-gated L8-6B HTTP/transaction certificate only
# TENANT POSTURE: tenant comes only from authorized sheriff context
# FAIL-CLOSED POSTURE: auth/body/precondition/conflict/persistence failures abort and deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
