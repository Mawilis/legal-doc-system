"""
TITLE: WILSY OS Legal Work Assignment Registry

VERSION: v1.0.0-AS-P2-LEGAL-WORK-ASSIGNMENT-REGISTRY

EPITOME:
    Persist immutable Legal work-assignment history and derive one exact
    current assignment from strict successor lineage without storing a
    mutable current pointer.

AUTHORITY BOUNDARY:
    Persistence and currentness only. This registry does not authorize work
    assignment, IAM, matter access, workflow transition, supervision,
    professional status, billing, payment, execution or settlement.

CURRENTNESS:
    Derived exclusively from immutable tenant/work-item history.

TRANSACTION BOUNDARY:
    Every read/write requires a caller-owned already-active Mongo transaction.

FINANCIAL POSTURE:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
"""

from __future__ import annotations

import hmac
from collections import defaultdict
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_work_assignment import (
    LegalWorkAssignment,
)


VERSION: Final[str] = (
    "v1.0.0-AS-P2-LEGAL-WORK-ASSIGNMENT-REGISTRY"
)

COLLECTION_NAME: Final[str] = "legal_work_assignments"

ASSIGNMENT_IDENTITY_INDEX_NAME: Final[str] = (
    "legal_work_assignment_tenant_assignment_unique"
)

INITIAL_WORK_ITEM_INDEX_NAME: Final[str] = (
    "legal_work_assignment_tenant_work_initial_unique"
)

PREDECESSOR_INDEX_NAME: Final[str] = (
    "legal_work_assignment_tenant_predecessor_unique"
)

WORK_ITEM_HISTORY_INDEX_NAME: Final[str] = (
    "legal_work_assignment_tenant_work_history"
)

ASSIGNEE_INDEX_NAME: Final[str] = (
    "legal_work_assignment_tenant_assignee_history"
)


class RegistryError(RuntimeError):
    """Base fail-closed Legal work-assignment registry error."""


class RegistryTransactionRequiredError(RegistryError):
    """Caller-owned active Mongo transaction was not supplied."""


class RegistryConflictError(RegistryError):
    """Immutable replay, identity or lineage conflict."""


class RegistryNotFoundError(RegistryError):
    """Exact tenant-scoped durable truth does not exist."""


class RegistryPersistedRecordInvalidError(RegistryError):
    """Persisted assignment history is corrupt or ambiguous."""


class RegistryPersistenceUnavailableError(RegistryError):
    """Persistence operation failed outside a classified conflict."""


def _fail(
    error_type: type[RegistryError],
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(code)

    if cause is None:
        raise error

    raise error from cause


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
    ):
        _fail(
            RegistryConflictError,
            f"AS_P2_{name.upper()}_INVALID",
        )

    return value


