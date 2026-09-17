"""WILSY OS C1E-R1B ordinary real-Mongo certificate.

TITLE: WILSY AI Legal Advisory Ordinary Real-Mongo Certificate
VERSION: v1.1.2-C1E-R1F
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercises the production C1E advisory service against a writable,
         replica-set Mongo database and proves source identity, tenant scope,
         exact replay, stale-source rejection, lineage, and transaction abort.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_advisory_real_mongo.py
COLLABORATION / OWNERSHIP: Certifies C1E composition over C1C/L7B/C1D.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.1.2-C1E-R1F preserves the canonical result fixture by
           inserting a copy so Mongo _id injection cannot alter its fingerprint.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic records; no prompts,
                             provider output, secrets, or raw legal payloads persist.
TENANT BOUNDARY: Every source and registry lookup includes the authenticated tenant.
AUTHORITY BOUNDARY: Review-only advisory evidence; no legal/model/provider,
                    execution, payment, settlement, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Mongo unavailability skips as an environment defect;
                         corruption, drift, cross-tenant access, and conflicts fail.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Iterator, cast
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.intelligence.adapters.legal_operations_advisory_adapter import build_legal_advisory
from tools.eos.intelligence.domain.ai_tool_orchestration import AIToolOrchestration, OrchestrationPhase, orchestration_identity
from tools.eos.intelligence.domain.legal_ai_gateway import GATEWAY_PERMISSION, LegalAIToolInvocationEvidence, TOOL_CONTRACTS
from tools.eos.intelligence.registry.ai_tool_orchestration_registry import COLLECTION as ORCHESTRATION_COLLECTION, AIToolOrchestrationRegistry, ensure_indexes as ensure_orchestration_indexes
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import COLLECTION as INVOCATION_COLLECTION, LegalAIToolInvocationRegistry, ensure_indexes as ensure_invocation_indexes
from tools.eos.intelligence.registry.next_best_action_advisory_registry import COLLECTION as ADVISORY_COLLECTION, NextBestActionAdvisoryConflictError, NextBestActionAdvisoryRegistry, NextBestActionAdvisoryRegistryError, ensure_indexes as ensure_advisory_indexes
from tools.eos.intelligence.wilsy_ai_advisory_service import WilsyAIAdvisoryService, WilsyAIAdvisoryServiceError

MONGO_URI = os.getenv("C1E_MONGO_URI", os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"))
REPLICA_SET = os.getenv("C1E_MONGO_REPLICA_SET", "wilsyVendorCertRS")
STAMP = datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc)
TENANT = "tenant-c1e-r1b"


def _context(tenant: str = TENANT) -> TenantAuthorizationContext:
    """Create explicit synthetic authenticated context for this certificate."""
    identity = SimpleNamespace(identity_id=f"principal-{tenant}", tenant_id=tenant)
    decision = SimpleNamespace(authorized=True, reason=SimpleNamespace(value="AUTHORIZED"))
    return TenantAuthorizationContext(identity=cast(Any, identity), tenant_id=tenant, decision=cast(Any, decision))


class _Reader:
    """Tenant-scoped legal evidence reader with call and payload tripwires."""

    def __init__(self, collection: Any) -> None:
        self.collection, self.calls = collection, 0

    def read(self, *, contract: Any, resource_identity: str, context: TenantAuthorizationContext, collections: Any) -> dict[str, object]:
        self.calls += 1
        assert contract.entity_type == "ServiceAttempt"
        row = self.collection.find_one({"tenant_id": context.tenant_id, "attempt_id": resource_identity})
        if row is None:
            raise WilsyAIAdvisoryServiceError("C1E_SOURCE_PROJECTION_INVALID")
        return {field: row[field] for field in contract.allowed_fields if field in row}


class _Authority:
    """Explicit legal-authority seam; it grants no provider or financial authority."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, *, contract: Any, context: TenantAuthorizationContext, session: Any) -> bool:
        self.calls += 1
        assert contract.underlying_permission == "legal_operations:attempt:read"
        assert context.tenant_id == TENANT and session is not None
        return True


