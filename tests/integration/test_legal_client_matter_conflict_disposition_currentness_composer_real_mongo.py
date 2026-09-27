"""Real-Mongo certificate for conflict-disposition currentness composition.

TITLE: WILSY OS Legal Client Matter Conflict Disposition Currentness Composer Real-Mongo Certificate
VERSION: v1.0.0-L9C6-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published registry/composer/projection chain against a
         writable UUID-isolated Mongo replica set without touching canonical
         data or creating currentness persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_conflict_disposition_currentness_composer_real_mongo.py
COLLABORATION / OWNERSHIP: L9C3 owns durable disposition history; L9C5 owns
                            pure currentness and read-only composition. This
                            certificate owns only disposable runtime evidence.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9C6-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
           covers physical indexes, active caller transactions, exact scope,
           time precedence, ambiguity, corruption rejection, deterministic
           recomposition and zero downstream/currentness writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Disposable synthetic opaque identifiers only. No
                             canonical URI, credentials, PII, bearer tokens or
                             raw evidence is printed or persisted outside the
                             disposable database.
TENANT BOUNDARY: Every composition uses exact tenant, matter, matter
                 fingerprint, client party and subject fingerprint filters.
AUTHORITY BOUNDARY: Runtime certificate only; no Engagement IAM, mandate,
                    Representation, Court, API, UI, Node or finance authority.
FINANCIAL AUTHORITY BOUNDARY: No financial mutation; Kennel EOS remains the
                              exclusive financial execution authority.
TRANSACTION BOUNDARY: Tests own disposable sessions and transactions. The
                      composer starts, commits and aborts none.
FAIL-CLOSED DECLARATION: Infrastructure unavailability skips explicitly for
                         operator execution; corrupt durable evidence and
                         invalid transactions fail closed.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import ast
import os
from pathlib import Path
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition import (
    LegalClientMatterConflictDisposition,
)
from tools.eos.legal_operations.domain.legal_client_matter_conflict_disposition_currentness import (
    LegalClientMatterConflictDispositionCurrentnessState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_conflict_disposition_currentness_composer import (
    LegalClientMatterConflictDispositionCurrentnessComposer,
    LegalClientMatterConflictDispositionCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_conflict_disposition_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 27, 20, 0, tzinfo=timezone.utc)
TENANT_A = "tenant-a-l9c6"
TENANT_B = "tenant-b-l9c6"
MATTER = "matter-l9c6"
MATTER_FP = "a" * 128
OTHER_MATTER_FP = "b" * 128
PARTY = "party-l9c6"
OTHER_PARTY = "party-other-l9c6"
SUBJECT = "c" * 128
OTHER_SUBJECT = "d" * 128


class ReadOnlyCountingCollection:
    """Proxy disposable collection that records reads and rejects writes."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.find_calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.write_calls = 0

    def with_options(self, **_options: Any) -> "ReadOnlyCountingCollection":
        return self

    def find(self, *args: Any, **kwargs: Any) -> Any:
        self.find_calls.append((args, kwargs))
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
    """Yield a UUID-isolated disposable database after topology preflight."""
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
            server_info = client.server_info()
            server_version = server_info.get("version")
            pymongo_version = getattr(__import__("pymongo"), "version", "unknown")
        except (PyMongoError, OSError) as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version
        assert isinstance(pymongo_version, str) and pymongo_version
        database_name = f"wilsy_l9c6_curr_comp_{uuid.uuid4().hex}"
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


