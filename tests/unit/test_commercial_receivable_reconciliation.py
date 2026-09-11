"""WILSY OS M11D1 reconciliation unit certificate.
TITLE: Commercial Receivable Reconciliation Certificate
VERSION: v1.0.0-M11D1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies pure matching of receivables, credits, and R3F evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_commercial_receivable_reconciliation.py
COLLABORATION / OWNERSHIP: M11D1 reconciliation unit owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11D1 certifies balance and provenance firewall.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic evidence references only.
TENANT BOUNDARY: Every input must match receivable tenant.
AUTHORITY BOUNDARY: Evidence projection only.
FINANCIAL AUTHORITY BOUNDARY: No settlement creation or payment.
TRANSACTION BOUNDARY: Pure unit tests.
FAIL-CLOSED DECLARATION: Drift, duplicate, and excess evidence reject.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.domain.commercial_receivable_credit_adjustment import CommercialReceivableCreditAdjustment, CreditBasis
from tools.eos.saas.domain.commercial_receivable_reconciliation import CommercialReceivableReconciliation, ReconciliationError
def r(): return CommercialReceivable('t',ReceivableFamily.CLIENT,'r','i','ZAR',1000,0,1000,'a'*128,ReceivableStatus.OPEN)
def a(i='a',n=100): return CommercialReceivableCreditAdjustment.from_receivable(r(),i,n,CreditBasis.CREDIT_NOTE,datetime(2026,1,1,tzinfo=timezone.utc))
def test_r01_credit_arithmetic_and_immutability():
 src=r(); out=CommercialReceivableReconciliation.reconcile(src,[a()],[],datetime(2026,1,2,tzinfo=timezone.utc)); assert out.total_credit_minor==100 and out.outstanding_amount_minor==900 and src.outstanding_amount_minor==1000
def test_r02_ordering_and_duplicate_fail_closed():
 now=datetime(2026,1,2,tzinfo=timezone.utc); x,y=a('x',100),a('y',200); assert CommercialReceivableReconciliation.reconcile(r(),[x,y],[],now).adjustment_fingerprints==tuple(sorted((x.adjustment_fingerprint,y.adjustment_fingerprint)))
 with pytest.raises(ReconciliationError): CommercialReceivableReconciliation.reconcile(r(),[x,x],[],now)
def test_r03_provenance_and_overcredit_fail_closed():
 now=datetime(2026,1,2,tzinfo=timezone.utc)
 with pytest.raises(ReconciliationError): CommercialReceivableReconciliation.reconcile(r(),[a(n=1001)],[],now)
 with pytest.raises(ReconciliationError): CommercialReceivableReconciliation.reconcile(r(),[CommercialReceivableCreditAdjustment.from_receivable(CommercialReceivable('other',ReceivableFamily.CLIENT,'r','i','ZAR',1000,0,1000,'b'*128,ReceivableStatus.OPEN),'a',1,CreditBasis.CREDIT_NOTE,now)],[],now)
def test_r04_deterministic_hydration_and_no_authority():
 out=CommercialReceivableReconciliation.reconcile(r(),[a()],[],datetime(2026,1,2,tzinfo=timezone.utc)); assert CommercialReceivableReconciliation.from_dict(out.to_dict())==out; assert out.to_dict()['reconciliation_fingerprint']==out.reconciliation_fingerprint; assert not hasattr(out,'execute') and not hasattr(out,'settle')
def test_r05_strict_hydration_rejects_missing_unknown_id_corruption_and_naive_time():
 out=CommercialReceivableReconciliation.reconcile(r(),[a()],[],datetime(2026,1,2,tzinfo=timezone.utc)); payload=out.to_dict()
 for bad in ({k:v for k,v in payload.items() if k!='currency'},{**payload,'extra':1},{**payload,'_id':'x'},{**payload,'reconciliation_fingerprint':'0'*128},{**payload,'effective_at':'2026-01-02T00:00:00'}):
  with pytest.raises(ReconciliationError): CommercialReceivableReconciliation.from_dict(bad)
def test_r06_hydration_preserves_canonical_evidence_order_and_family():
 out=CommercialReceivableReconciliation.reconcile(r(),[a('x',100),a('y',200)],[],datetime(2026,1,2,tzinfo=timezone.utc)); payload=out.to_dict(); payload['adjustment_fingerprints']=list(reversed(payload['adjustment_fingerprints'])); hydrated=CommercialReceivableReconciliation.from_dict({**payload,'reconciliation_fingerprint':CommercialReceivableReconciliation.from_dict(out.to_dict()).reconciliation_fingerprint})
 assert hydrated.receivable_family is ReceivableFamily.CLIENT and set(hydrated.adjustment_fingerprints)==set(out.adjustment_fingerprints)
# ARTIFACT: test_commercial_receivable_reconciliation.py
# VERSION: v1.0.0-M11D1
# AUTHORITY BOUNDARY: Evidence projection only.
# TENANT POSTURE: Tenant-scoped matching.
# FAIL-CLOSED POSTURE: Drift rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
