"""Durable append-only POS commercial evidence registry.

Persists M9 tender intents, cash tender evidence, return intents and refund
intents. Sale persistence remains owned by POSSaleRegistry. Every operation
uses a caller-owned active transaction and binds tenant, location and sale.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha3_512
import json
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.pos_commercial import (
    POSCashTender, POSSale, POSRefundIntent, POSReturnIntent, POSTenderIntent,
)

COLLECTION_NAME: Final = "pos_commercial_evidence"
EVIDENCE_TYPES: Final = {
    POSTenderIntent: "TENDER_INTENT",
    POSCashTender: "CASH_TENDER",
    POSReturnIntent: "RETURN_INTENT",
    POSRefundIntent: "REFUND_INTENT",
}


class POSCommercialEvidenceRegistryError(RuntimeError):
    pass


class POSCommercialEvidenceConflict(POSCommercialEvidenceRegistryError):
    pass


class POSCommercialEvidenceNotFound(POSCommercialEvidenceRegistryError):
    pass


def _tx(session: Any) -> Any:
    if session is None or not callable(getattr(session, "with_transaction", None)) or getattr(session, "has_ended", True):
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_LIVE_CALLER_SESSION_REQUIRED")
    return session


def _canonical_digest(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return sha3_512(encoded).hexdigest()


def ensure_indexes(collection: Any) -> None:
    try:
        collection.create_index(
            [("tenant_id", ASCENDING), ("location_id", ASCENDING), ("evidence_type", ASCENDING), ("evidence_id", ASCENDING)],
            unique=True, name="pos_commercial_evidence_identity_unique",
        )
        collection.create_index(
            [("tenant_id", ASCENDING), ("location_id", ASCENDING), ("evidence_type", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True, name="pos_commercial_evidence_idempotency_unique",
        )
        collection.create_index(
            [("tenant_id", ASCENDING), ("location_id", ASCENDING), ("sale_id", ASCENDING), ("occurred_at", ASCENDING)],
            name="pos_commercial_evidence_sale_history",
        )
    except (AttributeError, PyMongoError) as error:
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_INDEX_UNAVAILABLE") from error


def record_evidence(*, sale: POSSale, evidence: Any, evidence_id: str, idempotency_key: str,
                    recorded_by_principal_id: str, collection: Any, session: Any) -> dict:
    tx = _tx(session)
    if type(sale) is not POSSale or type(evidence) not in EVIDENCE_TYPES:
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_CANONICAL_INPUT_REQUIRED")
    if not isinstance(evidence_id, str) or not evidence_id or evidence_id != evidence_id.strip():
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_ID_INVALID")
    if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip():
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_IDEMPOTENCY_KEY_INVALID")
    if not isinstance(recorded_by_principal_id, str) or not recorded_by_principal_id or recorded_by_principal_id != recorded_by_principal_id.strip():
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_ACTOR_INVALID")
    evidence_sale_id = getattr(evidence, "sale_id", getattr(evidence, "original_sale_id", None))
    if (
        evidence.tenant_id != sale.tenant_id
        or evidence.location_id != sale.location_id
        or evidence_sale_id != sale.sale_id
    ):
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_SALE_PROVENANCE_MISMATCH")
    if isinstance(evidence, (POSTenderIntent, POSCashTender, POSRefundIntent)) and evidence.currency != sale.currency:
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_CURRENCY_MISMATCH")
    payload = evidence.to_dict()
    evidence_type = EVIDENCE_TYPES[type(evidence)]
    occurred_at = getattr(evidence, "recorded_at", None) or datetime.now(timezone.utc).isoformat()
    base_record = {
        "schema": "WILSY-POS-COMMERCIAL-EVIDENCE/V1",
        "version": "v1.0.0-POS-COMMERCIAL-EVIDENCE",
        "tenant_id": sale.tenant_id,
        "location_id": sale.location_id,
        "sale_id": sale.sale_id,
        "sale_fingerprint": sale.fingerprint,
        "evidence_type": evidence_type,
        "evidence_id": evidence_id,
        "idempotency_key": idempotency_key,
        "recorded_by_principal_id": recorded_by_principal_id,
        "occurred_at": occurred_at,
        "evidence": payload,
    }
    identity = {
        "tenant_id": sale.tenant_id, "location_id": sale.location_id,
        "evidence_type": evidence_type, "evidence_id": evidence_id,
    }
    try:
        existing = collection.find_one(identity, session=tx)
        if existing is not None:
            existing.pop("_id", None)
            fingerprint = existing.pop("fingerprint", None)
            recorded_at = existing.pop("recorded_at", None)
            expected = {**base_record, "recorded_at": recorded_at}
            if existing != base_record or fingerprint != _canonical_digest(expected):
                raise POSCommercialEvidenceConflict("POS_EVIDENCE_DIVERGENT_REPLAY")
            return {**expected, "fingerprint": fingerprint}
        record = {**base_record, "recorded_at": datetime.now(timezone.utc).isoformat()}
        record["fingerprint"] = _canonical_digest(record)
        collection.insert_one(record, session=tx)
    except DuplicateKeyError as error:
        raise POSCommercialEvidenceConflict("POS_EVIDENCE_REPLAY_RACE_RETRY_TRANSACTION") from error
    except PyMongoError as error:
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_PERSISTENCE_UNAVAILABLE") from error
    persisted = collection.find_one(identity, session=tx)
    if persisted is None:
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_CREATE_READBACK_MISSING")
    persisted.pop("_id", None)
    if persisted != record:
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_CREATE_READBACK_MISMATCH")
    return persisted


def get_by_idempotency(*, tenant_id: str, location_id: str, evidence_type: str,
                       idempotency_key: str, collection: Any, session: Any) -> dict | None:
    """Resolve one exact immutable command replay before capacity mutation."""
    tx = _tx(session)
    row = collection.find_one({
        "tenant_id": tenant_id, "location_id": location_id,
        "evidence_type": evidence_type, "idempotency_key": idempotency_key,
    }, session=tx)
    if row is None:
        return None
    row.pop("_id", None)
    fingerprint = row.pop("fingerprint", None)
    if fingerprint != _canonical_digest(row):
        raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_PERSISTED_FINGERPRINT_INVALID")
    row["fingerprint"] = fingerprint
    return row


def list_sale_evidence(*, tenant_id: str, location_id: str, sale_id: str, collection: Any, session: Any) -> tuple[dict, ...]:
    tx = _tx(session)
    rows = tuple(collection.find(
        {"tenant_id": tenant_id, "location_id": location_id, "sale_id": sale_id},
        session=tx,
    ).sort([("evidence_type", ASCENDING), ("evidence_id", ASCENDING)]))
    result = []
    for row in rows:
        row.pop("_id", None)
        fingerprint = row.pop("fingerprint", None)
        if fingerprint != _canonical_digest(row):
            raise POSCommercialEvidenceRegistryError("POS_EVIDENCE_PERSISTED_FINGERPRINT_INVALID")
        row["fingerprint"] = fingerprint
        result.append(row)
    return tuple(result)


class POSCommercialEvidenceRegistry:
    ensure_indexes = staticmethod(ensure_indexes)
    record_evidence = staticmethod(record_evidence)
    list_sale_evidence = staticmethod(list_sale_evidence)
    get_by_idempotency = staticmethod(get_by_idempotency)


__all__ = [
    "COLLECTION_NAME", "POSCommercialEvidenceConflict",
    "POSCommercialEvidenceNotFound", "POSCommercialEvidenceRegistry",
    "POSCommercialEvidenceRegistryError", "ensure_indexes",
    "get_by_idempotency", "list_sale_evidence", "record_evidence",
]
