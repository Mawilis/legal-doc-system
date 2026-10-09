"""Real-Mongo certificate for L9C11-P5 Engagement currentness composition.

TITLE: WILSY OS Legal Engagement Currentness Composer Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P5-ENGAGEMENT-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published P3 domain, P4 composer and immutable Engagement
         registry against a writable UUID-isolated Mongo replica set without
         touching canonical data.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_engagement_currentness_real_mongo.py
COLLABORATION / OWNERSHIP: P1 owns durable Engagement history; P3 owns pure
                            currentness semantics; P4 owns one exact read and
                            delegation. This certificate owns disposable
                            runtime evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P5 certifies sanctioned topology, physical indexes,
           caller-owned transactions, exact history reads, state parity,
           tenant/lineage isolation, durable corruption rejection, snapshot
           behavior and zero composer writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only. URI, credentials,
                             durable payloads and bearer secrets are never
                             printed.
TENANT BOUNDARY: Every composition uses exact tenant, matter, fingerprint,
                 client-party and subject-fingerprint lineage.
AUTHORITY BOUNDARY: Runtime certificate only. No Representation, IAM, Court,
                    HTTP, UI, Node or financial authority is read or changed.
TRANSACTION BOUNDARY: The certificate owns disposable session lifecycle; the
                      composer owns none of it.
FAIL-CLOSED DECLARATION: Unavailable infrastructure skips explicitly for
                         operator runtime; invalid transactions, malformed
                         durable rows and cross-lineage evidence fail closed.
"""
from __future__ import annotations

import ast
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

