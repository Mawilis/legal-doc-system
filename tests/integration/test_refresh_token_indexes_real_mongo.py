"""Disposable real-Mongo certificate for refresh-token index authority.

TITLE: R10C2I3 Refresh Token Index Authority Real-Mongo Certificate
VERSION: v1.0.0-R10C2I3-REFRESH-TOKEN-INDEX-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance integration certification
EPITOME: Proves the frozen two-index refresh-token topology against a real,
    writable MongoDB 7 replica set using only synthetic data and UUID-scoped
    disposable databases.  The certificate covers dry-run safety, additive
    APPLY, server metadata, uniqueness, precondition refusal, conflicts,
    ordering, idempotency, document immutability, and cleanup.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_refresh_token_indexes_real_mongo.py
COLLABORATION / OWNERSHIP: Directly exercises
    tools/eos/saas/auth/migrations/refresh_token_indexes.py.  The certificate
    owns disposable fixtures and never selects the canonical resolver/database.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2I3-REFRESH-TOKEN-INDEX-REAL-MONGO-CERT - Adds the isolated
    MongoDB 7 certificate for exact token uniqueness and tenant/user lookup.
    It proves additive-only DDL, no drops, no TTL, no document authority,
    real duplicate enforcement, and run-scoped cleanup.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Bearer strings are synthetic and held only in
    memory.  Reports, errors, logs, IDs, and assertion messages never contain
    bearer values or connection credentials.
TENANT BOUNDARY: Every admitted row has exact non-empty string tenant_id and
    user_id values; malformed or absent tenant identity blocks APPLY.
AUTHORITY BOUNDARY: Disposable index-topology evidence only.  No canonical
    resolver, AuthRegistry, refresh issuance, password, credential revision,
    JWT, MFA, recovery, session, role, Node, or financial authority.
TRANSACTION BOUNDARY: Mongo index DDL is not a document transaction; no
    transaction is started or inferred by the production index authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority;
    Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations

import ast
import inspect
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.monitoring import CommandListener, CommandStartedEvent
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.auth.migrations import refresh_token_indexes as authority


URI_ENV = "R10C2I3_REFRESH_TOKEN_INDEX_MONGO_URI"
DATABASE_PREFIX = "wilsy_r10c2i3_refresh_indexes_"
REPLICA_SET = "wilsyVendorCertRS"
COLLECTION = "refresh_tokens"
BASE_TIME = datetime(2026, 9, 22, 8, 0, tzinfo=timezone.utc)
EXPIRY = BASE_TIME + timedelta(days=1)
VERSION = "v1.0.0-R10C2I3-REFRESH-TOKEN-INDEX-REAL-MONGO-CERT"
_TOKEN_UNSET = object()


class CreateIndexListener(CommandListener):
    """Record only real createIndexes command ordering, never row contents."""

    def __init__(self) -> None:
        self.events: list[tuple[str, tuple[str, ...]]] = []

    def started(self, event: CommandStartedEvent) -> None:
        if event.command_name != "createIndexes":
            return
        raw_indexes = event.command.get("indexes", [])
        names = tuple(
            str(index.get("name"))
            for index in raw_indexes
            if isinstance(index, Mapping) and index.get("name") is not None
        )
        self.events.append((str(event.command.get("create")), names))

    def succeeded(self, event: Any) -> None:
        del event
        return

    def failed(self, event: Any) -> None:
        del event
        return

    def clear(self) -> None:
        self.events.clear()


class DisposableMongoContext:
    """Own one UUID-scoped synthetic database and its refresh collection."""

    def __init__(self, client: MongoClient[Any], database_name: str) -> None:
        self.client = client
        self.database_name = database_name
        self.database = client.get_database(
            database_name,
            read_concern=ReadConcern("majority"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        self.refresh_tokens = self.database.get_collection(COLLECTION)


def _runtime_uri() -> str:
    """Require an explicit loopback URI and reject canonical or hosted targets."""

    uri = os.environ.get(URI_ENV, "")
    if not uri:
        pytest.fail(f"{URI_ENV} is required")
    parsed = urlparse(uri)
    if parsed.scheme != "mongodb":
        pytest.fail("certificate requires a loopback mongodb URI")
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        pytest.fail("certificate requires a loopback Mongo endpoint")
    if parsed.path.strip("/") in {"wilsy", "wilsy/"}:
        pytest.fail("canonical Mongo database is not admissible")
    if "mongodb.net" in uri or "atlas" in uri.lower():
        pytest.fail("hosted Mongo endpoint is not admissible")
    return uri


def _open_runtime(listener: CreateIndexListener) -> MongoClient[Any]:
    """Open and certify the externally owned writable MongoDB 7 replica set."""

    client = MongoClient(
        _runtime_uri(),
        replicaSet=REPLICA_SET,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
        event_listeners=[listener],
    )
    try:
        hello = client.admin.command("hello")
        address = client.address
        version = str(client.server_info().get("version", ""))
        if hello.get("setName") != REPLICA_SET:
            raise RuntimeError("required replica set is unavailable")
        if hello.get("isWritablePrimary") is not True:
            raise RuntimeError("writable primary is required")
        if not address or address[0] not in {"127.0.0.1", "localhost", "::1"}:
            raise RuntimeError("non-loopback primary")
        if not version.startswith("7."):
            raise RuntimeError("MongoDB 7.x is required")
        return client
    except Exception:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_runtime() -> Iterator[tuple[MongoClient[Any], CreateIndexListener]]:
    """Provide one disposable client and close only that client."""

    listener = CreateIndexListener()
    client = _open_runtime(listener)
    try:
        yield client, listener
    finally:
        client.close()


@pytest.fixture()
def mongo_context(
    mongo_runtime: tuple[MongoClient[Any], CreateIndexListener],
) -> Iterator[DisposableMongoContext]:
    """Create and remove one UUID-scoped database for every test."""

    client, _listener = mongo_runtime
    database_name = DATABASE_PREFIX + uuid.uuid4().hex
    assert len(database_name) <= 63
    assert database_name.startswith(DATABASE_PREFIX)
    assert database_name != "wilsy"
    context = DisposableMongoContext(client, database_name)
    try:
        yield context
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()


def _token(seed: str) -> str:
    """Return a synthetic bearer value that is never rendered by assertions."""

    return f"synthetic-r10c2i3-{seed}-{uuid.uuid4().hex}"


def _row(
    *,
    token: Any = _TOKEN_UNSET,
    tenant: Any = "tenant-one",
    user: Any = "user-one",
    include_token: bool = True,
    include_tenant: bool = True,
    include_user: bool = True,
    row_id: str | None = None,
) -> dict[str, Any]:
    """Build one synthetic refresh row with explicitly controlled fields."""

    document: dict[str, Any] = {
        "_id": row_id or f"row-{uuid.uuid4().hex}",
        "expires": EXPIRY,
        "metadata": "synthetic-protected-metadata",
    }
    if include_token:
        document["token"] = _token("row") if token is _TOKEN_UNSET else token
    if include_tenant:
        document["tenant_id"] = tenant
    if include_user:
        document["user_id"] = user
    return document


def _seed(context: DisposableMongoContext, rows: list[dict[str, Any]]) -> None:
    """Insert only test-owned synthetic rows."""

    if rows:
        context.refresh_tokens.insert_many(rows)


def _snapshot(context: DisposableMongoContext) -> tuple[tuple[tuple[str, Any], ...], ...]:
    """Capture semantic row state without producing output containing bearers."""

    rows = list(context.refresh_tokens.find({}, {"_id": 1, "token": 1, "tenant_id": 1, "user_id": 1, "expires": 1, "metadata": 1}))
    return tuple(
        sorted(
            tuple(sorted(row.items(), key=lambda item: item[0]))
            for row in rows
        )
    )


def _index_map(context: DisposableMongoContext) -> dict[str, dict[str, Any]]:
    """Read server topology into safe metadata without row values."""

    result: dict[str, dict[str, Any]] = {}
    for raw in context.refresh_tokens.list_indexes():
        name = str(raw["name"])
        result[name] = {
            "key": tuple((str(key), int(value)) for key, value in raw["key"].items()),
            "unique": raw.get("unique") is True,
            "sparse": raw.get("sparse", False) is True,
            "partial": "partialFilterExpression" in raw,
            "ttl": "expireAfterSeconds" in raw,
        }
    return result


def _target_names() -> set[str]:
    return {authority.TOKEN_INDEX_NAME, authority.TENANT_USER_INDEX_NAME}


def _apply(context: DisposableMongoContext) -> authority.RefreshTokenIndexReport:
    """Invoke the frozen production authority in explicit APPLY mode."""

    return authority.reconcile_refresh_token_indexes(
        refresh_tokens=context.refresh_tokens,
        mode=authority.IndexMode.APPLY,
    )


def test_real_runtime_is_loopback_writable_mongodb_7(
    mongo_runtime: tuple[MongoClient[Any], CreateIndexListener],
) -> None:
    """Certify the disposable runtime anchor and no canonical database use."""

    client, _listener = mongo_runtime
    hello = client.admin.command("hello")
    assert hello["setName"] == REPLICA_SET
    assert hello["isWritablePrimary"] is True
    assert client.address is not None
    assert client.address[0] in {"127.0.0.1", "localhost", "::1"}
    assert str(client.server_info()["version"]).startswith("7.")


def test_real_dry_run_default_and_explicit_have_zero_ddl(
    mongo_context: DisposableMongoContext,
) -> None:
    """Certify both dry-run forms preserve rows and the _id_ topology only."""

    _seed(mongo_context, [_row(row_id="dry-one"), _row(row_id="dry-two", user="user-two")])
    before_rows = _snapshot(mongo_context)
    before_indexes = _index_map(mongo_context)
    omitted = authority.reconcile_refresh_token_indexes(refresh_tokens=mongo_context.refresh_tokens)
    explicit = authority.reconcile_refresh_token_indexes(
        refresh_tokens=mongo_context.refresh_tokens,
        mode=authority.IndexMode.DRY_RUN,
    )
    assert omitted.state == "DRY_RUN_READY"
    assert explicit.state == "DRY_RUN_READY"
    assert omitted.planned_creates == explicit.planned_creates == 2
    assert omitted.applied_creates == explicit.applied_creates == 0
    assert _index_map(mongo_context) == before_indexes
    assert set(before_indexes) == {"_id_"}
    assert _snapshot(mongo_context) == before_rows


def test_real_apply_creates_exact_server_indexes_and_preserves_documents(
    mongo_context: DisposableMongoContext,
    mongo_runtime: tuple[MongoClient[Any], CreateIndexListener],
) -> None:
    """Certify exact metadata, DDL ordering, no TTL, and row immutability."""

    _seed(mongo_context, [_row(row_id="apply-one"), _row(row_id="apply-two", user="user-two")])
    before_rows = _snapshot(mongo_context)
    _listener = mongo_runtime[1]
    _listener.clear()
    report = _apply(mongo_context)
    topology = _index_map(mongo_context)
    assert report.state == "APPLY_VERIFIED"
    assert report.applied_creates == report.verified_creates == 2
    assert set(topology) == {"_id_", *(_target_names())}
    token = topology[authority.TOKEN_INDEX_NAME]
    tenant_user = topology[authority.TENANT_USER_INDEX_NAME]
    assert token["key"] == authority.TOKEN_INDEX_KEYS
    assert token["unique"] is True
    assert token["sparse"] is False and token["partial"] is False and token["ttl"] is False
    assert tenant_user["key"] == authority.TENANT_USER_INDEX_KEYS
    assert tenant_user["unique"] is False
    assert tenant_user["sparse"] is False and tenant_user["partial"] is False and tenant_user["ttl"] is False
    assert [names for _collection, names in _listener.events] == [
        (authority.TOKEN_INDEX_NAME,),
        (authority.TENANT_USER_INDEX_NAME,),
    ]
    assert _snapshot(mongo_context) == before_rows


def test_real_token_unique_enforcement_rejects_duplicate_bearer(
    mongo_context: DisposableMongoContext,
) -> None:
    """Certify server-enforced uniqueness with a test-owned duplicate insert."""

    token = _token("unique")
    _seed(mongo_context, [_row(token=token, row_id="unique-one")])
    _apply(mongo_context)
    with pytest.raises(DuplicateKeyError):
        mongo_context.refresh_tokens.insert_one(
            _row(token=token, tenant="tenant-two", user="user-two", row_id="unique-two")
        )
    assert mongo_context.refresh_tokens.count_documents({}) == 1


def test_real_duplicate_precondition_blocks_before_any_target_ddl(
    mongo_context: DisposableMongoContext,
) -> None:
    """Certify duplicate existing bearers refuse APPLY before index creation."""

    duplicate = _token("duplicate")
    _seed(
        mongo_context,
        [_row(token=duplicate, row_id="duplicate-one"), _row(token=duplicate, row_id="duplicate-two", user="user-two")],
    )
    before_rows = _snapshot(mongo_context)
    report = _apply(mongo_context)
    assert report.state == "APPLY_BLOCKED"
    assert report.duplicate_token_groups == 1
    assert not (_target_names() & set(_index_map(mongo_context)))
    assert _snapshot(mongo_context) == before_rows


@pytest.mark.parametrize(
    "shape",
    ["missing", "null", "empty", "non-string"],
    ids=["missing", "null", "empty", "non-string"],
)
def test_real_invalid_token_shapes_block_apply(
    mongo_context: DisposableMongoContext,
    shape: str,
) -> None:
    """Certify each production-owned invalid token class refuses DDL."""

    values: dict[str, dict[str, Any]] = {
        "missing": _row(row_id="invalid-token" , include_token=False),
        "null": _row(row_id="invalid-token", token=None),
        "empty": _row(row_id="invalid-token", token=""),
        "non-string": _row(row_id="invalid-token", token=7),
    }
    _seed(mongo_context, [values[shape]])
    before_rows = _snapshot(mongo_context)
    report = _apply(mongo_context)
    assert report.state == "APPLY_BLOCKED"
    assert report.invalid_token_rows == 1
    assert not (_target_names() & set(_index_map(mongo_context)))
    assert _snapshot(mongo_context) == before_rows


@pytest.mark.parametrize(
    "shape",
    ["missing", "null", "empty", "non-string"],
    ids=["missing", "null", "empty", "non-string"],
)
def test_real_tenant_shape_barriers_block_apply(
    mongo_context: DisposableMongoContext,
    shape: str,
) -> None:
    """Certify absent and malformed tenant identity blocks both indexes."""

    values: dict[str, dict[str, Any]] = {
        "missing": _row(row_id="invalid-tenant", include_tenant=False),
        "null": _row(row_id="invalid-tenant", tenant=None),
        "empty": _row(row_id="invalid-tenant", tenant=""),
        "non-string": _row(row_id="invalid-tenant", tenant=7),
    }
    _seed(mongo_context, [values[shape]])
    report = _apply(mongo_context)
    assert report.state == "APPLY_BLOCKED"
    assert report.tenantless_rows == (1 if shape == "missing" else 0)
    assert report.invalid_tenant_rows == (0 if shape == "missing" else 1)
    assert not (_target_names() & set(_index_map(mongo_context)))


@pytest.mark.parametrize(
    "shape",
    ["missing", "null", "empty", "non-string"],
    ids=["missing", "null", "empty", "non-string"],
)
def test_real_user_identity_shape_barriers_block_apply(
    mongo_context: DisposableMongoContext,
    shape: str,
) -> None:
    """Certify absent and malformed user identity blocks tenant lookup DDL."""

    values: dict[str, dict[str, Any]] = {
        "missing": _row(row_id="invalid-user", include_user=False),
        "null": _row(row_id="invalid-user", user=None),
        "empty": _row(row_id="invalid-user", user=""),
        "non-string": _row(row_id="invalid-user", user=7),
    }
    _seed(mongo_context, [values[shape]])
    report = _apply(mongo_context)
    assert report.state == "APPLY_BLOCKED"
    assert report.invalid_user_id_rows == 1
    assert not (_target_names() & set(_index_map(mongo_context)))


def test_real_equivalent_alternate_names_are_reused(
    mongo_context: DisposableMongoContext,
) -> None:
    """Certify semantic topology satisfaction without redundant indexes."""

    _seed(mongo_context, [_row(row_id="alternate-name")])
    mongo_context.refresh_tokens.create_index(
        list(authority.TOKEN_INDEX_KEYS),
        unique=True,
        sparse=False,
        name="synthetic-token-equivalent",
    )
    mongo_context.refresh_tokens.create_index(
        list(authority.TENANT_USER_INDEX_KEYS),
        unique=False,
        sparse=False,
        name="synthetic-tenant-equivalent",
    )
    before = _index_map(mongo_context)
    report = _apply(mongo_context)
    after = _index_map(mongo_context)
    assert report.state == "APPLY_ALREADY_SATISFIED"
    assert report.applied_creates == 0
    assert after == before
    assert authority.TOKEN_INDEX_NAME not in after
    assert authority.TENANT_USER_INDEX_NAME not in after


def test_real_same_name_wrong_token_spec_blocks_without_drop_or_repair(
    mongo_context: DisposableMongoContext,
) -> None:
    """Certify a same-name token conflict leaves topology untouched."""

    _seed(mongo_context, [_row(row_id="wrong-token-spec")])
    mongo_context.refresh_tokens.create_index(
        [("token", 1)],
        unique=False,
        sparse=False,
        name=authority.TOKEN_INDEX_NAME,
    )
    before = _index_map(mongo_context)
    report = _apply(mongo_context)
    assert report.state == "APPLY_BLOCKED"
    assert report.token_index_state == "CONFLICTING_SPEC"
    assert _index_map(mongo_context) == before
    assert authority.TENANT_USER_INDEX_NAME not in before


def test_real_same_name_reversed_compound_order_blocks_without_drop_or_repair(
    mongo_context: DisposableMongoContext,
) -> None:
    """Certify tenant/user key order is not interchangeable."""

    _seed(mongo_context, [_row(row_id="wrong-compound-order")])
    mongo_context.refresh_tokens.create_index(
        [("user_id", 1), ("tenant_id", 1)],
        unique=False,
        sparse=False,
        name=authority.TENANT_USER_INDEX_NAME,
    )
    before = _index_map(mongo_context)
    report = _apply(mongo_context)
    assert report.state == "APPLY_BLOCKED"
    assert report.tenant_user_index_state == "CONFLICTING_NAME"
    assert _index_map(mongo_context) == before
    assert authority.TOKEN_INDEX_NAME not in before


def test_real_second_apply_is_exact_noop_and_has_no_new_create_commands(
    mongo_context: DisposableMongoContext,
    mongo_runtime: tuple[MongoClient[Any], CreateIndexListener],
) -> None:
    """Certify real topology idempotency and zero second APPLY DDL."""

    _seed(mongo_context, [_row(row_id="replay")])
    listener = mongo_runtime[1]
    first = _apply(mongo_context)
    first_topology = _index_map(mongo_context)
    listener.clear()
    second = _apply(mongo_context)
    assert first.state == "APPLY_VERIFIED"
    assert second.state == "APPLY_ALREADY_SATISFIED"
    assert second.planned_creates == second.applied_creates == 0
    assert _index_map(mongo_context) == first_topology
    assert listener.events == []


def test_real_reports_are_secret_free_and_source_boundaries_are_closed(
    mongo_context: DisposableMongoContext,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Certify report privacy and absence of canonical/authority imports."""

    duplicate = _token("privacy")
    _seed(mongo_context, [_row(token=duplicate, row_id="privacy-one"), _row(token=duplicate, row_id="privacy-two", user="user-two")])
    report = _apply(mongo_context)
    assert report.state == "APPLY_BLOCKED"
    assert duplicate not in repr(report)
    assert duplicate not in str(report)
    assert duplicate not in caplog.text
    source = inspect.getsource(authority)
    integration_source = Path(__file__).read_text(encoding="utf-8")
    assert "tools.eos." + "kernel" not in source
    assert "MongoClient" not in source
    assert "tools.eos." + "kernel" not in integration_source


