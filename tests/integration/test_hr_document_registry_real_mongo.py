"""TITLE: WILSY OS HR Document Registry Real-Mongo Certification.
VERSION: v1.0.0-P0-C12F4C-HR-DOCUMENT-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Real MongoDB replica-set certificate for immutable HR document metadata.
EPITOME: Proves exact indexes, no TTL, active transactions, replay,
caller abort, tenant/employee isolation, corruption rejection,
microsecond preservation and competing-writer safety.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_hr_document_registry_real_mongo.py
CERTIFICATION/UPDATE DATE: 2026-10-04.
CHANGELOG:
2026-10-04 v1.0.0-P0-C12F4C-HR-DOCUMENT-REGISTRY-REAL-MONGO-CERT
establishes the first real-Mongo HR document registry certificate.
AUTHORITY BOUNDARY: persistence evidence only; no IAM, HTTP, provider
execution, deletion authority, payroll, billing or financial execution.
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
    HrDocument,
    HrDocumentClass,
)
from tools.eos.saas.hr import hr_document_registry as registry
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryWriteIntent,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

PAYLOAD = (
    b"%PDF-1.7\n"
    b"REAL HR DOCUMENT REGISTRY CERTIFICATE\n"
    b"\x00\x01\xff"
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
                "P0_C12F4C_MONGO_UNAVAILABLE:"
                f"{type(error).__name__}"
            )

        assert (
            hello.get("setName")
            == EXPECTED_REPLICA_SET
        )

        assert (
            hello.get(
                "isWritablePrimary",
                hello.get("ismaster"),
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
            "wilsy_hr_doc_"
            + uuid.uuid4().hex[:8]
        )

        assert len(db_name) <= 63

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


def make_document(
    tenant_id: str,
    *,
    employee_id: str = "employee-001",
    document_id: str = "hrdoc-001",
    document_version_id: str = "hrdocver-001",
    document_class: HrDocumentClass = (
        HrDocumentClass.APPOINTMENT_LETTER
    ),
    created_at: datetime | None = None,
    supersedes_version_id: str | None = None,
) -> HrDocument:
    created = (
        created_at
        if created_at is not None
        else datetime(
            2026,
            10,
            4,
            8,
            0,
            0,
            654321,
            tzinfo=timezone.utc,
        )
    )

    intent = HrDocumentBinaryWriteIntent(
        tenant_id=tenant_id,
        employee_id=employee_id,
        document_id=document_id,
        document_version_id=document_version_id,
        ingestion_reference=(
            "ingest-"
            + document_version_id
        ),
        media_type="application/pdf",
        original_filename="appointment-letter.pdf",
        admitted_max_content_length=2_000_000,
    )

    evidence = HrDocumentBinaryObjectEvidence(
        provider_name="hr-provider",
        storage_reference=(
            "opaque/"
            + tenant_id
            + "/"
            + document_version_id
        ),
        object_version_reference=(
            "provider-"
            + document_version_id
        ),
        provider_integrity_reference=(
            "integrity-"
            + document_version_id
        ),
        write_intent_fingerprint=intent.fingerprint,
        content_length=len(PAYLOAD),
        content_fingerprint=hashlib.sha3_512(
            PAYLOAD
        ).hexdigest(),
    )

    return HrDocument.from_binary_evidence(
        intent=intent,
        evidence=evidence,
        document_class=document_class,
        created_at=created,
        created_by_principal_id="principal-hr-cert",
        retention_until=(
            created
            + timedelta(
                days=365
            )
        ),
        supersedes_version_id=supersedes_version_id,
    )


def commit(
    client: MongoClient[Any],
    collection: Any,
    value: HrDocument,
) -> HrDocument:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_document(
                value,
                collection,
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

    assert hello["setName"] == EXPECTED_REPLICA_SET

    assert (
        hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        )
        is True
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

    assert set(indexes) == {
        registry.DOCUMENT_VERSION_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.EMPLOYEE_CREATED_INDEX_NAME,
        registry.DOCUMENT_HISTORY_INDEX_NAME,
        registry.EMPLOYEE_CLASS_INDEX_NAME,
        registry.EMPLOYEE_SENSITIVITY_INDEX_NAME,
    }

    assert dict(
        indexes[
            registry.DOCUMENT_VERSION_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "document_version_id": 1,
    }

    assert dict(
        indexes[
            registry.FINGERPRINT_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }

    assert dict(
        indexes[
            registry.EMPLOYEE_CREATED_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "employee_id": 1,
        "created_at": -1,
    }

    assert dict(
        indexes[
            registry.DOCUMENT_HISTORY_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "employee_id": 1,
        "document_id": 1,
        "created_at": -1,
    }

    assert dict(
        indexes[
            registry.EMPLOYEE_CLASS_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "employee_id": 1,
        "document_class": 1,
        "created_at": -1,
    }

    assert dict(
        indexes[
            registry.EMPLOYEE_SENSITIVITY_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "employee_id": 1,
        "sensitivity": 1,
        "created_at": -1,
    }

    assert (
        indexes[
            registry.DOCUMENT_VERSION_INDEX_NAME
        ].get("unique")
        is True
    )

    assert (
        indexes[
            registry.FINGERPRINT_INDEX_NAME
        ].get("unique")
        is True
    )

    for name in (
        registry.EMPLOYEE_CREATED_INDEX_NAME,
        registry.DOCUMENT_HISTORY_INDEX_NAME,
        registry.EMPLOYEE_CLASS_INDEX_NAME,
        registry.EMPLOYEE_SENSITIVITY_INDEX_NAME,
    ):
        assert (
            indexes[name].get("unique")
            is not True
        )

    assert all(
        "expireAfterSeconds"
        not in row
        for row in indexes.values()
    )


def test_real_commit_exact_replay_and_metadata_only_shape(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, database, collection = mongo_context

    tenant = (
        "tenant-replay-"
        + uuid.uuid4().hex
    )

    value = make_document(
        tenant
    )

    assert commit(
        client,
        collection,
        value,
    ) == value

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

    row = collection.find_one(
        {
            "tenant_id": tenant,
        }
    )

    assert isinstance(
        row,
        dict,
    )

    assert set(row) == (
        set(
            registry.HR_DOCUMENT_RECORD_FIELDS
        )
        | {"_id"}
    )

    assert row["created_at"] == (
        "2026-10-04T08:00:00.654321+00:00"
    )

    assert (
        row["retention_until"]
        == "2027-10-04T08:00:00.654321+00:00"
    )

    forbidden = {
        "content_bytes",
        "raw_file",
        "payment_id",
        "settlement_id",
        "execution_id",
        "billing_authorized",
        "payment_authorized",
        "employee_name",
        "email",
        "phone",
    }

    assert forbidden.isdisjoint(
        row
    )

    assert set(
        database.list_collection_names()
    ) == {
        registry.COLLECTION
    }


def test_real_tenant_employee_and_document_scope_is_exact(
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

    base = datetime(
        2026,
        10,
        4,
        8,
        0,
        tzinfo=timezone.utc,
    )

    first = make_document(
        tenant_a,
        employee_id="employee-a",
        document_id="document-a",
        document_version_id="version-a1",
        created_at=base,
    )

    second = make_document(
        tenant_a,
        employee_id="employee-a",
        document_id="document-a",
        document_version_id="version-a2",
        created_at=(
            base
            + timedelta(
                seconds=1
            )
        ),
        supersedes_version_id="version-a1",
    )

    other_employee = make_document(
        tenant_a,
        employee_id="employee-b",
        document_id="document-b",
        document_version_id="version-b1",
        created_at=(
            base
            + timedelta(
                seconds=2
            )
        ),
    )

    foreign_tenant = make_document(
        tenant_b,
        employee_id="employee-a",
        document_id="document-a",
        document_version_id="version-foreign",
        created_at=(
            base
            + timedelta(
                seconds=3
            )
        ),
    )

    for value in (
        first,
        second,
        other_employee,
        foreign_tenant,
    ):
        commit(
            client,
            collection,
            value,
        )

    with client.start_session() as session:
        with session.start_transaction():
            employee_rows = registry.list_employee_documents(
                tenant_a,
                "employee-a",
                collection,
                session=session,
            )

            assert [
                item.document_version_id
                for item in employee_rows
            ] == [
                "version-a2",
                "version-a1",
            ]

            history = registry.list_document_versions(
                tenant_a,
                "employee-a",
                "document-a",
                collection,
                session=session,
            )

            assert [
                item.document_version_id
                for item in history
            ] == [
                "version-a2",
                "version-a1",
            ]

            assert (
                registry.list_employee_documents(
                    tenant_a,
                    "employee-missing",
                    collection,
                    session=session,
                )
                == ()
            )

            with pytest.raises(
                registry.HrDocumentRegistryNotFoundError
            ):
                registry.get_document_version(
                    tenant_a,
                    foreign_tenant.document_version_id,
                    collection,
                    session=session,
                )


def test_real_class_scoped_read_is_exact(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-class-"
        + uuid.uuid4().hex
    )

    appointment = make_document(
        tenant,
        document_id="doc-appointment",
        document_version_id="version-appointment",
    )

    warning = make_document(
        tenant,
        document_id="doc-warning",
        document_version_id="version-warning",
        document_class=HrDocumentClass.WARNING,
    )

    commit(
        client,
        collection,
        appointment,
    )

    commit(
        client,
        collection,
        warning,
    )

    with client.start_session() as session:
        with session.start_transaction():
            values = (
                registry.list_employee_documents_by_class(
                    tenant,
                    "employee-001",
                    HrDocumentClass.WARNING,
                    collection,
                    session=session,
                )
            )

    assert values == (
        warning,
    )


def test_real_microseconds_survive_round_trip(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-time-"
        + uuid.uuid4().hex
    )

    value = make_document(
        tenant
    )

    commit(
        client,
        collection,
        value,
    )

    with client.start_session() as session:
        with session.start_transaction():
            hydrated = registry.get_document_version(
                tenant,
                value.document_version_id,
                collection,
                session=session,
            )

    assert (
        hydrated.created_at.microsecond
        == 654321
    )

    assert (
        hydrated.retention_until
        is not None
    )

    assert (
        hydrated.retention_until.microsecond
        == 654321
    )


def test_real_divergent_version_collision_rejects_without_mutation(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-conflict-"
        + uuid.uuid4().hex
    )

    original = make_document(
        tenant
    )

    commit(
        client,
        collection,
        original,
    )

    before = deepcopy(
        collection.find_one(
            {
                "tenant_id": tenant,
            }
        )
    )

    divergent = make_document(
        tenant,
        document_class=HrDocumentClass.WARNING,
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            registry.HrDocumentRegistryConflictError
        ):
            registry.persist_document(
                divergent,
                collection,
                session=session,
            )

        session.abort_transaction()

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1

    assert collection.find_one(
        {
            "tenant_id": tenant,
        }
    ) == before


def test_real_corruption_rejected_before_projection(
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

    value = make_document(
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
            "tenant_id": tenant,
        },
        {
            "$set": {
                "fingerprint":
                    "0" * 128
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentRegistryPersistedRecordInvalidError
            ):
                registry.get_document_version(
                    tenant,
                    value.document_version_id,
                    collection,
                    session=session,
                )

    collection.replace_one(
        {
            "_id": original["_id"],
        },
        original,
    )

    collection.update_one(
        {
            "tenant_id": tenant,
        },
        {
            "$set": {
                "unexpected":
                    "authority"
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.HrDocumentRegistryPersistedRecordInvalidError
            ):
                registry.get_document_version(
                    tenant,
                    value.document_version_id,
                    collection,
                    session=session,
                )


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

    value = make_document(
        tenant
    )

    with client.start_session() as session:
        session.start_transaction()

        registry.persist_document(
            value,
            collection,
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


def test_real_competing_consumers_do_not_duplicate(
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

    value = make_document(
        tenant
    )

    barrier = Barrier(
        2
    )

    def contender(
        _: int,
    ) -> str:
        with client.start_session() as session:
            session.start_transaction()

            barrier.wait()

            try:
                registry.persist_document(
                    value,
                    collection,
                    session=session,
                )

                session.commit_transaction()

                return "COMMITTED"

            except registry.HrDocumentRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()

                return "RETRY_REQUIRED"

            except registry.HrDocumentRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()

                return "CONFLICT"

            except PyMongoError:
                if session.in_transaction:
                    session.abort_transaction()

                return "MONGO_RETRY"

    with ThreadPoolExecutor(
        max_workers=2
    ) as pool:
        outcomes = list(
            pool.map(
                contender,
                (
                    1,
                    2,
                ),
            )
        )

    assert all(
        outcome in {
            "COMMITTED",
            "RETRY_REQUIRED",
            "CONFLICT",
            "MONGO_RETRY",
        }
        for outcome in outcomes
    )

    assert outcomes.count(
        "COMMITTED"
    ) >= 1

    assert collection.count_documents(
        {
            "tenant_id": tenant,
        }
    ) == 1


# ARTIFACT: tests/integration/test_hr_document_registry_real_mongo.py
# VERSION: v1.0.0-P0-C12F4C-HR-DOCUMENT-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real Mongo persistence certificate only
# TRANSACTION BOUNDARY: caller-owned active transaction
# RETENTION BOUNDARY: verifies TTL absence; no deletion authority
# STORAGE BOUNDARY: metadata only; no binary provider execution
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
