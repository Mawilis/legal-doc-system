"""TITLE: Tenant Business-Role Repository Real-Mongo Certificate.
VERSION: v1.1.0-TENANT-BUSINESS-ROLE-REPOSITORY-REAL-MONGO-CERT
AUTHORITY: Real persistence evidence only; no authorization or execution.
EPITOME: Certifies isolated collection, indexes, round trips, scope, CAS, and corruption.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_business_role_repository_real_mongo.py
CERTIFICATION/UPDATE DATE: 2026-09-05.
CHANGELOG: v1.1.0 completes the governed F1B real-Mongo matrix.
TENANT BOUNDARY: Every lookup is exact principal/tenant scope.
FINANCIAL AUTHORITY: Kennel EOS exclusively executes financial operations.
"""
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_authority import (
    BusinessRoleResolution,
    resolve_current_tenant_business_role,
)
from tools.eos.auth.tenant_business_role_repository import (TenantBusinessRoleAlreadyExistsError, TenantBusinessRolePersistedRecordInvalidError, TenantBusinessRoleRepository, TenantBusinessRoleNotFoundError, TenantBusinessRoleRepositoryError, TenantBusinessRoleRevisionConflictError)

def test_real_mongo_business_role_repository() -> None:
 client=MongoClient(os.getenv('TEST_VENDOR_MONGO_URI','mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS'),serverSelectionTimeoutMS=2000); db=client['wilsy_business_role_'+uuid4().hex]; c=db['tenant_business_roles']; repo=TenantBusinessRoleRepository
 try:
  try: client.admin.command('ping')
  except ServerSelectionTimeoutError as error: pytest.skip(f'governed Mongo unavailable: {error}')
  stamp=datetime(2026,1,1,tzinfo=timezone.utc); repo.ensure_indexes(c); info=c.index_information(); assert any(i.get('unique') is True and list(i['key'])==[('principal_id',1),('tenant_id',1)] and name=='principal_tenant_business_role_unique' for name,i in info.items())
  active=TenantBusinessRoleAuthority('p','a','tenant_owner',TenantBusinessRoleStatus.ACTIVE,0,stamp,None); repo.insert(active,c); got=repo.resolve('p','a',c); assert got==active and got.effective_at.tzinfo is not None and got.effective_at.utcoffset()==timedelta(0)
  with pytest.raises(TenantBusinessRoleAlreadyExistsError): repo.insert(active,c)
  assert repo.resolve('p','a',c)==active
  revoked=TenantBusinessRoleAuthority('p','b','tenant_manager',TenantBusinessRoleStatus.REVOKED,0,stamp,stamp+timedelta(seconds=1)); repo.insert(revoked,c); got=repo.resolve('p','b',c); assert got==revoked and got.revoked_at is not None and got.revoked_at.tzinfo is not None and got.revoked_at.utcoffset()==timedelta(0)
  with pytest.raises(TenantBusinessRoleNotFoundError): repo.resolve('other','a',c)
  for tenant,role in [('tenant-a','tenant_admin'),('tenant-b','tenant_auditor')]: repo.insert(TenantBusinessRoleAuthority('multi',tenant,role,TenantBusinessRoleStatus.ACTIVE,0,stamp,None),c)
  assert repo.resolve('multi','tenant-a',c).business_role=='tenant_admin' and repo.resolve('multi','tenant-b',c).business_role=='tenant_auditor'
  repo.insert(TenantBusinessRoleAuthority('pa','shared','tenant_owner',TenantBusinessRoleStatus.ACTIVE,0,stamp,None),c); repo.insert(TenantBusinessRoleAuthority('pb','shared','tenant_admin',TenantBusinessRoleStatus.ACTIVE,0,stamp,None),c); assert repo.resolve('pa','shared',c).business_role=='tenant_owner' and repo.resolve('pb','shared',c).business_role=='tenant_admin'
  db['role_assignments'].insert_one({'principal_id':'legacy','tenant_id':'legacy','role_id':'tenant_owner','status':'ACTIVE','revision':0})
  with pytest.raises(TenantBusinessRoleNotFoundError): repo.resolve('legacy','legacy',c)
  c.insert_one({'principal_id':'bad','tenant_id':'bad','business_role':'AUDITOR','status':'ACTIVE','revision':0,'effective_at':stamp,'revoked_at':None})
  with pytest.raises(TenantBusinessRolePersistedRecordInvalidError): repo.resolve('bad','bad',c)
  updated=TenantBusinessRoleAuthority('p','a','tenant_admin',TenantBusinessRoleStatus.ACTIVE,1,stamp,None); assert repo.compare_and_swap(updated,0,c)==updated
  with pytest.raises(TenantBusinessRoleRevisionConflictError): repo.compare_and_swap(TenantBusinessRoleAuthority('p','a','tenant_owner',TenantBusinessRoleStatus.ACTIVE,2,stamp,None),0,c)
  assert repo.resolve('p','a',c)==updated
  with pytest.raises(TenantBusinessRoleRevisionConflictError): repo.compare_and_swap(TenantBusinessRoleAuthority('p','a','tenant_owner',TenantBusinessRoleStatus.ACTIVE,3,stamp,None),1,c)
  assert repo.resolve('p','a',c)==updated
  with client.start_session() as session:
   session.start_transaction()
   repo.insert(TenantBusinessRoleAuthority('tx','tenant','tenant_owner',TenantBusinessRoleStatus.ACTIVE,0,stamp,None),c,session=session)
   assert c.find_one({'principal_id':'tx','tenant_id':'tenant'},session=session) is not None
   session.abort_transaction()
  assert c.find_one({'principal_id':'tx','tenant_id':'tenant'}) is None
 finally:
  try: db.client.drop_database(db.name)
  except PyMongoError as error: _ = error
  client.close()
