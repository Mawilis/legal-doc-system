import os, uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from threading import Barrier
from dataclasses import replace
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from tools.eos.saas.domain.vendor import VendorIdentity
from tools.eos.saas.domain.vendor_bill import VendorBill
from tools.eos.saas.domain.financial_approval_policy_evaluation import *
from tools.eos.saas.domain.financial_approval_actor_authorization import *
from tools.eos.saas.billing.vendor_registry import VendorRegistry
from tools.eos.saas.billing.vendor_bill_registry import VendorBillRegistry
from tools.eos.saas.billing.financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationRegistry, _compute_vendor_bill_policy_snapshot_fingerprint
from tools.eos.saas.billing.financial_approval_actor_authorization_registry import *

def fixture():
 c=MongoClient(os.environ['TEST_VENDOR_MONGO_URI']); db=c['actor_auth_'+uuid.uuid4().hex]; v,b,p,a=db['vendors'],db['vendor_bills'],db['financial_approval_policy_evaluations'],db['financial_approval_actor_authorizations']; VendorRegistry.ensure_indexes(v); VendorBillRegistry.ensure_indexes(b); FinancialApprovalPolicyEvaluationRegistry.ensure_indexes(p); FinancialApprovalActorAuthorizationRegistry.ensure_indexes(a); vendor=VendorRegistry.create(VendorIdentity(tenant_id='t',legal_name='V'),v); bill=VendorBill(tenant_id='t',vendor_id=vendor.vendor_id,payable_id='p',gross_amount_minor=100,currency='ZAR',issue_date=date(2026,1,1),due_date=date(2026,2,1),received_at=datetime(2026,1,1,tzinfo=timezone.utc),approval_policy_reference='POL'); VendorBillRegistry.create(bill,b); opened=VendorBillRegistry.open_bill('t','p',1,'open',b).vendor_bill; req=FinancialApprovalRequirement('r','CFO',1); ev=FinancialApprovalPolicyEvaluation(tenant_id='t',evaluation_id='e',subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL,subject_id='p',subject_revision=2,approval_policy_reference='POL',approval_policy_version='1',approval_required=True,approval_requirements=(req,),rejection_rule=FinancialApprovalRejectionRule.ANY_VALID_REJECTION_BLOCKS,subject_snapshot_fingerprint=_compute_vendor_bill_policy_snapshot_fingerprint(opened),evaluator_reference='resolver',evaluated_at=datetime(2026,1,1,tzinfo=timezone.utc),created_at=datetime(2026,1,1,tzinfo=timezone.utc)); FinancialApprovalPolicyEvaluationRegistry.create(ev,'ev-key',p); auth=FinancialApprovalActorAuthorization(tenant_id='t',authorization_id='auth',subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL,subject_id='p',subject_revision=2,evaluation_id='e',approval_policy_reference='POL',approval_policy_version='1',requirement_id='r',actor_id='actor',actor_capacity='CFO',authorization_source_reference='rbac',authorization_basis_reference='grant',authorized_at=datetime(2026,1,1,tzinfo=timezone.utc),authorization_evidence_fingerprint='a'*128,created_at=datetime(2026,1,1,tzinfo=timezone.utc)); return c,db,p,a,auth

def test_actor_authorization_registry_matrix_real_mongo():
 c,db,p,a,auth=fixture(); first=FinancialApprovalActorAuthorizationRegistry.create(auth,'key',a); replay=FinancialApprovalActorAuthorizationRegistry.create(auth,'key',a); assert first.outcome.value=='CREATED' and replay.outcome.value=='IDEMPOTENT_REPLAY'; altered=replace(auth,actor_id='other')
 try: FinancialApprovalActorAuthorizationRegistry.create(altered,'key',a)
 except FinancialApprovalActorAuthorizationIdempotencyKeyReuseError: pass
 else: raise AssertionError('reuse accepted')
 try: FinancialApprovalActorAuthorizationRegistry.create(auth,'other',a)
 except FinancialApprovalActorAuthorizationCreateConflictError: pass
 else: raise AssertionError('identity conflict accepted')
 assert FinancialApprovalActorAuthorizationRegistry.get('t','auth',a)==auth
 try: FinancialApprovalActorAuthorizationRegistry.get('other','auth',a)
 except FinancialApprovalActorAuthorizationNotFoundError: pass
 else: raise AssertionError('cross tenant disclosure')
 assert len(FinancialApprovalActorAuthorizationRegistry.list_for_requirement('t','e','r',100,a))==1
 a.update_one({'authorization_id':'auth'},{'$set':{'authorization_evidence_fingerprint':'bad'}})
 try: FinancialApprovalActorAuthorizationRegistry.get('t','auth',a)
 except FinancialApprovalActorAuthorizationPersistedRecordInvalidError: pass
 else: raise AssertionError('corrupt auth accepted')
 c.drop_database(db.name); c.close()

def test_bounded_requirement_keyset_pagination_real_mongo():
 c,db,p,a,auth=fixture()
 for i in range(23): FinancialApprovalActorAuthorizationRegistry.create(replace(auth,authorization_id=f'page-{i:03d}',authorization_evidence_fingerprint=('a' if i%2==0 else 'b')*128),f'page-key-{i}',a)
 cursor=None; seen=[]; sizes=[]
 while True:
  page=FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page('t','e','r',5,cursor,a); sizes.append(len(page.items)); seen.extend(x.authorization_id for x in page.items)
  if page.next_cursor is None: break
  cursor=page.next_cursor
 assert sizes==[5,5,5,5,3] and len(seen)==len(set(seen))==23
 c.drop_database(db.name); c.close()

