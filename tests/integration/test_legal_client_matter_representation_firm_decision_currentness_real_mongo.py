"""Real-Mongo certificate for the published L9C11-P22 currentness lane.

TITLE: WILSY OS Legal Firm Representation Decision Currentness Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P22R-FIRM-REPRESENTATION-DECISION-CURRENTNESS-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published P22 pure projection and one-read composer against
         a writable UUID-isolated Mongo replica set.  Every durable decision is
         persisted through P9; currentness remains read-only derived evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_representation_firm_decision_currentness_real_mongo.py
COLLABORATION / OWNERSHIP: P2 owns immutable firm decisions; P9 owns durable
                            append-only history; P22 owns pure projection and
                            the composer owns one caller-session read. This file
                            owns disposable certification evidence only.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P22R certifies sanctioned topology, exact tenant,
           matter, client, subject, P1, representative and role lineage,
           transaction/session forwarding, all P22 states, future exclusion,
           duplicate normalization, ambiguity, corruption blocking,
           deterministic explicit-time projection and zero writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no credentials, PII, canonical database or raw
                             authorization payloads are printed.
TENANT BOUNDARY: Every durable read and projection uses the exact tenant,
                 matter, client, subject, P1 authority, representative and
                 role lineage supplied by the caller.
AUTHORITY BOUNDARY: Disposable P22R evidence only. No IAM, final
                    Representation, Court, HTTP/UI/Node or financial authority.
TRANSACTION BOUNDARY: This certificate owns disposable sessions and seed
                      transactions; P22 starts, commits and aborts none.
FAIL-CLOSED DECLARATION: Unavailable infrastructure skips explicitly for
                         operator runtime; invalid transactions, malformed
                         rows, cross-lineage evidence and ambiguity fail closed.
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
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    LegalClientMatterRepresentationFirmDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import (
    LegalClientMatterRepresentationFirmDecisionCurrentnessState,
    project_legal_client_matter_representation_firm_decision_currentness,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_representation_firm_decision_currentness_composer import (
    LegalClientMatterRepresentationFirmDecisionCurrentnessComposer,
    LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_representation_firm_decision_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
TENANT_A = "tenant-l9c11-p22r-a"
TENANT_B = "tenant-l9c11-p22r-b"
MATTER = "matter-l9c11-p22r"
OTHER_MATTER = "matter-other-l9c11-p22r"
MATTER_FP = "a" * 128
OTHER_MATTER_FP = "b" * 128
PARTY = "party-l9c11-p22r"
OTHER_PARTY = "party-other-l9c11-p22r"
SUBJECT_FP = "c" * 128
OTHER_SUBJECT_FP = "d" * 128
REPRESENTATIVE_A = "principal-l9c11-p22r-a"
REPRESENTATIVE_B = "principal-l9c11-p22r-b"
ROLE = "LEGAL_PRACTITIONER"


@dataclass
class MongoContext:
    """One disposable database and its canonical P9 decision collection."""

    client: MongoClient[Any]
    database: Any
    collection: Any
    server_version: str
    pymongo_version: str


class CountingCollection:
    """Read proxy recording P9 reads and rejecting composer writes."""

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
        raise AssertionError("P22 composer attempted insert")

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("P22 composer attempted update")

    def delete_many(self, *_args: Any, **_kwargs: Any) -> None:
        self.write_calls += 1
        raise AssertionError("P22 composer attempted delete")

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)


class CorruptingCollection(CountingCollection):
    """Bounded read fixture that corrupts a row without changing P9 indexes."""

    def __init__(self, inner: Any, replacement: dict[str, object]) -> None:
        super().__init__(inner)
        self.replacement = replacement

    def find(self, query: dict[str, object], **kwargs: object) -> tuple[dict[str, object], ...]:
        self.find_calls.append((dict(query), dict(kwargs)))
        rows: list[dict[str, object]] = []
        for raw in self.inner.find(query, **kwargs):
            row = dict(raw)
            if row.get("decision_id") == self.replacement.get("decision_id"):
                row.update(self.replacement)
            rows.append(row)
        return tuple(rows)


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Make one sanctioned writable UUID-isolated database per test."""
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
            with client.start_session() as probe:
                probe.start_transaction()
                assert probe.in_transaction is True
                probe.abort_transaction()
        except (PyMongoError, OSError) as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version_value, str) and server_version_value
        assert isinstance(pymongo_version, str) and pymongo_version
        database_name = f"wilsy_l9c11_p22r_{uuid.uuid4().hex}"
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
        yield MongoContext(client, database, collection, str(server_version_value), pymongo_version)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _authority(
    *,
    tenant_id: str = TENANT_A,
    authority_id: str = "authority-l9c11-p22r-1",
    case_matter_id: str = MATTER,
    matter_fingerprint: str = MATTER_FP,
    client_party_id: str = PARTY,
    subject_identity_fingerprint: str = SUBJECT_FP,
    representative_principal_id: str = REPRESENTATIVE_A,
    representative_role: str = ROLE,
    source_evidence_fingerprint: str = "3" * 128,
) -> LegalClientMatterRepresentationAuthority:
    """Build one valid P1 authority used by the public P2 constructor."""
    return LegalClientMatterRepresentationAuthority(
        authority_id=authority_id,
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=client_party_id,
        subject_reference="client:subject-l9c11-p22r",
        subject_identity_fingerprint=subject_identity_fingerprint,
        engagement_id="engagement-l9c11-p22r",
        engagement_fingerprint="e" * 128,
        mandate_id="mandate-l9c11-p22r",
        mandate_fingerprint="f" * 128,
        mandate_scope_reference="scope:l9c11:p22r",
        mandate_scope_fingerprint="1" * 128,
        mandate_capabilities=("ADVISORY", "NEGOTIATION"),
        acting_capacity_id="capacity-l9c11-p22r",
        acting_capacity_fingerprint="2" * 128,
        representative_principal_id=representative_principal_id,
        representative_role=representative_role,
        representation_scope_capabilities=("ADVISORY",),
        decision=LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        appointing_principal_id="principal-client-l9c11-p22r",
        source_evidence_reference=f"source:{authority_id}",
        source_evidence_fingerprint=source_evidence_fingerprint,
        authorization_evidence_reference=f"authorization:{authority_id}",
        authorization_evidence_fingerprint="4" * 128,
        occurred_at=BASE,
        effective_from=BASE,
        effective_until=BASE + timedelta(days=30),
        idempotency_key=f"idempotency:{authority_id}",
    )


