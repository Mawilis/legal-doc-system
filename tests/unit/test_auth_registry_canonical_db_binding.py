"""WILSY OS canonical authentication database-binding certificate.

TITLE: AuthRegistry Canonical Database Binding Certificate
VERSION: v1.1.1-CANONICAL-SIGNING-CONFIG-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves authentication persistence consumes the lazy Kernel database
         accessor without creating a private client or weakening auth semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_auth_registry_canonical_db_binding.py
COLLABORATION / OWNERSHIP: Exercises tools.eos.saas.auth.auth_registry in
                           isolation with deterministic collection doubles.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG:
  v1.1.1-CANONICAL-SIGNING-CONFIG-CERT — Supplies an explicit synthetic
    WILSY_JWT_SECRET for session issuance so fail-closed signing configuration
    is tested without relying on ambient host state.
  v1.1.0-LEGACY-ID-SYMMETRY-CERT — Proves canonical and legacy ObjectId
    identity symmetry through MFA enrollment persistence and replay-safe reads.
  v1.0.0-CANONICAL-DB-BINDING-CERT — Initial focused certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No real credentials, tokens, or database are used.
TENANT BOUNDARY: Durable tenant, role, and permission fields are asserted intact.
AUTHORITY BOUNDARY: Unit evidence only; no authentication authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta
from typing import Any

import bcrypt
import pytest
import pyotp
from bson import ObjectId
from pymongo.errors import ConnectionFailure

from tools.eos.saas.auth import auth_registry
from tools.eos.saas.domain.auth import User


class _Result:
    def __init__(self, modified_count: int = 1) -> None:
        self.modified_count = modified_count


class _Collection:
    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []

    def insert_one(self, document: dict[str, Any]) -> _Result:
        self.documents.append(dict(document))
        return _Result()

    def find_one(self, query: dict[str, Any], **_kwargs: Any) -> dict[str, Any] | None:
        return next((doc for doc in self.documents if all(doc.get(k) == v for k, v in query.items())), None)

    def update_one(self, query: dict[str, Any], update: dict[str, Any], upsert: bool = False) -> _Result:
        document = self.find_one(query)
        if document is None:
            if not upsert:
                return _Result(0)
            document = dict(query)
            self.documents.append(document)
        document.update(update.get("$set", {}))
        return _Result()


class _Database:
    def __init__(self) -> None:
        self.collections = {name: _Collection() for name in ("users", "sessions", "otp_secrets", "refresh_tokens", "tenants", "principal_authorities")}
        self.collections["tenants"].documents.extend([
            {"tenant_id": "TENANT-UNIT", "name": "Unit", "industry": "Legal", "plan": "ENTERPRISE", "status": "ACTIVE"},
            {"tenant_id": "TENANT-NEW", "name": "New", "industry": "Legal", "plan": "ENTERPRISE", "status": "ACTIVE"},
        ])

    def __getitem__(self, name: str) -> _Collection:
        return self.collections[name]


def _user_document(registry: auth_registry.AuthRegistry, password: str = "ValidPassword!123") -> dict[str, Any]:
    return {
        "user_id": "WILSYAUTH-unit-user",
        "email": "unit@example.com",
        "firstName": "Unit",
        "lastName": "User",
        "role": "FIELD_DEPUTY",
        "permissions": ["legal:read"],
        "tenantId": "TENANT-UNIT",
        "passwordHash": registry.hash_password(password),
        "mfaRegistered": True,
        "hasSignedCovenant": True,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }


def test_source_has_no_private_mongo_lifecycle() -> None:
    source = inspect.getsource(auth_registry)
    assert "MongoClient(" not in source
    assert "MONGODB_URI" not in source
    assert "MONGO_URI" not in source
    assert "DATABASE_URL" not in source
    assert "mongodb://127.0.0.1" not in source
    assert "users_collection =" not in source
    assert "sessions_collection =" not in source
    assert "otp_secrets_collection =" not in source
    assert "refresh_tokens_collection =" not in source


def test_database_unavailable_fails_closed_and_recovers_without_reimport(monkeypatch: pytest.MonkeyPatch) -> None:
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: None)
    with pytest.raises(ConnectionFailure):
        registry.get_user_by_email("unit@example.com")
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)
    assert registry.get_user_by_email("unit@example.com") is None


def test_all_auth_collections_are_resolved_from_canonical_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", "unit-canonical-signing-secret")
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)

    user = registry.register_user("new@example.com", "ValidPassword!123", "New", "User", "USER", "TENANT-NEW")
    assert database["users"].documents[0]["email"] == "new@example.com"
    database["principal_authorities"].documents.append({"principal_id": user.id, "status": "ACTIVE", "revision": 0})

    secret = registry.create_otp_secret(user.id)
    assert database["otp_secrets"].documents[0]["user_id"] == user.id
    assert registry.get_otp_secret(user.id) == secret

    refresh = registry.generate_refresh_token(user.id)
    assert database["refresh_tokens"].documents[0]["token"] == refresh
    assert registry.validate_refresh_token(refresh) == user.id

    session = registry.create_session(user)
    assert database["sessions"].documents[0]["user_id"] == user.id
    assert session.tenantId == "TENANT-NEW"

    updated = registry.update_user(user.id, role="UPDATED_ROLE", permissions=["legal:write"])
    assert updated is not None
    assert updated.role == "UPDATED_ROLE"
    assert updated.permissions == ["legal:write"]


def test_authentication_and_durable_identity_semantics_remain_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)
    document = _user_document(registry)
    database["users"].documents.append(document)

    user = registry.authenticate("unit@example.com", "ValidPassword!123")
    assert user is not None
    assert user.tenantId == "TENANT-UNIT"
    assert user.role == "FIELD_DEPUTY"
    assert user.permissions == ["legal:read"]
    assert registry.authenticate("unit@example.com", "wrong-password") is None
    assert registry.authenticate("missing@example.com", "wrong-password") is None
    assert bcrypt.checkpw(b"ValidPassword!123", user.passwordHash.encode("utf-8"))


def test_refresh_token_expiry_semantics_remain_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)
    database["refresh_tokens"].documents.append({
        "token": "expired-token",
        "user_id": "WILSYAUTH-expired",
        "expires": datetime.utcnow() - timedelta(minutes=1),
    })
    assert registry.validate_refresh_token("expired-token") is None


def test_canonical_user_id_lookup_and_update_remain_symmetric(monkeypatch: pytest.MonkeyPatch) -> None:
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)
    document = _user_document(registry)
    database["users"].documents.append(document)

    user = registry.get_user_by_id("WILSYAUTH-unit-user")
    assert user is not None
    updated = registry.update_user(user.id, mfaRegistered=False)
    assert updated is not None
    assert updated.id == "WILSYAUTH-unit-user"
    assert updated.mfaRegistered is False
    assert document["tenantId"] == "TENANT-UNIT"
    assert document["role"] == "FIELD_DEPUTY"
    assert document["permissions"] == ["legal:read"]


def test_legacy_object_id_identity_reads_updates_and_preserves_otp_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)
    legacy_object_id = ObjectId("507f1f77bcf86cd799439011")
    existing_secret = "JBSWY3DPEHPK3PXP"
    document = _user_document(registry)
    document.pop("user_id")
    document["email"] = "legacy@example.com"
    document["mfaRegistered"] = False
    document["_id"] = legacy_object_id
    database["users"].documents.append(document)
    database["otp_secrets"].documents.append({
        "user_id": str(legacy_object_id),
        "secret": existing_secret,
        "created_at": datetime.utcnow(),
    })

    effective_id = str(legacy_object_id)
    user = registry.get_user_by_id(effective_id)
    assert user is not None
    assert user.id == effective_id
    assert user.tenantId == "TENANT-UNIT"
    assert user.role == "FIELD_DEPUTY"
    assert user.permissions == ["legal:read"]
    assert registry.get_otp_secret(effective_id) == existing_secret
    assert registry.verify_otp(effective_id, "000000") is False

    updated = registry.update_user(effective_id, mfaRegistered=True)
    assert updated is not None
    assert updated.id == effective_id
    assert updated.mfaRegistered is True
    assert document["mfaRegistered"] is True
    assert database["otp_secrets"].documents[0]["secret"] == existing_secret
    assert len(database["otp_secrets"].documents) == 1

    authenticated = registry.authenticate("legacy@example.com", "ValidPassword!123")
    assert authenticated is not None
    assert authenticated.id == effective_id
    assert authenticated.mfaRegistered is True


def test_malformed_or_nonexistent_legacy_identity_fails_closed_without_mutation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)
    canonical = _user_document(registry)
    database["users"].documents.append(canonical)
    before = dict(canonical)

    assert registry.get_user_by_id("not-an-object-id") is None
    assert registry.update_user("not-an-object-id", mfaRegistered=True) is None
    assert registry.update_user(str(ObjectId("507f1f77bcf86cd799439012")), mfaRegistered=True) is None
    assert canonical == before


def test_legacy_mfa_update_does_not_generate_or_rotate_otp_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database = _Database()
    registry = auth_registry.AuthRegistry()
    monkeypatch.setattr(auth_registry.kernel_db, "get_database", lambda: database)
    legacy_object_id = ObjectId("507f1f77bcf86cd799439013")
    existing_secret = "JBSWY3DPEHPK3PXP"
    document = _user_document(registry)
    document.pop("user_id")
    document["_id"] = legacy_object_id
    database["users"].documents.append(document)
    database["otp_secrets"].documents.append({"user_id": str(legacy_object_id), "secret": existing_secret})

    effective_id = str(legacy_object_id)
    assert registry.verify_otp(effective_id, pyotp.TOTP(existing_secret).now()) is True
    assert registry.update_user(effective_id, mfaRegistered=True) is not None
    assert registry.get_otp_secret(effective_id) == existing_secret
    assert len(database["otp_secrets"].documents) == 1


"""
ARTIFACT: tests/unit/test_auth_registry_canonical_db_binding.py
VERSION: v1.1.1-CANONICAL-SIGNING-CONFIG-CERT
AUTHORITY BOUNDARY: deterministic unit evidence for AuthRegistry persistence binding
TENANT POSTURE: durable tenant, role, and permissions remain unchanged
FAIL-CLOSED POSTURE: unavailable canonical database raises ConnectionFailure
FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
