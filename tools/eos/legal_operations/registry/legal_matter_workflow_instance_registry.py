"""TITLE: WILSY OS Legal Matter Workflow Instance Registry.

VERSION: v1.0.1-G7G-R14-LEGAL-MATTER-WORKFLOW-INSTANCE-REGISTRY

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations.

EPITOME:
    Persist, hydrate, exact-replay and read immutable
    LegalMatterWorkflowInstance evidence under exact tenant boundaries.

TRANSACTION BOUNDARY:
    Every operational read/write method requires one caller-owned already-active
    Mongo transaction.

    This registry never starts, commits, aborts or retries a transaction.

PERSISTENCE MODEL:
    - tenant + workflow_instance_id is uniquely durable;
    - tenant + immutable fingerprint is uniquely durable;
    - one matter may have multiple workflow instances;
    - create returns exact same-identity replay;
    - same identity with divergent fingerprint rejects;
    - duplicate races require whole-transaction retry;
    - persisted corruption rejects fail closed;
    - no TTL deletion.

AUTHORITY BOUNDARY:
    This registry does not create or re-evaluate workflow activation, IAM,
    progression, current stage, transition authority, gate satisfaction, work
    generation, assignment, supervision, Legal-event truth, commercial
    entitlement or financial execution.
"""
from __future__ import annotations

from collections.abc import Mapping
import hmac
from typing import Any, Final, NoReturn, cast

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_matter_workflow_instance import (
    LegalMatterWorkflowInstance,
)


VERSION: Final[str] = (
    "v1.0.1-G7G-R14-LEGAL-MATTER-WORKFLOW-INSTANCE-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "legal_matter_workflow_instances"
)

IDENTITY_INDEX_NAME: Final[str] = (
    "legal_matter_workflow_instance_identity_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_matter_workflow_instance_fingerprint_unique"
)

MATTER_HISTORY_INDEX_NAME: Final[str] = (
    "legal_matter_workflow_instance_matter_history"
)

DEFINITION_HISTORY_INDEX_NAME: Final[str] = (
    "legal_matter_workflow_instance_definition_history"
)


