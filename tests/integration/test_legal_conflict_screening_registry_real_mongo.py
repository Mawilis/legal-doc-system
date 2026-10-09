"""Real-Mongo certificate for L8-8E durable conflict-screening registry.

TITLE: Legal Conflict Screening Registry Real-Mongo Certificate
VERSION: v1.0.0-L8-8E-LEGAL-CONFLICT-SCREENING-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable L8-8E screening persistence against one disposable
         writable Mongo replica set: physical indexes, commit/replay, rollback,
         tenant isolation, ordered histories/review queue, corruption rejection,
         and deterministic competing immutable identities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_conflict_screening_registry_real_mongo.py
CERTIFICATION / UPDATE DATE: 2026-09-25
TRANSACTION BOUNDARY: Test caller owns every session/transaction.
AUTHORITY BOUNDARY: Physical screening persistence/read evidence only; no legal
                    conflict determination, resolution, waiver or clearance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
FAIL-CLOSED DECLARATION: Once fixture yields, index, product, transaction,
                         replay, corruption and concurrency defects fail.
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


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 25, 18, 0, tzinfo=timezone.utc)
FP_SUBJECT = "a" * 128
FP_EVIDENCE = "b" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated collection after replica-set capability checks."""
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

        database = client[f"wilsy_l8_8e_screening_{uuid.uuid4().hex}"]
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


def _matter(tenant: str, matter_id: str) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def _party(
    tenant: str,
    *,
    matter_id: str,
    party_id: str,
    side: LegalMatterPartySide,
) -> Any:
    return register_legal_matter_party(
        matter=_matter(tenant, matter_id),
        party_id=party_id,
        party_kind=LegalMatterPartyKind.ORGANIZATION,
        party_side=side,
        matter_role=(
            LegalMatterPartyRole.CLIENT
            if side is LegalMatterPartySide.CLIENT_SIDE
            else LegalMatterPartyRole.RESPONDENT
        ),
        subject_reference="organization:acme",
        subject_identity_fingerprint=FP_SUBJECT,
        display_name="Acme Legal",
        registered_at=NOW,
        source_evidence_reference=f"party-source:{party_id}",
        source_evidence_fingerprint=FP_EVIDENCE,
    )


