"""WILSY OS HR Commit-Uncertainty Registry Real-Mongo Certificate.

TITLE: HR Document Commit-Uncertainty Registry Real-Mongo Certificate
VERSION: v1.0.0-P0-C12F6D-HR-COMMIT-UNCERTAINTY-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify the F6D append-once HR commit-uncertainty registry against a
real MongoDB replica set, including exact indexes, caller-owned
transactions, restart durability, exact replay, isolation, corruption
rejection and competing-writer safety.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_hr_document_commit_uncertainty_registry_real_mongo.py

CERTIFICATION / UPDATE DATE: 2026-10-05

AUTHORITY BOUNDARY:
Real-Mongo persistence certification only. No provider IO,
reconciliation, deletion, retention/disposal decision, IAM, HTTP,
payroll, billing, payment, settlement or financial execution authority.

TOPOLOGY BOUNDARY:
Only the dedicated loopback wilsyVendorCertRS replica set is accepted.
Every test uses a UUID-isolated disposable database.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_document import (
    HrDocumentClass,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    HrDocumentCommitUncertainty,
    open_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr import (
    hr_document_commit_uncertainty_registry
    as registry,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    (
        "mongodb://127.0.0.1:27027/"
        "?replicaSet=wilsyVendorCertRS"
    ),
)

EXPECTED_REPLICA_SET = (
    "wilsyVendorCertRS"
)

PAYLOAD = (
    b"WILSY-HR-F6D-REAL-MONGO-"
    b"COMMIT-UNCERTAINTY"
)


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[
        MongoClient[Any],
        Any,
        Any,
    ]
]:
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )

    database: Any = None

    try:
        try:
            hello = client.admin.command(
                "hello"
            )

        except PyMongoError as error:
            pytest.fail(
                "P0_C12F6D_REAL_MONGO_UNAVAILABLE:"
                f"{type(error).__name__}"
            )

        assert (
            hello.get(
                "setName"
            )
            == EXPECTED_REPLICA_SET
        )

        assert (
            hello.get(
                "isWritablePrimary",
                hello.get(
                    "ismaster"
                ),
            )
            is True
        )

        assert (
            hello.get(
                "logicalSessionTimeoutMinutes"
            )
            is not None
        )

        db_name = (
            "wilsy_hr_uncert_"
            + uuid.uuid4().hex[:12]
        )

        assert len(
            db_name
        ) <= 63

        database = client[
            db_name
        ]

        collection = database.get_collection(
            registry.COLLECTION,
            write_concern=WriteConcern(
                w="majority",
                j=True,
            ),
            read_concern=ReadConcern(
                "majority"
            ),
        )

        registry.ensure_indexes(
            collection
        )

        yield (
            client,
            database,
            collection,
        )

    finally:
        if database is not None:
            client.drop_database(
                database.name
            )

        client.close()


def make_uncertainty(
    tenant_id: str,
    *,
    employee_id: str = "employee-f6d",
    document_id: str = "document-f6d",
    document_version_id: str = "document-version-f6d",
    ingestion_reference: str = "ingestion-f6d",
    storage_reference: str = "opaque/f6d/object",
    object_version_reference: str = "provider-version-f6d",
    created_at: datetime | None = None,
) -> HrDocumentCommitUncertainty:
    created = (
        created_at
        if created_at is not None
        else datetime(
            2026,
            10,
            5,
            10,
            11,
            12,
            123456,
            tzinfo=timezone.utc,
        )
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id=employee_id,
        document_id=document_id,
        document_version_id=document_version_id,
        ingestion_reference=ingestion_reference,
        media_type="application/pdf",
        original_filename=(
            "employment-contract.pdf"
        ),
        admitted_max_content_length=4096,
    )

    evidence = HrDocumentBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference=storage_reference,
        object_version_reference=(
            object_version_reference
        ),
        provider_integrity_reference=(
            "provider-integrity-f6d"
        ),
        write_intent_fingerprint=(
            intent.fingerprint
        ),
        content_length=len(
            PAYLOAD
        ),
        content_fingerprint=(
            hashlib.sha3_512(
                PAYLOAD
            ).hexdigest()
        ),
    )

    return open_hr_document_commit_uncertainty(
        intent=intent,
        object_evidence=evidence,
        document_class=(
            HrDocumentClass.EMPLOYMENT_CONTRACT
        ),
        created_at=created,
        created_by_principal_id=(
            "principal-f6d-real"
        ),
        retention_until=(
            created
            + timedelta(
                days=365
            )
        ),
        legal_hold=False,
        supersedes_version_id=None,
        detected_at=(
            created
            + timedelta(
                seconds=3,
                microseconds=222,
            )
        ),
    )


def commit(
    client: MongoClient[Any],
    collection: Any,
    value: HrDocumentCommitUncertainty,
) -> HrDocumentCommitUncertainty:
    owner = (
        registry.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            return owner.create_or_replay(
                value,
                session=session,
            )


def test_real_topology_supports_transactions(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, _ = mongo_context

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
            "isWritablePrimary",
            hello.get(
                "ismaster"
            ),
        )
        is True
    )

    assert (
        hello.get(
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )


def test_real_indexes_are_exact_unique_and_have_no_ttl(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        row["name"]: row
        for row in collection.list_indexes()
        if row["name"] != "_id_"
    }

    assert set(
        indexes
    ) == {
        registry.UNCERTAINTY_INDEX_NAME,
        registry.INGESTION_INDEX_NAME,
        registry.PROVIDER_OBJECT_INDEX_NAME,
        registry.DETECTED_INDEX_NAME,
    }

    assert dict(
        indexes[
            registry.UNCERTAINTY_INDEX_NAME
        ][
            "key"
        ]
    ) == {
        "tenant_id": 1,
        "uncertainty_id": 1,
    }

    assert dict(
        indexes[
            registry.INGESTION_INDEX_NAME
        ][
            "key"
        ]
    ) == {
        "tenant_id": 1,
        "ingestion_reference": 1,
    }

    assert dict(
        indexes[
            registry.PROVIDER_OBJECT_INDEX_NAME
        ][
            "key"
        ]
    ) == {
        "tenant_id": 1,
        "provider_name": 1,
        "storage_reference": 1,
        "object_version_reference": 1,
    }

    assert dict(
        indexes[
            registry.DETECTED_INDEX_NAME
        ][
            "key"
        ]
    ) == {
        "tenant_id": 1,
        "detected_at": -1,
        "uncertainty_id": 1,
    }

    for name in (
        registry.UNCERTAINTY_INDEX_NAME,
        registry.INGESTION_INDEX_NAME,
        registry.PROVIDER_OBJECT_INDEX_NAME,
    ):
        assert (
            indexes[
                name
            ].get(
                "unique"
            )
            is True
        )

    assert (
        indexes[
            registry.DETECTED_INDEX_NAME
        ].get(
            "unique"
        )
        is not True
    )

    assert all(
        "expireAfterSeconds"
        not in row
        for row in indexes.values()
    )


def test_real_commit_restart_replay_and_exact_shape(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, database, collection = (
        mongo_context
    )

    tenant = (
        "tenant-replay-"
        + uuid.uuid4().hex
    )

    value = make_uncertainty(
        tenant
    )

    assert commit(
        client,
        collection,
        value,
    ) == value

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    # New registry instance models process/service restart.
    restarted = (
        registry.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            replay = restarted.create_or_replay(
                value,
                session=session,
            )

            loaded = restarted.get(
                tenant_id=tenant,
                uncertainty_id=(
                    value.uncertainty_id
                ),
                session=session,
            )

            listed = (
                restarted.list_tenant_uncertainties(
                    tenant_id=tenant,
                    session=session,
                )
            )

    assert replay == value
    assert loaded == value
    assert listed == (
        value,
    )

    row = collection.find_one(
        {
            "tenant_id": tenant,
        }
    )

    assert isinstance(
        row,
        dict,
    )

    assert set(
        row
    ) == (
        set(
            value.to_dict()
        )
        | {
            "_id"
        }
    )

    assert row[
        "created_at"
    ] == (
        "2026-10-05T10:11:12.123456+00:00"
    )

    assert row[
        "retention_until"
    ] == (
        "2027-10-05T10:11:12.123456+00:00"
    )

    assert row[
        "detected_at"
    ] == (
        "2026-10-05T10:11:15.123678+00:00"
    )

    forbidden = {
        "content_bytes",
        "raw_bytes",
        "body",
        "orphan",
        "mongo_commit_failed",
        "resolved",
        "reconciled",
        "deleted",
        "available",
        "authorized_availability",
        "provider_delete_authorized",
        "billing_authorized",
        "payment_authorized",
        "settlement_authorized",
    }

    assert forbidden.isdisjoint(
        row
    )

    assert all(
        not isinstance(
            item,
            (
                bytes,
                bytearray,
                memoryview,
            ),
        )
        for item in row.values()
    )

    assert set(
        database.list_collection_names()
    ) == {
        registry.COLLECTION
    }


def test_real_caller_abort_leaves_zero_rows(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-abort-"
        + uuid.uuid4().hex
    )

    value = make_uncertainty(
        tenant
    )

    owner = (
        registry.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        session.start_transaction()

        owner.create_or_replay(
            value,
            session=session,
        )

        assert collection.count_documents(
            {
                "tenant_id": tenant,
            },
            session=session,
        ) == 1

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 0


def test_real_inactive_transaction_rejected_zero_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    value = make_uncertainty(
        "tenant-inactive-"
        + uuid.uuid4().hex
    )

    owner = (
        registry.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with pytest.raises(
            registry.HrDocumentCommitUncertaintyRegistryTransactionRequiredError
        ):
            owner.create_or_replay(
                value,
                session=session,
            )

    assert collection.count_documents(
        {}
    ) == 0


def test_real_tenant_isolation_is_exact(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant_a = (
        "tenant-a-"
        + uuid.uuid4().hex
    )

    tenant_b = (
        "tenant-b-"
        + uuid.uuid4().hex
    )

    first = make_uncertainty(
        tenant_a
    )

    second = make_uncertainty(
        tenant_b
    )

    commit(
        client,
        collection,
        first,
    )

    commit(
        client,
        collection,
        second,
    )

    owner = (
        registry.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            assert (
                owner.list_tenant_uncertainties(
                    tenant_id=tenant_a,
                    session=session,
                )
                == (
                    first,
                )
            )

            assert (
                owner.list_tenant_uncertainties(
                    tenant_id=tenant_b,
                    session=session,
                )
                == (
                    second,
                )
            )

            with pytest.raises(
                registry.HrDocumentCommitUncertaintyRegistryNotFoundError
            ):
                owner.get(
                    tenant_id=tenant_b,
                    uncertainty_id=(
                        first.uncertainty_id
                    ),
                    session=session,
                )


def test_real_ingestion_and_provider_identity_divergence_fail_closed(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-divergence-"
        + uuid.uuid4().hex
    )

    first = make_uncertainty(
        tenant,
        ingestion_reference=(
            "ingestion-same"
        ),
        storage_reference=(
            "opaque/f6d/object-one"
        ),
        object_version_reference=(
            "provider-version-one"
        ),
    )

    same_ingestion = make_uncertainty(
        tenant,
        ingestion_reference=(
            "ingestion-same"
        ),
        storage_reference=(
            "opaque/f6d/object-two"
        ),
        object_version_reference=(
            "provider-version-two"
        ),
    )

    same_provider = make_uncertainty(
        tenant,
        ingestion_reference=(
            "ingestion-other"
        ),
        storage_reference=(
            first.storage_reference
        ),
        object_version_reference=(
            first.object_version_reference
        ),
    )

    commit(
        client,
        collection,
        first,
    )

    owner = (
        registry.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentCommitUncertaintyRegistryConflictError,
                match=(
                    "P0_C12F6D_DIVERGENT_INGESTION_IDENTITY"
                ),
            ):
                owner.create_or_replay(
                    same_ingestion,
                    session=session,
                )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentCommitUncertaintyRegistryConflictError,
                match=(
                    "P0_C12F6D_DIVERGENT_PROVIDER_OBJECT_IDENTITY"
                ),
            ):
                owner.create_or_replay(
                    same_provider,
                    session=session,
                )

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


def test_real_corruption_rejected_without_healing(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-corrupt-"
        + uuid.uuid4().hex
    )

    value = make_uncertainty(
        tenant
    )

    commit(
        client,
        collection,
        value,
    )

    original = deepcopy(
        collection.find_one(
            {
                "tenant_id": tenant,
            }
        )
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
            "$set":
                {
                    "fingerprint":
                        "0" * 128,
                },
        },
    )

    owner = (
        registry.HrDocumentCommitUncertaintyRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError
            ):
                owner.get(
                    tenant_id=tenant,
                    uncertainty_id=(
                        value.uncertainty_id
                    ),
                    session=session,
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

    assert (
        corrupted[
            "fingerprint"
        ]
        == "0" * 128
    )

    collection.replace_one(
        {
            "_id":
                original["_id"],
        },
        original,
    )

    collection.update_one(
        {
            "_id":
                original["_id"],
        },
        {
            "$set":
                {
                    "unexpected":
                        "authority",
                },
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentCommitUncertaintyRegistryPersistedRecordInvalidError
            ):
                owner.get(
                    tenant_id=tenant,
                    uncertainty_id=(
                        value.uncertainty_id
                    ),
                    session=session,
                )


def test_real_competing_writers_do_not_duplicate(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-race-"
        + uuid.uuid4().hex
    )

    value = make_uncertainty(
        tenant
    )

    barrier = Barrier(
        2
    )

    def worker() -> str:
        owner = (
            registry.HrDocumentCommitUncertaintyRegistry(
                collection
            )
        )

        try:
            with client.start_session() as session:
                session.start_transaction()

                barrier.wait(
                    timeout=5
                )

                owner.create_or_replay(
                    value,
                    session=session,
                )

                session.commit_transaction()

            return "committed"

        except (
            registry.HrDocumentCommitUncertaintyRegistryRetryRequiredError
        ):
            return "retry"

        except PyMongoError as error:
            if (
                error.has_error_label(
                    "TransientTransactionError"
                )
                or error.has_error_label(
                    "UnknownTransactionCommitResult"
                )
            ):
                return "retry"

            raise

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        results = list(
            executor.map(
                lambda _: worker(),
                range(
                    2
                ),
            )
        )

    assert (
        results.count(
            "committed"
        )
        >= 1
    )

    assert all(
        result
        in {
            "committed",
            "retry",
        }
        for result in results
    )

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


# ARTIFACT: tests/integration/test_hr_document_commit_uncertainty_registry_real_mongo.py
# VERSION: v1.0.0-P0-C12F6D-HR-COMMIT-UNCERTAINTY-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo HR uncertainty persistence only
# TOPOLOGY: dedicated loopback wilsyVendorCertRS on port 27027
# DATABASE: UUID-isolated disposable database only
# TRANSACTION: caller-owned active transaction required
# REPLAY: committed exact replay survives registry restart
# TENANT POSTURE: exact tenant-scoped reads
# CORRUPTION POSTURE: fail closed without healing
# COMPETING WRITERS: at most one durable row
# TTL AUTHORITY: none
# UPDATE/DELETE AUTHORITY: none
# PROVIDER IO AUTHORITY: none
# RECONCILIATION AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
