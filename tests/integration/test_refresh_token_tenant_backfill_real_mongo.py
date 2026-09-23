"""Disposable real-Mongo certification for exact refresh tenant backfill.

TITLE: WILSY OS Refresh Token Tenant Backfill Real-Mongo Certificate
VERSION: v1.0.0-R10C2D-REFRESH-TENANT-EXACT-BACKFILL-REAL-MONGO-CERT
AUTHORITY: WILSY OS migration certification governance
EPITOME: Exercises the governed migration participant against synthetic rows
    in isolated disposable replica-set databases.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_refresh_token_tenant_backfill_real_mongo.py
COLLABORATION / OWNERSHIP: The migration owns exact reconciliation; this
    certificate owns only disposable fixtures and assertions.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2D-REFRESH-TENANT-EXACT-BACKFILL-REAL-MONGO-CERT - Certifies
    dry-run, exact mapping, guarded APPLY, caller commit/abort, isolation,
    idempotency, bounds, and transaction non-ownership on MongoDB.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only aggregate assertions are reported. Synthetic
    bearer values never enter assertion messages or output.
TENANT BOUNDARY: Every expected tenant is derived from an exact synthetic
    user document; no canonical resolver or cross-tenant inference is used.
AUTHORITY BOUNDARY: Test certificate only; no production migration, token,
    credential, JWT, MFA, Node, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains the exclusive financial
    execution authority.
"""
from __future__ import annotations

import ast
import inspect
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

import pytest
from bson import ObjectId
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.auth.migrations import refresh_token_tenant_backfill as migration


URI_ENV = "R10C2D_REFRESH_TENANT_BACKFILL_MONGO_URI"
DATABASE_PREFIX = "wilsy_r10c2d_refresh_backfill_"
REPLICA_SET = "wilsyVendorCertRS"
BASE_TIME = datetime(2026, 9, 22, 8, 0, tzinfo=timezone.utc)
EXPIRY = BASE_TIME + timedelta(days=1)


class DisposableMongoContext:
    """Own one synthetic database while the test owns the client lifetime."""

    def __init__(self, client: MongoClient[Any], database_name: str) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        self.users = self.database.get_collection("users")
        self.refresh_tokens = self.database.get_collection("refresh_tokens")


def _runtime_uri() -> str:
    """Require an explicit loopback Mongo URI and never disclose it."""

    uri = os.environ.get(URI_ENV, "")
    if not uri:
        pytest.fail(f"{URI_ENV} is required")
    parsed = urlparse(uri)
    if parsed.scheme not in {"mongodb", "mongodb+srv"}:
        pytest.fail("Mongo URI scheme is not admissible")
    if parsed.scheme == "mongodb+srv" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        pytest.fail("certificate requires a loopback Mongo endpoint")
    if parsed.path.strip("/") in {"wilsy", "wilsy/"} or "mongodb.net" in uri or "atlas" in uri.lower():
        pytest.fail("canonical or hosted Mongo endpoint is not admissible")
    return uri


def _open_runtime() -> MongoClient[Any]:
    """Open and certify the externally owned writable replica set."""

    client: MongoClient[Any] = MongoClient(
        _runtime_uri(),
        replicaSet=REPLICA_SET,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
    )
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary") is not True:
            raise RuntimeError("writable replica-set primary is required")
        address = client.address
        if not address or address[0] not in {"127.0.0.1", "localhost", "::1"}:
            raise RuntimeError("non-loopback primary")
        if not str(client.server_info().get("version", "")).startswith("7."):
            raise RuntimeError("MongoDB 7.x is required")
        return client
    except Exception:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_client() -> Iterator[MongoClient[Any]]:
    """Provide the externally owned test client and close only that client."""

    client = _open_runtime()
    try:
        yield client
    finally:
        client.close()


