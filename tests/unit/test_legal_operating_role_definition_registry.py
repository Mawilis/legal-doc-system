from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError


NOW = datetime(
    2026,
    10,
    13,
    12,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


class ActiveSession:
    in_transaction = True


class InactiveSession:
    in_transaction = False


class Cursor:
    def __init__(
        self,
        rows: list[
            dict[str, object]
        ],
    ) -> None:
        self._rows = rows

    def sort(
        self,
        field: str,
        direction: int,
    ) -> "Cursor":
        def revision_key(
            row: dict[str, object],
        ) -> int:
            value = row.get(field)

            if (
                isinstance(value, bool)
                or not isinstance(value, int)
            ):
                raise TypeError(
                    "TEST_CURSOR_REVISION_KEY_NOT_INT"
                )

            return value

        self._rows.sort(
            key=revision_key,
            reverse=direction < 0,
        )

        return self

    def __iter__(self):
        return iter(
            self._rows
        )


class Collection:
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
                deepcopy(keys),
                unique,
                name,
            )
        )

        return name

    def find_one(
        self,
        query: dict[
            str,
            object,
        ],
        *,
        session: Any = None,
    ) -> dict[
        str,
        object,
    ] | None:
        del session

        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value
                in query.items()
            ):
                return deepcopy(row)

        return None

    def find(
        self,
        query: dict[
            str,
            object,
        ],
        *,
        session: Any = None,
    ) -> Cursor:
        del session

        return Cursor(
            [
                deepcopy(row)
                for row in self.rows
                if all(
                    row.get(key) == value
                    for key, value
                    in query.items()
                )
            ]
        )

    def insert_one(
        self,
        document: dict[
            str,
            object,
        ],
        *,
        session: Any = None,
    ) -> object:
        del session

        tenant = document["tenant_id"]

        if (
            "principal_operating_role_binding_id"
            in document
        ):
            identity_field = (
                "principal_operating_role_binding_id"
            )
            revision_field = (
                "binding_revision"
            )

        elif (
            "capability_binding_id"
            in document
        ):
            identity_field = (
                "capability_binding_id"
            )
            revision_field = (
                "capability_binding_revision"
            )

        elif (
            "scope_binding_id"
            in document
        ):
            identity_field = (
                "scope_binding_id"
            )
            revision_field = (
                "scope_binding_revision"
            )

        else:
            identity_field = (
                "operating_role_id"
            )
            revision_field = (
                "role_revision"
            )

        for row in self.rows:
            if (
                row.get("tenant_id")
                == tenant
                and row.get(identity_field)
                == document[identity_field]
                and row.get(revision_field)
                == document[revision_field]
            ):
                raise DuplicateKeyError(
                    "identity"
                )

            if (
                row.get("tenant_id")
                == tenant
                and row.get("fingerprint")
                == document["fingerprint"]
            ):
                raise DuplicateKeyError(
                    "fingerprint"
                )

        self.rows.append(
            deepcopy(document)
        )

        return object()

from dataclasses import replace

from tools.eos.legal_operations.domain.legal_operating_role_definition import (
    LegalOperatingRoleDefinition,
)
from tools.eos.legal_operations.registry.legal_operating_role_definition_registry import (
    LegalOperatingRoleDefinitionRegistry,
    RegistryConflictError,
    RegistryTransactionRequiredError,
)


def make_role(
    *,
    revision: int = 1,
    when: datetime = NOW,
    predecessor: str | None = None,
) -> LegalOperatingRoleDefinition:
    return LegalOperatingRoleDefinition(
        tenant_id="tenant-a",
        operating_role_id="role-1",
        role_revision=revision,
        display_name=f"Role {revision}",
        description="Configured role",
        effective_from=when,
        supersedes_fingerprint=predecessor,
    )


def test_indexes_and_no_ttl() -> None:
    collection = Collection()
    registry = LegalOperatingRoleDefinitionRegistry(
        collection
    )

    registry.ensure_indexes()

    assert len(
        collection.indexes
    ) >= 4

    assert all(
        "expireAfterSeconds"
        not in repr(index)
        for index in collection.indexes
    )


def test_create_replay_and_currentness() -> None:
    collection = Collection()
    registry = LegalOperatingRoleDefinitionRegistry(
        collection
    )
    tx = ActiveSession()

    first = make_role()

    assert (
        registry.persist_revision(
            first,
            session=tx,
        )
        == first
    )

    assert (
        registry.persist_revision(
            first,
            session=tx,
        )
        == first
    )

    second = make_role(
        revision=2,
        when=NOW + timedelta(days=1),
        predecessor=first.fingerprint,
    )

    assert (
        registry.persist_revision(
            second,
            session=tx,
        )
        == second
    )

    assert (
        registry.resolve_current(
            "tenant-a",
            "role-1",
            NOW,
            session=tx,
        )
        == first
    )

    assert (
        registry.resolve_current(
            "tenant-a",
            "role-1",
            NOW + timedelta(days=2),
            session=tx,
        )
        == second
    )


def test_divergence_gap_and_transaction_reject() -> None:
    collection = Collection()
    registry = LegalOperatingRoleDefinitionRegistry(
        collection
    )
    tx = ActiveSession()

    first = make_role()

    registry.persist_revision(
        first,
        session=tx,
    )

    divergent = replace(
        first,
        display_name="Different",
        fingerprint="",
    )

    with pytest.raises(
        RegistryConflictError
    ):
        registry.persist_revision(
            divergent,
            session=tx,
        )

    with pytest.raises(
        RegistryConflictError
    ):
        registry.persist_revision(
            make_role(
                revision=3,
                when=NOW + timedelta(days=3),
                predecessor=first.fingerprint,
            ),
            session=tx,
        )

    with pytest.raises(
        RegistryTransactionRequiredError
    ):
        registry.get_history(
            "tenant-a",
            "role-1",
            session=InactiveSession(),
        )

def test_index_contract_has_no_duplicate_key_option_signature() -> None:
    """Reject Mongo-equivalent duplicate indexes with different names."""
    collection = Collection()
    registry = LegalOperatingRoleDefinitionRegistry(collection)

    registry.ensure_indexes()

    signatures: set[tuple[str, bool]] = set()
    names: set[str] = set()

    for keys, unique, name in collection.indexes:
        signature = (
            repr(keys),
            unique,
        )

        assert signature not in signatures
        signatures.add(signature)
        names.add(name)

    assert len(collection.indexes) == 4

    assert names == {
        "legal_operating_role_definitions_identity_unique",
        "legal_operating_role_definitions_fingerprint_unique",
        "legal_operating_role_definitions_history",
        "legal_operating_role_definitions_currentness",
    }

    assert (
        "legal_operating_role_definition_role_history"
        not in names
    )
