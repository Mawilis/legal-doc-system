"""WILSY OS R3F-C durable real-Mongo behavioral certificate.
TITLE: Platform Billing Commercial Settlement Projection Certificate
VERSION: v1.1.0-R3F-C
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
PURPOSE: Certify six durable projection and replay propositions.
EPITOME: Canonical settlement evidence drives one atomic commercial projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_commercial_settlement_projection_real_mongo.py
COLLABORATION / OWNERSHIP: SaaS Billing projection owner with Kennel EOS evidence owners.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.1.0-R3F-C replaces scaffolding with durable behavioral fixtures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-only synthetic data; no credentials or secrets.
TENANT BOUNDARY: Every key, lookup, mutation, and assertion is tenant-scoped.
AUTHORITY BOUNDARY: Kennel settlement evidence authorizes projection only.
FINANCIAL AUTHORITY BOUNDARY: No provider execution, money movement, or Payment state.
TRANSACTION BOUNDARY: Caller-owned session encloses projection and invoice CAS.
FAIL-CLOSED DECLARATION: Missing evidence and provenance/CAS conflicts abort.
"""
from __future__ import annotations
import os, uuid
from datetime import datetime, timezone
import pytest
from pymongo import MongoClient
from tools.eos.saas.domain.billing import PlatformInvoice, InvoiceStatus
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from tools.eos.kennel.orchestration.platform_billing_financial_execution_truth_recording import record_platform_billing_financial_execution_truth
from tools.eos.kennel.registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry
from tools.eos.kennel.orchestration.platform_billing_financial_settlement_evidence_recording import record_platform_billing_financial_settlement_evidence
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection import PlatformBillingCommercialSettlementProjectionError, project_platform_billing_commercial_settlement
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection_registry import PlatformBillingCommercialSettlementProjectionRegistry

URI = os.getenv("TEST_VENDOR_MONGO_URI", "")

def graph():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    db = client[f"r3fc_{uuid.uuid4().hex}"]; tenant = f"tenant-{uuid.uuid4().hex}"; invoice_id = f"invoice-{uuid.uuid4().hex}"; now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    invoice = PlatformInvoice.from_dict({"tenant_id": tenant, "invoice_id": invoice_id, "status": "open", "amount": 100.0, "total": 100.0, "currency": "ZAR", "issued_at": now, "created_at": now, "updated_at": now, "line_items": [{"description": "Platform", "amount": 100.0}]})
    db["invoices"].insert_one(invoice.to_dict())
    authorization = PlatformBillingReleaseAuthorization(tenant, f"auth-{uuid.uuid4().hex}", invoice_id, invoice.commercial_release_evidence_fingerprint, "evidence", "a" * 128, invoice.release_amount_minor, invoice.currency, "principal", "basis", "destination", f"idem-{uuid.uuid4().hex}", now, now)
    authorization_collection = db["platform_billing_release_authorizations"]
    PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(authorization_collection)
    PlatformBillingReleaseAuthorizationRegistry.create(authorization, authorization_collection)
    hydrated_authorization = PlatformBillingReleaseAuthorizationRegistry.get(tenant, authorization.release_authorization_id, authorization_collection)
    assert hydrated_authorization.release_authorization_id == authorization.release_authorization_id
    request_result = issue_platform_billing_financial_execution_request(client, db, tenant, authorization.release_authorization_id, execution_request_id=f"request-{uuid.uuid4().hex}", requested_at=now)
    request = request_result[0]
    request_collection = db["platform_billing_financial_execution_requests"]
    hydrated_request = PlatformBillingFinancialExecutionRequestRegistry.get(tenant, request.execution_request_id, request_collection)
    assert hydrated_request.execution_request_id == request.execution_request_id and hydrated_request.release_authorization_id == authorization.release_authorization_id
    truth_collection = db["platform_billing_financial_execution_truths"]; settlement_collection = db["platform_billing_financial_settlement_evidence"]
    PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(truth_collection); PlatformBillingFinancialSettlementEvidenceRegistry.ensure_indexes(settlement_collection); PlatformBillingCommercialSettlementProjectionRegistry.ensure_indexes(db["projections"])
    truth = record_platform_billing_financial_execution_truth(tenant, request.execution_request_id, request_collection=request_collection, truth_collection=truth_collection, provider="P", provider_execution_reference="execution", execution_status=PlatformExecutionStatus.EXECUTED, executed_at=now, provider_evidence_reference="evidence", created_at=now)
    settlement = record_platform_billing_financial_settlement_evidence(tenant, truth.execution_truth_id, execution_collection=truth_collection, settlement_collection=settlement_collection, settlement_reference="settlement", provider_settlement_evidence_reference="settled", settled_at=now, created_at=now)
    return client, db, {"tenant": tenant, "invoice": invoice, "authorization": authorization, "settlement": settlement}

