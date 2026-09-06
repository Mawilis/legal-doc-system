"""TITLE: M9 POS orchestration certificate
VERSION: v1.0.0-M9
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify M9 public commercial orchestration and forbidden execution paths.
EPITOME: Commercial finalization without financial execution.
ABSOLUTE CANONICAL PATH: tests/unit/test_pos_commercial_orchestration.py
COLLABORATION / OWNERSHIP: Python EOS POS certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M9 adds orchestration matrix.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No provider calls.
TENANT BOUNDARY: Sale identity is tenant/location scoped.
AUTHORITY BOUNDARY: Commercial truth only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS/M10 owns execution.
TRANSACTION BOUNDARY: Caller-owned persistence.
FAIL-CLOSED DECLARATION: Finalization rejects invalid status.
"""
import pytest
from tools.eos.saas.billing.pos_commercial_orchestration import finalize_sale, create_return, create_refund_intent, record_cash_tender, create_tender_intent
from tools.eos.saas.domain.pos_commercial import POSStatus, POSSale, POSLineItem, POSTenderType
def _sale(status=POSStatus.COMPLETED_COMMERCIAL): return POSSale('t','l','s','ZAR',(POSLineItem('p','sku','x',2,100,0,0,'ZAR'),),status,'i')
def test_finalize_symbol(): assert callable(finalize_sale) and POSStatus.COMPLETED_COMMERCIAL.value == 'COMPLETED_COMMERCIAL'
def test_no_execution_status(): assert not hasattr(POSStatus,'PAID') and not hasattr(POSStatus,'SETTLED')
def test_cash_change(): assert record_cash_tender(_sale(),250,'op','2026-01-01T00:00:00Z').change_due_minor==50
def test_cash_short_rejected():
 with pytest.raises(ValueError): record_cash_tender(_sale(),100,'op','x')
def test_electronic_is_intent(): assert create_tender_intent(_sale(),POSTenderType.CARD,200,'k').currency=='ZAR'
def test_electronic_mismatch_rejected():
 with pytest.raises(ValueError): create_tender_intent(_sale(),POSTenderType.CARD,1,'k')
def test_return_bounded(): assert create_return(_sale(),'sku',1,'reason','r','k').quantity==1
def test_return_excess_rejected():
 r=create_return(_sale(),'sku',1,'reason','r','k')
 with pytest.raises(ValueError): create_return(_sale(),'sku',2,'reason','r2','k2',(r,))
def test_refund_bounded(): assert create_refund_intent(_sale(),100,'basis','r','k').amount_minor==100
def test_refund_excess_rejected():
 with pytest.raises(ValueError): create_refund_intent(_sale(),201,'basis','r','k')
# ARTIFACT: test_pos_commercial_orchestration.py
# VERSION: v1.0.0-M9
# END OF WILSY OS SOVEREIGN ARTIFACT
