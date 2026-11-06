"""Revision-guarded POS return and refund capacity reservations.

This registry prevents concurrent return quantities or refund intents from
exceeding the original commercial sale. It owns no payment execution, refund
execution, paid state or settlement truth. Caller owns the transaction.
"""
from __future__ import annotations

from hashlib import sha3_512
import json
from typing import Any

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.pos_commercial import POSSale, POSStatus


COLLECTION_NAME = "pos_commercial_capacity_current"


class POSCommercialCapacityError(RuntimeError):
    pass


class POSCommercialCapacityConflict(POSCommercialCapacityError):
    pass


class POSCommercialCapacityExceeded(POSCommercialCapacityError):
    pass


def _tx(session: Any) -> Any:
    if session is None or not callable(getattr(session, "with_transaction", None)) or getattr(session, "has_ended", True):
        raise POSCommercialCapacityError("POS_CAPACITY_LIVE_CALLER_SESSION_REQUIRED")
    return session


def _fingerprint(value: dict) -> str:
    return sha3_512(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def ensure_indexes(collection: Any) -> None:
    try:
        collection.create_index(
            [("tenant_id", ASCENDING), ("location_id", ASCENDING), ("sale_id", ASCENDING), ("capacity_type", ASCENDING), ("capacity_key", ASCENDING)],
            unique=True, name="pos_commercial_capacity_identity_unique",
        )
    except (AttributeError, PyMongoError) as error:
        raise POSCommercialCapacityError("POS_CAPACITY_INDEX_UNAVAILABLE") from error


def _read(identity: dict, collection: Any, session: Any) -> dict | None:
    row = collection.find_one(identity, session=session)
    if row is None:
        return None
    row.pop("_id", None)
    fingerprint = row.pop("fingerprint", None)
    if fingerprint != _fingerprint(row):
        raise POSCommercialCapacityError("POS_CAPACITY_PERSISTED_FINGERPRINT_INVALID")
    row["fingerprint"] = fingerprint
    return row


def _reserve(*, sale: POSSale, capacity_type: str, capacity_key: str,
             amount: int, maximum: int, idempotency_key: str,
             collection: Any, session: Any) -> dict:
    tx = _tx(session)
    if type(sale) is not POSSale or sale.status is not POSStatus.COMPLETED_COMMERCIAL:
        raise POSCommercialCapacityError("POS_CAPACITY_FINAL_SALE_REQUIRED")
    if type(amount) is not int or amount <= 0 or type(maximum) is not int or maximum <= 0:
        raise POSCommercialCapacityError("POS_CAPACITY_AMOUNT_INVALID")
    if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip():
        raise POSCommercialCapacityError("POS_CAPACITY_IDEMPOTENCY_KEY_INVALID")
    identity = {
        "tenant_id": sale.tenant_id, "location_id": sale.location_id,
        "sale_id": sale.sale_id, "capacity_type": capacity_type,
        "capacity_key": capacity_key,
    }
    current = _read(identity, collection, tx)
    reserved = 0 if current is None else current["reserved_amount"]
    if current is not None and current["sale_fingerprint"] != sale.fingerprint:
        raise POSCommercialCapacityError("POS_CAPACITY_SALE_FINGERPRINT_MISMATCH")
    if reserved + amount > maximum:
        raise POSCommercialCapacityExceeded("POS_CAPACITY_EXCEEDED")
    revision = 0 if current is None else current["revision"] + 1
    payload = {
        "schema": "WILSY-POS-COMMERCIAL-CAPACITY/V1",
        "version": "v1.0.0-POS-COMMERCIAL-CAPACITY",
        **identity,
        "sale_fingerprint": sale.fingerprint,
        "revision": revision,
        "reserved_amount": reserved + amount,
        "maximum_amount": maximum,
        "last_idempotency_key": idempotency_key,
    }
    record = {**payload, "fingerprint": _fingerprint(payload)}
    try:
        if current is None:
            collection.insert_one(dict(record), session=tx)
        else:
            result = collection.replace_one(
                {**identity, "revision": current["revision"], "fingerprint": current["fingerprint"]},
                record, session=tx,
            )
            if getattr(result, "matched_count", 0) != 1:
                raise POSCommercialCapacityConflict("POS_CAPACITY_STALE_REVISION")
    except DuplicateKeyError as error:
        raise POSCommercialCapacityConflict("POS_CAPACITY_INITIAL_INSERT_RACE") from error
    except PyMongoError as error:
        raise POSCommercialCapacityError("POS_CAPACITY_PERSISTENCE_UNAVAILABLE") from error
    persisted = _read(identity, collection, tx)
    if persisted is None or persisted != record:
        raise POSCommercialCapacityError("POS_CAPACITY_READBACK_MISMATCH")
    return persisted


def reserve_return(*, sale: POSSale, sku: str, quantity: int,
                   idempotency_key: str, collection: Any, session: Any) -> dict:
    _tx(session)
    line = next((item for item in sale.lines if item.sku == sku), None)
    if line is None:
        raise POSCommercialCapacityError("POS_RETURN_SKU_NOT_IN_SALE")
    return _reserve(
        sale=sale, capacity_type="RETURN_QUANTITY", capacity_key=sku,
        amount=quantity, maximum=line.quantity, idempotency_key=idempotency_key,
        collection=collection, session=session,
    )


def reserve_refund(*, sale: POSSale, amount_minor: int,
                   idempotency_key: str, collection: Any, session: Any) -> dict:
    _tx(session)
    return _reserve(
        sale=sale, capacity_type="REFUND_AMOUNT", capacity_key="SALE_TOTAL",
        amount=amount_minor, maximum=sale.total_minor,
        idempotency_key=idempotency_key, collection=collection, session=session,
    )


class POSCommercialCapacityRegistry:
    ensure_indexes = staticmethod(ensure_indexes)
    reserve_return = staticmethod(reserve_return)
    reserve_refund = staticmethod(reserve_refund)


__all__ = [
    "COLLECTION_NAME", "POSCommercialCapacityConflict",
    "POSCommercialCapacityExceeded", "POSCommercialCapacityRegistry",
    "POSCommercialCapacityError", "ensure_indexes", "reserve_refund",
    "reserve_return",
]
