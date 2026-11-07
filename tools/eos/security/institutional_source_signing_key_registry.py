"""TITLE: WILSY EOS Institutional Source Signing-Key Lifecycle Registry
VERSION: v1.0.0
AUTHORITY: WILSY EOS Security Engineering; persistence authority only
EPITOME: Append-only, source-bound Ed25519 public-key enrollment, revocation and rotation evidence.
ABSOLUTE CANONICAL PATH: tools/eos/security/institutional_source_signing_key_registry.py
COLLABORATION / OWNERSHIP: Consumed by institutional signer source-response authentication; MongoDB owns durable records.
CERTIFICATION / UPDATE DATE: 2026-11-08
CHANGELOG:
- v1.0.0: Introduce immutable key enrollment, append-only revocation and bounded rotation events.
COMPLIANCE: Caller-owned MongoDB transaction; deterministic fingerprints; unique source/key and public-key identities.
SECURITY / PRIVACY POSTURE: Public keys only; no private material, secrets, provider credentials or fabricated institutional trust anchors.
TENANT BOUNDARY: Source trust is source-system scoped, not tenant-issued authority.
AUTHORITY BOUNDARY: Registry records approved governance decisions; it does not approve them, authenticate callers, or issue verifier success.
FINANCIAL AUTHORITY BOUNDARY: No financial execution authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any, Final, Mapping

from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.client_session import ClientSession

KEY_COLLECTION: Final[str] = "eos_institutional_source_signing_keys"
EVENT_COLLECTION: Final[str] = "eos_institutional_source_signing_key_events"
SCHEMA: Final[str] = "wilsy.eos.institutional_source_signing_key.v1"
EVENT_SCHEMA: Final[str] = "wilsy.eos.institutional_source_signing_key_event.v1"
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}\Z")
_FINGERPRINT = re.compile(r"[0-9a-f]{64}\Z")


class SourceSigningKeyRegistryError(RuntimeError):
    """Stable fail-closed registry error; no provider or database details escape."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class SourceSigningKeyRegistryConflict(SourceSigningKeyRegistryError):
    """Conflict caused by duplicate identity, replay, or invalid lifecycle transition."""


def _identifier(field: str, value: object) -> str:
    if type(value) is not str or _IDENTIFIER.fullmatch(value) is None:
        raise SourceSigningKeyRegistryError(f"SOURCE_SIGNING_KEY_{field.upper()}_INVALID")
    return value


def _instant(field: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise SourceSigningKeyRegistryError(f"SOURCE_SIGNING_KEY_{field.upper()}_INVALID")
    return value.astimezone(timezone.utc)


def _canonical(value: Mapping[str, Any]) -> bytes:
    def encode(item: object) -> object:
        if isinstance(item, datetime):
            return item.astimezone(timezone.utc).isoformat()
        if isinstance(item, bytes):
            return item.hex()
        raise TypeError("unsupported canonical value")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=encode).encode("utf-8")


