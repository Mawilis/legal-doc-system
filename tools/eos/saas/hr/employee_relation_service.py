"""WILSY OS EmployeeRelation transactional orchestration service.

TITLE: Employee Relation Service
VERSION: v1.0.0-P0-C12E3B-EMPLOYEE-RELATION-SERVICE
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Bind one immutable EmployeeRelation to an existing authoritative
employee and persist it under a service-owned Mongo transaction.

CONSISTENCY BOUNDARY:
EmployeeRegistry does not accept a caller-owned Mongo session.
Employee identity is verified immediately before opening the
EmployeeRelation persistence transaction. No stronger atomic
employee+relation observation is claimed.

AUTHORITY EXCLUSIONS:
This service grants no IAM authority, exposes no HTTP/BFF route,
owns no relation update/delete operation, generates no artifacts,
performs no payroll calculation or execution, and performs no
payment, settlement, release, or other financial execution.
"""

from __future__ import annotations

from typing import Any, Final, NoReturn

from tools.eos.saas.domain.hr_operations import (
    EmployeeRelation,
)
from tools.eos.saas.hr.employee_relation_registry import (
    EmployeeRelationRegistryRetryRequiredError,
    persist_relation,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12E3B-EMPLOYEE-RELATION-SERVICE"
)

MAX_TRANSACTION_ATTEMPTS: Final[int] = 3


class EmployeeRelationServiceError(RuntimeError):
    default_code = "P0_C12E3B_SERVICE_ERROR"

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = (
            code
            or self.default_code
        )
        super().__init__(self.code)


class EmployeeRelationServiceInputError(
    EmployeeRelationServiceError
):
    default_code = (
        "P0_C12E3B_RELATION_INPUT_INVALID"
    )


class EmployeeRelationServiceDependencyError(
    EmployeeRelationServiceError
):
    default_code = (
        "P0_C12E3B_DEPENDENCY_REQUIRED"
    )


class EmployeeRelationServiceEmployeeNotFoundError(
    EmployeeRelationServiceError
):
    default_code = (
        "P0_C12E3B_EMPLOYEE_NOT_FOUND"
    )


class EmployeeRelationServiceEmployeeBindingError(
    EmployeeRelationServiceError
):
    default_code = (
        "P0_C12E3B_EMPLOYEE_BINDING_INVALID"
    )


def _raise(
    error_type: type[
        EmployeeRelationServiceError
    ],
    code: str | None = None,
) -> NoReturn:
    raise error_type(code)


def _require_dependency(
    name: str,
    value: Any,
) -> Any:
    if value is None:
        _raise(
            EmployeeRelationServiceDependencyError,
            f"P0_C12E3B_{name.upper()}_REQUIRED",
        )

    return value


def _bind_employee(
    relation: EmployeeRelation,
    employee_registry: Any,
) -> Any:
    try:
        employee = (
            employee_registry.get_employee_by_id(
                relation.employee_id,
                relation.tenant_id,
            )
        )
    except AttributeError:
        _raise(
            EmployeeRelationServiceDependencyError,
            "P0_C12E3B_EMPLOYEE_REGISTRY_INTERFACE_INVALID",
        )

    if employee is None:
        _raise(
            EmployeeRelationServiceEmployeeNotFoundError
        )

    if (
        getattr(
            employee,
            "employeeId",
            None,
        )
        != relation.employee_id
    ):
        _raise(
            EmployeeRelationServiceEmployeeBindingError,
            "P0_C12E3B_EMPLOYEE_ID_MISMATCH",
        )

    if (
        getattr(
            employee,
            "tenantId",
            None,
        )
        != relation.tenant_id
    ):
        _raise(
            EmployeeRelationServiceEmployeeBindingError,
            "P0_C12E3B_EMPLOYEE_TENANT_MISMATCH",
        )

    return employee


def record_employee_relation(
    relation: EmployeeRelation,
    *,
    employee_registry: Any,
    relation_collection: Any,
    mongo_client: Any,
    max_attempts: int = MAX_TRANSACTION_ATTEMPTS,
) -> EmployeeRelation:
    """Record one immutable employee relation."""

    if type(relation) is not EmployeeRelation:
        _raise(
            EmployeeRelationServiceInputError
        )

    employee_registry = _require_dependency(
        "employee_registry",
        employee_registry,
    )

    relation_collection = _require_dependency(
        "relation_collection",
        relation_collection,
    )

    mongo_client = _require_dependency(
        "mongo_client",
        mongo_client,
    )

    _bind_employee(
        relation,
        employee_registry,
    )

    try:
        requested_attempts = int(
            max_attempts
        )
    except (
        TypeError,
        ValueError,
    ):
        _raise(
            EmployeeRelationServiceInputError,
            "P0_C12E3B_MAX_ATTEMPTS_INVALID",
        )

    attempts = min(
        max(
            1,
            requested_attempts,
        ),
        MAX_TRANSACTION_ATTEMPTS,
    )

    for attempt in range(attempts):
        try:
            session_context = (
                mongo_client.start_session()
            )
        except AttributeError:
            _raise(
                EmployeeRelationServiceDependencyError,
                "P0_C12E3B_MONGO_CLIENT_INTERFACE_INVALID",
            )

        with session_context as session:
            try:
                session.start_transaction()
            except AttributeError:
                _raise(
                    EmployeeRelationServiceDependencyError,
                    "P0_C12E3B_SESSION_INTERFACE_INVALID",
                )

            try:
                persisted = persist_relation(
                    relation,
                    relation_collection,
                    session=session,
                )

                session.commit_transaction()

                return persisted

            except (
                EmployeeRelationRegistryRetryRequiredError
            ):
                if getattr(
                    session,
                    "in_transaction",
                    False,
                ):
                    session.abort_transaction()

                if (
                    attempt + 1
                    >= attempts
                ):
                    raise

            except Exception:
                if getattr(
                    session,
                    "in_transaction",
                    False,
                ):
                    session.abort_transaction()

                raise

    raise (
        EmployeeRelationRegistryRetryRequiredError()
    )


class EmployeeRelationService:
    record_employee_relation = staticmethod(
        record_employee_relation
    )


__all__ = [
    "MAX_TRANSACTION_ATTEMPTS",
    "VERSION",
    "EmployeeRelationService",
    "EmployeeRelationServiceDependencyError",
    "EmployeeRelationServiceEmployeeBindingError",
    "EmployeeRelationServiceEmployeeNotFoundError",
    "EmployeeRelationServiceError",
    "EmployeeRelationServiceInputError",
    "record_employee_relation",
]
