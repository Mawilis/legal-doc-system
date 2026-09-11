"""WILSY OS M11D1 credit-adjustment unit certificate.
TITLE: Commercial Credit Adjustment Certificate
VERSION: v1.0.0-M11D1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies immutable credit provenance and strict minor-unit law.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_commercial_receivable_credit_adjustment.py
COLLABORATION / OWNERSHIP: M11D1 credit unit owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11D1 certifies credit boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only.
TENANT BOUNDARY: Source receivable binding is mandatory.
AUTHORITY BOUNDARY: Commercial adjustment only.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, or execution.
TRANSACTION BOUNDARY: Pure unit tests.
FAIL-CLOSED DECLARATION: Invalid amounts and provenance reject.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.domain.commercial_receivable_credit_adjustment import CommercialReceivableCreditAdjustment, CreditAdjustmentError, CreditBasis
def r(f=ReceivableFamily.CLIENT, tenant='t'):
 return CommercialReceivable(tenant,f,'r','i','ZAR',1000,0,1000,'a'*128,ReceivableStatus.OPEN)
def test_c01_platform_client_and_provenance():
 a=CommercialReceivableCreditAdjustment.from_receivable(r(ReceivableFamily.PLATFORM), 'a1',100,CreditBasis.CREDIT_NOTE,datetime(2026,1,1,tzinfo=timezone.utc)); assert a.receivable_family is ReceivableFamily.PLATFORM and a.source_invoice_id=='i'
 assert CommercialReceivableCreditAdjustment.from_receivable(r(), 'a1',100,CreditBasis.SERVICE_CREDIT,datetime(2026,1,1,tzinfo=timezone.utc)).tenant_id=='t'
@pytest.mark.parametrize('amount',[0,-1,True,1.5])
def test_c02_invalid_amount(amount):
 with pytest.raises(CreditAdjustmentError): CommercialReceivableCreditAdjustment.from_receivable(r(),'a',amount,CreditBasis.CREDIT_NOTE,datetime(2026,1,1,tzinfo=timezone.utc))
def test_c03_round_trip_drift_unknown_id_and_fingerprint():
 a=CommercialReceivableCreditAdjustment.from_receivable(r(),'a',100,CreditBasis.CREDIT_NOTE,datetime(2026,1,1,tzinfo=timezone.utc)); p=a.to_dict(); assert CommercialReceivableCreditAdjustment.from_dict(p)==a
 with pytest.raises(CreditAdjustmentError): CommercialReceivableCreditAdjustment.from_dict({**p,'_id':'x'})
 with pytest.raises(CreditAdjustmentError): CommercialReceivableCreditAdjustment.from_dict({**p,'amount_minor':101})
def test_c04_no_execution_authority():
 a=CommercialReceivableCreditAdjustment.from_receivable(r(),'a',100,CreditBasis.CREDIT_NOTE,datetime(2026,1,1,tzinfo=timezone.utc)); assert not hasattr(a,'paid') and not hasattr(a,'execute')
# ARTIFACT: test_commercial_receivable_credit_adjustment.py
# VERSION: v1.0.0-M11D1
# AUTHORITY BOUNDARY: Commercial adjustment only.
# TENANT POSTURE: Source-bound.
# FAIL-CLOSED POSTURE: Invalid evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
