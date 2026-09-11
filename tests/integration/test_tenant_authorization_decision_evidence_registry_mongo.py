"""WILSY OS governed real-Mongo authorization-evidence certificate.

VERSION: v1.1.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REAL-MONGO-CERT
AUTHORITY: Runtime persistence and caller-owned transaction evidence only.
TENANT BOUNDARY: Every fixture and lookup is explicitly tenant scoped.
FINANCIAL AUTHORITY: Kennel EOS exclusively executes financial operations.
"""
from __future__ import annotations
import os
from uuid import uuid4
import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidenceRegistry,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth import permission_namespace, roles, tenant_authority_policy, tenant_authorization

class _Repo:
    def __init__(self, collection, kind): self.collection, self.kind = collection, kind
    def resolve(self, *args, **kwargs):
        session = kwargs.get("session")
        if self.kind == "principal": return PrincipalAuthorityRepository.get(args[0], self.collection, session=session)
        if self.kind == "membership": return TenantMembershipRepository.resolve(args[0], args[1], self.collection, session=session)
        return RoleAssignmentRepository.resolve(args[0], args[1], args[2], self.collection, session=session)

def _registry(db):
    return TenantAuthorizationDecisionEvidenceRegistry(db["evidence"], principal_repository=_Repo(db["principals"], "principal"), membership_repository=_Repo(db["memberships"], "membership"), role_assignment_repository=_Repo(db["assignments"], "assignment"), business_role_repository=_Repo(db["assignments"], "assignment"))

def _seed(db, tenant, principal):
    PrincipalAuthorityRepository.ensure_indexes(db["principals"]); TenantMembershipRepository.ensure_indexes(db["memberships"]); RoleAssignmentRepository.ensure_indexes(db["assignments"])
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0), db["principals"])
    TenantMembershipRepository.insert(TenantMembershipAuthority(principal, tenant, TenantMembershipStatus.ACTIVE, 7), db["memberships"])
    for role in ("tenant_owner", "ENTERPRISE_ADMIN"):
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal, tenant, role, RoleAssignmentStatus.ACTIVE, 0), db["assignments"])
        db["assignments"].update_one({"principal_id": principal, "tenant_id": tenant, "role_id": role}, {"$set": {"revision": 11}})

def _request(tenant, principal, key, subject="subject"):
    return dict(tenant_id=tenant, principal_id=principal, operation="platform_billing_release", permission="platform_billing:release", subject_reference=subject, subject_evidence_fingerprint="a" * 128, idempotency_key=key)

