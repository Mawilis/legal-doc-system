# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS – KENNEL VENDOR IDENTITY REGISTRY                                                                       ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ VERSION:        v1.7.0-REPLAY-FLOOR-PRESENCE-INTEGRITY                                                        ║
║ EPITOME:        Tenant-isolated Mongo persistence for vendor identity with database-enforced revision CAS.      ║
║                 It stores no payable, payment destination, approval, release, or settlement state.              ║
║ BIBLICAL ANCHOR: Psalm 1:3 — "And he shall be like a tree planted by the rivers of water..."                  ║
║ ABSOLUTE PATH:  /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/vendor_registry.py               ║
║ COLLABORATION:  Wilson Khanyezi (Founder/Chief Architect) mandated concurrency-safe AP foundations.             ║
║                 AI Engineering (Codex) implemented persistence after domain-freeze discovery.                   ║
║ CHANGE RECORD:  2026-08-25 — Distinguished absent replay-floor legacy state from explicit null corruption.   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Dict, List, Mapping, Optional, Tuple

from pymongo import ReturnDocument, WriteConcern
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern

from ...kernel.db import get_database
from ..domain.billing import parse_datetime
from ..domain.vendor import VendorDomainError, VendorIdentity

logger = logging.getLogger("WilsyOS.VendorRegistry")
VENDOR_COLLECTION = "vendors"
AUDIT_COLLECTION = "billing_audit_events"
FINANCIAL_WRITE_CONCERN = WriteConcern(w="majority", j=True, wtimeout=10_000)
FINANCIAL_READ_CONCERN = ReadConcern("majority")


class VendorRegistryError(RuntimeError):
    """Base structured persistence failure for the Kennel vendor registry."""


class VendorNotFoundError(VendorRegistryError):
    """Raised without cross-tenant ownership disclosure when a tenant-scoped vendor does not exist."""


class VendorRevisionConflictError(VendorRegistryError):
    """Raised when the database predicate rejects a stale optimistic-concurrency revision."""


class VendorDuplicateError(VendorRegistryError):
    """Raised when immutable tenant plus vendor identity collides at Mongo persistence time."""


class VendorPersistenceError(VendorRegistryError):
    """Raised when Mongo cannot persist a vendor mutation; underlying failures are not converted to success."""


class VendorPersistedRecordInvalidError(VendorRegistryError):
    """Raised when an existing Mongo document violates the immutable vendor persistence contract."""


class VendorAuditPendingError(VendorRegistryError):
    """Signals a committed vendor mutation whose durable audit intent still requires delivery."""


class VendorAuditEventEvidenceConflictError(VendorRegistryError):
    """Raised when an occupied audit event key does not represent the immutable pending audit intent."""


class VendorIdempotencyKeyReuseError(VendorRegistryError):
    """Raised when a command identity is reused for materially different vendor mutation semantics."""


class VendorIdempotencyHorizonExceededError(VendorRegistryError):
    """Raised when retained evidence cannot prove whether an old command identity previously committed."""


class VendorMutationOutcome(StrEnum):
    """Discriminates successful persistence invocations without collapsing structured failures into values."""
    COMMITTED_AUDITED = "COMMITTED_AUDITED"
    COMMITTED_AUDIT_PENDING = "COMMITTED_AUDIT_PENDING"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"


@dataclass(frozen=True)
class VendorMutationResult:
    """Machine-readable success truth for a Vendor mutation or persisted command replay."""
    outcome: VendorMutationOutcome
    vendor: VendorIdentity
    committed_revision: int
    current_revision: int
    idempotency_key: Optional[str]
    audit_event_key: Optional[str]

    @property
    def revision(self) -> int:
        """Preserves read-only compatibility for callers that previously consumed `VendorIdentity.revision`."""
        return self.vendor.revision


def _normalized_legal_name(value: str) -> str:
    """Returns a whitespace-folded, case-normalized soft-duplicate signal; it is intentionally non-unique."""
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _command_receipt(tenant_id: str, vendor_id: str, expected_revision: int, idempotency_key: str, changes: Mapping[str, Any]) -> Dict[str, Any]:
    """Builds a bounded, non-sensitive receipt fingerprint for one caller-owned update command."""
    key = idempotency_key.strip()
    if not key or len(key) > 128:
        raise VendorDomainError("idempotency_key must be a non-empty string of at most 128 characters")
    payload = {"tenant_id": tenant_id, "vendor_id": vendor_id, "expected_revision": expected_revision, "operation": "VENDOR_REVISED", "changes": dict(changes)}
    fingerprint = hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
    return {"idempotency_key": key, "fingerprint": fingerprint, "expected_revision": expected_revision}