def _decision(
    *,
    source_authority: LegalClientMatterRepresentationAuthority | None = None,
    decision_value: str = "ACCEPTED",
    suffix: str = "one",
    effective_from: datetime = BASE,
) -> LegalClientMatterRepresentationFirmDecision:
    """Build one canonical P2 decision bound to one exact P1 authority."""
    authority = source_authority or _authority()
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority,
        decision=decision_value,
        decision_actor_principal_id=f"principal-firm-{suffix}",
        authorization_evidence_reference=f"authorization:firm-{suffix}",
        authorization_evidence_fingerprint="5" * 128,
        source_evidence_reference=f"source:firm-{suffix}",
        source_evidence_fingerprint="6" * 128,
        occurred_at=effective_from,
        effective_from=effective_from,
        idempotency_key=f"idempotency:firm-{suffix}",
    )


def _persist(context: MongoContext, value: LegalClientMatterRepresentationFirmDecision) -> None:
    """Persist through P9 in a caller-owned transaction."""
    with context.client.start_session() as session:
        with session.start_transaction():
            registry.persist_firm_decision(value, context.collection, session=session)


def _compose(
    context: MongoContext,
    *,
    evaluated_at: datetime = BASE + timedelta(hours=1),
    session: Any | None = None,
    target_collection: Any | None = None,
    tenant_id: str = TENANT_A,
    case_matter_id: str = MATTER,
    matter_fingerprint: str = MATTER_FP,
    client_party_id: str = PARTY,
    subject_identity_fingerprint: str = SUBJECT_FP,
    representation_authority_id: str | None = None,
    representation_authority_fingerprint: str | None = None,
    representative_principal_id: str = REPRESENTATIVE_A,
    representative_role: str = ROLE,
) -> Any:
    """Compose one exact P22 projection, owning a transaction only for setup."""
    authority = _authority(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=client_party_id,
        subject_identity_fingerprint=subject_identity_fingerprint,
        representative_principal_id=representative_principal_id,
        representative_role=representative_role,
    )
    owned = session is None
    transaction = context.client.start_session() if owned else session
    assert transaction is not None
    try:
        if owned:
            transaction.start_transaction()
        composer = LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(
            decision_collection=target_collection or context.collection,
        )
        return composer.compose_currentness(
            tenant_id,
            case_matter_id,
            matter_fingerprint,
            client_party_id,
            subject_identity_fingerprint,
            representation_authority_id or authority.authority_id,
            representation_authority_fingerprint or authority.fingerprint,
            representative_principal_id,
            representative_role,
            evaluated_at,
            transaction,
        )
    finally:
        if owned:
            transaction.abort_transaction()
            transaction.end_session()


