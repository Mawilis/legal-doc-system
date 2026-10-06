"""Immutable persistence for canonical deputy-principal identity bindings.

TITLE: WILSY OS Deputy Principal Binding Registry
VERSION: v1.0.4-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY
AUTHORITY: Durable immutable persistence and exact resolution of L8-6B bindings.
EPITOME: Persist one canonical principal-to-Deputy identity relation exactly
         once with unique tenant/principal and tenant/deputy keys, exact replay,
         strict hydration, deterministic fingerprint verification, caller-owned
         sessions, and no authorization, lifecycle, queue, rebind, delete,
         billing, payment, or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/deputy_principal_binding_registry.py
COLLABORATION / OWNERSHIP: deputy_principal_binding.py owns immutable value
                            semantics; P1 owns Deputy truth; IAM owns principal
                            and role truth; this registry owns persistence only.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.4-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY
           makes the already-proven one-sided natural-key branches explicit to
           static analysis with non-None Mapping casts; runtime conflict,
           corruption, replay, persistence, and authority semantics are unchanged.
           2026-09-23 v1.0.3-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY
           classifies one valid natural-key match as an immutable identity
           conflict rather than persisted corruption, while malformed located
           rows still fail as corruption. Mongo insert receives a defensive
           document copy so driver-added _id cannot mutate the canonical
           comparison payload and fabricate a post-insert conflict.
           2026-09-23 v1.0.2-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY
           centralizes two-key replay classification and applies it to both
           ordinary reads and DuplicateKey race recovery; no branch may accept
           one natural key before proving the other is mutually consistent.
           2026-09-23 v1.0.1-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY
           requires both tenant/principal and tenant/deputy natural-key lookups
           to be mutually consistent before exact replay, so pre-index legacy
           duplicate/corrupt rows fail closed instead of short-circuiting.
           2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY
           establishes immutable exact-replay persistence, unique principal and
           deputy tenant keys, strict persisted-shape/fingerprint hydration,
           exact principal/deputy resolution, and caller-session propagation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores only opaque canonical binding evidence; no
                             credentials, tokens, profiles, location, payment,
                             provider, or AI data.
TENANT BOUNDARY: Every index, lookup, replay check, and returned binding is
                 scoped by explicit tenant_id; foreign rows are ordinary absence.
AUTHORITY BOUNDARY: Persistence only. The registry does not prove active
                    principal, membership, tenant_deputy role, DEPUTY assignment,
                    queue access, service authority, or actor authorization.
FINANCIAL AUTHORITY BOUNDARY: No financial semantics; Kennel EOS exclusive.
TRANSACTION BOUNDARY: Caller owns optional Mongo session/transaction; this
                      registry never starts, commits, aborts, retries, updates,
                      deletes, or rebinds identity.
FAIL-CLOSED DECLARATION: Duplicate non-identical keys, malformed persisted
                         shape, fingerprint drift, absence, database errors,
                         and cross-scope evidence reject without healing.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, Mapping, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.deputy_principal_binding import (
    SCHEMA,
    VERSION as BINDING_VERSION,
    DeputyPrincipalBinding,
)


VERSION: Final[str] = "v1.0.4-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY"
COLLECTION: Final[str] = "legal_operations_deputy_principal_bindings"
_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "tenant_id",
        "principal_id",
        "deputy_id",
        "sheriff_office_id",
        "deputy_fingerprint",
        "bound_at",
        "evidence_reference",
        "fingerprint",
    }
)


class DeputyPrincipalBindingRegistryError(RuntimeError):
    """Base fail-closed L8-6B binding persistence failure."""

    def __init__(self, code: str) -> None:
        """Create one stable registry error code."""
        self.code = code
        super().__init__(code)


class DeputyPrincipalBindingNotFoundError(DeputyPrincipalBindingRegistryError):
    """No binding exists for the exact tenant/natural-key predicate."""


class DeputyPrincipalBindingConflictError(DeputyPrincipalBindingRegistryError):
    """A principal or Deputy is already bound to different immutable evidence."""


class DeputyPrincipalBindingPersistedRecordInvalidError(
    DeputyPrincipalBindingRegistryError
):
    """Persisted binding evidence failed strict shape/fingerprint validation."""


def _fail(
    code: str,
    cause: BaseException | None = None,
    *,
    error_type: type[DeputyPrincipalBindingRegistryError] = (
        DeputyPrincipalBindingRegistryError
    ),
) -> NoReturn:
    """Raise one stable registry failure while retaining technical cause."""
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _target(collection: Collection[Any] | Any | None) -> Any:
    """Resolve injected/default collection without taking transaction ownership."""
    if collection is not None:
        if isinstance(collection, Collection):
            return collection.with_options(
                codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc)
            )
        return collection

    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE")
    return database.get_collection(
        COLLECTION,
        codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc),
    )


def _query_identity(name: str, value: object) -> str:
    """Require one trimmed opaque lookup identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            "L8_6B_BINDING_NOT_FOUND",
            error_type=DeputyPrincipalBindingNotFoundError,
        )
    return cast(str, value)


