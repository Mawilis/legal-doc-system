"""TITLE: WILSY EOS Institutional Source Signing-Key Lifecycle Registry
VERSION: v1.4.0
AUTHORITY: WILSY EOS Security Engineering; persistence authority only
EPITOME: Append-only, source-bound Ed25519 public-key enrollment, revocation and rotation evidence.
ABSOLUTE CANONICAL PATH: tools/eos/security/institutional_source_signing_key_registry.py
COLLABORATION / OWNERSHIP: Consumed by institutional signer source-response authentication; MongoDB owns durable records.
CERTIFICATION / UPDATE DATE: 2026-11-08
CHANGELOG:
- v1.0.0: Introduce immutable key enrollment, append-only revocation and bounded rotation events.
- v1.1.0: Persist proposal and approval evidence fingerprints; derive lifecycle
  projections from immutable events; add transactionally anchored per-key audit
  hash chains and an indexed governance-denial evidence collection.
- v1.2.0: Verify the complete existing event chain and audit head inside the
  registry append boundary before every lifecycle mutation.
- v1.3.0: Add tenant-partitioned, hash-chained denial records and audit heads
  with full-chain verification before every denial append.
- v1.4.0: Normalize denial timestamps to MongoDB millisecond precision before hashing.
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
AUDIT_HEAD_COLLECTION: Final[str] = "eos_institutional_source_signing_key_audit_heads"
DENIAL_COLLECTION: Final[str] = "eos_institutional_source_signing_key_denials"
DENIAL_HEAD_COLLECTION: Final[str] = "eos_institutional_source_signing_key_denial_audit_heads"
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

def _record_fingerprint(record: Mapping[str, Any]) -> str:
    """Fingerprint immutable domain fields, excluding MongoDB's storage _id."""
    canonical_record = {key: value for key, value in record.items() if key != "_id"}
    return sha256(_canonical(canonical_record)).hexdigest()


