"""Real-Mongo certificate for L8-8H durable conflict-review registry.

TITLE: Legal Conflict Review Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable L8-8H human-review persistence against one disposable
         writable Mongo replica set: physical indexes, commit/replay, complete
         screening history, reviewer/outcome audit reads, rollback, tenant
         isolation, corruption rejection and synchronized identity races.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_conflict_review_registry_real_mongo.py
CERTIFICATION / UPDATE DATE: 2026-09-25
TRANSACTION BOUNDARY: Test caller owns every session/transaction.
AUTHORITY BOUNDARY: Physical human-review persistence/read evidence only; no
                    IAM admission, waiver, ethical wall, engagement or representation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
FAIL-CLOSED DECLARATION: Once fixture yields, index, transaction, replay,
                         corruption and concurrency defects fail certification.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewDetermination,
    LegalConflictReviewOutcome,
    determine_legal_conflict_review,
)
from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictMatchKind,
    LegalConflictMatchSignal,
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
)
from tools.eos.legal_operations.registry import legal_conflict_review_registry as registry


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 22, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated review collection after replica-set checks."""
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
        except PyMongoError as error:
            pytest.skip(
                f"host Mongo unavailable during hello: {type(error).__name__}: {error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.skip("replica set has no writable primary")
        if hello.get("logicalSessionTimeoutMinutes") is None:
            pytest.skip("replica set has no logical-session capability")

        database = client[f"wilsy_l8_8h_review_{uuid.uuid4().hex}"]
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


def _screening(
    tenant: str,
    *,
    screening_id: str = "screening-1",
) -> LegalConflictScreeningResult:
    match = LegalConflictMatchSignal(
        tenant_id=tenant,
        subject_identity_fingerprint=FP_B,
        source_party_id="party-source",
        source_case_matter_id="matter-1",
        source_party_fingerprint=FP_A,
        matched_party_id="party-match",
        matched_case_matter_id="matter-2",
        matched_party_fingerprint=FP_C,
        match_kind=LegalConflictMatchKind.OPPOSING_SIDE_EXACT_SUBJECT_MATCH,
    )
    return LegalConflictScreeningResult(
        tenant_id=tenant,
        screening_id=screening_id,
        source_party_id="party-source",
        source_case_matter_id="matter-1",
        source_party_fingerprint=FP_A,
        subject_identity_fingerprint=FP_B,
        screened_at=NOW,
        status=LegalConflictScreeningStatus.REVIEW_REQUIRED,
        matches=(match,),
        source_evidence_reference=f"screening-source:{screening_id}",
        source_evidence_fingerprint=FP_C,
    )


def _review(
    tenant: str,
    *,
    review_id: str,
    screening_id: str = "screening-1",
    reviewer: str = "principal-reviewer",
    outcome: LegalConflictReviewOutcome = LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
    reviewed_at: datetime | None = None,
) -> LegalConflictReviewDetermination:
    return determine_legal_conflict_review(
        screening=_screening(tenant, screening_id=screening_id),
        review_id=review_id,
        reviewer_principal_id=reviewer,
        reviewer_authorization_reference=f"iam-authorization:{reviewer}",
        reviewer_authorization_fingerprint=FP_A,
        outcome=outcome,
        review_reason_reference=f"review-reason:{review_id}",
        reviewed_at=reviewed_at or (NOW + timedelta(minutes=1)),
        source_evidence_reference=f"review-source:{review_id}",
        source_evidence_fingerprint=FP_B,
    )


def _commit(
    client: MongoClient[Any],
    collection: Any,
    value: LegalConflictReviewDetermination,
) -> LegalConflictReviewDetermination:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_review(
                value,
                collection,
                session=session,
            )


def test_real_index_metadata_is_exact_and_has_no_ttl_or_current_pointer(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Certify four physical immutable-history indexes only."""
    _, _, collection = mongo_context
    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
        if entry["name"] != "_id_"
    }
    assert set(indexes) == {
        registry.REVIEW_ID_INDEX_NAME,
        registry.SCREENING_HISTORY_INDEX_NAME,
        registry.REVIEWER_HISTORY_INDEX_NAME,
        registry.OUTCOME_HISTORY_INDEX_NAME,
    }
    assert dict(indexes[registry.REVIEW_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "review_id": 1,
    }
    assert indexes[registry.REVIEW_ID_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.SCREENING_HISTORY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "screening_id": 1,
        "reviewed_at": 1,
    }
    assert dict(indexes[registry.REVIEWER_HISTORY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "reviewer_principal_id": 1,
        "reviewed_at": -1,
    }
    assert dict(indexes[registry.OUTCOME_HISTORY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "outcome": 1,
        "reviewed_at": -1,
    }
    assert all(
        entry.get("unique") is not True
        for name, entry in indexes.items()
        if name != registry.REVIEW_ID_INDEX_NAME
    )
    assert all("expireAfterSeconds" not in entry for entry in indexes.values())


def test_real_commit_replay_histories_and_tenant_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Certify replay plus screening/reviewer/outcome histories by exact tenant."""
    client, _, collection = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    foreign = f"tenant-b-{uuid.uuid4().hex}"
    first = _review(
        tenant,
        review_id="review-1",
        outcome=LegalConflictReviewOutcome.ESCALATION_REQUIRED,
        reviewed_at=NOW + timedelta(minutes=1),
    )
    second = _review(
        tenant,
        review_id="review-2",
        outcome=LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
        reviewed_at=NOW + timedelta(minutes=2),
    )
    third = _review(
        tenant,
        review_id="review-3",
        screening_id="screening-2",
        reviewer="principal-other",
        outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        reviewed_at=NOW + timedelta(minutes=3),
    )
    foreign_value = _review(
        foreign,
        review_id="review-foreign",
        outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
    )
    for value in (first, second, third, foreign_value):
        assert _commit(client, collection, value) == value
    assert _commit(client, collection, first) == first

    with client.start_session() as session:
        with session.start_transaction():
            screening_history = registry.list_screening_reviews(
                tenant,
                "screening-1",
                collection,
                session=session,
            )
            reviewer_history = registry.list_reviewer_reviews(
                tenant,
                "principal-reviewer",
                collection,
                session=session,
            )
            no_conflict = registry.list_outcome_reviews(
                tenant,
                LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
                collection,
                session=session,
            )
            assert [item.review_id for item in screening_history] == [
                "review-1",
                "review-2",
            ]
            assert {item.review_id for item in reviewer_history} == {
                "review-1",
                "review-2",
            }
            assert [item.review_id for item in no_conflict] == ["review-2"]
            with pytest.raises(registry.LegalConflictReviewRegistryNotFoundError):
                registry.get_review(
                    foreign,
                    "review-1",
                    collection,
                    session=session,
                )


def test_real_caller_abort_rolls_back_review_insert(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Registry never owns caller transaction commit."""
    client, _, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _review(tenant, review_id="review-abort")
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_review(value, collection, session=session)
        assert collection.count_documents(
            {"tenant_id": tenant},
            session=session,
        ) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0


def test_real_divergent_same_review_identity_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Immutable review identity cannot be rebound to another determination."""
    client, _, collection = mongo_context
    tenant = f"tenant-conflict-{uuid.uuid4().hex}"
    first = _review(
        tenant,
        review_id="review-1",
        outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
    )
    _commit(client, collection, first)
    divergent = _review(
        tenant,
        review_id="review-1",
        outcome=LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalConflictReviewRegistryConflictError):
            registry.persist_review(
                divergent,
                collection,
                session=session,
            )
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Physical envelope/payload tampering cannot hydrate as review truth."""
    client, _, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _review(tenant, review_id="review-corrupt")
    _commit(client, collection, value)
    original = deepcopy(collection.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)

    collection.update_one(
        {"_id": original["_id"]},
        {"$set": {"review_payload.review_reason_reference": "tampered"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.LegalConflictReviewRegistryPersistedRecordInvalidError
            ):
                registry.get_review(
                    tenant,
                    value.review_id,
                    collection,
                    session=session,
                )
    collection.replace_one({"_id": original["_id"]}, original)


def test_real_competing_same_review_identity_has_one_durable_winner(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Two synchronized divergent creates cannot produce two review rows."""
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    left = _review(
        tenant,
        review_id="review-race",
        outcome=LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
    )
    right = _review(
        tenant,
        review_id="review-race",
        outcome=LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
    )
    barrier = Barrier(2)

    def contender(value: LegalConflictReviewDetermination) -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.persist_review(
                    value,
                    collection,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"
            except registry.LegalConflictReviewRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except registry.LegalConflictReviewRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"
            except registry.LegalConflictReviewRegistryPersistenceUnavailableError as error:
                if session.in_transaction:
                    session.abort_transaction()
                cause = error.__cause__
                if isinstance(cause, PyMongoError) and cause.has_error_label(
                    "TransientTransactionError"
                ):
                    return "RETRY_REQUIRED"
                return "PERSISTENCE_UNAVAILABLE"
            except Exception as error:
                if session.in_transaction:
                    session.abort_transaction()
                return type(error).__name__

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(contender, (left, right)))

    assert outcomes.count("COMMITTED") == 1
    assert sum(
        outcome in {"RETRY_REQUIRED", "CONFLICT"}
        for outcome in outcomes
    ) == 1
    assert collection.count_documents({"tenant_id": tenant}) == 1
    row = collection.find_one({"tenant_id": tenant})
    assert isinstance(row, dict)
    assert row["review_id"] == "review-race"


# ARTIFACT: test_legal_conflict_review_registry_real_mongo.py
# VERSION: v1.0.0-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable human-review persistence/read evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant-scoped indexes/queries
# FAIL-CLOSED POSTURE: rollback/divergence/corruption/concurrency cannot invent review truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
