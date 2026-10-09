"""Real-Mongo certificate for the L9C11-P19 P18 evidence registry.

TITLE: WILSY OS Legal Client Representation Authorization Evidence Registry Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P19-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the published P18 immutable evidence registry against a writable,
         UUID-isolated Mongo replica set: physical indexes, caller-owned
         transactions, canonical BSON, rollback, replay/collision behavior,
         tenant isolation, deterministic history and strict corruption failure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_representation_authorization_evidence_registry_real_mongo.py
COLLABORATION / OWNERSHIP: P17 owns the immutable evidence value; P18 owns the
                            registry contract; P19 owns only disposable runtime
                            persistence evidence. IAM, currentness, orchestration,
                            Representation formation, Court and finance remain
                            separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P19 certifies real replica-set index, transaction,
           BSON, durability, rollback, replay, collision, race, tenant-history
           and strict-corruption behavior for the published P18 registry.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: URI credentials and bearer material are never
                             printed; all data is synthetic and opaque.
TENANT BOUNDARY: Every operation is exact tenant scoped; canonical ``wilsy``
                 is prohibited and only UUID-isolated disposable databases are used.
AUTHORITY BOUNDARY: Disposable P18 persistence evidence only. No IAM, currentness,
                    lifecycle, orchestration, Representation, Court, HTTP/UI/Node
                    or financial authority is added.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for execution
                              and settlement truth.
TRANSACTION BOUNDARY: The certificate owns disposable session lifecycle; the
                      registry owns no transaction lifecycle.
FAIL-CLOSED DECLARATION: Topology, index, rollback, corruption, isolation,
                         collision, race and cleanup failures fail certification.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import ast
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from threading import Barrier
from typing import Any, Iterator, cast
import uuid

import pymongo
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacityType,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authorization_evidence import (
    REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS,
    LegalClientMatterRepresentationAuthorizationDecision,
    LegalClientMatterRepresentationAuthorizationEvidence,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_representation_authorization_evidence_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128


class MongoContext:
    """Disposable Mongo handles and topology facts for one certificate test."""

    def __init__(self, client: MongoClient[Any], database: Any, collection: Any, version: str) -> None:
        self.client = client
        self.database = database
        self.collection = collection
        self.version = version


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield one UUID-isolated database on the sanctioned writable replica set."""
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
        except PyMongoError as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version
        database_name = f"wilsy_l9c11_rep_auth_ev_{uuid.uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        collection = database.get_collection(registry.COLLECTION)
        registry.ensure_indexes(collection)
        registry.ensure_indexes(collection)
        yield MongoContext(client, database, collection, cast(str, server_version))
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _evidence(
    *,
    tenant: str = "tenant-real-a",
    matter_id: str = "matter-real-p19",
    matter_fingerprint: str = HEX_A,
    party_id: str = "party-real-p19",
    subject_fingerprint: str = HEX_B,
    appointing_principal: str = "principal-client-p19",
    acting_capacity_id: str = "capacity-real-p19",
    acting_capacity_fingerprint: str = HEX_C,
    engagement_id: str = "engagement-real-p19",
    engagement_fingerprint: str = HEX_D,
    mandate_id: str = "mandate-real-p19",
    mandate_fingerprint: str = HEX_E,
    representative_principal: str = "principal-representative-p19",
    representative_role: str = "LEGAL_ATTORNEY",
    source_reference: str = "source:p19",
    source_fingerprint: str = HEX_A,
    offset: int = 0,
    idempotency_key: str | None = None,
) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Construct valid P17 evidence through the published domain API only."""
    occurred = BASE + timedelta(minutes=offset)
    return LegalClientMatterRepresentationAuthorizationEvidence(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_reference="client:subject-real-p19",
        subject_identity_fingerprint=subject_fingerprint,
        client_subject_principal_id=appointing_principal,
        appointing_principal_id=appointing_principal,
        appointing_principal_status=PrincipalStatus.ACTIVE,
        appointing_membership_status=TenantMembershipStatus.ACTIVE,
        appointing_membership_revision=3,
        appointing_role="LEGAL_CLIENT",
        appointing_role_assignment_revision=4,
        client_visibility_reference="visibility:p19",
        client_visibility_fingerprint=HEX_D,
        client_visibility_status="ACTIVE",
        acting_capacity_id=acting_capacity_id,
        acting_capacity_fingerprint=acting_capacity_fingerprint,
        acting_capacity_type=LegalClientActingCapacityType.SELF,
        engagement_id=engagement_id,
        engagement_fingerprint=engagement_fingerprint,
        mandate_id=mandate_id,
        mandate_fingerprint=mandate_fingerprint,
        mandate_scope_reference="scope:p19",
        mandate_scope_fingerprint=HEX_E,
        mandate_capabilities=["ADVISORY", "NEGOTIATION"],
        representative_principal_id=representative_principal,
        representative_principal_status=PrincipalStatus.ACTIVE,
        representative_membership_status=TenantMembershipStatus.ACTIVE,
        representative_membership_revision=5,
        representative_role_assignment_revision=6,
        representative_role=representative_role,
        representative_eligibility_policy_version="roles:v1.29.0",
        representation_scope_capabilities=["ADVISORY"],
        decision=LegalClientMatterRepresentationAuthorizationDecision.AUTHORIZED,
        source_evidence_reference=source_reference,
        source_evidence_fingerprint=source_fingerprint,
        occurred_at=occurred,
        effective_from=occurred + timedelta(minutes=1),
        idempotency_key=idempotency_key or f"idempotency:p19:{tenant}:{offset}:{source_reference}",
    )


def _history_kwargs(value: LegalClientMatterRepresentationAuthorizationEvidence) -> dict[str, str]:
    """Return the exact published P18 history filter fields."""
    return {
        "tenant_id": value.tenant_id,
        "case_matter_id": value.case_matter_id,
        "matter_fingerprint": value.matter_fingerprint,
        "client_party_id": value.client_party_id,
        "subject_identity_fingerprint": value.subject_identity_fingerprint,
        "appointing_principal_id": value.appointing_principal_id,
        "acting_capacity_id": value.acting_capacity_id,
        "acting_capacity_fingerprint": value.acting_capacity_fingerprint,
        "engagement_id": value.engagement_id,
        "engagement_fingerprint": value.engagement_fingerprint,
        "mandate_id": value.mandate_id,
        "mandate_fingerprint": value.mandate_fingerprint,
        "representative_principal_id": value.representative_principal_id,
        "representative_role": value.representative_role,
    }


def _commit(context: MongoContext, value: LegalClientMatterRepresentationAuthorizationEvidence) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Persist one value under caller-owned transaction lifecycle."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.persist_authorization_evidence(value, context.collection, session=session)
        session.commit_transaction()
        return result


def _read(context: MongoContext, tenant_id: str, evidence_id: str) -> LegalClientMatterRepresentationAuthorizationEvidence:
    """Read one value under a fresh caller-owned transaction."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.get_authorization_evidence(tenant_id, evidence_id, context.collection, session=session)
        session.commit_transaction()
        return result


