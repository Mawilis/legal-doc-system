"""WILSY OS M10B2 real-Mongo certificate.
TITLE: POS Financial Movement Execution Real-Mongo Certificate
VERSION: v1.1.0-M10B2
AUTHORITY: Wilsy OS Core Governance
EPITOME: Six bounded POS-to-Kennel host scenarios.
ABSOLUTE CANONICAL PATH: tests/integration/test_pos_financial_movement_execution_real_mongo.py
COLLABORATION / OWNERSHIP: POS bridge integration certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.1.0-M10B2 isolates every host run in a unique certificate database.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers and deterministic provider.
TENANT BOUNDARY: Certificate-owned database.
AUTHORITY BOUNDARY: Kennel execution evidence only.
FINANCIAL AUTHORITY BOUNDARY: No settlement or paid inference.
TRANSACTION BOUNDARY: Certificate owns client/session.
FAIL-CLOSED DECLARATION: Missing TEST_VENDOR_MONGO_URI fails hard.
"""
import os
import uuid
import pytest
from pymongo import MongoClient
from datetime import datetime, timezone
from tools.eos.auth.tenant_authorization_decision_evidence import TenantAuthorizationDecisionEvidence
from tools.eos.saas.domain.pos_commercial import POSLineItem, POSSale, POSStatus, POSTenderIntent, POSTenderType, POSRefundIntent
from tools.eos.saas.billing.pos_financial_execution_authorization_issuance import issue_pos_collection_execution_authorization, issue_pos_refund_execution_authorization
from tools.eos.saas.billing.pos_financial_movement_execution import execute_pos_collection, execute_pos_refund
from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.financial_movement_execution import FinancialMovementDirection, FinancialMovementExecutionTruth
from tools.eos.kennel.orchestration.financial_movement_execution_orchestrator import FinancialMovementExecutionOrchestrator, FinancialMovementProviderResult
from tools.eos.kennel.registry.financial_movement_execution_registry import FinancialMovementExecutionRegistry

CERTIFICATE_DATABASE_SCOPE = "RUN_UNIQUE"
CERTIFICATE_CLEANUP_SCOPE = "CERTIFICATE_OWNED_ONLY"
CROSS_RUN_STALE_AUTHORIZATION_COLLISION = "IMPOSSIBLE_BY_CONSTRUCTION"
CROSS_RUN_STALE_EXECUTION_COLLISION = "IMPOSSIBLE_BY_CONSTRUCTION"

