"""TITLE: D12 SYSTEM permission command plane real-Mongo certificate.
VERSION: v1.1.0-D12-P7-BREAK-GLASS-COMMAND-PLANE-REAL-MONGO
AUTHORITY: End-to-end bootstrap seed, assignment, and revocation certification.
EPITOME: Proves the closed command plane in caller-owned transactions on an isolated replica set database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_system_permission_command_plane_real_mongo.py
COLLABORATION / OWNERSHIP: Principal, bootstrap, assignment registries and D12 command services.
CERTIFICATION DATE: 2026-10-15
CHANGELOG: v1.1.0 adds exact P7 assignment/revocation, replay and rollback proof.
COMPLIANCE / SECURITY: UUID isolation; canonical wilsy read-only; no TTL/delete/wildcard/recursion.
TENANT BOUNDARY: SYSTEM only.
AUTHORITY BOUNDARY: Delegates and revokes only privileged_activation:issue and privileged_activation:break_glass after exact bootstrap seeding.
FINANCIAL AUTHORITY BOUNDARY: None.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
import os
from threading import Barrier
from typing import Any
from uuid import uuid4
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.current_system_permission_bootstrap_authority import CurrentSystemPermissionBootstrapAuthorityResolver
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.system_permission_assignment_command_service import SystemPermissionAssignmentCommandService
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentConflictError
from tools.eos.auth.system_permission_bootstrap_authority import SystemPermissionBootstrapAuthority
from tools.eos.auth.system_permission_bootstrap_authority_registry import SystemPermissionBootstrapAuthorityRegistry
from tools.eos.auth.system_permission_bootstrap_seed_service import SystemPermissionBootstrapSeedService
from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence, SystemPermissionCommandOperation
from tools.eos.auth.system_permission_command_policy import ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION, PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION, PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, REVOKE_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION
from tools.eos.auth.system_permission_revocation_command_service import SystemPermissionRevocationCommandService

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
NOW = datetime(2026, 10, 14, 15, 0, tzinfo=timezone.utc)


@pytest.fixture()
def context() -> Any:
    client: MongoClient[Any] = MongoClient(URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000, socketTimeoutMS=5000)
    hello = client.admin.command("hello")
    assert hello.get("setName") == "wilsyVendorCertRS" and hello.get("isWritablePrimary") is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    canonical_before = tuple(sorted(client["wilsy"].list_collection_names()))
    name = "wilsy_d12_command_" + uuid4().hex[:20]
    db = client[name]
    principals = db["principal_authorities"]
    bootstrap_collection = db["system_permission_bootstrap_authorities"]
    assignment_collection = db["system_permission_assignments"]
    bootstrap_registry = SystemPermissionBootstrapAuthorityRegistry(bootstrap_collection)
    assignment_registry = SystemPermissionAssignmentRegistry(assignment_collection)
    bootstrap_registry.ensure_indexes(); assignment_registry.ensure_indexes()
    bootstrap_resolver = CurrentSystemPermissionBootstrapAuthorityResolver(principal_collection=principals, bootstrap_registry=bootstrap_registry)
    possession = CurrentSystemPermissionPossessionResolver(principal_collection=principals, assignment_registry=assignment_registry)
    yield {"client": client, "db": db, "name": name, "principals": principals, "bootstraps": bootstrap_collection, "assignments": assignment_collection, "bootstrap_registry": bootstrap_registry, "assignment_registry": assignment_registry, "possession": possession, "seed": SystemPermissionBootstrapSeedService(principal_collection=principals, bootstrap_resolver=bootstrap_resolver, assignment_registry=assignment_registry), "assign": SystemPermissionAssignmentCommandService(principal_collection=principals, possession_resolver=possession, assignment_registry=assignment_registry), "revoke": SystemPermissionRevocationCommandService(principal_collection=principals, possession_resolver=possession, assignment_registry=assignment_registry), "canonical_before": canonical_before}
    assert tuple(sorted(client["wilsy"].list_collection_names())) == canonical_before
    client.drop_database(name); assert name not in client.list_database_names(); client.close()


def _seed_evidence(purpose: str, permission: str, suffix: str) -> SystemPermissionCommandEvidence:
    return SystemPermissionCommandEvidence(SystemPermissionCommandOperation.BOOTSTRAP_SEED, "actor-a", "actor-a", permission, "evidence-seed-" + suffix, NOW, "idem-seed-" + suffix, bootstrap_id="bootstrap-" + suffix, bootstrap_purpose=purpose)


def _install_base(context: Any) -> None:
    context["principals"].insert_many([{"principal_id": "actor-a", "status": "ACTIVE", "revision": 1}, {"principal_id": "target-a", "status": "ACTIVE", "revision": 1}])
    with context["client"].start_session() as session:
        session.start_transaction()
        for purpose, suffix in ((ASSIGN_BOOTSTRAP_PURPOSE, "assign"), (REVOKE_BOOTSTRAP_PURPOSE, "revoke")):
            context["bootstrap_registry"].create_or_replay(SystemPermissionBootstrapAuthority.issue(bootstrap_id="bootstrap-" + suffix, actor_principal_id="actor-a", purpose=purpose, evidence_reference="installation-" + suffix, issued_at=NOW - timedelta(minutes=1)), idempotency_key="bootstrap-idem-" + suffix, session=session)
        session.commit_transaction()


def _commit_seed_commands(context: Any) -> None:
    with context["client"].start_session() as session:
        session.start_transaction()
        context["seed"].seed(_seed_evidence(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION, "assign"), session=session)
        context["seed"].seed(_seed_evidence(REVOKE_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION, "revoke"), session=session)
        session.commit_transaction()


def _assignment_evidence(*, evidence: str = "evidence-assign-activation", idempotency: str = "idem-assign-activation", actor: str = "actor-a", target: str = "target-a", permission: str = PRIVILEGED_ACTIVATION_ISSUE_PERMISSION) -> SystemPermissionCommandEvidence:
    return SystemPermissionCommandEvidence(SystemPermissionCommandOperation.ASSIGN, actor, target, permission, evidence, NOW + timedelta(minutes=1), idempotency)


def test_real_command_plane_seed_assign_revoke_replay_and_boundaries(context: Any) -> None:
    _install_base(context)
    seed_assign = _seed_evidence(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION, "assign")
    seed_revoke = _seed_evidence(REVOKE_BOOTSTRAP_PURPOSE, REVOKE_COMMAND_PERMISSION, "revoke")
    with context["client"].start_session() as session:
        session.start_transaction()
        context["seed"].seed(seed_assign, session=session); context["seed"].seed(seed_revoke, session=session)
        assert context["possession"].resolve(principal_id="actor-a", permission_id=ASSIGN_COMMAND_PERMISSION, session=session) is not None
        assert context["possession"].resolve(principal_id="actor-a", permission_id=REVOKE_COMMAND_PERMISSION, session=session) is not None
        session.commit_transaction()
    assignment_evidence = SystemPermissionCommandEvidence(SystemPermissionCommandOperation.ASSIGN, "actor-a", "target-a", PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, "evidence-assign-activation", NOW + timedelta(minutes=1), "idem-assign-activation")
    with context["client"].start_session() as session:
        session.start_transaction(); assigned = context["assign"].assign(assignment_evidence, session=session); session.commit_transaction()
    revocation_evidence = SystemPermissionCommandEvidence(SystemPermissionCommandOperation.REVOKE, "actor-a", "target-a", PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, "evidence-revoke-activation", NOW + timedelta(minutes=2), "idem-revoke-activation", assignment_id=assigned.assignment_id)
    with context["client"].start_session() as session:
        session.start_transaction(); revoked = context["revoke"].revoke(revocation_evidence, session=session); session.commit_transaction()
    assert revoked.status.value == "REVOKED" and context["possession"].resolve(principal_id="target-a", permission_id=PRIVILEGED_ACTIVATION_ISSUE_PERMISSION) is None
    with context["client"].start_session() as session:
        session.start_transaction()
        assert context["seed"].seed(seed_assign, session=session).permission_id == ASSIGN_COMMAND_PERMISSION
        assert context["assign"].assign(assignment_evidence, session=session) == assigned
        assert context["revoke"].revoke(revocation_evidence, session=session) == revoked
        session.commit_transaction()
    assert context["assignments"].count_documents({}) == 4
    assert set(context["db"].list_collection_names()) <= {"principal_authorities", "system_permission_bootstrap_authorities", "system_permission_assignments"}
    for collection in (context["bootstraps"], context["assignments"]):
        assert all("expireAfterSeconds" not in index for index in collection.list_indexes())
    assert not hasattr(context["assignment_registry"], "delete")


def test_real_p7_permission_assign_revoke_replay_and_abort(context: Any) -> None:
    _install_base(context)
    _commit_seed_commands(context)
    command = _assignment_evidence(evidence="p7-assign", idempotency="p7-assign-idem", permission=PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION)
    with context["client"].start_session() as session:
        session.start_transaction()
        pending = context["assign"].assign(command, session=session)
        assert context["possession"].resolve(principal_id="target-a", permission_id=PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION, session=session) == pending
        session.abort_transaction()
    assert context["possession"].resolve(principal_id="target-a", permission_id=PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION) is None
    with context["client"].start_session() as session:
        session.start_transaction(); assigned = context["assign"].assign(command, session=session); session.commit_transaction()
    with context["client"].start_session() as session:
        session.start_transaction(); assert context["assign"].assign(command, session=session) == assigned; session.commit_transaction()
    revoke = SystemPermissionCommandEvidence(SystemPermissionCommandOperation.REVOKE, "actor-a", "target-a", PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION, "p7-revoke", NOW + timedelta(minutes=2), "p7-revoke-idem", assignment_id=assigned.assignment_id)
    with context["client"].start_session() as session:
        session.start_transaction(); pending_revoke = context["revoke"].revoke(revoke, session=session); session.abort_transaction()
    assert context["possession"].resolve(principal_id="target-a", permission_id=PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION) == assigned
    with context["client"].start_session() as session:
        session.start_transaction(); revoked = context["revoke"].revoke(revoke, session=session); session.commit_transaction()
    assert revoked == pending_revoke
    assert context["possession"].resolve(principal_id="target-a", permission_id=PRIVILEGED_ACTIVATION_BREAK_GLASS_PERMISSION) is None
    with context["client"].start_session() as session:
        session.start_transaction(); assert context["revoke"].revoke(revoke, session=session) == revoked; session.commit_transaction()
    assert not ({"privileged_activations", "privileged_break_glass_command_evidence", "payments", "settlements"} & set(context["db"].list_collection_names()))


def test_real_abort_zero_inactive_target_and_recursive_policy(context: Any) -> None:
    _install_base(context)
    with context["client"].start_session() as session:
        session.start_transaction(); context["seed"].seed(_seed_evidence(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION, "assign"), session=session); session.abort_transaction()
    assert context["assignments"].count_documents({}) == 0
    with pytest.raises(Exception):
        SystemPermissionCommandEvidence(SystemPermissionCommandOperation.ASSIGN, "actor-a", "target-a", "system_permission_assignment:*", "e", NOW, "i")


def test_real_divergent_seed_assignment_and_revocation_replay(context: Any) -> None:
    _install_base(context)
    _commit_seed_commands(context)
    baseline_count = context["assignments"].count_documents({})
    divergent_seed = SystemPermissionCommandEvidence(SystemPermissionCommandOperation.BOOTSTRAP_SEED, "actor-a", "actor-a", ASSIGN_COMMAND_PERMISSION, "different-seed-evidence", NOW, "idem-seed-assign", bootstrap_id="bootstrap-assign", bootstrap_purpose=ASSIGN_BOOTSTRAP_PURPOSE)
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(SystemPermissionAssignmentConflictError):
            context["seed"].seed(divergent_seed, session=session)
        session.abort_transaction()
    assert context["assignments"].count_documents({}) == baseline_count
    exact = _assignment_evidence()
    with context["client"].start_session() as session:
        session.start_transaction(); assigned = context["assign"].assign(exact, session=session); session.commit_transaction()
    divergent_assign = _assignment_evidence(evidence="different-assignment-evidence")
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(SystemPermissionAssignmentConflictError):
            context["assign"].assign(divergent_assign, session=session)
        session.abort_transaction()
    revoke = SystemPermissionCommandEvidence(SystemPermissionCommandOperation.REVOKE, "actor-a", "target-a", PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, "revoke-evidence", NOW + timedelta(minutes=2), "idem-revoke", assignment_id=assigned.assignment_id)
    with context["client"].start_session() as session:
        session.start_transaction(); context["revoke"].revoke(revoke, session=session); session.commit_transaction()
    divergent_revoke = SystemPermissionCommandEvidence(SystemPermissionCommandOperation.REVOKE, "actor-a", "target-a", PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, "different-revoke-evidence", NOW + timedelta(minutes=2), "idem-revoke", assignment_id=assigned.assignment_id)
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(SystemPermissionAssignmentConflictError):
            context["revoke"].revoke(divergent_revoke, session=session)
        session.abort_transaction()
    assert context["assignments"].count_documents({}) == baseline_count + 2


def test_real_inactive_actor_target_missing_command_and_closed_policy_denials(context: Any) -> None:
    _install_base(context)
    context["principals"].insert_one({"principal_id": "actor-without-command", "status": "ACTIVE", "revision": 1})
    _commit_seed_commands(context)
    baseline = context["assignments"].count_documents({})
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(Exception, match="CURRENT_ASSIGNMENT_COMMAND_AUTHORITY_REQUIRED"):
            context["assign"].assign(_assignment_evidence(actor="actor-without-command"), session=session)
        with pytest.raises(Exception, match="CURRENT_REVOCATION_COMMAND_AUTHORITY_REQUIRED"):
            context["revoke"].revoke(SystemPermissionCommandEvidence(SystemPermissionCommandOperation.REVOKE, "actor-without-command", "target-a", PRIVILEGED_ACTIVATION_ISSUE_PERMISSION, "e", NOW, "i", assignment_id="missing-assignment"), session=session)
        session.abort_transaction()
    context["principals"].update_one({"principal_id": "target-a"}, {"$set": {"status": "SUSPENDED"}})
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(Exception, match="TARGET_PRINCIPAL_NOT_CURRENT"):
            context["assign"].assign(_assignment_evidence(), session=session)
        session.abort_transaction()
    context["principals"].update_one({"principal_id": "actor-a"}, {"$set": {"status": "SUSPENDED"}})
    with context["client"].start_session() as session:
        session.start_transaction()
        with pytest.raises(Exception, match="CURRENT_ASSIGNMENT_COMMAND_AUTHORITY_REQUIRED"):
            context["assign"].assign(_assignment_evidence(), session=session)
        with pytest.raises(Exception, match="CURRENT_BOOTSTRAP_REQUIRED"):
            context["seed"].seed(_seed_evidence(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION, "assign"), session=session)
        session.abort_transaction()
    for permission in (ASSIGN_COMMAND_PERMISSION, REVOKE_COMMAND_PERMISSION, "kernel:write", "tenant:profile:write"):
        with context["client"].start_session() as session:
            session.start_transaction()
            with pytest.raises(Exception):
                context["assign"].assign(_assignment_evidence(permission=permission), session=session)
            session.abort_transaction()
    assert context["assignments"].count_documents({}) == baseline


def test_real_concurrent_competing_bootstrap_seed_is_one_durable_assignment(context: Any) -> None:
    _install_base(context)
    evidence = _seed_evidence(ASSIGN_BOOTSTRAP_PURPOSE, ASSIGN_COMMAND_PERMISSION, "assign")
    barrier = Barrier(2)

    def worker() -> str:
        with context["client"].start_session() as session:
            session.start_transaction()
            barrier.wait(timeout=5)
            try:
                context["seed"].seed(evidence, session=session)
                session.commit_transaction()
                return "COMMITTED"
            except (PyMongoError, SystemPermissionAssignmentConflictError):
                if session.in_transaction:
                    session.abort_transaction()
                return "DENIED"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = tuple(pool.map(lambda _: worker(), range(2)))
    assert results.count("COMMITTED") == 1
    assert results.count("DENIED") == 1
    assert context["assignments"].count_documents({"principal_id": "actor-a", "permission_id": ASSIGN_COMMAND_PERMISSION}) == 1


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_system_permission_command_plane_real_mongo.py
# VERSION: v1.1.0-D12-P7-BREAK-GLASS-COMMAND-PLANE-REAL-MONGO
# AUTHORITY BOUNDARY: CLOSED SEED, ASSIGNMENT, AND REVOCATION CERTIFICATE
# TENANT POSTURE: UUID-ISOLATED SYSTEM ONLY
# FAIL-CLOSED POSTURE: NO TTL, DELETE, RECURSION, WILDCARD, OR ARBITRARY AUTHORITY
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