class LegalMatterWorkflowInstanceRegistryError(RuntimeError):
    """Base stable registry failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalMatterWorkflowInstanceRegistryInputError(
    LegalMatterWorkflowInstanceRegistryError
):
    """Caller supplied malformed registry input."""


class LegalMatterWorkflowInstanceRegistryTransactionRequiredError(
    LegalMatterWorkflowInstanceRegistryError
):
    """Caller omitted one already-active Mongo transaction."""


class LegalMatterWorkflowInstanceRegistryConflictError(
    LegalMatterWorkflowInstanceRegistryError
):
    """Immutable identity or replay semantics conflict."""


class LegalMatterWorkflowInstanceRegistryNotFoundError(
    LegalMatterWorkflowInstanceRegistryError
):
    """Requested workflow instance is absent."""


class LegalMatterWorkflowInstanceRegistryPersistedRecordInvalidError(
    LegalMatterWorkflowInstanceRegistryError
):
    """Durable record failed strict domain hydration."""


class LegalMatterWorkflowInstanceRegistryRetryTransactionError(
    LegalMatterWorkflowInstanceRegistryError
):
    """Caller must abort and retry the complete transaction."""


class LegalMatterWorkflowInstanceRegistryPersistenceError(
    LegalMatterWorkflowInstanceRegistryError
):
    """Mongo persistence/read failed without safe classification."""


def _raise(
    error_type: type[LegalMatterWorkflowInstanceRegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)
    if cause is None:
        raise error
    raise error from cause


def _require_transaction(session: object) -> object:
    """Require one caller-owned already-active transaction."""
    if session is None:
        _raise(
            LegalMatterWorkflowInstanceRegistryTransactionRequiredError,
            "G7G_R14_ACTIVE_TRANSACTION_REQUIRED",
        )

    try:
        active = bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )
    except Exception as error:
        _raise(
            LegalMatterWorkflowInstanceRegistryTransactionRequiredError,
            "G7G_R14_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if not active:
        _raise(
            LegalMatterWorkflowInstanceRegistryTransactionRequiredError,
            "G7G_R14_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _identifier(
    name: str,
    value: object,
) -> str:
    if not isinstance(value, str):
        _raise(
            LegalMatterWorkflowInstanceRegistryInputError,
            f"G7G_R14_{name.upper()}_INVALID",
        )

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or len(normalized) > 320
    ):
        _raise(
            LegalMatterWorkflowInstanceRegistryInputError,
            f"G7G_R14_{name.upper()}_INVALID",
        )

    return normalized


def _tenant(value: object) -> str:
    tenant = _identifier(
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
            LegalMatterWorkflowInstanceRegistryInputError,
            "G7G_R14_TENANT_REQUIRED",
        )

    return tenant


def _document(
    value: LegalMatterWorkflowInstance,
) -> dict[str, object]:
    return dict(
        value.to_dict()
    )


def _canonical_row(
    raw: Mapping[str, object],
) -> dict[str, object]:
    row = dict(raw)
    row.pop("_id", None)
    return row


def _hydrate(
    raw: Mapping[str, object],
) -> LegalMatterWorkflowInstance:
    try:
        return LegalMatterWorkflowInstance.from_dict(
            _canonical_row(raw)
        )
    except Exception as error:
        _raise(
            LegalMatterWorkflowInstanceRegistryPersistedRecordInvalidError,
            "G7G_R14_PERSISTED_RECORD_INVALID",
            error,
        )


def _same(
    left: LegalMatterWorkflowInstance,
    right: LegalMatterWorkflowInstance,
) -> bool:
    return hmac.compare_digest(
        left.fingerprint,
        right.fingerprint,
    )


def _mongo_failure(
    error: PyMongoError,
) -> NoReturn:
    try:
        transient = error.has_error_label(
            "TransientTransactionError"
        )
    except Exception:
        transient = False

    if transient:
        _raise(
            LegalMatterWorkflowInstanceRegistryRetryTransactionError,
            "G7G_R14_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )

    _raise(
        LegalMatterWorkflowInstanceRegistryPersistenceError,
        "G7G_R14_PERSISTENCE_FAILURE",
        error,
    )


class LegalMatterWorkflowInstanceRegistry:
    """Immutable tenant-scoped workflow-instance persistence."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            _raise(
                LegalMatterWorkflowInstanceRegistryInputError,
                "G7G_R14_COLLECTION_REQUIRED",
            )
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create exact governed non-TTL indexes."""
        try:
            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    (
                        "workflow_instance_id",
                        ASCENDING,
                    ),
                ],
                unique=True,
                name=IDENTITY_INDEX_NAME,
            )

            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("fingerprint", ASCENDING),
                ],
                unique=True,
                name=FINGERPRINT_INDEX_NAME,
            )

            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    ("case_matter_id", ASCENDING),
                    ("started_at", ASCENDING),
                    (
                        "workflow_instance_id",
                        ASCENDING,
                    ),
                ],
                unique=False,
                name=MATTER_HISTORY_INDEX_NAME,
            )

            self._collection.create_index(
                [
                    ("tenant_id", ASCENDING),
                    (
                        "workflow_definition_id",
                        ASCENDING,
                    ),
                    ("started_at", ASCENDING),
                    (
                        "workflow_instance_id",
                        ASCENDING,
                    ),
                ],
                unique=False,
                name=DEFINITION_HISTORY_INDEX_NAME,
            )
        except PyMongoError as error:
            _raise(
                LegalMatterWorkflowInstanceRegistryPersistenceError,
                "G7G_R14_INDEX_CREATION_FAILED",
                error,
            )

    def create_or_replay(
        self,
        value: LegalMatterWorkflowInstance,
        *,
        session: object,
    ) -> LegalMatterWorkflowInstance:
        """Insert one immutable instance or return exact durable replay."""
        if not isinstance(
            value,
            LegalMatterWorkflowInstance,
        ):
            _raise(
                LegalMatterWorkflowInstanceRegistryInputError,
                "G7G_R14_INSTANCE_INVALID",
            )

        tx = _require_transaction(
            session
        )

        query = {
            "tenant_id":
                value.tenant_id,
            "workflow_instance_id":
                value.workflow_instance_id,
        }

        try:
            existing = self._collection.find_one(
                query,
                session=tx,
            )

            if existing is not None:
                persisted = _hydrate(
                    cast(
                        Mapping[str, object],
                        existing,
                    )
                )

                if not _same(
                    persisted,
                    value,
                ):
                    _raise(
                        LegalMatterWorkflowInstanceRegistryConflictError,
                        "G7G_R14_DIVERGENT_REPLAY",
                    )

                return persisted

            self._collection.insert_one(
                _document(value),
                session=tx,
            )

        except DuplicateKeyError as error:
            _raise(
                LegalMatterWorkflowInstanceRegistryRetryTransactionError,
                "G7G_R14_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except LegalMatterWorkflowInstanceRegistryError:
            raise
        except PyMongoError as error:
            _mongo_failure(error)

        return value

    def get_by_id(
        self,
        tenant_id: str,
        workflow_instance_id: str,
        *,
        session: object,
    ) -> LegalMatterWorkflowInstance:
        """Read one exact tenant-scoped workflow instance."""
        tenant = _tenant(
            tenant_id
        )

        instance_id = _identifier(
            "workflow_instance_id",
            workflow_instance_id,
        )

        tx = _require_transaction(
            session
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "workflow_instance_id":
                        instance_id,
                },
                session=tx,
            )
        except PyMongoError as error:
            _mongo_failure(error)

        if raw is None:
            _raise(
                LegalMatterWorkflowInstanceRegistryNotFoundError,
                "G7G_R14_INSTANCE_NOT_FOUND",
            )

        value = _hydrate(
            cast(
                Mapping[str, object],
                raw,
            )
        )

        if (
            value.tenant_id != tenant
            or value.workflow_instance_id
            != instance_id
        ):
            _raise(
                LegalMatterWorkflowInstanceRegistryPersistedRecordInvalidError,
                "G7G_R14_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def list_matter_instances(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalMatterWorkflowInstance,
        ...
    ]:
        """Read all immutable workflow instances for one exact matter."""
        tenant = _tenant(
            tenant_id
        )

        matter_id = _identifier(
            "case_matter_id",
            case_matter_id,
        )

        tx = _require_transaction(
            session
        )

        try:
            cursor = self._collection.find(
                {
                    "tenant_id": tenant,
                    "case_matter_id":
                        matter_id,
                },
                session=tx,
            ).sort(
                [
                    ("started_at", ASCENDING),
                    (
                        "workflow_instance_id",
                        ASCENDING,
                    ),
                ]
            )

            rows = tuple(cursor)
        except PyMongoError as error:
            _mongo_failure(error)

        values: list[
            LegalMatterWorkflowInstance
        ] = []

        for raw in rows:
            value = _hydrate(
                cast(
                    Mapping[str, object],
                    raw,
                )
            )

            if (
                value.tenant_id != tenant
                or value.case_matter_id
                != matter_id
            ):
                _raise(
                    LegalMatterWorkflowInstanceRegistryPersistedRecordInvalidError,
                    "G7G_R14_PERSISTED_SCOPE_MISMATCH",
                )

            values.append(value)

        return tuple(values)


def ensure_indexes(
    collection: Any,
) -> None:
    """Create governed instance indexes on one explicit collection."""
    LegalMatterWorkflowInstanceRegistry(
        collection
    ).ensure_indexes()


__all__ = [
    "COLLECTION_NAME",
    "DEFINITION_HISTORY_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "MATTER_HISTORY_INDEX_NAME",
    "VERSION",
    "LegalMatterWorkflowInstanceRegistry",
    "LegalMatterWorkflowInstanceRegistryConflictError",
    "LegalMatterWorkflowInstanceRegistryError",
    "LegalMatterWorkflowInstanceRegistryInputError",
    "LegalMatterWorkflowInstanceRegistryNotFoundError",
    "LegalMatterWorkflowInstanceRegistryPersistedRecordInvalidError",
    "LegalMatterWorkflowInstanceRegistryPersistenceError",
    "LegalMatterWorkflowInstanceRegistryRetryTransactionError",
    "LegalMatterWorkflowInstanceRegistryTransactionRequiredError",
    "ensure_indexes",
]

# ARTIFACT: legal_matter_workflow_instance_registry.py
# VERSION: v1.0.1-G7G-R14-LEGAL-MATTER-WORKFLOW-INSTANCE-REGISTRY
# COLLECTION: legal_matter_workflow_instances
# TTL INDEX: NONE
# MUTABLE CURRENT STAGE AUTHORITY: NONE
# TRANSITION AUTHORITY: NONE
# WORK GENERATION AUTHORITY: NONE
# IAM AUTHORITY: NONE
# COMMERCIAL AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# TRANSACTION POSTURE: caller owns active transaction and whole-transaction retry
# TENANT POSTURE: exact tenant correlation; cross-tenant inference prohibited
# FAIL-CLOSED POSTURE: malformed, incomplete, or divergent evidence rejects
# END OF WILSY OS SOVEREIGN ARTIFACT
