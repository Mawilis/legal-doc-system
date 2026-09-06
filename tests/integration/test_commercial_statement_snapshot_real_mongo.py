"""WILSY OS M7 durable real-Mongo statement certificate.

TITLE: Six-scenario commercial statement snapshot certificate
VERSION: v1.1.0-M7
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Exercise production platform/client statement graphs against Mongo.
EPITOME: Durable tenant-scoped snapshots, replay, isolation, and corruption gates.
ABSOLUTE CANONICAL PATH: tests/integration/test_commercial_statement_snapshot_real_mongo.py
COLLABORATION / OWNERSHIP: SaaS Billing statement and Kennel evidence owners.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.1.0-M7 replaces six environment placeholders with behavioral tests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic UUID data; no secrets or provider calls.
TENANT BOUNDARY: Every query and snapshot is tenant/account scoped.
AUTHORITY BOUNDARY: Projection and evidence only; Kennel owns execution truth.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, or provider authority is invented.
TRANSACTION BOUNDARY: Certificate-owned client/session is forwarded to registries.
FAIL-CLOSED DECLARATION: Missing URI, provenance drift, conflicts, and corruption fail.
"""
from __future__ import annotations
import os, uuid
from datetime import datetime, timezone
import pytest
from pymongo import MongoClient
from tools.eos.saas.domain.billing import ClientInvoice, PlatformInvoice
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from tools.eos.kennel.orchestration.platform_billing_financial_execution_truth_recording import record_platform_billing_financial_execution_truth
from tools.eos.kennel.registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry
from tools.eos.kennel.orchestration.platform_billing_financial_settlement_evidence_recording import record_platform_billing_financial_settlement_evidence
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection import project_platform_billing_commercial_settlement
from tools.eos.saas.billing.platform_billing_commercial_settlement_projection_registry import PlatformBillingCommercialSettlementProjectionRegistry
from tools.eos.saas.domain.commercial_statement import CommercialStatementSnapshot, StatementFamily, StatementLedgerKind
from tools.eos.saas.billing.commercial_statement_engine import CommercialStatementError, generate_commercial_statement
from tools.eos.saas.billing.commercial_statement_registry import CommercialStatementRegistryError, CommercialStatementSnapshotRegistry

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "").strip()

def _client():
    if not URI: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    return client, client[f"m7_statement_{uuid.uuid4().hex}"], f"m7-{uuid.uuid4().hex}", datetime(2026, 1, 1, tzinfo=timezone.utc)

def _invoice(tenant, now, customer="customer-a"):
    return ClientInvoice.from_dict({"tenant_id":tenant,"invoice_id":f"invoice-{uuid.uuid4().hex}","customer_id":customer,"status":"open","total":125.0,"amount":125.0,"currency":"ZAR","line_items":[{"description":"Service","amount":125.0}],"issued_at":now,"due_at":now})

def _save(db, snapshot, *, session=None):
    c = db["commercial_statement_snapshots"]; CommercialStatementSnapshotRegistry.ensure_indexes(c); return CommercialStatementSnapshotRegistry.create(snapshot, c, session=session)

def _statement(tenant, now, invoice, lane=StatementLedgerKind.CLIENT, account="customer-a"):
    return generate_commercial_statement(tenant_id=tenant, ledger_kind=lane, family=StatementFamily.OPEN_ITEM, account_id=account, currency="ZAR", as_of=now, invoices=(invoice,))

def _platform_graph():
    client, db, tenant, now = _client(); invoice = PlatformInvoice.from_dict({"tenant_id":tenant,"invoice_id":f"platform-{uuid.uuid4().hex}","status":"open","total":100.0,"amount":100.0,"currency":"ZAR","line_items":[{"description":"Platform","amount":100.0}],"issued_at":now,"due_at":now})
    db["platform_invoices"].insert_one(invoice.to_dict()); auth = PlatformBillingReleaseAuthorization(tenant, f"auth-{uuid.uuid4().hex}", invoice.invoice_id, invoice.commercial_release_evidence_fingerprint, "evidence", "a"*128, invoice.release_amount_minor, invoice.currency, "principal", "basis", "destination", f"idem-{uuid.uuid4().hex}", now, now)
    ac = db["platform_billing_release_authorizations"]; PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(ac); PlatformBillingReleaseAuthorizationRegistry.create(auth, ac)
    request, _ = issue_platform_billing_financial_execution_request(client, db, tenant, auth.release_authorization_id, execution_request_id=f"request-{uuid.uuid4().hex}", requested_at=now)
    rc = db["platform_billing_financial_execution_requests"]; tc = db["platform_billing_financial_execution_truths"]; ec = db["platform_billing_financial_settlement_evidence"]; pc = db["platform_billing_commercial_settlement_projections"]
    PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(tc); PlatformBillingFinancialSettlementEvidenceRegistry.ensure_indexes(ec); PlatformBillingCommercialSettlementProjectionRegistry.ensure_indexes(pc)
    truth = record_platform_billing_financial_execution_truth(tenant, request.execution_request_id, request_collection=rc, truth_collection=tc, provider="certificate", provider_execution_reference="execution", execution_status=PlatformExecutionStatus.EXECUTED, executed_at=now, provider_evidence_reference="evidence", created_at=now)
    evidence = record_platform_billing_financial_settlement_evidence(tenant, truth.execution_truth_id, execution_collection=tc, settlement_collection=ec, settlement_reference="settlement", provider_settlement_evidence_reference="settled", settled_at=now, created_at=now)
    with client.start_session() as session:
        with session.start_transaction():
            projection = project_platform_billing_commercial_settlement(tenant, evidence.settlement_evidence_id, settlement_collection=ec, release_authorization_collection=ac, platform_invoice_collection=db["platform_invoices"], commercial_projection_collection=pc, session=session)
    return client, db, tenant, now, invoice, projection

