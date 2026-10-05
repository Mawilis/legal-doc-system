"""WILSY OS HR Commit-Reconciliation Outcome Registry Real-Mongo Certificate.

TITLE: HR Document Commit-Reconciliation Outcome Registry Real-Mongo Certificate
VERSION: v1.0.0-P0-C12F6E2-HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Certify the append-once F6E2 reconciliation-outcome registry against a
real MongoDB replica set.

AUTHORITY BOUNDARY:
Persistence certification only. No reconciliation decision authority,
provider IO, provider deletion, orphan determination, uncertainty mutation,
IAM, HTTP, retention/disposal, billing, payment, settlement or financial
execution authority.

TOPOLOGY BOUNDARY:
Only the dedicated loopback wilsyVendorCertRS replica set is accepted.
Every test uses a UUID-isolated disposable database.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_hr_document_commit_reconciliation_outcome_registry_real_mongo.py

CERTIFICATION / UPDATE DATE: 2026-10-05
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
from tools.eos.saas.domain.hr_document_commit_reconciliation_outcome import (
    HrDocumentCommitReconciliationOutcome,
    HrDocumentCommitReconciliationOutcomeEvidence,
    record_hr_document_commit_reconciliation_outcome,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    open_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr import (
    hr_document_commit_reconciliation_outcome_registry
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
    b"WILSY-HR-F6E2-REAL-MONGO-OUTCOME"
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

        db_name = (
            "wilsy_hr_outcome_"
            + uuid.uuid4().hex[:12]
        )

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
):
    intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id="employee-f6e2",
        document_id="document-f6e2",
        document_version_id=(
            "document-version-f6e2"
        ),
        ingestion_reference=(
            "ingestion-f6e2"
        ),
        media_type="application/pdf",
        original_filename=(
            "employment-contract.pdf"
        ),
        admitted_max_content_length=4096,
    )

    evidence = HrDocumentBinaryObjectEvidence(
        provider_name="aws_s3",
        storage_reference=(
            "hr/v1/opaque-f6e2-object"
        ),
        object_version_reference=(
            "provider-version-f6e2"
        ),
        provider_integrity_reference=(
            "provider-integrity-f6e2"
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

    created = datetime(
        2026,
        10,
        5,
        13,
        0,
        0,
        123456,
        tzinfo=timezone.utc,
    )

    return open_hr_document_commit_uncertainty(
        intent=intent,
        object_evidence=evidence,
        document_class=(
            HrDocumentClass.EMPLOYMENT_CONTRACT
        ),
        created_at=created,
        created_by_principal_id=(
            "principal-f6e2"
        ),
        retention_until=None,
        legal_hold=False,
        supersedes_version_id=None,
        detected_at=created,
    )


def make_outcome(
    tenant_id: str,
    *,
    result: HrDocumentCommitReconciliationOutcome = (
        HrDocumentCommitReconciliationOutcome
        .COMMITTED_CONFIRMED
    ),
    seconds_after: int = 60,
) -> HrDocumentCommitReconciliationOutcomeEvidence:
    uncertainty = make_uncertainty(
        tenant_id
    )

    document = uncertainty.to_hr_document()

    return record_hr_document_commit_reconciliation_outcome(
        uncertainty=uncertainty,
        document=document,
        outcome=result,
        reconciled_at=(
            uncertainty.detected_at
            + timedelta(
                seconds=seconds_after
            )
        ),
    )


def commit(
    client: MongoClient[Any],
    collection: Any,
    value: HrDocumentCommitReconciliationOutcomeEvidence,
) -> HrDocumentCommitReconciliationOutcomeEvidence:
    owner = (
        registry.HrDocumentCommitReconciliationOutcomeRegistry(
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
            "logicalSessionTimeoutMinutes"
        )
        is not None
    )


def test_real_indexes_are_exact_and_have_no_ttl(
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
        registry.OUTCOME_ID_INDEX_NAME,
        registry.UNCERTAINTY_INDEX_NAME,
        registry.RECONCILED_INDEX_NAME,
    }

    assert dict(
        indexes[
            registry.OUTCOME_ID_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "outcome_id": 1,
    }

    assert dict(
        indexes[
            registry.UNCERTAINTY_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "uncertainty_id": 1,
    }

    assert dict(
        indexes[
            registry.RECONCILED_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "reconciled_at": -1,
        "outcome_id": 1,
    }

    assert (
        indexes[
            registry.OUTCOME_ID_INDEX_NAME
        ].get(
            "unique"
        )
        is True
    )

    assert (
        indexes[
            registry.UNCERTAINTY_INDEX_NAME
        ].get(
            "unique"
        )
        is True
    )

    assert (
        indexes[
            registry.RECONCILED_INDEX_NAME
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
        "tenant-outcome-replay-"
        + uuid.uuid4().hex
    )

    value = make_outcome(
        tenant
    )

    assert commit(
        client,
        collection,
        value,
    ) == value

    restarted = (
        registry.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            replay = restarted.create_or_replay(
                value,
                session=session,
            )

            loaded = restarted.get_by_uncertainty(
                tenant_id=tenant,
                uncertainty_id=(
                    value.uncertainty_id
                ),
                session=session,
            )

    assert replay == value
    assert loaded == value

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

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
        "reconciled_at"
    ] == value.reconciled_at.isoformat()

    forbidden = {
        "content_bytes",
        "raw_bytes",
        "orphan_proven",
        "provider_delete_authorized",
        "mongo_commit_failed",
        "billing_authorized",
        "payment_authorized",
        "settlement_authorized",
    }

    assert forbidden.isdisjoint(
        row
    )

    assert set(
        database.list_collection_names()
    ) == {
        registry.COLLECTION
    }


def test_real_abort_leaves_zero_rows(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-outcome-abort-"
        + uuid.uuid4().hex
    )

    value = make_outcome(
        tenant
    )

    owner = (
        registry.HrDocumentCommitReconciliationOutcomeRegistry(
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


def test_real_tenant_isolation_is_exact(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant_a = (
        "tenant-outcome-a-"
        + uuid.uuid4().hex
    )

    tenant_b = (
        "tenant-outcome-b-"
        + uuid.uuid4().hex
    )

    first = make_outcome(
        tenant_a
    )

    second = make_outcome(
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
        registry.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            assert (
                owner.get_by_uncertainty(
                    tenant_id=tenant_a,
                    uncertainty_id=(
                        first.uncertainty_id
                    ),
                    session=session,
                )
                == first
            )

            with pytest.raises(
                registry.HrDocumentCommitReconciliationOutcomeRegistryNotFoundError
            ):
                owner.get_by_uncertainty(
                    tenant_id=tenant_b,
                    uncertainty_id=(
                        first.uncertainty_id
                    ),
                    session=session,
                )


def test_real_terminal_outcome_divergence_rejected(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-outcome-divergence-"
        + uuid.uuid4().hex
    )

    confirmed = make_outcome(
        tenant,
        result=(
            HrDocumentCommitReconciliationOutcome
            .COMMITTED_CONFIRMED
        ),
    )

    recovered = make_outcome(
        tenant,
        result=(
            HrDocumentCommitReconciliationOutcome
            .COMMIT_RECOVERED
        ),
    )

    assert (
        confirmed.uncertainty_id
        == recovered.uncertainty_id
    )

    commit(
        client,
        collection,
        confirmed,
    )

    owner = (
        registry.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentCommitReconciliationOutcomeRegistryConflictError
            ):
                owner.create_or_replay(
                    recovered,
                    session=session,
                )

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


def test_real_reconciliation_time_divergence_rejected(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-outcome-time-"
        + uuid.uuid4().hex
    )

    first = make_outcome(
        tenant,
        seconds_after=60,
    )

    second = make_outcome(
        tenant,
        seconds_after=61,
    )

    commit(
        client,
        collection,
        first,
    )

    owner = (
        registry.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentCommitReconciliationOutcomeRegistryConflictError
            ):
                owner.create_or_replay(
                    second,
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
        "tenant-outcome-corrupt-"
        + uuid.uuid4().hex
    )

    value = make_outcome(
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
        registry.HrDocumentCommitReconciliationOutcomeRegistry(
            collection
        )
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentCommitReconciliationOutcomeRegistryPersistedRecordInvalidError
            ):
                owner.get_by_uncertainty(
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


def test_real_competing_terminal_outcomes_do_not_coexist(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-outcome-race-"
        + uuid.uuid4().hex
    )

    confirmed = make_outcome(
        tenant,
        result=(
            HrDocumentCommitReconciliationOutcome
            .COMMITTED_CONFIRMED
        ),
    )

    recovered = make_outcome(
        tenant,
        result=(
            HrDocumentCommitReconciliationOutcome
            .COMMIT_RECOVERED
        ),
    )

    barrier = Barrier(
        2
    )

    def worker(
        value: HrDocumentCommitReconciliationOutcomeEvidence,
    ) -> str:
        owner = (
            registry.HrDocumentCommitReconciliationOutcomeRegistry(
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
            registry.HrDocumentCommitReconciliationOutcomeRegistryRetryRequiredError,
            registry.HrDocumentCommitReconciliationOutcomeRegistryConflictError,
        ):
            return "rejected_or_retry"

        except PyMongoError as error:
            if (
                error.has_error_label(
                    "TransientTransactionError"
                )
                or error.has_error_label(
                    "UnknownTransactionCommitResult"
                )
            ):
                return "rejected_or_retry"

            raise

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:
        results = list(
            executor.map(
                worker,
                (
                    confirmed,
                    recovered,
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
            "rejected_or_retry",
        }
        for result in results
    )

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    persisted = collection.find_one(
        {
            "tenant_id": tenant,
        }
    )

    assert isinstance(
        persisted,
        dict,
    )

    assert persisted[
        "uncertainty_id"
    ] == confirmed.uncertainty_id


# ARTIFACT: tests/integration/test_hr_document_commit_reconciliation_outcome_registry_real_mongo.py
# VERSION: v1.0.0-P0-C12F6E2-HR-COMMIT-RECONCILIATION-OUTCOME-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo outcome persistence only
# TOPOLOGY: dedicated loopback wilsyVendorCertRS on port 27027
# DATABASE: UUID-isolated disposable database only
# ONE TERMINAL OUTCOME PER UNCERTAINTY: mandatory
# EXACT REPLAY: restart-safe
# ABORT POSTURE: zero durable row
# CORRUPTION POSTURE: fail closed without healing
# TTL AUTHORITY: none
# UPDATE/DELETE AUTHORITY: none
# PROVIDER IO AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