@pytest.fixture(scope="module")
def runtime():
    uri=os.environ.get("TEST_VENDOR_MONGO_URI")
    if not uri: raise RuntimeError("TEST_VENDOR_MONGO_URI is required")
    client=MongoClient(uri, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    database_name = f"wilsy_m10b2_cert_{uuid.uuid4().hex}"
    try:
        yield client, database_name
    finally:
        client.drop_database(database_name)
        client.close()

class Provider:
    def __init__(self): self.count=0
    def execute(self, command): self.count+=1; return FinancialMovementProviderResult("cert-provider", "ref-"+command.execution_command_id, FinancialExecutionStatus.EXECUTED, "evidence", datetime.now(timezone.utc))
class ScenarioDatabase:
    def __init__(self, database, scenario): self._database=database; self._scenario=scenario
    def __getitem__(self, name): return self._database[f"{name}_{self._scenario}"] if name in ("authorizations", "execution_truth") else self._database[name]
_scenario_counter = 0
def setup(runtime, scenario=None):
    global _scenario_counter
    if scenario is None:
        _scenario_counter += 1
        scenario = f"rm_posk{_scenario_counter:02d}"
    client, database_name = runtime
    db=client[database_name]; c=db[f"execution_truth_{scenario}"]; auth=db[f"authorizations_{scenario}"]; c.delete_many({}); auth.delete_many({}); s=POSSale("tenant","location","sale","ZAR",(POSLineItem("p","sku","item",1,100,0,0,"ZAR"),),POSStatus.COMPLETED_COMMERCIAL,"sale-key"); e=TenantAuthorizationDecisionEvidence("tenant","decision","principal","op","perm","role","admin",0,0,"sale","a"*128,"v1","v1","v1","v1","idem",datetime.now(timezone.utc)); return ScenarioDatabase(db, scenario),c,s,e

def test_rm_posk01_canonical_collection(runtime):
    db,c,s,e=setup(runtime); t=POSTenderIntent("tenant","location","sale",POSTenderType.CARD,100,"ZAR","collect"); a=issue_pos_collection_execution_authorization(s,t,e,db["authorizations"],authorization_id="auth",idempotency_key="collect"); p=Provider(); out=execute_pos_collection(s,t,a,c,FinancialMovementExecutionOrchestrator(p)); hydrated=FinancialMovementExecutionRegistry.get_by_idempotency_key("tenant","POS","sale",FinancialMovementDirection.COLLECTION,"collect",c); assert out.execution_truth.direction is FinancialMovementDirection.COLLECTION and out.execution_truth.authority_subject_kind == "POS" and out.execution_truth.authority_subject_id == "sale" and p.count==1 and hydrated == out.execution_truth
def test_rm_posk02_provenance_poison(runtime):
    db,c,s,e=setup(runtime); t=POSTenderIntent("tenant","location","sale",POSTenderType.CARD,100,"ZAR","poison"); a=issue_pos_collection_execution_authorization(s,t,e,db["authorizations"],authorization_id="auth2",idempotency_key="poison"); p=Provider()
    with pytest.raises(Exception): execute_pos_collection(s,POSTenderIntent("other","location","sale",POSTenderType.CARD,100,"ZAR","x"),a,c,FinancialMovementExecutionOrchestrator(p))
    assert p.count==0 and c.count_documents({})==0
def test_rm_posk03_identical_replay(runtime):
    db,c,s,e=setup(runtime); t=POSTenderIntent("tenant","location","sale",POSTenderType.CARD,100,"ZAR","replay"); a=issue_pos_collection_execution_authorization(s,t,e,db["authorizations"],authorization_id="auth3",idempotency_key="replay"); p=Provider(); o=FinancialMovementExecutionOrchestrator(p); x=execute_pos_collection(s,t,a,c,o); y=execute_pos_collection(s,t,a,c,o); assert p.count==1 and c.count_documents({})==1 and x.execution_truth.execution_truth_id==y.execution_truth.execution_truth_id
def test_rm_posk04_divergent_replay(runtime):
    db,c,s,e=setup(runtime); t=POSTenderIntent("tenant","location","sale",POSTenderType.CARD,100,"ZAR","diverge"); a=issue_pos_collection_execution_authorization(s,t,e,db["authorizations"],authorization_id="auth4",idempotency_key="diverge"); p=Provider(); o=FinancialMovementExecutionOrchestrator(p); first=execute_pos_collection(s,t,a,c,o); object.__setattr__(a,"amount_minor",99)
    with pytest.raises(Exception): execute_pos_collection(s,t,a,c,o)
    assert p.count==1 and c.count_documents({})==1 and c.find_one({"execution_truth_id":first.execution_truth.execution_truth_id}) is not None
def test_rm_posk05_canonical_refund(runtime):
    db,c,s,e=setup(runtime); r=POSRefundIntent("tenant","location","refund","sale",50,"ZAR","return","refund"); a=issue_pos_refund_execution_authorization(s,r,e,db["authorizations"],authorization_id="auth5",idempotency_key="refund"); p=Provider(); out=execute_pos_refund(s,r,a,c,FinancialMovementExecutionOrchestrator(p)); assert out.execution_truth.direction is FinancialMovementDirection.DISBURSEMENT and out.execution_truth.executed_amount_minor==50 and p.count==1
def test_rm_posk06_cash_and_settlement_firewall(runtime):
    db,c,s,e=setup(runtime); t=POSTenderIntent("tenant","location","sale",POSTenderType.CASH,100,"ZAR","cash"); p=Provider()
    with pytest.raises(Exception): issue_pos_collection_execution_authorization(s,t,e,db["authorizations"],authorization_id="auth6",idempotency_key="cash")
    assert p.count==0 and c.count_documents({})==0 and not hasattr(s,"paid") and not hasattr(s,"settled")

# ARTIFACT: test_pos_financial_movement_execution_real_mongo.py
# VERSION: v1.1.0-M10B2
# AUTHORITY BOUNDARY: Integration evidence only.
# FAIL-CLOSED POSTURE: Missing Mongo configuration fails hard.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
