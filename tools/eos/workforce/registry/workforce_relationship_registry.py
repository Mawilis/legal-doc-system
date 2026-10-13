"""Append-only workforce relationship history registry.

VERSION:
    v1.0.0-WILSY-W3B-WORKFORCE-RELATIONSHIP-REGISTRY

AUTHORITY:
    Durable immutable workforce-history persistence and bounded reads only.

Transaction lifecycle and retries remain caller-owned.
No TTL, update, delete, IAM, commercial, session, or financial authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, cast

from pymongo import ASCENDING
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)

from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
)


VERSION: Final[str] = (
    "v1.0.0-WILSY-W3B-WORKFORCE-RELATIONSHIP-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "workforce_relationship_history"
)

REVISION_INDEX_NAME: Final[str] = (
    "workforce_relationship_scope_identity_revision_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "workforce_relationship_scope_fingerprint_unique"
)

PRINCIPAL_INDEX_NAME: Final[str] = (
    "workforce_relationship_scope_principal_history"
)


class WorkforceRelationshipRegistryError(RuntimeError):
    """Base persistence error."""


class WorkforceRelationshipRegistryInputError(
    WorkforceRelationshipRegistryError
):
    """Malformed registry input."""


class WorkforceRelationshipRegistryTransactionRequiredError(
    WorkforceRelationshipRegistryError
):
    """Operational reads/writes require caller-owned active transaction."""


class WorkforceRelationshipRegistryNotFoundError(
    WorkforceRelationshipRegistryError
):
    """Requested immutable workforce evidence is absent."""


class WorkforceRelationshipRegistryConflictError(
    WorkforceRelationshipRegistryError
):
    """Identity, lineage, or replay conflicts."""


class WorkforceRelationshipRegistryPersistedRecordInvalidError(
    WorkforceRelationshipRegistryError
):
    """Persisted row cannot hydrate to canonical W3A truth."""


class WorkforceRelationshipRegistryRetryTransactionError(
    WorkforceRelationshipRegistryError
):
    """Caller must abort and retry the complete transaction."""


def _require_nonblank(
    value: object,
    field: str,
) -> str:
    if type(value) is not str or not value.strip():
        raise WorkforceRelationshipRegistryInputError(
            f"{field.upper()}_INVALID"
        )

    return value.strip()


def _require_transaction(
    session: object,
) -> object:
    if session is None:
        raise WorkforceRelationshipRegistryTransactionRequiredError(
            "W3B_ACTIVE_TRANSACTION_REQUIRED"
        )

    try:
        active = getattr(
            session,
            "in_transaction",
        )
    except Exception as error:
        raise WorkforceRelationshipRegistryTransactionRequiredError(
            "W3B_ACTIVE_TRANSACTION_REQUIRED"
        ) from error

    if active is not True:
        raise WorkforceRelationshipRegistryTransactionRequiredError(
            "W3B_ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _collection(
    collection: Any,
) -> Any:
    if collection is None:
        raise WorkforceRelationshipRegistryInputError(
            "COLLECTION_REQUIRED"
        )

    return collection


def _hydrate(
    raw: object,
) -> WorkforceRelationship:
    if not isinstance(raw, Mapping):
        raise WorkforceRelationshipRegistryPersistedRecordInvalidError(
            "W3B_PERSISTED_RECORD_INVALID"
        )

    document = dict(raw)
    document.pop("_id", None)

    try:
        return WorkforceRelationship.from_dict(
            cast(Mapping[str, Any], document)
        )
    except Exception as error:
        raise WorkforceRelationshipRegistryPersistedRecordInvalidError(
            "W3B_PERSISTED_RECORD_INVALID"
        ) from error


def ensure_indexes(
    collection: Any,
) -> None:
    """Create exact non-TTL history/query indexes."""

    target = _collection(collection)

    try:
        target.create_index(
            [
                ("scope_kind", ASCENDING),
                ("scope_id", ASCENDING),
                ("relationship_id", ASCENDING),
                ("revision", ASCENDING),
            ],
            unique=True,
            name=REVISION_INDEX_NAME,
        )

        target.create_index(
            [
                ("scope_kind", ASCENDING),
                ("scope_id", ASCENDING),
                ("fingerprint", ASCENDING),
            ],
            unique=True,
            name=FINGERPRINT_INDEX_NAME,
        )

        target.create_index(
            [
                ("scope_kind", ASCENDING),
                ("scope_id", ASCENDING),
                ("principal_id", ASCENDING),
                ("status_effective_at", ASCENDING),
            ],
            unique=False,
            name=PRINCIPAL_INDEX_NAME,
        )
    except Exception as error:
        raise WorkforceRelationshipRegistryError(
            "W3B_INDEX_CREATION_FAILED"
        ) from error


def get_revision(
    scope_kind: str,
    scope_id: str,
    relationship_id: str,
    revision: int,
    *,
    collection: Any,
    session: object,
) -> WorkforceRelationship:
    tx = _require_transaction(session)

    if (
        type(revision) is not int
        or revision < 1
    ):
        raise WorkforceRelationshipRegistryInputError(
            "REVISION_INVALID"
        )

    scope = _require_nonblank(
        scope_kind,
        "scope_kind",
    )
    owner = _require_nonblank(
        scope_id,
        "scope_id",
    )
    identity = _require_nonblank(
        relationship_id,
        "relationship_id",
    )

    try:
        raw = _collection(collection).find_one(
            {
                "scope_kind": scope,
                "scope_id": owner,
                "relationship_id": identity,
                "revision": revision,
            },
            session=tx,
        )
    except PyMongoError as error:
        raise WorkforceRelationshipRegistryError(
            "W3B_READ_FAILED"
        ) from error

    if raw is None:
        raise WorkforceRelationshipRegistryNotFoundError(
            "W3B_RELATIONSHIP_REVISION_NOT_FOUND"
        )

    return _hydrate(raw)


def list_history(
    scope_kind: str,
    scope_id: str,
    relationship_id: str,
    *,
    collection: Any,
    session: object,
) -> tuple[WorkforceRelationship, ...]:
    tx = _require_transaction(session)

    scope = _require_nonblank(
        scope_kind,
        "scope_kind",
    )
    owner = _require_nonblank(
        scope_id,
        "scope_id",
    )
    identity = _require_nonblank(
        relationship_id,
        "relationship_id",
    )

    try:
        cursor = _collection(collection).find(
            {
                "scope_kind": scope,
                "scope_id": owner,
                "relationship_id": identity,
            },
            session=tx,
        ).sort("revision", ASCENDING)

        rows = tuple(cursor)
    except PyMongoError as error:
        raise WorkforceRelationshipRegistryError(
            "W3B_HISTORY_READ_FAILED"
        ) from error

    if not rows:
        raise WorkforceRelationshipRegistryNotFoundError(
            "W3B_RELATIONSHIP_HISTORY_NOT_FOUND"
        )

    values = tuple(
        _hydrate(raw)
        for raw in rows
    )

    if tuple(
        value.revision
        for value in values
    ) != tuple(
        range(1, len(values) + 1)
    ):
        raise WorkforceRelationshipRegistryPersistedRecordInvalidError(
            "W3B_REVISION_HISTORY_INVALID"
        )

    previous = None

    for value in values:
        if previous is not None:
            if (
                value.supersedes_fingerprint
                != previous.fingerprint
            ):
                raise WorkforceRelationshipRegistryPersistedRecordInvalidError(
                    "W3B_FINGERPRINT_CHAIN_INVALID"
                )

            if (
                value.scope_kind
                is not previous.scope_kind
                or value.scope_id
                != previous.scope_id
                or value.relationship_id
                != previous.relationship_id
                or value.principal_id
                != previous.principal_id
                or value.relationship_type
                is not previous.relationship_type
            ):
                raise WorkforceRelationshipRegistryPersistedRecordInvalidError(
                    "W3B_HISTORY_IDENTITY_INVALID"
                )

        previous = value

    return values


def list_principal_relationships(
    scope_kind: str,
    scope_id: str,
    principal_id: str,
    *,
    collection: Any,
    session: object,
) -> tuple[WorkforceRelationship, ...]:
    tx = _require_transaction(session)

    scope = _require_nonblank(
        scope_kind,
        "scope_kind",
    )
    owner = _require_nonblank(
        scope_id,
        "scope_id",
    )
    principal = _require_nonblank(
        principal_id,
        "principal_id",
    )

    try:
        rows = tuple(
            _collection(collection).find(
                {
                    "scope_kind": scope,
                    "scope_id": owner,
                    "principal_id": principal,
                },
                session=tx,
            ).sort(
                [
                    ("relationship_id", ASCENDING),
                    ("revision", ASCENDING),
                ]
            )
        )
    except PyMongoError as error:
        raise WorkforceRelationshipRegistryError(
            "W3B_PRINCIPAL_HISTORY_READ_FAILED"
        ) from error

    return tuple(
        _hydrate(raw)
        for raw in rows
    )


def persist_revision(
    relationship: WorkforceRelationship,
    *,
    collection: Any,
    session: object,
) -> WorkforceRelationship:
    """Append one immutable revision or return its exact replay."""

    tx = _require_transaction(session)

    if not isinstance(
        relationship,
        WorkforceRelationship,
    ):
        raise WorkforceRelationshipRegistryInputError(
            "WORKFORCE_RELATIONSHIP_REQUIRED"
        )

    target = _collection(collection)

    identity_filter = {
        "scope_kind":
            relationship.scope_kind.value,
        "scope_id":
            relationship.scope_id,
        "relationship_id":
            relationship.relationship_id,
        "revision":
            relationship.revision,
    }

    try:
        existing_raw = target.find_one(
            identity_filter,
            session=tx,
        )
    except PyMongoError as error:
        raise WorkforceRelationshipRegistryError(
            "W3B_PREWRITE_READ_FAILED"
        ) from error

    if existing_raw is not None:
        existing = _hydrate(
            existing_raw
        )

        if (
            existing.fingerprint
            == relationship.fingerprint
            and existing == relationship
        ):
            return existing

        raise WorkforceRelationshipRegistryConflictError(
            "W3B_DIVERGENT_REPLAY"
        )

    if relationship.revision > 1:
        try:
            predecessor_raw = target.find_one(
                {
                    "scope_kind":
                        relationship.scope_kind.value,
                    "scope_id":
                        relationship.scope_id,
                    "relationship_id":
                        relationship.relationship_id,
                    "revision":
                        relationship.revision - 1,
                },
                session=tx,
            )
        except PyMongoError as error:
            raise WorkforceRelationshipRegistryError(
                "W3B_PREDECESSOR_READ_FAILED"
            ) from error

        if predecessor_raw is None:
            raise WorkforceRelationshipRegistryConflictError(
                "W3B_PREDECESSOR_REQUIRED"
            )

        predecessor = _hydrate(
            predecessor_raw
        )

        if (
            predecessor.fingerprint
            != relationship.supersedes_fingerprint
        ):
            raise WorkforceRelationshipRegistryConflictError(
                "W3B_PREDECESSOR_FINGERPRINT_MISMATCH"
            )

        if (
            predecessor.principal_id
            != relationship.principal_id
            or predecessor.relationship_type
            is not relationship.relationship_type
        ):
            raise WorkforceRelationshipRegistryConflictError(
                "W3B_RELATIONSHIP_IDENTITY_CHANGED"
            )

        if (
            predecessor.effective_from
            != relationship.effective_from
        ):
            raise WorkforceRelationshipRegistryConflictError(
                "W3B_EFFECTIVE_FROM_CHANGED"
            )

        if (
            relationship.status_effective_at
            < predecessor.status_effective_at
        ):
            raise WorkforceRelationshipRegistryConflictError(
                "W3B_STATUS_TIME_REGRESSION"
            )

        if predecessor.status.value == "ENDED":
            raise WorkforceRelationshipRegistryConflictError(
                "W3B_ENDED_RELATIONSHIP_TERMINAL"
            )

    try:
        target.insert_one(
            relationship.to_dict(),
            session=tx,
        )
    except DuplicateKeyError as error:
        raise WorkforceRelationshipRegistryRetryTransactionError(
            "W3B_DUPLICATE_RACE_RETRY_TRANSACTION"
        ) from error
    except PyMongoError as error:
        if getattr(
            error,
            "has_error_label",
            lambda _: False,
        )("TransientTransactionError"):
            raise WorkforceRelationshipRegistryRetryTransactionError(
                "W3B_TRANSIENT_RETRY_TRANSACTION"
            ) from error

        raise WorkforceRelationshipRegistryError(
            "W3B_INSERT_FAILED"
        ) from error

    return get_revision(
        relationship.scope_kind.value,
        relationship.scope_id,
        relationship.relationship_id,
        relationship.revision,
        collection=target,
        session=tx,
    )


__all__ = [
    "COLLECTION_NAME",
    "FINGERPRINT_INDEX_NAME",
    "PRINCIPAL_INDEX_NAME",
    "REVISION_INDEX_NAME",
    "VERSION",
    "WorkforceRelationshipRegistryConflictError",
    "WorkforceRelationshipRegistryError",
    "WorkforceRelationshipRegistryInputError",
    "WorkforceRelationshipRegistryNotFoundError",
    "WorkforceRelationshipRegistryPersistedRecordInvalidError",
    "WorkforceRelationshipRegistryRetryTransactionError",
    "WorkforceRelationshipRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_revision",
    "list_history",
    "list_principal_relationships",
    "persist_revision",
]


# HISTORY: APPEND ONLY.
# TTL INDEX: NONE.
# MUTABLE CURRENT FLAG: NONE.
# TRANSACTION OWNER: CALLER.
# IAM AUTHORITY: NONE.
# FINANCIAL EXECUTION AUTHORITY: NONE.
