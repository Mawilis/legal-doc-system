"""Real-Mongo certificate for immutable EmployeeRelation registry."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import date
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_operations import (
    EMPLOYEE_RELATION_FIELDS,
    EmployeeRelation,
    EmployeeRelationActionType,
    EmployeeRelationStatus,
)
from tools.eos.saas.hr import employee_relation_registry as registry


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"


@pytest.fixture
def mongo_context() -> Iterator[
    tuple[MongoClient[Any], Any, Any]
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
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                "P0_C12E2B_MONGO_UNAVAILABLE:"
                f"{type(error).__name__}"
            )

        assert hello.get("setName") == EXPECTED_REPLICA_SET

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

        # 8-char UUID suffix keeps total DB name safely under
        # MongoDB's 63-character database-name ceiling.
        db_name = (
            "wilsy_hr_rel_"
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


def relation(
    tenant: str,
    *,
    relation_id: str = "relation-001",
    employee_id: str = "employee-001",
    action: EmployeeRelationActionType = (
        EmployeeRelationActionType.WRITTEN_WARNING
    ),
    incident_date: date = date(
        2026,
        10,
        1,
    ),
) -> EmployeeRelation:
    return EmployeeRelation(
        tenant_id=tenant,
        relation_id=relation_id,
        employee_id=employee_id,
        action_type=action,
        incident_date=incident_date,
        policy_breach="Attendance policy",
        incident_summary="Documented attendance exception.",
        corrective_action="Written warning and review.",
        status=EmployeeRelationStatus.ISSUED,
    )


def commit(
    client: MongoClient[Any],
    collection: Any,
    value: EmployeeRelation,
) -> EmployeeRelation:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_relation(
                value,
                collection,
                session=session,
            )


def test_real_topology_supports_transactions(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, _ = mongo_context

    hello = client.admin.command("hello")

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


def test_real_index_metadata_is_exact_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    _, _, collection = mongo_context

    indexes = {
        row["name"]: row
        for row in collection.list_indexes()
        if row["name"] != "_id_"
    }

    assert set(indexes) == {
        registry.RELATION_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.EMPLOYEE_INCIDENT_INDEX_NAME,
    }

    assert dict(
        indexes[
            registry.RELATION_ID_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "relation_id": 1,
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
            registry.EMPLOYEE_INCIDENT_INDEX_NAME
        ]["key"]
    ) == {
        "tenant_id": 1,
        "employee_id": 1,
        "incident_date": -1,
    }

    assert (
        indexes[
            registry.RELATION_ID_INDEX_NAME
        ].get("unique")
        is True
    )

    assert (
        indexes[
            registry.FINGERPRINT_INDEX_NAME
        ].get("unique")
        is True
    )

    assert (
        indexes[
            registry.EMPLOYEE_INCIDENT_INDEX_NAME
        ].get("unique")
        is not True
    )

    assert all(
        "expireAfterSeconds"
        not in row
        for row
        in indexes.values()
    )


def test_real_commit_exact_replay_and_domain_only_row_shape(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, database, collection = mongo_context

    tenant = (
        "tenant-replay-"
        + uuid.uuid4().hex
    )

    value = relation(
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
        set(EMPLOYEE_RELATION_FIELDS)
        | {"_id"}
    )

    assert (
        row["incident_date"]
        == "2026-10-01"
    )

    forbidden = {
        "payment_id",
        "settlement_id",
        "execution_id",
        "bank_account",
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


def test_real_tenant_and_employee_scope_is_exact(
    mongo_context: tuple[MongoClient[Any], Any, Any],
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

    older = relation(
        tenant_a,
        relation_id="relation-old",
        employee_id="employee-a",
        incident_date=date(
            2026,
            10,
            1,
        ),
    )

    newer = relation(
        tenant_a,
        relation_id="relation-new",
        employee_id="employee-a",
        action=(
            EmployeeRelationActionType.SUSPENSION
        ),
        incident_date=date(
            2026,
            10,
            2,
        ),
    )

    other_employee = relation(
        tenant_a,
        relation_id="relation-other-employee",
        employee_id="employee-b",
    )

    foreign = relation(
        tenant_b,
        relation_id="relation-foreign",
        employee_id="employee-a",
    )

    for value in (
        older,
        newer,
        other_employee,
        foreign,
    ):
        commit(
            client,
            collection,
            value,
        )

    with client.start_session() as session:
        with session.start_transaction():
            values = registry.list_employee_relations(
                tenant_a,
                "employee-a",
                collection,
                session=session,
            )

            assert [
                item.relation_id
                for item in values
            ] == [
                "relation-new",
                "relation-old",
            ]

            with pytest.raises(
                registry.EmployeeRelationRegistryNotFoundError
            ):
                registry.get_relation(
                    tenant_a,
                    foreign.relation_id,
                    collection,
                    session=session,
                )

    assert collection.count_documents(
        {
            "tenant_id": tenant_a,
        }
    ) == 3

    assert collection.count_documents(
        {
            "tenant_id": tenant_b,
        }
    ) == 1


def test_real_divergent_identity_collision_rejects_without_mutation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-conflict-"
        + uuid.uuid4().hex
    )

    first = relation(
        tenant
    )

    commit(
        client,
        collection,
        first,
    )

    before = deepcopy(
        collection.find_one(
            {
                "tenant_id": tenant,
            }
        )
    )

    divergent = relation(
        tenant,
        action=(
            EmployeeRelationActionType.FINAL_WRITTEN_WARNING
        ),
    )

    with client.start_session() as session:
        session.start_transaction()

        with pytest.raises(
            registry.EmployeeRelationRegistryConflictError
        ):
            registry.persist_relation(
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


def test_real_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-corrupt-"
        + uuid.uuid4().hex
    )

    value = relation(
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
                "corrective_action":
                    "Tampered sanction"
            }
        },
    )

    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.EmployeeRelationRegistryPersistedRecordInvalidError
            ):
                registry.get_relation(
                    tenant,
                    value.relation_id,
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
                registry.EmployeeRelationRegistryPersistedRecordInvalidError
            ):
                registry.get_relation(
                    tenant,
                    value.relation_id,
                    collection,
                    session=session,
                )


def test_real_caller_abort_leaves_zero_rows(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-abort-"
        + uuid.uuid4().hex
    )

    value = relation(
        tenant
    )

    with client.start_session() as session:
        session.start_transaction()

        registry.persist_relation(
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
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    client, _, collection = mongo_context

    tenant = (
        "tenant-race-"
        + uuid.uuid4().hex
    )

    value = relation(
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
                registry.persist_relation(
                    value,
                    collection,
                    session=session,
                )

                session.commit_transaction()

                return "COMMITTED"

            except (
                registry.EmployeeRelationRegistryRetryRequiredError
            ):
                if session.in_transaction:
                    session.abort_transaction()

                return "RETRY_REQUIRED"

            except (
                registry.EmployeeRelationRegistryConflictError
            ):
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