from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import (
    LegalClientMatterEngagementCurrentnessState,
    project_legal_client_matter_engagement_currentness,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_engagement_currentness_composer import (
    LegalClientMatterEngagementCurrentnessComposer,
    LegalClientMatterEngagementCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT_A = "tenant-l9c11-p5-a"
TENANT_B = "tenant-l9c11-p5-b"
MATTER = "matter-l9c11-p5"
OTHER_MATTER = "matter-other-l9c11-p5"
MATTER_FP = "a" * 128
OTHER_MATTER_FP = "b" * 128
PARTY = "party-l9c11-p5"
OTHER_PARTY = "party-other-l9c11-p5"
SUBJECT_FP = "c" * 128
OTHER_SUBJECT_FP = "d" * 128


class CountingCollection:
    """Real collection proxy recording reads and rejecting composer writes."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.find_calls: list[tuple[dict[str, object], dict[str, object]]] = []
        self.write_calls = 0

    def with_options(self, **_options: Any) -> "CountingCollection":
        return self

    def find(self, query: dict[str, object], **kwargs: object) -> Any:
        self.find_calls.append((dict(query), dict(kwargs)))
        return self.inner.find(query, **kwargs)

    def insert_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("currentness composer attempted insert")

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("currentness composer attempted update")

    def delete_many(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("currentness composer attempted delete")

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield a writable UUID-isolated database on the sanctioned replica set."""
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
            import pymongo

            pymongo_version = pymongo.version
        except (PyMongoError, OSError) as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version
        assert isinstance(pymongo_version, str) and pymongo_version
        database_name = f"wilsy_l9c11_engcur_{uuid.uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        collection = database.get_collection(
            registry.COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        registry.ensure_indexes(collection)
        registry.ensure_indexes(collection)
        yield client, database, collection
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _engagement(
    *,
    tenant_id: str = TENANT_A,
    engagement_id: str = "engagement-l9c11-p5-1",
    idempotency_key: str | None = None,
    effective_offset: int = 5,
    case_matter_id: str = MATTER,
    matter_fingerprint: str = MATTER_FP,
    client_party_id: str = PARTY,
    subject_identity_fingerprint: str = SUBJECT_FP,
) -> LegalClientMatterEngagement:
    """Construct one valid immutable Engagement through the domain API."""
    identity = idempotency_key or f"idempotency:{engagement_id}"
    effective = BASE + timedelta(minutes=effective_offset)
    return LegalClientMatterEngagement(
        engagement_id=engagement_id,
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=client_party_id,
        subject_reference="client:subject-l9c11-p5",
        subject_identity_fingerprint=subject_identity_fingerprint,
        acting_capacity_id="capacity-l9c11-p5",
        acting_capacity_fingerprint="e" * 128,
        client_acceptance_id="acceptance-l9c11-p5",
        client_acceptance_fingerprint="f" * 128,
        instrument_id="instrument-l9c11-p5",
        version="v1",
        instrument_fingerprint="1" * 128,
        content_fingerprint="2" * 128,
        mandate_id="mandate-l9c11-p5",
        mandate_scope="scope:limited",
        mandate_fingerprint="3" * 128,
        conflict_disposition_id="conflict-l9c11-p5",
        conflict_disposition_fingerprint="4" * 128,
        firm_decision_id=f"firm-decision:{engagement_id}",
        decision_actor_principal_id="principal-l9c11-p5",
        firm_decision_fingerprint="5" * 128,
        authorization_evidence_reference="evidence:authorization-l9c11-p5",
        authorization_evidence_fingerprint="6" * 128,
        source_evidence_reference=f"evidence:formation:{engagement_id}",
        source_evidence_fingerprint="7" * 128,
        effective_from=effective,
        idempotency_key=identity,
    )


def _commit(client: MongoClient[Any], collection: Any, value: LegalClientMatterEngagement) -> None:
    """Persist one row while the certificate owns the caller transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            registry.persist_engagement(value, collection, session=session)


def _compose(
    client: MongoClient[Any],
    collection: Any,
    *,
    evaluation_time: datetime = BASE + timedelta(hours=1),
    session: Any | None = None,
    target_collection: Any | None = None,
    **scope: str,
) -> Any:
    """Compose exact lineage, optionally inside a supplied session."""
    owned = session is None
    transaction = client.start_session() if owned else session
    assert transaction is not None
    try:
        if owned:
            transaction.start_transaction()
        composer = LegalClientMatterEngagementCurrentnessComposer(
            engagement_collection=target_collection or collection,
        )
        return composer.compose_currentness(
            scope.get("tenant_id", TENANT_A),
            scope.get("case_matter_id", MATTER),
            scope.get("matter_fingerprint", MATTER_FP),
            scope.get("client_party_id", PARTY),
            scope.get("subject_identity_fingerprint", SUBJECT_FP),
            evaluation_time,
            transaction,
        )
    finally:
        if owned:
            transaction.abort_transaction()
            transaction.end_session()


def test_real_topology_indexes_and_no_current_pointer(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """The sanctioned replica set and physical registry indexes are exact."""
    _, database, collection = mongo_context
    indexes = {
        item["name"]: item
        for item in collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert database.name != "wilsy"
    collections = set(database.list_collection_names())
    assert registry.COLLECTION in collections
    assert not any("current" in name.lower() for name in collections)
    assert set(indexes) == {
        registry.ENGAGEMENT_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }
    assert indexes[registry.ENGAGEMENT_ID_INDEX_NAME].get("unique") is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert indexes[registry.HISTORY_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in indexes.values())
    assert all("current" not in item["name"].lower() for item in indexes.values())


def test_real_transaction_required_and_session_is_caller_owned(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Missing/inactive sessions reject and active callers retain lifecycle."""
    client, _, collection = mongo_context
    composer = LegalClientMatterEngagementCurrentnessComposer(
        engagement_collection=collection,
    )
    with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError):
        composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, BASE, None)
    with client.start_session() as inactive:
        with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, BASE, inactive)
    with client.start_session() as session:
        session.start_transaction()
        result = composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, BASE, session)
        assert result.state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT
        assert session.in_transaction is True
        session.abort_transaction()


