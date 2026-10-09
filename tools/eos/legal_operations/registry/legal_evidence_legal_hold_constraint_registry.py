"""WILSY OS — durable Legal Evidence legal-hold constraint history registry.

TITLE: Legal Evidence Legal Hold Constraint Registry
VERSION: v1.0.0-L10A2R-C4D4B-R3-LEGAL-HOLD-CONSTRAINT-REGISTRY
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Persist and exactly replay immutable sourced legal-hold facts while
         preserving tenant-scoped hold and provider-object history without
         deriving current state, issuing or releasing holds, or authorizing
         downstream disposition.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/registry/legal_evidence_legal_hold_constraint_registry.py
COLLABORATION / OWNERSHIP:
    C4D4B domain owns immutable legal-hold fact truth and hold-blocking
    assessment semantics. This registry owns durable append-only persistence,
    exact replay, strict hydration, and bounded history enumeration only.
    Legal-hold issuance/release authority, current-state projection, retention
    satisfaction, orphan proof, deletion authorization, provider mutation and
    reconciliation remain separately certified later gates.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0-L10A2R-C4D4B-R3 establishes one immutable fact identity per exact
    tenant+fingerprint, non-unique hold/provider-object history indexes,
    active caller-owned transaction enforcement, exact replay, strict
    chronology/state hydration, bounded history enumeration and zero-TTL
    posture without deriving a governing/current hold state.
COMPLIANCE:
    Governance-aligned legal evidence persistence primitive only. This registry
    does not determine whether litigation, investigation, court, client,
    regulatory or other facts legally require a hold and does not select an
    authoritative legal source.
SECURITY / PRIVACY POSTURE:
    Stores only opaque legal-hold constraint evidence already validated by the
    domain. No credentials, secrets, raw source evidence, provider IO, network
    capability, deletion execution or financial execution authority.
TENANT BOUNDARY:
    Every durable identity, replay lookup and history read is exact tenant
    scoped. Cross-tenant absence is indistinguishable from ordinary absence.
AUTHORITY BOUNDARY:
    Durable append-only legal-hold constraint persistence/replay and bounded
    immutable history enumeration only. No current-state selection, issuance,
    release, transition authorization, retention satisfaction, orphan proof,
    deletion authorization or provider mutation.
FINANCIAL AUTHORITY BOUNDARY:
    No billing, invoice, charge, payment, execution or settlement truth.
    Kennel EOS remains exclusive financial execution authority.

TRANSACTION BOUNDARY:
    Caller supplies and owns one already-active Mongo transaction for every
    operational read or write. This registry never starts, commits, aborts or
    retries transactions.

HISTORY BOUNDARY:
    Same hold reference and same provider-object identity may legitimately
    have multiple immutable facts. Only tenant+fingerprint is unique.
    History ordering is deterministic but ordering never confers legal or
    current-state authority.

TTL POSTURE:
    No TTL index is permitted. Institutional legal-hold evidence must not
    disappear because wall-clock time elapsed.

FAIL-CLOSED DECLARATION:
    Missing transaction, malformed query scope, corrupt persisted evidence,
    replay divergence, duplicate races, history overflow, ambiguous schema and
    Mongo failures reject. Persisted corruption is never healed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldConstraintError,
    LegalEvidenceLegalHoldState,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D4B-R3-LEGAL-HOLD-CONSTRAINT-REGISTRY"
)

COLLECTION: Final[str] = (
    "legal_evidence_legal_hold_constraints"
)

INDEX_TENANT_FINGERPRINT: Final[str] = (
    "legal_evidence_legal_hold_tenant_fingerprint_unique"
)

INDEX_TENANT_HOLD_HISTORY: Final[str] = (
    "legal_evidence_legal_hold_tenant_hold_history"
)

INDEX_TENANT_PROVIDER_OBJECT_HISTORY: Final[str] = (
    "legal_evidence_legal_hold_tenant_provider_object_history"
)

INDEX_TENANT_HOLD_STATE_HISTORY: Final[str] = (
    "legal_evidence_legal_hold_tenant_hold_state_history"
)

MAX_HOLD_HISTORY: Final[int] = 512
MAX_PROVIDER_OBJECT_HISTORY: Final[int] = 2048

_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "tenant_id",
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "hold_reference",
        "source_evidence_reference",
        "source_evidence_fingerprint",
        "imposed_at",
        "state",
        "released_at",
        "retention_satisfied",
        "orphan_proven",
        "provider_delete_authorized",
        "fingerprint",
    }
)


class LegalEvidenceLegalHoldConstraintRegistryError(
    RuntimeError
):
    """Base durable C4D4B legal-hold registry failure."""


class LegalEvidenceLegalHoldConstraintTransactionRequiredError(
    LegalEvidenceLegalHoldConstraintRegistryError
):
    """Caller did not supply one already-active Mongo transaction."""


class LegalEvidenceLegalHoldConstraintInputError(
    LegalEvidenceLegalHoldConstraintRegistryError
):
    """Malformed query scope or unsupported persistence interface."""


class LegalEvidenceLegalHoldConstraintConflictError(
    LegalEvidenceLegalHoldConstraintRegistryError
):
    """Exact immutable fact identity was reused for divergent evidence."""


class LegalEvidenceLegalHoldConstraintNotFoundError(
    LegalEvidenceLegalHoldConstraintRegistryError
):
    """Exact tenant-scoped immutable legal-hold fact was not found."""


class LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError(
    LegalEvidenceLegalHoldConstraintRegistryError
):
    """Persisted legal-hold evidence is malformed, corrupt or divergent."""


class LegalEvidenceLegalHoldConstraintPersistenceError(
    LegalEvidenceLegalHoldConstraintRegistryError
):
    """Mongo persistence or collection interaction failed."""


def _raise(
    error_type: type[LegalEvidenceLegalHoldConstraintRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    """Raise one stable structured C4D4B registry error."""

    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _target(
    collection: Any,
) -> Any:
    """Require one collection-like persistence target."""

    if collection is None:
        _raise(
            LegalEvidenceLegalHoldConstraintInputError,
            "L10A2R_C4D4B_R3_COLLECTION_REQUIRED",
        )

    return collection


def _active_transaction(
    session: Any,
) -> Any:
    """Require one already-active caller-owned Mongo transaction."""

    if session is None:
        _raise(
            LegalEvidenceLegalHoldConstraintTransactionRequiredError,
            "L10A2R_C4D4B_R3_ACTIVE_TRANSACTION_REQUIRED",
        )

    try:
        marker = getattr(
            session,
            "in_transaction",
        )

        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ) as error:
        _raise(
            LegalEvidenceLegalHoldConstraintTransactionRequiredError,
            "L10A2R_C4D4B_R3_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalEvidenceLegalHoldConstraintTransactionRequiredError,
            "L10A2R_C4D4B_R3_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _query_text(
    name: str,
    value: object,
) -> str:
    """Require one exact non-empty, non-coerced query identity."""

    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
    ):
        _raise(
            LegalEvidenceLegalHoldConstraintInputError,
            f"L10A2R_C4D4B_R3_{name.upper()}_INVALID",
        )

    return value


def _query_fingerprint(
    value: object,
) -> str:
    """Require one lowercase SHA3-512 query fingerprint."""

    fingerprint = _query_text(
        "fingerprint",
        value,
    )

    if (
        len(
            fingerprint
        )
        != 128
        or any(
            character
            not in "0123456789abcdef"
            for character in fingerprint
        )
    ):
        _raise(
            LegalEvidenceLegalHoldConstraintInputError,
            "L10A2R_C4D4B_R3_FINGERPRINT_INVALID",
        )

    return fingerprint


def _persisted_utc(
    name: str,
    value: object,
) -> datetime:
    """Hydrate exact aware persisted ISO-8601 chronology."""

    if not isinstance(
        value,
        str,
    ):
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            f"L10A2R_C4D4B_R3_PERSISTED_{name.upper()}_INVALID",
        )

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00",
            )
        )
    except ValueError as error:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            f"L10A2R_C4D4B_R3_PERSISTED_{name.upper()}_INVALID",
            error,
        )

    if (
        parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            f"L10A2R_C4D4B_R3_PERSISTED_{name.upper()}_INVALID",
        )

    return parsed.astimezone(
        timezone.utc
    )


def _validated_value(
    value: object,
) -> LegalEvidenceLegalHoldConstraint:
    """Reconstruct one exact C4D4B fact to detect tampered input."""

    if type(
        value
    ) is not LegalEvidenceLegalHoldConstraint:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4B_R3_VALUE_TYPE_INVALID",
        )

    try:
        validated = LegalEvidenceLegalHoldConstraint(
            tenant_id=value.tenant_id,
            provider_name=value.provider_name,
            storage_reference=value.storage_reference,
            object_version_reference=value.object_version_reference,
            hold_reference=value.hold_reference,
            source_evidence_reference=value.source_evidence_reference,
            source_evidence_fingerprint=value.source_evidence_fingerprint,
            imposed_at=value.imposed_at,
            state=value.state,
            released_at=value.released_at,
            retention_satisfied=value.retention_satisfied,
            orphan_proven=value.orphan_proven,
            provider_delete_authorized=value.provider_delete_authorized,
            fingerprint=value.fingerprint,
        )
    except LegalEvidenceLegalHoldConstraintError as error:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4B_R3_VALUE_INVALID",
            error,
        )
    except (
        AttributeError,
        TypeError,
        ValueError,
    ) as error:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4B_R3_VALUE_INVALID",
            error,
        )

    if validated != value:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4B_R3_VALUE_DIVERGED",
        )

    return validated


def _document(
    value: LegalEvidenceLegalHoldConstraint,
) -> dict[str, object]:
    """Return one exact append-only durable legal-hold fact."""

    validated = _validated_value(
        value
    )

    return {
        "tenant_id":
            validated.tenant_id,
        "provider_name":
            validated.provider_name,
        "storage_reference":
            validated.storage_reference,
        "object_version_reference":
            validated.object_version_reference,
        "hold_reference":
            validated.hold_reference,
        "source_evidence_reference":
            validated.source_evidence_reference,
        "source_evidence_fingerprint":
            validated.source_evidence_fingerprint,
        "imposed_at":
            validated.imposed_at.isoformat(),
        "state":
            validated.state.value,
        "released_at":
            (
                validated.released_at.isoformat()
                if validated.released_at
                is not None
                else None
            ),
        "retention_satisfied":
            False,
        "orphan_proven":
            False,
        "provider_delete_authorized":
            False,
        "fingerprint":
            validated.fingerprint,
    }


def _hydrate(
    row: object,
) -> LegalEvidenceLegalHoldConstraint:
    """Hydrate one exact persisted fact; never heal durable corruption."""

    if not isinstance(
        row,
        dict,
    ):
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4B_R3_PERSISTED_RECORD_INVALID",
        )

    payload = dict(
        row
    )

    payload.pop(
        "_id",
        None,
    )

    if set(
        payload
    ) != _PERSISTED_FIELDS:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4B_R3_PERSISTED_RECORD_INVALID",
        )

    imposed_at = _persisted_utc(
        "imposed_at",
        payload["imposed_at"],
    )

    released_raw = payload[
        "released_at"
    ]

    released_at: datetime | None

    if released_raw is None:
        released_at = None
    else:
        released_at = _persisted_utc(
            "released_at",
            released_raw,
        )

    try:
        state = LegalEvidenceLegalHoldState(
            payload["state"]
        )

        return LegalEvidenceLegalHoldConstraint(
            tenant_id=payload["tenant_id"],
            provider_name=payload["provider_name"],
            storage_reference=payload["storage_reference"],
            object_version_reference=payload["object_version_reference"],
            hold_reference=payload["hold_reference"],
            source_evidence_reference=payload["source_evidence_reference"],
            source_evidence_fingerprint=payload[
                "source_evidence_fingerprint"
            ],
            imposed_at=imposed_at,
            state=state,
            released_at=released_at,
            retention_satisfied=payload[
                "retention_satisfied"
            ],
            orphan_proven=payload[
                "orphan_proven"
            ],
            provider_delete_authorized=payload[
                "provider_delete_authorized"
            ],
            fingerprint=payload[
                "fingerprint"
            ],
        )
    except (
        LegalEvidenceLegalHoldConstraintError,
        TypeError,
        ValueError,
    ) as error:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            "L10A2R_C4D4B_R3_PERSISTED_RECORD_INVALID",
            error,
        )


def _same(
    expected: LegalEvidenceLegalHoldConstraint,
    row: object,
) -> LegalEvidenceLegalHoldConstraint:
    """Require one durable fingerprint row to equal one exact immutable fact."""

    actual = _hydrate(
        row
    )

    if actual != expected:
        _raise(
            LegalEvidenceLegalHoldConstraintConflictError,
            "L10A2R_C4D4B_R3_IMMUTABLE_REPLAY_DIVERGENCE",
        )

    return actual


def _bounded_history(
    collection: Any,
    query: dict[str, object],
    *,
    session: Any,
    limit: int,
    overflow_code: str,
) -> tuple[LegalEvidenceLegalHoldConstraint, ...]:
    """Read one bounded exact tenant-scoped immutable history."""

    try:
        cursor = collection.find(
            query,
            session=session,
        )

        cursor = cursor.sort(
            [
                (
                    "imposed_at",
                    DESCENDING,
                ),
                (
                    "fingerprint",
                    ASCENDING,
                ),
            ]
        )

        cursor = cursor.limit(
            limit + 1
        )

        rows = list(
            cursor
        )
    except PyMongoError as error:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistenceError,
            "L10A2R_C4D4B_R3_READ_FAILED",
            error,
        )
    except AttributeError as error:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistenceError,
            "L10A2R_C4D4B_R3_COLLECTION_INTERFACE_INVALID",
            error,
        )

    if len(
        rows
    ) > limit:
        _raise(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
            overflow_code,
        )

    values = tuple(
        _hydrate(
            row
        )
        for row in rows
    )

    return tuple(
        sorted(
            values,
            key=lambda item: (
                item.imposed_at,
                item.fingerprint,
            ),
            reverse=True,
        )
    )


class LegalEvidenceLegalHoldConstraintRegistry:
    """Append-only tenant-scoped durable C4D4B fact/history registry."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        """Bind one registry to one collection-like persistence target."""

        self._collection = _target(
            collection
        )

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact immutable fact and non-unique history indexes."""

        try:
            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "fingerprint",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=INDEX_TENANT_FINGERPRINT,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "hold_reference",
                        ASCENDING,
                    ),
                    (
                        "imposed_at",
                        DESCENDING,
                    ),
                ],
                unique=False,
                name=INDEX_TENANT_HOLD_HISTORY,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "provider_name",
                        ASCENDING,
                    ),
                    (
                        "storage_reference",
                        ASCENDING,
                    ),
                    (
                        "object_version_reference",
                        ASCENDING,
                    ),
                    (
                        "imposed_at",
                        DESCENDING,
                    ),
                ],
                unique=False,
                name=INDEX_TENANT_PROVIDER_OBJECT_HISTORY,
            )

            self._collection.create_index(
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "hold_reference",
                        ASCENDING,
                    ),
                    (
                        "state",
                        ASCENDING,
                    ),
                    (
                        "imposed_at",
                        DESCENDING,
                    ),
                ],
                unique=False,
                name=INDEX_TENANT_HOLD_STATE_HISTORY,
            )

        except PyMongoError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_INDEX_CREATION_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

    def create_or_replay(
        self,
        value: LegalEvidenceLegalHoldConstraint,
        *,
        session: Any,
    ) -> LegalEvidenceLegalHoldConstraint:
        """Persist one immutable fact or return its exact fingerprint replay.

        The same tenant+hold reference and same tenant+provider object may
        contain multiple immutable facts. Fingerprint is the exact fact
        identity. This method never selects current state or performs a hold
        transition.
        """

        tx = _active_transaction(
            session
        )

        validated = _validated_value(
            value
        )

        try:
            existing = self._collection.find_one(
                {
                    "tenant_id":
                        validated.tenant_id,
                    "fingerprint":
                        validated.fingerprint,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if existing is not None:
            return _same(
                validated,
                existing,
            )

        document = _document(
            validated
        )

        try:
            result = self._collection.insert_one(
                document,
                session=tx,
            )

            if getattr(
                result,
                "acknowledged",
                False,
            ) is not True:
                _raise(
                    LegalEvidenceLegalHoldConstraintPersistenceError,
                    "L10A2R_C4D4B_R3_INSERT_NOT_ACKNOWLEDGED",
                )

        except DuplicateKeyError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintConflictError,
                "L10A2R_C4D4B_R3_WHOLE_TRANSACTION_RETRY_REQUIRED",
                error,
            )
        except LegalEvidenceLegalHoldConstraintRegistryError:
            raise
        except PyMongoError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_INSERT_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return validated

    def get_by_fingerprint(
        self,
        *,
        tenant_id: str,
        fingerprint: str,
        session: Any,
    ) -> LegalEvidenceLegalHoldConstraint:
        """Read one exact immutable fact under tenant+fingerprint identity."""

        tx = _active_transaction(
            session
        )

        tenant = _query_text(
            "tenant_id",
            tenant_id,
        )

        digest = _query_fingerprint(
            fingerprint
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "fingerprint":
                        digest,
                },
                session=tx,
            )
        except PyMongoError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_READ_FAILED",
                error,
            )
        except AttributeError as error:
            _raise(
                LegalEvidenceLegalHoldConstraintPersistenceError,
                "L10A2R_C4D4B_R3_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                LegalEvidenceLegalHoldConstraintNotFoundError,
                "L10A2R_C4D4B_R3_NOT_FOUND",
            )

        value = _hydrate(
            row
        )

        if (
            value.tenant_id != tenant
            or value.fingerprint != digest
        ):
            _raise(
                LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
                "L10A2R_C4D4B_R3_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def list_hold_history(
        self,
        *,
        tenant_id: str,
        hold_reference: str,
        session: Any,
    ) -> tuple[LegalEvidenceLegalHoldConstraint, ...]:
        """List bounded immutable facts for one exact tenant+hold reference.

        Ordering is deterministic evidence presentation only. The first row is
        not asserted to be current, governing, legally sufficient or released.
        """

        tx = _active_transaction(
            session
        )

        tenant = _query_text(
            "tenant_id",
            tenant_id,
        )

        hold = _query_text(
            "hold_reference",
            hold_reference,
        )

        values = _bounded_history(
            self._collection,
            {
                "tenant_id":
                    tenant,
                "hold_reference":
                    hold,
            },
            session=tx,
            limit=MAX_HOLD_HISTORY,
            overflow_code=(
                "L10A2R_C4D4B_R3_HOLD_HISTORY_LIMIT_EXCEEDED"
            ),
        )

        if any(
            value.tenant_id != tenant
            or value.hold_reference != hold
            for value in values
        ):
            _raise(
                LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
                "L10A2R_C4D4B_R3_HISTORY_SCOPE_MISMATCH",
            )

        return values

    def list_provider_object_history(
        self,
        *,
        tenant_id: str,
        provider_name: str,
        storage_reference: str,
        object_version_reference: str,
        session: Any,
    ) -> tuple[LegalEvidenceLegalHoldConstraint, ...]:
        """List bounded immutable hold facts for one provider object version.

        This method enumerates history only and never determines which fact, if
        any, currently governs preservation or disposition.
        """

        tx = _active_transaction(
            session
        )

        tenant = _query_text(
            "tenant_id",
            tenant_id,
        )

        provider = _query_text(
            "provider_name",
            provider_name,
        )

        storage = _query_text(
            "storage_reference",
            storage_reference,
        )

        version = _query_text(
            "object_version_reference",
            object_version_reference,
        )

        values = _bounded_history(
            self._collection,
            {
                "tenant_id":
                    tenant,
                "provider_name":
                    provider,
                "storage_reference":
                    storage,
                "object_version_reference":
                    version,
            },
            session=tx,
            limit=MAX_PROVIDER_OBJECT_HISTORY,
            overflow_code=(
                "L10A2R_C4D4B_R3_PROVIDER_OBJECT_HISTORY_LIMIT_EXCEEDED"
            ),
        )

        if any(
            value.tenant_id != tenant
            or value.provider_name != provider
            or value.storage_reference != storage
            or value.object_version_reference
            != version
            for value in values
        ):
            _raise(
                LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
                "L10A2R_C4D4B_R3_HISTORY_SCOPE_MISMATCH",
            )

        return values


