"""WILSY OS AuthRegistry session-currentness BSON UTC certificate.

TITLE: AuthRegistry Session Currentness Real-Mongo Certificate
VERSION: v1.1.0-CONSOLIDATION-IDENTITY-TRANSACTION-CERT
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Proves default PyMongo BSON datetime hydration is safely normalized without changing authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_auth_registry_session_currentness_real_mongo.py
COLLABORATION / OWNERSHIP: AuthRegistry and Kernel Mongo runtime.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
  v1.1.0-CONSOLIDATION-IDENTITY-TRANSACTION-CERT adds real BSON identity corruption, collision, MFA preservation and transaction rollback evidence.
  v1.0.0-P3-R3G-C6-A established naive/aware UTC, expiry, binding, and transaction proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic data; no usable bearer or credential.
TENANT BOUNDARY: Exact tenant/principal/reference predicates remain mandatory.
AUTHORITY BOUNDARY: Session currentness read only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import os, uuid
from types import SimpleNamespace
from typing import Any, Iterator, cast
import pytest
from bson import ObjectId
from pymongo import MongoClient
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
TENANT, PRINCIPAL, REFERENCE = "tenant-c6-a", "principal-c6-a", "WILSYSESSION-c6-a"
NOW = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)

class TenantRegistry:
    @classmethod
    def resolve_canonical_tenant(cls, value: object, *, allow_alias: bool = False, session: object = None) -> object:
        del allow_alias, session
        if value != TENANT: raise ValueError("AUTH_TENANT_CANONICAL_INVALID")
        return SimpleNamespace(tenant_id=TENANT)

@pytest.fixture()
def context(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[MongoClient[Any], Any, AuthRegistry]]:
    client: MongoClient[Any] = MongoClient(URI, serverSelectionTimeoutMS=3000)
    hello = client.admin.command("hello"); assert hello.get("setName") == "wilsyVendorCertRS" and hello.get("isWritablePrimary") is True
    database = client["wilsy_auth_session_utc_" + uuid.uuid4().hex]; assert database.name != "wilsy"
    monkeypatch.setattr(kernel_db, "_db", database); monkeypatch.setattr(kernel_db, "_client", client); monkeypatch.setattr(kernel_db, "_ready", True)
    auth = AuthRegistry(); cast(Any, auth).tenant_registry = TenantRegistry
    database["users"].insert_one({"user_id": PRINCIPAL, "email": "c6a@example.com", "firstName": "C6", "lastName": "A", "role": "USER", "permissions": [], "tenantId": TENANT, "passwordHash": "synthetic", "credential_revision": 7, "mfaRegistered": True, "hasSignedCovenant": True, "createdAt": NOW.replace(tzinfo=None), "updatedAt": NOW.replace(tzinfo=None)})
    try: yield client, database, auth
    finally: client.drop_database(database.name); client.close()

def _row(expires: object) -> dict[str, object]:
    return {"tenant_id": TENANT, "user_id": PRINCIPAL, "session_reference": REFERENCE, "expires_at": expires}

def test_default_bson_future_and_expired_session_with_caller_transaction(context) -> None:
    """Certify session expiry through the caller-owned real transaction."""
    client, database, auth = context
    database["sessions"].insert_one(_row(NOW + timedelta(minutes=1)))
    with client.start_session() as session:
        with session.start_transaction():
            assert auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW, session=session)
    persisted = database["sessions"].find_one({"session_reference": REFERENCE}); assert persisted is not None and cast(datetime, persisted["expires_at"]).tzinfo is None
    database["sessions"].update_one({"session_reference": REFERENCE}, {"$set": {"expires_at": NOW - timedelta(seconds=1)}})
    assert not auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)

def test_aware_utc_and_malformed_or_binding_mismatch(context) -> None:
    """Malformed expiry and mismatched persisted principals never pass currentness."""
    _client, database, auth = context
    database["sessions"].insert_one(_row(NOW + timedelta(minutes=1)))
    assert auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)
    database["sessions"].update_one({"session_reference": REFERENCE}, {"$set": {"expires_at": "malformed"}})
    assert not auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)
    database["sessions"].replace_one({"session_reference": REFERENCE}, {**_row(NOW + timedelta(minutes=1)), "user_id": "foreign"})
    assert not auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)


@pytest.mark.parametrize("mongo_id", [None, False, 42, "507f1f77bcf86cd799439099"])
def test_real_bson_corrupt_identity_cannot_hydrate_or_create_authority(context, mongo_id: object) -> None:
    """Persisted non-ObjectId fallbacks fail without repairing the document."""
    _client, database, auth = context
    document = {"_id": mongo_id, "tenantId": TENANT, "email": "malformed@example.com"}
    database.users.insert_one(document)
    with pytest.raises(AuthRegistryTenantError, match="^AUTH_PRINCIPAL_IDENTITY_INVALID$"):
        auth.get_user_by_email("malformed@example.com")
    assert database.users.find_one({"_id": mongo_id}) == document
    assert database.sessions.count_documents({"tenant_id": TENANT}) == 0
    assert database.refresh_tokens.count_documents({"tenant_id": TENANT}) == 0


def test_real_legacy_identity_preserves_mfa_and_transaction_rollback(context) -> None:
    """Legacy BSON identity remains stable without backfill across commit and abort."""
    client, database, auth = context
    legacy_id = ObjectId()
    principal = str(legacy_id)
    database.users.insert_one({"_id": legacy_id, "tenantId": TENANT, "email": "legacy@example.com", "mfaRegistered": True})
    database.otp_secrets.insert_one({"user_id": principal, "secret": "synthetic-factor-preserve"})
    before = database.users.find_one({"_id": legacy_id})
    with client.start_session() as session:
        session.start_transaction()
        user = auth.get_user_by_id(principal, session=session)
        assert user is not None and user.id == principal and user.mfaRegistered
        assert auth.get_credential_revision(TENANT, principal, session=session) == 0
        assert auth.compare_and_swap_password_hash(TENANT, principal, 0, "synthetic-rollback-verifier", session=session) == 1
        session.abort_transaction()
    assert database.users.find_one({"_id": legacy_id}) == before
    with client.start_session() as session:
        with session.start_transaction():
            assert auth.compare_and_swap_password_hash(TENANT, principal, 0, "synthetic-committed-verifier", session=session) == 1
    persisted = database.users.find_one({"_id": legacy_id})
    assert persisted is not None and "user_id" not in persisted
    assert persisted["credential_revision"] == 1
    assert auth.get_otp_secret(principal) == "synthetic-factor-preserve"
    assert database.otp_secrets.count_documents({"user_id": principal}) == 1


def test_real_canonical_legacy_collision_rejects_read_and_mfa_write(context) -> None:
    """A real identity collision cannot redirect auth reads or mutation predicates."""
    _client, database, auth = context
    legacy_id = ObjectId()
    principal = str(legacy_id)
    database.users.insert_many([
        {"_id": legacy_id, "tenantId": TENANT, "email": "legacy@example.com", "mfaRegistered": False},
        {"user_id": principal, "tenantId": TENANT, "email": "collision@example.com", "mfaRegistered": False},
    ])
    for operation in [lambda: auth.get_user_by_id(principal), lambda: auth.get_user_by_email("legacy@example.com"), lambda: auth.update_user(principal, mfaRegistered=True)]:
        with pytest.raises(AuthRegistryTenantError, match="^AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS$"):
            operation()
    assert database.users.count_documents({"tenantId": TENANT, "mfaRegistered": True}) == 1  # Existing canonical fixture only.
    assert database.users.find_one({"_id": legacy_id})["mfaRegistered"] is False


def test_real_foreign_tenant_cannot_supply_credential_identity(context) -> None:
    """A valid ObjectId in another tenant cannot satisfy an exact credential read."""
    _client, database, auth = context
    legacy_id = ObjectId()
    database.users.insert_one({"_id": legacy_id, "tenantId": "foreign-tenant", "email": "foreign@example.com"})
    with pytest.raises(AuthRegistryTenantError, match="^AUTH_PRINCIPAL_CREDENTIAL_NOT_FOUND$"):
        auth.get_credential_revision(TENANT, str(legacy_id))
    assert "user_id" not in database.users.find_one({"_id": legacy_id})


# ARTIFACT: test_auth_registry_session_currentness_real_mongo.py
# VERSION: v1.1.0-CONSOLIDATION-IDENTITY-TRANSACTION-CERT
# AUTHORITY BOUNDARY: Real-Mongo session-currentness certification only.
# TENANT POSTURE: Exact tenant/principal/reference scope.
# FAIL-CLOSED POSTURE: Malformed, expired, missing, or mismatched sessions deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