def _hydrate_command_receipts(document: Mapping[str, Any], current_revision: int) -> List[Dict[str, Any]]:
    """Validates the persisted, newest-first command ledger before replay logic can consume it."""
    raw = document.get("command_receipts", [])
    if not isinstance(raw, list):
        raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
    receipts: List[Dict[str, Any]] = []
    seen_keys = set()
    prior_committed = current_revision + 1
    for item in raw:
        if not isinstance(item, dict):
            raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
        key, fingerprint = item.get("idempotency_key"), item.get("fingerprint")
        expected, committed = item.get("expected_revision"), item.get("committed_revision")
        if (not isinstance(key, str) or not key.strip() or len(key) > 128 or not isinstance(fingerprint, str)
                or not re.fullmatch(r"[0-9a-f]{128}", fingerprint) or not isinstance(expected, int)
                or isinstance(expected, bool) or expected < 1 or not isinstance(committed, int)
                or isinstance(committed, bool) or committed != expected + 1 or committed > current_revision
                or committed >= prior_committed or key in seen_keys):
            raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
        receipts.append(dict(item)); seen_keys.add(key); prior_committed = committed
    floor_present = "replay_floor_revision" in document
    floor = document.get("replay_floor_revision")
    if not floor_present:
        if receipts:
            raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
        return receipts
    if (floor is None or not isinstance(floor, int) or isinstance(floor, bool) or floor < 1
            or floor > current_revision or not receipts
            or floor != min(row["expected_revision"] for row in receipts)):
        raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
    return receipts


def _hydrate_persisted_vendor(document: Mapping[str, Any]) -> Tuple[VendorIdentity, List[Dict[str, Any]]]:
    """Hydrates a Vendor only after its identity and durable idempotency state satisfy one canonical contract."""
    vendor = _vendor_from_document(document)
    return vendor, _hydrate_command_receipts(document, vendor.revision)


def _collection_or_raise(collection: Optional[Collection] = None) -> Collection:
    """Returns a vendor collection bound to explicit financial write and read consistency guarantees."""
    target = collection
    if target is None:
        db = get_database()
        if db is None:
            raise VendorPersistenceError("KENNEL_VENDOR_PERSISTENCE_UNAVAILABLE")
        target = db[VENDOR_COLLECTION]
    return target.with_options(
        write_concern=FINANCIAL_WRITE_CONCERN,
        read_concern=FINANCIAL_READ_CONCERN,
    )


def _audit_collection_or_none(vendor_collection: Optional[Collection] = None) -> Optional[Collection]:
    """Returns the colocated audit collection for an injected test collection or the shared Kennel database."""
    if vendor_collection is not None:
        return vendor_collection.database[AUDIT_COLLECTION].with_options(
            write_concern=FINANCIAL_WRITE_CONCERN,
            read_concern=FINANCIAL_READ_CONCERN,
        )
    db = get_database()
    return (
        db[AUDIT_COLLECTION].with_options(
            write_concern=FINANCIAL_WRITE_CONCERN,
            read_concern=FINANCIAL_READ_CONCERN,
        )
        if db is not None else None
    )


def _vendor_from_document(document: Mapping[str, Any]) -> VendorIdentity:
    """Hydrates the canonical vendor domain model from its tenant-scoped Mongo document."""
    def required_text(field: str) -> str:
        value = document.get(field)
        if not isinstance(value, str) or not value.strip():
            raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
        return value.strip()

    def optional_text(field: str) -> Optional[str]:
        value = document.get(field)
        if value is None:
            return None
        if not isinstance(value, str):
            raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
        return value

    tenant_id = required_text("tenant_id")
    vendor_id = required_text("vendor_id")
    legal_name = required_text("legal_name")
    revision = document.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
    metadata = document.get("metadata", {})
    if not isinstance(metadata, dict):
        raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
    created_at = parse_datetime(document.get("created_at"))
    updated_at = parse_datetime(document.get("updated_at"))
    if created_at is None or updated_at is None:
        raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
    proof_hash = document.get("proof_hash")
    if not isinstance(proof_hash, str):
        raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
    return VendorIdentity(
        tenant_id=tenant_id, vendor_id=vendor_id, legal_name=legal_name,
        trading_name=optional_text("trading_name"), tax_identifier=optional_text("tax_identifier"),
        registration_identifier=optional_text("registration_identifier"), email=optional_text("email"),
        phone=optional_text("phone"), country_code=optional_text("country_code"), metadata=metadata,
        revision=revision, created_at=created_at, updated_at=updated_at, proof_hash=proof_hash,
    )


