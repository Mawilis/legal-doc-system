"""
WILSY OS — Legal Transition Work Materialization Receipt Registry

TITLE:
    Immutable Transition-to-Work Materialization Receipt Registry

VERSION:
    v1.0.0-P14-P14-TRANSITION-WORK-MATERIALIZATION-RECEIPT-REGISTRY

PURPOSE:
    Persist immutable historical evidence binding one exact tenant-scoped
    workflow transition to one exact transition-work materialization receipt.

DURABILITY:
    One tenant+transition has exactly one immutable receipt. Exact replay
    returns the same durable truth. Divergent policy/output reinterpretation
    fails closed. Persistence is insert-only and non-TTL.

TENANT BOUNDARY:
    Every durable identity and read predicate begins with exact tenant scope.

TRANSACTION BOUNDARY:
    Caller owns an active transaction and whole-transaction retry.

PERSISTENCE BOUNDARY:
    MongoDB storage metadata ``_id`` is removed from a copy immediately before
    strict receipt-domain hydration. No arbitrary persisted field is ignored.

AUTHORITY BOUNDARY:
    Persistence and read projection only. This registry selects no policy,
    creates no work item, assigns or supervises no principal, grants no IAM or
    professional authority, calculates no legal deadline, delivers no
    notification, invokes no AI, and performs no financial action.

COMPETITIVE POSTURE:
    Historical stage-trigger automation is durably replay-locked so later
    mutable configuration cannot reinterpret transition→policy→work history.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive for financial execution.

FAIL-CLOSED DECLARATION:
    Inactive transactions, divergent transition replay, identity/fingerprint
    collision, malformed persisted truth or cross-tenant scope rejects.
"""

from __future__ import annotations

from typing import Any, Final, Mapping, NoReturn

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_transition_work_materialization_receipt import (
    LegalTransitionWorkMaterializationReceipt,
    LegalTransitionWorkMaterializationReceiptError,
)


VERSION: Final[str] = (
    "v1.0.0-P14-P14-"
    "TRANSITION-WORK-MATERIALIZATION-RECEIPT-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "legal_transition_work_materialization_receipts"
)

IDENTITY_INDEX_NAME: Final[str] = (
    "legal_transition_work_materialization_receipt_identity_unique"
)

TRANSITION_INDEX_NAME: Final[str] = (
    "legal_transition_work_materialization_receipt_transition_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "legal_transition_work_materialization_receipt_fingerprint_unique"
)

MATTER_INDEX_NAME: Final[str] = (
    "legal_transition_work_materialization_receipt_matter"
)

POLICY_INDEX_NAME: Final[str] = (
    "legal_transition_work_materialization_receipt_policy"
)


class LegalTransitionWorkMaterializationReceiptRegistryError(
    RuntimeError
):
    """Base immutable receipt-registry failure."""


class LegalTransitionWorkMaterializationReceiptRegistryInputError(
    LegalTransitionWorkMaterializationReceiptRegistryError
):
    """Caller supplied invalid registry input."""


class LegalTransitionWorkMaterializationReceiptRegistryTransactionRequiredError(
    LegalTransitionWorkMaterializationReceiptRegistryError
):
    """Caller did not supply an active transaction."""


class LegalTransitionWorkMaterializationReceiptRegistryConflictError(
    LegalTransitionWorkMaterializationReceiptRegistryError
):
    """Immutable receipt identity or transition replay conflicted."""


class LegalTransitionWorkMaterializationReceiptRegistryNotFoundError(
    LegalTransitionWorkMaterializationReceiptRegistryError
):
    """Requested immutable receipt was not found."""


class LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError(
    LegalTransitionWorkMaterializationReceiptRegistryError
):
    """Persisted row failed exact receipt hydration/correlation."""


class LegalTransitionWorkMaterializationReceiptRegistryRetryTransactionError(
    LegalTransitionWorkMaterializationReceiptRegistryError
):
    """Caller must retry the complete transaction."""


