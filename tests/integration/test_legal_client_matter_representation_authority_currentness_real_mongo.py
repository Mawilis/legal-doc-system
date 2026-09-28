"""Real-Mongo certificate for L9C11-P21A currentness composition.

TITLE: WILSY OS Legal Client Representation Authority Currentness Real-Mongo Certificate
VERSION: v1.1.0-L9C11-P21AR-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published P21A pure projection and composer against one
         writable UUID-isolated Mongo replica set without touching canonical
         data. Valid P1 rows always enter through the P7 registry; corruption
         cases persist independently unique rows and introduce duplicate
         identity only at a bounded read fixture, preserving every P7 index.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_representation_authority_currentness_real_mongo.py
COLLABORATION / OWNERSHIP: P1 owns immutable authority values; P7 owns
                            durable exact-lineage history; P21A owns pure
                            currentness and one-read composition. This file
                            owns disposable runtime evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.1.0-L9C11-P21AR certifies exact positive P1 role and scope
           propagation while preserving the prior runtime boundary.
           v1.0.0-L9C11-P21AR certifies sanctioned topology, disposable
           database isolation, caller-owned transaction/session propagation,
           exact representative-specific lineage, all six P21A states,
           duplicate normalization, ambiguity, future exclusion, strict
           hydration, corruption fail-closed behavior, deterministic order
           independence and zero composer writes. P21AR1 repairs the
           corruption fixture without disabling or dropping a P7 unique index.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
                             URI, credentials, PII and raw secrets are never
                             printed.
TENANT BOUNDARY: Every compose uses exact tenant, matter, matter fingerprint,
                 client party, subject fingerprint and representative
                 principal lineage.
AUTHORITY BOUNDARY: Disposable P21A runtime evidence only. No IAM, firm
                    decision, Representation, Court, HTTP, UI, Node or
                    financial authority is changed.
TRANSACTION BOUNDARY: The certificate owns disposable sessions and
                      transactions; P21A composer owns none of their lifecycle.
FAIL-CLOSED DECLARATION: Unavailable infrastructure skips explicitly for
                         operator runtime; invalid transactions, malformed
                         persisted rows and cross-lineage evidence fail closed.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
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

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import (
    LegalClientMatterRepresentationAuthorityCurrentnessState,
    project_legal_client_matter_representation_authority_currentness,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_authority_currentness_composer import (
    LegalClientMatterRepresentationAuthorityCurrentnessComposer,
    LegalClientMatterRepresentationAuthorityCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_representation_authority_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT_A = "tenant-l9c11-p21ar-a"
TENANT_B = "tenant-l9c11-p21ar-b"
MATTER = "matter-l9c11-p21ar"
OTHER_MATTER = "matter-other-l9c11-p21ar"
MATTER_FP = "a" * 128
OTHER_MATTER_FP = "b" * 128
PARTY = "party-l9c11-p21ar"
OTHER_PARTY = "party-other-l9c11-p21ar"
SUBJECT_FP = "c" * 128
OTHER_SUBJECT_FP = "d" * 128
REPRESENTATIVE_A = "principal-l9c11-p21ar-a"
REPRESENTATIVE_B = "principal-l9c11-p21ar-b"


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


class CorruptingCollection(CountingCollection):
    """Read-only fixture proxy that corrupts identity after durable reads."""

    def __init__(self, inner: Any, replacements: dict[str, dict[str, object]]) -> None:
        super().__init__(inner)
        self.replacements = replacements

    def find(self, query: dict[str, object], **kwargs: object) -> tuple[dict[str, object], ...]:
        self.find_calls.append((dict(query), dict(kwargs)))
        rows: list[dict[str, object]] = []
        for raw in self.inner.find(query, **kwargs):
            row = dict(raw)
            authority_id = row.get("authority_id")
            replacement = self.replacements.get(authority_id) if isinstance(authority_id, str) else None
            rows.append(dict(replacement) if replacement is not None else row)
        return tuple(rows)


@dataclass(frozen=True)
class MongoContext:
    """Disposable topology and exact P7 collection handles."""

    client: MongoClient[Any]
    database: Any
    collection: Any
    server_version: str
    pymongo_version: str


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield one sanctioned writable UUID-isolated database."""
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
            server_version_value = client.server_info().get("version")
            import pymongo

            pymongo_version = pymongo.version
        except (PyMongoError, OSError) as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version_value, str) and server_version_value
        assert isinstance(pymongo_version, str) and pymongo_version
        database_name = f"wilsy_l9c11_p21ar_{uuid.uuid4().hex}"
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
        yield MongoContext(client, database, collection, server_version_value, pymongo_version)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _authority(
    *,
    tenant_id: str = TENANT_A,
    authority_id: str = "authority-l9c11-p21ar-1",
    decision: str = "APPOINTED",
    effective_from: datetime = BASE,
    case_matter_id: str = MATTER,
    matter_fingerprint: str = MATTER_FP,
    client_party_id: str = PARTY,
    subject_identity_fingerprint: str = SUBJECT_FP,
    representative_principal_id: str = REPRESENTATIVE_A,
    representative_role: str = "LEGAL_PRACTITIONER",
    representation_scope_capabilities: tuple[str, ...] = ("ADVISORY",),
) -> LegalClientMatterRepresentationAuthority:
    """Construct one valid immutable P1 value through its public domain API."""
    return LegalClientMatterRepresentationAuthority(
        authority_id=authority_id,
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=client_party_id,
        subject_reference="client:subject-l9c11-p21ar",
        subject_identity_fingerprint=subject_identity_fingerprint,
        engagement_id="engagement-l9c11-p21ar",
        engagement_fingerprint="e" * 128,
        mandate_id="mandate-l9c11-p21ar",
        mandate_fingerprint="f" * 128,
        mandate_scope_reference="scope:l9c11:p21ar",
        mandate_scope_fingerprint="1" * 128,
        mandate_capabilities=("ADVISORY", "NEGOTIATION"),
        acting_capacity_id="capacity-l9c11-p21ar",
        acting_capacity_fingerprint="2" * 128,
        representative_principal_id=representative_principal_id,
        representative_role=representative_role,
        representation_scope_capabilities=representation_scope_capabilities,
        decision=decision,
        appointing_principal_id="principal-client-l9c11-p21ar",
        source_evidence_reference=f"source:{authority_id}",
        source_evidence_fingerprint="3" * 128,
        authorization_evidence_reference=f"authorization:{authority_id}",
        authorization_evidence_fingerprint="4" * 128,
        occurred_at=effective_from,
        effective_from=effective_from,
        effective_until=effective_from + timedelta(days=30),
        idempotency_key=f"idempotency:{authority_id}",
    )


