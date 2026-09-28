"""Real-Mongo certificate for the L9C9-P4 currentness composer.

TITLE: WILSY OS Legal Engagement Firm Decision Currentness Composer Real-Mongo Certificate
VERSION: v1.0.0-L9C9-P5-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published registry/composer/P3 chain against a writable
         UUID-isolated Mongo replica set without touching canonical data.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_engagement_firm_decision_currentness_composer_real_mongo.py
COLLABORATION / OWNERSHIP: P1 owns durable firm-decision history; P3 owns
                            currentness semantics; P4 owns one-read
                            composition. This certificate owns disposable
                            runtime evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C9-P5-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
           covers topology, physical indexes, caller transactions, exact
           history reads, state parity, isolation, corruption boundaries,
           snapshot behavior and zero composer writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only. Credentials,
                             URI values and durable sensitive payloads are
                             never printed.
TENANT BOUNDARY: Every composition is exact tenant/matter/fingerprint/
                 client/subject scoped.
AUTHORITY BOUNDARY: Runtime certificate only; no IAM, Engagement,
                    Representation, Court, API, UI, Node or finance authority.
TRANSACTION BOUNDARY: Tests own disposable sessions and transactions; the
                      composer owns none of their lifecycle.
FAIL-CLOSED DECLARATION: Infrastructure unavailability skips explicitly for
                         operator runtime; invalid transactions and corrupt
                         durable evidence fail closed.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision_currentness import (
    LegalClientMatterEngagementFirmDecisionCurrentnessState,
    project_legal_client_matter_engagement_firm_decision_currentness,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_firm_decision_currentness_composer import (
    LegalClientMatterEngagementFirmDecisionCurrentnessComposer,
    LegalClientMatterEngagementFirmDecisionCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_firm_decision_registry as registry,
)


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)
TENANT_A = "tenant-l9c9-p5-a"
TENANT_B = "tenant-l9c9-p5-b"
MATTER = "matter-l9c9-p5"
MATTER_FP = "a" * 128
OTHER_MATTER_FP = "b" * 128
PARTY = "party-l9c9-p5"
OTHER_PARTY = "party-other-l9c9-p5"
SUBJECT_FP = "c" * 128
OTHER_SUBJECT_FP = "d" * 128


class CountingCollection:
    """Collection proxy recording reads and rejecting composer writes."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.find_calls = 0
        self.write_calls = 0

    def with_options(self, **_options: Any) -> "CountingCollection":
        return self

    def find(self, *args: Any, **kwargs: Any) -> Any:
        self.find_calls += 1
        return self.inner.find(*args, **kwargs)

    def insert_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("composer attempted insert")

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("composer attempted update")

    def delete_many(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("composer attempted delete")

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield a writable UUID-isolated disposable database after topology checks."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
            server_version = client.server_info().get("version")
            pymongo_version = getattr(__import__("pymongo"), "version", "unknown")
        except (PyMongoError, OSError) as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version
        assert isinstance(pymongo_version, str) and pymongo_version
        database_name = f"wilsy_l9c9_p5_{uuid.uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        collection = database.get_collection(
            registry.COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _decision(
    *,
    tenant_id: str = TENANT_A,
    decision_id: str = "decision-l9c9-p5-1",
    state: str = "ACCEPTED",
    effective_offset: int = 5,
    matter_id: str = MATTER,
    matter_fingerprint: str = MATTER_FP,
    party_id: str = PARTY,
    subject_fingerprint: str = SUBJECT_FP,
) -> LegalClientMatterEngagementFirmDecision:
    """Build valid immutable evidence with deterministic aware chronology."""
    effective = NOW + timedelta(minutes=effective_offset)
    return LegalClientMatterEngagementFirmDecision(
        decision_id=decision_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_reference="client:subject-l9c9-p5",
        subject_identity_fingerprint=subject_fingerprint,
        decision=state,
        decision_actor_principal_id="principal-l9c9-p5",
        authorization_evidence_reference="iam:l9c9:p5",
        authorization_evidence_fingerprint="e" * 128,
        source_evidence_reference=f"source:{decision_id}",
        source_evidence_fingerprint="f" * 128,
        occurred_at=effective,
        effective_from=effective,
        idempotency_key=f"idempotency:{decision_id}",
    )


def _commit(client: MongoClient[Any], collection: Any, value: LegalClientMatterEngagementFirmDecision) -> None:
    """Persist one canonical row through the certified registry only."""
    with client.start_session() as session:
        with session.start_transaction():
            registry.persist_firm_decision(value, collection, session=session)


def _history(client: MongoClient[Any], collection: Any, **scope: str) -> tuple[LegalClientMatterEngagementFirmDecision, ...]:
    """Read exact history directly under one caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return registry.list_firm_decisions_for_context(
                scope["tenant_id"], scope["case_matter_id"], scope["matter_fingerprint"],
                scope["client_party_id"], scope["subject_identity_fingerprint"], collection,
                session=session,
            )


def _compose(
    client: MongoClient[Any], collection: Any, *, evaluation_time: datetime = NOW + timedelta(hours=1),
    decision_collection: Any | None = None, session: Any | None = None, **scope: str,
) -> Any:
    """Compose one exact scope, optionally inside a supplied session."""
    target = _decision()
    values = {
        "tenant_id": scope.get("tenant_id", target.tenant_id),
        "case_matter_id": scope.get("case_matter_id", target.case_matter_id),
        "matter_fingerprint": scope.get("matter_fingerprint", target.matter_fingerprint),
        "client_party_id": scope.get("client_party_id", target.client_party_id),
        "subject_identity_fingerprint": scope.get("subject_identity_fingerprint", target.subject_identity_fingerprint),
    }
    owned = session is None
    if owned:
        session = client.start_session()
    try:
        if owned:
            session.start_transaction()
        composer = LegalClientMatterEngagementFirmDecisionCurrentnessComposer(
            decision_collection=decision_collection or collection,
        )
        return composer.compose_currentness(**values, evaluated_at=evaluation_time, session=session)
    finally:
        if owned:
            session.abort_transaction()
            session.end_session()


def test_real_topology_indexes_and_no_current_pointer(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """The sanctioned topology and physical P1 indexes are exact and non-TTL."""
    _, database, collection = mongo_context
    indexes = {entry["name"]: entry for entry in collection.list_indexes() if entry["name"] != "_id_"}
    assert database.name != "wilsy"
    assert set(indexes) == {registry.DECISION_ID_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME, registry.IDEMPOTENCY_INDEX_NAME, registry.HISTORY_INDEX_NAME}
    assert indexes[registry.DECISION_ID_INDEX_NAME].get("unique") is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert indexes[registry.HISTORY_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in entry for entry in indexes.values())
    assert all("current" not in entry["name"].lower() for entry in indexes.values())


def test_real_transaction_required_and_composer_owns_no_lifecycle(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Missing/inactive sessions reject; active caller remains lifecycle owner."""
    client, _, collection = mongo_context
    composer = LegalClientMatterEngagementFirmDecisionCurrentnessComposer(decision_collection=collection)
    with pytest.raises(LegalClientMatterEngagementFirmDecisionCurrentnessComposerError):
        composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, NOW, None)
    with client.start_session() as inactive:
        with pytest.raises(LegalClientMatterEngagementFirmDecisionCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, NOW, inactive)
    with client.start_session() as session:
        session.start_transaction()
        result = composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, NOW, session)
        assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
        assert session.in_transaction is True
        session.abort_transaction()


