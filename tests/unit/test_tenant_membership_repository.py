"""Unit certification for tenant membership repository semantics."""
import pytest
from typing import cast, Mapping
from pymongo.client_session import ClientSession
from pymongo.collection import Collection as MongoCollection
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import *

class Result:
    def __init__(self, matched_count=1): self.matched_count = matched_count
class Collection:
    def __init__(self): self.rows = []
    def create_index(self, *a, **k): return "idx"
    def insert_one(self, doc, session=None):
        if any((r["principal_id"], r["tenant_id"]) == (doc["principal_id"], doc["tenant_id"]) for r in self.rows):
            from pymongo.errors import DuplicateKeyError; raise DuplicateKeyError("duplicate")
        self.rows.append(dict(doc)); self.session=session
    def find_one(self, query, session=None):
        self.session=session
        return next((dict(r) for r in self.rows if all(r.get(k)==v for k,v in query.items())), None)
    def replace_one(self, query, doc, upsert=False, session=None):
        self.session=session
        for i,r in enumerate(self.rows):
            if all(r.get(k)==v for k,v in query.items()): self.rows[i]=dict(doc); return Result()
        return Result(0)

def m(**kw):
    v=dict(principal_id="p",tenant_id="t",status=TenantMembershipStatus.ACTIVE,revision=0); v.update(kw); return TenantMembershipAuthority(cast(str,v["principal_id"]),cast(str,v["tenant_id"]),cast(TenantMembershipStatus,v["status"]),cast(int,v["revision"]))
def c(value): return cast(MongoCollection[Mapping[str, object]], value)

def test_insert_resolve_exact_shape_duplicate_and_absence():
    fake=Collection(); TenantMembershipRepository.ensure_indexes(c(fake)); TenantMembershipRepository.insert(m(),c(fake))
    assert TenantMembershipRepository.resolve("p","t",c(fake))==m()
    assert set(fake.rows[0])=={"principal_id","tenant_id","status","revision"}
    with pytest.raises(TenantMembershipAlreadyExistsError): TenantMembershipRepository.insert(m(),c(fake))
    with pytest.raises(TenantMembershipNotFoundError): TenantMembershipRepository.resolve("missing","t",c(fake))

def test_cas_requires_natural_key_and_exact_revision():
    fake=Collection(); TenantMembershipRepository.insert(m(),c(fake))
    assert TenantMembershipRepository.compare_and_swap(m(status=TenantMembershipStatus.SUSPENDED,revision=1),0,c(fake)).revision==1
    with pytest.raises(TenantMembershipRevisionConflictError): TenantMembershipRepository.compare_and_swap(m(revision=2),0,c(fake))
    with pytest.raises(TenantMembershipRevisionConflictError): TenantMembershipRepository.compare_and_swap(m(principal_id="other",revision=2),1,c(fake))

def test_malformed_persisted_state_and_no_authority_fields():
    fake=Collection(); fake.rows.append({"principal_id":"p","tenant_id":"t","status":"UNKNOWN","revision":0})
    with pytest.raises(TenantMembershipPersistedRecordInvalidError): TenantMembershipRepository.resolve("p","t",c(fake))
    assert not {"role","permissions","credential_id","financial","kernel"}.intersection(m().__dataclass_fields__)

def test_session_is_forwarded_without_transaction_ownership():
    fake=Collection(); token=cast(ClientSession, object()); TenantMembershipRepository.insert(m(),c(fake),session=token); TenantMembershipRepository.resolve("p","t",c(fake),session=token); assert fake.session is token
