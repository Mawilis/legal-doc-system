"""R23 real-Mongo certificate for the concrete OpenAI adapter seam.

TITLE: WILSY AI OpenAI Adapter Real-Mongo Certificate
VERSION: v1.0.0-C1B-R23
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercise the real entitlement, capacity, admission, invocation, and
         usage registries through the authenticated route with a deterministic
         SDK double and no external provider network.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_reasoning_openai_adapter_real_mongo.py
COLLABORATION / OWNERSHIP: Certifies the concrete adapter with the published
                            C1B HTTP composition and canonical Mongo authorities.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R23 establishes success, failure accounting, held
           capacity, replay, and exact usage persistence against real Mongo.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant data and SDK doubles only; no key
                             or provider network is used.
TENANT BOUNDARY: All registry reads and writes use the seeded tenant identity.
AUTHORITY BOUNDARY: Reasoning compute/admission evidence only; no legal or money truth.
FAIL-CLOSED DECLARATION: Mongo unavailability fails as an environment defect.
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
from tools.eos.intelligence.domain.ai_model_execution import ModelExecutionOutcome
from tools.eos.intelligence.domain.ai_model_provider_binding import (
    AIModelProviderBinding,
    ServerOwnedModelProviderBinding,
)
from tools.eos.intelligence.providers.openai_responses_provider import OpenAIResponsesProvider
from tools.eos.intelligence.registry.ai_model_invocation_registry import (
    COLLECTION as INVOCATION_COLLECTION,
    ensure_indexes as ensure_invocation_indexes,
)
from tools.eos.saas.billing.wilsy_ai_commercial_policy import WilsyAITier, get_wilsy_ai_commercial_policy
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    COLLECTION as ENTITLEMENT_COLLECTION,
    WilsyAIEntitlementRegistry,
    ensure_indexes as ensure_entitlement_indexes,
)
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import (
    COLLECTION as ADMISSION_COLLECTION,
    ensure_indexes as ensure_admission_indexes,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    COLLECTION as OBSERVATION_COLLECTION,
    ensure_indexes as ensure_observation_indexes,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import WilsyAIEntitlement, WilsyAIEntitlementState


URI = os.getenv("TEST_WILSY_AI_REASONING_MONGO_URI", os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"))
REPLICA_SET = os.getenv("TEST_WILSY_AI_REASONING_REPLICA_SET", "wilsyVendorCertRS")
NOW = datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc)
EVIDENCE_FP = "a" * 128


class FakeResponses:
    """Deterministic SDK Responses surface; it never opens a network socket."""

    def __init__(self, failure: bool = False) -> None:
        self.failure = failure
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self.failure:
            raise TimeoutError("provider detail must not escape")
        return SimpleNamespace(
            id="resp-r23-mongo",
            output_text="bounded Mongo response",
            usage=SimpleNamespace(input_tokens=5, output_tokens=4),
        )


class FakeClient:
    """SDK-shaped injected client used by OpenAIResponsesProvider."""

    def __init__(self, responses: FakeResponses) -> None:
        self.responses = responses


def _context(tenant_id: str) -> TenantAuthorizationContext:
    """Build an authorized context with server-owned principal identity."""
    return TenantAuthorizationContext(
        identity=cast(Any, SimpleNamespace(identity_id="principal-r23")),
        tenant_id=tenant_id,
        decision=cast(Any, SimpleNamespace(authorized=True)),
    )


@pytest.fixture()
def database() -> Iterator[tuple[MongoClient, Any]]:
    """Yield a writable replica-set database or fail closed as environment defect."""
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except (PyMongoError, OSError) as error:
        client.close()
        pytest.fail(f"ENVIRONMENT_DEFECT: Mongo runtime unavailable ({type(error).__name__})")
    if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary", hello.get("ismaster", False)) is not True:
        client.close()
        pytest.fail("ENVIRONMENT_DEFECT: writable expected replica-set primary unavailable")
    database = client[f"c1b_r23_openai_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


def _seed(database: Any, tenant_id: str) -> None:
    """Persist one active canonical reasoning entitlement."""
    ensure_entitlement_indexes(database[ENTITLEMENT_COLLECTION])
    ensure_admission_indexes(database[ADMISSION_COLLECTION])
    ensure_invocation_indexes(database[INVOCATION_COLLECTION])
    ensure_observation_indexes(database[OBSERVATION_COLLECTION])
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    entitlement = WilsyAIEntitlement(
        tenant_id=tenant_id,
        entitlement_id="entitlement-r23",
        module_id="WILSY_AI_REASONING",
        module_name="Authenticated reasoning",
        tier=WilsyAITier.STARTER,
        policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE,
        source_requirements=("source",),
        capability_grants=("reasoning",),
        source_readiness_evidence_reference="ready-r23",
        source_readiness_evidence_fingerprint=EVIDENCE_FP,
    )
    registry = WilsyAIEntitlementRegistry(database[ENTITLEMENT_COLLECTION])
    with database.client.start_session() as session:
        session.start_transaction()
        created = registry.create_or_replay(entitlement, idempotency_key="seed-r23", session=session)
        registry.transition(
            tenant_id=tenant_id,
            entitlement_id=created.entitlement_id,
            target_state=WilsyAIEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activate-r23",
            evidence_fingerprint=EVIDENCE_FP,
            occurred_at=NOW,
            session=session,
        )
        session.commit_transaction()


def _app(binding: ServerOwnedModelProviderBinding, tenant_id: str) -> FastAPI:
    """Compose the real router with an injected server-owned adapter binding."""
    app = FastAPI()
    app.state.wilsy_ai_reasoning_provider_binding = binding
    app.include_router(module.router, prefix="/api")
    app.dependency_overrides[module._REASONING_AUTH] = lambda: _context(tenant_id)
    return app


def _session(client: MongoClient) -> Any:
    """Start one caller transaction for the router's bounded helper."""
    session = client.start_session()
    session.start_transaction()
    return session


