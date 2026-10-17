"""
TITLE: WILSY OS Legal Work Completion Event Registry
VERSION: v1.0.0-P14-R14-WORK-COMPLETION-EVENT-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Legal Operations

PURPOSE:
    Persist immutable LegalWorkCompletionEvent evidence under exact tenant
    scope and provide deterministic history reads.

AUTHORITY BOUNDARY:
    This registry owns durability only. It does not decide whether an actor
    may complete work, authenticate IAM, mutate LegalWorkItem status, satisfy
    dependencies, assign/supervise work, notify, invoke AI or execute finance.

TRANSACTION BOUNDARY:
    Caller owns the active Mongo transaction and whole-transaction retry.
"""

from __future__ import annotations

from collections.abc import Mapping
import hmac
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)

from tools.eos.legal_operations.domain.legal_work_completion_event import (
    LegalWorkCompletionEvent,
    LegalWorkCompletionEventError,
)


VERSION: Final[str] = (
    "v1.0.0-P14-R14-WORK-COMPLETION-EVENT-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "legal_work_completion_events"
)

IDENTITY_INDEX_NAME: Final[str] = (
    "legal_work_completion_event_identity_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_work_completion_event_fingerprint_unique"
)

WORK_HISTORY_INDEX_NAME: Final[str] = (
    "legal_work_completion_work_history_unique"
)

MATTER_HISTORY_INDEX_NAME: Final[str] = (
    "legal_work_completion_matter_history"
)

ACTOR_HISTORY_INDEX_NAME: Final[str] = (
    "legal_work_completion_actor_history"
)


class LegalWorkCompletionEventRegistryError(
    RuntimeError
):
    """Base stable completion-event durability failure."""

    def __init__(
        self,
        code: str,
    ) -> None:
        self.code = code
        super().__init__(
            code
        )


class LegalWorkCompletionEventRegistryInputError(
    LegalWorkCompletionEventRegistryError
):
    """Invalid caller input."""


class LegalWorkCompletionEventRegistryTransactionRequiredError(
    LegalWorkCompletionEventRegistryError
):
    """Active caller transaction absent."""


class LegalWorkCompletionEventRegistryConflictError(
    LegalWorkCompletionEventRegistryError
):
    """Immutable completion truth conflicts with durable truth."""


class LegalWorkCompletionEventRegistryNotFoundError(
    LegalWorkCompletionEventRegistryError
):
    """Exact tenant completion event is absent."""


class LegalWorkCompletionEventRegistryPersistedRecordInvalidError(
    LegalWorkCompletionEventRegistryError
):
    """Durable row is malformed or corrupt."""


class LegalWorkCompletionEventRegistryRetryTransactionError(
    LegalWorkCompletionEventRegistryError
):
    """Caller must retry the whole transaction."""


class LegalWorkCompletionEventRegistryPersistenceError(
    LegalWorkCompletionEventRegistryError
):
    """Mongo operation failed."""


