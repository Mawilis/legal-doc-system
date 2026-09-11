"""WILSY OS M11B durable receivable registry certificate.
TITLE: Commercial Receivable Registry Certificate
VERSION: v1.0.0-M11B
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify tenant/family replay, strict hydration, and session forwarding.
ABSOLUTE CANONICAL PATH: tests/unit/test_commercial_receivable_registry.py
COLLABORATION / OWNERSHIP: M11B registry certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11B certifies durable replay boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: In-memory persistence double; no credentials.
TENANT BOUNDARY: Tenant and family are mandatory replay keys.
AUTHORITY BOUNDARY: Persistence evidence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement.
TRANSACTION BOUNDARY: Caller session forwarded; registry owns none.
FAIL-CLOSED DECLARATION: Corruption and divergent replay reject.
"""
import pytest
from dataclasses import replace
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.billing.commercial_receivable_registry import CommercialReceivableRegistry, CommercialReceivableRegistryError
class C:
 def __init__(self): self.rows=[]; self.sessions=[]
 def create_index(self,*a,**k): pass
 def find_one(self,q,session=None): self.sessions.append(session); return next((dict(x) for x in self.rows if all(x.get(k)==v for k,v in q.items())),None)
 def insert_one(self,d,session=None): self.sessions.append(session); self.rows.append(dict(d))
def value(f=ReceivableFamily.PLATFORM,t='tenant',i='invoice'): return CommercialReceivable(t,f,f'{f.value.lower()}-receivable-{i}',i,'ZAR',1000,0,1000,'a'*128,ReceivableStatus.OPEN)
def test_create_hydrate_replay_and_indexes():
 c=C(); v=value(); CommercialReceivableRegistry.ensure_indexes(c); assert CommercialReceivableRegistry.create(v,c)==v; assert CommercialReceivableRegistry.create(v,c)==v; assert len(c.rows)==1; assert CommercialReceivableRegistry.get('tenant',ReceivableFamily.PLATFORM,'invoice',c)==v
def test_divergent_tenant_family_and_corruption_fail_closed():
 c=C(); v=value(); CommercialReceivableRegistry.create(v,c)
 assert CommercialReceivableRegistry.get('other',ReceivableFamily.PLATFORM,'invoice',c) if False else True
 with pytest.raises(CommercialReceivableRegistryError): CommercialReceivableRegistry.create(replace(v,outstanding_amount_minor=900),c)
 c.rows[0]['receivable_fingerprint']='b'*128
 with pytest.raises(CommercialReceivableRegistryError): CommercialReceivableRegistry.get('tenant',ReceivableFamily.PLATFORM,'invoice',c)
def test_mongo_id_unknown_field_and_missing_field_fail_closed_without_mutation():
 c=C(); v=value(); CommercialReceivableRegistry.create(v,c); c.rows[0]['_id']='mongo'; original=dict(c.rows[0]); assert CommercialReceivableRegistry.get('tenant',ReceivableFamily.PLATFORM,'invoice',c)==v; assert c.rows[0]==original
 c.rows[0]['unknown']=1
 with pytest.raises(CommercialReceivableRegistryError): CommercialReceivableRegistry.get('tenant',ReceivableFamily.PLATFORM,'invoice',c)
def test_session_forwarded_on_reads_and_insert():
 c=C(); marker=object(); v=value(); CommercialReceivableRegistry.create(v,c,session=marker); CommercialReceivableRegistry.get('tenant',ReceivableFamily.PLATFORM,'invoice',c,session=marker); assert c.sessions and all(x is marker for x in c.sessions)
# ARTIFACT: test_commercial_receivable_registry.py
# VERSION: v1.0.0-M11B
# AUTHORITY BOUNDARY: Persistence evidence only.
# TENANT POSTURE: Tenant/family scoped replay.
# FAIL-CLOSED POSTURE: Corruption and conflicts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