def test_real_exact_history_read_and_zero_composer_writes(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """One read carries the exact five-field filter and same session."""
    client, _, collection = mongo_context
    value = _engagement()
    _commit(client, collection, value)
    counted = CountingCollection(collection)
    with client.start_session() as session:
        session.start_transaction()
        result = _compose(client, collection, session=session, target_collection=counted)
        assert result.state is LegalClientMatterEngagementCurrentnessState.CURRENT
        assert len(counted.find_calls) == 1
        query, kwargs = counted.find_calls[0]
        assert query == {
            "tenant_id": TENANT_A,
            "case_matter_id": MATTER,
            "matter_fingerprint": MATTER_FP,
            "client_party_id": PARTY,
            "subject_identity_fingerprint": SUBJECT_FP,
        }
        assert kwargs["session"] is session
        assert counted.write_calls == 0
        assert session.in_transaction is True
        session.abort_transaction()


def test_real_empty_single_future_and_eligible_plus_future_states(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Empty, future-only and eligible-plus-future states pass through P3."""
    client, _, collection = mongo_context
    assert _compose(client, collection, evaluation_time=BASE).state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT
    _commit(client, collection, _engagement(engagement_id="future", effective_offset=120))
    assert _compose(client, collection, evaluation_time=BASE + timedelta(minutes=60)).state is LegalClientMatterEngagementCurrentnessState.NO_ENGAGEMENT
    eligible = _engagement(engagement_id="eligible", effective_offset=5)
    _commit(client, collection, eligible)
    result = _compose(client, collection, evaluation_time=BASE + timedelta(minutes=60))
    assert result.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert result.decisive_engagement_id == eligible.engagement_id
    assert result.decisive_engagement_fingerprint == eligible.fingerprint
    assert result.decisive_effective_from == eligible.effective_from


def test_real_exact_duplicate_replay_is_one_row_and_current(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Registry uniqueness prevents physical duplicates; replay stays current."""
    client, _, collection = mongo_context
    value = _engagement()
    _commit(client, collection, value)
    _commit(client, collection, value)
    assert collection.count_documents({}) == 1
    result = _compose(client, collection)
    assert result.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert result.normalized_engagement_count == 1


def test_real_distinct_eligible_rows_are_ambiguous_without_supersession(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Later and same-effective distinct immutable rows never latest-win."""
    client, _, collection = mongo_context
    earlier = _engagement(engagement_id="earlier", effective_offset=5)
    later = _engagement(engagement_id="later", effective_offset=10)
    _commit(client, collection, earlier)
    _commit(client, collection, later)
    result = _compose(client, collection)
    assert result.state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS
    assert result.decisive_engagement_id is None

    same_effective_db = client[f"wilsy_l9c11_engcur_same_{uuid.uuid4().hex}"]
    try:
        same_effective_collection = same_effective_db[registry.COLLECTION]
        registry.ensure_indexes(same_effective_collection)
        _commit(client, same_effective_collection, _engagement(engagement_id="same-a"))
        _commit(client, same_effective_collection, _engagement(engagement_id="same-b"))
        assert _compose(client, same_effective_collection).state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS
    finally:
        client.drop_database(same_effective_db.name)


def test_real_tenant_and_lineage_isolation(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Neighboring tenant and one-field lineage rows cannot leak into scope."""
    client, _, collection = mongo_context
    _commit(client, collection, _engagement(engagement_id="exact"))
    _commit(client, collection, _engagement(tenant_id=TENANT_B, engagement_id="tenant-neighbor"))
    _commit(client, collection, _engagement(engagement_id="matter-neighbor", case_matter_id=OTHER_MATTER))
    _commit(client, collection, _engagement(engagement_id="matter-fp-neighbor", matter_fingerprint=OTHER_MATTER_FP))
    _commit(client, collection, _engagement(engagement_id="party-neighbor", client_party_id=OTHER_PARTY))
    _commit(client, collection, _engagement(engagement_id="subject-neighbor", subject_identity_fingerprint=OTHER_SUBJECT_FP))
    result = _compose(client, collection)
    assert result.state is LegalClientMatterEngagementCurrentnessState.CURRENT
    assert result.decisive_engagement_id == "exact"
    assert result.candidate_engagement_ids == ("exact",)


def test_real_history_order_does_not_change_projection(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Equivalent histories inserted in reverse order project identically."""
    client, database, collection = mongo_context
    first = _engagement(engagement_id="order-first", effective_offset=5)
    second = _engagement(engagement_id="order-second", effective_offset=10)
    _commit(client, collection, first)
    _commit(client, collection, second)
    forward = _compose(client, collection)
    reverse_database = client[f"wilsy_l9c11_engcur_order_{uuid.uuid4().hex}"]
    try:
        reverse_collection = reverse_database[registry.COLLECTION]
        registry.ensure_indexes(reverse_collection)
        _commit(client, reverse_collection, second)
        _commit(client, reverse_collection, first)
        reverse = _compose(client, reverse_collection)
        assert forward == reverse
    finally:
        assert database.name != reverse_database.name
        client.drop_database(reverse_database.name)


def test_real_corruption_and_divergent_identity_fail_closed(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Tampered canonical fields, ID and fingerprint reject at hydration."""
    client, _, collection = mongo_context
    value = _engagement()
    _commit(client, collection, value)
    collection.update_one(
        {"tenant_id": TENANT_A, "engagement_id": value.engagement_id},
        {"$set": {"mandate_scope": "tampered"}},
    )
    with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError) as error:
        _compose(client, collection)
    assert error.value.code == "L9C11_P4_HISTORY_READ_FAILED"

    id_database = client[f"wilsy_l9c11_engcur_idcorrupt_{uuid.uuid4().hex}"]
    fingerprint_database = client[f"wilsy_l9c11_engcur_fpcorrupt_{uuid.uuid4().hex}"]
    try:
        id_collection = id_database[registry.COLLECTION]
        fingerprint_collection = fingerprint_database[registry.COLLECTION]
        registry.ensure_indexes(id_collection)
        registry.ensure_indexes(fingerprint_collection)
        id_value = _engagement(engagement_id="id-corrupt")
        fp_value = _engagement(engagement_id="fp-corrupt")
        _commit(client, id_collection, id_value)
        _commit(client, fingerprint_collection, fp_value)
        id_collection.update_one(
            {"tenant_id": TENANT_A, "engagement_id": id_value.engagement_id},
            {"$set": {"engagement_id": "tampered-id"}},
        )
        fingerprint_collection.update_one(
            {"tenant_id": TENANT_A, "engagement_id": fp_value.engagement_id},
            {"$set": {"fingerprint": "9" * 128}},
        )
        for target in (id_collection, fingerprint_collection):
            with pytest.raises(LegalClientMatterEngagementCurrentnessComposerError) as raised:
                _compose(client, target)
            assert raised.value.code == "L9C11_P4_HISTORY_READ_FAILED"
    finally:
        client.drop_database(id_database.name)
        client.drop_database(fingerprint_database.name)


def test_real_snapshot_consistency_and_fresh_transaction_visibility(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """A transaction snapshot remains stable; a fresh transaction sees commit."""
    client, _, collection = mongo_context
    _commit(client, collection, _engagement(engagement_id="snapshot-old"))
    with client.start_session() as original:
        original.start_transaction()
        first = _compose(client, collection, session=original)
        _commit(client, collection, _engagement(engagement_id="snapshot-new", effective_offset=10))
        again = _compose(client, collection, session=original)
        assert first == again
        original.abort_transaction()
    fresh = _compose(client, collection)
    assert fresh.state is LegalClientMatterEngagementCurrentnessState.AMBIGUOUS


def test_real_corrupt_blocked_state_is_owned_by_p3() -> None:
    """A wrong-lineage candidate reaches P3 as CORRUPT_BLOCKED, not current."""
    candidate = _engagement(tenant_id=TENANT_B)
    projected = project_legal_client_matter_engagement_currentness(
        tenant_id=TENANT_A,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_identity_fingerprint=SUBJECT_FP,
        evaluated_at=BASE + timedelta(hours=1),
        engagements=(candidate,),
    )
    assert projected.state is LegalClientMatterEngagementCurrentnessState.CORRUPT_BLOCKED


def test_real_authority_surface_and_pointer_absence() -> None:
    """Static/runtime certificate scope excludes downstream authorities."""
    source = Path(
        "tools/eos/legal_operations/orchestration/legal_client_matter_engagement_currentness_composer.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = " ".join(
        ast.unparse(node).lower()
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    assert "legal_client_matter_engagement_currentness" in imports
    assert all(
        token not in imports
        for token in (
            "representation",
            "iam",
            "court",
            "http",
            "finance",
            "kennel",
        )
    )
    assert "datetime.now" not in source
    assert "utcnow" not in source
    assert "max(" not in source
    assert "sorted(" not in source


# ARTIFACT: test_legal_client_matter_engagement_currentness_real_mongo.py
# VERSION: v1.0.0-L9C11-P5-ENGAGEMENT-CURRENTNESS-COMPOSER-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo currentness composition evidence
# TENANT POSTURE: UUID-isolated database and exact five-field lineage queries
# FAIL-CLOSED POSTURE: unavailable runtime skips; corruption/isolation fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
