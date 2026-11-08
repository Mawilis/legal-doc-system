"""HTTP-to-real-Mongo certificate for the tenant-neutral SYSTEM login journey.

The test mounts the production global-auth router and uses a disposable MongoDB
replica set for credential, principal, permission, workforce, MFA challenge,
factor replay state, session, refresh, and revocation persistence. Only the
test decryptor is synthetic; the TOTP verifier and all persistence paths are
real. No tenant membership or SYSTEM authority is fabricated by browser input.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import httpx
import pyotp
import pytest
from fastapi import Depends, FastAPI
from pymongo import MongoClient

from tools.eos.api import global_principal_auth_router as auth_router
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.global_principal_system_session_authority import (
    CHALLENGE_COLLECTION,
    REFRESH_COLLECTION,
    SESSION_COLLECTION,
    GlobalPrincipalSystemMfaChallengeService,
    GlobalPrincipalSystemSessionAuthority,
)
from tools.eos.auth.global_principal_totp_verifier import (
    COLLECTION as FACTOR_COLLECTION,
    GlobalPrincipalTotpVerifier,
)
from tools.eos.auth.current_system_permission_possession import (
    CurrentSystemPermissionPossessionResolver,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_credential import PrincipalCredential
from tools.eos.auth.principal_credential_repository import PrincipalCredentialRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.system_permission_assignment_registry import (
    COLLECTION as ASSIGNMENT_COLLECTION,
    SystemPermissionAssignmentRegistry,
)
from tools.eos.kernel import db as kernel_db
from tools.eos.system_services.eos_authorizer import SystemServicesEosAuthorizer
from tools.eos.system_services.support_case_registry import (
    CASE_COLLECTION,
    EVENT_COLLECTION,
    SupportCaseRegistry,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import workforce_relationship_registry as workforce_registry


URI = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI", "")
PASSWORD = "Synthetic-System-Password!482"
SECRET = "JBSWY3DPEHPK3PXP"
EMAIL = "system-http-certificate@example.test"
PERMISSION = "system_services:queue:read"


def _request(app: FastAPI, method: str, path: str, *, payload: dict[str, Any] | None = None,
             headers: dict[str, str] | None = None) -> httpx.Response:
    async def invoke() -> httpx.Response:
        transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
        async with httpx.AsyncClient(transport=transport, base_url="http://system-cert.test") as client:
            return await client.request(method, path, json=payload, headers=headers)
    return asyncio.run(invoke())


@pytest.fixture()
def system_http_mongo(monkeypatch: pytest.MonkeyPatch):
    if not URI:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=5000, retryWrites=True, tz_aware=True)
    expected_replica_set = os.getenv(
        "TEST_GLOBAL_PRINCIPAL_MONGO_REPLICA_SET", "wilsyGlobalPrincipalCertRS"
    )
    actual_replica_set = client.admin.command("hello").get("setName")
    if actual_replica_set != expected_replica_set:
        client.close()
        pytest.fail(
            f"wrong certification replica set: expected {expected_replica_set!r}, "
            f"received {actual_replica_set!r}"
        )
    database_name = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_DATABASE")
    if database_name != "wilsy_global_principal_mfa_cert":
        client.close()
        pytest.fail(
            "TEST_GLOBAL_PRINCIPAL_MONGO_DATABASE must be "
            "'wilsy_global_principal_mfa_cert'"
        )
    database = client[database_name]
    suffix = uuid.uuid4().hex
    principal_id = "system-http-principal-" + uuid.uuid4().hex
    platform_scope_id = "platform-cert-" + uuid.uuid4().hex
    now = datetime.now(timezone.utc).replace(microsecond=0)

    principals = database[f"principal_authorities_cert_{suffix}"]
    credentials = database[f"principal_credentials_cert_{suffix}"]
    factors = database[f"{FACTOR_COLLECTION}_cert_{suffix}"]
    challenges = database[f"{CHALLENGE_COLLECTION}_cert_{suffix}"]
    sessions = database[f"{SESSION_COLLECTION}_cert_{suffix}"]
    refresh_tokens = database[f"{REFRESH_COLLECTION}_cert_{suffix}"]
    assignment_collection = database[f"{ASSIGNMENT_COLLECTION}_cert_{suffix}"]
    assignments = SystemPermissionAssignmentRegistry(assignment_collection)
    workforce = database[f"{workforce_registry.COLLECTION_NAME}_cert_{suffix}"]

    PrincipalAuthorityRepository.ensure_indexes(principals)
    PrincipalCredentialRepository.ensure_indexes(credentials)
    GlobalPrincipalTotpVerifier.ensure_indexes(factors)
    GlobalPrincipalSystemMfaChallengeService.ensure_indexes(challenges)
    GlobalPrincipalSystemSessionAuthority.ensure_indexes(sessions, refresh_tokens)
    assignments.ensure_indexes()
    workforce_registry.ensure_indexes(workforce)

    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), principals
    )
    PrincipalCredentialRepository.insert(
        PrincipalCredential(
            principal_id=principal_id,
            normalized_email=EMAIL,
            password_hash=bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(rounds=4)).decode(),
            credential_revision=4,
            mfa_enabled=True,
        ),
        credentials,
    )
    factors.insert_one({
        "principal_id": principal_id,
        "status": "ACTIVE",
        "credential_revision": 4,
        "encrypted_secret": "test-envelope-only",
    })

    case_registry = SupportCaseRegistry(
        cases=database[f"{CASE_COLLECTION}_cert_{suffix}"],
        events=database[f"{EVENT_COLLECTION}_cert_{suffix}"],
    )
    case_registry.ensure_indexes()

    possession = CurrentSystemPermissionPossessionResolver(
        principal_collection=principals,
        assignment_registry=assignments,
    )
    authorizer = SystemServicesEosAuthorizer(
        possession_resolver=possession,
        workforce_collection=workforce,
        platform_scope_id=platform_scope_id,
    )
    with client.start_session() as seed_session:
        seed_session.start_transaction()
        assignment = SystemPermissionAssignment.assign(
            assignment_id="system-assignment-" + uuid.uuid4().hex,
            principal_id=principal_id,
            permission_id=PERMISSION,
            assigned_by_principal_id="independent-platform-approver",
            assigned_at=now,
            assignment_evidence_reference="test-evidence:system-http-assignment",
        )
        assignments.create_or_replay(
            assignment,
            idempotency_key="system-http-assignment-" + uuid.uuid4().hex,
            session=seed_session,
        )
        relationship = WorkforceRelationship(
            relationship_id="workforce-" + uuid.uuid4().hex,
            revision=1,
            scope_kind=WorkforceScopeKind.PLATFORM,
            scope_id=platform_scope_id,
            principal_id=principal_id,
            relationship_type=WorkforceRelationshipType.EMPLOYEE,
            status=WorkforceRelationshipStatus.ACTIVE,
            effective_from=now - timedelta(days=1),
            effective_until=None,
            status_effective_at=now - timedelta(days=1),
            reason_reference="test-evidence:active-platform-workforce",
            supersedes_fingerprint=None,
        )
        workforce_registry.persist_revision(
            relationship, collection=workforce, session=seed_session
        )
        seed_session.commit_transaction()

    verifier = GlobalPrincipalTotpVerifier(
        collection=factors,
        decrypt_secret=lambda envelope, *, principal_id, credential_revision, expected_principal_id=principal_id: (
            SECRET if envelope == "test-envelope-only" and principal_id == expected_principal_id
            and credential_revision == 4 else ""
        ),
    )

    monkeypatch.setenv("WILSY_JWT_SECRET", "test-only-secret-that-is-not-a-production-key")
    monkeypatch.setattr(kernel_db, "get_database", lambda: database)
    monkeypatch.setattr(auth_router, "get_client", lambda: client)
    monkeypatch.setattr(auth_router, "get_database", lambda: database)

    # Keep HTTP certification isolated to this fixture's UUID-suffixed
    # principal and credential collections while exercising real auth logic.
    from tools.eos.auth.principal_credential_authentication import (
        authenticate_global_principal as _authenticate_global_principal,
    )

    class _CredentialRepository:
        def get_by_email(self, email, *, session=None):
            return PrincipalCredentialRepository.get_by_email(
                email, credentials, session=session
            )

    class _PrincipalRepository:
        def get(self, requested_principal_id, *, session=None):
            return PrincipalAuthorityRepository.get(
                requested_principal_id, principals, session=session
            )

    def _authenticate_isolated(**kwargs):
        return _authenticate_global_principal(
            **kwargs,
            credential_repository=_CredentialRepository(),
            principal_repository=_PrincipalRepository(),
        )

    monkeypatch.setattr(
        auth_router, "authenticate_global_principal", _authenticate_isolated
    )

    # Route all MFA and SYSTEM session persistence through this fixture's
    # isolated collections; do not change production collection names.
    monkeypatch.setattr(
        auth_router, "GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION", factors.name
    )
    monkeypatch.setattr(
        auth_router, "SYSTEM_MFA_CHALLENGE_COLLECTION", challenges.name
    )
    monkeypatch.setattr(
        auth_router, "SYSTEM_SESSION_COLLECTION", sessions.name
    )
    monkeypatch.setattr(
        auth_router, "SYSTEM_REFRESH_COLLECTION", refresh_tokens.name
    )

    from tools.eos.auth import authentication
    monkeypatch.setattr(authentication, "get_client", lambda: client)
    monkeypatch.setattr(authentication, "get_database", lambda: database)
    monkeypatch.setattr(
        authentication, "SYSTEM_SESSION_COLLECTION", sessions.name
    )

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(auth_router.router)
    app.state.global_principal_auth_indexes_ready = True
    app.state.global_principal_session_indexes_ready = True
    app.state.global_principal_mfa_factor_indexes_ready = True
    app.state.global_principal_system_session_indexes_ready = True
    app.state.system_services_authority_ready = True
    app.state.system_services_case_indexes_ready = True
    app.state.system_services_authorizer = authorizer
    app.state.global_principal_totp_verifier = verifier

    @app.get("/certificate/protected")
    async def protected(identity=Depends(get_current_identity)):
        return {"principal_id": identity.identity_id, "tenant_id": identity.tenant_id,
                "roles": identity.roles, "permissions": identity.permissions}

    try:
        yield {
            "client": client, "database": database, "app": app,
            "principal_id": principal_id, "email": EMAIL, "password": PASSWORD,
            "now": now, "factors": factors, "challenges": challenges,
            "sessions": sessions, "refresh_tokens": refresh_tokens,
        }
    finally:
        for collection in (
            principals, credentials, factors, challenges, sessions, refresh_tokens,
            assignment_collection, workforce,
            database[f"{CASE_COLLECTION}_cert_{suffix}"],
            database[f"{EVENT_COLLECTION}_cert_{suffix}"],
        ):
            collection.drop()
        client.close()


def _login(state):
    response = _request(
        state["app"], "POST", "/auth/global/login",
        payload={"email": state["email"], "password": state["password"]},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "MFA_REQUIRED"
    assert body["scope"] == "SYSTEM"
    assert body["workspace_id"] == "SYSTEM_SERVICES"
    return body


def _valid_code():
    return pyotp.TOTP(SECRET).now()


def test_real_http_system_login_mfa_access_refresh_replay_logout_and_tenant_header_isolation(system_http_mongo):
    state = system_http_mongo
    challenge = _login(state)
    authenticated = _request(
        state["app"], "POST", "/auth/global/verify-mfa",
        payload={"mfa_challenge": challenge["mfa_challenge"], "code": _valid_code()},
    )
    assert authenticated.status_code == 200, authenticated.text
    tokens = authenticated.json()
    assert tokens["status"] == "AUTHENTICATED"
    assert tokens["scope"] == "SYSTEM"
    assert tokens["principal_id"] == state["principal_id"]
    assert tokens["workspace_id"] == "SYSTEM_SERVICES"
    assert state["challenges"].count_documents({
        "principal_id": state["principal_id"],
        "consumed_at": {"$ne": None},
    }) == 1
    assert state["sessions"].count_documents({
        "principal_id": state["principal_id"],
        "revoked_at": None,
    }) == 1
    assert state["refresh_tokens"].count_documents({
        "principal_id": state["principal_id"],
        "consumed_at": None,
        "revoked_at": None,
    }) == 1
    active_session = state["sessions"].find_one({
        "principal_id": state["principal_id"],
        "revoked_at": None,
    })
    active_refresh = state["refresh_tokens"].find_one({
        "principal_id": state["principal_id"],
        "consumed_at": None,
        "revoked_at": None,
    })
    assert active_session is not None and active_refresh is not None
    assert active_session["credential_revision"] == 4
    assert active_refresh["session_reference"] == active_session["session_reference"]

    headers = {
        "Authorization": "Bearer " + tokens["access_token"],
        "X-Tenant-ID": "tenant-attacker-controlled",
    }
    protected = _request(state["app"], "GET", "/certificate/protected", headers=headers)
    assert protected.status_code == 200, protected.text
    assert protected.json() == {
        "principal_id": state["principal_id"],
        "tenant_id": "SYSTEM",
        "roles": ["SYSTEM_SERVICES"],
        "permissions": [],
    }

    refreshed = _request(
        state["app"], "POST", "/auth/global/refresh",
        payload={"refresh_token": tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200, refreshed.text
    successor = refreshed.json()
    assert successor["status"] == "REFRESHED"
    assert successor["refresh_token"] != tokens["refresh_token"]

    replay = _request(
        state["app"], "POST", "/auth/global/refresh",
        payload={"refresh_token": tokens["refresh_token"]},
    )
    assert replay.status_code == 401

    successor_headers = {"Authorization": "Bearer " + successor["access_token"]}
    still_current = _request(
        state["app"], "GET", "/certificate/protected", headers=successor_headers
    )
    assert still_current.status_code == 200

    logout = _request(
        state["app"], "POST", "/auth/global/logout", headers=successor_headers
    )
    assert logout.status_code == 200, logout.text
    assert logout.json()["status"] == "SIGNED_OUT"
    denied = _request(
        state["app"], "GET", "/certificate/protected", headers=successor_headers
    )
    assert denied.status_code == 401
    assert state["sessions"].count_documents({
        "principal_id": state["principal_id"], "revoked_at": {"$ne": None}
    }) == 1


def test_real_http_system_failed_mfa_does_not_consume_challenge_or_totp_step(system_http_mongo):
    state = system_http_mongo
    challenge = _login(state)
    valid = _valid_code()
    invalid = f"{(int(valid) + 100000) % 1000000:06d}"
    failed = _request(
        state["app"], "POST", "/auth/global/verify-mfa",
        payload={"mfa_challenge": challenge["mfa_challenge"], "code": invalid},
    )
    assert failed.status_code == 401
    challenge_row = state["challenges"].find_one({"principal_id": state["principal_id"]})
    factor_row = state["factors"].find_one({"principal_id": state["principal_id"]})
    assert challenge_row["consumed_at"] is None
    assert factor_row.get("last_accepted_step") is None

    success = _request(
        state["app"], "POST", "/auth/global/verify-mfa",
        payload={"mfa_challenge": challenge["mfa_challenge"], "code": valid},
    )
    assert success.status_code == 200, success.text


def test_real_http_system_expired_mfa_challenge_is_rejected(system_http_mongo):
    state = system_http_mongo
    challenge = _login(state)
    state["challenges"].update_one(
        {"principal_id": state["principal_id"]},
        {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)}},
    )
    response = _request(
        state["app"], "POST", "/auth/global/verify-mfa",
        payload={"mfa_challenge": challenge["mfa_challenge"], "code": _valid_code()},
    )
    assert response.status_code == 401
    assert state["sessions"].count_documents({"principal_id": state["principal_id"]}) == 0


def test_real_http_system_verification_failure_rolls_back_factor_and_challenge_writes(
    system_http_mongo, monkeypatch: pytest.MonkeyPatch
):
    state = system_http_mongo
    challenge = _login(state)
    original = GlobalPrincipalSystemSessionAuthority.issue_after_mfa

    def fail_after_mfa(self, *args, **kwargs):
        raise RuntimeError("SIMULATED_SESSION_ISSUANCE_INTERRUPTION")

    monkeypatch.setattr(
        GlobalPrincipalSystemSessionAuthority, "issue_after_mfa", fail_after_mfa
    )
    interrupted = _request(
        state["app"], "POST", "/auth/global/verify-mfa",
        payload={"mfa_challenge": challenge["mfa_challenge"], "code": _valid_code()},
    )
    assert interrupted.status_code == 500

    challenge_row = state["challenges"].find_one({"principal_id": state["principal_id"]})
    factor_row = state["factors"].find_one({"principal_id": state["principal_id"]})
    assert challenge_row["consumed_at"] is None
    assert factor_row.get("last_accepted_step") is None
    assert state["sessions"].count_documents({"principal_id": state["principal_id"]}) == 0

    monkeypatch.setattr(
        GlobalPrincipalSystemSessionAuthority, "issue_after_mfa", original
    )
    recovered = _request(
        state["app"], "POST", "/auth/global/verify-mfa",
        payload={"mfa_challenge": challenge["mfa_challenge"], "code": _valid_code()},
    )
    assert recovered.status_code == 200, recovered.text
