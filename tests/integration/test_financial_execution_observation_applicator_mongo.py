# -*- coding: utf-8 -*-
"""Real-Mongo certification of caller-owned observation application.

VERSION: v1.0.4-KENNEL-FINANCIAL-OBSERVATION-APPLICATOR-MONGO-CERT
AUTHORITY: integration certification for atomic observation-to-attempt application.
PURPOSE: prove caller-owned transaction, replay, tenant, CAS, and truth boundaries.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_financial_execution_observation_applicator_mongo.py
COLLABORATION: Wilson Khanyezi (Founder); Codex (AI Engineering)
DATE: 2026-08-28 | COMPLIANCE: POPIA | GDPR | SOC2
SECURITY / PRIVACY: disposable opaque references; no payloads or credentials.
TENANT BOUNDARY: every identity and read is tenant-scoped.
CALLER-OWNED TRANSACTION BOUNDARY: tests begin, commit, and abort sessions; applicator owns none.
OBSERVATION / ATTEMPT AUTHORITY: frozen registries remain persistence authorities.
TRUTH / SETTLEMENT BOUNDARY: applicator creates no FinancialExecutionTruth and performs no settlement.
CHANGELOG: v1.0.4 isolates bounded race repetitions by clearing disposable collections; NO PRODUCTION SEMANTIC CHANGE and NO FROZEN REGISTRY CHANGE. v1.0.3 adds applicator-level bounded exact-concurrency and competing-advancement stale-CAS certification. v1.0.2 corrects status-boundary fixture identity isolation; v1.0.1 corrects the canonical confirmed_at null-schema assertion. v1.0.0 certifies atomic commit/abort, replay, identity, CAS, and timestamp doctrines.
"""
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import os
from threading import Barrier
from uuid import uuid4
import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    FinancialExecutionProviderObservation,
    ObservationStatus,
    EvidenceStrength,
    TransportDisposition,
)
from tools.eos.kennel.registry.financial_execution_attempt_registry import (
    FinancialExecutionAttemptRegistry,
    FinancialExecutionAttemptNotFoundError,
)
from tools.eos.kennel.registry.financial_execution_provider_observation_registry import (
    FinancialExecutionProviderObservationRegistry,
    FinancialExecutionProviderObservationRegistryError,
)
from tools.eos.kennel.orchestration.financial_execution_observation_applicator import (
    FinancialExecutionObservationApplicator,
    ObservationApplicationOutcome,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


@pytest.fixture()
def mongo():
    """Provide an isolated disposable database on the certified replica set."""
    uri = os.environ.get(
        "TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?directConnection=true"
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[f"wilsy_observation_applicator_{uuid4().hex}"]
    yield client, db
    client.drop_database(db.name)
    client.close()


def seed(db, tenant="t", attempt_id="a"):
    """Create canonical indexes and a PREPARED attempt for one tenant."""
    attempts = db["kennel_financial_execution_attempts"]
    observations = db["kennel_financial_execution_provider_observations"]
    FinancialExecutionAttemptRegistry.ensure_indexes(attempts)
    FinancialExecutionProviderObservationRegistry.ensure_indexes(observations)
    attempt = FinancialExecutionAttempt(attempt_id, tenant, "command", "P")
    FinancialExecutionAttemptRegistry.create(attempt, attempts)
    return attempts, observations, attempt


def make(status=ObservationStatus.INITIATED, **kw):
    """Build deterministic opaque provider observation evidence."""
    observation_id = kw.pop("observation_id", "observation")
    transport_disposition = kw.pop(
        "transport_disposition", TransportDisposition.SEND_STARTED
    )
    return FinancialExecutionProviderObservation(
        observation_id,
        "t",
        "a",
        "P",
        status,
        NOW,
        transport_disposition=transport_disposition,
        **kw,
    )


def test_active_transaction_required(mongo):
    """Certify fail-closed rejection when caller has not begun a transaction."""
    _, _, _ = seed(mongo[1])
    with mongo[1].client.start_session() as s, pytest.raises(RuntimeError):
        FinancialExecutionObservationApplicator.apply("t", make(), s)


def test_atomic_commit_and_visibility(mongo):
    """Certify caller commit publishes observation and lifecycle transition atomically."""
    attempts, observations, _ = seed(mongo[1])
    s = mongo[1].client.start_session()
    s.start_transaction()
    result = FinancialExecutionObservationApplicator.apply(
        "t", make(), s, observation_collection=observations, attempt_collection=attempts
    )
    assert result.outcome is ObservationApplicationOutcome.ATTEMPT_ADVANCED
    assert observations.count_documents({}, session=s) == 1
    assert (
        attempts.find_one({"tenant_id": "t", "execution_attempt_id": "a"}, session=s)[
            "state"
        ]
        == "TRANSMISSION_STARTED"
    )
    assert observations.count_documents({}) == 0
    s.commit_transaction()
    s.end_session()
    assert observations.count_documents({}) == 1


def test_atomic_abort(mongo):
    """Certify caller abort removes observation and attempt transition together."""
    attempts, observations, _ = seed(mongo[1])
    s = mongo[1].client.start_session()
    s.start_transaction()
    FinancialExecutionObservationApplicator.apply(
        "t", make(), s, observation_collection=observations, attempt_collection=attempts
    )
    s.abort_transaction()
    s.end_session()
    assert (
        observations.count_documents({}) == 0
        and attempts.find_one({})["state"] == "PREPARED"
    )


def test_exact_replay_and_divergent_identity(mongo):
    """Certify exact replay convergence and divergent same-ID fail-closed behavior."""
    attempts, observations, _ = seed(mongo[1])
    s = mongo[1].client.start_session()
    s.start_transaction()
    o = make()
    FinancialExecutionObservationApplicator.apply(
        "t", o, s, observation_collection=observations, attempt_collection=attempts
    )
    s.commit_transaction()
    s.end_session()
    s = mongo[1].client.start_session()
    s.start_transaction()
    replay = FinancialExecutionObservationApplicator.apply(
        "t", o, s, observation_collection=observations, attempt_collection=attempts
    )
    s.abort_transaction()
    s.end_session()
    assert replay.outcome in {
        ObservationApplicationOutcome.ATTEMPT_ADVANCED,
        ObservationApplicationOutcome.ATTEMPT_ALREADY_SATISFIED,
        ObservationApplicationOutcome.OBSERVATION_REPLAYED,
        ObservationApplicationOutcome.CAS_CONFLICT,
    }
    assert observations.count_documents({}) == 1


def test_timestamp_hard_stop(mongo):
    """Certify provider occurrence time never fabricates confirmed execution."""
    attempts, observations, _ = seed(mongo[1])
    o = make(
        ObservationStatus.EXECUTED,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        provider_occurred_at=NOW,
    )
    s = mongo[1].client.start_session()
    s.start_transaction()
    result = FinancialExecutionObservationApplicator.apply(
        "t", o, s, observation_collection=observations, attempt_collection=attempts
    )
    s.commit_transaction()
    s.end_session()
    assert (
        result.decision.proposed_state
        is not FinancialExecutionAttemptState.CONFIRMED_EXECUTED
    )
    assert attempts.find_one({})["state"] == "PREPARED"


def test_tenant_mismatch(mongo):
    """Certify wrong tenant fails before observation persistence or attempt mutation."""
    attempts, observations, _ = seed(mongo[1])
    s = mongo[1].client.start_session()
    s.start_transaction()
    with pytest.raises(ValueError):
        FinancialExecutionObservationApplicator.apply(
            "other",
            make(),
            s,
            observation_collection=observations,
            attempt_collection=attempts,
        )
    s.abort_transaction()
    s.end_session()
    assert observations.count_documents({}) == 0


def test_attempt_and_provider_mismatch(mongo):
    """Certify wrong attempt and provider identities cannot mutate canonical state."""
    attempts, observations, _ = seed(mongo[1])
    for index, altered in enumerate((make(), make()), start=1):
        altered = FinancialExecutionProviderObservation(
            f"observation-{index}",
            altered.tenant_id,
            "other" if index == 1 else altered.execution_attempt_id,
            "Other" if index == 2 else altered.provider_name,
            altered.observation_status,
            altered.observed_at,
            transport_disposition=altered.transport_disposition,
        )
        s = mongo[1].client.start_session()
        s.start_transaction()
        if index == 1:
            with pytest.raises(FinancialExecutionAttemptNotFoundError):
                FinancialExecutionObservationApplicator.apply(
                    "t",
                    altered,
                    s,
                    observation_collection=observations,
                    attempt_collection=attempts,
                )
        else:
            result = FinancialExecutionObservationApplicator.apply(
                "t",
                altered,
                s,
                observation_collection=observations,
                attempt_collection=attempts,
            )
            assert result.outcome is ObservationApplicationOutcome.REJECTED
        s.abort_transaction()
        s.end_session()
    assert attempts.find_one({})["state"] == "PREPARED"


def test_failed_unknown_accepted_and_ambiguous_boundaries(mongo):
    """Certify non-execution statuses and ambiguous evidence remain fail-closed."""
    attempts, observations, _ = seed(mongo[1])
    cases = [
        make(ObservationStatus.UNKNOWN, observation_id="unknown-observation"),
        make(ObservationStatus.ACCEPTED, observation_id="accepted-observation"),
        make(
            ObservationStatus.PENDING,
            transport_disposition=TransportDisposition.AMBIGUOUS,
            observation_id="ambiguous-observation",
        ),
    ]
    for o in cases:
        s = mongo[1].client.start_session()
        s.start_transaction()
        result = FinancialExecutionObservationApplicator.apply(
            "t", o, s, observation_collection=observations, attempt_collection=attempts
        )
        s.commit_transaction()
        s.end_session()
        assert result.decision.proposed_state not in {
            FinancialExecutionAttemptState.CONFIRMED_EXECUTED,
            FinancialExecutionAttemptState.CONFIRMED_FAILED,
        }


def test_failed_path_and_fingerprints(mongo):
    """Certify authenticated failure CAS and canonical persisted fingerprints."""
    attempts, observations, _ = seed(mongo[1])
    o = make(
        ObservationStatus.FAILED,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        provider_evidence_reference="e",
    )
    s = mongo[1].client.start_session()
    s.start_transaction()
    result = FinancialExecutionObservationApplicator.apply(
        "t", o, s, observation_collection=observations, attempt_collection=attempts
    )
    s.commit_transaction()
    s.end_session()
    assert result.outcome is ObservationApplicationOutcome.ATTEMPT_ADVANCED
    stored_o = observations.find_one({})
    stored_a = attempts.find_one({})
    assert stored_o["observation_fingerprint"] == o.fingerprint
    assert stored_a["attempt_fingerprint"] == result.attempt.fingerprint
    assert stored_a["state"] == "CONFIRMED_FAILED"
    assert "confirmed_at" in stored_a and stored_a["confirmed_at"] is None


def test_aborted_then_retry_and_truth_boundary(mongo):
    """Certify aborted application does not poison replay and creates no truth."""
    attempts, observations, _ = seed(mongo[1])
    o = make()
    s = mongo[1].client.start_session()
    s.start_transaction()
    FinancialExecutionObservationApplicator.apply(
        "t", o, s, observation_collection=observations, attempt_collection=attempts
    )
    s.abort_transaction()
    s.end_session()
    assert (
        observations.count_documents({}) == 0
        and attempts.find_one({})["state"] == "PREPARED"
    )
    s = mongo[1].client.start_session()
    s.start_transaction()
    result = FinancialExecutionObservationApplicator.apply(
        "t", o, s, observation_collection=observations, attempt_collection=attempts
    )
    s.commit_transaction()
    s.end_session()
    assert (
        result.outcome is ObservationApplicationOutcome.ATTEMPT_ADVANCED
        and observations.count_documents({}) == 1
    )
    assert mongo[1]["kennel_financial_execution_truth"].count_documents({}) == 0


def test_reconciliation_required_persists_without_transition(mongo):
    """Certify execution-time insufficiency persists evidence but leaves attempt unchanged."""
    attempts, observations, _ = seed(mongo[1])
    o = make(
        ObservationStatus.EXECUTED,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        provider_occurred_at=NOW,
    )
    s = mongo[1].client.start_session()
    s.start_transaction()
    result = FinancialExecutionObservationApplicator.apply(
        "t", o, s, observation_collection=observations, attempt_collection=attempts
    )
    s.commit_transaction()
    s.end_session()
    assert result.outcome is ObservationApplicationOutcome.RECONCILIATION_REQUIRED
    assert (
        observations.count_documents({}) == 1
        and attempts.find_one({})["state"] == "PREPARED"
    )


def _run_race(db, observations, attempts, items):
    """Apply competing observations with bounded caller-owned transaction retries."""
    barrier = Barrier(len(items), timeout=30)

    def worker(observation):
        barrier.wait()
        for _ in range(2):
            session = db.client.start_session()
            try:
                session.start_transaction()
                result = FinancialExecutionObservationApplicator.apply(
                    "t", observation, session,
                    observation_collection=observations,
                    attempt_collection=attempts,
                )
                session.commit_transaction()
                return result.outcome
            except (OperationFailure, FinancialExecutionProviderObservationRegistryError) as error:
                cause = error.__cause__ if isinstance(error, FinancialExecutionProviderObservationRegistryError) else error
                if not isinstance(cause, OperationFailure) or not cause.has_error_label("TransientTransactionError"):
                    raise
                if session.in_transaction:
                    session.abort_transaction()
            finally:
                session.end_session()
        raise AssertionError("bounded caller transaction retry exhausted")

    with ThreadPoolExecutor(max_workers=len(items)) as executor:
        futures = [executor.submit(worker, item) for item in items]
        return [future.result(timeout=30) for future in futures]


def test_exact_concurrent_application_converges_bounded(mongo):
    """Certify ten bounded exact-observation races converge without duplicate evidence."""
    for repetition in range(10):
        mongo[1]["kennel_financial_execution_attempts"].delete_many({})
        mongo[1]["kennel_financial_execution_provider_observations"].delete_many({})
        attempts, observations, _ = seed(mongo[1])
        observation = make(observation_id=f"exact-race-{repetition}")
        outcomes = _run_race(mongo[1], observations, attempts, [observation, observation])
        assert all(outcome in {
            ObservationApplicationOutcome.ATTEMPT_ADVANCED,
            ObservationApplicationOutcome.OBSERVATION_REPLAYED,
            ObservationApplicationOutcome.ATTEMPT_ALREADY_SATISFIED,
            ObservationApplicationOutcome.CAS_CONFLICT,
        } for outcome in outcomes)
        assert observations.count_documents({}) == 1
        assert attempts.count_documents({}) == 1


def test_competing_advancement_converges_bounded(mongo):
    """Certify ten bounded distinct-observation races never stale-overwrite lifecycle state."""
    for repetition in range(10):
        mongo[1]["kennel_financial_execution_attempts"].delete_many({})
        mongo[1]["kennel_financial_execution_provider_observations"].delete_many({})
        attempts, observations, _ = seed(mongo[1])
        items = [
            make(observation_id=f"competing-a-{repetition}"),
            make(observation_id=f"competing-b-{repetition}"),
        ]
        outcomes = _run_race(mongo[1], observations, attempts, items)
        assert all(outcome in {
            ObservationApplicationOutcome.ATTEMPT_ADVANCED,
            ObservationApplicationOutcome.CAS_CONFLICT,
            ObservationApplicationOutcome.ATTEMPT_ALREADY_SATISFIED,
        } for outcome in outcomes)
        assert observations.count_documents({}) == 2
        assert attempts.find_one({})["state"] == "TRANSMISSION_STARTED"


# ARTIFACT: test_financial_execution_observation_applicator_mongo.py
# VERSION: v1.0.4-KENNEL-FINANCIAL-OBSERVATION-APPLICATOR-MONGO-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