def _transaction(
    session: Any,
) -> Any:
    if (
        session is None
        or not bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )
    ):
        _fail(
            RegistryTransactionRequiredError,
            "AS_P2_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )

    return session


def _without_id(
    raw: Any,
) -> dict[str, object]:
    if not isinstance(raw, dict):
        _fail(
            RegistryPersistedRecordInvalidError,
            "AS_P2_PERSISTED_RECORD_INVALID",
        )

    return {
        str(key): value
        for key, value in raw.items()
        if key != "_id"
    }


class LegalWorkAssignmentRegistry:
    """Append-only durable Legal work-assignment history."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create exact uniqueness/read indexes and never TTL."""

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("assignment_id", ASCENDING),
            ],
            unique=True,
            name=ASSIGNMENT_IDENTITY_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("work_item_id", ASCENDING),
            ],
            unique=True,
            partialFilterExpression={
                "supersedes_assignment_id": None,
            },
            name=INITIAL_WORK_ITEM_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("supersedes_assignment_id", ASCENDING),
            ],
            unique=True,
            partialFilterExpression={
                "supersedes_assignment_id": {
                    "$type": "string",
                },
            },
            name=PREDECESSOR_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("work_item_id", ASCENDING),
                ("assigned_at", ASCENDING),
                ("assignment_id", ASCENDING),
            ],
            unique=False,
            name=WORK_ITEM_HISTORY_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("assignee_principal_id", ASCENDING),
                ("assigned_at", ASCENDING),
                ("assignment_id", ASCENDING),
            ],
            unique=False,
            name=ASSIGNEE_INDEX_NAME,
        )

    @staticmethod
    def _hydrate(
        raw: Any,
    ) -> LegalWorkAssignment:
        try:
            return LegalWorkAssignment.from_dict(
                _without_id(raw)
            )
        except Exception as exc:
            raise RegistryPersistedRecordInvalidError(
                "AS_P2_PERSISTED_RECORD_INVALID"
            ) from exc

    @staticmethod
    def _equal(
        left: LegalWorkAssignment,
        right: LegalWorkAssignment,
    ) -> bool:
        return (
            hmac.compare_digest(
                left.fingerprint,
                right.fingerprint,
            )
            and left == right
        )

    @staticmethod
    def _validate_history(
        values: tuple[
            LegalWorkAssignment,
            ...
        ],
    ) -> tuple[
        LegalWorkAssignment,
        ...
    ]:
        if not values:
            return ()

        tenant = values[0].tenant_id
        work_item = values[0].work_item_id
        matter = values[0].case_matter_id

        by_id: dict[
            str,
            LegalWorkAssignment,
        ] = {}

        children: dict[
            str,
            list[LegalWorkAssignment],
        ] = defaultdict(list)

        roots: list[
            LegalWorkAssignment
        ] = []

        for value in values:
            if (
                value.tenant_id != tenant
                or value.work_item_id != work_item
                or value.case_matter_id != matter
            ):
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_LINEAGE_SCOPE_MISMATCH",
                )

            if value.assignment_id in by_id:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_DUPLICATE_ASSIGNMENT_ID",
                )

            by_id[value.assignment_id] = value

            if (
                value.supersedes_assignment_id
                is None
            ):
                roots.append(value)
            else:
                children[
                    value.supersedes_assignment_id
                ].append(value)

        if len(roots) != 1:
            _fail(
                RegistryPersistedRecordInvalidError,
                "AS_P2_INITIAL_ASSIGNMENT_AMBIGUOUS",
            )

        for predecessor_id, successors in children.items():
            if predecessor_id not in by_id:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_PREDECESSOR_NOT_FOUND",
                )

            if len(successors) != 1:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_BRANCHED_HISTORY",
                )

        ordered: list[
            LegalWorkAssignment
        ] = []

        seen: set[str] = set()

        current = roots[0]

        while True:
            if current.assignment_id in seen:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_CYCLIC_HISTORY",
                )

            seen.add(
                current.assignment_id
            )
            ordered.append(current)

            successors = children.get(
                current.assignment_id,
                [],
            )

            if not successors:
                break

            successor = successors[0]

            if (
                successor.assigned_at
                <= current.assigned_at
            ):
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_ASSIGNED_AT_NOT_INCREASING",
                )

            current = successor

        if len(seen) != len(values):
            _fail(
                RegistryPersistedRecordInvalidError,
                "AS_P2_DISCONNECTED_HISTORY",
            )

        return tuple(ordered)

    def get_by_assignment_id(
        self,
        tenant_id: str,
        assignment_id: str,
        *,
        session: Any,
    ) -> LegalWorkAssignment:
        """Return one exact immutable assignment."""

        tx = _transaction(session)
        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        identity = _text(
            "assignment_id",
            assignment_id,
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "assignment_id": identity,
                },
                session=tx,
            )
        except PyMongoError as exc:
            _fail(
                RegistryPersistenceUnavailableError,
                "AS_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        if raw is None:
            _fail(
                RegistryNotFoundError,
                "AS_P2_ASSIGNMENT_NOT_FOUND",
            )

        value = self._hydrate(raw)

        if (
            value.tenant_id != tenant
            or value.assignment_id != identity
        ):
            _fail(
                RegistryPersistedRecordInvalidError,
                "AS_P2_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def get_history_if_any(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkAssignment,
        ...
    ]:
        """Return complete immutable lineage or empty tuple."""

        tx = _transaction(session)

        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        work_item = _text(
            "work_item_id",
            work_item_id,
        )

        try:
            rows = tuple(
                self._collection.find(
                    {
                        "tenant_id": tenant,
                        "work_item_id": work_item,
                    },
                    session=tx,
                )
            )
        except PyMongoError as exc:
            _fail(
                RegistryPersistenceUnavailableError,
                "AS_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        values = tuple(
            self._hydrate(raw)
            for raw in rows
        )

        for value in values:
            if (
                value.tenant_id != tenant
                or value.work_item_id != work_item
            ):
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_PERSISTED_SCOPE_MISMATCH",
                )

        return self._validate_history(
            values
        )

    def get_history(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkAssignment,
        ...
    ]:
        """Return immutable assignment history and reject absence."""

        history = self.get_history_if_any(
            tenant_id,
            work_item_id,
            session=session,
        )

        if not history:
            _fail(
                RegistryNotFoundError,
                "AS_P2_HISTORY_NOT_FOUND",
            )

        return history

    def resolve_current(
        self,
        tenant_id: str,
        work_item_id: str,
        *,
        session: Any,
    ) -> LegalWorkAssignment | None:
        """Derive current assignment from immutable lineage."""

        history = self.get_history_if_any(
            tenant_id,
            work_item_id,
            session=session,
        )

        if not history:
            return None

        return history[-1]

    def persist(
        self,
        value: LegalWorkAssignment,
        *,
        session: Any,
    ) -> LegalWorkAssignment:
        """Append initial assignment or exact next reassignment."""

        tx = _transaction(session)

        if not isinstance(
            value,
            LegalWorkAssignment,
        ):
            _fail(
                RegistryConflictError,
                "AS_P2_DOMAIN_VALUE_REQUIRED",
            )

        identity_query = {
            "tenant_id": value.tenant_id,
            "assignment_id": value.assignment_id,
        }

        try:
            existing_raw = (
                self._collection.find_one(
                    identity_query,
                    session=tx,
                )
            )
        except PyMongoError as exc:
            _fail(
                RegistryPersistenceUnavailableError,
                "AS_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        if existing_raw is not None:
            existing = self._hydrate(
                existing_raw
            )

            if self._equal(
                existing,
                value,
            ):
                return existing

            _fail(
                RegistryConflictError,
                "AS_P2_DIVERGENT_REPLAY",
            )

        history = self.get_history_if_any(
            value.tenant_id,
            value.work_item_id,
            session=tx,
        )

        if not history:
            if (
                value.supersedes_assignment_id
                is not None
            ):
                _fail(
                    RegistryConflictError,
                    "AS_P2_INITIAL_ASSIGNMENT_SUPERSEDES",
                )
        else:
            current = history[-1]

            if (
                value.case_matter_id
                != current.case_matter_id
            ):
                _fail(
                    RegistryConflictError,
                    "AS_P2_LINEAGE_SCOPE_MISMATCH",
                )

            if (
                value.supersedes_assignment_id
                != current.assignment_id
            ):
                _fail(
                    RegistryConflictError,
                    "AS_P2_STALE_PREDECESSOR",
                )

            if (
                value.assigned_at
                <= current.assigned_at
            ):
                _fail(
                    RegistryConflictError,
                    "AS_P2_ASSIGNED_AT_NOT_INCREASING",
                )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError:
            raced_raw = (
                self._collection.find_one(
                    identity_query,
                    session=tx,
                )
            )

            if raced_raw is not None:
                raced = self._hydrate(
                    raced_raw
                )

                if self._equal(
                    raced,
                    value,
                ):
                    return raced

            _fail(
                RegistryConflictError,
                "AS_P2_COMPETING_ASSIGNMENT_CONFLICT",
            )
        except PyMongoError as exc:
            _fail(
                RegistryPersistenceUnavailableError,
                "AS_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        return self.get_by_assignment_id(
            value.tenant_id,
            value.assignment_id,
            session=tx,
        )

    def list_current_for_assignee(
        self,
        tenant_id: str,
        principal_id: str,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkAssignment,
        ...
    ]:
        """Return only current assignments owned by one principal."""

        tx = _transaction(session)

        tenant = _text(
            "tenant_id",
            tenant_id,
        )
        principal = _text(
            "principal_id",
            principal_id,
        )

        try:
            rows = tuple(
                self._collection.find(
                    {
                        "tenant_id": tenant,
                    },
                    session=tx,
                )
            )
        except PyMongoError as exc:
            _fail(
                RegistryPersistenceUnavailableError,
                "AS_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        values = tuple(
            self._hydrate(raw)
            for raw in rows
        )

        grouped: dict[
            str,
            list[LegalWorkAssignment],
        ] = defaultdict(list)

        for value in values:
            if value.tenant_id != tenant:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "AS_P2_PERSISTED_SCOPE_MISMATCH",
                )

            grouped[
                value.work_item_id
            ].append(value)

        selected: list[
            LegalWorkAssignment
        ] = []

        for work_item_id in sorted(grouped):
            history = self._validate_history(
                tuple(grouped[work_item_id])
            )

            if (
                history
                and history[-1].assignee_principal_id
                == principal
            ):
                selected.append(
                    history[-1]
                )

        return tuple(
            sorted(
                selected,
                key=lambda item: (
                    item.assigned_at,
                    item.work_item_id,
                    item.assignment_id,
                ),
            )
        )


__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "ASSIGNMENT_IDENTITY_INDEX_NAME",
    "INITIAL_WORK_ITEM_INDEX_NAME",
    "PREDECESSOR_INDEX_NAME",
    "WORK_ITEM_HISTORY_INDEX_NAME",
    "ASSIGNEE_INDEX_NAME",
    "LegalWorkAssignmentRegistry",
    "RegistryError",
    "RegistryTransactionRequiredError",
    "RegistryConflictError",
    "RegistryNotFoundError",
    "RegistryPersistedRecordInvalidError",
    "RegistryPersistenceUnavailableError",
]

# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: legal_work_assignment_registry.py
# APPEND-ONLY IMMUTABLE HISTORY: YES
# CURRENTNESS: DERIVED FROM IMMUTABLE LINEAGE
# MUTABLE CURRENT POINTER: NONE
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# UPDATE / REPLACE / DELETE AUTHORITY: NONE
# IAM AUTHORITY: NONE
# SUPERVISION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# ==============================================================================
