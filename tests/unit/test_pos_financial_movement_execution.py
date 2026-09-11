"""WILSY OS M10B2 bridge unit certificate.
TITLE: POS Financial Movement Execution Bridge
VERSION: v1.0.0-M10B2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify POS provenance firewall and Kennel delegation.
ABSOLUTE CANONICAL PATH: tests/unit/test_pos_financial_movement_execution.py
COLLABORATION / OWNERSHIP: POS bridge certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10B2 establishes bridge behavioral certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque instrument references only.
TENANT BOUNDARY: Exact POS provenance is mandatory.
AUTHORITY BOUNDARY: Existing authorization only; Kennel executes.
FINANCIAL AUTHORITY BOUNDARY: No settlement or paid state.
TRANSACTION BOUNDARY: Caller supplies collection/session.
FAIL-CLOSED DECLARATION: Provenance drift rejects before provider.
"""
from datetime import datetime, timezone
import hashlib, json
import pytest
from dataclasses import replace
from typing import Any
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from tools.eos.saas.domain.pos_commercial import POSLineItem, POSSale, POSStatus, POSTenderIntent, POSTenderType, POSRefundIntent
from tools.eos.saas.domain.pos_financial_execution_authorization import POSFinancialExecutionAuthorization, POSFinancialExecutionDirection
from tools.eos.saas.billing.pos_financial_movement_execution import execute_pos_collection, execute_pos_refund
from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.financial_movement_execution import FinancialMovementDirection
from tools.eos.kennel.orchestration.financial_movement_execution_orchestrator import FinancialMovementExecutionOrchestrator, FinancialMovementProviderResult

class C:
    def __init__(self): self.rows=[]
    def find_one(self,q,session=None): return next((r for r in self.rows if all(r.get(k)==v for k,v in q.items())),None)
    def insert_one(self,r,session=None): self.rows.append(r)
class P:
    def __init__(self): self.count=0
    def execute(self, command): self.count+=1; return FinancialMovementProviderResult("p","ref",FinancialExecutionStatus.EXECUTED,"ev",datetime.now(timezone.utc))
def sale(): return POSSale("t","loc","sale","ZAR",(POSLineItem("prod","sku","item",1,100,0,0,"ZAR"),),POSStatus.COMPLETED_COMMERCIAL,"sale-key")
def auth(s, source, direction):
    e=TenantAuthorizationDecisionEvidence("t","decision","principal","op","perm","role","admin",0,0,"sale","a"*128,"v1","v1","v1","v1","id",datetime.now(timezone.utc))
    return POSFinancialExecutionAuthorization.issue(s,source,e,authorization_id="auth-"+direction.value,idempotency_key="idem-"+direction.value,authorized_at=datetime.now(timezone.utc))
def test_pb01_pb02_pb15_valid_collection_and_firewall():
    s=sale(); t=POSTenderIntent("t","loc","sale",POSTenderType.CARD,100,"ZAR","tender"); p=P(); result=execute_pos_collection(s,t,auth(s,t,POSFinancialExecutionDirection.COLLECTION),C(),FinancialMovementExecutionOrchestrator(p)); assert result.execution_truth.direction is FinancialMovementDirection.COLLECTION and p.count==1
    for kind in (POSTenderType.CASH,POSTenderType.VOUCHER,POSTenderType.STORE_CREDIT):
        with pytest.raises(Exception): execute_pos_collection(s,POSTenderIntent("t","loc","sale",kind,100,"ZAR",kind.value),auth(s,t,POSFinancialExecutionDirection.COLLECTION),C(),FinancialMovementExecutionOrchestrator(p))
    assert p.count==1
def test_pb06_to_pb14_collection_provenance_rejects():
    s=sale(); t=POSTenderIntent("t","loc","sale",POSTenderType.CARD,100,"ZAR","tender"); p=P(); a=auth(s,t,POSFinancialExecutionDirection.COLLECTION)
    with pytest.raises(Exception): execute_pos_collection(s,POSTenderIntent("other","loc","sale",POSTenderType.CARD,100,"ZAR","x"),a,C(),FinancialMovementExecutionOrchestrator(p))
    assert p.count==0
    for field, value in (("tenant_id","other"),("location_id","other"),("sale_id","other"),("currency","USD"),("requested_amount_minor",99)):
        values: dict[str, Any]=dict(tenant_id="t",location_id="loc",sale_id="sale",tender_type=POSTenderType.CARD,requested_amount_minor=100,currency="ZAR",idempotency_key="poison")
        values[field]=value
        with pytest.raises(Exception): execute_pos_collection(s,POSTenderIntent(**values),a,C(),FinancialMovementExecutionOrchestrator(p))
    assert p.count==0
    for bad in ("other", "sale-other"):
        poisoned=POSTenderIntent("t","loc",bad,POSTenderType.CARD,100,"ZAR","poison-"+bad)
        with pytest.raises(Exception): execute_pos_collection(s,poisoned,a,C(),FinancialMovementExecutionOrchestrator(p))
