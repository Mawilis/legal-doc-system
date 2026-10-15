"""
TITLE:
    WILSY OS System Permission Assignment Durable Registry

VERSION:
    v1.0.0-P4-R4-D7-SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY

AUTHORITY:
    Wilsy OS Sovereign IAM

EPITOME:
    Persist immutable revisioned SYSTEM permission-assignment evidence without
    granting current permission authority, assignment authority, privileged
    activation, break-glass authority, or financial execution authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_assignment_registry.py

CHANGELOG:
    v1.0.0-P4-R4-D7-SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY
        Introduces caller-transaction-owned append-only persistence for immutable
        SYSTEM permission assignments. Physical uniqueness is assignment_id +
        revision; assignment_id remains stable logical identity. Exact replay,
        terminal revocation, BSON datetime hydration, fingerprint verification
        and corruption rejection are enforced.

AUTHORITY BOUNDARY:
    Durable assignment history is evidence only. Registry lifecycle currentness
    does not prove principal currentness and does not authorize permission use.

FINANCIAL AUTHORITY BOUNDARY:
    NONE.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.system_permission_assignment import (
    SCHEMA,
    VERSION as DOMAIN_VERSION,
    SystemPermissionAssignment,
    SystemPermissionAssignmentError,
    SystemPermissionAssignmentStatus,
)


VERSION: Final = (
    "v1.0.0-P4-R4-D7-"
    "SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY"
)

COLLECTION: Final = "system_permission_assignments"

ASSIGNMENT_REVISION_INDEX: Final = (
    "system_permission_assignment_revision_unique"
)

SCOPE_OPERATION_IDEMPOTENCY_INDEX: Final = (
    "system_permission_assignment_scope_operation_idempotency_unique"
)

SCOPE_HISTORY_INDEX: Final = (
    "system_permission_assignment_scope_history"
)

_ASSIGN: Final = "ASSIGN"
_REVOKE: Final = "REVOKE"


class SystemPermissionAssignmentRegistryError(RuntimeError):
    """Base registry failure with one stable machine-readable code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class SystemPermissionAssignmentTransactionRequiredError(
    SystemPermissionAssignmentRegistryError
):
    """Caller did not provide an active transaction."""


class SystemPermissionAssignmentConflictError(
    SystemPermissionAssignmentRegistryError
):
    """Replay, identity, lifecycle, or current-state conflict."""


class SystemPermissionAssignmentNotFoundError(
    SystemPermissionAssignmentRegistryError
):
    """Exact assignment history does not exist."""


class SystemPermissionAssignmentPersistedInvalidError(
    SystemPermissionAssignmentRegistryError
):
    """Persisted material failed strict integrity validation."""


class SystemPermissionAssignmentPersistenceError(
    SystemPermissionAssignmentRegistryError
):
    """Mongo persistence failed or exposed an invalid interface."""


def _identifier(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or "*" in value
    ):
        raise SystemPermissionAssignmentRegistryError(
            name + "_INVALID"
        )
    return value


def _timestamp(
    name: str,
    value: object,
) -> datetime:
    if not isinstance(value, datetime):
        raise SystemPermissionAssignmentPersistedInvalidError(
            name + "_INVALID"
        )

    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _active_transaction(
    session: object,
) -> object:
    if (
        session is None
        or getattr(session, "in_transaction", False)
        is not True
    ):
        raise SystemPermissionAssignmentTransactionRequiredError(
            "ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _scope_query(
    *,
    principal_id: str,
    permission_id: str,
) -> dict[str, object]:
    return {
        "principal_id":
            _identifier("PRINCIPAL_ID", principal_id),
        "permission_id":
            _identifier("PERMISSION_ID", permission_id),
    }


