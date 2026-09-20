"""WILSY OS canonical access-token issuance and verification certificate.

TITLE: Canonical Access-Token Contract Certificate
VERSION: v1.0.0-R1D-B0F-B4-R2
AUTHORITY: Deterministic token interoperability evidence only.
EPITOME: Proves MFA/login issuance and EOS protected-route verification share
         one cryptographic owner, one secret authority, and one claim contract.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_canonical_access_token_contract.py
COLLABORATION / OWNERSHIP: Exercises AuthRegistry, jwt_provider,
                           get_current_identity, and legal-acceptance transport.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R1D-B0F-B4-R2 establishes direct round-trip and fail-closed
           certificates without a live database, login, OTP, or browser.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Fixture-only credentials and secrets; no values are
                            emitted outside the in-memory test process.
TENANT BOUNDARY: Tenant claims are asserted exact and remain downstream context.
AUTHORITY BOUNDARY: Cryptographic token contract only; durable principal status
                    remains authoritative in the repository dependency.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import inspect
import json
import time
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import FastAPI
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from starlette.requests import Request

from tools.eos.api import auth_router, legal_acceptance_router
from tools.eos.auth import authentication, jwt_provider
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.domain.auth import VerifyOTPRequest


SECRET = "canonical-token-contract-unit-secret"
TENANT = "WILSYTENANT-4CD2FZ4O"
PRINCIPAL = "WILSYAUTH-canonical-principal"


class _TenantRegistry:
    """Canonical tenant fixture; it grants no membership or role authority."""

    @staticmethod
    def resolve_canonical_tenant(reference: str, **_kwargs: Any) -> SimpleNamespace:
        if reference != TENANT:
            raise RuntimeError("tenant not found")
        return SimpleNamespace(tenant_id=TENANT)


class _PrincipalRepository:
    def __init__(self, status: PrincipalStatus = PrincipalStatus.ACTIVE) -> None:
        self.status = status

    def get(self, principal_id: str) -> PrincipalAuthority:
        return PrincipalAuthority(principal_id, self.status, 0)


def _request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": []})


def _credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _run_identity(token: str, repository: _PrincipalRepository) -> SovereignIdentity:
    return asyncio.run(
        authentication.get_current_identity(
            _request(), _credentials(token), None, repository  # type: ignore[arg-type]
        )
    )


def _resign(payload: dict[str, Any], secret: str = SECRET) -> str:
    """Build a fixture token for negative claim tests using the same HS256 wire format."""
    header = {"alg": "HS256", "typ": "JWT"}
    encode = lambda value: base64.urlsafe_b64encode(
        json.dumps(value, separators=(",", ":"), sort_keys=True).encode()
    ).rstrip(b"=").decode()
    signing_input = f"{encode(header)}.{encode(payload)}"
    signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def test_auth_registry_issues_provider_token_with_canonical_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    registry = AuthRegistry(cast(Any, _TenantRegistry()))
    token = registry.generate_jwt(PRINCIPAL, TENANT, "FIELD_DEPUTY", ["legal:read"])
    payload = jwt_provider.verify_access_token(token)
    assert payload is not None
    assert payload["identity_id"] == PRINCIPAL
    assert payload["tenant_id"] == TENANT
    assert payload["roles"] == ["FIELD_DEPUTY"]
    assert payload["permissions"] == ["legal:read"]
    assert isinstance(payload["iat"], int) and isinstance(payload["exp"], int)
    assert "sub" not in payload and "role" not in payload


def test_auth_registry_has_no_independent_crypto_authority() -> None:
    source = inspect.getsource(AuthRegistry)
    assert "jwt.encode" not in source
    assert "JWT_SECRET" not in source
    assert "create_access_token" in source


def test_canonical_token_round_trips_through_current_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": ["FIELD_DEPUTY"], "permissions": ["legal:read"]}
    )
    identity = _run_identity(token, _PrincipalRepository())
    assert identity.identity_id == PRINCIPAL
    assert identity.tenant_id == TENANT
    assert identity.status is PrincipalStatus.ACTIVE


def test_mfa_response_token_is_immediately_accepted_by_canonical_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    issuer = AuthRegistry(cast(Any, _TenantRegistry()))
    user = SimpleNamespace(
        id=PRINCIPAL,
        email="principal@example.com",
        firstName="Canonical",
        lastName="Principal",
        role="FIELD_DEPUTY",
        permissions=["legal:read"],
        tenantId=TENANT,
        mfaRegistered=True,
        hasSignedCovenant=True,
    )

    class _MfaRegistry:
        def get_user_by_email(self, _email: str) -> SimpleNamespace:
            return user

        def get_otp_secret(self, _user_id: str) -> str:
            return "enrolled"

        def verify_otp(self, _user_id: str, _code: str) -> bool:
            return True

        def create_session(self, _user: SimpleNamespace) -> SimpleNamespace:
            return SimpleNamespace(
                token=issuer.generate_jwt(user.id, user.tenantId, user.role, user.permissions)
            )

    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: _MfaRegistry())
    response = asyncio.run(
        auth_router.verify_otp(VerifyOTPRequest(email=user.email, code="123456"))
    )
    assert response.token is not None
    assert jwt_provider.verify_access_token(response.token) is not None
    assert _run_identity(response.token, _PrincipalRepository()).identity_id == PRINCIPAL


def test_legal_acceptance_status_accepts_canonical_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": ["FIELD_DEPUTY"], "permissions": ["legal:read"]}
    )
    app = FastAPI()
    app.include_router(legal_acceptance_router.router)

    class _Service:
        def status(self, identity: SovereignIdentity, **_kwargs: Any) -> dict[str, Any]:
            return {"status": "DOCUMENT_APPROVAL_REQUIRED", "tenantId": identity.tenant_id}

    # Override only the durable repository dependency; the route's actual
    # HTTPBearer -> verify_access_token -> get_current_identity chain remains live.
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: _PrincipalRepository()
    app.dependency_overrides[legal_acceptance_router._service] = lambda: _Service()
    response = TestClient(app).get(
        "/legal-acceptance/status", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["tenantId"] == TENANT



def test_legal_acceptance_document_route_uses_server_current_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": ["FIELD_DEPUTY"], "permissions": ["legal:read"]}
    )
    app = FastAPI()
    app.include_router(legal_acceptance_router.router)
    digest = "a" * 128

    class _Document:
        status = SimpleNamespace(value="APPROVED")
        sha3_512 = digest

        def to_document(self) -> dict[str, Any]:
            return {"document_id": "DOC-USER-TERMS", "version": "1.1.0", "sha3_512": digest}

    class _Registry:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str | None]] = []

        def get(self, document_id: str, version: str | None = None, **_kwargs: Any) -> Any:
            self.calls.append((document_id, version))
            if version is None:
                return SimpleNamespace(
                    status=SimpleNamespace(value="APPROVED"),
                    to_document=lambda: {"document_id": document_id, "version": "1.0.0", "sha3_512": "b" * 128},
                )
            assert version == "1.1.0"
            return _Document()

    registry = _Registry()

    class _Service:
        document_registry = registry
        document_collection = object()

        def status(self, identity: SovereignIdentity, **_kwargs: Any) -> dict[str, Any]:
            assert identity.tenant_id == TENANT
            return {"documents": [{"documentId": "DOC-USER-TERMS", "version": "1.1.0", "sha3_512": digest}]}

    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: _PrincipalRepository()
    app.dependency_overrides[legal_acceptance_router._service] = lambda: _Service()
    response = TestClient(app).get(
        "/legal-acceptance/documents/DOC-USER-TERMS", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["version"] == "1.1.0"
    assert registry.calls == [("DOC-USER-TERMS", "1.1.0")]


def test_legal_acceptance_stale_document_maps_to_422() -> None:
    error = legal_acceptance_router.LegalAcceptanceServiceError("LEGAL_ACCEPTANCE_DOCUMENT_NOT_CURRENT")
    translated = legal_acceptance_router._translate(error)
    assert translated.status_code == 422
    assert translated.detail == "LEGAL_ACCEPTANCE_DOCUMENT_NOT_CURRENT"

def test_legal_acceptance_http_uses_durable_business_role_not_jwt_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Actual router/service composition must ignore credential role projections."""
    from datetime import datetime, timezone

    from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
    from tools.eos.auth.tenant_membership import TenantMembershipStatus
    from tools.eos.kernel import db as kernel_db
    from tools.eos.legal_operations.domain.legal_acceptance import (
        LegalAgreementType,
        canonical_document_digest,
    )
    from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

    class _Collection:
        def __init__(self, rows=None):
            self.rows = list(rows or [])

        def find_one(self, query, *, sort=None, session=None):
            del session
            rows = [
                row
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ]
            if sort:
                for key, direction in reversed(sort):
                    rows.sort(
                        key=lambda row: row.get(key, ""),
                        reverse=direction < 0,
                    )
            return dict(rows[0]) if rows else None

        def find(self, query, *, session=None):
            del session
            return [
                dict(row)
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ]

    class _Database:
        def __init__(self, collections):
            self.collections = collections

        def __getitem__(self, name):
            return self.collections[name]

        def get_collection(self, name, **_kwargs):
            return self.collections[name]

    def _document_row(family: LegalAgreementType) -> dict[str, Any]:
        reference = f"http-cert:{family.value}:1.0.0"
        content = f"HTTP composition certificate {family.value}"
        return {
            "document_id": f"DOC-HTTP-{family.value}",
            "agreement_type": family.value,
            "version": "1.0.0",
            "title": family.value.replace("_", " ").title(),
            "jurisdiction": "ZA",
            "locale": "en-ZA",
            "effective_from": "2026-09-20T00:00:00+00:00",
            "status": "APPROVED",
            "content_reference": reference,
            "content": content,
            "sha3_512": canonical_document_digest(content, reference),
            "created_at": "2026-09-20T00:00:00+00:00",
            "supersedes_document_id": None,
        }

    documents = _Collection(
        [
            _document_row(LegalAgreementType.INSTITUTIONAL_CHARTER),
            _document_row(LegalAgreementType.USER_TERMS),
            _document_row(LegalAgreementType.ACCEPTABLE_USE),
            _document_row(LegalAgreementType.PRIVACY_NOTICE),
            _document_row(LegalAgreementType.AI_ASSISTANCE_NOTICE),
            _document_row(LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE),
        ]
    )
    acceptances = _Collection()
    memberships = _Collection(
        [
            {
                "principal_id": PRINCIPAL,
                "tenant_id": TENANT,
                "status": TenantMembershipStatus.ACTIVE.value,
                "revision": 0,
            }
        ]
    )
    business_roles = _Collection(
        [
            {
                "principal_id": PRINCIPAL,
                "tenant_id": TENANT,
                "business_role": "tenant_auditor",
                "status": TenantBusinessRoleStatus.ACTIVE.value,
                "revision": 0,
                "effective_at": datetime(2026, 9, 20, tzinfo=timezone.utc),
                "revoked_at": None,
            }
        ]
    )

    database = _Database(
        {
            "legal_document_versions": documents,
            "legal_acceptance_evidence": acceptances,
            "tenant_memberships": memberships,
            "tenant_business_roles": business_roles,
        }
    )

    def _canonical_tenant(reference: str, **_kwargs: Any) -> SimpleNamespace:
        if reference != TENANT:
            raise RuntimeError("tenant not found")
        return SimpleNamespace(tenant_id=TENANT)

    monkeypatch.setattr(kernel_db, "get_database", lambda: database)
    monkeypatch.setattr(
        TenantRegistry,
        "resolve_canonical_tenant",
        staticmethod(_canonical_tenant),
    )
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)

    app = FastAPI()
    app.include_router(legal_acceptance_router.router)
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalRepository()

    assert legal_acceptance_router._service not in app.dependency_overrides

    forged_admin_token = jwt_provider.create_access_token(
        {
            "identity_id": PRINCIPAL,
            "tenant_id": TENANT,
            "roles": ["SUPER_ADMIN"],
            "permissions": ["legal:read"],
        }
    )
    auditor_response = TestClient(app).get(
        "/legal-acceptance/status",
        headers={"Authorization": f"Bearer {forged_admin_token}"},
    )
    assert auditor_response.status_code == 200
    assert (
        LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE.value
        not in auditor_response.json()["missingAgreementTypes"]
    )

    business_roles.rows[0]["business_role"] = "tenant_admin"

    non_admin_token = jwt_provider.create_access_token(
        {
            "identity_id": PRINCIPAL,
            "tenant_id": TENANT,
            "roles": ["FIELD_DEPUTY"],
            "permissions": ["legal:read"],
        }
    )
    admin_response = TestClient(app).get(
        "/legal-acceptance/status",
        headers={"Authorization": f"Bearer {non_admin_token}"},
    )
    assert admin_response.status_code == 200
    assert (
        LegalAgreementType.ADMIN_RESPONSIBILITY_NOTICE.value
        in admin_response.json()["missingAgreementTypes"]
    )


