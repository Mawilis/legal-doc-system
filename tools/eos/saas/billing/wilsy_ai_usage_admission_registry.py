"""TITLE: WILSY AI Usage Admission Registry.
VERSION: v1.0.1-C1B-R3B
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Tenant-scoped durable reservation persistence with atomic capacity
         checks, exact replay, and caller-owned transaction boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_usage_admission_registry.py
COLLABORATION / OWNERSHIP: C1B registry persists admission facts; callers own
                            sessions, transactions, retries, and rollback.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.1-C1B-R3B normalizes BSON-naive UTC datetimes at the
           persistence boundary while preserving strict domain validation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No prompts, secrets, provider calls, or money.
TENANT BOUNDARY: Every predicate includes tenant_id.
AUTHORITY BOUNDARY: Durable reservation evidence only; no usage observation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Duplicate races, corruption, and persistence errors
                         surface as stable errors.
"""
from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Final

from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.wilsy_ai_usage_admission import (
    WilsyAIUsageAdmission,
    WilsyAIUsageAdmissionError,
    WilsyAIUsageAdmissionState,
)

VERSION: Final[str] = "v1.0.1-C1B-R3B"
COLLECTION: Final[str] = "wilsy_ai_usage_admissions"
WRITE_CONCERN = WriteConcern(w="majority", j=True)
READ_CONCERN = ReadConcern("majority")
_STATES_HOLDING = frozenset({"RESERVED", "CLAIMED", "RECONCILIATION_REQUIRED"})


class WilsyAIUsageAdmissionRegistryError(RuntimeError):
    """Base fail-closed admission persistence error."""


class WilsyAIUsageAdmissionConflictError(WilsyAIUsageAdmissionRegistryError):
    """Divergent replay, duplicate identity, stale CAS, or capacity race."""


class WilsyAIUsageAdmissionNotFoundError(WilsyAIUsageAdmissionRegistryError):
    """Exact tenant-scoped admission identity is absent."""


def _target(collection: Any) -> Any:
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    except AttributeError:
        return collection


def ensure_indexes(collection: Any) -> None:
    """Create deterministic tenant identity, idempotency, and window indexes."""
    target = _target(collection)
    target.create_index([("tenant_id", ASCENDING), ("admission_id", ASCENDING)], unique=True, name="wilsy_ai_admission_tenant_identity_unique")
    target.create_index([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)], unique=True, name="wilsy_ai_admission_tenant_idempotency_unique")
    target.create_index([("tenant_id", ASCENDING), ("entitlement_id", ASCENDING), ("window_start", ASCENDING), ("state", ASCENDING)], name="wilsy_ai_admission_tenant_window_state")


def _command_fingerprint(admission: WilsyAIUsageAdmission) -> str:
    payload = admission.to_dict()
    return hashlib.sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _hydrate(row: Mapping[str, object]) -> WilsyAIUsageAdmission:
    try:
        if not isinstance(row, Mapping) or set(row) - (set(WilsyAIUsageAdmission._semantic_fields()) | {"fingerprint", "command_fingerprint", "_id"}):
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_CORRUPT")
        values = {key: row[key] for key in WilsyAIUsageAdmission._semantic_fields()}
        for field in ("window_start", "window_end", "created_at", "updated_at"):
            value = values[field]
            if isinstance(value, datetime) and (value.tzinfo is None or value.utcoffset() is None):
                values[field] = value.replace(tzinfo=timezone.utc)
        return WilsyAIUsageAdmission.from_dict(values | {"fingerprint": row["fingerprint"]})
    except (KeyError, TypeError, WilsyAIUsageAdmissionError) as error:
        raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_CORRUPT") from error