def _document(value: DeputyPrincipalBinding) -> dict[str, object]:
    """Serialize one exact canonical immutable binding record."""
    if type(value) is not DeputyPrincipalBinding:
        _fail("L8_6B_BINDING_VALUE_INVALID")
    return value.to_dict()


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    """Remove Mongo transport identity and return exact persisted evidence."""
    result = dict(document)
    result.pop("_id", None)
    return result


def _hydrate(document: Mapping[str, object]) -> DeputyPrincipalBinding:
    """Strictly hydrate one stored immutable binding and verify fingerprint."""
    payload = _canonical(document)
    if set(payload) != _FIELDS:
        _fail(
            "L8_6B_BINDING_PERSISTED_RECORD_INVALID",
            error_type=DeputyPrincipalBindingPersistedRecordInvalidError,
        )
    if payload.get("schema") != SCHEMA or payload.get("version") != BINDING_VERSION:
        _fail(
            "L8_6B_BINDING_PERSISTED_RECORD_INVALID",
            error_type=DeputyPrincipalBindingPersistedRecordInvalidError,
        )
    try:
        tenant_id = cast(str, payload["tenant_id"])
        principal_id = cast(str, payload["principal_id"])
        deputy_id = cast(str, payload["deputy_id"])
        sheriff_office_id = cast(str, payload["sheriff_office_id"])
        deputy_fingerprint = cast(str, payload["deputy_fingerprint"])
        raw_bound_at = payload["bound_at"]
        if isinstance(raw_bound_at, str):
            bound_at = datetime.fromisoformat(raw_bound_at)
        elif isinstance(raw_bound_at, datetime):
            bound_at = raw_bound_at
        else:
            raise TypeError("bound_at type invalid")
        evidence_reference = cast(str, payload["evidence_reference"])

        value = cast(Any, object.__new__(DeputyPrincipalBinding))
        object.__setattr__(value, "tenant_id", tenant_id)
        object.__setattr__(value, "principal_id", principal_id)
        object.__setattr__(value, "deputy_id", deputy_id)
        object.__setattr__(value, "sheriff_office_id", sheriff_office_id)
        object.__setattr__(value, "deputy_fingerprint", deputy_fingerprint)
        object.__setattr__(value, "bound_at", bound_at)
        object.__setattr__(value, "evidence_reference", evidence_reference)
        value._validate()  # noqa: SLF001 - strict canonical hydration boundary.
        hydrated = cast(DeputyPrincipalBinding, value)
    except DeputyPrincipalBindingRegistryError:
        raise
    except Exception as error:
        _fail(
            "L8_6B_BINDING_PERSISTED_RECORD_INVALID",
            error,
            error_type=DeputyPrincipalBindingPersistedRecordInvalidError,
        )

    if hydrated.to_dict() != payload:
        _fail(
            "L8_6B_BINDING_PERSISTED_RECORD_INVALID",
            error_type=DeputyPrincipalBindingPersistedRecordInvalidError,
        )
    return hydrated


