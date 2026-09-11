"""WILSY OS M10A1 authorization issuer certificate.
TITLE: POS authorization issuance tests
VERSION: v1.0.0-M10
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify governed collection and refund authorization issuance.
EPITOME: Issuance consumes canonical M9 values and existing actor evidence.
ABSOLUTE CANONICAL PATH: tests/unit/test_pos_financial_execution_authorization_issuance.py
COLLABORATION / OWNERSHIP: Python EOS issuer certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10A1 adds issuer matrix.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider invocation or secrets.
TENANT BOUNDARY: Issuance requires exact source and authority tenant.
AUTHORITY BOUNDARY: Existing decision evidence required.
FINANCIAL AUTHORITY BOUNDARY: No execution, settlement, or paid state.
TRANSACTION BOUNDARY: Explicit collection/session.
FAIL-CLOSED DECLARATION: Missing or divergent evidence rejects.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.saas.billing.pos_financial_execution_authorization_issuance import issue_pos_collection_execution_authorization, issue_pos_refund_execution_authorization
from tools.eos.saas.domain.pos_commercial import POSRefundIntent, POSTenderIntent, POSTenderType
from tools.eos.saas.billing.pos_financial_execution_authorization_registry import POSFinancialExecutionAuthorizationRegistry
from test_pos_financial_execution_authorization import sale, authority
class C:
 def __init__(self): self.rows=[]
 def find_one(self,q,session=None): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
 def insert_one(self,d,session=None): self.rows.append(dict(d))
def test_collection_and_refund():
 c=C(); s=sale(); t=POSTenderIntent('t','l','s',POSTenderType.CARD,100,'ZAR','t'); a=issue_pos_collection_execution_authorization(s,t,authority(),c,authorization_id='a',idempotency_key='a'); r=POSRefundIntent('t','l','r','s',50,'ZAR','return','r'); b=issue_pos_refund_execution_authorization(s,r,authority(),c,authorization_id='b',idempotency_key='b'); assert a.direction.value=='COLLECTION' and b.direction.value=='DISBURSEMENT'
def test_missing_authority_rejects():
 with pytest.raises(ValueError): issue_pos_collection_execution_authorization(sale(),POSTenderIntent('t','l','s',POSTenderType.CARD,100,'ZAR','t'),None,C(),authorization_id='a',idempotency_key='a')
@pytest.mark.parametrize('field,source', [('tenant_id',POSTenderIntent('x','l','s',POSTenderType.CARD,100,'ZAR','t')),('location_id',POSTenderIntent('t','x','s',POSTenderType.CARD,100,'ZAR','t')),('sale_id',POSTenderIntent('t','l','x',POSTenderType.CARD,100,'ZAR','t')),('currency',POSTenderIntent('t','l','s',POSTenderType.CARD,100,'USD','t'))])
def test_provenance_mismatch_rejects(field,source):
 with pytest.raises(ValueError): issue_pos_collection_execution_authorization(sale(),source,authority(),C(),authorization_id='a',idempotency_key='a')
def test_identical_and_divergent_replay():
 c=C(); s=sale(); t=POSTenderIntent('t','l','s',POSTenderType.CARD,100,'ZAR','t'); auth=authority(); stamp=datetime(2026,1,1,tzinfo=timezone.utc); a=issue_pos_collection_execution_authorization(s,t,auth,c,authorization_id='a',idempotency_key='a',authorized_at=stamp); b=issue_pos_collection_execution_authorization(s,t,auth,c,authorization_id='a',idempotency_key='a',authorized_at=stamp); assert a==b and len(c.rows)==1
 with pytest.raises(Exception): issue_pos_collection_execution_authorization(s,t,authority('t'),c,authorization_id='a',idempotency_key='a')
def test_provider_and_execution_fields_absent():
 c=C(); a=issue_pos_collection_execution_authorization(sale(),POSTenderIntent('t','l','s',POSTenderType.CARD,100,'ZAR','t'),authority(),c,authorization_id='a',idempotency_key='a'); assert not any(hasattr(a,n) for n in ('provider','executed','settled','paid'))
# ARTIFACT: test_pos_financial_execution_authorization_issuance.py
# VERSION: v1.0.0-M10
# AUTHORITY BOUNDARY: Existing authority evidence required.
# FAIL-CLOSED POSTURE: Missing authority rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
