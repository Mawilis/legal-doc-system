import os, uuid
from typing import cast
from datetime import date, datetime, timezone
from dataclasses import replace
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from tools.eos.saas.billing.financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationRegistry, FinancialApprovalPolicyEvaluationIdempotencyKeyReuseError, _compute_vendor_bill_policy_snapshot_fingerprint, _hydrate_persisted_evaluation
from tools.eos.saas.billing.financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationNotFoundError
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from tools.eos.saas.billing.vendor_bill_registry import VendorBillRegistry
from tools.eos.saas.billing.vendor_registry import VendorRegistry
from tools.eos.saas.domain.vendor import VendorIdentity
from tools.eos.saas.domain.vendor_bill import VendorBill
from tools.eos.saas.domain.financial_approval_policy_evaluation import *

def test_policy_evaluation_first_create_and_subject_boundaries_real_mongo():
 c=MongoClient(os.environ['TEST_VENDOR_MONGO_URI']); db=c['policy_eval_'+uuid.uuid4().hex]; v,b,e=db['vendors'],db['vendor_bills'],db['financial_approval_policy_evaluations']; VendorRegistry.ensure_indexes(v); VendorBillRegistry.ensure_indexes(b); FinancialApprovalPolicyEvaluationRegistry.ensure_indexes(e); vendor=VendorRegistry.create(VendorIdentity(tenant_id='a',legal_name='V'),v)
 bill=VendorBill(tenant_id='a',vendor_id=vendor.vendor_id,payable_id='p',gross_amount_minor=100,currency='ZAR',issue_date=date(2026,1,1),due_date=date(2026,2,1),received_at=datetime(2026,1,1,tzinfo=timezone.utc),approval_policy_reference='POLICY-A'); VendorBillRegistry.create(bill,b); open_bill=VendorBillRegistry.open_bill('a','p',1,'open',b).vendor_bill
 def ev(rev=2,policy='POLICY-A',fingerprint=None,tenant='a',subject='p'):
  return FinancialApprovalPolicyEvaluation(tenant_id=tenant,evaluation_id='e'+uuid.uuid4().hex,subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL,subject_id=subject,subject_revision=rev,approval_policy_reference=policy,approval_policy_version='1',approval_required=False,approval_requirements=(),rejection_rule=FinancialApprovalRejectionRule.ANY_VALID_REJECTION_BLOCKS,subject_snapshot_fingerprint=fingerprint or _compute_vendor_bill_policy_snapshot_fingerprint(open_bill),evaluator_reference='resolver',evaluated_at=datetime(2026,1,1,tzinfo=timezone.utc),created_at=datetime(2026,1,1,tzinfo=timezone.utc))
 x=ev(); result=FinancialApprovalPolicyEvaluationRegistry.create(x,'key',e); raw=e.find_one({'evaluation_id':x.evaluation_id}); assert result.outcome.value=='CREATED' and raw and _hydrate_persisted_evaluation(raw)==x
 for candidate,error in ((ev(subject='missing'), 'VENDOR_BILL_NOT_FOUND'),(ev(rev=1),'FINANCIAL_APPROVAL_POLICY_SUBJECT_REVISION_CONFLICT'),(ev(policy='POLICY-B'),'FINANCIAL_APPROVAL_POLICY_REFERENCE_MISMATCH'),(ev(fingerprint='a'*128),'FINANCIAL_APPROVAL_POLICY_SUBJECT_SNAPSHOT_MISMATCH')):
  try: FinancialApprovalPolicyEvaluationRegistry.create(candidate,'k'+uuid.uuid4().hex,e)
  except Exception as exc: assert str(exc)==error
  else: raise AssertionError(error)
 c.drop_database(db.name); c.close()

