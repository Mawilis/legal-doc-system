"""Direct certificate for immutable EmployeeRelation durable registry."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

import pathlib

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.hr_operations import (
    EMPLOYEE_RELATION_FIELDS,
    EmployeeRelation,
    EmployeeRelationActionType,
    EmployeeRelationStatus,
)
from tools.eos.saas.hr import employee_relation_registry as registry


TENANT = "tenant-acme"
OTHER_TENANT = "tenant-other"
EMPLOYEE = "employee-001"


class FakeSession:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0

    def start_transaction(self) -> None:
        self.start_calls += 1

    def commit_transaction(self) -> None:
        self.commit_calls += 1

    def abort_transaction(self) -> None:
        self.abort_calls += 1


class FakeCursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, spec: list[tuple[str, int]]) -> "FakeCursor":
        for key, direction in reversed(spec):
            self.rows.sort(
                key=lambda row: row.get(key) or "",
                reverse=direction < 0,
            )
        return self

    def limit(self, value: int) -> "FakeCursor":
        self.rows = self.rows[:value]
        return self

    def __iter__(self):
        return iter(self.rows)


class FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []

    def with_options(self, **_: Any) -> "FakeCollection":
        return self

    def create_index(
        self,
        spec: list[tuple[str, int]],
        **kwargs: Any,
    ) -> str:
        self.indexes.append((spec, kwargs))
        return str(kwargs.get("name", ""))

    def find(
        self,
        query: dict[str, Any],
        *,
        session: Any = None,
    ) -> FakeCursor:
        def matches(row: dict[str, Any]) -> bool:
            for key, expected in query.items():
                if row.get(key) != expected:
                    return False
            return True

        return FakeCursor(
            [
                deepcopy(row)
                for row in self.rows
                if matches(row)
            ]
        )

    def find_one(
        self,
        query: dict[str, Any],
        *,
        session: Any = None,
    ) -> dict[str, Any] | None:
        rows = list(
            self.find(
                query,
                session=session,
            )
        )
        return rows[0] if rows else None

    def insert_one(
        self,
        document: dict[str, Any],
        *,
        session: Any = None,
    ) -> Any:
        for row in self.rows:
            if (
                row["tenant_id"] == document["tenant_id"]
                and (
                    row["relation_id"] == document["relation_id"]
                    or row["fingerprint"] == document["fingerprint"]
                )
            ):
                raise DuplicateKeyError(
                    "duplicate"
                )

        self.rows.append(
            deepcopy(document)
        )

        return object()


def relation(
    *,
    tenant: str = TENANT,
    relation_id: str = "relation-001",
    employee_id: str = EMPLOYEE,
    action: EmployeeRelationActionType = (
        EmployeeRelationActionType.WRITTEN_WARNING
    ),
) -> EmployeeRelation:
    return EmployeeRelation(
        tenant_id=tenant,
        relation_id=relation_id,
        employee_id=employee_id,
        action_type=action,
        incident_date=date(2026, 10, 1),
        policy_breach="Attendance policy",
        incident_summary="Documented attendance exception.",
        corrective_action="Written warning and review.",
        status=EmployeeRelationStatus.ISSUED,
    )


def test_indexes_are_exact_and_have_no_ttl() -> None:
    collection = FakeCollection()

    registry.ensure_indexes(
        collection
    )

    assert len(
        collection.indexes
    ) == 3

    specs = {
        kwargs["name"]: (
            spec,
            kwargs,
        )
        for spec, kwargs
        in collection.indexes
    }

    assert specs[
        registry.RELATION_ID_INDEX_NAME
    ][0] == [
        ("tenant_id", 1),
        ("relation_id", 1),
    ]

    assert specs[
        registry.FINGERPRINT_INDEX_NAME
    ][0] == [
        ("tenant_id", 1),
        ("fingerprint", 1),
    ]

    assert specs[
        registry.EMPLOYEE_INCIDENT_INDEX_NAME
    ][0] == [
        ("tenant_id", 1),
        ("employee_id", 1),
        ("incident_date", -1),
    ]

    assert specs[
        registry.RELATION_ID_INDEX_NAME
    ][1]["unique"] is True

    assert specs[
        registry.FINGERPRINT_INDEX_NAME
    ][1]["unique"] is True

    assert specs[
        registry.EMPLOYEE_INCIDENT_INDEX_NAME
    ][1]["unique"] is False

    assert all(
        "expireAfterSeconds"
        not in kwargs
        for _, kwargs
        in collection.indexes
    )


@pytest.mark.parametrize(
    "session",
    [
        None,
        FakeSession(False),
    ],
)
def test_active_transaction_is_required(
    session: Any,
) -> None:
    collection = FakeCollection()

    with pytest.raises(
        registry.EmployeeRelationRegistryTransactionRequiredError
    ):
        registry.persist_relation(
            relation(),
            collection,
            session=session,
        )


def test_persist_and_exact_replay_are_idempotent() -> None:
    collection = FakeCollection()
    value = relation()
    session = FakeSession()

    first = registry.persist_relation(
        value,
        collection,
        session=session,
    )

    second = registry.persist_relation(
        value,
        collection,
        session=session,
    )

    assert first == value
    assert second == value
    assert len(collection.rows) == 1


def test_divergent_relation_identity_collision_rejects() -> None:
    collection = FakeCollection()
    session = FakeSession()

    first = relation()
    registry.persist_relation(
        first,
        collection,
        session=session,
    )

    divergent = relation(
        action=EmployeeRelationActionType.FINAL_WRITTEN_WARNING,
    )

    with pytest.raises(
        registry.EmployeeRelationRegistryConflictError
    ):
        registry.persist_relation(
            divergent,
            collection,
            session=session,
        )

    assert len(collection.rows) == 1


def test_cross_tenant_identity_isolated() -> None:
    collection = FakeCollection()
    session = FakeSession()

    first = relation(
        tenant=TENANT,
    )

    second = relation(
        tenant=OTHER_TENANT,
    )

    registry.persist_relation(
        first,
        collection,
        session=session,
    )

    registry.persist_relation(
        second,
        collection,
        session=session,
    )

    assert (
        registry.get_relation(
            TENANT,
            first.relation_id,
            collection,
            session=session,
        )
        == first
    )

    assert (
        registry.get_relation(
            OTHER_TENANT,
            second.relation_id,
            collection,
            session=session,
        )
        == second
    )


def test_get_by_fingerprint_is_tenant_scoped() -> None:
    collection = FakeCollection()
    session = FakeSession()

    value = relation()

    registry.persist_relation(
        value,
        collection,
        session=session,
    )

    assert (
        registry.get_relation_by_fingerprint(
            TENANT,
            value.fingerprint,
            collection,
            session=session,
        )
        == value
    )

    with pytest.raises(
        registry.EmployeeRelationRegistryNotFoundError
    ):
        registry.get_relation_by_fingerprint(
            OTHER_TENANT,
            value.fingerprint,
            collection,
            session=session,
        )


def test_employee_scope_is_exact_and_ordered() -> None:
    collection = FakeCollection()
    session = FakeSession()

    older = relation(
        relation_id="relation-old",
    )

    newer = EmployeeRelation(
        tenant_id=TENANT,
        relation_id="relation-new",
        employee_id=EMPLOYEE,
        action_type=EmployeeRelationActionType.SUSPENSION,
        incident_date=date(2026, 10, 2),
        policy_breach="Attendance policy",
        incident_summary="Second documented exception.",
        corrective_action="Suspension pending review.",
        status=EmployeeRelationStatus.ISSUED,
    )

    foreign_employee = relation(
        relation_id="relation-foreign",
        employee_id="employee-999",
    )

    for value in (
        older,
        newer,
        foreign_employee,
    ):
        registry.persist_relation(
            value,
            collection,
            session=session,
        )

    values = registry.list_employee_relations(
        TENANT,
        EMPLOYEE,
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


def test_strict_hydration_rejects_extra_field() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = relation()

    registry.persist_relation(
        value,
        collection,
        session=session,
    )

    collection.rows[0][
        "unexpected"
    ] = "authority"

    with pytest.raises(
        registry.EmployeeRelationRegistryPersistedRecordInvalidError
    ):
        registry.get_relation(
            TENANT,
            value.relation_id,
            collection,
            session=session,
        )


def test_strict_hydration_rejects_tampered_domain_field() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = relation()

    registry.persist_relation(
        value,
        collection,
        session=session,
    )

    collection.rows[0][
        "corrective_action"
    ] = "Different sanction"

    with pytest.raises(
        registry.EmployeeRelationRegistryPersistedRecordInvalidError
    ):
        registry.get_relation(
            TENANT,
            value.relation_id,
            collection,
            session=session,
        )


def test_missing_relation_is_not_found() -> None:
    collection = FakeCollection()

    with pytest.raises(
        registry.EmployeeRelationRegistryNotFoundError
    ):
        registry.get_relation(
            TENANT,
            "relation-missing",
            collection,
            session=FakeSession(),
        )


def test_invalid_query_inputs_fail_closed() -> None:
    collection = FakeCollection()

    with pytest.raises(
        registry.EmployeeRelationRegistryInputError
    ):
        registry.get_relation(
            "",
            "relation-001",
            collection,
            session=FakeSession(),
        )

    with pytest.raises(
        registry.EmployeeRelationRegistryInputError
    ):
        registry.get_relation_by_fingerprint(
            TENANT,
            "G" * 128,
            collection,
            session=FakeSession(),
        )


def test_registry_does_not_own_transaction_lifecycle() -> None:
    collection = FakeCollection()
    session = FakeSession()

    registry.persist_relation(
        relation(),
        collection,
        session=session,
    )

    assert session.start_calls == 0
    assert session.commit_calls == 0
    assert session.abort_calls == 0


def test_persisted_row_shape_is_domain_only() -> None:
    collection = FakeCollection()
    session = FakeSession()
    value = relation()

    registry.persist_relation(
        value,
        collection,
        session=session,
    )

    assert set(
        collection.rows[0]
    ) == set(
        EMPLOYEE_RELATION_FIELDS
    )

    forbidden = {
        "payment_id",
        "settlement_id",
        "execution_id",
        "billing_authorized",
        "payment_authorized",
        "bank_account",
        "email",
        "phone",
        "employee_name",
    }

    assert forbidden.isdisjoint(
        collection.rows[0]
    )


def test_registry_source_has_no_update_delete_or_ttl_authority() -> None:
    source = registry.__file__

    assert source is not None

    text = pathlib.Path(
        source
    ).read_text(
        encoding="utf-8",
    )

    assert "expireAfterSeconds" not in text
    assert "update_one(" not in text
    assert "update_many(" not in text
    assert "delete_one(" not in text
    assert "delete_many(" not in text
    assert ".delete(" not in text
