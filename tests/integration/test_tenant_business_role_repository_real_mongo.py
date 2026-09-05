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
from tools.eos.auth.tenant_business_role_repository import (TenantBusinessRoleAlreadyExistsError, TenantBusinessRolePersistedRecordInvalidError, TenantBusinessRoleRepository, TenantBusinessRoleNotFoundError, TenantBusinessRoleRevisionConflictError)

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