__all__ = [
    "COLLECTION",
    "INDEX_TENANT_FINGERPRINT",
    "INDEX_TENANT_HOLD_HISTORY",
    "INDEX_TENANT_HOLD_STATE_HISTORY",
    "INDEX_TENANT_PROVIDER_OBJECT_HISTORY",
    "MAX_HOLD_HISTORY",
    "MAX_PROVIDER_OBJECT_HISTORY",
    "VERSION",
    "LegalEvidenceLegalHoldConstraintConflictError",
    "LegalEvidenceLegalHoldConstraintInputError",
    "LegalEvidenceLegalHoldConstraintNotFoundError",
    "LegalEvidenceLegalHoldConstraintPersistenceError",
    "LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError",
    "LegalEvidenceLegalHoldConstraintRegistry",
    "LegalEvidenceLegalHoldConstraintRegistryError",
    "LegalEvidenceLegalHoldConstraintTransactionRequiredError",
]


# ARTIFACT: legal_evidence_legal_hold_constraint_registry.py
# VERSION: v1.0.0-L10A2R-C4D4B-R3-LEGAL-HOLD-CONSTRAINT-REGISTRY
# AUTHORITY BOUNDARY: append-only durable legal-hold fact persistence/history only
# TENANT POSTURE: every identity and history read is exact tenant scoped
# FACT IDENTITY POSTURE: only tenant+fingerprint is unique
# HISTORY POSTURE: hold/provider-object/state histories are non-unique and immutable
# CURRENT-STATE POSTURE: registry derives no current or governing hold state
# TRANSACTION POSTURE: caller owns one already-active Mongo transaction
# REPLAY POSTURE: exact immutable fingerprint replay only
# CORRUPTION POSTURE: strict domain reconstruction; no self-healing
# TTL POSTURE: no TTL index or wall-clock deletion
# RETENTION POSTURE: no retention-satisfaction authority
# LEGAL-HOLD POSTURE: no issuance, release, activation or transition authority
# ORPHAN POSTURE: no orphan proof or inference authority
# DELETION POSTURE: no deletion authorization or provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# FAIL-CLOSED POSTURE: scope, transaction, corruption, overflow and Mongo failures reject
# END OF WILSY OS SOVEREIGN ARTIFACT