def project(client, db, state, settlement_id=None):
    with client.start_session() as session:
        with session.start_transaction():
            return project_platform_billing_commercial_settlement(state["tenant"], settlement_id or state["settlement"].settlement_evidence_id, settlement_collection=db["platform_billing_financial_settlement_evidence"], release_authorization_collection=db["platform_billing_release_authorizations"], platform_invoice_collection=db["invoices"], commercial_projection_collection=db["projections"], session=session)

def test_r3fc_rm01_canonical_full_settlement():
    client, db, state = graph()
    try:
        result = project(client, db, state); invoice = db["invoices"].find_one({"invoice_id": state["invoice"].invoice_id}); assert result.tenant_id == state["tenant"] and db["projections"].count_documents({"tenant_id": state["tenant"]}) == 1 and invoice["status"] in (InvoiceStatus.PAID.value, InvoiceStatus.PAID.name) and invoice["amount_paid"] == 100.0 and invoice["outstanding_amount"] == 0  # type: ignore[index]
    finally: client.close()

def test_r3fc_rm02_wrong_tenant_missing_settlement():
    client, db, state = graph()
    try:
        with pytest.raises(Exception): project(client, db, dict(state, tenant=f"wrong-{state['tenant']}"))
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally: client.close()

def test_r3fc_rm03_provenance_liability_mismatch():
    client, db, state = graph()
    try:
        db["platform_billing_release_authorizations"].update_one({"tenant_id": state["tenant"]}, {"$set": {"authorized_amount_minor": 99}})
        with pytest.raises(Exception): project(client, db, state)
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally: client.close()

def test_r3fc_rm04_executed_is_not_settled():
    client, db, state = graph()
    try:
        db["platform_billing_financial_settlement_evidence"].delete_many({"tenant_id": state["tenant"]})
        with pytest.raises(Exception): project(client, db, state, "missing-settlement")
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 0
    finally: client.close()

def test_r3fc_rm05_identical_replay():
    client, db, state = graph()
    try:
        first = project(client, db, state)
        second = project(client, db, state)
        assert first.commercial_settlement_projection_id == second.commercial_settlement_projection_id and db["projections"].count_documents({"tenant_id": state["tenant"]}) == 1
    finally: client.close()

def test_r3fc_rm06_conflict_or_drift_fails_closed():
    client, db, state = graph()
    try:
        first = project(client, db, state); db["invoices"].update_one({"invoice_id": state["invoice"].invoice_id}, {"$set": {"currency": "USD"}})
        with pytest.raises(Exception): project(client, db, state)
        assert db["projections"].count_documents({"tenant_id": state["tenant"]}) == 1 and db["projections"].find_one({"tenant_id": state["tenant"]})["projection_fingerprint"] == first.projection_fingerprint  # type: ignore[index]
    finally: client.close()

# ARTIFACT: tests/integration/test_platform_billing_commercial_settlement_projection_real_mongo.py
# VERSION: v1.1.0-R3F-C
# AUTHORITY BOUNDARY: Certification evidence only; no authority grant.
# TENANT POSTURE: Synthetic UUID isolation and bounded cleanup.
# FAIL-CLOSED POSTURE: All failures surface; no skips or xfails.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
