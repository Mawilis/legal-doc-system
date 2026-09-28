"""Real-Mongo certificate for the L9C11-P24 final Representation registry.

TITLE: WILSY OS Legal Client Matter Final Representation Registry Real-Mongo Certificate
VERSION: v1.0.0-L9C11-P24R-FINAL-REPRESENTATION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published immutable P24 registry against one writable,
         UUID-isolated sanctioned Mongo replica-set database: topology,
         physical indexes, caller-owned transactions, BSON normalization,
         exact replay/collision behavior, strict corruption rejection,
         tenant/lineage isolation, deterministic history and rollback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_final_representation_registry_real_mongo.py
COLLABORATION / OWNERSHIP: P24 domain owns immutable final Representation truth;
                            P24 registry owns only persistence and exact reads;
                            this certificate owns disposable runtime evidence.
                            Formation, currentness, IAM, Court, HTTP/UI/Node
                            and finance remain separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C11-P24R certifies sanctioned topology, isolated database
           naming, exact indexes, transaction ownership, durable BSON truth,
           replay/collision guards, strict hydration, rollback, history and
           cross-tenant/lineage isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Fixtures contain opaque synthetic identifiers only;
                             URI credentials and bearer material are not logged.
TENANT BOUNDARY: Every exact read and history query remains tenant and lineage
                 scoped; canonical database ``wilsy`` is never selected.
AUTHORITY BOUNDARY: Disposable P24 persistence evidence only. No IAM, current
                    pointer, Court, financial, HTTP/UI/Node or formation truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: The certificate owns sessions and commit/abort lifecycle;
                      the registry must not start, commit or abort a transaction.
FAIL-CLOSED DECLARATION: Topology, index drift, corruption, leakage, collision,
                         rollback and durability failures fail certification.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Iterator, cast
import uuid

import pymongo
import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_client_matter_engagement import LegalClientMatterEngagement
from tools.eos.legal_operations.domain.legal_client_matter_engagement_currentness import project_legal_client_matter_engagement_currentness
from tools.eos.legal_operations.domain.legal_client_matter_mandate import LegalClientMatterMandate
from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import (
    LegalClientMatterMandateCurrentness,
    LegalClientMatterMandateCurrentnessReason,
    LegalClientMatterMandateCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority import LegalClientMatterRepresentationAuthority
from tools.eos.legal_operations.domain.legal_client_matter_representation_authority_currentness import project_legal_client_matter_representation_authority_currentness
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision import LegalClientMatterRepresentationFirmDecision
from tools.eos.legal_operations.domain.legal_client_matter_representation_firm_decision_currentness import project_legal_client_matter_representation_firm_decision_currentness
from tools.eos.legal_operations.domain.legal_client_matter_final_representation import FINAL_REPRESENTATION_FIELDS, LegalClientMatterFinalRepresentation
from tools.eos.legal_operations.registry import legal_client_matter_final_representation_registry as registry


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128


class MongoContext:
    """Disposable handles for one UUID-isolated P24 database."""

    def __init__(self, client: MongoClient[Any], database: Any, collection: Any) -> None:
        self.client = client
        self.database = database
        self.collection = collection


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield one writable sanctioned database and always remove it."""
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
        database_name = f"wilsy_l9c11_p24r_{uuid.uuid4().hex}"
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


