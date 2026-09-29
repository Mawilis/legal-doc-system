"""Actual-Mongo certificate for Legal Evidence usage-observation durability.

TITLE: Legal Evidence Usage Observation Registry Actual-Mongo Certificate
VERSION: v1.0.0-L10A2Q-P3-LEGAL-EVIDENCE-USAGE-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Certify immutable P3A/P3B Legal Evidence usage observations against a
    writable Mongo replica set using real indexes, caller-owned transactions,
    exact replay, tenant isolation, rollback and corruption rejection.

EPITOME:
    CANONICAL LEGAL EVIDENCE COMMITTED
    -> USAGE OBSERVATION DERIVED
    -> USAGE OBSERVATION DURABLY RECORDED

    DURABLY RECORDED
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

CERTIFICATION / UPDATE DATE: 2026-09-30

TENANT POSTURE:
    All durable identities and reads remain exact tenant scoped. A neighboring
    tenant cannot use a known observation identity to obtain another tenant's
    durable usage evidence.

TRANSACTION POSTURE:
    Caller owns start/commit/abort. Registry methods require an already-active
    transaction and never manufacture transaction ownership.

AUTHORITY BOUNDARY:
    Raw Legal Evidence usage-observation durability only. No aggregation,
    remaining-capacity, reservation, entitlement mutation, billing, payment,
    settlement or execution authority.

ENVIRONMENT:
    TEST_VENDOR_MONGO_URI may override the dedicated certification URI.
    Default: mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_evidence_content import (
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    COLLECTION,
    INDEX_TENANT_DOCUMENT_OCCURRED,
    INDEX_TENANT_IDEMPOTENCY,
    INDEX_TENANT_OBSERVATION,
    INDEX_TENANT_OCCURRED,
    LegalEvidenceUsageObservationConflictError,
    LegalEvidenceUsageObservationNotFoundError,
    LegalEvidenceUsageObservationRegistry,
    LegalEvidenceUsageObservationRegistryError,
    LegalEvidenceUsageObservationTransactionRequiredError,
    ensure_indexes,
)


MONGO_URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

STAMP = datetime(2026, 9, 30, 1, 0, tzinfo=timezone.utc)
SOURCE_FP = "a" * 128


@pytest.fixture()
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any]
]:
    """Yield one UUID-isolated majority/journal certification collection."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )

    client.admin.command("ping")

    database = client[
        f"wilsy_l10a2q_p3_usage_cert_{uuid4().hex}"
    ]

    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(
            "majority",
            j=True,
        ),
        read_concern=ReadConcern("majority"),
    )

    ensure_indexes(collection)

    try:
        yield client, database, collection
    finally:
        client.drop_database(database.name)
        client.close()


def _observation(
    *,
    tenant_id: str = "tenant-l10a2q-p3-real-a",
    document_id: str = "document-l10a2q-p3-real",
    content: bytes = b"WILSY canonical Legal Evidence real Mongo usage",
) -> LegalEvidenceUsageObservation:
    canonical = register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id="matter-l10a2q-p3-real",
        document_id=document_id,
        media_type="application/pdf",
        original_filename=f"{document_id}.pdf",
        content=content,
        source_evidence_reference=f"source:{document_id}",
        source_evidence_fingerprint=SOURCE_FP,
        registered_at=STAMP,
    )

    return observe_legal_evidence_usage(
        content=canonical,
    )


def _index_key(index: dict[str, Any]) -> dict[str, Any]:
    return dict(index["key"])


def test_real_indexes_are_exact_unique_and_have_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
    }

    observation = indexes[INDEX_TENANT_OBSERVATION]
    idempotency = indexes[INDEX_TENANT_IDEMPOTENCY]
    occurred = indexes[INDEX_TENANT_OCCURRED]
    document_occurred = indexes[INDEX_TENANT_DOCUMENT_OCCURRED]

    assert _index_key(observation) == {
        "tenant_id": 1,
        "usage_observation_id": 1,
    }
    assert observation["unique"] is True

    assert _index_key(idempotency) == {
        "tenant_id": 1,
        "idempotency_key": 1,
    }
    assert idempotency["unique"] is True

    assert _index_key(occurred) == {
        "tenant_id": 1,
        "occurred_at": 1,
    }
    assert occurred.get("unique") is not True

    assert _index_key(document_occurred) == {
        "tenant_id": 1,
        "document_id": 1,
        "occurred_at": 1,
    }
    assert document_occurred.get("unique") is not True

    assert not any(
        "expireAfterSeconds" in entry
        for entry in indexes.values()
    )