def test_real_mongo_openai_adapter_success_failure_and_replay(database: tuple[MongoClient, Any], monkeypatch: pytest.MonkeyPatch) -> None:
    """Prove real durable chain, exact usage, reconciliation, and no replay call."""
    client, db = database
    tenant_id = f"tenant-r23-{uuid4().hex}"
    _seed(db, tenant_id)
    monkeypatch.setattr(module, "_collections", lambda: {"entitlement": db[ENTITLEMENT_COLLECTION], "admission": db[ADMISSION_COLLECTION], "invocation": db[INVOCATION_COLLECTION], "observation": db[OBSERVATION_COLLECTION]})
    monkeypatch.setattr(module, "_start_session", lambda: _session(client))

    success_responses = FakeResponses()
    success_provider = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(success_responses))
    success_binding = ServerOwnedModelProviderBinding(AIModelProviderBinding(provider_id="openai", model_id="gpt-5-mini", provider=success_provider))
    with TestClient(_app(success_binding, tenant_id)) as http:
        first = http.post("/api/wilsy-ai/reasoning", json={"prompt": "bounded success"}, headers={"Idempotency-Key": "r23-success"})
        replay = http.post("/api/wilsy-ai/reasoning", json={"prompt": "bounded success"}, headers={"Idempotency-Key": "r23-success"})
    assert first.status_code == 200, first.text
    assert replay.status_code == 409, replay.text
    assert len(success_responses.calls) == 1
    assert success_responses.calls[0]["store"] is False
    assert success_responses.calls[0]["tools"] == []
    assert db[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant_id, "outcome": ModelExecutionOutcome.SUCCESS.value}) == 1
    assert db[OBSERVATION_COLLECTION].count_documents({"tenant_id": tenant_id}) == 1
    assert db[ADMISSION_COLLECTION].count_documents({"tenant_id": tenant_id, "state": "COMPLETED"}) == 1

    failure_responses = FakeResponses(failure=True)
    failure_provider = OpenAIResponsesProvider(model_id="gpt-5-mini", client=FakeClient(failure_responses))
    failure_binding = ServerOwnedModelProviderBinding(AIModelProviderBinding(provider_id="openai", model_id="gpt-5-mini", provider=failure_provider))
    with TestClient(_app(failure_binding, tenant_id)) as http:
        failure = http.post("/api/wilsy-ai/reasoning", json={"prompt": "bounded failure"}, headers={"Idempotency-Key": "r23-failure"})
    assert failure.status_code == 503
    assert "provider detail" not in failure.text
    assert len(failure_responses.calls) == 1
    assert db[INVOCATION_COLLECTION].count_documents({"tenant_id": tenant_id, "outcome": ModelExecutionOutcome.PROVIDER_TIMEOUT.value}) == 1
    assert db[OBSERVATION_COLLECTION].count_documents({"tenant_id": tenant_id, "usage_observation_id": {"$regex": "r23-failure"}}) == 0
    assert db[ADMISSION_COLLECTION].count_documents({"tenant_id": tenant_id, "state": "RECONCILIATION_REQUIRED"}) == 1


# ARTIFACT: test_wilsy_ai_reasoning_openai_adapter_real_mongo.py
# VERSION: v1.0.0-C1B-R23
# AUTHORITY BOUNDARY: concrete adapter real-Mongo certificate only
# TENANT POSTURE: all assertions are tenant-scoped
# FAIL-CLOSED POSTURE: unavailable Mongo is an environment defect
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
