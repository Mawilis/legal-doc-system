"""Immutable tenant-scoped persistence for purpose-bound process-service GPS evidence.

TITLE: WILSY OS Process-Service Location Evidence Registry
VERSION: v1.0.0-P5L-LOCATION-EVIDENCE-REGISTRY
AUTHORITY: Persistence, hydration integrity, replay and access audit only.
TRANSACTION: Caller owns one active Mongo session/transaction.
PRIVACY: No TTL indexes or automatic deletion; retention requires an approved policy.
FINANCIAL AUTHORITY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Final, NoReturn, cast

from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.process_service_location_evidence_authority import (
    ProcessServiceLocationEvidenceAuthorityError,
    ProcessServiceLocationObservation,
    ProcessServiceLocationPermissionGrant,
    create_location_permission_grant,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ServiceAttempt
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)

VERSION: Final[str] = "v1.0.0-P5L-LOCATION-EVIDENCE-REGISTRY"
SCHEMA: Final[str] = "WILSY-PROCESS-SERVICE-LOCATION-EVIDENCE-REGISTRY/V1"
PERMISSION_COLLECTION: Final[str] = "process_service_location_permission_grants"
OBSERVATION_COLLECTION: Final[str] = "process_service_location_observations"
REVOCATION_COLLECTION: Final[str] = "process_service_location_permission_revocations"
ACCESS_AUDIT_COLLECTION: Final[str] = "process_service_location_access_audit"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$")
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN = frozenset({"default", "global", "global_root", "root", "master", "*"})

_GRANT_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "grant_id", "attempt_id", "fingerprint", "payload"})
_OBSERVATION_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "observation_id", "attempt_id", "grant_id", "fingerprint", "payload"})
_REVOCATION_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "grant_id", "revocation_id", "revoked_by_principal_id", "revoked_at", "reason_reference", "evidence_reference", "fingerprint"})
_ACCESS_FIELDS = frozenset({"schema", "version", "entity_type", "tenant_id", "event_id", "attempt_id", "grant_id", "actor_principal_id", "actor_scope", "accessed_at", "record_count", "purpose", "fingerprint"})


class ProcessServiceLocationEvidenceRegistryError(RuntimeError):
    """Base fail-closed location-evidence persistence failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class ProcessServiceLocationEvidenceRegistryTransactionRequiredError(ProcessServiceLocationEvidenceRegistryError):
    """No already-active caller-owned transaction was supplied."""


class ProcessServiceLocationEvidenceRegistryConflictError(ProcessServiceLocationEvidenceRegistryError):
    """Identity reuse, replay divergence, revoked grant or scope conflict."""


class ProcessServiceLocationEvidenceRegistryRecordInvalidError(ProcessServiceLocationEvidenceRegistryError):
    """Persisted envelope or canonical payload is malformed or divergent."""


class ProcessServiceLocationEvidenceRegistryRetryTransactionError(ProcessServiceLocationEvidenceRegistryError):
    """A duplicate race requires retrying the complete caller transaction."""


class ProcessServiceLocationEvidenceRegistryPersistenceError(ProcessServiceLocationEvidenceRegistryError):
    """MongoDB operation failed without a safe conflict classification."""


def _fail(kind: type[ProcessServiceLocationEvidenceRegistryError], code: str, cause: BaseException | None = None) -> NoReturn:
    error = kind(code)
    if cause is None:
        raise error
    raise error from cause


def _tenant(value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _ID.fullmatch(value) is None or value.casefold() in _FORBIDDEN:
        _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_TENANT_INVALID")
    return value


def _identity(value: object, code: str) -> str:
    if not isinstance(value, str) or value != value.strip() or _ID.fullmatch(value) is None:
        _fail(ProcessServiceLocationEvidenceRegistryError, code)
    return value


def _active(session: object) -> object:
    try:
        marker = getattr(session, "in_transaction", None)
        active = marker() if callable(marker) else marker
    except Exception as error:
        _fail(ProcessServiceLocationEvidenceRegistryTransactionRequiredError, "P5L_ACTIVE_TRANSACTION_REQUIRED", error)
    if active is not True:
        _fail(ProcessServiceLocationEvidenceRegistryTransactionRequiredError, "P5L_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _digest(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


def _canonical(row: Mapping[str, Any]) -> dict[str, Any]:
    value = dict(row)
    value.pop("_id", None)
    return value


def _timestamp(value: object, code: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail(ProcessServiceLocationEvidenceRegistryError, code)
    return value


def _iso(value: object, code: str) -> str:
    return _timestamp(value, code).isoformat()


def _parse_time(value: object, code: str) -> datetime:
    if not isinstance(value, str):
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, code)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, code, error)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.isoformat() != value:
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, code)
    return parsed


