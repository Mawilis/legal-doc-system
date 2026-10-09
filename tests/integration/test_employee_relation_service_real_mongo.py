"""Real-Mongo transaction certificate for EmployeeRelation service."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
import os
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_operations import (
    EmployeeRelation,
    EmployeeRelationActionType,
    EmployeeRelationStatus,
)
from tools.eos.saas.hr import employee_relation_registry as registry
from tools.eos.saas.hr import employee_relation_service as service


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)

EXPECTED_REPLICA_SET = "wilsyVendorCertRS"

TENANT = "tenant-service-cert"
EMPLOYEE_ID = "employee-001"


class FakeEmployee:
    def __init__(
        self,
        employee_id: str = EMPLOYEE_ID,
        tenant_id: str = TENANT,
    ) -> None:
        self.employeeId = employee_id
        self.tenantId = tenant_id


class FakeEmployeeRegistry:
    def __init__(self, value: Any) -> None:
        self.value = value
        self.calls: list[tuple[str, str]] = []

    def get_employee_by_id(
        self,
        employee_id: str,
        tenant_id: str,
    ) -> Any:
        self.calls.append(
            (
                employee_id,
                tenant_id,
            )
        )
        return self.value


class CountingClient:
    def __init__(
        self,
        client: MongoClient[Any],
    ) -> None:
        self.client = client
        self.session_count = 0

    def start_session(self) -> Any:
        self.session_count += 1
        return self.client.start_session()


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
            "wilsy_hr_svc_"
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
    *,
    relation_id: str = "relation-001",
    action: EmployeeRelationActionType = (
        EmployeeRelationActionType.WRITTEN_WARNING
    ),
) -> EmployeeRelation:
    return EmployeeRelation(
        tenant_id=TENANT,
        relation_id=relation_id,
        employee_id=EMPLOYEE_ID,
        action_type=action,
        incident_date=date(
            2026,
            10,
            4,
        ),
        policy_breach="Attendance policy",
        incident_summary=(
            "Documented attendance exception."
        ),
        corrective_action=(
            "Written warning and review."
        ),
        status=EmployeeRelationStatus.ISSUED,
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
        hello["setName"]
        == EXPECTED_REPLICA_SET
    )

    assert (
        hello.get(
            "isWritablePrimary",
            hello.get("ismaster"),
        )
        is True
    )


def test_real_success_and_exact_replay_one_row(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    employee_registry = FakeEmployeeRegistry(
        FakeEmployee()
    )

    counting = CountingClient(
        client
    )

    value = relation()

    first = service.record_employee_relation(
        value,
        employee_registry=employee_registry,
        relation_collection=collection,
        mongo_client=counting,
    )

    second = service.record_employee_relation(
        value,
        employee_registry=employee_registry,
        relation_collection=collection,
        mongo_client=counting,
    )

    assert first == value
    assert second == value

    assert collection.count_documents(
        {
            "tenant_id": TENANT,
        }
    ) == 1

    assert counting.session_count == 2

    assert employee_registry.calls == [
        (
            EMPLOYEE_ID,
            TENANT,
        ),
        (
            EMPLOYEE_ID,
            TENANT,
        ),
    ]


def test_real_missing_employee_zero_session_zero_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    counting = CountingClient(
        client
    )

    with pytest.raises(
        service.EmployeeRelationServiceEmployeeNotFoundError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(
                None
            ),
            relation_collection=collection,
            mongo_client=counting,
        )

    assert counting.session_count == 0

    assert collection.count_documents(
        {}
    ) == 0


def test_real_employee_binding_mismatch_zero_session_zero_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    counting = CountingClient(
        client
    )

    with pytest.raises(
        service.EmployeeRelationServiceEmployeeBindingError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee(
                    employee_id="employee-other",
                )
            ),
            relation_collection=collection,
            mongo_client=counting,
        )

    assert counting.session_count == 0

    assert collection.count_documents(
        {}
    ) == 0


def test_real_conflict_no_mutation(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
) -> None:
    client, _, collection = mongo_context

    counting = CountingClient(
        client
    )

    employee_registry = FakeEmployeeRegistry(
        FakeEmployee()
    )

    original = relation()

    service.record_employee_relation(
        original,
        employee_registry=employee_registry,
        relation_collection=collection,
        mongo_client=counting,
    )

    before = deepcopy(
        collection.find_one(
            {
                "tenant_id": TENANT,
                "relation_id":
                    original.relation_id,
            }
        )
    )

    divergent = relation(
        action=(
            EmployeeRelationActionType.FINAL_WRITTEN_WARNING
        )
    )

    with pytest.raises(
        registry.EmployeeRelationRegistryConflictError
    ):
        service.record_employee_relation(
            divergent,
            employee_registry=employee_registry,
            relation_collection=collection,
            mongo_client=counting,
        )

    assert collection.count_documents(
        {
            "tenant_id": TENANT,
        }
    ) == 1

    assert collection.find_one(
        {
            "tenant_id": TENANT,
            "relation_id":
                original.relation_id,
        }
    ) == before


def test_real_unexpected_failure_aborts_partial_insert(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, collection = mongo_context

    counting = CountingClient(
        client
    )

    value = relation(
        relation_id="relation-abort"
    )

    def partial_then_fail(
        passed: EmployeeRelation,
        passed_collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        passed_collection.insert_one(
            passed.to_dict(),
            session=session,
        )

        raise RuntimeError(
            "synthetic failure"
        )

    monkeypatch.setattr(
        service,
        "persist_relation",
        partial_then_fail,
    )

    with pytest.raises(
        RuntimeError
    ):
        service.record_employee_relation(
            value,
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee()
            ),
            relation_collection=collection,
            mongo_client=counting,
        )

    assert counting.session_count == 1

    assert collection.count_documents(
        {
            "relation_id":
                value.relation_id,
        }
    ) == 0


def test_real_retry_aborts_first_then_commits_second(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, collection = mongo_context

    counting = CountingClient(
        client
    )

    value = relation(
        relation_id="relation-retry"
    )

    real_persist = service.persist_relation

    attempts = 0

    def first_partial_then_retry(
        passed: EmployeeRelation,
        passed_collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            passed_collection.insert_one(
                passed.to_dict(),
                session=session,
            )

            raise (
                registry.EmployeeRelationRegistryRetryRequiredError()
            )

        return real_persist(
            passed,
            passed_collection,
            session=session,
        )

    monkeypatch.setattr(
        service,
        "persist_relation",
        first_partial_then_retry,
    )

    result = service.record_employee_relation(
        value,
        employee_registry=FakeEmployeeRegistry(
            FakeEmployee()
        ),
        relation_collection=collection,
        mongo_client=counting,
        max_attempts=2,
    )

    assert result == value
    assert attempts == 2
    assert counting.session_count == 2

    assert collection.count_documents(
        {
            "relation_id":
                value.relation_id,
        }
    ) == 1


def test_real_retry_exhaustion_zero_durable_write(
    mongo_context: tuple[
        MongoClient[Any],
        Any,
        Any,
    ],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _, collection = mongo_context

    counting = CountingClient(
        client
    )

    value = relation(
        relation_id="relation-retry-exhausted"
    )

    attempts = 0

    def partial_then_retry(
        passed: EmployeeRelation,
        passed_collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        nonlocal attempts
        attempts += 1

        passed_collection.insert_one(
            passed.to_dict(),
            session=session,
        )

        raise (
            registry.EmployeeRelationRegistryRetryRequiredError()
        )

    monkeypatch.setattr(
        service,
        "persist_relation",
        partial_then_retry,
    )

    with pytest.raises(
        registry.EmployeeRelationRegistryRetryRequiredError
    ):
        service.record_employee_relation(
            value,
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee()
            ),
            relation_collection=collection,
            mongo_client=counting,
            max_attempts=2,
        )

    assert attempts == 2
    assert counting.session_count == 2

    assert collection.count_documents(
        {
            "relation_id":
                value.relation_id,
        }
    ) == 0
