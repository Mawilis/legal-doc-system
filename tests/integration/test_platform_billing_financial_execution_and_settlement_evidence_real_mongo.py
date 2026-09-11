"""WILSY OS — R3F0 PLATFORM BILLING EXECUTION / SETTLEMENT CERTIFICATE

TITLE: Platform Billing Financial Execution and Settlement Evidence Real-Mongo Certificate
VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
PURPOSE: Execute six bounded durable platform evidence scenarios against governed Mongo.
EPITOME: Prove tenant-scoped execution-truth and settlement-evidence persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
COLLABORATION / OWNERSHIP: EOS Kennel platform-financial integration certificate.
CERTIFICATION / UPDATE DATE: 2026-09-06; structural remediation.
CHANGELOG: v1.1.0-R3F0-STRUCTURAL-REMEDIATION replaced incomplete one-line banner.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic UUID isolation; no secrets or raw provider credentials.
TENANT BOUNDARY: Every fixture, lookup, mutation, and assertion is tenant-scoped.
AUTHORITY BOUNDARY: Evidence certification only; no authority grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively; no provider execution or money movement.
TRANSACTION BOUNDARY: Governed Mongo client and caller-owned persistence graph only.
FAIL-CLOSED DECLARATION: Missing URI, invalid provenance, and persistence failures fail closed.
"""
from __future__ import annotations
import os,uuid
from datetime import datetime,timezone
import pytest
from pymongo import MongoClient
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization
from tools.eos.saas.billing.platform_billing_release_authorization_registry import PlatformBillingReleaseAuthorizationRegistry
from tools.eos.saas.billing.platform_billing_financial_execution_request_issuance import issue_platform_billing_financial_execution_request
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from tools.eos.kennel.orchestration.platform_billing_financial_execution_truth_recording import record_platform_billing_financial_execution_truth
from tools.eos.kennel.registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry
from tools.eos.kennel.orchestration.platform_billing_financial_settlement_evidence_recording import record_platform_billing_financial_settlement_evidence
URI=os.getenv('TEST_VENDOR_MONGO_URI','')
def setup_graph():
 if not URI: raise RuntimeError('TEST_VENDOR_MONGO_URI is required')
 c=MongoClient(URI,serverSelectionTimeoutMS=2000); d=c[f'r3f0_{uuid.uuid4().hex}']; n=datetime.now(timezone.utc); a=PlatformBillingReleaseAuthorization('t','a','i','a'*128,'e','b'*128,100,'ZAR','p','basis','dest','k',n,n); ac=d['platform_billing_release_authorizations']; PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(ac); ac.insert_one(a.to_persistence_dict()); issue_platform_billing_financial_execution_request(c,d,'t','a',execution_request_id='r',requested_at=n); PlatformBillingFinancialExecutionTruthRegistry.ensure_indexes(d['platform_billing_financial_execution_truths']); PlatformBillingFinancialSettlementEvidenceRegistry.ensure_indexes(d['platform_billing_financial_settlement_evidence']); return c,d,a
def truth(d, *, executed_at, created_at, provider_execution_reference='x', provider_evidence_reference='e'): return record_platform_billing_financial_execution_truth('t','r',request_collection=d['platform_billing_financial_execution_requests'],truth_collection=d['platform_billing_financial_execution_truths'],provider='P',provider_execution_reference=provider_execution_reference,execution_status=PlatformExecutionStatus.EXECUTED,executed_at=executed_at,provider_evidence_reference=provider_evidence_reference,created_at=created_at)
def close(c): c.close()
def test_r3f0_rm01():
 c,d,a=setup_graph()
 try:
  n=datetime(2026,1,1,tzinfo=timezone.utc); assert truth(d,executed_at=n,created_at=n).platform_invoice_id==a.platform_invoice_id
 finally: close(c)
def test_r3f0_rm02():
 c,d,_=setup_graph()
 try:
  with pytest.raises(Exception): record_platform_billing_financial_execution_truth('wrong','r',request_collection=d['platform_billing_financial_execution_requests'],truth_collection=d['platform_billing_financial_execution_truths'],provider='P',provider_execution_reference='x',execution_status=PlatformExecutionStatus.EXECUTED,executed_at=datetime.now(timezone.utc),provider_evidence_reference='e',created_at=datetime.now(timezone.utc))
 finally: close(c)