def _validate_envelope(
    row: Mapping[str, Any],
    *,
    fields: frozenset[str],
    entity_type: str,
    tenant_id: str,
    identity_field: str,
    identity_value: str,
) -> dict[str, Any]:
    value = _canonical(row)
    if set(value) != fields:
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_RECORD_SHAPE_INVALID")
    if value["schema"] != SCHEMA or value["version"] != VERSION or value["entity_type"] != entity_type:
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_RECORD_VERSION_INVALID")
    if value["tenant_id"] != tenant_id or value[identity_field] != identity_value:
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_RECORD_SCOPE_INVALID")
    payload = value.get("payload")
    fingerprint = value.get("fingerprint")
    if not isinstance(payload, Mapping) or not isinstance(fingerprint, str) or _SHA3.fullmatch(fingerprint) is None:
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_RECORD_PAYLOAD_INVALID")
    if _digest(payload) != fingerprint:
        _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_RECORD_FINGERPRINT_INVALID")
    return value


def _persist(
    collection: Any,
    record: dict[str, Any],
    *,
    identity_query: dict[str, str],
    session: object,
) -> dict[str, Any]:
    tx = _active(session)
    try:
        existing = collection.find_one(identity_query, session=tx)
    except PyMongoError as error:
        _fail(ProcessServiceLocationEvidenceRegistryPersistenceError, "P5L_READ_UNAVAILABLE", error)
    if existing is not None:
        if _canonical(cast(Mapping[str, Any], existing)) == record:
            return _canonical(cast(Mapping[str, Any], existing))
        _fail(ProcessServiceLocationEvidenceRegistryConflictError, "P5L_REPLAY_CONFLICT")
    try:
        collection.insert_one(record, session=tx)
    except DuplicateKeyError as error:
        _fail(ProcessServiceLocationEvidenceRegistryRetryTransactionError, "P5L_RETRY_TRANSACTION_REQUIRED", error)
    except PyMongoError as error:
        _fail(ProcessServiceLocationEvidenceRegistryPersistenceError, "P5L_INSERT_UNAVAILABLE", error)
    return record


