"""Real-Mongo certificate for the L9C11-P10 firm-decision registry.

TITLE: WILSY OS Legal Client Matter Representation Firm Decision Registry Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P10-FIRM-REPRESENTATION-DECISION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published P9 immutable registry against a writable,
         UUID-isolated Mongo replica set: topology, physical indexes,
         caller-owned transactions, BSON semantics, replay/collision behavior,
         tenant isolation, deterministic history and strict corruption failure.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_representation_firm_decision_registry_real_mongo.py
COLLABORATION / OWNERSHIP: P2 owns immutable firm-decision semantics; P9 owns
                            persistence; P10 owns only disposable real-Mongo
                            evidence. IAM, currentness, formation, Court and
                            finance remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P10 certifies topology, UUID database isolation,
           physical index identity, commit/rollback, BSON tuple/list round
           trips, exact replay/collision classification, tenant-bound history,
           duplicate-key races and strict corruption rejection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: URI credentials and bearer material are never
                             printed; fixtures use opaque synthetic values.
TENANT BOUNDARY: Every registry read and history filter is exact tenant and
                 exact lineage scoped; canonical database ``wilsy`` is barred.
AUTHORITY BOUNDARY: Disposable immutable decision-registry evidence only.
                    This certificate performs no IAM, currentness, lifecycle,
                    Representation formation, Court, HTTP/UI/Node or finance.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
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

from tools.eos.legal_operations.domain.legal_client_acting_capacity import (
    LegalClientActingCapacity,
)
from tools.eos.legal_operations.domain.legal_client_matter_engagement import (
    LegalClientMatterEngagement,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate import (
    LegalClientMatterMandate,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import (
    LegalClientMatterRepresentationAuthority,
    LegalClientMatterRepresentationAuthorityDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import (
    REPRESENTATION_FIRM_DECISION_FIELDS,
    LegalClientMatterRepresentationFirmDecision,
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
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
VARIANT_FIELDS = {
    "client_authority_scope_capabilities",
    "mandate_capabilities",
    "representation_scope_capabilities",
}


class MongoContext:
    """Disposable runtime handles for one UUID-isolated database."""

    def __init__(self, client: MongoClient[Any], database: Any, collection: Any) -> None:
        self.client = client
        self.database = database
        self.collection = collection


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield a writable sanctioned replica-set database and always clean it."""
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
        database_name = f"wilsy_l9c11_repfdec_{uuid.uuid4().hex}"
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


