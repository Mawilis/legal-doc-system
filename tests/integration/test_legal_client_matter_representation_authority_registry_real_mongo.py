"""Real-Mongo certificate for the L9C11-P8 Representation-authority registry.

TITLE: WILSY OS Legal Client Representation Authority Registry Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P8-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the published P7 append-only registry against a writable,
         UUID-isolated Mongo replica set: physical indexes, caller-owned
         transactions, canonical BSON, replay/collision behavior, races,
         tenant isolation, deterministic history and strict corruption failure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_representation_authority_registry_real_mongo.py
COLLABORATION / OWNERSHIP: P1 owns the immutable authority value; P7 owns the
                            registry contract; P8 owns only disposable runtime
                            evidence. IAM, currentness, lifecycle, formation,
                            Court and finance remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P8 certifies real replica-set durability, rollback,
           replay/collision classification, duplicate-key races, tenant-bound
           history, strict corruption rejection and UUID database isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: URI credentials and bearer material are never
                             printed; all fixtures use opaque synthetic values.
TENANT BOUNDARY: Every registry operation and lineage history query is exact
                 tenant scoped; canonical database ``wilsy`` is prohibited.
AUTHORITY BOUNDARY: Disposable persistence evidence only. This certificate
                    does not add IAM, currentness, lifecycle, Representation,
                    Court, HTTP/UI/Node or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement.
TRANSACTION BOUNDARY: The certificate owns sessions and transaction lifecycle;
                      the registry owns none.
FAIL-CLOSED DECLARATION: Topology, rollback, corruption, isolation, collision,
                         race and cleanup failures fail certification.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
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

from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    REPRESENTATION_AUTHORITY_FIELDS,
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)
from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
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
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128


class MongoContext:
    """Disposable runtime handles and topology evidence for one test."""

    def __init__(self, client: MongoClient[Any], database: Any, collection: Any) -> None:
        self.client = client
        self.database = database
        self.collection = collection


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield a UUID-isolated database on the sanctioned writable replica set."""
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
        database_name = f"wilsy_l9c11_repca_{uuid.uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        collection = database.get_collection(registry.COLLECTION)
        registry.ensure_indexes(collection)
        registry.ensure_indexes(collection)
        yield MongoContext(client, database, collection)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _upstream(
    *,
    tenant: str,
    matter_id: str,
    matter_fingerprint: str,
    party_id: str,
    subject_fingerprint: str,
    representative_principal: str,
    offset: int,
    authority_id: str | None = None,
    idempotency_key: str | None = None,
) -> LegalClientMatterRepresentationAuthority:
    """Construct upstream immutable values, then use the P1 canonical factory."""
    occurred = BASE + timedelta(minutes=offset)
    capacity = LegalClientActingCapacity(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        capacity_id="capacity-real-p8",
        principal_id=representative_principal,
        party_id=party_id,
        subject_reference="client:subject-real-p8",
        subject_identity_fingerprint=subject_fingerprint,
        capacity_type="REPRESENTATIVE",
        effective_from=occurred,
        effective_until=occurred + timedelta(days=90),
        source_evidence_reference="capacity-source:p8",
        source_evidence_fingerprint=HEX_A,
    )
    mandate = LegalClientMatterMandate(
        mandate_id="mandate-real-p8",
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_identity_fingerprint=subject_fingerprint,
        grant_actor_principal_id="principal-client-p8",
        acting_capacity_id=capacity.capacity_id,
        acting_capacity_fingerprint=capacity.fingerprint,
        breadth="LIMITED",
        scope_reference="scope:p8",
        scope_fingerprint=HEX_B,
        capabilities=["ADVISORY", "NEGOTIATION"],
        source_evidence_reference="mandate-source:p8",
        source_evidence_fingerprint=HEX_C,
        client_grant_reference="grant:p8",
        client_grant_fingerprint=HEX_D,
        firm_acknowledgment_reference="ack:p8",
        firm_acknowledgment_fingerprint=HEX_E,
        occurred_at=occurred,
        effective_from=occurred + timedelta(minutes=1),
        effective_until=occurred + timedelta(days=60),
        idempotency_key="mandate-idempotency:p8",
    )
    engagement = LegalClientMatterEngagement(
        engagement_id="engagement-real-p8",
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_reference="client:subject-real-p8",
        subject_identity_fingerprint=subject_fingerprint,
        acting_capacity_id=capacity.capacity_id,
        acting_capacity_fingerprint=capacity.fingerprint,
        client_acceptance_id="acceptance:p8",
        client_acceptance_fingerprint=HEX_A,
        instrument_id="instrument:p8",
        version="1",
        instrument_fingerprint=HEX_B,
        content_fingerprint=HEX_C,
        mandate_id=mandate.mandate_id,
        mandate_scope=mandate.scope_reference,
        mandate_fingerprint=mandate.fingerprint,
        conflict_disposition_id="conflict:p8",
        conflict_disposition_fingerprint=HEX_D,
        firm_decision_id="firm-decision:p8",
        decision_actor_principal_id="principal-firm:p8",
        firm_decision_fingerprint=HEX_E,
        authorization_evidence_reference="engagement-auth:p8",
        authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference="engagement-source:p8",
        source_evidence_fingerprint=HEX_B,
        effective_from=occurred + timedelta(minutes=2),
        idempotency_key="engagement-idempotency:p8",
    )
    return LegalClientMatterRepresentationAuthority.from_canonical(
        authority_id=authority_id or f"authority-{matter_id}-{offset}",
        engagement=engagement,
        mandate=mandate,
        acting_capacity=capacity,
        representative_principal_id=representative_principal,
        representative_role="LEGAL_PRACTITIONER",
        representation_scope_capabilities=["ADVISORY"],
        decision=LegalClientMatterRepresentationAuthorityDecision.APPOINTED,
        appointing_principal_id="principal-client-p8",
        source_evidence_reference="appointment-source:p8",
        source_evidence_fingerprint=HEX_C,
        authorization_evidence_reference="appointment-authorization:p8",
        authorization_evidence_fingerprint=HEX_D,
        occurred_at=occurred + timedelta(minutes=3),
        effective_from=occurred + timedelta(minutes=4),
        effective_until=occurred + timedelta(days=30),
        idempotency_key=idempotency_key or f"authority-idempotency:{matter_id}:{offset}",
    )


