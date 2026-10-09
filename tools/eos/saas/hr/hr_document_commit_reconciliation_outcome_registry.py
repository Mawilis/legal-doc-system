"""WILSY OS HR Commit-Reconciliation Outcome Registry.

TITLE: HR Document Commit-Reconciliation Outcome Registry
VERSION: v1.0.0-P0-C12F6E2-HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Persist exactly one immutable terminal reconciliation outcome for one
tenant-scoped HR document commit uncertainty.

EPITOME:
FROZEN F6E1 OUTCOME
+ CALLER-OWNED ACTIVE MONGO TRANSACTION
-> APPEND-ONCE DURABLE TERMINAL OUTCOME

IDENTITY:
- tenant_id + outcome_id is unique;
- tenant_id + uncertainty_id is unique;
- one uncertainty may acquire exactly one terminal outcome.

TERMINAL OUTCOME RULE:
Exact replay is allowed. A different outcome, timestamp, document binding,
or outcome identity for the same tenant-scoped uncertainty fails closed.

AUTHORITY BOUNDARY:
Immutable outcome persistence only. This registry grants no reconciliation
decision authority, provider IO, provider deletion, orphan determination,
uncertainty mutation, retention/disposal authority, IAM, HTTP, payroll,
billing, payment, settlement or financial execution authority.

TRANSACTION BOUNDARY:
The caller owns the active Mongo session, transaction, commit, abort and
whole-transaction retry. This registry never starts, commits, aborts or
retries transactions.

IMMUTABILITY:
Append-once exact replay only. No update, delete, purge or TTL authority.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_commit_reconciliation_outcome_registry.py

CERTIFICATION / UPDATE DATE: 2026-10-05

CHANGELOG:
2026-10-05 v1.0.0-P0-C12F6E2-HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY
establishes append-once terminal reconciliation-outcome persistence.

FAIL-CLOSED DECLARATION:
Missing/inactive transactions, malformed input, schema drift, fingerprint
corruption, conflicting terminal outcomes, timestamp divergence, duplicate-key
races and Mongo failures reject.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import (
    DuplicateKeyError,
    PyMongoError,
)
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_document_commit_reconciliation_outcome import (
    HrDocumentCommitReconciliationOutcomeError,
    HrDocumentCommitReconciliationOutcomeEvidence,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F6E2-"
    "HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY"
)

COLLECTION: Final[str] = (
    "hr_document_commit_reconciliation_outcomes"
)

OUTCOME_ID_INDEX_NAME: Final[str] = (
    "hr_document_commit_reconciliation_outcome_tenant_identity_unique"
)

UNCERTAINTY_INDEX_NAME: Final[str] = (
    "hr_document_commit_reconciliation_outcome_tenant_uncertainty_unique"
)

RECONCILED_INDEX_NAME: Final[str] = (
    "hr_document_commit_reconciliation_outcome_tenant_reconciled"
)

MAX_TENANT_OUTCOMES: Final[int] = 2000

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(
    w="majority",
    j=True,
)

READ_CONCERN: Final[ReadConcern] = ReadConcern(
    "majority"
)

_OUTCOME_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "outcome_id",
        "tenant_id",
        "uncertainty_id",
        "uncertainty_fingerprint",
        "document_version_id",
        "document_fingerprint",
        "outcome",
        "reconciled_at",
        "schema",
        "outcome_version",
        "fingerprint",
    }
)


class HrDocumentCommitReconciliationOutcomeRegistryError(
    RuntimeError
):
    """Base fail-closed F6E2 registry error."""

    default_code = (
        "P0_C12F6E2_REGISTRY_ERROR"
    )

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = (
            code
            or self.default_code
        )

        super().__init__(
            self.code
        )


class HrDocumentCommitReconciliationOutcomeRegistryInputError(
    HrDocumentCommitReconciliationOutcomeRegistryError
):
    default_code = (
        "P0_C12F6E2_INPUT_INVALID"
    )


class HrDocumentCommitReconciliationOutcomeRegistryTransactionRequiredError(
    HrDocumentCommitReconciliationOutcomeRegistryError
):
    default_code = (
        "P0_C12F6E2_ACTIVE_TRANSACTION_REQUIRED"
    )


class HrDocumentCommitReconciliationOutcomeRegistryNotFoundError(
    HrDocumentCommitReconciliationOutcomeRegistryError
):
    default_code = (
        "P0_C12F6E2_OUTCOME_NOT_FOUND"
    )


class HrDocumentCommitReconciliationOutcomeRegistryConflictError(
    HrDocumentCommitReconciliationOutcomeRegistryError
):
    default_code = (
        "P0_C12F6E2_TERMINAL_OUTCOME_CONFLICT"
    )


class HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError(
    HrDocumentCommitReconciliationOutcomeRegistryError
):
    default_code = (
        "P0_C12F6E2_PERSISTED_RECORD_INVALID"
    )


class HrDocumentCommitReconciliationOutcomeRegistryRetryRequiredError(
    HrDocumentCommitReconciliationOutcomeRegistryError
):
    default_code = (
        "P0_C12F6E2_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


class HrDocumentCommitReconciliationOutcomeRegistryPersistenceUnavailableError(
    HrDocumentCommitReconciliationOutcomeRegistryError
):
    default_code = (
        "P0_C12F6E2_PERSISTENCE_UNAVAILABLE"
    )


def _raise(
    error_type: type[
        HrDocumentCommitReconciliationOutcomeRegistryError
    ],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _raise_mongo(
    error: PyMongoError,
) -> NoReturn:
    if error.has_error_label(
        "TransientTransactionError"
    ):
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryRetryRequiredError,
            cause=error,
        )

    _raise(
        HrDocumentCommitReconciliationOutcomeRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(
    collection: Any,
) -> Any:
    if collection is None:
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryInputError,
            "P0_C12F6E2_COLLECTION_REQUIRED",
        )

    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(
                tz_aware=True,
            ),
        )

    except AttributeError:
        return collection


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryTransactionRequiredError
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(
                marker
            )
            else marker
        )

    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryTransactionRequiredError
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
        or len(
            value
        ) > 2048
    ):
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryInputError,
            f"P0_C12F6E2_{name.upper()}_INVALID",
        )

    return cast(
        str,
        value,
    )


def _serialize(
    value: HrDocumentCommitReconciliationOutcomeEvidence,
) -> dict[str, object]:
    """Serialize exact frozen F6E1 outcome evidence."""

    if (
        type(
            value
        )
        is not HrDocumentCommitReconciliationOutcomeEvidence
    ):
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryInputError,
            "P0_C12F6E2_OUTCOME_REQUIRED",
        )

    document = value.to_dict()

    if (
        set(
            document
        )
        != _OUTCOME_FIELDS
    ):
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
            "P0_C12F6E2_RECORD_SCHEMA_INVALID",
        )

    if any(
        isinstance(
            item,
            (
                bytes,
                bytearray,
                memoryview,
            ),
        )
        for item in document.values()
    ):
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
            "P0_C12F6E2_RAW_BYTES_FORBIDDEN",
        )

    return dict(
        document
    )


def _hydrate(
    row: Mapping[
        str,
        Any,
    ],
) -> HrDocumentCommitReconciliationOutcomeEvidence:
    """Strictly hydrate one persisted F6E1 terminal outcome."""

    try:
        if not isinstance(
            row,
            Mapping,
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError
            )

        persisted = dict(
            row
        )

        persisted.pop(
            "_id",
            None,
        )

        if (
            set(
                persisted
            )
            != _OUTCOME_FIELDS
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
                "P0_C12F6E2_RECORD_SCHEMA_INVALID",
            )

        if any(
            isinstance(
                item,
                (
                    bytes,
                    bytearray,
                    memoryview,
                ),
            )
            for item in persisted.values()
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
                "P0_C12F6E2_RAW_BYTES_FORBIDDEN",
            )

        value = (
            HrDocumentCommitReconciliationOutcomeEvidence.from_dict(
                cast(
                    Mapping[
                        str,
                        object,
                    ],
                    persisted,
                )
            )
        )

        if (
            _serialize(
                value
            )
            != persisted
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
                "P0_C12F6E2_RECORD_CORRELATION_INVALID",
            )

        return value

    except HrDocumentCommitReconciliationOutcomeRegistryError:
        raise

    except (
        KeyError,
        TypeError,
        ValueError,
        HrDocumentCommitReconciliationOutcomeError,
    ) as error:
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
            cause=error,
        )


def ensure_indexes(
    collection: Any,
) -> None:
    """Create exact closed append-only F6E2 indexes."""

    target = _target(
        collection
    )

    try:
        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "outcome_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=OUTCOME_ID_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "uncertainty_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=UNCERTAINTY_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "reconciled_at",
                    DESCENDING,
                ),
                (
                    "outcome_id",
                    ASCENDING,
                ),
            ],
            unique=False,
            name=RECONCILED_INDEX_NAME,
        )

    except PyMongoError as error:
        _raise_mongo(
            error
        )

    except AttributeError as error:
        _raise(
            HrDocumentCommitReconciliationOutcomeRegistryInputError,
            "P0_C12F6E2_COLLECTION_INTERFACE_INVALID",
            error,
        )


class HrDocumentCommitReconciliationOutcomeRegistry:
    """Append-once terminal F6E1 outcome persistence."""

    __slots__ = (
        "_collection",
    )

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = _target(
            collection
        )

    def ensure_indexes(
        self,
    ) -> None:
        """Create exact outcome indexes without TTL."""

        ensure_indexes(
            self._collection
        )

    def create_or_replay(
        self,
        value: HrDocumentCommitReconciliationOutcomeEvidence,
        *,
        session: Any,
    ) -> HrDocumentCommitReconciliationOutcomeEvidence:
        """Persist one terminal outcome or replay the exact same outcome."""

        tx = _active_transaction(
            session
        )

        if (
            type(
                value
            )
            is not HrDocumentCommitReconciliationOutcomeEvidence
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryInputError,
                "P0_C12F6E2_OUTCOME_REQUIRED",
            )

        # Exact outcome identity first.
        try:
            existing_identity = (
                self._collection.find_one(
                    {
                        "tenant_id":
                            value.tenant_id,
                        "outcome_id":
                            value.outcome_id,
                    },
                    session=tx,
                )
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryInputError,
                "P0_C12F6E2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if existing_identity is not None:
            persisted = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    existing_identity,
                )
            )

            if persisted != value:
                _raise(
                    HrDocumentCommitReconciliationOutcomeRegistryConflictError,
                    "P0_C12F6E2_DIVERGENT_OUTCOME_IDENTITY",
                )

            return persisted

        # Terminal lock: one outcome per tenant-scoped uncertainty.
        try:
            existing_uncertainty = (
                self._collection.find_one(
                    {
                        "tenant_id":
                            value.tenant_id,
                        "uncertainty_id":
                            value.uncertainty_id,
                    },
                    session=tx,
                )
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryInputError,
                "P0_C12F6E2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if existing_uncertainty is not None:
            persisted = _hydrate(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    existing_uncertainty,
                )
            )

            if persisted != value:
                _raise(
                    HrDocumentCommitReconciliationOutcomeRegistryConflictError,
                    "P0_C12F6E2_DIVERGENT_TERMINAL_OUTCOME",
                )

            return persisted

        document = _serialize(
            value
        )

        try:
            # PyMongo may add _id to its input mapping.
            self._collection.insert_one(
                dict(
                    document
                ),
                session=tx,
            )

        except DuplicateKeyError as error:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryRetryRequiredError,
                cause=error,
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryInputError,
                "P0_C12F6E2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        return value

    def get_by_uncertainty(
        self,
        *,
        tenant_id: str,
        uncertainty_id: str,
        session: Any,
    ) -> HrDocumentCommitReconciliationOutcomeEvidence:
        """Return the one exact tenant-scoped terminal outcome."""

        tx = _active_transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        uncertainty = _text(
            "uncertainty_id",
            uncertainty_id,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "uncertainty_id":
                        uncertainty,
                },
                session=tx,
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryInputError,
                "P0_C12F6E2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryNotFoundError
            )

        value = _hydrate(
            cast(
                Mapping[
                    str,
                    Any,
                ],
                row,
            )
        )

        if (
            value.tenant_id
            != tenant
            or value.uncertainty_id
            != uncertainty
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
                "P0_C12F6E2_SCOPE_CORRELATION_INVALID",
            )

        return value

    def get_by_outcome_id(
        self,
        *,
        tenant_id: str,
        outcome_id: str,
        session: Any,
    ) -> HrDocumentCommitReconciliationOutcomeEvidence:
        """Return one exact tenant-scoped outcome identity."""

        tx = _active_transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        outcome = _text(
            "outcome_id",
            outcome_id,
        )

        try:
            row = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "outcome_id":
                        outcome,
                },
                session=tx,
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryInputError,
                "P0_C12F6E2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if row is None:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryNotFoundError
            )

        value = _hydrate(
            cast(
                Mapping[
                    str,
                    Any,
                ],
                row,
            )
        )

        if (
            value.tenant_id
            != tenant
            or value.outcome_id
            != outcome
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
                "P0_C12F6E2_SCOPE_CORRELATION_INVALID",
            )

        return value

    def list_tenant_outcomes(
        self,
        *,
        tenant_id: str,
        session: Any,
    ) -> tuple[
        HrDocumentCommitReconciliationOutcomeEvidence,
        ...,
    ]:
        """Return bounded deterministic tenant-scoped outcomes."""

        tx = _active_transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        try:
            cursor = self._collection.find(
                {
                    "tenant_id":
                        tenant,
                },
                session=tx,
            )

            if hasattr(
                cursor,
                "limit",
            ):
                cursor = cursor.limit(
                    MAX_TENANT_OUTCOMES
                    + 1
                )

            rows = tuple(
                cast(
                    Mapping[
                        str,
                        Any,
                    ],
                    row,
                )
                for row in cursor
            )

        except PyMongoError as error:
            _raise_mongo(
                error
            )

        except AttributeError as error:
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryInputError,
                "P0_C12F6E2_COLLECTION_INTERFACE_INVALID",
                error,
            )

        if (
            len(
                rows
            )
            > MAX_TENANT_OUTCOMES
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
                "P0_C12F6E2_TENANT_OUTCOME_LIMIT_EXCEEDED",
            )

        values = tuple(
            _hydrate(
                row
            )
            for row in rows
        )

        if any(
            value.tenant_id
            != tenant
            for value in values
        ):
            _raise(
                HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError,
                "P0_C12F6E2_SCOPE_CORRELATION_INVALID",
            )

        return tuple(
            sorted(
                values,
                key=lambda item: (
                    item.reconciled_at,
                    item.outcome_id,
                ),
                reverse=True,
            )
        )


__all__ = [
    "VERSION",
    "COLLECTION",
    "OUTCOME_ID_INDEX_NAME",
    "UNCERTAINTY_INDEX_NAME",
    "RECONCILED_INDEX_NAME",
    "MAX_TENANT_OUTCOMES",
    "WRITE_CONCERN",
    "READ_CONCERN",
    "HrDocumentCommitReconciliationOutcomeRegistry",
    "HrDocumentCommitReconciliationOutcomeRegistryError",
    "HrDocumentCommitReconciliationOutcomeRegistryInputError",
    "HrDocumentCommitReconciliationOutcomeRegistryTransactionRequiredError",
    "HrDocumentCommitReconciliationOutcomeRegistryNotFoundError",
    "HrDocumentCommitReconciliationOutcomeRegistryConflictError",
    "HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError",
    "HrDocumentCommitReconciliationOutcomeRegistryRetryRequiredError",
    "HrDocumentCommitReconciliationOutcomeRegistryPersistenceUnavailableError",
    "ensure_indexes",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_commit_reconciliation_outcome_registry.py
# VERSION: v1.0.0-P0-C12F6E2-HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY
# AUTHORITY: append-once durable terminal reconciliation-outcome persistence
# ONE OUTCOME PER UNCERTAINTY: mandatory
# EXACT REPLAY: allowed
# DIVERGENT REPLAY: rejected
# TRANSACTION: caller-owned active transaction required
# TTL AUTHORITY: none
# UPDATE/DELETE AUTHORITY: none
# RECONCILIATION DECISION AUTHORITY: none
# PROVIDER IO AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
