"""Governed additive refresh-token index authority.

TITLE: WILSY OS Refresh Token Index Authority
VERSION: v1.0.0-R10C2I1-REFRESH-TOKEN-INDEX-AUTHORITY
AUTHORITY: WILSY OS Python EOS schema and topology governance
PURPOSE: Reconcile the two exact indexes required by tenant-scoped refresh
    authority without changing documents or owning a database connection.
EPITOME: A dry-run-first, fail-closed index participant.  APPLY is explicit,
    validates all refresh rows, creates the unique token index first, creates
    the tenant/user lookup index second, and verifies each exact topology.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/migrations/refresh_token_indexes.py
COLLABORATION / OWNERSHIP: The future operator supplies the explicit
    ``refresh_tokens`` collection and owns scheduling, connection, and DDL
    observation.  AuthRegistry remains the refresh business authority.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10C2I1-REFRESH-TOKEN-INDEX-AUTHORITY - Adds exact dry-run and
    explicit additive APPLY reconciliation for named raw-token uniqueness and
    tenant/user lookup.  No index drops, TTL, document writes, or connection
    lifecycle are included.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Token values are inspected only transiently for
    aggregate duplicate detection and never returned, logged, or embedded in
    errors.  Invalid or duplicate bearer material blocks unique-index APPLY.
TENANT BOUNDARY: Tenant/user topology is admitted only when every current row
    has a non-empty string ``tenant_id`` and ``user_id``.
AUTHORITY BOUNDARY: Additive refresh_tokens index reconciliation only.  No
    connection, token, password, JWT, session, MFA, Node, or data authority.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority;
    Kennel EOS remains the exclusive financial execution authority.
TRANSACTION BOUNDARY: Index DDL is not a document transaction.  This module
    never starts, commits, aborts, retries, or requires a ClientSession.
FAIL-CLOSED DECLARATION: Unknown topology, malformed rows, duplicate tokens,
    conflicting names/specifications, and every DDL or post-create mismatch
    stop without destructive compensation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Mapping, NoReturn, Sequence, cast


VERSION = "v1.0.0-R10C2I1-REFRESH-TOKEN-INDEX-AUTHORITY"
DEFAULT_MODE = "DRY_RUN"
TOKEN_INDEX_NAME = "refresh_token_token_unique"
TENANT_USER_INDEX_NAME = "refresh_token_tenant_user_lookup"
TOKEN_INDEX_KEYS = (("token", 1),)
TENANT_USER_INDEX_KEYS = (("tenant_id", 1), ("user_id", 1))


class IndexMode(str, Enum):
    """Explicit topology execution authority.

    ``DRY_RUN`` performs reads and aggregate classification only.  ``APPLY``
    is the sole value permitted to invoke ``create_index`` and is never
    inferred from a string, environment variable, or truthy object.
    """

    DRY_RUN = "DRY_RUN"
    APPLY = "APPLY"


class RefreshTokenIndexAuthorityError(RuntimeError):
    """Stable, secret-free refusal raised by the index authority.

    The code and optional bounded report describe topology or aggregate state;
    no token, user document, credential, URI, or connection secret is stored.
    """

    def __init__(self, code: str, *, report: "RefreshTokenIndexReport | None" = None) -> None:
        self.code = code
        self.report = report
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class RefreshTokenIndexReport:
    """Aggregate, immutable topology evidence safe for operator handling.

    Authority: refresh-token index reconciliation only.  Mutation semantics
    are limited to additive index DDL in explicit APPLY mode; document rows
    are never changed.  Tenant scope is represented by the required
    ``tenant_id``/``user_id`` precondition.  No transaction or financial
    authority is owned.
    """

    mode: str
    total_rows: int
    invalid_token_rows: int
    duplicate_token_groups: int
    duplicate_token_documents: int
    duplicate_token_max_cardinality: int
    tenantless_rows: int
    invalid_tenant_rows: int
    invalid_user_id_rows: int
    token_index_state: str
    tenant_user_index_state: str
    planned_creates: int
    applied_creates: int
    verified_creates: int
    state: str

    def to_dict(self) -> dict[str, object]:
        """Return aggregate fields only; bearer values and full documents stay absent."""

        return asdict(self)


@dataclass(frozen=True, slots=True)
class _Topology:
    indexes: tuple[dict[str, object], ...]
    token_state: str
    tenant_user_state: str


_EXPECTED = {
    TOKEN_INDEX_NAME: {
        "name": TOKEN_INDEX_NAME,
        "key": TOKEN_INDEX_KEYS,
        "unique": True,
        "sparse": False,
        "partial_present": False,
    },
    TENANT_USER_INDEX_NAME: {
        "name": TENANT_USER_INDEX_NAME,
        "key": TENANT_USER_INDEX_KEYS,
        "unique": False,
        "sparse": False,
        "partial_present": False,
    },
}


def _fail(code: str, *, report: RefreshTokenIndexReport | None = None) -> NoReturn:
    """Raise one bounded code without retaining caller-controlled secrets."""

    raise RefreshTokenIndexAuthorityError(code, report=report)


def _require_mode(mode: IndexMode) -> IndexMode:
    """Reject arbitrary mode values before any collection operation."""

    if not isinstance(mode, IndexMode):
        _fail("INVALID_MODE")
    return mode


def _key_tuple(raw_key: object) -> tuple[tuple[str, int], ...]:
    """Normalize ordered Mongo key metadata without discarding key order."""

    if isinstance(raw_key, Mapping):
        try:
            return tuple((str(key), int(value)) for key, value in raw_key.items())
        except (TypeError, ValueError):
            _fail("INVALID_INDEX_KEY")
    if isinstance(raw_key, Sequence) and not isinstance(raw_key, (str, bytes, bytearray)):
        result: list[tuple[str, int]] = []
        for item in raw_key:
            if not isinstance(item, Sequence) or len(item) != 2:
                _fail("INVALID_INDEX_KEY")
            try:
                result.append((str(item[0]), int(cast(Any, item[1]))))
            except (TypeError, ValueError):
                _fail("INVALID_INDEX_KEY")
        return tuple(result)
    _fail("INVALID_INDEX_KEY")


def _normalized_index(raw: Mapping[str, object]) -> dict[str, object]:
    """Normalize one ``list_indexes`` document for exact comparison."""

    name = raw.get("name")
    if not isinstance(name, str) or not name:
        _fail("INVALID_INDEX_NAME")
    return {
        "name": name,
        "key": _key_tuple(raw.get("key")),
        "unique": raw.get("unique") is True,
        "sparse": raw.get("sparse", False) is True,
        "partial_present": "partialFilterExpression" in raw,
    }


def _semantic_equal(actual: Mapping[str, object], expected: Mapping[str, object]) -> bool:
    """Compare only the exact key and safety options in the target contract."""

    return all(
        actual.get(field) == expected.get(field)
        for field in ("key", "unique", "sparse", "partial_present")
    )


def _classify_index(
    indexes: Sequence[dict[str, object]], expected: Mapping[str, object]
) -> str:
    """Classify missing, exact, equivalent, and conflicting topology."""

    name = str(expected["name"])
    same_name = next((item for item in indexes if item.get("name") == name), None)
    if same_name is not None:
        if _semantic_equal(same_name, expected):
            return "EXACTLY_SATISFIED"
        if same_name.get("key") == expected.get("key"):
            return "CONFLICTING_SPEC"
        return "CONFLICTING_NAME"
    if any(_semantic_equal(item, expected) for item in indexes):
        return "EQUIVALENT_SPEC_DIFFERENT_NAME"
    return "MISSING"


def _topology(refresh_tokens: Any) -> _Topology:
    """Read and classify all current index metadata without DDL."""

    list_indexes = getattr(refresh_tokens, "list_indexes", None)
    if not callable(list_indexes):
        _fail("INDEX_INTROSPECTION_REQUIRED")
    try:
        normalized = tuple(_normalized_index(dict(raw)) for raw in cast(Any, list_indexes()))
    except RefreshTokenIndexAuthorityError:
        raise
    except Exception as error:
        raise RefreshTokenIndexAuthorityError("INDEX_INTROSPECTION_FAILED") from error
    return _Topology(
        indexes=normalized,
        token_state=_classify_index(normalized, _EXPECTED[TOKEN_INDEX_NAME]),
        tenant_user_state=_classify_index(normalized, _EXPECTED[TENANT_USER_INDEX_NAME]),
    )


def _is_valid_token(value: object) -> bool:
    """Require the current raw bearer schema without exposing its value."""

    return isinstance(value, str) and bool(value)


def _is_valid_identity(value: object) -> bool:
    """Require a non-empty, non-whitespace durable user identity string."""

    return isinstance(value, str) and bool(value) and value == value.strip()


def _is_valid_tenant(value: object) -> bool:
    """Require a non-empty, non-whitespace tenant identity string."""

    return isinstance(value, str) and bool(value) and value == value.strip()


def _duplicate_counts(refresh_tokens: Any) -> tuple[int, int, int]:
    """Aggregate duplicate token cardinality without returning token keys."""

    aggregate = getattr(refresh_tokens, "aggregate", None)
    if not callable(aggregate):
        _fail("DUPLICATE_PREFLIGHT_REQUIRED")
    pipeline = [
        {"$group": {"_id": "$token", "cardinality": {"$sum": 1}}},
        {"$match": {"cardinality": {"$gt": 1}}},
    ]
    groups = documents = maximum = 0
    try:
        for raw in cast(Any, aggregate(pipeline)):
            cardinality = raw.get("cardinality") if isinstance(raw, Mapping) else None
            if isinstance(cardinality, bool) or not isinstance(cardinality, int) or cardinality < 2:
                _fail("DUPLICATE_PREFLIGHT_CORRUPT")
            groups += 1
            documents += cardinality
            maximum = max(maximum, cardinality)
    except RefreshTokenIndexAuthorityError:
        raise
    except Exception as error:
        raise RefreshTokenIndexAuthorityError("DUPLICATE_PREFLIGHT_FAILED") from error
    return groups, documents, maximum


def _row_preconditions(refresh_tokens: Any) -> tuple[int, int, int, int, int]:
    """Count invalid token, tenantless, invalid tenant, and invalid identity rows."""

    find = getattr(refresh_tokens, "find", None)
    if not callable(find):
        _fail("ROW_PREFLIGHT_REQUIRED")
    total = invalid_token = tenantless = invalid_tenant = invalid_user = 0
    projection = {"token": 1, "tenant_id": 1, "user_id": 1}
    try:
        for raw in cast(Any, find({}, projection=projection)):
            if not isinstance(raw, Mapping):
                _fail("ROW_PREFLIGHT_CORRUPT")
            total += 1
            if not _is_valid_token(raw.get("token")):
                invalid_token += 1
            if "tenant_id" not in raw:
                tenantless += 1
            elif not _is_valid_tenant(raw.get("tenant_id")):
                invalid_tenant += 1
            if not _is_valid_identity(raw.get("user_id")):
                invalid_user += 1
    except RefreshTokenIndexAuthorityError:
        raise
    except Exception as error:
        raise RefreshTokenIndexAuthorityError("ROW_PREFLIGHT_FAILED") from error
    return total, invalid_token, tenantless, invalid_tenant, invalid_user


def _report(
    *,
    mode: IndexMode,
    topology: _Topology,
    total: int,
    invalid_token: int,
    duplicate_groups: int,
    duplicate_documents: int,
    duplicate_max: int,
    tenantless: int,
    invalid_tenant: int,
    invalid_user: int,
    planned: int,
    applied: int,
    verified: int,
    state: str,
) -> RefreshTokenIndexReport:
    """Build one bounded aggregate report."""

    return RefreshTokenIndexReport(
        mode=mode.value,
        total_rows=total,
        invalid_token_rows=invalid_token,
        duplicate_token_groups=duplicate_groups,
        duplicate_token_documents=duplicate_documents,
        duplicate_token_max_cardinality=duplicate_max,
        tenantless_rows=tenantless,
        invalid_tenant_rows=invalid_tenant,
        invalid_user_id_rows=invalid_user,
        token_index_state=topology.token_state,
        tenant_user_index_state=topology.tenant_user_state,
        planned_creates=planned,
        applied_creates=applied,
        verified_creates=verified,
        state=state,
    )


def _run_preflight(refresh_tokens: Any, mode: IndexMode) -> RefreshTokenIndexReport:
    """Perform complete topology and row safety inspection before any DDL."""

    topology = _topology(refresh_tokens)
    total, invalid_token, tenantless, invalid_tenant, invalid_user = _row_preconditions(refresh_tokens)
    duplicate_groups, duplicate_documents, duplicate_max = _duplicate_counts(refresh_tokens)
    planned = sum(
        state == "MISSING"
        for state in (topology.token_state, topology.tenant_user_state)
    )
    blocked = (
        invalid_token > 0
        or duplicate_groups > 0
        or tenantless > 0
        or invalid_tenant > 0
        or invalid_user > 0
        or topology.token_state in {"CONFLICTING_NAME", "CONFLICTING_SPEC"}
        or topology.tenant_user_state in {"CONFLICTING_NAME", "CONFLICTING_SPEC"}
    )
    state = f"{mode.value}_BLOCKED" if blocked else f"{mode.value}_READY"
    return _report(
        mode=mode,
        topology=topology,
        total=total,
        invalid_token=invalid_token,
        duplicate_groups=duplicate_groups,
        duplicate_documents=duplicate_documents,
        duplicate_max=duplicate_max,
        tenantless=tenantless,
        invalid_tenant=invalid_tenant,
        invalid_user=invalid_user,
        planned=planned,
        applied=0,
        verified=0,
        state=state,
    )


def _verify_one(refresh_tokens: Any, expected: Mapping[str, object]) -> None:
    """Require one exact semantic index after its DDL call."""

    topology = _topology(refresh_tokens)
    actual_state = (
        topology.token_state
        if expected["name"] == TOKEN_INDEX_NAME
        else topology.tenant_user_state
    )
    if actual_state not in {"EXACTLY_SATISFIED", "EQUIVALENT_SPEC_DIFFERENT_NAME"}:
        _fail("POST_CREATE_SPEC_VERIFICATION_FAILED")


def _create_one(refresh_tokens: Any, expected: Mapping[str, object]) -> None:
    """Create one named index with the exact non-partial, non-sparse contract."""

    create_index = getattr(refresh_tokens, "create_index", None)
    if not callable(create_index):
        _fail("INDEX_DDL_REQUIRED")
    try:
        create_index(
            list(cast(tuple[tuple[str, int], ...], expected["key"])),
            unique=bool(expected["unique"]),
            sparse=False,
            name=str(expected["name"]),
        )
    except RefreshTokenIndexAuthorityError:
        raise
    except Exception as error:
        code = (
            "TOKEN_INDEX_CREATE_FAILED"
            if expected["name"] == TOKEN_INDEX_NAME
            else "TENANT_USER_INDEX_CREATE_FAILED"
        )
        raise RefreshTokenIndexAuthorityError(code) from error
    _verify_one(refresh_tokens, expected)


def reconcile_refresh_token_indexes(
    *,
    refresh_tokens: Any,
    mode: IndexMode = IndexMode.DRY_RUN,
) -> RefreshTokenIndexReport:
    """Inspect or explicitly create the two governed refresh-token indexes.

    Authority: additive ``refresh_tokens`` index topology only.  The caller
    supplies the collection and remains responsible for connection, timing,
    quiescence, and operational evidence.  No URI, database, client, session,
    transaction, document mutation, token issuance, password, JWT, MFA, Node,
    or financial authority is present.

    DRY_RUN performs only ``find``, aggregate, and index-list reads.  APPLY
    requires an explicit :class:`IndexMode.APPLY`, re-runs all preconditions,
    creates the unique raw-token index first and tenant/user lookup second,
    verifies each exact topology, and never drops or rebuilds anything.
    Invalid/duplicate tokens, tenantless or malformed tenant/user rows, and
    same-name conflicts fail closed before DDL.  A second APPLY is an exact
    no-op.  Errors contain only stable codes and bounded reports.
    """

    selected_mode = _require_mode(mode)
    if refresh_tokens is None:
        _fail("EXPLICIT_COLLECTION_REQUIRED")
    preflight = _run_preflight(refresh_tokens, selected_mode)
    if selected_mode is IndexMode.DRY_RUN:
        return preflight
    if preflight.state != "APPLY_READY":
        return preflight
    applied = 0
    verified = 0
    for name in (TOKEN_INDEX_NAME, TENANT_USER_INDEX_NAME):
        expected = _EXPECTED[name]
        state = preflight.token_index_state if name == TOKEN_INDEX_NAME else preflight.tenant_user_index_state
        if state != "MISSING":
            continue
        try:
            _create_one(refresh_tokens, expected)
        except RefreshTokenIndexAuthorityError as error:
            current = _topology(refresh_tokens)
            partial = _report(
                mode=selected_mode,
                topology=current,
                total=preflight.total_rows,
                invalid_token=preflight.invalid_token_rows,
                duplicate_groups=preflight.duplicate_token_groups,
                duplicate_documents=preflight.duplicate_token_documents,
                duplicate_max=preflight.duplicate_token_max_cardinality,
                tenantless=preflight.tenantless_rows,
                invalid_tenant=preflight.invalid_tenant_rows,
                invalid_user=preflight.invalid_user_id_rows,
                planned=preflight.planned_creates,
                applied=applied,
                verified=verified,
                state="APPLY_PARTIAL_FAILURE",
            )
            raise RefreshTokenIndexAuthorityError(error.code, report=partial) from error
        applied += 1
        verified += 1
    final = _run_preflight(refresh_tokens, selected_mode)
    if final.state != "APPLY_READY":
        _fail(
            "POST_APPLY_TOPOLOGY_OR_PRECONDITION_FAILED",
            report=_report(
                mode=selected_mode,
                topology=_topology(refresh_tokens),
                total=final.total_rows,
                invalid_token=final.invalid_token_rows,
                duplicate_groups=final.duplicate_token_groups,
                duplicate_documents=final.duplicate_token_documents,
                duplicate_max=final.duplicate_token_max_cardinality,
                tenantless=final.tenantless_rows,
                invalid_tenant=final.invalid_tenant_rows,
                invalid_user=final.invalid_user_id_rows,
                planned=final.planned_creates,
                applied=applied,
                verified=verified,
                state="APPLY_PARTIAL_FAILURE",
            ),
        )
    return _report(
        mode=selected_mode,
        topology=_topology(refresh_tokens),
        total=final.total_rows,
        invalid_token=final.invalid_token_rows,
        duplicate_groups=final.duplicate_token_groups,
        duplicate_documents=final.duplicate_token_documents,
        duplicate_max=final.duplicate_token_max_cardinality,
        tenantless=final.tenantless_rows,
        invalid_tenant=final.invalid_tenant_rows,
        invalid_user=final.invalid_user_id_rows,
        planned=preflight.planned_creates,
        applied=applied,
        verified=verified,
        state="APPLY_ALREADY_SATISFIED" if applied == 0 else "APPLY_VERIFIED",
    )


__all__ = [
    "DEFAULT_MODE",
    "IndexMode",
    "RefreshTokenIndexAuthorityError",
    "RefreshTokenIndexReport",
    "TENANT_USER_INDEX_KEYS",
    "TENANT_USER_INDEX_NAME",
    "TOKEN_INDEX_KEYS",
    "TOKEN_INDEX_NAME",
    "VERSION",
    "reconcile_refresh_token_indexes",
]


# ARTIFACT: refresh_token_indexes.py
# VERSION: v1.0.0-R10C2I1-REFRESH-TOKEN-INDEX-AUTHORITY
# AUTHORITY BOUNDARY: additive refresh_tokens index reconciliation only; no
# document, connection, token, password, JWT, MFA, Node, or financial power.
# TENANT POSTURE: exact tenant_id/user_id presence and validity are required.
# FAIL-CLOSED POSTURE: dry-run default, explicit APPLY, duplicate/invalid-row
# guards, ordered DDL, exact post-create verification, and no destructive DDL.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