def _authority(**overrides: object) -> LegalClientMatterRepresentationAuthority:
    """Return a valid P1-factory authority with deterministic overrides."""
    values: dict[str, object] = {
        "tenant": "tenant-real-a",
        "matter_id": "matter-real-p8",
        "matter_fingerprint": HEX_A,
        "party_id": "party-real-p8",
        "subject_fingerprint": HEX_B,
        "representative_principal": "principal-representative-p8",
        "offset": 0,
        "authority_id": None,
        "idempotency_key": None,
    }
    values.update(overrides)
    return _upstream(**cast(dict[str, Any], values))


def _commit(context: MongoContext, value: LegalClientMatterRepresentationAuthority) -> LegalClientMatterRepresentationAuthority:
    """Persist one value under caller-owned transaction lifecycle."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.persist_representation_authority(value, context.collection, session=session)
        session.commit_transaction()
        return result


def _read(
    context: MongoContext, tenant: str, authority_id: str
) -> LegalClientMatterRepresentationAuthority:
    """Read one value in a caller-owned read transaction."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.get_representation_authority(
            tenant, authority_id, context.collection, session=session
        )
        session.commit_transaction()
        return result


def _expected_bson_payload(value: LegalClientMatterRepresentationAuthority) -> dict[str, object]:
    """Model only Mongo's known tuple-to-array representation change."""
    payload = value.to_dict()
    for field in ("mandate_capabilities", "representation_scope_capabilities"):
        if isinstance(payload[field], tuple):
            payload[field] = list(cast(tuple[object, ...], payload[field]))
    return payload