def test_policy_evaluation_duplicate_and_invalid_keys_real_mongo():
 c=MongoClient(os.environ['TEST_VENDOR_MONGO_URI']); db=c['policy_eval_'+uuid.uuid4().hex]; v,b,e=db['vendors'],db['vendor_bills'],db['financial_approval_policy_evaluations']; VendorRegistry.ensure_indexes(v); VendorBillRegistry.ensure_indexes(b); FinancialApprovalPolicyEvaluationRegistry.ensure_indexes(e); vendor=VendorRegistry.create(VendorIdentity(tenant_id='a',legal_name='V'),v)
 bill=VendorBill(tenant_id='a',vendor_id=vendor.vendor_id,payable_id='p',gross_amount_minor=100,currency='ZAR',issue_date=date(2026,1,1),due_date=date(2026,2,1),received_at=datetime(2026,1,1,tzinfo=timezone.utc),approval_policy_reference='A'); VendorBillRegistry.create(bill,b); opened=VendorBillRegistry.open_bill('a','p',1,'open',b).vendor_bill
 def ev(): return FinancialApprovalPolicyEvaluation(tenant_id='a',evaluation_id='same',subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL,subject_id='p',subject_revision=2,approval_policy_reference='A',approval_policy_version='1',approval_required=False,approval_requirements=(),rejection_rule=FinancialApprovalRejectionRule.ANY_VALID_REJECTION_BLOCKS,subject_snapshot_fingerprint=_compute_vendor_bill_policy_snapshot_fingerprint(opened),evaluator_reference='r',evaluated_at=datetime(2026,1,1,tzinfo=timezone.utc),created_at=datetime(2026,1,1,tzinfo=timezone.utc))
 first=FinancialApprovalPolicyEvaluationRegistry.create(ev(),'key',e); replay=FinancialApprovalPolicyEvaluationRegistry.create(ev(),'key',e)
 raw_replay=e.find_one({'evaluation_id':'same'}); assert raw_replay is not None
 assert first.outcome.value=='CREATED' and replay.outcome.value=='IDEMPOTENT_REPLAY' and replay.evaluation == _hydrate_persisted_evaluation(raw_replay)
 altered=ev(); object.__setattr__(altered,'evaluator_reference','different')
 try: FinancialApprovalPolicyEvaluationRegistry.create(altered,'key',e)
 except FinancialApprovalPolicyEvaluationIdempotencyKeyReuseError as x: assert str(x)=='FINANCIAL_APPROVAL_POLICY_EVALUATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND'
 else: raise AssertionError('hostile key reuse accepted')
 try: FinancialApprovalPolicyEvaluationRegistry.create(ev(),'other-key',e)
 except Exception as x: assert str(x)=='FINANCIAL_APPROVAL_POLICY_EVALUATION_CREATE_CONFLICT'
 else: raise AssertionError('different key accepted')
 assert e.count_documents({})==1
 e.update_one({'evaluation_id':'same'},{'$set':{'create_fingerprint':'bad'}})
 try: FinancialApprovalPolicyEvaluationRegistry.create(ev(),'key',e)
 except Exception as x: assert str(x)=='FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID'
 else: raise AssertionError('corrupt fingerprint accepted')
 e.update_one({'evaluation_id':'same'},{'$set':{'create_fingerprint':'a'*128,'subject_revision':'corrupt'}})
 try: FinancialApprovalPolicyEvaluationRegistry.create(ev(),'key',e)
 except Exception as x: assert str(x)=='FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID'
 else: raise AssertionError('corrupt domain field accepted')
 for key in ('','   ',None,True,123,'x'*129):
  try: FinancialApprovalPolicyEvaluationRegistry.create(ev(),cast(str,key),e)
  except FinancialApprovalPolicyEvaluationDomainError: pass
  else: raise AssertionError(key)
 assert e.count_documents({})==1; c.drop_database(db.name); c.close()

def _race_fixture(db_name):
 c=MongoClient(os.environ['TEST_VENDOR_MONGO_URI']); db=c[db_name]; v,b,e=db['vendors'],db['vendor_bills'],db['financial_approval_policy_evaluations']; VendorRegistry.ensure_indexes(v); VendorBillRegistry.ensure_indexes(b); FinancialApprovalPolicyEvaluationRegistry.ensure_indexes(e); vendor=VendorRegistry.create(VendorIdentity(tenant_id='a',legal_name='V'),v); bill=VendorBill(tenant_id='a',vendor_id=vendor.vendor_id,payable_id='p',gross_amount_minor=100,currency='ZAR',issue_date=date(2026,1,1),due_date=date(2026,2,1),received_at=datetime(2026,1,1,tzinfo=timezone.utc),approval_policy_reference='A'); VendorBillRegistry.create(bill,b); opened=VendorBillRegistry.open_bill('a','p',1,'open',b).vendor_bill; evaluation=FinancialApprovalPolicyEvaluation(tenant_id='a',evaluation_id='same',subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL,subject_id='p',subject_revision=2,approval_policy_reference='A',approval_policy_version='1',approval_required=False,approval_requirements=(),rejection_rule=FinancialApprovalRejectionRule.ANY_VALID_REJECTION_BLOCKS,subject_snapshot_fingerprint=_compute_vendor_bill_policy_snapshot_fingerprint(opened),evaluator_reference='r',evaluated_at=datetime(2026,1,1,tzinfo=timezone.utc),created_at=datetime(2026,1,1,tzinfo=timezone.utc)); return c,db,e,evaluation

def test_policy_evaluation_identical_create_concurrency_real_mongo():
 c,db,e,evaluation=_race_fixture('policy_eval_'+uuid.uuid4().hex); barrier=Barrier(100)
 def run(_): barrier.wait(); return FinancialApprovalPolicyEvaluationRegistry.create(evaluation,'key',e).outcome.value
 with ThreadPoolExecutor(max_workers=100) as pool: outcomes=list(pool.map(run,range(100)))
 assert outcomes.count('CREATED')==1 and outcomes.count('IDEMPOTENT_REPLAY')==99 and e.count_documents({})==1
 c.drop_database(db.name); c.close()