def _history(context: MongoContext, value: LegalClientMatterRepresentationAuthorizationEvidence, *, limit: int = 500) -> tuple[LegalClientMatterRepresentationAuthorizationEvidence, ...]:
    """Read exact appointment-lineage history under a caller transaction."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.list_authorization_evidence_for_context(
            **_history_kwargs(value), evidence_collection=context.collection, session=session, limit=limit
        )
        session.commit_transaction()
        return result


def test_real_topology_and_index_metadata_are_exact_and_idempotent(mongo_context: MongoContext) -> None:
    """Prove writable topology, replica-set identity, indexes and idempotence."""
    assert mongo_context.version
    entries = {
        item["name"]: item
        for item in mongo_context.collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(entries) == {
        registry.EVIDENCE_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }
    assert list(entries[registry.EVIDENCE_ID_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1), ("evidence_id", 1)
    ]
    assert list(entries[registry.FINGERPRINT_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1), ("fingerprint", 1)
    ]
    assert list(entries[registry.IDEMPOTENCY_INDEX_NAME]["key"].items()) == [
        ("tenant_id", 1), ("idempotency_key", 1)
    ]
    assert list(entries[registry.HISTORY_INDEX_NAME]["key"].items()) == [
        (field, 1) for field in registry.HISTORY_INDEX_FIELDS
    ]
    assert entries[registry.EVIDENCE_ID_INDEX_NAME].get("unique") is True
    assert entries[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert entries[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert entries[registry.HISTORY_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in item for item in entries.values())
    before = {name: dict(item["key"]) for name, item in entries.items()}
    registry.ensure_indexes(mongo_context.collection)
    after = {
        item["name"]: dict(item["key"])
        for item in mongo_context.collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert after == before


def test_real_transaction_contract_and_session_visibility(mongo_context: MongoContext) -> None:
    """Missing/inactive transactions reject; caller transaction is preserved."""
    value = _evidence()
    with pytest.raises(registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError):
        registry.persist_authorization_evidence(value, mongo_context.collection, session=None)
    with mongo_context.client.start_session() as inactive:
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryTransactionRequiredError):
            registry.persist_authorization_evidence(value, mongo_context.collection, session=inactive)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.persist_authorization_evidence(value, mongo_context.collection, session=session) == value
        assert session.in_transaction
        assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 0
        session.commit_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_commit_durability_and_exact_bson_round_trip(mongo_context: MongoContext) -> None:
    """Committed raw BSON is exact except tuple-backed arrays and Mongo _id."""
    value = _evidence()
    assert _commit(mongo_context, value) == value
    row = mongo_context.collection.find_one({"tenant_id": value.tenant_id, "evidence_id": value.evidence_id})
    assert row is not None
    row.pop("_id", None)
    expected = value.to_dict()
    assert set(row) == REPRESENTATION_AUTHORIZATION_EVIDENCE_FIELDS
    assert set(row) == set(expected)
    for field in set(expected) - {"mandate_capabilities", "representation_scope_capabilities"}:
        assert row[field] == expected[field]
    assert row["mandate_capabilities"] == list(value.mandate_capabilities)
    assert row["representation_scope_capabilities"] == list(value.representation_scope_capabilities)
    assert _read(mongo_context, value.tenant_id, value.evidence_id) == value


def test_real_abort_rolls_back_without_registry_override(mongo_context: MongoContext) -> None:
    """Caller abort removes the uncommitted evidence row completely."""
    value = _evidence()
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        registry.persist_authorization_evidence(value, mongo_context.collection, session=session)
        assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 0


def test_real_exact_replay_is_one_durable_row(mongo_context: MongoContext) -> None:
    """Exact replay returns the historic value without a duplicate."""
    value = _evidence()
    assert _commit(mongo_context, value) == value
    assert _commit(mongo_context, value) == value
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_divergent_identities_fail_closed(mongo_context: MongoContext) -> None:
    """Divergent idempotency, evidence-id and fingerprint collisions reject."""
    value = _evidence()
    _commit(mongo_context, value)
    divergent_idempotency = _evidence(offset=1, idempotency_key=value.idempotency_key)
    divergent_evidence_id = _evidence(offset=2, idempotency_key="idempotency:p19:divergent-id")
    object.__setattr__(divergent_evidence_id, "evidence_id", value.evidence_id)
    divergent_fingerprint = _evidence(offset=3, idempotency_key="idempotency:p19:divergent-fp")
    object.__setattr__(divergent_fingerprint, "fingerprint", value.fingerprint)
    for candidate in (divergent_idempotency, divergent_evidence_id, divergent_fingerprint):
        with mongo_context.client.start_session() as session:
            session.start_transaction()
            with pytest.raises(registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError):
                registry.persist_authorization_evidence(candidate, mongo_context.collection, session=session)
            session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_duplicate_key_race_has_one_canonical_truth(mongo_context: MongoContext) -> None:
    """Concurrent exact contenders leave one row and never create a second truth."""
    value = _evidence()
    barrier = Barrier(2)

    def contender(_: int) -> str:
        try:
            with mongo_context.client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=10)
                result = registry.persist_authorization_evidence(value, mongo_context.collection, session=session)
                session.commit_transaction()
                assert result == value
                return "success"
        except (registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError, PyMongoError):
            return "retry"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(contender, range(2)))
    assert "success" in outcomes
    assert set(outcomes) <= {"success", "retry"}
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_divergent_duplicate_race_has_one_truth(mongo_context: MongoContext) -> None:
    """Concurrent divergent contenders cannot create two rows for one identity."""
    first = _evidence()
    second = _evidence(offset=1, idempotency_key=first.idempotency_key)
    barrier = Barrier(2)

    def contender(value: LegalClientMatterRepresentationAuthorizationEvidence) -> str:
        try:
            with mongo_context.client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=10)
                registry.persist_authorization_evidence(value, mongo_context.collection, session=session)
                session.commit_transaction()
                return "success"
        except (registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryConflictError, registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryRetryRequiredError, PyMongoError):
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(contender, (first, second)))
    assert outcomes.count("success") == 1
    assert outcomes.count("rejected") == 1
    assert mongo_context.collection.count_documents({"tenant_id": first.tenant_id}) == 1


def test_real_tenant_identity_fingerprint_idempotency_and_history_isolation(mongo_context: MongoContext) -> None:
    """Overlapping opaque identities remain isolated by tenant in every read."""
    tenant_a = _evidence(tenant="tenant-real-a")
    tenant_b = _evidence(tenant="tenant-real-b")
    _commit(mongo_context, tenant_a)
    _commit(mongo_context, tenant_b)
    assert _read(mongo_context, tenant_a.tenant_id, tenant_a.evidence_id) == tenant_a
    assert _read(mongo_context, tenant_b.tenant_id, tenant_b.evidence_id) == tenant_b
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.get_authorization_evidence_by_fingerprint(tenant_b.tenant_id, tenant_b.fingerprint, mongo_context.collection, session=session) == tenant_b
        assert registry.get_authorization_evidence_by_idempotency_key(tenant_a.tenant_id, tenant_a.idempotency_key, mongo_context.collection, session=session) == tenant_a
        for read in (
            lambda: registry.get_authorization_evidence("tenant-missing", tenant_a.evidence_id, mongo_context.collection, session=session),
            lambda: registry.get_authorization_evidence_by_fingerprint("tenant-missing", tenant_a.fingerprint, mongo_context.collection, session=session),
            lambda: registry.get_authorization_evidence_by_idempotency_key("tenant-missing", tenant_a.idempotency_key, mongo_context.collection, session=session),
        ):
            with pytest.raises(registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryNotFoundError):
                read()
        session.abort_transaction()
    assert _history(mongo_context, tenant_a) == (tenant_a,)
    assert _history(mongo_context, tenant_b) == (tenant_b,)


def test_real_multiple_immutable_rows_history_order_and_exact_filter(mongo_context: MongoContext) -> None:
    """Distinct canonical intent shares one lineage and history order is deterministic."""
    later = _evidence(offset=2, source_reference="source:p19-later", source_fingerprint=HEX_C)
    earlier = _evidence(offset=1, source_reference="source:p19-earlier", source_fingerprint=HEX_D)
    neighbors = (
        _evidence(matter_id="neighbor-matter", offset=3),
        _evidence(party_id="neighbor-party", offset=4),
        _evidence(subject_fingerprint=HEX_C, offset=5),
        _evidence(appointing_principal="neighbor-client", offset=6),
        _evidence(acting_capacity_id="neighbor-capacity", offset=7),
        _evidence(acting_capacity_fingerprint=HEX_D, offset=8),
        _evidence(engagement_id="neighbor-engagement", offset=9),
        _evidence(engagement_fingerprint=HEX_E, offset=10),
        _evidence(mandate_id="neighbor-mandate", offset=11),
        _evidence(mandate_fingerprint=HEX_A, offset=12),
        _evidence(representative_principal="neighbor-representative", offset=13),
        _evidence(representative_role="LEGAL_PARTNER", offset=14),
    )
    for value in (neighbors[0], later, neighbors[1], neighbors[2], neighbors[3], neighbors[4], neighbors[5], neighbors[6], neighbors[7], neighbors[8], neighbors[9], neighbors[10], neighbors[11], earlier):
        _commit(mongo_context, value)
    history = _history(mongo_context, earlier)
    assert history == (earlier, later)
    assert [item.effective_from for item in history] == sorted(item.effective_from for item in history)
    assert all(item.tenant_id == earlier.tenant_id for item in history)
    assert registry.HISTORY_INDEX_FIELDS[:14] == (
        "tenant_id", "case_matter_id", "matter_fingerprint", "client_party_id",
        "subject_identity_fingerprint", "appointing_principal_id", "acting_capacity_id",
        "acting_capacity_fingerprint", "engagement_id", "engagement_fingerprint", "mandate_id",
        "mandate_fingerprint", "representative_principal_id", "representative_role",
    )
    assert registry.HISTORY_INDEX_FIELDS[14:] == ("effective_from", "occurred_at", "fingerprint", "evidence_id")


def test_real_empty_history_is_empty_tuple(mongo_context: MongoContext) -> None:
    """An exact lineage with no rows returns an immutable empty tuple."""
    assert _history(mongo_context, _evidence()) == ()


@pytest.mark.parametrize(
    "field,bad_value,lookup",
    [
        ("schema", "CORRUPT", "evidence"),
        ("decision", "DECLINED", "evidence"),
        ("acting_capacity_type", "REPRESENTATIVE", "evidence"),
        ("representative_role", "LEGAL_CLIENT", "evidence"),
        ("matter_fingerprint", HEX_E, "evidence"),
        ("mandate_capabilities", ["NEGOTIATION"], "evidence"),
        ("representation_scope_capabilities", ["NEGOTIATION"], "evidence"),
        ("representative_membership_revision", -1, "evidence"),
        ("evidence_id", "client-representation-authorization:corrupt", "fingerprint"),
        ("fingerprint", HEX_E, "evidence"),
    ],
)
def test_real_strict_hydration_rejects_corrupt_rows(
    mongo_context: MongoContext, field: str, bad_value: object, lookup: str
) -> None:
    """Every representative persisted corruption fails closed without skipping."""
    value = _evidence()
    _commit(mongo_context, value)
    changed = mongo_context.collection.update_one(
        {"tenant_id": value.tenant_id, "evidence_id": value.evidence_id},
        {"$set": {field: bad_value}},
    )
    assert changed.modified_count == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError):
            if lookup == "fingerprint":
                registry.get_authorization_evidence_by_fingerprint(value.tenant_id, value.fingerprint, mongo_context.collection, session=session)
            else:
                registry.get_authorization_evidence(value.tenant_id, value.evidence_id, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_history_limit_and_wrong_context_fail_closed(mongo_context: MongoContext) -> None:
    """History is bounded, exact and rejects overflow rather than truncating."""
    first = _evidence(source_reference="source:limit-a", source_fingerprint=HEX_A)
    second = _evidence(offset=1, source_reference="source:limit-b", source_fingerprint=HEX_B)
    _commit(mongo_context, first)
    _commit(mongo_context, second)
    with pytest.raises(registry.LegalClientMatterRepresentationAuthorizationEvidenceRegistryPersistedRecordInvalidError):
        _history(mongo_context, first, limit=1)
    assert _history(mongo_context, first, limit=2) == (first, second)
    wrong_context = _evidence(tenant="tenant-missing")
    assert wrong_context.evidence_id != first.evidence_id
    assert wrong_context.fingerprint != first.fingerprint
    assert _history(mongo_context, wrong_context) == ()


def test_real_registry_static_authority_surface_is_narrow() -> None:
    """The published registry has no live authority, currentness or transport imports."""
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_representation_authorization_evidence_registry.py"
    ).read_text()
    imports = " ".join(
        ast.unparse(node).lower()
        for node in ast.walk(ast.parse(source))
        if isinstance(node, (ast.Import, ast.ImportFrom))
    )
    assert "principal_status" not in imports
    assert "tenant_membership" not in imports
    assert "currentness" not in imports
    assert "legal_client_matter_representation_authority" not in imports
    assert "http" not in imports
    assert "pymongo" in imports
    assert "CURRENT_POINTER" not in source
    assert "consumption_state" not in source.lower()
    assert "LegalClientMatterRepresentationAuthorizationEvidence(" not in source


# ARTIFACT: test_legal_client_matter_representation_authorization_evidence_registry_real_mongo.py
# VERSION: v1.0.0-L9C11-P19-CLIENT-REPRESENTATION-AUTHORIZATION-EVIDENCE-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P18 registry runtime evidence only
# TENANT POSTURE: UUID-isolated exact-tenant evidence; canonical wilsy excluded
# FAIL-CLOSED POSTURE: topology, indexes, transactions, corruption, isolation, history and races reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