def _document(
    value: SystemPermissionAssignment,
    *,
    operation_kind: str,
    operation_idempotency_key: str,
) -> dict[str, object]:
    """Convert fingerprint payload timestamps to BSON datetime representation."""

    payload = value.authority_payload()

    payload["assigned_at"] = value.assigned_at
    payload["revoked_at"] = value.revoked_at

    return {
        **payload,
        "assignment_fingerprint":
            value.assignment_fingerprint,
        "_operation_kind":
            operation_kind,
        "_operation_idempotency_key":
            operation_idempotency_key,
    }


def _hydrate(
    row: object,
) -> SystemPermissionAssignment:
    if not isinstance(row, Mapping):
        raise SystemPermissionAssignmentPersistedInvalidError(
            "PERSISTED_RECORD_INVALID"
        )

    expected = set(
        SystemPermissionAssignment.__dataclass_fields__
    ) | {
        "schema",
        "version",
        "assignment_fingerprint",
        "_operation_kind",
        "_operation_idempotency_key",
    }

    clean = dict(row)
    clean.pop("_id", None)

    if set(clean) != expected:
        raise SystemPermissionAssignmentPersistedInvalidError(
            "PERSISTED_SHAPE_INVALID"
        )

    if (
        clean.get("schema") != SCHEMA
        or clean.get("version") != DOMAIN_VERSION
    ):
        raise SystemPermissionAssignmentPersistedInvalidError(
            "PERSISTED_SCHEMA_VERSION_INVALID"
        )

    if clean.get("_operation_kind") not in {
        _ASSIGN,
        _REVOKE,
    }:
        raise SystemPermissionAssignmentPersistedInvalidError(
            "PERSISTED_OPERATION_INVALID"
        )

    _identifier(
        "OPERATION_IDEMPOTENCY_KEY",
        clean.get("_operation_idempotency_key"),
    )

    stored = clean.get("assignment_fingerprint")

    try:
        value = SystemPermissionAssignment(
            assignment_id=clean["assignment_id"],  # type: ignore[arg-type]
            principal_id=clean["principal_id"],  # type: ignore[arg-type]
            permission_id=clean["permission_id"],  # type: ignore[arg-type]
            status=SystemPermissionAssignmentStatus(
                clean["status"]
            ),
            assigned_by_principal_id=clean[
                "assigned_by_principal_id"
            ],  # type: ignore[arg-type]
            assigned_at=_timestamp(
                "ASSIGNED_AT",
                clean["assigned_at"],
            ),
            assignment_evidence_reference=clean[
                "assignment_evidence_reference"
            ],  # type: ignore[arg-type]
            revision=clean["revision"],  # type: ignore[arg-type]
            previous_assignment_fingerprint=clean[
                "previous_assignment_fingerprint"
            ],  # type: ignore[arg-type]
            revoked_by_principal_id=clean[
                "revoked_by_principal_id"
            ],  # type: ignore[arg-type]
            revoked_at=(
                None
                if clean["revoked_at"] is None
                else _timestamp(
                    "REVOKED_AT",
                    clean["revoked_at"],
                )
            ),
            revocation_evidence_reference=clean[
                "revocation_evidence_reference"
            ],  # type: ignore[arg-type]
        )

    except (
        KeyError,
        TypeError,
        ValueError,
        SystemPermissionAssignmentError,
    ) as error:
        raise SystemPermissionAssignmentPersistedInvalidError(
            "PERSISTED_RECORD_INVALID"
        ) from error

    if (
        not isinstance(stored, str)
        or stored != value.assignment_fingerprint
    ):
        raise SystemPermissionAssignmentPersistedInvalidError(
            "PERSISTED_FINGERPRINT_INVALID"
        )

    return value


def _propagate_transient(
    error: PyMongoError,
) -> None:
    if error.has_error_label(
        "TransientTransactionError"
    ):
        raise error


