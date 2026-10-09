"""Real-Mongo certificate for firm acknowledgment currentness composition.

TITLE: WILSY OS Legal Client Matter Mandate Acknowledgment Currentness Composer Real Mongo Certificate
VERSION: v1.0.0-L9B10-P3-RM-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove the published acknowledgment-currentness composer against real
         append-only grant and acknowledgment registries in UUID-isolated
         Mongo databases, including snapshot reads and fail-closed corruption.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_acknowledgment_currentness_composer_real_mongo.py
COLLABORATION / OWNERSHIP: The published composer, grant registry,
                            acknowledgment registry and projection remain the
                            production authorities. This certificate owns no
                            production behavior.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B10-P3-RM-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER
           certifies topology, caller transactions, every decision state,
           effective-time precedence, ambiguity, tenant isolation, corruption,
           snapshot consistency, append-only retention and zero projection
           persistence. No IAM, mandate, Engagement, Court or finance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only;
                             no credentials, PII, bearer tokens or canonical
                             database writes are permitted.
TENANT BOUNDARY: Every grant and acknowledgment operation is tenant-scoped;
                 overlapping opaque IDs across tenants are explicitly tested.
AUTHORITY BOUNDARY: Real-Mongo certificate for read-only currentness
                    composition only. No currentness persistence or downstream
                    legal, IAM, HTTP, UI or financial authority.
TRANSACTION BOUNDARY: The test owns all disposable sessions and transactions;
                      the composer must not start, commit, abort or retry.
FAIL-CLOSED DECLARATION: Runtime, topology, snapshot, corruption, lineage,
                         mutation or unexpected positive results fail the test.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern

from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgment,
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment_currentness import (
    LegalClientMatterMandateAcknowledgmentCurrentnessState,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_acknowledgment_currentness_composer import (
    LegalClientMatterMandateAcknowledgmentCurrentnessComposer,
    LegalClientMatterMandateAcknowledgmentCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
)
from tests.unit.test_legal_client_matter_mandate_grant import (
    BASE,
    capacity,
    grant,
    matter,
    party,
)


VERSION = "v1.0.0-L9B10-P3-RM-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"
T = BASE + timedelta(hours=3)
TENANT_A = "tenant-l9b10-rm-a"
TENANT_B = "tenant-l9b10-rm-b"


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient, Any, Any, Any]]:
    """Yield one UUID-isolated database and drop only that database afterward."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert client.server_info().get("version") == MONGO_VERSION
        with client.start_session() as probe:
            probe.start_transaction(read_concern=ReadConcern("snapshot"))
            assert probe.in_transaction is True
            probe.abort_transaction()
        database = client[f"wilsy_l9b10_ack_currentness_{uuid.uuid4().hex}"]
        grant_collection = database[grant_registry.COLLECTION]
        acknowledgment_collection = database[acknowledgment_registry.COLLECTION]
        grant_registry.ensure_indexes(grant_collection)
        acknowledgment_registry.ensure_indexes(acknowledgment_collection)
        yield client, database, grant_collection, acknowledgment_collection
    except PyMongoError as error:
        pytest.fail(f"real Mongo prerequisite/certificate failure: {type(error).__name__}")
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def _grant_for(tenant: str, grant_id: str, matter_id: str) -> Any:
    """Build one valid synthetic grant with an explicit tenant and identity."""
    source_matter = matter(tenant_id=tenant, matter_id=matter_id)
    source_party = party(source_matter=source_matter, party_id=f"party-{matter_id}")
    source_capacity = capacity(source_matter=source_matter, source_party=source_party)
    return grant(
        client_grant_id=grant_id,
        case_matter=source_matter,
        party=source_party,
        acting_capacity=source_capacity,
        idempotency_key=f"grant-idempotency:{tenant}:{grant_id}",
    )


def _acknowledgment(
    source: Any,
    *,
    decision: LegalClientMatterMandateAcknowledgmentDecision,
    acknowledgment_id: str,
    effective_from: datetime,
    occurred_at: datetime | None = None,
) -> LegalClientMatterMandateAcknowledgment:
    """Build one exact-grant-bound synthetic acknowledgment."""
    occurred = occurred_at or effective_from
    return LegalClientMatterMandateAcknowledgment.from_client_grant(
        client_grant=source,
        acknowledgment_id=acknowledgment_id,
        decision=decision,
        decision_actor_principal_id="principal-firm-l9b10-rm",
        authorization_evidence_reference="authorization:l9b10-rm",
        authorization_evidence_fingerprint="a" * 128,
        source_evidence_reference="source:l9b10-rm",
        source_evidence_fingerprint="b" * 128,
        occurred_at=occurred,
        effective_from=effective_from,
        idempotency_key=f"ack-idempotency:{acknowledgment_id}",
    )


