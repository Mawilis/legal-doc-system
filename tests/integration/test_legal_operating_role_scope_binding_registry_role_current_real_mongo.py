"""
TITLE: WILSY OS CX27 Scope Role-Indexed Current Read Real-Mongo Certificate

VERSION: v1.0.0-PW-P6F-SCOPE-ROLE-CURRENT-REAL-MONGO

EPITOME:
    Certify the exact role-revision-indexed effective-current scope read
    against a real transactional Mongo replica set.

AUTHORITY BOUNDARY:
    Scope metadata is descriptive only. It establishes no record, client,
    matter, IAM, assignment, supervision, workflow, or financial authority.

CURRENTNESS:
    Derived from immutable per-binding revision histories. No mutable pointer.

TRANSACTION:
    Caller owns one already-active Mongo transaction.
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.domain.legal_operating_role_scope_binding import (
    LegalOperatingRoleScopeBinding,
)
from tools.eos.legal_operations.registry.legal_operating_role_scope_binding_registry import (
    LegalOperatingRoleScopeBindingRegistry,
    RegistryPersistedRecordInvalidError,
    RegistryTransactionRequiredError,
)


URI = os.environ[
    "WILSY_PW_P6F_REAL_MONGO_URI"
]

NOW = datetime(
    2026,
    10,
    15,
    18,
    0,
    tzinfo=UTC,
)

TENANT = "tenant-p6f"
ROLE = "role-global-specialist"
ROLE_REVISION = 7


@pytest.fixture()
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
        uuidRepresentation="standard",
    )

    client.admin.command(
        "ping"
    )

    database = client[
        "wilsy_pw_p6f_"
        + uuid.uuid4().hex
    ]

    collection = database[
        "legal_operating_role_scope_bindings"
    ]

    registry = (
        LegalOperatingRoleScopeBindingRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    try:
        yield (
            client,
            database,
            collection,
            registry,
        )
    finally:
        client.drop_database(
            database.name
        )
        client.close()


def _binding(
    binding_id: str,
    binding_revision: int,
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    office_references: tuple[str, ...] = (
        "office:jhb",
    ),
    practice_references: tuple[str, ...] = (),
    business_unit_references: tuple[str, ...] = (),
    jurisdiction_references: tuple[str, ...] = (),
    effective_from: datetime = NOW,
    supersedes_fingerprint: str | None = None,
) -> LegalOperatingRoleScopeBinding:
    return LegalOperatingRoleScopeBinding(
        tenant_id=tenant_id,
        scope_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        scope_binding_revision=binding_revision,
        office_references=office_references,
        practice_references=practice_references,
        business_unit_references=business_unit_references,
        jurisdiction_references=jurisdiction_references,
        effective_from=effective_from,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def _persist(
    client: MongoClient[Any],
    registry: LegalOperatingRoleScopeBindingRegistry,
    value: LegalOperatingRoleScopeBinding,
) -> LegalOperatingRoleScopeBinding:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_revision(
                value,
                session=session,
            )


def _current(
    client: MongoClient[Any],
    registry: LegalOperatingRoleScopeBindingRegistry,
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    at: datetime = NOW,
) -> tuple[
    LegalOperatingRoleScopeBinding,
    ...
]:
    with client.start_session() as session:
        with session.start_transaction():
            return (
                registry.list_current_for_operating_role_revision(
                    tenant_id,
                    role_id,
                    role_revision,
                    at,
                    session=session,
                )
            )


def test_real_role_history_index_and_no_ttl(
    mongo_context: Any,
) -> None:
    _, _, collection, _ = mongo_context

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    assert (
        "legal_operating_role_scope_role_history"
        in indexes
    )

    role_index = indexes[
        "legal_operating_role_scope_role_history"
    ]

    assert dict(
        role_index["key"]
    ) == {
        "tenant_id": 1,
        "operating_role_id": 1,
        "operating_role_revision": 1,
        "scope_binding_revision": 1,
    }

    assert all(
        "expireAfterSeconds" not in item
        for item in indexes.values()
    )


def test_real_active_transaction_required(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    with pytest.raises(
        RegistryTransactionRequiredError,
        match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
    ):
        registry.list_current_for_operating_role_revision(
            TENANT,
            ROLE,
            ROLE_REVISION,
            NOW,
            session=None,
        )

    with client.start_session() as session:
        with pytest.raises(
            RegistryTransactionRequiredError,
            match="ACTIVE_CALLER_TRANSACTION_REQUIRED",
        ):
            registry.list_current_for_operating_role_revision(
                TENANT,
                ROLE,
                ROLE_REVISION,
                NOW,
                session=session,
            )


def test_real_multiple_independent_scope_chains(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    office = _binding(
        "scope-binding-office",
        1,
        office_references=(
            "office:jhb",
        ),
    )

    practice = _binding(
        "scope-binding-practice",
        1,
        office_references=(),
        practice_references=(
            "practice:disputes",
        ),
    )

    _persist(
        client,
        registry,
        practice,
    )

    _persist(
        client,
        registry,
        office,
    )

    current = _current(
        client,
        registry,
    )

    assert tuple(
        item.scope_binding_id
        for item in current
    ) == (
        "scope-binding-office",
        "scope-binding-practice",
    )


def test_real_successor_temporal_currentness_per_chain(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    first = _binding(
        "scope-binding-a",
        1,
        office_references=(
            "office:jhb",
        ),
    )

    _persist(
        client,
        registry,
        first,
    )

    second = _binding(
        "scope-binding-a",
        2,
        office_references=(
            "office:jhb",
            "office:cpt",
        ),
        effective_from=(
            NOW
            + timedelta(hours=1)
        ),
        supersedes_fingerprint=first.fingerprint,
    )

    _persist(
        client,
        registry,
        second,
    )

    before = _current(
        client,
        registry,
        at=NOW + timedelta(minutes=30),
    )

    after = _current(
        client,
        registry,
        at=NOW + timedelta(hours=2),
    )

    assert before == (
        first,
    )

    assert after == (
        second,
    )


def test_real_exact_role_revision_and_tenant_isolation(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    matching = _binding(
        "scope-binding-match",
        1,
        office_references=(),
        practice_references=(
            "practice:disputes",
        ),
    )

    old_role_revision = _binding(
        "scope-binding-old-revision",
        1,
        office_references=(
            "office:cpt",
        ),
        role_revision=6,
    )

    other_role = _binding(
        "scope-binding-other-role",
        1,
        office_references=(),
        jurisdiction_references=(
            "jurisdiction:ZA",
        ),
        role_id="role-other",
    )

    for value in (
        matching,
        old_role_revision,
        other_role,
    ):
        _persist(
            client,
            registry,
            value,
        )

    assert _current(
        client,
        registry,
    ) == (
        matching,
    )

    assert _current(
        client,
        registry,
        tenant_id="tenant-neighbor",
    ) == ()

    assert _current(
        client,
        registry,
        role_revision=6,
    ) == (
        old_role_revision,
    )


def test_real_future_initial_scope_chain_excluded_until_effective(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    future = _binding(
        "scope-binding-future",
        1,
        office_references=(),
        business_unit_references=(
            "business-unit:africa",
        ),
        effective_from=(
            NOW
            + timedelta(hours=1)
        ),
    )

    _persist(
        client,
        registry,
        future,
    )

    assert _current(
        client,
        registry,
        at=NOW,
    ) == ()

    assert _current(
        client,
        registry,
        at=NOW + timedelta(hours=2),
    ) == (
        future,
    )


def test_real_all_scope_dimensions_survive_current_read(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    value = _binding(
        "scope-binding-all",
        1,
        office_references=(
            "office:jhb",
        ),
        practice_references=(
            "practice:disputes",
        ),
        business_unit_references=(
            "business-unit:africa",
        ),
        jurisdiction_references=(
            "jurisdiction:ZA",
        ),
    )

    _persist(
        client,
        registry,
        value,
    )

    current = _current(
        client,
        registry,
    )

    assert current == (
        value,
    )

    assert current[0].office_references == (
        "office:jhb",
    )

    assert current[0].practice_references == (
        "practice:disputes",
    )

    assert (
        current[0].business_unit_references
        == (
            "business-unit:africa",
        )
    )

    assert current[0].jurisdiction_references == (
        "jurisdiction:ZA",
    )


def test_real_corrupt_persisted_row_rejected(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    valid = _binding(
        "scope-binding-corrupt",
        1,
    )

    _persist(
        client,
        registry,
        valid,
    )

    result = collection.update_one(
        {
            "tenant_id": TENANT,
            "scope_binding_id":
                valid.scope_binding_id,
            "scope_binding_revision": 1,
        },
        {
            "$set": {
                "fingerprint":
                    "0" * 128,
            }
        },
    )

    assert result.modified_count == 1

    with pytest.raises(
        RegistryPersistedRecordInvalidError,
        match="PERSISTED_RECORD_INVALID",
    ):
        _current(
            client,
            registry,
        )


# AUTHORITY BOUNDARY:
# read-only current organizational-scope metadata.
# No record/client/matter/IAM/assignment/supervision/workflow/financial authority.
