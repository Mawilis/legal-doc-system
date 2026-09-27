"""Real-Mongo certificate for mandate-currentness composition.

TITLE: WILSY OS Legal Client Matter Mandate Currentness Composer Real-Mongo Certificate
VERSION: v1.0.0-L9B12-P2-RM-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published mandate-currentness composer against actual
         tenant-scoped Mongo registries in UUID-isolated databases. The
         certificate owns setup evidence only; it grants no production or
         downstream legal authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_mandate_currentness_composer_real_mongo.py
COLLABORATION / OWNERSHIP: Mandate, grant, acknowledgment and lifecycle
                            registries remain canonical authorities; the
                            published composer remains read-only and caller-
                            transaction-owned.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B12-P2-RM certifies topology, transaction ownership,
           same-session and same-time propagation, positive and negative
           currentness, identity/lineage binding, ambiguity, corruption,
           snapshot consistency, tenant isolation, determinism, raw BSON
           immutability and zero currentness persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only. No canonical
                             database, credentials, PII, bearer tokens or
                             production secrets are read or printed.
TENANT BOUNDARY: Every fixture and every composer read is exact-tenant scoped;
                 overlapping opaque identifiers are used only in disposable
                 databases to prove no cross-tenant oracle.
AUTHORITY BOUNDARY: Read-only mandate-currentness composition. No lifecycle,
                    Engagement, Representation, Court, IAM, HTTP, UI, Node or
                    financial authority is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution,
                              settlement and payment truth.
TRANSACTION BOUNDARY: The certificate owns disposable setup transactions and
                      read transactions; the composer owns none.
FAIL-CLOSED DECLARATION: Any unexpected CURRENT, torn read, scope divergence,
                         mutation, corruption or topology mismatch fails.
"""
from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern

