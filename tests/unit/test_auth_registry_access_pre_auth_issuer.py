"""WILSY OS direct certificate for the F6 issuer seams.

TITLE: AuthRegistry ACCESS and PRE_AUTH Issuer Direct Certificate
VERSION: v1.0.0-R10C2F7-AUTH-REGISTRY-ACCESS-PREAUTH-ISSUER-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies the explicit AuthRegistry ACCESS and PRE_AUTH
         issuer boundaries without changing production or contacting MongoDB.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_auth_registry_access_pre_auth_issuer.py
COLLABORATION / OWNERSHIP: Uses deterministic in-memory collections and the
                           frozen JWT provider; no external state is accessed.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2F7-AUTH-REGISTRY-ACCESS-PREAUTH-ISSUER-CERT — Certifies fresh
    durable credential-revision binding for ACCESS issuance, explicit PRE_AUTH
    issuance without a revision read, transitional generic compatibility,
    create_session propagation, tenant isolation, and authority boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identities, hashes, sessions, and token
                            values only; diagnostics never emit bearer material.
TENANT BOUNDARY: Every durable revision read is exact tenant plus principal;
                 issuer claims remain projections pending downstream admission.
AUTHORITY BOUNDARY: AuthRegistry issuer seams only; jwt_provider owns signing,
                    callers own sessions and transactions, and no reset or
                    credential-comparison authority is activated here.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import ast
import inspect
from datetime import datetime
from types import SimpleNamespace
from typing import Any, cast

import pytest
from bson import ObjectId

from tools.eos.auth import jwt_provider
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.saas.auth import auth_registry as auth_registry_module
from tools.eos.saas.auth.auth_registry import (
    CREDENTIAL_REVISION_MAX,
    AuthRegistry,
    AuthRegistryTenantError,
)
from tools.eos.saas.domain.auth import User


class _CollectionResult:
    def __init__(self, *, deleted_count: int = 0) -> None:
        self.deleted_count = deleted_count


class _RecordingCollection:
    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = [dict(document) for document in (documents or [])]
        self.calls: list[tuple[str, Any, dict[str, Any]]] = []

    def find_one(self, query: dict[str, Any], **kwargs: Any) -> dict[str, Any] | None:
        self.calls.append(("find_one", dict(query), dict(kwargs)))
        for document in self.documents:
            matches = True
            for key, expected in query.items():
                if isinstance(expected, dict) and "$exists" in expected:
                    if (key in document) != expected["$exists"]:
                        matches = False
                elif document.get(key) != expected:
                    matches = False
            if matches:
                return dict(document)
        return None

    def insert_one(self, document: dict[str, Any], **kwargs: Any) -> _CollectionResult:
        self.calls.append(("insert_one", dict(document), dict(kwargs)))
        self.documents.append(dict(document))
        return _CollectionResult()


class _RecordingDatabase:
    def __init__(self, user_documents: list[dict[str, Any]]) -> None:
        self.collections = {
            "users": _RecordingCollection(user_documents),
            "sessions": _RecordingCollection(),
            "refresh_tokens": _RecordingCollection(),
            "principal_authorities": _RecordingCollection(),
            "otp_secrets": _RecordingCollection(),
            "tenants": _RecordingCollection(),
        }

    def __getitem__(self, name: str) -> _RecordingCollection:
        return self.collections[name]


class _TenantRegistry:
    @staticmethod
    def resolve_canonical_tenant(value: object, allow_alias: bool = False) -> SimpleNamespace:
        if value not in {"TENANT-ONE", "TENANT-TWO"}:
            raise ValueError("tenant is not canonical")
        return SimpleNamespace(tenant_id=value)


class _RecordingSession:
    def __init__(self) -> None:
        self.started = 0
        self.committed = 0
        self.aborted = 0
        self.retried = 0


def _user_document(revision: object = 17) -> dict[str, Any]:
    return {
        "user_id": "user-1",
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "email": "synthetic@wilsyos.org",
        "firstName": "Synthetic",
        "lastName": "Principal",
        "role": "USER",
        "permissions": ["legal:read"],
        "tenantId": "TENANT-ONE",
        "passwordHash": "bcrypt-synthetic-value",
        "credential_revision": revision,
        "mfaRegistered": False,
        "hasSignedCovenant": False,
    }


def _registry_fixture(
    monkeypatch: pytest.MonkeyPatch,
    *,
    revision: object = 17,
    user_documents: list[dict[str, Any]] | None = None,
) -> tuple[AuthRegistry, _RecordingDatabase]:
    database = _RecordingDatabase(user_documents or [_user_document(revision)])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    return AuthRegistry(cast(Any, _TenantRegistry)), database


def _provider_recorder(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def record(
        identity_data: dict[str, Any],
        expires_in_seconds: int = 86400,
        *,
        token_purpose: Any = None,
        credential_revision: int | None = None,
    ) -> str:
        calls.append(
            {
                "identity_data": dict(identity_data),
                "expires_in_seconds": expires_in_seconds,
                "token_purpose": token_purpose,
                "credential_revision": credential_revision,
            }
        )
        return "synthetic-provider-token"

    monkeypatch.setattr(auth_registry_module, "create_access_token", record)
    return calls


def test_public_issuer_signatures_are_exact() -> None:
    access = inspect.signature(AuthRegistry.generate_access_jwt)
    pre_auth = inspect.signature(AuthRegistry.generate_pre_auth_jwt)
    generic = inspect.signature(AuthRegistry.generate_jwt)
    session_creation = inspect.signature(AuthRegistry.create_session)
    assert list(access.parameters) == ["self", "user_id", "tenant_id", "role", "permissions", "session"]
    assert access.parameters["session"].kind is inspect.Parameter.KEYWORD_ONLY
    assert access.parameters["session"].default is None
    assert list(pre_auth.parameters) == ["self", "user_id", "tenant_id", "role", "permissions"]
    assert list(generic.parameters) == ["self", "user_id", "tenant_id", "role", "permissions"]
    assert list(session_creation.parameters) == ["self", "user", "session"]
    assert session_creation.parameters["session"].kind is inspect.Parameter.KEYWORD_ONLY
    assert session_creation.parameters["session"].default is None


@pytest.mark.parametrize("revision", [0, 17, CREDENTIAL_REVISION_MAX])
def test_access_passes_exact_durable_revision_to_provider(
    monkeypatch: pytest.MonkeyPatch, revision: int,
) -> None:
    registry, database = _registry_fixture(monkeypatch, revision=revision)
    calls = _provider_recorder(monkeypatch)
    sentinel = _RecordingSession()
    token = registry.generate_access_jwt(
        "user-1", "TENANT-ONE", "USER", ["legal:read"], session=sentinel
    )
    assert token == "synthetic-provider-token"
    assert calls[0]["token_purpose"] is jwt_provider.TokenPurpose.ACCESS
    assert calls[0]["credential_revision"] == revision
    assert calls[0]["identity_data"] == {
        "identity_id": "user-1",
        "tenant_id": "TENANT-ONE",
        "roles": ["USER"],
        "permissions": ["legal:read"],
    }
    assert database.collections["users"].calls[-1][2]["session"] is sentinel


def test_access_caller_cannot_assert_revision_or_bypass_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry, _database = _registry_fixture(monkeypatch, revision=9)
    with pytest.raises(TypeError):
        cast(Any, registry.generate_access_jwt)(
            "user-1", "TENANT-ONE", "USER", [], credential_revision=3
        )


def test_access_uses_fresh_durable_revision_over_stale_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry, _database = _registry_fixture(monkeypatch, revision=9)
    calls = _provider_recorder(monkeypatch)
    stale_snapshot_revision = 3
    observed: list[tuple[str, str, Any]] = []
    original = registry.get_credential_revision

    def record_revision(tenant_id: str, user_id: str, *, session: Any = None) -> int:
        observed.append((tenant_id, user_id, session))
        return original(tenant_id, user_id, session=session)

    monkeypatch.setattr(registry, "get_credential_revision", record_revision)
    registry.generate_access_jwt("user-1", "TENANT-ONE", "USER", [])
    assert stale_snapshot_revision != calls[0]["credential_revision"]
    assert calls[0]["credential_revision"] == 9
    assert observed[0][:2] == ("TENANT-ONE", "user-1")


def test_access_revision_read_is_exact_tenant_and_user_scoped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry, database = _registry_fixture(monkeypatch, revision=17)
    _provider_recorder(monkeypatch)
    registry.generate_access_jwt("user-1", "TENANT-ONE", "USER", [])
    query = database.collections["users"].calls[-1][1]
    assert query == {"user_id": "user-1", "tenantId": "TENANT-ONE"}
    assert "email" not in query and "username" not in query and "_id" not in query


@pytest.mark.parametrize(
    "revision, tenant_id, user_id",
    [("malformed", "TENANT-ONE", "user-1"), (17, "TENANT-TWO", "user-1"), (17, "TENANT-ONE", "missing")],
)
def test_access_fail_closed_for_malformed_missing_or_cross_tenant_identity(
    monkeypatch: pytest.MonkeyPatch,
    revision: object,
    tenant_id: str,
    user_id: str,
) -> None:
    registry, _database = _registry_fixture(monkeypatch, revision=revision)
    calls = _provider_recorder(monkeypatch)
    with pytest.raises(AuthRegistryTenantError):
        registry.generate_access_jwt(user_id, tenant_id, "USER", [])
    assert calls == []


def test_access_fail_closed_when_revision_authority_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry, _database = _registry_fixture(monkeypatch, revision=17)
    calls = _provider_recorder(monkeypatch)

    def unavailable(*_args: Any, **_kwargs: Any) -> int:
        raise AuthRegistryTenantError("AUTH_CREDENTIAL_REVISION_UNAVAILABLE")

    monkeypatch.setattr(registry, "get_credential_revision", unavailable)
    with pytest.raises(AuthRegistryTenantError):
        registry.generate_access_jwt("user-1", "TENANT-ONE", "USER", [])
    assert calls == []


def test_access_issuer_requires_keyword_only_session_boundary() -> None:
    parameter = inspect.signature(AuthRegistry.generate_access_jwt).parameters["session"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_pre_auth_passes_purpose_without_revision_or_database_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _provider_recorder(monkeypatch)
    database = _RecordingDatabase([_user_document(17)])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    token = registry.generate_pre_auth_jwt("user-1", "TENANT-ONE", "USER", ["legal:read"])
    assert token == "synthetic-provider-token"
    assert calls[0]["token_purpose"] is jwt_provider.TokenPurpose.PRE_AUTH
    assert calls[0]["credential_revision"] is None
    assert database.collections["users"].calls == []


def test_pre_auth_does_not_create_session_or_refresh_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _provider_recorder(monkeypatch)
    database = _RecordingDatabase([_user_document(17)])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    registry.generate_pre_auth_jwt("user-1", "TENANT-ONE", "USER", [])
    assert calls[0]["token_purpose"] is jwt_provider.TokenPurpose.PRE_AUTH
    assert database.collections["sessions"].calls == []
    assert database.collections["refresh_tokens"].calls == []


def test_pre_auth_preserves_identity_projection_without_route_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _provider_recorder(monkeypatch)
    registry, _database = _registry_fixture(monkeypatch, revision=17)
    registry.generate_pre_auth_jwt("user-1", "TENANT-ONE", "USER", ["legal:read"])
    assert calls[0]["identity_data"] == {
        "identity_id": "user-1",
        "tenant_id": "TENANT-ONE",
        "roles": ["USER"],
        "permissions": ["legal:read"],
    }


def test_generic_issuer_remains_unspecified_and_does_not_read_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _provider_recorder(monkeypatch)
    registry, database = _registry_fixture(monkeypatch, revision=17)
    token = registry.generate_jwt("user-1", "TENANT-ONE", "USER", [])
    assert token == "synthetic-provider-token"
    assert calls[0]["token_purpose"] is None
    assert calls[0]["credential_revision"] is None
    assert database.collections["users"].calls == []


def test_real_provider_access_round_trip_contains_access_and_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", "synthetic-f7-provider-secret")
    registry, _database = _registry_fixture(monkeypatch, revision=17)
    token = registry.generate_access_jwt("user-1", "TENANT-ONE", "USER", [])
    claims = jwt_provider.verify_access_token(token)
    assert claims is not None
    assert claims["token_purpose"] == "ACCESS"
    assert claims["credential_revision"] == 17
    assert claims["identity_id"] == "user-1"
    assert claims["tenant_id"] == "TENANT-ONE"


def test_real_provider_pre_auth_round_trip_omits_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", "synthetic-f7-provider-secret")
    registry, _database = _registry_fixture(monkeypatch, revision=17)
    token = registry.generate_pre_auth_jwt("user-1", "TENANT-ONE", "USER", [])
    claims = jwt_provider.verify_access_token(token)
    assert claims is not None
    assert claims["token_purpose"] == "PRE_AUTH"
    assert "credential_revision" not in claims


def test_real_provider_generic_round_trip_has_no_access_escalation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", "synthetic-f7-provider-secret")
    registry, _database = _registry_fixture(monkeypatch, revision=17)
    token = registry.generate_jwt("user-1", "TENANT-ONE", "USER", [])
    claims = jwt_provider.verify_access_token(token)
    assert claims is not None
    assert "token_purpose" not in claims
    assert "credential_revision" not in claims


def test_create_session_uses_access_issuer_and_preserves_exact_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", "synthetic-f7-provider-secret")
    registry, database = _registry_fixture(monkeypatch, revision=17)
    monkeypatch.setattr(
        registry,
        "_require_active_principal_authority",
        lambda _principal_id: SimpleNamespace(status=PrincipalStatus.ACTIVE),
    )
    access_calls: list[dict[str, Any]] = []
    original = registry.generate_access_jwt

    def record_access(*args: Any, **kwargs: Any) -> str:
        access_calls.append({"args": args, "kwargs": dict(kwargs)})
        return original(*args, **kwargs)

    monkeypatch.setattr(registry, "generate_access_jwt", record_access)
    sentinel = _RecordingSession()
    user = registry.get_user_by_id("user-1", session=sentinel)
    assert user is not None
    created = registry.create_session(user, session=sentinel)
    claims = jwt_provider.verify_access_token(created.token)
    assert claims is not None
    assert claims["token_purpose"] == "ACCESS"
    assert claims["credential_revision"] == 17
    assert len(access_calls) == 1
    assert access_calls[0]["kwargs"]["session"] is sentinel
    assert database.collections["sessions"].calls[-1][2]["session"] is sentinel
    assert database.collections["refresh_tokens"].calls[-1][2]["session"] is sentinel


def test_create_session_refresh_row_remains_tenant_bearing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", "synthetic-f7-provider-secret")
    registry, database = _registry_fixture(monkeypatch, revision=17)
    monkeypatch.setattr(
        registry,
        "_require_active_principal_authority",
        lambda _principal_id: SimpleNamespace(status=PrincipalStatus.ACTIVE),
    )
    sentinel = _RecordingSession()
    user = registry.get_user_by_id("user-1", session=sentinel)
    assert user is not None
    registry.create_session(user, session=sentinel)
    inserted = database.collections["refresh_tokens"].documents[-1]
    assert set(inserted) == {"token", "user_id", "tenant_id", "expires"}
    assert inserted["user_id"] == "user-1"
    assert inserted["tenant_id"] == "TENANT-ONE"
    assert isinstance(inserted["expires"], datetime)


def test_issuers_do_not_mutate_credentials_or_revoke_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = _provider_recorder(monkeypatch)
    registry, database = _registry_fixture(monkeypatch, revision=17)
    registry.generate_access_jwt("user-1", "TENANT-ONE", "USER", [])
    registry.generate_pre_auth_jwt("user-1", "TENANT-ONE", "USER", [])
    assert calls
    for name in ("users", "sessions", "refresh_tokens", "otp_secrets", "principal_authorities"):
        writes = [call for call in database.collections[name].calls if call[0] != "find_one"]
        assert writes == []


def test_access_and_pre_auth_do_not_own_transaction_lifecycle() -> None:
    source = inspect.getsource(AuthRegistry)
    tree = ast.parse(source)
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called.intersection(
        {"start_session", "start_transaction", "commit_transaction", "abort_transaction", "retry_transaction"}
    )


def test_auth_registry_issuer_authority_remains_separated() -> None:
    source = inspect.getsource(AuthRegistry)
    assert "verify_access_token" not in source
    assert "MongoClient" not in source
    assert "password_policy" not in source
    assert "password_recovery" not in source
    assert "PwnedPassword" not in source
    assert "HIBP" not in source
    assert "credential_revision" in source


def test_access_error_does_not_retain_sensitive_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry, _database = _registry_fixture(monkeypatch, revision="corrupt")
    with pytest.raises(AuthRegistryTenantError) as captured:
        registry.generate_access_jwt("user-1", "TENANT-ONE", "USER", [])
    assert "user-1" not in str(captured.value)
    assert "bcrypt" not in repr(captured.value)


def test_current_cutover_boundaries_are_explicit() -> None:
    source = inspect.getsource(AuthRegistry)
    assert "generate_pre_auth_jwt" in source
    assert "generate_access_jwt" in source
    assert "generate_jwt" in source
    assert "get_credential_revision" in source
    assert "verify_access_token" not in source


def test_certificate_self_identity_and_scope() -> None:
    module = inspect.getmodule(test_certificate_self_identity_and_scope)
    assert module is not None
    source = inspect.getsource(module)
    version = "v1.0.0-R10C2F7-AUTH-REGISTRY-ACCESS-PREAUTH-ISSUER-CERT"
    version_lines = [
        line for line in source.splitlines()
        if line.startswith("VERSION:") or line.lstrip().startswith(version)
    ]
    assert len(version_lines) == 3
    assert all(version in line for line in version_lines)
    for forbidden in ("TO" + "DO", "FIX" + "ME", "place" + "holder", "st" + "ub"):
        assert forbidden.lower() not in source.lower()


"""
ARTIFACT: tests/unit/test_auth_registry_access_pre_auth_issuer.py
VERSION: v1.0.0-R10C2F7-AUTH-REGISTRY-ACCESS-PREAUTH-ISSUER-CERT
AUTHORITY BOUNDARY: Offline direct evidence for AuthRegistry issuer seams only
TENANT POSTURE: Exact tenant and principal projections; durable admission remains downstream
FAIL-CLOSED POSTURE: Malformed, absent, mismatched, or unavailable revision authority cannot issue ACCESS
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