def test_rm_st01_platform_statement_snapshot_real_graph():
    client, db, tenant, now, original_invoice, projection = _platform_graph()
    try:
        invoice = PlatformInvoice.from_dict(db["platform_invoices"].find_one({"invoice_id":original_invoice.invoice_id}) or {})
        statement = generate_commercial_statement(tenant_id=tenant, ledger_kind=StatementLedgerKind.PLATFORM, family=StatementFamily.OPEN_ITEM, account_id=tenant, currency=invoice.currency, as_of=now, invoices=(invoice,), settlement_projections=(projection,))
        with client.start_session() as session:
            with session.start_transaction():
                snap = _save(db, CommercialStatementSnapshot.from_statement(statement, generated_at=now, source_evidence_fingerprint=projection.projection_fingerprint), session=session); hydrated = CommercialStatementSnapshotRegistry.get(tenant, snap.snapshot_id, db["commercial_statement_snapshots"], session=session)
        assert len(hydrated.statement.activities) == 2 and hydrated.statement.closing_balance_minor == 0 and hydrated.statement.activities[1].source_type == "r3f_settlement"
    finally: client.close()

def test_rm_st02_client_statement_snapshot_real_graph():
    client, db, tenant, now = _client()
    try:
        with client.start_session() as session:
            with session.start_transaction():
                snap = _save(db, CommercialStatementSnapshot.from_statement(_statement(tenant, now, _invoice(tenant, now)), generated_at=now), session=session); hydrated = CommercialStatementSnapshotRegistry.get(tenant, snap.snapshot_id, db["commercial_statement_snapshots"], session=session)
        assert hydrated.statement.ledger_kind is StatementLedgerKind.CLIENT and hydrated.statement.closing_balance_minor == 12500 and all(a.kind.value == "INVOICE_CHARGE" for a in hydrated.statement.activities)
    finally: client.close()

def test_rm_st03_tenant_and_customer_isolation_real_graph():
    client, db, tenant, now = _client(); invoice = _invoice(tenant, now)
    try:
        with pytest.raises(CommercialStatementError): _statement(f"wrong-{tenant}", now, invoice)
        with pytest.raises(CommercialStatementError): _statement(tenant, now, invoice, account="customer-b")
        assert db["commercial_statement_snapshots"].count_documents({}) == 0
    finally: client.close()

def test_rm_st04_cross_lane_and_provenance_fail_closed_real_graph():
    client, db, tenant, now = _client()
    try:
        with pytest.raises(CommercialStatementError): _statement(tenant, now, _invoice(tenant, now), lane=StatementLedgerKind.PLATFORM, account=tenant)
        platform = PlatformInvoice.from_dict({"tenant_id":tenant,"invoice_id":"platform-1","status":"open","total":10.0,"amount":10.0,"currency":"ZAR","line_items":[{"description":"Platform","amount":10.0}],"issued_at":now,"due_at":now})
        with pytest.raises(CommercialStatementError): _statement(tenant, now, platform)
        assert db["commercial_statement_snapshots"].count_documents({}) == 0
    finally: client.close()

def test_rm_st05_identical_snapshot_replay_real_graph():
    client, db, tenant, now = _client()
    try:
        with client.start_session() as session:
            with session.start_transaction():
                snap = CommercialStatementSnapshot.from_statement(_statement(tenant, now, _invoice(tenant, now)), generated_at=now); first, second = _save(db, snap, session=session), _save(db, snap, session=session)
                assert first.to_dict() == second.to_dict() and db["commercial_statement_snapshots"].count_documents({"tenant_id":tenant}, session=session) == 1
    finally: client.close()

def test_rm_st06_corrupt_snapshot_fail_closed_real_graph():
    client, db, tenant, now = _client()
    try:
        with client.start_session() as session:
            with session.start_transaction():
                snap = _save(db, CommercialStatementSnapshot.from_statement(_statement(tenant, now, _invoice(tenant, now)), generated_at=now), session=session); c = db["commercial_statement_snapshots"]; c.update_one({"tenant_id":tenant,"snapshot_id":snap.snapshot_id},{"$set":{"statement.closing_balance_minor":1}}, session=session)
                with pytest.raises(CommercialStatementRegistryError, match="M7_SNAPSHOT_CORRUPT"): CommercialStatementSnapshotRegistry.get(tenant, snap.snapshot_id, c, session=session)
        assert c.count_documents({"tenant_id":tenant}) == 1
    finally: client.close()

# ARTIFACT: test_commercial_statement_snapshot_real_mongo.py
# VERSION: v1.1.0-M7
# AUTHORITY BOUNDARY: Certification evidence only; no authority grant.
# TENANT POSTURE: Synthetic UUID isolation and bounded cleanup.
# FAIL-CLOSED POSTURE: No skips, xfails, or silent corruption repair.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
