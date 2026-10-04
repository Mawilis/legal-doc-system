"""WILSY OS durable immutable EmployeeRelation registry.

TITLE: Employee Relation Registry
VERSION: v1.0.0-P0-C12E2A-EMPLOYEE-RELATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Persist immutable EmployeeRelation evidence with exact tenant,
identity and employee scoping under caller-owned active Mongo
transactions.

AUTHORITY BOUNDARY:
Persistence only. This registry does not issue employee-relations
authority, authenticate a principal, authorize sanctions, execute
dismissal, calculate payroll, execute payment, generate artifacts,
expose HTTP, provide BFF transport, or wire the browser client.

TRANSACTION BOUNDARY:
The caller owns every transaction. This module never starts,
commits, aborts or retries a transaction.

IMMUTABILITY:
Append-only exact replay. No update, delete or TTL authority.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final, NoReturn, cast

from bson.codec_options import CodecOptions
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.hr_operations import (
    EMPLOYEE_RELATION_FIELDS,
    EmployeeRelation,
    EmployeeRelationError,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12E2A-EMPLOYEE-RELATION-REGISTRY"
)

COLLECTION: Final[str] = (
    "hr_employee_relations"
)

RELATION_ID_INDEX_NAME: Final[str] = (
    "hr_employee_relation_tenant_relation_unique"
)

FINGERPRINT_INDEX_NAME: Final[str] = (
    "hr_employee_relation_tenant_fingerprint_unique"
)

EMPLOYEE_INCIDENT_INDEX_NAME: Final[str] = (
    "hr_employee_relation_tenant_employee_incident"
)

MAX_EMPLOYEE_RELATIONS: Final[int] = 1000

WRITE_CONCERN: Final[WriteConcern] = WriteConcern(
    w="majority",
    j=True,
)

READ_CONCERN: Final[ReadConcern] = ReadConcern(
    "majority"
)


class EmployeeRelationRegistryError(RuntimeError):
    default_code = "P0_C12E2A_REGISTRY_ERROR"

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = (
            code
            or self.default_code
        )
        super().__init__(
            self.code
        )


class EmployeeRelationRegistryInputError(
    EmployeeRelationRegistryError
):
    default_code = (
        "P0_C12E2A_INPUT_INVALID"
    )


class EmployeeRelationRegistryTransactionRequiredError(
    EmployeeRelationRegistryError
):
    default_code = (
        "P0_C12E2A_ACTIVE_TRANSACTION_REQUIRED"
    )


class EmployeeRelationRegistryNotFoundError(
    EmployeeRelationRegistryError
):
    default_code = (
        "P0_C12E2A_RELATION_NOT_FOUND"
    )


class EmployeeRelationRegistryConflictError(
    EmployeeRelationRegistryError
):
    default_code = (
        "P0_C12E2A_RELATION_CONFLICT"
    )


class EmployeeRelationRegistryPersistedRecordInvalidError(
    EmployeeRelationRegistryError
):
    default_code = (
        "P0_C12E2A_PERSISTED_RECORD_INVALID"
    )


class EmployeeRelationRegistryRetryRequiredError(
    EmployeeRelationRegistryError
):
    default_code = (
        "P0_C12E2A_WHOLE_TRANSACTION_RETRY_REQUIRED"
    )


class EmployeeRelationRegistryPersistenceUnavailableError(
    EmployeeRelationRegistryError
):
    default_code = (
        "P0_C12E2A_PERSISTENCE_UNAVAILABLE"
    )


def _raise(
    error_type: type[
        EmployeeRelationRegistryError
    ],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _raise_mongo(
    error: PyMongoError,
) -> NoReturn:
    if error.has_error_label(
        "TransientTransactionError"
    ):
        _raise(
            EmployeeRelationRegistryRetryRequiredError,
            cause=error,
        )

    _raise(
        EmployeeRelationRegistryPersistenceUnavailableError,
        cause=error,
    )


def _target(
    collection: Any,
) -> Any:
    try:
        return collection.with_options(
            write_concern=WRITE_CONCERN,
            read_concern=READ_CONCERN,
            codec_options=CodecOptions(
                tz_aware=True,
            ),
        )
    except AttributeError:
        return collection


def _collection(
    value: Any,
) -> Any:
    if value is None:
        _raise(
            EmployeeRelationRegistryInputError,
            "P0_C12E2A_COLLECTION_REQUIRED",
        )

    return _target(
        value
    )


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        _raise(
            EmployeeRelationRegistryTransactionRequiredError
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        _raise(
            EmployeeRelationRegistryTransactionRequiredError
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
    ):
        _raise(
            EmployeeRelationRegistryInputError,
            f"P0_C12E2A_{name.upper()}_INVALID",
        )

    return value


def _fingerprint(
    value: object,
) -> str:
    text = _text(
        "fingerprint",
        value,
    )

    if (
        len(text) != 128
        or any(
            character
            not in "0123456789abcdef"
            for character in text
        )
    ):
        _raise(
            EmployeeRelationRegistryInputError,
            "P0_C12E2A_FINGERPRINT_INVALID",
        )

    return text


def ensure_indexes(
    collection: Any,
) -> None:
    target = _collection(
        collection
    )

    try:
        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "relation_id",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=RELATION_ID_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "fingerprint",
                    ASCENDING,
                ),
            ],
            unique=True,
            name=FINGERPRINT_INDEX_NAME,
        )

        target.create_index(
            [
                (
                    "tenant_id",
                    ASCENDING,
                ),
                (
                    "employee_id",
                    ASCENDING,
                ),
                (
                    "incident_date",
                    DESCENDING,
                ),
            ],
            unique=False,
            name=EMPLOYEE_INCIDENT_INDEX_NAME,
        )

    except PyMongoError as error:
        _raise_mongo(
            error
        )

    except AttributeError as error:
        _raise(
            EmployeeRelationRegistryInputError,
            "P0_C12E2A_COLLECTION_INTERFACE_INVALID",
            error,
        )


def _hydrate(
    document: Mapping[
        str,
        Any,
    ],
) -> EmployeeRelation:
    if not isinstance(
        document,
        Mapping,
    ):
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError
        )

    raw = dict(
        document
    )

    raw.pop(
        "_id",
        None,
    )

    if set(
        raw
    ) != set(
        EMPLOYEE_RELATION_FIELDS
    ):
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_RECORD_SCHEMA_INVALID",
        )

    try:
        value = EmployeeRelation.from_dict(
            cast(
                Mapping[
                    str,
                    object,
                ],
                raw,
            )
        )

    except (
        TypeError,
        ValueError,
        EmployeeRelationError,
    ) as error:
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_RELATION_PAYLOAD_INVALID",
            error,
        )

    if value.to_dict() != raw:
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_RECORD_CORRELATION_INVALID",
        )

    return value


def _rows(
    collection: Any,
    query: Mapping[
        str,
        object,
    ],
    *,
    session: Any,
    limit: int,
    sort: list[
        tuple[
            str,
            int,
        ]
    ] | None = None,
) -> list[
    Mapping[
        str,
        Any,
    ]
]:
    target = _collection(
        collection
    )

    try:
        cursor = target.find(
            dict(
                query
            ),
            session=session,
        )

        if (
            sort is not None
            and hasattr(
                cursor,
                "sort",
            )
        ):
            cursor = cursor.sort(
                sort
            )

        if hasattr(
            cursor,
            "limit",
        ):
            cursor = cursor.limit(
                limit
            )

        return [
            cast(
                Mapping[
                    str,
                    Any,
                ],
                row,
            )
            for row
            in cursor
        ]

    except PyMongoError as error:
        _raise_mongo(
            error
        )

    except AttributeError as error:
        _raise(
            EmployeeRelationRegistryInputError,
            "P0_C12E2A_COLLECTION_INTERFACE_INVALID",
            error,
        )


def get_relation(
    tenant_id: str,
    relation_id: str,
    collection: Any,
    *,
    session: Any,
) -> EmployeeRelation:
    tx = _active_transaction(
        session
    )

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    identity = _text(
        "relation_id",
        relation_id,
    )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "relation_id": identity,
        },
        session=tx,
        limit=2,
    )

    if not rows:
        _raise(
            EmployeeRelationRegistryNotFoundError
        )

    if len(rows) > 1:
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_DUPLICATE_RELATION_ID",
        )

    return _hydrate(
        rows[0]
    )


def get_relation_by_fingerprint(
    tenant_id: str,
    fingerprint: str,
    collection: Any,
    *,
    session: Any,
) -> EmployeeRelation:
    tx = _active_transaction(
        session
    )

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    digest = _fingerprint(
        fingerprint
    )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "fingerprint": digest,
        },
        session=tx,
        limit=2,
    )

    if not rows:
        _raise(
            EmployeeRelationRegistryNotFoundError
        )

    if len(rows) > 1:
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_DUPLICATE_RELATION_FINGERPRINT",
        )

    return _hydrate(
        rows[0]
    )


def list_employee_relations(
    tenant_id: str,
    employee_id: str,
    collection: Any,
    *,
    session: Any,
) -> tuple[
    EmployeeRelation,
    ...,
]:
    tx = _active_transaction(
        session
    )

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    employee = _text(
        "employee_id",
        employee_id,
    )

    rows = _rows(
        collection,
        {
            "tenant_id": tenant,
            "employee_id": employee,
        },
        session=tx,
        limit=MAX_EMPLOYEE_RELATIONS + 1,
        sort=[
            (
                "incident_date",
                DESCENDING,
            ),
            (
                "relation_id",
                ASCENDING,
            ),
        ],
    )

    if (
        len(rows)
        > MAX_EMPLOYEE_RELATIONS
    ):
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_EMPLOYEE_RELATION_LIMIT_EXCEEDED",
        )

    values = tuple(
        _hydrate(
            row
        )
        for row
        in rows
    )

    if any(
        value.tenant_id
        != tenant
        or value.employee_id
        != employee
        for value
        in values
    ):
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_SCOPE_CORRELATION_INVALID",
        )

    return tuple(
        sorted(
            values,
            key=lambda item: (
                item.incident_date
                or "",
                item.relation_id,
            ),
            reverse=True,
        )
    )


def persist_relation(
    relation: EmployeeRelation,
    collection: Any,
    *,
    session: Any,
) -> EmployeeRelation:
    tx = _active_transaction(
        session
    )

    if type(
        relation
    ) is not EmployeeRelation:
        _raise(
            EmployeeRelationRegistryInputError,
            "P0_C12E2A_EMPLOYEE_RELATION_REQUIRED",
        )

    try:
        relation.__post_init__()
    except Exception as error:
        _raise(
            EmployeeRelationRegistryInputError,
            "P0_C12E2A_EMPLOYEE_RELATION_INVALID",
            error,
        )

    target = _collection(
        collection
    )

    existing = _rows(
        target,
        {
            "tenant_id": relation.tenant_id,
            "relation_id": relation.relation_id,
        },
        session=tx,
        limit=2,
    )

    if len(
        existing
    ) > 1:
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_DUPLICATE_RELATION_ID",
        )

    if existing:
        hydrated = _hydrate(
            existing[0]
        )

        if (
            hydrated.to_dict()
            == relation.to_dict()
        ):
            return hydrated

        _raise(
            EmployeeRelationRegistryConflictError
        )

    by_fingerprint = _rows(
        target,
        {
            "tenant_id": relation.tenant_id,
            "fingerprint": relation.fingerprint,
        },
        session=tx,
        limit=2,
    )

    if len(
        by_fingerprint
    ) > 1:
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_DUPLICATE_RELATION_FINGERPRINT",
        )

    if by_fingerprint:
        hydrated = _hydrate(
            by_fingerprint[0]
        )

        if (
            hydrated.to_dict()
            == relation.to_dict()
        ):
            return hydrated

        _raise(
            EmployeeRelationRegistryConflictError
        )

    try:
        target.insert_one(
            relation.to_dict(),
            session=tx,
        )

    except DuplicateKeyError:
        # A competing writer may have inserted either immutable
        # identity first. Re-read both exact identities. Exact
        # replay succeeds; divergence fails closed.
        try:
            return get_relation(
                relation.tenant_id,
                relation.relation_id,
                target,
                session=tx,
            )
        except EmployeeRelationRegistryNotFoundError:
            try:
                replay = get_relation_by_fingerprint(
                    relation.tenant_id,
                    relation.fingerprint,
                    target,
                    session=tx,
                )
            except EmployeeRelationRegistryNotFoundError:
                _raise(
                    EmployeeRelationRegistryRetryRequiredError
                )

            if (
                replay.to_dict()
                == relation.to_dict()
            ):
                return replay

            _raise(
                EmployeeRelationRegistryConflictError
            )

    except PyMongoError as error:
        _raise_mongo(
            error
        )

    persisted = get_relation(
        relation.tenant_id,
        relation.relation_id,
        target,
        session=tx,
    )

    if (
        persisted.to_dict()
        != relation.to_dict()
    ):
        _raise(
            EmployeeRelationRegistryPersistedRecordInvalidError,
            "P0_C12E2A_POST_WRITE_CORRELATION_INVALID",
        )

    return persisted


class EmployeeRelationRegistry:
    ensure_indexes = staticmethod(
        ensure_indexes
    )

    get_relation = staticmethod(
        get_relation
    )

    get_relation_by_fingerprint = staticmethod(
        get_relation_by_fingerprint
    )

    list_employee_relations = staticmethod(
        list_employee_relations
    )

    persist_relation = staticmethod(
        persist_relation
    )


__all__ = [
    "COLLECTION",
    "EMPLOYEE_INCIDENT_INDEX_NAME",
    "FINGERPRINT_INDEX_NAME",
    "MAX_EMPLOYEE_RELATIONS",
    "READ_CONCERN",
    "RELATION_ID_INDEX_NAME",
    "VERSION",
    "WRITE_CONCERN",
    "EmployeeRelationRegistry",
    "EmployeeRelationRegistryConflictError",
    "EmployeeRelationRegistryError",
    "EmployeeRelationRegistryInputError",
    "EmployeeRelationRegistryNotFoundError",
    "EmployeeRelationRegistryPersistedRecordInvalidError",
    "EmployeeRelationRegistryPersistenceUnavailableError",
    "EmployeeRelationRegistryRetryRequiredError",
    "EmployeeRelationRegistryTransactionRequiredError",
    "ensure_indexes",
    "get_relation",
    "get_relation_by_fingerprint",
    "list_employee_relations",
    "persist_relation",
]
