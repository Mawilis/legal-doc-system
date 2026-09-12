"""Direct P5B certificate for append-only usage-observation persistence.

TITLE: WILSY AI Usage Observation Registry Direct Certificate
VERSION: v1.0.0-M13-P5B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove tenant-scoped idempotent append-only persistence without
         granting quota, billing, execution, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_usage_observation_registry.py
COLLABORATION / OWNERSHIP: Direct certificate for the P5B registry owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P5B certifies replay, divergence, isolation,
           corruption handling, and caller transaction ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationConflictError,
    WilsyAIUsageObservationNotFoundError,
    WilsyAIUsageObservationRegistry,
    WilsyAIUsageObservationRegistryError,
    ensure_indexes,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation

FP = "a" * 128
NOW = datetime(2026, 9, 12, tzinfo=timezone.utc)


class Result:
    def __init__(self, matched_count: int = 0) -> None: self.matched_count = matched_count


class Collection:
    def __init__(self) -> None: self.rows: list[dict[str, Any]] = []; self.indexes: list[Any] = []
    def with_options(self, **_: Any) -> "Collection": return self
    def create_index(self, keys: Any, **kwargs: Any) -> str: self.indexes.append((keys, kwargs)); return str(kwargs["name"])
    def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None:
        assert session is not None
        return next((row for row in self.rows if all(row.get(k) == v for k, v in query.items())), None)
    def insert_one(self, document: dict[str, Any], *, session: Any) -> None:
        assert session is not None
        if any(row.get("tenant_id") == document["tenant_id"] and row.get("usage_observation_id") == document["usage_observation_id"] for row in self.rows): raise DuplicateKeyError("identity")
        if any(row.get("tenant_id") == document["tenant_id"] and row.get("idempotency_key") == document["idempotency_key"] for row in self.rows): raise DuplicateKeyError("key")
        self.rows.append(dict(document))


def observation(tenant: str = "tenant-a", identifier: str = "usage-1", units: int = 1) -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation(tenant, identifier, "ent-1", 1, FP, "module-a", units, 10, 20, 0, NOW, "source-1", FP)


def test_exact_create_replay_and_indexes() -> None:
    collection, session = Collection(), object(); ensure_indexes(collection); registry = WilsyAIUsageObservationRegistry(collection)
    first = registry.create_or_replay(observation(), idempotency_key="key-1", session=session)
    assert registry.create_or_replay(observation(), idempotency_key="key-1", session=session) == first
    assert len(collection.rows) == 1 and len(collection.indexes) == 3


def test_divergent_idempotency_and_identity_fail_closed() -> None:
    collection, session = Collection(), object(); registry = WilsyAIUsageObservationRegistry(collection); registry.create_or_replay(observation(), idempotency_key="key-1", session=session)
    with pytest.raises(WilsyAIUsageObservationConflictError): registry.create_or_replay(observation(units=2), idempotency_key="key-1", session=session)
    with pytest.raises(WilsyAIUsageObservationConflictError): registry.create_or_replay(observation(identifier="usage-1", units=2), idempotency_key="key-2", session=session)


def test_tenant_isolation_and_corruption_are_not_absence() -> None:
    collection, session = Collection(), object(); registry = WilsyAIUsageObservationRegistry(collection); registry.create_or_replay(observation(), idempotency_key="key-1", session=session)
    with pytest.raises(WilsyAIUsageObservationNotFoundError): registry.get(tenant_id="tenant-b", usage_observation_id="usage-1", session=session)
    del collection.rows[0]["source_evidence_reference"]
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"): registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)


def test_extra_authority_fields_and_bad_registry_metadata_are_corruption() -> None:
    collection, session = Collection(), object(); registry = WilsyAIUsageObservationRegistry(collection); registry.create_or_replay(observation(), idempotency_key="key-1", session=session)
    collection.rows[0]["quota"] = 1
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"): registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)
    del collection.rows[0]["quota"]; collection.rows[0]["overage"] = 1
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"): registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)
    del collection.rows[0]["overage"]; collection.rows[0]["command_fingerprint"] = "bad"
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"): registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)


def test_mongo_id_metadata_is_allowed() -> None:
    collection, session = Collection(), object(); registry = WilsyAIUsageObservationRegistry(collection); created = registry.create_or_replay(observation(), idempotency_key="key-1", session=session)
    collection.rows[0]["_id"] = "mongo-id"
    assert registry.get(tenant_id="tenant-a", usage_observation_id=created.usage_observation_id, session=session) == created


def test_persistence_error_is_governed() -> None:
    class Broken(Collection):
        def insert_one(self, document: dict[str, Any], *, session: Any) -> None: raise PyMongoError("offline")
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="PERSISTENCE_UNAVAILABLE"): WilsyAIUsageObservationRegistry(Broken()).create_or_replay(observation(), idempotency_key="key", session=object())


def test_idempotency_lookup_error_is_governed() -> None:
    class BrokenLookup(Collection):
        def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None: raise PyMongoError("idempotency lookup offline")
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_PERSISTENCE_UNAVAILABLE"): WilsyAIUsageObservationRegistry(BrokenLookup()).create_or_replay(observation(), idempotency_key="key", session=object())


def test_identity_lookup_error_is_governed() -> None:
    class IdentityLookupFailure(Collection):
        def __init__(self) -> None: super().__init__(); self.calls = 0
        def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None:
            self.calls += 1
            if self.calls == 2: raise PyMongoError("identity lookup offline")
            return None
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_PERSISTENCE_UNAVAILABLE"): WilsyAIUsageObservationRegistry(IdentityLookupFailure()).create_or_replay(observation(), idempotency_key="key", session=object())


def test_conflict_class_is_not_rewritten_as_persistence_error() -> None:
    collection, session = Collection(), object(); registry = WilsyAIUsageObservationRegistry(collection); registry.create_or_replay(observation(), idempotency_key="key", session=session)
    with pytest.raises(WilsyAIUsageObservationConflictError, match="M13P5B_DIVERGENT_IDEMPOTENCY"): registry.create_or_replay(observation(units=2), idempotency_key="key", session=session)


def test_wrong_well_formed_command_fingerprint_is_corruption_on_get_and_replay() -> None:
    collection, session = Collection(), object(); registry = WilsyAIUsageObservationRegistry(collection); registry.create_or_replay(observation(), idempotency_key="key", session=session)
    collection.rows[0]["command_fingerprint"] = "b" * 128
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"): registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)
    with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"): registry.create_or_replay(observation(units=2), idempotency_key="key", session=session)


def test_append_only_and_caller_transaction_ownership() -> None:
    assert not any(name in dir(WilsyAIUsageObservationRegistry) for name in ("update", "delete", "transition", "start_transaction", "commit_transaction", "abort_transaction"))
