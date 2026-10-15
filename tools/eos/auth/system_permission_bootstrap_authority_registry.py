"""
TITLE:
    WILSY OS System Permission Bootstrap Authority Durable Registry

VERSION:
    v1.0.0-P4-R4-D11-R2-SYSTEM-PERMISSION-BOOTSTRAP-AUTHORITY-REGISTRY

AUTHORITY:
    Wilsy OS Sovereign IAM persistence only.

PURPOSE:
    Persist immutable SystemPermissionBootstrapAuthority revisions with exact
    replay, append-only ACTIVE -> RETIRED history, fail-closed hydration and
    caller-owned transaction semantics.

AUTHORITY BOUNDARY:
    This registry does not decide who may create bootstrap authority. It does
    not certify installation/offline trust, grant or revoke SYSTEM permission,
    authorize command execution, create privileged activation, create break-glass
    authority, or create financial authority.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
    SystemPermissionBootstrapAuthorityError,
    SystemPermissionBootstrapAuthorityStatus,
)


VERSION: Final = (
    "v1.0.0-P4-R4-D11-R2-"
    "SYSTEM-PERMISSION-BOOTSTRAP-AUTHORITY-REGISTRY"
)

COLLECTION: Final = "system_permission_bootstrap_authorities"

BOOTSTRAP_REVISION_INDEX: Final = (
    "system_permission_bootstrap_revision_unique"
)
BOOTSTRAP_CREATE_REPLAY_INDEX: Final = (
    "system_permission_bootstrap_scope_operation_idempotency_unique"
)
BOOTSTRAP_HISTORY_INDEX: Final = (
    "system_permission_bootstrap_principal_purpose_history"
)
BOOTSTRAP_STATUS_TIMELINE_INDEX: Final = (
    "system_permission_bootstrap_status_issued_timeline"
)

_ASSIGN: Final = "ASSIGN"
_RETIRE: Final = "RETIRE"


class SystemPermissionBootstrapAuthorityRegistryError(RuntimeError):
    """Base bounded persistence failure."""


class SystemPermissionBootstrapAuthorityTransactionRequiredError(
    SystemPermissionBootstrapAuthorityRegistryError
):
    """Caller failed to provide an already-active transaction."""


class SystemPermissionBootstrapAuthorityConflictError(
    SystemPermissionBootstrapAuthorityRegistryError
):
    """Create/retire request conflicts with durable history."""


class SystemPermissionBootstrapAuthorityNotFoundError(
    SystemPermissionBootstrapAuthorityRegistryError
):
    """Requested bootstrap authority history does not exist."""


class SystemPermissionBootstrapAuthorityPersistedInvalidError(
    SystemPermissionBootstrapAuthorityRegistryError
):
    """Persisted bootstrap authority is corrupt or inconsistent."""


class SystemPermissionBootstrapAuthorityPersistenceError(
    SystemPermissionBootstrapAuthorityRegistryError
):
    """Persistence layer failed closed."""


def _identifier(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise SystemPermissionBootstrapAuthorityPersistenceError(
            name + "_INVALID"
        )
    return value


def _timestamp(name: str, value: object) -> datetime:
    if not isinstance(value, datetime):
        raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
            name + "_INVALID"
        )

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    if value.utcoffset() is None:
        raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
            name + "_INVALID"
        )

    return value.astimezone(timezone.utc)


def _active_transaction(session: object) -> object:
    if session is None:
        raise SystemPermissionBootstrapAuthorityTransactionRequiredError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )

    try:
        active = getattr(session, "in_transaction")
    except Exception as error:
        raise SystemPermissionBootstrapAuthorityTransactionRequiredError(
            "ACTIVE_TRANSACTION_REQUIRED"
        ) from error

    if active is not True:
        raise SystemPermissionBootstrapAuthorityTransactionRequiredError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )

    return session


def _propagate_transient(error: PyMongoError) -> None:
    try:
        transient = error.has_error_label(
            "TransientTransactionError"
        )
    except Exception:
        transient = False

    if transient:
        raise error


def _document(
    authority: SystemPermissionBootstrapAuthority,
    *,
    operation_kind: str,
    operation_idempotency_key: str,
) -> dict[str, object]:
    if type(authority) is not SystemPermissionBootstrapAuthority:
        raise SystemPermissionBootstrapAuthorityPersistenceError(
            "BOOTSTRAP_AUTHORITY_REQUIRED"
        )

    row = authority.to_dict()
    row["issued_at"] = authority.issued_at
    row["retired_at"] = authority.retired_at
    row["_operation_kind"] = operation_kind
    row["_operation_idempotency_key"] = (
        operation_idempotency_key
    )
    return row


def _hydrate(row: object) -> SystemPermissionBootstrapAuthority:
    if not isinstance(row, dict):
        raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
            "PERSISTED_DOCUMENT_INVALID"
        )

    try:
        return SystemPermissionBootstrapAuthority(
            bootstrap_id=row["bootstrap_id"],
            actor_principal_id=row["actor_principal_id"],
            purpose=row["purpose"],
            evidence_reference=row["evidence_reference"],
            issued_at=_timestamp(
                "ISSUED_AT",
                row["issued_at"],
            ),
            status=SystemPermissionBootstrapAuthorityStatus(
                row["status"]
            ),
            revision=row["revision"],
            previous_fingerprint=row.get(
                "previous_fingerprint"
            ),
            retired_at=(
                None
                if row.get("retired_at") is None
                else _timestamp(
                    "RETIRED_AT",
                    row["retired_at"],
                )
            ),
            retirement_evidence_reference=row.get(
                "retirement_evidence_reference"
            ),
            authority_fingerprint=row[
                "authority_fingerprint"
            ],
        )
    except (
        KeyError,
        TypeError,
        ValueError,
        SystemPermissionBootstrapAuthorityError,
    ) as error:
        raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
            "PERSISTED_DOCUMENT_INVALID"
        ) from error


def _same_logical_authority(
    first: SystemPermissionBootstrapAuthority,
    second: SystemPermissionBootstrapAuthority,
) -> bool:
    return (
        first.bootstrap_id == second.bootstrap_id
        and first.actor_principal_id == second.actor_principal_id
        and first.purpose == second.purpose
        and first.evidence_reference == second.evidence_reference
        and first.issued_at == second.issued_at
    )


class SystemPermissionBootstrapAuthorityRegistry:
    """Append-only persistence for bootstrap authority evidence only."""

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "COLLECTION_REQUIRED"
            )
        self._collection = collection

    def ensure_indexes(self) -> None:
        indexes = (
            (
                [
                    ("bootstrap_id", ASCENDING),
                    ("revision", ASCENDING),
                ],
                True,
                BOOTSTRAP_REVISION_INDEX,
            ),
            (
                [
                    ("actor_principal_id", ASCENDING),
                    ("purpose", ASCENDING),
                    ("_operation_idempotency_key", ASCENDING),
                ],
                True,
                BOOTSTRAP_CREATE_REPLAY_INDEX,
            ),
            (
                [
                    ("actor_principal_id", ASCENDING),
                    ("purpose", ASCENDING),
                    ("revision", ASCENDING),
                ],
                False,
                BOOTSTRAP_HISTORY_INDEX,
            ),
            (
                [
                    ("status", ASCENDING),
                    ("issued_at", ASCENDING),
                ],
                False,
                BOOTSTRAP_STATUS_TIMELINE_INDEX,
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
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "INDEX_CREATION_FAILED"
            ) from error

    def _find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> object:
        try:
            return self._collection.find_one(
                query,
                session=session,
            )
        except AttributeError as error:
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

    def _insert(
        self,
        authority: SystemPermissionBootstrapAuthority,
        *,
        operation_kind: str,
        operation_idempotency_key: str,
        session: object,
    ) -> None:
        try:
            self._collection.insert_one(
                _document(
                    authority,
                    operation_kind=operation_kind,
                    operation_idempotency_key=operation_idempotency_key,
                ),
                session=session,
            )
        except DuplicateKeyError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise
            raise SystemPermissionBootstrapAuthorityConflictError(
                "DUPLICATE_KEY_CONFLICT"
            ) from error
        except AttributeError as error:
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

    def get_history(
        self,
        bootstrap_id: str,
        *,
        session: object = None,
    ) -> tuple[SystemPermissionBootstrapAuthority, ...]:
        identity = _identifier(
            "BOOTSTRAP_ID",
            bootstrap_id,
        )

        try:
            cursor = self._collection.find(
                {"bootstrap_id": identity},
                session=session,
            ).sort(
                "revision",
                ASCENDING,
            )
            rows = list(cursor)
        except AttributeError as error:
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        values = tuple(
            _hydrate(row)
            for row in rows
        )

        self._validate_chain(values)

        if any(
            value.bootstrap_id != identity
            for value in values
        ):
            raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                "BOOTSTRAP_HISTORY_BINDING_MISMATCH"
            )

        return values

    def _validate_chain(
        self,
        values: tuple[
            SystemPermissionBootstrapAuthority,
            ...,
        ],
    ) -> None:
        if not values:
            return

        first = values[0]

        if (
            first.revision != 1
            or first.status
            is not SystemPermissionBootstrapAuthorityStatus.ACTIVE
            or first.previous_fingerprint is not None
        ):
            raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                "INITIAL_REVISION_INVALID"
            )

        if len(values) > 2:
            raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                "REVISION_CHAIN_TOO_LONG"
            )

        baseline = first
        previous = first

        for expected_revision, current in enumerate(
            values[1:],
            start=2,
        ):
            if current.revision != expected_revision:
                raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                    "REVISION_CHAIN_GAP"
                )

            if not _same_logical_authority(
                baseline,
                current,
            ):
                raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                    "LOGICAL_AUTHORITY_BINDING_CHANGED"
                )

            if (
                current.previous_fingerprint
                != previous.authority_fingerprint
            ):
                raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                    "REVISION_CHAIN_FINGERPRINT_MISMATCH"
                )

            if (
                previous.status
                is not SystemPermissionBootstrapAuthorityStatus.ACTIVE
                or current.status
                is not SystemPermissionBootstrapAuthorityStatus.RETIRED
            ):
                raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                    "ILLEGAL_STATUS_TRANSITION"
                )

            previous = current

    def resolve_current(
        self,
        *,
        actor_principal_id: str,
        purpose: str,
        session: object = None,
    ) -> SystemPermissionBootstrapAuthority | None:
        actor = _identifier(
            "ACTOR_PRINCIPAL_ID",
            actor_principal_id,
        )
        bounded_purpose = _identifier(
            "PURPOSE",
            purpose,
        )

        try:
            rows = list(
                self._collection.find(
                    {
                        "actor_principal_id": actor,
                        "purpose": bounded_purpose,
                    },
                    session=session,
                ).sort(
                    [
                        ("bootstrap_id", ASCENDING),
                        ("revision", ASCENDING),
                    ]
                )
            )
        except AttributeError as error:
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error
        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionBootstrapAuthorityPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

        if not rows:
            return None

        grouped: dict[str, list[object]] = {}

        for row in rows:
            if not isinstance(row, dict):
                raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                    "PERSISTED_DOCUMENT_INVALID"
                )

            raw_id = row.get("bootstrap_id")

            if not isinstance(raw_id, str):
                raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                    "BOOTSTRAP_ID_INVALID"
                )

            grouped.setdefault(
                raw_id,
                [],
            ).append(row)

        active: list[
            SystemPermissionBootstrapAuthority
        ] = []

        for bootstrap_id, group in grouped.items():
            values = tuple(
                _hydrate(row)
                for row in group
            )

            self._validate_chain(values)
            latest = values[-1]

            if (
                latest.bootstrap_id != bootstrap_id
                or latest.actor_principal_id != actor
                or latest.purpose != bounded_purpose
            ):
                raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                    "CURRENT_SCOPE_BINDING_MISMATCH"
                )

            if (
                latest.status
                is SystemPermissionBootstrapAuthorityStatus.ACTIVE
            ):
                active.append(latest)

        if len(active) > 1:
            raise SystemPermissionBootstrapAuthorityPersistedInvalidError(
                "AMBIGUOUS_CURRENT_BOOTSTRAP_AUTHORITY"
            )

        return active[0] if active else None

    def create_or_replay(
        self,
        authority: SystemPermissionBootstrapAuthority,
        *,
        idempotency_key: str,
        session: object,
    ) -> SystemPermissionBootstrapAuthority:
        tx = _active_transaction(session)
        key = _identifier(
            "IDEMPOTENCY_KEY",
            idempotency_key,
        )

        if (
            type(authority)
            is not SystemPermissionBootstrapAuthority
            or authority.status
            is not SystemPermissionBootstrapAuthorityStatus.ACTIVE
            or authority.revision != 1
        ):
            raise SystemPermissionBootstrapAuthorityConflictError(
                "INITIAL_ACTIVE_REVISION_REQUIRED"
            )

        replay_row = self._find_one(
            {
                "actor_principal_id":
                    authority.actor_principal_id,
                "purpose":
                    authority.purpose,
                "_operation_idempotency_key":
                    key,
            },
            session=tx,
        )

        if replay_row is not None:
            replay = _hydrate(replay_row)

            if (
                replay == authority
                and isinstance(replay_row, dict)
                and replay_row.get("_operation_kind")
                == _ASSIGN
            ):
                return replay

            raise SystemPermissionBootstrapAuthorityConflictError(
                "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
            )

        if self.get_history(
            authority.bootstrap_id,
            session=tx,
        ):
            raise SystemPermissionBootstrapAuthorityConflictError(
                "BOOTSTRAP_ID_COLLISION"
            )

        self._insert(
            authority,
            operation_kind=_ASSIGN,
            operation_idempotency_key=key,
            session=tx,
        )

        return authority

    def retire_or_replay(
        self,
        authority: SystemPermissionBootstrapAuthority,
        *,
        retirement_idempotency_key: str,
        session: object,
    ) -> SystemPermissionBootstrapAuthority:
        tx = _active_transaction(session)
        key = _identifier(
            "RETIREMENT_IDEMPOTENCY_KEY",
            retirement_idempotency_key,
        )

        if (
            type(authority)
            is not SystemPermissionBootstrapAuthority
            or authority.status
            is not SystemPermissionBootstrapAuthorityStatus.RETIRED
        ):
            raise SystemPermissionBootstrapAuthorityConflictError(
                "RETIRED_AUTHORITY_REQUIRED"
            )

        replay_row = self._find_one(
            {
                "bootstrap_id":
                    authority.bootstrap_id,
                "_operation_idempotency_key":
                    key,
            },
            session=tx,
        )

        if replay_row is not None:
            replay = _hydrate(replay_row)

            if (
                replay == authority
                and isinstance(replay_row, dict)
                and replay_row.get("_operation_kind")
                == _RETIRE
            ):
                return replay

            raise SystemPermissionBootstrapAuthorityConflictError(
                "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
            )

        history = self.get_history(
            authority.bootstrap_id,
            session=tx,
        )

        if not history:
            raise SystemPermissionBootstrapAuthorityNotFoundError(
                "BOOTSTRAP_AUTHORITY_NOT_FOUND"
            )

        current = history[-1]

        if (
            current.status
            is SystemPermissionBootstrapAuthorityStatus.RETIRED
        ):
            raise SystemPermissionBootstrapAuthorityConflictError(
                "BOOTSTRAP_AUTHORITY_TERMINAL"
            )

        if (
            authority.revision != current.revision + 1
            or authority.previous_fingerprint
            != current.authority_fingerprint
        ):
            raise SystemPermissionBootstrapAuthorityConflictError(
                "STALE_OR_DIVERGENT_REVISION"
            )

        if not _same_logical_authority(
            current,
            authority,
        ):
            raise SystemPermissionBootstrapAuthorityConflictError(
                "RETIREMENT_BINDING_DIVERGENT"
            )

        expected = current.retire(
            retired_at=authority.retired_at,  # type: ignore[arg-type]
            retirement_evidence_reference=(
                authority.retirement_evidence_reference
            ),  # type: ignore[arg-type]
        )

        if expected != authority:
            raise SystemPermissionBootstrapAuthorityConflictError(
                "RETIREMENT_DIVERGENT"
            )

        self._insert(
            authority,
            operation_kind=_RETIRE,
            operation_idempotency_key=key,
            session=tx,
        )

        return authority


__all__ = [
    "VERSION",
    "COLLECTION",
    "BOOTSTRAP_REVISION_INDEX",
    "BOOTSTRAP_CREATE_REPLAY_INDEX",
    "BOOTSTRAP_HISTORY_INDEX",
    "BOOTSTRAP_STATUS_TIMELINE_INDEX",
    "SystemPermissionBootstrapAuthorityRegistry",
    "SystemPermissionBootstrapAuthorityRegistryError",
    "SystemPermissionBootstrapAuthorityTransactionRequiredError",
    "SystemPermissionBootstrapAuthorityConflictError",
    "SystemPermissionBootstrapAuthorityNotFoundError",
    "SystemPermissionBootstrapAuthorityPersistedInvalidError",
    "SystemPermissionBootstrapAuthorityPersistenceError",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tools/eos/auth/system_permission_bootstrap_authority_registry.py
# VERSION: v1.0.0-P4-R4-D11-R2-SYSTEM-PERMISSION-BOOTSTRAP-AUTHORITY-REGISTRY
# AUTHORITY TYPE: PERSISTENCE ONLY
# CALLER OWNS TRANSACTION: YES
# APPEND ONLY: YES
# DELETE: NONE
# TTL: NONE
# BOOTSTRAP CREATION POLICY: NONE
# OFFLINE INSTALLATION TRUST AUTHORITY: NONE
# SYSTEM PERMISSION GRANT AUTHORITY: NONE
# SYSTEM PERMISSION REVOCATION AUTHORITY: NONE
# ASSIGNMENT COMMAND AUTHORITY: NONE
# REVOCATION COMMAND AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