def test_r3f0_rm03():
 c,d,a=setup_graph()
 try:
  n=datetime(2026,1,1,tzinfo=timezone.utc); v=truth(d,executed_at=n,created_at=n); assert (v.executed_amount_minor,v.currency,v.platform_invoice_id)==(100,'ZAR',a.platform_invoice_id)
 finally: close(c)
def test_r3f0_rm04():
 c,d,_=setup_graph()
 try:
  n=datetime(2026,1,1,tzinfo=timezone.utc); v=truth(d,executed_at=n,created_at=n); s=record_platform_billing_financial_settlement_evidence('t',v.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=n,created_at=n); assert s.platform_execution_truth_id==v.execution_truth_id
 finally: close(c)
def test_r3f0_rm05():
 c,d,_=setup_graph()
 try:
  with pytest.raises(Exception): record_platform_billing_financial_settlement_evidence('wrong','missing',execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=datetime.now(timezone.utc),created_at=datetime.now(timezone.utc))
 finally: close(c)
def test_r3f0_rm06():
 c,d,_=setup_graph()
 try:
  observed_at=datetime(2026,1,1,tzinfo=timezone.utc); created_at=datetime(2026,1,1,0,0,1,tzinfo=timezone.utc)
  first=truth(d,executed_at=observed_at,created_at=created_at)
  replay=truth(d,executed_at=observed_at,created_at=created_at)
  assert replay==first
  hydrated=PlatformBillingFinancialExecutionTruthRegistry.get('t',first.execution_truth_id,d['platform_billing_financial_execution_truths'])
  assert hydrated==first
  with pytest.raises(Exception):
   truth(d,executed_at=observed_at,created_at=created_at,provider_execution_reference='different')
  settled_at=datetime(2026,1,2,tzinfo=timezone.utc); settlement_created_at=datetime(2026,1,2,0,0,1,tzinfo=timezone.utc)
  settlement=record_platform_billing_financial_settlement_evidence('t',first.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=settled_at,created_at=settlement_created_at)
  settlement_replay=record_platform_billing_financial_settlement_evidence('t',first.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='s',provider_settlement_evidence_reference='se',settled_at=settled_at,created_at=settlement_created_at)
  assert settlement_replay==settlement
  with pytest.raises(Exception):
   record_platform_billing_financial_settlement_evidence('t',first.execution_truth_id,execution_collection=d['platform_billing_financial_execution_truths'],settlement_collection=d['platform_billing_financial_settlement_evidence'],settlement_reference='different',provider_settlement_evidence_reference='se',settled_at=settled_at,created_at=settlement_created_at)
 finally: close(c)
# ARTIFACT: test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
# VERSION: v1.1.0
# AUTHORITY BOUNDARY: Kennel evidence only.
# END OF WILSY OS SOVEREIGN ARTIFACT
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tests/integration/test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
# COLLABORATION / OWNERSHIP: Kennel EOS platform financial domain; R3F0 certificates.
# CERTIFICATION / UPDATE DATE: 2026-09-06; structural remediation.
# CHANGELOG: v1.1.0-R3F0-STRUCTURAL-REMEDIATION complete sovereign metadata alignment.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Tenant isolation; UUID synthetic tests; no raw secrets.
# TENANT BOUNDARY: Every read, write, replay, and certificate assertion is tenant-scoped.
# AUTHORITY BOUNDARY: Kennel EOS is exclusive financial execution authority.
# FINANCIAL AUTHORITY BOUNDARY: Evidence only; no provider call, settlement inference, or paid state.
# TRANSACTION BOUNDARY: Caller-owned Mongo session propagates through durable operations.
# FAIL-CLOSED DECLARATION: Invalid authority, provenance, persistence, or hydration fails closed.
# BEGIN SOVEREIGN HEADER SEAL
# END SOVEREIGN HEADER SEAL

# ARTIFACT: tests/integration/test_platform_billing_financial_execution_and_settlement_evidence_real_mongo.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
