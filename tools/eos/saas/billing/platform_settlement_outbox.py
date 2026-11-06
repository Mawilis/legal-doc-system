"""Governed delivery of WILSY OS platform-settlement outbox events.

The outbox is a delivery queue, not financial authority. Delivery handlers must
be idempotent on event_key. A lease token fences stale workers after expiry.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping

from pymongo import ReturnDocument
from pymongo.collection import Collection


class SettlementOutboxError(RuntimeError):
    """Fail-closed outbox state or ownership error."""


def _aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise SettlementOutboxError("SETTLEMENT_OUTBOX_TIMESTAMP_INVALID")
    return value.astimezone(timezone.utc)


def claim_next_settlement_event(
    collection: Collection,
    *,
    worker_id: str,
    lease_token: str,
    now: datetime,
    lease_seconds: int = 60,
    session: Any = None,
) -> dict[str, Any] | None:
    """Claim one due event or reclaim an expired lease using an atomic CAS."""
    now = _aware(now)
    if not worker_id.strip() or not lease_token.strip() or lease_seconds <= 0:
        raise SettlementOutboxError("SETTLEMENT_OUTBOX_CLAIM_ARGUMENT_INVALID")
    query = {
        "$or": [
            {"delivery_status": {"$in": ["PENDING", "RETRY"]}, "available_at": {"$lte": now.isoformat()}},
            {"delivery_status": "CLAIMED", "lease_until": {"$lte": now}},
        ]
    }
    update = {
        "$set": {
            "delivery_status": "CLAIMED",
            "claimed_by": worker_id,
            "lease_token": lease_token,
            "lease_until": now + timedelta(seconds=lease_seconds),
            "updated_at": now.isoformat(),
        },
        "$inc": {"delivery_attempts": 1},
    }
    return collection.find_one_and_update(
        query,
        update,
        sort=[("available_at", 1), ("event_key", 1)],
        return_document=ReturnDocument.AFTER,
        session=session,
    )


def mark_settlement_event_delivered(
    collection: Collection,
    *,
    tenant_id: str,
    event_key: str,
    worker_id: str,
    lease_token: str,
    delivered_at: datetime,
    session: Any = None,
) -> bool:
    """Acknowledge only the current lease owner; never mutate audit evidence."""
    delivered_at = _aware(delivered_at)
    result = collection.update_one(
        {
            "tenant_id": tenant_id,
            "event_key": event_key,
            "delivery_status": "CLAIMED",
            "claimed_by": worker_id,
            "lease_token": lease_token,
        },
        {
            "$set": {
                "delivery_status": "DELIVERED",
                "delivered_at": delivered_at.isoformat(),
                "updated_at": delivered_at.isoformat(),
            },
            "$unset": {"claimed_by": "", "lease_token": "", "lease_until": "", "last_error_code": ""},
        },
        session=session,
    )
    return result.modified_count == 1


def schedule_settlement_event_retry(
    collection: Collection,
    *,
    tenant_id: str,
    event_key: str,
    worker_id: str,
    lease_token: str,
    retry_at: datetime,
    error_code: str,
    session: Any = None,
) -> bool:
    """Release a claimed event for retry using a bounded, non-sensitive code."""
    retry_at = _aware(retry_at)
    if not error_code or len(error_code) > 96 or not error_code.replace("_", "").isalnum():
        raise SettlementOutboxError("SETTLEMENT_OUTBOX_ERROR_CODE_INVALID")
    result = collection.update_one(
        {
            "tenant_id": tenant_id,
            "event_key": event_key,
            "delivery_status": "CLAIMED",
            "claimed_by": worker_id,
            "lease_token": lease_token,
        },
        {
            "$set": {
                "delivery_status": "RETRY",
                "available_at": retry_at.isoformat(),
                "last_error_code": error_code,
                "updated_at": retry_at.isoformat(),
            },
            "$unset": {"claimed_by": "", "lease_token": "", "lease_until": ""},
        },
        session=session,
    )
    return result.modified_count == 1


def dispatch_one_settlement_event(
    collection: Collection,
    *,
    worker_id: str,
    lease_token: str,
    now: datetime,
    deliver: Callable[[Mapping[str, Any], str], None],
    lease_seconds: int = 60,
    retry_delay_seconds: int = 60,
) -> str:
    """Deliver one event with event_key as the downstream idempotency key.

    External delivery occurs outside Mongo transactions. The receiver MUST
    deduplicate by event_key because a process may crash after remote success
    but before the local acknowledgement.
    """
    event = claim_next_settlement_event(
        collection,
        worker_id=worker_id,
        lease_token=lease_token,
        now=now,
        lease_seconds=lease_seconds,
    )
    if event is None:
        return "EMPTY"
    identity = {
        "tenant_id": event["tenant_id"],
        "event_key": event["event_key"],
    }
    try:
        deliver(event, event["event_key"])
    except Exception:
        retry_at = _aware(now) + timedelta(seconds=max(1, retry_delay_seconds))
        if not schedule_settlement_event_retry(
            collection,
            **identity,
            worker_id=worker_id,
            lease_token=lease_token,
            retry_at=retry_at,
            error_code="DELIVERY_FAILED",
        ):
            raise SettlementOutboxError("SETTLEMENT_OUTBOX_LEASE_LOST")
        return "RETRY"
    if not mark_settlement_event_delivered(
        collection,
        **identity,
        worker_id=worker_id,
        lease_token=lease_token,
        delivered_at=now,
    ):
        raise SettlementOutboxError("SETTLEMENT_OUTBOX_LEASE_LOST")
    return "DELIVERED"


__all__ = [
    "SettlementOutboxError",
    "claim_next_settlement_event",
    "mark_settlement_event_delivered",
    "schedule_settlement_event_retry",
    "dispatch_one_settlement_event",
]
