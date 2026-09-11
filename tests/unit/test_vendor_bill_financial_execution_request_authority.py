"""TITLE: Durable AP execution-request authority certificate.
VERSION: v1.0.0-M11-P5-R1B-AP2A.
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Direct AP request issuance and replay evidence.
ABSOLUTE CANONICAL PATH: tests/unit/test_vendor_bill_financial_execution_request_authority.py
COLLABORATION / OWNERSHIP: SaaS AP authority.
CERTIFICATION / UPDATE DATE: 2026-09-07.
CHANGELOG: v1.0.0 certifies durable request authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Exact tenant-scoped request identity.
AUTHORITY BOUNDARY: Request only; no provider or execution truth.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from tools.eos.saas.domain.vendor_bill_release_authorization import VendorBillReleaseAuthorization
from tools.eos.saas.billing.vendor_bill_release_authorization_registry import VendorBillReleaseAuthorizationRegistry
from tools.eos.saas.billing.vendor_bill_financial_execution_request_issuance import issue_vendor_bill_financial_execution_request
from tools.eos.saas.billing.vendor_bill_financial_execution_request_registry import VendorBillFinancialExecutionRequestRegistry

class C:
    def __init__(self): self.rows=[]
    def with_options(self,**_): return self
    def create_index(self,*_,**__): return "idx"
    def find_one(self,q,**_): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
    def insert_one(self,r,**_): self.rows.append(dict(r))

def test_durable_ap_request_issuance_replay_and_corruption():
    now=datetime(2026,1,1,tzinfo=timezone.utc); releases=C(); requests=C(); s=SimpleNamespace(in_transaction=True)
    auth=VendorBillReleaseAuthorization("t1","rel1","pay1",1,"approval","a"*128,100,"ZAR","actor","basis",now,now)
    VendorBillReleaseAuthorizationRegistry.create(auth,"release-key",releases,session=s)  # type: ignore[arg-type]
    value,replayed=issue_vendor_bill_financial_execution_request("t1","rel1",execution_command_id="req1",idempotency_key="key",amount_minor=100,currency="ZAR",payment_destination_reference="opaque",payable_id="pay1",requested_by_actor_id="actor",requested_at=now,collection=requests,release_collection=releases,session=s)
    assert replayed is False
    same,replayed=VendorBillFinancialExecutionRequestRegistry.create(value,requests,session=s); assert replayed is True and same==value
    assert VendorBillFinancialExecutionRequestRegistry.get("t1","req1",requests,session=s)==value
    requests.rows[0]["amount_minor"]=99
    try: VendorBillFinancialExecutionRequestRegistry.get("t1","req1",requests,session=s)
    except RuntimeError as exc: assert str(exc)=="REQUEST_PERSISTED_RECORD_INVALID"
    else: raise AssertionError("corrupt request accepted")

# ARTIFACT: test_vendor_bill_financial_execution_request_authority.py
# VERSION: v1.0.0-M11-P5-R1B-AP2A
# AUTHORITY BOUNDARY: AP request certificate only
# FAIL-CLOSED POSTURE: corruption and replay conflicts reject
# END OF WILSY OS SOVEREIGN ARTIFACT
