"""
TITLE: WILSY OS Legal Work Supervision Binding Registry

VERSION: v1.0.0-SV-P2-LEGAL-WORK-SUPERVISION-BINDING-REGISTRY

EPITOME:
    Persist immutable Legal supervision-binding history and derive effective
    current supervision from strict non-branching lineage without storing a
    mutable current pointer.

AUTHORITY BOUNDARY:
    Persistence/currentness only. This registry does not authorize IAM,
    assignment, professional authority, approval execution, workflow
    transition, billing, payment, execution or settlement.

CURRENTNESS:
    Derived from immutable successor chains plus effective dating.
    Multiple independent supervision chains may coexist.

TRANSACTION BOUNDARY:
    Every read/write requires a caller-owned already-active Mongo transaction.

FINANCIAL POSTURE:
    NONE. Kennel EOS exclusively owns financial execution and settlement.
"""

from __future__ import annotations

import hmac
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Final, NoReturn

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_work_supervision_binding import (
    LegalSupervisionScope,
    LegalWorkSupervisionBinding,
)


VERSION: Final[str] = (
    "v1.0.0-SV-P2-LEGAL-WORK-SUPERVISION-BINDING-REGISTRY"
)

COLLECTION_NAME: Final[str] = (
    "legal_work_supervision_bindings"
)

BINDING_IDENTITY_INDEX_NAME: Final[str] = (
    "legal_work_supervision_tenant_binding_unique"
)

PREDECESSOR_INDEX_NAME: Final[str] = (
    "legal_work_supervision_tenant_predecessor_unique"
)

SUPERVISOR_INDEX_NAME: Final[str] = (
    "legal_work_supervision_tenant_supervisor"
)

SUPERVISEE_INDEX_NAME: Final[str] = (
    "legal_work_supervision_tenant_supervisee"
)

WORK_SCOPE_INDEX_NAME: Final[str] = (
    "legal_work_supervision_tenant_work_scope"
)


class RegistryError(RuntimeError):
    """Base fail-closed Legal supervision registry error."""


class RegistryTransactionRequiredError(RegistryError):
    """Caller-owned active Mongo transaction was not supplied."""


class RegistryConflictError(RegistryError):
    """Immutable replay, identity or lineage conflict."""


class RegistryNotFoundError(RegistryError):
    """Exact tenant-scoped durable truth does not exist."""


class RegistryPersistedRecordInvalidError(RegistryError):
    """Persisted supervision history is corrupt or ambiguous."""


class RegistryPersistenceUnavailableError(RegistryError):
    """Persistence failed outside a classified semantic conflict."""


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
            f"SV_P2_{name.upper()}_INVALID",
        )

    return value


def _moment(
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail(
            RegistryConflictError,
            "SV_P2_AT_INVALID",
        )

    return value.astimezone(
        timezone.utc
    )


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
            "SV_P2_ACTIVE_CALLER_TRANSACTION_REQUIRED",
        )

    return session


def _without_id(
    raw: Any,
) -> dict[str, object]:
    if not isinstance(
        raw,
        dict,
    ):
        _fail(
            RegistryPersistedRecordInvalidError,
            "SV_P2_PERSISTED_RECORD_INVALID",
        )

    return {
        str(key): value
        for key, value in raw.items()
        if key != "_id"
    }


def _scope_token(
    value: LegalWorkSupervisionBinding,
) -> str:
    return LegalSupervisionScope(
        value.scope
    ).value


def _lineage_scope(
    value: LegalWorkSupervisionBinding,
) -> tuple[
    str,
    str,
    str,
    str | None,
    str,
    str,
]:
    return (
        value.tenant_id,
        value.case_matter_id,
        _scope_token(value),
        value.work_item_id,
        value.supervisee_principal_id,
        value.supervisor_principal_id,
    )