def test_real_index_metadata_is_exact_and_idempotent(mongo_context: MongoContext) -> None:
    """Physical unique and history indexes match the P7 contract."""
    entries = {
        item["name"]: item
        for item in mongo_context.collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(entries) == {
        registry.AUTHORITY_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }
    assert dict(entries[registry.AUTHORITY_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1, "authority_id": 1
    }
    assert dict(entries[registry.FINGERPRINT_INDEX_NAME]["key"]) == {
        "tenant_id": 1, "fingerprint": 1
    }
    assert dict(entries[registry.IDEMPOTENCY_INDEX_NAME]["key"]) == {
        "tenant_id": 1, "idempotency_key": 1
    }
    assert dict(entries[registry.HISTORY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "case_matter_id": 1,
        "matter_fingerprint": 1,
        "client_party_id": 1,
        "subject_identity_fingerprint": 1,
        "representative_principal_id": 1,
        "effective_from": 1,
        "occurred_at": 1,
        "fingerprint": 1,
        "authority_id": 1,
    }
    assert entries[registry.AUTHORITY_ID_INDEX_NAME].get("unique") is True
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


def test_real_transaction_contract_and_session_propagation(mongo_context: MongoContext) -> None:
    """Missing/inactive transactions fail and active caller sessions work."""
    value = _authority()
    with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError):
        registry.persist_representation_authority(value, mongo_context.collection, session=None)
    with mongo_context.client.start_session() as inactive:
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryTransactionRequiredError):
            registry.persist_representation_authority(value, mongo_context.collection, session=inactive)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.persist_representation_authority(value, mongo_context.collection, session=session) == value
        assert session.in_transaction
        session.commit_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_commit_durability_and_exact_canonical_bson(mongo_context: MongoContext) -> None:
    """Commit preserves semantic BSON while registry hydration restores the domain."""
    value = _authority()
    assert _commit(mongo_context, value) == value
    row = mongo_context.collection.find_one({"tenant_id": value.tenant_id, "authority_id": value.authority_id})
    assert row is not None
    row.pop("_id", None)
    expected = _expected_bson_payload(value)
    assert set(row) == set(REPRESENTATION_AUTHORITY_FIELDS)
    assert set(row) == set(expected)
    variant_fields = {"mandate_capabilities", "representation_scope_capabilities"}
    for field in set(expected) - variant_fields:
        assert row[field] == expected[field]
    assert row["mandate_capabilities"] == list(value.mandate_capabilities)
    assert row["representation_scope_capabilities"] == list(value.representation_scope_capabilities)
    assert row == expected
    assert _read(mongo_context, value.tenant_id, value.authority_id) == value
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_abort_rolls_back_without_registry_override(mongo_context: MongoContext) -> None:
    """Caller abort removes the uncommitted authority completely."""
    value = _authority()
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        registry.persist_representation_authority(value, mongo_context.collection, session=session)
        assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 0


def test_real_exact_replay_is_one_row(mongo_context: MongoContext) -> None:
    """Exact replay returns the historic row without inserting a duplicate."""
    value = _authority()
    assert _commit(mongo_context, value) == value
    assert _commit(mongo_context, value) == value
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_divergent_identities_fail_closed(mongo_context: MongoContext) -> None:
    """Idempotency, authority ID and fingerprint collisions cannot diverge."""
    value = _authority()
    _commit(mongo_context, value)
    candidates = (
        _authority(offset=1, authority_id="authority-divergent-id", idempotency_key=value.idempotency_key),
        _authority(offset=1, authority_id=value.authority_id, idempotency_key="authority-divergent-key"),
    )
    for candidate in candidates:
        with mongo_context.client.start_session() as session:
            session.start_transaction()
            with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryConflictError):
                registry.persist_representation_authority(candidate, mongo_context.collection, session=session)
            session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_fingerprint_corruption_fails_closed(mongo_context: MongoContext) -> None:
    """A matching fingerprint with divergent BSON is rejected by strict hydration."""
    value = _authority()
    _commit(mongo_context, value)
    changed = mongo_context.collection.update_one(
        {"tenant_id": value.tenant_id, "authority_id": value.authority_id},
        {"$set": {"decision": "DECLINED"}},
    )
    assert changed.modified_count == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError):
            registry.get_representation_authority(value.tenant_id, value.authority_id, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_duplicate_key_race_has_one_canonical_truth(mongo_context: MongoContext) -> None:
    """Concurrent exact contenders yield one durable row or a safe retry."""
    value = _authority()
    barrier = Barrier(2)

    def contender() -> str:
        try:
            with mongo_context.client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=10)
                result = registry.persist_representation_authority(value, mongo_context.collection, session=session)
                session.commit_transaction()
                assert result == value
                return "success"
        except (
            registry.LegalClientMatterRepresentationAuthorityRegistryRetryRequiredError,
            PyMongoError,
        ):
            return "retry"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: contender(), range(2)))
    assert "success" in outcomes
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_tenant_identity_fingerprint_and_idempotency_reads_are_isolated(mongo_context: MongoContext) -> None:
    """Shared opaque identities remain tenant scoped across all replay reads."""
    tenant_a = _authority(tenant="tenant-real-a")
    tenant_b = _authority(tenant="tenant-real-b")
    _commit(mongo_context, tenant_a)
    _commit(mongo_context, tenant_b)
    assert _read(mongo_context, tenant_a.tenant_id, tenant_a.authority_id) == tenant_a
    assert _read(mongo_context, tenant_b.tenant_id, tenant_b.authority_id) == tenant_b
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.get_representation_authority_by_fingerprint(tenant_b.tenant_id, tenant_b.fingerprint, mongo_context.collection, session=session) == tenant_b
        assert registry.get_representation_authority_by_idempotency_key(tenant_a.tenant_id, tenant_a.idempotency_key, mongo_context.collection, session=session) == tenant_a
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryNotFoundError):
            registry.get_representation_authority("tenant-missing", tenant_a.authority_id, mongo_context.collection, session=session)
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryNotFoundError):
            registry.get_representation_authority_by_fingerprint("tenant-missing", tenant_a.fingerprint, mongo_context.collection, session=session)
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryNotFoundError):
            registry.get_representation_authority_by_idempotency_key("tenant-missing", tenant_a.idempotency_key, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_multiple_rows_history_order_and_exact_filter(mongo_context: MongoContext) -> None:
    """Multiple immutable rows coexist and history order is deterministic."""
    earlier = _authority(offset=1)
    later = _authority(offset=2)
    neighbor_matter = _authority(matter_id="neighbor-matter", offset=3)
    neighbor_party = _authority(party_id="neighbor-party", offset=4)
    neighbor_subject = _authority(subject_fingerprint=HEX_C, offset=5)
    neighbor_principal = _authority(representative_principal="neighbor-principal", offset=6)
    for value in (later, neighbor_matter, neighbor_party, neighbor_subject, neighbor_principal, earlier):
        _commit(mongo_context, value)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        history = registry.list_representation_authorities_for_context(
            earlier.tenant_id,
            earlier.case_matter_id,
            earlier.matter_fingerprint,
            earlier.client_party_id,
            earlier.subject_identity_fingerprint,
            earlier.representative_principal_id,
            mongo_context.collection,
            session=session,
        )
        empty = registry.list_representation_authorities_for_context(
            earlier.tenant_id, "missing-matter", earlier.matter_fingerprint,
            earlier.client_party_id, earlier.subject_identity_fingerprint,
            earlier.representative_principal_id, mongo_context.collection,
            session=session,
        )
        session.abort_transaction()
    assert history == (earlier, later)
    assert empty == ()
    assert len(history) == 2
    assert [item.effective_from for item in history] == sorted(item.effective_from for item in history)
    assert all(item.tenant_id == earlier.tenant_id for item in history)


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("schema", "CORRUPT"),
        ("decision", "DECLINED"),
        ("representative_principal_id", "other-principal"),
        ("mandate_capabilities", ["NEGOTIATION"]),
        ("authorization_evidence_fingerprint", HEX_E),
    ],
)
def test_real_strict_hydration_rejects_corrupt_fields(
    mongo_context: MongoContext, field: str, bad_value: object
) -> None:
    """Corrupt schema, decision, principal, scope or evidence fails closed."""
    value = _authority()
    _commit(mongo_context, value)
    changed = mongo_context.collection.update_one(
        {"tenant_id": value.tenant_id, "authority_id": value.authority_id},
        {"$set": {field: bad_value}},
    )
    assert changed.modified_count == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationAuthorityRegistryPersistedRecordInvalidError):
            registry.get_representation_authority(value.tenant_id, value.authority_id, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_registry_static_authority_surface_is_narrow() -> None:
    """The registry source contains no downstream IAM/currentness authority."""
    source = Path(
        "tools/eos/legal_operations/registry/legal_client_matter_representation_authority_registry.py"
    ).read_text()
    assert "principal_status" not in source
    assert "tenant_authorization" not in source
    assert "currentness" in source.lower()
    assert "lifecycle" in source.lower()
    assert "firm decision" in source.lower()
    assert "LegalClientMatterRepresentationAuthority(" not in source
    assert "Court" in source
    assert "finance" in source.lower()


# ARTIFACT: test_legal_client_matter_representation_authority_registry_real_mongo.py
# VERSION: v1.0.0-L9C11-P8-CLIENT-REPRESENTATION-AUTHORITY-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P7 registry runtime evidence only
# TENANT POSTURE: UUID-isolated exact-tenant evidence; canonical wilsy excluded
# FAIL-CLOSED POSTURE: topology, transaction, durability, corruption, isolation and race failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
