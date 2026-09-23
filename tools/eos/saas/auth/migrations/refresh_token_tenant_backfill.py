"""WILSY OS exact refresh-token tenant backfill authority.

TITLE: WILSY OS Refresh Token Tenant Exact Backfill
VERSION: v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL
AUTHORITY: Wilsy OS Python EOS migration and reconciliation governance
PURPOSE: Reconcile only the genuinely missing ``tenant_id`` field on refresh
    rows whose existing identity maps to exactly one canonical user and one
    admissible tenant.
EPITOME: This is a bounded, dry-run-first transaction participant.  It proves
    an exact legacy refresh-row mapping before an explicitly selected APPLY
    mode may set one tenant field.  It never creates a client, chooses a
    database, owns a transaction, or changes any protected bearer material.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/migrations/refresh_token_tenant_backfill.py
COLLABORATION / OWNERSHIP: AuthRegistry refresh authority supplies the row
    semantics; a separately governed operator supplies collections and the
    caller-owned Mongo session.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL - Adds an aggregate-only,
    deterministic exact-identity reconciliation plan and an explicit APPLY
    participant with guarded one-row updates, readback, and post-write proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Reports and errors contain stable categories and
    counts only.  Refresh tokens, password hashes, JWTs, MFA material, user
    PII, and complete database rows are never returned, logged, or serialized.
TENANT BOUNDARY: A tenant is derived only from the exact durable user selected
    by AuthRegistry-compatible ``user_id`` then validated ObjectId fallback.
    Email, username, role, JWT, browser claims, and broad scans are forbidden.
AUTHORITY BOUNDARY: Missing-field refresh-row reconciliation only.  No token
    issuance or validation, credential revision, password, session, role,
    membership, MFA, Node, index, or deletion authority is present.
TRANSACTION BOUNDARY: APPLY requires an explicit MigrationMode.APPLY and an
    already active caller-owned session transaction.  This module never starts,
    commits, aborts, retries, or adjudicates a transaction.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority;
    Kennel EOS remains the exclusive financial execution authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, Mapping, NoReturn, Sequence, cast

from bson import ObjectId


VERSION = "v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL"
DEFAULT_MODE = "DRY_RUN"
INDEX_AUTHORITY = "ABSENT"
MAX_ROWS = 10_000
_REFRESH_PROJECTION = {
    "_id": 1,
    "user_id": 1,
    "token": 1,
    "expires": 1,
    "tenant_id": 1,
    "tenantId": 1,
}
_USER_PROJECTION = {"_id": 1, "user_id": 1, "tenantId": 1}
_RESERVED_TENANT_REFERENCES = frozenset(
    {
        "MASTER",
        "GLOBAL_ROOT",
        "WILSY",
        "WILSY_GLOBAL_ROOT",
        "WILSY_MASTER",
        "WILSY-SOVEREIGN-ROOT",
        "ROOT",
        "wilsy-sovereign-root",
    }
)


class MigrationMode(str, Enum):
    """Explicit execution authority for this migration participant.

    DRY_RUN owns read-only planning.  APPLY is the only value that permits a
    write, and it additionally requires an active transaction owned by the
    caller.  Arbitrary strings and truthy values are rejected.
    """

    DRY_RUN = "DRY_RUN"
    APPLY = "APPLY"


class RowClassification(str, Enum):
    """Bounded, non-sensitive outcome for one inspected refresh row."""

    ELIGIBLE_LEGACY_TENANTLESS = "ELIGIBLE_LEGACY_TENANTLESS"
    ALREADY_TENANT_BEARING_VALID = "ALREADY_TENANT_BEARING_VALID"
    PRESENT_TENANT_CORRUPT = "PRESENT_TENANT_CORRUPT"
    USER_ID_MISSING_OR_INVALID = "USER_ID_MISSING_OR_INVALID"
    CANONICAL_USER_AMBIGUOUS = "CANONICAL_USER_AMBIGUOUS"
    LEGACY_ID_AMBIGUOUS = "LEGACY_ID_AMBIGUOUS"
    AMBIGUOUS_IDENTITY = "AMBIGUOUS_IDENTITY"
    IDENTITY_PATH_AMBIGUOUS = "AMBIGUOUS_IDENTITY"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    USER_TENANT_INVALID = "USER_TENANT_INVALID"
    TENANT_MISMATCH = "TENANT_MISMATCH"
    ROW_STRUCTURALLY_CORRUPT = "ROW_STRUCTURALLY_CORRUPT"


class RefreshTokenTenantBackfillError(RuntimeError):
    """Stable fail-closed error without sensitive row or secret details."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class RefreshTokenTenantBackfillReport:
    """Aggregate migration evidence safe for operator output and audit storage.

    No row identity, token, user document, or write payload is retained.  An
    APPLY report means writes were verified inside the caller transaction; the
    caller still decides whether that transaction commits.
    """

    state: str
    mode: str
    total_examined: int
    eligible_rows: int
    already_valid_rows: int
    corrupt_rows: int
    ambiguous_rows: int
    unresolved_rows: int
    planned_writes: int
    applied_writes: int
    verified_writes: int

    def to_dict(self) -> dict[str, object]:
        """Return only bounded aggregate fields; never return source rows."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class _InspectedRow:
    row: Mapping[str, Any]
    classification: RowClassification
    derived_tenant_id: str | None


@dataclass(frozen=True, slots=True)
class _Scan:
    inspected: tuple[_InspectedRow, ...]
    total_examined: int
    eligible_rows: int
    already_valid_rows: int
    corrupt_rows: int
    ambiguous_rows: int
    unresolved_rows: int

    @property
    def blocked_rows(self) -> int:
        """Return rows that make an exact all-or-nothing apply unsafe."""

        return self.total_examined - self.eligible_rows - self.already_valid_rows


_CORRUPT = frozenset(
    {
        RowClassification.PRESENT_TENANT_CORRUPT,
        RowClassification.USER_TENANT_INVALID,
        RowClassification.TENANT_MISMATCH,
        RowClassification.ROW_STRUCTURALLY_CORRUPT,
    }
)
_AMBIGUOUS = frozenset(
    {
        RowClassification.CANONICAL_USER_AMBIGUOUS,
        RowClassification.LEGACY_ID_AMBIGUOUS,
        RowClassification.AMBIGUOUS_IDENTITY,
        RowClassification.IDENTITY_PATH_AMBIGUOUS,
    }
)
_UNRESOLVED = frozenset(
    {
        RowClassification.USER_ID_MISSING_OR_INVALID,
        RowClassification.USER_NOT_FOUND,
    }
)


def _fail(code: str) -> NoReturn:
    """Raise a bounded error code without embedding caller-controlled data."""

    raise RefreshTokenTenantBackfillError(code)


def _require_mode(mode: MigrationMode) -> MigrationMode:
    if not isinstance(mode, MigrationMode):
        _fail("INVALID_MODE")
    return mode


def _require_max_rows(max_rows: int) -> int:
    if isinstance(max_rows, bool) or not isinstance(max_rows, int):
        _fail("INVALID_MAX_ROWS")
    if max_rows < 1 or max_rows > MAX_ROWS:
        _fail("INVALID_MAX_ROWS")
    return max_rows


def _require_apply_transaction(session: Any) -> Any:
    if session is None or getattr(session, "in_transaction", False) is not True:
        _fail("APPLY_TRANSACTION_REQUIRED")
    return session


def _bounded_find(
    collection: Any,
    query: Mapping[str, Any],
    *,
    projection: Mapping[str, int],
    session: Any,
    limit: int,
    overflow_code: str,
) -> list[dict[str, Any]]:
    """Read a bounded projection while preserving the supplied session."""

    find = getattr(collection, "find", None)
    if not callable(find):
        _fail("COLLECTION_FIND_REQUIRED")
    try:
        kwargs: dict[str, Any] = {"projection": dict(projection)}
        if session is not None:
            kwargs["session"] = session
        cursor = cast(Iterable[Mapping[str, Any]], find(dict(query), **kwargs))
        rows: list[dict[str, Any]] = []
        for row in cursor:
            if not isinstance(row, Mapping):
                _fail("ROW_STRUCTURALLY_CORRUPT")
            rows.append(dict(row))
            if len(rows) > limit:
                if overflow_code == "ROW_SCOPE_EXCEEDED":
                    _fail(overflow_code)
                return rows
        return rows
    except RefreshTokenTenantBackfillError:
        raise
    except Exception as error:
        raise RefreshTokenTenantBackfillError("PERSISTENCE_READ_FAILED") from error


def _bounded_find_one(
    collection: Any,
    query: Mapping[str, Any],
    *,
    projection: Mapping[str, int],
    session: Any,
) -> dict[str, Any] | None:
    """Read one exact row with the caller session and no fallback query."""

    find_one = getattr(collection, "find_one", None)
    if not callable(find_one):
        _fail("COLLECTION_FIND_ONE_REQUIRED")
    try:
        kwargs: dict[str, Any] = {"projection": dict(projection)}
        if session is not None:
            kwargs["session"] = session
        row = find_one(dict(query), **kwargs)
        if row is None:
            return None
        if not isinstance(row, Mapping):
            _fail("ROW_STRUCTURALLY_CORRUPT")
        return dict(row)
    except RefreshTokenTenantBackfillError:
        raise
    except Exception as error:
        raise RefreshTokenTenantBackfillError("PERSISTENCE_READ_FAILED") from error


def _stable_order(rows: Sequence[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Return deterministic internal ordering without exposing identifiers."""

    return tuple(sorted(rows, key=lambda row: (type(row.get("_id")).__name__, repr(row.get("_id")))))


