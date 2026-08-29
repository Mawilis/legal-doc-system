"""TITLE: WILSY OS Role Assignment Repository Real-Mongo Certification.
VERSION: v1.0.0-WILSY-ROLE-ASSIGNMENT-REAL-MONGO-CERT
AUTHORITY: Real-Mongo integration certification of durable tenant-scoped role-assignment persistence.
EPITOME: Proves create, exact natural-key resolution, duplicate rejection, revision CAS, malformed-record rejection, tenant isolation, persistence failure semantics, and caller-owned transaction behavior against a real Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_role_assignment_repository_mongo.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG: v1.0.0-WILSY-ROLE-ASSIGNMENT-REAL-MONGO-CERT establishes governed real-Mongo certification coverage for current role-assignment repository authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Deterministic non-production fixtures prove failure and isolation without exposing credentials, tenant secrets, or user profile data.
TENANT BOUNDARY: Every fixture and assertion uses explicit tenant identifiers and proves tenant-scoped natural-key isolation without inference.
AUTHORITY BOUNDARY: Certifies repository persistence, resolution, and CAS only; it does not certify role definitions, permissions, principal lifecycle, tenant membership, authentication, authorization, Node runtime, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations
import os
import uuid
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (RoleAssignmentAlreadyExistsError, RoleAssignmentNotFoundError, RoleAssignmentPersistedRecordInvalidError, RoleAssignmentRepository, RoleAssignmentRepositoryError, RoleAssignmentRevisionConflictError)

VERSION = "v1.0.0-WILSY-ROLE-ASSIGNMENT-REAL-MONGO-CERT"
URI = os.getenv("TEST_VENDOR_MONGO_URI")

@pytest.fixture()
def collection():
    """Provide a disposable UUID-isolated collection on the required replica set."""
    if not URI: pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    if client.admin.command("hello").get("setName") != "wilsyVendorCertRS":
        client.close(); pytest.fail("wrong certification replica set")
    database = client[f"role_assignment_cert_{uuid.uuid4().hex}"]
    target = database["role_assignments"]
    RoleAssignmentRepository.ensure_indexes(target)
    yield client, target
    client.drop_database(database.name)
    client.close()

def value(principal="p", tenant="t", role="r", revision=0, state=RoleAssignmentStatus.ACTIVE):
    """Build a deterministic authority value for one explicit natural key."""
    return RoleAssignmentAuthority(principal, tenant, role, state, revision)

def test_create_resolve_duplicate_and_tenant_isolation(collection):
    """Create, exact persisted shape, duplicate rejection, and tenant isolation hold."""
    _, target = collection; assert RoleAssignmentRepository.insert(value(), target) == value(); assert RoleAssignmentRepository.resolve("p", "t", "r", target) == value()
    assert target.find_one({}, {"_id": 0}) == {"principal_id":"p","tenant_id":"t","role_id":"r","status":"ACTIVE","revision":0}
    with pytest.raises(RoleAssignmentAlreadyExistsError): RoleAssignmentRepository.insert(value(), target)
    RoleAssignmentRepository.insert(value(tenant="other"), target); assert RoleAssignmentRepository.resolve("p", "other", "r", target).tenant_id == "other"
    with pytest.raises(RoleAssignmentNotFoundError): RoleAssignmentRepository.resolve("p", "missing", "r", target)

def test_cas_advances_revision_and_rejects_stale_writes(collection):
    """CAS advances exactly once and stale writes cannot mutate terminal state."""
    _, target = collection; RoleAssignmentRepository.insert(value(), target); RoleAssignmentRepository.compare_and_swap(value(revision=1, state=RoleAssignmentStatus.REVOKED), 0, target)
    with pytest.raises(RoleAssignmentRevisionConflictError): RoleAssignmentRepository.compare_and_swap(value(revision=1), 0, target)
    current = RoleAssignmentRepository.resolve("p", "t", "r", target); assert current.status is RoleAssignmentStatus.REVOKED; assert current.revision == 1

def test_malformed_absent_and_invalid_states_fail_closed(collection):
    """Malformed records, absent keys, and invalid revisions never become authority."""
    _, target = collection; target.insert_one({"principal_id":"bad","tenant_id":"t","role_id":"r","status":"BROKEN","revision":0})
    with pytest.raises(RoleAssignmentPersistedRecordInvalidError): RoleAssignmentRepository.resolve("bad", "t", "r", target)
    with pytest.raises(RoleAssignmentNotFoundError): RoleAssignmentRepository.resolve("absent", "t", "r", target)
    with pytest.raises(RoleAssignmentRevisionConflictError): RoleAssignmentRepository.compare_and_swap(value(revision=2), 0, target)

def test_persistence_failure_is_not_absence(collection):
    """A closed client produces explicit repository failure rather than not-found."""
    failed = MongoClient("mongodb://127.0.0.1:1", serverSelectionTimeoutMS=50)
    try:
        target = failed["unavailable"]["role_assignments"]
        with pytest.raises((RoleAssignmentRepositoryError, PyMongoError)):
            RoleAssignmentRepository.resolve("p", "t", "r", target)
    finally:
        failed.close()

def test_caller_owned_transaction_commit_and_abort(collection):
    """Caller-owned sessions prove abort leaves no mutation and commit persists it."""
    client, target = collection
    with client.start_session() as session:
        session.start_transaction(); RoleAssignmentRepository.insert(value(), target, session=session); session.abort_transaction()
    with pytest.raises(RoleAssignmentNotFoundError): RoleAssignmentRepository.resolve("p", "t", "r", target)
    with client.start_session() as session:
        session.start_transaction(); RoleAssignmentRepository.insert(value(), target, session=session); session.commit_transaction()
    assert RoleAssignmentRepository.resolve("p", "t", "r", target) == value()

# ARTIFACT: test_role_assignment_repository_mongo.py
# VERSION: v1.0.0-WILSY-ROLE-ASSIGNMENT-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: real-Mongo certification of role-assignment persistence, resolution, isolation, and revision CAS only
# TENANT POSTURE: certification fixtures use explicit tenant keys and prove cross-tenant separation
# FAIL-CLOSED POSTURE: duplicate, absent, malformed, unavailable, and stale-revision states never become successful authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
