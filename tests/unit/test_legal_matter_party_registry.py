"""Direct certificate for L8-8B durable legal matter-party registry.

VERSION: v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_party_registry.py
AUTHORITY BOUNDARY: Registry persistence/read evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_matter_party import (
    LegalMatterParty,
    LegalMatterPartyKind,
    LegalMatterPartyRole,
    LegalMatterPartySide,
    register_legal_matter_party,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import legal_matter_party_registry as registry


NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor(list[dict[str, Any]]):
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
            return Cursor([{"placeholder": index} for index in range(self.overflow_count)])
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


def matter(tenant: str = "tenant-law", matter_id: str = "matter-1") -> CaseMatter:
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
    subject_fp: str = FP_A,
    subject_ref: str = "organization:acme",
    display_name: str = "Acme Legal",
) -> LegalMatterParty:
    return register_legal_matter_party(
        matter=matter(tenant, matter_id),
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=LegalMatterPartySide.CLIENT_SIDE,
        matter_role=LegalMatterPartyRole.CLIENT,
        subject_reference=subject_ref,
        subject_identity_fingerprint=subject_fp,
        display_name=display_name,
        registered_at=NOW,
        source_evidence_reference=f"party-source:{party_id}",
        source_evidence_fingerprint=FP_B,
    )


def test_index_contract_is_exact_and_tenant_scoped() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert collection.indexes == [
        {
            "key": [("tenant_id", 1), ("party_id", 1)],
            "unique": True,
            "name": registry.PARTY_ID_INDEX_NAME,
        },
        {
            "key": [
                ("tenant_id", 1),
                ("case_matter_id", 1),
                ("subject_identity_fingerprint", 1),
            ],
            "unique": True,
            "name": registry.MATTER_SUBJECT_INDEX_NAME,
        },
        {
            "key": [("tenant_id", 1), ("case_matter_id", 1)],
            "unique": False,
            "name": registry.MATTER_LOOKUP_INDEX_NAME,
        },
        {
            "key": [("tenant_id", 1), ("subject_identity_fingerprint", 1)],
            "unique": False,
            "name": registry.SUBJECT_LOOKUP_INDEX_NAME,
        },
    ]


@pytest.mark.parametrize(
    "operation",
    ["persist", "get", "list", "subject"],
)
def test_every_operational_path_requires_active_caller_transaction(
    operation: str,
) -> None:
    collection = Collection()
    value = party()
    with pytest.raises(registry.LegalMatterPartyRegistryTransactionRequiredError):
        if operation == "persist":
            registry.persist_party(value, collection, session=None)
        elif operation == "get":
            registry.get_party(value.tenant_id, value.party_id, collection, session=Session(False))
        elif operation == "list":
            registry.list_matter_parties(
                value.tenant_id,
                value.case_matter_id,
                collection,
                session=None,
            )
        else:
            registry.find_subject_occurrences(
                value.tenant_id,
                value.subject_identity_fingerprint,
                collection,
                session=Session(False),
            )


def test_create_exact_replay_and_session_propagation() -> None:
    collection = Collection()
    session = Session()
    value = party()
    created = registry.persist_party(value, collection, session=session)
    replay = registry.persist_party(value, collection, session=session)
    assert created == replay == value
    assert len(collection.rows) == 1
    assert collection.sessions
    assert all(item is session for item in collection.sessions)


def test_divergent_same_party_identity_fails_closed() -> None:
    collection = Collection()
    session = Session()
    first = party()
    registry.persist_party(first, collection, session=session)
    divergent = party(display_name="Different Display")
    with pytest.raises(registry.LegalMatterPartyRegistryConflictError) as raised:
        registry.persist_party(divergent, collection, session=session)
    assert raised.value.code == "L8_8B_PARTY_CONFLICT"
    assert len(collection.rows) == 1


def test_same_matter_subject_cannot_hide_behind_second_party_id() -> None:
    collection = Collection()
    session = Session()
    registry.persist_party(party(), collection, session=session)
    second = party(party_id="party-2")
    with pytest.raises(registry.LegalMatterPartyRegistryConflictError) as raised:
        registry.persist_party(second, collection, session=session)
    assert raised.value.code == "L8_8B_MATTER_SUBJECT_CONFLICT"
    assert len(collection.rows) == 1


def test_tenant_isolation_and_deterministic_matter_subject_reads() -> None:
    collection = Collection()
    session = Session()
    values = [
        party(party_id="party-b", subject_fp=FP_A, subject_ref="organization:acme"),
        party(
            matter_id="matter-2",
            party_id="party-a",
            subject_fp=FP_A,
            subject_ref="organization:acme",
        ),
        party(
            tenant="tenant-other",
            party_id="party-z",
            subject_fp=FP_A,
            subject_ref="organization:acme",
        ),
        party(
            party_id="party-c",
            subject_fp=FP_C,
            subject_ref="organization:other",
        ),
    ]
    for value in values:
        registry.persist_party(value, collection, session=session)

    matter_values = registry.list_matter_parties(
        "tenant-law",
        "matter-1",
        collection,
        session=session,
    )
    assert [item.party_id for item in matter_values] == ["party-b", "party-c"]

    occurrences = registry.find_subject_occurrences(
        "tenant-law",
        FP_A,
        collection,
        session=session,
    )
    assert [(item.case_matter_id, item.party_id) for item in occurrences] == [
        ("matter-1", "party-b"),
        ("matter-2", "party-a"),
    ]

    with pytest.raises(registry.LegalMatterPartyRegistryNotFoundError):
        registry.get_party(
            "tenant-other",
            "party-b",
            collection,
            session=session,
        )


def test_corrupt_persisted_payload_or_envelope_rejects() -> None:
    collection = Collection()
    session = Session()
    value = party()
    registry.persist_party(value, collection, session=session)
    pristine = deepcopy(collection.rows[0])

    collection.rows[0]["party_payload"]["display_name"] = "Tampered"
    with pytest.raises(registry.LegalMatterPartyRegistryPersistedRecordInvalidError):
        registry.get_party(value.tenant_id, value.party_id, collection, session=session)

    collection.rows[0] = deepcopy(pristine)
    collection.rows[0]["matter_fingerprint"] = FP_C
    with pytest.raises(registry.LegalMatterPartyRegistryPersistedRecordInvalidError) as raised:
        registry.get_party(value.tenant_id, value.party_id, collection, session=session)
    assert raised.value.code == "L8_8B_RECORD_CORRELATION_INVALID"


@pytest.mark.parametrize(
    ("query_kind", "limit", "code"),
    [
        ("matter", registry.MAX_MATTER_PARTIES, "L8_8B_MATTER_PARTY_LIMIT_EXCEEDED"),
        (
            "subject",
            registry.MAX_SUBJECT_OCCURRENCES,
            "L8_8B_SUBJECT_OCCURRENCE_LIMIT_EXCEEDED",
        ),
    ],
)
def test_bounded_query_overflow_fails_closed(
    query_kind: str,
    limit: int,
    code: str,
) -> None:
    collection = Collection()
    session = Session()
    value = party()
    if query_kind == "matter":
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "case_matter_id": value.case_matter_id,
        }
        collection.overflow_count = limit + 1
        call = lambda: registry.list_matter_parties(
            value.tenant_id,
            value.case_matter_id,
            collection,
            session=session,
        )
    else:
        collection.overflow_query = {
            "tenant_id": value.tenant_id,
            "subject_identity_fingerprint": value.subject_identity_fingerprint,
        }
        collection.overflow_count = limit + 1
        call = lambda: registry.find_subject_occurrences(
            value.tenant_id,
            value.subject_identity_fingerprint,
            collection,
            session=session,
        )
    with pytest.raises(registry.LegalMatterPartyRegistryPersistedRecordInvalidError) as raised:
        call()
    assert raised.value.code == code


def test_duplicate_key_insert_race_requires_whole_transaction_retry() -> None:
    collection = Collection()
    collection.insert_error = DuplicateKeyError("duplicate")
    with pytest.raises(registry.LegalMatterPartyRegistryRetryRequiredError) as raised:
        registry.persist_party(party(), collection, session=Session())
    assert raised.value.code == "L8_8B_WHOLE_TRANSACTION_RETRY_REQUIRED"


def test_unclassified_mongo_read_failure_is_persistence_unavailable() -> None:
    collection = Collection()
    collection.find_error = PyMongoError("offline")
    with pytest.raises(registry.LegalMatterPartyRegistryPersistenceUnavailableError) as raised:
        registry.get_party("tenant-law", "party-1", collection, session=Session())
    assert raised.value.code == "L8_8B_PERSISTENCE_UNAVAILABLE"


# ARTIFACT: test_legal_matter_party_registry.py
# VERSION: v1.0.0-L8-8B-LEGAL-MATTER-PARTY-REGISTRY-CERT
# AUTHORITY BOUNDARY: registry persistence/read evidence only
# TENANT POSTURE: all fake persistence predicates are exact tenant scoped
# FAIL-CLOSED POSTURE: transaction/corruption/divergence/overflow/race/outage rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
