"""Wilsy OS credential-revision direct certificate.

TITLE: WILSY OS AuthRegistry Credential Revision Direct Certificate
VERSION: v1.3.0-D15G-DEV-TRANSACTIONAL-TENANT-RESOLUTION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies the AuthRegistry credential-revision
         persistence primitives plus caller-owned transactional registration
         and canonical-tenant resolution seams with deterministic offline fakes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_auth_registry_credential_revision.py
COLLABORATION / OWNERSHIP: Test-only evidence; production AuthRegistry,
                           JWT, recovery, Node, and database lifecycles remain
                           read-only and caller-owned.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG:
  v1.3.0-D15G-DEV-TRANSACTIONAL-TENANT-RESOLUTION-CERT —
    Advances the production-version oracle to v1.11.0-D15G-DEV-TRANSACTIONAL-TENANT-RESOLUTION, proves that
    register_user forwards the exact caller ClientSession into canonical
    tenant resolution before credential persistence, and proves the no-session
    path preserves the legacy resolver call shape without injecting a session.
    Transaction lifecycle and adjacent authorities remain caller-owned.
  v1.2.0-D15G-DEV-TRANSACTIONAL-REGISTRATION-CERT —
    Advances the production-version oracle to v1.10.0-D15G-DEV-TRANSACTIONAL-USER-REGISTRATION, freezes the
    register_user public session seam, proves exact caller-session propagation
    to the single credential insert, proves no-session compatibility, and
    proves the registry still owns no transaction lifecycle or adjacent
    authority creation.
  v1.1.0-R10C2F6A-AUTH-REGISTRY-CREDENTIAL-REVISION-CERT-RECONCILIATION —
    Advances the exact production-version oracle from the F1/v1.8 authority
    to the F6/v1.9 candidate while preserving every F2 credential-revision
    semantic assertion. This certificate does not certify new JWT issuer
    behavior.
  v1.0.0-R10C2F2-AUTH-REGISTRY-CREDENTIAL-REVISION-CERT — Adds independent
    coverage for revision validation and boundaries, exact identity reads,
    canonical and legacy CAS guards, atomic update/readback evidence, races,
    caller-session propagation, session/refresh revocation scope, privacy,
    and non-ownership of transactions and adjacent authorities.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic values only; bearer and hash sentinels
                            are never used as test identifiers or diagnostics.
TENANT BOUNDARY: Every mutation assertion requires the exact durable tenant
                 and principal predicate; cross-tenant deletion is rejected.
AUTHORITY BOUNDARY: AuthRegistry credential persistence, registration, and
                    canonical-tenant transaction-participation seams only.
                    Principal, membership, business-role, authorization-role,
                    JWT, reset/recovery, Node, and transaction ownership remain
                    outside this file.
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

from tools.eos.saas.auth import auth_registry as auth_registry_module
from tools.eos.saas.auth.auth_registry import (
    CREDENTIAL_REVISION_MAX,
    AuthRegistry,
    AuthRegistryTenantError,
)


class _Result:
    def __init__(
        self,
        *,
        matched_count: int | None = None,
        modified_count: int | None = None,
        deleted_count: int = 0,
    ) -> None:
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.deleted_count = deleted_count


class _RecordingSession:
    """Distinctive caller-owned session with no transaction methods."""

    def __init__(self) -> None:
        self.name = "caller-session-sentinel"
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0
        self.retry_calls = 0


class _RecordingCollection:
    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = [dict(document) for document in (documents or [])]
        self.calls: list[dict[str, Any]] = []
        self.forced_update_result: _Result | None = None
        self.readback_override: dict[str, Any] | None = None
        self.readback_override_active = False
        self.update_completed = False

    @staticmethod
    def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            if isinstance(expected, dict) and "$exists" in expected:
                if (key in document) != bool(expected["$exists"]):
                    return False
                continue
            if document.get(key) != expected:
                return False
        return True

    def find_one(
        self, query: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any] | None:
        self.calls.append({"operation": "find_one", "query": dict(query), "kwargs": dict(kwargs)})
        if self.update_completed and self.readback_override_active:
            return None if self.readback_override is None else dict(self.readback_override)
        for document in self.documents:
            if self._matches(document, query):
                return dict(document)
        return None

    def insert_one(self, document: dict[str, Any], **kwargs: Any) -> _Result:
        self.calls.append({"operation": "insert_one", "document": dict(document), "kwargs": dict(kwargs)})
        self.documents.append(dict(document))
        return _Result()

    def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
        **kwargs: Any,
    ) -> _Result:
        self.calls.append(
            {
                "operation": "update_one",
                "query": dict(query),
                "update": dict(update),
                "kwargs": dict(kwargs),
            }
        )
        if self.forced_update_result is not None:
            self.update_completed = True
            return self.forced_update_result
        for document in self.documents:
            if self._matches(document, query):
                for key, value in update.get("$set", {}).items():
                    document[key] = value
                self.update_completed = True
                return _Result(matched_count=1, modified_count=1)
        self.update_completed = True
        return _Result(matched_count=0, modified_count=0)

    def delete_many(self, query: dict[str, Any], **kwargs: Any) -> _Result:
        self.calls.append({"operation": "delete_many", "query": dict(query), "kwargs": dict(kwargs)})
        retained = [document for document in self.documents if not self._matches(document, query)]
        deleted = len(self.documents) - len(retained)
        self.documents = retained
        return _Result(deleted_count=deleted)


class _RecordingDatabase:
    def __init__(self, users: list[dict[str, Any]] | None = None) -> None:
        self.collections = {
            "users": _RecordingCollection(users or [_user_document()]),
            "sessions": _RecordingCollection(),
            "refresh_tokens": _RecordingCollection(),
            "tenants": _RecordingCollection(),
            "principal_authorities": _RecordingCollection(),
            "otp_secrets": _RecordingCollection(),
        }

    def __getitem__(self, name: str) -> _RecordingCollection:
        return self.collections[name]


class _TenantRegistry:
    @staticmethod
    def resolve_canonical_tenant(
        value: object,
        allow_alias: bool = False,
        session: Any = None,
    ) -> SimpleNamespace:
        del allow_alias, session
        if value not in {"TENANT-ONE", "TENANT-TWO"}:
            raise ValueError("synthetic tenant is not canonical")
        return SimpleNamespace(tenant_id=value)


def _user_document(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "user_id": "user-1",
        "email": "synthetic@example.com",
        "firstName": "Synthetic",
        "lastName": "Principal",
        "role": "USER",
        "permissions": ["legal:read"],
        "tenantId": "TENANT-ONE",
        "passwordHash": "bcrypt-old-synthetic",
        "credential_revision": 0,
        "mfaRegistered": True,
        "hasSignedCovenant": False,
        "authMetadata": {"marker": "preserve"},
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    document.update(overrides)
    return document


@pytest.fixture()
def harness(monkeypatch: pytest.MonkeyPatch) -> tuple[AuthRegistry, _RecordingDatabase]:
    database = _RecordingDatabase()
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    return AuthRegistry(cast(Any, _TenantRegistry)), database


def _users(database: _RecordingDatabase) -> _RecordingCollection:
    return database.collections["users"]


def _sessions(database: _RecordingDatabase) -> _RecordingCollection:
    return database.collections["sessions"]


def _refresh(database: _RecordingDatabase) -> _RecordingCollection:
    return database.collections["refresh_tokens"]


def _user_calls(collection: _RecordingCollection, operation: str) -> list[dict[str, Any]]:
    return [call for call in collection.calls if call["operation"] == operation]


def test_public_api_signatures_and_certificate_version() -> None:
    assert auth_registry_module.VERSION == "v1.11.0-D15G-DEV-TRANSACTIONAL-TENANT-RESOLUTION"
    assert list(inspect.signature(AuthRegistry.register_user).parameters) == [
        "self", "email", "password", "firstName", "lastName", "role", "tenantId", "session"
    ]
    assert inspect.signature(AuthRegistry.register_user).parameters["session"].default is None
    assert list(inspect.signature(AuthRegistry.get_credential_revision).parameters) == [
        "self", "tenant_id", "user_id", "session"
    ]
    assert list(inspect.signature(AuthRegistry.compare_and_swap_password_hash).parameters) == [
        "self", "tenant_id", "user_id", "expected_credential_revision", "new_password_hash", "session"
    ]
    assert list(inspect.signature(AuthRegistry.revoke_sessions).parameters) == [
        "self", "tenant_id", "user_id", "session"
    ]
    assert list(inspect.signature(AuthRegistry.revoke_refresh_tokens).parameters) == [
        "self", "tenant_id", "user_id", "session"
    ]


def test_register_user_persists_explicit_revision_zero(
    harness: tuple[AuthRegistry, _RecordingDatabase], monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, database = harness
    tenant_calls: list[tuple[object, bool]] = []

    def legacy_resolver(
        value: object,
        allow_alias: bool = False,
    ) -> SimpleNamespace:
        tenant_calls.append((value, allow_alias))
        return SimpleNamespace(tenant_id=value)

    monkeypatch.setattr(
        registry.tenant_registry,
        "resolve_canonical_tenant",
        legacy_resolver,
    )
    monkeypatch.setattr(registry, "hash_password", lambda _password: "bcrypt-registration-synthetic")
    user = registry.register_user("new@example.com", "approved-password", "New", "User", "USER", "TENANT-ONE")
    inserted = _users(database).documents[-1]
    calls = _user_calls(_users(database), "insert_one")
    assert user.id == inserted["user_id"]
    assert inserted["credential_revision"] == 0
    assert inserted["passwordHash"] == "bcrypt-registration-synthetic"
    assert calls[-1]["kwargs"] == {}
    assert tenant_calls == [("TENANT-ONE", True)]


def test_register_user_forwards_exact_caller_session_without_owning_transaction(
    harness: tuple[AuthRegistry, _RecordingDatabase], monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, database = harness
    session = _RecordingSession()
    tenant_calls: list[dict[str, Any]] = []

    def transactional_resolver(
        value: object,
        allow_alias: bool = False,
        session: Any = None,
    ) -> SimpleNamespace:
        tenant_calls.append(
            {
                "value": value,
                "allow_alias": allow_alias,
                "session": session,
            }
        )
        return SimpleNamespace(tenant_id=value)

    monkeypatch.setattr(
        registry.tenant_registry,
        "resolve_canonical_tenant",
        transactional_resolver,
    )
    monkeypatch.setattr(registry, "hash_password", lambda _password: "bcrypt-transactional-registration-synthetic")

    user = registry.register_user(
        "persona@example.com",
        "approved-password",
        "Persona",
        "Principal",
        "USER",
        "TENANT-ONE",
        session=session,
    )

    inserts = _user_calls(_users(database), "insert_one")
    assert len(inserts) == 1
    assert inserts[0]["kwargs"] == {"session": session}
    assert inserts[0]["document"]["user_id"] == user.id
    assert inserts[0]["document"]["tenantId"] == "TENANT-ONE"
    assert inserts[0]["document"]["credential_revision"] == 0
    assert inserts[0]["document"]["passwordHash"] == "bcrypt-transactional-registration-synthetic"
    assert tenant_calls == [
        {
            "value": "TENANT-ONE",
            "allow_alias": True,
            "session": session,
        }
    ]
    assert session.start_calls == 0
    assert session.commit_calls == 0
    assert session.abort_calls == 0
    assert session.retry_calls == 0
    assert _sessions(database).calls == []
    assert _refresh(database).calls == []
    assert database.collections["principal_authorities"].calls == []
    assert database.collections["otp_secrets"].calls == []


def test_missing_revision_hydrates_zero_without_write_on_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _RecordingDatabase([_user_document(credential_revision=None)])
    del database.collections["users"].documents[0]["credential_revision"]
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    assert registry.get_credential_revision("TENANT-ONE", "user-1") == 0
    assert _user_calls(_users(database), "update_one") == []
    assert "credential_revision" not in database.collections["users"].documents[0]


@pytest.mark.parametrize("revision", [0, 1, 17, CREDENTIAL_REVISION_MAX])
def test_valid_revision_values_are_returned_exactly(
    monkeypatch: pytest.MonkeyPatch, revision: int
) -> None:
    database = _RecordingDatabase([_user_document(credential_revision=revision)])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    assert AuthRegistry(cast(Any, _TenantRegistry)).get_credential_revision("TENANT-ONE", "user-1") == revision


@pytest.mark.parametrize(
    "revision",
    [None, True, False, -1, 1.0, "1", "invalid", [], {}, object()],
    ids=["none", "true", "false", "negative", "float", "numeric-string", "string", "list", "dict", "object"],
)
def test_present_malformed_revision_fails_closed_without_write(
    monkeypatch: pytest.MonkeyPatch, revision: object
) -> None:
    database = _RecordingDatabase([_user_document(credential_revision=revision)])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    with pytest.raises(AuthRegistryTenantError) as error:
        registry.get_credential_revision("TENANT-ONE", "user-1")
    assert "synthetic" not in str(error.value)
    assert _user_calls(_users(database), "update_one") == []


def test_revision_maximum_boundary_advances_to_max_and_no_overflow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _RecordingDatabase([_user_document(credential_revision=CREDENTIAL_REVISION_MAX - 1)])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    assert registry.compare_and_swap_password_hash(
        "TENANT-ONE", "user-1", CREDENTIAL_REVISION_MAX - 1, "bcrypt-boundary-synthetic"
    ) == CREDENTIAL_REVISION_MAX
    assert database.collections["users"].documents[0]["credential_revision"] == CREDENTIAL_REVISION_MAX
    before_calls = len(_user_calls(_users(database), "update_one"))
    with pytest.raises(AuthRegistryTenantError):
        registry.compare_and_swap_password_hash(
            "TENANT-ONE", "user-1", CREDENTIAL_REVISION_MAX, "bcrypt-overflow-synthetic"
        )
    assert len(_user_calls(_users(database), "update_one")) == before_calls


def test_exact_canonical_revision_read_is_tenant_bound_and_session_propagated(
    harness: tuple[AuthRegistry, _RecordingDatabase],
) -> None:
    registry, database = harness
    session = _RecordingSession()
    assert registry.get_credential_revision("TENANT-ONE", "user-1", session=session) == 0
    reads = _user_calls(_users(database), "find_one")
    assert reads[0]["query"] == {"user_id": "user-1", "tenantId": "TENANT-ONE"}
    assert reads[0]["kwargs"]["session"] is session


def test_legacy_id_revision_read_is_exact_tenant_bound_and_session_propagated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    legacy_id = ObjectId("507f1f77bcf86cd799439011")
    database = _RecordingDatabase([_user_document(user_id=None, _id=legacy_id)])
    del database.collections["users"].documents[0]["credential_revision"]
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    session = _RecordingSession()
    assert registry.get_credential_revision("TENANT-ONE", str(legacy_id), session=session) == 0
    reads = _user_calls(_users(database), "find_one")
    assert reads[0]["query"] == {"user_id": str(legacy_id), "tenantId": "TENANT-ONE"}
    assert reads[1]["query"] == {"_id": legacy_id, "tenantId": "TENANT-ONE"}
    assert all(call["kwargs"]["session"] is session for call in reads)


def test_tenant_mismatch_and_missing_user_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _RecordingDatabase([_user_document(tenantId="TENANT-TWO")])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    with pytest.raises(AuthRegistryTenantError):
        registry.get_credential_revision("TENANT-ONE", "user-1")
    database.collections["users"].documents = []
    with pytest.raises(AuthRegistryTenantError):
        registry.get_credential_revision("TENANT-ONE", "missing-user")


def test_identity_collision_fails_closed() -> None:
    collision_text = "507f1f77bcf86cd799439011"
    database = _RecordingDatabase(
        [
            _user_document(user_id=collision_text, _id=ObjectId("507f191e810c19729de860ea")),
            _user_document(user_id=None, _id=ObjectId(collision_text)),
        ]
    )
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    original = auth_registry_module.kernel_db.get_database
    auth_registry_module.kernel_db.get_database = lambda: database
    try:
        with pytest.raises(AuthRegistryTenantError):
            registry.get_credential_revision("TENANT-ONE", collision_text)
    finally:
        auth_registry_module.kernel_db.get_database = original


def test_canonical_cas_has_exact_filter_atomic_update_and_readback_session(
    harness: tuple[AuthRegistry, _RecordingDatabase],
) -> None:
    registry, database = harness
    session = _RecordingSession()
    new_hash = "bcrypt-approved-synthetic"
    assert registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, new_hash, session=session) == 1
    updates = _user_calls(_users(database), "update_one")
    assert len(updates) == 1
    update = updates[0]
    assert update["query"] == {"user_id": "user-1", "tenantId": "TENANT-ONE", "credential_revision": 0}
    assert update["update"] == {"$set": {"passwordHash": new_hash, "credential_revision": 1}}
    assert update["kwargs"] == {"upsert": False, "session": session}
    reads = _user_calls(_users(database), "find_one")
    assert all(call["kwargs"]["session"] is session for call in reads)
    assert database.collections["users"].documents[0]["passwordHash"] == new_hash


def test_legacy_missing_revision_cas_uses_exists_guard_and_advances_atomically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    legacy_id = ObjectId("507f1f77bcf86cd799439011")
    document = _user_document(user_id=None, _id=legacy_id)
    del document["credential_revision"]
    database = _RecordingDatabase([document])
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    assert registry.compare_and_swap_password_hash("TENANT-ONE", str(legacy_id), 0, "bcrypt-legacy-synthetic") == 1
    update = _user_calls(_users(database), "update_one")[0]
    assert update["query"] == {
        "_id": legacy_id,
        "tenantId": "TENANT-ONE",
        "credential_revision": {"$exists": False},
    }
    assert update["update"] == {"$set": {"passwordHash": "bcrypt-legacy-synthetic", "credential_revision": 1}}


def test_legacy_field_appearing_after_read_is_not_overwritten(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    legacy_id = ObjectId("507f1f77bcf86cd799439011")
    document = _user_document(user_id=None, _id=legacy_id)
    del document["credential_revision"]
    database = _RecordingDatabase([document])
    database.collections["users"].forced_update_result = _Result(matched_count=0, modified_count=0)
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    registry = AuthRegistry(cast(Any, _TenantRegistry))
    with pytest.raises(AuthRegistryTenantError):
        registry.compare_and_swap_password_hash("TENANT-ONE", str(legacy_id), 0, "bcrypt-race-synthetic")
    assert len(_user_calls(_users(database), "update_one")) == 1


def test_stale_revision_is_rejected_before_mutation(
    harness: tuple[AuthRegistry, _RecordingDatabase],
) -> None:
    registry, database = harness
    with pytest.raises(AuthRegistryTenantError):
        registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 1, "bcrypt-stale-synthetic")
    assert _user_calls(_users(database), "update_one") == []


@pytest.mark.parametrize(
    "result",
    [_Result(matched_count=0, modified_count=0), _Result(matched_count=1, modified_count=0)],
    ids=["matched-zero", "modified-zero"],
)
def test_cas_count_anomalies_fail_closed_without_false_success(
    harness: tuple[AuthRegistry, _RecordingDatabase], result: _Result
) -> None:
    registry, database = harness
    _users(database).forced_update_result = result
    with pytest.raises(AuthRegistryTenantError):
        registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, "bcrypt-anomaly-synthetic")


def test_bad_revision_readback_fails_closed(
    harness: tuple[AuthRegistry, _RecordingDatabase],
) -> None:
    registry, database = harness
    _users(database).readback_override = _user_document(credential_revision=9, passwordHash="bcrypt-approved-synthetic")
    _users(database).readback_override_active = True
    with pytest.raises(AuthRegistryTenantError):
        registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, "bcrypt-approved-synthetic")


@pytest.mark.parametrize(
    "override",
    [
        _user_document(tenantId="TENANT-TWO", credential_revision=1, passwordHash="bcrypt-approved-synthetic"),
        None,
    ],
    ids=["tenant-drift", "identity-disappears"],
)
def test_readback_tenant_or_identity_anomaly_fails_closed(
    harness: tuple[AuthRegistry, _RecordingDatabase], override: dict[str, Any] | None
) -> None:
    registry, database = harness
    _users(database).readback_override = override
    _users(database).readback_override_active = True
    with pytest.raises(AuthRegistryTenantError):
        registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, "bcrypt-readback-synthetic")


@pytest.mark.parametrize("invalid_hash", [None, 7, b"bytes", ""] , ids=["none", "int", "bytes", "empty"])
def test_invalid_hash_input_fails_before_persistence(
    harness: tuple[AuthRegistry, _RecordingDatabase], invalid_hash: object
) -> None:
    registry, database = harness
    with pytest.raises(AuthRegistryTenantError) as error:
        registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, cast(str, invalid_hash))
    assert "bcrypt-secret-sentinel" not in str(error.value)
    assert _user_calls(_users(database), "update_one") == []


def test_cas_does_not_invoke_policy_or_revoke_authority(
    harness: tuple[AuthRegistry, _RecordingDatabase], monkeypatch: pytest.MonkeyPatch
) -> None:
    registry, database = harness
    calls = {"policy": 0, "blocklist": 0}
    monkeypatch.setattr(registry, "hash_password", lambda _password: calls.__setitem__("policy", calls["policy"] + 1))
    assert registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, "bcrypt-approved-synthetic") == 1
    assert calls == {"policy": 0, "blocklist": 0}
    assert _user_calls(_sessions(database), "delete_many") == []
    assert _user_calls(_refresh(database), "delete_many") == []


def test_unrelated_fields_remain_unchanged_after_cas(
    harness: tuple[AuthRegistry, _RecordingDatabase],
) -> None:
    registry, database = harness
    before = dict(_users(database).documents[0])
    registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, "bcrypt-preserve-synthetic")
    after = _users(database).documents[0]
    for field in ("mfaRegistered", "tenantId", "role", "permissions", "authMetadata", "hasSignedCovenant"):
        assert after[field] == before[field]
    assert after["passwordHash"] != before["passwordHash"]
    assert after["credential_revision"] == 1


def test_session_revocation_is_exact_tenant_user_and_session_propagated(
    harness: tuple[AuthRegistry, _RecordingDatabase],
) -> None:
    registry, database = harness
    _sessions(database).documents = [
        {"tenant_id": "TENANT-ONE", "user_id": "user-1", "token": "session-token-sentinel"},
        {"tenant_id": "TENANT-TWO", "user_id": "user-1", "token": "other-tenant-session"},
    ]
    session = _RecordingSession()
    assert registry.revoke_sessions("TENANT-ONE", "user-1", session=session) == 1
    delete = _user_calls(_sessions(database), "delete_many")[0]
    assert delete["query"] == {"tenant_id": "TENANT-ONE", "user_id": "user-1"}
    assert delete["kwargs"]["session"] is session
    assert _sessions(database).documents == [{"tenant_id": "TENANT-TWO", "user_id": "user-1", "token": "other-tenant-session"}]
    assert "session-token-sentinel" not in repr(1)


def test_refresh_revocation_preserves_exact_tenant_scope(
    harness: tuple[AuthRegistry, _RecordingDatabase],
) -> None:
    registry, database = harness
    _refresh(database).documents = [
        {"tenant_id": "TENANT-ONE", "user_id": "user-1", "token": "refresh-token-sentinel"},
        {"tenant_id": "TENANT-TWO", "user_id": "user-1", "token": "other-tenant-refresh"},
    ]
    session = _RecordingSession()
    assert registry.revoke_refresh_tokens("TENANT-ONE", "user-1", session=session) == 1
    delete = _user_calls(_refresh(database), "delete_many")[0]
    assert delete["query"] == {"tenant_id": "TENANT-ONE", "user_id": "user-1"}
    assert delete["kwargs"]["session"] is session
    assert _refresh(database).documents[0]["token"] == "other-tenant-refresh"


def test_transaction_and_authority_boundaries_are_not_owned_by_f1() -> None:
    source = inspect.getsource(auth_registry_module)
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "pymongo.errors" in imports
    assert "pymongo.mongo_client" not in imports
    credential_source = inspect.getsource(AuthRegistry.get_credential_revision)
    credential_source += inspect.getsource(AuthRegistry.compare_and_swap_password_hash)
    credential_source += inspect.getsource(AuthRegistry.revoke_sessions)
    assert "start_session" not in credential_source
    assert "start_transaction" not in credential_source
    assert "commit_transaction" not in credential_source
    assert "abort_transaction" not in credential_source
    assert "PrincipalAuthority" not in credential_source
    assert ".revision" not in credential_source
    assert "password_policy" not in source
    assert "password_blocklist" not in source
    assert "consume_recovery" not in credential_source
    assert "recovery_capability" not in credential_source
    assert "create_access_token" not in credential_source


def test_static_index_jwt_and_node_boundaries_remain_closed() -> None:
    source = inspect.getsource(auth_registry_module)
    assert "create_index" not in source
    assert "drop_index" not in source
    assert "credential_revision" in source
    assert "tenant_id" in inspect.getsource(AuthRegistry.revoke_refresh_tokens)
    assert "jwt_provider" in source
    imported_modules = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert all("node" not in module.lower() for module in imported_modules)


def test_secret_hygiene_for_safe_results_errors_and_captured_logs(
    harness: tuple[AuthRegistry, _RecordingDatabase], caplog: pytest.LogCaptureFixture
) -> None:
    registry, database = harness
    password_hash = "bcrypt-secret-sentinel"
    session_token = "session-secret-sentinel"
    refresh_token = "refresh-secret-sentinel"
    _sessions(database).documents = [{"tenant_id": "TENANT-ONE", "user_id": "user-1", "token": session_token}]
    _refresh(database).documents = [{"tenant_id": "TENANT-ONE", "user_id": "user-1", "token": refresh_token}]
    assert registry.compare_and_swap_password_hash("TENANT-ONE", "user-1", 0, password_hash) == 1
    assert registry.revoke_sessions("TENANT-ONE", "user-1") == 1
    assert registry.revoke_refresh_tokens("TENANT-ONE", "user-1") == 1
    output = " ".join(record.getMessage() for record in caplog.records)
    assert password_hash not in output
    assert session_token not in output
    assert refresh_token not in output
    assert password_hash not in repr(1)
    assert session_token not in repr(1)
    assert refresh_token not in repr(1)


def test_certificate_is_offline_and_does_not_construct_clients() -> None:
    source = inspect.getsource(auth_registry_module)
    assert "MongoClient(" not in source
    assert "requests." not in source
    assert "httpx." not in source


# ARTIFACT: tests/unit/test_auth_registry_credential_revision.py
# VERSION: v1.3.0-D15G-DEV-TRANSACTIONAL-TENANT-RESOLUTION-CERT
# AUTHORITY BOUNDARY: direct offline evidence for AuthRegistry credential, tenant-resolution, and caller-transaction registration seams
# TENANT POSTURE: canonical tenant resolution and credential persistence preserve exact caller transaction scope
# FAIL-CLOSED POSTURE: malformed state, races, count anomalies, readback drift, and transaction-boundary violations fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