def _event_fingerprint(event: Mapping[str, Any]) -> str:
    """Hash an event's canonical content, excluding storage and its own hash."""
    canonical_event = {
        key: value for key, value in event.items()
        if key not in {"_id", "event_hash_sha256"}
    }
    return sha256(_canonical(canonical_event)).hexdigest()


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
        self._heads = events.database[AUDIT_HEAD_COLLECTION]
        self._denials = events.database[DENIAL_COLLECTION]
        self._denial_heads = events.database[DENIAL_HEAD_COLLECTION]

    def _seal_event(self, event: dict[str, Any], session: ClientSession) -> None:
        """Verify the complete chain, then link the next event to its current head."""
        self._verify_event_chain(
            source_system_id=event["source_system_id"],
            key_id=event["key_id"],
            session=session,
        )
        previous = self._events.find_one(
            {
                "source_system_id": event["source_system_id"],
                "key_id": event["key_id"],
            },
            sort=[("event_sequence", -1)],
            session=session,
        )
        if previous is None:
            if event["event_sequence"] != 1:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_CHAIN_GAP")
            previous_hash = "0" * 64
        else:
            previous_hash = previous.get("event_hash_sha256")
            if (
                type(previous_hash) is not str
                or _FINGERPRINT.fullmatch(previous_hash) is None
                or previous["event_sequence"] + 1 != event["event_sequence"]
                or _event_fingerprint(previous) != previous_hash
            ):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_CHAIN_INVALID")
        event["previous_event_hash_sha256"] = previous_hash
        event_hash = _event_fingerprint(event)
        head_filter = {
            "source_system_id": event["source_system_id"],
            "key_id": event["key_id"],
        }
        head = self._heads.find_one(head_filter, session=session)
        if head is None:
            if event["event_sequence"] != 1:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_HEAD_MISSING")
            self._heads.insert_one({
                **head_filter,
                "event_sequence": event["event_sequence"],
                "event_hash_sha256": event_hash,
            }, session=session)
        else:
            if (
                head.get("event_sequence") + 1 != event["event_sequence"]
                or head.get("event_hash_sha256") != previous_hash
            ):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_HEAD_CONFLICT")
            result = self._heads.update_one(
                {
                    **head_filter,
                    "event_sequence": head["event_sequence"],
                    "event_hash_sha256": previous_hash,
                },
                {"$set": {
                    "event_sequence": event["event_sequence"],
                    "event_hash_sha256": event_hash,
                }},
                session=session,
            )
            if result.matched_count != 1:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_HEAD_CONFLICT")
        event["event_hash_sha256"] = event_hash

    def _verify_event_chain(
        self, *, source_system_id: str, key_id: str, session: ClientSession,
    ) -> None:
        """Reject missing, reordered, edited, or deleted lifecycle events."""
        expected_previous = "0" * 64
        expected_sequence = 1
        try:
            events = self._events.find(
                {"source_system_id": source_system_id, "key_id": key_id},
                session=session,
            ).sort("event_sequence", 1)
            for event in events:
                if (
                    event.get("event_sequence") != expected_sequence
                    or event.get("previous_event_hash_sha256") != expected_previous
                    or event.get("event_hash_sha256") != _event_fingerprint(event)
                ):
                    raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_CHAIN_INVALID")
                expected_previous = event["event_hash_sha256"]
                expected_sequence += 1
            head = self._heads.find_one(
                {"source_system_id": source_system_id, "key_id": key_id},
                session=session,
            )
            if expected_sequence == 1:
                if head is not None:
                    raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_HEAD_INVALID")
            elif (
                head is None
                or head.get("event_sequence") != expected_sequence - 1
                or head.get("event_hash_sha256") != expected_previous
            ):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_AUDIT_HEAD_INVALID")
        except SourceSigningKeyRegistryError:
            raise
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_AUDIT_CHAIN_UNAVAILABLE") from error

    def _verify_denial_chain(self, *, tenant_id: str, session: ClientSession) -> None:
        """Reject edited, missing, reordered or head-inconsistent tenant denial records."""
        expected_previous = "0" * 64
        expected_sequence = 1
        try:
            events = self._denials.find(
                {"tenant_id": tenant_id}, session=session,
            ).sort("event_sequence", 1)
            for event in events:
                if (
                    event.get("event_sequence") != expected_sequence
                    or event.get("previous_event_hash_sha256") != expected_previous
                    or event.get("event_hash_sha256") != _event_fingerprint(event)
                ):
                    raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DENIAL_AUDIT_CHAIN_INVALID")
                expected_previous = event["event_hash_sha256"]
                expected_sequence += 1
            head = self._denial_heads.find_one({"tenant_id": tenant_id}, session=session)
            if expected_sequence == 1:
                if head is not None:
                    raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DENIAL_AUDIT_HEAD_INVALID")
            elif (
                head is None
                or head.get("event_sequence") != expected_sequence - 1
                or head.get("event_hash_sha256") != expected_previous
            ):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DENIAL_AUDIT_HEAD_INVALID")
        except SourceSigningKeyRegistryError:
            raise
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_DENIAL_AUDIT_UNAVAILABLE") from error
        except (KeyError, TypeError, ValueError) as error:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DENIAL_AUDIT_CHAIN_INVALID") from error

    def record_denial(
        self, *, record: Mapping[str, Any], session: ClientSession,
    ) -> dict[str, Any]:
        """Append a bounded denial fact to the tenant's tamper-evident audit chain."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        event = dict(record)
        tenant = _identifier("tenant_id", event.get("tenant_id"))
        if event.get("event_type") != "DENIED":
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_DENIAL_EVENT_INVALID")
        occurred = _instant("occurred_at", event.get("occurred_at"))
        event["occurred_at"] = occurred.replace(
            microsecond=(occurred.microsecond // 1000) * 1000,
        )
        self._verify_denial_chain(tenant_id=tenant, session=session)
        head_filter = {"tenant_id": tenant}
        head = self._denial_heads.find_one(head_filter, session=session)
        if head is None:
            sequence = 1
            previous_hash = "0" * 64
        else:
            sequence = head["event_sequence"] + 1
            previous_hash = head["event_hash_sha256"]
        event["event_sequence"] = sequence
        event["previous_event_hash_sha256"] = previous_hash
        event_hash = _event_fingerprint(event)
        event["event_hash_sha256"] = event_hash
        if head is None:
            self._denial_heads.insert_one({
                **head_filter,
                "event_sequence": sequence,
                "event_hash_sha256": event_hash,
            }, session=session)
        else:
            result = self._denial_heads.update_one(
                {
                    **head_filter,
                    "event_sequence": head["event_sequence"],
                    "event_hash_sha256": previous_hash,
                },
                {"$set": {
                    "event_sequence": sequence,
                    "event_hash_sha256": event_hash,
                }},
                session=session,
            )
            if result.matched_count != 1:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DENIAL_AUDIT_HEAD_CONFLICT")
        try:
            self._denials.insert_one(event, session=session)
        except DuplicateKeyError as error:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DENIAL_AUDIT_DUPLICATE") from error
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_DENIAL_AUDIT_PERSISTENCE_FAILED") from error
        return event

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
            events.database[AUDIT_HEAD_COLLECTION].create_index(
                [("source_system_id", 1), ("key_id", 1)],
                unique=True, name="uq_source_signing_key_audit_head",
            )
            events.database[DENIAL_COLLECTION].create_index(
                [("correlation_id", 1)],
                unique=True, name="uq_source_signing_key_denial_correlation",
            )
            events.database[DENIAL_COLLECTION].create_index(
                [("source_system_id", 1), ("key_id", 1), ("occurred_at", 1)],
                name="ix_source_signing_key_denial_history",
            )
            events.database[DENIAL_COLLECTION].create_index(
                [("tenant_id", 1), ("event_sequence", 1)],
                unique=True, name="uq_source_signing_key_denial_tenant_sequence",
            )
            events.database[DENIAL_HEAD_COLLECTION].create_index(
                [("tenant_id", 1)],
                unique=True, name="uq_source_signing_key_denial_audit_tenant",
            )
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_INDEX_UNAVAILABLE") from error

    def propose(
        self, *, source_system_id: str, key_id: str, public_key_bytes: bytes,
        valid_from: datetime, valid_until: datetime,
        proposed_by_principal_id: str, proposal_reference: str,
        identity_proofing_evidence_reference: str,
        source_authority_evidence_reference: str,
        proposed_at: datetime, idempotency_key: str, session: ClientSession,
        proposal_evidence_fingerprint_sha256: str | None = None,
        rotation_id: str | None = None, supersedes_key_id: str | None = None,
        overlap_until: datetime | None = None,
    ) -> dict[str, Any]:
        """Persist an immutable PENDING proposal; it is not yet resolvable."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        proposer = _identifier("proposed_by_principal_id", proposed_by_principal_id)
        proposal = _identifier("proposal_reference", proposal_reference)
        identity_reference = _identifier("identity_proofing_evidence_reference", identity_proofing_evidence_reference)
        source_authority_reference = _identifier("source_authority_evidence_reference", source_authority_evidence_reference)
        if proposal_evidence_fingerprint_sha256 is not None and (
            type(proposal_evidence_fingerprint_sha256) is not str
            or _FINGERPRINT.fullmatch(proposal_evidence_fingerprint_sha256) is None
        ):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_PROPOSAL_EVIDENCE_FINGERPRINT_INVALID")
        idem = _identifier("idempotency_key", idempotency_key)
        start, end, occurred = (
            _instant("valid_from", valid_from), _instant("valid_until", valid_until),
            _instant("proposed_at", proposed_at),
        )
        occurred = occurred.replace(microsecond=(occurred.microsecond // 1000) * 1000)
        if type(public_key_bytes) is not bytes or len(public_key_bytes) != 32:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_PUBLIC_KEY_INVALID")
        fingerprint = sha256(public_key_bytes).hexdigest()
        if (supersedes_key_id is None) != (rotation_id is None) or (supersedes_key_id is None) != (overlap_until is None):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_ROTATION_FIELDS_INCOMPLETE")
        rotation = None
        predecessor_id = None
        overlap = None
        if supersedes_key_id is not None:
            predecessor_id = _identifier("supersedes_key_id", supersedes_key_id)
            rotation_name = _identifier("rotation_id", rotation_id)
            overlap = _instant("overlap_until", overlap_until)
            rotation = {
                "rotation_id": rotation_name,
                "supersedes_key_id": predecessor_id,
                "overlap_until": overlap,
            }
        command_fingerprint = sha256(_canonical({
            "source_system_id": source, "key_id": key,
            "public_key_fingerprint_sha256": fingerprint,
            "valid_from": start, "valid_until": end,
            "proposed_by_principal_id": proposer, "proposal_reference": proposal,
            "identity_proofing_evidence_reference": identity_reference,
            "source_authority_evidence_reference": source_authority_reference,
            "proposal_evidence_fingerprint_sha256": proposal_evidence_fingerprint_sha256,
            "rotation": rotation,
        })).hexdigest()
        prior = self._events.find_one(
            {"source_system_id": source, "idempotency_key": idem}, session=session,
        )
        if prior is not None:
            if prior.get("event_type") != "PROPOSED" or prior.get("command_fingerprint_sha256") != command_fingerprint:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DIVERGENT_REPLAY")
            existing = self._keys.find_one(
                {"source_system_id": source, "key_id": key}, session=session,
            )
            if existing is None:
                raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_REPLAY_RECORD_MISSING")
            return existing
        if end <= start or occurred >= end:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_VALIDITY_INTERVAL_INVALID")
        if occurred > datetime.now(timezone.utc):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_PROPOSAL_CANNOT_BE_FUTURE_DATED")
        if predecessor_id is not None:
            predecessor = self._keys.find_one(
                {"source_system_id": source, "key_id": predecessor_id}, session=session,
            )
            predecessor_approval = self._events.find_one(
                {"source_system_id": source, "key_id": predecessor_id, "event_type": "APPROVED"},
                session=session,
            )
            if (
                predecessor is None or predecessor_approval is None
                or predecessor_approval["occurred_at"] > occurred
            ):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ROTATION_PREDECESSOR_NOT_APPROVED_AT_PROPOSAL")
            if self._keys.find_one(
                {"source_system_id": source, "rotation.supersedes_key_id": predecessor_id},
                session=session,
            ) is not None:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ROTATION_ALREADY_REPLACED")
            if not (start < overlap <= predecessor["valid_until"] and start < end):
                raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_ROTATION_OVERLAP_INVALID")
        record = {
            "schema": SCHEMA, "source_system_id": source, "key_id": key,
            "public_key_bytes": public_key_bytes,
            "public_key_fingerprint_sha256": fingerprint,
            "valid_from": start, "valid_until": end,
            "proposal_reference": proposal, "proposed_by_principal_id": proposer,
            "identity_proofing_evidence_reference": identity_reference,
            "source_authority_evidence_reference": source_authority_reference,
            "proposed_at": occurred, "lifecycle_state": "PENDING",
            "rotation": rotation,
        }
        fingerprint_of_record = _record_fingerprint(record)
        event = {
            "schema": EVENT_SCHEMA, "event_type": "PROPOSED",
            "source_system_id": source, "key_id": key,
            "idempotency_key": idem, "occurred_at": occurred,
            "actor_principal_id": proposer, "proposal_reference": proposal,
            "proposal_evidence_fingerprint_sha256": proposal_evidence_fingerprint_sha256,
            "record_fingerprint_sha256": fingerprint_of_record,
            "command_fingerprint_sha256": command_fingerprint, "event_sequence": 1,
        }
        try:
            self._seal_event(event, session)
            self._keys.insert_one(record, session=session)
            self._events.insert_one(event, session=session)
        except DuplicateKeyError as error:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_IDENTITY_OR_FINGERPRINT_EXISTS") from error
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_PROPOSAL_PERSISTENCE_FAILED") from error
        return record

    def approve(
        self, *, source_system_id: str, key_id: str,
        approved_by_principal_id: str, governance_decision_reference: str,
        approval_evidence_reference: str, approved_at: datetime,
        idempotency_key: str, session: ClientSession,
        approval_evidence_fingerprint_sha256: str | None = None,
    ) -> dict[str, Any]:
        """Append independent approval bound to the exact immutable proposal."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        approver = _identifier("approved_by_principal_id", approved_by_principal_id)
        decision = _identifier("governance_decision_reference", governance_decision_reference)
        evidence = _identifier("approval_evidence_reference", approval_evidence_reference)
        if approval_evidence_fingerprint_sha256 is not None and (
            type(approval_evidence_fingerprint_sha256) is not str
            or _FINGERPRINT.fullmatch(approval_evidence_fingerprint_sha256) is None
        ):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_APPROVAL_EVIDENCE_FINGERPRINT_INVALID")
        idem = _identifier("idempotency_key", idempotency_key)
        occurred = _instant("approved_at", approved_at)
        occurred = occurred.replace(microsecond=(occurred.microsecond // 1000) * 1000)
        record = self._keys.find_one({"source_system_id": source, "key_id": key}, session=session)
        if record is None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
        if approver == record["proposed_by_principal_id"]:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_MAKER_CHECKER_VIOLATION")
        fingerprint = _record_fingerprint(record)
        command_fingerprint = sha256(_canonical({
            "source_system_id": source, "key_id": key,
            "approved_by_principal_id": approver,
            "governance_decision_reference": decision,
            "approval_evidence_reference": evidence,
            "approval_evidence_fingerprint_sha256": approval_evidence_fingerprint_sha256,
            "proposal_reference": record["proposal_reference"],
            "record_fingerprint_sha256": fingerprint,
        })).hexdigest()
        prior = self._events.find_one(
            {"source_system_id": source, "idempotency_key": idem}, session=session,
        )
        if prior is not None:
            if prior.get("event_type") != "APPROVED" or prior.get("command_fingerprint_sha256") != command_fingerprint:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DIVERGENT_REPLAY")
            return prior
        proposal_event = self._events.find_one(
            {"source_system_id": source, "key_id": key, "event_type": "PROPOSED"}, session=session,
        )
        if (
            proposal_event is None or occurred < proposal_event["occurred_at"]
            or occurred >= record["valid_until"]
            or occurred > datetime.now(timezone.utc)
        ):
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_PROPOSAL_NOT_CURRENT")
        event = {
            "schema": EVENT_SCHEMA, "event_type": "APPROVED",
            "source_system_id": source, "key_id": key,
            "idempotency_key": idem, "occurred_at": occurred,
            "actor_principal_id": approver,
            "governance_decision_reference": decision,
            "approval_evidence_reference": evidence,
            "approval_evidence_fingerprint_sha256": approval_evidence_fingerprint_sha256,
            "proposal_reference": record["proposal_reference"],
            "record_fingerprint_sha256": fingerprint,
            "command_fingerprint_sha256": command_fingerprint, "event_sequence": 2,
        }
        if self._events.find_one(
            {"source_system_id": source, "key_id": key, "event_type": "APPROVED"}, session=session
        ) is not None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ALREADY_APPROVED")
        try:
            self._seal_event(event, session)
            self._events.insert_one(event, session=session)
        except DuplicateKeyError as error:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_APPROVAL_CONFLICT") from error
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_APPROVAL_PERSISTENCE_FAILED") from error
        return event

    def get_proposal(
        self, *, source_system_id: str, key_id: str, session: ClientSession,
    ) -> dict[str, Any]:
        """Read one exact immutable proposal within the caller's transaction."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        try:
            record = self._keys.find_one(
                {"source_system_id": source, "key_id": key}, session=session,
            )
            if record is None:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
            self._verify_event_chain(
                source_system_id=source, key_id=key, session=session,
            )
            # The key document is an immutable proposal snapshot. Derive its
            # current lifecycle projection from append-only governance events.
            revoked = self._events.find_one(
                {"source_system_id": source, "key_id": key, "event_type": "REVOKED"},
                session=session,
            )
            approved = self._events.find_one(
                {"source_system_id": source, "key_id": key, "event_type": "APPROVED"},
                session=session,
            )
            record["lifecycle_state"] = (
                "REVOKED" if revoked is not None
                else "APPROVED" if approved is not None
                else "PENDING"
            )
            return record
        except SourceSigningKeyRegistryError:
            raise
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_READ_UNAVAILABLE") from error

    def revoke(
        self, *, source_system_id: str, key_id: str, revoked_at: datetime,
        reason_reference: str, approval_evidence_reference: str,
        revocation_approved_by_principal_id: str,
        approval_evidence_fingerprint_sha256: str,
        revoked_by_principal_id: str, governance_decision_reference: str,
        idempotency_key: str,
        session: ClientSession,
    ) -> dict[str, Any]:
        """Append an immediate, revision-specific revocation event."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        reason = _identifier("reason_reference", reason_reference)
        approval_evidence = _identifier("approval_evidence_reference", approval_evidence_reference)
        approval_principal = _identifier("revocation_approved_by_principal_id", revocation_approved_by_principal_id)
        approval_fingerprint = _identifier("approval_evidence_fingerprint_sha256", approval_evidence_fingerprint_sha256)
        if len(approval_fingerprint) != 64 or any(ch not in "0123456789abcdef" for ch in approval_fingerprint):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_APPROVAL_FINGERPRINT_INVALID")
        actor = _identifier("revoked_by_principal_id", revoked_by_principal_id)
        decision = _identifier("governance_decision_reference", governance_decision_reference)
        idem = _identifier("idempotency_key", idempotency_key)
        occurred = _instant("revoked_at", revoked_at)
        occurred = occurred.replace(microsecond=(occurred.microsecond // 1000) * 1000)
        record = self._keys.find_one(
            {"source_system_id": source, "key_id": key}, session=session,
        )
        if record is None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_FOUND")
        if actor == record["proposed_by_principal_id"] or approval_principal in {
            actor, record["proposed_by_principal_id"],
        }:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_MAKER_CHECKER_VIOLATION")
        record_fingerprint = _record_fingerprint(record)
        command_fingerprint = sha256(_canonical({
            "source_system_id": source, "key_id": key,
            "revoked_by_principal_id": actor,
            "revocation_approved_by_principal_id": approval_principal,
            "reason_reference": reason,
            "approval_evidence_reference": approval_evidence,
            "approval_evidence_fingerprint_sha256": approval_fingerprint,
            "governance_decision_reference": decision,
            "record_fingerprint_sha256": record_fingerprint,
        })).hexdigest()
        prior = self._events.find_one(
            {"source_system_id": source, "idempotency_key": idem}, session=session,
        )
        if prior is not None:
            if prior.get("event_type") != "REVOKED" or prior.get("command_fingerprint_sha256") != command_fingerprint:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_DIVERGENT_REPLAY")
            return prior
        if occurred > datetime.now(timezone.utc):
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_REVOCATION_CANNOT_BE_FUTURE_DATED")
        approval_event = self._events.find_one(
            {"source_system_id": source, "key_id": key, "event_type": "APPROVED"},
            session=session,
        )
        if approval_event is None or occurred < approval_event["occurred_at"]:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_APPROVED")
        if self._events.find_one(
            {"source_system_id": source, "key_id": key, "event_type": "REVOKED"},
            session=session,
        ) is not None:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ALREADY_REVOKED")
        event = {
            "schema": EVENT_SCHEMA, "event_type": "REVOKED",
            "source_system_id": source, "key_id": key,
            "idempotency_key": idem, "occurred_at": occurred,
            "actor_principal_id": actor,
            "revocation_approved_by_principal_id": approval_principal,
            "reason_reference": reason,
            "approval_evidence_reference": approval_evidence,
            "approval_evidence_fingerprint_sha256": approval_fingerprint,
            "governance_decision_reference": decision,
            "record_fingerprint_sha256": record_fingerprint,
            "public_key_fingerprint_sha256": record["public_key_fingerprint_sha256"],
            "command_fingerprint_sha256": command_fingerprint, "event_sequence": 3,
        }
        try:
            self._seal_event(event, session)
            self._events.insert_one(event, session=session)
        except DuplicateKeyError as error:
            raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_REVOCATION_CONFLICT") from error
        except PyMongoError as error:
            if error.has_error_label("TransientTransactionError"):
                raise
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_REVOCATION_PERSISTENCE_FAILED") from error
        return event

    def resolve_current(
        self, *, source_system_id: str, key_id: str, session: ClientSession,
    ) -> dict[str, Any]:
        """Resolve current authority using verifier time; callers cannot backdate."""
        return self.resolve_historical(
            source_system_id=source_system_id,
            key_id=key_id,
            evaluated_at=datetime.now(timezone.utc),
            session=session,
        )

    def resolve_historical(
        self, *, source_system_id: str, key_id: str, evaluated_at: datetime,
        session: ClientSession,
    ) -> dict[str, Any]:
        """Resolve historical signature-time trust for audit only, never current authorization."""
        if session is None:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_SESSION_REQUIRED")
        source = _identifier("source_system_id", source_system_id)
        key = _identifier("key_id", key_id)
        at = _instant("evaluated_at", evaluated_at)
        try:
            self._verify_event_chain(
                source_system_id=source, key_id=key, session=session,
            )
            record = self._keys.find_one(
                {"source_system_id": source, "key_id": key}, session=session
            )
            if record is None:
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_UNTRUSTED")
            if not (record["valid_from"] <= at < record["valid_until"]):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_OUTSIDE_VALIDITY")
            approval = self._events.find_one(
                {"source_system_id": source, "key_id": key, "event_type": "APPROVED",
                 "occurred_at": {"$lte": at}},
                session=session,
            )
            if approval is None or approval.get("record_fingerprint_sha256") != _record_fingerprint(record):
                raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_NOT_INDEPENDENTLY_APPROVED")
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
                successor_approval = self._events.find_one(
                    {"source_system_id": source, "key_id": successor["key_id"],
                     "event_type": "APPROVED", "occurred_at": {"$lte": at}},
                    session=session,
                )
                successor_is_approved = (
                    successor_approval is not None
                    and successor_approval.get("record_fingerprint_sha256")
                    == _record_fingerprint(successor)
                )
                if successor_is_approved:
                    overlap = successor.get("rotation", {}).get("overlap_until")
                    if overlap is None or at >= overlap:
                        raise SourceSigningKeyRegistryConflict("SOURCE_SIGNING_KEY_ROTATION_OVERLAP_ENDED")
            return record
        except SourceSigningKeyRegistryError:
            raise
        except PyMongoError as error:
            raise SourceSigningKeyRegistryError("SOURCE_SIGNING_KEY_RESOLUTION_UNAVAILABLE") from error


__all__ = [
    "KEY_COLLECTION", "EVENT_COLLECTION", "AUDIT_HEAD_COLLECTION", "DENIAL_COLLECTION", "SourceSigningKeyRegistryError",
    "SourceSigningKeyRegistryConflict", "InstitutionalSourceSigningKeyLifecycleRegistry",
]

# ARTIFACT: WILSY OS Institutional Source Signing-Key Lifecycle Registry
# VERSION: v1.4.0
# AUTHORITY BOUNDARY: Durable public-key lifecycle evidence only; no caller authorization or verifier-result issuance.
# TENANT POSTURE: Source-system scoped; no tenant-issued trust.
# FAIL-CLOSED POSTURE: Missing, invalid, expired, revoked, or unavailable trust is denied.
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