def _persist(context: MongoContext, value: LegalClientMatterRepresentationAuthority) -> None:
    """Persist canonical P1 evidence through P7 in a caller transaction."""
    with context.client.start_session() as session:
        with session.start_transaction():
            registry.persist_representation_authority(value, context.collection, session=session)


def _compose(
    context: MongoContext,
    *,
    evaluated_at: datetime = BASE + timedelta(hours=1),
    session: Any | None = None,
    target_collection: Any | None = None,
    **scope: str,
) -> Any:
    """Compose exact P7 lineage inside an owned or supplied transaction."""
    owned = session is None
    transaction = context.client.start_session() if owned else session
    assert transaction is not None
    try:
        if owned:
            transaction.start_transaction()
        composer = LegalClientMatterRepresentationAuthorityCurrentnessComposer(
            authority_collection=target_collection or context.collection,
        )
        return composer.compose_currentness(
            scope.get("tenant_id", TENANT_A),
            scope.get("case_matter_id", MATTER),
            scope.get("matter_fingerprint", MATTER_FP),
            scope.get("client_party_id", PARTY),
            scope.get("subject_identity_fingerprint", SUBJECT_FP),
            scope.get("representative_principal_id", REPRESENTATIVE_A),
            evaluated_at,
            transaction,
        )
    finally:
        if owned:
            transaction.abort_transaction()
            transaction.end_session()


def _assert_empty_currentness_surfaces(context: MongoContext) -> None:
    """Prove P21A created no mutable projection or lifecycle collection."""
    names = set(context.database.list_collection_names())
    assert "legal_client_matter_representation_authority_currentness" not in names
    assert not any("current" in name.lower() for name in names if name != registry.COLLECTION)


