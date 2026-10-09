"""Direct certificate for EmployeeRelation transactional service."""

from __future__ import annotations

from datetime import date
from typing import Any
import ast
import pathlib

import pytest

from tools.eos.saas.domain.hr_operations import (
    EmployeeRelation,
    EmployeeRelationActionType,
    EmployeeRelationStatus,
)
from tools.eos.saas.hr import employee_relation_service as service
from tools.eos.saas.hr.employee_relation_registry import (
    EmployeeRelationRegistryConflictError,
    EmployeeRelationRegistryRetryRequiredError,
)


TENANT = "tenant-acme"
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
            (employee_id, tenant_id)
        )
        return self.value


class FakeSession:
    def __init__(self) -> None:
        self.in_transaction = False
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0

    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> None:
        return None

    def start_transaction(self) -> None:
        self.start_calls += 1
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.commit_calls += 1
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.abort_calls += 1
        self.in_transaction = False


class FakeMongoClient:
    def __init__(self) -> None:
        self.sessions: list[FakeSession] = []

    def start_session(self) -> FakeSession:
        session = FakeSession()
        self.sessions.append(session)
        return session


class FakeCollection:
    pass


def relation(
    *,
    tenant: str = TENANT,
    employee_id: str = EMPLOYEE_ID,
) -> EmployeeRelation:
    return EmployeeRelation(
        tenant_id=tenant,
        relation_id="relation-001",
        employee_id=employee_id,
        action_type=(
            EmployeeRelationActionType.WRITTEN_WARNING
        ),
        incident_date=date(2026, 10, 1),
        policy_breach="Attendance policy",
        incident_summary=(
            "Documented attendance exception."
        ),
        corrective_action=(
            "Written warning and review."
        ),
        status=EmployeeRelationStatus.ISSUED,
    )


def test_record_relation_binds_employee_before_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    employee_registry = FakeEmployeeRegistry(
        FakeEmployee()
    )

    client = FakeMongoClient()
    collection = FakeCollection()
    value = relation()

    events: list[str] = []

    original = employee_registry.get_employee_by_id

    def lookup(
        employee_id: str,
        tenant_id: str,
    ) -> Any:
        events.append("EMPLOYEE_LOOKUP")
        return original(
            employee_id,
            tenant_id,
        )

    employee_registry.get_employee_by_id = lookup  # type: ignore[method-assign]

    def persist(
        passed: EmployeeRelation,
        passed_collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        events.append("RELATION_PERSIST")

        assert passed is value
        assert passed_collection is collection
        assert session.in_transaction is True

        return passed

    monkeypatch.setattr(
        service,
        "persist_relation",
        persist,
    )

    result = service.record_employee_relation(
        value,
        employee_registry=employee_registry,
        relation_collection=collection,
        mongo_client=client,
    )

    assert result == value

    assert events == [
        "EMPLOYEE_LOOKUP",
        "RELATION_PERSIST",
    ]

    assert employee_registry.calls == [
        (EMPLOYEE_ID, TENANT)
    ]

    assert len(client.sessions) == 1
    assert client.sessions[0].start_calls == 1
    assert client.sessions[0].commit_calls == 1
    assert client.sessions[0].abort_calls == 0


def test_missing_employee_fails_before_session() -> None:
    client = FakeMongoClient()

    with pytest.raises(
        service.EmployeeRelationServiceEmployeeNotFoundError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(None),
            relation_collection=FakeCollection(),
            mongo_client=client,
        )

    assert client.sessions == []


def test_employee_id_projection_must_match() -> None:
    client = FakeMongoClient()

    with pytest.raises(
        service.EmployeeRelationServiceEmployeeBindingError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee(
                    employee_id="employee-other"
                )
            ),
            relation_collection=FakeCollection(),
            mongo_client=client,
        )

    assert client.sessions == []


def test_employee_tenant_projection_must_match() -> None:
    client = FakeMongoClient()

    with pytest.raises(
        service.EmployeeRelationServiceEmployeeBindingError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee(
                    tenant_id="tenant-other"
                )
            ),
            relation_collection=FakeCollection(),
            mongo_client=client,
        )

    assert client.sessions == []


def test_relation_must_be_exact_domain_type() -> None:
    with pytest.raises(
        service.EmployeeRelationServiceInputError
    ):
        service.record_employee_relation(
            object(),  # type: ignore[arg-type]
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee()
            ),
            relation_collection=FakeCollection(),
            mongo_client=FakeMongoClient(),
        )