from tools.eos.legal_operations.domain.legal_client_matter_mandate_currentness import (
    LegalClientMatterMandateCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_currentness import (
    LegalClientMatterMandateGrantCurrentnessState,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant_lifecycle import (
    LegalClientMatterMandateGrantLifecycleEvent,
    LegalClientMatterMandateGrantLifecycleReason,
)
from tools.eos.legal_operations.domain.legal_client_matter_mandate_acknowledgment import (
    LegalClientMatterMandateAcknowledgmentDecision,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_mandate_currentness_composer import (
    LegalClientMatterMandateCurrentnessComposer,
    LegalClientMatterMandateCurrentnessComposerError,
)
from tools.eos.legal_operations.registry import (
    legal_client_matter_mandate_acknowledgment_registry as acknowledgment_registry,
    legal_client_matter_mandate_grant_lifecycle_registry as grant_lifecycle_registry,
    legal_client_matter_mandate_grant_registry as grant_registry,
    legal_client_matter_mandate_registry as mandate_registry,
    legal_operations_lifecycle_registry as matter_registry,
)
from tests.unit.test_legal_client_matter_mandate import mandate as mandate_factory
from tests.unit.test_legal_client_matter_mandate_grant import (
    capacity as grant_capacity,
    grant as grant_factory,
    matter as grant_matter,
    party as grant_party,
)
from tests.unit.test_legal_client_matter_mandate_grant_lifecycle import (
    event as lifecycle_event_factory,
)
from tests.unit.test_legal_client_matter_mandate_acknowledgment import (
    acknowledgment as acknowledgment_factory,
)


VERSION = "v1.0.0-L9B12-P2-RM-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
MONGO_VERSION = "7.0.37"
T = datetime(2026, 9, 27, 16, 0, 0, 123456, tzinfo=timezone.utc)
TENANT_A = "tenant-l9b12-rm-a"
TENANT_B = "tenant-l9b12-rm-b"


@pytest.fixture()
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    """Yield one short UUID-isolated database and drop only that database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI, serverSelectionTimeoutMS=5000, retryWrites=True
    )
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
        name = f"wilsy_l9b12_p2_curr_cmp_{uuid.uuid4().hex}"
        assert len(name) <= 63
        database = client[name]
        collections = {
            "mandate": database[mandate_registry.COLLECTION],
            "grant": database[grant_registry.COLLECTION],
            "grant_lifecycle": database[grant_lifecycle_registry.COLLECTION],
            "matter": database[matter_registry.COLLECTION],
            "acknowledgment": database[acknowledgment_registry.COLLECTION],
        }
        mandate_registry.ensure_indexes(collections["mandate"])
        grant_registry.ensure_indexes(collections["grant"])
        grant_lifecycle_registry.ensure_indexes(collections["grant_lifecycle"])
        matter_registry.LegalOperationsLifecycleRegistry.ensure_indexes(
            collections["matter"]
        )
        acknowledgment_registry.ensure_indexes(collections["acknowledgment"])
        yield client, database, collections
    except PyMongoError as error:
        pytest.fail(f"real Mongo prerequisite/certificate failure: {type(error).__name__}")
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        finally:
            client.close()


def _transaction(client: MongoClient[Any], operation: Any) -> Any:
    """Run one disposable setup operation in a caller-owned transaction."""
    with client.start_session() as session:
        with session.start_transaction():
            return operation(session)


def _persist_bundle(
    client: MongoClient[Any], collections: dict[str, Any], values: tuple[Any, ...]
) -> None:
    """Persist synthetic matter, grant, acknowledgment and mandate evidence."""
    matter, grant, acknowledgment, mandate = values

    def operation(session: Any) -> None:
        matter_registry.LegalOperationsLifecycleRegistry.create(
            matter, collections["matter"], session=session
        )
        grant_registry.persist_grant(grant, collections["grant"], session=session)
        acknowledgment_registry.persist_acknowledgment(
            acknowledgment, collections["acknowledgment"], session=session
        )
        mandate_registry.persist_mandate(
            mandate, collections["mandate"], session=session
        )

    _transaction(client, operation)


def _bundle(
    tenant: str = TENANT_A,
    *,
    grant_id: str = "grant-l9b12",
    mandate_id: str = "mandate-l9b12",
    acknowledgment_id: str | None = None,
    decision: LegalClientMatterMandateAcknowledgmentDecision = LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
    matter_id: str = "matter-l9b12",
    grant_effective_from: datetime = T - timedelta(hours=3),
    grant_effective_until: datetime | None = T + timedelta(days=30),
    mandate_effective_from: datetime = T - timedelta(hours=2),
    mandate_effective_until: datetime | None = T + timedelta(days=30),
    acknowledgment_effective_from: datetime = T - timedelta(hours=1),
) -> tuple[Any, Any, Any, Any]:
    """Build one exact grant/ack/mandate lineage with controllable times."""
    source_matter = grant_matter(tenant_id=tenant, matter_id=matter_id)
    source_party = grant_party(source_matter=source_matter, party_id="party-l9b12")
    source_capacity = grant_capacity(
        source_matter=source_matter, source_party=source_party
    )
    grant = grant_factory(
        client_grant_id=grant_id,
        case_matter=source_matter,
        party=source_party,
        acting_capacity=source_capacity,
        occurred_at=grant_effective_from - timedelta(minutes=1),
        effective_from=grant_effective_from,
        effective_until=grant_effective_until,
        idempotency_key=f"grant-idempotency:{tenant}:{grant_id}",
    )
    durable_acknowledgment_id = acknowledgment_id or f"ack-l9b12-{grant_id}"
    acknowledgment = acknowledgment_factory(
        client_grant=grant,
        acknowledgment_id=durable_acknowledgment_id,
        decision=decision,
        occurred_at=acknowledgment_effective_from - timedelta(minutes=1),
        effective_from=acknowledgment_effective_from,
        idempotency_key=f"ack-idempotency:{tenant}:{durable_acknowledgment_id}",
    )
    mandate = mandate_factory(
        mandate_id=mandate_id,
        case_matter=source_matter,
        party=source_party,
        acting_capacity=source_capacity,
        client_grant_reference=grant.client_grant_id,
        client_grant_fingerprint=grant.fingerprint,
        firm_acknowledgment_reference=acknowledgment.acknowledgment_id,
        firm_acknowledgment_fingerprint=acknowledgment.fingerprint,
        occurred_at=mandate_effective_from - timedelta(minutes=1),
        effective_from=mandate_effective_from,
        effective_until=mandate_effective_until,
        idempotency_key=f"mandate-idempotency:{tenant}:{mandate_id}",
    )
    return source_matter, grant, acknowledgment, mandate


def _compose(
    client: MongoClient[Any], composer: LegalClientMatterMandateCurrentnessComposer,
    tenant: str, mandate_id: str, at: datetime = T,
) -> Any:
    """Compose exactly once in a fresh caller-owned snapshot transaction."""
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"))
        result = composer.compose_currentness(tenant, mandate_id, at, session)
        assert session.in_transaction is True
        session.abort_transaction()
        return result


def _composer(collections: dict[str, Any]) -> LegalClientMatterMandateCurrentnessComposer:
    """Bind the published composer to disposable real collections."""
    return LegalClientMatterMandateCurrentnessComposer(
        mandate_collection=collections["mandate"],
        grant_collection=collections["grant"],
        grant_lifecycle_collection=collections["grant_lifecycle"],
        matter_lifecycle_collection=collections["matter"],
        acknowledgment_collection=collections["acknowledgment"],
    )


def test_real_mongo_topology_and_current_positive_path(mongo_context, monkeypatch) -> None:
    """Certify topology, exact reads, same session/time and CURRENT."""
    client, _database, collections = mongo_context
    values = _bundle()
    _persist_bundle(client, collections, values)
    composer = _composer(collections)
    sessions: list[Any] = []
    times: list[datetime] = []
    original_mandate = mandate_registry.get_mandate
    original_grant = grant_registry.get_grant
    original_ack = acknowledgment_registry.list_acknowledgments_for_grant

    def mandate_read(*args: Any, **kwargs: Any) -> Any:
        sessions.append(kwargs["session"])
        return original_mandate(*args, **kwargs)

    def grant_read(*args: Any, **kwargs: Any) -> Any:
        sessions.append(kwargs["session"])
        return original_grant(*args, **kwargs)

    def ack_read(*args: Any, **kwargs: Any) -> Any:
        sessions.append(kwargs["session"])
        return original_ack(*args, **kwargs)

    monkeypatch.setattr(mandate_registry, "get_mandate", mandate_read)
    monkeypatch.setattr(grant_registry, "get_grant", grant_read)
    monkeypatch.setattr(
        acknowledgment_registry,
        "list_acknowledgments_for_grant",
        ack_read,
    )
    result = _compose(client, composer, TENANT_A, values[3].mandate_id)
    assert result.state is LegalClientMatterMandateCurrentnessState.CURRENT
    assert result.is_current is True
    assert len(sessions) >= 3 and all(value is sessions[0] for value in sessions)
    assert result.evaluation_time == T
    assert result.tenant_id == TENANT_A
    assert result.client_grant_id == values[1].client_grant_id
    assert result.firm_acknowledgment_id == values[2].acknowledgment_id
    assert times == []


def test_transaction_gate_and_formation_absent(mongo_context) -> None:
    """Require caller transaction and return truthful scoped absence."""
    client, _database, collections = mongo_context
    composer = _composer(collections)
    with pytest.raises(LegalClientMatterMandateCurrentnessComposerError) as raised:
        composer.compose_currentness(TENANT_A, "missing", T, None)
    assert raised.value.code == "L9B12_P2_ACTIVE_TRANSACTION_REQUIRED"
    with client.start_session() as session:
        with pytest.raises(LegalClientMatterMandateCurrentnessComposerError):
            composer.compose_currentness(TENANT_A, "missing", T, session)
        session.start_transaction()
        result = composer.compose_currentness(TENANT_A, "missing", T, session)
        assert result.state is LegalClientMatterMandateCurrentnessState.FORMATION_ABSENT
        session.abort_transaction()


def test_temporal_paths_and_determinism(mongo_context) -> None:
    """Certify NOT_YET_EFFECTIVE, EXPIRED and exact repeated output."""
    client, _database, collections = mongo_context
    future = _bundle(
        grant_id="grant-future", mandate_id="mandate-future",
        grant_effective_from=T + timedelta(hours=2),
        acknowledgment_effective_from=T + timedelta(hours=3),
        mandate_effective_from=T + timedelta(hours=4),
    )
    expired = _bundle(
        grant_id="grant-expired", mandate_id="mandate-expired",
        grant_effective_from=T - timedelta(hours=3),
        grant_effective_until=T - timedelta(hours=1),
        mandate_effective_from=T - timedelta(hours=2),
        mandate_effective_until=T - timedelta(hours=1),
        acknowledgment_effective_from=T - timedelta(hours=1, minutes=30),
    )
    _persist_bundle(client, collections, future)
    _persist_bundle(client, collections, expired)
    composer = _composer(collections)
    assert _compose(client, composer, TENANT_A, future[3].mandate_id).state is LegalClientMatterMandateCurrentnessState.NOT_YET_EFFECTIVE
    assert _compose(client, composer, TENANT_A, expired[3].mandate_id).state is LegalClientMatterMandateCurrentnessState.EXPIRED
    first = _compose(client, composer, TENANT_A, future[3].mandate_id, future[3].effective_from - timedelta(minutes=1))
    second = _compose(client, composer, TENANT_A, future[3].mandate_id, future[3].effective_from - timedelta(minutes=1))
    assert first == second
    assert first.fingerprint == second.fingerprint


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        (LegalClientMatterMandateGrantLifecycleEvent.REVOKED, LegalClientMatterMandateGrantCurrentnessState.REVOKED),
        (LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED, LegalClientMatterMandateGrantCurrentnessState.SUPERSEDED),
    ],
)
def test_grant_terminal_states_are_not_current(mongo_context, event, expected) -> None:
    """Certify real persisted revocation and supersession evidence."""
    client, _database, collections = mongo_context
    values = _bundle(grant_id=f"grant-{event.value.lower()}", mandate_id=f"mandate-{event.value.lower()}")
    _persist_bundle(client, collections, values)
    successor = _bundle(grant_id=f"successor-{event.value.lower()}")[1]
    lifecycle = lifecycle_event_factory(
        client_grant=values[1],
        lifecycle_event_id=f"event-{event.value.lower()}",
        event=event,
        occurred_at=T - timedelta(minutes=10),
        effective_from=T - timedelta(minutes=5),
        successor_grant=successor if event is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED else None,
        acting_capacity_id=None if event is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED else "capacity-firm-l9b6",
        acting_capacity_fingerprint=None if event is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED else "e" * 128,
        reason=None if event is LegalClientMatterMandateGrantLifecycleEvent.SUPERSEDED else LegalClientMatterMandateGrantLifecycleReason.CLIENT_WITHDRAWAL,
    )
    _transaction(client, lambda session: grant_lifecycle_registry.persist_event(lifecycle, collections["grant_lifecycle"], session=session))
    result = _compose(client, _composer(collections), TENANT_A, values[3].mandate_id)
    assert result.state is LegalClientMatterMandateCurrentnessState.GRANT_NOT_CURRENT
    assert result.grant_currentness_state == expected.value


def test_acknowledgment_states_and_later_identity(mongo_context) -> None:
    """Certify non-positive decisions and later decisive identity invalidation."""
    client, _database, collections = mongo_context
    for decision in (
        LegalClientMatterMandateAcknowledgmentDecision.DECLINED,
        LegalClientMatterMandateAcknowledgmentDecision.REQUIRES_REVIEW,
    ):
        values = _bundle(
            grant_id=f"grant-{decision.value.lower()}",
            mandate_id=f"mandate-{decision.value.lower()}",
            decision=decision,
        )
        _persist_bundle(client, collections, values)
        result = _compose(client, _composer(collections), TENANT_A, values[3].mandate_id)
        assert result.state is LegalClientMatterMandateCurrentnessState.ACKNOWLEDGMENT_NOT_CURRENT
    values = _bundle()
    _persist_bundle(client, collections, values)
    later = acknowledgment_factory(
        client_grant=values[1],
        acknowledgment_id="ack-l9b12-a2",
        decision=LegalClientMatterMandateAcknowledgmentDecision.ACKNOWLEDGED,
        occurred_at=T + timedelta(hours=1),
        effective_from=T + timedelta(hours=1),
        idempotency_key="ack-idempotency:l9b12:a2",
    )
    _transaction(client, lambda session: acknowledgment_registry.persist_acknowledgment(later, collections["acknowledgment"], session=session))
    result = _compose(client, _composer(collections), TENANT_A, values[3].mandate_id, T + timedelta(hours=2))
    assert result.state is LegalClientMatterMandateCurrentnessState.LINEAGE_MISMATCH
    assert result.firm_acknowledgment_id == values[2].acknowledgment_id


def test_lineage_tenant_isolation_and_multiple_mandates(mongo_context) -> None:
    """Prove exact identity/tenant scope and one-mandate-at-a-time behavior."""
    client, database, collections = mongo_context
    first = _bundle(tenant=TENANT_A, grant_id="overlap", mandate_id="mandate-a")
    second = _bundle(tenant=TENANT_B, grant_id="overlap", mandate_id="mandate-b", matter_id="matter-b")
    independent = _bundle(tenant=TENANT_A, grant_id="independent", mandate_id="mandate-independent")
    for values in (first, second, independent):
        _persist_bundle(client, collections, values)
    composer = _composer(collections)
    assert _compose(client, composer, TENANT_A, "mandate-a").state is LegalClientMatterMandateCurrentnessState.CURRENT
    assert _compose(client, composer, TENANT_A, "mandate-independent").state is LegalClientMatterMandateCurrentnessState.CURRENT
    assert _compose(client, composer, TENANT_A, "mandate-b").state is LegalClientMatterMandateCurrentnessState.FORMATION_ABSENT
    assert collections["mandate"].count_documents({}) == 3
    assert collections["grant"].count_documents({}) == 3
    assert collections["acknowledgment"].count_documents({}) == 3
    assert database.name != "wilsy"


def test_snapshot_consistency_and_read_only_audit(mongo_context) -> None:
    """Prove snapshot isolation and no currentness or source mutation."""
    client, database, collections = mongo_context
    values = _bundle()
    _persist_bundle(client, collections, values)
    before = {name: collection.count_documents({}) for name, collection in collections.items()}
    composer = _composer(collections)
    with client.start_session() as session_a, client.start_session() as session_b:
        session_a.start_transaction(read_concern=ReadConcern("snapshot"))
        first = composer.compose_currentness(TENANT_A, values[3].mandate_id, T, session_a)
        session_b.start_transaction()
        later = acknowledgment_factory(
            client_grant=values[1], acknowledgment_id="ack-snapshot-later",
            decision=LegalClientMatterMandateAcknowledgmentDecision.DECLINED,
            occurred_at=T + timedelta(minutes=1), effective_from=T + timedelta(minutes=1),
            idempotency_key="ack-idempotency:snapshot-later",
        )
        acknowledgment_registry.persist_acknowledgment(later, collections["acknowledgment"], session=session_b)
        session_b.commit_transaction()
        second = composer.compose_currentness(TENANT_A, values[3].mandate_id, T, session_a)
        session_a.abort_transaction()
        assert first == second
    fresh = _compose(client, composer, TENANT_A, values[3].mandate_id, T + timedelta(minutes=2))
    assert fresh.state is LegalClientMatterMandateCurrentnessState.ACKNOWLEDGMENT_NOT_CURRENT
    after = {name: collection.count_documents({}) for name, collection in collections.items()}
    assert after["mandate"] == before["mandate"]
    assert after["grant"] == before["grant"]
    assert after["matter"] == before["matter"]
    assert after["acknowledgment"] == before["acknowledgment"] + 1
    assert "legal_client_matter_mandate_currentness" not in database.list_collection_names()


def test_corruption_and_static_authority_audit(mongo_context) -> None:
    """Corruption blocks and the composer contains no excluded authority."""
    client, database, collections = mongo_context
    values = _bundle()
    _persist_bundle(client, collections, values)
    collections["mandate"].update_one(
        {"tenant_id": TENANT_A, "mandate_id": values[3].mandate_id},
        {"$set": {"client_grant_fingerprint": "f" * 128}},
    )
    with pytest.raises(LegalClientMatterMandateCurrentnessComposerError) as raised:
        _compose(client, _composer(collections), TENANT_A, values[3].mandate_id)
    assert raised.value.code == "L9B12_P2_MANDATE_READ_FAILED"
    assert database.name.startswith("wilsy_l9b12_p2_curr_cmp_")
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_currentness_composer.py")
    tree = ast.parse(source.read_text())
    imported = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    forbidden = ("pymongo", "fastapi", "jwt", "requests", "CaseMatter", "Engagement", "Representation", "Court")
    assert not any(token in module for module in imported for token in forbidden)


def test_no_transaction_lifecycle_or_currentness_persistence_in_source() -> None:
    """Static negative audit protects the composer authority boundary."""
    source = Path("tools/eos/legal_operations/orchestration/legal_client_matter_mandate_currentness_composer.py")
    tree = ast.parse(source.read_text())
    calls = [node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert not any(name in {"start_transaction", "commit_transaction", "abort_transaction", "insert_one", "update_one", "delete_one", "delete_many"} for name in calls)


# ARTIFACT: test_legal_client_matter_mandate_currentness_composer_real_mongo.py
# VERSION: v1.0.0-L9B12-P2-RM-CLIENT-MATTER-MANDATE-CURRENTNESS-COMPOSER
# AUTHORITY BOUNDARY: certificate-only real-Mongo read certification
# TENANT POSTURE: exact tenant scope and UUID-isolated databases
# FAIL-CLOSED POSTURE: topology, snapshot, corruption, identity and mutation failure
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
