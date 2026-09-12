"""Wilsy OS M13-P5B durable append-only WILSY AI usage-observation registry.

TITLE: WILSY AI Usage Observation Registry
VERSION: v1.0.0-M13-P5B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist source-evidenced P5A observations exactly once while keeping
         all aggregation, quota, billing, execution, and settlement elsewhere.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/wilsy_ai_usage_observation_registry.py
COLLABORATION / OWNERSHIP: P5A owns immutable fact shape; P5B owns this
                            append-only persistence/replay; future P6 owns
                            derivation; callers own transactions; Kennel EOS
                            owns financial execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P5B establishes tenant-scoped identity/idempotency
           indexes, strict hydration, and caller-session persistence.
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

VERSION: Final[str] = "v1.0.0-M13-P5B"
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


__all__ = ["COLLECTION", "OBSERVATION_FIELDS", "VERSION", "WRITE_CONCERN", "READ_CONCERN", "WilsyAIUsageObservationRegistry", "WilsyAIUsageObservationRegistryError", "WilsyAIUsageObservationConflictError", "WilsyAIUsageObservationNotFoundError", "ensure_indexes"]

# ARTIFACT: wilsy_ai_usage_observation_registry.py
# VERSION: v1.0.0-M13-P5B
# AUTHORITY BOUNDARY: append-only raw usage-observation persistence only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
