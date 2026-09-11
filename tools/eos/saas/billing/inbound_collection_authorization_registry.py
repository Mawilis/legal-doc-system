"""WILSY OS M11 R8-R3B-P5 durable inbound collection authorization registry.
TITLE: Inbound Collection Authorization Registry and Lifecycle
VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Tenant-scoped durability, current-validity enforcement, revocation, and atomic single-use consumption for typed inbound collection authorization evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/inbound_collection_authorization_registry.py
COLLABORATION / OWNERSHIP: SaaS authorization persistence owner; callers own issuance composition, sessions, transactions, and retries.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE persists and strictly hydrates mandatory immutable expiry-policy provenance through the P4 domain fingerprint; v1.0.0-M11-R8-R3B-P5 established strict immutable authorization hydration, tenant/idempotency replay, bounded validity, revocation CAS, and exact collection-authority single-use CAS.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tenant-scoped predicates and opaque references; no provider, invoice-model, credential, or settlement data is resolved.
TENANT BOUNDARY: Every read and lifecycle CAS carries tenant_id and exact authorization identity.
AUTHORITY BOUNDARY: Durable authorization evidence and mutable lifecycle state only; no authorization issuance or collection-authority issuance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns outbound financial execution and settlement evidence.
TRANSACTION BOUNDARY: Caller supplies an active Mongo session and owns transaction start, commit, abort, and whole-transaction retry.
FAIL-CLOSED DECLARATION: Corrupt immutable evidence, impossible lifecycle, expired/revoked/consumed transitions, divergent replay, and CAS races reject.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Optional

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.domain.inbound_collection_authorization import (
    InboundCollectionAuthorization,
    InboundCollectionAuthorizationError,
)


VERSION = "v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE"
COLLECTION = "inbound_collection_authorizations"
_LIFECYCLE_FIELDS = frozenset(
    {"revoked_at", "revocation_reference", "consumed_at", "consumed_by_collection_authority_id"}
)


class InboundCollectionAuthorizationRegistryError(RuntimeError):
    """Base fail-closed error for durable authorization lifecycle operations."""


class InboundCollectionAuthorizationPersistedRecordInvalidError(InboundCollectionAuthorizationRegistryError):
    """Persisted immutable evidence or lifecycle state cannot be hydrated."""


class InboundCollectionAuthorizationReplayConflictError(InboundCollectionAuthorizationRegistryError):
    """A durable authorization identity exists with divergent immutable evidence."""


class InboundCollectionAuthorizationLifecycleConflictError(InboundCollectionAuthorizationRegistryError):
    """A revoke or consume CAS precondition failed without changing durable state."""


def _required_text(name: str, value: object) -> str:
    """Validate an opaque non-empty canonical lifecycle reference."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise InboundCollectionAuthorizationRegistryError(f"M11R8_P5_INVALID_{name.upper()}")
    return value


