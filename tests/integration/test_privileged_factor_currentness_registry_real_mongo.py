"""WILSY OS factor-currentness BSON UTC real-Mongo certificate.

TITLE: Privileged Factor Currentness Registry Real-Mongo Certificate
VERSION: v1.0.0-P3-R3G-C6-B
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Certifies default-client BSON UTC hydration without lifecycle or replay regression.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_privileged_factor_currentness_registry_real_mongo.py
COLLABORATION / OWNERSHIP: P3 factor currentness registry.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0-P3-R3G-C6-B establishes round-trip, corruption, replay, collision, transaction, and index proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic secret-free factor evidence only.
TENANT BOUNDARY: No tenant authority.
AUTHORITY BOUNDARY: Registry certification only; no OTP verification or activation.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from datetime import datetime, timezone
import os, uuid
from typing import Any, Iterator
import pytest
from pymongo import MongoClient
from tools.eos.auth.privileged_channel_currentness import FactorVerificationStatus, InteractiveFactorVerificationEvent
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    COLLECTION, FactorCurrentnessConflictError, FactorCurrentnessPersistenceError,
    PrivilegedFactorVerificationCurrentnessRegistry,
)

URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
NOW = datetime(2026, 10, 14, 12, 0, 0, 123000, tzinfo=timezone.utc)

@pytest.fixture()
def context() -> Iterator[tuple[MongoClient[Any], Any, PrivilegedFactorVerificationCurrentnessRegistry]]:
    client: MongoClient[Any] = MongoClient(URI, serverSelectionTimeoutMS=3000)
    hello = client.admin.command("hello"); assert hello.get("setName") == "wilsyVendorCertRS" and hello.get("isWritablePrimary") is True
    database = client["wilsy_factor_utc_" + uuid.uuid4().hex]; assert database.name != "wilsy"
    registry = PrivilegedFactorVerificationCurrentnessRegistry(database[COLLECTION]); registry.ensure_indexes()
    try: yield client, database[COLLECTION], registry
    finally: client.drop_database(database.name); client.close()

def event(reference: str = "factor-c6-b") -> InteractiveFactorVerificationEvent:
    return InteractiveFactorVerificationEvent(reference, "principal-c6-b", "session-c6-b", 7, NOW, FactorVerificationStatus.VERIFIED)

def test_default_bson_round_trip_exact_replay_and_no_ttl(context) -> None:
    client, collection, registry = context
    with client.start_session() as session:
        with session.start_transaction(): registry.create_or_replay(event(), recorded_at=NOW, session=session)
    raw = collection.find_one({}); assert raw is not None and raw["authenticated_at"].tzinfo is None
    with client.start_session() as session:
        with session.start_transaction():
            hydrated = registry.get(factor_verification_reference="factor-c6-b", session=session)
            assert hydrated == event()
            assert registry.create_or_replay(event(), recorded_at=NOW, session=session) == event()
    assert all("expireAfterSeconds" not in item for item in collection.list_indexes())

def test_malformed_collision_and_transaction_requirements_remain_closed(context) -> None:
    client, collection, registry = context
    with pytest.raises(FactorCurrentnessPersistenceError): registry.create_or_replay(event(), recorded_at=NOW, session=None)
    with client.start_session() as session:
        with session.start_transaction(): registry.create_or_replay(event(), recorded_at=NOW, session=session)
    divergent = InteractiveFactorVerificationEvent("factor-c6-b", "different", "session-c6-b", 7, NOW, FactorVerificationStatus.VERIFIED)
    with pytest.raises(FactorCurrentnessConflictError):
        with client.start_session() as session:
            with session.start_transaction(): registry.create_or_replay(divergent, recorded_at=NOW, session=session)
    collection.update_one({"factor_verification_reference": "factor-c6-b"}, {"$set": {"authenticated_at": "malformed"}})
    with pytest.raises(FactorCurrentnessPersistenceError): registry.get(factor_verification_reference="factor-c6-b")

# ARTIFACT: test_privileged_factor_currentness_registry_real_mongo.py
# VERSION: v1.0.0-P3-R3G-C6-B
# AUTHORITY BOUNDARY: Real-Mongo factor-currentness certification only.
# TENANT POSTURE: No tenant authority.
# FAIL-CLOSED POSTURE: Malformed timestamps, collisions, and absent transactions fail.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
