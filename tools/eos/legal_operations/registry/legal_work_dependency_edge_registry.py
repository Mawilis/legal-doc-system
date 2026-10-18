"""
TITLE: WILSY OS Legal Work Dependency Edge Registry
VERSION: v1.0.0-P14-R9-WORK-DEPENDENCY-EDGE-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Legal Operations

PURPOSE:
    Persist immutable tenant-scoped runtime dependency edges created from
    certified workflow materialization truth.

DURABILITY:
    Append-only. Exact replay returns the same durable truth. A previously
    bound runtime relation cannot be reinterpreted with new work or receipt
    fingerprint truth.

TRANSACTION BOUNDARY:
    Caller owns an active MongoDB transaction and whole-transaction retry.

AUTHORITY BOUNDARY:
    Persistence/read projection only. This registry does not satisfy a
    dependency, complete/release/block work, assign/supervise principals,
    grant IAM/professional authority, notify, invoke AI, or execute finance.

FINANCIAL AUTHORITY:
    None. Kennel EOS remains exclusive for financial execution.
"""

from __future__ import annotations

from typing import Any, Final, Mapping, NoReturn

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_work_dependency_edge import (
    LegalWorkDependencyEdge,
    LegalWorkDependencyEdgeError,
)


VERSION: Final[str] = (
    "v1.0.0-P14-R9-WORK-DEPENDENCY-EDGE-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "legal_work_dependency_edges"
)

IDENTITY_INDEX_NAME: Final[str] = (
    "legal_work_dependency_edge_identity_unique"
)

RELATION_INDEX_NAME: Final[str] = (
    "legal_work_dependency_edge_relation_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_work_dependency_edge_fingerprint_unique"
)

RECEIPT_INDEX_NAME: Final[str] = (
    "legal_work_dependency_edge_receipt"
)

MATTER_INDEX_NAME: Final[str] = (
    "legal_work_dependency_edge_matter"
)

PREDECESSOR_INDEX_NAME: Final[str] = (
    "legal_work_dependency_edge_predecessor"
)

SUCCESSOR_INDEX_NAME: Final[str] = (
    "legal_work_dependency_edge_successor"
)


class LegalWorkDependencyEdgeRegistryError(
    RuntimeError
):
    """Base immutable dependency-edge registry failure."""


class LegalWorkDependencyEdgeRegistryInputError(
    LegalWorkDependencyEdgeRegistryError
):
    """Caller supplied invalid registry input."""


class LegalWorkDependencyEdgeRegistryTransactionRequiredError(
    LegalWorkDependencyEdgeRegistryError
):
    """Caller did not provide an active transaction."""


class LegalWorkDependencyEdgeRegistryConflictError(
    LegalWorkDependencyEdgeRegistryError
):
    """Immutable dependency-edge identity/relation conflicted."""


class LegalWorkDependencyEdgeRegistryNotFoundError(
    LegalWorkDependencyEdgeRegistryError
):
    """Requested dependency edge does not exist."""


class LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError(
    LegalWorkDependencyEdgeRegistryError
):
    """Persisted edge failed exact hydration/correlation."""


class LegalWorkDependencyEdgeRegistryRetryTransactionError(
    LegalWorkDependencyEdgeRegistryError
):
    """Caller must retry the complete transaction."""


class LegalWorkDependencyEdgeRegistryPersistenceError(
    LegalWorkDependencyEdgeRegistryError
):
    """Unexpected persistence-layer failure."""