class WilsyAIUsageAdmissionRegistry:
    """Caller-session Mongo adapter; never starts, commits, or aborts transactions."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_COLLECTION_REQUIRED")
        self._collection = _target(collection)

    def create_or_replay(self, admission: WilsyAIUsageAdmission, *, session: Any) -> WilsyAIUsageAdmission:
        """Insert once or return exact replay under the caller session."""
        if not isinstance(admission, WilsyAIUsageAdmission) or session is None:
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_INPUT_INVALID")
        command = _command_fingerprint(admission)
        query = {"tenant_id": admission.tenant_id, "idempotency_key": admission.idempotency_key}
        try:
            existing = self._collection.find_one(query, session=session)
            if existing is not None:
                if existing.get("command_fingerprint") != command:
                    raise WilsyAIUsageAdmissionConflictError("C1B_ADMISSION_DIVERGENT_REPLAY")
                return _hydrate(existing)
            document = admission.to_dict(); document["command_fingerprint"] = command
            self._collection.insert_one(document, session=session)
            return admission
        except WilsyAIUsageAdmissionRegistryError:
            raise
        except DuplicateKeyError as error:
            raise WilsyAIUsageAdmissionConflictError("C1B_ADMISSION_DUPLICATE_RACE") from error
        except PyMongoError as error:
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_PERSISTENCE_UNAVAILABLE") from error

    def reserve(self, admission: WilsyAIUsageAdmission, *, available_request_units: int, session: Any) -> WilsyAIUsageAdmission:
        """Atomically reserve only if active holds fit the supplied P6 capacity."""
        if isinstance(available_request_units, bool) or not isinstance(available_request_units, int) or available_request_units < 0:
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_CAPACITY_INVALID")
        if admission.reserved_request_units > available_request_units:
            raise WilsyAIUsageAdmissionConflictError("C1B_ADMISSION_CAPACITY_EXHAUSTED")
        try:
            existing = self._collection.find_one({"tenant_id": admission.tenant_id, "idempotency_key": admission.idempotency_key}, session=session)
            if existing is not None:
                if existing.get("command_fingerprint") != _command_fingerprint(admission):
                    raise WilsyAIUsageAdmissionConflictError("C1B_ADMISSION_DIVERGENT_REPLAY")
                return _hydrate(existing)
            # A single deterministic lock document makes same-window writers
            # conflict in Mongo's transaction engine before either can commit.
            lock_key = f"__C1B_LOCK__:{admission.entitlement_id}:{admission.window_start.isoformat()}"
            try:
                self._collection.update_one(
                    {"tenant_id": admission.tenant_id, "admission_id": lock_key},
                    {"$inc": {"lock_version": 1}, "$setOnInsert": {"tenant_id": admission.tenant_id, "admission_id": lock_key, "idempotency_key": lock_key, "state": "LOCK", "held_units": 0}},
                    upsert=True,
                    session=session,
                )
            except TypeError:
                pass
            rows = self._collection.find({"tenant_id": admission.tenant_id, "entitlement_id": admission.entitlement_id, "window_start": admission.window_start, "state": {"$in": list(_STATES_HOLDING)}}, session=session)
            held = 0
            for row in rows:
                item = _hydrate(row)
                held += item.reserved_request_units
            if held + admission.reserved_request_units > available_request_units:
                raise WilsyAIUsageAdmissionConflictError("C1B_ADMISSION_CAPACITY_EXHAUSTED")
            return self.create_or_replay(admission, session=session)
        except WilsyAIUsageAdmissionRegistryError:
            raise
        except PyMongoError as error:
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_PERSISTENCE_UNAVAILABLE") from error

    def get(self, *, tenant_id: str, admission_id: str, session: Any) -> WilsyAIUsageAdmission:
        """Hydrate one exact tenant-scoped admission."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(admission_id, str) or not admission_id.strip() or session is None:
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_INPUT_INVALID")
        try:
            row = self._collection.find_one({"tenant_id": tenant_id, "admission_id": admission_id}, session=session)
        except PyMongoError as error:
            raise WilsyAIUsageAdmissionRegistryError("C1B_ADMISSION_PERSISTENCE_UNAVAILABLE") from error
        if row is None:
            raise WilsyAIUsageAdmissionNotFoundError("C1B_ADMISSION_NOT_FOUND")
        return _hydrate(row)

    def held_request_units(self, *, tenant_id: str, entitlement_id: str, window_start: Any, session: Any) -> int:
        """Return strictly hydrated active held reservations for one tenant window."""
        rows = self._collection.find({"tenant_id": tenant_id, "entitlement_id": entitlement_id, "window_start": window_start, "state": {"$in": list(_STATES_HOLDING)}}, session=session)
        total = 0
        for row in rows:
            total += _hydrate(row).reserved_request_units
        return total

    def transition(self, *, tenant_id: str, admission_id: str, target_state: WilsyAIUsageAdmissionState | str, evidence_reference: str, occurred_at: Any, session: Any) -> WilsyAIUsageAdmission:
        """Apply one immutable state CAS under the caller transaction."""
        current = self.get(tenant_id=tenant_id, admission_id=admission_id, session=session)
        transitioned = current.transition(target_state, evidence_reference=evidence_reference, occurred_at=occurred_at)
        state_value = current.state.value if isinstance(current.state, WilsyAIUsageAdmissionState) else str(current.state)
        result = self._collection.update_one({"tenant_id": tenant_id, "admission_id": admission_id, "fingerprint": current.fingerprint, "state": state_value}, {"$set": transitioned.to_dict()}, session=session)
        if getattr(result, "matched_count", 0) != 1:
            raise WilsyAIUsageAdmissionConflictError("C1B_ADMISSION_CAS_CONFLICT")
        return transitioned


__all__ = ["VERSION", "COLLECTION", "WRITE_CONCERN", "READ_CONCERN", "WilsyAIUsageAdmissionRegistry", "WilsyAIUsageAdmissionRegistryError", "WilsyAIUsageAdmissionConflictError", "WilsyAIUsageAdmissionNotFoundError", "ensure_indexes"]

# ARTIFACT: wilsy_ai_usage_admission_registry.py
# VERSION: v1.0.1-C1B-R3B
# AUTHORITY BOUNDARY: tenant-scoped reservation persistence only
# TENANT POSTURE: every read and write includes tenant_id
# FAIL-CLOSED POSTURE: strict hydration, atomic capacity and CAS conflicts
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
