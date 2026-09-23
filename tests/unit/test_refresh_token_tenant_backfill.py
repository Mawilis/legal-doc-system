"""WILSY OS direct certificate for the exact refresh-token tenant backfill.

TITLE: R10C2C Refresh Token Tenant Exact Backfill Direct Unit Certificate
VERSION: v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL-CERT
AUTHORITY: Wilsy OS Core Governance test certification
EPITOME: Deterministically certifies the production migration authority with
    recording fakes only.  The certificate proves dry-run safety, exact
    identity resolution, global ambiguity refusal, caller-owned transactions,
    guarded writes, readback, idempotency, and secret hygiene.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_refresh_token_tenant_backfill.py
COLLABORATION / OWNERSHIP: Certifies
    tools/eos/saas/auth/migrations/refresh_token_tenant_backfill.py without
    changing production or contacting either Mongo topology.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL-CERT - Adds an offline,
    order-independent direct certificate for exact tenant backfill authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic bearer sentinels are compared only in
    memory.  No token, document, identity, credential, or session secret is
    printed or returned by a test assertion.
TENANT BOUNDARY: Fakes expose only exact ``user_id`` and validated ObjectId
    predicates; email, username, JWT, role, and broad user scans are absent.
AUTHORITY BOUNDARY: Test evidence only.  No password, credential revision,
    JWT, MFA, session, Node, index, recovery, or financial authority.
TRANSACTION BOUNDARY: A sentinel caller session proves identity propagation;
    the production migration remains the transaction participant.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority;
    Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations

import ast
import inspect
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import pytest
from bson import ObjectId

from tools.eos.saas.auth.migrations import refresh_token_tenant_backfill as migration


TOKEN_SENTINEL = "synthetic-refresh-bearer-never-print"
EXPIRY = datetime.utcnow() + timedelta(days=1)


class FakeUpdateResult:
    """Minimal PyMongo update result shape used by the certificate."""

    def __init__(self, matched_count: int, modified_count: int) -> None:
        self.matched_count = matched_count
        self.modified_count = modified_count


class FakeSession:
    """Caller-owned session sentinel with explicit transaction state."""

    def __init__(self, *, active: bool = True) -> None:
        self.in_transaction = active


class RecordingCollection:
    """Faithful bounded fake for the production find/update operation shapes."""

    def __init__(
        self,
        rows: Iterable[Mapping[str, Any]],
        *,
        update_result: FakeUpdateResult | None = None,
        exact_read_hook: Callable[["RecordingCollection", Mapping[str, Any]], None] | None = None,
        update_hook: Callable[["RecordingCollection", Mapping[str, Any]], None] | None = None,
        readback_mutation: str | None = None,
        readback_disappears: bool = False,
    ) -> None:
        self.rows = [dict(row) for row in rows]
        self.calls: list[tuple[str, dict[str, Any], Any]] = []
        self.write_calls: list[tuple[str, dict[str, Any], Any]] = []
        self.update_arguments: list[tuple[dict[str, Any], dict[str, Any], bool, Any]] = []
        self.update_result = update_result
        self.exact_read_hook = exact_read_hook
        self.update_hook = update_hook
        self.readback_mutation = readback_mutation
        self.readback_disappears = readback_disappears
        self._exact_hook_used = False

    @staticmethod
    def _matches(row: Mapping[str, Any], query: Mapping[str, Any]) -> bool:
        for key, expected in query.items():
            if isinstance(expected, Mapping) and "$exists" in expected:
                if (key in row) is not bool(expected["$exists"]):
                    return False
            elif row.get(key) != expected:
                return False
        return True

    @staticmethod
    def _project(row: Mapping[str, Any], projection: Mapping[str, int] | None) -> dict[str, Any]:
        if projection is None:
            return dict(row)
        return {key: row[key] for key, enabled in projection.items() if enabled and key in row}

    def find(
        self,
        query: Mapping[str, Any],
        projection: Mapping[str, int] | None = None,
        *,
        session: Any = None,
    ) -> list[dict[str, Any]]:
        query_copy = dict(query)
        self.calls.append(("find", query_copy, session))
        return [self._project(row, projection) for row in self.rows if self._matches(row, query_copy)]

    def find_one(
        self,
        query: Mapping[str, Any],
        projection: Mapping[str, int] | None = None,
        *,
        session: Any = None,
    ) -> dict[str, Any] | None:
        query_copy = dict(query)
        self.calls.append(("find_one", query_copy, session))
        if "_id" in query_copy and not self._exact_hook_used and self.exact_read_hook is not None:
            self._exact_hook_used = True
            self.exact_read_hook(self, query_copy)
        found = self.find(query_copy, projection, session=session)
        return found[0] if found else None

    def update_one(
        self,
        query: Mapping[str, Any],
        update: Mapping[str, Any],
        *,
        upsert: bool = False,
        session: Any = None,
    ) -> FakeUpdateResult:
        query_copy = dict(query)
        update_copy = dict(update)
        self.calls.append(("update_one", query_copy, session))
        self.write_calls.append(("update_one", query_copy, session))
        self.update_arguments.append((query_copy, update_copy, upsert, session))
        if self.update_hook is not None:
            self.update_hook(self, query_copy)
        result = self.update_result
        if result is not None:
            return result
        for row in self.rows:
            if self._matches(row, query_copy):
                row.update(update_copy.get("$set", {}))
                if self.readback_mutation is not None:
                    row[self.readback_mutation] = (
                        "changed-user" if self.readback_mutation == "user_id" else
                        datetime.utcnow() if self.readback_mutation == "expires" else
                        "changed-bearer" if self.readback_mutation == "token" else
                        "changed-metadata"
                    )
                if self.readback_disappears:
                    self.rows.remove(row)
                return FakeUpdateResult(1, 1)
        return FakeUpdateResult(0, 0)

    def forbidden_write(self, operation: str) -> None:
        """Record any operation outside the migration authority."""

        self.write_calls.append((operation, {}, None))
        raise AssertionError(operation)

    def delete_many(self, *args: Any, **kwargs: Any) -> None:
        self.forbidden_write("delete_many")

    def insert_one(self, *args: Any, **kwargs: Any) -> None:
        self.forbidden_write("insert_one")

    def replace_one(self, *args: Any, **kwargs: Any) -> None:
        self.forbidden_write("replace_one")

    def create_index(self, *args: Any, **kwargs: Any) -> None:
        self.forbidden_write("create_index")

    def create_indexes(self, *args: Any, **kwargs: Any) -> None:
        self.forbidden_write("create_indexes")

    def drop_index(self, *args: Any, **kwargs: Any) -> None:
        self.forbidden_write("drop_index")


def refresh_row(user_id: Any, *, row_id: Any | None = None, **extra: Any) -> dict[str, Any]:
    """Build one synthetic refresh row without exposing its bearer value."""

    row: dict[str, Any] = {
        "_id": row_id if row_id is not None else ObjectId(),
        "user_id": user_id,
        "token": TOKEN_SENTINEL,
        "expires": EXPIRY,
    }
    row.update(extra)
    return row


def legacy_pair(*, row_id: Any | None = None, **refresh_options: Any) -> tuple[RecordingCollection, RecordingCollection, str]:
    """Return one ObjectId-fallback user and one tenantless refresh row."""

    user_id = ObjectId("507f1f77bcf86cd799439011")
    users = RecordingCollection([{"_id": user_id, "tenantId": "tenant-alpha"}])
    refresh = RecordingCollection([refresh_row(str(user_id), row_id=row_id)], **refresh_options)
    return users, refresh, str(user_id)


def canonical_pair(*, user_id: str = "WILSYAUTH-synthetic", **refresh_options: Any) -> tuple[RecordingCollection, RecordingCollection]:
    users = RecordingCollection([{"_id": ObjectId("507f1f77bcf86cd799439012"), "user_id": user_id, "tenantId": "tenant-beta"}])
    refresh = RecordingCollection([refresh_row(user_id)], **refresh_options)
    return users, refresh


def assert_error(call: Callable[[], Any], code: str) -> migration.RefreshTokenTenantBackfillError:
    """Assert one stable migration error without printing its content."""

    with pytest.raises(migration.RefreshTokenTenantBackfillError) as captured:
        call()
    assert captured.value.code == code
    return captured.value


def test_public_api_types_and_defaults_are_live() -> None:
    signature = inspect.signature(migration.reconcile_refresh_tokens)
    assert signature.parameters["mode"].default is migration.MigrationMode.DRY_RUN
    assert signature.parameters["max_rows"].default == 10_000
    assert migration.DEFAULT_MODE == "DRY_RUN"
    assert migration.MAX_ROWS == 10_000
    assert issubclass(migration.MigrationMode, str)
    assert issubclass(migration.RefreshTokenTenantBackfillError, RuntimeError)
    assert migration.RowClassification.ELIGIBLE_LEGACY_TENANTLESS.value == "ELIGIBLE_LEGACY_TENANTLESS"


def test_omitted_mode_is_dry_run_and_performs_zero_writes() -> None:
    users, refresh, _ = legacy_pair()
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.mode == migration.MigrationMode.DRY_RUN.value
    assert report.state == "DRY_RUN_READY"
    assert report.eligible_rows == report.planned_writes == 1
    assert report.applied_writes == report.verified_writes == 0
    assert refresh.write_calls == []


def test_explicit_dry_run_and_runtime_mode_boundary() -> None:
    users, refresh, _ = legacy_pair()
    explicit = migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.DRY_RUN
    )
    assert explicit.state == "DRY_RUN_READY"
    assert refresh.write_calls == []
    for invalid in ("APPLY", True, 1, None):
        assert_error(
            lambda invalid=invalid: migration.reconcile_refresh_tokens(
                refresh_tokens=refresh, users=users, mode=invalid  # type: ignore[arg-type]
            ),
            "INVALID_MODE",
        )
    assert refresh.write_calls == []


def test_apply_requires_session_and_active_transaction_before_write() -> None:
    users, refresh, _ = legacy_pair()
    assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY
        ),
        "APPLY_TRANSACTION_REQUIRED",
    )
    assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh,
            users=users,
            mode=migration.MigrationMode.APPLY,
            session=FakeSession(active=False),
        ),
        "APPLY_TRANSACTION_REQUIRED",
    )
    assert refresh.write_calls == []


def test_legacy_objectid_fallback_is_eligible_without_dry_run_write() -> None:
    users, refresh, object_id_text = legacy_pair()
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.eligible_rows == 1
    assert refresh.rows[0]["user_id"] == object_id_text
    assert refresh.rows[0].get("tenant_id") is None
    assert refresh.write_calls == []


def test_canonical_user_id_path_is_eligible() -> None:
    users, refresh = canonical_pair()
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.eligible_rows == 1
    assert report.unresolved_rows == report.ambiguous_rows == report.corrupt_rows == 0


def test_multiple_canonical_matches_block_apply_globally() -> None:
    users = RecordingCollection([
        {"_id": ObjectId("507f1f77bcf86cd799439013"), "user_id": "duplicate", "tenantId": "tenant-a"},
        {"_id": ObjectId("507f1f77bcf86cd799439014"), "user_id": "duplicate", "tenantId": "tenant-b"},
    ])
    refresh = RecordingCollection([refresh_row("duplicate")])
    report = migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
    )
    assert report.state == "APPLY_BLOCKED"
    assert report.ambiguous_rows == 1
    assert refresh.write_calls == []


def test_canonical_and_legacy_identity_collision_is_not_hidden_by_precedence() -> None:
    object_id = ObjectId("507f1f77bcf86cd799439015")
    users = RecordingCollection([
        {"_id": ObjectId("507f1f77bcf86cd799439016"), "user_id": str(object_id), "tenantId": "tenant-canonical"},
        {"_id": object_id, "tenantId": "tenant-legacy"},
    ])
    refresh = RecordingCollection([refresh_row(str(object_id))])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.ambiguous_rows == 1
    assert report.eligible_rows == 0
    blocked = migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
    )
    assert blocked.state == "APPLY_BLOCKED"
    assert refresh.write_calls == []


def test_user_absence_is_unresolved_and_blocks_apply() -> None:
    users = RecordingCollection([])
    refresh = RecordingCollection([refresh_row("absent-user")])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.unresolved_rows == 1
    assert report.eligible_rows == 0
    blocked = migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
    )
    assert blocked.state == "APPLY_BLOCKED"
    assert refresh.write_calls == []


@pytest.mark.parametrize("bad_user_id", [None, "", 7])
def test_invalid_refresh_user_id_is_rejected_without_guessing(bad_user_id: Any) -> None:
    users = RecordingCollection([])
    refresh = RecordingCollection([refresh_row(bad_user_id)])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.unresolved_rows == 1
    assert report.eligible_rows == 0
    assert refresh.write_calls == []


@pytest.mark.parametrize("tenant_value", [None, "", 7])
def test_invalid_user_tenant_is_rejected(tenant_value: Any) -> None:
    users = RecordingCollection([{"_id": ObjectId("507f1f77bcf86cd799439017"), "user_id": "tenant-invalid", "tenantId": tenant_value}])
    refresh = RecordingCollection([refresh_row("tenant-invalid")])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.corrupt_rows == 1
    assert report.eligible_rows == 0
    assert refresh.write_calls == []


def test_email_and_username_are_never_identity_fallbacks() -> None:
    users = RecordingCollection([{"_id": ObjectId("507f1f77bcf86cd799439018"), "email": "synthetic@example.invalid", "username": "synthetic", "tenantId": "tenant-a"}])
    refresh = RecordingCollection([refresh_row("synthetic@example.invalid")])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.unresolved_rows == 1
    queries = [query for _, query, _ in users.calls]
    assert all(set(query).issubset({"user_id", "_id"}) for query in queries)
    assert all("email" not in query and "username" not in query for query in queries)


def test_already_valid_row_is_idempotent_noop() -> None:
    users = RecordingCollection([{"_id": ObjectId("507f1f77bcf86cd799439019"), "user_id": "valid", "tenantId": "tenant-a"}])
    refresh = RecordingCollection([refresh_row("valid", tenant_id="tenant-a")])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.already_valid_rows == 1
    assert report.planned_writes == 0
    assert refresh.write_calls == []


@pytest.mark.parametrize("tenant_value", [None, "", 7])
def test_present_corrupt_tenant_is_not_repaired(tenant_value: Any) -> None:
    users = RecordingCollection([{"_id": ObjectId("507f1f77bcf86cd799439020"), "user_id": "corrupt", "tenantId": "tenant-a"}])
    refresh = RecordingCollection([refresh_row("corrupt", tenant_id=tenant_value)])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.corrupt_rows == 1
    assert report.planned_writes == 0
    assert refresh.write_calls == []


def test_present_wrong_tenant_is_not_repaired() -> None:
    users = RecordingCollection([{"_id": ObjectId("507f1f77bcf86cd799439021"), "user_id": "wrong", "tenantId": "tenant-a"}])
    refresh = RecordingCollection([refresh_row("wrong", tenant_id="tenant-b")])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.corrupt_rows == 1
    assert report.planned_writes == 0


@pytest.mark.parametrize(
    "mutated_row",
    [
        {"token": None},
        {"expires": "not-a-date"},
        {"_id": None},
    ],
)
def test_structurally_unsafe_refresh_rows_are_not_migrated(mutated_row: dict[str, Any]) -> None:
    source = refresh_row("structural")
    source.update(mutated_row)
    users = RecordingCollection([{"_id": ObjectId("507f1f77bcf86cd799439022"), "user_id": "structural", "tenantId": "tenant-a"}])
    refresh = RecordingCollection([source])
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    assert report.corrupt_rows == 1
    assert refresh.write_calls == []


def test_global_unsafe_plan_performs_zero_writes() -> None:
    eligible_users, eligible_refresh, _ = legacy_pair(row_id=ObjectId("507f1f77bcf86cd799439023"))
    unsafe_refresh = refresh_row("missing-user", row_id=ObjectId("507f1f77bcf86cd799439024"))
    eligible_refresh.rows.append(unsafe_refresh)
    report = migration.reconcile_refresh_tokens(
        refresh_tokens=eligible_refresh,
        users=eligible_users,
        mode=migration.MigrationMode.APPLY,
        session=FakeSession(),
    )
    assert report.state == "APPLY_BLOCKED"
    assert report.eligible_rows == 1
    assert report.unresolved_rows == 1
    assert eligible_refresh.write_calls == []


def test_max_rows_is_bounded_and_never_reports_truncated_safety() -> None:
    users, refresh, _ = legacy_pair()
    refresh.rows.append(refresh_row(refresh.rows[0]["user_id"], row_id=ObjectId("507f1f77bcf86cd799439025")))
    assert migration.MAX_ROWS == 10_000
    assert_error(
        lambda: migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users, max_rows=0),
        "INVALID_MAX_ROWS",
    )
    exact_bound = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users, max_rows=2)
    assert exact_bound.total_examined == 2
    assert_error(
        lambda: migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users, max_rows=1),
        "ROW_SCOPE_EXCEEDED",
    )
    assert refresh.write_calls == []


def test_apply_is_deterministically_ordered_by_internal_id() -> None:
    user_id = ObjectId("507f1f77bcf86cd799439026")
    users = RecordingCollection([{"_id": user_id, "tenantId": "tenant-a"}])
    high = refresh_row(str(user_id), row_id=ObjectId("507f1f77bcf86cd799439029"))
    low = refresh_row(str(user_id), row_id=ObjectId("507f1f77bcf86cd799439028"))
    refresh = RecordingCollection([high, low])
    migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
    )
    assert [call[0]["_id"] for call in refresh.update_arguments] == [low["_id"], high["_id"]]


def test_apply_rederives_eligibility_and_rejects_stale_state() -> None:
    users, refresh, _ = legacy_pair()

    def add_tenant(collection: RecordingCollection, query: Mapping[str, Any]) -> None:
        for row in collection.rows:
            if row.get("_id") == query.get("_id"):
                row["tenant_id"] = "tenant-alpha"

    refresh.exact_read_hook = add_tenant
    assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
        ),
        "APPLY_SOURCE_ROW_CHANGED",
    )
    assert refresh.write_calls == []


def test_successful_apply_guard_readback_and_protected_fields() -> None:
    users, refresh, _ = legacy_pair()
    original = dict(refresh.rows[0])
    session = FakeSession()
    report = migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=session
    )
    assert report.state == "APPLY_VERIFIED_PENDING_CALLER_COMMIT"
    assert report.planned_writes == report.applied_writes == report.verified_writes == 1
    query, update, upsert, update_session = refresh.update_arguments[0]
    assert query["_id"] == original["_id"]
    assert query["user_id"] == original["user_id"]
    assert query["tenant_id"] == {"$exists": False}
    assert update == {"$set": {"tenant_id": "tenant-alpha"}}
    assert upsert is False
    assert update_session is session
    for field in ("_id", "user_id", "token", "expires"):
        assert refresh.rows[0][field] == original[field]
    assert refresh.rows[0]["tenant_id"] == "tenant-alpha"


@pytest.mark.parametrize("result", [FakeUpdateResult(0, 0), FakeUpdateResult(1, 0), FakeUpdateResult(2, 2)])
def test_matched_or_modified_counts_must_be_exactly_one(result: FakeUpdateResult) -> None:
    users, refresh, _ = legacy_pair(update_result=result)
    error = assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
        ),
        "UPDATE_NOT_EXACT",
    )
    assert TOKEN_SENTINEL not in str(error)


@pytest.mark.parametrize("field", ["token", "user_id", "expires"])
def test_protected_field_races_fail_readback(field: str) -> None:
    users, refresh, _ = legacy_pair(readback_mutation=field)
    error = assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
        ),
        "READBACK_MISMATCH",
    )
    assert TOKEN_SENTINEL not in str(error)
    assert TOKEN_SENTINEL not in repr(error)


def test_row_disappearance_fails_without_replacement() -> None:
    def disappear(collection: RecordingCollection, query: Mapping[str, Any]) -> None:
        collection.rows.clear()

    users, refresh, _ = legacy_pair(exact_read_hook=disappear)
    assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
        ),
        "APPLY_SOURCE_ROW_CHANGED",
    )
    assert refresh.write_calls == []


def test_readback_disappearance_fails_closed() -> None:
    users, refresh, _ = legacy_pair(readback_disappears=True)
    assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
        ),
        "READBACK_MISMATCH",
    )


def test_idempotent_second_apply_has_zero_writes() -> None:
    users, refresh, _ = legacy_pair()
    session = FakeSession()
    first = migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=session
    )
    writes_after_first = len(refresh.write_calls)
    second = migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=session
    )
    assert first.state == "APPLY_VERIFIED_PENDING_CALLER_COMMIT"
    assert second.already_valid_rows == 1
    assert second.eligible_rows == 0
    assert second.applied_writes == second.verified_writes == 0
    assert len(refresh.write_calls) == writes_after_first == 1


def test_final_reconciliation_blocks_unexpected_new_unsafe_row() -> None:
    users, refresh, _ = legacy_pair()

    def append_unsafe(collection: RecordingCollection, query: Mapping[str, Any]) -> None:
        collection.rows.append(refresh_row("unexpected-user", row_id=ObjectId("507f1f77bcf86cd799439030")))

    refresh.update_hook = append_unsafe
    assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=FakeSession()
        ),
        "POST_WRITE_RECONCILIATION_FAILED",
    )


def test_session_identity_reaches_reads_writes_readback_and_final_reconciliation() -> None:
    users, refresh, _ = legacy_pair()
    session = FakeSession()
    migration.reconcile_refresh_tokens(
        refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY, session=session
    )
    assert users.calls
    assert refresh.calls
    assert all(call[2] is session for call in users.calls + refresh.calls)
    assert all(call[3] is session for call in refresh.update_arguments)


def test_report_and_errors_are_aggregate_and_secret_free() -> None:
    users, refresh, _ = legacy_pair()
    report = migration.reconcile_refresh_tokens(refresh_tokens=refresh, users=users)
    serialized = json.dumps(report.to_dict(), sort_keys=True)
    assert TOKEN_SENTINEL not in serialized
    assert set(report.to_dict()) == {
        "state", "mode", "total_examined", "eligible_rows", "already_valid_rows",
        "corrupt_rows", "ambiguous_rows", "unresolved_rows", "planned_writes",
        "applied_writes", "verified_writes",
    }
    error = assert_error(
        lambda: migration.reconcile_refresh_tokens(
            refresh_tokens=refresh, users=users, mode=migration.MigrationMode.APPLY
        ),
        "APPLY_TRANSACTION_REQUIRED",
    )
    assert TOKEN_SENTINEL not in str(error)
    assert TOKEN_SENTINEL not in repr(error)


def test_forbidden_operations_and_authority_imports_are_absent() -> None:
    source_path = Path(migration.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_calls = {
        "start_session", "start_transaction", "commit_transaction", "commit",
        "abort_transaction", "abort", "with_transaction", "delete_one", "delete_many",
        "insert_one", "replace_one", "create_index", "create_indexes", "drop_index",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in forbidden_calls
    imported_modules = {
        node.module or ""
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
    }
    forbidden_modules = {"boto3", "bcrypt", "jwt", "requests", "httpx", "pymongo", "tools.eos.kernel"}
    assert not imported_modules.intersection(forbidden_modules)
    assert "tools.eos.kernel" not in source
    assert "passwordHash" not in source
    assert "credentialRevision" not in source


def test_source_self_audit_and_public_certificate_scope() -> None:
    source_path = Path(migration.__file__)
    source = source_path.read_text(encoding="utf-8")
    assert source.startswith('"""WILSY OS exact refresh-token tenant backfill authority.')
    assert migration.VERSION == "v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL"
    assert source.count("VERSION: "+migration.VERSION) >= 2
    assert "END OF WILSY OS SOVEREIGN ARTIFACT" in source


# ARTIFACT: test_refresh_token_tenant_backfill.py
# VERSION: v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL-CERT
# AUTHORITY BOUNDARY: deterministic direct certificate only; no live migration.
# TENANT POSTURE: exact identity and tenant backfill invariants are exercised;
# ambiguous or corrupt rows remain untouched.
# FAIL-CLOSED POSTURE: no live database, network, index, delete, or production
# mutation is permitted by this certificate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