def _raise(
    error_type: type[
        LegalWorkDependencyEdgeRegistryError
    ],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(
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
            LegalWorkDependencyEdgeRegistryTransactionRequiredError,
            "P14_R9_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalWorkDependencyEdgeRegistryTransactionRequiredError,
            "P14_R9_ACTIVE_TRANSACTION_REQUIRED",
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 320
    ):
        _raise(
            LegalWorkDependencyEdgeRegistryInputError,
            f"P14_R9_{name.upper()}_INVALID",
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
            LegalWorkDependencyEdgeRegistryInputError,
            "P14_R9_TENANT_REQUIRED",
        )

    return tenant


def _hydrate(
    raw: Mapping[
        str,
        object,
    ],
) -> LegalWorkDependencyEdge:
    row = dict(
        raw
    )

    row.pop(
        "_id",
        None,
    )

    try:
        value = LegalWorkDependencyEdge.from_dict(
            row
        )
    except LegalWorkDependencyEdgeError as error:
        _raise(
            LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
            "P14_R9_PERSISTED_RECORD_INVALID",
            error,
        )

    if value.to_dict() != row:
        _raise(
            LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
            "P14_R9_RECORD_CORRELATION_INVALID",
        )

    return value


def _mongo(
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
            LegalWorkDependencyEdgeRegistryRetryTransactionError,
            "P14_R9_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )

    _raise(
        LegalWorkDependencyEdgeRegistryPersistenceError,
        "P14_R9_PERSISTENCE_FAILURE",
        error,
    )


class LegalWorkDependencyEdgeRegistry:
    """
    Append-only persistence of exact runtime work dependency relations.

    Persistence of an edge does not mean the dependency is satisfied and does
    not represent work completion or mutable blocked state.
    """

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            _raise(
                LegalWorkDependencyEdgeRegistryInputError,
                "P14_R9_COLLECTION_REQUIRED",
            )

        self._collection = collection

    def ensure_indexes(
        self,
    ) -> None:
        """Create tenant-first immutable non-TTL indexes."""
        indexes = (
            (
                [
                    ("tenant_id", 1),
                    ("dependency_edge_id", 1),
                ],
                True,
                IDENTITY_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("source_materialization_receipt_id", 1),
                    ("predecessor_work_item_id", 1),
                    ("successor_work_item_id", 1),
                ],
                True,
                RELATION_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("fingerprint", 1),
                ],
                True,
                FINGERPRINT_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("source_materialization_receipt_id", 1),
                ],
                False,
                RECEIPT_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("case_matter_id", 1),
                ],
                False,
                MATTER_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("predecessor_work_item_id", 1),
                ],
                False,
                PREDECESSOR_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("successor_work_item_id", 1),
                ],
                False,
                SUCCESSOR_INDEX_NAME,
            ),
        )

        try:
            for keys, unique, name in indexes:
                self._collection.create_index(
                    keys,
                    unique=unique,
                    name=name,
                )
        except AttributeError as error:
            _raise(
                LegalWorkDependencyEdgeRegistryInputError,
                "P14_R9_COLLECTION_INTERFACE_INVALID",
                error,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

    def create_or_replay(
        self,
        value: LegalWorkDependencyEdge,
        *,
        session: object,
    ) -> LegalWorkDependencyEdge:
        """
        Insert one edge or return exact replay.

        The structural runtime relation is permanently bound to one exact set
        of receipt/work fingerprints.
        """
        if type(value) is not LegalWorkDependencyEdge:
            _raise(
                LegalWorkDependencyEdgeRegistryInputError,
                "P14_R9_DEPENDENCY_EDGE_REQUIRED",
            )

        tx = _tx(
            session
        )

        relation_query = {
            "tenant_id":
                value.tenant_id,
            "source_materialization_receipt_id":
                value.source_materialization_receipt_id,
            "predecessor_work_item_id":
                value.predecessor_work_item_id,
            "successor_work_item_id":
                value.successor_work_item_id,
        }

        try:
            existing_raw = self._collection.find_one(
                relation_query,
                session=tx,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        if existing_raw is not None:
            existing = _hydrate(
                existing_raw
            )

            if (
                existing.dependency_edge_id
                == value.dependency_edge_id
                and existing.fingerprint
                == value.fingerprint
                and existing == value
            ):
                return existing

            _raise(
                LegalWorkDependencyEdgeRegistryConflictError,
                "P14_R9_DIVERGENT_RELATION_REPLAY",
            )

        identity_query = {
            "tenant_id":
                value.tenant_id,
            "dependency_edge_id":
                value.dependency_edge_id,
        }

        try:
            existing_identity_raw = self._collection.find_one(
                identity_query,
                session=tx,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        if existing_identity_raw is not None:
            existing_identity = _hydrate(
                existing_identity_raw
            )

            if (
                existing_identity.fingerprint
                == value.fingerprint
                and existing_identity == value
            ):
                return existing_identity

            _raise(
                LegalWorkDependencyEdgeRegistryConflictError,
                "P14_R9_DIVERGENT_IDENTITY_REPLAY",
            )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            raced_raw = self._collection.find_one(
                relation_query,
                session=tx,
            )

            if raced_raw is not None:
                raced = _hydrate(
                    raced_raw
                )

                if (
                    raced.dependency_edge_id
                    == value.dependency_edge_id
                    and raced.fingerprint
                    == value.fingerprint
                    and raced == value
                ):
                    return raced

                _raise(
                    LegalWorkDependencyEdgeRegistryConflictError,
                    "P14_R9_DIVERGENT_RELATION_REPLAY",
                    error,
                )

            _raise(
                LegalWorkDependencyEdgeRegistryRetryTransactionError,
                "P14_R9_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except PyMongoError as error:
            _mongo(
                error
            )
        except Exception as error:
            _raise(
                LegalWorkDependencyEdgeRegistryPersistenceError,
                "P14_R9_PERSISTENCE_FAILURE",
                error,
            )

        return self.get_by_id(
            value.tenant_id,
            value.dependency_edge_id,
            session=tx,
        )

    def get_by_id(
        self,
        tenant_id: str,
        dependency_edge_id: str,
        *,
        session: object,
    ) -> LegalWorkDependencyEdge:
        """Return one exact tenant-scoped immutable dependency edge."""
        tx = _tx(
            session
        )
        tenant = _tenant(
            tenant_id
        )
        identity = _text(
            "dependency_edge_id",
            dependency_edge_id,
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "dependency_edge_id":
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
                LegalWorkDependencyEdgeRegistryNotFoundError,
                "P14_R9_DEPENDENCY_EDGE_NOT_FOUND",
            )

        value = _hydrate(
            raw
        )

        if (
            value.tenant_id != tenant
            or value.dependency_edge_id
            != identity
        ):
            _raise(
                LegalWorkDependencyEdgeRegistryPersistedRecordInvalidError,
                "P14_R9_DEPENDENCY_EDGE_SCOPE_MISMATCH",
            )

        return value

    def list_by_receipt(
        self,
        tenant_id: str,
        receipt_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkDependencyEdge,
        ...,
    ]:
        """List exact receipt-emitted dependency edges deterministically."""
        return self._list(
            {
                "tenant_id":
                    _tenant(
                        tenant_id
                    ),
                "source_materialization_receipt_id":
                    _text(
                        "receipt_id",
                        receipt_id,
                    ),
            },
            session=session,
        )

    def list_predecessors(
        self,
        tenant_id: str,
        successor_work_item_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkDependencyEdge,
        ...,
    ]:
        """List dependency edges required by one successor work item."""
        return self._list(
            {
                "tenant_id":
                    _tenant(
                        tenant_id
                    ),
                "successor_work_item_id":
                    _text(
                        "successor_work_item_id",
                        successor_work_item_id,
                    ),
            },
            session=session,
        )

    def list_successors(
        self,
        tenant_id: str,
        predecessor_work_item_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalWorkDependencyEdge,
        ...,
    ]:
        """List dependency edges emitted from one predecessor work item."""
        return self._list(
            {
                "tenant_id":
                    _tenant(
                        tenant_id
                    ),
                "predecessor_work_item_id":
                    _text(
                        "predecessor_work_item_id",
                        predecessor_work_item_id,
                    ),
            },
            session=session,
        )

    def _list(
        self,
        query: dict[
            str,
            object,
        ],
        *,
        session: object,
    ) -> tuple[
        LegalWorkDependencyEdge,
        ...,
    ]:
        tx = _tx(
            session
        )

        try:
            rows = self._collection.find(
                query,
                session=tx,
            ).sort(
                [
                    (
                        "predecessor_work_item_id",
                        1,
                    ),
                    (
                        "successor_work_item_id",
                        1,
                    ),
                    (
                        "dependency_edge_id",
                        1,
                    ),
                ]
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        return tuple(
            _hydrate(
                row
            )
            for row in rows
        )


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: legal_work_dependency_edge_registry.py
# VERSION: v1.0.0-P14-R9-WORK-DEPENDENCY-EDGE-REGISTRY
# PERSISTENCE: IMMUTABLE / APPEND ONLY / NON-TTL
# EXACT REPLAY: YES
# SAME RUNTIME RELATION DIVERGENCE: FAIL CLOSED
# TENANT ISOLATION: REQUIRED
# MUTABLE CURRENT POINTER: NONE
# SATISFACTION / COMPLETION AUTHORITY: NONE
# BLOCKED / RELEASE AUTHORITY: NONE
# ASSIGNMENT / SUPERVISION / IAM AUTHORITY: NONE
# NOTIFICATION / AI AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
