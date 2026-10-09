"""WILSY OS C4D5C binary write-intent registry Real-Mongo certificate.

TITLE: Legal Evidence Binary Write Intent Registry Real-Mongo Certificate
VERSION: v1.0.0-L10A2R-C4D5C-BINARY-WRITE-INTENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Physically certify immutable original Legal Evidence binary
         write-intent durability, restart replay, transaction rollback,
         tenant isolation, strict corruption rejection and no-TTL indexes
         against the dedicated loopback Mongo replica set.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_binary_write_intent_registry_real_mongo.py
COLLABORATION / OWNERSHIP:
    C4D5C production registry owns durable provider-neutral original-intent
    evidence. This certificate owns only disposable synthetic real-Mongo
    certification. Provider execution, ingestion orchestration, cleanup
    classification, orphan proof and deletion remain separate gates.
CERTIFICATION / UPDATE DATE: 2026-09-30
CHANGELOG:
    v1.0.0-L10A2R-C4D5C establishes physical index metadata, caller-owned
    transactions, commit durability, restart-safe exact replay, rollback,
    tenant opacity, immutable divergence rejection and corruption rejection.
COMPLIANCE:
    Synthetic disposable runtime evidence only. No production tenant,
    credential, file content or provider operation is used.
SECURITY / PRIVACY POSTURE:
    Dedicated loopback replica-set runtime and UUID-isolated disposable
    database. Synthetic opaque identities only.
TENANT BOUNDARY:
    Every operational registry read/write is exact tenant scoped. Cross-tenant
    lookup is indistinguishable from scoped not-found.
AUTHORITY BOUNDARY:
    Real-Mongo original write-intent durability only. No provider success,
    retention, legal hold, orphan proof, deletion authorization or mutation.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
TRANSACTION BOUNDARY:
    Tests own every session and transaction. Registry starts, commits, aborts
    and retries none.
TOPOLOGY BOUNDARY:
    Dedicated loopback wilsyVendorCertRS on port 27027 only. Any other
    topology fails certification.
DATABASE BOUNDARY:
    One UUID-isolated disposable database is created and dropped per fixture.
FAIL-CLOSED DECLARATION:
    Missing topology, index divergence, transaction failure, replay divergence,
    rollback leakage, cross-tenant disclosure or corruption acceptance fails
    certification. Runtime unavailability is never represented as a pass.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import (
    COLLECTION,
    INDEX_TENANT_DOCUMENT_REGISTERED,
    INDEX_TENANT_FINGERPRINT,
    INDEX_TENANT_INGESTION,
    LegalEvidenceBinaryWriteIntentConflictError,
    LegalEvidenceBinaryWriteIntentNotFoundError,
    LegalEvidenceBinaryWriteIntentPersistedRecordInvalidError,
    LegalEvidenceBinaryWriteIntentRegistry,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryWriteIntent,
)


MONGO_URI = (
    "mongodb://127.0.0.1:27027/"
    "?replicaSet=wilsyVendorCertRS"
)
REPLICA_SET = "wilsyVendorCertRS"

REGISTERED_AT = datetime(
    2026,
    9,
    30,
    17,
    15,
    42,
    654321,
    tzinfo=timezone.utc,
)


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient,
        Database,
        Collection,
    ]
]:
    """Yield one disposable real-Mongo C4D5C registry context."""

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
    )

    hello = client.admin.command(
        "hello"
    )

    if (
        hello.get("setName")
        != REPLICA_SET
        or not bool(
            hello.get(
                "isWritablePrimary"
            )
        )
    ):
        client.close()
        raise RuntimeError(
            "C4D5C_REAL_MONGO_TOPOLOGY_INVALID"
        )

    database_name = (
        "wilsy_c4d5c_write_intent_"
        + uuid4().hex
    )

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

        assert (
            database_name
            not in client.list_database_names()
        )

        client.close()


def _start_transaction(
    session: object,
) -> None:
    """Start the canonical snapshot/majority caller-owned transaction."""

    session.start_transaction(  # type: ignore[attr-defined]
        read_concern=ReadConcern(
            "snapshot"
        ),
        write_concern=WriteConcern(
            w="majority"
        ),
    )


def _intent(
    *,
    tenant_id: str = "tenant-c4d5c-real",
    ingestion_reference: str = "ingestion-c4d5c-real",
    original_filename: str = "evidence.pdf",
) -> LegalEvidenceBinaryWriteIntent:
    return LegalEvidenceBinaryWriteIntent(
        tenant_id=tenant_id,
        case_matter_id="matter-c4d5c-real",
        document_id="document-c4d5c-real",
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename=original_filename,
        admitted_max_content_length=8192,
    )


def test_real_indexes_exact_unique_and_no_ttl(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    """Certify physical C4D5C Mongo index metadata."""

    _, _, collection = mongo_context

    registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )

    registry.ensure_indexes()

    indexes = {
        value["name"]: value
        for value in collection.list_indexes()
    }

    ingestion = indexes[
        INDEX_TENANT_INGESTION
    ]
    fingerprint = indexes[
        INDEX_TENANT_FINGERPRINT
    ]
    document = indexes[
        INDEX_TENANT_DOCUMENT_REGISTERED
    ]

    assert list(
        ingestion["key"].items()
    ) == [
        (
            "tenant_id",
            1,
        ),
        (
            "ingestion_reference",
            1,
        ),
    ]
    assert ingestion["unique"] is True

    assert list(
        fingerprint["key"].items()
    ) == [
        (
            "tenant_id",
            1,
        ),
        (
            "write_intent_fingerprint",
            1,
        ),
    ]
    assert fingerprint["unique"] is True

    assert list(
        document["key"].items()
    ) == [
        (
            "tenant_id",
            1,
        ),
        (
            "document_id",
            1,
        ),
        (
            "registered_at",
            1,
        ),
    ]
    assert document.get(
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
    """Certify commit durability, restart replay and tenant opacity."""

    client, _, collection = mongo_context

    first_registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )
    first_registry.ensure_indexes()

    intent = _intent()

    with client.start_session() as session:
        _start_transaction(
            session
        )

        created = (
            first_registry.create_or_replay(
                intent,
                registered_at=REGISTERED_AT,
                session=session,
            )
        )

        session.commit_transaction()

    assert collection.count_documents(
        {
            "tenant_id":
                intent.tenant_id,
        }
    ) == 1

    restarted_registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )

    with client.start_session() as session:
        _start_transaction(
            session
        )

        replayed = (
            restarted_registry.create_or_replay(
                intent,
                registered_at=REGISTERED_AT,
                session=session,
            )
        )

        by_ingestion = (
            restarted_registry
            .get_by_ingestion_reference(
                tenant_id=intent.tenant_id,
                ingestion_reference=(
                    intent.ingestion_reference
                ),
                session=session,
            )
        )

        by_fingerprint = (
            restarted_registry
            .get_by_fingerprint(
                tenant_id=intent.tenant_id,
                write_intent_fingerprint=(
                    intent.fingerprint
                ),
                session=session,
            )
        )

        with pytest.raises(
            LegalEvidenceBinaryWriteIntentNotFoundError,
            match="WRITE_INTENT_NOT_FOUND",
        ):
            (
                restarted_registry
                .get_by_ingestion_reference(
                    tenant_id="tenant-c4d5c-neighbor",
                    ingestion_reference=(
                        intent.ingestion_reference
                    ),
                    session=session,
                )
            )

        session.commit_transaction()

    assert replayed == created
    assert by_ingestion == created
    assert by_fingerprint == created

    assert collection.count_documents(
        {}
    ) == 1


def test_real_aborted_transaction_leaves_no_intent(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    """Certify caller abort rolls back the C4D5C insert completely."""

    client, _, collection = mongo_context

    registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )
    registry.ensure_indexes()

    intent = _intent(
        ingestion_reference=(
            "ingestion-c4d5c-abort"
        )
    )

    with client.start_session() as session:
        _start_transaction(
            session
        )

        registry.create_or_replay(
            intent,
            registered_at=REGISTERED_AT,
            session=session,
        )

        assert collection.count_documents(
            {
                "tenant_id":
                    intent.tenant_id,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id":
                intent.tenant_id,
        }
    ) == 0


def test_real_divergent_ingestion_replay_rejects_without_second_row(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    """Certify immutable ingestion identity under real unique indexes."""

    client, _, collection = mongo_context

    registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )
    registry.ensure_indexes()

    first = _intent()

    divergent = _intent(
        original_filename="different.pdf"
    )

    with client.start_session() as session:
        _start_transaction(
            session
        )

        registry.create_or_replay(
            first,
            registered_at=REGISTERED_AT,
            session=session,
        )

        session.commit_transaction()

    with client.start_session() as session:
        _start_transaction(
            session
        )

        with pytest.raises(
            LegalEvidenceBinaryWriteIntentConflictError,
            match="DIVERGENT_INGESTION_REFERENCE",
        ):
            registry.create_or_replay(
                divergent,
                registered_at=REGISTERED_AT,
                session=session,
            )

        session.abort_transaction()

    assert collection.count_documents(
        {}
    ) == 1


def test_real_registration_time_divergence_rejects(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    """Certify exact replay includes the original registration instant."""

    client, _, collection = mongo_context

    registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )
    registry.ensure_indexes()

    intent = _intent(
        ingestion_reference=(
            "ingestion-c4d5c-time"
        )
    )

    with client.start_session() as session:
        _start_transaction(
            session
        )

        registry.create_or_replay(
            intent,
            registered_at=REGISTERED_AT,
            session=session,
        )

        session.commit_transaction()

    with client.start_session() as session:
        _start_transaction(
            session
        )

        with pytest.raises(
            LegalEvidenceBinaryWriteIntentConflictError,
            match="DIVERGENT_INGESTION_REFERENCE",
        ):
            registry.create_or_replay(
                intent,
                registered_at=(
                    REGISTERED_AT
                    + timedelta(
                        microseconds=1
                    )
                ),
                session=session,
            )

        session.abort_transaction()

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
    """Certify corrupt durable intent cannot hydrate or self-heal."""

    client, _, collection = mongo_context

    registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )
    registry.ensure_indexes()

    intent = _intent(
        ingestion_reference=(
            "ingestion-c4d5c-corrupt"
        )
    )

    with client.start_session() as session:
        _start_transaction(
            session
        )

        registry.create_or_replay(
            intent,
            registered_at=REGISTERED_AT,
            session=session,
        )

        session.commit_transaction()

    original = collection.find_one(
        {
            "tenant_id":
                intent.tenant_id,
            "ingestion_reference":
                intent.ingestion_reference,
        }
    )

    assert original is not None

    collection.update_one(
        {
            "_id":
                original["_id"],
        },
        {
            "$set": {
                "media_type":
                    "text/plain",
            }
        },
    )

    with client.start_session() as session:
        _start_transaction(
            session
        )

        with pytest.raises(
            LegalEvidenceBinaryWriteIntentPersistedRecordInvalidError,
            match="PERSISTED_RECORD_INVALID",
        ):
            registry.get_by_ingestion_reference(
                tenant_id=intent.tenant_id,
                ingestion_reference=(
                    intent.ingestion_reference
                ),
                session=session,
            )

        session.abort_transaction()

    corrupted = collection.find_one(
        {
            "_id":
                original["_id"],
        }
    )

    assert corrupted is not None
    assert (
        corrupted["media_type"]
        == "text/plain"
    )


def test_real_persisted_write_intent_contains_no_provider_object_authority(
    mongo_context: tuple[
        MongoClient,
        Database,
        Collection,
    ],
) -> None:
    """Certify C4D5C durable row remains provider-neutral."""

    client, _, collection = mongo_context

    registry = (
        LegalEvidenceBinaryWriteIntentRegistry(
            collection
        )
    )
    registry.ensure_indexes()

    intent = _intent(
        ingestion_reference=(
            "ingestion-c4d5c-boundary"
        )
    )

    with client.start_session() as session:
        _start_transaction(
            session
        )

        registry.create_or_replay(
            intent,
            registered_at=REGISTERED_AT,
            session=session,
        )

        session.commit_transaction()

    row = collection.find_one(
        {
            "tenant_id":
                intent.tenant_id,
            "ingestion_reference":
                intent.ingestion_reference,
        }
    )

    assert row is not None

    forbidden = {
        "provider_name",
        "storage_reference",
        "object_version_reference",
        "provider_integrity_reference",
        "provider_success",
        "orphan_proven",
        "deletion_authorized",
        "provider_delete_authorized",
    }

    assert forbidden.isdisjoint(
        row.keys()
    )


# ARTIFACT: test_legal_evidence_binary_write_intent_registry_real_mongo.py
# VERSION: v1.0.0-L10A2R-C4D5C-BINARY-WRITE-INTENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical original binary write-intent durability only
# TOPOLOGY POSTURE: dedicated loopback wilsyVendorCertRS on port 27027
# DATABASE POSTURE: UUID-isolated disposable database only
# REPLAY POSTURE: restart-safe exact immutable replay
# TRANSACTION POSTURE: commit persists; caller abort leaves no row
# TENANT POSTURE: cross-tenant absence remains opaque
# CORRUPTION POSTURE: corrupt durable evidence rejects without self-healing
# TTL POSTURE: no TTL deletion
# PROVIDER POSTURE: registry evidence never asserts provider execution/success
# COVERAGE POSTURE: registry absence alone is never orphan proof
# DELETION POSTURE: no orphan proof or provider-object deletion authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
