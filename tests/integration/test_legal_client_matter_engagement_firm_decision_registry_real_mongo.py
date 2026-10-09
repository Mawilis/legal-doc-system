"""Real-Mongo certificate for the L9C9-P1 firm-decision registry.

TITLE: WILSY OS Legal Engagement Firm Decision Registry Real-Mongo Certificate
VERSION: v1.0.0-L9C9-P2-ENGAGEMENT-FIRM-DECISION-REGISTRY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published immutable registry against a writable UUID-
         isolated Mongo replica set: physical indexes, caller-owned commit and
         rollback, replay/collision behavior, tenant isolation, bounded
         history, strict corruption rejection and duplicate-key races.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_engagement_firm_decision_registry_real_mongo.py
COLLABORATION / OWNERSHIP: L9C9-P1 owns registry behavior; this certificate
                            owns only disposable runtime evidence. Currentness,
                            Engagement, IAM, Representation, Court and finance
                            remain outside this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Every registry operation receives a real caller-owned
                      session and transaction; registry lifecycle is audited.
FAIL-CLOSED DECLARATION: Infrastructure unavailability is skipped explicitly
                         for operator execution and never represented as pass.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from threading import Barrier
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_client_matter_engagement_firm_decision import (
    LegalClientMatterEngagementFirmDecision,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_engagement_firm_decision_registry as registry,
)


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 27, 20, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128
FP_D = "d" * 128
FP_E = "e" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, Any]]:
    """Yield one UUID-isolated disposable collection after topology checks."""
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
            pytest.skip(
                f"real Mongo unavailable for operator runtime: {type(error).__name__}"
            )
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert isinstance(server_version, str) and server_version
        database_name = f"wilsy_l9c9_reg_{uuid.uuid4().hex}"
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


def _decision(
    *,
    tenant_id: str = "tenant-l9c9",
    decision_id: str = "decision-l9c9-1",
    idempotency_key: str = "idempotency-l9c9-1",
    state: str = "ACCEPTED",
    effective_offset: int = 0,
    matter_id: str = "matter-l9c9",
    matter_fingerprint: str = FP_A,
    party_id: str = "party-l9c9",
    subject_fingerprint: str = FP_B,
) -> LegalClientMatterEngagementFirmDecision:
    """Build synthetic valid immutable evidence without upstream reads."""
    occurred = NOW + timedelta(minutes=effective_offset)
    return LegalClientMatterEngagementFirmDecision(
        decision_id=decision_id,
        tenant_id=tenant_id,
        case_matter_id=matter_id,
        matter_fingerprint=matter_fingerprint,
        client_party_id=party_id,
        subject_reference="client:subject-l9c9",
        subject_identity_fingerprint=subject_fingerprint,
        decision=state,
        decision_actor_principal_id="principal-l9c9",
        authorization_evidence_reference="iam:l9c9:authorization",
        authorization_evidence_fingerprint=FP_C,
        source_evidence_reference="source:l9c9:evidence",
        source_evidence_fingerprint=FP_D,
        occurred_at=occurred,
        effective_from=occurred,
        idempotency_key=idempotency_key,
    )


def _commit(
    client: MongoClient[Any], collection: Any, value: LegalClientMatterEngagementFirmDecision
) -> LegalClientMatterEngagementFirmDecision:
    with client.start_session() as session:
        session.start_transaction()
        result = registry.persist_firm_decision(value, collection, session=session)
        session.commit_transaction()
        return result


def _read(
    client: MongoClient[Any], collection: Any, tenant_id: str, decision_id: str
) -> LegalClientMatterEngagementFirmDecision:
    with client.start_session() as session:
        with session.start_transaction():
            return registry.get_firm_decision(tenant_id, decision_id, collection, session=session)


def test_real_index_metadata_is_exact_and_idempotent(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Physical indexes are tenant-scoped, deterministic and non-expiring."""
    _, database, collection = mongo_context
    indexes = {
        entry["name"]: entry
        for entry in collection.list_indexes()
        if entry["name"] != "_id_"
    }
    assert database.name != "wilsy"
    assert set(indexes) == {
        registry.DECISION_ID_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.IDEMPOTENCY_INDEX_NAME,
        registry.HISTORY_INDEX_NAME,
    }
    assert dict(indexes[registry.DECISION_ID_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "decision_id": 1,
    }
    assert indexes[registry.DECISION_ID_INDEX_NAME].get("unique") is True
    assert dict(indexes[registry.FINGERPRINT_INDEX_NAME]["key"]) == {
        "tenant_id": 1,
        "fingerprint": 1,
    }
    assert indexes[registry.FINGERPRINT_INDEX_NAME].get("unique") is True
    assert indexes[registry.IDEMPOTENCY_INDEX_NAME].get("unique") is True
    assert indexes[registry.HISTORY_INDEX_NAME].get("unique") is not True
    assert all("expireAfterSeconds" not in entry for entry in indexes.values())


def test_real_transaction_is_required_and_registry_does_not_own_lifecycle(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Missing/inactive sessions fail before collection work."""
    client, _, collection = mongo_context
    value = _decision()
    with pytest.raises(registry.LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError):
        registry.persist_firm_decision(value, collection, session=None)
    with client.start_session() as session:
        with pytest.raises(registry.LegalClientMatterEngagementFirmDecisionRegistryTransactionRequiredError):
            registry.persist_firm_decision(value, collection, session=session)


def test_real_commit_durability_and_exact_payload(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """External commit makes one exact canonical row durable."""
    client, _, collection = mongo_context
    value = _decision()
    assert _commit(client, collection, value) == value
    assert _read(client, collection, value.tenant_id, value.decision_id) == value
    row = collection.find_one({"tenant_id": value.tenant_id, "decision_id": value.decision_id})
    assert row is not None
    row.pop("_id", None)
    assert row == value.to_dict()
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_abort_rolls_back_without_registry_override(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Caller abort leaves no durable row."""
    client, _, collection = mongo_context
    value = _decision()
    with client.start_session() as session:
        session.start_transaction()
        registry.persist_firm_decision(value, collection, session=session)
        assert collection.count_documents({"tenant_id": value.tenant_id}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 0


def test_real_exact_replay_is_one_row_and_idempotent(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Exact replay returns historic canonical evidence without insertion."""
    client, _, collection = mongo_context
    value = _decision()
    assert _commit(client, collection, value) == value
    assert _commit(client, collection, value) == value
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_divergent_idempotency_and_decision_id_are_blocked(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Divergent immutable identities fail closed without a second row."""
    client, _, collection = mongo_context
    value = _decision()
    _commit(client, collection, value)
    divergent_idempotency = _decision(
        decision_id="decision-l9c9-2",
        idempotency_key=value.idempotency_key,
        state="DECLINED",
    )
    divergent_id = _decision(
        idempotency_key="idempotency-l9c9-2",
        state="DECLINED",
    )
    for candidate in (divergent_idempotency, divergent_id):
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(registry.LegalClientMatterEngagementFirmDecisionRegistryConflictError):
                    registry.persist_firm_decision(candidate, collection, session=session)
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_real_tenant_identity_and_fingerprint_reads_are_isolated(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Identical opaque identities in different tenants never cross-read."""
    client, _, collection = mongo_context
    tenant_a = _decision(tenant_id="tenant-a", decision_id="shared", idempotency_key="shared-key")
    tenant_b = _decision(tenant_id="tenant-b", decision_id="shared", idempotency_key="shared-key")
    assert _commit(client, collection, tenant_a) == tenant_a
    assert _commit(client, collection, tenant_b) == tenant_b
    assert _read(client, collection, "tenant-a", "shared") == tenant_a
    assert _read(client, collection, "tenant-b", "shared") == tenant_b
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientMatterEngagementFirmDecisionRegistryNotFoundError):
                registry.get_firm_decision("tenant-a", "not-shared", collection, session=session)
            with pytest.raises(registry.LegalClientMatterEngagementFirmDecisionRegistryNotFoundError):
                registry.get_firm_decision_by_fingerprint("tenant-a", tenant_b.fingerprint, collection, session=session)


def test_real_fingerprint_corruption_fails_strict_hydration(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Corrupt BSON is rejected and never repaired in memory."""
    client, _, collection = mongo_context
    value = _decision()
    _commit(client, collection, value)
    assert collection.update_one(
        {"tenant_id": value.tenant_id, "decision_id": value.decision_id},
        {"$set": {"fingerprint": "0" * 128}},
    ).matched_count == 1
    with client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(registry.LegalClientMatterEngagementFirmDecisionRegistryPersistedRecordInvalidError):
                registry.get_firm_decision(value.tenant_id, value.decision_id, collection, session=session)


def test_real_history_filter_order_is_exact_and_empty_is_canonical(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """History returns every exact lineage row in deterministic chronology."""
    client, _, collection = mongo_context
    earlier = _decision(decision_id="earlier", idempotency_key="earlier-key", effective_offset=1)
    later = _decision(decision_id="later", idempotency_key="later-key", state="DECLINED", effective_offset=2)
    neighbor_matter = _decision(decision_id="neighbor-matter", idempotency_key="neighbor-matter-key", matter_id="other-matter")
    neighbor_party = _decision(decision_id="neighbor-party", idempotency_key="neighbor-party-key", party_id="other-party")
    for value in (later, earlier, neighbor_matter, neighbor_party):
        _commit(client, collection, value)
    with client.start_session() as session:
        with session.start_transaction():
            history = registry.list_firm_decisions_for_context(
                earlier.tenant_id,
                earlier.case_matter_id,
                earlier.matter_fingerprint,
                earlier.client_party_id,
                earlier.subject_identity_fingerprint,
                collection,
                session=session,
            )
            empty = registry.list_firm_decisions_for_context(
                earlier.tenant_id,
                "missing-matter",
                earlier.matter_fingerprint,
                earlier.client_party_id,
                earlier.subject_identity_fingerprint,
                collection,
                session=session,
            )
    assert history == (earlier, later)
    assert empty == ()
    assert all(item.tenant_id == earlier.tenant_id for item in history)
    assert all(item.case_matter_id == earlier.case_matter_id for item in history)


def test_real_duplicate_key_race_has_one_durable_truth(
    mongo_context: tuple[MongoClient[Any], Any, Any],
) -> None:
    """Concurrent identical contenders reconcile to one row or one retry."""
    client, _, collection = mongo_context
    value = _decision()
    barrier = Barrier(2)

    def contender() -> str:
        try:
            with client.start_session() as session:
                session.start_transaction()
                barrier.wait(timeout=10)
                result = registry.persist_firm_decision(value, collection, session=session)
                session.commit_transaction()
                assert result == value
                return "success"
        except (
            registry.LegalClientMatterEngagementFirmDecisionRegistryRetryRequiredError,
            PyMongoError,
        ):
            return "retry"

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: contender(), range(2)))
    assert "success" in outcomes
    assert collection.count_documents({"tenant_id": value.tenant_id}) == 1


def test_registry_source_excludes_authority_rereads_currentness_and_formation() -> None:
    """Static audit keeps persistence separate from later authorities."""
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_engagement_firm_decision_registry.py").read_text()
    assert "tenant_authorization_decision_evidence_registry" not in source
    assert "principal_status" not in source
    assert "ClientAcceptance" not in source
    assert "CaseMatter" not in source
    assert "LegalMatterParty" not in source
    assert "currentness" in source.lower()
    assert "LegalClientMatterEngagement(" not in source


# ARTIFACT: test_legal_client_matter_engagement_firm_decision_registry_real_mongo.py
# VERSION: v1.0.0-L9C9-P2-ENGAGEMENT-FIRM-DECISION-REGISTRY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable registry runtime evidence only
# TENANT POSTURE: UUID-isolated exact-tenant evidence; canonical wilsy excluded
# FAIL-CLOSED POSTURE: topology, transaction, corruption and authority failures reject; infrastructure skips explicitly
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