def _classify_existing_pair(
    document: dict[str, object],
    principal_existing: Mapping[str, object] | None,
    deputy_existing: Mapping[str, object] | None,
) -> DeputyPrincipalBinding | None:
    """Classify exact replay, natural-key collision, absence, or corruption.

    Neither lookup means the binding is absent. Two exact, mutually identical
    lookups prove replay. One valid lookup means exactly one natural key is
    already owned by different immutable binding evidence and therefore is a
    conflict. Hydration still runs before that classification, so malformed
    durable evidence remains persisted-record corruption rather than conflict.
    """
    if principal_existing is None and deputy_existing is None:
        return None

    if principal_existing is None:
        _hydrate(cast(Mapping[str, object], deputy_existing))
        _fail(
            "L8_6B_BINDING_CONFLICT",
            error_type=DeputyPrincipalBindingConflictError,
        )
    if deputy_existing is None:
        _hydrate(cast(Mapping[str, object], principal_existing))
        _fail(
            "L8_6B_BINDING_CONFLICT",
            error_type=DeputyPrincipalBindingConflictError,
        )

    principal_value = _hydrate(principal_existing)
    deputy_value = _hydrate(deputy_existing)
    if (
        principal_value.to_dict() != document
        or deputy_value.to_dict() != document
        or principal_value != deputy_value
    ):
        _fail(
            "L8_6B_BINDING_CONFLICT",
            error_type=DeputyPrincipalBindingConflictError,
        )
    return principal_value


