"""TITLE: R3D Platform Execution Request Domain Certificate
VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-UNIT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify immutable R3C3-derived request laws.
EPITOME: Unit evidence only; no production authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_financial_execution_request.py
COLLABORATION / OWNERSHIP: R3D domain certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 certifies domain invariants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic values only.
TENANT BOUNDARY: Tenant identity is asserted.
AUTHORITY BOUNDARY: Certification evidence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement.
TRANSACTION BOUNDARY: No database transaction.
FAIL-CLOSED POSTURE: Invalid domain values are rejected.
"""
from datetime import datetime, timezone
from typing import Any
import pytest
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest, PlatformBillingFinancialExecutionRequestError
from tools.eos.saas.domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization

T=datetime(2026,1,1,tzinfo=timezone.utc)
def auth(): return PlatformBillingReleaseAuthorization("t","r","i","a"*128,"e","b"*128,100,"ZAR","p","basis","dest-ref","key",T,T)
def test_derives_exact_r3c3_provenance():
    r=PlatformBillingFinancialExecutionRequest.from_release_authorization(auth(),"x",T)
    assert r.tenant_id=="t" and r.release_authorization_id=="r" and r.platform_invoice_id=="i" and r.amount_minor==100 and r.currency=="ZAR" and r.payment_destination_reference=="dest-ref"
    with pytest.raises((AttributeError, TypeError)): setattr(r, "amount_minor", 1)
@pytest.mark.parametrize("field,value",[("tenant_id"," "),("amount_minor",0),("currency","zar"),("requested_at",datetime(2026,1,1))])
def test_invalid_request_rejected(field,value):
    values=dict(execution_request_id="x",tenant_id="t",release_authorization_id="r",platform_invoice_id="i",release_authorization_fingerprint="a"*128,amount_minor=100,currency="ZAR",payment_destination_reference="dest",idempotency_key="k",requested_by_principal_id="p",authorization_basis_reference="b",requested_at=T); values[field]=value
    with pytest.raises(PlatformBillingFinancialExecutionRequestError): PlatformBillingFinancialExecutionRequest(**(values))  # type: ignore[arg-type]
def test_fingerprint_deterministic_and_provider_neutral():
    r=PlatformBillingFinancialExecutionRequest.from_release_authorization(auth(),"x",T); assert r.fingerprint==r.fingerprint and len(r.fingerprint)==128
    assert not any(hasattr(r,n) for n in ("provider_transaction_id","settlement_id","paid_state","kennel_command_id","payable_id"))
# ARTIFACT: test_platform_billing_financial_execution_request.py
# VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-UNIT
# AUTHORITY BOUNDARY: certification only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