def _authority(
    *,
    tenant: str = "tenant-real-p10",
    matter_id: str = "matter-real-p10",
    matter_fingerprint: str = HEX_A,
    party_id: str = "party-real-p10",
    subject_fingerprint: str = HEX_B,
    representative_principal: str = "principal-representative-p10",
    offset: int = 0,
    authority_id: str | None = None,
    idempotency_key: str | None = None,
) -> LegalClientMatterRepresentationAuthority:
    """Construct valid upstream immutable values through published factories."""
    occurred = BASE + timedelta(minutes=offset)
    capacity = LegalClientActingCapacity(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        capacity_id="capacity-real-p10",
        principal_id=representative_principal,
        party_id=party_id,
        subject_reference="client:subject-real-p10",
        subject_identity_fingerprint=subject_fingerprint,
        capacity_type="REPRESENTATIVE",
        effective_from=occurred,
        effective_until=occurred + timedelta(days=90),
        source_evidence_reference="capacity-source:p10",
        source_evidence_fingerprint=HEX_A,
    )
    mandate = LegalClientMatterMandate(
        mandate_id="mandate-real-p10",
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_identity_fingerprint=subject_fingerprint,
        grant_actor_principal_id="principal-client-p10",
        acting_capacity_id=capacity.capacity_id,
        acting_capacity_fingerprint=capacity.fingerprint,
        breadth="LIMITED",
        scope_reference="scope:p10",
        scope_fingerprint=HEX_B,
        capabilities=["ADVISORY", "NEGOTIATION"],
        source_evidence_reference="mandate-source:p10",
        source_evidence_fingerprint=HEX_C,
        client_grant_reference="grant:p10",
        client_grant_fingerprint=HEX_D,
        firm_acknowledgment_reference="ack:p10",
        firm_acknowledgment_fingerprint=HEX_E,
        occurred_at=occurred,
        effective_from=occurred + timedelta(minutes=1),
        effective_until=occurred + timedelta(days=60),
        idempotency_key=f"mandate-idempotency:p10:{matter_id}:{offset}",
    )
    engagement = LegalClientMatterEngagement(
        engagement_id="engagement-real-p10",
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_reference="client:subject-real-p10",
        subject_identity_fingerprint=subject_fingerprint,
        acting_capacity_id=capacity.capacity_id,
        acting_capacity_fingerprint=capacity.fingerprint,
        client_acceptance_id="acceptance:p10",
        client_acceptance_fingerprint=HEX_A,
        instrument_id="instrument:p10",
        version="1",
        instrument_fingerprint=HEX_B,
        content_fingerprint=HEX_C,
        mandate_id=mandate.mandate_id,
        mandate_scope=mandate.scope_reference,
        mandate_fingerprint=mandate.fingerprint,
        conflict_disposition_id="conflict:p10",
        conflict_disposition_fingerprint=HEX_D,
        firm_decision_id="firm-decision:p10",
        decision_actor_principal_id="principal-firm:p10",
        firm_decision_fingerprint=HEX_E,
        authorization_evidence_reference="engagement-auth:p10",
        authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference="engagement-source:p10",
        source_evidence_fingerprint=HEX_B,
        effective_from=occurred + timedelta(minutes=2),
        idempotency_key=f"engagement-idempotency:p10:{matter_id}:{offset}",
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
        appointing_principal_id="principal-client-p10",
        source_evidence_reference="appointment-source:p10",
        source_evidence_fingerprint=HEX_C,
        authorization_evidence_reference="appointment-authorization:p10",
        authorization_evidence_fingerprint=HEX_D,
        occurred_at=occurred + timedelta(minutes=3),
        effective_from=occurred + timedelta(minutes=4),
        effective_until=occurred + timedelta(days=30),
        idempotency_key=idempotency_key or f"authority-idempotency:{matter_id}:{offset}",
    )


def _decision(
    *,
    authority: LegalClientMatterRepresentationAuthority | None = None,
    state: str = "ACCEPTED",
    offset: int = 0,
    idempotency_key: str | None = None,
) -> LegalClientMatterRepresentationFirmDecision:
    """Construct one P2 value using only its canonical client-authority factory."""
    authority = authority or _authority(offset=offset)
    occurred = BASE + timedelta(minutes=offset + 6)
    return LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority,
        decision=state,
        decision_actor_principal_id="principal-firm-p10",
        authorization_evidence_reference="firm-authorization:p10",
        authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference="firm-decision-source:p10",
        source_evidence_fingerprint=HEX_B,
        occurred_at=occurred,
        effective_from=occurred + timedelta(minutes=1),
        idempotency_key=idempotency_key or f"firm-decision-idempotency:p10:{offset}",
    )


def _commit(context: MongoContext, value: LegalClientMatterRepresentationFirmDecision) -> LegalClientMatterRepresentationFirmDecision:
    """Persist one decision under caller-owned transaction lifecycle."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.persist_firm_decision(value, context.collection, session=session)
        session.commit_transaction()
        return result


def _read(context: MongoContext, tenant: str, decision_id: str) -> LegalClientMatterRepresentationFirmDecision:
    """Read one decision in a fresh caller-owned transaction."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.get_firm_decision(tenant, decision_id, context.collection, session=session)
        session.commit_transaction()
        return result


def _history_args(value: LegalClientMatterRepresentationFirmDecision) -> tuple[str, ...]:
    """Return the exact P9 history dimensions in published order."""
    return (
        value.tenant_id,
        value.case_matter_id,
        value.matter_fingerprint,
        value.client_party_id,
        value.subject_identity_fingerprint,
        value.representation_authority_id,
        value.representation_authority_fingerprint,
        value.representative_principal_id,
    )


