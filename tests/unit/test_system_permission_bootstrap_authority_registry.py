"""
TITLE:
    WILSY OS System Permission Bootstrap Authority Registry Direct Certificate
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.auth.system_permission_bootstrap_authority import (
    SystemPermissionBootstrapAuthority,
    SystemPermissionBootstrapAuthorityStatus,
)

from tools.eos.auth.system_permission_bootstrap_authority_registry import (
    SystemPermissionBootstrapAuthorityConflictError,
    SystemPermissionBootstrapAuthorityPersistedInvalidError,
    SystemPermissionBootstrapAuthorityRegistry,
    SystemPermissionBootstrapAuthorityTransactionRequiredError,
)


NOW = datetime(
    2026,
    10,
    14,
    20,
    0,
    tzinfo=timezone.utc,
)

ASSIGN_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_ASSIGNMENT_COMMAND_AUTHORITY"
)

REVOKE_PURPOSE = (
    "SEED_SYSTEM_PERMISSION_REVOCATION_COMMAND_AUTHORITY"
)


class FakeSession:
    in_transaction = True


class NoTransaction:
    in_transaction = False


def _sortable(
    row: dict[str, object],
    name: str,
) -> tuple[int, int, str]:
    value = row.get(name)

    if isinstance(value, bool):
        return (0, int(value), "")

    if isinstance(value, int):
        return (1, value, "")

    if isinstance(value, str):
        return (2, 0, value)

    if isinstance(value, datetime):
        return (
            3,
            0,
            value.isoformat(),
        )

    if value is None:
        return (4, 0, "")

    return (
        5,
        0,
        repr(value),
    )


class FakeCursor:
    def __init__(
        self,
        rows: list[dict[str, object]],
    ) -> None:
        self.rows = rows

    def sort(
        self,
        key: str | list[tuple[str, int]],
        direction: int | None = None,
    ) -> FakeCursor:
        if isinstance(key, list):
            for name, order in reversed(key):
                self.rows.sort(
                    key=lambda row: _sortable(
                        row,
                        name,
                    ),
                    reverse=(order == -1),
                )
            return self

        self.rows.sort(
            key=lambda row: _sortable(
                row,
                key,
            ),
            reverse=(direction == -1),
        )

        return self

    def __iter__(self):
        return iter(self.rows)


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[
            dict[str, object]
        ] = []

        self.indexes: list[
            tuple[
                object,
                bool,
                str,
            ]
        ] = []

    def create_index(
        self,
        keys: object,
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append(
            (
                keys,
                unique,
                name,
            )
        )
        return name

    def insert_one(
        self,
        row: dict[str, object],
        *,
        session: object,
    ) -> object:
        self.rows.append(dict(row))
        return object()

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
        sort: list[tuple[str, int]] | None = None,
    ) -> dict[str, object] | None:
        matches = [
            row
            for row in self.rows
            if all(
                row.get(name) == expected
                for name, expected in query.items()
            )
        ]

        if not matches:
            return None

        if sort is not None:
            for name, order in reversed(sort):
                matches.sort(
                    key=lambda row: _sortable(
                        row,
                        name,
                    ),
                    reverse=(order == -1),
                )

        return dict(matches[0])

    def find(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> FakeCursor:
        return FakeCursor(
            [
                dict(row)
                for row in self.rows
                if all(
                    row.get(name) == expected
                    for name, expected in query.items()
                )
            ]
        )


def active(
    *,
    bootstrap_id: str = "bootstrap-a",
    actor: str = "principal-a",
    purpose: str = ASSIGN_PURPOSE,
    evidence: str = "install-evidence-a",
) -> SystemPermissionBootstrapAuthority:
    return SystemPermissionBootstrapAuthority.issue(
        bootstrap_id=bootstrap_id,
        actor_principal_id=actor,
        purpose=purpose,
        evidence_reference=evidence,
        issued_at=NOW,
    )


def registry() -> tuple[
    SystemPermissionBootstrapAuthorityRegistry,
    FakeCollection,
]:
    collection = FakeCollection()

    return (
        SystemPermissionBootstrapAuthorityRegistry(
            collection
        ),
        collection,
    )


def test_index_contract_no_ttl() -> None:
    value, collection = registry()

    value.ensure_indexes()

    assert len(collection.indexes) == 4

    names = {
        name
        for _, _, name
        in collection.indexes
    }

    assert names == {
        "system_permission_bootstrap_revision_unique",
        "system_permission_bootstrap_scope_operation_idempotency_unique",
        "system_permission_bootstrap_principal_purpose_history",
        "system_permission_bootstrap_status_issued_timeline",
    }

    assert all(
        "expire" not in name.lower()
        for name in names
    )


def test_active_create_hydrate_and_exact_replay() -> None:
    value, collection = registry()
    first = active()

    created = value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    replay = value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    assert created == replay == first
    assert len(collection.rows) == 1
    assert value.get_history(
        first.bootstrap_id
    ) == (first,)


def test_divergent_create_replay_denied() -> None:
    value, _ = registry()

    value.create_or_replay(
        active(),
        idempotency_key="create-a",
        session=FakeSession(),
    )

    with pytest.raises(
        SystemPermissionBootstrapAuthorityConflictError,
        match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY",
    ):
        value.create_or_replay(
            active(
                bootstrap_id="bootstrap-b",
            ),
            idempotency_key="create-a",
            session=FakeSession(),
        )


def test_bootstrap_id_collision_denied() -> None:
    value, _ = registry()

    value.create_or_replay(
        active(),
        idempotency_key="create-a",
        session=FakeSession(),
    )

    with pytest.raises(
        SystemPermissionBootstrapAuthorityConflictError,
        match="BOOTSTRAP_ID_COLLISION",
    ):
        value.create_or_replay(
            active(
                actor="principal-b",
            ),
            idempotency_key="create-b",
            session=FakeSession(),
        )


def test_active_to_retired_history_and_exact_replay() -> None:
    value, collection = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    retired = first.retire(
        retired_at=(
            NOW + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    created = value.retire_or_replay(
        retired,
        retirement_idempotency_key="retire-a",
        session=FakeSession(),
    )

    replay = value.retire_or_replay(
        retired,
        retirement_idempotency_key="retire-a",
        session=FakeSession(),
    )

    assert created == replay == retired
    assert len(collection.rows) == 2

    assert value.get_history(
        first.bootstrap_id
    ) == (
        first,
        retired,
    )


def test_divergent_retire_replay_denied() -> None:
    value, _ = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    retired = first.retire(
        retired_at=(
            NOW + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    value.retire_or_replay(
        retired,
        retirement_idempotency_key="retire-a",
        session=FakeSession(),
    )

    divergent = first.retire(
        retired_at=(
            NOW + timedelta(minutes=2)
        ),
        retirement_evidence_reference="retire-b",
    )

    with pytest.raises(
        SystemPermissionBootstrapAuthorityConflictError,
        match="IDEMPOTENCY_KEY_DIVERGENT_REPLAY",
    ):
        value.retire_or_replay(
            divergent,
            retirement_idempotency_key="retire-a",
            session=FakeSession(),
        )


def test_retired_terminal() -> None:
    value, _ = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    retired = first.retire(
        retired_at=(
            NOW + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    value.retire_or_replay(
        retired,
        retirement_idempotency_key="retire-a",
        session=FakeSession(),
    )

    later = first.retire(
        retired_at=(
            NOW + timedelta(minutes=2)
        ),
        retirement_evidence_reference="retire-b",
    )

    with pytest.raises(
        SystemPermissionBootstrapAuthorityConflictError,
        match="BOOTSTRAP_AUTHORITY_TERMINAL",
    ):
        value.retire_or_replay(
            later,
            retirement_idempotency_key="retire-b",
            session=FakeSession(),
        )


def test_resolve_current_active_and_retired_none() -> None:
    value, _ = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    assert value.resolve_current(
        actor_principal_id="principal-a",
        purpose=ASSIGN_PURPOSE,
    ) == first

    retired = first.retire(
        retired_at=(
            NOW + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    value.retire_or_replay(
        retired,
        retirement_idempotency_key="retire-a",
        session=FakeSession(),
    )

    assert value.resolve_current(
        actor_principal_id="principal-a",
        purpose=ASSIGN_PURPOSE,
    ) is None


def test_actor_and_purpose_scope_isolation() -> None:
    value, _ = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    assert value.resolve_current(
        actor_principal_id="principal-b",
        purpose=ASSIGN_PURPOSE,
    ) is None

    assert value.resolve_current(
        actor_principal_id="principal-a",
        purpose=REVOKE_PURPOSE,
    ) is None


@pytest.mark.parametrize(
    ("field", "corrupt"),
    (
        ("status", "BROKEN"),
        ("issued_at", "not-time"),
        ("revision", 7),
        (
            "authority_fingerprint",
            "0" * 128,
        ),
    ),
)
def test_corrupt_persisted_material_fails_closed(
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

    collection.rows[0][field] = corrupt

    with pytest.raises(
        SystemPermissionBootstrapAuthorityPersistedInvalidError
    ):
        value.get_history(
            first.bootstrap_id
        )


def test_corrupt_revision_chain_fails_closed() -> None:
    value, collection = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    retired = first.retire(
        retired_at=(
            NOW + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    value.retire_or_replay(
        retired,
        retirement_idempotency_key="retire-a",
        session=FakeSession(),
    )

    collection.rows[1][
        "previous_fingerprint"
    ] = "c" * 128

    with pytest.raises(
        SystemPermissionBootstrapAuthorityPersistedInvalidError
    ):
        value.get_history(
            first.bootstrap_id
        )


def test_binding_change_corruption_fails_closed() -> None:
    value, collection = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    retired = first.retire(
        retired_at=(
            NOW + timedelta(minutes=1)
        ),
        retirement_evidence_reference="retire-a",
    )

    value.retire_or_replay(
        retired,
        retirement_idempotency_key="retire-a",
        session=FakeSession(),
    )

    collection.rows[1][
        "actor_principal_id"
    ] = "principal-b"

    with pytest.raises(
        SystemPermissionBootstrapAuthorityPersistedInvalidError
    ):
        value.get_history(
            first.bootstrap_id
        )


def test_default_bson_naive_utc_normalizes() -> None:
    value, collection = registry()
    first = active()

    value.create_or_replay(
        first,
        idempotency_key="create-a",
        session=FakeSession(),
    )

    collection.rows[0][
        "issued_at"
    ] = NOW.replace(
        tzinfo=None
    )

    history = value.get_history(
        first.bootstrap_id
    )

    assert (
        history[0].issued_at.tzinfo
        is timezone.utc
    )


@pytest.mark.parametrize(
    "session",
    (
        None,
        NoTransaction(),
    ),
)
def test_write_requires_active_transaction(
    session: object,
) -> None:
    value, collection = registry()

    with pytest.raises(
        SystemPermissionBootstrapAuthorityTransactionRequiredError,
        match="ACTIVE_TRANSACTION_REQUIRED",
    ):
        value.create_or_replay(
            active(),
            idempotency_key="create-a",
            session=session,
        )

    assert collection.rows == []


def test_no_delete_ttl_or_authorization_surface() -> None:
    value, _ = registry()

    for forbidden in (
        "delete",
        "purge",
        "authorize",
        "is_authorized",
        "grant_permission",
        "revoke_permission",
        "assign_permission",
        "issue_activation",
        "break_glass",
        "execute_financial",
        "resolve_principal",
    ):
        assert not hasattr(
            value,
            forbidden,
        )


def test_fake_cursor_typing_is_semantically_ordered() -> None:
    cursor = FakeCursor(
        [
            {
                "bootstrap_id": "b",
                "revision": 2,
            },
            {
                "bootstrap_id": "a",
                "revision": 2,
            },
            {
                "bootstrap_id": "a",
                "revision": 1,
            },
        ]
    )

    ordered = list(
        cursor.sort(
            [
                ("bootstrap_id", 1),
                ("revision", 1),
            ]
        )
    )

    assert [
        (
            row["bootstrap_id"],
            row["revision"],
        )
        for row in ordered
    ] == [
        ("a", 1),
        ("a", 2),
        ("b", 2),
    ]


# =============================================================================
# WILSY OS TEST ARTIFACT SEAL
# ARTIFACT: tests/unit/test_system_permission_bootstrap_authority_registry.py
# VERSION: v1.0.0-P4-R4-D11-R2-R1-BOOTSTRAP-AUTHORITY-REGISTRY-CERT
# TYPED FAKE COLLECTION: YES
# PERSISTENCE AUTHORITY ONLY: YES
# CREATION POLICY AUTHORITY: NONE
# OFFLINE INSTALLATION TRUST AUTHORITY: NONE
# SYSTEM PERMISSION GRANT AUTHORITY: NONE
# SYSTEM PERMISSION REVOCATION AUTHORITY: NONE
# ASSIGNMENT COMMAND AUTHORITY: NONE
# REVOCATION COMMAND AUTHORITY: NONE
# PRIVILEGED ACTIVATION AUTHORITY: NONE
# BREAK-GLASS AUTHORITY: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS TEST ARTIFACT
