"""
TITLE:
    WILSY OS System Permission Assignment Registry Direct Certificate

VERSION:
    v1.0.0-P4-R4-D7-SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY-CERT

PURPOSE:
    Certify append-only SYSTEM permission-assignment persistence semantics,
    transaction requirements, replay, terminal revocation, lifecycle resolution,
    BSON datetime hydration and corruption failure.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.auth.system_permission_assignment import (
    SystemPermissionAssignment,
    SystemPermissionAssignmentStatus,
)
from tools.eos.auth.system_permission_assignment_registry import (
    ASSIGNMENT_REVISION_INDEX,
    SCOPE_HISTORY_INDEX,
    SCOPE_OPERATION_IDEMPOTENCY_INDEX,
    SystemPermissionAssignmentConflictError,
    SystemPermissionAssignmentPersistedInvalidError,
    SystemPermissionAssignmentRegistry,
    SystemPermissionAssignmentTransactionRequiredError,
)


NOW = datetime(
    2026,
    10,
    14,
    16,
    0,
    tzinfo=timezone.utc,
)

PERMISSION = "privileged_activation:issue"


class FakeSession:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[
            dict[str, object]
        ] = []

        self.indexes: list[
            tuple[
                list[tuple[str, int]],
                bool,
                str,
            ]
        ] = []

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                list(keys),
                unique,
                name,
            )
        )
        return name

    @staticmethod
    def _matches(
        row: dict[str, object],
        query: dict[str, object],
    ) -> bool:
        return all(
            row.get(key) == value
            for key, value in query.items()
        )

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        del session

        for row in self.rows:
            if self._matches(
                row,
                query,
            ):
                return deepcopy(row)

        return None

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> list[dict[str, object]]:
        del session

        return [
            deepcopy(row)
            for row in self.rows
            if self._matches(
                row,
                query,
            )
        ]

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: object,
    ) -> object:
        assert session is not None

        self.rows.append(
            deepcopy(document)
        )

        return object()


def active(
    *,
    assignment_id: str = "assignment-a",
    principal_id: str = "principal-a",
) -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(
        assignment_id=assignment_id,
        principal_id=principal_id,
        permission_id=PERMISSION,
        assigned_by_principal_id="grantor-a",
        assigned_at=NOW,
        assignment_evidence_reference=
            "assignment-evidence",
    )


def registry() -> tuple[
    SystemPermissionAssignmentRegistry,
    FakeCollection,
]:
    collection = FakeCollection()

    return (
        SystemPermissionAssignmentRegistry(
            collection
        ),
        collection,
    )


def test_index_contract_is_revisioned_and_has_no_ttl() -> None:
    value, collection = registry()

    value.ensure_indexes()

    by_name = {
        name: (
            keys,
            unique,
        )
        for keys, unique, name
        in collection.indexes
    }

    assert set(by_name) == {
        ASSIGNMENT_REVISION_INDEX,
        SCOPE_OPERATION_IDEMPOTENCY_INDEX,
        SCOPE_HISTORY_INDEX,
    }

    assert by_name[
        ASSIGNMENT_REVISION_INDEX
    ] == (
        [
            ("assignment_id", 1),
            ("revision", 1),
        ],
        True,
    )

    assert by_name[
        SCOPE_OPERATION_IDEMPOTENCY_INDEX
    ] == (
        [
            ("principal_id", 1),
            ("permission_id", 1),
            (
                "_operation_idempotency_key",
                1,
            ),
        ],
        True,
    )

    assert by_name[
        SCOPE_HISTORY_INDEX
    ][1] is False


def test_active_create_hydrate_and_exact_replay() -> None:
    value, collection = registry()
    item = active()
    session = FakeSession()

    assert value.create_or_replay(
        item,
        idempotency_key="create-a",
        session=session,
    ) == item

    assert value.create_or_replay(
        item,
        idempotency_key="create-a",
        session=session,
    ) == item

    assert len(collection.rows) == 1

    assert isinstance(
        collection.rows[0]["assigned_at"],
        datetime,
    )

    assert value.get_history(
        item.assignment_id
    ) == (item,)


def test_divergent_replay_denied() -> None:
    value, collection = registry()

    value.create_or_replay(
        active(assignment_id="assignment-a"),
        idempotency_key="create-a",
        session=FakeSession(),
    )

    with pytest.raises(
        SystemPermissionAssignmentConflictError,
        match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY",
    ):
        value.create_or_replay(
            active(assignment_id="assignment-b"),
            idempotency_key="create-a",
            session=FakeSession(),
        )

    assert len(collection.rows) == 1


def test_assignment_id_collision_denied() -> None:
    value, collection = registry()

    value.create_or_replay(
        active(),
        idempotency_key="create-a",
        session=FakeSession(),
    )

    with pytest.raises(
        SystemPermissionAssignmentConflictError,
        match="ASSIGNMENT_ID_COLLISION",
    ):
        value.create_or_replay(
            active(principal_id="principal-b"),
            idempotency_key="create-b",
            session=FakeSession(),
        )

    assert len(collection.rows) == 1


def test_revocation_history_and_replay() -> None:
    value, collection = registry()

    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    revoked = first.revoke(
        revoked_by_principal_id="revoker-a",
        revoked_at=(
            NOW + timedelta(minutes=1)
        ),
        revocation_evidence_reference=
            "revocation",
    )

    assert value.revoke_or_replay(
        revoked,
        revocation_idempotency_key=
            "revoke-a",
        session=FakeSession(),
    ) == revoked

    assert value.revoke_or_replay(
        revoked,
        revocation_idempotency_key=
            "revoke-a",
        session=FakeSession(),
    ) == revoked

    assert value.get_history(
        first.assignment_id
    ) == (
        first,
        revoked,
    )

    assert len(collection.rows) == 2


def test_resolve_current_returns_active_only() -> None:
    value, _ = registry()

    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    assert value.resolve_current(
        principal_id="principal-a",
        permission_id=PERMISSION,
    ) == first

    revoked = first.revoke(
        revoked_by_principal_id="revoker-a",
        revoked_at=(
            NOW + timedelta(minutes=1)
        ),
        revocation_evidence_reference=
            "revocation",
    )

    value.revoke_or_replay(
        revoked,
        revocation_idempotency_key=
            "revoke-a",
        session=FakeSession(),
    )

    assert value.resolve_current(
        principal_id="principal-a",
        permission_id=PERMISSION,
    ) is None


def test_scope_isolation() -> None:
    value, _ = registry()

    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    assert value.resolve_current(
        principal_id="principal-b",
        permission_id=PERMISSION,
    ) is None


def test_identity_type_corruption_fails_closed() -> None:
    value, collection = registry()

    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    collection.rows[0][
        "assignment_id"
    ] = None

    with pytest.raises(
        SystemPermissionAssignmentPersistedInvalidError,
        match="PERSISTED_IDENTITY_INVALID",
    ):
        value.resolve_current(
            principal_id="principal-a",
            permission_id=PERMISSION,
        )


def test_write_requires_active_transaction() -> None:
    value, collection = registry()

    for session in (
        None,
        FakeSession(
            active=False
        ),
    ):
        with pytest.raises(
            SystemPermissionAssignmentTransactionRequiredError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            value.create_or_replay(
                active(),
                idempotency_key="create-a",
                session=session,
            )

    assert collection.rows == []


def test_default_bson_naive_datetime_normalizes_to_utc() -> None:
    value, collection = registry()

    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    assigned = collection.rows[0][
        "assigned_at"
    ]

    assert isinstance(
        assigned,
        datetime,
    )

    collection.rows[0][
        "assigned_at"
    ] = assigned.replace(
        tzinfo=None
    )

    loaded = value.get_history(
        first.assignment_id
    )[0]

    assert loaded.assigned_at.tzinfo is timezone.utc


@pytest.mark.parametrize(
    ("field", "corrupt"),
    (
        ("status", "BROKEN"),
        ("assigned_at", "not-time"),
        ("revision", 7),
        (
            "assignment_fingerprint",
            "0" * 128,
        ),
    ),
)
def test_corrupt_persisted_material_rejects(
    field: str,
    corrupt: object,
) -> None:
    value, collection = registry()

    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    collection.rows[0][
        field
    ] = corrupt

    with pytest.raises(
        SystemPermissionAssignmentPersistedInvalidError
    ):
        value.get_history(
            first.assignment_id
        )


def test_corrupt_chain_rejects() -> None:
    value, collection = registry()

    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    revoked = first.revoke(
        revoked_by_principal_id="revoker-a",
        revoked_at=(
            NOW + timedelta(minutes=1)
        ),
        revocation_evidence_reference=
            "revocation",
    )

    value.revoke_or_replay(
        revoked,
        revocation_idempotency_key=
            "revoke-a",
        session=FakeSession(),
    )

    collection.rows[1][
        "previous_assignment_fingerprint"
    ] = "c" * 128

    with pytest.raises(
        SystemPermissionAssignmentPersistedInvalidError
    ):
        value.get_history(
            first.assignment_id
        )


def test_no_authorization_or_mutation_surface() -> None:
    value, _ = registry()

    for forbidden in (
        "delete",
        "purge",
        "authorize",
        "is_authorized",
        "assign_permission",
        "revoke_permission",
        "activate",
        "issue_activation",
        "resolve_principal",
    ):
        assert not hasattr(
            value,
            forbidden,
        )


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/unit/test_system_permission_assignment_registry.py
# VERSION: v1.0.0-P4-R4-D7-SYSTEM-PERMISSION-ASSIGNMENT-REGISTRY-CERT
# CURRENT PRINCIPAL AUTHORITY: NONE
# FINAL PERMISSION AUTHORIZATION: NONE
# ASSIGNMENT COMMAND AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# P5 PRIVILEGED USE AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