def test_real_transaction_create_replay_get_and_cross_tenant_absence(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        first = registry.create_or_replay(
            observation,
            idempotency_key="idem-p3-real-replay",
            session=session,
        )
        second = registry.create_or_replay(
            observation,
            idempotency_key="idem-p3-real-replay",
            session=session,
        )

        own = registry.get(
            tenant_id=observation.tenant_id,
            usage_observation_id=observation.usage_observation_id,
            session=session,
        )

        assert first == observation
        assert second == observation
        assert own == observation

        with pytest.raises(
            LegalEvidenceUsageObservationNotFoundError,
            match="L10A2Q_P3B_OBSERVATION_NOT_FOUND",
        ):
            registry.get(
                tenant_id="tenant-l10a2q-p3-real-neighbor",
                usage_observation_id=observation.usage_observation_id,
                session=session,
            )

        session.commit_transaction()

    assert collection.count_documents(
        {
            "tenant_id": observation.tenant_id,
            "usage_observation_id": observation.usage_observation_id,
        }
    ) == 1


def test_real_divergent_idempotency_and_identity_reject(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)

    first = _observation(
        document_id="document-p3-real-a",
        content=b"real-content-a",
    )
    second = _observation(
        document_id="document-p3-real-b",
        content=b"real-content-b",
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        registry.create_or_replay(
            first,
            idempotency_key="idem-p3-real-conflict",
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        with pytest.raises(
            LegalEvidenceUsageObservationConflictError,
            match="L10A2Q_P3B_DIVERGENT_IDEMPOTENCY",
        ):
            registry.create_or_replay(
                second,
                idempotency_key="idem-p3-real-conflict",
                session=session,
            )

        session.abort_transaction()

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        with pytest.raises(
            LegalEvidenceUsageObservationConflictError,
            match="L10A2Q_P3B_DIVERGENT_OBSERVATION_IDENTITY",
        ):
            registry.create_or_replay(
                first,
                idempotency_key="idem-p3-real-other",
                session=session,
            )

        session.abort_transaction()


def test_real_aborted_transaction_leaves_no_usage_observation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)

    observation = _observation(
        document_id="document-p3-real-abort",
        content=b"abort-me",
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        registry.create_or_replay(
            observation,
            idempotency_key="idem-p3-real-abort",
            session=session,
        )

        assert collection.count_documents(
            {
                "tenant_id": observation.tenant_id,
                "usage_observation_id":
                    observation.usage_observation_id,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id": observation.tenant_id,
            "usage_observation_id":
                observation.usage_observation_id,
        }
    ) == 0


def test_real_inactive_transaction_rejects_before_write(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)
    observation = _observation(
        document_id="document-p3-real-no-tx",
        content=b"no-active-transaction",
    )

    with client.start_session() as session:
        with pytest.raises(
            LegalEvidenceUsageObservationTransactionRequiredError,
            match="L10A2Q_P3B_TRANSACTION_REQUIRED",
        ):
            registry.create_or_replay(
                observation,
                idempotency_key="idem-p3-real-no-tx",
                session=session,
            )

    assert collection.count_documents({}) == 0


def test_real_persisted_corruption_and_authority_injection_reject(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context
    registry = LegalEvidenceUsageObservationRegistry(collection)

    observation = _observation(
        document_id="document-p3-real-corrupt",
        content=b"corruption-certificate",
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )
        registry.create_or_replay(
            observation,
            idempotency_key="idem-p3-real-corrupt",
            session=session,
        )
        session.commit_transaction()

    row = collection.find_one(
        {
            "tenant_id": observation.tenant_id,
            "usage_observation_id":
                observation.usage_observation_id,
        }
    )

    assert row is not None

    forbidden = {
        "quota",
        "remaining_capacity",
        "reservation_id",
        "price",
        "amount",
        "currency",
        "invoice",
        "payment",
        "settlement",
        "execution",
        "overage",
    }
    assert forbidden.isdisjoint(row)

    collection.update_one(
        {
            "_id": row["_id"],
        },
        {
            "$set": {
                "quota": 1,
            }
        },
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern("majority"),
        )

        with pytest.raises(
            LegalEvidenceUsageObservationRegistryError,
            match="L10A2Q_P3B_CORRUPT_OBSERVATION",
        ):
            registry.get(
                tenant_id=observation.tenant_id,
                usage_observation_id=
                    observation.usage_observation_id,
                session=session,
            )

        session.abort_transaction()


# ARTIFACT: test_legal_evidence_usage_observation_registry_real_mongo.py
# VERSION: v1.0.0-L10A2Q-P3-LEGAL-EVIDENCE-USAGE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual-Mongo raw usage-observation durability only
# TENANT POSTURE: exact tenant-scoped identities, replay and reads
# TRANSACTION POSTURE: caller owns active Mongo transaction
# TTL POSTURE: no usage-observation TTL deletion index
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
