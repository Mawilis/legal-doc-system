"""Caller-transaction-owned persistence for WILSY headcount requisitions.

This registry stores requisition state only. It does not authorize actors,
create audit events, create employees, or provision identity or IAM. Callers
must compose authorization and audit/outbox writes in the same transaction.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.headcount_requisition import (
    HeadcountRequisition,
    RequisitionError,
)


COLLECTION: Final[str] = "hr_headcount_requisitions"
REQUISITION_INDEX: Final[str] = "hr_headcount_requisition_tenant_id_unique"
FINGERPRINT_INDEX: Final[str] = "hr_headcount_requisition_tenant_fingerprint_unique"
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)


class HeadcountRequisitionRegistryError(RuntimeError):
    code = "HEADCOUNT_REQUISITION_REGISTRY_ERROR"


class HeadcountRequisitionRegistryTransactionRequired(HeadcountRequisitionRegistryError):
    code = "HEADCOUNT_REQUISITION_ACTIVE_TRANSACTION_REQUIRED"


class HeadcountRequisitionRegistryNotFound(HeadcountRequisitionRegistryError):
    code = "HEADCOUNT_REQUISITION_NOT_FOUND"


class HeadcountRequisitionRegistryConflict(HeadcountRequisitionRegistryError):
    code = "HEADCOUNT_REQUISITION_REVISION_CONFLICT"


class HeadcountRequisitionRegistryUnavailable(HeadcountRequisitionRegistryError):
    code = "HEADCOUNT_REQUISITION_PERSISTENCE_UNAVAILABLE"


def _transaction(session: Any) -> Any:
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        raise HeadcountRequisitionRegistryTransactionRequired()
    return session


def _target(collection: Any) -> Any:
    if collection is None:
        raise HeadcountRequisitionRegistryUnavailable()
    try:
        return collection.with_options(write_concern=WRITE_CONCERN)
    except AttributeError:
        return collection


def ensure_indexes(collection: Any) -> None:
    target = _target(collection)
    try:
        target.create_index(
            [("tenant_id", ASCENDING), ("requisition_id", ASCENDING)],
            unique=True,
            name=REQUISITION_INDEX,
        )
        target.create_index(
            [("tenant_id", ASCENDING), ("fingerprint", ASCENDING)],
            unique=True,
            name=FINGERPRINT_INDEX,
        )
    except PyMongoError as error:
        raise HeadcountRequisitionRegistryUnavailable() from error


def _hydrate(row: Mapping[str, Any]) -> HeadcountRequisition:
    raw = dict(row)
    raw.pop("_id", None)
    try:
        value = HeadcountRequisition.from_dict(raw)
    except (TypeError, ValueError, RequisitionError) as error:
        raise HeadcountRequisitionRegistryUnavailable() from error
    if value.to_dict() != raw:
        raise HeadcountRequisitionRegistryUnavailable()
    return value


def get_requisition(
    tenant_id: str,
    requisition_id: str,
    collection: Any,
    *,
    session: Any,
) -> HeadcountRequisition:
    tx = _transaction(session)
    try:
        rows = list(_target(collection).find(
            {"tenant_id": tenant_id, "requisition_id": requisition_id},
            session=tx,
        ).limit(2))
    except PyMongoError as error:
        raise HeadcountRequisitionRegistryUnavailable() from error
    if not rows:
        raise HeadcountRequisitionRegistryNotFound()
    if len(rows) != 1:
        raise HeadcountRequisitionRegistryUnavailable()
    return _hydrate(rows[0])


def create_requisition(
    value: HeadcountRequisition,
    collection: Any,
    *,
    session: Any,
) -> HeadcountRequisition:
    tx = _transaction(session)
    if type(value) is not HeadcountRequisition or value.revision != 1:
        raise HeadcountRequisitionRegistryConflict()
    target = _target(collection)
    document = value.to_dict()
    try:
        existing = list(target.find(
            {"tenant_id": value.tenant_id, "requisition_id": value.requisition_id},
            session=tx,
        ).limit(2))
        if existing:
            if len(existing) == 1 and _hydrate(existing[0]).to_dict() == document:
                return value
            raise HeadcountRequisitionRegistryConflict()
        target.insert_one(document, session=tx)
        return value
    except DuplicateKeyError as error:
        raise HeadcountRequisitionRegistryConflict() from error
    except PyMongoError as error:
        raise HeadcountRequisitionRegistryUnavailable() from error


def replace_requisition(
    value: HeadcountRequisition,
    *,
    expected_revision: int,
    expected_fingerprint: str,
    collection: Any,
    session: Any,
) -> HeadcountRequisition:
    tx = _transaction(session)
    if type(value) is not HeadcountRequisition or value.revision != expected_revision + 1:
        raise HeadcountRequisitionRegistryConflict()
    target = _target(collection)
    try:
        result = target.replace_one(
            {
                "tenant_id": value.tenant_id,
                "requisition_id": value.requisition_id,
                "revision": expected_revision,
                "fingerprint": expected_fingerprint,
            },
            value.to_dict(),
            upsert=False,
            session=tx,
        )
        if result.modified_count == 1:
            return value
        current = list(target.find(
            {"tenant_id": value.tenant_id, "requisition_id": value.requisition_id},
            session=tx,
        ).limit(2))
        if len(current) == 1 and _hydrate(current[0]).to_dict() == value.to_dict():
            return value
        if not current:
            raise HeadcountRequisitionRegistryNotFound()
        raise HeadcountRequisitionRegistryConflict()
    except (HeadcountRequisitionRegistryNotFound, HeadcountRequisitionRegistryConflict):
        raise
    except DuplicateKeyError as error:
        raise HeadcountRequisitionRegistryConflict() from error
    except PyMongoError as error:
        raise HeadcountRequisitionRegistryUnavailable() from error


__all__ = [
    "COLLECTION", "REQUISITION_INDEX", "FINGERPRINT_INDEX",
    "HeadcountRequisitionRegistryError", "HeadcountRequisitionRegistryTransactionRequired",
    "HeadcountRequisitionRegistryNotFound", "HeadcountRequisitionRegistryConflict",
    "HeadcountRequisitionRegistryUnavailable", "ensure_indexes", "get_requisition",
    "create_requisition", "replace_requisition",
]