def _assert_no_downstream_surfaces(
    context: MongoContext,
    collections_before: set[str],
    row_counts_before: dict[str, int],
) -> None:
    """Prove P22 created no collection and changed no pre-existing rows.

    P9's ``legal_client_matter_representation_firm_decisions`` collection is a
    legitimate prerequisite and contains the word ``representation``. A broad
    substring absence assertion would therefore misclassify P9 as downstream.
    The differential is exact: no collection may appear after composition and
    every collection present before composition must retain its row count.
    """
    collections_after = set(context.database.list_collection_names())
    assert collections_after == collections_before
    assert registry.COLLECTION in collections_before
    assert {
        name: context.database[name].count_documents({})
        for name in collections_before
    } == row_counts_before
    assert "legal_client_matter_representation_authorities" not in collections_after
    assert "legal_client_matter_representation_authorization_evidence" not in collections_after
    assert "tenant_authorization_decision_evidence" not in collections_after


def test_real_topology_and_disposable_database_are_sanctioned(mongo_context: MongoContext) -> None:
    """Prove replica identity, writable primary, sessions, indexes and isolation."""
    assert mongo_context.database.name.startswith("wilsy_l9c11_p22r_")
    assert len(mongo_context.database.name) <= 63
    assert mongo_context.database.name != "wilsy"
    assert mongo_context.server_version and mongo_context.pymongo_version
    indexes = {item["name"]: item for item in mongo_context.collection.list_indexes() if item["name"] != "_id_"}
    assert set(indexes) == {
        registry.DECISION_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }
    assert indexes[registry.DECISION_ID_INDEX_NAME].get("unique") is True
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert indexes[registry.HISTORY_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in indexes.values())


def test_real_transaction_contract_and_missing_or_inactive_sessions(mongo_context: MongoContext) -> None:
    """Missing and inactive callers reject; active caller transaction is retained."""
    composer = LegalClientMatterRepresentationFirmDecisionCurrentnessComposer(
        decision_collection=mongo_context.collection,
    )
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError) as missing:
        composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, _authority().authority_id, _authority().fingerprint, REPRESENTATIVE_A, ROLE, BASE, None)
    assert missing.value.code == "L9C11_P22_COMPOSER_ACTIVE_TRANSACTION_REQUIRED"
    with mongo_context.client.start_session() as inactive:
        with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, _authority().authority_id, _authority().fingerprint, REPRESENTATIVE_A, ROLE, BASE, inactive)
    with mongo_context.client.start_session() as active:
        active.start_transaction()
        result = composer.compose_currentness(TENANT_A, MATTER, MATTER_FP, PARTY, SUBJECT_FP, _authority().authority_id, _authority().fingerprint, REPRESENTATIVE_A, ROLE, BASE, active)
        assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION
        assert active.in_transaction is True
        active.abort_transaction()


def test_real_one_p9_history_read_exact_lineage_same_session_and_zero_writes(mongo_context: MongoContext) -> None:
    """One P9 query carries exact lineage and the composer performs no write."""
    value = _decision()
    _persist(mongo_context, value)
    counted = CountingCollection(mongo_context.collection)
    before = mongo_context.collection.count_documents({})
    collections_before = set(mongo_context.database.list_collection_names())
    row_counts_before = {
        name: mongo_context.database[name].count_documents({})
        for name in collections_before
    }
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        result = _compose(mongo_context, session=session, target_collection=counted)
        assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED
        assert len(counted.find_calls) == 1
        query, kwargs = counted.find_calls[0]
        assert query == {
            "tenant_id": TENANT_A,
            "case_matter_id": MATTER,
            "matter_fingerprint": MATTER_FP,
            "client_party_id": PARTY,
            "subject_identity_fingerprint": SUBJECT_FP,
            "representation_authority_id": value.representation_authority_id,
            "representation_authority_fingerprint": value.representation_authority_fingerprint,
            "representative_principal_id": REPRESENTATIVE_A,
        }
        assert kwargs["session"] is session
        assert counted.write_calls == 0
        assert mongo_context.collection.count_documents({}) == before
        assert session.in_transaction is True
        session.abort_transaction()
    _assert_no_downstream_surfaces(mongo_context, collections_before, row_counts_before)