class ProcessServiceLocationEvidenceRegistry:
    """Persist permission grants, GPS observations, revocations and read-access audit."""

    @staticmethod
    def ensure_indexes(
        permission_collection: Any,
        observation_collection: Any,
        revocation_collection: Any,
        access_audit_collection: Any,
    ) -> None:
        """Create deterministic tenant indexes; intentionally create no TTL index."""
        try:
            permission_collection.create_index([("tenant_id", 1), ("grant_id", 1)], unique=True, name="p5l_permission_grant_unique")
            permission_collection.create_index([("tenant_id", 1), ("attempt_id", 1), ("granted_at", 1)], name="p5l_permission_attempt_history")
            observation_collection.create_index([("tenant_id", 1), ("observation_id", 1)], unique=True, name="p5l_location_observation_unique")
            observation_collection.create_index([("tenant_id", 1), ("attempt_id", 1), ("captured_at", 1)], name="p5l_location_attempt_history")
            revocation_collection.create_index([("tenant_id", 1), ("grant_id", 1)], unique=True, name="p5l_permission_revocation_unique")
            access_audit_collection.create_index([("tenant_id", 1), ("event_id", 1)], unique=True, name="p5l_location_access_event_unique")
            access_audit_collection.create_index([("tenant_id", 1), ("attempt_id", 1), ("accessed_at", 1)], name="p5l_location_access_history")
        except PyMongoError as error:
            _fail(ProcessServiceLocationEvidenceRegistryPersistenceError, "P5L_INDEX_PERSISTENCE_UNAVAILABLE", error)

    @staticmethod
    def persist_permission_grant(
        grant: ProcessServiceLocationPermissionGrant,
        collection: Any,
        *,
        session: object,
    ) -> ProcessServiceLocationPermissionGrant:
        """Insert one immutable permission grant or accept exact replay."""
        if type(grant) is not ProcessServiceLocationPermissionGrant:
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_PERMISSION_GRANT_REQUIRED")
        try:
            grant.__post_init__()
            payload = grant.to_dict()
            fingerprint = grant.fingerprint
        except ProcessServiceLocationEvidenceAuthorityError as error:
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_PERMISSION_GRANT_INVALID", error)
        record = {
            "schema": SCHEMA, "version": VERSION, "entity_type": "ProcessServiceLocationPermissionGrant",
            "tenant_id": grant.tenant_id, "grant_id": grant.grant_id, "attempt_id": grant.attempt_id,
            "fingerprint": fingerprint, "payload": payload,
        }
        _persist(collection, record, identity_query={"tenant_id": grant.tenant_id, "grant_id": grant.grant_id}, session=session)
        return grant

    @staticmethod
    def get_permission_grant(
        tenant_id: str,
        grant_id: str,
        collection: Any,
        *,
        attempt: ServiceAttempt,
        allocation_receipt: ProcessServiceAllocationReceipt,
        allocation_current: ProcessServiceAllocationCurrent,
        session: object,
    ) -> ProcessServiceLocationPermissionGrant:
        """Hydrate one grant by replaying its canonical domain factory against current P1/P4 sources."""
        tx = _active(session)
        tenant = _tenant(tenant_id)
        identity = _identity(grant_id, "P5L_GRANT_ID_INVALID")
        try:
            row = collection.find_one({"tenant_id": tenant, "grant_id": identity}, session=tx)
        except PyMongoError as error:
            _fail(ProcessServiceLocationEvidenceRegistryPersistenceError, "P5L_READ_UNAVAILABLE", error)
        if row is None:
            _fail(ProcessServiceLocationEvidenceRegistryConflictError, "P5L_PERMISSION_GRANT_NOT_FOUND")
        record = _validate_envelope(
            cast(Mapping[str, Any], row), fields=_GRANT_FIELDS,
            entity_type="ProcessServiceLocationPermissionGrant", tenant_id=tenant,
            identity_field="grant_id", identity_value=identity,
        )
        payload = cast(Mapping[str, Any], record["payload"])
        try:
            grant = create_location_permission_grant(
                attempt=attempt, allocation_receipt=allocation_receipt, allocation_current=allocation_current,
                grant_id=cast(str, payload["grant_id"]), device_id=cast(str, payload["device_id"]),
                permission_granted=True, purpose=cast(str, payload["purpose"]),
                permission_evidence_reference=cast(str, payload["permission_evidence_reference"]),
                permission_evidence_fingerprint=cast(str, payload["permission_evidence_fingerprint"]),
                granted_at=_parse_time(payload["granted_at"], "P5L_GRANT_TIMESTAMP_INVALID"),
                expires_at=_parse_time(payload["expires_at"], "P5L_GRANT_TIMESTAMP_INVALID"),
            )
        except (ProcessServiceLocationEvidenceAuthorityError, KeyError, TypeError) as error:
            _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_GRANT_HYDRATION_INVALID", error)
        if grant.to_dict() != dict(payload) or grant.fingerprint != record["fingerprint"]:
            _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_GRANT_HYDRATION_MISMATCH")
        return grant

    @staticmethod
    def persist_observation(
        observation: ProcessServiceLocationObservation,
        collection: Any,
        *,
        session: object,
    ) -> ProcessServiceLocationObservation:
        """Append one immutable GPS observation; no update or overwrite path exists."""
        if type(observation) is not ProcessServiceLocationObservation:
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_OBSERVATION_REQUIRED")
        try:
            observation.__post_init__()
            payload = observation.to_dict()
            fingerprint = observation.fingerprint
        except ProcessServiceLocationEvidenceAuthorityError as error:
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_OBSERVATION_INVALID", error)
        record = {
            "schema": SCHEMA, "version": VERSION, "entity_type": "ProcessServiceLocationObservation",
            "tenant_id": observation.tenant_id, "observation_id": observation.observation_id,
            "attempt_id": observation.attempt_id, "grant_id": observation.grant_id,
            "fingerprint": fingerprint, "payload": payload,
        }
        _persist(collection, record, identity_query={"tenant_id": observation.tenant_id, "observation_id": observation.observation_id}, session=session)
        return observation

    @staticmethod
    def list_observations_for_attempt(
        tenant_id: str,
        attempt_id: str,
        observation_collection: Any,
        *,
        session: object,
    ) -> tuple[dict[str, Any], ...]:
        """Return integrity-checked immutable payloads for one exact tenant/attempt."""
        tx = _active(session)
        tenant = _tenant(tenant_id)
        attempt = _identity(attempt_id, "P5L_ATTEMPT_ID_INVALID")
        try:
            cursor = observation_collection.find(
                {"tenant_id": tenant, "attempt_id": attempt}, session=tx
            ).sort([("captured_at", 1), ("observation_id", 1)])
            rows = tuple(cursor)
        except PyMongoError as error:
            _fail(ProcessServiceLocationEvidenceRegistryPersistenceError, "P5L_READ_UNAVAILABLE", error)
        result: list[dict[str, Any]] = []
        for row in rows:
            record = _validate_envelope(
                cast(Mapping[str, Any], row), fields=_OBSERVATION_FIELDS,
                entity_type="ProcessServiceLocationObservation", tenant_id=tenant,
                identity_field="observation_id", identity_value=cast(str, row.get("observation_id")),
            )
            if record["attempt_id"] != attempt:
                _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_OBSERVATION_ATTEMPT_BINDING_INVALID")
            payload = cast(Mapping[str, Any], record["payload"])
            if payload.get("tenant_id") != tenant or payload.get("attempt_id") != attempt or payload.get("observation_id") != record["observation_id"] or payload.get("grant_id") != record["grant_id"]:
                _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_OBSERVATION_PAYLOAD_BINDING_INVALID")
            result.append(dict(payload))
        return tuple(result)

    @staticmethod
    def revoke_permission_grant(
        *,
        tenant_id: str,
        grant_id: str,
        revocation_id: str,
        revoked_by_principal_id: str,
        revoked_at: datetime,
        reason_reference: str,
        evidence_reference: str,
        grant_collection: Any,
        revocation_collection: Any,
        session: object,
    ) -> dict[str, Any]:
        """Append an immutable revocation event; never rewrite the original grant."""
        tx = _active(session)
        tenant = _tenant(tenant_id)
        grant = _identity(grant_id, "P5L_GRANT_ID_INVALID")
        try:
            source = grant_collection.find_one({"tenant_id": tenant, "grant_id": grant}, session=tx)
        except PyMongoError as error:
            _fail(ProcessServiceLocationEvidenceRegistryPersistenceError, "P5L_READ_UNAVAILABLE", error)
        if source is None:
            _fail(ProcessServiceLocationEvidenceRegistryConflictError, "P5L_PERMISSION_GRANT_NOT_FOUND")
        _validate_envelope(
            cast(Mapping[str, Any], source), fields=_GRANT_FIELDS,
            entity_type="ProcessServiceLocationPermissionGrant", tenant_id=tenant,
            identity_field="grant_id", identity_value=grant,
        )
        identity = _identity(revocation_id, "P5L_REVOCATION_ID_INVALID")
        actor = _identity(revoked_by_principal_id, "P5L_REVOKING_PRINCIPAL_INVALID")
        if not isinstance(reason_reference, str) or not reason_reference.strip() or reason_reference != reason_reference.strip():
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_REVOCATION_REASON_INVALID")
        if not isinstance(evidence_reference, str) or not evidence_reference.strip() or evidence_reference != evidence_reference.strip():
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_REVOCATION_EVIDENCE_INVALID")
        revoked = _timestamp(revoked_at, "P5L_REVOCATION_TIMESTAMP_INVALID")
        values = {
            "schema": SCHEMA, "version": VERSION, "entity_type": "ProcessServiceLocationPermissionRevocation",
            "tenant_id": tenant, "grant_id": grant, "revocation_id": identity,
            "revoked_by_principal_id": actor, "revoked_at": revoked.isoformat(),
            "reason_reference": reason_reference, "evidence_reference": evidence_reference,
        }
        record = {**values, "fingerprint": _digest(values)}
        return _persist(
            revocation_collection, record,
            identity_query={"tenant_id": tenant, "grant_id": grant}, session=tx,
        )

    @staticmethod
    def assert_permission_grant_active(
        tenant_id: str,
        grant_id: str,
        revocation_collection: Any,
        *,
        session: object,
    ) -> None:
        """Reject an exact grant once a tenant-scoped revocation exists."""
        tx = _active(session)
        tenant = _tenant(tenant_id)
        grant = _identity(grant_id, "P5L_GRANT_ID_INVALID")
        try:
            row = revocation_collection.find_one({"tenant_id": tenant, "grant_id": grant}, session=tx)
        except PyMongoError as error:
            _fail(ProcessServiceLocationEvidenceRegistryPersistenceError, "P5L_READ_UNAVAILABLE", error)
        if row is not None:
            value = _canonical(cast(Mapping[str, Any], row))
            if set(value) != _REVOCATION_FIELDS or value.get("schema") != SCHEMA or value.get("version") != VERSION or value.get("entity_type") != "ProcessServiceLocationPermissionRevocation" or value.get("tenant_id") != tenant or value.get("grant_id") != grant or not isinstance(value.get("fingerprint"), str):
                _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_REVOCATION_RECORD_INVALID")
            expected = dict(value)
            fingerprint = cast(str, expected.pop("fingerprint"))
            if _digest(expected) != fingerprint:
                _fail(ProcessServiceLocationEvidenceRegistryRecordInvalidError, "P5L_REVOCATION_FINGERPRINT_INVALID")
            _fail(ProcessServiceLocationEvidenceRegistryConflictError, "P5L_PERMISSION_GRANT_REVOKED")

    @staticmethod
    def record_access(
        *,
        tenant_id: str,
        event_id: str,
        attempt_id: str,
        grant_id: str,
        actor_principal_id: str,
        actor_scope: str,
        accessed_at: datetime,
        record_count: int,
        purpose: str,
        collection: Any,
        session: object,
    ) -> dict[str, Any]:
        """Append metadata-only access audit; never duplicate GPS coordinates."""
        tx = _active(session)
        tenant = _tenant(tenant_id)
        event = _identity(event_id, "P5L_ACCESS_EVENT_ID_INVALID")
        attempt = _identity(attempt_id, "P5L_ATTEMPT_ID_INVALID")
        grant = _identity(grant_id, "P5L_GRANT_ID_INVALID")
        actor = _identity(actor_principal_id, "P5L_ACCESS_ACTOR_INVALID")
        if not isinstance(actor_scope, str) or not actor_scope.strip() or actor_scope != actor_scope.strip():
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_ACCESS_SCOPE_INVALID")
        if not isinstance(purpose, str) or not purpose.strip() or purpose != purpose.strip():
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_ACCESS_PURPOSE_INVALID")
        timestamp = _timestamp(accessed_at, "P5L_ACCESS_TIMESTAMP_INVALID")
        if isinstance(record_count, bool) or not isinstance(record_count, int) or record_count < 0:
            _fail(ProcessServiceLocationEvidenceRegistryError, "P5L_ACCESS_COUNT_INVALID")
        values = {
            "schema": SCHEMA, "version": VERSION, "entity_type": "ProcessServiceLocationAccessEvent",
            "tenant_id": tenant, "event_id": event, "attempt_id": attempt, "grant_id": grant,
            "actor_principal_id": actor, "actor_scope": actor_scope, "accessed_at": timestamp.isoformat(),
            "record_count": record_count, "purpose": purpose,
        }
        record = {**values, "fingerprint": _digest(values)}
        return _persist(collection, record, identity_query={"tenant_id": tenant, "event_id": event}, session=tx)


__all__ = [
    "ACCESS_AUDIT_COLLECTION", "OBSERVATION_COLLECTION", "PERMISSION_COLLECTION",
    "REVOCATION_COLLECTION", "SCHEMA", "VERSION",
    "ProcessServiceLocationEvidenceRegistry",
    "ProcessServiceLocationEvidenceRegistryConflictError",
    "ProcessServiceLocationEvidenceRegistryError",
    "ProcessServiceLocationEvidenceRegistryPersistenceError",
    "ProcessServiceLocationEvidenceRegistryRecordInvalidError",
    "ProcessServiceLocationEvidenceRegistryRetryTransactionError",
    "ProcessServiceLocationEvidenceRegistryTransactionRequiredError",
]

# ARTIFACT: process_service_location_evidence_registry.py
# VERSION: v1.0.0-P5L-LOCATION-EVIDENCE-REGISTRY
# AUTHORITY: Tenant-scoped immutable permission/location persistence, revocation and metadata-only access audit.
# TENANT: Exact tenant + grant/observation/attempt; no cross-tenant fallback.
# RETENTION: No TTL or automatic deletion; policy-specific retention must be approved before enforcement.
# END OF WILSY OS SOVEREIGN ARTIFACT
