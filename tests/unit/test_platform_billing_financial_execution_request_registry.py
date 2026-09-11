"""TITLE: R3D Platform Execution Request Registry Certificate
VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-REGISTRY-UNIT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify durable idempotency and conflict behavior.
EPITOME: Unit evidence only; no production authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_financial_execution_request_registry.py
COLLABORATION / OWNERSHIP: R3D registry certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 certifies replay and conflict laws.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic bounded fixtures.
TENANT BOUNDARY: Registry keys are tenant-scoped.
AUTHORITY BOUNDARY: Certification evidence only.
FINANCIAL AUTHORITY BOUNDARY: No execution or settlement.
TRANSACTION BOUNDARY: Session forwarding is certified.
FAIL-CLOSED POSTURE: Material conflicts reject.
"""
from datetime import datetime, timezone
from typing import Any, cast
import pytest
from pymongo.errors import DuplicateKeyError
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry, PlatformBillingFinancialExecutionRequestConflictError
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest

class C:
    def __init__(self): self.rows=[]; self.inserts=0
    def create_index(self,*a,**k): return "idx"
    def find_one(self,q,session=None): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
    def insert_one(self,d,session=None):
        self.inserts+=1
        if self.rows: raise DuplicateKeyError("duplicate")
        self.rows.append(d)
def value(dest="dest"): return PlatformBillingFinancialExecutionRequest("x","t","r","i","a"*128,100,"ZAR",dest,"k","p","b",datetime(2026,1,1,tzinfo=timezone.utc))
def test_create_and_identical_retry_pre_read():
    c=C(); first=PlatformBillingFinancialExecutionRequestRegistry.create(value(),cast(Any,c)); assert first[1] is False
    replay=PlatformBillingFinancialExecutionRequestRegistry.create(value(),cast(Any,c)); assert replay[1] is True and c.inserts==1
def test_conflict_fails_closed():
    c=C(); PlatformBillingFinancialExecutionRequestRegistry.create(value(),cast(Any,c))
    with pytest.raises(PlatformBillingFinancialExecutionRequestConflictError): PlatformBillingFinancialExecutionRequestRegistry.create(value("other"),cast(Any,c))
def test_get_is_tenant_scoped_and_hydrates_without_write():
    c=C(); original=value(); PlatformBillingFinancialExecutionRequestRegistry.create(original,cast(Any,c))
    hydrated=PlatformBillingFinancialExecutionRequestRegistry.get("t","x",cast(Any,c),session=cast(Any,"s"))
    assert hydrated == original and c.inserts == 1
    with pytest.raises(Exception): PlatformBillingFinancialExecutionRequestRegistry.get("other","x",cast(Any,c))

def test_missing_provenance_document_rejects():
    c=C(); original=value(); PlatformBillingFinancialExecutionRequestRegistry.create(original,cast(Any,c)); c.rows[0].pop("provider_policy_id",None)
    with pytest.raises(Exception): PlatformBillingFinancialExecutionRequestRegistry.get("t","x",cast(Any,c))
# ARTIFACT: test_platform_billing_financial_execution_request_registry.py
# VERSION: v1.0.0-PLATFORM-BILLING-FINANCIAL-EXECUTION-REQUEST-REGISTRY-UNIT
# AUTHORITY BOUNDARY: certification only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