@pytest.fixture()
def mongo_context(mongo_client: MongoClient[Any]) -> Iterator[DisposableMongoContext]:
    """Create and drop one UUID-scoped database for each test."""

    context = DisposableMongoContext(mongo_client, DATABASE_PREFIX + uuid.uuid4().hex)
    assert len(context.database_name) <= 63
    assert context.database_name != "wilsy"
    try:
        yield context
    finally:
        mongo_client.drop_database(context.database_name)
        assert context.database_name not in mongo_client.list_database_names()


def _token(seed: str) -> str:
    """Return a deterministic synthetic bearer value for fixture rows."""

    return f"synthetic-r10c2d-{seed}-{uuid.uuid4().hex}"


def _insert_user(
    context: DisposableMongoContext,
    *,
    user_id: str | None,
    tenant_id: str,
    user_object_id: ObjectId | None = None,
) -> ObjectId:
    """Insert one synthetic user with the requested identity shape."""

    object_id = user_object_id or ObjectId()
    document: dict[str, Any] = {"_id": object_id, "tenantId": tenant_id}
    if user_id is not None:
        document["user_id"] = user_id
    context.users.insert_one(document)
    return object_id


def _insert_refresh(
    context: DisposableMongoContext,
    user_id: str,
    *,
    tenant_id: Any = ...,
    row_id: ObjectId | None = None,
    token_seed: str = "row",
) -> ObjectId:
    """Insert one synthetic refresh row without exposing its bearer value."""

    object_id = row_id or ObjectId()
    document: dict[str, Any] = {
        "_id": object_id,
        "user_id": user_id,
        "token": _token(token_seed),
        "expires": EXPIRY,
        "metadata": "protected-metadata",
    }
    if tenant_id is not ...:
        document["tenant_id"] = tenant_id
    context.refresh_tokens.insert_one(document)
    return object_id


def _read(context: DisposableMongoContext, row_id: ObjectId, session: Any = None) -> dict[str, Any]:
    """Read one synthetic row by exact id, optionally inside a caller session."""

    kwargs: dict[str, Any] = {}
    if session is not None:
        kwargs["session"] = session
    row = context.refresh_tokens.find_one({"_id": row_id}, **kwargs)
    assert row is not None
    return dict(row)


def _assert_protected(before: dict[str, Any], after: dict[str, Any]) -> None:
    """Prove the migration changed no bearer or unrelated protected field."""

    for field in ("_id", "user_id", "token", "expires", "metadata"):
        assert after.get(field) == before.get(field)


def _indexes(collection: Any) -> tuple[tuple[str, tuple[tuple[str, int], ...]], ...]:
    """Return a safe, deterministic index topology snapshot."""

    result: list[tuple[str, tuple[tuple[str, int], ...]]] = []
    for name, spec in collection.index_information().items():
        result.append((name, tuple((str(key), int(value)) for key, value in spec["key"])))
    return tuple(sorted(result))


def test_real_runtime_is_loopback_writable_replica_set(mongo_client: MongoClient[Any]) -> None:
    """Certify the disposable Mongo runtime supports the required topology."""

    hello = mongo_client.admin.command("hello")
    assert hello["setName"] == REPLICA_SET
    assert hello["isWritablePrimary"] is True
    address = mongo_client.address
    assert address is not None
    assert address[0] in {"127.0.0.1", "localhost", "::1"}
    assert str(mongo_client.server_info()["version"]).startswith("7.")


def test_real_dry_run_legacy_and_canonical_paths_have_zero_writes(mongo_context: DisposableMongoContext) -> None:
    """Certify aggregate planning for both exact identity paths."""

    legacy_id = ObjectId()
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-legacy", user_object_id=legacy_id)
    canonical = "WILSYAUTH-canonical-r10c2d"
    _insert_user(mongo_context, user_id=canonical, tenant_id="tenant-canonical")
    legacy_row = _insert_refresh(mongo_context, str(legacy_id), token_seed="legacy")
    canonical_row = _insert_refresh(mongo_context, canonical, token_seed="canonical")
    before = (_read(mongo_context, legacy_row), _read(mongo_context, canonical_row))
    report = migration.reconcile_refresh_tokens(
        refresh_tokens=mongo_context.refresh_tokens,
        users=mongo_context.users,
    )
    assert report.state == "DRY_RUN_READY"
    assert report.eligible_rows == report.planned_writes == 2
    assert report.applied_writes == report.verified_writes == 0
    assert _read(mongo_context, legacy_row).get("tenant_id") is None
    assert _read(mongo_context, canonical_row).get("tenant_id") is None
    _assert_protected(before[0], _read(mongo_context, legacy_row))
    _assert_protected(before[1], _read(mongo_context, canonical_row))


