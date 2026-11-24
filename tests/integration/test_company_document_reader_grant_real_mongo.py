"""TITLE: WILSY OS Company Reader Provisioning Real-Mongo Certificate.
VERSION: v1.1.0-FOUNDER-INIT-MONGO-CERT
AUTHORITY: Disposable local replica set only; no canonical IAM or document writes.
EPITOME: Prove atomic narrow grants, audit/replay, denial, currentness, revocation,
rollback and independent Mission/Strategy publications using source authorities.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_company_document_reader_grant_real_mongo.py
COLLABORATION / OWNERSHIP: Existing reader grant, central IAM and document registry.
CERTIFICATION / UPDATE DATE: 2026-11-14
CHANGELOG:
    v1.1.0-FOUNDER-INIT-MONGO-CERT — Certifies the existing company-document reader grant and real-Mongo authority boundaries.
v1.0.0-COMPANY-READER-REAL-MONGO-CERT adds UUID-owned database evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque actors only; explicit loopback URI.
TENANT BOUNDARY: Exact company tenant within test-owned database; foreign denials.
AUTHORITY BOUNDARY: Test provisioning is not Founder acceptance or real approval.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, local
from datetime import datetime, timezone
import os
from uuid import uuid4
from typing import Any

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.company_document_reader_grant import CompanyDocumentReaderGrant, CompanyReaderGrantError
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository, RoleAssignmentNotFoundError
from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.auth.authorization_role_revocation_evidence_registry import AuthorizationRoleRevocationEvidenceRegistry
from tools.eos.api.authorization_role_revocation_router import _build_command
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID as TENANT
from tools.eos.saas.company_operating_document_registry import CompanyOperatingDocumentRegistry
from tools.eos.saas.domain.company_operating_document import CompanyDocumentClass, instant

VERSION = "v1.1.0-FOUNDER-INIT-MONGO-CERT"
ACTOR, TARGET = "synthetic-independent-grantor", "synthetic-existing-company-owner"
ROLE = "COMPANY_DOCUMENT_READER"


@pytest.fixture
def source():
    """Create/drop only a unique local disposable database; unavailable is not a pass."""
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", "")
    if not uri.startswith("mongodb://127.0.0.1:27028/"):
        pytest.fail("Explicit owned local replica-set URI required")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000, tz_aware=True)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS" and hello.get("isWritablePrimary")
    db = client["wilsy_founder_dev_" + uuid4().hex]
    command = CompanyDocumentReaderGrant(db)
    for collection, owner in (("principal_authorities", PrincipalAuthorityRepository),
        ("tenant_memberships", TenantMembershipRepository), ("tenant_business_roles", TenantBusinessRoleRepository),
        ("role_assignments", RoleAssignmentRepository)):
        owner.ensure_indexes(db[collection])
    command.evidence.ensure_indexes()
    AuthorizationRoleRevocationEvidenceRegistry(db["authorization_role_revocation_evidence"]).ensure_indexes()
    CompanyOperatingDocumentRegistry(db).provision_indexes()
    now = datetime.now(timezone.utc)
    for principal, capacity, grants in ((ACTOR, "tenant_admin", ["ENTERPRISE_ADMIN"]),
                                      (TARGET, "tenant_owner", ["ENTERPRISE_ADMIN"])):
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0), db["principal_authorities"])
        TenantMembershipRepository.insert(TenantMembershipAuthority(principal, TENANT, TenantMembershipStatus.ACTIVE, 0), db["tenant_memberships"])
        TenantBusinessRoleRepository.insert(TenantBusinessRoleAuthority(principal, TENANT, capacity, TenantBusinessRoleStatus.ACTIVE, 0, now, None), db["tenant_business_roles"])
        for role in grants:
            RoleAssignmentRepository.insert(RoleAssignmentAuthority(principal, TENANT, role, RoleAssignmentStatus.ACTIVE, 0), db["role_assignments"])
    command.require_indexes()
    try:
        yield db, command
    finally:
        client.drop_database(db.name)
        client.close()


def transact(db, callback):
    """Own a real snapshot/majority+journal transaction for one source command."""
    with db.client.start_session() as session:
        return session.with_transaction(callback, read_concern=ReadConcern("snapshot"), write_concern=WriteConcern(w="majority", j=True))


def grant(source, **changes):
    """Use explicit independent decision references and revision-guarded target."""
    db, command = source
    payload = dict(actor_principal_id=ACTOR, tenant_id=TENANT, target_principal_id=TARGET,
        target_business_role="tenant_owner", expected_membership_revision=0, expected_capacity_revision=0,
        expected_assignment_revision=None, approval_reference="SYNTHETIC-INDEPENDENT-DECISION",
        reason_reference="SYNTHETIC-READ-ONLY-ACCESS", idempotency_key="synthetic-grant")
    payload.update(changes)
    return transact(db, lambda session: command.execute(**payload, session=session))


def decision(source, permission="company_operating_document:read", operation="company_operating_document_read", **changes):
    """Resolve current authority with no workforce records and no UI inference."""
    db, command = source
    args = dict(principal_id=TARGET, tenant_id=TENANT, permission_id=permission, operation=operation,
        principal_repository=command.principals, membership_repository=command.memberships,
        role_assignment_repository=command.reads, business_role_repository=command.reads)
    args.update(changes)
    return transact(db, lambda session: authorize_tenant_operation(**args, session=session))


def test_grant_commit_audit_replay_and_scope(source):
    """New authority and immutable evidence commit together; replay never duplicates."""
    db, command = source
    assert not decision(source).authorized
    first = grant(source)
    assert first["state"] == "NEWLY_GRANTED" and decision(source).authorized
    evidence = command.evidence.get(tenant_id=TENANT, authorization_decision_id=first["authorization_decision_id"])
    assert evidence.authorization_evidence_fingerprint == first["authorization_evidence_fingerprint"]
    assert evidence.business_role == "tenant_admin" and evidence.authorization_role == "ENTERPRISE_ADMIN"
    assert evidence.subject_evidence_fingerprint == first["intent_fingerprint"]
    assert grant(source) == {**first, "state": "EXACT_REPLAY"}
    with pytest.raises(CompanyReaderGrantError, match="IDEMPOTENCY_CONFLICT"):
        grant(source, reason_reference="different")
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 1
    assert not decision(source, tenant_id="foreign-company").authorized
    for permission, operation in (("company_operating_document:author", "company_operating_document_author"),
        ("company_operating_document:publish", "company_operating_document_publish"),
        ("tenant:role_assignment:write", "role_grant")):
        assert not decision(source, permission, operation).authorized
    assert db["workforce_relationships"].count_documents({}) == 0


@pytest.mark.parametrize("changes,code", [
    ({"actor_principal_id": TARGET}, "INDEPENDENT_AUTHORITY_REQUIRED"),
    ({"tenant_id": "foreign-company"}, "INDEPENDENT_AUTHORITY_REQUIRED"),
    ({"expected_membership_revision": 1}, "TARGET_REVISION_CONFLICT"),
    ({"expected_capacity_revision": 1}, "TARGET_REVISION_CONFLICT"),
    ({"expected_assignment_revision": 0}, "ASSIGNMENT_CONFLICT"),
])
def test_invalid_grants_leave_no_assignment_or_evidence(source, changes, code):
    """Invalid intent fails without partial role/evidence success."""
    db, _ = source
    with pytest.raises(CompanyReaderGrantError, match=code):
        grant(source, **changes)
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 0
    with pytest.raises(RoleAssignmentNotFoundError):
        RoleAssignmentRepository.resolve(TARGET, TENANT, ROLE, db["role_assignments"])


@pytest.mark.parametrize("kind", ["membership", "capacity", "grantor_role", "grantor_capacity"])
def test_live_authority_changes_reject_new_grant(source, kind):
    """Every current membership/capacity/role decision is source-owned and uncached."""
    db, _ = source
    if kind == "membership":
        db["tenant_memberships"].update_one({"principal_id": TARGET}, {"$set": {"status": "REVOKED", "revision": 1}})
    elif kind == "capacity":
        db["tenant_business_roles"].update_one({"principal_id": TARGET}, {"$set": {"status": "REVOKED", "revision": 1, "revoked_at": datetime.now(timezone.utc)}})
    elif kind == "grantor_role":
        db["role_assignments"].update_one({"principal_id": ACTOR}, {"$set": {"status": "REVOKED", "revision": 1}})
    else:
        db["tenant_business_roles"].update_one({"principal_id": ACTOR}, {"$set": {"business_role": "tenant_owner", "revision": 1}})
    with pytest.raises(CompanyReaderGrantError):
        grant(source)
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 0


def test_revocation_historic_replay_and_explicit_regrant(source):
    """Existing revocation immediately denies reads; old grant replay cannot resurrect."""
    db, _ = source
    first = grant(source)
    revoke = _build_command(db)
    transact(db, lambda session: revoke.execute(actor_principal_id=ACTOR, tenant_id=TENANT,
        target_principal_id=TARGET, target_role_id=ROLE, expected_target_assignment_revision=0,
        reason_reference="SYNTHETIC-REVOKE", idempotency_key="synthetic-revoke", session=session))
    assert not decision(source).authorized
    assert grant(source) == {**first, "state": "EXACT_REPLAY"}
    assert not decision(source).authorized
    new = grant(source, idempotency_key="synthetic-regrant", expected_assignment_revision=1)
    assert new["assignment_revision"] == 2 and decision(source).authorized


@pytest.mark.parametrize("collection", ["tenant_memberships", "tenant_business_roles"])
def test_revoked_target_currentness_immediately_denies_existing_grant(source, collection):
    """A durable reader assignment never outranks revoked membership or capacity."""
    db, _ = source
    grant(source)
    changes: dict[str, Any] = dict(status="REVOKED", revision=1)
    if collection == "tenant_business_roles":
        changes["revoked_at"] = datetime.now(timezone.utc)
    db[collection].update_one({"principal_id": TARGET}, {"$set": changes})
    assert not decision(source).authorized


def test_abort_and_evidence_failure_do_not_commit_partial_authority(source, monkeypatch):
    """A failed readback or caller abort rolls back both source-owned writes."""
    db, command = source
    original = command.evidence.find_by_idempotency
    calls = 0
    def broken_readback(**kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise CompanyReaderGrantError("SYNTHETIC_EVIDENCE_FAILURE")
        return original(**kwargs)
    monkeypatch.setattr(command.evidence, "find_by_idempotency", broken_readback)
    with pytest.raises(CompanyReaderGrantError, match="SYNTHETIC_EVIDENCE_FAILURE"):
        grant(source)
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 0
    assert not decision(source).authorized


def test_reader_grant_preserves_independent_source_publication(source):
    """Unpublished remains verified absence; each approved immutable document reads back."""
    db, _ = source
    grant(source)
    registry = CompanyOperatingDocumentRegistry(db)
    now = datetime.now(timezone.utc)
    for classification in CompanyDocumentClass:
        assert transact(db, lambda session: registry.current(TENANT, classification, now=now, session=session)) is None
        for action, revision, actor, payload in [
            ("CREATE_DRAFT", 0, "synthetic-author", dict(title="Synthetic " + classification.value,
                document_version="1.0.0", sections=[dict(section_id="purpose", title="Synthetic", body="Test-only content") ])),
            ("SUBMIT", 1, "synthetic-author", {}),
            ("PUBLISH", 2, "synthetic-publisher", dict(approval_reference="SYNTHETIC-APPROVAL", effective_from=instant(now))),
        ]:
            transact(db, lambda session: registry.command(TENANT, classification, actor_id=actor, action=action,
                payload=payload, expected_revision=revision, idempotency_key=uuid4().hex, now=now, session=session))
        published = transact(db, lambda session: registry.current(TENANT, classification, now=now, session=session))
        assert published.revision == 3 and published.title == "Synthetic " + classification.value
        assert published.author_principal_id != published.approved_by_principal_id
        assert decision(source).authorized
    assert db["company_operating_document_revisions"].count_documents({}) == 6



def test_concurrent_same_key_arbitration_has_one_durable_grant(source, monkeypatch):
    """Synchronize competing snapshots; a loser retries the whole intent only."""
    db, command = source
    original = command.evidence.find_by_idempotency
    barrier, seen = Barrier(2), local()
    def synchronized(**kwargs):
        value = original(**kwargs)
        if not getattr(seen, "ready", False):
            seen.ready = True
            barrier.wait(timeout=10)
        return value
    monkeypatch.setattr(command.evidence, "find_by_idempotency", synchronized)
    def run():
        try:
            return grant(source)
        except CompanyReaderGrantError as error:
            assert error.status == 409
            return None
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: run(), range(2)))
    monkeypatch.setattr(command.evidence, "find_by_idempotency", original)
    assert sum(result is not None and result["state"] == "NEWLY_GRANTED" for result in results) == 1
    assert grant(source)["state"] == "EXACT_REPLAY"
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 1
    assert db["role_assignments"].count_documents({"principal_id": TARGET, "role_id": ROLE}) == 1


def test_old_grant_evidence_does_not_authorize_revoked_grantor(source):
    """Immutable replay evidence never substitutes for current granting authority."""
    db, _ = source
    grant(source)
    db["role_assignments"].update_one({"principal_id": ACTOR}, {"$set": {"status": "REVOKED", "revision": 1}})
    with pytest.raises(CompanyReaderGrantError, match="GRANT_DENIED"):
        grant(source)
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 1


def test_missing_indexes_are_explicit_without_runtime_ddl(source):
    """Ordinary grant admission cannot rebuild the canonical arbitration indexes."""
    db, command = source
    db["role_assignments"].drop_index("principal_tenant_role_assignment_unique")
    before = db["role_assignments"].index_information()
    with pytest.raises(CompanyReaderGrantError, match="INDEX_REQUIRED"):
        command.require_indexes()
    assert db["role_assignments"].index_information() == before


def test_missing_target_is_denial_not_source_outage(source):
    """A lawful absent member does not acquire authority or pretend to be a DB fault."""
    with pytest.raises(CompanyReaderGrantError) as error:
        grant(source, target_principal_id="synthetic-absent-target")
    assert error.value.status == 403



def _founder_dev_enabled(monkeypatch, db, principal=TARGET):
    """Explicitly opt in only the UUID-owned disposable replica fixture."""
    monkeypatch.setenv("WILSY_FOUNDER_DEV_INIT", "DISPOSABLE_READER_ONLY")
    monkeypatch.setenv("WILSY_EOS_ENV", "development")
    monkeypatch.setenv("WILSY_FOUNDER_DEV_DB", db.name)
    monkeypatch.setenv("WILSY_FOUNDER_DEV_PRINCIPAL", principal)


def _founder_init(source, **changes):
    db, command = source
    args = dict(authenticated_principal_id=TARGET, tenant_id=TENANT,
                expected_membership_revision=0, expected_capacity_revision=0)
    args.update(changes)
    return transact(db, lambda session: command.execute_disposable_founder_initialization(
        **args, session=session))


def test_founder_disposable_init_one_time_revoke_and_no_privilege_escalation(source, monkeypatch):
    """Founder read only: one durable admission, no repeat, no author/admin powers."""
    db, command = source
    _founder_dev_enabled(monkeypatch, db)
    assert not decision(source).authorized
    first = _founder_init(source)
    assert first["administrative_grantor_appointed"] is False
    assert first["canonical_tenant_changed"] is False
    assert decision(source).authorized
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 1
    assert db["role_assignments"].count_documents({"principal_id": TARGET, "role_id": ROLE}) == 1
    for permission, operation in (("company_operating_document:author", "company_operating_document_author"),
                                  ("company_operating_document:publish", "company_operating_document_publish"),
                                  ("tenant:role_assignment:write", "role_grant")):
        assert not decision(source, permission, operation).authorized
    with pytest.raises(CompanyReaderGrantError, match="FOUNDER_DEV_ALREADY_CONSUMED"):
        _founder_init(source)
    # Revoke the reader assignment directly as fixture-owned synthetic lifecycle data.
    db["role_assignments"].update_one({"principal_id": TARGET, "role_id": ROLE},
                                      {"$set": {"status": "REVOKED", "revision": 1}})
    assert not decision(source).authorized
    with pytest.raises(CompanyReaderGrantError, match="FOUNDER_DEV_ALREADY_CONSUMED"):
        _founder_init(source)
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 1


@pytest.mark.parametrize("change,code", [
    ({"authenticated_principal_id": ACTOR}, "FOUNDER_DEV_DISABLED"),
    ({"tenant_id": "foreign-tenant"}, "FOUNDER_DEV_TENANT_DENIED"),
    ({"expected_membership_revision": 1}, "FOUNDER_DEV_AUTHORITY_DENIED"),
    ({"expected_capacity_revision": 1}, "FOUNDER_DEV_AUTHORITY_DENIED"),
])
def test_founder_disposable_init_rejects_wrong_actor_scope_or_revision(source, monkeypatch, change, code):
    """Reject inappropriate actor, other tenant and stale revision before writing."""
    db, _ = source
    _founder_dev_enabled(monkeypatch, db)
    with pytest.raises(CompanyReaderGrantError, match=code):
        _founder_init(source, **change)
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 0
    assert db["role_assignments"].count_documents({"principal_id": TARGET, "role_id": ROLE}) == 0


def test_founder_disposable_init_requires_opt_in_and_atomic_rollback(source, monkeypatch):
    """Disabled by default; aborted transaction cannot leave authority evidence."""
    db, command = source
    with pytest.raises(CompanyReaderGrantError, match="FOUNDER_DEV_DISABLED"):
        _founder_init(source)
    _founder_dev_enabled(monkeypatch, db)
    monkeypatch.setenv("WILSY_EOS_ENV", "production")
    with pytest.raises(CompanyReaderGrantError, match="FOUNDER_DEV_DISABLED"):
        _founder_init(source)
    monkeypatch.setenv("WILSY_EOS_ENV", "development")
    monkeypatch.setenv("WILSY_FOUNDER_DEV_DB", "wilsy")
    with pytest.raises(CompanyReaderGrantError, match="FOUNDER_DEV_DISABLED"):
        _founder_init(source)
    monkeypatch.setenv("WILSY_FOUNDER_DEV_DB", db.name)
    with pytest.raises(RuntimeError, match="SYNTHETIC_ABORT"):
        def abort(session):
            command.execute_disposable_founder_initialization(
                authenticated_principal_id=TARGET, tenant_id=TENANT,
                expected_membership_revision=0, expected_capacity_revision=0, session=session)
            raise RuntimeError("SYNTHETIC_ABORT")
        transact(db, abort)
    assert db["tenant_authorization_decision_evidence"].count_documents({}) == 0
    assert db["role_assignments"].count_documents({"principal_id": TARGET, "role_id": ROLE}) == 0

# ARTIFACT: test_company_document_reader_grant_real_mongo.py
# VERSION: v1.1.0-FOUNDER-INIT-MONGO-CERT
# AUTHORITY BOUNDARY: Synthetic disposable command and source-read certification only.
# TENANT POSTURE: Exact company tenant inside UUID-owned local database.
# FAIL-CLOSED POSTURE: Unavailable infrastructure fails certification; no skip as success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