def test_policy_evaluation_different_command_identity_races_real_mongo():
 successes=conflicts=double_successes=raw_errors=unexpected=record_mismatches=0
 c,db,e,evaluation=_race_fixture('policy_eval_'+uuid.uuid4().hex)
 for _ in range(100):
  e.delete_many({}); left=replace(evaluation,evaluator_reference='left'); right=replace(evaluation,evaluator_reference='right'); barrier=Barrier(2)
  def run(item):
   try: barrier.wait(); return FinancialApprovalPolicyEvaluationRegistry.create(item[0],item[1],e).outcome.value
   except Exception as exc: return str(exc)
  with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(run,((left,'left-key'),(right,'right-key'))))
  successes += results.count('CREATED'); conflicts += results.count('FINANCIAL_APPROVAL_POLICY_EVALUATION_CREATE_CONFLICT'); double_successes += int(results.count('CREATED') != 1); raw_errors += sum('DuplicateKeyError' in x for x in results); unexpected += sum(x not in ('CREATED','FINANCIAL_APPROVAL_POLICY_EVALUATION_CREATE_CONFLICT') for x in results); record_mismatches += int(e.count_documents({}) != 1)
 assert (successes,conflicts,double_successes,raw_errors,unexpected,record_mismatches)==(100,100,0,0,0,0)
 c.drop_database(db.name); c.close()

def test_policy_evaluation_get_and_bounded_subject_list_real_mongo():
 c,db,e,base=_race_fixture('policy_eval_'+uuid.uuid4().hex)
 evaluations=[]
 for index in range(5):
  item=replace(base,evaluation_id='item-'+str(index),evaluator_reference='r'+str(index),created_at=datetime(2026,1,index+1,tzinfo=timezone.utc),evaluated_at=datetime(2026,1,index+1,tzinfo=timezone.utc))
  evaluations.append(item); FinancialApprovalPolicyEvaluationRegistry.create(item,'key-'+str(index),e)
 assert FinancialApprovalPolicyEvaluationRegistry.get('a','item-0',e)==evaluations[0]
 try: FinancialApprovalPolicyEvaluationRegistry.get('b','item-0',e)
 except FinancialApprovalPolicyEvaluationNotFoundError as exc: assert str(exc)=='FINANCIAL_APPROVAL_POLICY_EVALUATION_NOT_FOUND'
 else: raise AssertionError('cross-tenant disclosure')
 listed=FinancialApprovalPolicyEvaluationRegistry.list_for_subject('a',FinancialApprovalPolicySubjectType.VENDOR_BILL,'p',3,e)
 assert isinstance(listed,tuple) and [item.evaluation_id for item in listed]==['item-4','item-3','item-2']
 assert all(item.tenant_id=='a' for item in FinancialApprovalPolicyEvaluationRegistry.list_for_subject('a',FinancialApprovalPolicySubjectType.VENDOR_BILL,'p',250,e))
 e.update_one({'evaluation_id':'item-4'},{'$set':{'create_fingerprint':'bad'}})
 try: FinancialApprovalPolicyEvaluationRegistry.list_for_subject('a',FinancialApprovalPolicySubjectType.VENDOR_BILL,'p',3,e)
 except Exception as exc: assert str(exc)=='FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID'
 else: raise AssertionError('corrupt list record accepted')
 for invalid in (True,False,0,-1,1.5,'10',None,251):
  try: FinancialApprovalPolicyEvaluationRegistry.list_for_subject('a',FinancialApprovalPolicySubjectType.VENDOR_BILL,'p',cast(int,invalid),e)
  except FinancialApprovalPolicyEvaluationDomainError: pass
  else: raise AssertionError(invalid)
 c.drop_database(db.name); c.close()

def test_policy_evaluation_get_shared_session_real_mongo():
 c,db,e,evaluation=_race_fixture('policy_eval_'+uuid.uuid4().hex)
 FinancialApprovalPolicyEvaluationRegistry.create(evaluation,'session-key',e)
 assert FinancialApprovalPolicyEvaluationRegistry.get('a',evaluation.evaluation_id,e)==evaluation
 with c.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot'))
  assert FinancialApprovalPolicyEvaluationRegistry.get('a',evaluation.evaluation_id,e,session=session)==evaluation
  try: FinancialApprovalPolicyEvaluationRegistry.get('b',evaluation.evaluation_id,e,session=session)
  except FinancialApprovalPolicyEvaluationNotFoundError: pass
  else: raise AssertionError('cross-tenant disclosure')
  session.abort_transaction()
 e.update_one({'evaluation_id':evaluation.evaluation_id},{'$set':{'create_fingerprint':'bad'}})
 with c.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot'))
  try: FinancialApprovalPolicyEvaluationRegistry.get('a',evaluation.evaluation_id,e,session=session)
  except Exception as exc: assert str(exc)=='FINANCIAL_APPROVAL_POLICY_EVALUATION_PERSISTED_RECORD_INVALID'
  else: raise AssertionError('corruption accepted')
  session.abort_transaction()
 c.drop_database(db.name); c.close()