def _document_from_vendor(vendor: VendorIdentity) -> Dict[str, Any]:
    """Serializes one vendor to the persistence shape, excluding all payment-destination concepts by design."""
    return {
        "tenant_id": vendor.tenant_id, "tenantId": vendor.tenant_id,
        "vendor_id": vendor.vendor_id, "vendorId": vendor.vendor_id,
        "legal_name": vendor.legal_name, "legal_name_normalized": _normalized_legal_name(vendor.legal_name),
        "trading_name": vendor.trading_name, "tax_identifier": vendor.tax_identifier,
        "registration_identifier": vendor.registration_identifier, "email": vendor.email,
        "phone": vendor.phone, "country_code": vendor.country_code, "metadata": dict(vendor.metadata),
        "revision": vendor.revision, "proof_hash": vendor.proof_hash, "proofHash": vendor.proof_hash,
        "created_at": vendor.created_at, "updated_at": vendor.updated_at,
    }


def _audit_intent(event_type: str, vendor: VendorIdentity) -> Dict[str, Any]:
    """Builds a minimal deterministic audit-delivery intent; raw vendor identity values never enter the outbox."""
    return {
        "event_key": f"vendor:{vendor.tenant_id}:{vendor.vendor_id}:{vendor.revision}:{event_type}",
        "event_type": event_type,
        "proof_hash": vendor.proof_hash,
        "revision": vendor.revision,
        "schema_version": "WILSY-VENDOR-AUDIT-INTENT/V1",
        "status": "PENDING",
        "created_at": datetime.now().astimezone(),
    }


def _audit_event_document(intent: Mapping[str, Any], tenant_id: str, vendor_id: str) -> Dict[str, Any]:
    """Builds the one canonical immutable audit event shape from the durable embedded intent."""
    return {
        "event_key": intent["event_key"], "tenant_id": tenant_id, "event_type": intent["event_type"],
        "revision": intent["revision"], "proof_hash": intent["proof_hash"],
        "metadata": {"vendor_id": vendor_id, "revision": intent["revision"], "schema": "WILSY-VENDOR-IDENTITY/V1"},
        "created_at": intent["created_at"],
    }


def _assert_audit_event_matches_intent(event: Mapping[str, Any], intent: Mapping[str, Any], tenant_id: str, vendor_id: str, revision: int) -> None:
    """Fails closed unless an existing event is the exact immutable evidence represented by an audit intent."""
    metadata = event.get("metadata")
    expected = _audit_event_document(intent, tenant_id, vendor_id)
    if (
        not isinstance(metadata, Mapping)
        or not isinstance(event.get("event_key"), str) or event["event_key"] != expected["event_key"]
        or not isinstance(event.get("proof_hash"), str) or event["proof_hash"] != expected["proof_hash"]
        or not isinstance(event.get("revision"), int) or isinstance(event["revision"], bool) or event["revision"] != revision
        or not isinstance(event.get("tenant_id"), str) or event["tenant_id"] != tenant_id
        or not isinstance(event.get("event_type"), str) or event["event_type"] != expected["event_type"]
        or not isinstance(metadata.get("vendor_id"), str) or metadata["vendor_id"] != vendor_id
        or not isinstance(metadata.get("revision"), int) or isinstance(metadata["revision"], bool) or metadata["revision"] != revision
        or not isinstance(metadata.get("schema"), str) or metadata["schema"] != expected["metadata"]["schema"]
    ):
        raise VendorAuditEventEvidenceConflictError("AUDIT_EVENT_EVIDENCE_CONFLICT")