def _aware(name: str, value: object) -> datetime:
    """Require caller-supplied aware time and canonicalize it to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise InboundCollectionAuthorizationRegistryError(f"M11R8_P5_INVALID_{name.upper()}")
    return value.astimezone(timezone.utc)


def _canonical_timestamp(value: datetime) -> str:
    """Match the P4 ISO-8601 timestamp representation persisted in Mongo."""
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _query_rows(collection: Any, query: dict[str, object], *, session: Any) -> list[dict[str, Any]]:
    """Read at most two rows so duplicate durable identities fail closed."""
    try:
        cursor = collection.find(query, session=session)
        limited = cursor.limit(2) if hasattr(cursor, "limit") else cursor
        return [dict(row) for row in list(limited)[:2]]
    except PyMongoError as error:
        raise InboundCollectionAuthorizationRegistryError("M11R8_P5_LOOKUP_FAILED") from error
    except Exception as error:
        raise InboundCollectionAuthorizationRegistryError("M11R8_P5_LOOKUP_FAILED") from error


def _one(collection: Any, query: dict[str, object], *, session: Any) -> dict[str, Any] | None:
    """Resolve one exact tenant-scoped row or reject duplicate durable rows."""
    rows = _query_rows(collection, query, session=session)
    if len(rows) > 1:
        raise InboundCollectionAuthorizationRegistryError("M11R8_P5_MULTIPLE_DURABLE_AUTHORIZATIONS")
    return None if not rows else rows[0]


def _hydrate(document: dict[str, Any]) -> "InboundCollectionAuthorizationRecord":
    """Strictly reconstruct immutable authorization plus separate lifecycle state."""
    body = dict(document)
    body.pop("_id", None)
    try:
        lifecycle = body.pop("lifecycle")
        if not isinstance(lifecycle, dict) or set(lifecycle) != _LIFECYCLE_FIELDS:
            raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_INVALID_LIFECYCLE_SCHEMA")
        authorization = InboundCollectionAuthorization.from_dict(body)
        revoked_at = lifecycle["revoked_at"]
        consumed_at = lifecycle["consumed_at"]
        revocation_reference = lifecycle["revocation_reference"]
        consumed_by = lifecycle["consumed_by_collection_authority_id"]
        if revoked_at is not None:
            revoked_at = _aware("revoked_at", revoked_at)
        if consumed_at is not None:
            consumed_at = _aware("consumed_at", consumed_at)
        if (revoked_at is None) != (revocation_reference is None):
            raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_INVALID_REVOCATION_PAIR")
        if (consumed_at is None) != (consumed_by is None):
            raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_INVALID_CONSUMPTION_PAIR")
        if revoked_at is not None:
            _required_text("revocation_reference", revocation_reference)
            if revoked_at < authorization.authorized_at:
                raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_REVOCATION_BEFORE_AUTHORIZATION")
        if consumed_at is not None:
            _required_text("consumed_by_collection_authority_id", consumed_by)
            if consumed_at < authorization.authorized_at or consumed_at >= authorization.expires_at:
                raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_CONSUMPTION_OUTSIDE_WINDOW")
        if revoked_at is not None and consumed_at is not None:
            raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_REVOKED_AND_CONSUMED")
        return InboundCollectionAuthorizationRecord(
            authorization=authorization,
            revoked_at=revoked_at,
            revocation_reference=revocation_reference,
            consumed_at=consumed_at,
            consumed_by_collection_authority_id=consumed_by,
        )
    except InboundCollectionAuthorizationPersistedRecordInvalidError:
        raise
    except InboundCollectionAuthorizationRegistryError as error:
        raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_PERSISTED_RECORD_INVALID") from error
    except (InboundCollectionAuthorizationError, KeyError, TypeError, ValueError) as error:
        raise InboundCollectionAuthorizationPersistedRecordInvalidError("M11R8_P5_PERSISTED_RECORD_INVALID") from error


@dataclass(frozen=True, slots=True)
class InboundCollectionAuthorizationRecord:
    """Immutable registry snapshot combining P4 evidence with current lifecycle state."""

    authorization: InboundCollectionAuthorization
    revoked_at: datetime | None
    revocation_reference: str | None
    consumed_at: datetime | None
    consumed_by_collection_authority_id: str | None

    def is_currently_usable(self, at: datetime) -> bool:
        """Return validity at caller-supplied aware time without mutating the record."""
        evaluation = _aware("evaluation_at", at)
        return (
            self.revoked_at is None
            and self.consumed_at is None
            and self.authorization.authorized_at <= evaluation < self.authorization.expires_at
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize immutable evidence and lifecycle state with explicit separation."""
        return {
            **self.authorization.to_dict(),
            "lifecycle": {
                "revoked_at": self.revoked_at,
                "revocation_reference": self.revocation_reference,
                "consumed_at": self.consumed_at,
                "consumed_by_collection_authority_id": self.consumed_by_collection_authority_id,
            },
        }


