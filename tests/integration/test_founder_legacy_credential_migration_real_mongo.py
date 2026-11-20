"""TITLE: Founder Legacy Credential Migration Real-Mongo Certificate
VERSION: v1.0.0-EXACT-SOURCE-ISSUER-REPLICA-CERT
AUTHORITY: Canonical credential repository and immutable receipt in transaction.
EPITOME: Verify first issuance, readback, replay, no cross-tenant mutation and
  competing credential rejection with synthetic sources on disposable Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_founder_legacy_credential_migration_real_mongo.py
COLLABORATION / OWNERSHIP: Legacy Founder migration command and canonical
  PrincipalCredentialRepository; principal assessment has separate focused unit
  certificate. Synthetic password/OTP verifier is not live authentication.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.0.0-EXACT-SOURCE-ISSUER-REPLICA-CERT establishes physically
  committed majority Mongo credential and audit, stable replay, denied
  authentication, competing credential and no role/subscription writes.
COMPLIANCE: POPIA s19; GDPR Article32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic hashes, UUID database and auto cleanup.
TENANT BOUNDARY: Test-only exact tenant, no real Founder target.
AUTHORITY BOUNDARY: Auth verifier is test double; no real MFA/issuer claims.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Rejection persists no credential or audit.
"""
from __future__ import annotations

from dataclasses import dataclass
import os
import uuid
from typing import Any

from bson import ObjectId
from pymongo import MongoClient
import pytest

from tools.eos.auth import founder_legacy_credential_migration as migration
from tools.eos.auth.principal_credential import PrincipalCredential
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialRepository,
)

HASH = "$2b$12$" + "d" * 53


@dataclass
class _User:
    id: str
    tenantId: str
    mfaRegistered: bool = True


class _LegacyOwnerAuth:
    def __init__(self, principal_id: str, tenant_id: str) -> None:
        self.user = _User(principal_id, tenant_id)

    def authenticate(self, email: str, password: str) -> _User | None:
        return self.user if password == "synthetic-password" else None

    def verify_otp(self, user_id: str, code: str) -> bool:
        return user_id == self.user.id and code == "123456"


class _DatabaseProxy:
    """Exactly named test-only database facade, never connects to wilsy."""
    name = "wilsy"

    def __init__(self, database: Any) -> None:
        self.database = database

    def __getitem__(self, key: str) -> Any:
        return self.database[key]