def _valid_tenant_id(value: Any) -> bool:
    """Apply the non-network canonical tenant syntax admitted by AuthRegistry."""

    return (
        isinstance(value, str)
        and bool(value)
        and value == value.strip()
        and value not in _RESERVED_TENANT_REFERENCES
    )


def _identity_documents(users: Any, user_id: str, *, session: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Resolve canonical then validated legacy identity with exact predicates."""

    canonical = _bounded_find(
        users,
        {"user_id": user_id},
        projection=_USER_PROJECTION,
        session=session,
        limit=2,
        overflow_code="CANONICAL_USER_AMBIGUOUS",
    )
    legacy: list[dict[str, Any]] = []
    if ObjectId.is_valid(user_id):
        try:
            object_id = ObjectId(user_id)
        except (TypeError, ValueError):
            object_id = None
        if object_id is not None:
            legacy = _bounded_find(
                users,
                {"_id": object_id},
                projection=_USER_PROJECTION,
                session=session,
                limit=2,
                overflow_code="LEGACY_ID_AMBIGUOUS",
            )
    return canonical, legacy


def _resolve_tenant(
    users: Any,
    user_id: str,
    *,
    session: Any,
) -> tuple[RowClassification | None, str | None]:
    """Return exact identity classification and its durable tenant, if any."""

    canonical, legacy = _identity_documents(users, user_id, session=session)
    if len(canonical) > 1:
        return RowClassification.CANONICAL_USER_AMBIGUOUS, None
    if len(legacy) > 1:
        return RowClassification.LEGACY_ID_AMBIGUOUS, None
    if canonical and legacy:
        canonical_id = canonical[0].get("_id")
        legacy_id = legacy[0].get("_id")
        if canonical_id != legacy_id:
            return RowClassification.AMBIGUOUS_IDENTITY, None
    if canonical:
        user = canonical[0]
    elif legacy:
        user = legacy[0]
    else:
        return RowClassification.USER_NOT_FOUND, None
    tenant_id = user.get("tenantId")
    if not _valid_tenant_id(tenant_id):
        return RowClassification.USER_TENANT_INVALID, None
    return None, tenant_id


def _inspect_row(row: Mapping[str, Any], users: Any, *, session: Any) -> _InspectedRow:
    """Classify one row without changing it or returning its sensitive values."""

    if row.get("_id") is None:
        return _InspectedRow(row, RowClassification.ROW_STRUCTURALLY_CORRUPT, None)
    token = row.get("token")
    expires = row.get("expires")
    user_id = row.get("user_id")
    if not isinstance(token, str) or not token or not isinstance(expires, datetime) or "tenantId" in row:
        return _InspectedRow(row, RowClassification.ROW_STRUCTURALLY_CORRUPT, None)
    if not isinstance(user_id, str) or not user_id or user_id != user_id.strip():
        return _InspectedRow(row, RowClassification.USER_ID_MISSING_OR_INVALID, None)
    if "tenant_id" in row:
        stored_tenant = row.get("tenant_id")
        if not _valid_tenant_id(stored_tenant):
            return _InspectedRow(row, RowClassification.PRESENT_TENANT_CORRUPT, None)
    identity_classification, derived_tenant = _resolve_tenant(users, user_id, session=session)
    if identity_classification is not None:
        return _InspectedRow(row, identity_classification, None)
    if "tenant_id" in row and row.get("tenant_id") != derived_tenant:
        return _InspectedRow(row, RowClassification.TENANT_MISMATCH, derived_tenant)
    if "tenant_id" in row:
        return _InspectedRow(row, RowClassification.ALREADY_TENANT_BEARING_VALID, derived_tenant)
    return _InspectedRow(row, RowClassification.ELIGIBLE_LEGACY_TENANTLESS, derived_tenant)


def _scan(*, refresh_tokens: Any, users: Any, session: Any, max_rows: int) -> _Scan:
    """Inspect all rows in one bounded, deterministic read-only pass."""

    source_rows = _bounded_find(
        refresh_tokens,
        {},
        projection=_REFRESH_PROJECTION,
        session=session,
        limit=max_rows,
        overflow_code="ROW_SCOPE_EXCEEDED",
    )
    inspected = tuple(
        _inspect_row(row, users, session=session) for row in _stable_order(source_rows)
    )
    counts = {classification: 0 for classification in RowClassification}
    for item in inspected:
        counts[item.classification] += 1
    return _Scan(
        inspected=inspected,
        total_examined=len(inspected),
        eligible_rows=counts[RowClassification.ELIGIBLE_LEGACY_TENANTLESS],
        already_valid_rows=counts[RowClassification.ALREADY_TENANT_BEARING_VALID],
        corrupt_rows=sum(counts[item] for item in _CORRUPT),
        ambiguous_rows=sum(counts[item] for item in _AMBIGUOUS),
        unresolved_rows=sum(counts[item] for item in _UNRESOLVED),
    )


def _report(*, state: str, mode: MigrationMode, scan: _Scan, planned: int = 0,
            applied: int = 0, verified: int = 0) -> RefreshTokenTenantBackfillReport:
    return RefreshTokenTenantBackfillReport(
        state=state,
        mode=mode.value,
        total_examined=scan.total_examined,
        eligible_rows=scan.eligible_rows,
        already_valid_rows=scan.already_valid_rows,
        corrupt_rows=scan.corrupt_rows,
        ambiguous_rows=scan.ambiguous_rows,
        unresolved_rows=scan.unresolved_rows,
        planned_writes=planned,
        applied_writes=applied,
        verified_writes=verified,
    )


def _apply_one(*, refresh_tokens: Any, users: Any, item: _InspectedRow, session: Any) -> None:
    """Guard and verify one exact tenant-field update inside caller transaction."""

    row_id = item.row.get("_id")
    current = _bounded_find_one(
        refresh_tokens,
        {"_id": row_id},
        projection=_REFRESH_PROJECTION,
        session=session,
    )
    if current is None:
        _fail("APPLY_SOURCE_ROW_CHANGED")
    current_item = _inspect_row(current, users, session=session)
    if current_item.classification is not RowClassification.ELIGIBLE_LEGACY_TENANTLESS:
        _fail("APPLY_SOURCE_ROW_CHANGED")
    tenant_id = current_item.derived_tenant_id
    user_id = current.get("user_id")
    if not isinstance(tenant_id, str) or not isinstance(user_id, str):
        _fail("APPLY_SOURCE_ROW_CHANGED")
    update_one = getattr(refresh_tokens, "update_one", None)
    if not callable(update_one):
        _fail("COLLECTION_UPDATE_REQUIRED")
    try:
        result = update_one(
            {"_id": row_id, "user_id": user_id, "tenant_id": {"$exists": False}},
            {"$set": {"tenant_id": tenant_id}},
            upsert=False,
            session=session,
        )
    except Exception as error:
        raise RefreshTokenTenantBackfillError("PERSISTENCE_WRITE_FAILED") from error
    if getattr(result, "matched_count", 0) != 1 or getattr(result, "modified_count", 0) != 1:
        _fail("UPDATE_NOT_EXACT")
    readback = _bounded_find_one(
        refresh_tokens,
        {"_id": row_id},
        projection=_REFRESH_PROJECTION,
        session=session,
    )
    if readback is None:
        _fail("READBACK_MISMATCH")
    for field in ("_id", "user_id", "token", "expires"):
        if readback.get(field) != current.get(field):
            _fail("READBACK_MISMATCH")
    if readback.get("tenant_id") != tenant_id:
        _fail("READBACK_MISMATCH")


def reconcile_refresh_tokens(
    *,
    refresh_tokens: Any,
    users: Any,
    mode: MigrationMode = MigrationMode.DRY_RUN,
    session: Any = None,
    max_rows: int = MAX_ROWS,
) -> RefreshTokenTenantBackfillReport:
    """Plan or apply exact refresh-token tenant backfill.

    Authority: fills only absent ``tenant_id`` on exact eligible rows.
    Tenant scope: exact durable ``user_id`` then ObjectId fallback, with one
        validated ``tenantId``; no alternate identity or broad query is used.
    Mutation semantics: DRY_RUN performs reads only.  APPLY updates one row at
        a time with an ``_id``/``user_id``/missing-field guard and verifies each
        protected field after the write.
    Transaction ownership: APPLY requires ``session.in_transaction is True``;
        the caller owns commit, abort, retry, and unknown-commit handling.
    Failure semantics: any blocked row yields a bounded blocked report before
        writes; races, persistence failures, and readback divergence raise a
        stable ``RefreshTokenTenantBackfillError``.
    Secret handling and financial boundary: no bearer material is returned or
        logged, and no financial execution or settlement authority exists.
    """

    selected_mode = _require_mode(mode)
    bounded_rows = _require_max_rows(max_rows)
    if selected_mode is MigrationMode.APPLY:
        _require_apply_transaction(session)
    scan = _scan(refresh_tokens=refresh_tokens, users=users, session=session, max_rows=bounded_rows)
    if scan.blocked_rows:
        return _report(
            state=f"{selected_mode.value}_BLOCKED",
            mode=selected_mode,
            scan=scan,
        )
    if selected_mode is MigrationMode.DRY_RUN:
        return _report(
            state="DRY_RUN_READY",
            mode=selected_mode,
            scan=scan,
            planned=scan.eligible_rows,
        )
    if session is None:
        _fail("APPLY_TRANSACTION_REQUIRED")
    applied = 0
    for item in scan.inspected:
        if item.classification is RowClassification.ELIGIBLE_LEGACY_TENANTLESS:
            _apply_one(refresh_tokens=refresh_tokens, users=users, item=item, session=session)
            applied += 1
    final_scan = _scan(
        refresh_tokens=refresh_tokens,
        users=users,
        session=session,
        max_rows=bounded_rows,
    )
    if final_scan.blocked_rows or final_scan.eligible_rows:
        _fail("POST_WRITE_RECONCILIATION_FAILED")
    if final_scan.already_valid_rows < applied:
        _fail("POST_WRITE_VERIFICATION_FAILED")
    return _report(
        state="APPLY_VERIFIED_PENDING_CALLER_COMMIT",
        mode=selected_mode,
        scan=scan,
        planned=scan.eligible_rows,
        applied=applied,
        verified=applied,
    )


__all__ = [
    "DEFAULT_MODE",
    "INDEX_AUTHORITY",
    "MAX_ROWS",
    "MigrationMode",
    "RefreshTokenTenantBackfillError",
    "RefreshTokenTenantBackfillReport",
    "RowClassification",
    "VERSION",
    "reconcile_refresh_tokens",
]


# ARTIFACT: refresh_token_tenant_backfill.py
# VERSION: v1.0.0-R10C2C-REFRESH-TENANT-EXACT-BACKFILL
# AUTHORITY BOUNDARY: exact missing refresh-row tenant reconciliation only;
# no token issuance, deletion, index, credential, JWT, MFA, or finance power.
# TENANT POSTURE: exact AuthRegistry-compatible identity and durable tenant;
# ambiguous, corrupt, or unresolved rows fail closed without deletion.
# FAIL-CLOSED POSTURE: dry-run default, explicit APPLY, active caller
# transaction, guarded one-row update, protected-field readback, and a final
# reconciliation are mandatory.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