class VendorRegistry:
    """Persists tenant-local vendor identities using database predicates for isolation and revision correctness."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Creates only query-backed indexes: tenant/vendor retrieval, listings, and non-unique duplicate signals."""
        target = _collection_or_raise(collection)
        target.create_index([("tenant_id", 1), ("vendor_id", 1)], unique=True, name="tenant_vendor_identity_unique")
        target.create_index([("tenant_id", 1), ("created_at", -1)], name="tenant_vendor_listing")
        target.create_index([("tenant_id", 1), ("legal_name_normalized", 1)], name="tenant_vendor_duplicate_signal")
        target.create_index([("tenant_id", 1), ("audit_intent.status", 1)], name="tenant_vendor_pending_audit")
        audit = _audit_collection_or_none(target)
        if audit is not None:
            audit.create_index([("event_key", 1)], unique=True, name="vendor_audit_event_key_unique", partialFilterExpression={"event_key": {"$type": "string"}})

    @staticmethod
    def create(vendor: VendorIdentity, collection: Optional[Collection] = None) -> VendorIdentity:
        """Atomically inserts a generated immutable vendor identity; duplicate business names remain non-blocking signals."""
        if not isinstance(vendor, VendorIdentity):
            raise VendorDomainError("vendor must be a VendorIdentity")
        target = _collection_or_raise(collection)
        try:
            document = _document_from_vendor(vendor)
            document["audit_intent"] = _audit_intent("VENDOR_CREATED", vendor)
            target.insert_one(document)
        except DuplicateKeyError as error:
            raise VendorDuplicateError("VENDOR_IDENTITY_ALREADY_EXISTS") from error
        except PyMongoError as error:
            logger.error("[VENDOR_REGISTRY] create persistence failure vendor=%s tenant=%s", vendor.vendor_id, vendor.tenant_id)
            raise VendorPersistenceError("VENDOR_CREATE_FAILED") from error
        VendorRegistry._deliver_audit_intent(vendor.tenant_id, vendor.vendor_id, vendor.revision, target)
        return vendor

    @staticmethod
    def get(tenant_id: str, vendor_id: str, collection: Optional[Collection] = None) -> VendorIdentity:
        """Gets a vendor only through its authoritative tenant plus immutable vendor identity predicate."""
        target = _collection_or_raise(collection)
        document = target.find_one({"tenant_id": str(tenant_id).strip(), "vendor_id": str(vendor_id).strip()})
        if not document:
            raise VendorNotFoundError("VENDOR_NOT_FOUND")
        vendor, _ = _hydrate_persisted_vendor(document)
        return vendor

    @staticmethod
    def list(tenant_id: str, limit: int = 100, collection: Optional[Collection] = None) -> List[VendorIdentity]:
        """Lists only the requesting tenant's vendor identities in deterministic newest-first order."""
        bounded_limit = min(max(int(limit), 1), 250)
        target = _collection_or_raise(collection)
        return [_hydrate_persisted_vendor(row)[0] for row in target.find({"tenant_id": str(tenant_id).strip()}).sort("created_at", -1).limit(bounded_limit)]

    @staticmethod
    def update(tenant_id: str, vendor_id: str, expected_revision: int, changes: Mapping[str, Any], collection: Optional[Collection] = None, idempotency_key: Optional[str] = None) -> VendorMutationResult:
        """Applies an allowlisted vendor revision only when tenant, identity, and expected revision match in Mongo.

        A preparatory read feeds domain validation, but correctness comes from the conditional update predicate;
        a concurrent writer makes this operation return a deterministic revision conflict instead of overwriting.
        """
        target = _collection_or_raise(collection)
        current_document = target.find_one({"tenant_id": str(tenant_id).strip(), "vendor_id": str(vendor_id).strip()})
        if not current_document:
            raise VendorNotFoundError("VENDOR_NOT_FOUND")
        current, retained_receipts = _hydrate_persisted_vendor(current_document)
        receipt = _command_receipt(current.tenant_id, current.vendor_id, int(expected_revision), idempotency_key, changes) if idempotency_key is not None else None
        for prior in retained_receipts:
            if receipt is not None and prior.get("idempotency_key") == receipt["idempotency_key"]:
                if prior.get("fingerprint") != receipt["fingerprint"]:
                    raise VendorIdempotencyKeyReuseError("IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND")
                return VendorMutationResult(VendorMutationOutcome.IDEMPOTENT_REPLAY, current, int(prior.get("committed_revision") or current.revision), current.revision, receipt["idempotency_key"], None)
        replay_floor = current_document.get("replay_floor_revision")
        if receipt is not None and replay_floor is not None:
            if not isinstance(replay_floor, int) or isinstance(replay_floor, bool) or replay_floor < 1:
                raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
            if receipt["expected_revision"] < replay_floor:
                raise VendorIdempotencyHorizonExceededError("IDEMPOTENCY_HORIZON_EXCEEDED")
        if int(expected_revision) != current.revision:
            raise VendorRevisionConflictError("VENDOR_REVISION_CONFLICT")
        candidate = current.revise(tenant_id, expected_revision, **dict(changes))
        candidate_document = _document_from_vendor(candidate)
        if receipt:
            receipt["committed_revision"] = candidate.revision
            receipts = ([receipt] + retained_receipts)[:20]
            candidate_document["command_receipts"] = receipts
            candidate_document["replay_floor_revision"] = min(item["expected_revision"] for item in receipts)
        candidate_document["audit_intent"] = _audit_intent("VENDOR_REVISED", candidate)
        predicate = {"tenant_id": current.tenant_id, "vendor_id": current.vendor_id, "revision": int(expected_revision)}
        try:
            stored = target.find_one_and_update(
                predicate,
                {"$set": candidate_document},
                return_document=ReturnDocument.AFTER,
            )
        except PyMongoError as error:
            logger.error("[VENDOR_REGISTRY] update persistence failure vendor=%s tenant=%s", current.vendor_id, current.tenant_id)
            raise VendorPersistenceError("VENDOR_UPDATE_FAILED") from error
        if not stored:
            if receipt is not None:
                replay_document = target.find_one({"tenant_id": current.tenant_id, "vendor_id": current.vendor_id})
                if replay_document is not None:
                    replayed, replay_receipts = _hydrate_persisted_vendor(replay_document)
                    for prior in replay_receipts:
                        if prior.get("idempotency_key") == receipt["idempotency_key"] and prior.get("fingerprint") == receipt["fingerprint"]:
                            return VendorMutationResult(VendorMutationOutcome.IDEMPOTENT_REPLAY, replayed, int(prior.get("committed_revision") or replayed.revision), replayed.revision, receipt["idempotency_key"], None)
            # Scope-safe: the predicate contains tenant; no other tenant ownership is disclosed.
            raise VendorRevisionConflictError("VENDOR_REVISION_CONFLICT")
        persisted = _vendor_from_document(stored)
        audit_key = ((stored.get("audit_intent") or {}).get("event_key"))
        try:
            VendorRegistry._deliver_audit_intent(persisted.tenant_id, persisted.vendor_id, persisted.revision, target)
        except VendorAuditPendingError:
            return VendorMutationResult(VendorMutationOutcome.COMMITTED_AUDIT_PENDING, persisted, persisted.revision, persisted.revision, idempotency_key, audit_key)
        return VendorMutationResult(VendorMutationOutcome.COMMITTED_AUDITED, persisted, persisted.revision, persisted.revision, idempotency_key, audit_key)

    @staticmethod
    def _deliver_audit_intent(tenant_id: str, vendor_id: str, revision: int, collection: Optional[Collection] = None) -> None:
        """Idempotently publishes one durable vendor audit intent and acknowledges it only after anchor persistence."""
        target = _collection_or_raise(collection)
        document = target.find_one({"tenant_id": tenant_id, "vendor_id": vendor_id, "revision": revision})
        intent = (document or {}).get("audit_intent") or {}
        if not intent or intent.get("status") == "DELIVERED":
            return
        audit = _audit_collection_or_none(target)
        if audit is None:
            raise VendorAuditPendingError("VENDOR_COMMITTED_AUDIT_PENDING")
        try:
            canonical_revision = intent.get("revision")
            if not isinstance(canonical_revision, int) or isinstance(canonical_revision, bool) or canonical_revision != revision:
                raise VendorPersistedRecordInvalidError("VENDOR_PERSISTED_RECORD_INVALID")
            event = audit.find_one({"event_key": intent.get("event_key")})
            if event is None:
                try:
                    audit.insert_one(_audit_event_document(intent, tenant_id, vendor_id))
                except DuplicateKeyError:
                    event = audit.find_one({"event_key": intent.get("event_key")})
                    if event is None:
                        raise VendorAuditPendingError("VENDOR_COMMITTED_AUDIT_PENDING")
                else:
                    event = audit.find_one({"event_key": intent.get("event_key")})
                    if event is None:
                        raise VendorAuditPendingError("VENDOR_COMMITTED_AUDIT_PENDING")
            _assert_audit_event_matches_intent(event, intent, tenant_id, vendor_id, canonical_revision)
            target.update_one({"tenant_id": tenant_id, "vendor_id": vendor_id, "revision": revision, "audit_intent.event_key": intent["event_key"]}, {"$set": {"audit_intent.status": "DELIVERED", "audit_intent.delivered_at": datetime.now().astimezone()}})
        except PyMongoError as error:
            logger.error("[VENDOR_REGISTRY] audit delivery pending vendor=%s tenant=%s", vendor_id, tenant_id)
            raise VendorAuditPendingError("VENDOR_COMMITTED_AUDIT_PENDING") from error

    @staticmethod
    def recover_pending_audits(tenant_id: str, limit: int = 100, collection: Optional[Collection] = None) -> int:
        """Replays only one tenant's durable pending audit intents; callers may run this from an existing reconciliation job."""
        target = _collection_or_raise(collection)
        rows = target.find({"tenant_id": str(tenant_id).strip(), "audit_intent.status": "PENDING"}).sort("updated_at", 1).limit(min(max(int(limit), 1), 250))
        delivered = 0
        for row in rows:
            VendorRegistry._deliver_audit_intent(row["tenant_id"], row["vendor_id"], int(row["revision"]), target)
            delivered += 1
        return delivered
