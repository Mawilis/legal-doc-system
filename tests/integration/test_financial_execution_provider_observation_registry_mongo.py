# -*- coding: utf-8 -*-
"""Real-Mongo certification for provider-neutral observation persistence.

TITLE: Financial Execution Provider Observation Registry Mongo Certification
VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION-REGISTRY-MONGO-CERT
PURPOSE: Certify immutable tenant-scoped replay, corruption, concurrency, and transaction behavior.
CERTIFICATION AUTHORITY / SCOPE: Real MongoDB evidence for the observation registry only.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
LAST UPDATED: 2026-08-28
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY / PRIVACY POSTURE: no raw payloads, credentials, settlement, or truth mutation.
TENANT BOUNDARY: every fixture and query is tenant-scoped.
TRUTH BOUNDARY: observation persistence is distinct from attempt, execution truth, and settlement.
CHANGELOG: v1.0.0 establishes real-Mongo persistence certification; no financial semantic change.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os, uuid
from threading import Barrier
from typing import Any, cast
import pytest
from pymongo import MongoClient
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
)
from tools.eos.kennel.registry.financial_execution_provider_observation_registry import (
    COLLECTION,
    FinancialExecutionProviderObservationCreateConflictError,
    FinancialExecutionProviderObservationPersistedRecordInvalidError,
    FinancialExecutionProviderObservationRegistry,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture()
def mongo_db():
    """Create isolated Mongo state and clean it after each certification test."""
    uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    db = client["observation_cert_" + uuid.uuid4().hex]
    FinancialExecutionProviderObservationRegistry.ensure_indexes(db[COLLECTION])
    try:
        yield db
    finally:
        client.drop_database(db.name)
        client.close()


def make_observation(**changes: Any) -> FinancialExecutionProviderObservation:
    """Build a valid tenant-bound observation with deterministic baseline time."""
    values = dict(
        observation_id="obs-" + uuid.uuid4().hex,
        tenant_id="tenant",
        execution_attempt_id="attempt-" + uuid.uuid4().hex,
        provider_name="PayShap",
        observation_status=ObservationStatus.PENDING,
        observed_at=NOW,
    )
    values.update(changes)
    return FinancialExecutionProviderObservation(**cast(Any, values))


def test_indexes_create_and_round_trip(mongo_db):
    """Certify index authority and immutable create/get round-trip."""
    c = mongo_db[COLLECTION]
    names = {x["name"] for x in c.list_indexes()}
    assert {
        "tenant_observation_identity_unique",
        "tenant_attempt_observation_timeline",
        "tenant_provider_request_observations",
        "tenant_provider_execution_observations",
        "tenant_observation_status_timeline",
    } <= names
    o = make_observation()
    assert FinancialExecutionProviderObservationRegistry.create(o, c)[0] == "CREATED"
    assert (
        FinancialExecutionProviderObservationRegistry.get(
            o.tenant_id, o.observation_id, c
        )
        == o
    )


def test_exact_replay_and_divergent_conflict(mongo_db):
    """Certify exact replay and divergent same-ID conflict classification."""
    c = mongo_db[COLLECTION]
    o = make_observation(provider_request_reference="r")
    FinancialExecutionProviderObservationRegistry.create(o, c)
    assert (
        FinancialExecutionProviderObservationRegistry.create(o, c)[0]
        == "IDEMPOTENT_REPLAY"
    )
    with pytest.raises(FinancialExecutionProviderObservationCreateConflictError):
        FinancialExecutionProviderObservationRegistry.create(
            FinancialExecutionProviderObservation(
                **{**o.__dict__, "provider_request_reference": "other"}
            ),
            c,
        )


def test_tenant_and_attempt_isolation_ordering(mongo_db):
    """Certify tenant isolation and deterministic attempt ordering."""
    c = mongo_db[COLLECTION]
    a = make_observation(observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    b = make_observation(
        execution_attempt_id=a.execution_attempt_id,
        observed_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    FinancialExecutionProviderObservationRegistry.create(a, c)
    FinancialExecutionProviderObservationRegistry.create(b, c)
    assert [
        x.observation_id
        for x in FinancialExecutionProviderObservationRegistry.list_for_attempt(
            "tenant", a.execution_attempt_id, 10, c
        )
    ] == [a.observation_id, b.observation_id]
    assert (
        FinancialExecutionProviderObservationRegistry.list_for_attempt(
            "other", a.execution_attempt_id, 10, c
        )
        == ()
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("observation_status", "BROKEN"),
        ("transport_disposition", "BROKEN"),
        ("evidence_strength", "BROKEN"),
        ("observed_at", "2026-01-01T00:00:00"),
        ("provider_occurred_at", "2026-01-01T00:00:00"),
        ("correlation_fingerprint", "bad"),
        ("observation_id", "attempt"),
    ],
)
def test_corruption_fails_closed(mongo_db, field, value):
    """Certify corruption-first rejection for malformed persisted fields."""
    c = mongo_db[COLLECTION]
    o = make_observation()
    FinancialExecutionProviderObservationRegistry.create(o, c)
    c.update_one({"observation_id": o.observation_id}, {"$set": {field: value}})
    with pytest.raises(
        FinancialExecutionProviderObservationPersistedRecordInvalidError
    ):
        FinancialExecutionProviderObservationRegistry.get(
            o.tenant_id, value if field == "observation_id" else o.observation_id, c
        )


def test_fingerprint_and_security_surface(mongo_db):
    """Certify fingerprint integrity and absence of secret/truth fields."""
    c = mongo_db[COLLECTION]
    o = make_observation(
        provider_execution_reference="exec",
        provider_evidence_reference="e",
        provider_occurred_at=NOW,
    )
    FinancialExecutionProviderObservationRegistry.create(o, c)
    row = c.find_one({"observation_id": o.observation_id})
    assert row["observation_fingerprint"] == o.fingerprint
    assert not {"raw_payload", "secret", "settlement", "truth", "state"}.intersection(
        row
    )


def test_provider_references_non_unique(mongo_db):
    """Certify provider references remain non-unique across observations."""
    c = mongo_db[COLLECTION]
    a = make_observation(
        provider_request_reference="same", provider_execution_reference="same"
    )
    b = make_observation(
        provider_request_reference="same", provider_execution_reference="same"
    )
    FinancialExecutionProviderObservationRegistry.create(a, c)
    FinancialExecutionProviderObservationRegistry.create(b, c)
    assert c.count_documents({"provider_request_reference": "same"}) == 2


def test_session_commit_abort_and_collection_injection(mongo_db):
    """Certify caller-owned transaction visibility and collection injection."""
    c = mongo_db[COLLECTION]
    alt = mongo_db["alternate"]
    FinancialExecutionProviderObservationRegistry.ensure_indexes(alt)
    o = make_observation()
    client = c.database.client
    with client.start_session() as s:
        s.start_transaction()
        FinancialExecutionProviderObservationRegistry.create(o, alt, session=s)
        assert alt.find_one({"observation_id": o.observation_id}) is None
        s.commit_transaction()
    assert alt.find_one({"observation_id": o.observation_id}) is not None
    assert c.find_one({"observation_id": o.observation_id}) is None
    x = make_observation()
    s = client.start_session()
    s.start_transaction()
    FinancialExecutionProviderObservationRegistry.create(x, c, session=s)
    s.abort_transaction()
    s.end_session()
    assert c.find_one({"observation_id": x.observation_id}) is None


def _race(c, items):
    """Coordinate bounded concurrent creates without sleeps."""
    barrier = Barrier(len(items))

    def run(o):
        barrier.wait(timeout=30)
        return FinancialExecutionProviderObservationRegistry.create(o, c)

    with ThreadPoolExecutor(max_workers=len(items)) as ex:
        return [f.result(timeout=30) for f in [ex.submit(run, o) for o in items]]


def test_concurrent_exact_create(mongo_db):
    """Certify one create plus nine exact replay outcomes under concurrency."""
    c = mongo_db[COLLECTION]
    o = make_observation()
    out = _race(c, [o] * 10)
    assert sorted(x[0] for x in out) == ["CREATED"] + ["IDEMPOTENT_REPLAY"] * 9
    assert c.count_documents({"observation_id": o.observation_id}) == 1


def test_concurrent_divergent_create(mongo_db):
    """Certify one winner, one divergent conflict, and eight exact replays."""
    c = mongo_db[COLLECTION]
    o = make_observation()
    items = [
        FinancialExecutionProviderObservation(
            **{**o.__dict__, "provider_name": ("PayShap" if i == 0 else "Other")}
        )
        for i in range(10)
    ]
    out = []
    barrier = Barrier(10)

    def run(x):
        barrier.wait(timeout=30)
        try:
            return FinancialExecutionProviderObservationRegistry.create(x, c)[0]
        except FinancialExecutionProviderObservationCreateConflictError:
            return "CONFLICT"

    with ThreadPoolExecutor(max_workers=10) as ex:
        out = [f.result(timeout=30) for f in [ex.submit(run, x) for x in items]]
    assert (
        out.count("CREATED") == 1
        and out.count("CONFLICT") == 1
        and out.count("IDEMPOTENT_REPLAY") == 8
        and c.count_documents({"observation_id": o.observation_id}) == 1
    )


# ARTIFACT: test_financial_execution_provider_observation_registry_mongo.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-PROVIDER-OBSERVATION-REGISTRY-MONGO-CERT
# TENANT POSTURE: every test uses isolated tenant-scoped identities and queries.
# FAIL-CLOSED POSTURE: corruption, replay divergence, and transaction failures are explicit.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution truth; this artifact owns none.
# END OF WILSY OS SOVEREIGN ARTIFACT
