"""C1B-R19 real-Mongo HTTP certificate.

TITLE: WILSY AI Authenticated Reasoning HTTP Real-Mongo Certificate
VERSION: v1.0.0-C1B-R19
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercise the authenticated reasoning command against canonical Mongo
         registries with deterministic success, failure, and replay evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_reasoning_http_real_mongo.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/api/wilsy_ai_reasoning_router.py
                            and the published C1B/P4/P5A/P6 authorities.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes the official C1B-R19 HTTP Mongo certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic data; no raw provider error
                             or prompt is written to Mongo.
TENANT BOUNDARY: Every canonical registry call is tenant-scoped.
AUTHORITY BOUNDARY: Reasoning evidence/admission only; no legal or financial truth.
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


# ARTIFACT: test_wilsy_ai_reasoning_http_real_mongo.py
# VERSION: v1.0.0-C1B-R19
# AUTHORITY BOUNDARY: real-Mongo HTTP certificate only
# FAIL-CLOSED POSTURE: unavailable infrastructure fails certification
# END OF WILSY OS SOVEREIGN ARTIFACT