def test_missing_secret_fails_closed_for_issue_and_verify(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WILSY_JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="WILSY_JWT_SECRET"):
        jwt_provider.create_access_token(
            {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": [], "permissions": []}
        )
    assert jwt_provider.verify_access_token("a.b.c") is None


def test_missing_principal_claim_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": [], "permissions": []}
    )
    encoded_payload = token.split(".")[1] + "=="
    payload = json.loads(base64.urlsafe_b64decode(encoded_payload).decode())
    payload.pop("identity_id")
    assert jwt_provider.verify_access_token(_resign(payload)) is None


def test_tenant_claim_is_dynamic_projection_not_hardcoded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": "TENANT-DYNAMIC", "roles": [], "permissions": []}
    )
    payload = jwt_provider.verify_access_token(token)
    assert payload is not None
    assert payload["tenant_id"] == "TENANT-DYNAMIC"


def test_expired_invalid_signature_and_inactive_principal_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    real_time = time.time
    monkeypatch.setattr(jwt_provider.time, "time", lambda: 1000)
    token = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": [], "permissions": []},
        expires_in_seconds=10,
    )
    monkeypatch.setattr(jwt_provider.time, "time", lambda: 1011)
    assert jwt_provider.verify_access_token(token) is None
    assert jwt_provider.verify_access_token(token[:-1] + ("a" if token[-1] != "a" else "b")) is None
    monkeypatch.setattr(jwt_provider.time, "time", real_time)
    fresh = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": [], "permissions": []}
    )
    with pytest.raises(Exception):
        _run_identity(fresh, _PrincipalRepository(PrincipalStatus.SUSPENDED))


