"""Immutable Electrum completion inbox plus transactional processing projection."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from pymongo.errors import DuplicateKeyError


class ElectrumCompletionInboxError(RuntimeError):
    pass


class ElectrumCompletionInboxConflict(ElectrumCompletionInboxError):
    pass


class ElectrumCompletionInboxNotFound(ElectrumCompletionInboxError):
    pass


@dataclass(frozen=True, slots=True)
class ElectrumPayShapCompletionInboxEvent:
    provider_name: str
    message_id: str
    message_created_at: datetime
    uetr: str
    transaction_reference: str
    outcome: str
    payment_scheme: str
    payment_method: str
    amount_minor: int
    currency: str
    settlement_date: str | None
    creditor_account_fingerprint: str
    content_digest: str
    signature_key_id: str
    received_at: datetime

    def __post_init__(self):
        for name in ("provider_name", "message_id", "uetr", "transaction_reference",
                     "outcome", "payment_scheme", "payment_method", "currency", "signature_key_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ElectrumCompletionInboxError("ELECTRUM_INBOX_IDENTITY_INVALID")
        if self.provider_name != "ELECTRUM" or self.payment_scheme != "ZA_RPP":
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_PROVIDER_INVALID")
        if isinstance(self.amount_minor, bool) or not isinstance(self.amount_minor, int) or self.amount_minor <= 0:
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_AMOUNT_INVALID")
        for name in ("creditor_account_fingerprint", "content_digest"):
            value = getattr(self, name)
            if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise ElectrumCompletionInboxError("ELECTRUM_INBOX_FINGERPRINT_INVALID")
        for name in ("message_created_at", "received_at"):
            value = getattr(self, name)
            if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
                raise ElectrumCompletionInboxError("ELECTRUM_INBOX_TIMESTAMP_INVALID")
        if self.outcome not in {"APPROVED", "CANCELLED", "PENDING", "REJECTED", "PARTIALLY_ACCEPTED"}:
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_OUTCOME_INVALID")

    @property
    def fingerprint(self) -> str:
        payload = asdict(self)
        payload.pop("received_at", None)
        payload.pop("signature_key_id", None)
        for field in ("message_created_at",):
            payload[field] = payload[field].astimezone(timezone.utc).isoformat()
        return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for field in ("message_created_at", "received_at"):
            payload[field] = payload[field].astimezone(timezone.utc).isoformat()
        payload.update({
            "event_fingerprint": self.fingerprint,
            "processing_status": "PENDING",
            "processing_revision": 0,
            "processed_at": None,
            "allocation_id": None,
            "attempt_count": 0,
            "available_at": payload_received_at if (payload_received_at := payload.get("received_at")) else None,
            "last_error_code": None,
        })
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ElectrumPayShapCompletionInboxEvent":
        fields = {key: value for key, value in payload.items() if key in cls.__dataclass_fields__}
        for field in ("message_created_at", "received_at"):
            if isinstance(fields.get(field), str):
                fields[field] = datetime.fromisoformat(fields[field])
        value = cls(**fields)
        if payload.get("event_fingerprint") != value.fingerprint:
            raise ElectrumCompletionInboxConflict("ELECTRUM_INBOX_FINGERPRINT_MISMATCH")
        return value


class ElectrumPayShapCompletionInboxRegistry:
    @staticmethod
    def ensure_indexes(collection) -> None:
        collection.create_index(
            [("provider_name", 1), ("message_id", 1)],
            unique=True,
            name="uq_electrum_completion_message",
        )
        collection.create_index(
            [("provider_name", 1), ("uetr", 1), ("transaction_reference", 1)],
            unique=True,
            name="uq_electrum_completion_transaction",
        )
        collection.create_index(
            [("processing_status", 1), ("available_at", 1), ("received_at", 1)],
            name="ix_electrum_completion_pending",
        )

    @staticmethod
    def create(value: ElectrumPayShapCompletionInboxEvent, collection, *, session=None):
        message_query = {"provider_name": value.provider_name, "message_id": value.message_id}
        existing = collection.find_one(message_query, session=session)
        if existing is None:
            existing = collection.find_one({
                "provider_name": value.provider_name,
                "uetr": value.uetr,
                "transaction_reference": value.transaction_reference,
            }, session=session)
        if existing is not None:
            try:
                replay = ElectrumPayShapCompletionInboxEvent.from_dict(existing)
            except (TypeError, ValueError, KeyError) as error:
                raise ElectrumCompletionInboxConflict("ELECTRUM_INBOX_PERSISTED_RECORD_INVALID") from error
            if replay.fingerprint == value.fingerprint:
                return replay, True
            raise ElectrumCompletionInboxConflict("ELECTRUM_INBOX_DIVERGENT_REPLAY")
        try:
            collection.insert_one(value.to_dict(), session=session)
        except DuplicateKeyError as error:
            # A concurrent unique-index winner is resolved by retrying the ingress.
            raise ElectrumCompletionInboxConflict("ELECTRUM_INBOX_DUPLICATE_RACE") from error
        return value, False

    @staticmethod
    def get(provider_name: str, message_id: str, collection, *, session=None):
        doc = collection.find_one(
            {"provider_name": provider_name, "message_id": message_id},
            session=session,
        )
        if doc is None:
            raise ElectrumCompletionInboxNotFound("ELECTRUM_INBOX_EVENT_NOT_FOUND")
        try:
            return ElectrumPayShapCompletionInboxEvent.from_dict(doc), doc
        except (TypeError, ValueError, KeyError) as error:
            raise ElectrumCompletionInboxConflict("ELECTRUM_INBOX_PERSISTED_RECORD_INVALID") from error

    @staticmethod
    def mark_processed(
        event: ElectrumPayShapCompletionInboxEvent,
        *,
        collection,
        session,
        processed_at: datetime,
        allocation_id: str | None,
        ignored: bool = False,
        expected_revision: int = 0,
    ) -> None:
        if session is None or not bool(getattr(session, "in_transaction", False)):
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_CALLER_TRANSACTION_REQUIRED")
        if not isinstance(processed_at, datetime) or processed_at.tzinfo is None:
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_PROCESSED_AT_INVALID")
        if not ignored and (not isinstance(allocation_id, str) or not allocation_id.strip()):
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_ALLOCATION_ID_REQUIRED")
        status = "IGNORED" if ignored else "PROCESSED"
        result = collection.update_one(
            {
                "provider_name": event.provider_name,
                "message_id": event.message_id,
                "event_fingerprint": event.fingerprint,
                "processing_status": "PENDING",
                "processing_revision": expected_revision,
            },
            {
                "$set": {
                    "processing_status": status,
                    "processing_revision": expected_revision + 1,
                    "processed_at": processed_at.astimezone(timezone.utc).isoformat(),
                    "allocation_id": allocation_id,
                }
            },
            session=session,
        )
        if result.matched_count != 1:
            raise ElectrumCompletionInboxConflict("ELECTRUM_INBOX_PROCESSING_REVISION_CONFLICT")

    @staticmethod
    def schedule_retry(
        event: ElectrumPayShapCompletionInboxEvent,
        *,
        collection,
        session,
        expected_revision: int,
        expected_attempt_count: int,
        retry_at: datetime,
        error_code: str,
    ) -> None:
        import re
        if session is None or not bool(getattr(session, "in_transaction", False)):
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_CALLER_TRANSACTION_REQUIRED")
        if (
            isinstance(expected_revision, bool) or not isinstance(expected_revision, int) or expected_revision < 0
            or isinstance(expected_attempt_count, bool) or not isinstance(expected_attempt_count, int) or expected_attempt_count < 0
        ):
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_RETRY_REVISION_INVALID")
        if not isinstance(retry_at, datetime) or retry_at.tzinfo is None:
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_RETRY_TIME_INVALID")
        if not isinstance(error_code, str) or re.fullmatch(r"[A-Z0-9_]{1,64}", error_code) is None:
            raise ElectrumCompletionInboxError("ELECTRUM_INBOX_RETRY_CODE_INVALID")
        result = collection.update_one(
            {
                "provider_name": event.provider_name,
                "message_id": event.message_id,
                "event_fingerprint": event.fingerprint,
                "processing_status": "PENDING",
                "processing_revision": expected_revision,
                "attempt_count": expected_attempt_count,
            },
            {
                "$set": {
                    "processing_revision": expected_revision + 1,
                    "attempt_count": expected_attempt_count + 1,
                    "available_at": retry_at.astimezone(timezone.utc).isoformat(),
                    "last_error_code": error_code,
                }
            },
            session=session,
        )
        if result.matched_count != 1:
            raise ElectrumCompletionInboxConflict("ELECTRUM_INBOX_RETRY_REVISION_CONFLICT")


__all__ = [
    "ElectrumCompletionInboxError",
    "ElectrumCompletionInboxConflict",
    "ElectrumCompletionInboxNotFound",
    "ElectrumPayShapCompletionInboxEvent",
    "ElectrumPayShapCompletionInboxRegistry",
]