def _screening(
    tenant: str,
    *,
    screening_id: str,
    screened_at: datetime,
    with_match: bool,
) -> LegalConflictScreeningResult:
    source = _party(
        tenant,
        matter_id="matter-1",
        party_id="party-source",
        side=LegalMatterPartySide.CLIENT_SIDE,
    )
    occurrences = [source]
    if with_match:
        occurrences.append(
            _party(
                tenant,
                matter_id="matter-2",
                party_id="party-match",
                side=LegalMatterPartySide.ADVERSE_SIDE,
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


def _commit(
    client: MongoClient[Any],
    collection: Any,
    value: LegalConflictScreeningResult,
) -> LegalConflictScreeningResult:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.persist_screening(
                value,
                collection,
                session=session,
            )


def test_real_index_metadata_is_exact_and_has_no_ttl(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Certify all four physical index laws and immutable retention."""
    _, _, collection = mongo_context
    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
        if entry["name"] != "_id_"
    }
    assert set(indexes) == {
        registry.SCREENING_ID_INDEX_NAME,
        registry.SOURCE_HISTORY_INDEX_NAME,
        registry.SUBJECT_HISTORY_INDEX_NAME,
        registry.REVIEW_QUEUE_INDEX_NAME,
    }
    assert dict(indexes[registry.SCREENING_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "screening_id": 1,
    }
    assert indexes[registry.SCREENING_ID_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.SOURCE_HISTORY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "source_party_id": 1,
        "screened_at": -1,
    }
    assert dict(indexes[registry.SUBJECT_HISTORY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "subject_identity_fingerprint": 1,
        "screened_at": -1,
    }
    assert dict(indexes[registry.REVIEW_QUEUE_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "status": 1,
        "screened_at": -1,
    }
    assert all(
        entry.get("unique") is not True
        for name, entry in indexes.items()
        if name != registry.SCREENING_ID_INDEX_NAME
    )
    assert all("expireAfterSeconds" not in entry for entry in indexes.values())


def test_real_commit_replay_histories_review_queue_and_tenant_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Certify exact replay plus ordered tenant-scoped immutable read models."""
    client, _, collection = mongo_context
    tenant = f"tenant-a-{uuid.uuid4().hex}"
    foreign = f"tenant-b-{uuid.uuid4().hex}"
    old = _screening(
        tenant,
        screening_id="screening-old",
        screened_at=NOW,
        with_match=True,
    )
    mid = _screening(
        tenant,
        screening_id="screening-mid",
        screened_at=NOW + timedelta(minutes=1),
        with_match=True,
    )
    new = _screening(
        tenant,
        screening_id="screening-new",
        screened_at=NOW + timedelta(minutes=2),
        with_match=False,
    )
    foreign_value = _screening(
        foreign,
        screening_id="screening-foreign",
        screened_at=NOW + timedelta(minutes=3),
        with_match=True,
    )
    for value in (old, mid, new, foreign_value):
        assert _commit(client, collection, value) == value
    assert _commit(client, collection, old) == old

    with client.start_session() as session:
        with session.start_transaction():
            source = registry.list_source_screenings(
                tenant,
                "party-source",
                collection,
                session=session,
            )
            subject = registry.list_subject_screenings(
                tenant,
                FP_SUBJECT,
                collection,
                session=session,
            )
            review = registry.list_review_required(
                tenant,
                collection,
                session=session,
            )
            assert [value.screening_id for value in source] == [
                "screening-new",
                "screening-mid",
                "screening-old",
            ]
            assert [value.screening_id for value in subject] == [
                "screening-new",
                "screening-mid",
                "screening-old",
            ]
            assert [value.screening_id for value in review] == [
                "screening-mid",
                "screening-old",
            ]
            assert all(
                value.status is LegalConflictScreeningStatus.REVIEW_REQUIRED
                for value in review
            )
            with pytest.raises(
                registry.LegalConflictScreeningRegistryNotFoundError
            ):
                registry.get_screening(
                    foreign,
                    "screening-old",
                    collection,
                    session=session,
                )


def test_real_caller_abort_rolls_back_screening_insert(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Registry never steals transaction ownership from the caller."""
    client, _, collection = mongo_context
    tenant = f"tenant-abort-{uuid.uuid4().hex}"
    value = _screening(
        tenant,
        screening_id="screening-abort",
        screened_at=NOW,
        with_match=True,
    )
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_screening(value, collection, session=session)
        assert collection.count_documents(
            {"tenant_id": tenant},
            session=session,
        ) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0


def test_real_divergent_same_screening_identity_fails_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Immutable screening identity cannot be rebound to divergent evidence."""
    client, _, collection = mongo_context
    tenant = f"tenant-conflict-{uuid.uuid4().hex}"
    first = _screening(
        tenant,
        screening_id="screening-1",
        screened_at=NOW,
        with_match=False,
    )
    _commit(client, collection, first)
    divergent = _screening(
        tenant,
        screening_id="screening-1",
        screened_at=NOW,
        with_match=True,
    )
    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(
            registry.LegalConflictScreeningRegistryConflictError
        ):
            registry.persist_screening(
                divergent,
                collection,
                session=session,
            )
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_corruption_is_rejected_before_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Physical envelope/payload tampering cannot hydrate as screening truth."""
    client, _, collection = mongo_context
    tenant = f"tenant-corrupt-{uuid.uuid4().hex}"
    value = _screening(
        tenant,
        screening_id="screening-corrupt",
        screened_at=NOW,
        with_match=True,
    )
    _commit(client, collection, value)
    original = deepcopy(collection.find_one({"tenant_id": tenant}))
    assert isinstance(original, dict)

    collection.update_one(
        {"_id": original["_id"]},
        {"$set": {"screening_payload.screening_id": "tampered"}},
    )
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(
                registry.LegalConflictScreeningRegistryPersistedRecordInvalidError
            ):
                registry.get_screening(
                    tenant,
                    value.screening_id,
                    collection,
                    session=session,
                )
    collection.replace_one({"_id": original["_id"]}, original)


def test_real_competing_same_identity_has_one_durable_winner(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Two synchronized divergent creates cannot produce two screening rows."""
    client, _, collection = mongo_context
    tenant = f"tenant-race-{uuid.uuid4().hex}"
    left = _screening(
        tenant,
        screening_id="screening-race",
        screened_at=NOW,
        with_match=False,
    )
    right = _screening(
        tenant,
        screening_id="screening-race",
        screened_at=NOW,
        with_match=True,
    )
    barrier = Barrier(2)

    def contender(value: LegalConflictScreeningResult) -> str:
        with client.start_session() as session:
            session.start_transaction()
            barrier.wait()
            try:
                registry.persist_screening(
                    value,
                    collection,
                    session=session,
                )
                session.commit_transaction()
                return "COMMITTED"
            except registry.LegalConflictScreeningRegistryRetryRequiredError:
                if session.in_transaction:
                    session.abort_transaction()
                return "RETRY_REQUIRED"
            except registry.LegalConflictScreeningRegistryConflictError:
                if session.in_transaction:
                    session.abort_transaction()
                return "CONFLICT"
            except registry.LegalConflictScreeningRegistryPersistenceUnavailableError as error:
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
    assert row["screening_id"] == "screening-race"


# ARTIFACT: test_legal_conflict_screening_registry_real_mongo.py
# VERSION: v1.0.0-L8-8E-LEGAL-CONFLICT-SCREENING-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: physical immutable screening persistence/read evidence only
# TENANT POSTURE: UUID-isolated database and exact tenant-scoped indexes/queries
# FAIL-CLOSED POSTURE: rollback/divergence/corruption/concurrency cannot invent screening truth
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
