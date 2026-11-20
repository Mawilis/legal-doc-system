"""C1B-R19 real-Mongo HTTP certificate.

TITLE: WILSY AI Authenticated Reasoning HTTP Real-Mongo Certificate
VERSION: v1.1.0-READ-ONLY-CONTEXT-REPLICA-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercise the authenticated reasoning command against canonical Mongo
         registries with deterministic success, failure, and replay evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_reasoning_http_real_mongo.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/api/wilsy_ai_reasoning_router.py
                            and the published C1B/P4/P5A/P6 authorities.
CERTIFICATION / UPDATE DATE: 2026-11-20
CHANGELOG: v1.1.0-READ-ONLY-CONTEXT-REPLICA-CERT adds exact-tenant Projects
           context HTTP reads, source entitlement denial, stale revision and
           source-person verification on the real isolated replica set.
           v1.0.0 establishes the official C1B-R19 HTTP Mongo certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic data; no raw provider error
                             or prompt is written to Mongo.
TENANT BOUNDARY: Every canonical registry call is tenant-scoped.
AUTHORITY BOUNDARY: Real persistence and HTTP projection evidence only; IAM
                    is injected, not claimed as live authenticated acceptance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED DECLARATION: Mongo unavailability is an environment defect, never pass.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from types import SimpleNamespace
from typing import Any, Iterator, cast
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError

import tools.eos.api.wilsy_ai_reasoning_router as module
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.intelligence.domain.ai_model_execution import ModelProviderResult
from tools.eos.intelligence.domain.ai_model_provider_binding import ServerOwnedModelProviderBinding
from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import COLLECTION as ENTITLEMENT_COLLECTION, WilsyAIEntitlementRegistry, ensure_indexes as ensure_entitlement_indexes
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import COLLECTION as ADMISSION_COLLECTION, ensure_indexes as ensure_admission_indexes
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import COLLECTION as OBSERVATION_COLLECTION, ensure_indexes as ensure_observation_indexes
from tools.eos.intelligence.registry.ai_model_invocation_registry import COLLECTION as INVOCATION_COLLECTION, ensure_indexes as ensure_invocation_indexes
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState


URI = os.getenv("TEST_WILSY_AI_REASONING_MONGO_URI", os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"))
REPLICA_SET = os.getenv("TEST_WILSY_AI_REASONING_REPLICA_SET", "wilsyVendorCertRS")
NOW = datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc)
EVIDENCE_FP = "a" * 128


class Provider:
    """Deterministic provider double with externally visible call count."""

    def __init__(self, failure: bool = False) -> None:
        self.failure = failure
        self.calls = 0

    def execute(self, request: Any) -> ModelProviderResult:
        self.calls += 1
        if self.failure:
            raise TimeoutError("provider detail must never escape")
        return ModelProviderResult(provider_id="provider-http", model_id="model-http", response_text="bounded response", provider_request_id="request-http", input_tokens=3, output_tokens=2)


def _context(tenant_id: str) -> TenantAuthorizationContext:
    return TenantAuthorizationContext(identity=cast(Any, SimpleNamespace(identity_id="principal-http")), tenant_id=tenant_id, decision=cast(Any, SimpleNamespace(authorized=True)))


@pytest.fixture()
def database() -> Iterator[tuple[MongoClient, Any]]:
    """Yield a writable replica-set database or fail as an environment defect."""
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except (PyMongoError, OSError) as error:
        client.close()
        pytest.fail(f"ENVIRONMENT_DEFECT: Mongo runtime unavailable ({type(error).__name__})")
    if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary", hello.get("ismaster", False)) is not True:
        client.close()
        pytest.fail("ENVIRONMENT_DEFECT: writable expected replica-set primary unavailable")
    database = client[f"c1b_reasoning_http_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def _seed(database: Any, tenant_id: str) -> None:
    """Persist one active canonical WILSY_AI_REASONING entitlement."""
    ensure_entitlement_indexes(database[ENTITLEMENT_COLLECTION])
    ensure_admission_indexes(database[ADMISSION_COLLECTION])
    ensure_invocation_indexes(database[INVOCATION_COLLECTION])
    ensure_observation_indexes(database[OBSERVATION_COLLECTION])
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    entitlement = WilsyAIEntitlement(tenant_id=tenant_id, entitlement_id="entitlement-http", module_id="WILSY_AI_REASONING", module_name="Authenticated reasoning", tier=WilsyAITier.STARTER, policy_fingerprint=policy.policy_fingerprint, lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE, source_requirements=("source",), capability_grants=("reasoning",), source_readiness_evidence_reference="ready-http", source_readiness_evidence_fingerprint=EVIDENCE_FP)
    registry = WilsyAIEntitlementRegistry(database[ENTITLEMENT_COLLECTION])
    with database.client.start_session() as session:
        session.start_transaction()
        created = registry.create_or_replay(entitlement, idempotency_key="seed-http", session=session)
        registry.transition(tenant_id=tenant_id, entitlement_id=created.entitlement_id, target_state=WilsyAIEntitlementState.ACTIVE, expected_revision=0, evidence_reference="activate-http", evidence_fingerprint=EVIDENCE_FP, occurred_at=NOW, session=session)
        session.commit_transaction()


def _app(binding: ServerOwnedModelProviderBinding, tenant_id: str) -> FastAPI:
    app = FastAPI()
    app.state.wilsy_ai_reasoning_provider_binding = binding
    app.include_router(module.router, prefix="/api")
    app.dependency_overrides[module._REASONING_AUTH] = lambda: _context(tenant_id)
    return app


def _session(client: MongoClient) -> Any:
    """Start one caller-owned transaction for the router helper."""
    session = client.start_session()
    session.start_transaction()
    return session


def test_authenticated_reasoning_http_success_failure_and_replay(database: tuple[MongoClient, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    """Prove durable success/failure and one-call replay on real Mongo."""
    client, db = database
    tenant_id = f"tenant-http-{uuid4().hex}"
    _seed(db, tenant_id)
    monkeypatch.setattr(module, "_collections", lambda: {"entitlement": db[ENTITLEMENT_COLLECTION], "admission": db[ADMISSION_COLLECTION], "invocation": db[INVOCATION_COLLECTION], "observation": db[OBSERVATION_COLLECTION]})
    monkeypatch.setattr(module, "_start_session", lambda: _session(client))

    success_provider = Provider()
    success_binding = ServerOwnedModelProviderBinding.from_injected(provider=success_provider, provider_id="provider-http", model_id="model-http")
    with TestClient(_app(success_binding, tenant_id)) as http:
        first = http.post("/api/wilsy-ai/reasoning", json={"prompt": "bounded prompt"}, headers={"Idempotency-Key": "http-success"})
        replay = http.post("/api/wilsy-ai/reasoning", json={"prompt": "bounded prompt"}, headers={"Idempotency-Key": "http-success"})
    assert first.status_code == 200, first.text
    assert replay.status_code == 409, replay.text
    assert success_provider.calls == 1

    failure_provider = Provider(failure=True)
    failure_binding = ServerOwnedModelProviderBinding.from_injected(provider=failure_provider, provider_id="provider-http", model_id="model-http")
    with TestClient(_app(failure_binding, tenant_id)) as http:
        failure = http.post("/api/wilsy-ai/reasoning", json={"prompt": "bounded failure"}, headers={"Idempotency-Key": "http-failure"})
    assert failure.status_code == 503
    assert "provider detail" not in failure.text
    assert failure_provider.calls == 1



def test_read_only_project_context_real_source_and_denials(
    database: tuple[MongoClient, Any], monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify source registry, entitlement, names and stale denial without AI.

    IAM is explicitly injected, while Projects transaction/entitlement reads,
    project/name/participant/task registries and reasoning quota use real Mongo.
    No live database or real identity is touched and no model is invoked.
    """
    from datetime import date
    from tools.eos.api import projects_router as projects
    from tools.eos.saas.domain.project import Project, ProjectStatus
    from tools.eos.saas.domain.tenant_product_entitlement import create_tenant_product_entitlement
    from tools.eos.saas.entitlement import tenant_product_entitlement_registry as products

    client, db = database
    tenant = "tenant-context-replica"
    project_id = "prj-" + "e" * 48
    _seed(db, tenant)
    monkeypatch.setattr(projects.kernel_db, "get_client", lambda: client)
    monkeypatch.setattr(projects.kernel_db, "get_database", lambda: db)
    monkeypatch.setattr(module, "_database", lambda: db)
    monkeypatch.setattr(module, "_start_session", lambda: _session(client))
    monkeypatch.setattr(module, "_collections", lambda: {
        "entitlement": db[ENTITLEMENT_COLLECTION], "admission": db[ADMISSION_COLLECTION],
        "invocation": db[INVOCATION_COLLECTION], "observation": db[OBSERVATION_COLLECTION],
    })
    products.ensure_indexes(db[products.HISTORY_COLLECTION], db[products.CURRENT_COLLECTION])
    projects.ProjectRegistry.ensure_indexes(db[projects.PROJECT_COLLECTION], db[projects.PROJECT_EVENT_COLLECTION])
    projects.ProjectTaskRegistry.ensure_indexes(db[projects.PROJECT_TASK_COLLECTION], db[projects.PROJECT_TASK_EVENT_COLLECTION])
    projects.ProjectParticipantRegistry.ensure_indexes(db[projects.PROJECT_PARTICIPANT_COLLECTION], db[projects.PROJECT_PARTICIPANT_EVENT_COLLECTION])
    registry = projects.ProjectRegistry(db[projects.PROJECT_COLLECTION], db[projects.PROJECT_EVENT_COLLECTION])
    entitlement_id = projects.derive_tenant_product_entitlement_id(tenant, projects.TenantProductId.PROJECTS)
    entitlement = create_tenant_product_entitlement(
        tenant_id=tenant, entitlement_id=entitlement_id, product_id=projects.TenantProductId.PROJECTS,
        source_evidence_reference="synthetic-context-source", source_evidence_fingerprint="c" * 128,
    )
    with client.start_session() as session:
        session.start_transaction()
        products.create_or_replay(entitlement, db[products.HISTORY_COLLECTION], db[products.CURRENT_COLLECTION], session=session)
        products.transition(tenant_id=tenant, entitlement_id=entitlement_id,
            target_state="ACTIVE", expected_revision=0, evidence_reference="synthetic-activation",
            evidence_fingerprint="d" * 128, occurred_at=NOW,
            history_collection=db[products.HISTORY_COLLECTION], current_collection=db[products.CURRENT_COLLECTION], session=session)
        registry.create_or_replay(project=Project(
            tenant_id=tenant, project_id=project_id, name="Replica-backed contextual project", code="CONTEXT-CERT",
            summary=None, status=ProjectStatus.PLANNED, owner_principal_id=None, department_id=None,
            start_date=date(2026, 11, 20), target_date=None, source_type="internal", external_source_reference=None,
            created_by_principal_id="principal-http", created_at=NOW,
            updated_by_principal_id="principal-http", updated_at=NOW,
        ), actor_principal_id="principal-http", idempotency_key="context-create", occurred_at=NOW, session=session)
        session.commit_transaction()
    db["users"].insert_many([
        {"tenantId": tenant, "user_id": "principal-http", "firstName": "Verified", "lastName": "Person"},
        {"tenantId": "foreign-tenant", "user_id": "principal-http", "firstName": "Foreign", "lastName": "Secret"},
    ])
    ctx = TenantAuthorizationContext(identity=_context(tenant).identity, tenant_id=tenant,
        decision=cast(Any, SimpleNamespace(authorized=True, business_role="tenant_owner",
                                          authorization_role="PROJECTS_TENANT_OWNER")))
    provider = Provider()
    binding = ServerOwnedModelProviderBinding.from_injected(provider=provider)
    application = _app(binding, tenant)
    application.dependency_overrides[module._REASONING_AUTH] = lambda: ctx
    application.dependency_overrides[module.get_reasoning_project_authority] = lambda: ctx
    args = {"workspace": "PROJECTS", "project_id": project_id, "project_revision": 1}
    with TestClient(application) as http:
        good = http.get("/api/wilsy-ai/reasoning/context", params=args)
        assert good.status_code == 200, good.text
        assert good.json()["work"]["current_person_name"] == "Verified Person"
        assert "Foreign" not in good.text
        assert good.json()["work"]["project"]["name"] == "Replica-backed contextual project"
        assert good.json()["allowance"]["available_request_units"] == 35
        assert http.get("/api/wilsy-ai/reasoning/context", params={**args, "project_revision": 2}).status_code == 409
        assert http.get("/api/wilsy-ai/reasoning/context", params={**args, "project_id": "prj-" + "f" * 48}).status_code == 404
        with client.start_session() as session:
            session.start_transaction()
            products.transition(tenant_id=tenant, entitlement_id=entitlement_id,
                target_state="SUSPENDED", expected_revision=1, evidence_reference="synthetic-suspension",
                evidence_fingerprint="e" * 128, occurred_at=NOW,
                history_collection=db[products.HISTORY_COLLECTION], current_collection=db[products.CURRENT_COLLECTION], session=session)
            session.commit_transaction()
        assert http.get("/api/wilsy-ai/reasoning/context", params=args).status_code == 403
    assert provider.calls == 0
    assert db[ADMISSION_COLLECTION].count_documents({"tenant_id": tenant}) == 0
    assert db[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant}) == 0

# ARTIFACT: test_wilsy_ai_reasoning_http_real_mongo.py
# VERSION: v1.1.0-READ-ONLY-CONTEXT-REPLICA-CERT
# AUTHORITY BOUNDARY: real-Mongo HTTP certificate only
# TENANT POSTURE: Real-Mongo HTTP tests use isolated tenant-scoped evidence;
# cross-tenant authority is never inferred or granted.
# FAIL-CLOSED POSTURE: unavailable infrastructure fails certification
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
