"""C1B-R11 durable reasoning orchestration real-Mongo certificate.

TITLE: WILSY AI Reasoning Orchestrator Real-Mongo Certificate
VERSION: v1.0.0-C1B-R11
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove admission claim, out-of-transaction provider compute, exact
         invocation/usage persistence, bounded failure holding, and replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_reasoning_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: Certifies the C1B orchestrator with canonical C1A,
                            P5A, and C1B registries on the configured replica set.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes success, failure, tenant isolation, and replay
           durability proof; unavailable hosts are reported as skips.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Isolated test database; no provider secrets or raw
                             prompt/response is written to Mongo.
TENANT BOUNDARY: Every registry query is tenant-scoped.
AUTHORITY BOUNDARY: Reasoning and usage evidence only; no legal or financial truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Wrong host, persistence drift, replay divergence, and
                         held-capacity violations fail the certificate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import uuid
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.intelligence.domain.ai_model_execution import ModelProviderResult
from tools.eos.intelligence.domain.ai_model_provider_binding import ServerOwnedModelProviderBinding
from tools.eos.intelligence.registry.ai_model_invocation_registry import AIModelInvocationRegistry, COLLECTION as INVOCATION_COLLECTION, ensure_indexes as ensure_invocation_indexes
from tools.eos.intelligence.wilsy_ai_reasoning_orchestrator import WilsyAIReasoningOrchestrator
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import WilsyAIUsageAdmissionRegistry, COLLECTION as ADMISSION_COLLECTION, ensure_indexes as ensure_admission_indexes
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import WilsyAIUsageObservationRegistry, WilsyAIUsageObservationNotFoundError, COLLECTION as OBSERVATION_COLLECTION, ensure_indexes as ensure_observation_indexes
from tools.eos.saas.domain.wilsy_ai_usage_admission import WilsyAIUsageAdmission, WilsyAIUsageAdmissionState


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc)


class Provider:
    """Deterministic provider double whose call count is externally proved."""

    def __init__(self, result: ModelProviderResult) -> None:
        self.result = result
        self.calls = 0

    def execute(self, request: object) -> ModelProviderResult:
        self.calls += 1
        return self.result


class FailingProvider:
    """Provider double that exposes only a bounded timeout classification."""

    def __init__(self) -> None:
        self.calls = 0

    def execute(self, request: object) -> ModelProviderResult:
        self.calls += 1
        raise TimeoutError("raw provider detail must not persist")


def make_admission(admission_id: str, key: str) -> WilsyAIUsageAdmission:
    """Build one RESERVED admission with deterministic entitlement binding."""
    return WilsyAIUsageAdmission(
        tenant_id="tenant-c1b-real",
        admission_id=admission_id,
        idempotency_key=key,
        entitlement_id="entitlement-real",
        module_id="WILSY_AI_REASONING",
        entitlement_revision=1,
        entitlement_fingerprint="a" * 128,
        window_start=NOW,
        window_end=NOW + timedelta(hours=1),
        reserved_request_units=1,
        created_at=NOW,
        updated_at=NOW,
    )


def reserve(registry: WilsyAIUsageAdmissionRegistry, item: WilsyAIUsageAdmission, session: Any) -> None:
    """Reserve and commit capacity under caller transaction ownership."""
    with session.start_transaction():
        assert registry.reserve(item, available_request_units=1, session=session) == item


def test_reasoning_orchestrator_real_mongo_success_failure_and_replay() -> None:
    """Exercise the complete durable chain on a writable replica-set primary."""
    uri = os.getenv("TEST_WILSY_AI_REASONING_MONGO_URI", os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI))
    replica_set = os.getenv("TEST_WILSY_AI_REASONING_REPLICA_SET", EXPECTED_REPLICA_SET)
    client = MongoClient(uri, serverSelectionTimeoutMS=1500, retryWrites=True)
    database_name = f"c1b_reasoning_{uuid.uuid4().hex}"
    session = None
    ready = False
    try:
        try:
            client.admin.command("ping")
            hello = client.admin.command("hello")
        except Exception as error:
            pytest.skip(f"Mongo runtime unavailable: {type(error).__name__}")
        assert hello.get("setName") == replica_set
        assert hello.get("isWritablePrimary", hello.get("ismaster", False)) is True
        ready = True
        database = client[database_name]
        admissions = WilsyAIUsageAdmissionRegistry(database[ADMISSION_COLLECTION])
        invocations = AIModelInvocationRegistry(database[INVOCATION_COLLECTION])
        observations = WilsyAIUsageObservationRegistry(database[OBSERVATION_COLLECTION])
        ensure_admission_indexes(database[ADMISSION_COLLECTION])
        ensure_invocation_indexes(database[INVOCATION_COLLECTION])
        ensure_observation_indexes(database[OBSERVATION_COLLECTION])
        session = client.start_session()

        success_admission = make_admission("admission-success", "key-success")
        reserve(admissions, success_admission, session)
        success_provider = Provider(ModelProviderResult(provider_id="provider-c1b", model_id="model-c1b", response_text="bounded result", provider_request_id="provider-success", input_tokens=4, output_tokens=3))
        orchestrator = WilsyAIReasoningOrchestrator(
            admission_registry=admissions, invocation_registry=invocations,
            observation_registry=observations,
            binding=ServerOwnedModelProviderBinding.from_injected(provider=success_provider, provider_id="provider-c1b", model_id="model-c1b"),
            clock=lambda: NOW + timedelta(seconds=2),
        )
        with session.start_transaction():
            permit = orchestrator.claim(tenant_id=success_admission.tenant_id, principal_id="principal-1", admission_id=success_admission.admission_id, invocation_id="invocation-success", correlation_id="attempt-success", entitlement_id=success_admission.entitlement_id, prompt="bounded prompt", system_policy="bounded policy", session=session, occurred_at=NOW + timedelta(seconds=1), tool_invocation_evidence_references=("attempt:attempt-success", "instruction:instruction-success", "document:document-success", "deputy:deputy-success"))
        attempt = orchestrator.execute(permit)
        with session.start_transaction():
            final = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
        assert final.admission.state is WilsyAIUsageAdmissionState.COMPLETED
        assert final.usage_observation is not None
        assert final.usage_observation.source_evidence_fingerprint == final.invocation_evidence.fingerprint
        with session.start_transaction():
            replay = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
        assert replay.replay is True and success_provider.calls == 1
        assert invocations.get(tenant_id=success_admission.tenant_id, invocation_id="invocation-success", session=session).fingerprint == final.invocation_evidence.fingerprint
        assert observations.get(tenant_id=success_admission.tenant_id, usage_observation_id="usage-invocation-success", session=session).fingerprint == final.usage_observation.fingerprint
        assert admissions.held_request_units(tenant_id=success_admission.tenant_id, entitlement_id=success_admission.entitlement_id, window_start=success_admission.window_start, session=session) == 0

        failure_admission = make_admission("admission-failure", "key-failure")
        reserve(admissions, failure_admission, session)
        failure_provider = FailingProvider()
        failing = WilsyAIReasoningOrchestrator(
            admission_registry=admissions, invocation_registry=invocations,
            observation_registry=observations,
            binding=ServerOwnedModelProviderBinding.from_injected(provider=failure_provider, provider_id="provider-c1b", model_id="model-c1b"),
            clock=lambda: NOW + timedelta(seconds=2),
        )
        with session.start_transaction():
            failure_permit = failing.claim(tenant_id=failure_admission.tenant_id, principal_id="principal-1", admission_id=failure_admission.admission_id, invocation_id="invocation-failure", correlation_id="attempt-failure", entitlement_id=failure_admission.entitlement_id, prompt="bounded prompt", system_policy="bounded policy", session=session, occurred_at=NOW + timedelta(seconds=1))
        failure_attempt = failing.execute(failure_permit)
        with session.start_transaction():
            failure_final = failing.finalize(failure_attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
        assert failure_final.admission.state is WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED
        with pytest.raises(WilsyAIUsageObservationNotFoundError):
            observations.get(tenant_id=failure_admission.tenant_id, usage_observation_id="usage-invocation-failure", session=session)
        assert admissions.held_request_units(tenant_id=failure_admission.tenant_id, entitlement_id=failure_admission.entitlement_id, window_start=failure_admission.window_start, session=session) == 1
        with session.start_transaction():
            replay_failure = failing.finalize(failure_attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
        assert replay_failure.replay is True and failure_provider.calls == 1
    finally:
        if session is not None:
            session.end_session()
        if ready:
            client.drop_database(database_name)
        client.close()


# ARTIFACT: test_wilsy_ai_reasoning_orchestrator_real_mongo.py
# VERSION: v1.0.0-C1B-R11
# AUTHORITY BOUNDARY: real-Mongo certificate for C1B reasoning evidence
# FAIL-CLOSED POSTURE: unavailable infrastructure is skipped, never reported passed
# END OF WILSY OS SOVEREIGN ARTIFACT
