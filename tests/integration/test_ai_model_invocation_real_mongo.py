"""Creation-only C1A real-Mongo certificate artifact.

TITLE: WILSY AI Model Invocation Evidence Real-Mongo Certificate
VERSION: v1.0.0-WILSY-AI-MODEL-INVOCATION-REAL-MONGO
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves the dedicated model-invocation registry against the certified
         local replica set when a later host gate explicitly executes it.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_ai_model_invocation_real_mongo.py
COLLABORATION / OWNERSHIP: Certifies C1A domain and registry persistence;
                            no provider or external API is contacted.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes replica-set, index, tenant, session, transaction,
           replay, corruption, transport-boundary, and cleanup assertions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Local isolated database only; no prompt, provider,
                             secret, or network payload is sent.
TENANT BOUNDARY: Every registry operation and assertion is tenant-scoped.
AUTHORITY BOUNDARY: Durable model-compute evidence only; no legal or finance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Wrong replica set, non-writable primary, corruption,
                         divergence, or transaction drift fails the certificate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.intelligence.domain.ai_model_execution import (
    ModelExecutionInput,
    ModelInvocationEvidence,
    ModelProviderResult,
)
from tools.eos.intelligence.registry.ai_model_invocation_registry import (
    AIModelInvocationRegistry,
    AIModelInvocationRegistryConflictError,
    AIModelInvocationRegistryError,
    AIModelInvocationRegistryNotFoundError,
    COLLECTION,
    ensure_indexes,
)


DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE_TIME = datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc)


def make_evidence(*, tenant_id: str = "tenant-c1a", invocation_id: str = "invocation-1", response_text: str = "Bounded result.") -> ModelInvocationEvidence:
    """Compose one valid evidence record through the pure C1A contract."""
    request = ModelExecutionInput(
        tenant_id=tenant_id,
        principal_id="principal-1",
        invocation_id=invocation_id,
        correlation_id=f"correlation-{invocation_id}",
        entitlement_id="entitlement-1",
        provider_id="provider-neutral",
        model_id="model-neutral-v1",
        prompt="Bounded prompt.",
        system_policy="Bounded policy.",
        tool_invocation_evidence_references=("tool-evidence-1",),
    )
    result = ModelProviderResult(
        provider_id="provider-neutral",
        model_id="model-neutral-v1",
        response_text=response_text,
        provider_request_id=f"provider-request-{invocation_id}",
        input_tokens=2,
        output_tokens=2,
    )
    return ModelInvocationEvidence.from_execution(
        request,
        result,
        created_at=BASE_TIME,
        completed_at=BASE_TIME + timedelta(seconds=1),
    )


def test_model_invocation_registry_real_mongo_contract() -> None:
    """Exercise durable create, replay, isolation, transactions, and corruption."""
    uri = os.getenv("TEST_VENDOR_MONGO_URI", DEFAULT_URI)
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    database_name = f"c1a_model_invocation_{uuid.uuid4().hex}"
    database = client[database_name]
    collection = database[COLLECTION]
    session = None
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster", False)) is True
        registry = AIModelInvocationRegistry(collection)
        ensure_indexes(collection)
        index_names = {item["name"] for item in collection.list_indexes()}
        assert "wilsy_ai_model_invocation_tenant_identity_unique" in index_names

        evidence = make_evidence()
        session = client.start_session()
        with session.start_transaction():
            created = registry.create_or_replay(evidence, session=session)
            assert created == evidence
            assert registry.get(tenant_id=evidence.tenant_id, invocation_id=evidence.invocation_id, session=session) == evidence
        assert registry.get(tenant_id=evidence.tenant_id, invocation_id=evidence.invocation_id, session=session) == evidence

        with session.start_transaction():
            replay = registry.create_or_replay(evidence, session=session)
            assert replay == evidence
        divergent = make_evidence(response_text="Divergent bounded result.")
        with pytest.raises(AIModelInvocationRegistryConflictError, match="C1A_DIVERGENT_REPLAY"):
            registry.create_or_replay(divergent, session=session)
        with pytest.raises(AIModelInvocationRegistryNotFoundError):
            registry.get(tenant_id="tenant-other", invocation_id=evidence.invocation_id, session=session)

        aborted = make_evidence(invocation_id="aborted-invocation")
        session.start_transaction()
        registry.create_or_replay(aborted, session=session)
        session.abort_transaction()
        with pytest.raises(AIModelInvocationRegistryNotFoundError):
            registry.get(tenant_id=aborted.tenant_id, invocation_id=aborted.invocation_id, session=session)

        collection.update_one(
            {"tenant_id": evidence.tenant_id, "invocation_id": evidence.invocation_id},
            {"$set": {"unknown_persisted_field": "reject"}},
        )
        with pytest.raises(AIModelInvocationRegistryError, match="C1A_CORRUPT_EVIDENCE"):
            registry.get(tenant_id=evidence.tenant_id, invocation_id=evidence.invocation_id, session=session)
        collection.update_one(
            {"tenant_id": evidence.tenant_id, "invocation_id": evidence.invocation_id},
            {"$unset": {"unknown_persisted_field": ""}},
        )
        collection.update_one(
            {"tenant_id": evidence.tenant_id, "invocation_id": evidence.invocation_id},
            {"$set": {"fingerprint": "0" * 128}},
        )
        with pytest.raises(AIModelInvocationRegistryError, match="C1A_CORRUPT_EVIDENCE"):
            registry.get(tenant_id=evidence.tenant_id, invocation_id=evidence.invocation_id, session=session)
    finally:
        if session is not None:
            session.end_session()
        client.drop_database(database_name)
        client.close()


# ARTIFACT: test_ai_model_invocation_real_mongo.py
# VERSION: v1.0.0-WILSY-AI-MODEL-INVOCATION-REAL-MONGO
# AUTHORITY BOUNDARY: host certification artifact only
# TENANT POSTURE: exact tenant predicates and isolation assertions
# FAIL-CLOSED POSTURE: wrong host, corruption, and divergence fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
