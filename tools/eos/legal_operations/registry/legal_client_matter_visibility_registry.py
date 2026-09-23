"""Durable immutable history for Legal Operations client-matter visibility.

TITLE: WILSY OS Legal Client Matter Visibility Registry
VERSION: v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY
AUTHORITY: Durable append-only persistence and current-state resolution of L8-7A visibility evidence.
EPITOME: Persist one ACTIVE client-to-CaseMatter visibility grant and at most one
         immutable REVOKED successor per stable binding identity, derive current
         visibility only from complete strict history, enumerate active matters
         for one exact tenant/client principal, preserve exact replay, tenant
         isolation, caller-owned sessions, and fail closed on corruption,
         lifecycle gaps, reactivation, divergent replay, or persistence failure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_client_matter_visibility_registry.py
COLLABORATION / OWNERSHIP: L8-7A owns immutable visibility value semantics; P1
                            owns CaseMatter truth; IAM owns current principal,
                            membership, business role and permissions; this
                            registry owns append-only visibility persistence and
                            strict current-history derivation only. Provisioning
                            orchestration and client projection remain later gates.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY
           establishes tenant-scoped append-only grant/revocation persistence,
           exact replay, stable binding-identity lifecycle validation, many-
           matter-per-client and many-client-per-matter support, strict active
           resolution, deterministic active-matter enumeration, unique snapshot/
           lifecycle indexes, race recovery, and no delete/reactivation/healing.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Stores only opaque visibility relation evidence; no
                             credentials, tokens, document payloads, client
                             profiles, GPS, provider, AI, payment, or settlement data.
TENANT BOUNDARY: Every query, index and returned value is tenant-scoped; foreign
                 rows are indistinguishable from absence.
AUTHORITY BOUNDARY: Persistence/currentness only. An ACTIVE registry result does
                    not itself prove authentication, membership, LEGAL_CLIENT
                    role, read permission, or HTTP authorization.
FINANCIAL AUTHORITY BOUNDARY: No invoice, payment, execution or settlement
                              semantics; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller owns optional Mongo session/transaction; registry
                      never starts, commits, aborts, retries whole transactions,
                      updates, deletes, or mutates durable evidence in place.
FAIL-CLOSED DECLARATION: Malformed shape, fingerprint drift, duplicate/divergent
                         lifecycle snapshots, revoked-only history, reactivation,
                         tenant/scope drift, persistence failure and ambiguous
                         duplicate-key races reject without healing.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    SCHEMA,
    VERSION as BINDING_VERSION,
    LegalClientMatterVisibilityBinding,
    LegalClientMatterVisibilityStatus,
)


VERSION: Final[str] = "v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY"
COLLECTION: Final[str] = "legal_operations_client_matter_visibility_bindings"
_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "binding_identity",
        "tenant_id",
        "client_principal_id",
        "case_matter_id",
        "source_case_matter_fingerprint",
        "granted_by_principal_id",
        "granted_at",
        "grant_evidence_reference",
        "status",
        "revoked_by_principal_id",
        "revoked_at",
        "revocation_evidence_reference",
        "fingerprint",
    }
)


class LegalClientMatterVisibilityRegistryError(RuntimeError):
    """Base fail-closed L8-7B persistence/currentness failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalClientMatterVisibilityNotFoundError(
    LegalClientMatterVisibilityRegistryError
):
    """No current ACTIVE binding exists for the exact tenant/client/matter scope."""


class LegalClientMatterVisibilityConflictError(
    LegalClientMatterVisibilityRegistryError
):
    """A relation lifecycle conflicts with existing immutable evidence."""


class LegalClientMatterVisibilityPersistedRecordInvalidError(
    LegalClientMatterVisibilityRegistryError
):
    """Persisted visibility evidence failed strict shape/history validation."""


def _fail(
    code: str,
    cause: BaseException | None = None,
    *,
    error_type: type[LegalClientMatterVisibilityRegistryError] = (
        LegalClientMatterVisibilityRegistryError
    ),
) -> NoReturn:
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
        _fail("L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE")
    return database.get_collection(
        COLLECTION,
        codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc),
    )


