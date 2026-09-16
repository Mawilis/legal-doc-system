"""Host-backed M13-P6B bounded retrieval certificate.

TITLE: WILSY AI Usage Observation P6B Retrieval Real-Mongo Certificate
VERSION: v1.1.0-M13-P6B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify exhaustive caller-transaction observation retrieval and its
         frozen P6A composition on the certified local Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_usage_observation_registry_p6b_real_mongo.py
COLLABORATION / OWNERSHIP: P6B integration certificate; P5B persists raw
                            facts, P6A derives capacity, and Kennel EOS owns
                            financial execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.1.0-M13-P6B adds explicit full first-use limits and a genuine
           nonempty complete-window capacity/provenance transition while
           preserving bounded retrieval, tenant/binding isolation, strict
           corruption handling, ordering, and caller-owned transactions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient

import tools.eos.saas.billing.wilsy_ai_usage_observation_registry as registry_module
from tools.eos.saas.billing.wilsy_ai_usage_capacity import derive_wilsy_ai_usage_capacity as _derive_capacity
from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationRegistry,
    WilsyAIUsageObservationRegistryError,
    ensure_indexes,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.domain.wilsy_ai_usage_window import WilsyAIUsageWindowEvidence


URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
FP = "a" * 128
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def _entitlement() -> WilsyAIEntitlement:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    pending = WilsyAIEntitlement(
        tenant_id="tenant-a", entitlement_id="ent-a", module_id="module-a", module_name="Inbox",
        tier=WilsyAITier.STARTER, policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE, source_requirements=("records",),
        capability_grants=("ai.summary",), source_readiness_evidence_reference="ready",
        source_readiness_evidence_fingerprint=FP,
    )
    return pending.transition(WilsyAIEntitlementState.ACTIVE, expected_revision=0,
                              evidence_reference="active", evidence_fingerprint=FP,
                              occurred_at=datetime(2026, 9, 1, tzinfo=timezone.utc))


def _observation(ent: WilsyAIEntitlement, ident: str, when: datetime, *, tenant: str | None = None,
                 module: str | None = None, revision: int | None = None,
                 entitlement_fp: str | None = None) -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation(
        tenant or ent.tenant_id, ident, ent.entitlement_id, ent.lifecycle_revision if revision is None else revision,
        ent.fingerprint if entitlement_fp is None else entitlement_fp, module or ent.module_id,
        2, 10, 20, 1, when, f"source-{ident}", FP,
    )


def _row(item: WilsyAIUsageObservation, key: str) -> dict[str, object]:
    payload = item.to_dict()
    payload.update(idempotency_key=key, command_fingerprint=registry_module._command_fingerprint(item, key))
    return payload


@pytest.fixture()
def bounded_database() -> object:
    client = MongoClient(URI, serverSelectionTimeoutMS=1500)
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
            pytest.skip("certified writable wilsyVendorCertRS unavailable")
    except Exception as error:
        pytest.skip(f"host Mongo unavailable: {type(error).__name__}")
    database = client[f"wilsy_ai_usage_p6b_cert_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def _insert(registry: WilsyAIUsageObservationRegistry, client: MongoClient, item: WilsyAIUsageObservation, key: str) -> None:
    with client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(item, idempotency_key=key, session=session)
        session.commit_transaction()


def test_real_mongo_bounded_retrieval_and_p6a_chain(bounded_database: object) -> None:
    client, database = bounded_database  # type: ignore[misc]
    ent = _entitlement()
    collection = database["wilsy_ai_usage_observations"]
    ensure_indexes(collection)
    registry = WilsyAIUsageObservationRegistry(collection)
    _insert(registry, client, _observation(ent, "late", datetime(2026, 9, 12, 11, tzinfo=timezone.utc)), "late")
    _insert(registry, client, _observation(ent, "early", datetime(2026, 9, 1, tzinfo=timezone.utc)), "early")
    _insert(registry, client, _observation(ent, "prior", datetime(2026, 8, 31, 23, tzinfo=timezone.utc)), "prior")
    _insert(registry, client, _observation(ent, "future", datetime(2026, 9, 12, 13, tzinfo=timezone.utc)), "future")
    _insert(registry, client, _observation(ent, "other-tenant", datetime(2026, 9, 5, tzinfo=timezone.utc), tenant="tenant-b"), "other-tenant")
    _insert(registry, client, _observation(ent, "other-module", datetime(2026, 9, 5, tzinfo=timezone.utc), module="module-b"), "other-module")
    with client.start_session() as session:
        session.start_transaction()
        bounded = registry.get_bounded_for_p6a(
            tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
            expected_entitlement_revision=ent.lifecycle_revision, expected_entitlement_fingerprint=ent.fingerprint,
            as_of=AS_OF, session=session,
        )
        assert session.in_transaction is True
        assert [item.usage_observation_id for item in bounded] == ["early", "late"]
        assert bounded[0].source_evidence_fingerprint == FP
        window = WilsyAIUsageWindowEvidence(
            tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
            entitlement_revision=ent.lifecycle_revision, entitlement_fingerprint=ent.fingerprint,
            as_of=AS_OF, window_start=datetime(2026, 9, 1, tzinfo=timezone.utc), window_end=AS_OF,
            observation_count=len(bounded), observation_fingerprints=tuple(item.fingerprint for item in bounded),
            observations=bounded,
        )
        capacity = _derive_capacity(entitlement=ent, usage_window=window, as_of=AS_OF)
        assert capacity.daily_consumed_request_units == 2 and capacity.monthly_consumed_automation_actions == 2
        session.abort_transaction()

    first_use_collection = database["wilsy_ai_usage_p6b_first_use"]
    ensure_indexes(first_use_collection)
    first_use_registry = WilsyAIUsageObservationRegistry(first_use_collection)
    policy = get_wilsy_ai_commercial_policy(ent.tier)
    binding_filter = {
        "tenant_id": ent.tenant_id,
        "entitlement_id": ent.entitlement_id,
        "module_id": ent.module_id,
        "entitlement_revision": ent.lifecycle_revision,
        "entitlement_fingerprint": ent.fingerprint,
    }
    with client.start_session() as session:
        session.start_transaction()
        empty_window = first_use_registry.get_complete_window_for_p6a(
            tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
            expected_entitlement_revision=ent.lifecycle_revision,
            expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session,
        )
        assert empty_window.observation_count == 0 and empty_window.observations == ()
        empty_capacity = _derive_capacity(entitlement=ent, usage_window=empty_window, as_of=AS_OF)
        assert empty_capacity.daily_consumed_request_units == 0
        assert empty_capacity.monthly_consumed_automation_actions == 0
        assert empty_capacity.daily_remaining_request_units == policy.daily_request_limit
        assert empty_capacity.monthly_remaining_automation_actions == policy.monthly_automation_limit
        assert empty_capacity.daily_exhausted is False
        assert empty_capacity.monthly_exhausted is False
        assert empty_capacity.usage_window_fingerprint == empty_window.fingerprint
        assert first_use_collection.count_documents(binding_filter) == 0
        session.abort_transaction()
        assert session.in_transaction is False

    genuine_observation = _observation(ent, "genuine", datetime(2026, 9, 12, 10, tzinfo=timezone.utc))
    _insert(first_use_registry, client, genuine_observation, "genuine")
    assert first_use_collection.count_documents(binding_filter) == 1

    with client.start_session() as session:
        session.start_transaction()
        nonempty_window = first_use_registry.get_complete_window_for_p6a(
            tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id,
            expected_entitlement_revision=ent.lifecycle_revision,
            expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session,
        )
        assert nonempty_window.observation_count == 1
        assert len(nonempty_window.observations) == 1
        assert nonempty_window.observations[0].usage_observation_id == genuine_observation.usage_observation_id
        assert nonempty_window.observations[0].fingerprint == genuine_observation.fingerprint
        assert nonempty_window.fingerprint != empty_window.fingerprint
        nonempty_capacity = _derive_capacity(entitlement=ent, usage_window=nonempty_window, as_of=AS_OF)
        assert nonempty_capacity.usage_window_fingerprint == nonempty_window.fingerprint
        assert nonempty_capacity.usage_window_fingerprint != empty_capacity.usage_window_fingerprint
        assert nonempty_capacity.daily_consumed_request_units == genuine_observation.request_units
        assert nonempty_capacity.monthly_consumed_automation_actions == genuine_observation.automation_actions
        assert nonempty_capacity.daily_remaining_request_units == policy.daily_request_limit - genuine_observation.request_units
        assert nonempty_capacity.monthly_remaining_automation_actions == policy.monthly_automation_limit - genuine_observation.automation_actions
        assert nonempty_capacity.fingerprint != empty_capacity.fingerprint
        session.abort_transaction()
        assert session.in_transaction is False

    assert first_use_collection.count_documents(binding_filter) == 1
    assert collection.count_documents({"tenant_id": "tenant-a"}) == 5

    conflict_collection = database["wilsy_ai_usage_p6b_conflict"]
    ensure_indexes(conflict_collection)
    conflict_registry = WilsyAIUsageObservationRegistry(conflict_collection)
    _insert(conflict_registry, client, _observation(ent, "conflict", AS_OF, revision=2, entitlement_fp="b" * 128), "conflict")
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_BINDING_CONFLICT"):
            conflict_registry.get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=ent.lifecycle_revision, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session)
        session.abort_transaction()

    corrupt_collection = database["wilsy_ai_usage_p6b_corrupt"]
    ensure_indexes(corrupt_collection)
    corrupt_registry = WilsyAIUsageObservationRegistry(corrupt_collection)
    _insert(corrupt_registry, client, _observation(ent, "corrupt", AS_OF), "corrupt")
    corrupt_collection.update_one({"usage_observation_id": "corrupt"}, {"$set": {"source_evidence_reference": "changed"}})
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"):
            corrupt_registry.get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=ent.lifecycle_revision, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session)
        session.abort_transaction()

    empty_collection = database["wilsy_ai_usage_p6b_empty"]
    ensure_indexes(empty_collection)
    empty_registry = WilsyAIUsageObservationRegistry(empty_collection)
    _insert(empty_registry, client, _observation(ent, "old", datetime(2026, 8, 31, tzinfo=timezone.utc)), "old")
    with client.start_session() as session:
        session.start_transaction()
        assert empty_registry.get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=ent.lifecycle_revision, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session) == ()
        session.abort_transaction()

    malformed_collection = database["wilsy_ai_usage_p6b_malformed"]
    malformed_registry = WilsyAIUsageObservationRegistry(malformed_collection)
    malformed_collection.insert_one(_row(_observation(ent, "malformed", AS_OF), "malformed"))
    malformed_collection.update_one({"usage_observation_id": "malformed"}, {"$set": {"occurred_at": "not-a-timestamp"}})
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"):
            malformed_registry.get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=ent.lifecycle_revision, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session)
        session.abort_transaction()

    duplicate_collection = database["wilsy_ai_usage_p6b_duplicate"]
    duplicate = _row(_observation(ent, "duplicate", AS_OF), "duplicate")
    duplicate_collection.insert_one(duplicate)
    duplicate_copy = dict(duplicate)
    duplicate_copy.pop("_id", None)
    duplicate_collection.insert_one(duplicate_copy)
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P6B_DUPLICATE_EVIDENCE"):
            WilsyAIUsageObservationRegistry(duplicate_collection).get_bounded_for_p6a(tenant_id=ent.tenant_id, entitlement_id=ent.entitlement_id, module_id=ent.module_id, expected_entitlement_revision=ent.lifecycle_revision, expected_entitlement_fingerprint=ent.fingerprint, as_of=AS_OF, session=session)
        session.abort_transaction()


# ARTIFACT: test_wilsy_ai_usage_observation_registry_p6b_real_mongo.py
# VERSION: v1.1.0-M13-P6B
# AUTHORITY BOUNDARY: bounded raw observation retrieval only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
