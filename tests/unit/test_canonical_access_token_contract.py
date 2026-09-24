"""WILSY OS canonical access-token issuance and verification certificate.

TITLE: Canonical Access-Token Contract Certificate
VERSION: v1.2.0-D19-CANONICAL-TENANT-PRACTICE-PROFILE-PROJECTION-CERT
AUTHORITY: Deterministic token interoperability evidence only.
EPITOME: Proves MFA/login issuance and EOS protected-route verification share
         one cryptographic owner, one secret authority, and one claim contract.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_canonical_access_token_contract.py
COLLABORATION / OWNERSHIP: Exercises AuthRegistry, jwt_provider,
                           get_current_identity, and workspace-bootstrap transport.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.2.0-D19-CANONICAL-TENANT-PRACTICE-PROFILE-PROJECTION-CERT certifies that workspace-bootstrap projects canonical
           tenant alias, industry, region and sector as descriptive practice
           context while continuing to exclude plan/subscription, tax/contact,
           compliance, verification and financial authority. The projection is
           still sourced only after current workspace authority revalidation.
           v1.1.0-D17-LEGAL-PRESENTATION-PERMISSION-PROJECTION-CERT certifies workspace-level Legal
           presentation permissions from the real tenant authorization compositor:
           forged JWT roles/permissions remain excluded, an auditor receives an
           authoritative empty subset, a current LEGAL_PARTNER receives only the
           four bounded Legal Command Center permissions, and granting-role
           authority outage fails bounded 503.
           v1.0.2-R10C2F9C-CANONICAL-ACCESS-TOKEN-CERT-RECONCILIATION reconciles
           protected ACCESS fixtures with the F9 purpose/revision contract while
           preserving server-side principal and workspace authority assertions.
           v1.0.1-R1D-B0F-B4-R2-CLEAN-CHECKOUT-REPAIR removes premature
           legal-acceptance router coupling so this certificate is independently
           runnable from a clean published checkout.
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

from tools.eos.api import auth_router
from tools.eos.auth import authentication, jwt_provider
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepositoryError,
)
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
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

    def resolve(self, principal_id: str, **_kwargs: Any) -> PrincipalAuthority:
        return PrincipalAuthority(principal_id, self.status, 0)


class _MembershipRepository:
    """Exact active membership fixture for workspace permission composition."""

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        **_kwargs: Any,
    ) -> SimpleNamespace:
        return SimpleNamespace(
            principal_id=principal_id,
            tenant_id=tenant_id,
            status=TenantMembershipStatus.ACTIVE,
            revision=7,
        )


class _WorkspaceRoleReader:
    """Composite business/final-role fixture matching tenant authorization HTTP."""

    def __init__(
        self,
        *,
        business_role: str,
        active_roles: tuple[str, ...] = (),
        unavailable: bool = False,
    ) -> None:
        self.business_role = business_role
        self.active_roles = frozenset(active_roles)
        self.unavailable = unavailable

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        **_kwargs: Any,
    ) -> SimpleNamespace:
        if self.unavailable:
            raise RoleAssignmentRepositoryError(
                "ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE"
            )
        if role_id.startswith("tenant_"):
            if role_id != self.business_role:
                raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
            return SimpleNamespace(
                principal_id=principal_id,
                tenant_id=tenant_id,
                business_role=role_id,
                status=TenantBusinessRoleStatus.ACTIVE,
                revision=11,
            )
        if role_id in self.active_roles:
            return SimpleNamespace(
                principal_id=principal_id,
                tenant_id=tenant_id,
                role_id=role_id,
                status=RoleAssignmentStatus.ACTIVE,
                revision=13,
            )
        raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")


def _override_workspace_dependencies(
    app: FastAPI,
    *,
    business_role: str = "tenant_auditor",
    active_roles: tuple[str, ...] = (),
    unavailable: bool = False,
) -> None:
    app.dependency_overrides[
        authentication.get_principal_authority_repository
    ] = lambda: _PrincipalRepository()
    app.dependency_overrides[
        auth_router.get_tenant_membership_repository
    ] = lambda: _MembershipRepository()
    app.dependency_overrides[
        auth_router.get_tenant_authority_role_repository
    ] = lambda: _WorkspaceRoleReader(
        business_role=business_role,
        active_roles=active_roles,
        unavailable=unavailable,
    )


class _CredentialRevisionRegistry:
    """Deterministic durable-revision fixture for the real authentication seam."""

    def __init__(self, calls: list[tuple[str, str]] | None = None, revision: int = 0) -> None:
        self.calls = calls if calls is not None else []
        self.revision = revision

    def get_credential_revision(self, tenant_id: str, principal_id: str) -> int:
        self.calls.append((tenant_id, principal_id))
        return self.revision


def _install_durable_revision(
    monkeypatch: pytest.MonkeyPatch,
    calls: list[tuple[str, str]] | None = None,
    revision: int = 0,
) -> _CredentialRevisionRegistry:
    """Bind authentication to a recording, matching durable revision authority."""

    registry = _CredentialRevisionRegistry(calls, revision)
    monkeypatch.setattr(authentication, "AuthRegistry", lambda: registry)
    return registry


def _request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": []})


def _credentials(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


def _run_identity(
    token: str,
    repository: _PrincipalRepository,
    monkeypatch: pytest.MonkeyPatch,
    durable_calls: list[tuple[str, str]] | None = None,
) -> SovereignIdentity:
    _install_durable_revision(monkeypatch, durable_calls)
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
    durable_calls: list[tuple[str, str]] = []
    _install_durable_revision(monkeypatch, durable_calls)
    token = jwt_provider.create_access_token(
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": ["FIELD_DEPUTY"], "permissions": ["legal:read"]},
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=0,
    )
    identity = _run_identity(token, _PrincipalRepository(), monkeypatch, durable_calls)
    assert identity.identity_id == PRINCIPAL
    assert identity.tenant_id == TENANT
    assert identity.status is PrincipalStatus.ACTIVE
    assert durable_calls == [(TENANT, PRINCIPAL)]


def test_mfa_response_token_is_immediately_accepted_by_canonical_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    issuer = AuthRegistry(cast(Any, _TenantRegistry()))
    durable_calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        issuer,
        "get_credential_revision",
        lambda tenant_id, principal_id, **_kwargs: durable_calls.append(
            (tenant_id, principal_id)
        )
        or 0,
    )
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
                token=issuer.generate_access_jwt(
                    user.id, user.tenantId, user.role, user.permissions
                )
            )

    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: _MfaRegistry())
    response = asyncio.run(
        auth_router.verify_otp(VerifyOTPRequest(email=user.email, code="123456"))
    )
    assert response.token is not None
    payload = jwt_provider.verify_access_token(response.token)
    assert payload is not None
    assert payload["token_purpose"] == "ACCESS"
    assert payload["credential_revision"] == 0
    assert _run_identity(response.token, _PrincipalRepository(), monkeypatch).identity_id == PRINCIPAL
    assert durable_calls == [(TENANT, PRINCIPAL)]


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
        {"identity_id": PRINCIPAL, "tenant_id": TENANT, "roles": [], "permissions": []},
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=0,
    )
    with pytest.raises(Exception):
        _run_identity(fresh, _PrincipalRepository(PrincipalStatus.SUSPENDED), monkeypatch)


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
        },
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=0,
    )
    _install_durable_revision(monkeypatch)

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
                alias="canonical-law",
                region="ZA",
                sector="Law",
                subscription_tier="SOVEREIGN_ENTERPRISE",
                verified=True,
                compliance_flags={"certified": True},
                organization=SimpleNamespace(
                    organization_name="Canonical Tenant",
                    legal_name="Canonical Tenant (Pty) Ltd",
                    industry="Legal Services",
                    plan="SOVEREIGN_ENTERPRISE",
                    tax_id="FORBIDDEN-TAX-ID",
                    contact_email="forbidden@example.invalid",
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
    _override_workspace_dependencies(app)

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
            "legalPermissions": [],
            "tenant": {
                "tenantId": TENANT,
                "name": "Canonical Tenant",
                "legalName": "Canonical Tenant (Pty) Ltd",
                "alias": "canonical-law",
                "industry": "Legal Services",
                "region": "ZA",
                "sector": "Law",
                "status": "ACTIVE",
            },
        },
    }

    serialized = response.json()
    assert "roles" not in serialized["user"]
    assert "permissions" not in serialized["user"]
    assert "role" not in serialized["user"]
    assert serialized["workspace"]["legalPermissions"] == []
    tenant_payload = serialized["workspace"]["tenant"]
    for forbidden in (
        "plan",
        "subscriptionTier",
        "subscription_tier",
        "taxId",
        "tax_id",
        "contactEmail",
        "contact_email",
        "complianceFlags",
        "compliance_flags",
        "verified",
        "operatingModel",
        "operating_model",
    ):
        assert forbidden not in tenant_payload

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
        },
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=0,
    )
    _install_durable_revision(monkeypatch)

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
    _override_workspace_dependencies(app)

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
        },
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=0,
    )
    _install_durable_revision(monkeypatch)

    outage_codes = (
        "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_UNAVAILABLE",
        "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE",
        "WORKSPACE_BOOTSTRAP_TENANT_UNAVAILABLE",
        "WORKSPACE_BOOTSTRAP_PERMISSION_AUTHORITY_UNAVAILABLE",
    )

    app = FastAPI()
    app.include_router(auth_router.router)
    _override_workspace_dependencies(app)

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


def test_workspace_bootstrap_projects_exact_authorized_legal_permissions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only current full tenant authorization may become Legal UI permission hints."""

    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {
            "identity_id": PRINCIPAL,
            "tenant_id": TENANT,
            "email": "principal@example.com",
            "roles": ["SUPER_ADMIN"],
            "permissions": ["*"],
        },
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=0,
    )
    _install_durable_revision(monkeypatch)

    def _projection(*, identity: SovereignIdentity, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(
            principal_id=identity.identity_id,
            email="principal@example.com",
            tenant_id=identity.tenant_id,
            business_role="tenant_legal_partner",
            membership_revision=7,
            business_role_revision=11,
            tenant=SimpleNamespace(
                tenant_id=TENANT,
                status="ACTIVE",
                organization=SimpleNamespace(
                    organization_name="Canonical Law",
                    legal_name="Canonical Law Inc.",
                ),
            ),
        )

    monkeypatch.setattr(
        auth_router,
        "build_workspace_bootstrap_projection",
        _projection,
    )

    app = FastAPI()
    app.include_router(auth_router.router)
    _override_workspace_dependencies(
        app,
        business_role="tenant_legal_partner",
        active_roles=("LEGAL_PARTNER",),
    )

    response = TestClient(app).get(
        "/auth/workspace-bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["workspace"]["businessRole"] == "tenant_legal_partner"
    assert payload["workspace"]["legalPermissions"] == [
        "legal_operations:billing:read",
        "legal_operations:instruction:write",
        "legal_operations:invoice:read",
        "legal_operations:return:write",
    ]
    assert "permissions" not in payload["user"]
    assert "roles" not in payload["user"]
    assert "*" not in json.dumps(payload["workspace"]["legalPermissions"])


def test_workspace_bootstrap_permission_authority_outage_is_bounded_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Final-role authority outage cannot be mistaken for an empty grant set."""

    monkeypatch.setenv("WILSY_JWT_SECRET", SECRET)
    token = jwt_provider.create_access_token(
        {
            "identity_id": PRINCIPAL,
            "tenant_id": TENANT,
            "roles": [],
            "permissions": [],
        },
        token_purpose=jwt_provider.TokenPurpose.ACCESS,
        credential_revision=0,
    )
    _install_durable_revision(monkeypatch)

    def _projection(*, identity: SovereignIdentity, **_kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(
            principal_id=identity.identity_id,
            email="principal@example.com",
            tenant_id=identity.tenant_id,
            business_role="tenant_legal_partner",
            membership_revision=7,
            business_role_revision=11,
            tenant=SimpleNamespace(
                tenant_id=TENANT,
                status="ACTIVE",
                organization=SimpleNamespace(
                    organization_name="Canonical Law",
                    legal_name="Canonical Law Inc.",
                ),
            ),
        )

    monkeypatch.setattr(
        auth_router,
        "build_workspace_bootstrap_projection",
        _projection,
    )

    app = FastAPI()
    app.include_router(auth_router.router)
    _override_workspace_dependencies(
        app,
        business_role="tenant_legal_partner",
        active_roles=("LEGAL_PARTNER",),
        unavailable=True,
    )

    response = TestClient(app).get(
        "/auth/workspace-bootstrap",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Workspace authority is unavailable."
    }
    assert "ROLE_ASSIGNMENT" not in response.text


# ARTIFACT: test_canonical_access_token_contract.py
# VERSION: v1.2.0-D19-CANONICAL-TENANT-PRACTICE-PROFILE-PROJECTION-CERT
# AUTHORITY BOUNDARY: deterministic token interoperability plus bounded server-owned workspace Legal permission and descriptive canonical tenant practice-profile projection evidence only
# TENANT POSTURE: exact tenant claim is preserved; durable membership remains downstream
# FAIL-CLOSED POSTURE: missing configuration, malformed claims, expiry, signatures, inactive principals, workspace authority drift, permission-authority outage, or attempts to infer plan/subscription/operating-model authority deny or remain excluded
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