class _AbortAfterWrite:
    """Fault-injection registry proving the service aborts partial persistence."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner

    def __getattr__(self, name: str) -> Any:
        return getattr(self.inner, name)

    def create_or_replay(self, advisory: Any, *, session: Any) -> Any:
        self.inner.create_or_replay(advisory, session=session)
        raise RuntimeError("certificate rollback tripwire")


@pytest.fixture(scope="module")
def mongo_database() -> Iterator[tuple[MongoClient, Any]]:
    """Yield an isolated writable replica-set database or skip as environment defect."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except (PyMongoError, OSError) as error:
        client.close()
        pytest.skip(f"ENVIRONMENT_DEFECT: Mongo runtime unavailable ({type(error).__name__})")
    if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary", hello.get("ismaster", False)) is not True:
        client.close()
        pytest.skip("ENVIRONMENT_DEFECT: writable replica-set primary unavailable")
    database = client[f"c1e_r1b_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def _result(tenant: str, attempt: str, state: str = "ALLOCATED") -> dict[str, object]:
    """Return the bounded server-side ServiceAttempt projection."""
    return {"tenant_id": tenant, "attempt_id": attempt, "instruction_id": f"instruction-{attempt}", "document_id": f"document-{attempt}", "deputy_id": f"deputy-{attempt}", "state": state, "evidence_identity": f"evidence-{attempt}"}


def _fingerprint(value: dict[str, object]) -> str:
    """Match the C1C/L7B canonical SHA3-512 result identity."""
    return hashlib.sha3_512(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _chain(tenant: str, attempt: str, token: str, stamp: datetime = STAMP) -> tuple[AIToolOrchestration, LegalAIToolInvocationEvidence, dict[str, object]]:
    """Build complete immutable C1C root plus L7B invocation evidence."""
    principal, root_id, invocation_id = f"principal-{tenant}", orchestration_identity(tenant, f"principal-{tenant}", f"idempotency-{token}"), f"invocation-{token}"
    result, contract = _result(tenant, attempt), TOOL_CONTRACTS["legal.attempt.read.v1"]
    root = AIToolOrchestration(root_id, tenant, principal, root_id, OrchestrationPhase.COMPLETED, f"planner-{token}", tool_invocation_id=invocation_id, synthesis_invocation_id=f"synthesis-{token}", tool_identity="legal.attempt.read.v1", resource_identity=attempt, evidence_references=(f"evidence-{token}",), outcome="TOOL_ASSISTED", revision=1, occurred_at=stamp)
    invocation = LegalAIToolInvocationEvidence(invocation_id, tenant, principal, "legal.attempt.read.v1", "v1", GATEWAY_PERMISSION, contract.underlying_permission, contract.capability, "tenant_legal_partner", f"entitlement-{tenant}", 1, "a" * 128, "STARTER", "b" * 128, f"capacity:{tenant}", "c" * 128, root_id, "d" * 128, "READ", f"ServiceAttempt:{attempt}", _fingerprint(result), stamp)
    return root, invocation, result


def _persist(database: Any, root: Any, invocation: Any) -> None:
    """Persist C1C/L7B facts inside one caller-owned transaction."""
    with database.client.start_session() as session:
        session.start_transaction()
        AIToolOrchestrationRegistry(database[ORCHESTRATION_COLLECTION]).create_or_replay(root, session=session)
        LegalAIToolInvocationRegistry(database[INVOCATION_COLLECTION]).create_or_replay(invocation, session=session)
        session.commit_transaction()


def _service(database: Any, reader: _Reader, authority: _Authority, advisory_registry: Any | None = None) -> WilsyAIAdvisoryService:
    """Compose production C1E with real registries and explicit seams."""
    return WilsyAIAdvisoryService(database=database, session_factory=database.client.start_session, orchestration_registry=AIToolOrchestrationRegistry(database[ORCHESTRATION_COLLECTION]), invocation_registry=LegalAIToolInvocationRegistry(database[INVOCATION_COLLECTION]), advisory_registry=advisory_registry or NextBestActionAdvisoryRegistry(database[ADVISORY_COLLECTION]), legal_reader=reader, authority_checker=authority)


def test_c1e_r1b_service_real_mongo_replay_stale_lineage_tenant_and_abort(mongo_database: tuple[MongoClient, Any]) -> None:
    """Prove replay, provenance, stale rejection, lineage arbitration, and rollback."""
    client, database = mongo_database
    ensure_orchestration_indexes(database[ORCHESTRATION_COLLECTION]); ensure_invocation_indexes(database[INVOCATION_COLLECTION]); ensure_advisory_indexes(database[ADVISORY_COLLECTION])
    assert {item["name"] for item in database[ADVISORY_COLLECTION].list_indexes()} >= {"c1d_advisory_identity_unique", "c1d_advisory_fingerprint_unique", "c1d_advisory_snapshot_unique", "c1d_advisory_successor_unique"}
    attempt = f"attempt-{uuid4().hex}"
    root, invocation, result = _chain(TENANT, attempt, "ordinary")
    database["c1e_source_attempts"].insert_one(dict(result)); _persist(database, root, invocation)
    reader, authority = _Reader(database["c1e_source_attempts"]), _Authority(); service = _service(database, reader, authority)
    first = asyncio.run(service.generate(orchestration_id=root.orchestration_id, context=_context(), generated_at=STAMP))
    assert first.replay is False and first.advisory.tenant_id == TENANT and first.advisory.scope_ref == root.orchestration_id
    sources_by_type = {item.evidence_type: item for item in first.advisory.source_references}
    assert sources_by_type["LEGAL_TOOL_RESULT"].evidence_identity == f"ServiceAttempt:{attempt}"
    assert first.advisory.generated_at == "2026-09-17T08:00:00Z"
    assert len(first.advisory.source_snapshot_fingerprint) == 128 and len(first.advisory.fingerprint) == 128
    assert database[ADVISORY_COLLECTION].count_documents({"tenant_id": TENANT}) == 1 and authority.calls >= 1 and reader.calls >= 2
    assert not any(hasattr(service, name) for name in ("execute", "run_model", "pay", "settle", "release"))
    replay = asyncio.run(_service(database, _Reader(database["c1e_source_attempts"]), _Authority()).generate(orchestration_id=root.orchestration_id, context=_context(), generated_at=STAMP))
    assert replay.replay is True and replay.advisory.to_dict() == first.advisory.to_dict() and database[ADVISORY_COLLECTION].count_documents({"tenant_id": TENANT}) == 1
    divergent = build_legal_advisory(tenant_id=TENANT, scope_ref=root.orchestration_id, root=root, invocation=invocation, result=result, generated_at="2026-09-17T08:30:00Z")
    with client.start_session() as session:
        with pytest.raises(NextBestActionAdvisoryConflictError, match="DIVERGENT_REPLAY"):
            NextBestActionAdvisoryRegistry(database[ADVISORY_COLLECTION]).create_or_replay(divergent, session=session)
    with client.start_session() as session:
        with pytest.raises(NextBestActionAdvisoryRegistryError, match="NOT_FOUND"):
            NextBestActionAdvisoryRegistry(database[ADVISORY_COLLECTION]).get(tenant_id="tenant-foreign", advisory_id=first.advisory.advisory_id, session=session)
    database["c1e_source_attempts"].update_one({"tenant_id": TENANT, "attempt_id": attempt}, {"$set": {"state": "CHANGED_AFTER_CAPTURE"}})
    with pytest.raises(WilsyAIAdvisoryServiceError, match="SOURCE_SNAPSHOT_STALE"):
        asyncio.run(service.get(advisory_id=first.advisory.advisory_id, context=_context()))
    with pytest.raises(WilsyAIAdvisoryServiceError, match="SOURCE_SNAPSHOT_STALE"):
        asyncio.run(service.generate(orchestration_id=root.orchestration_id, context=_context(), generated_at=STAMP))
    assert database[ADVISORY_COLLECTION].count_documents({"tenant_id": TENANT}) == 1
    # Direct immutable lineage certificate: one predecessor, one successor, no second successor.
    predecessor, predecessor_invocation, predecessor_result = _chain(TENANT, "lineage-a", "lineage-a")
    successor_root, successor_invocation, successor_result = _chain(TENANT, "lineage-b", "lineage-b", datetime(2026, 9, 17, 9, 0, tzinfo=timezone.utc))
    predecessor_advisory = build_legal_advisory(tenant_id=TENANT, scope_ref="lineage-scope", root=predecessor, invocation=predecessor_invocation, result=predecessor_result, generated_at=STAMP)
    successor_advisory = build_legal_advisory(tenant_id=TENANT, scope_ref="lineage-scope", root=successor_root, invocation=successor_invocation, result=successor_result, generated_at="2026-09-17T09:00:00Z", supersedes_advisory_id=predecessor_advisory.advisory_id)
    registry = NextBestActionAdvisoryRegistry(database[ADVISORY_COLLECTION])
    with client.start_session() as session:
        session.start_transaction(); registry.create_or_replay(predecessor_advisory, session=session); registry.create_or_replay(successor_advisory, session=session); session.commit_transaction()
    with client.start_session() as session:
        predecessor_before = predecessor_advisory.to_dict()
        assert registry.get_status(tenant_id=TENANT, advisory_id=predecessor_advisory.advisory_id, session=session).disposition == "STALE"
        assert registry.get_status(tenant_id=TENANT, advisory_id=successor_advisory.advisory_id, session=session).disposition == "CURRENT"
        assert registry.get(tenant_id=TENANT, advisory_id=predecessor_advisory.advisory_id, session=session).to_dict() == predecessor_before
        assert successor_advisory.generated_at > predecessor_advisory.generated_at and successor_advisory.source_snapshot_fingerprint != predecessor_advisory.source_snapshot_fingerprint
        with pytest.raises(NextBestActionAdvisoryConflictError):
            conflict_root, conflict_invocation, conflict_result = _chain(TENANT, "lineage-c", "lineage-c", datetime(2026, 9, 17, 10, 0, tzinfo=timezone.utc))
            registry.create_or_replay(build_legal_advisory(tenant_id=TENANT, scope_ref="lineage-scope", root=conflict_root, invocation=conflict_invocation, result=conflict_result, generated_at="2026-09-17T10:00:00Z", supersedes_advisory_id=predecessor_advisory.advisory_id), session=session)
    corrupt = first.advisory.to_dict(); corrupt["advisory_id"] = "corrupt-advisory"; corrupt["scope_ref"] = "corrupt-scope"; corrupt["fingerprint"] = "0" * 128
    database[ADVISORY_COLLECTION].insert_one(corrupt)
    with client.start_session() as session:
        with pytest.raises(NextBestActionAdvisoryRegistryError, match="CORRUPT"):
            registry.get(tenant_id=TENANT, advisory_id="corrupt-advisory", session=session)
    rollback_root, rollback_invocation, rollback_result = _chain(TENANT, f"attempt-rollback-{uuid4().hex}", "rollback"); database["c1e_source_attempts"].insert_one(rollback_result); _persist(database, rollback_root, rollback_invocation)
    with pytest.raises(WilsyAIAdvisoryServiceError, match="RECONCILIATION_REQUIRED"):
        asyncio.run(_service(database, reader, authority, _AbortAfterWrite(registry)).generate(orchestration_id=rollback_root.orchestration_id, context=_context(), generated_at=STAMP))
    assert database[ADVISORY_COLLECTION].count_documents({"tenant_id": TENANT, "scope_ref": rollback_root.orchestration_id}) == 0
    assert not database[ADVISORY_COLLECTION].count_documents({"provider": {"$exists": True}}) and not database[ADVISORY_COLLECTION].count_documents({"model": {"$exists": True}})
    assert not database[ADVISORY_COLLECTION].count_documents({"ServiceExecution": {"$exists": True}}) and not database[ADVISORY_COLLECTION].count_documents({"ReturnOfService": {"$exists": True}})


# ARTIFACT: test_wilsy_ai_advisory_real_mongo.py
# VERSION: v1.1.0-C1E-R1B
# AUTHORITY BOUNDARY: ordinary real-Mongo certificate only; no production authority
# TENANT POSTURE: every fixture query is UUID-isolated and tenant-scoped
# FAIL-CLOSED POSTURE: unavailable Mongo is an environment skip; corruption and drift fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# CERTIFICATION: one ordinary executable real-Mongo certificate; environment-gated only for unavailable Mongo
# END OF WILSY OS SOVEREIGN ARTIFACT