class LegalWorkSupervisionBindingRegistry:
    """Append-only durable supervision history with derived currentness."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create uniqueness/read indexes; never create TTL."""

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                (
                    "supervision_binding_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=BINDING_IDENTITY_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                (
                    "supersedes_supervision_binding_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            partialFilterExpression={
                "supersedes_supervision_binding_id": {
                    "$type": "string",
                },
            },
            name=PREDECESSOR_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                (
                    "supervisor_principal_id",
                    ASCENDING,
                ),
                ("effective_from", ASCENDING),
                (
                    "supervision_binding_id",
                    ASCENDING,
                ),
            ],
            unique=False,
            name=SUPERVISOR_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                (
                    "supervisee_principal_id",
                    ASCENDING,
                ),
                ("effective_from", ASCENDING),
                (
                    "supervision_binding_id",
                    ASCENDING,
                ),
            ],
            unique=False,
            name=SUPERVISEE_INDEX_NAME,
        )

        self._collection.create_index(
            [
                ("tenant_id", ASCENDING),
                ("case_matter_id", ASCENDING),
                ("scope", ASCENDING),
                ("work_item_id", ASCENDING),
                ("effective_from", ASCENDING),
            ],
            unique=False,
            name=WORK_SCOPE_INDEX_NAME,
        )

    @staticmethod
    def _hydrate(
        raw: Any,
    ) -> LegalWorkSupervisionBinding:
        try:
            return (
                LegalWorkSupervisionBinding.from_dict(
                    _without_id(raw)
                )
            )
        except Exception as exc:
            raise (
                RegistryPersistedRecordInvalidError(
                    "SV_P2_PERSISTED_RECORD_INVALID"
                )
            ) from exc

    @staticmethod
    def _equal(
        left: LegalWorkSupervisionBinding,
        right: LegalWorkSupervisionBinding,
    ) -> bool:
        return (
            hmac.compare_digest(
                left.fingerprint,
                right.fingerprint,
            )
            and left == right
        )

    @classmethod
    def _validate_chains(
        cls,
        values: tuple[
            LegalWorkSupervisionBinding,
            ...
        ],
    ) -> tuple[
        tuple[
            LegalWorkSupervisionBinding,
            ...
        ],
        ...
    ]:
        """Validate all independent chains and return deterministic lineage."""

        if not values:
            return ()

        by_id: dict[
            str,
            LegalWorkSupervisionBinding,
        ] = {}

        children: dict[
            str,
            list[
                LegalWorkSupervisionBinding
            ],
        ] = defaultdict(list)

        roots: list[
            LegalWorkSupervisionBinding
        ] = []

        for value in values:
            identity = (
                value.supervision_binding_id
            )

            if identity in by_id:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "SV_P2_DUPLICATE_BINDING_ID",
                )

            by_id[
                identity
            ] = value

            predecessor = (
                value.supersedes_supervision_binding_id
            )

            if predecessor is None:
                roots.append(value)
            else:
                children[
                    predecessor
                ].append(value)

        for predecessor_id, successors in children.items():
            if predecessor_id not in by_id:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "SV_P2_PREDECESSOR_NOT_FOUND",
                )

            if len(successors) != 1:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "SV_P2_BRANCHED_HISTORY",
                )

        if not roots:
            _fail(
                RegistryPersistedRecordInvalidError,
                "SV_P2_ROOT_BINDING_MISSING",
            )

        ordered_chains: list[
            tuple[
                LegalWorkSupervisionBinding,
                ...
            ]
        ] = []

        globally_seen: set[str] = set()

        for root in sorted(
            roots,
            key=lambda item: (
                item.effective_from,
                item.supervision_binding_id,
            ),
        ):
            chain: list[
                LegalWorkSupervisionBinding
            ] = []

            seen: set[str] = set()

            current = root

            root_scope = _lineage_scope(
                root
            )

            while True:
                identity = (
                    current.supervision_binding_id
                )

                if identity in seen:
                    _fail(
                        RegistryPersistedRecordInvalidError,
                        "SV_P2_CYCLIC_HISTORY",
                    )

                if identity in globally_seen:
                    _fail(
                        RegistryPersistedRecordInvalidError,
                        "SV_P2_HISTORY_OVERLAP",
                    )

                if (
                    _lineage_scope(current)
                    != root_scope
                ):
                    _fail(
                        RegistryPersistedRecordInvalidError,
                        "SV_P2_LINEAGE_SCOPE_MISMATCH",
                    )

                seen.add(
                    identity
                )

                globally_seen.add(
                    identity
                )

                chain.append(
                    current
                )

                successors = children.get(
                    identity,
                    [],
                )

                if not successors:
                    break

                successor = successors[0]

                if (
                    successor.effective_from
                    <= current.effective_from
                ):
                    _fail(
                        RegistryPersistedRecordInvalidError,
                        "SV_P2_EFFECTIVE_FROM_NOT_INCREASING",
                    )

                current = successor

            ordered_chains.append(
                tuple(chain)
            )

        if len(globally_seen) != len(values):
            _fail(
                RegistryPersistedRecordInvalidError,
                "SV_P2_DISCONNECTED_HISTORY",
            )

        return tuple(
            ordered_chains
        )

    @staticmethod
    def _current_from_chain(
        chain: tuple[
            LegalWorkSupervisionBinding,
            ...
        ],
        at: datetime,
    ) -> LegalWorkSupervisionBinding | None:
        applicable = tuple(
            value
            for value in chain
            if value.effective_from <= at
        )

        if not applicable:
            return None

        current = applicable[-1]

        if (
            current.effective_until is not None
            and current.effective_until <= at
        ):
            return None

        return current

    @classmethod
    def _current_values(
        cls,
        values: tuple[
            LegalWorkSupervisionBinding,
            ...
        ],
        at: datetime,
    ) -> tuple[
        LegalWorkSupervisionBinding,
        ...
    ]:
        chains = cls._validate_chains(
            values
        )

        current = tuple(
            candidate
            for chain in chains
            for candidate in (
                cls._current_from_chain(
                    chain,
                    at,
                ),
            )
            if candidate is not None
        )

        return tuple(
            sorted(
                current,
                key=lambda item: (
                    item.effective_from,
                    item.supervision_binding_id,
                ),
            )
        )

    def _load_tenant(
        self,
        tenant_id: str,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkSupervisionBinding,
        ...
    ]:
        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
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
                "SV_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        values = tuple(
            self._hydrate(
                raw
            )
            for raw in rows
        )

        for value in values:
            if value.tenant_id != tenant:
                _fail(
                    RegistryPersistedRecordInvalidError,
                    "SV_P2_PERSISTED_SCOPE_MISMATCH",
                )

        return values

    def get_by_binding_id(
        self,
        tenant_id: str,
        binding_id: str,
        *,
        session: Any,
    ) -> LegalWorkSupervisionBinding:
        """Return one exact immutable supervision binding."""

        tx = _transaction(
            session
        )

        tenant = _text(
            "tenant_id",
            tenant_id,
        )

        identity = _text(
            "supervision_binding_id",
            binding_id,
        )

        try:
            raw = self._collection.find_one(
                {
                    "tenant_id": tenant,
                    "supervision_binding_id":
                        identity,
                },
                session=tx,
            )
        except PyMongoError as exc:
            _fail(
                RegistryPersistenceUnavailableError,
                "SV_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        if raw is None:
            _fail(
                RegistryNotFoundError,
                "SV_P2_BINDING_NOT_FOUND",
            )

        value = self._hydrate(
            raw
        )

        if (
            value.tenant_id != tenant
            or value.supervision_binding_id
            != identity
        ):
            _fail(
                RegistryPersistedRecordInvalidError,
                "SV_P2_PERSISTED_SCOPE_MISMATCH",
            )

        return value

    def persist(
        self,
        value: LegalWorkSupervisionBinding,
        *,
        session: Any,
    ) -> LegalWorkSupervisionBinding:
        """Append one initial binding or one exact successor."""

        tx = _transaction(
            session
        )

        if not isinstance(
            value,
            LegalWorkSupervisionBinding,
        ):
            _fail(
                RegistryConflictError,
                "SV_P2_DOMAIN_VALUE_REQUIRED",
            )

        identity_query = {
            "tenant_id":
                value.tenant_id,
            "supervision_binding_id":
                value.supervision_binding_id,
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
                "SV_P2_PERSISTENCE_UNAVAILABLE",
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
                "SV_P2_DIVERGENT_REPLAY",
            )

        predecessor_id = (
            value.supersedes_supervision_binding_id
        )

        if predecessor_id is not None:
            try:
                predecessor_raw = (
                    self._collection.find_one(
                        {
                            "tenant_id":
                                value.tenant_id,
                            "supervision_binding_id":
                                predecessor_id,
                        },
                        session=tx,
                    )
                )
            except PyMongoError as exc:
                _fail(
                    RegistryPersistenceUnavailableError,
                    "SV_P2_PERSISTENCE_UNAVAILABLE",
                    exc,
                )

            if predecessor_raw is None:
                _fail(
                    RegistryConflictError,
                    "SV_P2_PREDECESSOR_NOT_FOUND",
                )

            predecessor = self._hydrate(
                predecessor_raw
            )

            if (
                _lineage_scope(value)
                != _lineage_scope(predecessor)
            ):
                _fail(
                    RegistryConflictError,
                    "SV_P2_LINEAGE_SCOPE_MISMATCH",
                )

            if (
                value.effective_from
                <= predecessor.effective_from
            ):
                _fail(
                    RegistryConflictError,
                    "SV_P2_EFFECTIVE_FROM_NOT_INCREASING",
                )

            try:
                successor_raw = (
                    self._collection.find_one(
                        {
                            "tenant_id":
                                value.tenant_id,
                            "supersedes_supervision_binding_id":
                                predecessor_id,
                        },
                        session=tx,
                    )
                )
            except PyMongoError as exc:
                _fail(
                    RegistryPersistenceUnavailableError,
                    "SV_P2_PERSISTENCE_UNAVAILABLE",
                    exc,
                )

            if successor_raw is not None:
                successor = self._hydrate(
                    successor_raw
                )

                if self._equal(
                    successor,
                    value,
                ):
                    return successor

                _fail(
                    RegistryConflictError,
                    "SV_P2_STALE_PREDECESSOR",
                )

        try:
            self._collection.insert_one(
                value.to_dict(),
                session=tx,
            )
        except DuplicateKeyError:
            try:
                raced_identity_raw = (
                    self._collection.find_one(
                        identity_query,
                        session=tx,
                    )
                )
            except PyMongoError as exc:
                _fail(
                    RegistryPersistenceUnavailableError,
                    "SV_P2_PERSISTENCE_UNAVAILABLE",
                    exc,
                )

            if raced_identity_raw is not None:
                raced = self._hydrate(
                    raced_identity_raw
                )

                if self._equal(
                    raced,
                    value,
                ):
                    return raced

            _fail(
                RegistryConflictError,
                "SV_P2_COMPETING_BINDING_CONFLICT",
            )
        except PyMongoError as exc:
            _fail(
                RegistryPersistenceUnavailableError,
                "SV_P2_PERSISTENCE_UNAVAILABLE",
                exc,
            )

        return self.get_by_binding_id(
            value.tenant_id,
            value.supervision_binding_id,
            session=tx,
        )

    def list_current_for_supervisor(
        self,
        tenant_id: str,
        supervisor_principal_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkSupervisionBinding,
        ...
    ]:
        """Return all current chains supervised by one principal."""

        supervisor = _text(
            "supervisor_principal_id",
            supervisor_principal_id,
        )

        moment = _moment(
            at
        )

        current = self._current_values(
            self._load_tenant(
                tenant_id,
                session=session,
            ),
            moment,
        )

        return tuple(
            value
            for value in current
            if (
                value.supervisor_principal_id
                == supervisor
            )
        )

    def list_current_for_supervisee(
        self,
        tenant_id: str,
        supervisee_principal_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkSupervisionBinding,
        ...
    ]:
        """Return all current chains governing one supervisee."""

        supervisee = _text(
            "supervisee_principal_id",
            supervisee_principal_id,
        )

        moment = _moment(
            at
        )

        current = self._current_values(
            self._load_tenant(
                tenant_id,
                session=session,
            ),
            moment,
        )

        return tuple(
            value
            for value in current
            if (
                value.supervisee_principal_id
                == supervisee
            )
        )

    def list_current_for_work_item(
        self,
        tenant_id: str,
        case_matter_id: str,
        work_item_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkSupervisionBinding,
        ...
    ]:
        """Return current WORK_ITEM-scoped supervision."""

        matter = _text(
            "case_matter_id",
            case_matter_id,
        )

        work_item = _text(
            "work_item_id",
            work_item_id,
        )

        moment = _moment(
            at
        )

        current = self._current_values(
            self._load_tenant(
                tenant_id,
                session=session,
            ),
            moment,
        )

        return tuple(
            value
            for value in current
            if (
                value.case_matter_id
                == matter
                and _scope_token(value)
                == LegalSupervisionScope.WORK_ITEM.value
                and value.work_item_id
                == work_item
            )
        )

    def list_current_for_matter(
        self,
        tenant_id: str,
        case_matter_id: str,
        at: datetime,
        *,
        session: Any,
    ) -> tuple[
        LegalWorkSupervisionBinding,
        ...
    ]:
        """Return current MATTER-scoped supervision only."""

        matter = _text(
            "case_matter_id",
            case_matter_id,
        )

        moment = _moment(
            at
        )

        current = self._current_values(
            self._load_tenant(
                tenant_id,
                session=session,
            ),
            moment,
        )

        return tuple(
            value
            for value in current
            if (
                value.case_matter_id
                == matter
                and _scope_token(value)
                == LegalSupervisionScope.MATTER.value
            )
        )


__all__ = [
    "VERSION",
    "COLLECTION_NAME",
    "BINDING_IDENTITY_INDEX_NAME",
    "PREDECESSOR_INDEX_NAME",
    "SUPERVISOR_INDEX_NAME",
    "SUPERVISEE_INDEX_NAME",
    "WORK_SCOPE_INDEX_NAME",
    "LegalWorkSupervisionBindingRegistry",
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
# ARTIFACT: legal_work_supervision_binding_registry.py
# APPEND-ONLY IMMUTABLE HISTORY: YES
# MULTIPLE INDEPENDENT SUPERVISION CHAINS: YES
# CURRENTNESS: DERIVED FROM IMMUTABLE EFFECTIVE-DATED LINEAGE
# MUTABLE CURRENT POINTER: NONE
# CALLER-OWNED ACTIVE TRANSACTION REQUIRED: YES
# UPDATE / REPLACE / DELETE AUTHORITY: NONE
# IAM AUTHORITY: NONE
# ASSIGNMENT AUTHORITY: NONE
# APPROVAL EXECUTION AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# ==============================================================================
