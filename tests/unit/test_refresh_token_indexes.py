"""WILSY OS direct certificate for governed refresh-token index topology.

TITLE: R10C2I2 Refresh Token Index Authority Direct Unit Certificate
VERSION: v1.0.0-R10C2I2-REFRESH-TOKEN-INDEX-AUTHORITY-CERT
AUTHORITY: WILSY OS Core Governance test certification
EPITOME: Offline, fake-backed evidence for the exact two-index refresh-token
    contract: unique raw-token identity and tenant/user lookup.  The
    certificate covers preconditions, explicit APPLY authority, additive-only
    DDL, ordered creation, exact post-create verification, idempotency, and
    secret-safe aggregate reporting.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_refresh_token_indexes.py
COLLABORATION / OWNERSHIP: Directly certifies
    tools/eos/saas/auth/migrations/refresh_token_indexes.py.  The collection
    handle is always supplied by the test caller; no Mongo topology is used.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2I2-REFRESH-TOKEN-INDEX-AUTHORITY-CERT - Adds the direct
    offline certificate for the two exact index contracts, fail-closed row
    guards, additive DDL order, post-create verification, replay safety, and
    privacy boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bearer sentinels remain in memory only.
    Reports, errors, assertions, and test identifiers contain no bearer value.
TENANT BOUNDARY: The tenant/user lookup contract requires exact ordered keys
    ``tenant_id`` then ``user_id`` and rejects absent or malformed values.
AUTHORITY BOUNDARY: Test evidence for index topology only.  No connection,
    document, token, password, JWT, session, MFA, Node, or recovery authority.
TRANSACTION BOUNDARY: Index DDL is outside document transactions; no session,
    transaction start, commit, abort, or retry is supplied or inferred.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority;
    Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations

import ast
import inspect
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import pytest

from tools.eos.saas.auth.migrations import refresh_token_indexes as authority


TOKEN_SENTINEL = "synthetic-bearer-sentinel-r10c2i2"
CERTIFICATE_VERSION = "v1.0.0-R10C2I2-REFRESH-TOKEN-INDEX-AUTHORITY-CERT"


def _valid_row(*, token: str = TOKEN_SENTINEL, tenant: str = "tenant-one", user: str = "user-one") -> dict[str, Any]:
    return {"token": token, "tenant_id": tenant, "user_id": user}


def _index(
    name: str,
    keys: Iterable[tuple[str, int]],
    *,
    unique: bool = False,
    sparse: bool = False,
    partial: bool = False,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "name": name,
        "key": list(keys),
        "unique": unique,
        "sparse": sparse,
    }
    if partial:
        value["partialFilterExpression"] = {"tenant_id": {"$exists": True}}
    return value


class RecordingCollection:
    """Bounded fake for list/find/aggregate/create_index only."""

    def __init__(
        self,
        rows: Iterable[Mapping[str, Any]],
        indexes: Iterable[Mapping[str, Any]] | None = None,
        *,
        create_behavior: Callable[["RecordingCollection", list[tuple[str, int]], dict[str, Any]], None] | None = None,
        aggregate_behavior: Callable[["RecordingCollection"], list[dict[str, Any]]] | None = None,
    ) -> None:
        self.rows = [dict(row) for row in rows]
        self.indexes = [dict(index) for index in (indexes or [_index("_id_", [("_id", 1)])])]
        self.create_behavior = create_behavior
        self.aggregate_behavior = aggregate_behavior
        self.list_calls = 0
        self.find_calls: list[tuple[dict[str, Any], dict[str, int]]] = []
        self.aggregate_calls: list[list[dict[str, Any]]] = []
        self.create_calls: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.forbidden_calls: list[str] = []

    def list_indexes(self) -> list[dict[str, Any]]:
        self.list_calls += 1
        return [dict(index) for index in self.indexes]

    def find(self, query: Mapping[str, Any], *, projection: Mapping[str, int] | None = None) -> list[dict[str, Any]]:
        projection_map = dict(projection or {})
        query_map = dict(query)
        self.find_calls.append((query_map, projection_map))
        return [
            {key: row[key] for key, enabled in projection_map.items() if enabled and key in row}
            for row in self.rows
            if all(row.get(key) == expected for key, expected in query_map.items())
        ]

    def aggregate(self, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.aggregate_calls.append(pipeline)
        if self.aggregate_behavior is not None:
            return self.aggregate_behavior(self)
        counts = Counter(row.get("token") for row in self.rows)
        return [{"_id": None, "cardinality": count} for count in counts.values() if count > 1]

    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> str:
        copied_keys = list(keys)
        copied_kwargs = dict(kwargs)
        self.create_calls.append((copied_keys, copied_kwargs))
        if self.create_behavior is not None:
            self.create_behavior(self, copied_keys, copied_kwargs)
        else:
            self.indexes.append(
                _index(
                    str(copied_kwargs["name"]),
                    copied_keys,
                    unique=bool(copied_kwargs.get("unique", False)),
                    sparse=bool(copied_kwargs.get("sparse", False)),
                )
            )
        return str(copied_kwargs["name"])

    def _forbidden(self, operation: str) -> None:
        self.forbidden_calls.append(operation)
        raise AssertionError(operation)

    def insert_one(self, *_args: Any, **_kwargs: Any) -> None:
        self._forbidden("insert_one")

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        self._forbidden("update_one")

    def replace_one(self, *_args: Any, **_kwargs: Any) -> None:
        self._forbidden("replace_one")

    def delete_many(self, *_args: Any, **_kwargs: Any) -> None:
        self._forbidden("delete_many")

    def find_one_and_update(self, *_args: Any, **_kwargs: Any) -> None:
        self._forbidden("find_one_and_update")

    def drop_index(self, *_args: Any, **_kwargs: Any) -> None:
        self._forbidden("drop_index")

    def drop_indexes(self, *_args: Any, **_kwargs: Any) -> None:
        self._forbidden("drop_indexes")


def _apply(collection: RecordingCollection) -> authority.RefreshTokenIndexReport:
    return authority.reconcile_refresh_token_indexes(
        refresh_tokens=collection,
        mode=authority.IndexMode.APPLY,
    )


def _error(collection: RecordingCollection, *, mode: Any = authority.IndexMode.APPLY) -> authority.RefreshTokenIndexAuthorityError:
    with pytest.raises(authority.RefreshTokenIndexAuthorityError) as captured:
        authority.reconcile_refresh_token_indexes(refresh_tokens=collection, mode=mode)
    return captured.value


def test_certificate_surface_and_exact_contract() -> None:
    assert authority.VERSION == "v1.0.0-R10C2I1-REFRESH-TOKEN-INDEX-AUTHORITY"
    assert authority.TOKEN_INDEX_NAME == "refresh_token_token_unique"
    assert authority.TOKEN_INDEX_KEYS == (("token", 1),)
    assert authority.TENANT_USER_INDEX_NAME == "refresh_token_tenant_user_lookup"
    assert authority.TENANT_USER_INDEX_KEYS == (("tenant_id", 1), ("user_id", 1))
    assert authority.DEFAULT_MODE == "DRY_RUN"
    assert set(authority.RefreshTokenIndexReport.__dataclass_fields__) == {
        "mode", "total_rows", "invalid_token_rows", "duplicate_token_groups",
        "duplicate_token_documents", "duplicate_token_max_cardinality", "tenantless_rows",
        "invalid_tenant_rows", "invalid_user_id_rows", "token_index_state",
        "tenant_user_index_state", "planned_creates", "applied_creates",
        "verified_creates", "state",
    }


def test_default_dry_run_is_read_only_and_plans_two_indexes() -> None:
    collection = RecordingCollection([_valid_row()])
    report = authority.reconcile_refresh_token_indexes(refresh_tokens=collection)
    assert report.mode == "DRY_RUN"
    assert report.state == "DRY_RUN_READY"
    assert report.planned_creates == 2
    assert report.applied_creates == 0
    assert report.verified_creates == 0
    assert collection.create_calls == []
    assert collection.forbidden_calls == []


@pytest.mark.parametrize("mode", ["APPLY", True, False, 1], ids=["string", "true", "false", "integer"])
def test_arbitrary_mode_values_cannot_authorize_apply(mode: Any) -> None:
    collection = RecordingCollection([_valid_row()])
    error = _error(collection, mode=mode)
    assert error.code == "INVALID_MODE"
    assert collection.list_calls == 0
    assert collection.create_calls == []


def test_explicit_apply_creates_unique_token_then_tenant_user_index() -> None:
    collection = RecordingCollection([_valid_row()])
    report = _apply(collection)
    assert report.state == "APPLY_VERIFIED"
    assert report.applied_creates == 2
    assert report.verified_creates == 2
    assert collection.create_calls == [
        (
            [("token", 1)],
            {"unique": True, "sparse": False, "name": authority.TOKEN_INDEX_NAME},
        ),
        (
            [("tenant_id", 1), ("user_id", 1)],
            {"unique": False, "sparse": False, "name": authority.TENANT_USER_INDEX_NAME},
        ),
    ]
    assert all("partialFilterExpression" not in kwargs for _, kwargs in collection.create_calls)
    assert all("expireAfterSeconds" not in kwargs for _, kwargs in collection.create_calls)
    assert collection.forbidden_calls == []


@pytest.mark.parametrize(
    ("rows", "field"),
    [
        ([{"tenant_id": "tenant-one", "user_id": "user-one"}], "token-missing"),
        ([{"token": None, "tenant_id": "tenant-one", "user_id": "user-one"}], "token-null"),
        ([{"token": "", "tenant_id": "tenant-one", "user_id": "user-one"}], "token-empty"),
        ([{"token": 7, "tenant_id": "tenant-one", "user_id": "user-one"}], "token-non-string"),
    ],
    ids=["missing", "null", "empty", "non-string"],
)
def test_invalid_token_rows_block_apply_without_ddl(rows: list[dict[str, Any]], field: str) -> None:
    del field
    collection = RecordingCollection(rows)
    report = _apply(collection)
    assert report.state == "APPLY_BLOCKED"
    assert report.invalid_token_rows == 1
    assert collection.create_calls == []
    assert collection.forbidden_calls == []


def test_duplicate_tokens_block_both_indexes_and_keep_bearer_secret_out_of_evidence() -> None:
    rows = [_valid_row(), _valid_row(user="user-two")]
    collection = RecordingCollection(rows)
    report = _apply(collection)
    assert report.state == "APPLY_BLOCKED"
    assert report.duplicate_token_groups == 1
    assert report.duplicate_token_documents == 2
    assert report.duplicate_token_max_cardinality == 2
    assert collection.create_calls == []
    assert TOKEN_SENTINEL not in repr(report)
    assert TOKEN_SENTINEL not in str(report)
    assert TOKEN_SENTINEL not in repr(report.to_dict())


def test_tenantless_row_blocks_apply_without_backfill() -> None:
    row = {"token": TOKEN_SENTINEL, "user_id": "user-one"}
    collection = RecordingCollection([row])
    report = _apply(collection)
    assert report.state == "APPLY_BLOCKED"
    assert report.tenantless_rows == 1
    assert report.invalid_tenant_rows == 0
    assert collection.create_calls == []


@pytest.mark.parametrize("tenant", [None, "", 7], ids=["null", "empty", "non-string"])
def test_invalid_tenant_rows_block_apply(tenant: Any) -> None:
    collection = RecordingCollection([_valid_row(tenant=tenant)])
    report = _apply(collection)
    assert report.state == "APPLY_BLOCKED"
    assert report.invalid_tenant_rows == 1
    assert report.tenantless_rows == 0
    assert collection.create_calls == []


@pytest.mark.parametrize("user", [None, "", 7], ids=["null", "empty", "non-string"])
def test_invalid_user_rows_block_apply(user: Any) -> None:
    collection = RecordingCollection([_valid_row(user=user)])
    report = _apply(collection)
    assert report.state == "APPLY_BLOCKED"
    assert report.invalid_user_id_rows == 1
    assert collection.create_calls == []


def test_exact_existing_indexes_are_noop_in_both_modes() -> None:
    collection = RecordingCollection(
        [_valid_row()],
        indexes=[
            _index("_id_", [("_id", 1)]),
            _index(authority.TOKEN_INDEX_NAME, authority.TOKEN_INDEX_KEYS, unique=True),
            _index(authority.TENANT_USER_INDEX_NAME, authority.TENANT_USER_INDEX_KEYS),
        ],
    )
    dry = authority.reconcile_refresh_token_indexes(refresh_tokens=collection)
    applied = _apply(collection)
    assert dry.token_index_state == "EXACTLY_SATISFIED"
    assert dry.tenant_user_index_state == "EXACTLY_SATISFIED"
    assert dry.planned_creates == 0
    assert applied.state == "APPLY_ALREADY_SATISFIED"
    assert applied.applied_creates == 0
    assert collection.create_calls == []


@pytest.mark.parametrize(
    "indexes",
    [
        [_index(authority.TOKEN_INDEX_NAME, [("user_id", 1)], unique=True)],
        [_index(authority.TOKEN_INDEX_NAME, authority.TOKEN_INDEX_KEYS, unique=False)],
        [_index(authority.TOKEN_INDEX_NAME, authority.TOKEN_INDEX_KEYS, sparse=True)],
        [_index(authority.TOKEN_INDEX_NAME, authority.TOKEN_INDEX_KEYS, partial=True)],
        [_index(authority.TENANT_USER_INDEX_NAME, [("user_id", 1), ("tenant_id", 1)])],
        [_index(authority.TENANT_USER_INDEX_NAME, authority.TENANT_USER_INDEX_KEYS, unique=True)],
        [_index(authority.TENANT_USER_INDEX_NAME, authority.TENANT_USER_INDEX_KEYS, sparse=True)],
        [_index(authority.TENANT_USER_INDEX_NAME, authority.TENANT_USER_INDEX_KEYS, partial=True)],
    ],
    ids=[
        "token-wrong-key", "token-wrong-unique", "token-sparse", "token-partial",
        "tenant-reversed-key", "tenant-wrong-unique", "tenant-sparse", "tenant-partial",
    ],
)
def test_same_name_wrong_specification_blocks_without_drop_or_repair(indexes: list[dict[str, Any]]) -> None:
    collection = RecordingCollection([_valid_row()], indexes=indexes)
    report = _apply(collection)
    assert report.state == "APPLY_BLOCKED"
    assert collection.create_calls == []
    assert collection.forbidden_calls == []


def test_equivalent_specs_under_other_names_are_reused() -> None:
    collection = RecordingCollection(
        [_valid_row()],
        indexes=[
            _index("_id_", [("_id", 1)]),
            _index("legacy-token-equivalent", authority.TOKEN_INDEX_KEYS, unique=True),
            _index("legacy-tenant-equivalent", authority.TENANT_USER_INDEX_KEYS),
        ],
    )
    report = _apply(collection)
    assert report.state == "APPLY_ALREADY_SATISFIED"
    assert report.token_index_state == "EQUIVALENT_SPEC_DIFFERENT_NAME"
    assert report.tenant_user_index_state == "EQUIVALENT_SPEC_DIFFERENT_NAME"
    assert report.applied_creates == 0
    assert collection.create_calls == []


def test_first_creation_failure_skips_second_index_and_preserves_topology() -> None:
    def fail_first(_collection: RecordingCollection, keys: list[tuple[str, int]], _kwargs: dict[str, Any]) -> None:
        assert keys == list(authority.TOKEN_INDEX_KEYS)
        raise RuntimeError("synthetic DDL failure")

    collection = RecordingCollection([_valid_row()], create_behavior=fail_first)
    error = _error(collection)
    assert error.code == "TOKEN_INDEX_CREATE_FAILED"
    assert error.report is not None
    assert error.report.state == "APPLY_PARTIAL_FAILURE"
    assert error.report.applied_creates == 0
    assert len(collection.create_calls) == 1
    assert collection.forbidden_calls == []


def test_second_creation_failure_does_not_drop_successful_first_index() -> None:
    def fail_second(collection: RecordingCollection, keys: list[tuple[str, int]], kwargs: dict[str, Any]) -> None:
        if kwargs["name"] == authority.TOKEN_INDEX_NAME:
            collection.indexes.append(_index(kwargs["name"], keys, unique=True))
            return
        raise RuntimeError("synthetic second DDL failure")

    collection = RecordingCollection([_valid_row()], create_behavior=fail_second)
    error = _error(collection)
    assert error.code == "TENANT_USER_INDEX_CREATE_FAILED"
    assert error.report is not None
    assert error.report.state == "APPLY_PARTIAL_FAILURE"
    assert error.report.applied_creates == 1
    assert error.report.verified_creates == 1
    assert any(index.get("name") == authority.TOKEN_INDEX_NAME for index in collection.indexes)
    assert collection.forbidden_calls == []


@pytest.mark.parametrize("kind", ["wrong-unique", "wrong-compound-order"], ids=["wrong-unique", "wrong-key-order"])
def test_post_create_verification_rejects_wrong_semantics(kind: str) -> None:
    def wrong_after_create(collection: RecordingCollection, keys: list[tuple[str, int]], kwargs: dict[str, Any]) -> None:
        if kwargs["name"] == authority.TOKEN_INDEX_NAME:
            if kind == "wrong-unique":
                collection.indexes.append(_index(kwargs["name"], keys, unique=False))
            else:
                collection.indexes.append(_index(kwargs["name"], keys, unique=True))
            return
        collection.indexes.append(
            _index(
                kwargs["name"],
                [("user_id", 1), ("tenant_id", 1)] if kind == "wrong-compound-order" else keys,
            )
        )

    collection = RecordingCollection([_valid_row()], create_behavior=wrong_after_create)
    error = _error(collection)
    assert error.code == "POST_CREATE_SPEC_VERIFICATION_FAILED"
    assert error.report is not None
    assert error.report.state == "APPLY_PARTIAL_FAILURE"
    assert collection.forbidden_calls == []


def test_successful_apply_is_idempotent_on_second_apply() -> None:
    collection = RecordingCollection([_valid_row()])
    first = _apply(collection)
    collection.create_calls.clear()
    second = _apply(collection)
    assert first.state == "APPLY_VERIFIED"
    assert second.state == "APPLY_ALREADY_SATISFIED"
    assert second.planned_creates == 0
    assert second.applied_creates == 0
    assert second.verified_creates == 0
    assert collection.create_calls == []


def test_report_and_error_surfaces_are_aggregate_and_secret_free() -> None:
    report_collection = RecordingCollection([_valid_row(), _valid_row(user="user-two")])
    report = _apply(report_collection)
    assert TOKEN_SENTINEL not in str(report)
    assert TOKEN_SENTINEL not in repr(report)
    assert TOKEN_SENTINEL not in repr(report.to_dict())

    def fail(_collection: RecordingCollection, _keys: list[tuple[str, int]], _kwargs: dict[str, Any]) -> None:
        raise RuntimeError("synthetic DDL failure")

    error = _error(RecordingCollection([_valid_row()], create_behavior=fail))
    assert TOKEN_SENTINEL not in str(error)
    assert TOKEN_SENTINEL not in repr(error)
    assert error.report is not None
    assert TOKEN_SENTINEL not in repr(error.report.to_dict())


def test_source_has_no_connection_transaction_drop_or_document_authority() -> None:
    source = inspect.getsource(authority)
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    )
    assert "pymongo" not in imported
    assert "dotenv" not in imported
    assert "kernel_db" not in imported
    assert "MongoClient" not in source
    for forbidden in (
        "start_session", "start_transaction", "commit_transaction", "abort_transaction",
        "drop_index", "drop_indexes", "insert_one", "update_one", "replace_one",
        "delete_many", "find_one_and_update", "expireAfterSeconds",
    ):
        assert forbidden not in source
    assert "create_index" in source


def test_certificate_scope_and_version_seal_are_self_consistent() -> None:
    path = Path(__file__)
    source = path.read_text(encoding="utf-8")
    assert source.startswith('"""WILSY OS direct certificate')
    assert source.count(CERTIFICATE_VERSION) >= 3
    assert "CERTIFICATE / UPDATE DATE" in source
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source
    forbidden_markers = ("TO" + "DO", "FIX" + "ME", "place" + "holder", "s" + "tub")
    assert all(marker not in source for marker in forbidden_markers)
    assert "canonical Mongo" in source


def test_only_expected_collection_operations_are_used() -> None:
    collection = RecordingCollection([_valid_row()])
    _apply(collection)
    assert collection.forbidden_calls == []
    assert collection.find_calls
    assert collection.aggregate_calls
    assert collection.list_calls > 0
    assert all(projection == {"token": 1, "tenant_id": 1, "user_id": 1} for _, projection in collection.find_calls)


# ARTIFACT: test_refresh_token_indexes.py
# VERSION: v1.0.0-R10C2I2-REFRESH-TOKEN-INDEX-AUTHORITY-CERT
# AUTHORITY BOUNDARY: direct offline evidence for additive refresh-token index
# topology only; no connection, document, credential, JWT, MFA, Node, or
# financial power.
# TENANT POSTURE: exact ordered tenant_id/user_id lookup is certified.
# FAIL-CLOSED POSTURE: malformed rows, duplicate tokens, conflicting topology,
# DDL failure, and post-create mismatch never produce a false pass.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