def test_real_empty_and_three_decision_states(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """NO_DECISION and each applicable P3 state are returned exactly."""
    client, _, collection = mongo_context
    assert _compose(client, collection, evaluation_time=NOW).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
    for offset, state, expected in ((5, "ACCEPTED", "ACCEPTED"), (10, "DECLINED", "DECLINED"), (15, "REQUIRES_REVIEW", "REQUIRES_REVIEW")):
        _commit(client, collection, _decision(decision_id=f"single-{state}", state=state, effective_offset=offset))
        assert _compose(client, collection, evaluation_time=NOW + timedelta(hours=1)).state.value == expected


@pytest.mark.parametrize(
    ("later_state", "expected"),
    [("DECLINED", "DECLINED"), ("REQUIRES_REVIEW", "REQUIRES_REVIEW")],
)
def test_real_obsolete_accepted_is_blocked(mongo_context: tuple[MongoClient[Any], Any, Any], later_state: str, expected: str) -> None:
    """A later non-positive decision supersedes an earlier acceptance."""
    client, _, collection = mongo_context
    _commit(client, collection, _decision(decision_id=f"earlier-{later_state}", state="ACCEPTED", effective_offset=5))
    _commit(client, collection, _decision(decision_id=f"later-{later_state}", state=later_state, effective_offset=10))
    assert _compose(client, collection).state.value == expected


def test_real_later_accepted_restores(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """A later acceptance restores the positive currentness state."""
    client, _, collection = mongo_context
    _commit(client, collection, _decision(decision_id="declined", state="DECLINED", effective_offset=5))
    _commit(client, collection, _decision(decision_id="restored", state="ACCEPTED", effective_offset=10))
    assert _compose(client, collection).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED


def test_real_same_effective_same_state_and_conflicts(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Same-state duplicates resolve; differing states are ambiguous."""
    client, _, collection = mongo_context
    _commit(client, collection, _decision(decision_id="same-a", state="ACCEPTED", effective_offset=5))
    _commit(client, collection, _decision(decision_id="same-b", state="ACCEPTED", effective_offset=5))
    assert _compose(client, collection).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    for first, second in (("ACCEPTED", "DECLINED"), ("ACCEPTED", "REQUIRES_REVIEW"), ("DECLINED", "REQUIRES_REVIEW")):
        db = client["wilsy_l9c9_p5_same_effective_" + uuid.uuid4().hex]
        try:
            target = db.get_collection(registry.COLLECTION)
            registry.ensure_indexes(target)
            _commit(client, target, _decision(decision_id="conflict-a", state=first, effective_offset=5))
            _commit(client, target, _decision(decision_id="conflict-b", state=second, effective_offset=5))
            assert _compose(client, target).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.AMBIGUOUS
        finally:
            client.drop_database(db.name)


def test_real_future_exclusion_and_order_independence(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """P3 excludes future evidence and insertion order is not authority."""
    client, _, collection = mongo_context
    future = _decision(decision_id="future", state="DECLINED", effective_offset=120)
    _commit(client, collection, future)
    assert _compose(client, collection, evaluation_time=NOW + timedelta(minutes=60)).state is LegalClientMatterEngagementFirmDecisionCurrentnessState.NO_DECISION
    _commit(client, collection, _decision(decision_id="earlier", state="ACCEPTED", effective_offset=5))
    first = _compose(client, collection, evaluation_time=NOW + timedelta(minutes=60))
    assert first.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    direct_history = _history(client, collection, tenant_id=TENANT_A, case_matter_id=MATTER, matter_fingerprint=MATTER_FP, client_party_id=PARTY, subject_identity_fingerprint=SUBJECT_FP)
    direct = project_legal_client_matter_engagement_firm_decision_currentness(tenant_id=TENANT_A, case_matter_id=MATTER, matter_fingerprint=MATTER_FP, client_party_id=PARTY, subject_identity_fingerprint=SUBJECT_FP, evaluated_at=NOW + timedelta(minutes=60), decisions=direct_history)
    assert first == direct


def test_real_exact_scope_isolation_and_one_history_read(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Neighboring tenant, matter, fingerprint, party and subject rows do not leak."""
    client, _, collection = mongo_context
    _commit(client, collection, _decision(decision_id="exact", state="ACCEPTED", effective_offset=5))
    _commit(client, collection, _decision(tenant_id=TENANT_B, decision_id="tenant-neighbor", state="DECLINED", effective_offset=10))
    _commit(client, collection, _decision(decision_id="matter-neighbor", matter_id="other-matter", state="DECLINED", effective_offset=10))
    _commit(client, collection, _decision(decision_id="fingerprint-neighbor", matter_fingerprint=OTHER_MATTER_FP, state="DECLINED", effective_offset=10))
    _commit(client, collection, _decision(decision_id="party-neighbor", party_id=OTHER_PARTY, state="DECLINED", effective_offset=10))
    _commit(client, collection, _decision(decision_id="subject-neighbor", subject_fingerprint=OTHER_SUBJECT_FP, state="DECLINED", effective_offset=10))
    counted = CountingCollection(collection)
    result = _compose(client, counted)
    assert result.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED
    assert result.tenant_id == TENANT_A and result.case_matter_id == MATTER
    assert counted.find_calls == 1
    assert counted.write_calls == 0


def test_real_projection_parity_and_zero_composer_writes(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Composer equals direct P3 and leaves durable collection unchanged."""
    client, _, collection = mongo_context
    _commit(client, collection, _decision(decision_id="parity", state="ACCEPTED", effective_offset=5))
    before = collection.count_documents({})
    counted = CountingCollection(collection)
    with client.start_session() as session:
        session.start_transaction()
        history = registry.list_firm_decisions_for_context(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, collection, session=session)
        direct = project_legal_client_matter_engagement_firm_decision_currentness(tenant_id=TENANT_A, case_matter_id=MATTER, matter_fingerprint=MATTER_FP, client_party_id=PARTY, subject_identity_fingerprint=SUBJECT_FP, evaluated_at=NOW + timedelta(hours=1), decisions=history)
        composed = LegalClientMatterEngagementFirmDecisionCurrentnessComposer(decision_collection=counted).compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, NOW + timedelta(hours=1), session)
        assert composed == direct
        session.abort_transaction()
    assert collection.count_documents({}) == before
    assert counted.write_calls == 0


def test_real_corrupt_persisted_history_fails_at_registry_boundary(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Strict registry hydration rejects malformed durable evidence."""
    client, _, collection = mongo_context
    value = _decision(decision_id="corrupt")
    _commit(client, collection, value)
    collection.update_one({"tenant_id": TENANT_A, "decision_id": "corrupt"}, {"$set": {"decision": "NOT_A_DECISION"}})
    with pytest.raises(LegalClientMatterEngagementFirmDecisionCurrentnessComposerError) as raised:
        _compose(client, collection)
    assert raised.value.code == "L9C9_P4_HISTORY_READ_FAILED"


def test_real_snapshot_and_caller_commit_abort_control(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Original transaction retains its snapshot; fresh transaction sees commit."""
    client, _, collection = mongo_context
    _commit(client, collection, _decision(decision_id="snapshot-old", state="DECLINED", effective_offset=5))
    with client.start_session() as original:
        original.start_transaction()
        old = _compose(client, collection, session=original)
        _commit(client, collection, _decision(decision_id="snapshot-new", state="ACCEPTED", effective_offset=10))
        again = _compose(client, collection, session=original)
        assert old.state is again.state
        original.abort_transaction()
    fresh = _compose(client, collection)
    assert fresh.state is LegalClientMatterEngagementFirmDecisionCurrentnessState.ACCEPTED


def test_real_authority_surface_is_narrow() -> None:
    """Static certificate confirms no foreign authority imports or clock reads."""
    path = Path("tools/eos/legal_operations/orchestration/legal_client_matter_engagement_firm_decision_currentness_composer.py")
    text = path.read_text()
    assert "datetime.now" not in text and "utcnow" not in text
    assert all(token not in text.lower() for token in ("pymongo", "clientacceptance", "principal_status", "conflict_currentness", "mandate_currentness"))
    assert "legal_client_matter_engagement_firm_decision_currentness" in text


# ARTIFACT: test_legal_client_matter_engagement_firm_decision_currentness_composer_real_mongo.py
# VERSION: v1.0.0-L9C9-P5-ENGAGEMENT-FIRM-DECISION-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo runtime evidence only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