# ARTIFACT: test_canonical_access_token_contract.py
# VERSION: v1.0.0-R1D-B0F-B4-R2
# AUTHORITY BOUNDARY: deterministic token interoperability evidence only
# TENANT POSTURE: exact tenant claim is preserved; durable membership remains downstream
# FAIL-CLOSED POSTURE: missing configuration, malformed claims, expiry, signatures, and inactive principals deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT


def test_workspace_bootstrap_http_uses_server_projection_not_jwt_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workspace bootstrap must serialize server authority, never JWT role claims."""

    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)

    token = jwt_provider.create_access_token(
        {
            "identity_id": PRINCIPAL,
            "tenant_id": TENANT,
            "email": "principal@example.com",
            # Deliberately forged transport projections.
            "roles": ["SUPER_ADMIN"],
            "permissions": ["*"],
        }
    )

    projection_calls: list[tuple[str, str, tuple[str, ...], tuple[str, ...]]] = []

    def _projection(*, identity: SovereignIdentity, **_kwargs: Any) -> SimpleNamespace:
        projection_calls.append(
            (
                identity.identity_id,
                identity.tenant_id,
                tuple(identity.roles),
                tuple(identity.permissions),
            )
        )
        return SimpleNamespace(
            principal_id=PRINCIPAL,
            email="principal@example.com",
            tenant_id=TENANT,
            business_role="tenant_auditor",
            membership_revision=7,
            business_role_revision=11,
            tenant=SimpleNamespace(
                tenant_id=TENANT,
                status="ACTIVE",
                organization=SimpleNamespace(
                    organization_name="Canonical Tenant",
                    legal_name="Canonical Tenant (Pty) Ltd",
                ),
            ),
        )

    # Establish the future composition seam without requiring production
    # implementation before the RED certificate is observed.
    monkeypatch.setattr(
        auth_router,
        "build_workspace_bootstrap_projection",
        _projection,
        raising=False,
    )

    app = FastAPI()
    app.include_router(auth_router.router)
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalRepository()

    response = TestClient(app).get(
        "/auth/workspace-bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "READY",
        "user": {
            "id": PRINCIPAL,
            "email": "principal@example.com",
        },
        "workspace": {
            "tenantId": TENANT,
            "businessRole": "tenant_auditor",
            "membershipRevision": 7,
            "businessRoleRevision": 11,
            "tenant": {
                "tenantId": TENANT,
                "name": "Canonical Tenant",
                "legalName": "Canonical Tenant (Pty) Ltd",
                "status": "ACTIVE",
            },
        },
    }

    serialized = response.json()
    assert "roles" not in serialized["user"]
    assert "permissions" not in serialized["user"]
    assert "role" not in serialized["user"]

    # The real authentication chain may carry forged JWT projections into the
    # candidate identity, but the endpoint must source workspace authority from
    # build_workspace_bootstrap_projection instead.
    assert projection_calls == [
        (
            PRINCIPAL,
            TENANT,
            ("SUPER_ADMIN",),
            ("*",),
        )
    ]


def test_workspace_bootstrap_http_denial_is_bounded_403(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workspace authority denials must fail closed without leaking internals."""

    from tools.eos.auth.workspace_bootstrap_projection import (
        WorkspaceBootstrapProjectionError,
    )

    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {
            "identity_id": PRINCIPAL,
            "tenant_id": TENANT,
            "roles": ["SUPER_ADMIN"],
            "permissions": ["*"],
        }
    )

    def _denied(**_kwargs: Any) -> Any:
        raise WorkspaceBootstrapProjectionError(
            "WORKSPACE_BOOTSTRAP_MEMBERSHIP_INACTIVE"
        )

    monkeypatch.setattr(
        auth_router,
        "build_workspace_bootstrap_projection",
        _denied,
    )

    app = FastAPI()
    app.include_router(auth_router.router)
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalRepository()

    response = TestClient(app).get(
        "/auth/workspace-bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Workspace access denied."}
    assert "MEMBERSHIP_INACTIVE" not in response.text
    assert "SUPER_ADMIN" not in response.text
    assert '"*"' not in response.text


def test_workspace_bootstrap_http_authority_outage_is_bounded_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Workspace authority infrastructure failures must remain unavailable, not denied."""

    from tools.eos.auth.workspace_bootstrap_projection import (
        WorkspaceBootstrapProjectionError,
    )

    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {
            "identity_id": PRINCIPAL,
            "tenant_id": TENANT,
            "roles": ["FIELD_DEPUTY"],
            "permissions": ["legal:read"],
        }
    )

    outage_codes = (
        "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_UNAVAILABLE",
        "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE",
        "WORKSPACE_BOOTSTRAP_TENANT_UNAVAILABLE",
    )

    app = FastAPI()
    app.include_router(auth_router.router)
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalRepository()

    client = TestClient(app)

    for code in outage_codes:
        def _unavailable(**_kwargs: Any) -> Any:
            raise WorkspaceBootstrapProjectionError(code)

        monkeypatch.setattr(
            auth_router,
            "build_workspace_bootstrap_projection",
            _unavailable,
        )

        response = client.get(
            "/auth/workspace-bootstrap",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 503
        assert response.json() == {
            "detail": "Workspace authority is unavailable."
        }
        assert code not in response.text
