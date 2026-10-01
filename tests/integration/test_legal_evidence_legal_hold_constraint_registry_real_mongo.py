"""Real-Mongo certificate for the C4D4B legal-hold constraint registry.

TITLE: Legal Evidence Legal Hold Constraint Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D4B-R5-LEGAL-HOLD-REGISTRY-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Certify real transactional append-only legal-hold fact durability,
         immutable ACTIVE/RELEASED history, restart replay, rollback, tenant
         isolation, corruption rejection and retry semantics without deriving
         current state or granting later authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_legal_hold_constraint_registry_real_mongo.py
COLLABORATION / OWNERSHIP:
    Test-only real-Mongo certificate for frozen C4D4B-R3 production behavior.
CERTIFICATION / UPDATE DATE: 2026-10-01
CHANGELOG:
    v1.0.0 establishes real replica-set certification of exact indexes, active
    transaction enforcement, committed durability, restart replay, rollback,
    append-only hold history, tenant isolation, corruption rejection,
    duplicate-key whole-transaction retry and zero-TTL posture.
COMPLIANCE:
    Real Mongo durability certificate only.
SECURITY / PRIVACY POSTURE:
    UUID-isolated disposable database; synthetic opaque evidence only.
TENANT BOUNDARY:
    Every write/read/history query remains exact tenant scoped.
AUTHORITY BOUNDARY:
    Durable legal-hold fact persistence/history only; no current-state,
    issuance, release, retention, orphan, deletion or provider authority.
FINANCIAL AUTHORITY BOUNDARY:
    No financial authority; Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_evidence_legal_hold_constraint import (
    LegalEvidenceLegalHoldConstraint,
    LegalEvidenceLegalHoldState,
)
from tools.eos.legal_operations.registry.legal_evidence_legal_hold_constraint_registry import (
    COLLECTION,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_HOLD_HISTORY,
    INDEX_TENANT_HOLD_STATE_HISTORY,
    INDEX_TENANT_PROVIDER_OBJECT_HISTORY,
    LegalEvidenceLegalHoldConstraintConflictError,
    LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError,
    LegalEvidenceLegalHoldConstraintRegistry,
    LegalEvidenceLegalHoldConstraintTransactionRequiredError,
)


URI = os.environ.get(
    "WILSY_VENDOR_CERT_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

BASE = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)


@pytest.fixture
def mongo_context() -> Any:
    client = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
    )

    hello = client.admin.command(
        "hello"
    )

    assert hello.get(
        "setName"
    ) == "wilsyVendorCertRS"

    assert hello.get(
        "isWritablePrimary"
    ) is True

    database_name = (
        "wilsy_c4d4b_r5_"
        + uuid4().hex
    )

    assert database_name != "wilsy"

    database = client[
        database_name
    ]

    collection = database[
        COLLECTION
    ]

    try:
        yield (
            client,
            database,
            collection,
        )
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def _fact(
    *,
    tenant: str = "tenant-alpha",
    hold: str = "hold-alpha",
    provider: str = "s3",
    storage: str = "bucket-alpha",
    version: str = "object-v1",
    state: LegalEvidenceLegalHoldState = (
        LegalEvidenceLegalHoldState.ACTIVE
    ),
    released_at: datetime | None = None,
    imposed_at: datetime = BASE,
    source_reference: str = "source-alpha",
    source_fingerprint: str = "a" * 128,
) -> LegalEvidenceLegalHoldConstraint:
    return LegalEvidenceLegalHoldConstraint(
        tenant_id=tenant,
        provider_name=provider,
        storage_reference=storage,
        object_version_reference=version,
        hold_reference=hold,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=source_fingerprint,
        imposed_at=imposed_at,
        state=state,
        released_at=released_at,
    )


def _commit_fact(
    *,
    client: MongoClient[Any],
    registry: LegalEvidenceLegalHoldConstraintRegistry,
    value: LegalEvidenceLegalHoldConstraint,
) -> LegalEvidenceLegalHoldConstraint:
    with client.start_session() as session:
        session.start_transaction()

        persisted = registry.create_or_replay(
            value,
            session=session,
        )

        session.commit_transaction()

    return persisted


def test_real_topology_database_and_indexes(
    mongo_context: Any,
) -> None:
    client, database, collection = mongo_context

    hello = client.admin.command(
        "hello"
    )

    assert hello["setName"] == (
        "wilsyVendorCertRS"
    )

    assert hello[
        "isWritablePrimary"
    ] is True

    assert database.name.startswith(
        "wilsy_c4d4b_r5_"
    )

    assert database.name != "wilsy"

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
    }

    fingerprint = indexes[
        INDEX_TENANT_FINGERPRINT
    ]
    hold_history = indexes[
        INDEX_TENANT_HOLD_HISTORY
    ]
    object_history = indexes[
        INDEX_TENANT_PROVIDER_OBJECT_HISTORY
    ]
    state_history = indexes[
        INDEX_TENANT_HOLD_STATE_HISTORY
    ]

    assert fingerprint["key"] == {
        "tenant_id": 1,
        "fingerprint": 1,
    }
    assert fingerprint["unique"] is True

    assert hold_history["key"] == {
        "tenant_id": 1,
        "hold_reference": 1,
        "imposed_at": -1,
    }
    assert hold_history.get(
        "unique",
        False,
    ) is False

    assert object_history["key"] == {
        "tenant_id": 1,
        "provider_name": 1,
        "storage_reference": 1,
        "object_version_reference": 1,
        "imposed_at": -1,
    }
    assert object_history.get(
        "unique",
        False,
    ) is False

    assert state_history["key"] == {
        "tenant_id": 1,
        "hold_reference": 1,
        "state": 1,
        "imposed_at": -1,
    }
    assert state_history.get(
        "unique",
        False,
    ) is False

    assert all(
        "expireAfterSeconds"
        not in item
        for item in indexes.values()
    )


def test_real_inactive_transaction_rejects_before_write(
    mongo_context: Any,
) -> None:
    client, _, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    with client.start_session() as session:
        with pytest.raises(
            LegalEvidenceLegalHoldConstraintTransactionRequiredError
        ):
            registry.create_or_replay(
                _fact(),
                session=session,
            )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_commit_restart_replay_and_append_only_active_released_history(
    mongo_context: Any,
) -> None:
    client, database, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    active = _fact()

    released = _fact(
        state=LegalEvidenceLegalHoldState.RELEASED,
        released_at=BASE + timedelta(
            days=7
        ),
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=active,
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=released,
    )

    assert collection.count_documents(
        {
            "tenant_id":
                active.tenant_id,
            "hold_reference":
                active.hold_reference,
        }
    ) == 2

    database_name = database.name

    fresh_client = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
    )

    try:
        fresh_collection = fresh_client[
            database_name
        ][
            COLLECTION
        ]

        fresh_registry = (
            LegalEvidenceLegalHoldConstraintRegistry(
                fresh_collection
            )
        )

        with fresh_client.start_session() as session:
            session.start_transaction()

            replayed_active = (
                fresh_registry.create_or_replay(
                    active,
                    session=session,
                )
            )

            replayed_released = (
                fresh_registry.create_or_replay(
                    released,
                    session=session,
                )
            )

            by_fingerprint = (
                fresh_registry.get_by_fingerprint(
                    tenant_id=active.tenant_id,
                    fingerprint=active.fingerprint,
                    session=session,
                )
            )

            hold_history = (
                fresh_registry.list_hold_history(
                    tenant_id=active.tenant_id,
                    hold_reference=active.hold_reference,
                    session=session,
                )
            )

            object_history = (
                fresh_registry.list_provider_object_history(
                    tenant_id=active.tenant_id,
                    provider_name=active.provider_name,
                    storage_reference=active.storage_reference,
                    object_version_reference=(
                        active.object_version_reference
                    ),
                    session=session,
                )
            )

            session.commit_transaction()

        assert replayed_active == active
        assert replayed_released == released
        assert by_fingerprint == active
        assert set(hold_history) == {
            active,
            released,
        }
        assert set(object_history) == {
            active,
            released,
        }

        assert fresh_collection.count_documents(
            {
                "tenant_id":
                    active.tenant_id,
                "hold_reference":
                    active.hold_reference,
            }
        ) == 2

    finally:
        fresh_client.close()


def test_real_aborted_transaction_rolls_back(
    mongo_context: Any,
) -> None:
    client, _, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    value = _fact(
        hold="hold-rollback",
    )

    with client.start_session() as session:
        session.start_transaction()

        registry.create_or_replay(
            value,
            session=session,
        )

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id":
                value.tenant_id,
            "fingerprint":
                value.fingerprint,
        }
    ) == 0


def test_real_same_provider_object_accepts_multiple_distinct_hold_facts(
    mongo_context: Any,
) -> None:
    client, _, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    first = _fact(
        hold="hold-one",
    )

    second = _fact(
        hold="hold-two",
        source_reference="source-two",
        source_fingerprint="b" * 128,
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=first,
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=second,
    )

    with client.start_session() as session:
        session.start_transaction()

        history = (
            registry.list_provider_object_history(
                tenant_id=first.tenant_id,
                provider_name=first.provider_name,
                storage_reference=first.storage_reference,
                object_version_reference=(
                    first.object_version_reference
                ),
                session=session,
            )
        )

        session.commit_transaction()

    assert set(history) == {
        first,
        second,
    }


def test_real_cross_tenant_same_hold_and_provider_object_are_isolated(
    mongo_context: Any,
) -> None:
    client, _, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    left = _fact(
        tenant="tenant-left",
    )

    right = _fact(
        tenant="tenant-right",
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=left,
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=right,
    )

    with client.start_session() as session:
        session.start_transaction()

        left_history = (
            registry.list_hold_history(
                tenant_id=left.tenant_id,
                hold_reference=left.hold_reference,
                session=session,
            )
        )

        right_history = (
            registry.list_hold_history(
                tenant_id=right.tenant_id,
                hold_reference=right.hold_reference,
                session=session,
            )
        )

        session.commit_transaction()

    assert left_history == (
        left,
    )
    assert right_history == (
        right,
    )


def test_real_corrupted_persisted_row_rejects_without_healing(
    mongo_context: Any,
) -> None:
    client, _, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    value = _fact(
        hold="hold-corrupt",
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=value,
    )

    original = collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
            "fingerprint":
                value.fingerprint,
        }
    )

    assert isinstance(
        original,
        dict,
    )

    collection.update_one(
        {
            "_id":
                original["_id"],
        },
        {
            "$set": {
                "source_evidence_fingerprint":
                    "b" * 128,
            }
        },
    )

    corrupted = collection.find_one(
        {
            "_id":
                original["_id"],
        }
    )

    assert isinstance(
        corrupted,
        dict,
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            LegalEvidenceLegalHoldConstraintPersistedRecordInvalidError
        ):
            registry.get_by_fingerprint(
                tenant_id=value.tenant_id,
                fingerprint=value.fingerprint,
                session=session,
            )

        session.abort_transaction()

    after = collection.find_one(
        {
            "_id":
                original["_id"],
        }
    )

    assert after == corrupted


class _HideIdentityReads:
    def __init__(
        self,
        collection: Any,
    ) -> None:
        self._collection = collection

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: Any,
    ) -> None:
        del query
        del session
        return None

    def insert_one(
        self,
        document: dict[str, object],
        *,
        session: Any,
    ) -> Any:
        return self._collection.insert_one(
            document,
            session=session,
        )


def test_real_duplicate_key_requires_whole_transaction_retry_then_fresh_replay(
    mongo_context: Any,
) -> None:
    client, _, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    value = _fact(
        hold="hold-race",
    )

    _commit_fact(
        client=client,
        registry=registry,
        value=value,
    )

    hidden = (
        LegalEvidenceLegalHoldConstraintRegistry(
            _HideIdentityReads(
                collection
            )
        )
    )

    with client.start_session() as stale_session:
        stale_session.start_transaction()

        with pytest.raises(
            LegalEvidenceLegalHoldConstraintConflictError,
            match=(
                "L10A2R_C4D4B_R3_"
                "WHOLE_TRANSACTION_RETRY_REQUIRED"
            ),
        ):
            hidden.create_or_replay(
                value,
                session=stale_session,
            )

        assert stale_session.in_transaction is True

        stale_session.abort_transaction()

    with client.start_session() as fresh_session:
        fresh_session.start_transaction()

        replayed = registry.create_or_replay(
            value,
            session=fresh_session,
        )

        fresh_session.commit_transaction()

    assert replayed == value

    assert collection.count_documents(
        {
            "tenant_id":
                value.tenant_id,
            "fingerprint":
                value.fingerprint,
        }
    ) == 1


def test_real_registry_grants_no_later_authority_or_mutators(
    mongo_context: Any,
) -> None:
    _, _, collection = mongo_context

    registry = LegalEvidenceLegalHoldConstraintRegistry(
        collection
    )

    forbidden = {
        "get_current",
        "resolve_current",
        "set_current",
        "advance",
        "transition",
        "release",
        "activate",
        "update",
        "delete",
        "remove",
        "satisfy_retention",
        "prove_orphan",
        "authorize_delete",
    }

    public = {
        name
        for name in dir(registry)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(
        public
    )

    assert public == {
        "create_or_replay",
        "ensure_indexes",
        "get_by_fingerprint",
        "list_hold_history",
        "list_provider_object_history",
    }


# ARTIFACT: test_legal_evidence_legal_hold_constraint_registry_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D4B-R5-LEGAL-HOLD-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo certificate for append-only C4D4B durability/history
# TENANT POSTURE: real tenant-isolated persistence and history reads certified
# HISTORY POSTURE: ACTIVE/RELEASED and multiple hold facts remain append-only
# RESTART POSTURE: fresh-client committed replay is certified
# ROLLBACK POSTURE: aborted transaction leaves no durable row
# CORRUPTION POSTURE: malformed durable rows fail closed without healing
# RETRY POSTURE: duplicate races require caller-owned whole transaction restart
# TTL POSTURE: exact real index metadata contains no TTL
# CURRENT-STATE POSTURE: no current/latest authority is inferred
# DELETION POSTURE: no deletion/provider mutation authority is accepted
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
