"""Host-backed M13-P5B certificate for durable append-only observations.

TITLE: WILSY AI Usage Observation Registry Real-Mongo Certificate
VERSION: v1.0.0-M13-P5B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify durable source-evidenced usage observations on the certified
         Mongo replica set without deriving quota or financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_usage_observation_registry_real_mongo.py
COLLABORATION / OWNERSHIP: P5B registry integration certificate; P6 and
                            financial authorities remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M13-P5B certifies durable insert/replay, tenant isolation,
           uniqueness, strict corruption rejection, and session propagation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationConflictError,
    WilsyAIUsageObservationNotFoundError,
    WilsyAIUsageObservationRegistry,
    WilsyAIUsageObservationRegistryError,
    ensure_indexes,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
FP = "a" * 128


def _observation() -> WilsyAIUsageObservation:
    return WilsyAIUsageObservation("tenant-a", "usage-1", "ent-1", 1, FP, "module-a", 1, 10, 20, 0, datetime(2026, 9, 12, 12, tzinfo=timezone.utc), "source-1", FP)


@pytest.fixture()
def bounded_database() -> object:
    client = MongoClient(URI, serverSelectionTimeoutMS=1500)
    database = None
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != "wilsyVendorCertRS" or not hello.get("isWritablePrimary", hello.get("ismaster", False)):
            pytest.skip("certified writable wilsyVendorCertRS unavailable")
    except Exception as error:
        pytest.skip(f"host Mongo unavailable: {type(error).__name__}")
    database = client[f"wilsy_ai_usage_cert_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def test_real_mongo_append_only_replay_and_corruption(bounded_database: object) -> None:
    client, database = bounded_database  # type: ignore[misc]
    collection = database["wilsy_ai_usage_observations"]
    ensure_indexes(collection)
    registry = WilsyAIUsageObservationRegistry(collection)
    with client.start_session() as session:
        session.start_transaction()
        first = registry.create_or_replay(_observation(), idempotency_key="key-1", session=session)
        session.commit_transaction()
    with client.start_session() as session:
        session.start_transaction()
        replay = registry.create_or_replay(_observation(), idempotency_key="key-1", session=session)
        session.commit_transaction()
    assert replay == first and collection.count_documents({"tenant_id": "tenant-a"}) == 1
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(WilsyAIUsageObservationConflictError, match="M13P5B_DIVERGENT_IDEMPOTENCY"):
            registry.create_or_replay(WilsyAIUsageObservation("tenant-a", "usage-1", "ent-1", 1, FP, "module-a", 2, 10, 20, 0, datetime(2026, 9, 12, 12, tzinfo=timezone.utc), "source-1", FP), idempotency_key="key-1", session=session)
        session.abort_transaction()
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(WilsyAIUsageObservationConflictError, match="M13P5B_DIVERGENT_OBSERVATION_IDENTITY"):
            registry.create_or_replay(WilsyAIUsageObservation("tenant-a", "usage-1", "ent-1", 1, FP, "module-a", 2, 10, 20, 0, datetime(2026, 9, 12, 12, tzinfo=timezone.utc), "source-1", FP), idempotency_key="key-2", session=session)
        session.abort_transaction()
    with client.start_session() as session:
        with pytest.raises(WilsyAIUsageObservationNotFoundError): registry.get(tenant_id="tenant-b", usage_observation_id="usage-1", session=session)
    row = collection.find_one({"tenant_id": "tenant-a", "usage_observation_id": "usage-1"})
    assert row is not None and row["source_evidence_fingerprint"] == FP and row["fingerprint"] == first.fingerprint
    collection.update_one({"_id": row["_id"]}, {"$set": {"command_fingerprint": "b" * 128}})
    with client.start_session() as session:
        with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"):
            registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)
    collection.update_one({"_id": row["_id"]}, {"$set": {"command_fingerprint": row["command_fingerprint"]}})
    collection.update_one({"_id": row["_id"]}, {"$set": {"quota": 1}})
    with client.start_session() as session:
        with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"):
            registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)
    collection.update_one({"_id": row["_id"]}, {"$unset": {"quota": 1}})
    collection.update_one({"_id": row["_id"]}, {"$unset": {"source_evidence_reference": 1}})
    with client.start_session() as session:
        with pytest.raises(WilsyAIUsageObservationRegistryError, match="M13P5B_CORRUPT_OBSERVATION"): registry.get(tenant_id="tenant-a", usage_observation_id="usage-1", session=session)
    assert not any(key in row for key in ("tier", "quota", "invoice", "payment", "settlement", "execution", "overage"))


# ARTIFACT: test_wilsy_ai_usage_observation_registry_real_mongo.py
# VERSION: v1.0.0-M13-P5B
# END OF WILSY OS SOVEREIGN ARTIFACT
