import os, uuid
from datetime import date, datetime, timezone
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from tools.eos.saas.domain.vendor import VendorIdentity
from tools.eos.saas.domain.vendor_bill import VendorBill
from tools.eos.saas.domain.financial_approval_policy_evaluation import *
from tools.eos.saas.domain.financial_approval_decision import FinancialApprovalDecision, FinancialApprovalDecisionType, FinancialApprovalSubjectType as DecisionSubjectType
from tools.eos.saas.domain.financial_approval_actor_authorization import FinancialApprovalActorAuthorization
from tools.eos.saas.billing.vendor_registry import VendorRegistry
from tools.eos.saas.billing.vendor_bill_registry import VendorBillRegistry
from tools.eos.saas.billing.financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationRegistry, _compute_vendor_bill_policy_snapshot_fingerprint
from tools.eos.saas.billing.financial_approval_decision_registry import FinancialApprovalDecisionRegistry, FinancialApprovalDecisionPersistedRecordInvalidError
from tools.eos.saas.billing.financial_approval_actor_authorization_registry import FinancialApprovalActorAuthorizationRegistry

def test_cross_registry_shared_snapshot_real_mongo():
 client=MongoClient(os.environ['TEST_VENDOR_MONGO_URI']); db=client['shared_snapshot_'+uuid.uuid4().hex]; vendors,bills,evaluations,decisions,authorizations=[db[x] for x in ('vendors','vendor_bills','financial_approval_policy_evaluations','financial_approval_decisions','financial_approval_actor_authorizations')]
 VendorRegistry.ensure_indexes(vendors); VendorBillRegistry.ensure_indexes(bills); FinancialApprovalPolicyEvaluationRegistry.ensure_indexes(evaluations); FinancialApprovalDecisionRegistry.ensure_indexes(decisions); FinancialApprovalActorAuthorizationRegistry.ensure_indexes(authorizations)
 vendor=VendorRegistry.create(VendorIdentity(tenant_id='tenant-a',legal_name='V'),vendors); bill=VendorBill(tenant_id='tenant-a',vendor_id=vendor.vendor_id,payable_id='payable-1',gross_amount_minor=100,currency='ZAR',issue_date=date(2026,1,1),due_date=date(2026,2,1),received_at=datetime(2026,1,1,tzinfo=timezone.utc),approval_policy_reference='POL'); VendorBillRegistry.create(bill,bills); opened=VendorBillRegistry.open_bill('tenant-a','payable-1',1,'open',bills).vendor_bill; requirement=FinancialApprovalRequirement('req','CFO',1); evaluation=FinancialApprovalPolicyEvaluation(tenant_id='tenant-a',evaluation_id='eval-1',subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL,subject_id='payable-1',subject_revision=2,approval_policy_reference='POL',approval_policy_version='1',approval_required=True,approval_requirements=(requirement,),rejection_rule=FinancialApprovalRejectionRule.ANY_VALID_REJECTION_BLOCKS,subject_snapshot_fingerprint=_compute_vendor_bill_policy_snapshot_fingerprint(opened),evaluator_reference='resolver',evaluated_at=datetime(2026,1,1,tzinfo=timezone.utc),created_at=datetime(2026,1,1,tzinfo=timezone.utc)); FinancialApprovalPolicyEvaluationRegistry.create(evaluation,'eval-key',evaluations)
 def decision(i,actor='actor-a'):
  return FinancialApprovalDecision(tenant_id='tenant-a',decision_id=i,subject_type=DecisionSubjectType.VENDOR_BILL,subject_id='payable-1',decision=FinancialApprovalDecisionType.APPROVED,actor_id=actor,actor_capacity='CFO',reason='ok',approval_policy_reference='POL',approval_policy_version='1',subject_revision=2,decided_at=datetime(2026,1,1,tzinfo=timezone.utc),created_at=datetime(2026,1,1,tzinfo=timezone.utc))
 def auth(i,actor='actor-a'):
  return FinancialApprovalActorAuthorization(tenant_id='tenant-a',authorization_id=i,subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL,subject_id='payable-1',subject_revision=2,evaluation_id='eval-1',approval_policy_reference='POL',approval_policy_version='1',requirement_id='req',actor_id=actor,actor_capacity='CFO',authorization_source_reference='rbac',authorization_basis_reference='grant',authorized_at=datetime(2026,1,1,tzinfo=timezone.utc),authorization_evidence_fingerprint='a'*128,created_at=datetime(2026,1,1,tzinfo=timezone.utc))
 FinancialApprovalDecisionRegistry.create(decision('decision-a'),'decision-a-key',decisions); FinancialApprovalActorAuthorizationRegistry.create(auth('auth-a'),'auth-a-key',authorizations)
 with client.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot'))
  assert FinancialApprovalPolicyEvaluationRegistry.get('tenant-a','eval-1',evaluations,session=session)==evaluation
  FinancialApprovalDecisionRegistry.create(decision('decision-b','actor-b'),'decision-b-key',decisions); FinancialApprovalActorAuthorizationRegistry.create(auth('auth-b','actor-b'),'auth-b-key',authorizations)
  assert [d.decision_id for d in FinancialApprovalDecisionRegistry.list_for_subject('tenant-a',DecisionSubjectType.VENDOR_BILL,'payable-1',100,decisions,session=session)]==['decision-a']
  assert [a.authorization_id for a in FinancialApprovalActorAuthorizationRegistry.list_for_requirement('tenant-a','eval-1','req',100,authorizations,session=session)]==['auth-a']
  assert FinancialApprovalDecisionRegistry.list_for_subject('tenant-b',DecisionSubjectType.VENDOR_BILL,'payable-1',100,decisions,session=session)==[]
  assert FinancialApprovalActorAuthorizationRegistry.list_for_requirement('tenant-b','eval-1','req',100,authorizations,session=session)==()
  assert session.in_transaction
  session.abort_transaction()
 assert [d.decision_id for d in FinancialApprovalDecisionRegistry.list_for_subject('tenant-a',DecisionSubjectType.VENDOR_BILL,'payable-1',100,decisions)]==['decision-a','decision-b']
 assert [a.authorization_id for a in FinancialApprovalActorAuthorizationRegistry.list_for_requirement('tenant-a','eval-1','req',100,authorizations)]==['auth-a','auth-b']
 decisions.update_one({'decision_id':'decision-a'},{'$set':{'create_fingerprint':'bad'}})
 with client.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot'))
  try: FinancialApprovalDecisionRegistry.list_for_subject('tenant-a',DecisionSubjectType.VENDOR_BILL,'payable-1',100,decisions,session=session)
  except FinancialApprovalDecisionPersistedRecordInvalidError: pass
  else: raise AssertionError('corrupt evidence accepted')
  session.abort_transaction()
 client.drop_database(db.name); client.close()