@pytest.mark.parametrize(
    ("decision_value", "expected", "positive"),
    [("ACCEPTED", "ACCEPTED", True), ("DECLINED", "DECLINED", False), ("REQUIRES_REVIEW", "REQUIRES_REVIEW", False)],
)
def test_real_single_states(
    mongo_context: MongoContext,
    decision_value: str,
    expected: str,
    positive: bool,
) -> None:
    """Each one-row P2 state projects exactly and only ACCEPTED is positive."""
    value = _decision(decision_value=decision_value)
    _persist(mongo_context, value)
    result = _compose(mongo_context)
    assert result.state.value == expected
    assert result.is_currently_accepted is positive
    assert result.is_usable is positive
    if not positive:
        assert result.decisive_decision_id is None
        assert result.decisive_decision_fingerprint is None


def test_real_empty_history_is_no_decision(mongo_context: MongoContext) -> None:
    """No exact P9 rows produce NO_DECISION and no selected evidence."""
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION
    assert result.is_currently_accepted is False
    assert result.candidate_decision_ids == ()


@pytest.mark.parametrize("decision_value", ["ACCEPTED", "DECLINED", "REQUIRES_REVIEW"])
def test_real_future_rows_are_excluded(mongo_context: MongoContext, decision_value: str) -> None:
    """Explicit evaluated_at excludes future decisions without a wall-clock read."""
    _persist(mongo_context, _decision(decision_value=decision_value, effective_from=BASE + timedelta(days=1)))
    result = _compose(mongo_context, evaluated_at=BASE)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION
    assert result.normalized_decision_count == 1
    assert result.eligible_decision_count == 0


@pytest.mark.parametrize("decision_value", ["ACCEPTED", "DECLINED", "REQUIRES_REVIEW"])
def test_real_exact_replay_is_one_row_and_normalized(mongo_context: MongoContext, decision_value: str) -> None:
    """P9 idempotent replay stays one durable row and one semantic decision."""
    value = _decision(decision_value=decision_value)
    _persist(mongo_context, value)
    _persist(mongo_context, value)
    assert mongo_context.collection.count_documents({}) == 1
    result = _compose(mongo_context)
    assert result.normalized_decision_count == 1
    assert result.eligible_decision_count == 1
    assert result.state.value == decision_value


@pytest.mark.parametrize(
    ("left", "right"),
    [("ACCEPTED", "ACCEPTED"), ("ACCEPTED", "DECLINED"), ("ACCEPTED", "REQUIRES_REVIEW"), ("DECLINED", "REQUIRES_REVIEW"), ("DECLINED", "DECLINED"), ("REQUIRES_REVIEW", "REQUIRES_REVIEW")],
)
def test_real_distinct_eligible_rows_are_ambiguous_without_precedence(
    mongo_context: MongoContext, left: str, right: str
) -> None:
    """Every two distinct eligible truths remains AMBIGUOUS; no latest-wins."""
    _persist(mongo_context, _decision(decision_value=left, suffix="left"))
    _persist(mongo_context, _decision(decision_value=right, suffix="right"))
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS
    assert result.is_currently_accepted is False
    assert result.decisive_decision_id is None


def test_real_later_effective_does_not_supersede_earlier(mongo_context: MongoContext) -> None:
    """Different effective times do not invent supersession or newest-wins."""
    _persist(mongo_context, _decision(suffix="early", effective_from=BASE + timedelta(minutes=1)))
    _persist(mongo_context, _decision(decision_value="DECLINED", suffix="late", effective_from=BASE + timedelta(minutes=2)))
    result = _compose(mongo_context, evaluated_at=BASE + timedelta(minutes=3))
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS


def test_real_same_effective_distinct_rows_are_ambiguous(mongo_context: MongoContext) -> None:
    """Distinct same-effective rows remain ambiguous."""
    _persist(mongo_context, _decision(suffix="same-a"))
    _persist(mongo_context, _decision(suffix="same-b"))
    assert _compose(mongo_context).state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.AMBIGUOUS


