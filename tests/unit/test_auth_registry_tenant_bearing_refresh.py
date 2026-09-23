"""WILSY OS tenant-bearing refresh authority certificate.

TITLE: AuthRegistry Tenant-Bearing Refresh Direct Unit Certificate
VERSION: v1.1.0-R10C2F6B-TENANT-BEARING-REFRESH-CERT-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Directly certifies the R10C2B Python refresh-token creation,
         validation, compatibility, and tenant-scoped revocation seams.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_auth_registry_tenant_bearing_refresh.py
COLLABORATION / OWNERSHIP: Exercises AuthRegistry with deterministic recording
                           fakes; no canonical or disposable Mongo is used.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2B-TENANT-BEARING-REFRESH-CERT — Certifies explicit and
    backward-compatible tenant-bearing refresh creation, temporary missing-
    field validation, corrupt-present rejection, exact tenant+user revocation,
    caller-session propagation, and transaction ownership boundaries. This is
    not a migration, index, credential-revision, JWT-invalidation, or financial
    authority certificate.
  v1.1.0-R10C2F6B-TENANT-BEARING-REFRESH-CERT-RECONCILIATION — Reconciles
    create_session() observation from transitional generate_jwt() to explicit
    generate_access_jwt(); tenant-bearing refresh/session semantics remain
    unchanged. No JWT verification or durable revision comparison is certified.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identities and bearer values only;
                            no secret is emitted by assertions or diagnostics.
TENANT BOUNDARY: Every tenant-bearing assertion uses the durable tenantId
                 projection and exact tenant_id + user_id revocation predicate.
AUTHORITY BOUNDARY: Unit evidence for AuthRegistry only; caller owns sessions
                    and transactions; no migration authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import ast
import inspect
from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any, cast

import pytest
from bson import ObjectId

from tools.eos.saas.auth import auth_registry as auth_registry_module
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError
from tools.eos.saas.domain.auth import User
from tools.eos.auth.principal_status import PrincipalStatus


class _Result:
    def __init__(self, *, deleted_count: int = 0) -> None:
        self.deleted_count = deleted_count


class _RecordingSession:
    def __init__(self) -> None:
        self.started = 0
        self.committed = 0
        self.aborted = 0
        self.retried = 0


class _RecordingCollection:
    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = [dict(document) for document in (documents or [])]
        self.calls: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    def find_one(self, query: dict[str, Any], **kwargs: Any) -> dict[str, Any] | None:
        self.calls.append(("find_one", dict(query), dict(kwargs)))
        return next(
            (
                document
                for document in self.documents
                if all(document.get(key) == value for key, value in query.items())
            ),
            None,
        )

    def insert_one(self, document: dict[str, Any], **kwargs: Any) -> _Result:
        self.calls.append(("insert_one", dict(document), dict(kwargs)))
        self.documents.append(dict(document))
        return _Result()

    def delete_many(self, query: dict[str, Any], **kwargs: Any) -> _Result:
        self.calls.append(("delete_many", dict(query), dict(kwargs)))
        retained = [
            document
            for document in self.documents
            if not all(document.get(key) == value for key, value in query.items())
        ]
        deleted_count = len(self.documents) - len(retained)
        self.documents = retained
        return _Result(deleted_count=deleted_count)

    def update_one(self, query: dict[str, Any], update: dict[str, Any], **kwargs: Any) -> _Result:
        self.calls.append(("update_one", {"query": dict(query), "update": dict(update)}, dict(kwargs)))
        return _Result()


class _RecordingDatabase:
    def __init__(self, user_documents: list[dict[str, Any]] | None = None) -> None:
        self.collections = {
            "users": _RecordingCollection(user_documents or [_user_document()]),
            "refresh_tokens": _RecordingCollection(),
            "sessions": _RecordingCollection(),
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
            raise ValueError("tenant is not an active canonical tenant")
        return SimpleNamespace(tenant_id=value)


def _user_document() -> dict[str, Any]:
    return {
        "user_id": "user-1",
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "email": "user@example.com",
        "firstName": "Synthetic",
        "lastName": "Principal",
        "role": "USER",
        "permissions": ["legal:read"],
        "tenantId": "TENANT-ONE",
        "passwordHash": "bcrypt-synthetic-value",
        "mfaRegistered": False,
        "hasSignedCovenant": False,
    }


@pytest.fixture()
def harness(monkeypatch: pytest.MonkeyPatch) -> tuple[AuthRegistry, _RecordingDatabase, User]:
    database = _RecordingDatabase()
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    user = registry.get_user_by_id("user-1")
    assert user is not None
    return registry, database, user


def _refresh_collection(database: _RecordingDatabase) -> _RecordingCollection:
    return database.collections["refresh_tokens"]


def test_public_signatures_and_certificate_scope() -> None:
    generation = inspect.signature(AuthRegistry.generate_refresh_token)
    validation = inspect.signature(AuthRegistry.validate_refresh_token)
    revocation = inspect.signature(AuthRegistry.revoke_refresh_tokens)
    session_creation = inspect.signature(AuthRegistry.create_session)
    identity_read = inspect.signature(AuthRegistry.get_user_by_id)
    assert list(generation.parameters) == ["self", "user_id", "tenant_id", "session"]
    assert generation.parameters["tenant_id"].default is None
    assert generation.parameters["session"].default is None
    assert list(validation.parameters) == ["self", "token", "session"]
    assert validation.parameters["session"].default is None
    assert list(revocation.parameters) == ["self", "tenant_id", "user_id", "session"]
    assert revocation.parameters["session"].default is None
    assert list(session_creation.parameters) == ["self", "user", "session"]
    assert session_creation.parameters["session"].default is None
    assert list(identity_read.parameters) == ["self", "user_id", "session"]
    assert identity_read.parameters["session"].default is None


def test_explicit_tenant_creation_persists_exact_semantic_fields(harness: tuple[AuthRegistry, _RecordingDatabase, User]) -> None:
    registry, database, user = harness
    caller_session = _RecordingSession()
    token = registry.generate_refresh_token(user.id, user.tenantId, session=caller_session)
    refresh = _refresh_collection(database)
    inserted = refresh.documents[-1]
    assert set(inserted) == {"token", "user_id", "tenant_id", "expires"}
    assert inserted["token"] == token
    assert inserted["user_id"] == user.id
    assert inserted["tenant_id"] == user.tenantId
    assert isinstance(inserted["expires"], datetime)
    assert refresh.calls[-1][2]["session"] is caller_session


def test_omitted_tenant_derives_canonical_tenant_and_never_inserts_tenantless(harness: tuple[AuthRegistry, _RecordingDatabase, User]) -> None:
    registry, database, user = harness
    registry.generate_refresh_token(user.id)
    inserted = _refresh_collection(database).documents[-1]
    assert inserted["tenant_id"] == user.tenantId
    assert inserted.get("tenant_id") not in (None, "")


@pytest.mark.parametrize("invalid_tenant", ["", "   ", 7, "UNKNOWN-TENANT"])
def test_creation_rejects_mismatched_or_corrupt_explicit_tenant(
    harness: tuple[AuthRegistry, _RecordingDatabase, User], invalid_tenant: object,
) -> None:
    registry, database, user = harness
    before = len(_refresh_collection(database).documents)
    with pytest.raises(AuthRegistryTenantError):
        registry.generate_refresh_token(user.id, invalid_tenant)  # type: ignore[arg-type]
    assert len(_refresh_collection(database).documents) == before

    before = len(_refresh_collection(database).documents)
    with pytest.raises(AuthRegistryTenantError):
        registry.generate_refresh_token(user.id, "TENANT-TWO")
    assert len(_refresh_collection(database).documents) == before


def test_create_session_chain_is_tenant_bearing_and_preserves_session_identity(
    harness: tuple[AuthRegistry, _RecordingDatabase, User], monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry, database, user = harness
    access_issuer_calls: list[dict[str, Any]] = []

    def record_access_issuer(
        user_id: str,
        tenant_id: str,
        role: str,
        permissions: list[str],
        *,
        session: Any = None,
    ) -> str:
        access_issuer_calls.append(
            {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "role": role,
                "permissions": list(permissions),
                "session": session,
            }
        )
        return "synthetic-session-jwt"

    monkeypatch.setattr(registry, "generate_access_jwt", record_access_issuer)
    monkeypatch.setattr(
        registry,
        "_require_active_principal_authority",
        lambda _principal_id: SimpleNamespace(status=PrincipalStatus.ACTIVE),
    )
    caller_session = _RecordingSession()
    created = registry.create_session(user, session=caller_session)
    sessions = database.collections["sessions"]
    refresh = _refresh_collection(database)
    assert len(access_issuer_calls) == 1
    assert access_issuer_calls[0]["user_id"] == user.id
    assert access_issuer_calls[0]["tenant_id"] == user.tenantId
    assert access_issuer_calls[0]["role"] == user.role
    assert access_issuer_calls[0]["permissions"] == user.permissions
    assert access_issuer_calls[0]["session"] is caller_session
    assert created.tenantId == user.tenantId
    assert sessions.documents[0]["tenant_id"] == user.tenantId
    assert refresh.documents[0]["user_id"] == user.id
    assert refresh.documents[0]["tenant_id"] == user.tenantId
    assert sessions.calls[0][2]["session"] is caller_session
    assert refresh.calls[-1][2]["session"] is caller_session


def _seed_refresh(database: _RecordingDatabase, **overrides: Any) -> str:
    token = "synthetic-refresh-token"
    row = {
        "token": token,
        "user_id": "user-1",
        "tenant_id": "TENANT-ONE",
        "expires": datetime.utcnow() + timedelta(minutes=5),
    }
    row.update(overrides)
    _refresh_collection(database).documents.append(row)
    return token


def test_tenant_bearing_validation_success_and_exact_token_lookup(
    harness: tuple[AuthRegistry, _RecordingDatabase, User],
) -> None:
    registry, database, _user = harness
    token = _seed_refresh(database)
    caller_session = _RecordingSession()
    assert registry.validate_refresh_token(token, session=caller_session) == "user-1"
    refresh_calls = _refresh_collection(database).calls
    assert refresh_calls[0][0] == "find_one"
    assert refresh_calls[0][1] == {"token": token}
    assert refresh_calls[0][2]["session"] is caller_session
    user_calls = database.collections["users"].calls
    assert all(set(call[1]).issubset({"user_id", "_id"}) for call in user_calls)


def test_cross_tenant_refresh_fails_closed_without_repair_or_write(
    harness: tuple[AuthRegistry, _RecordingDatabase, User],
) -> None:
    registry, database, _user = harness
    token = _seed_refresh(database, tenant_id="TENANT-TWO")
    assert registry.validate_refresh_token(token) is None
    assert not any(call[0] in {"insert_one", "update_one", "delete_many"} for call in _refresh_collection(database).calls)


@pytest.mark.parametrize("corrupt_tenant", [None, "", 7])
def test_present_corrupt_tenant_is_not_treated_as_legacy(
    harness: tuple[AuthRegistry, _RecordingDatabase, User], corrupt_tenant: object,
) -> None:
    registry, database, _user = harness
    token = _seed_refresh(database, tenant_id=corrupt_tenant)
    assert registry.validate_refresh_token(token) is None
    assert all(call[0] == "find_one" for call in _refresh_collection(database).calls)


def test_missing_tenant_has_temporary_read_only_legacy_compatibility(
    harness: tuple[AuthRegistry, _RecordingDatabase, User],
) -> None:
    registry, database, _user = harness
    token = _seed_refresh(database)
    _refresh_collection(database).documents[0].pop("tenant_id")
    caller_session = _RecordingSession()
    assert registry.validate_refresh_token(token, session=caller_session) == "user-1"
    assert all(call[0] == "find_one" for call in _refresh_collection(database).calls)
    assert all(call[0] not in {"insert_one", "update_one", "delete_many"} for call in _refresh_collection(database).calls)
    assert _refresh_collection(database).documents[0].get("tenant_id") is None


def test_legacy_identity_uses_only_existing_user_id_then_validated_object_id_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    legacy_id = ObjectId("507f1f77bcf86cd799439012")
    database = _RecordingDatabase([dict(_user_document(), _id=legacy_id)])
    database.collections["users"].documents[0].pop("user_id")
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    token = _seed_refresh(database)
    _refresh_collection(database).documents[0]["user_id"] = str(legacy_id)
    assert registry.validate_refresh_token(token) == str(legacy_id)
    user_queries = [call[1] for call in database.collections["users"].calls]
    assert user_queries[0] == {"user_id": str(legacy_id)}
    assert user_queries[1] == {"_id": legacy_id}
    assert all(set(query).issubset({"user_id", "_id"}) for query in user_queries)


@pytest.mark.parametrize(
    "expiry, expected",
    [(datetime.utcnow() - timedelta(seconds=1), None), ("not-a-date", None)],
)
def test_expired_and_malformed_expiry_fail_closed(
    harness: tuple[AuthRegistry, _RecordingDatabase, User], expiry: object, expected: str | None,
) -> None:
    registry, database, _user = harness
    token = _seed_refresh(database, expires=expiry)
    assert registry.validate_refresh_token(token) is expected


def test_tenant_scoped_revocation_exact_filter_excludes_legacy_and_cross_tenant_rows(
    harness: tuple[AuthRegistry, _RecordingDatabase, User],
) -> None:
    registry, database, _user = harness
    refresh = _refresh_collection(database)
    refresh.documents.extend([
        {"token": "migrated", "user_id": "user-1", "tenant_id": "TENANT-ONE"},
        {"token": "legacy", "user_id": "user-1"},
        {"token": "other-tenant", "user_id": "user-1", "tenant_id": "TENANT-TWO"},
    ])
    caller_session = _RecordingSession()
    assert registry.revoke_refresh_tokens("TENANT-ONE", "user-1", session=caller_session) == 1
    call = refresh.calls[-1]
    assert call[0] == "delete_many"
    assert call[1] == {"tenant_id": "TENANT-ONE", "user_id": "user-1"}
    assert call[2]["session"] is caller_session
    assert [row["token"] for row in refresh.documents] == ["legacy", "other-tenant"]
    assert "token" not in call[1]


def test_revocation_validates_user_tenant_before_delete(harness: tuple[AuthRegistry, _RecordingDatabase, User]) -> None:
    registry, database, _user = harness
    _seed_refresh(database, tenant_id="TENANT-TWO")
    with pytest.raises(AuthRegistryTenantError):
        registry.revoke_refresh_tokens("TENANT-TWO", "user-1")
    assert not any(call[0] == "delete_many" for call in _refresh_collection(database).calls)


def test_transaction_index_and_authority_boundaries_are_absent() -> None:
    source = inspect.getsource(AuthRegistry)
    tree = ast.parse(source)
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called_attributes.intersection({"start_session", "start_transaction", "commit_transaction", "abort_transaction"})
    assert not called_attributes.intersection({"create_index", "create_indexes", "ensure_indexes"})
    assert "credentialRevision" not in source
    assert "password_policy" not in source
    assert "PwnedPassword" not in source
    assert "HIBP" not in source
    assert "delete_many({\"user_id\"" not in source


def test_refresh_operations_do_not_mutate_mfa_roles_or_tenant_authority(
    harness: tuple[AuthRegistry, _RecordingDatabase, User],
) -> None:
    registry, database, user = harness
    token = registry.generate_refresh_token(user.id, user.tenantId)
    assert registry.validate_refresh_token(token) == user.id
    registry.revoke_refresh_tokens(user.tenantId, user.id)
    for collection_name in ("users", "otp_secrets", "principal_authorities"):
        writes = [
            call
            for call in database.collections[collection_name].calls
            if call[0] in {"insert_one", "update_one", "delete_many"}
        ]
        assert writes == []


def test_refresh_token_is_not_echoed_by_failure_contract(
    harness: tuple[AuthRegistry, _RecordingDatabase, User],
) -> None:
    registry, database, _user = harness
    token = "distinctive-refresh-secret-value"
    _seed_refresh(database, token=token, tenant_id="TENANT-TWO")
    result = registry.validate_refresh_token(token)
    assert result is None
    assert token not in repr(result)


"""
ARTIFACT: tests/unit/test_auth_registry_tenant_bearing_refresh.py
VERSION: v1.1.0-R10C2F6B-TENANT-BEARING-REFRESH-CERT-RECONCILIATION
AUTHORITY BOUNDARY: Offline direct unit evidence for AuthRegistry refresh seams only
TENANT POSTURE: Exact tenant-bearing creation and tenant_id + user_id revocation;
                missing tenant remains temporary pre-migration compatibility
FAIL-CLOSED POSTURE: Mismatched, corrupt-present, expired, and malformed refresh
                     authority is rejected without migration-on-read
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
MIGRATION POSTURE: No canonical data access, migration, or index creation
END OF WILSY OS SOVEREIGN ARTIFACT
"""
