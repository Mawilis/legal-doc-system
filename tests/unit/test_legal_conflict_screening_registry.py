"""Direct certificate for L8-8E durable legal conflict-screening registry.

VERSION: v1.0.0-L8-8E-LEGAL-CONFLICT-SCREENING-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_conflict_screening_registry.py
AUTHORITY BOUNDARY: Immutable screening persistence/read evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_conflict_screening import (
    LegalConflictScreeningResult,
    LegalConflictScreeningStatus,
    build_legal_conflict_screening,
)
from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import legal_conflict_screening_registry as registry


NOW = datetime(2026, 9, 25, 17, 0, tzinfo=timezone.utc)
FP_SUBJECT = "a" * 128
FP_EVIDENCE = "b" * 128
FP_OTHER = "c" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor(list[dict[str, Any]]):
    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        rows = list(self)
        for field, direction in reversed(keys):
            rows.sort(
                key=lambda row: row.get(field),
                reverse=direction < 0,
            )
        return Cursor(rows)

    def limit(self, value: int) -> "Cursor":
        return Cursor(self[:value])


class Result:
    def __init__(self, inserted_id: str = "inserted") -> None:
        self.inserted_id = inserted_id


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
            return Cursor(
                [{"placeholder": index} for index in range(self.overflow_count)]
            )
        return Cursor(
            [
                deepcopy(row)
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ]
        )

    def insert_one(self, document: dict[str, object], *, session: Any) -> Result:
        self.sessions.append(session)
        if self.insert_error is not None:
            raise self.insert_error
        row = deepcopy(document)
        row["_id"] = f"id-{len(self.rows) + 1}"
        self.rows.append(row)
        return Result()


def matter(tenant: str, matter_id: str) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def party(
    *,
    tenant: str = "tenant-law",
    matter_id: str = "matter-1",
    party_id: str = "party-1",
    side: LegalMatterPartySide = LegalMatterPartySide.CLIENT_SIDE,
    subject_fp: str = FP_SUBJECT,
) -> Any:
    return register_legal_matter_party(
        matter=matter(tenant, matter_id),
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=side,
        matter_role=(
            LegalMatterPartyRole.CLIENT
            if side is LegalMatterPartySide.CLIENT_SIDE
            else LegalMatterPartyRole.RESPONDENT
        ),
        subject_reference="organization:acme",
        subject_identity_fingerprint=subject_fp,
        display_name="Acme Legal",
        registered_at=NOW,
        source_evidence_reference=f"party-source:{party_id}",
        source_evidence_fingerprint=FP_EVIDENCE,
    )


def screening(
    *,
    tenant: str = "tenant-law",
    screening_id: str = "screening-1",
    source_party_id: str = "party-1",
    screened_at: datetime = NOW,
    with_match: bool = False,
    subject_fp: str = FP_SUBJECT,
) -> LegalConflictScreeningResult:
    source = party(
        tenant=tenant,
        party_id=source_party_id,
        subject_fp=subject_fp,
    )
    occurrences = [source]
    if with_match:
        occurrences.append(
            party(
                tenant=tenant,
                matter_id="matter-2",
                party_id=f"{source_party_id}-match",
                side=LegalMatterPartySide.ADVERSE_SIDE,
                subject_fp=subject_fp,
            )
        )
    return build_legal_conflict_screening(
        source_party=source,
        occurrences=tuple(occurrences),
        screening_id=screening_id,
        screened_at=screened_at,
        source_evidence_reference=f"screening-source:{screening_id}",
        source_evidence_fingerprint=FP_EVIDENCE,
    )


def test_index_contract_is_exact_and_has_no_mutable_resolution_index() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert collection.indexes == [
        {
            "key": [("tenant_id", 1), ("screening_id", 1)],
            "unique": True,
            "name": registry.SCREENING_ID_INDEX_NAME,
        },
        {
            "key": [
                ("tenant_id", 1),
                ("source_party_id", 1),
                ("screened_at", -1),
            ],
            "unique": False,
            "name": registry.SOURCE_HISTORY_INDEX_NAME,
        },
        {
            "key": [
                ("tenant_id", 1),
                ("subject_identity_fingerprint", 1),
                ("screened_at", -1),
            ],
            "unique": False,
            "name": registry.SUBJECT_HISTORY_INDEX_NAME,
        },
        {
            "key": [
                ("tenant_id", 1),
                ("status", 1),
                ("screened_at", -1),
            ],
            "unique": False,
            "name": registry.REVIEW_QUEUE_INDEX_NAME,
        },
    ]
    rendered = repr(collection.indexes).lower()
    for forbidden in ("resolved", "waived", "clearance", "ethical_wall"):
        assert forbidden not in rendered


@pytest.mark.parametrize(
    "operation",
    ["persist", "get", "source", "subject", "review"],
)
def test_every_operational_path_requires_active_caller_transaction(
    operation: str,
) -> None:
    collection = Collection()
    value = screening(with_match=True)
    with pytest.raises(
        registry.LegalConflictScreeningRegistryTransactionRequiredError
    ):
        if operation == "persist":
            registry.persist_screening(value, collection, session=None)
        elif operation == "get":
            registry.get_screening(
                value.tenant_id,
                value.screening_id,
                collection,
                session=Session(False),
            )
        elif operation == "source":
            registry.list_source_screenings(
                value.tenant_id,
                value.source_party_id,
                collection,
                session=None,
            )
        elif operation == "subject":
            registry.list_subject_screenings(
                value.tenant_id,
                value.subject_identity_fingerprint,
                collection,
                session=Session(False),
            )
        else:
            registry.list_review_required(
                value.tenant_id,
                collection,
                session=None,
            )


def test_create_exact_replay_and_session_propagation() -> None:
    collection = Collection()
    session = Session()
    value = screening(with_match=True)
    created = registry.persist_screening(value, collection, session=session)
    replay = registry.persist_screening(value, collection, session=session)
    assert created == replay == value
    assert len(collection.rows) == 1
    assert collection.sessions
    assert all(item is session for item in collection.sessions)


def test_divergent_same_screening_identity_fails_closed() -> None:
    collection = Collection()
    session = Session()
    first = screening(with_match=False)
    registry.persist_screening(first, collection, session=session)
    divergent = screening(
        screening_id=first.screening_id,
        with_match=True,
    )
    with pytest.raises(
        registry.LegalConflictScreeningRegistryConflictError
    ) as raised:
        registry.persist_screening(
            divergent,
            collection,
            session=session,
        )
    assert raised.value.code == "L8_8E_SCREENING_CONFLICT"
    assert len(collection.rows) == 1


def test_tenant_isolation_histories_review_queue_and_ordering() -> None:
    collection = Collection()
    session = Session()
    values = [
        screening(
            screening_id="screening-old",
            screened_at=NOW,
            with_match=True,
        ),
        screening(
            screening_id="screening-new",
            screened_at=NOW + timedelta(minutes=2),
            with_match=False,
        ),
        screening(
            screening_id="screening-mid",
            screened_at=NOW + timedelta(minutes=1),
            with_match=True,
        ),
        screening(
            tenant="tenant-other",
            screening_id="screening-foreign",
            screened_at=NOW + timedelta(minutes=3),
            with_match=True,
        ),
    ]
    for value in values:
        registry.persist_screening(value, collection, session=session)

    source = registry.list_source_screenings(
        "tenant-law",
        "party-1",
        collection,
        session=session,
    )
    assert [value.screening_id for value in source] == [
        "screening-new",
        "screening-mid",
        "screening-old",
    ]

    subject = registry.list_subject_screenings(
        "tenant-law",
        FP_SUBJECT,
        collection,
        session=session,
    )
    assert [value.screening_id for value in subject] == [
        "screening-new",
        "screening-mid",
        "screening-old",
    ]

    review = registry.list_review_required(
        "tenant-law",
        collection,
        session=session,
    )
    assert [value.screening_id for value in review] == [
        "screening-mid",
        "screening-old",
    ]
    assert all(
        value.status is LegalConflictScreeningStatus.REVIEW_REQUIRED
        for value in review
    )

    with pytest.raises(registry.LegalConflictScreeningRegistryNotFoundError):
        registry.get_screening(
            "tenant-other",
            "screening-old",
            collection,
            session=session,
        )


def test_corrupt_payload_and_envelope_reject_before_projection() -> None:
    collection = Collection()
    session = Session()
    value = screening(with_match=True)
    registry.persist_screening(value, collection, session=session)
    pristine = deepcopy(collection.rows[0])

    collection.rows[0]["screening_payload"]["screening_id"] = "tampered"
    with pytest.raises(
        registry.LegalConflictScreeningRegistryPersistedRecordInvalidError
    ):
        registry.get_screening(
            value.tenant_id,
            value.screening_id,
            collection,
            session=session,
        )

    collection.rows[0] = deepcopy(pristine)
    collection.rows[0]["status"] = LegalConflictScreeningStatus.NO_MATCH_FOUND.value
    with pytest.raises(
        registry.LegalConflictScreeningRegistryPersistedRecordInvalidError
    ) as raised:
        registry.get_screening(
            value.tenant_id,
            value.screening_id,
            collection,
            session=session,
        )
    assert raised.value.code == "L8_8E_RECORD_CORRELATION_INVALID"


@pytest.mark.parametrize(
    ("kind", "limit", "code"),
    [
        (
            "source",
            registry.MAX_SOURCE_SCREENINGS,
            "L8_8E_SOURCE_SCREENING_LIMIT_EXCEEDED",
        ),
        (
            "subject",
            registry.MAX_SUBJECT_SCREENINGS,
            "L8_8E_SUBJECT_SCREENING_LIMIT_EXCEEDED",
        ),
        (
            "review",
            registry.MAX_REVIEW_QUEUE,
            "L8_8E_REVIEW_QUEUE_LIMIT_EXCEEDED",
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
    value = screening(with_match=True)
    if kind == "source":
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "source_party_id": value.source_party_id,
        }
        call = lambda: registry.list_source_screenings(
            value.tenant_id,
            value.source_party_id,
            collection,
            session=session,
        )
    elif kind == "subject":
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "subject_identity_fingerprint": value.subject_identity_fingerprint,
        }
        call = lambda: registry.list_subject_screenings(
            value.tenant_id,
            value.subject_identity_fingerprint,
            collection,
            session=session,
        )
    else:
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "status": LegalConflictScreeningStatus.REVIEW_REQUIRED.value,
        }
        call = lambda: registry.list_review_required(
            value.tenant_id,
            collection,
            session=session,
        )
    collection.overflow_count = limit + 1
    with pytest.raises(
        registry.LegalConflictScreeningRegistryPersistedRecordInvalidError
    ) as raised:
        call()
    assert raised.value.code == code


def test_duplicate_key_insert_race_requires_whole_transaction_retry() -> None:
    collection = Collection()
    collection.insert_error = DuplicateKeyError("duplicate")
    with pytest.raises(
        registry.LegalConflictScreeningRegistryRetryRequiredError
    ) as raised:
        registry.persist_screening(
            screening(with_match=True),
            collection,
            session=Session(),
        )
    assert raised.value.code == "L8_8E_WHOLE_TRANSACTION_RETRY_REQUIRED"


def test_unclassified_mongo_read_failure_is_persistence_unavailable() -> None:
    collection = Collection()
    collection.find_error = PyMongoError("offline")
    with pytest.raises(
        registry.LegalConflictScreeningRegistryPersistenceUnavailableError
    ) as raised:
        registry.get_screening(
            "tenant-law",
            "screening-1",
            collection,
            session=Session(),
        )
    assert raised.value.code == "L8_8E_PERSISTENCE_UNAVAILABLE"


def test_public_registry_surface_has_no_resolution_or_clearance_mutators() -> None:
    public_names = set(registry.LegalConflictScreeningRegistry.__dict__)
    forbidden = {
        "resolve",
        "waive",
        "clear",
        "approve",
        "decline",
        "establish_ethical_wall",
        "accept_client",
        "authorize_representation",
    }
    assert public_names.isdisjoint(forbidden)


# ARTIFACT: test_legal_conflict_screening_registry.py
# VERSION: v1.0.0-L8-8E-LEGAL-CONFLICT-SCREENING-REGISTRY-CERT
# AUTHORITY BOUNDARY: immutable screening persistence/read evidence only
# TENANT POSTURE: every fake persistence query is exact tenant scoped
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/overflow/race/outage rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