def test_requirement_pagination_260_snapshot_and_corruption_real_mongo():
 c,db,p,a,auth=fixture()
 for i in range(260): FinancialApprovalActorAuthorizationRegistry.create(replace(auth,authorization_id=f'bulk-{i:03d}',authorization_evidence_fingerprint=('a' if i%2==0 else 'b')*128),f'bulk-key-{i}',a)
 with c.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot')); page=FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page('t','e','r',250,None,a,session=session); assert len(page.items)==250 and page.next_cursor is not None
  outside=MongoClient(os.environ['TEST_VENDOR_MONGO_URI']); ext=outside[db.name]['financial_approval_actor_authorizations']; extra=replace(auth,authorization_id='bulk-new',authorization_evidence_fingerprint='c'*128); FinancialApprovalActorAuthorizationRegistry.create(extra,'bulk-new-key',ext); outside.close()
  page2=FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page('t','e','r',250,page.next_cursor,a,session=session); assert len(page2.items)==10 and 'bulk-new' not in {x.authorization_id for x in page2.items}; session.commit_transaction()
 fresh=FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page('t','e','r',250,None,a); fresh2=FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page('t','e','r',250,fresh.next_cursor,a); assert 'bulk-new' in {x.authorization_id for x in fresh.items+fresh2.items}
 a.update_one({'authorization_id':'bulk-255'},{'$set':{'authorization_evidence_fingerprint':'bad'}}); first=FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page('t','e','r',250,None,a)
 try: FinancialApprovalActorAuthorizationRegistry.list_for_requirement_page('t','e','r',10,first.next_cursor,a)
 except FinancialApprovalActorAuthorizationPersistedRecordInvalidError: pass
 else: raise AssertionError('corrupt authorization skipped')
 c.drop_database(db.name); c.close()

def test_actor_authorization_requirement_list_shared_session_real_mongo():
 c,db,p,a,auth=fixture()
 second=replace(auth,authorization_id='auth-2',actor_id='actor-2')
 FinancialApprovalActorAuthorizationRegistry.create(auth,'key-1',a); FinancialApprovalActorAuthorizationRegistry.create(second,'key-2',a)
 plain=FinancialApprovalActorAuthorizationRegistry.list_for_requirement('t','e','r',100,a)
 assert [item.authorization_id for item in plain]==['auth','auth-2']
 with c.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot'))
  listed=FinancialApprovalActorAuthorizationRegistry.list_for_requirement('t','e','r',100,a,session=session)
  assert [item.authorization_id for item in listed]==['auth','auth-2']
  assert FinancialApprovalActorAuthorizationRegistry.list_for_requirement('other','e','r',100,a,session=session)==()
  assert FinancialApprovalActorAuthorizationRegistry.list_for_requirement('t','other-evaluation','r',100,a,session=session)==()
  assert FinancialApprovalActorAuthorizationRegistry.list_for_requirement('t','e','other-requirement',100,a,session=session)==()
  session.abort_transaction()
 a.update_one({'authorization_id':'auth'},{'$set':{'authorization_evidence_fingerprint':'bad'}})
 with c.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot'))
  try: FinancialApprovalActorAuthorizationRegistry.list_for_requirement('t','e','r',100,a,session=session)
  except FinancialApprovalActorAuthorizationPersistedRecordInvalidError: pass
  else: raise AssertionError('corrupt authorization accepted')
  assert FinancialApprovalActorAuthorizationRegistry.list_for_requirement('t','e','empty',100,a,session=session)==()
  session.abort_transaction()
 c.drop_database(db.name); c.close()

def test_actor_authorization_registry_concurrency_real_mongo():
 c,db,p,a,auth=fixture(); barrier=Barrier(100)
 def run(_):
  try: barrier.wait(); return FinancialApprovalActorAuthorizationRegistry.create(auth,'key',a).outcome.value
  except Exception as exc: return type(exc).__name__
 with ThreadPoolExecutor(max_workers=100) as pool: outcomes=list(pool.map(run,range(100)))
 assert outcomes.count('CREATED')==1 and outcomes.count('IDEMPOTENT_REPLAY')==99 and a.count_documents({})==1
 c.drop_database(db.name); c.close()

def test_actor_authorization_registry_different_command_identity_races_real_mongo():
 c,db,p,a,auth=fixture(); created=conflicts=double=raw=unexpected=mismatch=0
 for _ in range(100):
  a.delete_many({}); left=replace(auth,actor_id='left'); right=replace(auth,actor_id='right'); barrier=Barrier(2)
  def run(item):
   try:
    barrier.wait(); return FinancialApprovalActorAuthorizationRegistry.create(item[0],item[1],a).outcome.value
   except Exception as exc: return str(exc)
  with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(run,((left,'left-key'),(right,'right-key'))))
  created += results.count('CREATED'); conflicts += results.count('FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_CREATE_CONFLICT'); double += int(results.count('CREATED')!=1); raw += sum('DuplicateKeyError' in x for x in results); unexpected += sum(x not in ('CREATED','FINANCIAL_APPROVAL_ACTOR_AUTHORIZATION_CREATE_CONFLICT') for x in results); mismatch += int(a.count_documents({})!=1)
 assert (created,conflicts,double,raw,unexpected,mismatch)==(100,100,0,0,0,0)
 c.drop_database(db.name); c.close()
