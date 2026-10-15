"""
TITLE: WILSY OS CX27 Capability Role-Indexed Current Read Real-Mongo Certificate

VERSION: v1.0.0-PW-P6C-CAPABILITY-ROLE-CURRENT-REAL-MONGO

EPITOME:
    Certify the role-revision-indexed effective-current capability read against
    a real transactional Mongo replica set.

AUTHORITY BOUNDARY:
    Capability association metadata only. No IAM permission possession,
    assignment, supervision, workflow, matter-access, or financial authority.

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

from tools.eos.legal_operations.domain.legal_operating_role_capability_binding import (
    LegalOperatingRoleCapabilityBinding,
)
from tools.eos.legal_operations.registry.legal_operating_role_capability_binding_registry import (
    LegalOperatingRoleCapabilityBindingRegistry,
    RegistryPersistedRecordInvalidError,
    RegistryTransactionRequiredError,
)


URI = os.environ[
    "WILSY_PW_P6C_REAL_MONGO_URI"
]

NOW = datetime(
    2026,
    10,
    15,
    18,
    0,
    tzinfo=UTC,
)

TENANT = "tenant-p6c"
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
        "wilsy_pw_p6c_"
        + uuid.uuid4().hex
    ]

    collection = database[
        "legal_operating_role_capability_bindings"
    ]

    registry = (
        LegalOperatingRoleCapabilityBindingRegistry(
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
    capability_ids: tuple[str, ...],
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    effective_from: datetime = NOW,
    supersedes_fingerprint: str | None = None,
) -> LegalOperatingRoleCapabilityBinding:
    return LegalOperatingRoleCapabilityBinding(
        tenant_id=tenant_id,
        capability_binding_id=binding_id,
        operating_role_id=role_id,
        operating_role_revision=role_revision,
        capability_binding_revision=binding_revision,
        capability_ids=capability_ids,
        effective_from=effective_from,
        supersedes_fingerprint=supersedes_fingerprint,
    )


def _persist(
    client: MongoClient[Any],
    registry: LegalOperatingRoleCapabilityBindingRegistry,
    value: LegalOperatingRoleCapabilityBinding,
) -> LegalOperatingRoleCapabilityBinding:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_revision(
                value,
                session=session,
            )


def _current(
    client: MongoClient[Any],
    registry: LegalOperatingRoleCapabilityBindingRegistry,
    *,
    tenant_id: str = TENANT,
    role_id: str = ROLE,
    role_revision: int = ROLE_REVISION,
    at: datetime = NOW,
) -> tuple[
    LegalOperatingRoleCapabilityBinding,
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
        "legal_operating_role_capability_role_history"
        in indexes
    )

    role_index = indexes[
        "legal_operating_role_capability_role_history"
    ]

    assert dict(
        role_index["key"]
    ) == {
        "tenant_id": 1,
        "operating_role_id": 1,
        "operating_role_revision": 1,
        "capability_binding_revision": 1,
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


def test_real_multiple_independent_binding_chains(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    alpha = _binding(
        "capability-binding-a",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    zulu = _binding(
        "capability-binding-z",
        1,
        (
            "PRACTICE_CORPORATE",
        ),
    )

    _persist(
        client,
        registry,
        zulu,
    )

    _persist(
        client,
        registry,
        alpha,
    )

    current = _current(
        client,
        registry,
    )

    assert tuple(
        item.capability_binding_id
        for item in current
    ) == (
        "capability-binding-a",
        "capability-binding-z",
    )


def test_real_successor_temporal_currentness_per_chain(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    first = _binding(
        "capability-binding-a",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    _persist(
        client,
        registry,
        first,
    )

    second = _binding(
        "capability-binding-a",
        2,
        (
            "PRACTICE_DISPUTES",
            "PRACTICE_CORPORATE",
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
        "capability-binding-match",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    old_role_revision = _binding(
        "capability-binding-old-revision",
        1,
        (
            "PRACTICE_CORPORATE",
        ),
        role_revision=6,
    )

    other_role = _binding(
        "capability-binding-other-role",
        1,
        (
            "PRACTICE_DISPUTES",
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


def test_real_future_initial_chain_excluded_until_effective(
    mongo_context: Any,
) -> None:
    client, _, _, registry = mongo_context

    future = _binding(
        "capability-binding-future",
        1,
        (
            "PRACTICE_DISPUTES",
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


def test_real_corrupt_persisted_row_rejected(
    mongo_context: Any,
) -> None:
    client, _, collection, registry = mongo_context

    valid = _binding(
        "capability-binding-corrupt",
        1,
        (
            "PRACTICE_DISPUTES",
        ),
    )

    _persist(
        client,
        registry,
        valid,
    )

    result = collection.update_one(
        {
            "tenant_id": TENANT,
            "capability_binding_id":
                valid.capability_binding_id,
            "capability_binding_revision": 1,
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
# read-only current capability association metadata.
# No IAM, assignment, supervision, workflow, matter, or financial authority.