def _assert_p7_unique_indexes_preserved(context: MongoContext) -> None:
    """Prove corruption fixtures never disable P7 uniqueness enforcement."""
    indexes = {
        item["name"]: item
        for item in context.collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert indexes[registry.AUTHORITY_ID_INDEX_NAME].get("unique") is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True


def test_real_topology_and_disposable_database_are_sanctioned(mongo_context: MongoContext) -> None:
    """Prove writable primary, sessions, transactions, replica identity and isolation."""
    assert mongo_context.database.name.startswith("wilsy_l9c11_p21ar_")
    assert len(mongo_context.database.name) <= 63
    assert mongo_context.database.name != "wilsy"
    assert mongo_context.server_version
    assert mongo_context.pymongo_version
    indexes = {
        item["name"]: item
        for item in mongo_context.collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(indexes) == {
        registry.AUTHORITY_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }
    assert indexes[registry.AUTHORITY_ID_INDEX_NAME].get("unique") is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert indexes[registry.HISTORY_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_transaction_contract_and_session_propagation(mongo_context: MongoContext) -> None:
    """Missing/inactive sessions reject; active callers retain lifecycle."""
    client = mongo_context.client
    composer = LegalClientMatterRepresentationAuthorityCurrentnessComposer(
        authority_collection=mongo_context.collection,
    )
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError):
        composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, REPRESENTATIVE_A, BASE, None)
    with client.start_session() as inactive:
        with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, REPRESENTATIVE_A, BASE, inactive)
    with client.start_session() as session:
        session.start_transaction()
        result = composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, REPRESENTATIVE_A, BASE, session)
        assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
        assert session.in_transaction is True
        session.abort_transaction()


def test_real_one_history_read_exact_lineage_and_zero_writes(mongo_context: MongoContext) -> None:
    """One read carries all six P7 lineage fields and the same session."""
    value = _authority()
    _persist(mongo_context, value)
    counted = CountingCollection(mongo_context.collection)
    before = mongo_context.collection.count_documents({})
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        result = _compose(mongo_context, session=session, target_collection=counted)
        assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED
        assert result.representative_role == value.representative_role
        assert result.representation_scope_capabilities == value.representation_scope_capabilities
        assert len(counted.find_calls) == 1
        query, kwargs = counted.find_calls[0]
        assert query == {
            "tenant_id": TENANT_A,
            "case_matter_id": MATTER,
            "matter_fingerprint": MATTER_FP,
            "client_party_id": PARTY,
            "subject_identity_fingerprint": SUBJECT_FP,
            "representative_principal_id": REPRESENTATIVE_A,
        }
        assert kwargs["session"] is session
        assert counted.write_calls == 0
        assert mongo_context.collection.count_documents({}) == before
        assert session.in_transaction is True
        session.abort_transaction()
    _assert_empty_currentness_surfaces(mongo_context)


@pytest.mark.parametrize(
    ("decision", "expected", "positive"),
    [("APPOINTED", "APPOINTED", True), ("DECLINED", "DECLINED", False), ("REQUIRES_REVIEW", "REQUIRES_REVIEW", False)],
)
def test_real_single_decision_states(
    mongo_context: MongoContext,
    decision: str,
    expected: str,
    positive: bool,
) -> None:
    """One canonical effective P1 row projects to its exact decision state."""
    _persist(mongo_context, _authority(decision=decision))
    result = _compose(mongo_context)
    assert result.state.value == expected
    assert result.is_currently_appointed is positive
    if positive:
        assert result.representative_role == "LEGAL_PRACTITIONER"
        assert result.representation_scope_capabilities == ("ADVISORY",)
    else:
        assert result.representative_role is None
        assert result.representation_scope_capabilities == ()


def test_real_empty_history_and_future_appointment_are_no_authority(mongo_context: MongoContext) -> None:
    """Empty and future-only histories are not positive currentness."""
    assert _compose(mongo_context, evaluated_at=BASE).state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    _persist(mongo_context, _authority(effective_from=BASE + timedelta(days=1)))
    result = _compose(mongo_context, evaluated_at=BASE)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    assert result.normalized_authority_count == 1
    assert result.eligible_authority_count == 0
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


def test_real_exact_replay_is_one_row_and_normalized(mongo_context: MongoContext) -> None:
    """P7 exact replay remains one durable row and one semantic authority."""
    value = _authority()
    _persist(mongo_context, value)
    _persist(mongo_context, value)
    assert mongo_context.collection.count_documents({}) == 1
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED
    assert result.normalized_authority_count == 1
    assert result.eligible_authority_count == 1


def test_real_distinct_appointed_rows_are_ambiguous_without_latest_wins(mongo_context: MongoContext) -> None:
    """Two distinct eligible appointments never choose the later row."""
    _persist(mongo_context, _authority(authority_id="authority-early", effective_from=BASE - timedelta(minutes=5)))
    _persist(mongo_context, _authority(authority_id="authority-late", effective_from=BASE))
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
    assert result.decisive_authority_id is None
    assert result.candidate_authority_ids == ("authority-early", "authority-late")
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