class SystemPermissionAssignmentRegistry:
    """Persist exact append-only SYSTEM permission-assignment histories."""

    def __init__(
        self,
        collection: Any,
    ) -> None:
        if collection is None:
            raise SystemPermissionAssignmentPersistenceError(
                "COLLECTION_REQUIRED"
            )
        self._collection = collection

    def ensure_indexes(self) -> None:
        """Create the three sanctioned indexes and no TTL index."""

        specs = (
            (
                [
                    ("assignment_id", ASCENDING),
                    ("revision", ASCENDING),
                ],
                True,
                ASSIGNMENT_REVISION_INDEX,
            ),
            (
                [
                    ("principal_id", ASCENDING),
                    ("permission_id", ASCENDING),
                    (
                        "_operation_idempotency_key",
                        ASCENDING,
                    ),
                ],
                True,
                SCOPE_OPERATION_IDEMPOTENCY_INDEX,
            ),
            (
                [
                    ("principal_id", ASCENDING),
                    ("permission_id", ASCENDING),
                    ("assigned_at", ASCENDING),
                    ("assignment_id", ASCENDING),
                    ("revision", ASCENDING),
                ],
                False,
                SCOPE_HISTORY_INDEX,
            ),
        )

        try:
            for keys, unique, name in specs:
                self._collection.create_index(
                    keys,
                    unique=unique,
                    name=name,
                )

        except AttributeError as error:
            raise SystemPermissionAssignmentPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error

        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionAssignmentPersistenceError(
                "INDEX_CREATION_FAILED"
            ) from error

    def _find_one(
        self,
        query: Mapping[str, object],
        *,
        session: object = None,
    ) -> Mapping[str, object] | None:
        try:
            return self._collection.find_one(
                dict(query),
                session=session,
            )

        except AttributeError as error:
            raise SystemPermissionAssignmentPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error

        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionAssignmentPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

    def _find(
        self,
        query: Mapping[str, object],
        *,
        session: object = None,
    ) -> list[Mapping[str, object]]:
        try:
            return list(
                self._collection.find(
                    dict(query),
                    session=session,
                )
            )

        except AttributeError as error:
            raise SystemPermissionAssignmentPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error

        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionAssignmentPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

    def _insert(
        self,
        value: SystemPermissionAssignment,
        *,
        operation_kind: str,
        operation_idempotency_key: str,
        session: object,
    ) -> None:
        try:
            self._collection.insert_one(
                _document(
                    value,
                    operation_kind=operation_kind,
                    operation_idempotency_key=
                        operation_idempotency_key,
                ),
                session=session,
            )

        except DuplicateKeyError as error:
            if error.has_error_label(
                "TransientTransactionError"
            ):
                raise

            raise SystemPermissionAssignmentConflictError(
                "DUPLICATE_KEY_CONFLICT"
            ) from error

        except AttributeError as error:
            raise SystemPermissionAssignmentPersistenceError(
                "COLLECTION_INTERFACE_INVALID"
            ) from error

        except PyMongoError as error:
            _propagate_transient(error)
            raise SystemPermissionAssignmentPersistenceError(
                "PERSISTENCE_UNAVAILABLE"
            ) from error

    def get_history(
        self,
        assignment_id: str,
        *,
        session: object = None,
    ) -> tuple[
        SystemPermissionAssignment,
        ...,
    ]:
        """Return and validate the complete immutable assignment chain."""

        identity = _identifier(
            "ASSIGNMENT_ID",
            assignment_id,
        )

        values = [
            _hydrate(row)
            for row in self._find(
                {"assignment_id": identity},
                session=session,
            )
        ]

        values.sort(
            key=lambda item: item.revision
        )

        if not values:
            return ()

        if (
            values[0].revision != 1
            or values[0].status
            is not SystemPermissionAssignmentStatus.ACTIVE
        ):
            raise SystemPermissionAssignmentPersistedInvalidError(
                "PERSISTED_CHAIN_INVALID"
            )

        for expected, value in enumerate(
            values,
            start=1,
        ):
            if value.revision != expected:
                raise SystemPermissionAssignmentPersistedInvalidError(
                    "PERSISTED_CHAIN_INVALID"
                )

            if expected > 1:
                prior = values[
                    expected - 2
                ]

                if (
                    value.previous_assignment_fingerprint
                    != prior.assignment_fingerprint
                ):
                    raise SystemPermissionAssignmentPersistedInvalidError(
                        "PERSISTED_CHAIN_INVALID"
                    )

                if (
                    value.assignment_id != prior.assignment_id
                    or value.principal_id != prior.principal_id
                    or value.permission_id != prior.permission_id
                    or value.assigned_by_principal_id
                    != prior.assigned_by_principal_id
                    or value.assigned_at != prior.assigned_at
                    or value.assignment_evidence_reference
                    != prior.assignment_evidence_reference
                ):
                    raise SystemPermissionAssignmentPersistedInvalidError(
                        "PERSISTED_CHAIN_DIVERGENT"
                    )

        if (
            len(values) > 2
            or (
                len(values) == 2
                and values[-1].status
                is not SystemPermissionAssignmentStatus.REVOKED
            )
        ):
            raise SystemPermissionAssignmentPersistedInvalidError(
                "PERSISTED_CHAIN_INVALID"
            )

        return tuple(values)

    def create_or_replay(
        self,
        assignment: SystemPermissionAssignment,
        *,
        idempotency_key: str,
        session: object,
    ) -> SystemPermissionAssignment:
        """Persist initial ACTIVE evidence or return exact replay."""

        tx = _active_transaction(session)

        key = _identifier(
            "IDEMPOTENCY_KEY",
            idempotency_key,
        )

        if type(assignment) is not SystemPermissionAssignment:
            raise SystemPermissionAssignmentPersistenceError(
                "ASSIGNMENT_REQUIRED"
            )

        if (
            assignment.status
            is not SystemPermissionAssignmentStatus.ACTIVE
            or assignment.revision != 1
        ):
            raise SystemPermissionAssignmentConflictError(
                "INITIAL_ACTIVE_REVISION_REQUIRED"
            )

        scope = _scope_query(
            principal_id=assignment.principal_id,
            permission_id=assignment.permission_id,
        )

        replay_row = self._find_one(
            {
                **scope,
                "_operation_idempotency_key":
                    key,
            },
            session=tx,
        )

        if replay_row is not None:
            replay = _hydrate(replay_row)

            if (
                replay == assignment
                and replay_row.get(
                    "_operation_kind"
                )
                == _ASSIGN
            ):
                return replay

            raise SystemPermissionAssignmentConflictError(
                "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
            )

        if self.get_history(
            assignment.assignment_id,
            session=tx,
        ):
            raise SystemPermissionAssignmentConflictError(
                "ASSIGNMENT_ID_COLLISION"
            )

        self._insert(
            assignment,
            operation_kind=_ASSIGN,
            operation_idempotency_key=key,
            session=tx,
        )

        return assignment

    def revoke_or_replay(
        self,
        assignment: SystemPermissionAssignment,
        *,
        revocation_idempotency_key: str,
        session: object,
    ) -> SystemPermissionAssignment:
        """Persist exact terminal successor or return exact replay."""

        tx = _active_transaction(session)

        key = _identifier(
            "REVOCATION_IDEMPOTENCY_KEY",
            revocation_idempotency_key,
        )

        if (
            type(assignment)
            is not SystemPermissionAssignment
            or assignment.status
            is not SystemPermissionAssignmentStatus.REVOKED
        ):
            raise SystemPermissionAssignmentConflictError(
                "REVOKED_ASSIGNMENT_REQUIRED"
            )

        replay_row = self._find_one(
            {
                "assignment_id":
                    assignment.assignment_id,
                "_operation_idempotency_key":
                    key,
            },
            session=tx,
        )

        if replay_row is not None:
            replay = _hydrate(replay_row)

            if (
                replay == assignment
                and replay_row.get(
                    "_operation_kind"
                )
                == _REVOKE
            ):
                return replay

            raise SystemPermissionAssignmentConflictError(
                "IDEMPOTENCY_KEY_DIVERGENT_REPLAY"
            )

        history = self.get_history(
            assignment.assignment_id,
            session=tx,
        )

        if not history:
            raise SystemPermissionAssignmentNotFoundError(
                "ASSIGNMENT_NOT_FOUND"
            )

        current = history[-1]

        if (
            current.status
            is SystemPermissionAssignmentStatus.REVOKED
        ):
            raise SystemPermissionAssignmentConflictError(
                "ASSIGNMENT_TERMINAL"
            )

        if (
            assignment.revision
            != current.revision + 1
            or assignment.previous_assignment_fingerprint
            != current.assignment_fingerprint
        ):
            raise SystemPermissionAssignmentConflictError(
                "STALE_OR_DIVERGENT_REVISION"
            )

        expected = current.revoke(
            revoked_by_principal_id=(
                assignment.revoked_by_principal_id
            ),  # type: ignore[arg-type]
            revoked_at=assignment.revoked_at,  # type: ignore[arg-type]
            revocation_evidence_reference=(
                assignment.revocation_evidence_reference
            ),  # type: ignore[arg-type]
        )

        if expected != assignment:
            raise SystemPermissionAssignmentConflictError(
                "REVOCATION_DIVERGENT"
            )

        self._insert(
            assignment,
            operation_kind=_REVOKE,
            operation_idempotency_key=key,
            session=tx,
        )

        return assignment

    def resolve_current(
        self,
        *,
        principal_id: str,
        permission_id: str,
        session: object = None,
    ) -> SystemPermissionAssignment | None:
        """Resolve latest ACTIVE registry lifecycle state only."""

        scope = _scope_query(
            principal_id=principal_id,
            permission_id=permission_id,
        )

        rows = self._find(
            scope,
            session=session,
        )

        identities: set[str] = set()

        for row in rows:
            identity = row.get(
                "assignment_id"
            )

            if not isinstance(
                identity,
                str,
            ):
                raise SystemPermissionAssignmentPersistedInvalidError(
                    "PERSISTED_IDENTITY_INVALID"
                )

            identities.add(
                identity
            )

        current: list[
            SystemPermissionAssignment
        ] = []

        for identity in sorted(
            identities
        ):
            history = self.get_history(
                identity,
                session=session,
            )

            latest = history[-1]

            if (
                latest.principal_id == principal_id
                and latest.permission_id == permission_id
                and latest.status
                is SystemPermissionAssignmentStatus.ACTIVE
            ):
                current.append(
                    latest
                )

        if len(current) > 1:
            raise SystemPermissionAssignmentConflictError(
                "MULTIPLE_CURRENT_ASSIGNMENTS"
            )

        return (
            None
            if not current
            else current[0]
        )


