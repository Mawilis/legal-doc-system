"""TITLE: Privileged Factor Currentness Auth HTTP Real-Mongo Certificate.
VERSION: v1.0.0-P3-R3G-S5-A2-AUTH-HTTP-ATOMICITY
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies that the production-mounted OTP HTTP route atomically commits
one canonical session and one interactive factor-currentness event in a real
MongoDB replica-set transaction, and aborts both on post-session failure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_privileged_factor_currentness_auth_http_real_mongo.py
COLLABORATION / OWNERSHIP: Auth router, AuthRegistry, Kernel DB seams, factor
currentness registry, WilsyAPIServer, and local certification replica set.
CERTIFICATION/UPDATE DATE: 2026-10-14.
CHANGELOG:
  v1.0.0-P3-R3G-S5-A2-AUTH-HTTP-ATOMICITY: Adds success, invalid-OTP, and
  post-session transactional-failure proofs through POST /api/auth/verify-otp,
  plus production identity proof for validate-MFA and both OTP aliases.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: UUID-isolated synthetic data only; raw OTP and bearer
material are asserted absent from factor-currentness evidence.
TENANT BOUNDARY: Every credential revision read remains exact tenant/principal scoped.
AUTHORITY BOUNDARY: Security-assurance evidence is not privileged activation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

import inspect
import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pyotp
import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from tools.eos.api import auth_router
from tools.eos.api.server import WilsyAPIServer
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    COLLECTION as FACTOR_COLLECTION,
    PrivilegedFactorVerificationCurrentnessRegistry,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


class _TenantRegistry:
    tenant_id = "tenant-factor-http-cert"

    @classmethod
    def resolve_canonical_tenant(
        cls,
        tenant_reference: object,
        *,
        allow_alias: bool = False,
        session: object = None,
    ) -> object:
        del allow_alias, session
        if tenant_reference != cls.tenant_id:
            raise ValueError("AUTH_TENANT_CANONICAL_INVALID")
        return SimpleNamespace(tenant_id=cls.tenant_id)


class _CertificateAuthRegistry(AuthRegistry):
    """Use canonical AuthRegistry persistence with synthetic admission authority."""

    def __init__(self) -> None:
        super().__init__()
        self.tenant_registry = _TenantRegistry

    def _require_active_principal_authority(
        self,
        principal_id: str,
    ) -> Any:
        return SimpleNamespace(principal_id=principal_id, status="ACTIVE")


class _PostSessionFailureRegistry(_CertificateAuthRegistry):
    """Fail after canonical session insert to exercise real transaction abort."""

    def generate_refresh_token(
        self,
        user_id: str,
        tenant_id: str | None = None,
        *,
        session: Any = None,
    ) -> str:
        del user_id, tenant_id, session
        raise ConnectionFailure("CERTIFICATE_POST_SESSION_FAILURE")


@dataclass(frozen=True)
class _MongoContext:
    client: MongoClient[Any]
    database: Any


@pytest.fixture
def mongo_context() -> Iterator[_MongoContext]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        ) is True
        database = client[
            f"wilsy_factor_http_cert_{uuid.uuid4().hex}"
        ]
        assert database.name != "wilsy"
        PrivilegedFactorVerificationCurrentnessRegistry(
            database[FACTOR_COLLECTION]
        ).ensure_indexes()
        yield _MongoContext(client, database)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _seed(database: Any) -> tuple[str, str, str, int]:
    principal_id = f"WILSYAUTH-{uuid.uuid4()}"
    email = f"factor-{uuid.uuid4().hex}@example.com"
    secret = pyotp.random_base32()
    revision = 7
    database["users"].insert_one(
        {
            "user_id": principal_id,
            "email": email,
            "firstName": "Factor",
            "lastName": "Certificate",
            "role": "CERTIFICATE_USER",
            "permissions": [],
            "tenantId": _TenantRegistry.tenant_id,
            "passwordHash": "not-used-by-otp-certificate",
            "credential_revision": revision,
            "mfaRegistered": True,
            "hasSignedCovenant": False,
        }
    )
    database["otp_secrets"].insert_one(
        {"user_id": principal_id, "secret": secret}
    )
    return principal_id, email, secret, revision


def _http(
    monkeypatch: pytest.MonkeyPatch,
    context: _MongoContext,
    registry: AuthRegistry,
) -> TestClient:
    monkeypatch.setenv(
        "WILSY_JWT_SECRET",
        "a2-certificate-only-secret-with-more-than-thirty-two-bytes",
    )
    monkeypatch.setattr(kernel_db, "get_database", lambda: context.database)
    monkeypatch.setattr(kernel_db, "get_client", lambda: context.client)
    monkeypatch.setattr(auth_router, "get_auth_registry", lambda _tenant: registry)
    app = WilsyAPIServer(reasoning_provider_binding=object()).get_app()
    return TestClient(app)


def _invalid_code(secret: str) -> str:
    current = pyotp.TOTP(secret).now()
    replacement = "0" if current[-1] != "0" else "1"
    return f"{current[:-1]}{replacement}"


def test_verify_otp_commits_session_and_factor_atomically(
    monkeypatch: pytest.MonkeyPatch,
    mongo_context: _MongoContext,
) -> None:
    principal_id, email, secret, revision = _seed(mongo_context.database)
    registry = _CertificateAuthRegistry()
    response = _http(monkeypatch, mongo_context, registry).post(
        "/api/auth/verify-otp",
        json={"email": email, "code": pyotp.TOTP(secret).now()},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["status"] == "AUTHENTICATED"
    bearer = payload["token"]

    session_row = mongo_context.database["sessions"].find_one(
        {"user_id": principal_id}
    )
    factor_row = mongo_context.database[FACTOR_COLLECTION].find_one(
        {"principal_id": principal_id}
    )
    assert session_row is not None
    assert factor_row is not None
    assert factor_row["session_reference"] == session_row["session_reference"]
    assert factor_row["credential_revision"] == revision
    assert factor_row["status"] == "VERIFIED"
    assert str(factor_row["factor_verification_reference"]).startswith(
        "WILSYFACTOR-"
    )
    assert factor_row["factor_verification_reference"] != bearer
    assert secret not in repr(factor_row)
    assert pyotp.TOTP(secret).now() not in repr(factor_row)


def test_invalid_otp_writes_neither_session_nor_factor(
    monkeypatch: pytest.MonkeyPatch,
    mongo_context: _MongoContext,
) -> None:
    principal_id, email, secret, _revision = _seed(mongo_context.database)
    registry = _CertificateAuthRegistry()
    response = _http(monkeypatch, mongo_context, registry).post(
        "/api/auth/verify-otp",
        json={"email": email, "code": _invalid_code(secret)},
    )
    assert response.status_code == 401
    assert mongo_context.database["sessions"].count_documents(
        {"user_id": principal_id}
    ) == 0
    assert mongo_context.database[FACTOR_COLLECTION].count_documents(
        {"principal_id": principal_id}
    ) == 0


def test_post_session_failure_aborts_session_and_factor(
    monkeypatch: pytest.MonkeyPatch,
    mongo_context: _MongoContext,
) -> None:
    principal_id, email, secret, _revision = _seed(mongo_context.database)
    registry = _PostSessionFailureRegistry()
    response = _http(monkeypatch, mongo_context, registry).post(
        "/api/auth/verify-otp",
        json={"email": email, "code": pyotp.TOTP(secret).now()},
    )
    assert response.status_code == 500
    assert mongo_context.database["sessions"].count_documents(
        {"user_id": principal_id}
    ) == 0
    assert mongo_context.database["refresh_tokens"].count_documents(
        {"user_id": principal_id}
    ) == 0
    assert mongo_context.database[FACTOR_COLLECTION].count_documents(
        {"principal_id": principal_id}
    ) == 0


def test_production_route_identities_and_validate_transaction_compatibility() -> None:
    app = WilsyAPIServer(reasoning_provider_binding=object()).get_app()
    mounts = [
        route
        for route in app.routes
        if type(route).__name__ == "_IncludedRouter"
        and getattr(route, "original_router", None) is auth_router.router
    ]
    assert len(mounts) == 1
    prefix = getattr(mounts[0], "include_context").prefix
    bindings = {
        (f"{prefix}{route.path}", method): route.endpoint
        for route in auth_router.router.routes
        if isinstance(route, APIRoute)
        for method in (route.methods or set())
    }
    assert bindings[("/api/auth/verify-otp", "POST")] is auth_router.verify_otp
    assert bindings[("/api/auth/verify-3fa", "POST")] is auth_router.verify_otp
    assert bindings[("/api/auth/validate-mfa-setup", "POST")] is auth_router.validate_mfa_setup
    assert "_create_factor_current_session(" in inspect.getsource(
        auth_router.validate_mfa_setup
    )
    assert not any(
        endpoint is auth_router._create_factor_current_session
        for endpoint in bindings.values()
    )


# ARTIFACT: test_privileged_factor_currentness_auth_http_real_mongo.py
# VERSION: v1.0.0-P3-R3G-S5-A2-AUTH-HTTP-ATOMICITY
# AUTHORITY BOUNDARY: Real persistence and HTTP observation only; no privileged activation or role authority.
# TENANT POSTURE: UUID-isolated disposable database and exact tenant/principal credential reads.
# FAIL-CLOSED POSTURE: Invalid OTP and post-session failure must leave zero durable session/factor rows.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
