"""Direct certificate for L8-8H legal conflict-review registry.

VERSION: v1.0.0-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_review_registry.py
AUTHORITY BOUNDARY: Immutable review persistence/read evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

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


NOW = datetime(2026, 9, 25, 21, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor(list[dict[str, Any]]):
    def sort(self, *_args: Any, **_kwargs: Any) -> "Cursor":
        return self

    def limit(self, value: int) -> "Cursor":
        return Cursor(self[:value])


class Result:
    inserted_id = "inserted"


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[dict[str, Any]] = []
        self.sessions: list[Any] = []
        self.insert_error: Exception | None = None
        self.find_error: Exception | None = None
        self.overflow_query: dict[str, object] | None = None
        self.overflow_count = 0

    def with_options(self, **_kwargs: Any) -> "Collection":
        return self

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, object], *, session: Any) -> Cursor:
        self.sessions.append(session)
        if self.find_error is not None:
            raise self.find_error
        if self.overflow_query == query:
            return Cursor([{"placeholder": index} for index in range(self.overflow_count)])
        rows = [
            deepcopy(row)
            for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ]
        return Cursor(rows)

    def insert_one(self, document: dict[str, object], *, session: Any) -> Result:
        self.sessions.append(session)
        if self.insert_error is not None:
            raise self.insert_error
        row = deepcopy(document)
        row["_id"] = f"id-{len(self.rows) + 1}"
        self.rows.append(row)
        return Result()


def screening(
    *,
    screening_id: str = "screening-1",
    status: LegalConflictScreeningStatus = LegalConflictScreeningStatus.REVIEW_REQUIRED,
) -> LegalConflictScreeningResult:
    matches = (
        (
            LegalConflictMatchSignal(
                tenant_id="tenant-law",
                subject_identity_fingerprint=FP_B,
                source_party_id="party-1",
                source_case_matter_id="matter-1",
                source_party_fingerprint=FP_A,
                matched_party_id="party-2",
                matched_case_matter_id="matter-2",
                matched_party_fingerprint=FP_C,
                match_kind=LegalConflictMatchKind.CROSS_MATTER_EXACT_SUBJECT_MATCH,
            ),
        )
        if status is LegalConflictScreeningStatus.REVIEW_REQUIRED
        else ()
    )
    return LegalConflictScreeningResult(
        tenant_id="tenant-law",
        screening_id=screening_id,
        source_party_id="party-1",
        source_case_matter_id="matter-1",
        source_party_fingerprint=FP_A,
        subject_identity_fingerprint=FP_B,
        screened_at=NOW,
        status=status,
        matches=matches,
        source_evidence_reference="screening-source:1",
        source_evidence_fingerprint=FP_C,
    )


def review(
    *,
    review_id: str = "review-1",
    screening_id: str = "screening-1",
    reviewer: str = "principal-reviewer-1",
    outcome: LegalConflictReviewOutcome = LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
    reviewed_at: datetime | None = None,
) -> LegalConflictReviewDetermination:
    return determine_legal_conflict_review(
        screening=screening(screening_id=screening_id),
        review_id=review_id,
        reviewer_principal_id=reviewer,
        reviewer_authorization_reference=f"iam-authorization:{reviewer}",
        reviewer_authorization_fingerprint=FP_A,
        outcome=outcome,
        review_reason_reference=f"review-reason:{review_id}",
        reviewed_at=reviewed_at or (NOW + timedelta(minutes=5)),
        source_evidence_reference=f"review-evidence:{review_id}",
        source_evidence_fingerprint=FP_B,
    )


def test_index_contract_is_exact_and_has_no_current_pointer_or_ttl() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert collection.indexes == [
        {
            "key": [("tenant_id", 1), ("review_id", 1)],
            "unique": True,
            "name": registry.REVIEW_ID_INDEX_NAME,
        },
        {
            "key": [
                ("tenant_id", 1),
                ("screening_id", 1),
                ("reviewed_at", 1),
            ],
            "unique": False,
            "name": registry.SCREENING_HISTORY_INDEX_NAME,
        },
        {
            "key": [
                ("tenant_id", 1),
                ("reviewer_principal_id", 1),
                ("reviewed_at", -1),
            ],
            "unique": False,
            "name": registry.REVIEWER_HISTORY_INDEX_NAME,
        },
        {
            "key": [
                ("tenant_id", 1),
                ("outcome", 1),
                ("reviewed_at", -1),
            ],
            "unique": False,
            "name": registry.OUTCOME_HISTORY_INDEX_NAME,
        },
    ]


@pytest.mark.parametrize(
    "operation",
    ["persist", "get", "screening", "reviewer", "outcome"],
)
def test_every_operational_path_requires_active_caller_transaction(
    operation: str,
) -> None:
    collection = Collection()
    value = review()
    with pytest.raises(registry.LegalConflictReviewRegistryTransactionRequiredError):
        if operation == "persist":
            registry.persist_review(value, collection, session=None)
        elif operation == "get":
            registry.get_review(value.tenant_id, value.review_id, collection, session=Session(False))
        elif operation == "screening":
            registry.list_screening_reviews(
                value.tenant_id,
                value.screening_id,
                collection,
                session=None,
            )
        elif operation == "reviewer":
            registry.list_reviewer_reviews(
                value.tenant_id,
                value.reviewer_principal_id,
                collection,
                session=Session(False),
            )
        else:
            registry.list_outcome_reviews(
                value.tenant_id,
                value.outcome,
                collection,
                session=None,
            )


def test_create_exact_replay_and_session_propagation() -> None:
    collection = Collection()
    session = Session()
    value = review()
    created = registry.persist_review(value, collection, session=session)
    replay = registry.persist_review(value, collection, session=session)
    assert created == replay == value
    assert len(collection.rows) == 1
    assert collection.sessions
    assert all(item is session for item in collection.sessions)


def test_divergent_same_review_identity_fails_closed() -> None:
    collection = Collection()
    session = Session()
    first = review()
    registry.persist_review(first, collection, session=session)
    divergent = determine_legal_conflict_review(
        screening=screening(),
        review_id=first.review_id,
        reviewer_principal_id=first.reviewer_principal_id,
        reviewer_authorization_reference=first.reviewer_authorization_reference,
        reviewer_authorization_fingerprint=first.reviewer_authorization_fingerprint,
        outcome=LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
        review_reason_reference="different-reason",
        reviewed_at=first.reviewed_at,
        source_evidence_reference=first.source_evidence_reference,
        source_evidence_fingerprint=first.source_evidence_fingerprint,
    )
    with pytest.raises(registry.LegalConflictReviewRegistryConflictError):
        registry.persist_review(divergent, collection, session=session)
    assert len(collection.rows) == 1


def test_multiple_reviews_for_one_screening_are_preserved_as_history() -> None:
    collection = Collection()
    session = Session()
    escalation = review(
        review_id="review-1",
        outcome=LegalConflictReviewOutcome.ESCALATION_REQUIRED,
        reviewed_at=NOW + timedelta(minutes=1),
    )
    final = review(
        review_id="review-2",
        outcome=LegalConflictReviewOutcome.NO_CONFLICT_IDENTIFIED,
        reviewed_at=NOW + timedelta(minutes=2),
    )
    registry.persist_review(final, collection, session=session)
    registry.persist_review(escalation, collection, session=session)
    history = registry.list_screening_reviews(
        "tenant-law",
        "screening-1",
        collection,
        session=session,
    )
    assert {item.review_id for item in history} == {"review-1", "review-2"}
    assert len(history) == 2


def test_reviewer_and_outcome_reads_are_tenant_scoped() -> None:
    collection = Collection()
    session = Session()
    values = [
        review(review_id="review-a", reviewer="principal-a"),
        review(
            review_id="review-b",
            screening_id="screening-2",
            reviewer="principal-a",
            outcome=LegalConflictReviewOutcome.ESCALATION_REQUIRED,
        ),
        review(
            review_id="review-c",
            screening_id="screening-3",
            reviewer="principal-b",
        ),
    ]
    for value in values:
        registry.persist_review(value, collection, session=session)

    by_reviewer = registry.list_reviewer_reviews(
        "tenant-law",
        "principal-a",
        collection,
        session=session,
    )
    assert {item.review_id for item in by_reviewer} == {"review-a", "review-b"}

    by_outcome = registry.list_outcome_reviews(
        "tenant-law",
        LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
        collection,
        session=session,
    )
    assert {item.review_id for item in by_outcome} == {"review-a", "review-c"}


def test_foreign_tenant_absence_is_not_disclosed() -> None:
    collection = Collection()
    session = Session()
    registry.persist_review(review(), collection, session=session)
    with pytest.raises(registry.LegalConflictReviewRegistryNotFoundError):
        registry.get_review(
            "tenant-other",
            "review-1",
            collection,
            session=session,
        )


def test_corrupt_payload_and_envelope_are_rejected() -> None:
    collection = Collection()
    session = Session()
    value = review()
    registry.persist_review(value, collection, session=session)
    pristine = deepcopy(collection.rows[0])

    collection.rows[0]["review_payload"]["review_reason_reference"] = "tampered"
    with pytest.raises(registry.LegalConflictReviewRegistryPersistedRecordInvalidError):
        registry.get_review(
            value.tenant_id,
            value.review_id,
            collection,
            session=session,
        )

    collection.rows[0] = deepcopy(pristine)
    collection.rows[0]["screening_id"] = "screening-tampered"
    with pytest.raises(registry.LegalConflictReviewRegistryPersistedRecordInvalidError) as raised:
        registry.get_review(
            value.tenant_id,
            value.review_id,
            collection,
            session=session,
        )
    assert raised.value.code == "L8_8H_RECORD_CORRELATION_INVALID"


@pytest.mark.parametrize(
    ("kind", "limit", "code"),
    [
        (
            "screening",
            registry.MAX_SCREENING_REVIEWS,
            "L8_8H_SCREENING_REVIEW_LIMIT_EXCEEDED",
        ),
        (
            "reviewer",
            registry.MAX_REVIEWER_REVIEWS,
            "L8_8H_REVIEWER_REVIEW_LIMIT_EXCEEDED",
        ),
        (
            "outcome",
            registry.MAX_OUTCOME_REVIEWS,
            "L8_8H_OUTCOME_REVIEW_LIMIT_EXCEEDED",
        ),
    ],
)
def test_bounded_query_overflow_fails_closed(
    kind: str,
    limit: int,
    code: str,
) -> None:
    collection = Collection()
    session = Session()
    value = review()
    if kind == "screening":
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "screening_id": value.screening_id,
        }
        call = lambda: registry.list_screening_reviews(
            value.tenant_id,
            value.screening_id,
            collection,
            session=session,
        )
    elif kind == "reviewer":
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "reviewer_principal_id": value.reviewer_principal_id,
        }
        call = lambda: registry.list_reviewer_reviews(
            value.tenant_id,
            value.reviewer_principal_id,
            collection,
            session=session,
        )
    else:
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "outcome": LegalConflictReviewOutcome.CONFLICT_IDENTIFIED.value,
        }
        call = lambda: registry.list_outcome_reviews(
            value.tenant_id,
            LegalConflictReviewOutcome.CONFLICT_IDENTIFIED,
            collection,
            session=session,
        )
    collection.overflow_count = limit + 1
    with pytest.raises(registry.LegalConflictReviewRegistryPersistedRecordInvalidError) as raised:
        call()
    assert raised.value.code == code


def test_duplicate_key_insert_race_requires_whole_transaction_retry() -> None:
    collection = Collection()
    collection.insert_error = DuplicateKeyError("duplicate")
    with pytest.raises(registry.LegalConflictReviewRegistryRetryRequiredError):
        registry.persist_review(review(), collection, session=Session())


def test_unclassified_mongo_read_failure_is_persistence_unavailable() -> None:
    collection = Collection()
    collection.find_error = PyMongoError("offline")
    with pytest.raises(registry.LegalConflictReviewRegistryPersistenceUnavailableError):
        registry.get_review(
            "tenant-law",
            "review-1",
            collection,
            session=Session(),
        )


# ARTIFACT: test_legal_conflict_review_registry.py
# VERSION: v1.0.0-L8-8H-LEGAL-CONFLICT-REVIEW-REGISTRY-CERT
# AUTHORITY BOUNDARY: immutable review persistence/read evidence only
# TENANT POSTURE: all fake persistence predicates are exact tenant scoped
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/overflow/race/outage rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
