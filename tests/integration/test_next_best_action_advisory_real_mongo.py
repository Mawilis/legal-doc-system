"""Authored C1D-R1A real-Mongo certificate (execution deferred to R1A).

TITLE: Next-Best-Action Advisory Real-Mongo Certificate
VERSION: v1.0.0-C1D-R1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Executable certificate for append-only advisory persistence, replay,
         tenant isolation, corruption rejection, transaction ownership, and lineage.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_next_best_action_advisory_real_mongo.py
COLLABORATION / OWNERSHIP: C1D registry certificate; host execution belongs to C1D-R1A.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.0-C1D-R1 authors the collection-safe R1A certificate without executing it.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.intelligence.adapters.legal_operations_advisory_adapter import POLICY_ID, POLICY_VERSION, build_legal_advisory
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolOrchestration, OrchestrationPhase, orchestration_identity
from tools.eos.intelligence.domain.legal_ai_gateway import GATEWAY_PERMISSION, LegalAIToolInvocationEvidence, TOOL_CONTRACTS
from tools.eos.intelligence.domain.next_best_action_advisory import build_advisory
from tools.eos.intelligence.registry.next_best_action_advisory_registry import COLLECTION, NextBestActionAdvisoryConflictError, NextBestActionAdvisoryRegistry, NextBestActionAdvisoryRegistryError, ensure_indexes

URI = os.getenv("C1D_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")


@pytest.fixture(scope="module")
def mongo_database():
    client = MongoClient(URI, serverSelectionTimeoutMS=1500)
    try:
        client.admin.command("ping")
    except PyMongoError as error:
        client.close()
        pytest.skip(f"C1D-R1A Mongo runtime unavailable: {type(error).__name__}")
    database = client[f"c1d_r1a_{uuid.uuid4().hex}"]
    try:
        yield database
    finally:
        client.drop_database(database.name)
        client.close()


def _advisory(tenant: str, attempt: str, stamp: datetime, idempotency: str, supersedes: str | None = None):
    principal = "principal-c1d-r1a"
    root_id = orchestration_identity(tenant, principal, idempotency)
    result = {"tenant_id": tenant, "attempt_id": attempt, "state": "ALLOCATED"}
    result_fp = hashlib.sha3_512(json.dumps(result, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    root = AIToolOrchestration(root_id, tenant, principal, root_id, OrchestrationPhase.COMPLETED, f"planner-{idempotency}", tool_invocation_id=f"inv-{idempotency}", synthesis_invocation_id=f"synth-{idempotency}", tool_identity="legal.attempt.read.v1", resource_identity=attempt, evidence_references=(f"result-{idempotency}",), outcome="TOOL_ASSISTED", revision=1, occurred_at=stamp)
    contract = TOOL_CONTRACTS["legal.attempt.read.v1"]
    invocation = LegalAIToolInvocationEvidence(f"inv-{idempotency}", tenant, principal, "legal.attempt.read.v1", "v1", GATEWAY_PERMISSION, contract.underlying_permission, contract.capability, "role", f"ent-{tenant}", 1, "a" * 128, "tier", "b" * 128, f"capacity:{tenant}", "c" * 128, root_id, "d" * 128, "READ", attempt, result_fp, stamp)
    return build_legal_advisory(tenant_id=tenant, scope_ref="matter-r1a", root=root, invocation=invocation, result=result, generated_at=stamp, supersedes_advisory_id=supersedes), result


def test_append_replay_tenant_isolation_lineage_corruption_and_abort(mongo_database):
    collection = mongo_database[COLLECTION]
    ensure_indexes(collection)
    assert {index["name"] for index in collection.list_indexes()} >= {"c1d_advisory_identity_unique", "c1d_advisory_fingerprint_unique", "c1d_advisory_snapshot_unique", "c1d_advisory_successor_unique"}
    registry = NextBestActionAdvisoryRegistry(collection)
    first, _ = _advisory("tenant-a", "attempt-a", datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc), "one")
    with mongo_database.client.start_session() as session:
        session.start_transaction()
        registry.create_or_replay(first, session=session)
        session.commit_transaction()

    restarted = NextBestActionAdvisoryRegistry(collection)
    with mongo_database.client.start_session() as session:
        assert restarted.create_or_replay(first, session=session) == first
        with pytest.raises(NextBestActionAdvisoryRegistryError, match="NOT_FOUND"):
            restarted.get(tenant_id="tenant-b", advisory_id=first.advisory_id, session=session)

    with mongo_database.client.start_session() as session:
        before = restarted.get(tenant_id="tenant-a", advisory_id=first.advisory_id, session=session)
        divergent = build_advisory(
            tenant_id=first.tenant_id,
            scope_ref=first.scope_ref,
            policy_id=POLICY_ID,
            policy_version=POLICY_VERSION,
            source_references=first.source_references,
            action_title=first.recommendation.action_title,
            target_subsystem=first.recommendation.target_subsystem,
            rationale=f"{first.recommendation.rationale} Divergent replay candidate.",
            risk_level=first.recommendation.risk_level,
            generated_at="2026-09-17T08:30:00Z",
        )
        assert divergent.advisory_id == first.advisory_id
        assert divergent.to_dict() != first.to_dict()
        with pytest.raises(NextBestActionAdvisoryConflictError):
            restarted.create_or_replay(divergent, session=session)
        assert restarted.get(tenant_id="tenant-a", advisory_id=first.advisory_id, session=session).to_dict() == before.to_dict()

        predecessor_snapshot = first.source_snapshot_fingerprint
        successor, _ = _advisory("tenant-a", "attempt-b", datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc), "three", first.advisory_id)
        successor_snapshot = successor.source_snapshot_fingerprint
        assert successor_snapshot != predecessor_snapshot
        restarted.create_or_replay(successor, session=session)
        predecessor_status = restarted.get_status(tenant_id="tenant-a", advisory_id=first.advisory_id, session=session)
        assert predecessor_status.disposition == "STALE"
        assert predecessor_status.superseded_by_advisory_id == successor.advisory_id
        status = restarted.get_status(tenant_id="tenant-a", advisory_id=successor.advisory_id, session=session)
        assert status.disposition == "CURRENT"
        assert status.superseded_by_advisory_id is None
        hydrated_predecessor = restarted.get(tenant_id="tenant-a", advisory_id=first.advisory_id, session=session)
        hydrated_successor = restarted.get(tenant_id="tenant-a", advisory_id=successor.advisory_id, session=session)
        assert hydrated_predecessor.source_snapshot_fingerprint == predecessor_snapshot
        assert hydrated_successor.source_snapshot_fingerprint == successor_snapshot
        assert hydrated_predecessor.source_references == first.source_references
        assert hydrated_successor.source_references == successor.source_references
        assert hydrated_successor.supersedes_advisory_id == hydrated_predecessor.advisory_id
        assert hydrated_predecessor.to_dict() == before.to_dict()

        successor_2, _ = _advisory("tenant-a", "attempt-c", datetime(2026, 9, 17, 10, 0, tzinfo=timezone.utc), "four", first.advisory_id)
        assert successor_2.advisory_id != successor.advisory_id
        assert successor_2.supersedes_advisory_id == first.advisory_id
        assert successor_2.tenant_id == first.tenant_id
        assert successor_2.scope_ref == first.scope_ref
        assert successor_2.source_snapshot_fingerprint not in {predecessor_snapshot, successor_snapshot}
        assert successor_2.generated_at > first.generated_at
        rows_before_second_successor = collection.count_documents({"tenant_id": "tenant-a"}, session=session)
        with pytest.raises(NextBestActionAdvisoryConflictError):
            restarted.create_or_replay(successor_2, session=session)
        assert collection.count_documents({"tenant_id": "tenant-a"}, session=session) == rows_before_second_successor
        first_successor_status = restarted.get_status(tenant_id="tenant-a", advisory_id=first.advisory_id, session=session)
        assert first_successor_status.disposition == "STALE"
        assert first_successor_status.superseded_by_advisory_id == successor.advisory_id

    aborted, _ = _advisory("tenant-a", "attempt-d", datetime(2026, 9, 17, 11, 0, tzinfo=timezone.utc), "five")
    with mongo_database.client.start_session() as session:
        session.start_transaction()
        restarted.create_or_replay(aborted, session=session)
        session.abort_transaction()
    with mongo_database.client.start_session() as session:
        with pytest.raises(NextBestActionAdvisoryRegistryError, match="NOT_FOUND"):
            restarted.get(tenant_id="tenant-a", advisory_id=aborted.advisory_id, session=session)

    corrupt_collection = mongo_database[f"{COLLECTION}_corruption"]
    corrupt_registry = NextBestActionAdvisoryRegistry(corrupt_collection)
    corrupt_document = first.to_dict()
    corrupt_document["fingerprint"] = "0" * 128
    corrupt_collection.insert_one(corrupt_document)
    with mongo_database.client.start_session() as session:
        with pytest.raises(NextBestActionAdvisoryRegistryError, match="CORRUPT"):
            corrupt_registry.get(tenant_id="tenant-a", advisory_id=first.advisory_id, session=session)


# ARTIFACT: test_next_best_action_advisory_real_mongo.py
# VERSION: v1.0.0-C1D-R1
# CERTIFICATION: authored R1A certificate; execution intentionally deferred
# END OF WILSY OS SOVEREIGN ARTIFACT