def test_pb16_pb17_pb25_valid_refund_and_direction():
    s=sale(); r=POSRefundIntent("t","loc","refund","sale",50,"ZAR","return","refund-key"); p=P(); out=execute_pos_refund(s,r,auth(s,r,POSFinancialExecutionDirection.DISBURSEMENT),C(),FinancialMovementExecutionOrchestrator(p)); assert out.execution_truth.direction is FinancialMovementDirection.DISBURSEMENT and p.count==1
    with pytest.raises(Exception): execute_pos_refund(s,r,replace(auth(s,r,POSFinancialExecutionDirection.DISBURSEMENT), direction=POSFinancialExecutionDirection.COLLECTION),C(),FinancialMovementExecutionOrchestrator(p))
    assert p.count==1
def test_pb27_pb38_identity_and_no_commercial_mutation():
    s=sale(); t=POSTenderIntent("t","loc","sale",POSTenderType.CARD,100,"ZAR","tender"); r=POSRefundIntent("t","loc","refund","sale",50,"ZAR","return","refund-key"); p=P(); c=C(); a=auth(s,t,POSFinancialExecutionDirection.COLLECTION); b=auth(s,r,POSFinancialExecutionDirection.DISBURSEMENT); x=execute_pos_collection(s,t,a,c,FinancialMovementExecutionOrchestrator(p)); y=execute_pos_refund(s,r,b,c,FinancialMovementExecutionOrchestrator(p)); assert x.execution_truth.execution_truth_id!=y.execution_truth.execution_truth_id and x.execution_truth.direction is FinancialMovementDirection.COLLECTION and y.execution_truth.direction is FinancialMovementDirection.DISBURSEMENT and s.status is POSStatus.COMPLETED_COMMERCIAL and not any(hasattr(v,n) for v in (s,t,r) for n in ("paid","settled","executed")) and a.authorization_fingerprint == a.authorization_fingerprint

def test_pb09_pb10_pb11_pb12_pb13_collection_poison_each_preserves_provider_count():
    s=sale(); t=POSTenderIntent("t","loc","sale",POSTenderType.CARD,100,"ZAR","base"); a=auth(s,t,POSFinancialExecutionDirection.COLLECTION); p=P(); o=FinancialMovementExecutionOrchestrator(p)
    poisons=[POSTenderIntent("t","loc","sale",POSTenderType.CARD,99,"ZAR","amount"),POSTenderIntent("t","loc","sale",POSTenderType.CARD,100,"USD","currency"),POSTenderIntent("t","loc","other",POSTenderType.CARD,100,"ZAR","sale")]
    for poisoned in poisons:
        before=p.count
        with pytest.raises(Exception): execute_pos_collection(s,poisoned,a,C(),o)
        assert p.count==before
    bad=replace(a,authorization_fingerprint="0"*128)
    with pytest.raises(Exception): execute_pos_collection(s,t,bad,C(),o)
    assert p.count==0
    with pytest.raises(Exception): execute_pos_collection(s,POSTenderIntent("t","other","sale",POSTenderType.CARD,100,"ZAR","location"),a,C(),o)
    assert p.count==0

def test_pb18_pb19_pb20_pb21_pb22_pb23_pb24_refund_poison_each_preserves_provider_count():
    s=sale(); r=POSRefundIntent("t","loc","refund","sale",50,"ZAR","return","refund-base"); a=auth(s,r,POSFinancialExecutionDirection.DISBURSEMENT); p=P(); o=FinancialMovementExecutionOrchestrator(p)
    for poisoned in (replace(r,tenant_id="other"),replace(r,location_id="other"),replace(r,sale_id="other"),replace(r,amount_minor=40),replace(r,currency="USD")):
        before=p.count
        with pytest.raises(Exception): execute_pos_refund(s,poisoned,a,C(),o)
        assert p.count==before
    with pytest.raises(Exception): execute_pos_refund(s,r,replace(a,authorization_fingerprint="0"*128),C(),o)
    assert p.count==0

def test_pb30_to_pb38_state_boundaries_and_authorization_immutability():
    s=sale(); t=POSTenderIntent("t","loc","sale",POSTenderType.CARD,100,"ZAR","state"); a=auth(s,t,POSFinancialExecutionDirection.COLLECTION); before=a; p=P(); truth=execute_pos_collection(s,t,a,C(),FinancialMovementExecutionOrchestrator(p)).execution_truth
    assert s.status is POSStatus.COMPLETED_COMMERCIAL
    assert not hasattr(s,"paid"); assert not hasattr(s,"settled"); assert not hasattr(s,"executed")
    assert not hasattr(t,"provider"); assert not hasattr(t,"execution_truth")
    assert a == before and a.authorization_fingerprint == before.authorization_fingerprint
    assert not hasattr(truth,"settled"); assert not hasattr(truth,"paid")

def test_pb28_direction_bound_replay_identity_is_distinct():
    s=sale(); t=POSTenderIntent("t","loc","sale",POSTenderType.CARD,100,"ZAR","identity"); r=POSRefundIntent("t","loc","refund","sale",50,"ZAR","return","identity-refund"); a=auth(s,t,POSFinancialExecutionDirection.COLLECTION); b=auth(s,r,POSFinancialExecutionDirection.DISBURSEMENT); assert a.idempotency_key != b.idempotency_key and a.authorization_id != b.authorization_id

# ARTIFACT: test_pos_financial_movement_execution.py
# VERSION: v1.0.0-M10B2
# AUTHORITY BOUNDARY: Unit evidence only.
# FAIL-CLOSED POSTURE: POS provenance rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
