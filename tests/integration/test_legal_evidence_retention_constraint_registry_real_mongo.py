"""Real-Mongo certificate for C4D4A retention-constraint registry.

TITLE: Legal Evidence Retention Constraint Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D4A-R5-RETENTION-CONSTRAINT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Certify actual MongoDB replica-set durability, exact indexes, caller-owned
    transactions, commit/restart replay, rollback, tenant isolation, strict
    corruption rejection and duplicate-key whole-transaction recovery for the
    already-valid C4D4A retention constraint.

AUTHORITY BOUNDARY:
    Durable persistence/replay only. This certificate creates no retention
    satisfaction, legal-hold release, orphan proof, deletion authorization,
    provider mutation, billing, payment, execution or settlement authority.

TRANSACTION POSTURE:
    Every Mongo session and transaction is owned by this certificate caller.
    The production registry never starts, commits or aborts a transaction.

TTL POSTURE:
    No TTL index is permitted.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from typing import Any
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_retention_constraint import (
    LegalEvidenceRetentionConstraint,
)
from tools.eos.legal_operations.registry.legal_evidence_retention_constraint_registry import (
    COLLECTION,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_PROVIDER_OBJECT,
    INDEX_TENANT_SOURCE_EVIDENCE,
    LegalEvidenceRetentionConstraintConflictError,
    LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
    LegalEvidenceRetentionConstraintRegistry,
    LegalEvidenceRetentionConstraintTransactionRequiredError,
)


URI = os.environ.get(
    "WILSY_VENDOR_CERT_MONGO_URI",
    (
        "mongodb://127.0.0.1:27027/"
        "?replicaSet=wilsyVendorCertRS"
    ),
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

UTC = timezone.utc

BASE = datetime(
    2026,
    10,
    1,
    12,
    0,
    tzinfo=UTC,
)

SHA_A = "a" * 128


@dataclass
class _Context:
    client: MongoClient[Any]
    database: Database[Any]
    collection: Collection[Any]
    registry: LegalEvidenceRetentionConstraintRegistry
    database_name: str


class _HideIdentityReads:
    """Hide replay pre-reads once so real Mongo produces duplicate-key."""

    def __init__(
        self,
        collection: Collection[Any],
    ) -> None:
        self._collection = collection
        self._remaining_hidden_reads = 2

    def find_one(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        if self._remaining_hidden_reads > 0:
            self._remaining_hidden_reads -= 1
            return None

        return self._collection.find_one(
            *args,
            **kwargs,
        )

    def insert_one(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self._collection.insert_one(
            *args,
            **kwargs,
        )

    def create_index(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        return self._collection.create_index(
            *args,
            **kwargs,
        )


def _value(
    *,
    tenant_id: str = "tenant-c4d4a-r5",
    provider_name: str = "s3",
    storage_reference: str = "bucket-c4d4a-r5",
    object_version_reference: str = "object-version-c4d4a-r5",
    source_evidence_reference: str = "retention-source-c4d4a-r5",
    source_evidence_fingerprint: str = SHA_A,
    imposed_at: datetime = BASE,
    retain_until: datetime = BASE + timedelta(days=365),
) -> LegalEvidenceRetentionConstraint:
    return LegalEvidenceRetentionConstraint(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference=storage_reference,
        object_version_reference=object_version_reference,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        imposed_at=imposed_at,
        retain_until=retain_until,
    )


@pytest.fixture
def mongo_context() -> Any:
    client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
    )

    hello = client.admin.command(
        "hello"
    )

    assert (
        hello.get(
            "setName"
        )
        == EXPECTED_REPLICA_SET
    )

    assert (
        hello.get(
            "isWritablePrimary"
        )
        is True
    )

    database_name = (
        "wilsy_c4d4a_r5_"
        + uuid4().hex
    )

    assert database_name != "wilsy"

    database = client.get_database(
        database_name,
        read_concern=ReadConcern(
            "snapshot"
        ),
        write_concern=WriteConcern(
            "majority",
            j=True,
        ),
    )

    collection: Collection[Any] = database[
        COLLECTION
    ]

    registry = LegalEvidenceRetentionConstraintRegistry(
        collection
    )

    registry.ensure_indexes()

    context = _Context(
        client=client,
        database=database,
        collection=collection,
        registry=registry,
        database_name=database_name,
    )

    try:
        yield context
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def _commit(
    context: _Context,
    value: LegalEvidenceRetentionConstraint,
) -> LegalEvidenceRetentionConstraint:
    with context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            ),
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
        )

        result = context.registry.create_or_replay(
            value,
            session=session,
        )

        session.commit_transaction()

    return result


def test_real_topology_database_and_indexes(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    hello = context.client.admin.command(
        "hello"
    )

    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello["isWritablePrimary"] is True

    assert context.database_name.startswith(
        "wilsy_c4d4a_r5_"
    )
    assert context.database_name != "wilsy"

    indexes = {
        item["name"]: item
        for item in context.collection.list_indexes()
    }

    assert INDEX_TENANT_FINGERPRINT in indexes
    assert INDEX_TENANT_PROVIDER_OBJECT in indexes
    assert INDEX_TENANT_SOURCE_EVIDENCE in indexes

    fingerprint = indexes[
        INDEX_TENANT_FINGERPRINT
    ]

    assert dict(
        fingerprint["key"]
    ) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }

    assert fingerprint.get(
        "unique"
    ) is True

    provider_object = indexes[
        INDEX_TENANT_PROVIDER_OBJECT
    ]

    assert dict(
        provider_object["key"]
    ) == {
        "tenant_id": 1,
        "provider_name": 1,
        "storage_reference": 1,
        "object_version_reference": 1,
    }

    assert provider_object.get(
        "unique"
    ) is True

    source = indexes[
        INDEX_TENANT_SOURCE_EVIDENCE
    ]

    assert dict(
        source["key"]
    ) == {
        "tenant_id": 1,
        "source_evidence_reference": 1,
    }

    assert source.get(
        "unique",
        False,
    ) is False

    for item in indexes.values():
        assert "expireAfterSeconds" not in item


def test_real_inactive_transaction_rejects_before_write(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _value(
        tenant_id=(
            "tenant-c4d4a-r5-inactive-"
            + uuid4().hex
        )
    )

    with context.client.start_session() as session:
        assert session.in_transaction is False

        with pytest.raises(
            LegalEvidenceRetentionConstraintTransactionRequiredError,
            match="ACTIVE_TRANSACTION_REQUIRED",
        ):
            context.registry.create_or_replay(
                value,
                session=session,
            )

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 0
    )


def test_real_commit_restart_replay_and_iso_chronology(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _value(
        tenant_id=(
            "tenant-c4d4a-r5-replay-"
            + uuid4().hex
        )
    )

    created = _commit(
        context,
        value,
    )

    assert created == value

    raw = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert raw is not None

    assert raw["imposed_at"] == value.imposed_at.isoformat()
    assert raw["retain_until"] == value.retain_until.isoformat()

    assert isinstance(
        raw["imposed_at"],
        str,
    )
    assert isinstance(
        raw["retain_until"],
        str,
    )

    fresh_client: MongoClient[Any] = MongoClient(
        URI,
        serverSelectionTimeoutMS=5000,
    )

    try:
        fresh_collection = fresh_client[
            context.database_name
        ][
            COLLECTION
        ]

        restarted = LegalEvidenceRetentionConstraintRegistry(
            fresh_collection
        )

        with fresh_client.start_session() as session:
            session.start_transaction(
                read_concern=ReadConcern(
                    "snapshot"
                ),
                write_concern=WriteConcern(
                    "majority",
                    j=True,
                ),
            )

            replayed = restarted.create_or_replay(
                value,
                session=session,
            )

            by_object = restarted.get_by_provider_object(
                tenant_id=value.tenant_id,
                provider_name=value.provider_name,
                storage_reference=value.storage_reference,
                object_version_reference=(
                    value.object_version_reference
                ),
                session=session,
            )

            by_fingerprint = restarted.get_by_fingerprint(
                tenant_id=value.tenant_id,
                fingerprint=value.fingerprint,
                session=session,
            )

            session.commit_transaction()

        assert replayed == value
        assert by_object == value
        assert by_fingerprint == value

    finally:
        fresh_client.close()

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 1
    )


def test_real_aborted_transaction_rolls_back(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _value(
        tenant_id=(
            "tenant-c4d4a-r5-abort-"
            + uuid4().hex
        )
    )

    with context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            ),
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
        )

        context.registry.create_or_replay(
            value,
            session=session,
        )

        assert (
            context.collection.count_documents(
                {
                    "tenant_id":
                        value.tenant_id,
                },
                session=session,
            )
            == 1
        )

        session.abort_transaction()

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 0
    )


def test_real_provider_object_divergence_rejects_without_second_row(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    tenant = (
        "tenant-c4d4a-r5-divergent-"
        + uuid4().hex
    )

    first = _value(
        tenant_id=tenant,
    )

    divergent = _value(
        tenant_id=tenant,
        source_evidence_reference=(
            "retention-source-c4d4a-r5-divergent"
        ),
        retain_until=BASE + timedelta(days=730),
    )

    assert first.fingerprint != divergent.fingerprint

    _commit(
        context,
        first,
    )

    with context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            ),
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
        )

        with pytest.raises(
            LegalEvidenceRetentionConstraintConflictError,
            match="IMMUTABLE_REPLAY_DIVERGENCE",
        ):
            context.registry.create_or_replay(
                divergent,
                session=session,
            )

        session.abort_transaction()

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    tenant,
            }
        )
        == 1
    )


def test_real_cross_tenant_same_provider_object_isolated(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    suffix = uuid4().hex

    first = _value(
        tenant_id=(
            "tenant-c4d4a-r5-a-"
            + suffix
        )
    )

    second = _value(
        tenant_id=(
            "tenant-c4d4a-r5-b-"
            + suffix
        )
    )

    _commit(
        context,
        first,
    )

    _commit(
        context,
        second,
    )

    assert (
        context.collection.count_documents(
            {
                "provider_name":
                    first.provider_name,
                "storage_reference":
                    first.storage_reference,
                "object_version_reference":
                    first.object_version_reference,
            }
        )
        == 2
    )

    with context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            ),
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
        )

        assert (
            context.registry.get_by_provider_object(
                tenant_id=first.tenant_id,
                provider_name=first.provider_name,
                storage_reference=first.storage_reference,
                object_version_reference=(
                    first.object_version_reference
                ),
                session=session,
            )
            == first
        )

        assert (
            context.registry.get_by_provider_object(
                tenant_id=second.tenant_id,
                provider_name=second.provider_name,
                storage_reference=second.storage_reference,
                object_version_reference=(
                    second.object_version_reference
                ),
                session=session,
            )
            == second
        )

        session.commit_transaction()


def test_real_corruption_rejects_without_healing(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _value(
        tenant_id=(
            "tenant-c4d4a-r5-corrupt-"
            + uuid4().hex
        )
    )

    _commit(
        context,
        value,
    )

    context.collection.update_one(
        {
            "tenant_id":
                value.tenant_id,
        },
        {
            "$set": {
                "source_evidence_fingerprint":
                    "0" * 128,
            }
        },
    )

    corrupt_before = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert corrupt_before is not None

    with context.client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            ),
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
        )

        with pytest.raises(
            LegalEvidenceRetentionConstraintPersistedRecordInvalidError,
            match="PERSISTED_RECORD_INVALID",
        ):
            context.registry.get_by_fingerprint(
                tenant_id=value.tenant_id,
                fingerprint=value.fingerprint,
                session=session,
            )

        session.abort_transaction()

    corrupt_after = context.collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
        }
    )

    assert corrupt_after == corrupt_before


def test_real_duplicate_key_requires_abort_then_fresh_transaction_replays(
    mongo_context: _Context,
) -> None:
    context = mongo_context

    value = _value(
        tenant_id=(
            "tenant-c4d4a-r5-race-"
            + uuid4().hex
        )
    )

    _commit(
        context,
        value,
    )

    stale_registry = LegalEvidenceRetentionConstraintRegistry(
        _HideIdentityReads(
            context.collection
        )
    )

    with context.client.start_session() as stale:
        stale.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            ),
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
        )

        with pytest.raises(
            LegalEvidenceRetentionConstraintConflictError,
            match="WHOLE_TRANSACTION_RETRY_REQUIRED",
        ):
            stale_registry.create_or_replay(
                value,
                session=stale,
            )

        assert stale.in_transaction is True

        stale.abort_transaction()

    with context.client.start_session() as retry:
        retry.start_transaction(
            read_concern=ReadConcern(
                "snapshot"
            ),
            write_concern=WriteConcern(
                "majority",
                j=True,
            ),
        )

        replayed = context.registry.create_or_replay(
            value,
            session=retry,
        )

        retry.commit_transaction()

    assert replayed == value

    assert (
        context.collection.count_documents(
            {
                "tenant_id":
                    value.tenant_id,
            }
        )
        == 1
    )


def test_real_registry_surface_grants_no_later_authority(
    mongo_context: _Context,
) -> None:
    _ = mongo_context

    source = (
        "tools/eos/legal_operations/registry/"
        "legal_evidence_retention_constraint_registry.py"
    )

    text = open(
        source,
        encoding="utf-8",
    ).read()

    assert ".start_transaction(" not in text
    assert ".commit_transaction(" not in text
    assert ".abort_transaction(" not in text

    assert ".delete_one(" not in text
    assert ".delete_many(" not in text
    assert ".update_one(" not in text
    assert ".update_many(" not in text

    assert "expireAfterSeconds" not in text

    methods = set(
        vars(
            LegalEvidenceRetentionConstraintRegistry
        )
    )

    assert methods.isdisjoint(
        {
            "satisfy_retention",
            "mark_retention_satisfied",
            "release_legal_hold",
            "clear_legal_hold",
            "prove_orphan",
            "authorize_delete",
            "authorize_deletion",
            "delete",
            "update",
            "remove",
        }
    )


# ARTIFACT: test_legal_evidence_retention_constraint_registry_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D4A-R5-RETENTION-CONSTRAINT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo durability/replay evidence only
# TENANT POSTURE: exact tenant-scoped identity/read isolation
# TRANSACTION POSTURE: caller owns active transaction; duplicate race requires retry
# REPLAY POSTURE: fresh-client durable exact replay only
# CORRUPTION POSTURE: corrupt durable evidence rejects without healing
# CHRONOLOGY POSTURE: imposed_at and retain_until remain exact aware ISO text
# TTL POSTURE: exact indexes and no TTL deletion
# RETENTION POSTURE: no satisfaction or legal-sufficiency authority
# LEGAL HOLD POSTURE: no issue/release/clearance authority
# ORPHAN POSTURE: no orphan-proof authority
# DELETION POSTURE: no update/delete/provider mutation authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN CERTIFICATE