@pytest.fixture
def isolated_source(monkeypatch: pytest.MonkeyPatch):
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI_REQUIRED")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    if hello.get("setName") != "wilsyGlobalPrincipalCertRS" or not hello.get(
        "isWritablePrimary", hello.get("ismaster")
    ):
        pytest.fail("WRONG_GLOBAL_PRINCIPAL_TEST_REPLICA")
    database = client["founder_legacy_migration_cert_" + uuid.uuid4().hex]
    principal_id = str(ObjectId())
    tenant = "synthetic-founder-" + uuid.uuid4().hex
    email = "cert-owner@example.com"
    source = {
        "_id": ObjectId(principal_id),
        "email": email,
        "tenantId": tenant,
        "passwordHash": HASH,
        "credential_revision": 0,
        "mfaRegistered": True,
    }
    database["users"].insert_one(source)
    monkeypatch.setattr(migration, "FOUNDER_EMAIL", email)
    monkeypatch.setattr(migration, "FOUNDER_TENANT_ID", tenant)
    monkeypatch.setattr(migration.kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(migration.kernel_db, "get_database",
                        lambda: _DatabaseProxy(database))
    monkeypatch.setattr(migration, "get_auth_registry",
                        lambda _value: _LegacyOwnerAuth(principal_id, tenant))

    def assessed(*, document: dict[str, Any],
                 matching_email_record_count: int,
                 session: Any) -> Any:
        assert matching_email_record_count == 1
        assert document["_id"] == source["_id"]
        credential = PrincipalCredential(
            principal_id=principal_id,
            normalized_email=email,
            password_hash=HASH,
            credential_revision=0,
            mfa_enabled=True,
        )
        from types import SimpleNamespace
        return SimpleNamespace(
            disposition="ELIGIBLE_FOR_GOVERNED_MIGRATION",
            credential=credential, tenant_id=tenant,
            reason_code="LEGACY_CREDENTIAL_AUTHORITIES_MATCH",
        )

    monkeypatch.setattr(migration, "assess_legacy_user_credential", assessed)
    try:
        yield client, database, email, principal_id
    finally:
        client.drop_database(database.name)
        client.close()


def test_source_owned_issuance_and_idempotent_audit_replay(
    isolated_source: tuple[Any, Any, str, str],
) -> None:
    _client, db, email, principal_id = isolated_source
    first = migration.migrate_founder_credential(
        password="synthetic-password", otp_code="123456",
    )
    assert first["credential_state"] == "ISSUED"
    assert first["migration_audit"] == "PERSISTED"
    credential = PrincipalCredentialRepository.get_by_email(
        email, db["principal_credentials"],
    )
    assert credential.principal_id == principal_id
    assert credential.mfa_enabled is True
    assert credential.password_hash == HASH
    replay = migration.migrate_founder_credential(
        password="synthetic-password", otp_code="123456",
    )
    assert replay["credential_state"] == "ALREADY_ISSUED"
    assert db["principal_credentials"].count_documents({}) == 1
    assert db[migration._AUDIT_COLLECTION].count_documents({}) == 1
    for forbidden in ("role_assignments", "tenant_memberships", "subscriptions",
                      "wilsy_ai_entitlements"):
        assert db[forbidden].count_documents({}) == 0


def test_wrong_owner_password_or_otp_never_creates_credential(
    isolated_source: tuple[Any, Any, str, str],
) -> None:
    _client, db, _email, _principal_id = isolated_source
    for password, otp, expected in (
        ("bad-password", "123456", "FOUNDER_LEGACY_OWNER_PASSWORD_NOT_VERIFIED"),
        ("synthetic-password", "000000", "FOUNDER_LEGACY_OWNER_MFA_NOT_VERIFIED"),
    ):
        with pytest.raises(migration.FounderCredentialMigrationRejected,
                           match=expected):
            migration.migrate_founder_credential(password=password, otp_code=otp)
    assert db["principal_credentials"].count_documents({}) == 0
    assert db[migration._AUDIT_COLLECTION].count_documents({}) == 0


def test_competing_credential_does_not_overwrite_current_source(
    isolated_source: tuple[Any, Any, str, str],
) -> None:
    _client, db, email, _principal_id = isolated_source
    PrincipalCredentialRepository.ensure_indexes(db["principal_credentials"])
    PrincipalCredentialRepository.insert(PrincipalCredential(
        principal_id="different-principal",
        normalized_email=email,
        password_hash=HASH,
        credential_revision=0,
        mfa_enabled=True,
    ), db["principal_credentials"])
    with pytest.raises(migration.FounderCredentialMigrationRejected,
                       match="FOUNDER_GLOBAL_CREDENTIAL_CONFLICT"):
        migration.migrate_founder_credential(
            password="synthetic-password", otp_code="123456",
        )
    assert db["principal_credentials"].count_documents({}) == 1
    assert db[migration._AUDIT_COLLECTION].count_documents({}) == 0


# ARTIFACT: test_founder_legacy_credential_migration_real_mongo.py
# VERSION: v1.0.0-EXACT-SOURCE-ISSUER-REPLICA-CERT
# AUTHORITY BOUNDARY: synthetic factor test + physical majority Mongo credential
# TENANT POSTURE: UUID-isolated synthetic Founder, never live identity
# FAIL-CLOSED POSTURE: wrong factor, conflict, no receipt never becomes issuance
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