def _disposition(
    *,
    tenant_id: str = TENANT_A,
    matter_id: str = MATTER,
    matter_fingerprint: str = MATTER_FP,
    party_id: str = PARTY,
    subject_fingerprint: str = SUBJECT,
    disposition_id: str = "disp-l9c6-1",
    review_id: str = "review-l9c6-1",
    review_fingerprint: str = "e" * 128,
    disposition: str = "ENGAGEMENT_PERMITTED",
    effective_offset: int = 0,
    screening_id: str = "screening-l9c6",
) -> LegalClientMatterConflictDisposition:
    """Build one valid synthetic immutable disposition row."""
    occurred = NOW + timedelta(minutes=effective_offset - 1)
    effective = NOW + timedelta(minutes=effective_offset)
    return LegalClientMatterConflictDisposition(
        disposition_id=disposition_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        screening_id=screening_id,
        screening_fingerprint="f" * 128,
        conflict_review_id=review_id,
        conflict_review_fingerprint=review_fingerprint,
        review_outcome="NO_CONFLICT_IDENTIFIED",
        client_party_id=party_id,
        subject_identity_fingerprint=subject_fingerprint,
        disposition=disposition,
        decision_actor_principal_id="principal-l9c6",
        authorization_evidence_reference="iam:l9c6:authorization",
        authorization_evidence_fingerprint="1" * 128,
        supporting_evidence_reference="review:l9c6:evidence",
        supporting_evidence_fingerprint="2" * 128,
        occurred_at=occurred,
        effective_from=effective,
        idempotency_key=f"idempotency:l9c6:{disposition_id}",
    )


def _commit(client: MongoClient[Any], collection: Any, value: LegalClientMatterConflictDisposition) -> None:
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_disposition(value, collection, session=session)
        session.commit_transaction()


def _compose(client: MongoClient[Any], collection: Any, *, evaluation_time: datetime = NOW + timedelta(minutes=1), **scope: str) -> Any:
    target = _disposition()
    values = {
        "tenant_id": scope.get("tenant_id", target.tenant_id),
        "case_matter_id": scope.get("case_matter_id", target.case_matter_id),
        "matter_fingerprint": scope.get("matter_fingerprint", target.matter_fingerprint),
        "client_party_id": scope.get("client_party_id", target.client_party_id),
        "subject_identity_fingerprint": scope.get("subject_identity_fingerprint", target.subject_identity_fingerprint),
    }
    with client.start_session() as session:
        with session.start_transaction():
            composer = LegalClientMatterConflictDispositionCurrentnessComposer(disposition_collection=collection)
            return composer.compose_currentness(**values, evaluation_time=evaluation_time, session=session)


def test_real_index_metadata_has_no_ttl_or_current_pointer(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Physical registry indexes match immutable history and no TTL/current index."""
    _, database, collection = mongo_context
    indexes = {entry["name"]: entry for entry in collection.list_indexes() if entry["name"] != "_id_"}
    assert database.name != "wilsy"
    assert set(indexes) == {
        registry.DISPOSITION_ID_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME, registry.REVIEW_LINEAGE_INDEX_NAME,
        registry.HISTORY_INDEX_NAME, registry.MATTER_FINGERPRINT_HISTORY_INDEX_NAME,
        registry.CLIENT_PARTY_HISTORY_INDEX_NAME, registry.SUBJECT_HISTORY_INDEX_NAME,
    }
    assert all("expireAfterSeconds" not in entry for entry in indexes.values())
    assert all("current" not in entry["name"].lower() for entry in indexes.values())


def test_real_transaction_requires_caller_active_transaction(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Missing and inactive caller sessions fail before registry reads."""
    client, _, collection = mongo_context
    composer = LegalClientMatterConflictDispositionCurrentnessComposer(disposition_collection=collection)
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError):
        composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT, NOW, None)
    with client.start_session() as session:
        with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT, NOW, session)