# ARTIFACT: test_tenant_business_role_repository_real_mongo.py
# VERSION: v1.1.0-TENANT-BUSINESS-ROLE-REPOSITORY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real persistence evidence only
# TENANT POSTURE: exact principal/tenant isolation
# FAIL-CLOSED POSTURE: uniqueness, corruption, stale and gap CAS reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT


def test_multi_capacity_history_cas_and_abort_are_atomic_on_real_replica_set() -> None:
    """Prove the multi-capacity current projection and immutable history share caller transactions."""
    uri = os.getenv(
        "TEST_VENDOR_MONGO_URI",
        "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
    )
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    database = client[f"wilsy_business_role_multi_{uuid4().hex}"]
    legacy = database["tenant_business_roles"]
    current = database["tenant_business_role_assignments"]
    history = database["tenant_business_role_assignment_history"]
    repo = TenantBusinessRoleRepository
    stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)

    try:
        hello = client.admin.command("hello")
        assert hello.get("isWritablePrimary") is True
        assert hello.get("setName") == "wilsyVendorCertRS"

        repo.ensure_indexes(legacy)
        repo.ensure_multi_capacity_indexes(database)
        current_indexes = current.index_information()
        history_indexes = history.index_information()
        assert current_indexes["principal_tenant_business_role_capacity_unique"]["unique"] is True
        assert history_indexes["principal_tenant_business_role_history_revision_unique"]["unique"] is True

        # Preserve the legacy capacity while adding a second independent capacity.
        legacy_partner = TenantBusinessRoleAuthority(
            "principal", "tenant", "tenant_legal_partner",
            TenantBusinessRoleStatus.ACTIVE, 0, stamp, None,
        )
        repo.insert(legacy_partner, legacy)
        owner = TenantBusinessRoleAuthority(
            "principal", "tenant", "tenant_owner",
            TenantBusinessRoleStatus.ACTIVE, 0, stamp, None,
        )

        with client.start_session() as session:
            with session.start_transaction():
                assert repo.record_capacity_revision(
                    owner, None, database, session=session
                ) == owner

            resolved = repo.resolve_all("principal", "tenant", legacy)
            assert {value.business_role for value in resolved} == {
                "tenant_legal_partner", "tenant_owner"
            }
            assert repo.resolve_business_role(
                "principal", "tenant", "tenant_owner", legacy
            ) == owner
            assert history.count_documents({
                "principal_id": "principal",
                "tenant_id": "tenant",
                "business_role": "tenant_owner",
            }) == 1

            revised_owner = TenantBusinessRoleAuthority(
                "principal", "tenant", "tenant_owner",
                TenantBusinessRoleStatus.ACTIVE, 1, stamp, None,
            )
            with session.start_transaction():
                assert repo.record_capacity_revision(
                    revised_owner, 0, database, session=session
                ) == revised_owner

            assert current.find_one({
                "principal_id": "principal",
                "tenant_id": "tenant",
                "business_role": "tenant_owner",
            })["revision"] == 1
            assert history.count_documents({
                "principal_id": "principal",
                "tenant_id": "tenant",
                "business_role": "tenant_owner",
            }) == 2

            class CurrentCapacityReader:
                def resolve_all_business_roles(self, principal_id, tenant_id, *, session=None):
                    return repo.resolve_all(principal_id, tenant_id, legacy, session=session)

            reader = CurrentCapacityReader()
            owner_decision = resolve_current_tenant_business_role(
                principal_id="principal", tenant_id="tenant",
                repository=reader, operation="crm_work_item_create",
                session=session,
            )
            legal_decision = resolve_current_tenant_business_role(
                principal_id="principal", tenant_id="tenant",
                repository=reader, operation="legal_matter_deadline_read",
                session=session,
            )
            assert owner_decision.role == "tenant_owner"
            assert owner_decision.resolution is BusinessRoleResolution.RESOLVED
            assert legal_decision.role == "tenant_legal_partner"
            assert legal_decision.resolution is BusinessRoleResolution.RESOLVED

            # Revoke only the owner capacity. The Legal specialist fact and
            # its operation eligibility remain independently current.
            revoked_owner = TenantBusinessRoleAuthority(
                "principal", "tenant", "tenant_owner",
                TenantBusinessRoleStatus.REVOKED, 2, stamp,
                stamp + timedelta(seconds=1),
            )
            with session.start_transaction():
                repo.record_capacity_revision(
                    revoked_owner, 1, database, session=session
                )
            owner_after_revoke = resolve_current_tenant_business_role(
                principal_id="principal", tenant_id="tenant",
                repository=reader, operation="crm_work_item_create",
                session=session,
            )
            legal_after_revoke = resolve_current_tenant_business_role(
                principal_id="principal", tenant_id="tenant",
                repository=reader, operation="legal_matter_deadline_read",
                session=session,
            )
            assert owner_after_revoke.role is None
            assert owner_after_revoke.resolution is BusinessRoleResolution.NO_ELIGIBLE_TENANT_BUSINESS_ROLE
            assert legal_after_revoke.role == "tenant_legal_partner"
            assert legal_after_revoke.resolution is BusinessRoleResolution.RESOLVED
            assert current.find_one({
                "principal_id": "principal", "tenant_id": "tenant",
                "business_role": "tenant_owner",
            })["revision"] == 2
            assert current.find_one({
                "principal_id": "principal", "tenant_id": "tenant",
                "business_role": "tenant_legal_partner",
            }) is None
            assert history.count_documents({
                "principal_id": "principal", "tenant_id": "tenant",
                "business_role": "tenant_owner",
            }) == 3

            # A stale current revision rejects after the candidate history
            # append; the caller transaction must roll that append back.
            current.insert_one({
                "principal_id": "principal", "tenant_id": "tenant",
                "business_role": "tenant_manager", "status": "ACTIVE",
                "revision": 2, "effective_at": stamp, "revoked_at": None,
            })
            stale = TenantBusinessRoleAuthority(
                "principal", "tenant", "tenant_manager",
                TenantBusinessRoleStatus.ACTIVE, 2, stamp, None,
            )
            with pytest.raises(TenantBusinessRoleRevisionConflictError):
                with session.start_transaction():
                    repo.record_capacity_revision(
                        stale, 1, database, session=session
                    )
            assert current.find_one({
                "principal_id": "principal",
                "tenant_id": "tenant",
                "business_role": "tenant_manager",
            })["revision"] == 2
            assert history.count_documents({
                "principal_id": "principal",
                "tenant_id": "tenant",
                "business_role": "tenant_manager",
            }) == 0

            # Explicit caller abort must remove both current and history writes.
            aborted = TenantBusinessRoleAuthority(
                "principal", "tenant", "tenant_admin",
                TenantBusinessRoleStatus.ACTIVE, 0, stamp, None,
            )
            with pytest.raises(RuntimeError, match="force caller abort"):
                with session.start_transaction():
                    repo.record_capacity_revision(
                        aborted, None, database, session=session
                    )
                    raise RuntimeError("force caller abort")

        assert current.find_one({
            "principal_id": "principal",
            "tenant_id": "tenant",
            "business_role": "tenant_admin",
        }) is None
        assert history.count_documents({
            "principal_id": "principal",
            "tenant_id": "tenant",
            "business_role": "tenant_admin",
        }) == 0
    finally:
        try:
            client.drop_database(database.name)
        finally:
            client.close()


