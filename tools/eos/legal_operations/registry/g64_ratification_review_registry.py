"""Append-only independent-review and second-approval evidence for G64.

VERSION: v1.0.0-G64-SEPARATION-OF-DUTIES-REVIEW-REGISTRY
AUTHORITY: Review evidence storage only; never establishes institutional authority.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Final, Mapping

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.write_concern import WriteConcern

VERSION: Final[str] = "v1.0.0-G64-SEPARATION-OF-DUTIES-REVIEW-REGISTRY"
COLLECTION: Final[str] = "g64_ratification_review_evidence"
SCHEMA: Final[str] = "WILSY-G64-REVIEW-EVIDENCE/V1"
WRITE_CONCERN: Final[WriteConcern] = WriteConcern(w="majority", j=True)


class G64ReviewRegistryError(RuntimeError):
    """Stable, content-free review-registry failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def ensure_indexes(collection: Any) -> None:
    """Create review event uniqueness and bounded lookup indexes at startup."""
    collection.with_options(write_concern=WRITE_CONCERN).create_index(
        [
            ("tenant_id", ASCENDING),
            ("institution_id", ASCENDING),
            ("record_id", ASCENDING),
            ("event_id", ASCENDING),
        ],
        unique=True,
        name="g64_review_tenant_institution_record_event_unique",
    )
    collection.with_options(write_concern=WRITE_CONCERN).create_index(
        [
            ("tenant_id", ASCENDING),
            ("institution_id", ASCENDING),
            ("record_id", ASCENDING),
            ("created_at", ASCENDING),
        ],
        name="g64_review_record_history",
    )
    for event_type, index_name in (
        ("SECOND_APPROVAL_POLICY", "g64_one_second_approval_policy_per_record"),
        ("SECOND_APPROVAL", "g64_one_second_approval_per_record"),
    ):
        collection.with_options(write_concern=WRITE_CONCERN).create_index(
            [
                ("tenant_id", ASCENDING),
                ("institution_id", ASCENDING),
                ("record_id", ASCENDING),
                ("payload.event_type", ASCENDING),
            ],
            unique=True,
            partialFilterExpression={"payload.event_type": event_type},
            name=index_name,
        )


def _replay_projection(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Exclude server-generated event time so a retry remains idempotent."""
    return {key: value for key, value in payload.items() if key != "created_at"}


def append_review_event(
    *,
    tenant_id: str,
    institution_id: str,
    record_id: str,
    event_id: str,
    payload: Mapping[str, Any],
    collection: Any,
    session: Any,
) -> dict[str, Any]:
    """Append immutable event in the caller's active transaction; exact replay only."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise G64ReviewRegistryError("G64_REVIEW_ACTIVE_TRANSACTION_REQUIRED")
    if not all(isinstance(value, str) and value.strip() == value and value for value in (
        tenant_id, institution_id, record_id, event_id
    )):
        raise G64ReviewRegistryError("G64_REVIEW_IDENTITY_INVALID")
    if not isinstance(payload, Mapping) or payload.get("event_id") != event_id:
        raise G64ReviewRegistryError("G64_REVIEW_PAYLOAD_INVALID")
    try:
        canonical = json.dumps(
            dict(payload), sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise G64ReviewRegistryError("G64_REVIEW_PAYLOAD_INVALID") from error
    digest = hashlib.sha3_512(canonical).hexdigest()
    key = {
        "tenant_id": tenant_id,
        "institution_id": institution_id,
        "record_id": record_id,
        "event_id": event_id,
    }
    target = collection.with_options(write_concern=WRITE_CONCERN)
    try:
        existing = target.find_one(key, session=session)
        if existing is not None:
            previous = existing.get("payload")
            if (
                existing.get("schema") != SCHEMA
                or existing.get("version") != VERSION
                or existing.get("tenant_id") != tenant_id
                or existing.get("institution_id") != institution_id
                or existing.get("record_id") != record_id
                or existing.get("event_id") != event_id
                or not isinstance(previous, dict)
                or existing.get("payload_sha3_512") != hashlib.sha3_512(
                    json.dumps(previous, sort_keys=True, separators=(",", ":"),
                               ensure_ascii=True, allow_nan=False).encode("ascii")
                ).hexdigest()
                or _replay_projection(previous) != _replay_projection(payload)
            ):
                raise G64ReviewRegistryError("G64_REVIEW_IMMUTABLE_EVENT_CONFLICT")
            return existing
        document = {
            **key,
            "schema": SCHEMA,
            "version": VERSION,
            "payload": dict(payload),
            "payload_sha3_512": digest,
            "created_at": payload.get("created_at"),
        }
        target.insert_one(document, session=session)
        return document
    except G64ReviewRegistryError:
        raise
    except DuplicateKeyError as error:
        raise G64ReviewRegistryError("G64_REVIEW_WHOLE_TRANSACTION_RETRY_REQUIRED") from error
    except PyMongoError as error:
        raise G64ReviewRegistryError("G64_REVIEW_PERSISTENCE_UNAVAILABLE") from error


def list_review_events(
    *, tenant_id: str, institution_id: str, record_id: str,
    collection: Any, session: Any, limit: int = 100,
) -> tuple[dict[str, Any], ...]:
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise G64ReviewRegistryError("G64_REVIEW_ACTIVE_TRANSACTION_REQUIRED")
    if type(limit) is not int or not 1 <= limit <= 100:
        raise G64ReviewRegistryError("G64_REVIEW_LIMIT_INVALID")
    target = collection.with_options(write_concern=WRITE_CONCERN)
    rows = target.find(
        {"tenant_id": tenant_id, "institution_id": institution_id, "record_id": record_id},
        session=session,
    ).sort("created_at", -1).limit(limit)
    output = []
    for row in rows:
        payload = row.get("payload")
        if (
            row.get("schema") != SCHEMA
            or row.get("version") != VERSION
            or row.get("tenant_id") != tenant_id
            or row.get("institution_id") != institution_id
            or row.get("record_id") != record_id
            or not isinstance(row.get("event_id"), str)
            or not isinstance(payload, dict)
            or payload.get("event_id") != row.get("event_id")
            or payload.get("tenant_id") != tenant_id
            or payload.get("institution_id") != institution_id
            or payload.get("record_id") != record_id
        ):
            raise G64ReviewRegistryError("G64_REVIEW_PERSISTED_EVENT_INVALID")
        try:
            canonical = json.dumps(
                payload, sort_keys=True, separators=(",", ":"),
                ensure_ascii=True, allow_nan=False,
            ).encode("ascii")
        except (TypeError, ValueError, UnicodeEncodeError) as error:
            raise G64ReviewRegistryError("G64_REVIEW_PERSISTED_EVENT_INVALID") from error
        digest = hashlib.sha3_512(canonical).hexdigest()
        if digest != row.get("payload_sha3_512"):
            raise G64ReviewRegistryError("G64_REVIEW_PERSISTED_EVENT_INVALID")
        output.append(row)
    return tuple(output)
