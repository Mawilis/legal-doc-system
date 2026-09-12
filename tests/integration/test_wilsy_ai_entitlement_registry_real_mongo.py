"""Host-backed M13-P4 certificate for durable WILSY AI entitlement evidence.

TITLE: WILSY AI Entitlement Registry Real-Mongo Certificate
VERSION: v1.0.0-M13-P4
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify tenant-scoped durable entitlement persistence on the local
         Mongo replica set without introducing financial or execution truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_entitlement_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Integration certificate for the P4 registry;
                            Kennel EOS remains financial authority.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P4 certifies real-Mongo replay, isolation, uniqueness,
           corruption rejection, and caller-owned session behavior.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import WilsyAIEntitlementRegistry, ensure_indexes
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
FP = "a" * 128


def _value(tenant: str, module: str = "module-a") -> WilsyAIEntitlement:
    return WilsyAIEntitlement(tenant, f"ent-{tenant}-{module}", module, "Owner Inbox", WilsyAITier.STARTER, get_wilsy_ai_commercial_policy(WilsyAITier.STARTER).policy_fingerprint, WilsyAIEntitlementState.PENDING_SOURCE, ("records",), ("ai.summary",), "ready", FP)


@pytest.fixture()
def mongo_database() -> object:
    client = MongoClient(URI, serverSelectionTimeoutMS=1500)
    database = None
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
            pytest.skip("required wilsyVendorCertRS writable replica set unavailable")
        database = client[f"wilsy_ai_entitlement_cert_{uuid4().hex}"]
        yield client, database
    except Exception as error:
        pytest.skip(f"host Mongo unavailable: {type(error).__name__}")
    finally:
        try:
            if database is not None:
                database.drop()
        except Exception:
            pass
        client.close()


def test_real_mongo_entitlement_authority(mongo_database: object) -> None:
    client, database = mongo_database  # type: ignore[misc]
    collection = database["wilsy_ai_entitlements"]
    ensure_indexes(collection)
    registry = WilsyAIEntitlementRegistry(collection)
    with client.start_session() as session:
        session.start_transaction()
        first = registry.create_or_replay(_value("tenant-a"), idempotency_key="k1", session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        active = registry.transition(tenant_id="tenant-a", entitlement_id=first.entitlement_id, target_state=WilsyAIEntitlementState.ACTIVE, expected_revision=0, evidence_reference="activation", evidence_fingerprint=FP, occurred_at=datetime.now(timezone.utc), session=session)
        session.commit_transaction()
    assert active.lifecycle_revision == 1 and active.lifecycle_state is WilsyAIEntitlementState.ACTIVE
    with client.start_session() as session:
        session.start_transaction()
        suspended = registry.transition(tenant_id="tenant-a", entitlement_id=first.entitlement_id, target_state=WilsyAIEntitlementState.SUSPENDED, expected_revision=1, evidence_reference="suspension", evidence_fingerprint=FP, occurred_at=datetime.now(timezone.utc), session=session)
        session.commit_transaction()
    assert suspended.lifecycle_revision == 2
    with client.start_session() as session:
        session.start_transaction()
        replay = registry.create_or_replay(_value("tenant-a"), idempotency_key="k1", session=session)
        session.commit_transaction()
    assert replay.lifecycle_revision == 2 and collection.count_documents({"tenant_id": "tenant-a"}) == 1
    assert replay.policy_fingerprint == get_wilsy_ai_commercial_policy(WilsyAITier.STARTER).policy_fingerprint
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(Exception): registry.create_or_replay(_value("tenant-a", "module-b"), idempotency_key="k1", session=session)
        session.abort_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(Exception): registry.transition(tenant_id="tenant-a", entitlement_id=first.entitlement_id, target_state=WilsyAIEntitlementState.ACTIVE, expected_revision=1, evidence_reference="stale", evidence_fingerprint=FP, occurred_at=datetime.now(timezone.utc), session=session)
        session.abort_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(Exception): registry.get(tenant_id="tenant-b", entitlement_id=first.entitlement_id, session=session)
        session.abort_transaction()
    raw = collection.find_one({"tenant_id": "tenant-a", "idempotency_key": "k1"})
    assert raw is not None
    collection.update_one({"_id": raw["_id"]}, {"$set": {"fingerprint": "f" * 128}})
    with client.start_session() as session:
        with pytest.raises(Exception): registry.get(tenant_id="tenant-a", entitlement_id=first.entitlement_id, session=session)
    collection.update_one({"_id": raw["_id"]}, {"$unset": {"policy_fingerprint": 1}})
    with client.start_session() as session:
        with pytest.raises(Exception, match="M13P4_CORRUPT_ENTITLEMENT"): registry.get(tenant_id="tenant-a", entitlement_id=first.entitlement_id, session=session)
    assert not any(key in raw for key in ("invoice", "payment", "settlement", "usage", "execution", "paid"))


# ARTIFACT: test_wilsy_ai_entitlement_registry_real_mongo.py
# VERSION: v1.0.0-M13-P4
# END OF WILSY OS SOVEREIGN ARTIFACT