def _expected_bson_payload(value: LegalClientMatterRepresentationFirmDecision) -> dict[str, object]:
    """Model only Mongo's known tuple-to-array representation changes."""
    payload = value.to_dict()
    for field in VARIANT_FIELDS:
        if isinstance(payload[field], tuple):
            payload[field] = list(cast(tuple[object, ...], payload[field]))
    return payload


def test_real_index_metadata_is_exact_and_idempotent(mongo_context: MongoContext) -> None:
    """Physical unique and lineage indexes match the P9 contract."""
    entries = {
        item["name"]: item
        for item in mongo_context.collection.list_indexes()
        if item["name"] != "_id_"
    }
    assert set(entries) == {
        registry.DECISION_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }
    assert dict(entries[registry.DECISION_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "decision_id": 1,
    }
    assert dict(entries[registry.FINGERPRINT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }
    assert dict(entries[registry.IDEMPOTENCY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "idempotency_key": 1,
    }
    assert dict(entries[registry.HISTORY_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "case_matter_id": 1,
        "matter_fingerprint": 1,
        "client_party_id": 1,
        "subject_identity_fingerprint": 1,
        "representation_authority_id": 1,
        "representation_authority_fingerprint": 1,
        "representative_principal_id": 1,
        "effective_from": 1,
        "occurred_at": 1,
        "fingerprint": 1,
        "decision_id": 1,
    }
    assert entries[registry.DECISION_ID_INDEX_NAME].get("unique") is True
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
    value = _decision()
    with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError):
        registry.persist_firm_decision(value, mongo_context.collection, session=None)
    with mongo_context.client.start_session() as inactive:
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryTransactionRequiredError):
            registry.persist_firm_decision(value, mongo_context.collection, session=inactive)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.persist_firm_decision(value, mongo_context.collection, session=session) == value
        assert session.in_transaction
        session.commit_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_commit_durability_and_exact_canonical_bson(mongo_context: MongoContext) -> None:
    """Commit preserves semantic BSON while hydration restores P2 tuples."""
    value = _decision()
    assert _commit(mongo_context, value) == value
    row = mongo_context.collection.find_one(
        {"tenant_id": value.tenant_id, "decision_id": value.decision_id}
    )
    assert row is not None
    row.pop("_id", None)
    expected = _expected_bson_payload(value)
    assert set(row) == set(REPRESENTATION_FIRM_DECISION_FIELDS)
    assert set(row) == set(expected)
    for field in set(expected) - VARIANT_FIELDS:
        assert row[field] == expected[field]
    for field in VARIANT_FIELDS:
        assert row[field] == list(cast(tuple[object, ...], getattr(value, field)))
    assert row == expected
    assert _read(mongo_context, value.tenant_id, value.decision_id) == value
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_abort_rolls_back_without_registry_override(mongo_context: MongoContext) -> None:
    """Caller abort removes the uncommitted decision completely."""
    value = _decision()
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        registry.persist_firm_decision(value, mongo_context.collection, session=session)
        assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 0


def test_real_exact_replay_is_one_row(mongo_context: MongoContext) -> None:
    """Exact replay returns the historic decision without a duplicate."""
    value = _decision()
    assert _commit(mongo_context, value) == value
    assert _commit(mongo_context, value) == value
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_divergent_replay_identities_fail_closed(mongo_context: MongoContext) -> None:
    """Idempotency, decision-ID and fingerprint collisions cannot diverge."""
    value = _decision()
    _commit(mongo_context, value)
    idempotency = _decision(offset=1, idempotency_key=value.idempotency_key)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryConflictError):
            registry.persist_firm_decision(idempotency, mongo_context.collection, session=session)
        session.abort_transaction()
    decision_id = _decision(offset=2)
    object.__setattr__(decision_id, "decision_id", value.decision_id)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryConflictError):
            registry.persist_firm_decision(decision_id, mongo_context.collection, session=session)
        session.abort_transaction()
    fingerprint = _decision(offset=3)
    object.__setattr__(fingerprint, "fingerprint", value.fingerprint)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryConflictError):
            registry.persist_firm_decision(fingerprint, mongo_context.collection, session=session)
        session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_fingerprint_corruption_fails_closed(mongo_context: MongoContext) -> None:
    """A matching identity with divergent durable payload is rejected."""
    value = _decision()
    _commit(mongo_context, value)
    changed = mongo_context.collection.update_one(
        {"tenant_id": value.tenant_id, "decision_id": value.decision_id},
        {"$set": {"representation_authority_id": "tampered-authority"}},
    )
    assert changed.modified_count == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError):
            registry.get_firm_decision(value.tenant_id, value.decision_id, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_duplicate_key_race_has_one_canonical_truth(mongo_context: MongoContext) -> None:
    """Concurrent exact contenders yield one durable row or a safe retry."""
    value = _decision()
    barrier = Barrier(2)

    def contender() -> str:
        try:
            with mongo_context.client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=10)
                result = registry.persist_firm_decision(value, mongo_context.collection, session=session)
                session.commit_transaction()
                assert result == value
                return "success"
        except (
            registry.LegalClientMatterRepresentationFirmDecisionRegistryRetryRequiredError,
            PyMongoError,
        ):
            return "retry"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: contender(), range(2)))
    assert "success" in outcomes
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_tenant_identity_fingerprint_idempotency_reads_are_isolated(mongo_context: MongoContext) -> None:
    """Decision identities and replay reads remain tenant scoped."""
    tenant_a = _decision(authority=_authority(tenant="tenant-real-a", authority_id="shared-authority"))
    tenant_b = _decision(authority=_authority(tenant="tenant-real-b", authority_id="shared-authority"))
    _commit(mongo_context, tenant_a)
    _commit(mongo_context, tenant_b)
    assert _read(mongo_context, tenant_a.tenant_id, tenant_a.decision_id) == tenant_a
    assert _read(mongo_context, tenant_b.tenant_id, tenant_b.decision_id) == tenant_b
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.get_firm_decision_by_fingerprint(tenant_b.tenant_id, tenant_b.fingerprint, mongo_context.collection, session=session) == tenant_b
        assert registry.get_firm_decision_by_idempotency_key(tenant_a.tenant_id, tenant_a.idempotency_key, mongo_context.collection, session=session) == tenant_a
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError):
            registry.get_firm_decision("tenant-missing", tenant_a.decision_id, mongo_context.collection, session=session)
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError):
            registry.get_firm_decision_by_fingerprint("tenant-missing", tenant_a.fingerprint, mongo_context.collection, session=session)
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryNotFoundError):
            registry.get_firm_decision_by_idempotency_key("tenant-missing", tenant_a.idempotency_key, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_multiple_rows_history_order_and_exact_filter(mongo_context: MongoContext) -> None:
    """Multiple immutable decisions coexist and history order is deterministic."""
    shared_authority = _authority(
        authority_id="shared-history-authority",
        idempotency_key="shared-history-authority-key",
    )
    earlier = _decision(
        authority=shared_authority,
        offset=1,
        idempotency_key="shared-history-decision-earlier",
    )
    later = _decision(
        authority=shared_authority,
        offset=2,
        idempotency_key="shared-history-decision-later",
    )
    neighbor_matter = _decision(authority=_authority(matter_id="neighbor-matter", offset=3), offset=3)
    neighbor_matter_fp = _decision(authority=_authority(matter_fingerprint=HEX_C, offset=4), offset=4)
    neighbor_party = _decision(authority=_authority(party_id="neighbor-party", offset=5), offset=5)
    neighbor_subject = _decision(authority=_authority(subject_fingerprint=HEX_D, offset=6), offset=6)
    neighbor_authority = _decision(authority=_authority(authority_id="neighbor-authority", offset=7), offset=7)
    neighbor_authority_fp = _decision(authority=_authority(offset=8), offset=8)
    neighbor_principal = _decision(authority=_authority(representative_principal="neighbor-principal", offset=9), offset=9)
    for value in (later, neighbor_matter, neighbor_matter_fp, neighbor_party, neighbor_subject, neighbor_authority, neighbor_authority_fp, neighbor_principal, earlier):
        _commit(mongo_context, value)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        history = registry.list_firm_decisions_for_context(
            earlier.tenant_id,
            earlier.case_matter_id,
            earlier.matter_fingerprint,
            earlier.client_party_id,
            earlier.subject_identity_fingerprint,
            earlier.representation_authority_id,
            earlier.representation_authority_fingerprint,
            earlier.representative_principal_id,
            mongo_context.collection,
            session=session,
        )
        empty = registry.list_firm_decisions_for_context(
            "tenant-real-p10", "missing-matter", HEX_A, "party-real-p10", HEX_B,
            earlier.representation_authority_id,
            earlier.representation_authority_fingerprint,
            earlier.representative_principal_id,
            mongo_context.collection,
            session=session,
        )
        session.abort_transaction()
    assert history == (earlier, later)
    assert empty == ()
    assert len(history) == 2
    assert [item.effective_from for item in history] == sorted(item.effective_from for item in history)


def test_real_history_isolation_excludes_each_neighbor_dimension(mongo_context: MongoContext) -> None:
    """Exact history excludes tenant, lineage and client-authority neighbors."""
    value = _decision()
    _commit(mongo_context, value)
    neighbors = (
        _decision(authority=_authority(tenant="tenant-neighbor"), offset=1),
        _decision(authority=_authority(matter_id="matter-neighbor"), offset=2),
        _decision(authority=_authority(matter_fingerprint=HEX_C), offset=3),
        _decision(authority=_authority(party_id="party-neighbor"), offset=4),
        _decision(authority=_authority(subject_fingerprint=HEX_D), offset=5),
        _decision(authority=_authority(authority_id="authority-neighbor"), offset=6),
        _decision(authority=_authority(offset=7), offset=7),
        _decision(authority=_authority(representative_principal="principal-neighbor"), offset=8),
    )
    for neighbor in neighbors:
        _commit(mongo_context, neighbor)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.list_firm_decisions_for_context(
            value.tenant_id,
            value.case_matter_id,
            value.matter_fingerprint,
            value.client_party_id,
            value.subject_identity_fingerprint,
            value.representation_authority_id,
            value.representation_authority_fingerprint,
            value.representative_principal_id,
            mongo_context.collection,
            session=session,
        ) == (value,)
        session.abort_transaction()


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("schema", "CORRUPT"),
        ("decision_version", "CORRUPT"),
        ("decision", "CORRUPT"),
        ("representation_authority_id", "tampered-authority"),
        ("representation_authority_fingerprint", HEX_E),
        ("representative_principal_id", "tampered-principal"),
        ("mandate_capabilities", ["UNKNOWN"]),
        ("representation_scope_capabilities", "ADVISORY"),
        ("authorization_evidence_fingerprint", HEX_E),
        ("fingerprint", "0" * 128),
    ],
)
def test_real_strict_hydration_rejects_corrupt_fields(
    mongo_context: MongoContext, field: str, bad_value: object
) -> None:
    """Schema, identity, scope, evidence and fingerprint corruption fail closed."""
    value = _decision()
    _commit(mongo_context, value)
    changed = mongo_context.collection.update_one(
        {"tenant_id": value.tenant_id, "decision_id": value.decision_id},
        {"$set": {field: bad_value}},
    )
    assert changed.modified_count == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterRepresentationFirmDecisionRegistryPersistedRecordInvalidError):
            registry.get_firm_decision(value.tenant_id, value.decision_id, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_registry_static_authority_surface_is_narrow() -> None:
    """The registry source has no client-authority, IAM or downstream authority."""
    source = Path(
        "tools/eos/legal_operations/registry/"
        "legal_client_matter_representation_firm_decision_registry.py"
    ).read_text()
    assert "legal_client_matter_representation_authority_registry" not in source
    assert "principal_status" not in source
    assert "matter_assignment" not in source
    assert "currentness" in source.lower()
    assert "lifecycle" in source.lower()
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source
    assert "Court" in source
    assert "financial" in source.lower()


# ARTIFACT: test_legal_client_matter_representation_firm_decision_registry_real_mongo.py
# VERSION: v1.0.0-L9C11-P10-FIRM-REPRESENTATION-DECISION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P9 registry runtime evidence only
# TENANT POSTURE: UUID-isolated exact-tenant and exact-lineage evidence
# FAIL-CLOSED POSTURE: topology, transactions, BSON, corruption, isolation and races reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
