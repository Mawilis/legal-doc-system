"""TITLE: Explicit Founder Canonical-Development Admission Adversarial Certificate.
VERSION: v1.0.1
AUTHORITY: Task-owned loopback replica set only; synthetic credentials and data.
EPITOME: Prove this new operator contract's denial, atomicity and durable single use.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_founder_development_admission_real_mongo.py
COLLABORATION / OWNERSHIP: New operator contract and existing canonical source owners.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG: v1.0.1 corrects the valid synthetic email domain and proves expired
ACCESS, stale-preflight, missing-transaction and pre-existing-role denial.
v1.0.0 adds isolated adversarial evidence without repeating previous suites.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY: Test signing secret and fixture sessions only; no canonical URI.
SECURITY / PRIVACY POSTURE: Integration certification uses governed test fixtures; no credentials, personal records, or production identity data are exposed.
TENANT BOUNDARY: Exact approved IDs are synthetic records solely in UUID-owned DBs.
AUTHORITY BOUNDARY: Passing tests do not authenticate the real Founder or approve a grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
from threading import Barrier
from uuid import uuid4
from typing import Any

from bson import ObjectId
import pytest
from pymongo import MongoClient, ReadPreference
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.founder_development_admission import (
    FounderDevelopmentAdmission, FounderAdmissionError, TENANT, PRINCIPAL, DECISION,
    ROLE, PERMISSION, COLLECTION, database_target, governance_digest,
)
from tools.eos.auth import jwt_provider
from tools.eos.auth.jwt_provider import create_access_token, TokenPurpose
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization import authorize_tenant_operation

SESSION = "WILSYSESSION-SYNTHETIC-CANONICAL-DEV-CERT"


def transaction(db: Any, callback: Any) -> Any:
    """Own one real snapshot/majority+journal transaction, including complete retries."""
    with db.client.start_session() as session:
        return session.with_transaction(callback, read_concern=ReadConcern("snapshot"),
            read_preference=ReadPreference.PRIMARY, write_concern=WriteConcern(w="majority", j=True))


@pytest.fixture
def source(monkeypatch: Any) -> Any:
    """Seed/drop only this UUID-owned loopback DB; missing infrastructure is a failure."""
    uri = os.getenv("FOUNDER_ADMISSION_TEST_URI", "")
    if uri != "mongodb://127.0.0.1:27189/?replicaSet=wilsyFounderAdmissionCertRS":
        pytest.fail("Explicit task-owned Founder replica URI required")
    for key in ("ENV", "WILSY_ENV", "WILSY_EOS_ENV"):
        monkeypatch.setenv(key, "development")
    for key in ("NODE_ENV", "APP_ENV", "ENVIRONMENT", "VERCEL_ENV"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("WILSY_FOUNDER_CANONICAL_ADMISSION", DECISION)
    monkeypatch.setenv("WILSY_JWT_SECRET", "synthetic-founder-admission-key-for-isolated-certification-only")
    client = MongoClient(uri, tz_aware=True, serverSelectionTimeoutMS=4000)
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") and hello.get("setName") == "wilsyFounderAdmissionCertRS"
    db = client["wilsy_founder_admission_cert_" + uuid4().hex]
    now = datetime.now(timezone.utc)
    for name, owner in (("principal_authorities", PrincipalAuthorityRepository),
        ("tenant_memberships", TenantMembershipRepository), ("tenant_business_roles", TenantBusinessRoleRepository),
        ("role_assignments", RoleAssignmentRepository)):
        owner.ensure_indexes(db[name])
    db['tenants'].insert_one({'tenant_id':TENANT,'status':'ACTIVE','name':'Synthetic dev cert', 'plan':'ENTERPRISE'})
    db['users'].insert_one({'_id':ObjectId(PRINCIPAL),'tenantId':TENANT,'email':'founder-cert@example.com',
        'firstName':'Synthetic','lastName':'Recipient','role':'SUPER_ADMIN','permissions':[], 'credential_revision':0})
    db['sessions'].insert_one({'tenant_id':TENANT,'user_id':PRINCIPAL,'session_reference':SESSION,
        'expires_at':now+timedelta(hours=1),'created_at':now})
    PrincipalAuthorityRepository.create(PrincipalAuthority(PRINCIPAL,PrincipalStatus.ACTIVE,0),db['principal_authorities'])
    TenantMembershipRepository.insert(TenantMembershipAuthority(PRINCIPAL,TENANT,TenantMembershipStatus.ACTIVE,0),db['tenant_memberships'])
    TenantBusinessRoleRepository.insert(TenantBusinessRoleAuthority(PRINCIPAL,TENANT,'tenant_owner',TenantBusinessRoleStatus.ACTIVE,0,now,None),db['tenant_business_roles'])
    RoleAssignmentRepository.insert(RoleAssignmentAuthority(PRINCIPAL,TENANT,'ENTERPRISE_ADMIN',RoleAssignmentStatus.ACTIVE,0),db['role_assignments'])
    command = FounderDevelopmentAdmission(db,target_fingerprint=database_target(db),decision=DECISION,approval_fingerprint=governance_digest())
    command.command.evidence.ensure_indexes()
    command.provision_evidence_indexes()
    token = create_access_token({'identity_id':PRINCIPAL,'tenant_id':TENANT,'session_reference':SESSION,'roles':['SUPER_ADMIN'],'permissions':[]},
        token_purpose=TokenPurpose.ACCESS,credential_revision=0)
    try:
        yield db,command,token
    finally:
        client.drop_database(db.name)
        client.close()


def execute(source: Any, **changes: Any) -> Any:
    """Use the exact explicit decision; tests supply only their own signed fixture token."""
    db,command,token=source
    args=dict(access_token=token,tenant_id=TENANT,principal_id=PRINCIPAL,idempotency_key='synthetic-once',
        expected_principal_revision=0,expected_membership_revision=0,expected_capacity_revision=0,expected_admin_revision=0)
    args.update(changes)
    return transaction(db,lambda session:command.execute(session=session,**args))


def assert_empty(db: Any) -> None:
    """Verify zero new role, consumption and read-decision evidence after denial/abort."""
    assert db['role_assignments'].count_documents({'tenant_id':TENANT,'principal_id':PRINCIPAL,'role_id':ROLE})==0
    assert db[COLLECTION].count_documents({'tenant_id':TENANT})==0
    assert db['tenant_authorization_decision_evidence'].count_documents({'tenant_id':TENANT})==0


def test_commit_independent_readback_and_exact_privilege(source: Any) -> None:
    """Separate real client verifies fingerprints; only the singleton reader is added."""
    db,command,_=source
    result=execute(source)
    assert result['assignment_status']=='ACTIVE' and result['assignment_revision']==0
    with MongoClient(os.environ['FOUNDER_ADMISSION_TEST_URI'],tz_aware=True) as other:
        read=FounderDevelopmentAdmission(other[db.name],target_fingerprint=database_target(other[db.name]),
            decision=DECISION,approval_fingerprint=governance_digest()).readback()
        assert read==result
    record=db[COLLECTION].find_one({'tenant_id':TENANT,'decision_id':DECISION})
    assert record['independent_approver'] is None and record['ordinary_independent_grant'] is False
    assert record['permissions']==[PERMISSION] and record['consumed'] is True
    assert 'access_token' not in record and 'session_reference' not in record
    roles=set(db['role_assignments'].distinct('role_id',{'tenant_id':TENANT,'principal_id':PRINCIPAL}))
    assert roles=={'ENTERPRISE_ADMIN',ROLE}
    assert db['tenant_business_roles'].find_one({'tenant_id':TENANT})['business_role']=='tenant_owner'


@pytest.mark.parametrize('key',['ENV','WILSY_ENV','WILSY_EOS_ENV','NODE_ENV','APP_ENV','ENVIRONMENT','VERCEL_ENV'])
def test_every_production_marker_denies(source: Any,monkeypatch: Any,key: str) -> None:
    """One production marker dominates all otherwise valid development controls."""
    monkeypatch.setenv(key,'production')
    with pytest.raises(FounderAdmissionError,match='DEVELOPMENT_CONTROLS_REQUIRED'):execute(source)
    assert_empty(source[0])


@pytest.mark.parametrize('key',['ENV','WILSY_ENV','WILSY_EOS_ENV','WILSY_FOUNDER_CANONICAL_ADMISSION'])
def test_missing_development_control_denies(source: Any,monkeypatch: Any,key: str) -> None:
    """No default or inherited permissive environment admits a command."""
    monkeypatch.delenv(key)
    with pytest.raises(FounderAdmissionError,match='DEVELOPMENT_CONTROLS_REQUIRED'):execute(source)
    assert_empty(source[0])


@pytest.mark.parametrize('field,value',[('tenant_id','foreign-tenant'),('principal_id','foreign-principal')])
def test_exact_scope_only(source: Any,field: str,value: str) -> None:
    """Cross-tenant/principal callers neither mutate nor discover foreign authority."""
    with pytest.raises(FounderAdmissionError,match='EXACT_SCOPE_REQUIRED'):execute(source,**{field:value})
    assert_empty(source[0])


def test_target_and_decision_and_approval_binding(source: Any) -> None:
    """Operator binding cannot be redirected by a decision string or target digest."""
    db,_,_=source
    for changes in ({'target_fingerprint':'0'*128},{'decision':'another-decision'},{'approval_fingerprint':'0'*128}):
        args=dict(target_fingerprint=database_target(db),decision=DECISION,approval_fingerprint=governance_digest());args.update(changes)
        with pytest.raises(FounderAdmissionError):FounderDevelopmentAdmission(db,**args)
    assert_empty(db)


@pytest.mark.parametrize('field',['expected_principal_revision','expected_membership_revision','expected_capacity_revision','expected_admin_revision'])
def test_revision_currentness(source: Any,field: str) -> None:
    """Every source revision is an independent precondition of initial admission."""
    with pytest.raises(FounderAdmissionError,match='AUTHORITY_REVISION_DENIED'):execute(source,**{field:1})
    assert_empty(source[0])


@pytest.mark.parametrize('change',['invalid','pre_auth','wrong_principal','wrong_tenant','missing_session','wrong_revision','system'])
def test_signed_access_binding(source: Any,change: str) -> None:
    """A signed token or label alone never substitutes for current exact ACCESS authority."""
    args={'identity_id':PRINCIPAL,'tenant_id':TENANT,'session_reference':SESSION,'roles':['SUPER_ADMIN'],'permissions':[]}
    purpose=TokenPurpose.ACCESS;revision=0
    if change=='pre_auth':purpose=TokenPurpose.PRE_AUTH
    if change=='wrong_principal':args['identity_id']='other'
    if change=='wrong_tenant':args['tenant_id']='other'
    if change=='missing_session':args.pop('session_reference')
    if change=='wrong_revision':revision=1
    if change=='system':args['principal_scope']='SYSTEM'
    token='not-a-jwt' if change=='invalid' else create_access_token(args,token_purpose=purpose,credential_revision=revision)
    with pytest.raises(FounderAdmissionError):execute(source,access_token=token)
    assert_empty(source[0])


def test_cryptographically_signed_expired_access_denies(source: Any, monkeypatch: Any) -> None:
    """A correctly signed but expired ACCESS bearer never reaches authority writes."""
    _, _, _ = source
    claims = {'identity_id': PRINCIPAL, 'tenant_id': TENANT, 'session_reference': SESSION,
              'roles': ['SUPER_ADMIN'], 'permissions': []}
    with monkeypatch.context() as scoped:
        scoped.setattr(jwt_provider.time, 'time', lambda: 1_000_000)
        expired = create_access_token(claims, expires_in_seconds=1,
                                      token_purpose=TokenPurpose.ACCESS, credential_revision=0)
    with pytest.raises(FounderAdmissionError, match='CURRENT_ACCESS_SESSION_REQUIRED'):
        execute(source, access_token=expired)
    assert_empty(source[0])


@pytest.mark.parametrize('change',['expired','deleted','wrong_tenant'])
def test_durable_session_currentness(source: Any,change: str) -> None:
    """Expired, revoked/deleted or rebound durable sessions fail before assignment."""
    db,_,_=source
    key={'tenant_id':TENANT,'user_id':PRINCIPAL,'session_reference':SESSION}
    if change=='deleted':db['sessions'].delete_one(key)
    elif change=='expired':db['sessions'].update_one(key,{'$set':{'expires_at':datetime.now(timezone.utc)-timedelta(seconds=1)}})
    else:db['sessions'].update_one(key,{'$set':{'tenant_id':'foreign'}})
    with pytest.raises(FounderAdmissionError,match='SESSION_NOT_CURRENT'):execute(source)
    assert_empty(db)


@pytest.mark.parametrize('collection,filter_value',[('principal_authorities',{'principal_id':PRINCIPAL}),
    ('tenant_memberships',{'tenant_id':TENANT,'principal_id':PRINCIPAL}),
    ('tenant_business_roles',{'tenant_id':TENANT,'principal_id':PRINCIPAL}),
    ('role_assignments',{'tenant_id':TENANT,'principal_id':PRINCIPAL,'role_id':'ENTERPRISE_ADMIN'})])
def test_inactive_authorities_deny(source: Any,collection: str,filter_value: Any) -> None:
    """No active session can replace suspended/revoked source authority."""
    db,_,_=source
    db[collection].update_one(filter_value,{'$set':{'status':'REVOKED'}})
    with pytest.raises((FounderAdmissionError,RuntimeError)):execute(source)
    assert_empty(db)


def test_atomic_rollback_when_evidence_fails(source: Any,monkeypatch: Any) -> None:
    """Post-assignment evidence failure aborts assignment and consumption together."""
    db,command,_=source
    def fail(**kwargs: Any) -> None:raise TenantAuthorizationDecisionEvidenceRegistryError('synthetic-integrity-failure')
    from tools.eos.auth.tenant_authorization_decision_evidence_registry import TenantAuthorizationDecisionEvidenceRegistryError
    monkeypatch.setattr(command.command.evidence,'issue',fail)
    with pytest.raises(FounderAdmissionError,match='PERSISTENCE_OR_EVIDENCE_FAILURE'):execute(source)
    assert_empty(db)


def test_caller_abort_rolls_back_all_records(source: Any) -> None:
    """The command never commits its caller's pending transaction."""
    db,command,token=source
    with db.client.start_session() as s:
        s.start_transaction()
        command.execute(access_token=token,tenant_id=TENANT,principal_id=PRINCIPAL,idempotency_key='synthetic-once',
            expected_principal_revision=0,expected_membership_revision=0,expected_capacity_revision=0,expected_admin_revision=0,session=s)
        s.abort_transaction()
    assert_empty(db)


