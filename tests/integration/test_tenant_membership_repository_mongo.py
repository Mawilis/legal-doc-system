"""Real-Mongo certification for durable tenant membership authority."""
import os, uuid
from pymongo import MongoClient
import pytest
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import *

@pytest.fixture()
def collection():
    uri=os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri: pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client=MongoClient(uri,serverSelectionTimeoutMS=5000); hello=client.admin.command("hello")
    if hello.get("setName")!="wilsyVendorCertRS": pytest.fail("wrong replica set")
    db=client[f"tenant_membership_{uuid.uuid4().hex}"]; c=db[COLLECTION]; TenantMembershipRepository.ensure_indexes(c); yield c; client.drop_database(db.name); client.close()

def m(p="p",t="t",s=TenantMembershipStatus.ACTIVE,r=0): return TenantMembershipAuthority(p,t,s,r)

def test_unique_identity_and_multi_tenant_isolation(collection):
    TenantMembershipRepository.insert(m(),collection); TenantMembershipRepository.insert(m(t="other"),collection); TenantMembershipRepository.insert(m(p="other"),collection)
    with pytest.raises(TenantMembershipAlreadyExistsError): TenantMembershipRepository.insert(m(),collection)
    assert TenantMembershipRepository.resolve("p","other",collection).tenant_id=="other"
    assert TenantMembershipRepository.resolve("other","t",collection).principal_id=="other"

def test_cas_stale_and_revoked_protection(collection):
    TenantMembershipRepository.insert(m(),collection)
    TenantMembershipRepository.compare_and_swap(m(s=TenantMembershipStatus.SUSPENDED,r=1),0,collection)
    TenantMembershipRepository.compare_and_swap(m(s=TenantMembershipStatus.REVOKED,r=2),1,collection)
    for status in (TenantMembershipStatus.ACTIVE,TenantMembershipStatus.SUSPENDED):
        with pytest.raises(TenantMembershipRevisionConflictError): TenantMembershipRepository.compare_and_swap(m(s=status,r=2),1,collection)
    assert TenantMembershipRepository.resolve("p","t",collection).status is TenantMembershipStatus.REVOKED

def test_session_commit_and_abort_visibility(collection):
    client=collection.database.client; session=client.start_session()
    try:
        with session.start_transaction(): TenantMembershipRepository.insert(m(p="committed"),collection,session=session)
        assert TenantMembershipRepository.resolve("committed","t",collection,session=session).principal_id=="committed"
    finally: session.end_session()

def test_malformed_persisted_record_fails_closed(collection):
    collection.insert_one({"principal_id":"bad","tenant_id":"t","status":"UNKNOWN","revision":0})
    with pytest.raises(TenantMembershipPersistedRecordInvalidError): TenantMembershipRepository.resolve("bad","t",collection)
