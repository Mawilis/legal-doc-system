"""WILSY OS M10A1 authorization registry certificate.
TITLE: POS authorization registry tests
VERSION: v1.0.0-M10
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify durable authorization replay, hydration, and isolation.
EPITOME: Explicit collection persistence without hidden lifecycle ownership.
ABSOLUTE CANONICAL PATH: tests/unit/test_pos_financial_execution_authorization_registry.py
COLLABORATION / OWNERSHIP: Python EOS registry certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10A1 adds registry behavior matrix.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collection only.
TENANT BOUNDARY: Tenant-scoped lookups.
AUTHORITY BOUNDARY: Persistence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement.
TRANSACTION BOUNDARY: Caller-owned session.
FAIL-CLOSED DECLARATION: Replay and corruption reject.
"""
from datetime import datetime, timezone
from tools.eos.saas.billing.pos_financial_execution_authorization_registry import POSFinancialExecutionAuthorizationRegistry
from tools.eos.saas.domain.pos_financial_execution_authorization import POSFinancialExecutionAuthorization
from test_pos_financial_execution_authorization import sale, tender, authority
class C:
 def __init__(self): self.rows=[]; self.inserts=0
 def create_index(self,*a,**k): return 'idx'
 def find_one(self,q,session=None): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
 def insert_one(self,d,session=None): self.inserts+=1; self.rows.append(dict(d))
def value(i='x'): return POSFinancialExecutionAuthorization.issue(sale(),tender(),authority(),authorization_id=i,idempotency_key=i,authorized_at=datetime.now(timezone.utc))
def test_create_get_replay_and_indexes():
 c=C(); POSFinancialExecutionAuthorizationRegistry.ensure_indexes(c); a=value(); assert POSFinancialExecutionAuthorizationRegistry.create(a,c)==a; assert POSFinancialExecutionAuthorizationRegistry.get('t','x',c)==a; assert POSFinancialExecutionAuthorizationRegistry.create(a,c)==a; assert c.inserts==1
def test_divergent_replay_rejects():
 c=C(); POSFinancialExecutionAuthorizationRegistry.create(value(),c); changed=value(); changed=POSFinancialExecutionAuthorization.issue(sale(),tender(),authority(),authorization_id='x',idempotency_key='x',authorized_at=datetime.now(timezone.utc))
 c.rows[0]['amount_minor']=99
 try: POSFinancialExecutionAuthorizationRegistry.get('t','x',c); assert False
 except RuntimeError: pass
def test_session_forwarding():
 c=C(); seen=[]
 original=c.find_one
 def find(q,session=None): seen.append(session); return original(q,session)
 c.find_one=find; POSFinancialExecutionAuthorizationRegistry.create(value(),c,session='caller'); POSFinancialExecutionAuthorizationRegistry.get('t','x',c,session='caller'); assert seen and all(x=='caller' for x in seen)
def test_mongo_id_hydrates_without_entering_domain_state():
 c=C(); a=value(); c.rows.append({**a.to_dict(), '_id': 'mongo-object-id'}); hydrated=POSFinancialExecutionAuthorizationRegistry.get('t','x',c); assert hydrated==a and hydrated.authorization_fingerprint==a.authorization_fingerprint and not hasattr(hydrated,'_id')
# ARTIFACT: test_pos_financial_execution_authorization_registry.py
# VERSION: v1.0.0-M10
# AUTHORITY BOUNDARY: Persistence only.
# FAIL-CLOSED POSTURE: Corrupt durable evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