@pytest.mark.parametrize("second_decision", ["DECLINED", "REQUIRES_REVIEW"])
def test_real_mixed_decisions_are_ambiguous(
    mongo_context: MongoContext,
    second_decision: str,
) -> None:
    """APPOINTED plus either negative decision is ambiguous."""
    _persist(mongo_context, _authority(authority_id="authority-appointed"))
    _persist(mongo_context, _authority(authority_id="authority-second", decision=second_decision))
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
    assert result.is_currently_appointed is False
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


def test_real_same_effective_distinct_rows_are_ambiguous(mongo_context: MongoContext) -> None:
    """Same-effective distinct immutable rows remain ambiguous."""
    _persist(mongo_context, _authority(authority_id="authority-same-a"))
    _persist(mongo_context, _authority(authority_id="authority-same-b"))
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.AMBIGUOUS
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


def test_real_representative_specific_isolation(mongo_context: MongoContext) -> None:
    """Representative A history never widens into representative B."""
    _persist(mongo_context, _authority(representative_principal_id=REPRESENTATIVE_A, authority_id="authority-a"))
    assert _compose(mongo_context, representative_principal_id=REPRESENTATIVE_B).state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    _persist(mongo_context, _authority(representative_principal_id=REPRESENTATIVE_B, authority_id="authority-b"))
    result_a = _compose(mongo_context, representative_principal_id=REPRESENTATIVE_A)
    result_b = _compose(mongo_context, representative_principal_id=REPRESENTATIVE_B)
    assert result_a.state is result_b.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED
    assert result_a.candidate_authority_ids == ("authority-a",)
    assert result_b.candidate_authority_ids == ("authority-b",)


def test_real_tenant_and_all_lineage_dimensions_are_isolated(mongo_context: MongoContext) -> None:
    """Tenant, matter, matter fingerprint, party, subject and representative cannot leak."""
    _persist(mongo_context, _authority(authority_id="exact"))
    _persist(mongo_context, _authority(tenant_id=TENANT_B, authority_id="tenant-neighbor"))
    _persist(mongo_context, _authority(case_matter_id=OTHER_MATTER, authority_id="matter-neighbor"))
    _persist(mongo_context, _authority(matter_fingerprint=OTHER_MATTER_FP, authority_id="matter-fp-neighbor"))
    _persist(mongo_context, _authority(client_party_id=OTHER_PARTY, authority_id="party-neighbor"))
    _persist(mongo_context, _authority(subject_identity_fingerprint=OTHER_SUBJECT_FP, authority_id="subject-neighbor"))
    _persist(mongo_context, _authority(representative_principal_id=REPRESENTATIVE_B, authority_id="representative-neighbor"))
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED
    assert result.candidate_authority_ids == ("exact",)


def test_real_duplicate_identity_corruption_returns_corrupt_blocked(mongo_context: MongoContext) -> None:
    """Unique durable rows plus a bounded duplicate identity reach P21A corruption."""
    first = _authority(authority_id="authority-corrupt", decision="APPOINTED")
    second = _authority(authority_id="authority-corrupt-source", decision="DECLINED")
    _persist(mongo_context, first)
    _persist(mongo_context, second)
    corrupt = _authority(authority_id="authority-corrupt", decision="DECLINED")
    counted = CorruptingCollection(
        mongo_context.collection,
        {second.authority_id: corrupt.to_dict()},
    )
    result = _compose(mongo_context, target_collection=counted)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert result.is_currently_appointed is False
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()
    assert mongo_context.collection.count_documents({}) == 2
    assert counted.write_calls == 0
    _assert_p7_unique_indexes_preserved(mongo_context)


def test_real_mixed_valid_and_corrupt_identity_fails_closed(mongo_context: MongoContext) -> None:
    """A valid row plus a unique durable row corrupted at read never falls back."""
    valid = _authority(authority_id="authority-mixed", decision="APPOINTED")
    conflicting = _authority(authority_id="authority-mixed-source", decision="REQUIRES_REVIEW")
    _persist(mongo_context, valid)
    _persist(mongo_context, conflicting)
    corrupt = _authority(authority_id="authority-mixed", decision="REQUIRES_REVIEW")
    counted = CorruptingCollection(
        mongo_context.collection,
        {conflicting.authority_id: corrupt.to_dict()},
    )
    result = _compose(mongo_context, target_collection=counted)
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert mongo_context.collection.count_documents({}) == 2
    assert counted.write_calls == 0
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()
    _assert_p7_unique_indexes_preserved(mongo_context)