def _fixture(
    *,
    tenant: str = "tenant-p24-real",
    matter_id: str = "matter-p24-real",
    matter_fingerprint: str = HEX_A,
    client_party_id: str = "party-p24-real",
    subject_fingerprint: str = HEX_B,
    representative_principal: str = "principal-representative-p24",
    authority_id: str = "authority-p24-real",
    decision_variant: str = "base",
    final_offset: int = 6,
    source_reference: str = "evidence:final-p24-real",
    idempotency_key: str = "idempotency:final-p24-real",
) -> LegalClientMatterFinalRepresentation:
    """Construct one valid P24 value through published domain constructors."""
    token = matter_id.replace("-", "_")
    mandate = LegalClientMatterMandate(
        mandate_id=f"mandate-{token}", tenant_id=tenant, case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint, client_party_id=client_party_id,
        subject_identity_fingerprint=subject_fingerprint, grant_actor_principal_id=f"principal-client-{token}",
        acting_capacity_id=f"capacity-{token}", acting_capacity_fingerprint=HEX_C, breadth="LIMITED",
        scope_reference=f"scope:{token}", scope_fingerprint=HEX_D, capabilities=["ADVISORY", "NEGOTIATION"],
        source_evidence_reference=f"evidence:mandate-{token}", source_evidence_fingerprint=HEX_A,
        client_grant_reference=f"grant-{token}", client_grant_fingerprint=HEX_B,
        firm_acknowledgment_reference=f"ack-{token}", firm_acknowledgment_fingerprint=HEX_E,
        occurred_at=BASE + timedelta(minutes=1), effective_from=BASE + timedelta(minutes=2),
        effective_until=None, idempotency_key=f"idempotency:mandate-{token}",
    )
    engagement = LegalClientMatterEngagement(
        engagement_id=f"engagement-{token}", tenant_id=tenant, case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint, client_party_id=client_party_id,
        subject_reference=f"client:subject-{token}", subject_identity_fingerprint=subject_fingerprint,
        acting_capacity_id=mandate.acting_capacity_id, acting_capacity_fingerprint=mandate.acting_capacity_fingerprint,
        client_acceptance_id=f"acceptance-{token}", client_acceptance_fingerprint=HEX_A,
        instrument_id=f"instrument-{token}", version="v1", instrument_fingerprint=HEX_B,
        content_fingerprint=HEX_C, mandate_id=mandate.mandate_id, mandate_scope=mandate.scope_reference,
        mandate_fingerprint=mandate.fingerprint, conflict_disposition_id=f"conflict-{token}",
        conflict_disposition_fingerprint=HEX_D, firm_decision_id=f"engagement-decision-{token}",
        decision_actor_principal_id=f"principal-firm-{token}", firm_decision_fingerprint=HEX_E,
        authorization_evidence_reference=f"evidence:engagement-auth-{token}", authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference=f"evidence:engagement-{token}", source_evidence_fingerprint=HEX_B,
        effective_from=BASE + timedelta(minutes=3), idempotency_key=f"idempotency:engagement-{token}",
    )
    authority = LegalClientMatterRepresentationAuthority(
        authority_id=authority_id, tenant_id=tenant, case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint, client_party_id=client_party_id,
        subject_reference=engagement.subject_reference, subject_identity_fingerprint=subject_fingerprint,
        engagement_id=engagement.engagement_id, engagement_fingerprint=engagement.fingerprint,
        mandate_id=mandate.mandate_id, mandate_fingerprint=mandate.fingerprint,
        mandate_scope_reference=mandate.scope_reference, mandate_scope_fingerprint=mandate.scope_fingerprint,
        mandate_capabilities=mandate.capabilities, acting_capacity_id=mandate.acting_capacity_id,
        acting_capacity_fingerprint=mandate.acting_capacity_fingerprint, representative_principal_id=representative_principal,
        representative_role="LEGAL_ATTORNEY", representation_scope_capabilities=("ADVISORY",), decision="APPOINTED",
        appointing_principal_id=f"principal-client-{token}", source_evidence_reference=f"evidence:authority-{token}",
        source_evidence_fingerprint=HEX_C, authorization_evidence_reference=f"evidence:authority-auth-{token}",
        authorization_evidence_fingerprint=HEX_D, occurred_at=BASE + timedelta(minutes=4),
        effective_from=BASE + timedelta(minutes=4), effective_until=None, idempotency_key=f"idempotency:authority-{token}",
    )
    decision = LegalClientMatterRepresentationFirmDecision.from_client_authority(
        client_authority=authority, decision="ACCEPTED", decision_actor_principal_id=f"principal-firm-{token}",
        authorization_evidence_reference=f"evidence:decision-auth-{token}", authorization_evidence_fingerprint=HEX_A,
        source_evidence_reference=f"evidence:decision-{token}-{decision_variant}", source_evidence_fingerprint=HEX_B,
        occurred_at=BASE + timedelta(minutes=5), effective_from=BASE + timedelta(minutes=5),
        idempotency_key=f"idempotency:decision-{token}-{decision_variant}",
    )
    evaluated_at = BASE + timedelta(days=1)
    authority_currentness = project_legal_client_matter_representation_authority_currentness(
        tenant_id=authority.tenant_id, case_matter_id=authority.case_matter_id, matter_fingerprint=authority.matter_fingerprint,
        client_party_id=authority.client_party_id, subject_identity_fingerprint=authority.subject_identity_fingerprint,
        representative_principal_id=authority.representative_principal_id, evaluated_at=evaluated_at, authorities=(authority,),
    )
    decision_currentness = project_legal_client_matter_representation_firm_decision_currentness(
        tenant_id=decision.tenant_id, case_matter_id=decision.case_matter_id, matter_fingerprint=decision.matter_fingerprint,
        client_party_id=decision.client_party_id, subject_identity_fingerprint=decision.subject_identity_fingerprint,
        representation_authority_id=authority.authority_id, representation_authority_fingerprint=authority.fingerprint,
        representative_principal_id=authority.representative_principal_id, representative_role=authority.representative_role,
        evaluated_at=evaluated_at, decisions=(decision,),
    )
    engagement_currentness = project_legal_client_matter_engagement_currentness(
        tenant_id=engagement.tenant_id, case_matter_id=engagement.case_matter_id, matter_fingerprint=engagement.matter_fingerprint,
        client_party_id=engagement.client_party_id, subject_identity_fingerprint=engagement.subject_identity_fingerprint,
        evaluated_at=evaluated_at, engagements=(engagement,),
    )
    mandate_currentness = LegalClientMatterMandateCurrentness(
        currentness_id=f"mandate-currentness-{token}", tenant_id=tenant, mandate_id=mandate.mandate_id,
        mandate_fingerprint=mandate.fingerprint, case_matter_id=matter_id, matter_fingerprint=matter_fingerprint,
        client_party_id=client_party_id, subject_identity_fingerprint=subject_fingerprint,
        client_grant_id=mandate.client_grant_reference, client_grant_fingerprint=mandate.client_grant_fingerprint,
        firm_acknowledgment_id=mandate.firm_acknowledgment_reference, firm_acknowledgment_fingerprint=mandate.firm_acknowledgment_fingerprint,
        effective_from=mandate.effective_from, effective_until=None, evaluation_time=evaluated_at,
        grant_currentness_state="CURRENT", grant_currentness_fingerprint=HEX_A, grant_currentness_tenant_id=tenant,
        grant_currentness_client_grant_id=mandate.client_grant_reference, grant_currentness_client_grant_fingerprint=mandate.client_grant_fingerprint,
        grant_currentness_case_matter_id=matter_id, grant_currentness_matter_fingerprint=matter_fingerprint,
        grant_currentness_client_party_id=client_party_id, grant_currentness_subject_identity_fingerprint=subject_fingerprint,
        acknowledgment_currentness_state="ACKNOWLEDGED", acknowledgment_currentness_fingerprint=HEX_B,
        acknowledgment_currentness_tenant_id=tenant, acknowledgment_currentness_client_grant_id=mandate.client_grant_reference,
        acknowledgment_currentness_client_grant_fingerprint=mandate.client_grant_fingerprint, acknowledgment_currentness_case_matter_id=matter_id,
        acknowledgment_currentness_matter_fingerprint=matter_fingerprint, acknowledgment_currentness_client_party_id=client_party_id,
        acknowledgment_currentness_subject_identity_fingerprint=subject_fingerprint,
        decisive_acknowledgment_ids=(mandate.firm_acknowledgment_reference,), decisive_acknowledgment_fingerprints=(mandate.firm_acknowledgment_fingerprint,),
        corruption_evidence_fingerprints=(), state=LegalClientMatterMandateCurrentnessState.CURRENT,
        reason=LegalClientMatterMandateCurrentnessReason.CURRENT,
    )
    return LegalClientMatterFinalRepresentation.from_canonical(
        authority=authority, authority_currentness=authority_currentness, firm_decision=decision,
        firm_decision_currentness=decision_currentness, engagement=engagement, engagement_currentness=engagement_currentness,
        mandate=mandate, mandate_currentness=mandate_currentness, representation_scope_capabilities=("ADVISORY",),
        representative_eligibility_reference=f"evidence:eligibility-{token}", representative_eligibility_fingerprint=HEX_C,
        source_evidence_reference=source_reference, source_evidence_fingerprint=HEX_D,
        effective_from=BASE + timedelta(minutes=final_offset), occurred_at=BASE + timedelta(minutes=final_offset + 1),
        idempotency_key=idempotency_key,
    )


