"""Host-backed M13-P6D certificate for the WILSY AI capacity HTTP seam.

TITLE: WILSY AI Usage-Capacity HTTP Real-Mongo Certificate
VERSION: v1.0.0-M13-P6D-WILSY-AI-CAPACITY-HTTP-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify the production FastAPI capacity route against a writable
         replica set using canonical P4/P5B/P6B/P6C/P6A authorities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_usage_capacity_http_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for billing_router.py; P4 owns
                            entitlement truth, P5B/P6B own usage evidence,
                            P6A owns capacity derivation, and Kennel EOS owns
                            financial execution and settlement.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.0.0-M13-P6D certifies real-Mongo authorized capacity retrieval,
           deterministic replay, tenant isolation, corruption rejection, and
           production transaction composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic data only; no providers,
                             secrets, KMS, customer records, or payments.
TENANT BOUNDARY: Authorization context is the sole route tenant source; all
                 registry operations remain explicitly tenant-scoped.
AUTHORITY BOUNDARY: Host-backed HTTP composition evidence only; no new
                    entitlement, usage, quota, commercial, or financial truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Unavailable hosts skip before execution; all seeded
                         domain corruption and cross-tenant requests fail closed.
"""
from __future__ import annotations

import importlib
import os
import sys
import types
from datetime import datetime, timezone
from typing import Any, Iterator, cast
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.saas.billing.wilsy_ai_commercial_policy import (
    WilsyAITier,
    get_wilsy_ai_commercial_policy,
)
from tools.eos.saas.billing.wilsy_ai_entitlement_registry import (
    COLLECTION as ENTITLEMENT_COLLECTION,
    WilsyAIEntitlementRegistry,
    ensure_indexes as ensure_entitlement_indexes,
)
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    COLLECTION as OBSERVATION_COLLECTION,
    WilsyAIUsageObservationRegistry,
    ensure_indexes as ensure_observation_indexes,
)
from tools.eos.saas.domain.wilsy_ai_entitlement import (
    WilsyAIEntitlement,
    WilsyAIEntitlementState,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.billing.wilsy_ai_usage_capacity import WilsyAIUsageCapacity
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext


URI = os.environ.get(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_SET_NAME = "wilsyVendorCertRS"
AS_OF = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
ACTIVATED_AT = datetime(2026, 9, 1, 0, 0, tzinfo=timezone.utc)
EVIDENCE_FP = "a" * 128
TENANT_A = "tenant-p6d-real-a"
TENANT_B = "tenant-p6d-real-b"


def _pending(tenant_id: str, entitlement_id: str, module_id: str) -> WilsyAIEntitlement:
    """Build one canonical pending entitlement for synthetic host evidence."""
    policy = get_wilsy_ai_commercial_policy(WilsyAITier.STARTER)
    return WilsyAIEntitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        module_id=module_id,
        module_name="Owner Inbox",
        tier=WilsyAITier.STARTER,
        policy_fingerprint=policy.policy_fingerprint,
        lifecycle_state=WilsyAIEntitlementState.PENDING_SOURCE,
        source_requirements=("records",),
        capability_grants=("ai.summary",),
        source_readiness_evidence_reference=f"ready-{tenant_id}",
        source_readiness_evidence_fingerprint=EVIDENCE_FP,
    )


def _observation(
    entitlement: WilsyAIEntitlement,
    usage_id: str,
    request_units: int = 7,
    automation_actions: int = 4,
) -> WilsyAIUsageObservation:
    """Build one P5A observation bound to the canonical active entitlement."""
    return WilsyAIUsageObservation(
        tenant_id=entitlement.tenant_id,
        usage_observation_id=usage_id,
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=entitlement.lifecycle_revision,
        entitlement_fingerprint=entitlement.fingerprint,
        module_id=entitlement.module_id,
        request_units=request_units,
        input_tokens=10,
        output_tokens=20,
        automation_actions=automation_actions,
        occurred_at=datetime(2026, 9, 13, 11, 0, tzinfo=timezone.utc),
        source_evidence_reference=f"source-{usage_id}",
        source_evidence_fingerprint=EVIDENCE_FP,
    )


def _authorized_context(tenant_id: str) -> TenantAuthorizationContext:
    """Create synthetic authorization context without replacing production auth."""
    identity = types.SimpleNamespace(identity_id=f"principal-{tenant_id}")
    decision = types.SimpleNamespace(authorized=True)
    return TenantAuthorizationContext(
        identity=cast(Any, identity),
        tenant_id=tenant_id,
        decision=cast(Any, decision),
    )


@pytest.fixture()
def mongo_database() -> Iterator[tuple[MongoClient, Any]]:
    """Yield a UUID-isolated writable replica-set database or skip preflight."""
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True)
    try:
        hello = client.admin.command("hello")
    except (PyMongoError, OSError) as error:
        client.close()
        pytest.skip(f"M13_P6D_HOST_RUNTIME unavailable: {type(error).__name__}")
    if hello.get("setName") != EXPECTED_SET_NAME:
        client.close()
        pytest.skip(
            f"M13_P6D_HOST_RUNTIME replica-set mismatch: {hello.get('setName')!r}"
        )
    if hello.get("isWritablePrimary", hello.get("ismaster", False)) is not True:
        client.close()
        pytest.skip("M13_P6D_HOST_RUNTIME writable primary unavailable")
    database = client[f"wilsy_ai_p6d_http_real_{uuid4().hex}"]
    try:
        yield client, database
    finally:
        client.drop_database(database.name)
        client.close()