def test_real_positive_projection_binds_exact_p2_p1_representative_role_scope(mongo_context: MongoContext) -> None:
    """A single ACCEPTED result exposes exact P2/P1 and representative evidence."""
    value = _decision()
    _persist(mongo_context, value)
    result = _compose(mongo_context)
    assert result.decisive_decision_id == value.decision_id
    assert result.decisive_decision_fingerprint == value.fingerprint
    assert result.representation_authority_id == value.representation_authority_id
    assert result.representation_authority_fingerprint == value.representation_authority_fingerprint
    assert result.representative_principal_id == value.representative_principal_id
    assert result.representative_role == value.representative_role
    assert result.decisive_representation_scope_capabilities == value.representation_scope_capabilities
    assert result.evaluated_at == BASE + timedelta(hours=1)


def test_real_p1_authority_and_representative_isolation(mongo_context: MongoContext) -> None:
    """Different P1 authority and representative histories never leak."""
    exact = _decision()
    _persist(mongo_context, exact)
    other_authority = _decision(source_authority=_authority(authority_id="authority-other"), suffix="other-authority")
    _persist(mongo_context, other_authority)
    same_id_other_fingerprint = _decision(
        source_authority=_authority(source_evidence_fingerprint="7" * 128),
        suffix="same-id-other-fingerprint",
    )
    _persist(mongo_context, same_id_other_fingerprint)
    other_rep = _decision(source_authority=_authority(representative_principal_id=REPRESENTATIVE_B), suffix="other-rep")
    _persist(mongo_context, other_rep)
    assert _compose(mongo_context).candidate_decision_ids == (exact.decision_id,)
    assert _compose(mongo_context, representative_principal_id=REPRESENTATIVE_B).candidate_decision_ids == (other_rep.decision_id,)


def test_real_tenant_matter_client_subject_isolation(mongo_context: MongoContext) -> None:
    """Tenant, matter, matter fingerprint, party and subject are exact filters."""
    exact = _decision()
    _persist(mongo_context, exact)
    _persist(mongo_context, _decision(source_authority=_authority(tenant_id=TENANT_B), suffix="tenant-b"))
    _persist(mongo_context, _decision(source_authority=_authority(case_matter_id=OTHER_MATTER), suffix="matter"))
    _persist(mongo_context, _decision(source_authority=_authority(matter_fingerprint=OTHER_MATTER_FP), suffix="matter-fp"))
    _persist(mongo_context, _decision(source_authority=_authority(client_party_id=OTHER_PARTY), suffix="party"))
    _persist(mongo_context, _decision(source_authority=_authority(subject_identity_fingerprint=OTHER_SUBJECT_FP), suffix="subject"))
    result = _compose(mongo_context)
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED
    assert result.candidate_decision_ids == (exact.decision_id,)


def test_real_role_mismatch_fails_closed_after_p9_filter(mongo_context: MongoContext) -> None:
    """P9 omits role from its query; P22 must reject a mismatched returned role."""
    mismatched = _decision(source_authority=_authority(representative_role="LEGAL_PARTNER"), suffix="role-mismatch")
    _persist(mongo_context, mismatched)
    result = _compose(
        mongo_context,
        representation_authority_id=mismatched.representation_authority_id,
        representation_authority_fingerprint=mismatched.representation_authority_fingerprint,
        representative_role=ROLE,
    )
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED
    assert result.is_currently_accepted is False


def test_real_malformed_row_is_rejected_by_strict_p9_hydration(mongo_context: MongoContext) -> None:
    """A durable malformed fingerprint fails closed before positive projection."""
    value = _decision()
    _persist(mongo_context, value)
    counted = CorruptingCollection(
        mongo_context.collection,
        {"decision_id": value.decision_id, "fingerprint": "9" * 128},
    )
    with pytest.raises(LegalClientMatterRepresentationFirmDecisionCurrentnessComposerError) as error:
        _compose(mongo_context, target_collection=counted)
    assert error.value.code == "L9C11_P22_COMPOSER_HISTORY_READ_FAILED"
    assert counted.write_calls == 0