def _commit(context: MongoContext, value: LegalClientMatterFinalRepresentation) -> LegalClientMatterFinalRepresentation:
    """Persist and commit using caller-owned lifecycle."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.persist_final_representation(value, context.collection, session=session)
        session.commit_transaction()
        return result


def _read(context: MongoContext, value: LegalClientMatterFinalRepresentation) -> LegalClientMatterFinalRepresentation:
    """Read by ID in a fresh caller-owned transaction."""
    with context.client.start_session() as session:
        session.start_transaction()
        result = registry.get_final_representation(value.tenant_id, value.representation_id, context.collection, session=session)
        session.commit_transaction()
        return result


def _history(context: MongoContext, value: LegalClientMatterFinalRepresentation, *, session: Any, limit: int = registry.MAX_HISTORY_READS) -> tuple[LegalClientMatterFinalRepresentation, ...]:
    """Read exact P24 history dimensions in the published API order."""
    return registry.list_final_representations_for_context(
        value.tenant_id, value.case_matter_id, value.matter_fingerprint, value.client_party_id,
        value.subject_identity_fingerprint, value.representative_principal_id,
        value.representation_authority_id, value.firm_representation_decision_id,
        context.collection, session=session, limit=limit,
    )


def test_real_topology_and_isolated_database(mongo_context: MongoContext) -> None:
    """The fixture is a writable expected replica-set disposable database."""
    assert mongo_context.database.name.startswith("wilsy_l9c11_p24r_")
    assert len(mongo_context.database.name) <= 63
    assert mongo_context.database.name != "wilsy"
    hello = mongo_context.client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert isinstance(mongo_context.client.server_info().get("version"), str)
    assert pymongo.version


def test_real_index_metadata_matches_p24_contract(mongo_context: MongoContext) -> None:
    """Physical indexes are exact, idempotent, non-TTL and non-currentness."""
    entries = {item["name"]: item for item in mongo_context.collection.list_indexes() if item["name"] != "_id_"}
    assert set(entries) == {
        registry.REPRESENTATION_ID_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME, registry.IDEMPOTENCY_INDEX_NAME,
        registry.MATTER_CLIENT_REPRESENTATIVE_HISTORY_INDEX_NAME, registry.MATTER_AUTHORITY_HISTORY_INDEX_NAME,
        registry.MATTER_DECISION_HISTORY_INDEX_NAME, registry.MATTER_EFFECTIVE_HISTORY_INDEX_NAME,
    }
    assert dict(entries[registry.REPRESENTATION_ID_INDEX_NAME]["key"]) == {"tenant_id": 1, "representation_id": 1}
    assert dict(entries[registry.FINGERPRINT_INDEX_NAME]["key"]) == {"tenant_id": 1, "fingerprint": 1}
    assert dict(entries[registry.IDEMPOTENCY_INDEX_NAME]["key"]) == {"tenant_id": 1, "idempotency_key": 1}
    assert dict(entries[registry.MATTER_CLIENT_REPRESENTATIVE_HISTORY_INDEX_NAME]["key"]) == {"tenant_id": 1, "case_matter_id": 1, "client_party_id": 1, "representative_principal_id": 1, "effective_from": 1}
    assert dict(entries[registry.MATTER_AUTHORITY_HISTORY_INDEX_NAME]["key"]) == {"tenant_id": 1, "case_matter_id": 1, "representation_authority_id": 1, "representation_authority_fingerprint": 1}
    assert dict(entries[registry.MATTER_DECISION_HISTORY_INDEX_NAME]["key"]) == {"tenant_id": 1, "case_matter_id": 1, "firm_representation_decision_id": 1, "firm_representation_decision_fingerprint": 1}
    assert dict(entries[registry.MATTER_EFFECTIVE_HISTORY_INDEX_NAME]["key"]) == {"tenant_id": 1, "case_matter_id": 1, "effective_from": 1}
    assert entries[registry.REPRESENTATION_ID_INDEX_NAME].get("unique") is True
    assert entries[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert entries[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert all(item.get("unique") is not True for name, item in entries.items() if name not in {registry.REPRESENTATION_ID_INDEX_NAME, registry.FINGERPRINT_INDEX_NAME, registry.IDEMPOTENCY_INDEX_NAME})
    assert all("expireAfterSeconds" not in item for item in entries.values())
    assert all("current" not in name.casefold() for name in entries)
    before = {name: dict(item["key"]) for name, item in entries.items()}
    registry.ensure_indexes(mongo_context.collection)
    after = {item["name"]: dict(item["key"]) for item in mongo_context.collection.list_indexes() if item["name"] != "_id_"}
    assert after == before


def test_real_transaction_contract_and_same_session_visibility(mongo_context: MongoContext) -> None:
    """Missing/inactive sessions reject; one active caller session is propagated."""
    value = _fixture()
    with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryTransactionRequiredError):
        registry.persist_final_representation(value, mongo_context.collection, session=None)
    with mongo_context.client.start_session() as inactive:
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryTransactionRequiredError):
            registry.persist_final_representation(value, mongo_context.collection, session=inactive)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.persist_final_representation(value, mongo_context.collection, session=session) == value
        assert registry.get_final_representation(value.tenant_id, value.representation_id, mongo_context.collection, session=session) == value
        assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        assert session.in_transaction is True
        session.commit_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_registry_does_not_own_transaction_lifecycle() -> None:
    """Static guard prevents transaction ownership from entering the registry."""
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_final_representation_registry.py").read_text()
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source


def test_real_commit_durability_and_bson_tuple_normalization(mongo_context: MongoContext) -> None:
    """Commit stores arrays and fresh hydration restores the canonical tuple."""
    value = _fixture()
    assert _commit(mongo_context, value) == value
    row = mongo_context.collection.find_one({"tenant_id": value.tenant_id, "representation_id": value.representation_id})
    assert row is not None
    row.pop("_id", None)
    expected = value.to_dict()
    expected["representation_scope_capabilities"] = list(cast(tuple[str, ...], expected["representation_scope_capabilities"]))
    assert set(row) == set(FINAL_REPRESENTATION_FIELDS)
    assert row == expected
    assert isinstance(row["representation_scope_capabilities"], list)
    assert _read(mongo_context, value) == value
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_abort_rolls_back(mongo_context: MongoContext) -> None:
    """Caller abort removes the uncommitted final Representation completely."""
    value = _fixture()
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        registry.persist_final_representation(value, mongo_context.collection, session=session)
        assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 0


def test_real_exact_replay_is_one_row(mongo_context: MongoContext) -> None:
    """Exact replay returns canonical truth without a duplicate durable row."""
    value = _fixture()
    assert _commit(mongo_context, value) == value
    assert _commit(mongo_context, value) == value
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


@pytest.mark.parametrize("identity", ["representation_id", "fingerprint", "idempotency_key"])
def test_real_divergent_identity_collisions_fail_closed(mongo_context: MongoContext, identity: str) -> None:
    """Each published replay identity rejects divergent canonical truth."""
    value = _fixture()
    _commit(mongo_context, value)
    divergent = _fixture(source_reference=f"evidence:divergent-{identity}", idempotency_key=f"idempotency:divergent-{identity}")
    object.__setattr__(divergent, identity, getattr(value, identity))
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryConflictError):
            registry.persist_final_representation(divergent, mongo_context.collection, session=session)
        session.abort_transaction()
    assert mongo_context.collection.count_documents({"tenant_id": value.tenant_id}) == 1


@pytest.mark.parametrize(
    "identity,alternate",
    [("representation_id", "representation_id"), ("fingerprint", "fingerprint"), ("idempotency_key", "idempotency_key")],
)
def test_real_database_unique_indexes_enforce_replay_identity(mongo_context: MongoContext, identity: str, alternate: str) -> None:
    """Raw bounded inserts prove each unique index rejects duplicates."""
    value = _fixture()
    _commit(mongo_context, value)
    raw = value.to_dict()
    raw[identity] = getattr(value, identity)
    raw["representation_id"] = raw["representation_id"] if identity == "representation_id" else f"raw-{identity}-id"
    raw["fingerprint"] = raw["fingerprint"] if identity == "fingerprint" else (HEX_E if identity != "fingerprint" else raw["fingerprint"])
    raw["idempotency_key"] = raw["idempotency_key"] if identity == "idempotency_key" else f"raw-{identity}-key"
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(DuplicateKeyError):
            mongo_context.collection.insert_one(raw, session=session)
        session.abort_transaction()
    assert alternate == identity


def test_real_tenant_scoped_identity_fingerprint_and_idempotency_reads(mongo_context: MongoContext) -> None:
    """All exact lookup APIs are tenant scoped and fail closed cross-tenant."""
    tenant_a = _fixture(tenant="tenant-p24-a", matter_id="matter-p24-a", idempotency_key="idempotency:p24-a")
    tenant_b = _fixture(tenant="tenant-p24-b", matter_id="matter-p24-b", idempotency_key="idempotency:p24-b")
    _commit(mongo_context, tenant_a); _commit(mongo_context, tenant_b)
    assert _read(mongo_context, tenant_a) == tenant_a
    assert _read(mongo_context, tenant_b) == tenant_b
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert registry.get_final_representation_by_fingerprint(tenant_b.tenant_id, tenant_b.fingerprint, mongo_context.collection, session=session) == tenant_b
        assert registry.get_final_representation_by_idempotency_key(tenant_a.tenant_id, tenant_a.idempotency_key, mongo_context.collection, session=session) == tenant_a
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryNotFoundError):
            registry.get_final_representation("tenant-p24-missing", tenant_a.representation_id, mongo_context.collection, session=session)
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryNotFoundError):
            registry.get_final_representation_by_fingerprint("tenant-p24-missing", tenant_a.fingerprint, mongo_context.collection, session=session)
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryNotFoundError):
            registry.get_final_representation_by_idempotency_key("tenant-p24-missing", tenant_a.idempotency_key, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_exact_history_order_and_limit(mongo_context: MongoContext) -> None:
    """History is bounded, append-only and sorted by effective/occurred/fingerprint/ID."""
    values = tuple(_fixture(final_offset=offset, source_reference=f"evidence:history-{offset}", idempotency_key=f"idempotency:history-{offset}") for offset in (8, 6, 7))
    for value in values:
        _commit(mongo_context, value)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        history = _history(mongo_context, values[0], session=session)
        assert [item.effective_from for item in history] == sorted(item.effective_from for item in history)
        assert history == tuple(sorted(values, key=lambda item: (item.effective_from, item.occurred_at, item.fingerprint, item.representation_id)))
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError):
            _history(mongo_context, values[0], session=session, limit=2)
        assert _history(mongo_context, values[0], session=session, limit=3) == history
        session.abort_transaction()


def test_real_representative_p1_p2_matter_client_and_subject_isolation(mongo_context: MongoContext) -> None:
    """Exact history excludes every neighboring lineage dimension."""
    base = _fixture()
    neighbors = (
        _fixture(
            representative_principal="principal-p24-neighbor",
            authority_id="authority-p24-neighbor",
            idempotency_key="idempotency:p24-neighbor-representative",
        ),
        _fixture(
            authority_id="authority-p24-neighbor-p1",
            idempotency_key="idempotency:p24-neighbor-p1",
        ),
        _fixture(decision_variant="neighbor-p2", source_reference="evidence:neighbor-p2", idempotency_key="idempotency:neighbor-p2"),
        _fixture(
            matter_id="matter-p24-neighbor",
            matter_fingerprint=HEX_C,
            client_party_id="party-p24-neighbor",
            subject_fingerprint=HEX_D,
            authority_id="authority-p24-neighbor-context",
            idempotency_key="idempotency:p24-neighbor-matter-client-subject",
        ),
    )
    _commit(mongo_context, base)
    for neighbor in neighbors:
        _commit(mongo_context, neighbor)
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        assert _history(mongo_context, base, session=session) == (base,)
        assert _history(mongo_context, neighbors[0], session=session) == (neighbors[0],)
        session.abort_transaction()


@pytest.mark.parametrize(
    "field,bad_value",
    [("client_party_id", ""), ("representation_scope_capabilities", "ADVISORY"), ("fingerprint", "0" * 128)],
)
def test_real_strict_hydration_rejects_corrupt_required_fields(mongo_context: MongoContext, field: str, bad_value: object) -> None:
    """Malformed identity, wrong BSON shape and bad fingerprint fail closed."""
    value = _fixture()
    _commit(mongo_context, value)
    changed = mongo_context.collection.update_one({"tenant_id": value.tenant_id, "representation_id": value.representation_id}, {"$set": {field: bad_value}})
    assert changed.modified_count == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError):
            registry.get_final_representation(value.tenant_id, value.representation_id, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_strict_hydration_rejects_missing_required_field(mongo_context: MongoContext) -> None:
    """A missing durable field is not silently defaulted."""
    value = _fixture()
    _commit(mongo_context, value)
    changed = mongo_context.collection.update_one({"tenant_id": value.tenant_id, "representation_id": value.representation_id}, {"$unset": {"source_evidence_reference": ""}})
    assert changed.modified_count == 1
    with mongo_context.client.start_session() as session:
        session.start_transaction()
        with pytest.raises(registry.LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError):
            registry.get_final_representation(value.tenant_id, value.representation_id, mongo_context.collection, session=session)
        session.abort_transaction()


def test_real_append_only_and_zero_downstream_authority() -> None:
    """Registry exposes no mutation/currentness/downstream authority surface."""
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_final_representation_registry.py").read_text()
    assert "update_one" not in source and "replace_one" not in source and "delete_one" not in source
    assert "current_pointer" not in source.lower()
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source
    assert "currentness" in source.lower()
    assert "LegalClientMatterFinalRepresentationRegistry" in source


# ARTIFACT: test_legal_client_matter_final_representation_registry_real_mongo.py
# VERSION: v1.0.0-L9C11-P24R-FINAL-REPRESENTATION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable P24 registry runtime evidence only
# TENANT POSTURE: UUID-isolated database with exact tenant and lineage filters
# FAIL-CLOSED POSTURE: topology, transactions, BSON, corruption, collisions, isolation and rollback reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