def test_real_global_unsafe_collision_has_zero_writes_and_abort_is_clean(mongo_context: DisposableMongoContext) -> None:
    """Certify canonical/legacy collision blocks APPLY without mutation."""

    collision = str(ObjectId())
    _insert_user(mongo_context, user_id=collision, tenant_id="tenant-canonical")
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-legacy", user_object_id=ObjectId(collision))
    row_id = _insert_refresh(mongo_context, collision, token_seed="collision")
    before = _read(mongo_context, row_id)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        report = migration.reconcile_refresh_tokens(
            refresh_tokens=mongo_context.refresh_tokens,
            users=mongo_context.users,
            mode=migration.MigrationMode.APPLY,
            session=session,
        )
        assert report.state == "APPLY_BLOCKED"
        assert report.ambiguous_rows == 1
        assert _read(mongo_context, row_id, session).get("tenant_id") is None
        session.abort_transaction()
    _assert_protected(before, _read(mongo_context, row_id))


@pytest.mark.parametrize("bad_tenant", [None, "", "tenant-other"])
def test_real_present_corrupt_tenant_is_not_repaired(
    mongo_context: DisposableMongoContext, bad_tenant: Any
) -> None:
    """Certify present null, empty, and mismatched tenant values are blocked."""

    canonical = "WILSYAUTH-corrupt-r10c2d"
    _insert_user(mongo_context, user_id=canonical, tenant_id="tenant-real")
    row_id = _insert_refresh(mongo_context, canonical, tenant_id=bad_tenant, token_seed="corrupt")
    before = _read(mongo_context, row_id)
    report = migration.reconcile_refresh_tokens(
        refresh_tokens=mongo_context.refresh_tokens,
        users=mongo_context.users,
    )
    assert report.state == "DRY_RUN_BLOCKED"
    assert report.corrupt_rows == 1
    after = _read(mongo_context, row_id)
    assert after.get("tenant_id") == bad_tenant
    _assert_protected(before, after)


def test_real_apply_requires_session_and_active_transaction(mongo_context: DisposableMongoContext) -> None:
    """Certify APPLY cannot write without an active caller transaction."""

    legacy_id = ObjectId()
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-real", user_object_id=legacy_id)
    row_id = _insert_refresh(mongo_context, str(legacy_id), token_seed="requires-session")
    with pytest.raises(migration.RefreshTokenTenantBackfillError) as no_session:
        migration.reconcile_refresh_tokens(
            refresh_tokens=mongo_context.refresh_tokens,
            users=mongo_context.users,
            mode=migration.MigrationMode.APPLY,
        )
    assert no_session.value.code == "APPLY_TRANSACTION_REQUIRED"
    with mongo_context.client.start_session() as session:
        with pytest.raises(migration.RefreshTokenTenantBackfillError) as inactive:
            migration.reconcile_refresh_tokens(
                refresh_tokens=mongo_context.refresh_tokens,
                users=mongo_context.users,
                mode=migration.MigrationMode.APPLY,
                session=session,
            )
        assert inactive.value.code == "APPLY_TRANSACTION_REQUIRED"
    assert _read(mongo_context, row_id).get("tenant_id") is None