class InstitutionalSourceSigningKeyLifecycleRegistry:
    """Persist immutable source-key records and append-only lifecycle events.

    Every mutation requires a caller-owned MongoDB session. The caller owns
    transaction start, commit, abort, retry and authorization. This registry
    never stores private keys and never creates a trust decision from enrollment
    alone. Resolution fails closed on missing, not-yet-valid, expired, revoked,
    or rotation-superseded keys.
    """

    def __init__(self, keys: Collection, events: Collection) -> None:
        self._keys = keys
        self._events = events

    @staticmethod
    def ensure_indexes(keys: Collection, events: Collection) -> None:
        """Create deterministic unique indexes; caller controls deployment."""
        try:
            keys.create_index(
                [("source_system_id", 1), ("key_id", 1)],
                unique=True, name="uq_source_signing_key_identity",
            )
            keys.create_index(
                [("public_key_fingerprint_sha256", 1)],
                unique=True, name="uq_source_signing_key_fingerprint",
            )
            keys.create_index(
                [("source_system_id", 1), ("rotation.supersedes_key_id", 1)],
                unique=True,
                partialFilterExpression={"rotation.supersedes_key_id": {"$exists": True}},
                name="uq_source_signing_key_rotation_predecessor",
            )
            keys.create_index(
                [("source_system_id", 1), ("rotation.rotation_id", 1)],
                unique=True,
                partialFilterExpression={"rotation.rotation_id": {"$exists": True}},
                name="uq_source_signing_key_rotation_id",
            )
            events.create_index(
                [("source_system_id", 1), ("idempotency_key", 1)],
                unique=True, name="uq_source_signing_key_event_idempotency",
            )
            events.create_index(
                [("source_system_id", 1), ("key_id", 1), ("event_sequence", 1)],
                unique=True, name="uq_source_signing_key_event_sequence",
            )
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_INDEX_UNAVAILABLE") from error

    def enroll(
        self, *, source_system_id: str, key_id: str, public_key_bytes: bytes,
        valid_from: datetime, valid_until: datetime,
        governance_decision_reference: str, approved_by_principal_id: str,
        enrolled_at: datetime, idempotency_key: str, session: ClientSession,
        rotation_id: str | None = None, supersedes_key_id: str | None = None,
        overlap_until: datetime | None = None,
    ) -> dict[str, Any]:
        """Insert an immutable public-key record and its enrollment event.

        A replacement key must identify its predecessor and an explicit overlap
        end no later than the predecessor's expiry. Approval evidence and actor
        are required but are not independently validated here.
        """
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        decision = _identifier("governance_decision_reference", governance_decision_reference)
        approver = _identifier("approved_by_principal_id", approved_by_principal_id)
        idem = _identifier("idempotency_key", idempotency_key)
        start, end, occurred = (
            _instant("valid_from", valid_from),
            _instant("valid_until", valid_until),
            _instant("enrolled_at", enrolled_at),
        )
        if type(public_key_bytes) is not bytes or len(public_key_bytes) != 32:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_PUBLIC_KEY_INVALID")
        if end <= start:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_VALIDITY_INTERVAL_INVALID")
        fingerprint = sha256(public_key_bytes).hexdigest()
        if (supersedes_key_id is None) != (rotation_id is None) or (supersedes_key_id is None) != (overlap_until is None):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_ROTATION_FIELDS_INCOMPLETE")
        rotation = None
        if supersedes_key_id is not None:
            predecessor_id = _identifier("supersedes_key_id", supersedes_key_id)
            rotation_name = _identifier("rotation_id", rotation_id)
            overlap = _instant("overlap_until", overlap_until)
            predecessor = self._keys.find_one(
                {"source_system_id": source, "key_id": predecessor_id}, session=session
            )
            if self._keys.find_one(
                {"source_system_id": source, "rotation.supersedes_key_id": predecessor_id},
                session=session,
            ) is not None:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ROTATION_ALREADY_REPLACED")
            if predecessor is None:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ROTATION_PREDECESSOR_MISSING")
            if not (start < overlap <= predecessor["valid_until"] and start < end):
                raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_ROTATION_OVERLAP_INVALID")
            rotation = {
                "rotation_id": rotation_name,
                "supersedes_key_id": predecessor_id,
                "overlap_until": overlap,
            }
        record = {
            "schema": SCHEMA,
            "source_system_id": source,
            "key_id": key,
            "public_key_bytes": public_key_bytes,
            "public_key_fingerprint_sha256": fingerprint,
            "valid_from": start,
            "valid_until": end,
            "governance_decision_reference": decision,
            "approved_by_principal_id": approver,
            "enrolled_at": occurred,
            "rotation": rotation,
        }
        event_payload = {
            "schema": EVENT_SCHEMA, "event_type": "ENROLLED",
            "source_system_id": source, "key_id": key,
            "idempotency_key": idem, "occurred_at": occurred,
            "actor_principal_id": approver,
            "governance_decision_reference": decision,
            "record_fingerprint_sha256": sha256(_canonical(record)).hexdigest(),
        }
        prior = self._events.find_one(
            {"source_system_id": source, "idempotency_key": idem}, session=session
        )
        if prior is not None:
            if prior.get("record_fingerprint_sha256") != event_payload["record_fingerprint_sha256"]:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DIVERGENT_REPLAY")
            existing = self._keys.find_one(
                {"source_system_id": source, "key_id": key}, session=session
            )
            if existing is None:
                raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_REPLAY_RECORD_MISSING")
            return existing
        try:
            self._keys.insert_one(record, session=session)
            event_payload["event_sequence"] = 1
            self._events.insert_one(event_payload, session=session)
        except DuplicateKeyError as error:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_IDENTITY_OR_FINGERPRINT_EXISTS") from error
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_ENROLLMENT_PERSISTENCE_FAILED") from error
        return record

    def revoke(
        self, *, source_system_id: str, key_id: str, revoked_at: datetime,
        reason_reference: str, revoked_by_principal_id: str,
        governance_decision_reference: str, idempotency_key: str,
        session: ClientSession,
    ) -> dict[str, Any]:
        """Append an immediate, revision-specific revocation event."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        reason = _identifier("reason_reference", reason_reference)
        actor = _identifier("revoked_by_principal_id", revoked_by_principal_id)
        decision = _identifier("governance_decision_reference", governance_decision_reference)
        idem = _identifier("idempotency_key", idempotency_key)
        occurred = _instant("revoked_at", revoked_at)
        if occurred > datetime.now(timezone.utc):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_REVOCATION_CANNOT_BE_FUTURE_DATED")
        record = self._keys.find_one({"source_system_id": source, "key_id": key}, session=session)
        if record is None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
        event = {
            "schema": EVENT_SCHEMA, "event_type": "REVOKED",
            "source_system_id": source, "key_id": key,
            "idempotency_key": idem, "occurred_at": occurred,
            "actor_principal_id": actor, "reason_reference": reason,
            "governance_decision_reference": decision,
            "record_fingerprint_sha256": record["public_key_fingerprint_sha256"],
            "event_sequence": 2,
        }
        prior = self._events.find_one(
            {"source_system_id": source, "idempotency_key": idem}, session=session
        )
        if prior is not None:
            if prior != event:
                comparable = {k: v for k, v in prior.items() if k != "_id"}
                if comparable != event:
                    raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DIVERGENT_REPLAY")
            return prior
        if self._events.find_one(
            {"source_system_id": source, "key_id": key, "event_type": "REVOKED"}, session=session
        ):
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ALREADY_REVOKED")
        try:
            self._events.insert_one(event, session=session)
        except DuplicateKeyError as error:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_REVOCATION_CONFLICT") from error
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_REVOCATION_PERSISTENCE_FAILED") from error
        return event

    def resolve(
        self, *, source_system_id: str, key_id: str, evaluated_at: datetime,
        session: ClientSession,
    ) -> dict[str, Any]:
        """Return a usable public key only when lifecycle evidence permits it."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        at = _instant("evaluated_at", evaluated_at)
        try:
            record = self._keys.find_one(
                {"source_system_id": source, "key_id": key}, session=session
            )
            if record is None:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_UNTRUSTED")
            if not (record["valid_from"] <= at < record["valid_until"]):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_OUTSIDE_VALIDITY")
            revocation = self._events.find_one(
                {"source_system_id": source, "key_id": key, "event_type": "REVOKED",
                 "occurred_at": {"$lte": at}},
                sort=[("occurred_at", 1)], session=session,
            )
            if revocation is not None:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_REVOKED")
            successor = self._keys.find_one(
                {"source_system_id": source, "rotation.supersedes_key_id": key},
                session=session,
            )
            if successor is not None:
                overlap = successor.get("rotation", {}).get("overlap_until")
                if overlap is None or at >= overlap:
                    raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ROTATION_OVERLAP_ENDED")
            return record
        except SourceSigningKeyRegistryError:
            raise
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_RESOLUTION_UNAVAILABLE") from error


__all__ = [
    "KEY_COLLECTION", "EVENT_COLLECTION", "SourceSigningKeyRegistryError",
    "SourceSigningKeyRegistryConflict", "InstitutionalSourceSigningKeyLifecycleRegistry",
]

# ARTIFACT: WILSY OS Institutional Source Signing-Key Lifecycle Registry
# VERSION: v1.0.0
# AUTHORITY BOUNDARY: Durable public-key lifecycle evidence only; no caller authorization or verifier-result issuance.
# TENANT POSTURE: Source-system scoped; no tenant-issued trust.
# FAIL-CLOSED POSTURE: Missing, invalid, expired, revoked, or unavailable trust is denied.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