def test_real_domain_mixed_valid_and_corrupt_history_is_corrupt_blocked() -> None:
    """The pure P22 seam blocks malformed evidence rather than falling back."""
    value = _decision()
    result = project_legal_client_matter_representation_firm_decision_currentness(
        tenant_id=TENANT_A,
        case_matter_id=MATTER,
        matter_fingerprint=MATTER_FP,
        client_party_id=PARTY,
        subject_identity_fingerprint=SUBJECT_FP,
        representation_authority_id=value.representation_authority_id,
        representation_authority_fingerprint=value.representation_authority_fingerprint,
        representative_principal_id=REPRESENTATIVE_A,
        representative_role=ROLE,
        evaluated_at=BASE + timedelta(hours=1),
        decisions=(value, object()),  # type: ignore[arg-type]
    )
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.CORRUPT_BLOCKED
    assert result.is_currently_accepted is False


def test_real_history_order_and_repeat_composition_are_deterministic(mongo_context: MongoContext) -> None:
    """P9 sorting and P22 canonical ordering produce repeatable snapshots."""
    first = _decision(suffix="order-first", effective_from=BASE)
    second = _decision(decision_value="DECLINED", suffix="order-second", effective_from=BASE + timedelta(minutes=1))
    _persist(mongo_context, first)
    _persist(mongo_context, second)
    forward = _compose(mongo_context)
    repeated = _compose(mongo_context)
    assert forward == repeated
    reverse_database = mongo_context.client[f"wilsy_l9c11_p22r_order_{uuid.uuid4().hex}"]
    try:
        reverse_collection = reverse_database[registry.COLLECTION]
        registry.ensure_indexes(reverse_collection)
        reverse_context = MongoContext(mongo_context.client, reverse_database, reverse_collection, mongo_context.server_version, mongo_context.pymongo_version)
        _persist(reverse_context, second)
        _persist(reverse_context, first)
        assert _compose(reverse_context) == forward
    finally:
        mongo_context.client.drop_database(reverse_database.name)


def test_real_explicit_evaluated_at_has_no_clock_reads_or_implicit_dependency(mongo_context: MongoContext) -> None:
    """Explicit aware UTC evaluation controls projection and source has no clock call."""
    future = _decision(effective_from=BASE + timedelta(days=1))
    _persist(mongo_context, future)
    result = _compose(mongo_context, evaluated_at=BASE)
    assert result.evaluated_at == BASE
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.NO_DECISION
    source = Path("tools/eos/legal_operations/domain/legal_client_matter_representation_firm_decision_currentness.py").read_text(encoding="utf-8")
    assert "datetime.now" not in source
    assert "datetime.utcnow" not in source


def test_real_zero_writes_and_no_lifecycle_or_downstream_authority(mongo_context: MongoContext) -> None:
    """Composition changes no P2 rows and creates no currentness/downstream truth."""
    _persist(mongo_context, _decision())
    before_rows = mongo_context.collection.count_documents({})
    before_collections = set(mongo_context.database.list_collection_names())
    before_counts = {
        name: mongo_context.database[name].count_documents({})
        for name in before_collections
    }
    counted = CountingCollection(mongo_context.collection)
    result = _compose(mongo_context, target_collection=counted)
    after_collections = set(mongo_context.database.list_collection_names())
    assert result.state is LegalClientMatterRepresentationFirmDecisionCurrentnessState.ACCEPTED
    assert counted.write_calls == 0
    assert mongo_context.collection.count_documents({}) == before_rows
    assert after_collections == before_collections
    _assert_no_downstream_surfaces(mongo_context, before_collections, before_counts)
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_representation_firm_decision_currentness_composer.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assert all(token not in source for token in ("insert_one", "update_one", "delete_one", "start_transaction", "commit_transaction", "abort_transaction"))
    imports = " ".join(ast.unparse(node).lower() for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
    assert all(token not in imports for token in ("iam", "representation_formation", "court", "finance", "http", "ui", "node"))


# ARTIFACT: test_legal_client_matter_representation_firm_decision_currentness_real_mongo.py
# VERSION: v1.0.0-L9C11-P22R-FIRM-REPRESENTATION-DECISION-CURRENTNESS-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P22 currentness real-Mongo evidence only
# TENANT POSTURE: UUID-isolated database and exact P1/representative/role lineage
# FAIL-CLOSED POSTURE: unavailable runtime skips; corruption, multiplicity and isolation fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