@pytest.fixture()
def production_router(monkeypatch: Any) -> Iterator[Any]:
    """Import the real router while isolating its unrelated legacy registry."""
    registry_name = "tools.eos.saas.billing.billing_registry"
    router_name = "tools.eos.api.billing_router"
    previous_registry = sys.modules.get(registry_name)
    previous_router = sys.modules.pop(router_name, None)
    stub = types.ModuleType(registry_name)
    setattr(stub, "BillingRegistry", type("BillingRegistry", (), {}))
    setattr(stub, "get_billing_registry", lambda: object())
    setattr(stub, "db", None)
    setattr(stub, "client", None)
    sys.modules[registry_name] = stub
    try:
        module = importlib.import_module(router_name)
        yield module
    finally:
        sys.modules.pop(router_name, None)
        if previous_router is not None:
            sys.modules[router_name] = previous_router
        if previous_registry is not None:
            sys.modules[registry_name] = previous_registry
        else:
            sys.modules.pop(registry_name, None)


def _seed(database: Any) -> tuple[WilsyAIEntitlement, WilsyAIEntitlement, WilsyAIEntitlement]:
    """Persist two active entitlements and one active no-evidence entitlement."""
    entitlement_collection = database[ENTITLEMENT_COLLECTION]
    observation_collection = database[OBSERVATION_COLLECTION]
    ensure_entitlement_indexes(entitlement_collection)
    ensure_observation_indexes(observation_collection)
    entitlement_registry = WilsyAIEntitlementRegistry(entitlement_collection)
    observation_registry = WilsyAIUsageObservationRegistry(observation_collection)
    pending_a = _pending(TENANT_A, "entitlement-p6d-a", "module-p6d-a")
    pending_b = _pending(TENANT_B, "entitlement-p6d-b", "module-p6d-b")
    pending_empty = _pending(TENANT_A, "entitlement-p6d-empty", "module-p6d-empty")
    with database.client.start_session() as session:
        session.start_transaction()
        active_a = entitlement_registry.create_or_replay(
            pending_a, idempotency_key="idem-p6d-a", session=session
        )
        active_a = entitlement_registry.transition(
            tenant_id=TENANT_A,
            entitlement_id=active_a.entitlement_id,
            target_state=WilsyAIEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activation-p6d-a",
            evidence_fingerprint=EVIDENCE_FP,
            occurred_at=ACTIVATED_AT,
            session=session,
        )
        active_b = entitlement_registry.create_or_replay(
            pending_b, idempotency_key="idem-p6d-b", session=session
        )
        active_b = entitlement_registry.transition(
            tenant_id=TENANT_B,
            entitlement_id=active_b.entitlement_id,
            target_state=WilsyAIEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activation-p6d-b",
            evidence_fingerprint=EVIDENCE_FP,
            occurred_at=ACTIVATED_AT,
            session=session,
        )
        active_empty = entitlement_registry.create_or_replay(
            pending_empty, idempotency_key="idem-p6d-empty", session=session
        )
        active_empty = entitlement_registry.transition(
            tenant_id=TENANT_A,
            entitlement_id=active_empty.entitlement_id,
            target_state=WilsyAIEntitlementState.ACTIVE,
            expected_revision=0,
            evidence_reference="activation-p6d-empty",
            evidence_fingerprint=EVIDENCE_FP,
            occurred_at=ACTIVATED_AT,
            session=session,
        )
        observation_registry.create_or_replay(
            _observation(active_a, "usage-p6d-a"),
            idempotency_key="usage-idem-p6d-a",
            session=session,
        )
        session.commit_transaction()
    return active_a, active_b, active_empty


