"""Wilsy OS M13-P6B durable append-only WILSY AI usage-observation registry.

TITLE: WILSY AI Usage Observation Registry
VERSION: v1.2.0-M13-P6B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist source-evidenced P5A observations exactly once while keeping
         all aggregation, quota, billing, execution, and settlement elsewhere.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_usage_observation_registry.py
COLLABORATION / OWNERSHIP: P5A owns immutable fact shape; P5B owns this
                            append-only persistence/replay; P6B owns this
                            bounded retrieval seam for P6A; callers own
                            transactions; Kennel EOS owns financial execution
                            and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.2.0-M13-P6B preserves P5B append/replay authority and adds
           immutable complete-window evidence, including authoritative empty
           windows, for P6A first-use derivation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets, providers, clients, quotas, or money.
TENANT BOUNDARY: Every read/replay query includes explicit tenant_id.
AUTHORITY BOUNDARY: Append-only raw observation evidence only; no mutation,
                    aggregation, entitlement, quota, billing, or execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Persistence errors, duplicate conflicts, and corrupt
                         documents surface as governed failures, never absence.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Any, Final

from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.domain.wilsy_ai_usage_observation import (
    WilsyAIUsageObservation,
    WilsyAIUsageObservationError,
)
from tools.eos.saas.domain.wilsy_ai_usage_window import WilsyAIUsageWindowEvidence

VERSION: Final[str] = "v1.2.0-M13-P6B"
COLLECTION: Final[str] = "wilsy_ai_usage_observations"
OBSERVATION_FIELDS: Final[tuple[str, ...]] = (
    "schema", "observation_version", "tenant_id", "usage_observation_id",
    "entitlement_id", "entitlement_revision", "entitlement_fingerprint",
    "module_id", "request_units", "input_tokens", "output_tokens",
    "automation_actions", "occurred_at", "source_evidence_reference",
    "source_evidence_fingerprint", "fingerprint",
)
_REGISTRY_METADATA_FIELDS: Final[frozenset[str]] = frozenset({"idempotency_key", "command_fingerprint"})
_ALLOWED_PERSISTED_FIELDS: Final[frozenset[str]] = frozenset(OBSERVATION_FIELDS) | _REGISTRY_METADATA_FIELDS | {"_id"}
_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
WRITE_CONCERN = WriteConcern(w="majority", j=True)
READ_CONCERN = ReadConcern("majority")


class WilsyAIUsageObservationRegistryError(ValueError):
    """Base governed P5B persistence error."""


class WilsyAIUsageObservationConflictError(WilsyAIUsageObservationRegistryError):
    """A tenant-scoped identity or idempotency key has divergent evidence."""


class WilsyAIUsageObservationNotFoundError(WilsyAIUsageObservationRegistryError):
    """An exact tenant-scoped observation is absent."""


def _target(collection: Any) -> Any:
    try:
        return collection.with_options(write_concern=WRITE_CONCERN, read_concern=READ_CONCERN)
    except AttributeError:
        return collection


def ensure_indexes(collection: Any) -> None:
    """Create only deterministic append-only lookup indexes."""
    target = _target(collection)
    target.create_index([("tenant_id", 1), ("usage_observation_id", 1)], unique=True, name="wilsy_ai_usage_tenant_observation_unique")
    target.create_index([("tenant_id", 1), ("idempotency_key", 1)], unique=True, name="wilsy_ai_usage_tenant_idempotency_unique")
    target.create_index([("tenant_id", 1), ("occurred_at", 1), ("usage_observation_id", 1)], name="wilsy_ai_usage_tenant_occurred_lookup")
    target.create_index([("tenant_id", 1), ("entitlement_id", 1), ("module_id", 1), ("occurred_at", 1), ("usage_observation_id", 1)], name="wilsy_ai_usage_tenant_entitlement_module_lookup")


def _command_fingerprint(observation: WilsyAIUsageObservation, idempotency_key: str) -> str:
    payload = {"tenant_id": observation.tenant_id, "idempotency_key": idempotency_key, "observation": observation.to_dict()}
    return hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _hydrate(row: Mapping[str, object]) -> WilsyAIUsageObservation:
    try:
        if not isinstance(row, Mapping) or not set(row).issubset(_ALLOWED_PERSISTED_FIELDS):
            raise WilsyAIUsageObservationRegistryError("M13P5B_CORRUPT_OBSERVATION")
        idempotency_key = row["idempotency_key"]
        command_fingerprint = row["command_fingerprint"]
        if not isinstance(idempotency_key, str) or not idempotency_key.strip() or not isinstance(command_fingerprint, str) or len(command_fingerprint) != 128 or not set(command_fingerprint) <= _HEX:
            raise WilsyAIUsageObservationRegistryError("M13P5B_CORRUPT_OBSERVATION")
        payload = {field: row[field] for field in OBSERVATION_FIELDS}
        observation = WilsyAIUsageObservation.from_dict(payload)
        expected = _command_fingerprint(observation, idempotency_key)
        if not hmac.compare_digest(command_fingerprint, expected):
            raise WilsyAIUsageObservationRegistryError("M13P5B_CORRUPT_OBSERVATION")
        return observation
    except (KeyError, TypeError, WilsyAIUsageObservationError) as error:
        raise WilsyAIUsageObservationRegistryError("M13P5B_CORRUPT_OBSERVATION") from error


class WilsyAIUsageObservationRegistry:
    """Append-only caller-session registry for tenant-scoped raw observations."""

    __slots__ = ("_collection",)

    def __init__(self, collection: Any) -> None:
        if collection is None:
            raise WilsyAIUsageObservationRegistryError("M13P5B_COLLECTION_REQUIRED")
        self._collection = _target(collection)

    def create_or_replay(self, observation: WilsyAIUsageObservation, *, idempotency_key: str, session: Any) -> WilsyAIUsageObservation:
        """Append once or return exact replay; caller owns session/transaction."""
        if not isinstance(observation, WilsyAIUsageObservation) or not isinstance(idempotency_key, str) or not idempotency_key.strip() or session is None:
            raise WilsyAIUsageObservationRegistryError("M13P5B_INPUT_INVALID")
        command = _command_fingerprint(observation, idempotency_key)
        try:
            existing = self._collection.find_one({"tenant_id": observation.tenant_id, "idempotency_key": idempotency_key}, session=session)
        except PyMongoError as error:
            raise WilsyAIUsageObservationRegistryError("M13P5B_PERSISTENCE_UNAVAILABLE") from error
        if existing is not None:
            persisted = _hydrate(existing)
            if persisted != observation or existing.get("command_fingerprint") != command:
                raise WilsyAIUsageObservationConflictError("M13P5B_DIVERGENT_IDEMPOTENCY")
            return persisted
        try:
            identity = self._collection.find_one({"tenant_id": observation.tenant_id, "usage_observation_id": observation.usage_observation_id}, session=session)
        except PyMongoError as error:
            raise WilsyAIUsageObservationRegistryError("M13P5B_PERSISTENCE_UNAVAILABLE") from error
        if identity is not None:
            raise WilsyAIUsageObservationConflictError("M13P5B_DIVERGENT_OBSERVATION_IDENTITY")
        document = observation.to_dict()
        document.update({"idempotency_key": idempotency_key, "command_fingerprint": command})
        try:
            self._collection.insert_one(document, session=session)
        except DuplicateKeyError as error:
            raise WilsyAIUsageObservationConflictError("M13P5B_DUPLICATE_OBSERVATION") from error
        except PyMongoError as error:
            raise WilsyAIUsageObservationRegistryError("M13P5B_PERSISTENCE_UNAVAILABLE") from error
        return observation

    def get(self, *, tenant_id: str, usage_observation_id: str, session: Any) -> WilsyAIUsageObservation:
        """Return one exact tenant-scoped observation with strict hydration."""
        if not isinstance(tenant_id, str) or not tenant_id.strip() or not isinstance(usage_observation_id, str) or not usage_observation_id.strip() or session is None:
            raise WilsyAIUsageObservationRegistryError("M13P5B_INPUT_INVALID")
        try:
            row = self._collection.find_one({"tenant_id": tenant_id, "usage_observation_id": usage_observation_id}, session=session)
        except PyMongoError as error:
            raise WilsyAIUsageObservationRegistryError("M13P5B_PERSISTENCE_UNAVAILABLE") from error
        if row is None:
            raise WilsyAIUsageObservationNotFoundError("M13P5B_OBSERVATION_NOT_FOUND")
        return _hydrate(row)

    def get_bounded_for_p6a(
        self,
        *,
        tenant_id: str,
        entitlement_id: str,
        module_id: str,
        expected_entitlement_revision: int,
        expected_entitlement_fingerprint: str,
        as_of: Any,
        session: Any,
    ) -> tuple[WilsyAIUsageObservation, ...]:
        """Read one complete tenant/entitlement/module month snapshot for P6A.

        The caller must have started a Mongo transaction (or equivalent
        snapshot) and retains commit/abort ownership.  The registry queries
        without a timestamp predicate because persisted timestamps are ISO
        evidence strings; every candidate is strictly hydrated and parsed,
        then bounded in UTC through ``as_of``.  Empty means no rows in this
        snapshot, never zero usage or a completeness assertion for P6A.
        """
        if (
            not isinstance(tenant_id, str)
            or not tenant_id.strip()
            or not isinstance(entitlement_id, str)
            or not entitlement_id.strip()
            or not isinstance(module_id, str)
            or not module_id.strip()
            or isinstance(expected_entitlement_revision, bool)
            or not isinstance(expected_entitlement_revision, int)
            or expected_entitlement_revision < 0
            or not isinstance(expected_entitlement_fingerprint, str)
            or len(expected_entitlement_fingerprint) != 128
            or not set(expected_entitlement_fingerprint) <= _HEX
            or not isinstance(as_of, datetime)
            or as_of.tzinfo is None
            or as_of.utcoffset() is None
            or session is None
        ):
            raise WilsyAIUsageObservationRegistryError("M13P6B_INPUT_INVALID")
        active_transaction = getattr(session, "in_transaction", False)
        if callable(active_transaction):
            active_transaction = active_transaction()
        if active_transaction is not True:
            raise WilsyAIUsageObservationRegistryError("M13P6B_TRANSACTION_REQUIRED")
        as_of_utc = as_of.astimezone(timezone.utc)
        month_start = as_of_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        query = {"tenant_id": tenant_id, "entitlement_id": entitlement_id, "module_id": module_id}
        bounded: list[WilsyAIUsageObservation] = []
        seen_ids: set[str] = set()
        seen_fingerprints: set[str] = set()
        try:
            cursor = self._collection.find(query, session=session)
            for row in cursor:
                observation = _hydrate(row)
                if not (month_start <= observation.occurred_at <= as_of_utc) or observation.occurred_at >= month_end:
                    continue
                if (
                    observation.tenant_id != tenant_id
                    or observation.entitlement_id != entitlement_id
                    or observation.module_id != module_id
                    or observation.entitlement_revision != expected_entitlement_revision
                    or observation.entitlement_fingerprint != expected_entitlement_fingerprint
                ):
                    raise WilsyAIUsageObservationRegistryError("M13P6B_BINDING_CONFLICT")
                if observation.usage_observation_id in seen_ids or observation.fingerprint in seen_fingerprints:
                    raise WilsyAIUsageObservationRegistryError("M13P6B_DUPLICATE_EVIDENCE")
                seen_ids.add(observation.usage_observation_id)
                seen_fingerprints.add(observation.fingerprint)
                bounded.append(observation)
        except PyMongoError as error:
            raise WilsyAIUsageObservationRegistryError("M13P6B_PERSISTENCE_UNAVAILABLE") from error
        return tuple(sorted(bounded, key=lambda item: (item.occurred_at, item.usage_observation_id)))

    def get_complete_window_for_p6a(
        self,
        *,
        tenant_id: str,
        entitlement_id: str,
        module_id: str,
        expected_entitlement_revision: int,
        expected_entitlement_fingerprint: str,
        as_of: Any,
        session: Any,
    ) -> WilsyAIUsageWindowEvidence:
        """Return exhaustive complete-window evidence under caller snapshot.

        Every exact binding row is strictly hydrated.  Historical and future
        observations are excluded from this bounded month/as-of result only
        after hydration; malformed rows and in-window binding/duplicate drift
        fail closed.  An empty result is valid proof of no observed usage in
        this registry snapshot, never a synthetic usage fact.
        """
        if (
            not isinstance(tenant_id, str) or not tenant_id.strip()
            or not isinstance(entitlement_id, str) or not entitlement_id.strip()
            or not isinstance(module_id, str) or not module_id.strip()
            or isinstance(expected_entitlement_revision, bool)
            or not isinstance(expected_entitlement_revision, int)
            or expected_entitlement_revision < 0
            or not isinstance(expected_entitlement_fingerprint, str)
            or len(expected_entitlement_fingerprint) != 128
            or not set(expected_entitlement_fingerprint) <= _HEX
            or not isinstance(as_of, datetime)
            or as_of.tzinfo is None or as_of.utcoffset() is None
            or session is None
        ):
            raise WilsyAIUsageObservationRegistryError("M13P6B_INPUT_INVALID")
        active_transaction = getattr(session, "in_transaction", False)
        if callable(active_transaction):
            active_transaction = active_transaction()
        if active_transaction is not True:
            raise WilsyAIUsageObservationRegistryError("M13P6B_TRANSACTION_REQUIRED")
        as_of_utc = as_of.astimezone(timezone.utc)
        month_start = as_of_utc.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        bounded: list[WilsyAIUsageObservation] = []
        seen_ids: set[str] = set()
        seen_fingerprints: set[str] = set()
        try:
            cursor = self._collection.find(
                {"tenant_id": tenant_id, "entitlement_id": entitlement_id, "module_id": module_id},
                session=session,
            )
            for row in cursor:
                observation = _hydrate(row)
                if (
                    observation.tenant_id != tenant_id
                    or observation.entitlement_id != entitlement_id
                    or observation.module_id != module_id
                ):
                    raise WilsyAIUsageObservationRegistryError("M13P6B_BINDING_CONFLICT")
                if observation.occurred_at < month_start or observation.occurred_at > as_of_utc:
                    continue
                if (
                    observation.entitlement_revision != expected_entitlement_revision
                    or observation.entitlement_fingerprint != expected_entitlement_fingerprint
                ):
                    raise WilsyAIUsageObservationRegistryError("M13P6B_BINDING_CONFLICT")
                if observation.usage_observation_id in seen_ids or observation.fingerprint in seen_fingerprints:
                    raise WilsyAIUsageObservationRegistryError("M13P6B_DUPLICATE_EVIDENCE")
                seen_ids.add(observation.usage_observation_id)
                seen_fingerprints.add(observation.fingerprint)
                bounded.append(observation)
        except PyMongoError as error:
            raise WilsyAIUsageObservationRegistryError("M13P6B_PERSISTENCE_UNAVAILABLE") from error
        ordered = tuple(sorted(bounded, key=lambda item: (item.occurred_at, item.usage_observation_id)))
        return WilsyAIUsageWindowEvidence(
            tenant_id=tenant_id,
            entitlement_id=entitlement_id,
            module_id=module_id,
            entitlement_revision=expected_entitlement_revision,
            entitlement_fingerprint=expected_entitlement_fingerprint,
            as_of=as_of_utc,
            window_start=month_start,
            window_end=as_of_utc,
            observation_count=len(ordered),
            observation_fingerprints=tuple(item.fingerprint for item in ordered),
            observations=ordered,
        )


__all__ = ["COLLECTION", "OBSERVATION_FIELDS", "VERSION", "WRITE_CONCERN", "READ_CONCERN", "WilsyAIUsageObservationRegistry", "WilsyAIUsageObservationRegistryError", "WilsyAIUsageObservationConflictError", "WilsyAIUsageObservationNotFoundError", "ensure_indexes"]

# ARTIFACT: wilsy_ai_usage_observation_registry.py
# VERSION: v1.2.0-M13-P6B
# AUTHORITY BOUNDARY: append-only raw usage-observation persistence only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