def test_real_caller_abort_rolls_back_verified_migration(mongo_context: DisposableMongoContext) -> None:
    """Certify a verified participant write disappears on caller abort."""

    legacy_id = ObjectId()
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-abort", user_object_id=legacy_id)
    row_id = _insert_refresh(mongo_context, str(legacy_id), token_seed="abort")
    before = _read(mongo_context, row_id)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        report = migration.reconcile_refresh_tokens(
            refresh_tokens=mongo_context.refresh_tokens,
            users=mongo_context.users,
            mode=migration.MigrationMode.APPLY,
            session=session,
        )
        assert report.state == "APPLY_VERIFIED_PENDING_CALLER_COMMIT"
        assert report.applied_writes == report.verified_writes == 1
        assert _read(mongo_context, row_id, session).get("tenant_id") == "tenant-abort"
        session.abort_transaction()
    after = _read(mongo_context, row_id)
    assert after.get("tenant_id") is None
    _assert_protected(before, after)


def test_real_caller_commit_persists_exact_tenant_and_protected_fields(mongo_context: DisposableMongoContext) -> None:
    """Certify caller commit persists one exact tenant field only."""

    legacy_id = ObjectId()
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-commit", user_object_id=legacy_id)
    row_id = _insert_refresh(mongo_context, str(legacy_id), token_seed="commit")
    before = _read(mongo_context, row_id)
    index_before = _indexes(mongo_context.refresh_tokens)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        report = migration.reconcile_refresh_tokens(
            refresh_tokens=mongo_context.refresh_tokens,
            users=mongo_context.users,
            mode=migration.MigrationMode.APPLY,
            session=session,
        )
        assert report.state == "APPLY_VERIFIED_PENDING_CALLER_COMMIT"
        session.commit_transaction()
    after = _read(mongo_context, row_id)
    assert after.get("tenant_id") == "tenant-commit"
    _assert_protected(before, after)
    assert _indexes(mongo_context.refresh_tokens) == index_before == (("_id_", (("_id", 1),)),)


def test_real_exact_row_isolation_and_no_migration_inserts_or_deletes(mongo_context: DisposableMongoContext) -> None:
    """Certify only eligible rows receive guarded updates."""

    legacy_id = ObjectId()
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-isolated", user_object_id=legacy_id)
    first = _insert_refresh(mongo_context, str(legacy_id), token_seed="first")
    second = _insert_refresh(mongo_context, str(legacy_id), token_seed="second")
    valid = _insert_refresh(mongo_context, str(legacy_id), tenant_id="tenant-isolated", token_seed="valid")
    ids_before = {row["_id"] for row in mongo_context.refresh_tokens.find({}, {"_id": 1})}
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        report = migration.reconcile_refresh_tokens(
            refresh_tokens=mongo_context.refresh_tokens,
            users=mongo_context.users,
            mode=migration.MigrationMode.APPLY,
            session=session,
        )
        assert report.applied_writes == 2
        session.commit_transaction()
    ids_after = {row["_id"] for row in mongo_context.refresh_tokens.find({}, {"_id": 1})}
    assert ids_after == ids_before
    assert mongo_context.refresh_tokens.count_documents({}) == 3
    assert _read(mongo_context, first).get("tenant_id") == "tenant-isolated"
    assert _read(mongo_context, second).get("tenant_id") == "tenant-isolated"
    assert _read(mongo_context, valid).get("tenant_id") == "tenant-isolated"


def test_real_second_apply_and_post_commit_dry_run_are_noops(mongo_context: DisposableMongoContext) -> None:
    """Certify replay is idempotent and a committed row is already valid."""

    legacy_id = ObjectId()
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-replay", user_object_id=legacy_id)
    row_id = _insert_refresh(mongo_context, str(legacy_id), token_seed="replay")
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        migration.reconcile_refresh_tokens(
            refresh_tokens=mongo_context.refresh_tokens,
            users=mongo_context.users,
            mode=migration.MigrationMode.APPLY,
            session=session,
        )
        session.commit_transaction()
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        replay = migration.reconcile_refresh_tokens(
            refresh_tokens=mongo_context.refresh_tokens,
            users=mongo_context.users,
            mode=migration.MigrationMode.APPLY,
            session=session,
        )
        assert replay.state == "APPLY_VERIFIED_PENDING_CALLER_COMMIT"
        assert replay.eligible_rows == replay.applied_writes == replay.verified_writes == 0
        assert replay.already_valid_rows == 1
        session.abort_transaction()
    dry_run = migration.reconcile_refresh_tokens(
        refresh_tokens=mongo_context.refresh_tokens,
        users=mongo_context.users,
    )
    assert dry_run.state == "DRY_RUN_READY"
    assert dry_run.already_valid_rows == 1 and dry_run.planned_writes == 0
    assert _read(mongo_context, row_id).get("tenant_id") == "tenant-replay"