def _query_identity(value: object) -> str:
    """Require one trimmed opaque lookup identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(
            "L8_7B_VISIBILITY_NOT_FOUND",
            error_type=LegalClientMatterVisibilityNotFoundError,
        )
    return cast(str, value)


def _document(value: LegalClientMatterVisibilityBinding) -> dict[str, object]:
    """Serialize one exact canonical immutable visibility snapshot."""
    if type(value) is not LegalClientMatterVisibilityBinding:
        _fail("L8_7B_VISIBILITY_VALUE_INVALID")
    return value.to_dict()


def _canonical(document: Mapping[str, object]) -> dict[str, object]:
    result = dict(document)
    result.pop("_id", None)
    return result


def _parse_time(value: object, code: str) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            _fail(
                code,
                error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
            )
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as error:
            _fail(
                code,
                error,
                error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
            )
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            _fail(
                code,
                error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
            )
        return parsed
    _fail(
        code,
        error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
    )


def _hydrate(
    document: Mapping[str, object],
) -> LegalClientMatterVisibilityBinding:
    """Strictly hydrate one immutable visibility snapshot and verify fingerprint."""
    payload = _canonical(document)
    if set(payload) != _FIELDS:
        _fail(
            "L8_7B_VISIBILITY_PERSISTED_RECORD_INVALID",
            error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
        )
    if payload.get("schema") != SCHEMA or payload.get("version") != BINDING_VERSION:
        _fail(
            "L8_7B_VISIBILITY_PERSISTED_RECORD_INVALID",
            error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
        )

    try:
        value = cast(Any, object.__new__(LegalClientMatterVisibilityBinding))
        object.__setattr__(value, "tenant_id", cast(str, payload["tenant_id"]))
        object.__setattr__(
            value,
            "client_principal_id",
            cast(str, payload["client_principal_id"]),
        )
        object.__setattr__(
            value,
            "case_matter_id",
            cast(str, payload["case_matter_id"]),
        )
        object.__setattr__(
            value,
            "source_case_matter_fingerprint",
            cast(str, payload["source_case_matter_fingerprint"]),
        )
        object.__setattr__(
            value,
            "granted_by_principal_id",
            cast(str, payload["granted_by_principal_id"]),
        )
        object.__setattr__(
            value,
            "granted_at",
            _parse_time(
                payload["granted_at"],
                "L8_7B_VISIBILITY_PERSISTED_RECORD_INVALID",
            ),
        )
        object.__setattr__(
            value,
            "grant_evidence_reference",
            cast(str, payload["grant_evidence_reference"]),
        )
        object.__setattr__(
            value,
            "status",
            LegalClientMatterVisibilityStatus(cast(str, payload["status"])),
        )
        object.__setattr__(
            value,
            "revoked_by_principal_id",
            cast(str | None, payload["revoked_by_principal_id"]),
        )
        object.__setattr__(
            value,
            "revoked_at",
            _parse_time(
                payload["revoked_at"],
                "L8_7B_VISIBILITY_PERSISTED_RECORD_INVALID",
            ),
        )
        object.__setattr__(
            value,
            "revocation_evidence_reference",
            cast(str | None, payload["revocation_evidence_reference"]),
        )
        value._validate()  # noqa: SLF001 - strict canonical hydration boundary.
        hydrated = cast(LegalClientMatterVisibilityBinding, value)
    except LegalClientMatterVisibilityRegistryError:
        raise
    except Exception as error:
        _fail(
            "L8_7B_VISIBILITY_PERSISTED_RECORD_INVALID",
            error,
            error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
        )

    if hydrated.to_dict() != payload:
        _fail(
            "L8_7B_VISIBILITY_PERSISTED_RECORD_INVALID",
            error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
        )
    return hydrated


def _same_grant(
    active: LegalClientMatterVisibilityBinding,
    revoked: LegalClientMatterVisibilityBinding,
) -> bool:
    """Prove a revoked snapshot is the immutable successor of one exact grant."""
    return (
        active.binding_identity == revoked.binding_identity
        and active.tenant_id == revoked.tenant_id
        and active.client_principal_id == revoked.client_principal_id
        and active.case_matter_id == revoked.case_matter_id
        and active.source_case_matter_fingerprint
        == revoked.source_case_matter_fingerprint
        and active.granted_by_principal_id == revoked.granted_by_principal_id
        and active.granted_at == revoked.granted_at
        and active.grant_evidence_reference == revoked.grant_evidence_reference
        and active.status is LegalClientMatterVisibilityStatus.ACTIVE
        and revoked.status is LegalClientMatterVisibilityStatus.REVOKED
    )


def _classify_history(
    rows: list[Mapping[str, object]],
) -> tuple[
    LegalClientMatterVisibilityBinding,
    LegalClientMatterVisibilityBinding | None,
]:
    """Validate one complete relation history and return ACTIVE plus optional revoke."""
    if not rows:
        _fail(
            "L8_7B_VISIBILITY_NOT_FOUND",
            error_type=LegalClientMatterVisibilityNotFoundError,
        )
    values = [_hydrate(row) for row in rows]
    identities = {value.binding_identity for value in values}
    if len(identities) != 1:
        _fail(
            "L8_7B_VISIBILITY_HISTORY_INVALID",
            error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
        )

    active = [
        value
        for value in values
        if value.status is LegalClientMatterVisibilityStatus.ACTIVE
    ]
    revoked = [
        value
        for value in values
        if value.status is LegalClientMatterVisibilityStatus.REVOKED
    ]
    if len(active) != 1 or len(revoked) > 1 or len(values) != len(active) + len(revoked):
        _fail(
            "L8_7B_VISIBILITY_HISTORY_INVALID",
            error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
        )
    current_active = active[0]
    current_revoked = revoked[0] if revoked else None
    if current_revoked is not None and not _same_grant(
        current_active,
        current_revoked,
    ):
        _fail(
            "L8_7B_VISIBILITY_HISTORY_INVALID",
            error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
        )
    return current_active, current_revoked


def _history(
    target: Any,
    *,
    tenant_id: str,
    binding_identity: str,
    session: Any,
) -> list[Mapping[str, object]]:
    """Load the complete immutable history for one stable binding identity."""
    try:
        rows = list(
            target.find(
                {
                    "tenant_id": tenant_id,
                    "binding_identity": binding_identity,
                },
                session=session,
            )
        )
    except PyMongoError as error:
        _fail("L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)
    return [cast(Mapping[str, object], row) for row in rows]


class LegalClientMatterVisibilityRegistry:
    """Append and resolve immutable client-matter visibility history only."""

    @staticmethod
    def ensure_indexes(collection: Collection[Any] | Any | None = None) -> None:
        """Create tenant-scoped immutable snapshot/lifecycle/enumeration indexes."""
        target = _target(collection)
        try:
            target.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("binding_identity", ASCENDING),
                    ("status", ASCENDING),
                ],
                unique=True,
                name="legal_operations_client_matter_visibility_lifecycle_unique",
            )
            target.create_index(
                [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
                unique=True,
                name="legal_operations_client_matter_visibility_fingerprint_unique",
            )
            target.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("client_principal_id", ASCENDING),
                    ("binding_identity", ASCENDING),
                ],
                name="legal_operations_client_visibility_principal_history",
            )
            target.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("case_matter_id", ASCENDING),
                    ("binding_identity", ASCENDING),
                ],
                name="legal_operations_matter_visibility_client_history",
            )
        except PyMongoError as error:
            _fail("L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def grant(
        value: LegalClientMatterVisibilityBinding,
        collection: Collection[Any] | Any | None = None,
        *,
        session: Any = None,
    ) -> LegalClientMatterVisibilityBinding:
        """Insert one ACTIVE grant, return exact replay, or reject reactivation."""
        document = _document(value)
        if value.status is not LegalClientMatterVisibilityStatus.ACTIVE:
            _fail("L8_7B_ACTIVE_GRANT_REQUIRED")
        target = _target(collection)
        rows = _history(
            target,
            tenant_id=value.tenant_id,
            binding_identity=value.binding_identity,
            session=session,
        )
        if rows:
            active, revoked = _classify_history(rows)
            if revoked is not None:
                _fail(
                    "L8_7B_VISIBILITY_REACTIVATION_FORBIDDEN",
                    error_type=LegalClientMatterVisibilityConflictError,
                )
            if active.to_dict() == document:
                return active
            _fail(
                "L8_7B_VISIBILITY_CONFLICT",
                error_type=LegalClientMatterVisibilityConflictError,
            )

        try:
            target.insert_one(dict(document), session=session)
        except DuplicateKeyError as error:
            raced = _history(
                target,
                tenant_id=value.tenant_id,
                binding_identity=value.binding_identity,
                session=session,
            )
            if raced:
                try:
                    active, revoked = _classify_history(raced)
                except LegalClientMatterVisibilityRegistryError as classification_error:
                    raise classification_error from error
                if revoked is None and active.to_dict() == document:
                    return active
            _fail(
                "L8_7B_VISIBILITY_CONFLICT",
                error,
                error_type=LegalClientMatterVisibilityConflictError,
            )
        except PyMongoError as error:
            _fail("L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)

        persisted = _history(
            target,
            tenant_id=value.tenant_id,
            binding_identity=value.binding_identity,
            session=session,
        )
        active, revoked = _classify_history(persisted)
        if revoked is not None or active.to_dict() != document:
            _fail(
                "L8_7B_VISIBILITY_CONFLICT",
                error_type=LegalClientMatterVisibilityConflictError,
            )
        return active

    @staticmethod
    def revoke(
        value: LegalClientMatterVisibilityBinding,
        collection: Collection[Any] | Any | None = None,
        *,
        session: Any = None,
    ) -> LegalClientMatterVisibilityBinding:
        """Append one REVOKED successor or return exact immutable replay."""
        document = _document(value)
        if value.status is not LegalClientMatterVisibilityStatus.REVOKED:
            _fail("L8_7B_REVOKED_SNAPSHOT_REQUIRED")
        target = _target(collection)
        rows = _history(
            target,
            tenant_id=value.tenant_id,
            binding_identity=value.binding_identity,
            session=session,
        )
        active, revoked = _classify_history(rows)
        if not _same_grant(active, value):
            _fail(
                "L8_7B_VISIBILITY_CONFLICT",
                error_type=LegalClientMatterVisibilityConflictError,
            )
        if revoked is not None:
            if revoked.to_dict() == document:
                return revoked
            _fail(
                "L8_7B_VISIBILITY_CONFLICT",
                error_type=LegalClientMatterVisibilityConflictError,
            )

        try:
            target.insert_one(dict(document), session=session)
        except DuplicateKeyError as error:
            raced = _history(
                target,
                tenant_id=value.tenant_id,
                binding_identity=value.binding_identity,
                session=session,
            )
            try:
                raced_active, raced_revoked = _classify_history(raced)
            except LegalClientMatterVisibilityRegistryError as classification_error:
                raise classification_error from error
            if (
                _same_grant(raced_active, value)
                and raced_revoked is not None
                and raced_revoked.to_dict() == document
            ):
                return raced_revoked
            _fail(
                "L8_7B_VISIBILITY_CONFLICT",
                error,
                error_type=LegalClientMatterVisibilityConflictError,
            )
        except PyMongoError as error:
            _fail("L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)

        persisted = _history(
            target,
            tenant_id=value.tenant_id,
            binding_identity=value.binding_identity,
            session=session,
        )
        persisted_active, persisted_revoked = _classify_history(persisted)
        if (
            not _same_grant(persisted_active, value)
            or persisted_revoked is None
            or persisted_revoked.to_dict() != document
        ):
            _fail(
                "L8_7B_VISIBILITY_CONFLICT",
                error_type=LegalClientMatterVisibilityConflictError,
            )
        return persisted_revoked

    @staticmethod
    def resolve_current_active(
        tenant_id: str,
        client_principal_id: str,
        case_matter_id: str,
        collection: Collection[Any] | Any | None = None,
        *,
        session: Any = None,
    ) -> LegalClientMatterVisibilityBinding:
        """Resolve exact current ACTIVE relation or explicit non-visibility."""
        tenant = _query_identity(tenant_id)
        principal = _query_identity(client_principal_id)
        matter = _query_identity(case_matter_id)
        target = _target(collection)
        try:
            rows = list(
                target.find(
                    {
                        "tenant_id": tenant,
                        "client_principal_id": principal,
                        "case_matter_id": matter,
                    },
                    session=session,
                )
            )
        except PyMongoError as error:
            _fail("L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)
        if not rows:
            _fail(
                "L8_7B_VISIBILITY_NOT_FOUND",
                error_type=LegalClientMatterVisibilityNotFoundError,
            )
        active, revoked = _classify_history(
            [cast(Mapping[str, object], row) for row in rows]
        )
        if (
            active.tenant_id != tenant
            or active.client_principal_id != principal
            or active.case_matter_id != matter
        ):
            _fail(
                "L8_7B_VISIBILITY_HISTORY_INVALID",
                error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
            )
        if revoked is not None:
            _fail(
                "L8_7B_VISIBILITY_NOT_FOUND",
                error_type=LegalClientMatterVisibilityNotFoundError,
            )
        return active

    @staticmethod
    def list_active_for_principal(
        tenant_id: str,
        client_principal_id: str,
        collection: Collection[Any] | Any | None = None,
        *,
        session: Any = None,
    ) -> tuple[LegalClientMatterVisibilityBinding, ...]:
        """Enumerate exact current ACTIVE matter visibility for one client principal."""
        tenant = _query_identity(tenant_id)
        principal = _query_identity(client_principal_id)
        target = _target(collection)
        try:
            rows = list(
                target.find(
                    {
                        "tenant_id": tenant,
                        "client_principal_id": principal,
                    },
                    session=session,
                )
            )
        except PyMongoError as error:
            _fail("L8_7B_VISIBILITY_PERSISTENCE_UNAVAILABLE", error)

        grouped: dict[str, list[Mapping[str, object]]] = {}
        for raw in rows:
            row = cast(Mapping[str, object], raw)
            hydrated = _hydrate(row)
            if (
                hydrated.tenant_id != tenant
                or hydrated.client_principal_id != principal
            ):
                _fail(
                    "L8_7B_VISIBILITY_HISTORY_INVALID",
                    error_type=LegalClientMatterVisibilityPersistedRecordInvalidError,
                )
            grouped.setdefault(hydrated.binding_identity, []).append(row)

        result: list[LegalClientMatterVisibilityBinding] = []
        for history_rows in grouped.values():
            active, revoked = _classify_history(history_rows)
            if revoked is None:
                result.append(active)
        return tuple(
            sorted(
                result,
                key=lambda value: (
                    value.case_matter_id,
                    value.binding_identity,
                    value.fingerprint,
                ),
            )
        )


__all__ = [
    "COLLECTION",
    "VERSION",
    "LegalClientMatterVisibilityConflictError",
    "LegalClientMatterVisibilityNotFoundError",
    "LegalClientMatterVisibilityPersistedRecordInvalidError",
    "LegalClientMatterVisibilityRegistry",
    "LegalClientMatterVisibilityRegistryError",
]


# ARTIFACT: legal_client_matter_visibility_registry.py
# VERSION: v1.0.0-L8-7B-LEGAL-CLIENT-MATTER-VISIBILITY-REGISTRY
# AUTHORITY BOUNDARY: append-only visibility persistence and strict current-history derivation only
# TENANT POSTURE: every lookup/history is exact-tenant scoped; foreign rows are ordinary absence
# FAIL-CLOSED POSTURE: corruption, gaps, divergent replay, reactivation, scope drift and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
