"""WILSY OS AuthRegistry session-currentness BSON UTC certificate.

TITLE: AuthRegistry Session Currentness Real-Mongo Certificate
VERSION: v1.0.0-P3-R3G-C6-A
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Proves default PyMongo BSON datetime hydration is safely normalized without changing authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_auth_registry_session_currentness_real_mongo.py
COLLABORATION / OWNERSHIP: AuthRegistry and Kernel Mongo runtime.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-C6-A establishes naive/aware UTC, expiry, binding, and transaction proofs.
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
from pymongo import MongoClient
from tools.eos.kernel import db as kernel_db
from tools.eos.saas.auth.auth_registry import AuthRegistry

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
    client, database, auth = context
    database["sessions"].insert_one(_row(NOW + timedelta(minutes=1)))
    with client.start_session() as session:
        with session.start_transaction():
            assert auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW, session=session)
    persisted = database["sessions"].find_one({"session_reference": REFERENCE}); assert persisted is not None and cast(datetime, persisted["expires_at"]).tzinfo is None
    database["sessions"].update_one({"session_reference": REFERENCE}, {"$set": {"expires_at": NOW - timedelta(seconds=1)}})
    assert not auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)

def test_aware_utc_and_malformed_or_binding_mismatch(context) -> None:
    _client, database, auth = context
    database["sessions"].insert_one(_row(NOW + timedelta(minutes=1)))
    assert auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)
    database["sessions"].update_one({"session_reference": REFERENCE}, {"$set": {"expires_at": "malformed"}})
    assert not auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)
    database["sessions"].replace_one({"session_reference": REFERENCE}, {**_row(NOW + timedelta(minutes=1)), "user_id": "foreign"})
    assert not auth.is_session_current(TENANT, PRINCIPAL, REFERENCE, at=NOW)

# ARTIFACT: test_auth_registry_session_currentness_real_mongo.py
# VERSION: v1.0.0-P3-R3G-C6-A
# AUTHORITY BOUNDARY: Real-Mongo session-currentness certification only.
# TENANT POSTURE: Exact tenant/principal/reference scope.
# FAIL-CLOSED POSTURE: Malformed, expired, missing, or mismatched sessions deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