def test_missing_dependencies_fail_closed() -> None:
    value = relation()

    for kwargs in (
        {
            "employee_registry": None,
            "relation_collection": FakeCollection(),
            "mongo_client": FakeMongoClient(),
        },
        {
            "employee_registry": FakeEmployeeRegistry(
                FakeEmployee()
            ),
            "relation_collection": None,
            "mongo_client": FakeMongoClient(),
        },
        {
            "employee_registry": FakeEmployeeRegistry(
                FakeEmployee()
            ),
            "relation_collection": FakeCollection(),
            "mongo_client": None,
        },
    ):
        with pytest.raises(
            service.EmployeeRelationServiceDependencyError
        ):
            service.record_employee_relation(
                value,
                **kwargs,
            )


def test_registry_conflict_aborts_and_propagates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeMongoClient()

    def fail(
        relation: EmployeeRelation,
        collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        raise EmployeeRelationRegistryConflictError()

    monkeypatch.setattr(
        service,
        "persist_relation",
        fail,
    )

    with pytest.raises(
        EmployeeRelationRegistryConflictError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee()
            ),
            relation_collection=FakeCollection(),
            mongo_client=client,
        )

    assert len(client.sessions) == 1
    assert client.sessions[0].abort_calls == 1
    assert client.sessions[0].commit_calls == 0


def test_registry_retry_required_retries_whole_transaction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeMongoClient()
    attempts = 0

    def persist(
        passed: EmployeeRelation,
        collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise (
                EmployeeRelationRegistryRetryRequiredError()
            )

        return passed

    monkeypatch.setattr(
        service,
        "persist_relation",
        persist,
    )

    value = relation()

    result = service.record_employee_relation(
        value,
        employee_registry=FakeEmployeeRegistry(
            FakeEmployee()
        ),
        relation_collection=FakeCollection(),
        mongo_client=client,
        max_attempts=2,
    )

    assert result == value
    assert attempts == 2
    assert len(client.sessions) == 2
    assert client.sessions[0].abort_calls == 1
    assert client.sessions[1].commit_calls == 1


def test_retry_exhaustion_propagates_retry_required(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeMongoClient()

    def fail(
        relation: EmployeeRelation,
        collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        raise (
            EmployeeRelationRegistryRetryRequiredError()
        )

    monkeypatch.setattr(
        service,
        "persist_relation",
        fail,
    )

    with pytest.raises(
        EmployeeRelationRegistryRetryRequiredError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee()
            ),
            relation_collection=FakeCollection(),
            mongo_client=client,
            max_attempts=2,
        )

    assert len(client.sessions) == 2
    assert all(
        item.abort_calls == 1
        for item in client.sessions
    )


def test_unexpected_persistence_failure_aborts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeMongoClient()

    def fail(
        relation: EmployeeRelation,
        collection: Any,
        *,
        session: Any,
    ) -> EmployeeRelation:
        raise RuntimeError(
            "database failure"
        )

    monkeypatch.setattr(
        service,
        "persist_relation",
        fail,
    )

    with pytest.raises(
        RuntimeError
    ):
        service.record_employee_relation(
            relation(),
            employee_registry=FakeEmployeeRegistry(
                FakeEmployee()
            ),
            relation_collection=FakeCollection(),
            mongo_client=client,
        )

    assert len(client.sessions) == 1
    assert client.sessions[0].abort_calls == 1
    assert client.sessions[0].commit_calls == 0


def test_service_executable_ast_has_no_forbidden_authority() -> None:
    source = service.__file__

    assert source is not None

    text = pathlib.Path(
        source
    ).read_text(
        encoding="utf-8",
    )

    tree = ast.parse(text)

    imported_roots: set[str] = set()
    defined_functions: set[str] = set()
    called_symbols: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(
                alias.name.split(".", 1)[0]
                for alias in node.names
            )

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_roots.add(
                    node.module.split(".", 1)[0]
                )

        elif isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            defined_functions.add(
                node.name
            )

        elif isinstance(node, ast.Call):
            fn = node.func

            if isinstance(fn, ast.Name):
                called_symbols.add(
                    fn.id
                )

            elif isinstance(fn, ast.Attribute):
                called_symbols.add(
                    fn.attr
                )

    forbidden_import_roots = {
        "fastapi",
        "flask",
        "django",
        "requests",
        "httpx",
    }

    forbidden_functions = {
        "update_relation",
        "delete_relation",
        "execute_payment",
        "settle_payment",
        "release_payment",
        "generate_artifact",
        "calculate_payroll",
        "execute_payroll",
    }

    assert imported_roots.isdisjoint(
        forbidden_import_roots
    )

    assert defined_functions.isdisjoint(
        forbidden_functions
    )

    assert called_symbols.isdisjoint(
        forbidden_functions
    )

    assert "APIRouter" not in text
    assert "bank_account" not in text
    assert "financial_execution_command" not in text
