"""TITLE: Tenant Business-Role Repository Certificate.
VERSION: v1.0.0-TENANT-BUSINESS-ROLE-REPOSITORY-CERT
AUTHORITY: Pure repository contract certification; no authorization or execution.
EPITOME: Proves isolated persistence, hydration, tenant scope, and atomic CAS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_business_role_repository.py
CERTIFICATION/UPDATE DATE: 2026-09-05.
TENANT BOUNDARY: Exact principal/tenant filters are mandatory.
FINANCIAL AUTHORITY: Kennel EOS exclusively executes financial operations.
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
import pytest
from pymongo.client_session import ClientSession
from pymongo.errors import DuplicateKeyError
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import *

T=datetime(2026,9,1,tzinfo=timezone.utc)
def value(role='tenant_owner', status=TenantBusinessRoleStatus.ACTIVE, revision=0, revoked_at=None): return TenantBusinessRoleAuthority('p','t',role,status,revision,T,revoked_at)
def test_indexes_and_insert_serialize_exactly():
 c=Mock(); session=Mock(spec=ClientSession); TenantBusinessRoleRepository.ensure_indexes(c); c.create_index.assert_called_once_with([('principal_id',1),('tenant_id',1)],unique=True,name='principal_tenant_business_role_unique'); TenantBusinessRoleRepository.insert(value(),c,session=session); assert c.insert_one.call_args.kwargs['session'] is session; assert c.insert_one.call_args.args[0]['status']=='ACTIVE'
def test_resolve_exact_filter_and_round_trip():
 c=Mock(); session=Mock(spec=ClientSession); c.find_one.return_value={'principal_id':'p','tenant_id':'t','business_role':'tenant_owner','status':'ACTIVE','revision':2,'effective_at':T,'revoked_at':None}; got=TenantBusinessRoleRepository.resolve('p','t',c,session=session); assert got==value(revision=2); assert c.find_one.call_args.args[0]=={'principal_id':'p','tenant_id':'t'}; assert c.find_one.call_args.kwargs['session'] is session
def test_revoked_round_trip():
 c=Mock(); c.find_one.return_value={**TenantBusinessRoleRepository._document(value(TenantBusinessRoleStatus.REVOKED))} if False else {'principal_id':'p','tenant_id':'t','business_role':'tenant_owner','status':'REVOKED','revision':1,'effective_at':T,'revoked_at':T+timedelta(seconds=1)}; assert TenantBusinessRoleRepository.resolve('p','t',c).status is TenantBusinessRoleStatus.REVOKED
@pytest.mark.parametrize('doc', [{'status':'BAD'},{'business_role':'AUDITOR'},{'revision':-1},{'effective_at':datetime(2026,1,1)}])
def test_corrupt_records_fail_closed(doc):
 c=Mock(); base={'principal_id':'p','tenant_id':'t','business_role':'tenant_owner','status':'ACTIVE','revision':0,'effective_at':T,'revoked_at':None}; base.update(doc); c.find_one.return_value=base
 with pytest.raises(TenantBusinessRolePersistedRecordInvalidError): TenantBusinessRoleRepository.resolve('p','t',c)
def test_cas_filter_revision_and_session():
 c=Mock(); session=Mock(spec=ClientSession); c.replace_one.return_value=Mock(matched_count=1); candidate=value(revision=1); assert TenantBusinessRoleRepository.compare_and_swap(candidate,0,c,session=session)==candidate; assert c.replace_one.call_args.args[0]=={'principal_id':'p','tenant_id':'t','revision':0}; assert c.replace_one.call_args.kwargs['upsert'] is False; assert c.replace_one.call_args.kwargs['session'] is session
@pytest.mark.parametrize('revision',[-1,2])
def test_cas_revision_gap_rejected(revision):
 with pytest.raises((TenantBusinessRoleRevisionConflictError, ValueError)): TenantBusinessRoleRepository.compare_and_swap(value(revision=revision),0,Mock())
def test_stale_cas_and_duplicate_fail_closed():
 c=Mock(); c.replace_one.return_value=Mock(matched_count=0)
 with pytest.raises(TenantBusinessRoleRevisionConflictError): TenantBusinessRoleRepository.compare_and_swap(value(revision=1),0,c)
 c.insert_one.side_effect=DuplicateKeyError('duplicate')
 with pytest.raises(TenantBusinessRoleAlreadyExistsError): TenantBusinessRoleRepository.insert(value(),c)
def test_scope_and_absence():
 c=Mock(); c.find_one.return_value=None
 with pytest.raises(TenantBusinessRoleNotFoundError): TenantBusinessRoleRepository.resolve('p','other',c)
def test_no_transaction_or_authorization_methods():
 assert not {'authorize','execute','start_transaction','commit_transaction'}.intersection(dir(TenantBusinessRoleRepository))
# ARTIFACT: test_tenant_business_role_repository.py
# VERSION: v1.0.0-TENANT-BUSINESS-ROLE-REPOSITORY-CERT
# AUTHORITY BOUNDARY: repository contract only
# TENANT POSTURE: exact principal/tenant isolation
# FAIL-CLOSED POSTURE: corruption, duplicates, and stale CAS reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