class LegalTransitionWorkMaterializationReceiptRegistryPersistenceError(
    LegalTransitionWorkMaterializationReceiptRegistryError
):
    """Unexpected persistence-layer failure."""


def _raise(
    error_type: type[
        LegalTransitionWorkMaterializationReceiptRegistryError
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
            LegalTransitionWorkMaterializationReceiptRegistryTransactionRequiredError,
            "P14_P14_ACTIVE_TRANSACTION_REQUIRED",
            error,
        )

    if active is not True:
        _raise(
            LegalTransitionWorkMaterializationReceiptRegistryTransactionRequiredError,
            "P14_P14_ACTIVE_TRANSACTION_REQUIRED",
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
            LegalTransitionWorkMaterializationReceiptRegistryInputError,
            f"P14_P14_{name.upper()}_INVALID",
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
            LegalTransitionWorkMaterializationReceiptRegistryInputError,
            "P14_P14_TENANT_REQUIRED",
        )

    return tenant


def _revision(
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        _raise(
            LegalTransitionWorkMaterializationReceiptRegistryInputError,
            "P14_P14_POLICY_REVISION_INVALID",
        )

    return value


def _hydrate(
    raw: Mapping[str, object],
) -> LegalTransitionWorkMaterializationReceipt:
    row = dict(
        raw
    )

    row.pop(
        "_id",
        None,
    )

    try:
        value = LegalTransitionWorkMaterializationReceipt.from_dict(
            row
        )
    except (
        LegalTransitionWorkMaterializationReceiptError,
        TypeError,
        ValueError,
        KeyError,
    ) as error:
        _raise(
            LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
            "P14_P14_PERSISTED_RECORD_INVALID",
            error,
        )

    if value.to_dict() != row:
        _raise(
            LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
            "P14_P14_RECORD_CORRELATION_INVALID",
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
            LegalTransitionWorkMaterializationReceiptRegistryRetryTransactionError,
            "P14_P14_WHOLE_TRANSACTION_RETRY_REQUIRED",
            error,
        )

    _raise(
        LegalTransitionWorkMaterializationReceiptRegistryPersistenceError,
        "P14_P14_PERSISTENCE_FAILURE",
        error,
    )


class LegalTransitionWorkMaterializationReceiptRegistry:
    """
    Append-only durability for transition-work materialization receipts.

    One tenant+transition is permanently bound to one immutable receipt.
    """

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryInputError,
                "P14_P14_COLLECTION_REQUIRED",
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
                    ("receipt_id", 1),
                ],
                True,
                IDENTITY_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("transition_id", 1),
                ],
                True,
                TRANSITION_INDEX_NAME,
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
                    ("case_matter_id", 1),
                ],
                False,
                MATTER_INDEX_NAME,
            ),
            (
                [
                    ("tenant_id", 1),
                    ("policy_id", 1),
                    ("policy_revision", 1),
                ],
                False,
                POLICY_INDEX_NAME,
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
                LegalTransitionWorkMaterializationReceiptRegistryInputError,
                "P14_P14_COLLECTION_INTERFACE_INVALID",
                error,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

    def create_or_replay(
        self,
        value: LegalTransitionWorkMaterializationReceipt,
        *,
        session: object,
    ) -> LegalTransitionWorkMaterializationReceipt:
        """
        Insert one immutable receipt or return one exact durable replay.

        Same tenant+transition with any different receipt semantics fails
        closed and can never adopt a newer policy revision or output set.
        """
        if (
            type(value)
            is not LegalTransitionWorkMaterializationReceipt
        ):
            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryInputError,
                "P14_P14_RECEIPT_REQUIRED",
            )

        tx = _tx(
            session
        )

        transition_query = {
            "tenant_id":
                value.tenant_id,
            "transition_id":
                value.transition_id,
        }

        try:
            existing_raw = self._collection.find_one(
                transition_query,
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
                existing.receipt_id == value.receipt_id
                and existing.fingerprint == value.fingerprint
                and existing == value
            ):
                return existing

            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryConflictError,
                "P14_P14_DIVERGENT_TRANSITION_REPLAY",
            )

        receipt_query = {
            "tenant_id":
                value.tenant_id,
            "receipt_id":
                value.receipt_id,
        }

        try:
            existing_receipt_raw = self._collection.find_one(
                receipt_query,
                session=tx,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        if existing_receipt_raw is not None:
            existing_receipt = _hydrate(
                existing_receipt_raw
            )

            if (
                existing_receipt.transition_id
                == value.transition_id
                and existing_receipt.fingerprint
                == value.fingerprint
                and existing_receipt == value
            ):
                return existing_receipt

            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryConflictError,
                "P14_P14_DIVERGENT_RECEIPT_REPLAY",
            )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError as error:
            raced_raw = self._collection.find_one(
                transition_query,
                session=tx,
            )

            if raced_raw is not None:
                raced = _hydrate(
                    raced_raw
                )

                if (
                    raced.receipt_id == value.receipt_id
                    and raced.fingerprint == value.fingerprint
                    and raced == value
                ):
                    return raced

                _raise(
                    LegalTransitionWorkMaterializationReceiptRegistryConflictError,
                    "P14_P14_DIVERGENT_TRANSITION_REPLAY",
                    error,
                )

            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryRetryTransactionError,
                "P14_P14_DUPLICATE_RACE_RETRY_TRANSACTION",
                error,
            )
        except PyMongoError as error:
            _mongo(
                error
            )
        except Exception as error:
            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryPersistenceError,
                "P14_P14_PERSISTENCE_FAILURE",
                error,
            )

        return self.get_by_transition_id(
            value.tenant_id,
            value.transition_id,
            session=tx,
        )

    def get_by_receipt_id(
        self,
        tenant_id: str,
        receipt_id: str,
        *,
        session: object,
    ) -> LegalTransitionWorkMaterializationReceipt:
        """Return one exact tenant-scoped receipt identity."""
        tx = _tx(
            session
        )

        tenant = _tenant(
            tenant_id
        )
        identity = _text(
            "receipt_id",
            receipt_id,
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "receipt_id":
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
                LegalTransitionWorkMaterializationReceiptRegistryNotFoundError,
                "P14_P14_RECEIPT_NOT_FOUND",
            )

        value = _hydrate(
            raw
        )

        if (
            value.tenant_id != tenant
            or value.receipt_id != identity
        ):
            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
                "P14_P14_RECEIPT_SCOPE_MISMATCH",
            )

        return value

    def get_by_transition_id(
        self,
        tenant_id: str,
        transition_id: str,
        *,
        session: object,
    ) -> LegalTransitionWorkMaterializationReceipt:
        """Return the sole immutable receipt for one tenant transition."""
        tx = _tx(
            session
        )

        tenant = _tenant(
            tenant_id
        )
        transition = _text(
            "transition_id",
            transition_id,
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id":
                        tenant,
                    "transition_id":
                        transition,
                },
                session=tx,
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        if raw is None:
            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryNotFoundError,
                "P14_P14_TRANSITION_RECEIPT_NOT_FOUND",
            )

        value = _hydrate(
            raw
        )

        if (
            value.tenant_id != tenant
            or value.transition_id != transition
        ):
            _raise(
                LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
                "P14_P14_TRANSITION_SCOPE_MISMATCH",
            )

        return value

    def list_matter(
        self,
        tenant_id: str,
        case_matter_id: str,
        *,
        session: object,
    ) -> tuple[
        LegalTransitionWorkMaterializationReceipt,
        ...,
    ]:
        """List immutable receipts for one exact tenant matter."""
        tx = _tx(
            session
        )

        tenant = _tenant(
            tenant_id
        )
        matter = _text(
            "case_matter_id",
            case_matter_id,
        )

        try:
            raws = tuple(
                self._collection.find(
                    {
                        "tenant_id":
                            tenant,
                        "case_matter_id":
                            matter,
                    },
                    session=tx,
                )
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        values = tuple(
            sorted(
                (
                    _hydrate(
                        raw
                    )
                    for raw in raws
                ),
                key=lambda item: (
                    item.materialized_at,
                    item.transition_id,
                    item.receipt_id,
                ),
            )
        )

        for value in values:
            if (
                value.tenant_id != tenant
                or value.case_matter_id != matter
            ):
                _raise(
                    LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
                    "P14_P14_MATTER_SCOPE_MISMATCH",
                )

        return values

    def list_policy_revision(
        self,
        tenant_id: str,
        policy_id: str,
        policy_revision: int,
        *,
        session: object,
    ) -> tuple[
        LegalTransitionWorkMaterializationReceipt,
        ...,
    ]:
        """List receipts bound to one exact immutable policy revision."""
        tx = _tx(
            session
        )

        tenant = _tenant(
            tenant_id
        )
        policy = _text(
            "policy_id",
            policy_id,
        )
        revision = _revision(
            policy_revision
        )

        try:
            raws = tuple(
                self._collection.find(
                    {
                        "tenant_id":
                            tenant,
                        "policy_id":
                            policy,
                        "policy_revision":
                            revision,
                    },
                    session=tx,
                )
            )
        except PyMongoError as error:
            _mongo(
                error
            )

        values = tuple(
            sorted(
                (
                    _hydrate(
                        raw
                    )
                    for raw in raws
                ),
                key=lambda item: (
                    item.materialized_at,
                    item.transition_id,
                    item.receipt_id,
                ),
            )
        )

        for value in values:
            if (
                value.tenant_id != tenant
                or value.policy_id != policy
                or value.policy_revision != revision
            ):
                _raise(
                    LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError,
                    "P14_P14_POLICY_SCOPE_MISMATCH",
                )

        return values


__all__ = [
    "COLLECTION_NAME",
    "FINGERPRINT_INDEX_NAME",
    "IDENTITY_INDEX_NAME",
    "MATTER_INDEX_NAME",
    "POLICY_INDEX_NAME",
    "TRANSITION_INDEX_NAME",
    "VERSION",
    "LegalTransitionWorkMaterializationReceiptRegistry",
    "LegalTransitionWorkMaterializationReceiptRegistryConflictError",
    "LegalTransitionWorkMaterializationReceiptRegistryError",
    "LegalTransitionWorkMaterializationReceiptRegistryInputError",
    "LegalTransitionWorkMaterializationReceiptRegistryNotFoundError",
    "LegalTransitionWorkMaterializationReceiptRegistryPersistedRecordInvalidError",
    "LegalTransitionWorkMaterializationReceiptRegistryPersistenceError",
    "LegalTransitionWorkMaterializationReceiptRegistryRetryTransactionError",
    "LegalTransitionWorkMaterializationReceiptRegistryTransactionRequiredError",
]


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_transition_work_materialization_receipt_registry.py
# VERSION: v1.0.0-P14-P14-TRANSITION-WORK-MATERIALIZATION-RECEIPT-REGISTRY
# AUTHORITY BOUNDARY: immutable receipt persistence/read projection only
# ONE TENANT+TRANSITION / ONE RECEIPT: YES
# EXACT REPLAY: YES
# DIVERGENT POLICY / OUTPUT REPLAY: FAIL CLOSED
# MONGO _id NORMALIZATION: exact persistence boundary only
# TTL / UPDATE / REPLACE / DELETE / UPSERT: NONE
# MUTABLE CURRENT POINTER: NONE
# POLICY SELECTION AUTHORITY: NONE
# WORK-ITEM CREATION AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# IAM / PROFESSIONAL AUTHORITY: NONE
# LEGAL-DEADLINE AUTHORITY: NONE
# NOTIFICATION-DELIVERY AUTHORITY: NONE
# AI EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
