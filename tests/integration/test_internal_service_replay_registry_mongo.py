"""WILSY OS Internal Service Replay Registry Real-Mongo Certification."""
import os, uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import pytest
from pymongo import MongoClient
from tools.eos.auth.internal_service_replay_registry import *

@pytest.fixture()
def collection():
    uri=os.getenv('TEST_VENDOR_MONGO_URI')
    if not uri: pytest.skip('TEST_VENDOR_MONGO_URI is required')
    client=MongoClient(uri,serverSelectionTimeoutMS=5000); assert client.admin.command('hello').get('setName')=='wilsyVendorCertRS'
    db=client['internal_service_replay_cert_'+uuid.uuid4().hex]; c=db[COLLECTION]; InternalServiceReplayRegistry.ensure_indexes(c); yield c; client.drop_database(db.name); client.close()

def test_real_mongo_claim_and_indexes(collection):
    r=InternalServiceReplayRegistry(collection); assert r.consume_once(service_id='s',key_id='k',nonce='n',expires_at=4102444800); assert not r.consume_once(service_id='s',key_id='k',nonce='n',expires_at=4102444800); assert r.consume_once(service_id='other',key_id='k',nonce='n',expires_at=4102444800); assert r.consume_once(service_id='s',key_id='other',nonce='n',expires_at=4102444800)
    row=collection.find_one({'service_id':'s','key_id':'k','nonce':'n'}); expected_expiry=datetime.fromtimestamp(4102444800, tz=timezone.utc).replace(tzinfo=None); assert isinstance(row['expires_at'],datetime) and row['expires_at'].tzinfo is None and row['expires_at'] == expected_expiry; assert isinstance(row['created_at'],datetime) and row['created_at'].tzinfo is None
    names={x['name']:x for x in collection.list_indexes()}; assert names['internal_service_replay_identity_unique']['unique']; assert names['internal_service_replay_expiry_ttl']['expireAfterSeconds']==0

def test_concurrent_identical_claims(collection):
    total=16; barrier=__import__('threading').Barrier(total); r=InternalServiceReplayRegistry(collection)
    def claim(_): barrier.wait(); return r.consume_once(service_id='s',key_id='k',nonce='same',expires_at=4102444800)
    with ThreadPoolExecutor(max_workers=total) as pool: results=list(pool.map(claim, range(total)))
    print(f'CONCURRENT_IDENTICAL_TOTAL={total}'); print(f'CONCURRENT_IDENTICAL_TRUE_COUNT={results.count(True)}'); print(f'CONCURRENT_IDENTICAL_FALSE_COUNT={results.count(False)}')
    assert results.count(True)==1 and results.count(False)==total-1

def test_concurrent_distinct_claims(collection):
    total=16; barrier=__import__('threading').Barrier(total); r=InternalServiceReplayRegistry(collection)
    def claim(i): barrier.wait(); return r.consume_once(service_id='s',key_id='k',nonce=f'{i:032x}',expires_at=4102444800)
    with ThreadPoolExecutor(max_workers=total) as pool: results=list(pool.map(claim, range(total)))
    print(f'CONCURRENT_DISTINCT_TOTAL={total}'); print(f'CONCURRENT_DISTINCT_TRUE_COUNT={results.count(True)}'); print(f'CONCURRENT_DISTINCT_FALSE_COUNT={results.count(False)}')
    assert all(results) and results.count(False)==0

# ARTIFACT: test_internal_service_replay_registry_mongo.py
# VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-REPLAY
# END OF WILSY OS SOVEREIGN ARTIFACT