__all__ = [
    "VERSION",
    "COLLECTION",
    "ASSIGNMENT_REVISION_INDEX",
    "SCOPE_OPERATION_IDEMPOTENCY_INDEX",
    "SCOPE_HISTORY_INDEX",
    "SystemPermissionAssignmentRegistryError",
    "SystemPermissionAssignmentTransactionRequiredError",
    "SystemPermissionAssignmentConflictError",
    "SystemPermissionAssignmentNotFoundError",
    "SystemPermissionAssignmentPersistedInvalidError",
    "SystemPermissionAssignmentPersistenceError",
    "SystemPermissionAssignmentRegistry",
]


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tools/eos/auth/system_permission_assignment_registry.py
# VERSION: v1.0.0-P4-R4-D7-SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY
# STORAGE: append-only immutable revision history
# PHYSICAL UNIQUE KEY: assignment_id + revision
# LOGICAL IDENTITY: assignment_id
# TENANT AUTHORITY: NONE
# ROLE AUTHORITY: NONE
# CURRENT PRINCIPAL AUTHORITY: NONE
# FINAL PERMISSION AUTHORIZATION: NONE
# ASSIGNMENT ISSUANCE AUTHORITY: NONE
# ASSIGNMENT REVOCATION AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# P5 PRIVILEGED USE AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# TTL / DELETE AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
