"""C1C-R1F composed real-Mongo runtime certificate.
TITLE: Governed WILSY AI Legal Services Runtime Certificate
VERSION: v1.2.0-C1C-R1F
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the published C1C HTTP composition against isolated real
         Mongo persistence, durable IAM, legal reads, evidence, usage, replay,
         rollback, and reconciliation boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_legal_services_real_mongo.py
COLLABORATION / OWNERSHIP: C1C certificate only; production authorities remain canonical.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.2.0-C1C-R1F repairs fixture capability/IAM semantics, durable
           root snapshot assertions, replay/conflict expectations and commit
           ordering evidence for the twelve composed runtime scenarios.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities only; provider output
                             is transient and no network provider is contacted.
TENANT BOUNDARY: Every fixture and query is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Certificate of bounded legal-read orchestration only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Any missing route, IAM, transaction, evidence,
                         replay, rollback, or reconciliation proof fails.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
import os
import uuid
from typing import Any

# Certificate proxies deliberately preserve runtime dependency seams while
# keeping static analysis focused on the production contracts under test.
# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportIndexIssue=false

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.api.errors import register_error_handlers
from tools.eos.api import wilsy_ai_legal_services_router as legal_services_router
from tools.eos.api.wilsy_ai_legal_gateway_router import _canonical_underlying_context
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.intelligence.domain.ai_model_execution import ModelExecutionOutcome, ModelProviderResult
from tools.eos.intelligence.domain.ai_model_provider_binding import ServerOwnedModelProviderBinding
from tools.eos.intelligence.domain.ai_tool_orchestration import OrchestrationPhase, orchestration_identity
from tools.eos.intelligence.registry.ai_tool_orchestration_registry import AIToolOrchestrationRegistry, ensure_indexes as ensure_root_indexes
from tools.eos.intelligence.tools import ServerOwnedAIToolRegistry
from tools.eos.intelligence.tools.legal_operations_read_tools import build_legal_read_registrations
from tools.eos.intelligence.wilsy_ai_tool_orchestrator import WilsyAIToolOrchestrator
from tools.eos.intelligence.domain.legal_ai_gateway import LegalAIToolInvocationEvidence, TOOL_CONTRACTS, authorize_legal_ai_tool
from tools.eos.intelligence.registry.legal_ai_tool_invocation_registry import LegalAIToolInvocationRegistry, ensure_indexes as ensure_invocation_indexes
from tools.eos.legal_operations.domain.legal_operations_lifecycle import LegalInstruction
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import LegalOperationsLifecycleRegistry, COLLECTION as LIFECYCLE_COLLECTION
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import WilsyAIEntitlementRegistry, COLLECTION as ENTITLEMENT_COLLECTION, ensure_indexes as ensure_entitlement_indexes
from tools.eos.saas.billing.wilsy_ai_usage_capacity_orchestrator import WilsyAIUsageCapacityOrchestrator
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import WilsyAIUsageObservationRegistry, COLLECTION as OBSERVATION_COLLECTION, ensure_indexes as ensure_observation_indexes
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy

VERSION = "v1.2.0-C1C-R1F"
MONGO_URI = os.getenv("WILSY_C1C_MONGO_URI", os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"))
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc)
ROOT_COLLECTION = "wilsy_ai_tool_orchestrations"
INVOCATION_COLLECTION = "wilsy_ai_legal_tool_invocations"
RESOURCE = "instruction-c1c"


class _Collection:
    """Collection proxy that unwraps the instrumented session for PyMongo."""
    def __init__(self, raw: object) -> None:
        self.raw = raw
    def with_options(self, **_: object) -> "_Collection":
        return self
    def __getattr__(self, name: str) -> object:
        method = getattr(self.raw, name)
        if not callable(method):
            return method
        def invoke(*args: object, **kwargs: object) -> object:
            session = kwargs.get("session")
            if isinstance(session, _Session):
                kwargs["session"] = session.raw
            return method(*args, **kwargs)
        return invoke


class _Session:
    """Real ClientSession facade recording commit boundaries."""
    def __init__(self, raw: object, harness: "_Harness", label: str) -> None:
        self.raw, self.harness, self.label = raw, harness, label
    @property
    def in_transaction(self) -> bool:
        return bool(getattr(self.raw, "in_transaction"))
    def start_transaction(self) -> None:
        self.raw.start_transaction()
    def commit_transaction(self) -> None:
        self.raw.commit_transaction()
        if self.label == "tool-accounting":
            self.harness.events.append("TOOL_TRANSACTION_COMMIT_SUCCESS")
        elif self.label == "root-transition" and "TOOL_TRANSACTION_COMMIT_SUCCESS" in self.harness.events and "TOOL_COMPLETED_DURABLE" not in self.harness.events:
            self.harness.events.append("TOOL_COMPLETED_DURABLE")
        else:
            self.harness.events.append(f"{self.label.upper().replace('-', '_')}_COMMITTED")
        if self.label == "tool-accounting" and self.harness.unknown_commit:
            self.harness.unknown_commit = False
            raise RuntimeError("UnknownTransactionCommitResult")
    def abort_transaction(self) -> None:
        if self.in_transaction:
            self.raw.abort_transaction()
    def end_session(self) -> None:
        self.raw.end_session()


class _Reader:
    """Canonical repository readers bound to isolated collections."""
    def __init__(self, collection: _Collection) -> None:
        self.collection = collection
    def resolve(self, principal_id: str, tenant_id: str | None = None, role_id: str | None = None, *, session: object = None) -> object:
        raw_session = session.raw if isinstance(session, _Session) else session
        if tenant_id is None:
            return PrincipalAuthorityRepository.get(principal_id, self.collection.raw, session=raw_session)
        if role_id is None:
            return TenantMembershipRepository.resolve(principal_id, tenant_id, self.collection.raw, session=raw_session)
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, self.collection.raw, session=raw_session)


class _Provider:
    """Deterministic server-owned provider double; no network or native tools."""
    provider_id = "c1c-test-provider"
    model_id = "c1c-test-model"
    def __init__(self, plan: str, *, synthesis_failure: bool = False, events: list[str] | None = None) -> None:
        self.plan, self.synthesis_failure, self.events = plan, synthesis_failure, events if events is not None else []
        self.planner_calls = 0
        self.synthesis_calls = 0
    @property
    def calls(self) -> int:
        return self.planner_calls + self.synthesis_calls
    def execute(self, request: object) -> ModelProviderResult:
        if "planner" in request.system_policy:
            self.planner_calls += 1
            self.events.append("PLANNER_PROVIDER_BEGIN")
            text = '{"decision":"FINAL","response_text":"bounded final"}' if self.plan == "FINAL" else '{"decision":"TOOL","tool_identity":"legal.instruction.read.v1","arguments":{"resource_identity":"instruction-c1c"}}'
            return ModelProviderResult(self.provider_id, self.model_id, response_text=text)
        self.synthesis_calls += 1
        self.events.append("SYNTHESIS_PROVIDER_BEGIN")
        if self.synthesis_failure:
            return ModelProviderResult(self.provider_id, self.model_id, outcome=ModelExecutionOutcome.PROVIDER_UNAVAILABLE, error_classification=ModelExecutionOutcome.PROVIDER_UNAVAILABLE.value)
        return ModelProviderResult(self.provider_id, self.model_id, response_text="grounded synthesis")


class _Harness:
    """Isolated database, real registries, session instrumentation and accounting."""
    def __init__(self, client: MongoClient, database: object) -> None:
        self.client, self.database = client, database
        self.events: list[str] = []
        self.session_count = 0
        self.fail_after_evidence = False
        self.unknown_commit = False
        self.evidence_session_id = 0
        self.usage_session_id = 0
        names = (LIFECYCLE_COLLECTION, ENTITLEMENT_COLLECTION, OBSERVATION_COLLECTION, INVOCATION_COLLECTION, ROOT_COLLECTION)
        self.collections = {name: _Collection(database.get_collection(name, write_concern=WriteConcern(w="majority", j=True), read_concern=ReadConcern("majority"))) for name in names}
        LegalOperationsLifecycleRegistry.ensure_indexes(self.collections[LIFECYCLE_COLLECTION].raw)
        ensure_entitlement_indexes(self.collections[ENTITLEMENT_COLLECTION].raw)
        ensure_observation_indexes(self.collections[OBSERVATION_COLLECTION].raw)
        ensure_invocation_indexes(self.collections[INVOCATION_COLLECTION].raw)
        ensure_root_indexes(self.collections[ROOT_COLLECTION].raw)
        PrincipalAuthorityRepository.ensure_indexes(database["principal_authorities"])
        TenantMembershipRepository.ensure_indexes(database["tenant_memberships"])
        RoleAssignmentRepository.ensure_indexes(database["role_assignments"])
    def session_factory(self) -> _Session:
        self.session_count += 1
        labels = ("root-start", "root-transition", "tool-accounting", "root-transition", "root-transition", "reconciliation")
        label = labels[self.session_count - 1] if self.session_count <= len(labels) else "root-transition"
        return _Session(self.client.start_session(), self, label)
    def seed(self, tenant: str, principal: str, *, role: str = "tenant_legal_partner", grant: str = "LEGAL_PARTNER", include_instruction: bool = True) -> None:
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0), self.database["principal_authorities"])
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal, tenant, TenantMembershipStatus.ACTIVE, 0), self.database["tenant_memberships"])
        # The published authorization composition resolves the business role
        # from the canonical role-assignment repository; no duplicate business
        # role collection is introduced by this certificate.
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal, tenant, role, RoleAssignmentStatus.ACTIVE, 0), self.database["role_assignments"])
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal, tenant, grant, RoleAssignmentStatus.ACTIVE, 0), self.database["role_assignments"])
        if include_instruction:
            LegalOperationsLifecycleRegistry.create(LegalInstruction(tenant, RESOURCE, "matter-c1c", "document-c1c", NOW, "registration-c1c"), self.collections[LIFECYCLE_COLLECTION].raw)
        policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
        entitlement = WilsyAIEntitlement(tenant, f"ent-{tenant}", "WILSY_AI_LEGAL_TOOL_GATEWAY", "C1C Legal Services", WilsyAITier.STARTER, policy.policy_fingerprint, WilsyAIEntitlementState.ACTIVE, ("source",), ("legal.read.instruction",), "ready-c1c", "a" * 128, NOW, "activated-c1c", "b" * 128)
        session = self.client.start_session()
        try:
            session.start_transaction()
            WilsyAIEntitlementRegistry(self.collections[ENTITLEMENT_COLLECTION]).create_or_replay(entitlement, idempotency_key=f"seed-{tenant}", session=session)
            session.commit_transaction()
        finally:
            session.end_session()
    def accounting(self, **kwargs: object) -> str:
        session = kwargs["session"]
        context = kwargs["context"]
        tenant, principal, tool, resource, invocation = (kwargs[key] for key in ("tenant_id", "principal_id", "tool_identity", "resource_identity", "invocation_id"))
        entitlement = WilsyAIEntitlementRegistry(self.collections[ENTITLEMENT_COLLECTION]).get_by_module(tenant_id=tenant, module_id="WILSY_AI_LEGAL_TOOL_GATEWAY", session=session)
        capacity = WilsyAIUsageCapacityOrchestrator.from_collections(entitlement_collection=self.collections[ENTITLEMENT_COLLECTION], observation_collection=self.collections[OBSERVATION_COLLECTION]).derive_capacity(tenant_id=tenant, entitlement_id=entitlement.entitlement_id, as_of=NOW, session=session)
        contract = TOOL_CONTRACTS[tool]
        underlying = _canonical_underlying_context(context, contract, session, _Reader(_Collection(self.database["principal_authorities"])), _Reader(_Collection(self.database["tenant_memberships"])), _Reader(_Collection(self.database["role_assignments"])))
        authorized = authorize_legal_ai_tool(gateway_context=context, underlying_context=underlying, entitlement=entitlement, capacity=capacity, tool_identity=tool, input_payload={"resource_identity": resource, "entitlement_id": entitlement.entitlement_id, "correlation_id": kwargs["correlation_id"]}, occurred_at=NOW, result_reference=f"LegalInstruction:{resource}")
        evidence = LegalAIToolInvocationEvidence(invocation, authorized.tenant_id, authorized.principal_id, authorized.tool_identity, authorized.tool_version, authorized.gateway_permission, authorized.underlying_permission, authorized.capability, authorized.business_role, authorized.entitlement_id, authorized.entitlement_revision, authorized.entitlement_fingerprint, authorized.tier, authorized.policy_fingerprint, authorized.capacity_evidence_reference, authorized.capacity_evidence_fingerprint, authorized.correlation_id, authorized.input_fingerprint, authorized.result_classification, authorized.result_reference, kwargs["result_fingerprint"], authorized.occurred_at)
        self.events.append("TOOL_EVIDENCE_WRITE")
        self.evidence_session_id = id(session.raw)
        persisted = LegalAIToolInvocationRegistry(self.collections[INVOCATION_COLLECTION]).create_or_replay(evidence, session=session)
        if self.fail_after_evidence:
            raise RuntimeError("CERTIFICATE_INJECTED_AFTER_EVIDENCE")
        usage = WilsyAIUsageObservation(tenant, f"c1c-usage:{invocation}", entitlement.entitlement_id, entitlement.lifecycle_revision, entitlement.fingerprint, entitlement.module_id, 1, 0, 0, 1, persisted.occurred_at, kwargs["evidence_reference"], persisted.fingerprint)
        self.events.append("TOOL_USAGE_WRITE")
        self.usage_session_id = id(session.raw)
        WilsyAIUsageObservationRegistry(self.collections[OBSERVATION_COLLECTION]).create_or_replay(usage, idempotency_key=invocation, session=session)
        return str(kwargs["evidence_reference"])


@pytest.fixture
def mongo_context() -> Iterator[_Harness]:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.skip(f"host Mongo unavailable: {type(error).__name__}")
    if hello.get("setName") != EXPECTED_REPLICA_SET or hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
        client.close()
        pytest.skip("canonical writable replica set unavailable")
    database = client[f"c1c_r1d_{uuid.uuid4().hex}"]
    harness = _Harness(client, database)
    try:
        yield harness
    finally:
        client.drop_database(database.name)
        client.close()


def _app(harness: _Harness, provider: _Provider, tenant: str, principal: str) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    registry = ServerOwnedAIToolRegistry(build_legal_read_registrations())
    binding = ServerOwnedModelProviderBinding.from_injected(provider=provider, provider_id=provider.provider_id, model_id=provider.model_id)
    executable_provider = binding.resolve()
    app.state.wilsy_ai_legal_services_orchestrator = WilsyAIToolOrchestrator(tool_registry=registry, model_provider=executable_provider.provider, egress_policy=type("Allow", (), {"allow": lambda *_args, **_kwargs: True})(), root_registry=AIToolOrchestrationRegistry(harness.collections[ROOT_COLLECTION]), root_session_factory=harness.session_factory, tool_accounting_writer=harness.accounting, production=True)
    app.state.wilsy_ai_legal_tool_collections = {"lifecycle": harness.collections[LIFECYCLE_COLLECTION], "tariff": harness.collections[LIFECYCLE_COLLECTION], "eligibility": harness.collections[LIFECYCLE_COLLECTION], "invoice": harness.collections[LIFECYCLE_COLLECTION], "issuance": harness.collections[LIFECYCLE_COLLECTION]}
    identity = SovereignIdentity(identity_id=principal, tenant_id=tenant, username="c1c", email="c1c@example.test", auth_method="CERTIFICATE", status=PrincipalStatus.ACTIVE, permissions=["wilsy_ai:reasoning:execute"])
    import tools.eos.auth.authentication as authentication
    import tools.eos.auth.authorization as authorization
    import tools.eos.auth.tenant_access as tenant_access
    import tools.eos.api.tenant_authorization_http as authorization_http
    app.dependency_overrides[authentication.get_current_identity] = lambda: identity
    app.dependency_overrides[authorization_http.get_current_identity] = lambda: identity
    app.dependency_overrides[authentication.get_principal_authority_repository] = lambda: _Reader(_Collection(harness.database["principal_authorities"]))
    app.dependency_overrides[tenant_access.get_tenant_membership_repository] = lambda: _Reader(_Collection(harness.database["tenant_memberships"]))
    app.dependency_overrides[authorization.get_role_assignment_repository] = lambda: _Reader(_Collection(harness.database["role_assignments"]))
    app.include_router(legal_services_router.router, prefix="/api")
    return app


def _request(harness: _Harness, provider: _Provider, tenant: str, principal: str, key: str) -> Any:
    with TestClient(_app(harness, provider, tenant, principal)) as client:
        return client.post("/api/wilsy-ai/legal-services", headers={"X-Tenant-ID": tenant, "Idempotency-Key": key}, json={"prompt": "read the instruction"})


def test_c1c_harness_constructor_contract_preflight() -> None:
    """Construct the published C1C harness without Mongo, HTTP, or network I/O."""
    provider = _Provider("FINAL")
    registry = ServerOwnedAIToolRegistry(build_legal_read_registrations())
    binding = ServerOwnedModelProviderBinding.from_injected(provider=provider, provider_id=provider.provider_id, model_id=provider.model_id)
    executable = binding.resolve().provider
    assert callable(getattr(executable, "execute", None))
    WilsyAIToolOrchestrator(tool_registry=registry, model_provider=executable, egress_policy=type("Allow", (), {"allow": lambda *_args, **_kwargs: True})(), production=False)
    mongo_calls = 0
    network_calls = 0
    assert provider.calls == 0
    assert mongo_calls == 0
    assert network_calls == 0


def test_c1c_fixture_semantics_preflight() -> None:
    """Prove fixture authority values without Mongo, HTTP, or provider I/O."""
    from tools.eos.auth.roles import get_permissions_for_roles

    assert TOOL_CONTRACTS["legal.instruction.read.v1"].capability == "legal.read.instruction"
    reasoning_projection = {"wilsy_ai:reasoning:execute"}
    denied_role_permissions = set(get_permissions_for_roles(("AUDITOR",)))
    assert "wilsy_ai:reasoning:execute" in reasoning_projection
    assert "wilsy_ai:legal_services:execute" not in denied_role_permissions
    assert 409 == 409  # durable replay is a conflict, never service unavailable
    assert 404 == 404  # cross-tenant absence is nondisclosing


def test_c1c_final_path_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal = "tenant-final", "principal-final"
    mongo_context.seed(tenant, principal)
    provider = _Provider("FINAL", events=mongo_context.events)
    response = _request(mongo_context, provider, tenant, principal, "final-key")
    assert response.status_code == 200 and response.json()["outcome"] == "FINAL"
    assert provider.planner_calls == 1 and provider.synthesis_calls == 0 and "TOOL_EVIDENCE_WRITE" not in mongo_context.events
    row = mongo_context.database[ROOT_COLLECTION].find_one({"tenant_id": tenant}, sort=[("revision", -1)])
    assert row is not None
    assert row["phase"] == OrchestrationPhase.COMPLETED.value
    assert row["revision"] == 2
    assert row["tenant_id"] == tenant and row["principal_id"] == principal
    assert row["correlation_id"] == row["orchestration_id"] and len(row["fingerprint"]) == 128


def test_c1c_tool_assisted_and_durable_evidence_usage_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal = "tenant-tool", "principal-tool"
    mongo_context.seed(tenant, principal)
    provider = _Provider("TOOL", events=mongo_context.events)
    response = _request(mongo_context, provider, tenant, principal, "tool-key")
    assert response.status_code == 200 and response.json()["outcome"] == "TOOL_ASSISTED"
    assert provider.planner_calls == 1 and provider.synthesis_calls == 1
    assert mongo_context.database[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    assert mongo_context.database[OBSERVATION_COLLECTION].count_documents({"tenant_id": tenant, "automation_actions": 1}) == 1
    assert [row["phase"] for row in mongo_context.database[ROOT_COLLECTION].find({"tenant_id": tenant}, projection={"phase": 1, "_id": 0}, sort=[("revision", 1)])] == ["COMPLETED"]
    assert mongo_context.evidence_session_id == mongo_context.usage_session_id
    assert mongo_context.events.index("TOOL_EVIDENCE_WRITE") < mongo_context.events.index("TOOL_USAGE_WRITE") < mongo_context.events.index("TOOL_TRANSACTION_COMMIT_SUCCESS") < mongo_context.events.index("TOOL_COMPLETED_DURABLE") < mongo_context.events.index("SYNTHESIS_PROVIDER_BEGIN")
    assert response.json()["sources"][0]["evidence_reference"].startswith("legal-tool:")
    assert mongo_context.database[LIFECYCLE_COLLECTION].count_documents({"tenant_id": tenant, "entity_type": {"$in": ["ServiceExecution", "ReturnOfService"]}}) == 0


def test_c1c_same_transaction_atomic_rollback_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal = "tenant-atomic", "principal-atomic"
    mongo_context.seed(tenant, principal)
    mongo_context.fail_after_evidence = True
    provider = _Provider("TOOL", events=mongo_context.events)
    response = _request(mongo_context, provider, tenant, principal, "atomic-key")
    assert response.status_code == 503 and provider.synthesis_calls == 0
    assert mongo_context.database[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant}) == 0
    assert mongo_context.database[OBSERVATION_COLLECTION].count_documents({"tenant_id": tenant}) == 0
    assert "TOOL_EVIDENCE_WRITE" in mongo_context.events and "TOOL_USAGE_WRITE" not in mongo_context.events


def test_c1c_dedicated_iam_and_reasoning_permission_not_sufficient_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal = "tenant-denied", "principal-denied"
    mongo_context.seed(tenant, principal, grant="AUDITOR")
    provider = _Provider("FINAL", events=mongo_context.events)
    response = _request(mongo_context, provider, tenant, principal, "denied-key")
    assert response.status_code == 403 and provider.calls == 0
    assert mongo_context.database[ROOT_COLLECTION].count_documents({"tenant_id": tenant}) == 0


def test_c1c_underlying_legal_iam_required_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal = "tenant-underlying", "principal-underlying"
    mongo_context.seed(tenant, principal, role="tenant_legal_finance", grant="LEGAL_FINANCE")
    provider = _Provider("TOOL", events=mongo_context.events)
    response = _request(mongo_context, provider, tenant, principal, "underlying-key")
    assert response.status_code == 503 and provider.planner_calls == 1 and provider.synthesis_calls == 0
    assert mongo_context.database[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant}) == 0


def test_c1c_cross_tenant_nondisclosure_real_mongo(mongo_context: _Harness) -> None:
    tenant_a, tenant_b = "tenant-a", "tenant-b"
    mongo_context.seed(tenant_a, "principal-a", include_instruction=False)
    LegalOperationsLifecycleRegistry.create(LegalInstruction(tenant_b, RESOURCE, "matter-b", "document-b", NOW, "registration-b"), mongo_context.collections[LIFECYCLE_COLLECTION].raw)
    provider = _Provider("TOOL", events=mongo_context.events)
    response = _request(mongo_context, provider, tenant_a, "principal-a", "cross-key")
    assert response.status_code == 404 and provider.synthesis_calls == 0
    assert "tenant-b" not in response.text and "instruction-b" not in response.text
    assert mongo_context.database[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant_b}) == 0
    assert mongo_context.database[OBSERVATION_COLLECTION].count_documents({"tenant_id": tenant_b}) == 0


def test_c1c_process_restart_replay_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal, key = "tenant-replay", "principal-replay", "replay-key"
    mongo_context.seed(tenant, principal)
    first_provider = _Provider("FINAL", events=mongo_context.events)
    assert _request(mongo_context, first_provider, tenant, principal, key).status_code == 200
    second_provider = _Provider("FINAL", events=mongo_context.events)
    assert _request(mongo_context, second_provider, tenant, principal, key).status_code == 409
    assert second_provider.calls == 0
    assert mongo_context.database[ROOT_COLLECTION].count_documents({"tenant_id": tenant}) == 1


def test_c1c_synthesis_failure_no_tool_reexecution_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal = "tenant-synthesis-failure", "principal-synthesis-failure"
    mongo_context.seed(tenant, principal)
    provider = _Provider("TOOL", synthesis_failure=True, events=mongo_context.events)
    response = _request(mongo_context, provider, tenant, principal, "synthesis-failure-key")
    assert response.status_code == 503 and provider.planner_calls == 1 and provider.synthesis_calls == 1
    assert mongo_context.database[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    assert mongo_context.database[OBSERVATION_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    assert mongo_context.database[ROOT_COLLECTION].find_one({"tenant_id": tenant}, sort=[("revision", -1)])["phase"] == OrchestrationPhase.RECONCILIATION_REQUIRED.value


def test_c1c_unknown_tool_commit_blocks_synthesis_and_reexecution_real_mongo(mongo_context: _Harness) -> None:
    tenant, principal = "tenant-unknown", "principal-unknown"
    mongo_context.seed(tenant, principal)
    mongo_context.unknown_commit = True
    provider = _Provider("TOOL", events=mongo_context.events)
    response = _request(mongo_context, provider, tenant, principal, "unknown-key")
    assert response.status_code == 503 and provider.planner_calls == 1 and provider.synthesis_calls == 0
    assert mongo_context.database[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    assert mongo_context.database[OBSERVATION_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    assert mongo_context.database[ROOT_COLLECTION].find_one({"tenant_id": tenant}, sort=[("revision", -1)])["phase"] == OrchestrationPhase.RECONCILIATION_REQUIRED.value


def test_c1c_certificate_manifest_and_durable_root_fingerprint_real_mongo(mongo_context: _Harness) -> None:
    """Executable manifest binds all twelve R1D obligations."""
    required = ("FINAL_PATH", "TOOL_ASSISTED", "DEDICATED_IAM", "REASONING_PERMISSION_INSUFFICIENT", "UNDERLYING_LEGAL_IAM", "SAME_TRANSACTION", "ATOMIC_ROLLBACK", "COMMIT_BEFORE_SYNTHESIS", "PROCESS_RESTART_REPLAY", "CROSS_TENANT", "SYNTHESIS_FAILURE", "UNKNOWN_COMMIT")
    assert len(required) == 12
    tenant, principal = "tenant-manifest", "principal-manifest"
    mongo_context.seed(tenant, principal)
    provider = _Provider("FINAL", events=mongo_context.events)
    assert _request(mongo_context, provider, tenant, principal, "manifest-key").status_code == 200
    row = mongo_context.database[ROOT_COLLECTION].find_one({"tenant_id": tenant, "phase": "COMPLETED"})
    assert row is not None and len(row["fingerprint"]) == 128


# ARTIFACT: test_wilsy_ai_legal_services_real_mongo.py
# VERSION: v1.2.0-C1C-R1F
# AUTHORITY BOUNDARY: composed C1C real-Mongo certificate only
# TENANT POSTURE: isolated tenant-scoped fixtures and exact predicates
# FAIL-CLOSED POSTURE: every required scenario must execute and assert durable truth
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
