"""WILSY OS M11D2 AR1P domain certificate.
TITLE: Platform Receivable Closure Domain Certificate
VERSION: v1.1.0-M11D2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies strict immutable PLATFORM closure evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_commercial_receivable_closure_projection.py
COLLABORATION / OWNERSHIP: M11D2 domain certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.1.0-M11D2 certifies strict construction and hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant identifiers only.
TENANT BOUNDARY: PLATFORM projection remains tenant-bound.
AUTHORITY BOUNDARY: Settlement-derived projection only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
TRANSACTION BOUNDARY: Pure unit tests.
FAIL-CLOSED DECLARATION: Invalid schema and provenance reject.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.saas.domain.platform_billing_commercial_receivable_closure_projection import PlatformBillingCommercialReceivableClosureProjection as P, PlatformBillingCommercialReceivableClosureProjectionError as E
def p(): return P('t','c','i','a'*128,'s','b'*128,'e','r','ZAR',100,100,0,datetime(2026,1,1,tzinfo=timezone.utc),datetime(2026,1,2,tzinfo=timezone.utc),'CLOSED')
def test_domain_round_trip_and_fingerprint(): assert P.from_dict(p().to_dict())==p()
@pytest.mark.parametrize('field,value',[('currency','USD'),('receivable_status','PAID'),('remaining_receivable_amount_minor',1),('closed_receivable_amount_minor',99),('original_receivable_amount_minor',True)])
def test_domain_rejects_invalid_material_fields(field,value):
 d=p().__dict__ if hasattr(p(),'__dict__') else p().to_dict(); d.pop('projection_fingerprint',None); d[field]=value
 with pytest.raises(E): P(**d)
def test_domain_rejects_unknown_missing_id_and_corrupt_fingerprint():
 d=p().to_dict()
 for bad in ({**d,'extra':1},{k:v for k,v in d.items() if k!='currency'},{**d,'_id':'x'},{**d,'projection_fingerprint':'0'*128}):
  with pytest.raises(E): P.from_dict(bad)
# ARTIFACT: test_platform_billing_commercial_receivable_closure_projection.py
# VERSION: v1.1.0-M11D2
# AUTHORITY BOUNDARY: Settlement-derived projection only.
# TENANT POSTURE: PLATFORM scoped.
# FAIL-CLOSED POSTURE: Invalid evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