def _commit(client: MongoClient, operation: Any) -> None:
    """Execute one setup write in a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            operation(session)


def _persist_grant(value: Any, collection: Any, session: Any) -> None:
    """Persist one canonical grant through the real registry."""
    grant_registry.persist_grant(value, collection, session=session)


def _persist_acknowledgment(value: Any, collection: Any, session: Any) -> None:
    """Persist one canonical acknowledgment through the real registry."""
    acknowledgment_registry.persist_acknowledgment(value, collection, session=session)


def _compose(
    client: MongoClient,
    composer: LegalClientMatterMandateAcknowledgmentCurrentnessComposer,
    tenant: str,
    grant_id: str,
    at: datetime,
    *,
    read_concern: ReadConcern | None = None,
) -> Any:
    """Compose once in a fresh caller-owned transaction."""
    with client.start_session() as session:
        session.start_transaction(read_concern=read_concern) if read_concern else session.start_transaction()
        result = composer.compose_currentness(tenant, grant_id, at, session)
        assert session.in_transaction is True
        session.abort_transaction()
        return result


def _composer(
    grant_collection: Any,
    acknowledgment_collection: Any,
) -> LegalClientMatterMandateAcknowledgmentCurrentnessComposer:
    """Bind the published composer to the disposable real collections."""
    return LegalClientMatterMandateAcknowledgmentCurrentnessComposer(
        grant_collection=grant_collection,
        acknowledgment_collection=acknowledgment_collection,
    )


def test_real_mongo_topology_and_read_only_decision_states(mongo_context, monkeypatch) -> None:
    """Certify transaction gating, no/future history and all single decisions."""
    client, database, grant_collection, acknowledgment_collection = mongo_context
    composer = _composer(grant_collection, acknowledgment_collection)
    sessions: list[Any] = []
    original_grant_read = grant_registry.get_grant
    original_history_read = acknowledgment_registry.list_acknowledgments_for_grant

    def spy_grant(*args: Any, **kwargs: Any) -> Any:
        sessions.append(kwargs["session"])
        return original_grant_read(*args, **kwargs)

    def spy_history(*args: Any, **kwargs: Any) -> Any:
        sessions.append(kwargs["session"])
        return original_history_read(*args, **kwargs)

    monkeypatch.setattr(grant_registry, "get_grant", spy_grant)
    monkeypatch.setattr(
        acknowledgment_registry,
        "list_acknowledgments_for_grant",
        spy_history,
    )
    with pytest.raises(LegalClientMatterMandateAcknowledgmentCurrentnessComposerError):
        composer.compose_currentness(TENANT_A, "missing", T, None)
    with client.start_session() as inactive:
        with pytest.raises(LegalClientMatterMandateAcknowledgmentCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, "missing", T, inactive)

    source = _grant_for(TENANT_A, "states", "matter-states")
    _commit(client, lambda session: _persist_grant(source, grant_collection, session))
    before_collections = set(database.list_collection_names())
    no_decision = _compose(client, composer, TENANT_A, "states", T)
    assert no_decision.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION
    assert no_decision.decisive_acknowledgment_ids == ()

    future = _acknowledgment(
        source,
        decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        acknowledgment_id="future",
        effective_from=T + timedelta(minutes=1),
    )
    _commit(client, lambda session: _persist_acknowledgment(future, acknowledgment_collection, session))
    future_result = _compose(client, composer, TENANT_A, "states", T)
    assert future_result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION

    for index, decision in enumerate(LegalClientMatterMandateAcknowledgmentDecision):
        value = _acknowledgment(
            source,
            decision=decision,
            acknowledgment_id=f"single-{index}",
            effective_from=T + timedelta(minutes=2 + index),
        )
        # Each single decision is evaluated at its own exact effective boundary.
        _commit(client, lambda session, value=value: _persist_acknowledgment(value, acknowledgment_collection, session))
        result = _compose(client, composer, TENANT_A, "states", value.effective_from)
        assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState(decision.value)

    assert set(database.list_collection_names()) == before_collections
    assert database.name.startswith("wilsy_l9b10_ack_currentness_")
    assert database.name != "wilsy"
    assert all(item is not None for item in sessions)


def test_real_mongo_effective_transitions_and_same_effective_conflicts(mongo_context) -> None:
    """Certify append-only transitions, identical decisions and ambiguity."""
    client, database, grant_collection, acknowledgment_collection = mongo_context
    composer = _composer(grant_collection, acknowledgment_collection)

    source = _grant_for(TENANT_A, "transitions", "matter-transitions")
    _commit(client, lambda session: _persist_grant(source, grant_collection, session))
    earlier = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED, acknowledgment_id="earlier", effective_from=T - timedelta(hours=1))
    later_ack = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="later-ack", effective_from=T)
    _commit(client, lambda session: (_persist_acknowledgment(earlier, acknowledgment_collection, session), _persist_acknowledgment(later_ack, acknowledgment_collection, session)))
    assert _compose(client, composer, TENANT_A, "transitions", T).state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED

    later_declined = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED, acknowledgment_id="later-declined", effective_from=T + timedelta(hours=1))
    _commit(client, lambda session: _persist_acknowledgment(later_declined, acknowledgment_collection, session))
    assert _compose(client, composer, TENANT_A, "transitions", T + timedelta(hours=1)).state is LegalClientMatterMandateAcknowledgmentCurrentnessState.DECLINED

    later_review = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW, acknowledgment_id="later-review", effective_from=T + timedelta(hours=2))
    _commit(client, lambda session: _persist_acknowledgment(later_review, acknowledgment_collection, session))
    assert _compose(client, composer, TENANT_A, "transitions", T + timedelta(hours=2)).state is LegalClientMatterMandateAcknowledgmentCurrentnessState.REQUIRES_REVIEW
    assert acknowledgment_collection.count_documents({"tenant_id": TENANT_A, "client_grant_id": "transitions"}) == 4

    for index, decision in enumerate(LegalClientMatterMandateAcknowledgmentDecision):
        value = _grant_for(TENANT_A, f"same-{index}", f"matter-same-{index}")
        _commit(client, lambda session, value=value: _persist_grant(value, grant_collection, session))
        one = _acknowledgment(value, decision=decision, acknowledgment_id=f"same-{index}-a", effective_from=T)
        two = _acknowledgment(value, decision=decision, acknowledgment_id=f"same-{index}-b", effective_from=T)
        _commit(client, lambda session, one=one, two=two: (_persist_acknowledgment(one, acknowledgment_collection, session), _persist_acknowledgment(two, acknowledgment_collection, session)))
        result = _compose(client, composer, TENANT_A, f"same-{index}", T)
        assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState(decision.value)
        assert set(result.decisive_acknowledgment_ids) == {one.acknowledgment_id, two.acknowledgment_id}

    conflict_grant = _grant_for(TENANT_A, "conflict", "matter-conflict")
    _commit(client, lambda session: _persist_grant(conflict_grant, grant_collection, session))
    conflict_values = tuple(
        _acknowledgment(conflict_grant, decision=decision, acknowledgment_id=f"conflict-{index}", effective_from=T)
        for index, decision in enumerate(LegalClientMatterMandateAcknowledgmentDecision)
    )
    _commit(client, lambda session: tuple(_persist_acknowledgment(value, acknowledgment_collection, session) for value in reversed(conflict_values)))
    conflict_result = _compose(client, composer, TENANT_A, "conflict", T)
    assert conflict_result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS
    assert set(conflict_result.decisive_acknowledgment_ids) == {value.acknowledgment_id for value in conflict_values}
    assert database.name != "wilsy"


def test_real_mongo_order_boundary_and_determinism(mongo_context) -> None:
    """Certify insertion/order independence, exact boundary and fingerprints."""
    client, _, grant_collection, acknowledgment_collection = mongo_context
    composer = _composer(grant_collection, acknowledgment_collection)
    source = _grant_for(TENANT_A, "ordering", "matter-ordering")
    _commit(client, lambda session: _persist_grant(source, grant_collection, session))
    declined = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED, acknowledgment_id="order-declined", effective_from=T, occurred_at=T - timedelta(minutes=2))
    acknowledged = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="order-ack", effective_from=T, occurred_at=T - timedelta(minutes=1))
    _commit(client, lambda session: (_persist_acknowledgment(declined, acknowledgment_collection, session), _persist_acknowledgment(acknowledged, acknowledgment_collection, session)))
    first = _compose(client, composer, TENANT_A, "ordering", T)
    assert first.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.AMBIGUOUS
    acknowledgment_collection.delete_many({"tenant_id": TENANT_A, "client_grant_id": "ordering"})
    _commit(client, lambda session: (_persist_acknowledgment(acknowledged, acknowledgment_collection, session), _persist_acknowledgment(declined, acknowledgment_collection, session)))
    second = _compose(client, composer, TENANT_A, "ordering", T)
    assert second.state is first.state
    assert second.fingerprint == first.fingerprint
    assert second.decisive_acknowledgment_fingerprints == first.decisive_acknowledgment_fingerprints

    boundary = _grant_for(TENANT_A, "boundary", "matter-boundary")
    _commit(client, lambda session: _persist_grant(boundary, grant_collection, session))
    exact = _acknowledgment(boundary, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="boundary-exact", effective_from=T)
    _commit(client, lambda session: _persist_acknowledgment(exact, acknowledgment_collection, session))
    boundary_result = _compose(client, composer, TENANT_A, "boundary", T)
    assert boundary_result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED
    with client.start_session() as first_session, client.start_session() as second_session:
        first_session.start_transaction()
        first_value = composer.compose_currentness(TENANT_A, "boundary", T, first_session)
        second_session.start_transaction()
        second_value = composer.compose_currentness(TENANT_A, "boundary", T, second_session)
        assert first_session.in_transaction and second_session.in_transaction
        first_session.abort_transaction()
        second_session.abort_transaction()
    assert first_value.fingerprint == second_value.fingerprint == boundary_result.fingerprint


def test_real_mongo_tenant_isolation_lineage_and_corruption(mongo_context) -> None:
    """Certify tenant scope, lineage blocking, BSON corruption and retention."""
    client, database, grant_collection, acknowledgment_collection = mongo_context
    composer = _composer(grant_collection, acknowledgment_collection)
    grant_a = _grant_for(TENANT_A, "overlap", "matter-overlap-a")
    grant_b = _grant_for(TENANT_B, "overlap", "matter-overlap-b")
    _commit(client, lambda session: (_persist_grant(grant_a, grant_collection, session), _persist_grant(grant_b, grant_collection, session)))
    only_b = _acknowledgment(grant_b, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="overlap-ack", effective_from=T)
    _commit(client, lambda session: _persist_acknowledgment(only_b, acknowledgment_collection, session))
    assert _compose(client, composer, TENANT_A, "overlap", T).state is LegalClientMatterMandateAcknowledgmentCurrentnessState.NO_DECISION
    assert _compose(client, composer, TENANT_B, "overlap", T).state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED

    wrong_matter = matter(tenant_id=TENANT_A, matter_id="matter-wrong-lineage")
    wrong_party = party(source_matter=wrong_matter, party_id="party-wrong-lineage")
    wrong_capacity = capacity(source_matter=wrong_matter, source_party=wrong_party)
    wrong_grant = grant(client_grant_id="overlap", case_matter=wrong_matter, party=wrong_party, acting_capacity=wrong_capacity, idempotency_key="wrong-lineage-grant")
    wrong = _acknowledgment(wrong_grant, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="wrong-lineage", effective_from=T)
    _commit(client, lambda session: _persist_acknowledgment(wrong, acknowledgment_collection, session))
    result = _compose(client, composer, TENANT_A, "overlap", T)
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.CORRUPT_BLOCKED
    assert result.is_usable is False

    corrupt_grant = _grant_for(TENANT_A, "corrupt", "matter-corrupt")
    _commit(client, lambda session: _persist_grant(corrupt_grant, grant_collection, session))
    corrupt_ack = _acknowledgment(corrupt_grant, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="corrupt", effective_from=T)
    _commit(client, lambda session: _persist_acknowledgment(corrupt_ack, acknowledgment_collection, session))
    acknowledgment_collection.update_one({"tenant_id": TENANT_A, "acknowledgment_id": "corrupt"}, {"$set": {"decision": "CORRUPTED"}})
    with pytest.raises(LegalClientMatterMandateAcknowledgmentCurrentnessComposerError):
        _compose(client, composer, TENANT_A, "corrupt", T)
    assert acknowledgment_collection.count_documents({"tenant_id": TENANT_A, "client_grant_id": "corrupt"}) == 1
    assert not any("currentness" in name for name in database.list_collection_names())


def test_real_mongo_snapshot_consistency_and_append_only_retention(mongo_context) -> None:
    """Prove a transaction snapshot cannot observe a later concurrent commit."""
    client, database, grant_collection, acknowledgment_collection = mongo_context
    composer = _composer(grant_collection, acknowledgment_collection)
    source = _grant_for(TENANT_A, "snapshot", "matter-snapshot")
    _commit(client, lambda session: _persist_grant(source, grant_collection, session))
    earlier = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="snapshot-earlier", effective_from=T - timedelta(hours=1))
    _commit(client, lambda session: _persist_acknowledgment(earlier, acknowledgment_collection, session))
    with client.start_session() as session_a, client.start_session() as session_b:
        session_a.start_transaction(read_concern=ReadConcern("snapshot"))
        before = composer.compose_currentness(TENANT_A, "snapshot", T, session_a)
        assert before.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED
        later = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED, acknowledgment_id="snapshot-later", effective_from=T + timedelta(hours=1))
        session_b.start_transaction()
        _persist_acknowledgment(later, acknowledgment_collection, session_b)
        session_b.commit_transaction()
        during = composer.compose_currentness(TENANT_A, "snapshot", T + timedelta(hours=1), session_a)
        assert during.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED
        assert session_a.in_transaction is True
        session_a.abort_transaction()
    after = _compose(client, composer, TENANT_A, "snapshot", T + timedelta(hours=1))
    assert after.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.DECLINED
    assert acknowledgment_collection.count_documents({"tenant_id": TENANT_A, "client_grant_id": "snapshot"}) == 2
    assert not any("currentness" in name for name in database.list_collection_names())


def test_real_mongo_read_only_audit_and_no_ttl(mongo_context) -> None:
    """Audit indexes, retention, no currentness collection and source exclusions."""
    client, database, grant_collection, acknowledgment_collection = mongo_context
    composer = _composer(grant_collection, acknowledgment_collection)
    source = _grant_for(TENANT_A, "audit", "matter-audit")
    _commit(client, lambda session: _persist_grant(source, grant_collection, session))
    value = _acknowledgment(source, decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED, acknowledgment_id="audit", effective_from=T)
    _commit(client, lambda session: _persist_acknowledgment(value, acknowledgment_collection, session))
    before = {
        "grant": grant_collection.count_documents({}),
        "ack": acknowledgment_collection.count_documents({}),
        "collections": tuple(sorted(database.list_collection_names())),
    }
    result = _compose(client, composer, TENANT_A, "audit", T)
    after = {
        "grant": grant_collection.count_documents({}),
        "ack": acknowledgment_collection.count_documents({}),
        "collections": tuple(sorted(database.list_collection_names())),
    }
    assert result.state is LegalClientMatterMandateAcknowledgmentCurrentnessState.ACKNOWLEDGED
    assert before == after
    indexes = list(acknowledgment_collection.list_indexes())
    assert all("expireAfterSeconds" not in index for index in indexes)
    assert not any("currentness" in name for name in after["collections"])
    assert database.name != "wilsy"
    source_text = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_acknowledgment_currentness_composer.py").read_text()
    assert "legal_client_matter_mandate_grant_currentness_composer" not in source_text
    assert "start_transaction" not in source_text
    assert "commit_transaction" not in source_text
    assert "abort_transaction" not in source_text
    assert "insert_one" not in source_text
    assert "update_one" not in source_text
    assert "delete_many" not in source_text
    assert "create_index" not in source_text
    assert "IAM" in source_text and "Engagement" in source_text
    assert pymongo_version


# ARTIFACT: test_legal_client_matter_mandate_acknowledgment_currentness_composer_real_mongo.py
# VERSION: v1.0.0-L9B10-P3-RM-FIRM-MANDATE-ACKNOWLEDGMENT-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: disposable real-Mongo read-only composer certificate
# TENANT POSTURE: UUID-isolated tenant-scoped grant and acknowledgment evidence
# FAIL-CLOSED POSTURE: topology, transaction, state, corruption and mutation failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
