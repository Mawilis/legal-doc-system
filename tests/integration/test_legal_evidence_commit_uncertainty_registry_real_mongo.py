"""Real-Mongo certificate for durable Legal Evidence commit uncertainty.

TITLE: Legal Evidence Commit Uncertainty Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4B-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Prove the C4B registry against a real loopback Mongo replica set using
    caller-owned transactions, durable exact replay, tenant isolation,
    immutable corruption rejection and rollback semantics.

EPITOME:
    C4A COMMIT UNCERTAINTY
    -> REAL MONGO DURABILITY
    -> RESTART-SAFE DISCOVERY
    != ORPHAN PROVEN
    != RECONCILIATION PERFORMED
    != PROVIDER DELETE AUTHORIZED
    != AUTHORIZED AVAILABILITY

SAFETY:
    The suite accepts only the dedicated loopback certification replica set and
    creates one UUID-isolated disposable database which is dropped afterward.
    It must never touch production/auth databases.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import os
import uuid
from typing import Iterator

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
    open_legal_evidence_commit_uncertainty,
)
from tools.eos.legal_operations.registry.legal_evidence_commit_uncertainty_registry import (
    COLLECTION,
    DETECTED_INDEX_NAME,
    INGESTION_INDEX_NAME,
    PROVIDER_OBJECT_INDEX_NAME,
    UNCERTAINTY_INDEX_NAME,
    LegalEvidenceCommitUncertaintyRegistry,
    LegalEvidenceCommitUncertaintyRegistryConflictError,
    LegalEvidenceCommitUncertaintyRegistryError,
    LegalEvidenceCommitUncertaintyRegistryNotFoundError,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryWriteIntent,
)


MONGO_URI = os.environ.get(
    "WILSY_C4B_REAL_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_HOST = "127.0.0.1"
EXPECTED_PORT = 27027
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

AT = datetime(
    2026,
    9,
    30,
    13,
    45,
    0,
    123456,
    tzinfo=timezone.utc,
)

CONTENT = b"c4b-real-mongo-provider-completed-content"
CONTENT_FP = hashlib.sha3_512(CONTENT).hexdigest()
SOURCE_FP = hashlib.sha3_512(
    b"c4b-real-mongo-source-evidence"
).hexdigest()


def _assert_safe_client(
    client: MongoClient,
) -> None:
    address = client.address

    assert address is not None
    host, port = address

    assert host in {
        EXPECTED_HOST,
        "localhost",
    }
    assert port == EXPECTED_PORT

    hello = client.admin.command(
        "hello"
    )

    assert hello.get(
        "setName"
    ) == EXPECTED_REPLICA_SET

    assert hello.get(
        "isWritablePrimary"
    ) is True


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient,
        Database,
        Collection,
    ]
]:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
    )

    _assert_safe_client(
        client
    )

    database_name = (
        "wilsy_c4b_commit_uncertainty_"
        + uuid.uuid4().hex
    )

    assert database_name.startswith(
        "wilsy_c4b_commit_uncertainty_"
    )

    db = client[
        database_name
    ]

    collection = db[
        COLLECTION
    ]

    try:
        yield (
            client,
            db,
            collection,
        )
    finally:
        client.drop_database(
            database_name
        )
        client.close()


def _value(
    *,
    tenant_id: str = "tenant-c4b-real",
    matter_id: str = "matter-c4b-real",
    document_id: str = "document-c4b-real",
    ingestion_reference: str = "ingestion-c4b-real",
    reservation_id: str = "reservation-c4b-real",
    storage_reference: str = "legal-evidence/v1/c4b-real",
    object_version_reference: str = "version-c4b-real",
    detected_at: datetime = AT,
) -> LegalEvidenceCommitUncertainty:
    intent = LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        document_id=document_id,
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        admitted_max_content_length=4096,
    )

    reservation = LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_reference,
        remaining_capacity_fingerprint="a" * 128,
        reserved_storage_bytes=len(CONTENT),
        reserved_ingress_bytes=len(CONTENT),
        reserved_document_versions=1,
        reserved_at=AT - timedelta(minutes=5),
        expires_at=AT + timedelta(minutes=20),
    )

    object_evidence = (
        LegalEvidenceBinaryObjectEvidence(
            provider_name="aws_s3",
            storage_reference=storage_reference,
            object_version_reference=object_version_reference,
            provider_integrity_reference='"etag-c4b-real"',
            write_intent_fingerprint=intent.fingerprint,
            content_length=len(CONTENT),
            content_fingerprint=CONTENT_FP,
        )
    )

    return open_legal_evidence_commit_uncertainty(
        reservation=reservation,
        intent=intent,
        object_evidence=object_evidence,
        observed_content_length=len(CONTENT),
        observed_content_fingerprint=CONTENT_FP,
        source_evidence_reference="source-c4b-real",
        source_evidence_fingerprint=SOURCE_FP,
        detected_at=detected_at,
    )


def test_real_indexes_exact_unique_and_no_ttl(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    _, _, collection = mongo_context

    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
    }

    assert {
        UNCERTAINTY_INDEX_NAME,
        INGESTION_INDEX_NAME,
        PROVIDER_OBJECT_INDEX_NAME,
        DETECTED_INDEX_NAME,
    }.issubset(indexes)

    assert indexes[
        UNCERTAINTY_INDEX_NAME
    ]["unique"] is True

    assert indexes[
        INGESTION_INDEX_NAME
    ]["unique"] is True

    assert indexes[
        PROVIDER_OBJECT_INDEX_NAME
    ]["unique"] is True

    assert indexes[
        DETECTED_INDEX_NAME
    ].get(
        "unique",
        False,
    ) is False

    for index in indexes.values():
        assert (
            "expireAfterSeconds"
            not in index
        )


def test_real_commit_restart_replay_and_cross_tenant_absence(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    client, _, collection = mongo_context

    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    value = _value()

    with client.start_session() as session:
        with session.start_transaction():
            created = registry.create_or_replay(
                value,
                session=session,
            )
            assert created == value

    assert collection.count_documents(
        {}
    ) == 1

    restarted_registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            replayed = restarted_registry.create_or_replay(
                value,
                session=session,
            )

            loaded = restarted_registry.get(
                tenant_id=value.tenant_id,
                uncertainty_id=value.uncertainty_id,
                session=session,
            )

            listed = (
                restarted_registry.list_tenant_uncertainties(
                    tenant_id=value.tenant_id,
                    session=session,
                )
            )

            assert replayed == value
            assert loaded == value
            assert listed == (
                value,
            )

            with pytest.raises(
                LegalEvidenceCommitUncertaintyRegistryNotFoundError,
                match="L10A2R_C4B_UNCERTAINTY_NOT_FOUND",
            ):
                restarted_registry.get(
                    tenant_id="tenant-neighbor",
                    uncertainty_id=value.uncertainty_id,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 1

    persisted = collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
            "uncertainty_id":
                value.uncertainty_id,
        }
    )

    assert persisted is not None

    forbidden = {
        "content",
        "content_bytes",
        "body",
        "raw_bytes",
        "orphan",
        "mongo_commit_failed",
        "metadata_missing",
        "resolved",
        "reconciled",
        "deleted",
        "available",
        "authorized_availability",
    }

    assert forbidden.isdisjoint(
        persisted
    )

    assert all(
        not isinstance(
            item,
            (
                bytes,
                bytearray,
            ),
        )
        for item in persisted.values()
    )


def test_real_abort_leaves_no_uncertainty_row(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    client, _, collection = mongo_context

    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    value = _value()

    with client.start_session() as session:
        session.start_transaction()

        registry.create_or_replay(
            value,
            session=session,
        )

        assert collection.count_documents(
            {},
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents(
        {}
    ) == 0


def test_real_ingestion_and_provider_identity_divergence_fail_closed(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    client, _, collection = mongo_context

    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    first = _value()

    second_same_ingestion = _value(
        storage_reference=(
            "legal-evidence/v1/c4b-real-second"
        ),
        object_version_reference=(
            "version-c4b-real-second"
        ),
    )

    second_same_provider = _value(
        ingestion_reference=(
            "ingestion-c4b-real-second"
        ),
        reservation_id=(
            "reservation-c4b-real-second"
        ),
    )

    with client.start_session() as session:
        with session.start_transaction():
            registry.create_or_replay(
                first,
                session=session,
            )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalEvidenceCommitUncertaintyRegistryConflictError,
                match="L10A2R_C4B_DIVERGENT_INGESTION_IDENTITY",
            ):
                registry.create_or_replay(
                    second_same_ingestion,
                    session=session,
                )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalEvidenceCommitUncertaintyRegistryConflictError,
                match="L10A2R_C4B_DIVERGENT_PROVIDER_OBJECT_IDENTITY",
            ):
                registry.create_or_replay(
                    second_same_provider,
                    session=session,
                )

    assert collection.count_documents(
        {}
    ) == 1


def test_real_persisted_corruption_rejects_without_healing(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    client, _, collection = mongo_context

    registry = (
        LegalEvidenceCommitUncertaintyRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    value = _value()

    with client.start_session() as session:
        with session.start_transaction():
            registry.create_or_replay(
                value,
                session=session,
            )

    original = collection.find_one(
        {
            "tenant_id":
                value.tenant_id,
            "uncertainty_id":
                value.uncertainty_id,
        }
    )

    assert original is not None

    collection.update_one(
        {
            "_id":
                original["_id"],
        },
        {
            "$set":
                {
                    "fingerprint":
                        "f" * 128,
                },
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                LegalEvidenceCommitUncertaintyRegistryError,
                match="L10A2R_C4B_CORRUPT_UNCERTAINTY",
            ):
                registry.get(
                    tenant_id=value.tenant_id,
                    uncertainty_id=value.uncertainty_id,
                    session=session,
                )

    corrupted = collection.find_one(
        {
            "_id":
                original["_id"],
        }
    )

    assert corrupted is not None
    assert corrupted[
        "fingerprint"
    ] == "f" * 128


# ARTIFACT: test_legal_evidence_commit_uncertainty_registry_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4B-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo uncertainty durability only
# TOPOLOGY POSTURE: dedicated loopback wilsyVendorCertRS on port 27027
# DATABASE POSTURE: UUID-isolated disposable DB only
# REPLAY POSTURE: restart-safe exact replay
# TRANSACTION POSTURE: commit persists; abort leaves no row
# TENANT POSTURE: cross-tenant absence remains opaque
# TTL POSTURE: no TTL
# RECONCILIATION POSTURE: no reconciliation outcome inferred
# DELETION POSTURE: no provider-object deletion authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