def test_real_empty_history_is_no_disposition(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Exact empty history is a non-positive projection and writes nothing."""
    client, _, collection = mongo_context
    result = _compose(client, collection)
    assert result.state is LegalClientMatterConflictDispositionCurrentnessState.NO_DISPOSITION
    assert collection.count_documents({}) == 0


@pytest.mark.parametrize(
    ("disposition", "expected"),
    [
        ("ENGAGEMENT_PERMITTED", LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED),
        ("ENGAGEMENT_PROHIBITED", LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PROHIBITED),
        ("ENGAGEMENT_UNRESOLVED", LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_UNRESOLVED),
    ],
)
def test_real_single_states_and_lineage(
    mongo_context: tuple[MongoClient[Any], Any, Any], disposition: str, expected: LegalClientMatterConflictDispositionCurrentnessState,
) -> None:
    """Each explicit durable state composes without reinterpretation."""
    client, _, collection = mongo_context
    value = _disposition(disposition=disposition)
    _commit(client, collection, value)
    result = _compose(client, collection)
    assert result.state is expected
    assert result.decisive_disposition_ids == (value.disposition_id,)
    assert result.decisive_disposition_fingerprints == (value.fingerprint,)
    assert result.decisive_screening_ids == (value.screening_id,)
    assert result.decisive_conflict_review_ids == (value.conflict_review_id,)
    assert result.is_engagement_permitted is (expected is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED)


def test_real_future_and_supersession_semantics(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Future evidence is excluded, then later effective evidence supersedes."""
    client, _, collection = mongo_context
    permitted = _disposition(disposition_id="disp-permitted", review_id="review-permitted", effective_offset=0)
    prohibited = _disposition(disposition="ENGAGEMENT_PROHIBITED", disposition_id="disp-prohibited", review_id="review-prohibited", effective_offset=10)
    _commit(client, collection, permitted)
    _commit(client, collection, prohibited)
    before = _compose(client, collection, evaluation_time=NOW + timedelta(minutes=5))
    after = _compose(client, collection, evaluation_time=NOW + timedelta(minutes=11))
    assert before.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED
    assert after.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PROHIBITED
    assert collection.count_documents({}) == 2


def test_real_unresolved_supersedes_permit(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """A later unresolved record removes stale positive authority."""
    client, _, collection = mongo_context
    _commit(client, collection, _disposition(disposition_id="disp-permitted", review_id="review-permitted"))
    _commit(client, collection, _disposition(disposition="ENGAGEMENT_UNRESOLVED", disposition_id="disp-unresolved", review_id="review-unresolved", effective_offset=10))
    result = _compose(client, collection, evaluation_time=NOW + timedelta(minutes=11))
    assert result.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_UNRESOLVED
    assert not result.is_engagement_permitted


@pytest.mark.parametrize(
    "states",
    [
        ("ENGAGEMENT_PERMITTED", "ENGAGEMENT_PERMITTED"),
        ("ENGAGEMENT_PERMITTED", "ENGAGEMENT_PROHIBITED"),
        ("ENGAGEMENT_PERMITTED", "ENGAGEMENT_UNRESOLVED"),
        ("ENGAGEMENT_PROHIBITED", "ENGAGEMENT_UNRESOLVED"),
    ],
)
def test_real_same_effective_identical_or_conflicting_states(
    mongo_context: tuple[MongoClient[Any], Any, Any], states: tuple[str, str],
) -> None:
    """Same-effective equal states resolve; differing states are ambiguous."""
    client, _, collection = mongo_context
    first = _disposition(disposition=states[0], disposition_id="disp-first", review_id="review-first", review_fingerprint="3" * 128, effective_offset=5)
    second = _disposition(disposition=states[1], disposition_id="disp-second", review_id="review-second", review_fingerprint="4" * 128, effective_offset=5)
    _commit(client, collection, first)
    _commit(client, collection, second)
    result = _compose(client, collection, evaluation_time=NOW + timedelta(minutes=6))
    expected = states[0] if states[0] == states[1] else "AMBIGUOUS"
    assert result.state.value == expected
    assert set(result.decisive_disposition_ids) == {first.disposition_id, second.disposition_id}


def test_real_tenant_and_context_isolation(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Overlapping IDs and nearby contexts cannot cross exact registry scope."""
    client, _, collection = mongo_context
    tenant_a = _disposition(tenant_id=TENANT_A, disposition_id="shared", review_id="review-a")
    tenant_b = _disposition(tenant_id=TENANT_B, disposition_id="shared", review_id="review-b")
    other_matter = _disposition(matter_id="other-matter", disposition_id="other-matter", review_id="review-other-matter")
    other_party = _disposition(party_id=OTHER_PARTY, disposition_id="other-party", review_id="review-other-party")
    other_subject = _disposition(subject_fingerprint=OTHER_SUBJECT, disposition_id="other-subject", review_id="review-other-subject")
    for value in (tenant_a, tenant_b, other_matter, other_party, other_subject):
        _commit(client, collection, value)
    result_a = _compose(client, collection, tenant_id=TENANT_A)
    result_b = _compose(client, collection, tenant_id=TENANT_B)
    assert result_a.decisive_disposition_fingerprints == (tenant_a.fingerprint,)
    assert result_b.decisive_disposition_fingerprints == (tenant_b.fingerprint,)
    assert tenant_b.fingerprint not in result_a.decisive_disposition_fingerprints
    assert tenant_a.fingerprint not in result_b.decisive_disposition_fingerprints
    assert _compose(client, collection, matter_fingerprint=OTHER_MATTER_FP).state is LegalClientMatterConflictDispositionCurrentnessState.NO_DISPOSITION
    assert _compose(client, collection, client_party_id=OTHER_PARTY).state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED
    assert _compose(client, collection, subject_identity_fingerprint=OTHER_SUBJECT).state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED


@pytest.mark.parametrize("field,value", [("fingerprint", "bad"), ("disposition", "NOT_A_STATE"), ("effective_from", "bad-time"), ("conflict_review_fingerprint", "bad-lineage")])
def test_real_corrupt_bson_fails_closed(mongo_context: tuple[MongoClient[Any], Any, Any], field: str, value: object) -> None:
    """Corrupt authoritative BSON cannot be skipped into a permit."""
    client, _, collection = mongo_context
    original = _disposition()
    _commit(client, collection, original)
    stored = collection.find_one({"tenant_id": original.tenant_id})
    assert isinstance(stored, dict)
    tampered = deepcopy(stored)
    tampered[field] = value
    collection.replace_one({"_id": stored["_id"]}, tampered)
    try:
        with client.start_session() as session:
            with session.start_transaction():
                composer = LegalClientMatterConflictDispositionCurrentnessComposer(disposition_collection=collection)
                with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError):
                    composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT, NOW, session)
    finally:
        collection.replace_one({"_id": stored["_id"]}, stored)


def test_real_same_session_and_zero_writes(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """One active caller session reaches the read and composition performs no writes."""
    client, _, collection = mongo_context
    _commit(client, collection, _disposition())
    proxy = ReadOnlyCountingCollection(collection)
    with client.start_session() as session:
        with session.start_transaction():
            composer = LegalClientMatterConflictDispositionCurrentnessComposer(disposition_collection=proxy)
            result = composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT, NOW + timedelta(minutes=1), session)
            assert proxy.find_calls and proxy.find_calls[-1][1]["session"] is session
            assert proxy.write_calls == 0
    assert result.state is LegalClientMatterConflictDispositionCurrentnessState.ENGAGEMENT_PERMITTED


def test_real_currentness_is_not_persisted_and_recomposition_is_deterministic(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Repeated unchanged snapshots produce identical evidence and no new collection."""
    client, database, collection = mongo_context
    _commit(client, collection, _disposition())
    first = _compose(client, collection)
    second = _compose(client, collection)
    assert first == second and first.fingerprint == second.fingerprint
    assert database.list_collection_names() == [registry.COLLECTION]
    row = collection.find_one({"tenant_id": TENANT_A})
    assert isinstance(row, dict)
    assert "currentness" not in row and "current" not in row and "latest" not in row


def test_real_naive_time_fails_closed(mongo_context: tuple[MongoClient[Any], Any, Any]) -> None:
    """Wall-clock-free composition rejects naive evaluation timestamps."""
    client, _, collection = mongo_context
    with pytest.raises(LegalClientMatterConflictDispositionCurrentnessComposerError):
        _compose(client, collection, evaluation_time=NOW.replace(tzinfo=None))


def test_real_static_authority_audit() -> None:
    """Composer has no downstream or transaction-owning imports."""
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_conflict_disposition_currentness_composer.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    imported = {
        node.module.split(".")[0]
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    imported.update(
        alias.name.split(".")[0]
        for node in ast.walk(module)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert imported.isdisjoint({"pymongo", "motor", "jwt", "requests", "httpx"})
    assert "datetime.now" not in source and "utcnow" not in source


# ARTIFACT: test_legal_client_matter_conflict_disposition_currentness_composer_real_mongo.py
# VERSION: v1.0.0-L9C6-CONFLICT-DISPOSITION-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable runtime evidence only; no production authority
# TENANT POSTURE: UUID-isolated database and exact five-dimensional context reads
# FAIL-CLOSED POSTURE: topology/corruption/transaction/scope failures cannot pass
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