def test_missing_caller_transaction_and_stale_preflight_deny(source: Any) -> None:
    """Execution requires both a live caller transaction and a sub-minute preflight."""
    db, command, token = source
    arguments = dict(access_token=token, tenant_id=TENANT, principal_id=PRINCIPAL,
        idempotency_key='synthetic-once', expected_principal_revision=0,
        expected_membership_revision=0, expected_capacity_revision=0,
        expected_admin_revision=0)
    with pytest.raises(FounderAdmissionError, match='CALLER_TRANSACTION_REQUIRED'):
        command.execute(session=None, **arguments)
    command.preflight_at = 0
    with pytest.raises(FounderAdmissionError, match='PREFLIGHT_EXPIRED'):
        transaction(db, lambda session: command.execute(session=session, **arguments))
    assert_empty(db)


@pytest.mark.parametrize('status', [RoleAssignmentStatus.ACTIVE, RoleAssignmentStatus.REVOKED])
def test_existing_reader_assignment_in_any_state_denies(source: Any, status: RoleAssignmentStatus) -> None:
    """A prior active or revoked reader record cannot be overwritten or reinitialized."""
    db, _, _ = source
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(PRINCIPAL, TENANT, ROLE, status, 0), db['role_assignments'],
    )
    with pytest.raises(FounderAdmissionError, match='ASSIGNMENT_ALREADY_EXISTS'):
        execute(source)
    assert db[COLLECTION].count_documents({'tenant_id': TENANT}) == 0
    assert db['tenant_authorization_decision_evidence'].count_documents({'tenant_id': TENANT}) == 0
    persisted = RoleAssignmentRepository.resolve(PRINCIPAL, TENANT, ROLE, db['role_assignments'])
    assert persisted.status is status and persisted.revision == 0