def test_real_max_rows_bound_refuses_without_write(mongo_context: DisposableMongoContext) -> None:
    """Certify a bounded scope refusal leaves both rows tenantless."""

    legacy_id = ObjectId()
    _insert_user(mongo_context, user_id=None, tenant_id="tenant-bound", user_object_id=legacy_id)
    first = _insert_refresh(mongo_context, str(legacy_id), token_seed="bound-first")
    second = _insert_refresh(mongo_context, str(legacy_id), token_seed="bound-second")
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(migration.RefreshTokenTenantBackfillError) as bounded:
            migration.reconcile_refresh_tokens(
                refresh_tokens=mongo_context.refresh_tokens,
                users=mongo_context.users,
                mode=migration.MigrationMode.APPLY,
                session=session,
                max_rows=1,
            )
        assert bounded.value.code == "ROW_SCOPE_EXCEEDED"
        session.abort_transaction()
    assert _read(mongo_context, first).get("tenant_id") is None
    assert _read(mongo_context, second).get("tenant_id") is None


def test_real_secret_hygiene_and_no_canonical_resolver_or_transaction_ownership() -> None:
    """Certify source boundaries and aggregate report secret hygiene."""

    source_path = Path(inspect.getfile(migration))
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_calls = {
        "start_session", "start_transaction", "commit_transaction", "commit",
        "abort_transaction", "abort", "with_transaction", "delete_one",
        "delete_many", "insert_one", "replace_one", "create_index", "create_indexes",
        "drop_index",
    }
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert calls.isdisjoint(forbidden_calls)
    assert "tools.eos." + "kernel" not in source
    assert "bcrypt" not in source.lower()
    assert "passwordhash" not in source.lower()
    assert "credentialrevision" not in source.lower()
    report = migration.RefreshTokenTenantBackfillReport("DRY_RUN_READY", "DRY_RUN", 1, 1, 0, 0, 0, 0, 1, 0, 0)
    rendered = json.dumps(report.to_dict(), sort_keys=True)
    assert "synthetic-r10c2d" not in rendered
    assert report.mode == "DRY_RUN"


def test_real_cleanup_is_run_scoped_and_no_canonical_database_is_selected(
    mongo_client: MongoClient[Any],
) -> None:
    """Certify the database naming and explicit cleanup contract."""

    name = DATABASE_PREFIX + uuid.uuid4().hex
    assert name.startswith(DATABASE_PREFIX)
    assert len(name) <= 63
    assert name != "wilsy"
    database = mongo_client.get_database(name)
    database.get_collection("marker").insert_one({"marker": "synthetic"})
    mongo_client.drop_database(name)
    assert name not in mongo_client.list_database_names()


__all__ = ["URI_ENV", "DATABASE_PREFIX", "REPLICA_SET"]


# ARTIFACT: test_refresh_token_tenant_backfill_real_mongo.py
# VERSION: v1.0.0-R10C2D-REFRESH-TENANT-EXACT-BACKFILL-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable integration evidence only.
# TENANT POSTURE: synthetic exact identity and tenant mapping; no canonical data.
# FAIL-CLOSED POSTURE: loopback replica set, explicit caller transactions,
# protected-field assertions, and guaranteed run-scoped database cleanup.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