class DeputyPrincipalBindingRegistry:
    """Persist and resolve immutable deputy-principal bindings only.

    The registry has no update/delete/rebind method. A successful create either
    inserts one previously absent binding or returns an exact immutable replay.
    Principal lifecycle, membership, tenant_deputy business role, DEPUTY role
    assignment, actor authorization, and canonical Deputy existence must be
    proved by the separate L8-6B orchestration gate before create is called.
    """

    @staticmethod
    def ensure_indexes(collection: Collection[Any] | Any | None = None) -> None:
        """Create two-way tenant-scoped one-to-one binding indexes."""
        target = _target(collection)
        try:
            target.create_index(
                [("tenant_id", ASCENDING), ("principal_id", ASCENDING)],
                unique=True,
                name="legal_operations_tenant_principal_deputy_binding_unique",
            )
            target.create_index(
                [("tenant_id", ASCENDING), ("deputy_id", ASCENDING)],
                unique=True,
                name="legal_operations_tenant_deputy_principal_binding_unique",
            )
            target.create_index(
                [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
                unique=True,
                name="legal_operations_tenant_deputy_binding_fingerprint_unique",
            )
        except PyMongoError as error:
            _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def create(
        value: DeputyPrincipalBinding,
        collection: Collection[Any] | Any | None = None,
        *,
        session: Any = None,
    ) -> DeputyPrincipalBinding:
        """Insert one immutable binding or return exact replay.

        The caller owns any transaction/session. Non-identical use of either
        the tenant/principal or tenant/deputy key fails as a binding conflict;
        no overwrite, rebind, role grant, or inferred authorization occurs.
        """
        document = _document(value)
        target = _target(collection)
        principal_query = {
            "tenant_id": value.tenant_id,
            "principal_id": value.principal_id,
        }
        deputy_query = {
            "tenant_id": value.tenant_id,
            "deputy_id": value.deputy_id,
        }

        try:
            principal_existing = target.find_one(principal_query, session=session)
            deputy_existing = target.find_one(deputy_query, session=session)
        except PyMongoError as error:
            _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", error)

        existing_value = _classify_existing_pair(
            document,
            cast(Mapping[str, object] | None, principal_existing),
            cast(Mapping[str, object] | None, deputy_existing),
        )
        if existing_value is not None:
            return existing_value

        try:
            target.insert_one(dict(document), session=session)
        except DuplicateKeyError as error:
            try:
                raced_principal = target.find_one(principal_query, session=session)
                raced_deputy = target.find_one(deputy_query, session=session)
            except PyMongoError as read_error:
                _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", read_error)
            try:
                raced_value = _classify_existing_pair(
                    document,
                    cast(Mapping[str, object] | None, raced_principal),
                    cast(Mapping[str, object] | None, raced_deputy),
                )
            except DeputyPrincipalBindingRegistryError as classification_error:
                raise classification_error from error
            if raced_value is not None:
                return raced_value
            _fail(
                "L8_6B_BINDING_CONFLICT",
                error,
                error_type=DeputyPrincipalBindingConflictError,
            )
        except PyMongoError as error:
            _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", error)

        try:
            persisted = target.find_one(principal_query, session=session)
        except PyMongoError as error:
            _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", error)
        if persisted is None:
            _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE")
        hydrated = _hydrate(cast(Mapping[str, object], persisted))
        if hydrated.to_dict() != document:
            _fail(
                "L8_6B_BINDING_CONFLICT",
                error_type=DeputyPrincipalBindingConflictError,
            )
        return hydrated

    @staticmethod
    def resolve_by_principal(
        tenant_id: str,
        principal_id: str,
        collection: Collection[Any] | Any | None = None,
        *,
        session: Any = None,
    ) -> DeputyPrincipalBinding:
        """Resolve one exact tenant/principal binding or explicit absence."""
        tenant = _query_identity("tenant_id", tenant_id)
        principal = _query_identity("principal_id", principal_id)
        try:
            row = _target(collection).find_one(
                {"tenant_id": tenant, "principal_id": principal},
                session=session,
            )
        except PyMongoError as error:
            _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", error)
        if row is None:
            _fail(
                "L8_6B_BINDING_NOT_FOUND",
                error_type=DeputyPrincipalBindingNotFoundError,
            )
        value = _hydrate(cast(Mapping[str, object], row))
        if value.tenant_id != tenant or value.principal_id != principal:
            _fail(
                "L8_6B_BINDING_PERSISTED_RECORD_INVALID",
                error_type=DeputyPrincipalBindingPersistedRecordInvalidError,
            )
        return value

    @staticmethod
    def resolve_by_deputy(
        tenant_id: str,
        deputy_id: str,
        collection: Collection[Any] | Any | None = None,
        *,
        session: Any = None,
    ) -> DeputyPrincipalBinding:
        """Resolve one exact tenant/Deputy binding or explicit absence."""
        tenant = _query_identity("tenant_id", tenant_id)
        deputy = _query_identity("deputy_id", deputy_id)
        try:
            row = _target(collection).find_one(
                {"tenant_id": tenant, "deputy_id": deputy},
                session=session,
            )
        except PyMongoError as error:
            _fail("L8_6B_BINDING_PERSISTENCE_UNAVAILABLE", error)
        if row is None:
            _fail(
                "L8_6B_BINDING_NOT_FOUND",
                error_type=DeputyPrincipalBindingNotFoundError,
            )
        value = _hydrate(cast(Mapping[str, object], row))
        if value.tenant_id != tenant or value.deputy_id != deputy:
            _fail(
                "L8_6B_BINDING_PERSISTED_RECORD_INVALID",
                error_type=DeputyPrincipalBindingPersistedRecordInvalidError,
            )
        return value


__all__ = [
    "COLLECTION",
    "VERSION",
    "DeputyPrincipalBindingConflictError",
    "DeputyPrincipalBindingNotFoundError",
    "DeputyPrincipalBindingPersistedRecordInvalidError",
    "DeputyPrincipalBindingRegistry",
    "DeputyPrincipalBindingRegistryError",
]


# ARTIFACT: deputy_principal_binding_registry.py
# VERSION: v1.0.4-L8-6B-DEPUTY-PRINCIPAL-BINDING-REGISTRY
# AUTHORITY BOUNDARY: immutable exact-replay binding persistence/resolution only
# TENANT POSTURE: unique tenant/principal and tenant/deputy keys; foreign rows are absence
# FAIL-CLOSED POSTURE: conflicts, corruption, absence, database failure, and fingerprint drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
