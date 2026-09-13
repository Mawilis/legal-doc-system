"""Host-backed M13-P6C certificate for capacity runtime composition.

TITLE: WILSY AI Usage Capacity Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-M13-P6C
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove one caller-started Mongo transaction composes P4 entitlement
         truth, P6B observations, and unchanged P6A capacity derivation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_usage_capacity_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for the P6C composition owner;
                            Kennel EOS remains financial execution/settlement
                            authority.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.0.0-M13-P6C certifies real-Mongo same-session composition,
           deterministic capacity, and caller-owned transaction lifecycle.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Local replica-set evidence only; no providers,
                             secrets, clients, invoices, or financial actions.
TENANT BOUNDARY: Isolated UUID database and explicit tenant-scoped registry
                 calls are required for every operation.
AUTHORITY BOUNDARY: Runtime composition and read/derive evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
"""
import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    WilsyAIEntitlementRegistry,
    ensure_indexes as ensure_entitlement_indexes,
)
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import (
    WilsyAIUsageCapacityOrchestrator,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationRegistry,
    ensure_indexes as ensure_observation_indexes,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import (
    WilsyAIEntitlement,
    WilsyAIEntitlementState,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation


URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
FP = "a" * 128
TENANT = "tenant-p6c-real"
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)
ACTIVATED_AT = datetime(2026, 9, 1, tzinfo=timezone.utc)


def _pending() -> WilsyAIEntitlement:
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    return WilsyAIEntitlement(
        tenant_id=TENANT,
        entitlement_id="entitlement-p6c-real",
        module_id="module-p6c-real",
        module_name="Owner Inbox",
        tier=WilsyAITier.STARTER,
        policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE,
        source_requirements=("records",),
        capability_grants=("ai.summary",),
        source_readiness_evidence_reference="ready",
        source_readiness_evidence_fingerprint=FP,
    )


def _observation(entitlement: WilsyAIEntitlement) -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation(
        entitlement.tenant_id,
        "usage-p6c-real",
        entitlement.entitlement_id,
        entitlement.lifecycle_revision,
        entitlement.fingerprint,
        entitlement.module_id,
        3,
        10,
        20,
        2,
        datetime(2026, 9, 12, 11, tzinfo=timezone.utc),
        "source-p6c-real",
        FP,
    )


@pytest.fixture()
def mongo_database() -> object:
    client = MongoClient(URI, serverSelectionTimeoutMS=1500)
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get(
            "isWritablePrimary", hello.get("ismaster", False)
        ):
            pytest.skip("required wilsyVendorCertRS writable replica set unavailable")
    except Exception as error:
        pytest.skip(f"host Mongo unavailable: {type(error).__name__}")
    database = client[f"wilsy_ai_capacity_p6c_cert_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def test_real_mongo_same_transaction_composes_p4_p6b_and_p6a(
    mongo_database: object,
) -> None:
    client, database = mongo_database  # type: ignore[misc]
    entitlement_collection = database["wilsy_ai_entitlements"]
    observation_collection = database["wilsy_ai_usage_observations"]
    ensure_entitlement_indexes(entitlement_collection)
    ensure_observation_indexes(observation_collection)
    entitlement_registry = WilsyAIEntitlementRegistry(entitlement_collection)
    observation_registry = WilsyAIUsageObservationRegistry(observation_collection)
    orchestrator = WilsyAIUsageCapacityOrchestrator(
        entitlement_registry=entitlement_registry,
        observation_registry=observation_registry,
    )
    pending = _pending()
    with client.start_session() as session:
        session.start_transaction()
        active = entitlement_registry.create_or_replay(
            pending,
            idempotency_key="entitlement-p6c-real",
            session=session,
        )
        active = entitlement_registry.transition(
            tenant_id=TENANT,
            entitlement_id=active.entitlement_id,
            target_state=WilsyAIEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activation-p6c-real",
            evidence_fingerprint=FP,
            occurred_at=ACTIVATED_AT,
            session=session,
        )
        observation_registry.create_or_replay(
            _observation(active),
            idempotency_key="usage-p6c-real",
            session=session,
        )
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        first = orchestrator.derive_capacity(
            tenant_id=TENANT,
            entitlement_id="entitlement-p6c-real",
            as_of=AS_OF,
            session=session,
        )
        assert first.daily_consumed_request_units == 3
        assert first.monthly_consumed_automation_actions == 2
        assert session.in_transaction is True
        session.commit_transaction()

    with client.start_session() as session:
        session.start_transaction()
        replay = orchestrator.derive_capacity(
            tenant_id=TENANT,
            entitlement_id="entitlement-p6c-real",
            as_of=AS_OF,
            session=session,
        )
        assert replay == first
        assert session.in_transaction is True
        session.abort_transaction()

    stored_entitlement = entitlement_collection.find_one({"tenant_id": TENANT})
    stored_observation = observation_collection.find_one({"tenant_id": TENANT})
    assert stored_entitlement is not None and stored_observation is not None
    assert not any(
        field in stored_observation
        for field in ("quota", "invoice", "payment", "execution", "settlement", "usage_total")
    )


# ARTIFACT: test_wilsy_ai_usage_capacity_orchestrator_real_mongo.py
# VERSION: v1.0.0-M13-P6C
# AUTHORITY BOUNDARY: host-backed P4/P6B/P6A composition certificate only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