class InboundCollectionAuthorizationRegistry:
    """Persist and consume typed authorization evidence without issuing it."""

    @staticmethod
    def _hydrate(document: dict[str, Any]) -> InboundCollectionAuthorizationRecord:
        """Expose strict hydration for registry-local certificate inspection."""
        return _hydrate(document)

    @staticmethod
    def _require_active_transaction(session: Any) -> Any:
        """Require caller-owned active transaction; never create, commit, or abort one."""
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise InboundCollectionAuthorizationRegistryError("M11R8_P5_ACTIVE_TRANSACTION_REQUIRED")
        return session

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create only tenant-scoped authorization-ID and idempotency uniqueness indexes."""
        collection.create_index(
            [("tenant_id", ASCENDING), ("inbound_collection_authorization_id", ASCENDING)],
            unique=True,
            name="tenant_inbound_collection_authorization_identity_unique",
        )
        collection.create_index(
            [("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)],
            unique=True,
            name="tenant_inbound_collection_authorization_idempotency_unique",
        )

    @staticmethod
    def _get_row(tenant_id: str, authorization_id: str, collection: Any, *, session: Any) -> InboundCollectionAuthorizationRecord | None:
        tenant = _required_text("tenant_id", tenant_id)
        auth_id = _required_text("authorization_id", authorization_id)
        row = _one(collection, {"tenant_id": tenant, "inbound_collection_authorization_id": auth_id}, session=session)
        return None if row is None else _hydrate(row)

    @staticmethod
    def get(tenant_id: str, authorization_id: str, collection: Any, *, session: Any = None) -> InboundCollectionAuthorizationRecord | None:
        """Return one strictly hydrated tenant-scoped authorization snapshot."""
        tx = InboundCollectionAuthorizationRegistry._require_active_transaction(session)
        return InboundCollectionAuthorizationRegistry._get_row(tenant_id, authorization_id, collection, session=tx)

    @staticmethod
    def get_by_idempotency_key(tenant_id: str, idempotency_key: str, collection: Any, *, session: Any = None) -> InboundCollectionAuthorizationRecord | None:
        """Return one strictly hydrated tenant-scoped idempotency record."""
        tx = InboundCollectionAuthorizationRegistry._require_active_transaction(session)
        tenant = _required_text("tenant_id", tenant_id)
        key = _required_text("idempotency_key", idempotency_key.strip() if isinstance(idempotency_key, str) else idempotency_key)
        row = _one(collection, {"tenant_id": tenant, "idempotency_key": key}, session=tx)
        return None if row is None else _hydrate(row)

    @staticmethod
    def create(value: InboundCollectionAuthorization, collection: Any, *, session: Any = None) -> InboundCollectionAuthorizationRecord:
        """Persist initial unrevoked/unconsumed evidence or return exact current replay.

        Lifecycle state is always initialized by this registry. Duplicate-key races
        propagate so the caller can restart its entire transaction.
        """
        tx = InboundCollectionAuthorizationRegistry._require_active_transaction(session)
        if not isinstance(value, InboundCollectionAuthorization):
            raise InboundCollectionAuthorizationReplayConflictError("M11R8_P5_INVALID_AUTHORIZATION")
        tenant = value.tenant_id
        id_row = _one(collection, {"tenant_id": tenant, "inbound_collection_authorization_id": value.inbound_collection_authorization_id}, session=tx)
        idem_row = _one(collection, {"tenant_id": tenant, "idempotency_key": value.idempotency_key}, session=tx)
        existing = [row for row in (id_row, idem_row) if row is not None]
        if existing:
            hydrated = [_hydrate(row) for row in existing]
            if len({record.authorization.to_dict()["authorization_evidence_fingerprint"] for record in hydrated}) != 1:
                raise InboundCollectionAuthorizationReplayConflictError("M11R8_P5_DISAGREEING_REPLAY_FACTS")
            record = hydrated[0]
            if record.authorization != value:
                raise InboundCollectionAuthorizationReplayConflictError("M11R8_P5_DIVERGENT_REPLAY")
            return record
        document = {
            **value.to_dict(),
            "lifecycle": {
                "revoked_at": None,
                "revocation_reference": None,
                "consumed_at": None,
                "consumed_by_collection_authority_id": None,
            },
        }
        try:
            collection.insert_one(document, session=tx)
        except DuplicateKeyError:
            raise
        except PyMongoError as error:
            raise InboundCollectionAuthorizationRegistryError("M11R8_P5_INSERT_FAILED") from error
        return _hydrate(document)

    @staticmethod
    def revoke(
        tenant_id: str,
        authorization_id: str,
        revocation_reference: str,
        revoked_at: datetime,
        collection: Any,
        *,
        session: Any = None,
        expected_authorization_evidence_fingerprint: str | None = None,
    ) -> InboundCollectionAuthorizationRecord:
        """Atomically revoke an unconsumed authorization using caller time and session."""
        tx = InboundCollectionAuthorizationRegistry._require_active_transaction(session)
        reference = _required_text("revocation_reference", revocation_reference)
        when = _aware("revoked_at", revoked_at)
        current = InboundCollectionAuthorizationRegistry._get_row(tenant_id, authorization_id, collection, session=tx)
        if current is None or (expected_authorization_evidence_fingerprint is not None and current.authorization.authorization_evidence_fingerprint != expected_authorization_evidence_fingerprint):
            raise InboundCollectionAuthorizationLifecycleConflictError("M11R8_P5_REVOCATION_PRECONDITION_FAILED")
        if current.revoked_at is not None or current.consumed_at is not None or when < current.authorization.authorized_at:
            raise InboundCollectionAuthorizationLifecycleConflictError("M11R8_P5_REVOCATION_PRECONDITION_FAILED")
        query: dict[str, object] = {
            "tenant_id": current.authorization.tenant_id,
            "inbound_collection_authorization_id": current.authorization.inbound_collection_authorization_id,
            "authorization_evidence_fingerprint": current.authorization.authorization_evidence_fingerprint,
            "lifecycle.revoked_at": None,
            "lifecycle.consumed_at": None,
            "authorized_at": {"$lte": _canonical_timestamp(when)},
        }
        try:
            result = collection.update_one(query, {"$set": {"lifecycle.revoked_at": when, "lifecycle.revocation_reference": reference}}, session=tx)
        except PyMongoError as error:
            raise InboundCollectionAuthorizationRegistryError("M11R8_P5_REVOCATION_UPDATE_FAILED") from error
        if getattr(result, "matched_count", 0) != 1:
            raise InboundCollectionAuthorizationLifecycleConflictError("M11R8_P5_REVOCATION_PRECONDITION_FAILED")
        return replace(current, revoked_at=when, revocation_reference=reference)

    @staticmethod
    def consume(
        tenant_id: str,
        authorization_id: str,
        authorization_evidence_fingerprint: str,
        consumed_at: datetime,
        consumed_by_collection_authority_id: str,
        collection: Any,
        *,
        session: Any = None,
    ) -> InboundCollectionAuthorizationRecord:
        """Atomically consume once and bind the exact collection-authority identity."""
        tx = InboundCollectionAuthorizationRegistry._require_active_transaction(session)
        consumer = _required_text("consumed_by_collection_authority_id", consumed_by_collection_authority_id)
        when = _aware("consumed_at", consumed_at)
        current = InboundCollectionAuthorizationRegistry._get_row(tenant_id, authorization_id, collection, session=tx)
        if current is None or current.authorization.authorization_evidence_fingerprint != authorization_evidence_fingerprint:
            raise InboundCollectionAuthorizationLifecycleConflictError("M11R8_P5_CONSUMPTION_PRECONDITION_FAILED")
        if current.revoked_at is not None or current.consumed_at is not None or not (current.authorization.authorized_at <= when < current.authorization.expires_at):
            raise InboundCollectionAuthorizationLifecycleConflictError("M11R8_P5_CONSUMPTION_PRECONDITION_FAILED")
        query: dict[str, object] = {
            "tenant_id": current.authorization.tenant_id,
            "inbound_collection_authorization_id": current.authorization.inbound_collection_authorization_id,
            "authorization_evidence_fingerprint": authorization_evidence_fingerprint,
            "lifecycle.revoked_at": None,
            "lifecycle.consumed_at": None,
            "authorized_at": {"$lte": _canonical_timestamp(when)},
            "expires_at": {"$gt": _canonical_timestamp(when)},
        }
        try:
            result = collection.update_one(query, {"$set": {"lifecycle.consumed_at": when, "lifecycle.consumed_by_collection_authority_id": consumer}}, session=tx)
        except PyMongoError as error:
            raise InboundCollectionAuthorizationRegistryError("M11R8_P5_CONSUMPTION_UPDATE_FAILED") from error
        if getattr(result, "matched_count", 0) != 1:
            raise InboundCollectionAuthorizationLifecycleConflictError("M11R8_P5_CONSUMPTION_PRECONDITION_FAILED")
        return replace(current, consumed_at=when, consumed_by_collection_authority_id=consumer)


__all__ = [
    "COLLECTION",
    "InboundCollectionAuthorizationLifecycleConflictError",
    "InboundCollectionAuthorizationPersistedRecordInvalidError",
    "InboundCollectionAuthorizationRecord",
    "InboundCollectionAuthorizationRegistry",
    "InboundCollectionAuthorizationRegistryError",
    "InboundCollectionAuthorizationReplayConflictError",
    "VERSION",
]


# ARTIFACT: inbound_collection_authorization_registry.py
# VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE
# AUTHORITY BOUNDARY: Durable authorization evidence and lifecycle CAS only.
# TENANT POSTURE: Tenant-scoped identity, idempotency, reads, revocation, and consumption.
# FAIL-CLOSED POSTURE: Strict hydration, expiry, revocation, single-use, replay, and caller-session enforcement.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