def test_real_source_has_no_drop_ttl_or_document_write_authority() -> None:
    """Certify production source exposes only aggregate reads and index DDL."""

    source = inspect.getsource(authority)
    tree = ast.parse(source)
    calls = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert calls.isdisjoint(
        {
            "drop_index", "drop_indexes", "insert_one", "update_one", "replace_one",
            "delete_one", "delete_many", "find_one_and_update", "start_session",
            "start_transaction", "commit_transaction", "abort_transaction",
        }
    )
    assert "expireAfterSeconds" not in source
    assert "MongoClient" not in source


def test_real_certificate_source_self_audit() -> None:
    """Certify header, version agreement, seal, and marker-free source."""

    source = Path(__file__).read_text(encoding="utf-8")
    assert source.startswith('"""Disposable real-Mongo certificate')
    assert source.count(VERSION) >= 3
    assert "CERTIFICATION / UPDATE DATE" in source
    assert "R10C2I3_REFRESH_TOKEN_INDEX_MONGO_URI" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    forbidden = ("TO" + "DO", "FIX" + "ME", "place" + "holder", "s" + "tub")
    assert all(marker not in source for marker in forbidden)


def test_real_cleanup_contract_is_run_scoped(
    mongo_runtime: tuple[MongoClient[Any], CreateIndexListener],
) -> None:
    """Certify an explicitly disposable database can be removed cleanly."""

    client, _listener = mongo_runtime
    name = DATABASE_PREFIX + uuid.uuid4().hex
    assert name != "wilsy"
    client.get_database(name).get_collection("marker").insert_one({"marker": "synthetic"})
    client.drop_database(name)
    assert name not in client.list_database_names()


__all__ = ["COLLECTION", "DATABASE_PREFIX", "REPLICA_SET", "URI_ENV"]


# ARTIFACT: test_refresh_token_indexes_real_mongo.py
# VERSION: v1.0.0-R10C2I3-REFRESH-TOKEN-INDEX-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo index-topology evidence only.
# TENANT POSTURE: exact tenant_id/user_id preconditions and ordered lookup.
# FAIL-CLOSED POSTURE: loopback-only runtime, UUID database cleanup, row
# guards, additive DDL, exact metadata, duplicate enforcement, and no drops.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
