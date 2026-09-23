"""Direct certificate for R1D-B0F-B3A tenant identity reconciliation.

TITLE: Legacy Super-Administrator Tenant Reconciliation Certificate
VERSION: v1.0.0-R1D-B0F-B3A-TENANT-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves exact principal selection, tenant invariants, immutable-field
         preservation, scoped revocation, transaction rollback, idempotency,
         and dry-run safety without a live database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_reconcile_legacy_super_admin_tenant.py
COLLABORATION / OWNERSHIP: Certificate for the paired auth migration utility.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-R1D-B0F-B3A-TENANT-RECONCILIATION - Covers migration success,
           refusal, replay, confirmation, and no-pseudo-tenant guarantees.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Fixtures use explicit canonical and legacy tenant identities.
AUTHORITY BOUNDARY: Test-only proof of the migration boundary; no auth grant.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from bson import ObjectId

from tools.eos.saas.auth.migrations import reconcile_legacy_super_admin_tenant as migration
from tools.eos.saas.auth.migrations.reconcile_legacy_super_admin_tenant import (
    CANONICAL_TENANT_ID,
    LEGACY_TENANT_ID,
    MigrationReport,
    TenantIdentityMigrationError,
    main,
    run_migration,
)


PRINCIPAL_ID = "507f1f77bcf86cd799439011"
OTHER_ID = "507f1f77bcf86cd799439012"


def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
    return all(document.get(key) == value for key, value in query.items())


class FakeResult:
    def __init__(self, *, matched: int = 0, modified: int = 0, deleted: int = 0) -> None:
        self.matched_count = matched
        self.modified_count = modified
        self.deleted_count = deleted


class FakeCollection:
    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self.docs = deepcopy(docs)
        self.write_calls = 0
        self.force_deleted_count: int | None = None

    def find(self, query: dict[str, Any], **_: Any) -> list[dict[str, Any]]:
        return [deepcopy(doc) for doc in self.docs if _matches(doc, query)]

    def update_one(self, query: dict[str, Any], update: dict[str, Any], **_: Any) -> FakeResult:
        self.write_calls += 1
        matches = [doc for doc in self.docs if _matches(doc, query)]
        if not matches:
            return FakeResult()
        doc = matches[0]
        changed = doc.get("tenantId") != update["$set"]["tenantId"]
        doc.update(update["$set"])
        return FakeResult(matched=1, modified=1 if changed else 0)

    def delete_many(self, query: dict[str, Any], **_: Any) -> FakeResult:
        self.write_calls += 1
        before = len(self.docs)
        self.docs = [doc for doc in self.docs if not _matches(doc, query)]
        deleted = before - len(self.docs)
        return FakeResult(deleted=deleted if self.force_deleted_count is None else self.force_deleted_count)


class FakeDatabase:
    name = "unit-certification"

    def __init__(self, *, duplicate_legacy: bool = False, pseudo: bool = False,
                 bad_target: bool = False, missing_target: bool = False,
                 wrong_old_tenant: bool = False) -> None:
        user = {
            "_id": ObjectId(PRINCIPAL_ID),
            "email": "principal@example.test",
            "firstName": "Root",
            "lastName": "Principal",
            "role": "SUPER_ADMIN",
            "permissions": ["*"],
            "tenantId": "other-tenant" if wrong_old_tenant else LEGACY_TENANT_ID,
            "passwordHash": "$2b$12$immutable",
            "mfaRegistered": True,
            "hasSignedCovenant": None,
            "updatedAt": "before",
        }
        users = [user]
        if duplicate_legacy:
            users.append(deepcopy(user))
        self.collections = {
            "users": FakeCollection(users),
            "sessions": FakeCollection([
                {"user_id": PRINCIPAL_ID, "token": "secret-jwt"},
                {"user_id": OTHER_ID, "token": "other-jwt"},
            ]),
            "refresh_tokens": FakeCollection([
                {"user_id": PRINCIPAL_ID, "token": "secret-refresh"},
                {"user_id": OTHER_ID, "token": "other-refresh"},
            ]),
            "tenants": FakeCollection([
                *([] if missing_target else [{"tenant_id": CANONICAL_TENANT_ID, "alias": "wilsy", "status": "ACTIVE", "verified": True}]),
                *([{"tenant_id": LEGACY_TENANT_ID}] if pseudo else []),
            ]),
            "otp_secrets": FakeCollection([{"user_id": PRINCIPAL_ID, "secret": "otp-secret"}]),
        }
        if bad_target:
            self.collections["tenants"].docs[0]["verified"] = False

    def __getitem__(self, key: str) -> FakeCollection:
        return self.collections[key]


class FakeSession:
    def __init__(self, database: FakeDatabase) -> None:
        self.database = database

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_: Any) -> None:
        return None

    def with_transaction(self, callback: Any) -> Any:
        snapshot = {name: deepcopy(collection.docs) for name, collection in self.database.collections.items()}
        try:
            return callback(self)
        except Exception:
            for name, docs in snapshot.items():
                self.database.collections[name].docs = docs
            raise


class FakeClient:
    def __init__(self, database: FakeDatabase) -> None:
        self.database = database

    def start_session(self) -> FakeSession:
        return FakeSession(self.database)


def test_dry_run_is_redacted_and_write_free() -> None:
    database = FakeDatabase()
    report = run_migration(principal_id=PRINCIPAL_ID, database=database, dry_run=True)
    assert report.state == "dry_run_pending"
    assert report.session_count == 1
    assert report.refresh_token_count == 1
    assert report.user_tenant_field_changed_only is False
    assert all(collection.write_calls == 0 for collection in database.collections.values())
    assert "passwordHash" not in report.to_dict()


def test_execution_changes_only_tenant_and_revokes_exact_principal() -> None:
    database = FakeDatabase()
    before = deepcopy(database["users"].docs[0])
    report = run_migration(
        principal_id=PRINCIPAL_ID,
        database=database,
        client=FakeClient(database),
        dry_run=False,
        confirm_old_tenant=LEGACY_TENANT_ID,
        confirm_new_tenant=CANONICAL_TENANT_ID,
    )
    after = database["users"].docs[0]
    assert report.state == "migrated"
    assert after["tenantId"] == CANONICAL_TENANT_ID
    assert {key: value for key, value in after.items() if key != "tenantId"} == {key: value for key, value in before.items() if key != "tenantId"}
    assert database["sessions"].docs == [{"user_id": OTHER_ID, "token": "other-jwt"}]
    assert database["refresh_tokens"].docs == [{"user_id": OTHER_ID, "token": "other-refresh"}]
    assert database["tenants"].docs == [{"tenant_id": CANONICAL_TENANT_ID, "alias": "wilsy", "status": "ACTIVE", "verified": True}]
    assert database["otp_secrets"].docs == [{"user_id": PRINCIPAL_ID, "secret": "otp-secret"}]


def test_second_execution_is_idempotent_noop() -> None:
    database = FakeDatabase()
    client = FakeClient(database)
    run_migration(principal_id=PRINCIPAL_ID, database=database, client=client, dry_run=False,
                  confirm_old_tenant=LEGACY_TENANT_ID, confirm_new_tenant=CANONICAL_TENANT_ID)
    calls = sum(collection.write_calls for collection in database.collections.values())
    report = run_migration(principal_id=PRINCIPAL_ID, database=database, client=client, dry_run=False,
                           confirm_old_tenant=LEGACY_TENANT_ID, confirm_new_tenant=CANONICAL_TENANT_ID)
    assert report.state == "already_reconciled"
    assert sum(collection.write_calls for collection in database.collections.values()) == calls


def test_transaction_rolls_back_user_and_revocations_on_partial_write_failure() -> None:
    database = FakeDatabase()
    before_user = deepcopy(database["users"].docs)
    before_sessions = deepcopy(database["sessions"].docs)
    database["sessions"].force_deleted_count = 0
    with pytest.raises(TenantIdentityMigrationError, match="PRINCIPAL_SESSION_REVOCATION_NOT_EXACT"):
        run_migration(principal_id=PRINCIPAL_ID, database=database, client=FakeClient(database), dry_run=False,
                      confirm_old_tenant=LEGACY_TENANT_ID, confirm_new_tenant=CANONICAL_TENANT_ID)
    assert database["users"].docs == before_user
    assert database["sessions"].docs == before_sessions


@pytest.mark.parametrize("kwargs,code,confirmed", [
    ({}, "EXPLICIT_TENANT_CONFIRMATION_REQUIRED", False),
    ({"duplicate_legacy": True}, "PRINCIPAL_IDENTITY_NOT_EXACT", True),
    ({"pseudo": True}, "LEGACY_PSEUDO_TENANT_EXISTS", True),
    ({"bad_target": True}, "CANONICAL_TENANT_VERIFIED_MISMATCH", True),
    ({"missing_target": True}, "CANONICAL_TENANT_NOT_EXACTLY_ONE", True),
    ({"wrong_old_tenant": True}, "LEGACY_PRINCIPAL_NOT_EXACTLY_ONE", True),
])
def test_preconditions_fail_closed_without_writes(kwargs: dict[str, Any], code: str, confirmed: bool) -> None:
    database = FakeDatabase(**kwargs)
    with pytest.raises(TenantIdentityMigrationError) as error:
        run_migration(principal_id=PRINCIPAL_ID, database=database, client=FakeClient(database), dry_run=False,
                      confirm_old_tenant=LEGACY_TENANT_ID if confirmed else None,
                      confirm_new_tenant=CANONICAL_TENANT_ID if confirmed else None)
    assert error.value.code == code
    assert all(collection.write_calls == 0 for collection in database.collections.values())


def test_invalid_principal_and_partial_reconciliation_are_denied() -> None:
    database = FakeDatabase()
    with pytest.raises(TenantIdentityMigrationError, match="INVALID_PRINCIPAL_OBJECT_ID"):
        run_migration(principal_id="not-an-object-id", database=database)
    database["users"].docs[0]["tenantId"] = CANONICAL_TENANT_ID
    with pytest.raises(TenantIdentityMigrationError, match="PARTIAL_RECONCILIATION_REQUIRES_REVIEW"):
        run_migration(principal_id=PRINCIPAL_ID, database=database, dry_run=True)


def test_cli_connects_before_database_access_and_disconnects_owned_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    events: list[str] = []
    database = object()
    client = object()
    report = MigrationReport(
        state="dry_run_pending", database_name=None, principal_id=PRINCIPAL_ID,
        old_tenant_id=LEGACY_TENANT_ID, new_tenant_id=CANONICAL_TENANT_ID,
        role="SUPER_ADMIN", mfa_registered=True, session_count=0,
        refresh_token_count=0, user_tenant_field_changed_only=False,
        stale_sessions_revoked=False, stale_refresh_tokens_revoked=False,
        dry_run=True,
    )
    monkeypatch.setattr(migration.kernel_db, "connect_db", lambda: (events.append("connect") or (True, "ok")))
    monkeypatch.setattr(migration.kernel_db, "get_database", lambda: (events.append("get_database") or database))
    monkeypatch.setattr(migration.kernel_db, "get_client", lambda: (events.append("get_client") or client))
    monkeypatch.setattr(migration.kernel_db, "disconnect_db", lambda: events.append("disconnect"))
    monkeypatch.setattr(migration, "run_migration", lambda **kwargs: (events.append("run") or report))
    assert main(["--principal-id", PRINCIPAL_ID, "--dry-run"]) == 0
    assert events == ["connect", "get_database", "get_client", "run", "disconnect"]


def test_cli_connection_failure_is_nonzero_and_does_not_disconnect(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    events: list[str] = []
    monkeypatch.setattr(migration.kernel_db, "connect_db", lambda: (events.append("connect") or (False, "unavailable")))
    monkeypatch.setattr(migration.kernel_db, "disconnect_db", lambda: events.append("disconnect"))
    assert main(["--principal-id", PRINCIPAL_ID, "--dry-run"]) == 2
    assert events == ["connect"]
    assert capsys.readouterr().out.strip() == "AUTH_DATABASE_UNAVAILABLE"


def test_cli_database_failure_closes_owned_connection(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    events: list[str] = []
    monkeypatch.setattr(migration.kernel_db, "connect_db", lambda: (events.append("connect") or (True, "ok")))
    monkeypatch.setattr(migration.kernel_db, "get_database", lambda: (events.append("get_database") or None))
    monkeypatch.setattr(migration.kernel_db, "get_client", lambda: events.append("get_client"))
    monkeypatch.setattr(migration.kernel_db, "disconnect_db", lambda: events.append("disconnect"))
    assert main(["--principal-id", PRINCIPAL_ID, "--dry-run"]) == 2
    assert events == ["connect", "get_database", "get_client", "disconnect"]
    assert capsys.readouterr().out.strip() == "AUTH_DATABASE_UNAVAILABLE"


def test_cli_has_no_duplicate_connector_or_uri_parser() -> None:
    source = Path(migration.__file__).read_text(encoding="utf-8")
    assert "MongoClient" not in source
    assert "MONGODB_URI" not in source


# ARTIFACT: test_reconcile_legacy_super_admin_tenant.py
# VERSION: v1.0.0-R1D-B0F-B3A-TENANT-RECONCILIATION
# AUTHORITY BOUNDARY: certificate-only proof of exact identity migration
# TENANT POSTURE: explicit tenant fixtures and principal scope
# FAIL-CLOSED POSTURE: refusal and rollback are asserted without weakening production guards
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
