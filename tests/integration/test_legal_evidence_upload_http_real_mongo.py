"""Real-Mongo HTTP certificate for authenticated Legal Evidence upload.

TITLE: Legal Evidence Upload HTTP Real-Mongo Certificate
VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove HTTP multipart through current ProcessDocument resolution,
         capacity/write-intent transactions, deterministic provider-port
         execution and canonical two-plane Mongo commit.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_evidence_upload_http_real_mongo.py
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L10A4 establishes the host-backed certificate.
TENANT BOUNDARY: UUID-isolated database and exact tenant predicates.
PROVIDER BOUNDARY: Deterministic certified storage-port seam; no AWS claim.
FINANCIAL AUTHORITY BOUNDARY: No financial mutation; Kennel EOS exclusively.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
import hashlib
import os
import uuid
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
import pytest

from tools.eos.api import legal_evidence_upload_router as router_module
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.domain.legal_operations_lifecycle import ProcessDocument
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import COLLECTION as LIFECYCLE_COLLECTION, LegalOperationsLifecycleRegistry
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import LegalEvidenceBinaryChunkEvidence, LegalEvidenceBinaryObjectEvidence, LegalEvidenceBinaryWriteSession
from tools.eos.legal_operations.service.legal_evidence_upload_orchestrator import LegalEvidenceUploadOrchestrator
from tools.eos.saas.billing import plan_registry as plan_module
from tools.eos.saas.billing import subscription_registry as subscription_module
from tools.eos.saas.billing.legal_evidence_capacity_profile_resolver import CAPACITY_FEATURE_STARTER
from tools.eos.saas.billing.plan_registry import PlanRegistry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.tenant_product_entitlement import TenantProductEntitlementState, create_tenant_product_entitlement
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import derive_tenant_product_entitlement_id
from tools.eos.saas.entitlement import tenant_product_entitlement_registry as entitlement_module


URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
TENANT = "tenant-l10a4-upload-cert"
AT = datetime(2026, 10, 12, 8, 0, tzinfo=timezone.utc)


class _Storage:
    """Deterministic provider-port adapter used only by this certificate."""
    def __init__(self) -> None:
        self.data = bytearray()

    def begin(self, intent: Any) -> LegalEvidenceBinaryWriteSession:
        return LegalEvidenceBinaryWriteSession(provider_name="test-provider", write_session_reference="session-1", storage_reference="opaque-storage-1", write_intent_fingerprint=intent.fingerprint)

    def write_chunk(self, intent: Any, session: Any, *, sequence: int, chunk: bytes) -> LegalEvidenceBinaryChunkEvidence:
        self.data.extend(chunk)
        return LegalEvidenceBinaryChunkEvidence(sequence=sequence, chunk_length=len(chunk), provider_part_reference=f"part-{sequence}")

    def complete(self, intent: Any, session: Any, *, chunks: tuple[Any, ...], content_length: int, content_fingerprint: str) -> LegalEvidenceBinaryObjectEvidence:
        assert len(self.data) == content_length
        assert hashlib.sha3_512(bytes(self.data)).hexdigest() == content_fingerprint
        return LegalEvidenceBinaryObjectEvidence(provider_name="test-provider", storage_reference="opaque-storage-1", object_version_reference="version-1", provider_integrity_reference="integrity-1", write_intent_fingerprint=intent.fingerprint, content_length=content_length, content_fingerprint=content_fingerprint)

    def inspect(self, intent: Any, evidence: Any) -> Any:
        return evidence

    def abort(self, intent: Any, session: Any) -> None:
        self.data.clear()


@pytest.fixture(scope="module")
def certificate() -> Iterator[tuple[Any, TestClient]]:
    client: MongoClient[Any] = MongoClient(URI, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS"
    assert hello.get("isWritablePrimary") is True
    database_name = "wilsy_l10a4_" + uuid.uuid4().hex
    database = client[database_name]
    original_plans = plan_module.plans_collection
    original_subscriptions = subscription_module.subscriptions_collection
    plan_module.plans_collection = database.get_collection("plans")
    subscription_module.subscriptions_collection = database.get_collection("subscriptions")
    try:
        PlanRegistry._ensure_indexes()
        plan = PlanRegistry.create({
            "name": "Legal Evidence Certificate", "price": 1.0, "currency": "ZAR",
            "billingFrequency": "monthly", "planType": "PROFESSIONAL",
            "idempotencyKey": "l10a4-plan", "active": True,
            "features": ["legal.documents", CAPACITY_FEATURE_STARTER],
            "metadata": {"certificate": True}, "tags": ["l10a4"], "user": "L10A4-CERT",
        })
        SubscriptionRegistry.create({
            "tenantId": TENANT, "planId": plan["plan"].plan_id,
            "startDate": AT.isoformat(), "idempotencyKey": "l10a4-subscription",
            "billingMode": "PLATFORM", "onboardingRef": "L10A4", "sector": "LEGAL",
            "region": "ZA", "metadata": {"certificate": True},
        }, tenant_id_header=TENANT)

        history = database.get_collection(entitlement_module.HISTORY_COLLECTION)
        current = database.get_collection(entitlement_module.CURRENT_COLLECTION)
        entitlement_module.ensure_indexes(history, current)
        entitlement_id = derive_tenant_product_entitlement_id(TENANT, TenantProductId.LEGAL_OPERATIONS)
        pending = create_tenant_product_entitlement(
            tenant_id=TENANT, entitlement_id=entitlement_id,
            product_id=TenantProductId.LEGAL_OPERATIONS,
            source_evidence_reference="l10a4-subscription",
            source_evidence_fingerprint="a" * 128,
        )
        lifecycle = database.get_collection(LIFECYCLE_COLLECTION)
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        with client.start_session() as session:
            session.start_transaction()
            entitlement_module.create_or_replay(pending, history, current, session=session)
            entitlement_module.transition(
                tenant_id=TENANT, entitlement_id=entitlement_id,
                target_state=TenantProductEntitlementState.ACTIVE, expected_revision=0,
                evidence_reference="l10a4-activation", evidence_fingerprint="b" * 128,
                occurred_at=AT, history_collection=history, current_collection=current, session=session,
            )
            LegalOperationsLifecycleRegistry.create(
                ProcessDocument(
                    tenant_id=TENANT, document_id="document-1", case_matter_id="matter-1",
                    document_type="summons", registered_at=AT,
                    registration_evidence_reference="l10a4-registration",
                ), lifecycle, session=session,
            )
            session.commit_transaction()

        orchestrator = LegalEvidenceUploadOrchestrator(client=client, database=database, storage=_Storage())
        app = FastAPI()
        app.include_router(router_module.router, prefix="/api")
        identity = SovereignIdentity(
            identity_id="partner-1", tenant_id=TENANT, username=None, email=None,
            roles=["LEGAL_PARTNER"], auth_method="test", status=PrincipalStatus.ACTIVE,
        )
        context = TenantAuthorizationContext(identity=identity, tenant_id=TENANT, decision=object())  # type: ignore[arg-type]
        app.dependency_overrides[router_module._WRITE] = lambda: context
        app.dependency_overrides[router_module.get_legal_evidence_upload_orchestrator] = lambda: orchestrator
        yield database, TestClient(app)
    finally:
        plan_module.plans_collection = original_plans
        subscription_module.subscriptions_collection = original_subscriptions
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


def test_real_mongo_http_upload_commits_canonical_metadata(certificate: tuple[Any, TestClient]) -> None:
    database, http = certificate
    content = b"%PDF-1.7\nreal mongo legal evidence\n"
    response = http.post(
        "/api/legal-operations/evidence/documents/document-1",
        headers={"Idempotency-Key": "l10a4-upload-command"},
        files={"file": ("proof.pdf", content, "application/pdf")},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["state"] == "COMMITTED"
    assert payload["document_id"] == "document-1"
    assert payload["case_matter_id"] == "matter-1"
    assert payload["content_length"] == len(content)
    assert payload["content_fingerprint"] == hashlib.sha3_512(content).hexdigest()
    assert payload["uncertainty_id"] is None
    assert database["legal_evidence_binary_write_intents"].count_documents({"tenant_id": TENANT}) == 1
    assert database["legal_evidence_object_metadata"].count_documents({"tenant_id": TENANT}) == 1
    assert database["legal_evidence_capacity_reservations"].count_documents({"tenant_id": TENANT, "status": "CONSUMED"}) == 1
    assert database["legal_evidence_commit_uncertainties"].count_documents({"tenant_id": TENANT}) == 0


# ARTIFACT: test_legal_evidence_upload_http_real_mongo.py
# VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: actual Mongo plus deterministic provider-port certificate
# TENANT POSTURE: UUID-isolated database and exact tenant predicates
# FAIL-CLOSED POSTURE: topology, persistence, correlation or commit failure fails
# PROVIDER POSTURE: deterministic seam only; no AWS execution claim
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
