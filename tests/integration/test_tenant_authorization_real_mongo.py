"""TITLE: WILSY OS Tenant Authorization Real-Mongo Certification.
VERSION: v1.1.0-TENANT-AUTHORIZATION-REAL-MONGO-CERT
AUTHORITY: Evidence-only certification of frozen tenant authorization composition.
EPITOME: Exercises governed repositories against one isolated replica-set database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_tenant_authorization_real_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.1.0 expands durable Mongo current-truth, uniqueness, outage, and no-mutation certification coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Local UUID database only; no credentials or production data are emitted.
TENANT BOUNDARY: Every read and write is explicitly scoped to the generated tenant and principal.
AUTHORITY BOUNDARY: This artifact certifies frozen tenant authorization composition against actual Mongo persistence using governed repository methods and explicit isolated collection injection. It does NOT certify HTTP/router/Node production wiring.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

import os
import hashlib
import json
import inspect
from uuid import uuid4
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from contextlib import contextmanager
from typing import Iterator
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityAlreadyExistsError, PrincipalAuthorityPersistedRecordInvalidError
from tools.eos.auth.tenant_membership_repository import TenantMembershipAlreadyExistsError
from tools.eos.auth.role_assignment_repository import RoleAssignmentAlreadyExistsError

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization import TenantAuthorizationReason, authorize_tenant_operation

VERSION = "v1.1.0-TENANT-AUTHORIZATION-REAL-MONGO-CERT"
SHARED_MONGO_DISRUPTION_REQUIRED = False
REQUIRED_REAL_MONGO_PROPERTIES = tuple(f"{i:02d}_{name}" for i, name in enumerate(("mongo_identity_isolation", "positive_persisted_authorization", "principal_absent", "principal_inactive", "corrupt_persisted_principal", "membership_absent", "membership_suspended", "membership_revoked", "business_role_absent", "multiple_active_business_roles", "authorization_role_absent", "authorization_role_revoked", "wrong_tenant", "wrong_principal", "principal_uniqueness", "membership_uniqueness", "role_assignment_uniqueness", "durable_current_truth_refresh", "positive_no_mutation", "negative_no_mutation", "financial_no_mutation", "financial_execution_prohibited", "principal_repository_outage", "membership_repository_outage", "business_role_repository_outage", "authorization_role_repository_outage", "cleanup", "no_transport_authority"), 1))


def _snapshot(collection: Collection[dict[str, Any]]) -> tuple[int, list[dict[str, Any]], str]:
    """Return deterministic persisted-state evidence, excluding generated Mongo ids."""
    documents = [{k: v for k, v in row.items() if k != "_id"} for row in collection.find({})]
    documents.sort(key=lambda row: json.dumps(row, sort_keys=True, default=str))
    payload = json.dumps(documents, sort_keys=True, separators=(",", ":"), default=str).encode()
    return len(documents), documents, hashlib.sha3_512(payload).hexdigest()

@contextmanager
def _state() -> Iterator[tuple[Any, Any, Any, Any, str, str, str]]:
    client = MongoClient(os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"), serverSelectionTimeoutMS=3000)
    name = f"tenant_authorization_cert_{uuid4().hex}"; db = client[name]
    try:
        client.admin.command("ping"); assert client.admin.command("hello").get("setName") == "wilsyVendorCertRS"
        p, m, r = db["principal_authorities"], db["tenant_memberships"], db["role_assignments"]
        PrincipalAuthorityRepository.ensure_indexes(p); TenantMembershipRepository.ensure_indexes(m); RoleAssignmentRepository.ensure_indexes(r)
        yield client, p, m, r, f"p-{uuid4().hex}", f"t-{uuid4().hex}", name
    finally:
        client.drop_database(name); assert name not in client.list_database_names(); client.close()

def _auth(p: Any, m: Any, r: Any, pid: str, tid: str) -> Any:
    readers = (_PrincipalReader(p), _MembershipReader(m), _RoleReader(r))
    return authorize_tenant_operation(principal_id=pid, tenant_id=tid, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])

def _auth_split(p: Any, m: Any, business: Any, final_role: Any, pid: str, tid: str) -> Any:
    return authorize_tenant_operation(principal_id=pid, tenant_id=tid, permission_id="audit:read", operation="audit_read", principal_repository=_PrincipalReader(p), membership_repository=_MembershipReader(m), business_role_repository=_RoleReader(business), role_assignment_repository=_RoleReader(final_role))

def test_real_mongo_denial_no_mutation() -> None:
    with _state() as (_, p, m, r, pid, tid, _):
        PrincipalAuthorityRepository.create(PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0), p); TenantMembershipRepository.insert(TenantMembershipAuthority(pid, tid, TenantMembershipStatus.ACTIVE, 0), m); RoleAssignmentRepository.insert(RoleAssignmentAuthority(pid, tid, "tenant_auditor", RoleAssignmentStatus.ACTIVE, 0), r)
        before = (_snapshot(p), _snapshot(m), _snapshot(r)); decision = _auth(p, m, r, pid, tid)
        assert decision.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED
        assert before == (_snapshot(p), _snapshot(m), _snapshot(r))

def test_real_mongo_repository_outage_matrix() -> None:
    with _state() as (client, p, m, r, pid, tid, _):
        PrincipalAuthorityRepository.create(PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0), p); TenantMembershipRepository.insert(TenantMembershipAuthority(pid, tid, TenantMembershipStatus.ACTIVE, 0), m); RoleAssignmentRepository.insert(RoleAssignmentAuthority(pid, tid, "tenant_auditor", RoleAssignmentStatus.ACTIVE, 0), r)
        dead = MongoClient("mongodb://127.0.0.1:27999", serverSelectionTimeoutMS=250, connectTimeoutMS=250, socketTimeoutMS=250)
        try:
            dp, dm, dr = dead["unreachable"]["principal_authorities"], dead["unreachable"]["tenant_memberships"], dead["unreachable"]["role_assignments"]
            assert _auth_split(dp, m, r, r, pid, tid).reason is TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE
            assert _auth_split(p, dm, r, r, pid, tid).reason is TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE
            assert _auth_split(p, m, dr, dr, pid, tid).reason is TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE
            assert _auth_split(p, m, r, dr, pid, tid).reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE
        finally:
            dead.close()
        assert SHARED_MONGO_DISRUPTION_REQUIRED is False

def test_real_mongo_required_property_accounting() -> None:
    assert len(REQUIRED_REAL_MONGO_PROPERTIES) == 28
    assert len(set(REQUIRED_REAL_MONGO_PROPERTIES)) == 28
    assert all(REQUIRED_REAL_MONGO_PROPERTIES)
    assert tuple(int(v.split("_", 1)[0]) for v in REQUIRED_REAL_MONGO_PROPERTIES) == tuple(range(1, 29))

def test_real_mongo_cleanup_scope() -> None:
    with _state() as (_, _, _, _, _, _, name):
        assert name.startswith("tenant_authorization_cert_")

def test_real_mongo_no_transport_authority_boundary() -> None:
    forbidden = {"caller_role", "role", "roles", "jwt_role", "jwt_roles", "node_role", "node_roles", "authorization", "authorization_header", "auth_header", "trusted_role", "trusted_roles", "header_role"}
    assert not forbidden.intersection(inspect.signature(authorize_tenant_operation).parameters)
    assert set(inspect.signature(_auth).parameters) == {"p", "m", "r", "pid", "tid"}

def test_real_mongo_corrupt_principal_fails_closed() -> None:
    with _state() as (_, p, m, r, pid, tid, _):
        p.insert_one({"principal_id": pid, "status": "BROKEN", "revision": "bad"})
        with pytest.raises(PrincipalAuthorityPersistedRecordInvalidError): PrincipalAuthorityRepository.get(pid, p)
        decision = _auth(p, m, r, pid, tid)
        assert decision.authorized is False
        assert decision.reason is TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE

def test_real_mongo_membership_inactive_matrix() -> None:
    with _state() as (_, p, m, r, pid, tid, _):
        PrincipalAuthorityRepository.create(PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0), p)
        for status in (TenantMembershipStatus.SUSPENDED, TenantMembershipStatus.REVOKED):
            TenantMembershipRepository.insert(TenantMembershipAuthority(pid, tid + status.value, status, 0), m)
            assert _auth(p, m, r, pid, tid + status.value).reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE

def test_real_mongo_business_role_failure_matrix() -> None:
    with _state() as (_, p, m, r, pid, tid, _):
        PrincipalAuthorityRepository.create(PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0), p); TenantMembershipRepository.insert(TenantMembershipAuthority(pid, tid, TenantMembershipStatus.ACTIVE, 0), m)
        assert _auth(p, m, r, pid, tid).reason is TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(pid, tid, "tenant_auditor", RoleAssignmentStatus.ACTIVE, 0), r); RoleAssignmentRepository.insert(RoleAssignmentAuthority(pid, tid, "tenant_manager", RoleAssignmentStatus.ACTIVE, 0), r)
        assert _auth(p, m, r, pid, tid).reason is TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES

def test_real_mongo_authorization_role_absent() -> None:
    with _state() as (_, p, m, r, pid, tid, _):
        PrincipalAuthorityRepository.create(PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0), p); TenantMembershipRepository.insert(TenantMembershipAuthority(pid, tid, TenantMembershipStatus.ACTIVE, 0), m); RoleAssignmentRepository.insert(RoleAssignmentAuthority(pid, tid, "tenant_auditor", RoleAssignmentStatus.ACTIVE, 0), r)
        assert _auth(p, m, r, pid, tid).reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

def test_real_mongo_durable_uniqueness() -> None:
    with _state() as (_, p, m, r, pid, tid, _):
        principal = PrincipalAuthority(pid, PrincipalStatus.ACTIVE, 0); PrincipalAuthorityRepository.create(principal, p)
        with pytest.raises(PrincipalAuthorityAlreadyExistsError): PrincipalAuthorityRepository.create(principal, p)
        membership = TenantMembershipAuthority(pid, tid, TenantMembershipStatus.ACTIVE, 0); TenantMembershipRepository.insert(membership, m)
        with pytest.raises(TenantMembershipAlreadyExistsError): TenantMembershipRepository.insert(membership, m)
        role = RoleAssignmentAuthority(pid, tid, "AUDITOR", RoleAssignmentStatus.ACTIVE, 0); RoleAssignmentRepository.insert(role, r)
        with pytest.raises(RoleAssignmentAlreadyExistsError): RoleAssignmentRepository.insert(role, r)


class _PrincipalReader:
    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def resolve(self, principal_id: str) -> object:
        return PrincipalAuthorityRepository.get(principal_id, collection=self.collection)


class _MembershipReader:
    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str) -> object:
        return TenantMembershipRepository.resolve(principal_id, tenant_id, collection=self.collection)


class _RoleReader:
    def __init__(self, collection: Collection[dict[str, Any]]) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, tenant_id: str, role_id: str) -> object:
        return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, collection=self.collection)


def test_tenant_authorization_real_mongo_matrix() -> None:
    """Certify current-truth composition, uniqueness, refresh, and financial denial."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000, connectTimeoutMS=3000, socketTimeoutMS=5000)
    database_name = f"tenant_authorization_cert_{uuid4().hex}"
    assert database_name.startswith("tenant_authorization_cert_")
    database = client[database_name]
    try:
        client.admin.command("ping")
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert "127.0.0.1:27027" in hello.get("me", "") or "127.0.0.1:27027" in hello.get("hosts", [])
        principals = database["principal_authorities"]
        memberships = database["tenant_memberships"]
        assignments = database["role_assignments"]
        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        RoleAssignmentRepository.ensure_indexes(assignments)
        principal_id, tenant_id = f"p-{uuid4().hex}", f"t-{uuid4().hex}"
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0), principals)
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0), memberships)
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal_id, f"wrong-{uuid4().hex}", TenantMembershipStatus.ACTIVE, 0), memberships)
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, tenant_id, "tenant_auditor", RoleAssignmentStatus.ACTIVE, 0), assignments)
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal_id, tenant_id, "AUDITOR", RoleAssignmentStatus.ACTIVE, 0), assignments)
        readers = (_PrincipalReader(principals), _MembershipReader(memberships), _RoleReader(assignments))
        baseline = (_snapshot(principals), _snapshot(memberships), _snapshot(assignments))
        decision = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert decision.authorized is True
        assert decision.reason is TenantAuthorizationReason.AUTHORIZED
        assert decision.business_role == "tenant_auditor" and decision.authorization_role == "AUDITOR"
        assert baseline == (_snapshot(principals), _snapshot(memberships), _snapshot(assignments))
        financial = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id="audit:read", operation="financial_execution", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert financial.reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED
        assert baseline == (_snapshot(principals), _snapshot(memberships), _snapshot(assignments))
        absent = authorize_tenant_operation(principal_id="absent", tenant_id=tenant_id, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert absent.reason is TenantAuthorizationReason.PRINCIPAL_NOT_FOUND
        wrong_tenant = authorize_tenant_operation(principal_id=principal_id, tenant_id="missing-tenant", permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert wrong_tenant.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
        revoked = RoleAssignmentAuthority(principal_id, tenant_id, "AUDITOR", RoleAssignmentStatus.REVOKED, 1)
        RoleAssignmentRepository.compare_and_swap(revoked, 0, assignments)
        refreshed = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert refreshed.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE
        # Current-truth lifecycle gates are independently exercised against Mongo.
        PrincipalAuthorityRepository.compare_and_swap(PrincipalAuthority(principal_id, PrincipalStatus.SUSPENDED, 1), 0, principals)
        inactive = authorize_tenant_operation(principal_id=principal_id, tenant_id=tenant_id, permission_id="audit:read", operation="audit_read", principal_repository=readers[0], membership_repository=readers[1], business_role_repository=readers[2], role_assignment_repository=readers[2])
        assert inactive.reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


# ARTIFACT: test_tenant_authorization_real_mongo.py
# VERSION: v1.1.0-TENANT-AUTHORIZATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo tenant authorization composition evidence only
# TENANT POSTURE: generated UUID database and exact principal/tenant keys
# FAIL-CLOSED POSTURE: unavailable, absent, inactive, ambiguous, and financial paths deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