def _raise(
    kind: type[
        LegalWorkCompletionEventRegistryError
    ],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = kind(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _tx(
    session: object,
) -> object:
    marker = (
        getattr(
            session,
            "in_transaction",
            None,
        )
        if session is not None
        else None
    )

    try:
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
            LegalWorkCompletionEventRegistryTransactionRequiredError,
            "P14_R14_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalWorkCompletionEventRegistryTransactionRequiredError,
            "P14_R14_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value) > 320
    ):
        _raise(
            LegalWorkCompletionEventRegistryInputError,
            f"P14_R14_{name.upper()}_INVALID",
        )

    return value


def _tenant(
    value: object,
) -> str:
    tenant = _text(
        "tenant_id",
        value,
    )

    if tenant.casefold() in {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }:
        _raise(
            LegalWorkCompletionEventRegistryInputError,
            "P14_R14_TENANT_REQUIRED",
        )

    return tenant


def _hydrate(
    raw: Mapping[
        str,
        object,
    ],
) -> LegalWorkCompletionEvent:
    row = dict(
        raw
    )
    row.pop(
        "_id",
        None,
    )

    try:
        value = (
            LegalWorkCompletionEvent.from_dict(
                row
            )
        )
    except LegalWorkCompletionEventError as error:
        _raise(
            LegalWorkCompletionEventRegistryPersistedRecordInvalidError,
            "P14_R14_PERSISTED_RECORD_INVALID",
            error,
        )

    if value.to_dict() != row:
        _raise(
            LegalWorkCompletionEventRegistryPersistedRecordInvalidError,
            "P14_R14_RECORD_CORRELATION_INVALID",
        )

    return value


def _mongo(
    error: PyMongoError,
) -> NoReturn:
    try:
        transient = (
            error.has_error_label(
                "TransientTransactionError"
            )
        )
    except Exception:
        transient = False

    if transient:
        _raise(
            LegalWorkCompletionEventRegistryRetryTransactionError,
            "P14_R14_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )

    _raise(
        LegalWorkCompletionEventRegistryPersistenceError,
        "P14_R14_PERSISTENCE_FAILURE",
        error,
    )


class LegalWorkCompletionEventRegistry:
    """Append-only exact-tenant completion-event durability."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            _raise(
                LegalWorkCompletionEventRegistryInputError,
                "P14_R14_COLLECTION_REQUIRED",
            )

        self._collection = (
            collection
        )

    def ensure_indexes(
        self,
    ) -> None:
        indexes = (
            (
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "completion_event_id",
                        ASCENDING,
                    ),
                ],
                True,
                IDENTITY_INDEX_NAME,
            ),
            (
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
                True,
                FINGERPRINT_INDEX_NAME,
            ),
            (
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "work_item_id",
                        ASCENDING,
                    ),
                ],
                True,
                WORK_HISTORY_INDEX_NAME,
            ),
            (
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "case_matter_id",
                        ASCENDING,
                    ),
                    (
                        "completed_at",
                        ASCENDING,
                    ),
                    (
                        "completion_event_id",
                        ASCENDING,
                    ),
                ],
                False,
                MATTER_HISTORY_INDEX_NAME,
            ),
            (
                [
                    (
                        "tenant_id",
                        ASCENDING,
                    ),
                    (
                        "actor_principal_id",
                        ASCENDING,
                    ),
                    (
                        "completed_at",
                        ASCENDING,
                    ),
                    (
                        "completion_event_id",
                        ASCENDING,
                    ),
                ],
                False,
                ACTOR_HISTORY_INDEX_NAME,
            ),
        )

        try:
            for (
                keys,
                unique,
                name,
            ) in indexes:
                self._collection.create_index(
                    keys,
                    unique=unique,
                    name=name,
                )
        except AttributeError as error:
            _raise(
                LegalWorkCompletionEventRegistryInputError,
                "P14_R14_COLLECTION_INTERFACE_INVALID",
                error,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

    def create_or_replay(
        self,
        value: LegalWorkCompletionEvent,
        *,
        session: object,
    ) -> LegalWorkCompletionEvent:
        """Persist one immutable completion fact or return exact replay."""
        if type(value) is not LegalWorkCompletionEvent:
            _raise(
                LegalWorkCompletionEventRegistryInputError,
                "P14_R14_COMPLETION_EVENT_REQUIRED",
            )

        tx = _tx(
            session
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id":
                        value.tenant_id,
                    "completion_event_id":
                        value.completion_event_id,
                },
                session=tx,
            )

            if raw is not None:
                persisted = _hydrate(
                    cast(
                        Mapping[str, object],
                        raw,
                    )
                )

                if (
                    hmac.compare_digest(
                        persisted.fingerprint,
                        value.fingerprint,
                    )
                    and persisted == value
                ):
                    return persisted

                _raise(
                    LegalWorkCompletionEventRegistryConflictError,
                    "P14_R14_DIVERGENT_REPLAY",
                )

            existing_work = (
                self._collection.find_one(
                    {
                        "tenant_id":
                            value.tenant_id,
                        "work_item_id":
                            value.work_item_id,
                    },
                    session=tx,
                )
            )

            if existing_work is not None:
                persisted_work = _hydrate(
                    cast(
                        Mapping[str, object],
                        existing_work,
                    )
                )

                if persisted_work == value:
                    return persisted_work

                _raise(
                    LegalWorkCompletionEventRegistryConflictError,
                    "P14_R14_WORK_ALREADY_COMPLETED_DIFFERENTLY",
                )

            collision = (
                self._collection.find_one(
                    {
                        "tenant_id":
                            value.tenant_id,
                        "fingerprint":
                            value.fingerprint,
                    },
                    session=tx,
                )
            )

            if collision is not None:
                _raise(
                    LegalWorkCompletionEventRegistryConflictError,
                    "P14_R14_FINGERPRINT_COLLISION",
                )

            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )

        except DuplicateKeyError as error:
            _raise(
                LegalWorkCompletionEventRegistryRetryTransactionError,
                "P14_R14_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except LegalWorkCompletionEventRegistryError:
            raise
        except PyMongoError as error:
            _mongo(
                error
            )

        return value

    def get_by_id(
        self,
        tenant_id: str,
        completion_event_id: str,
        *,
        session: object,
    ) -> LegalWorkCompletionEvent:
        tenant = _tenant(
            tenant_id
        )
        identity = _text(
            "completion_event_id",
            completion_event_id,
        )
        tx = _tx(
            session
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "completion_event_id":
                        identity,
                },
                session=tx,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        if raw is None:
            _raise(
                LegalWorkCompletionEventRegistryNotFoundError,
                "P14_R14_COMPLETION_EVENT_NOT_FOUND",
            )

        value = _hydrate(
            cast(
                Mapping[str, object],
                raw,
            )
        )

        if (
            value.tenant_id
            != tenant
            or value.completion_event_id
            != identity
        ):
            _raise(
                LegalWorkCompletionEventRegistryPersistedRecordInvalidError,
                "P14_R14_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def _list(
        self,
        query: dict[
            str,
            object,
        ],
        *,
        session: object,
    ) -> tuple[
        LegalWorkCompletionEvent,
        ...,
    ]:
        tx = _tx(
            session
        )

        try:
            rows = tuple(
                self._collection.find(
                    query,
                    session=tx,
                ).sort(
                    [
                        (
                            "completed_at",
                            ASCENDING,
                        ),
                        (
                            "completion_event_id",
                            ASCENDING,
                        ),
                    ]
                )
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        values = tuple(
            _hydrate(
                cast(
                    Mapping[str, object],
                    row,
                )
            )
            for row in rows
        )

        tenant = query[
            "tenant_id"
        ]

        if any(
            value.tenant_id
            != tenant
            for value in values
        ):
            _raise(
                LegalWorkCompletionEventRegistryPersistedRecordInvalidError,
                "P14_R14_PERSISTED_SCOPE_MISMATCH",
            )

        return values

    def list_work_history(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkCompletionEvent,
        ...,
    ]:
        return self._list(
            {
                "tenant_id":
                    _tenant(
                        tenant_id
                    ),
                "work_item_id":
                    _text(
                        "work_item_id",
                        work_item_id,
                    ),
            },
            session=session,
        )

    def list_matter_history(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkCompletionEvent,
        ...,
    ]:
        return self._list(
            {
                "tenant_id":
                    _tenant(
                        tenant_id
                    ),
                "case_matter_id":
                    _text(
                        "case_matter_id",
                        case_matter_id,
                    ),
            },
            session=session,
        )

    def list_actor_history(
        self,
        tenant_id: str,
        actor_principal_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkCompletionEvent,
        ...,
    ]:
        return self._list(
            {
                "tenant_id":
                    _tenant(
                        tenant_id
                    ),
                "actor_principal_id":
                    _text(
                        "actor_principal_id",
                        actor_principal_id,
                    ),
            },
            session=session,
        )


__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "LegalWorkCompletionEventRegistry",
    "LegalWorkCompletionEventRegistryError",
    "LegalWorkCompletionEventRegistryInputError",
    "LegalWorkCompletionEventRegistryTransactionRequiredError",
    "LegalWorkCompletionEventRegistryConflictError",
    "LegalWorkCompletionEventRegistryNotFoundError",
    "LegalWorkCompletionEventRegistryPersistedRecordInvalidError",
    "LegalWorkCompletionEventRegistryRetryTransactionError",
    "LegalWorkCompletionEventRegistryPersistenceError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_completion_event_registry.py
# VERSION: v1.0.0-P14-R14-WORK-COMPLETION-EVENT-REGISTRY
# APPEND-ONLY DURABILITY: YES
# TENANT-FIRST: YES
# ACTIVE CALLER TRANSACTION: REQUIRED
# TTL: ABSENT
# MUTABLE CURRENT POINTER: ABSENT
# WORK ITEM MUTATION: NONE
# COMPLETION COMMAND AUTHORITY: NONE
# DEPENDENCY SATISFACTION AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