def test_single_use_divergent_replay_and_revocation_terminality(source: Any) -> None:
    """Same or divergent re-execution cannot regrant a revoked or deleted role."""
    db,command,_=source
    execute(source)
    with pytest.raises(FounderAdmissionError,match='ALREADY_CONSUMED'):execute(source)
    with pytest.raises(FounderAdmissionError,match='IDEMPOTENCY_CONFLICT'):execute(source,idempotency_key='divergent')
    RoleAssignmentRepository.compare_and_swap(RoleAssignmentAuthority(PRINCIPAL,TENANT,ROLE,RoleAssignmentStatus.REVOKED,1),0,db['role_assignments'])
    assert command.readback()['assignment_status']=='REVOKED'
    with pytest.raises(FounderAdmissionError,match='ALREADY_CONSUMED'):execute(source)
    db['role_assignments'].delete_one({'tenant_id':TENANT,'principal_id':PRINCIPAL,'role_id':ROLE})
    with pytest.raises(FounderAdmissionError,match='ALREADY_CONSUMED'):execute(source)
    assert command.readback()['assignment_status']=='ABSENT'
    assert db[COLLECTION].count_documents({'tenant_id':TENANT})==1


def test_concurrent_consumption_one_winner(source: Any) -> None:
    """Deterministic start arbitration yields one commit and one permanent denial."""
    db,_,_=source;barrier=Barrier(2)
    def worker() -> str:
        barrier.wait()
        try:execute(source);return 'COMMITTED'
        except FounderAdmissionError as error:return error.code
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(lambda _:worker(),range(2)))
    assert results.count('COMMITTED')==1
    assert all(v=='COMMITTED' or v in {'FOUNDER_ADMISSION_ALREADY_CONSUMED','FOUNDER_ADMISSION_CONCURRENT_CONSUMPTION_DENIED'} for v in results)
    assert db[COLLECTION].count_documents({'tenant_id':TENANT})==1
    assert db['role_assignments'].count_documents({'tenant_id':TENANT,'principal_id':PRINCIPAL,'role_id':ROLE})==1


def test_evidence_corruption_and_missing_index_denied(source: Any) -> None:
    """Damaged governance cannot be trusted, and unindexed execution never starts."""
    db,command,_=source
    db[COLLECTION].drop_index('founder_development_decision_once')
    with pytest.raises(FounderAdmissionError,match='INDEX_REQUIRED'):execute(source)
    assert_empty(db)
    command.provision_evidence_indexes();execute(source)
    db[COLLECTION].update_one({'tenant_id':TENANT},{'$set':{'permissions':['*']}})
    with pytest.raises(FounderAdmissionError,match='EVIDENCE_INVALID'):command.readback()


# ARTIFACT: test_founder_development_admission_real_mongo.py
# VERSION: v1.0.1
# AUTHORITY BOUNDARY: New isolated contract certification only; no canonical mutations
# TENANT POSTURE: Exact IDs in task-owned UUID database; no protected Mongo target
# FAIL-CLOSED POSTURE: Missing infrastructure is a failure; replay/currentness/production denials required
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