def test_multi_capacity_concurrent_revision_writers_are_fenced_on_real_replica_set() -> None:
    """Two concurrent writers cannot both advance the same capacity revision."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    client = MongoClient(
        os.getenv(
            "TEST_VENDOR_MONGO_URI",
            "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
        ),
        serverSelectionTimeoutMS=5000,
        retryWrites=True,
    )
    database = client[f"wilsy_business_role_race_{uuid4().hex}"]
    legacy = database["tenant_business_roles"]
    current = database["tenant_business_role_assignments"]
    history = database["tenant_business_role_assignment_history"]
    repo = TenantBusinessRoleRepository
    stamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    barrier = Barrier(2)

    try:
        assert client.admin.command("hello").get("isWritablePrimary") is True
        repo.ensure_indexes(legacy)
        repo.ensure_multi_capacity_indexes(database)
        initial = TenantBusinessRoleAuthority(
            "principal", "tenant", "tenant_owner",
            TenantBusinessRoleStatus.ACTIVE, 0, stamp, None,
        )
        with client.start_session() as session:
            with session.start_transaction():
                repo.record_capacity_revision(
                    initial, None, database, session=session
                )

        def write(status: TenantBusinessRoleStatus):
            candidate = TenantBusinessRoleAuthority(
                "principal", "tenant", "tenant_owner",
                status, 1, stamp,
                stamp + timedelta(seconds=1)
                if status is TenantBusinessRoleStatus.REVOKED else None,
            )
            try:
                with client.start_session() as session:
                    with session.start_transaction():
                        barrier.wait(timeout=10)
                        repo.record_capacity_revision(
                            candidate, 0, database, session=session
                        )
                return "COMMITTED"
            except (
                TenantBusinessRoleRevisionConflictError,
                TenantBusinessRoleRepositoryError,
            ):
                return "REJECTED"

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(
                write,
                (TenantBusinessRoleStatus.ACTIVE, TenantBusinessRoleStatus.REVOKED),
            ))

        assert outcomes.count("COMMITTED") == 1
        assert outcomes.count("REJECTED") == 1
        winner = current.find_one({
            "principal_id": "principal", "tenant_id": "tenant",
            "business_role": "tenant_owner",
        })
        assert winner["revision"] == 1
        assert history.count_documents({
            "principal_id": "principal", "tenant_id": "tenant",
            "business_role": "tenant_owner",
        }) == 2
    finally:
        try:
            client.drop_database(database.name)
        finally:
            client.close()