def _client(): return MongoClient(os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"), serverSelectionTimeoutMS=2000)

def test_real_mongo_authority_transactions_replay_revocation_and_corruption():
    client = _client(); db = client[f"wilsy_auth_evidence_{uuid4().hex}"]; registry = _registry(db); registry.ensure_indexes()
    try:
        info = db["evidence"].index_information()
        assert any(i.get("unique") and list(i["key"]) == [("tenant_id", 1), ("idempotency_key", 1)] for i in info.values())
        assert any(i.get("unique") and list(i["key"]) == [("authorization_decision_id", 1)] for i in info.values())
        tenant, principal, key = "tenant-a", "principal-a", "key-a"; _seed(db, tenant, principal)
        with client.start_session() as session:
            with pytest.raises(TenantAuthorizationDecisionEvidenceTransactionRequiredError): registry.issue(**_request(tenant, principal, key), session=session)
            with session.start_transaction():
                first = registry.issue(**_request(tenant, principal, key), session=session)
                assert db["evidence"].count_documents({}) == 0
        assert db["evidence"].count_documents({}) == 1
        assert (first.business_role, first.authorization_role, first.membership_revision, first.role_assignment_revision) == ("tenant_owner", "ENTERPRISE_ADMIN", 7, 11)
        assert (first.permission_namespace_version, first.authorization_role_policy_version, first.tenant_business_role_policy_version, first.tenant_authorization_composition_version) == (permission_namespace.VERSION, roles.VERSION, tenant_authority_policy.VERSION, tenant_authorization.VERSION)
        original = first
        with client.start_session() as session:
            with session.start_transaction():
                assert registry.issue(**_request(tenant, principal, key), session=session) == original
                with pytest.raises(TenantAuthorizationDecisionEvidenceConflictError): registry.issue(**_request(tenant, principal, key, "other"), session=session)
        db["assignments"].update_one({"principal_id": principal, "tenant_id": tenant, "role_id": "ENTERPRISE_ADMIN"}, {"$set": {"status": "REVOKED"}})
        with client.start_session() as session:
            with session.start_transaction(): assert registry.issue(**_request(tenant, principal, key), session=session) == original
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(TenantAuthorizationDecisionEvidenceAuthorizationDeniedError): registry.issue(**_request(tenant, principal, "new-key"), session=session)
        assert db["evidence"].count_documents({"idempotency_key": "new-key"}) == 0
        db["evidence"].update_one({"idempotency_key": key}, {"$set": {"authorization_evidence_fingerprint": "corrupt"}})
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(Exception): registry.issue(**_request(tenant, principal, key), session=session)
        assert db["evidence"].count_documents({"idempotency_key": key}) == 1
        assert "payment" not in set(db["evidence"].find_one({"idempotency_key": key}) or {})
        _seed(db, "tenant-b", "principal-b")
        with client.start_session() as session:
            with pytest.raises(RuntimeError):
                with session.start_transaction():
                    registry.issue(**_request("tenant-b", "principal-b", "abort-key"), session=session)
                    raise RuntimeError("abort")
        assert db["evidence"].count_documents({"tenant_id": "tenant-b"}) == 0
    finally: db.client.drop_database(db.name); client.close()

def test_real_mongo_tenant_scoped_keys_and_duplicate_indexes():
    client = _client(); db = client[f"wilsy_auth_evidence_{uuid4().hex}"]; registry = _registry(db); registry.ensure_indexes()
    try:
        for tenant in ("tenant-a", "tenant-b"): _seed(db, tenant, f"principal-{tenant[-1]}")
        values = []
        for tenant in ("tenant-a", "tenant-b"):
            with client.start_session() as session:
                with session.start_transaction(): values.append(registry.issue(**_request(tenant, f"principal-{tenant[-1]}", "same-key"), session=session))
        assert values[0].authorization_decision_id != values[1].authorization_decision_id; assert db["evidence"].count_documents({}) == 2
        doc = values[0].to_persisted()
        with pytest.raises(DuplicateKeyError): db["evidence"].insert_one(dict(doc, authorization_decision_id=uuid4().hex))
        with pytest.raises(DuplicateKeyError): db["evidence"].insert_one(dict(doc, tenant_id="tenant-c", idempotency_key="other-key"))
    finally: db.client.drop_database(db.name); client.close()

def test_real_mongo_missing_session_rejected_without_evidence():
    client = _client(); db = client[f"wilsy_auth_evidence_{uuid4().hex}"]; registry = _registry(db); registry.ensure_indexes()
    try:
        _seed(db, "tenant-m", "principal-m")
        with pytest.raises(TenantAuthorizationDecisionEvidenceTransactionRequiredError): registry.issue(**_request("tenant-m", "principal-m", "missing-key"), session=None)
        assert db["evidence"].count_documents({"tenant_id": "tenant-m", "idempotency_key": "missing-key"}) == 0
    finally: db.client.drop_database(db.name); client.close()

def test_real_mongo_corrupt_basis_reference_fails_closed():
    client = _client(); db = client[f"wilsy_auth_evidence_{uuid4().hex}"]; registry = _registry(db); registry.ensure_indexes()
    try:
        _seed(db, "tenant-basis", "principal-basis")
        with client.start_session() as session:
            with session.start_transaction(): original = registry.issue(**_request("tenant-basis", "principal-basis", "basis-key"), session=session)
        db["evidence"].update_one({"idempotency_key": "basis-key"}, {"$set": {"authorization_basis_reference": "corrupt-basis"}})
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(Exception): registry.issue(**_request("tenant-basis", "principal-basis", "basis-key"), session=session)
        row = db["evidence"].find_one({"idempotency_key": "basis-key"}); assert row is not None; assert row["authorization_decision_id"] == original.authorization_decision_id; assert db["evidence"].count_documents({"idempotency_key": "basis-key"}) == 1
    finally: db.client.drop_database(db.name); client.close()

def test_real_mongo_strict_extra_field_corruption_fails_closed():
    client = _client(); db = client[f"wilsy_auth_evidence_{uuid4().hex}"]; registry = _registry(db); registry.ensure_indexes()
    try:
        _seed(db, "tenant-shape", "principal-shape")
        with client.start_session() as session:
            with session.start_transaction(): original = registry.issue(**_request("tenant-shape", "principal-shape", "shape-key"), session=session)
        db["evidence"].update_one({"idempotency_key": "shape-key"}, {"$set": {"unexpected_runtime_test_field": "forbidden"}})
        with client.start_session() as session:
            with session.start_transaction():
                with pytest.raises(Exception): registry.issue(**_request("tenant-shape", "principal-shape", "shape-key"), session=session)
        row = db["evidence"].find_one({"idempotency_key": "shape-key"}); assert row is not None; assert row["authorization_decision_id"] == original.authorization_decision_id; assert db["evidence"].count_documents({"idempotency_key": "shape-key"}) == 1
    finally: db.client.drop_database(db.name); client.close()

# ARTIFACT: test_tenant_authorization_decision_evidence_registry_mongo.py
# VERSION: v1.1.0-TENANT-AUTHORIZATION-DECISION-EVIDENCE-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: canonical real-Mongo evidence only; no approval or execution.
# TENANT POSTURE: explicit tenant-scoped idempotency and provenance.
# FAIL-CLOSED POSTURE: transaction, denial, replay conflict, corruption, and uniqueness failures are explicit.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