def test_real_malformed_required_field_is_rejected_by_strict_p7_hydration(mongo_context: MongoContext) -> None:
    """Malformed persisted P1 data is rejected before any positive projection."""
    value = _authority(authority_id="authority-malformed")
    _persist(mongo_context, value)
    mongo_context.collection.update_one(
        {"tenant_id": TENANT_A, "authority_id": value.authority_id},
        {"$set": {"fingerprint": "9" * 128}},
    )
    with pytest.raises(LegalClientMatterRepresentationAuthorityCurrentnessComposerError) as raised:
        _compose(mongo_context)
    assert raised.value.code == "L9C11_P21A_COMPOSER_HISTORY_READ_FAILED"


def test_real_history_order_and_repeat_composition_are_deterministic(mongo_context: MongoContext) -> None:
    """Different insertion order and repeated reads produce identical snapshots."""
    first = _authority(authority_id="authority-order-first", effective_from=BASE - timedelta(minutes=5))
    second = _authority(authority_id="authority-order-second", effective_from=BASE - timedelta(minutes=1), decision="DECLINED")
    _persist(mongo_context, first)
    _persist(mongo_context, second)
    forward = _compose(mongo_context)
    repeated = _compose(mongo_context)
    assert forward == repeated
    reverse_db = mongo_context.client[f"wilsy_l9c11_p21ar_order_{uuid.uuid4().hex}"]
    try:
        reverse_collection = reverse_db[registry.COLLECTION]
        registry.ensure_indexes(reverse_collection)
        reverse_context = MongoContext(
            mongo_context.client,
            reverse_db,
            reverse_collection,
            mongo_context.server_version,
            mongo_context.pymongo_version,
        )
        _persist(reverse_context, second)
        _persist(reverse_context, first)
        reverse = _compose(reverse_context)
        assert forward == reverse
    finally:
        mongo_context.client.drop_database(reverse_db.name)


def test_real_explicit_evaluated_at_is_forwarded_without_clock_reads(mongo_context: MongoContext) -> None:
    """A supplied instant controls future exclusion and no wall clock is used."""
    future = _authority(effective_from=BASE + timedelta(days=1))
    _persist(mongo_context, future)
    explicit = BASE
    result = _compose(mongo_context, evaluated_at=explicit)
    assert result.evaluated_at == explicit
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.NO_AUTHORITY
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_representation_authority_currentness.py").read_text(encoding="utf-8")
    assert "datetime.now" not in source
    assert "datetime.utcnow" not in source


def test_real_no_lifecycle_authority_or_current_pointer_is_created(mongo_context: MongoContext) -> None:
    """P21A remains a read-only projection and creates no downstream truth."""
    _persist(mongo_context, _authority())
    before = set(mongo_context.database.list_collection_names())
    result = _compose(mongo_context)
    after = set(mongo_context.database.list_collection_names())
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.APPOINTED
    assert before == after
    assert not any(token in name.lower() for name in after for token in ("current", "lifecycle", "firm_decision"))
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_representation_authority_currentness_composer.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = " ".join(
        ast.unparse(node).lower()
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    assert all(token not in imports for token in ("iam", "firm_decision", "court", "finance", "http", "ui", "node"))
    assert all(token not in source for token in ("insert_one", "update_one", "delete_one", "start_transaction", "commit_transaction", "abort_transaction"))


def test_real_p21a_domain_corruption_projection_is_fail_closed() -> None:
    """The pure P21A seam retains CORRUPT_BLOCKED semantics independently of P7."""
    malformed = object()
    result = project_legal_client_matter_representation_authority_currentness(
        tenant_id=TENANT_A,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_identity_fingerprint=SUBJECT_FP,
        representative_principal_id=REPRESENTATIVE_A,
        evaluated_at=BASE,
        authorities=(malformed,),  # type: ignore[arg-type]
    )
    assert result.state is LegalClientMatterRepresentationAuthorityCurrentnessState.CORRUPT_BLOCKED
    assert result.representative_role is None
    assert result.representation_scope_capabilities == ()


# ARTIFACT: test_legal_client_matter_representation_authority_currentness_real_mongo.py
# VERSION: v1.1.0-L9C11-P21AR-CLIENT-REPRESENTATION-AUTHORITY-CURRENTNESS-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P21A real-Mongo currentness composition evidence
# TENANT POSTURE: UUID-isolated database and exact six-field representative-specific lineage
# FAIL-CLOSED POSTURE: unavailable runtime skips; corruption and isolation fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