def _app(module: Any, context: TenantAuthorizationContext) -> FastAPI:
    """Mount the unchanged production router and override only its auth seam."""
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module._WILSY_AI_CAPACITY_READ_AUTHORIZATION] = (
        lambda: context
    )
    return app


def test_real_mongo_production_capacity_route_and_fail_closed_boundaries(
    mongo_database: tuple[MongoClient, Any],
    production_router: Any,
    monkeypatch: Any,
) -> None:
    """Prove end-to-end P4/P6B/P6A retrieval and HTTP isolation/corruption."""
    client, database = mongo_database
    active_a, active_b, active_empty = _seed(database)
    module = production_router
    monkeypatch.setattr(module, "_require_db", lambda: database)
    monkeypatch.setattr(module, "_require_mongo_client", lambda: client)
    app = _app(module, _authorized_context(TENANT_A))
    path = "/billing/wilsy-ai/usage-capacity/evidence"
    query = {"entitlement_id": active_a.entitlement_id, "as_of": "2026-09-13T12:00:00+00:00"}

    with TestClient(app) as http:
        first_response = http.get(path, params=query)
        assert first_response.status_code == 200, first_response.text
        first_payload = first_response.json()
        second_response = http.get(path, params=query)
        assert second_response.status_code == 200
        assert second_response.json() == first_payload

        assert first_payload == WilsyAIUsageCapacity.from_dict(first_payload).to_dict()
        assert first_payload["tenant_id"] == TENANT_A
        assert first_payload["entitlement_id"] == active_a.entitlement_id
        assert first_payload["module_id"] == active_a.module_id
        assert first_payload["entitlement_revision"] == active_a.lifecycle_revision
        assert first_payload["entitlement_fingerprint"] == active_a.fingerprint
        assert first_payload["daily_consumed_request_units"] == 7
        assert first_payload["monthly_consumed_automation_actions"] == 4

        cross_tenant = http.get(
            path,
            params={"entitlement_id": active_b.entitlement_id, "as_of": query["as_of"]},
        )
        assert cross_tenant.status_code == 404
        assert active_b.entitlement_id not in cross_tenant.text

        missing = http.get(
            path,
            params={"entitlement_id": "entitlement-p6d-missing", "as_of": query["as_of"]},
        )
        assert missing.status_code == 404

        no_evidence = http.get(
            path,
            params={"entitlement_id": active_empty.entitlement_id, "as_of": query["as_of"]},
        )
        assert no_evidence.status_code == 409
        assert "0" not in no_evidence.text

    observation_collection = database[OBSERVATION_COLLECTION]
    row = observation_collection.find_one(
        {"tenant_id": TENANT_A, "usage_observation_id": "usage-p6d-a"}
    )
    assert row is not None
    observation_collection.update_one(
        {"_id": row["_id"]}, {"$set": {"request_units": 8}}
    )
    with TestClient(app) as http:
        corrupt = http.get(path, params=query)
    assert corrupt.status_code == 409
    assert "unavailable" not in corrupt.text.lower()


# ARTIFACT: test_wilsy_ai_usage_capacity_http_real_mongo.py
# VERSION: v1.0.0-M13-P6D-WILSY-AI-CAPACITY-HTTP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: host-backed P6D HTTP composition evidence only
# TENANT POSTURE: authorization context supplies explicit own-tenant scope
# FAIL-CLOSED POSTURE: host absence skips preflight; domain corruption never succeeds
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
