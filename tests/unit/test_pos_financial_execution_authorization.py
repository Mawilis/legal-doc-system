"""WILSY OS M10A1 POS authorization domain certificate.
TITLE: POS execution authorization domain tests
VERSION: v1.0.0-M10
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify directional POS authorization invariants and firewalls.
EPITOME: Prove immutable authority binding without execution truth.
ABSOLUTE CANONICAL PATH: tests/unit/test_pos_financial_execution_authorization.py
COLLABORATION / OWNERSHIP: Python EOS authorization certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10A1 adds domain authorization matrix.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider credentials.
TENANT BOUNDARY: Tests require exact tenant/location provenance.
AUTHORITY BOUNDARY: Existing authority evidence only.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, or paid truth.
TRANSACTION BOUNDARY: Pure domain tests.
FAIL-CLOSED DECLARATION: Invalid provenance and unsupported tenders reject.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.saas.domain.pos_commercial import POSSale, POSLineItem, POSStatus, POSTenderIntent, POSRefundIntent, POSTenderType
from tools.eos.saas.domain.pos_financial_execution_authorization import POSFinancialExecutionAuthorization, POSFinancialExecutionDirection
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidenceError
def authority(tenant='t'):
 return TenantAuthorizationDecisionEvidence(tenant,'aid','principal','op','perm','role','auth',0,0,'subject','a'*128,'v','v','v','v','idem',datetime.now(timezone.utc))
def sale(): return POSSale('t','l','s','ZAR',(POSLineItem('p','sku','x',1,100,0,0,'ZAR'),),POSStatus.COMPLETED_COMMERCIAL,'i')
def tender(): return POSTenderIntent('t','l','s',POSTenderType.CARD,100,'ZAR','ti')
def test_collection_and_roundtrip():
 a=POSFinancialExecutionAuthorization.issue(sale(),tender(),authority(),authorization_id='x',idempotency_key='a',authorized_at=datetime.now(timezone.utc)); assert a.direction is POSFinancialExecutionDirection.COLLECTION; assert POSFinancialExecutionAuthorization.from_dict(a.to_dict())==a
def test_refund_direction():
 r=POSRefundIntent('t','l','r','s',50,'ZAR','return','ri'); assert POSFinancialExecutionAuthorization.issue(sale(),r,authority(),authorization_id='r',idempotency_key='b',authorized_at=datetime.now(timezone.utc)).direction is POSFinancialExecutionDirection.DISBURSEMENT
@pytest.mark.parametrize('kind',[POSTenderType.CASH,POSTenderType.VOUCHER,POSTenderType.STORE_CREDIT])
def test_unsupported_tender(kind):
 with pytest.raises(ValueError): POSFinancialExecutionAuthorization.issue(sale(),POSTenderIntent('t','l','s',kind,100,'ZAR','x'),authority(),authorization_id='x',idempotency_key='x',authorized_at=datetime.now(timezone.utc))
def test_wrong_authority_tenant():
 with pytest.raises(ValueError): POSFinancialExecutionAuthorization.issue(sale(),tender(),authority('other'),authorization_id='x',idempotency_key='x',authorized_at=datetime.now(timezone.utc))
def test_direction_changes_fingerprint():
 a=POSFinancialExecutionAuthorization.issue(sale(),tender(),authority(),authorization_id='x',idempotency_key='a',authorized_at=datetime.now(timezone.utc)); r=POSRefundIntent('t','l','r','s',50,'ZAR','return','ri'); b=POSFinancialExecutionAuthorization.issue(sale(),r,authority(),authorization_id='x',idempotency_key='a',authorized_at=a.authorized_at); assert a.authorization_fingerprint != b.authorization_fingerprint
def test_corrupt_fingerprint_rejected():
 a=POSFinancialExecutionAuthorization.issue(sale(),tender(),authority(),authorization_id='x',idempotency_key='a',authorized_at=datetime.now(timezone.utc)); d=a.to_dict(); d['amount_minor']=99
 with pytest.raises(ValueError): POSFinancialExecutionAuthorization.from_dict(d)
def test_no_financial_state_fields():
 a=POSFinancialExecutionAuthorization.issue(sale(),tender(),authority(),authorization_id='x',idempotency_key='a',authorized_at=datetime.now(timezone.utc)); assert not any(hasattr(a,n) for n in ('paid','settled','executed'))
def test_amount_and_currency_firewalls():
 with pytest.raises(ValueError): POSFinancialExecutionAuthorization.issue(sale(),POSTenderIntent('t','l','s',POSTenderType.CARD,True,'ZAR','x'),authority(),authorization_id='x',idempotency_key='x',authorized_at=datetime.now(timezone.utc))
 with pytest.raises(ValueError): POSFinancialExecutionAuthorization.issue(sale(),POSTenderIntent('t','l','s',POSTenderType.CARD,100,'usd','x'),authority(),authorization_id='x',idempotency_key='x',authorized_at=datetime.now(timezone.utc))
# ARTIFACT: test_pos_financial_execution_authorization.py
# VERSION: v1.0.0-M10
# AUTHORITY BOUNDARY: Binding only.
# FAIL-CLOSED POSTURE: Invalid authority rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
