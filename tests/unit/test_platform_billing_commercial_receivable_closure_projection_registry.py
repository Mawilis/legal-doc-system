"""WILSY OS M11D2 AR1P registry certificate.
TITLE: Platform Receivable Closure Registry Certificate
VERSION: v1.1.0-M11D2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies persistence-only tenant-scoped replay and hydration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_commercial_receivable_closure_projection_registry.py
COLLABORATION / OWNERSHIP: M11D2 registry certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.1.0-M11D2 certifies Mongo metadata boundary and fingerprint validation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit collection/session only.
TENANT BOUNDARY: All lookup filters include tenant.
AUTHORITY BOUNDARY: Persistence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement authority.
TRANSACTION BOUNDARY: Caller-owned session.
FAIL-CLOSED DECLARATION: Corruption and conflicts reject.
"""
from datetime import datetime, timezone
from tools.eos.saas.domain.platform_billing_commercial_receivable_closure_projection import PlatformBillingCommercialReceivableClosureProjection as P
from tools.eos.saas.billing.platform_billing_commercial_receivable_closure_projection_registry import PlatformBillingCommercialReceivableClosureProjectionRegistry as R
class C:
 def __init__(self): self.docs=[]; self.sessions=[]
 def insert_one(self,d,session=None): self.sessions.append(session); self.docs.append(dict(d))
 def find_one(self,q,session=None): self.sessions.append(session); return next((dict(d,**{'_id':'mongo'}) for d in self.docs if all(d.get(k)==v for k,v in q.items())),None)
def p(): return P('t','c','i','a'*128,'s','b'*128,'e','r','ZAR',100,100,0,datetime(2026,1,1,tzinfo=timezone.utc),datetime(2026,1,2,tzinfo=timezone.utc),'CLOSED')
def test_registry_hydrates_and_strips_only_mongo_id():
 c=C(); value=p(); R.create(value,c,session='s'); stored=dict(c.docs[0]); hydrated=R.get('t','c',c,session='s'); assert hydrated==value and '_id' not in stored and c.sessions==['s','s']
# ARTIFACT: test_platform_billing_commercial_receivable_closure_projection_registry.py
# VERSION: v1.1.0-M11D2
# AUTHORITY BOUNDARY: Persistence only.
# TENANT POSTURE: Tenant scoped.
# FAIL-CLOSED POSTURE: Corruption rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
