import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from tools.eos.saas.billing.financial_approval_aggregator import FinancialApprovalAggregator
from tools.eos.saas.billing.financial_approval_effective_result_registry import *
from tests.integration.test_financial_approval_aggregator_mongo import fixture

def test_effective_result_registry_create_replay_reference_and_corruption_real_mongo():
 c, source, p, d, a, ev, opened = fixture(1); result = FinancialApprovalAggregator(database=source).aggregate('t','e','result-1',ev.evaluated_at,ev.created_at)
 dbname=source.name; db=source; collection=db[COLLECTION]; FinancialApprovalEffectiveResultRegistry.ensure_indexes(collection)
 first=FinancialApprovalEffectiveResultRegistry.create(result,'key-1',collection); replay=FinancialApprovalEffectiveResultRegistry.create(result,'key-1',collection)
 assert first.outcome is FinancialApprovalEffectiveResultCreateOutcome.CREATED and replay.outcome is FinancialApprovalEffectiveResultCreateOutcome.IDEMPOTENT_REPLAY
 assert FinancialApprovalEffectiveResultRegistry.get('t','result-1',collection)==result
 listed=FinancialApprovalEffectiveResultRegistry.list_for_evaluation('t','e',10,collection); assert listed==(result,)
 collection.update_one({'result_id':'result-1'},{'$set':{'create_command_fingerprint':'bad'}})
 try: FinancialApprovalEffectiveResultRegistry.get('t','result-1',collection)
 except FinancialApprovalEffectiveResultPersistedRecordInvalidError: pass
 else: raise AssertionError('corruption accepted')
 with c.start_session() as session:
  session.start_transaction(read_concern=ReadConcern('snapshot')); session.abort_transaction()
 c.drop_database(dbname); c.close()

def test_effective_result_registry_identical_create_concurrency_real_mongo():
 c, source, p, d, a, ev, opened = fixture(1); result=FinancialApprovalAggregator(database=source).aggregate('t','e','race-result',ev.evaluated_at,ev.created_at); collection=source[COLLECTION]; FinancialApprovalEffectiveResultRegistry.ensure_indexes(collection)
 def run(_):
  try: return FinancialApprovalEffectiveResultRegistry.create(result,'race-key',collection).outcome
  except Exception as error: return error
 with ThreadPoolExecutor(max_workers=32) as pool: outcomes=list(pool.map(run,range(100)))
 assert sum(x is FinancialApprovalEffectiveResultCreateOutcome.CREATED for x in outcomes)==1 and sum(x is FinancialApprovalEffectiveResultCreateOutcome.IDEMPOTENT_REPLAY for x in outcomes)==99 and collection.count_documents({})==1
 c.drop_database(source.name); c.close()
