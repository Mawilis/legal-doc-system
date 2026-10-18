"""WILSY OS governed authorization-role revocation command real-Mongo certificate.

TITLE: Governed Authorization Role Revocation Command Real-Mongo Certificate
VERSION: v1.0.1-P1-R3C-H2-RACE-HARNESS-REPAIR
AUTHORITY: Wilsy OS Core Governance / Sovereign IAM Design
EPITOME: Certify production IAM authorization and atomic authorization-evidence,
         role-assignment CAS, and revocation-evidence composition on real Mongo.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_authorization_role_revocation_command_real_mongo.py
COLLABORATION / OWNERSHIP: H2 certifies the unchanged G1 command and certified
                            repositories against the sanctioned replica set.
CERTIFICATION / UPDATE DATE: 2026-10-18
CHANGELOG: v1.0.1-P1-R3C-H2-RACE-HARNESS-REPAIR removes winner-order dependence by replaying the actual losing divergent request after a real concurrency race;
           v1.0.0-P1-R3C-H2 established UUID-isolated commit/abort, replay,
           denial, rollback, race, restart, currentness, and tenant-isolation proof.
COMPLIANCE: NIST privileged-access lifecycle principles; POPIA section 19;
            GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque fixtures only; no customer or
                             canonical database access and no secret material.
TENANT BOUNDARY: Every actor, target, assignment, and evidence read/write is
                 bound to an explicit tenant and genuine caller session.
AUTHORITY BOUNDARY: Real-Mongo IAM command certification only; no HTTP, Legal
                    Operations, root, recovery, break-glass, or JIT authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
TRANSACTION BOUNDARY: Test host owns sessions, transactions, abort, commit, and
                      whole-transaction retry; the command owns none.
FAIL-CLOSED DECLARATION: Authority, target, policy, CAS, evidence, concurrency,
                         and replay divergence failures never become success.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from threading import Barrier
from typing import Any, Iterator, TypedDict
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from tools.eos.auth.authorization_role_revocation_command import (
    AuthorizationRoleRevocationCommand,
    AuthorizationRoleRevocationCommandAuthorizationDeniedError,
    AuthorizationRoleRevocationCommandPolicyDeniedError,
    AuthorizationRoleRevocationCommandReplayConflictError,
    AuthorizationRoleRevocationCommandTargetInvalidError,
    AuthorizationRoleRevocationResultState,
)
from tools.eos.auth.authorization_role_revocation_evidence_registry import (
    COLLECTION as REVOCATION_COLLECTION,
    AuthorizationRoleRevocationEvidenceRegistry,
)
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_authorization import authorize_tenant_operation
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    COLLECTION as AUTHORIZATION_COLLECTION,
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository


VERSION = "v1.0.1-P1-R3C-H2-RACE-HARNESS-REPAIR"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_p1_r3c_h2_"
TENANT = "tenant-r3c-h2-a"
FOREIGN_TENANT = "tenant-r3c-h2-b"
ACTOR = "principal-r3c-h2-actor"
TARGET = "principal-r3c-h2-target"
NOW = datetime(2026, 10, 14, 8, 0, 0, 123000, tzinfo=timezone.utc)
COLLECTION_NAMES = (
    "principal_authorities",
    "tenant_memberships",
    "tenant_business_roles",
    "role_assignments",
    AUTHORIZATION_COLLECTION,
    REVOCATION_COLLECTION,
)
UNRELATED_COLLECTIONS = (
    "auth_sessions",
    "refresh_tokens",
    "root_rotations",
    "root_recoveries",
    "break_glass_activations",
    "privileged_activations",
    "financial_executions",
    "legal_operations_commands",
)


def _client() -> MongoClient[Any]:
    """Open and prove one client to the sanctioned writable replica set."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5_000,
        retryWrites=True,
        tz_aware=True,
    )
    hello = client.admin.command("hello")
    assert hello.get("setName") == REPLICA_SET
    assert bool(hello.get("isWritablePrimary", hello.get("ismaster", False)))
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    return client


@dataclass(slots=True)
class Context:
    """One disposable database with production collection-bound authorities."""

    client: MongoClient[Any]
    database: Any
    collections: dict[str, Any]
    principal_repository: Any
    membership_repository: Any
    business_role_repository: Any
    role_repository: Any
    authorization_registry: TenantAuthorizationDecisionEvidenceRegistry
    revocation_registry: AuthorizationRoleRevocationEvidenceRegistry

    def command(self, token: str = "base", *, revocation_registry: Any = None) -> AuthorizationRoleRevocationCommand:
        """Construct the unchanged production command with deterministic factories."""
        return AuthorizationRoleRevocationCommand(
            principal_repository=self.principal_repository,
            membership_repository=self.membership_repository,
            role_assignment_repository=self.role_repository,
            business_role_repository=self.business_role_repository,
            role_assignment_collection=self.collections["role_assignments"],
            authorization_evidence_registry=self.authorization_registry,
            revocation_evidence_registry=revocation_registry or self.revocation_registry,
            clock=lambda: NOW,
            revocation_id_factory=lambda: f"revocation-r3c-h2-{token}",
        )


def _context(client: MongoClient[Any], database: Any) -> Context:
    """Bind production repositories to exact disposable collections."""
    collections = {name: database[name] for name in COLLECTION_NAMES}
    principal_collection = collections["principal_authorities"]
    membership_collection = collections["tenant_memberships"]
    business_collection = collections["tenant_business_roles"]
    role_collection = collections["role_assignments"]

    class PrincipalRepository:
        @staticmethod
        def resolve(principal_id: str, *, session: Any = None) -> PrincipalAuthority:
            return PrincipalAuthorityRepository.resolve(principal_id, principal_collection, session=session)

    class MembershipRepository:
        @staticmethod
        def resolve(principal_id: str, tenant_id: str, *, session: Any = None) -> TenantMembershipAuthority:
            return TenantMembershipRepository.resolve(principal_id, tenant_id, membership_collection, session=session)

    class BusinessRoleRepository:
        @staticmethod
        def resolve(principal_id: str, tenant_id: str, role_id: str, *, session: Any = None) -> TenantBusinessRoleAuthority:
            value = TenantBusinessRoleRepository.resolve(principal_id, tenant_id, business_collection, session=session)
            if value.business_role != role_id:
                raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
            return value

    class RoleRepository:
        @staticmethod
        def resolve(
            principal_id: str,
            tenant_id: str,
            role_id: str,
            collection: Any = None,
            *,
            session: Any = None,
        ) -> RoleAssignmentAuthority:
            return RoleAssignmentRepository.resolve(principal_id, tenant_id, role_id, role_collection, session=session)

        @staticmethod
        def compare_and_swap(
            value: RoleAssignmentAuthority,
            expected_revision: int,
            collection: Any = None,
            *,
            session: Any = None,
        ) -> RoleAssignmentAuthority:
            return RoleAssignmentRepository.compare_and_swap(value, expected_revision, role_collection, session=session)

    for repository, collection in (
        (PrincipalAuthorityRepository, principal_collection),
        (TenantMembershipRepository, membership_collection),
        (TenantBusinessRoleRepository, business_collection),
        (RoleAssignmentRepository, role_collection),
    ):
        repository.ensure_indexes(collection)
    authorization_registry = TenantAuthorizationDecisionEvidenceRegistry(
        collections[AUTHORIZATION_COLLECTION],
        principal_repository=PrincipalRepository,
        membership_repository=MembershipRepository,
        role_assignment_repository=RoleRepository,
        business_role_repository=BusinessRoleRepository,
    )
    authorization_registry.ensure_indexes()
    revocation_registry = AuthorizationRoleRevocationEvidenceRegistry(collections[REVOCATION_COLLECTION])
    revocation_registry.ensure_indexes()
    return Context(
        client,
        database,
        collections,
        PrincipalRepository,
        MembershipRepository,
        BusinessRoleRepository,
        RoleRepository,
        authorization_registry,
        revocation_registry,
    )


@pytest.fixture()
def mongo_context() -> Iterator[Context]:
    """Yield one UUID-isolated database and drop only that exact database."""
    client = _client()
    database_name = DATABASE_PREFIX + uuid.uuid4().hex
    assert database_name.startswith(DATABASE_PREFIX)
    database = client[database_name]
    context = _context(client, database)
    try:
        yield context
    finally:
        client.drop_database(database_name)
        client.close()


def _seed(
    context: Context,
    *,
    target_role: str = "AUDITOR",
    actor_status: PrincipalStatus = PrincipalStatus.ACTIVE,
    membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
    business_role: str = "tenant_admin",
    actor_role_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    target_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
    include_target: bool = True,
) -> None:
    """Seed real actor and target IAM exclusively through production repositories."""
    c = context.collections
    PrincipalAuthorityRepository.create(PrincipalAuthority(ACTOR, actor_status, 0), c["principal_authorities"])
    PrincipalAuthorityRepository.create(PrincipalAuthority(TARGET, PrincipalStatus.ACTIVE, 0), c["principal_authorities"])
    TenantMembershipRepository.insert(TenantMembershipAuthority(ACTOR, TENANT, membership_status, 0), c["tenant_memberships"])
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(ACTOR, TENANT, business_role, TenantBusinessRoleStatus.ACTIVE, 0, NOW, None),
        c["tenant_business_roles"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(ACTOR, TENANT, "ENTERPRISE_ADMIN", actor_role_status, 0),
        c["role_assignments"],
    )
    if include_target:
        RoleAssignmentRepository.insert(
            RoleAssignmentAuthority(TARGET, TENANT, target_role, target_status, 0),
            c["role_assignments"],
        )


class CommandArguments(TypedDict):
    """Strongly typed command material matching the production execute contract."""

    actor_principal_id: str
    tenant_id: str
    target_principal_id: str
    target_role_id: str
    expected_target_assignment_revision: int
    reason_reference: str
    idempotency_key: str


def _arguments(
    *,
    actor_principal_id: str = ACTOR,
    tenant_id: str = TENANT,
    target_principal_id: str = TARGET,
    target_role_id: str = "AUDITOR",
    expected_target_assignment_revision: int = 0,
    reason_reference: str = "case:R3C-H2-001",
    idempotency_key: str = "idempotency-r3c-h2-001",
) -> CommandArguments:
    """Return the canonical command material for one ordinary revocation."""
    return {
        "actor_principal_id": actor_principal_id,
        "tenant_id": tenant_id,
        "target_principal_id": target_principal_id,
        "target_role_id": target_role_id,
        "expected_target_assignment_revision":
            expected_target_assignment_revision,
        "reason_reference": reason_reference,
        "idempotency_key": idempotency_key,
    }


def _invoke(context: Context, command: AuthorizationRoleRevocationCommand, *, commit: bool, arguments: CommandArguments | None = None) -> Any:
    """Invoke inside a caller-owned transaction and explicitly commit or abort."""
    with context.client.start_session() as session:
        session.start_transaction()
        try:
            result = command.execute(**(arguments or _arguments()), session=session)
            if commit:
                session.commit_transaction()
            else:
                session.abort_transaction()
            return result
        except BaseException:
            if session.in_transaction:
                session.abort_transaction()
            raise


def _counts(context: Context) -> tuple[int, int]:
    """Return physical authorization and revocation evidence counts."""
    return (
        context.collections[AUTHORIZATION_COLLECTION].count_documents({}),
        context.collections[REVOCATION_COLLECTION].count_documents({}),
    )


def _target(context: Context, role: str = "AUDITOR", tenant: str = TENANT) -> RoleAssignmentAuthority:
    """Resolve current target assignment through the production repository."""
    return RoleAssignmentRepository.resolve(TARGET, tenant, role, context.collections["role_assignments"])


def test_real_atomic_commit_and_post_commit_current_authority(mongo_context: Context) -> None:
    """Prove all three writes commit together and revoked target authority is denied."""
    context = mongo_context
    _seed(context)
    c = context.collections
    TenantMembershipRepository.insert(TenantMembershipAuthority(TARGET, TENANT, TenantMembershipStatus.ACTIVE, 0), c["tenant_memberships"])
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(TARGET, TENANT, "tenant_auditor", TenantBusinessRoleStatus.ACTIVE, 0, NOW, None),
        c["tenant_business_roles"],
    )
    command = context.command("commit")
    with context.client.start_session() as session:
        session.start_transaction()
        result = command.execute(**_arguments(), session=session)
        assert result.state is AuthorizationRoleRevocationResultState.NEWLY_REVOKED
        assert c[AUTHORIZATION_COLLECTION].count_documents({}, session=session) == 1
        assert context.role_repository.resolve(TARGET, TENANT, "AUDITOR", session=session).status is RoleAssignmentStatus.REVOKED
        assert c[REVOCATION_COLLECTION].count_documents({}, session=session) == 1
        session.commit_transaction()
    assert _counts(context) == (1, 1)
    assert _target(context) == RoleAssignmentAuthority(TARGET, TENANT, "AUDITOR", RoleAssignmentStatus.REVOKED, 1)
    denied = authorize_tenant_operation(
        principal_id=TARGET,
        tenant_id=TENANT,
        permission_id="audit:read",
        operation="audit_read",
        principal_repository=context.principal_repository,
        membership_repository=context.membership_repository,
        role_assignment_repository=context.role_repository,
        business_role_repository=context.business_role_repository,
    )
    assert denied.authorized is False
    assert all(context.database[name].count_documents({}) == 0 for name in UNRELATED_COLLECTIONS)


def test_caller_abort_rolls_back_all_three_writes(mongo_context: Context) -> None:
    """Prove caller abort removes authorization evidence, CAS, and revocation evidence."""
    context = mongo_context
    _seed(context)
    result = _invoke(context, context.command("abort"), commit=False)
    assert result.state is AuthorizationRoleRevocationResultState.NEWLY_REVOKED
    assert _counts(context) == (0, 0)
    assert _target(context) == RoleAssignmentAuthority(TARGET, TENANT, "AUDITOR", RoleAssignmentStatus.ACTIVE, 0)


def test_exact_replay_divergence_and_restart_reconciliation(mongo_context: Context) -> None:
    """Prove replay-before-authority, divergence zero-write, and fresh-client durability."""
    context = mongo_context
    _seed(context)
    original = _invoke(context, context.command("durable"), commit=True)
    before_assignment = _target(context)
    before_counts = _counts(context)
    replay = _invoke(context, context.command("unused"), commit=False)
    assert replay.state is AuthorizationRoleRevocationResultState.EXACT_REPLAY
    assert replay.revocation_evidence == original.revocation_evidence
    assert _counts(context) == before_counts == (1, 1)
    assert _target(context) == before_assignment
    with pytest.raises(AuthorizationRoleRevocationCommandReplayConflictError):
        _invoke(context, context.command("unused-2"), commit=False, arguments=_arguments(reason_reference="case:DIVERGENT"))
    assert _counts(context) == before_counts and _target(context) == before_assignment
    fresh_client = _client()
    try:
        restarted = _context(fresh_client, fresh_client[context.database.name])
        restarted_result = _invoke(restarted, restarted.command("unused-3"), commit=False)
        assert restarted_result.state is AuthorizationRoleRevocationResultState.EXACT_REPLAY
        assert restarted_result.revocation_evidence == original.revocation_evidence
    finally:
        fresh_client.close()


@pytest.mark.parametrize(
    ("actor_status", "membership_status", "business_role", "actor_role_status", "tenant"),
    (
        (PrincipalStatus.SUSPENDED, TenantMembershipStatus.ACTIVE, "tenant_admin", RoleAssignmentStatus.ACTIVE, TENANT),
        (PrincipalStatus.ACTIVE, TenantMembershipStatus.SUSPENDED, "tenant_admin", RoleAssignmentStatus.ACTIVE, TENANT),
        (PrincipalStatus.ACTIVE, TenantMembershipStatus.ACTIVE, "tenant_auditor", RoleAssignmentStatus.ACTIVE, TENANT),
        (PrincipalStatus.ACTIVE, TenantMembershipStatus.ACTIVE, "tenant_admin", RoleAssignmentStatus.REVOKED, TENANT),
        (PrincipalStatus.ACTIVE, TenantMembershipStatus.ACTIVE, "tenant_admin", RoleAssignmentStatus.ACTIVE, FOREIGN_TENANT),
    ),
)
def test_real_current_authorization_denials_are_zero_write(
    mongo_context: Context,
    actor_status: PrincipalStatus,
    membership_status: TenantMembershipStatus,
    business_role: str,
    actor_role_status: RoleAssignmentStatus,
    tenant: str,
) -> None:
    """Physically certify every durable actor-IAM conjunct and foreign-tenant denial."""
    context = mongo_context
    _seed(
        context,
        actor_status=actor_status,
        membership_status=membership_status,
        business_role=business_role,
        actor_role_status=actor_role_status,
    )
    with pytest.raises(AuthorizationRoleRevocationCommandAuthorizationDeniedError):
        _invoke(context, context.command("denied"), commit=False, arguments=_arguments(tenant_id=tenant))
    assert _counts(context) == (0, 0)
    assert _target(context).status is RoleAssignmentStatus.ACTIVE


@pytest.mark.parametrize("variant", ("missing", "foreign", "revoked", "stale"))
def test_real_target_validation_denials_are_zero_write(mongo_context: Context, variant: str) -> None:
    """Missing, foreign, already-revoked, and stale targets fail before first write."""
    context = mongo_context
    _seed(context, include_target=variant != "missing", target_status=RoleAssignmentStatus.REVOKED if variant == "revoked" else RoleAssignmentStatus.ACTIVE)
    arguments = _arguments()
    if variant == "foreign":
        row = context.collections["role_assignments"].find_one({"principal_id": TARGET, "role_id": "AUDITOR"})
        assert row is not None
        context.collections["role_assignments"].delete_one({"_id": row["_id"]})
        RoleAssignmentRepository.insert(RoleAssignmentAuthority(TARGET, FOREIGN_TENANT, "AUDITOR", RoleAssignmentStatus.ACTIVE, 0), context.collections["role_assignments"])
    if variant == "stale":
        arguments["expected_target_assignment_revision"] = 1
    with pytest.raises(AuthorizationRoleRevocationCommandTargetInvalidError):
        _invoke(context, context.command("target-denied"), commit=False, arguments=arguments)
    assert _counts(context) == (0, 0)
    assert context.collections["role_assignments"].count_documents({"status": "REVOKED"}) == (1 if variant == "revoked" else 0)


@pytest.mark.parametrize("role", ("ENTERPRISE_ADMIN", "SOVEREIGN_ARCHITECT"))
def test_real_root_policy_denial_is_zero_write(mongo_context: Context, role: str) -> None:
    """Enterprise and system-root targets remain outside ordinary command authority."""
    context = mongo_context
    _seed(context, target_role=role)
    with pytest.raises(AuthorizationRoleRevocationCommandPolicyDeniedError):
        _invoke(context, context.command("root-denied"), commit=False, arguments=_arguments(target_role_id=role))
    assert _counts(context) == (0, 0)
    assert _target(context, role).status is RoleAssignmentStatus.ACTIVE


def test_revocation_evidence_failure_then_caller_abort_rolls_back_prior_writes(mongo_context: Context) -> None:
    """Inject only the third persistence failure and prove caller abort restores all state."""
    context = mongo_context
    _seed(context)

    class FailingRevocationRegistry:
        def get_by_tenant_idempotency(
            self,
            *,
            tenant_id: str,
            idempotency_key: str,
            session: Any = None,
        ) -> Any:
            return context.revocation_registry.get_by_tenant_idempotency(
                tenant_id=tenant_id,
                idempotency_key=idempotency_key,
                session=session,
            )

        def create_or_replay(self, evidence: Any, *, session: Any) -> Any:
            raise RuntimeError("INJECTED_REVOCATION_EVIDENCE_FAILURE")

    with pytest.raises(RuntimeError, match="INJECTED_REVOCATION_EVIDENCE_FAILURE"):
        _invoke(context, context.command("failure", revocation_registry=FailingRevocationRegistry()), commit=False)
    assert _counts(context) == (0, 0)
    assert _target(context) == RoleAssignmentAuthority(TARGET, TENANT, "AUDITOR", RoleAssignmentStatus.ACTIVE, 0)


def _race(context: Context, arguments: CommandArguments, token: str, barrier: Barrier) -> str:
    """Run one independently-sessioned real command contender without command retry."""
    client = _client()
    local = _context(client, client[context.database.name])
    try:
        with client.start_session() as session:
            session.start_transaction()
            try:
                barrier.wait(timeout=15)
                result = local.command(token).execute(**arguments, session=session)
                session.commit_transaction()
                return result.state.value
            except BaseException as error:
                if session.in_transaction:
                    session.abort_transaction()
                return "FAIL_CLOSED:" + type(error).__name__
    finally:
        client.close()


def test_stale_cas_race_has_one_winner_and_no_loser_evidence(mongo_context: Context) -> None:
    """Two distinct commands race one revision; only one complete transaction persists."""
    context = mongo_context
    _seed(context)
    barrier = Barrier(2)
    left = _arguments(idempotency_key="race-left")
    right = _arguments(idempotency_key="race-right", reason_reference="case:RACE-RIGHT")
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(f.result(timeout=45) for f in (
            pool.submit(_race, context, left, "race-left", barrier),
            pool.submit(_race, context, right, "race-right", barrier),
        ))
    assert outcomes.count("NEWLY_REVOKED") == 1
    assert _target(context) == RoleAssignmentAuthority(TARGET, TENANT, "AUDITOR", RoleAssignmentStatus.REVOKED, 1)
    assert _counts(context) == (1, 1)


@pytest.mark.parametrize("divergent", (False, True))
def test_competing_commands_converge_through_host_fresh_transaction_retry(
    mongo_context: Context, divergent: bool
) -> None:
    """Identical competition replays; divergent competition rejects without hybrid evidence."""
    context = mongo_context
    _seed(context)
    barrier = Barrier(2)
    left = _arguments()
    right = _arguments(reason_reference="case:DIVERGENT-RACE") if divergent else _arguments()
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = tuple(f.result(timeout=45) for f in (
            pool.submit(_race, context, left, "competition-left", barrier),
            pool.submit(_race, context, right, "competition-right", barrier),
        ))
    assert outcomes.count("NEWLY_REVOKED") == 1
    assert _counts(context) == (1, 1)
    durable = context.collections[REVOCATION_COLLECTION].find_one({})
    assert durable is not None
    assert durable["reason_reference"] in {left["reason_reference"], right["reason_reference"]}
    if divergent:
        losing_request = (
            right
            if durable["reason_reference"] == left["reason_reference"]
            else left
        )
        with pytest.raises(AuthorizationRoleRevocationCommandReplayConflictError):
            _invoke(
                context,
                context.command("retry-divergent"),
                commit=False,
                arguments=losing_request,
            )
    else:
        retry = _invoke(context, context.command("retry-exact"), commit=False, arguments=left)
        assert retry.state is AuthorizationRoleRevocationResultState.EXACT_REPLAY
    assert context.collections[AUTHORIZATION_COLLECTION].count_documents({}) == 1


def test_tenant_history_isolation_and_physical_blast_radius(mongo_context: Context) -> None:
    """Foreign tenant replay is absent and unrelated sovereign collections remain untouched."""
    context = mongo_context
    _seed(context)
    _invoke(context, context.command("isolation"), commit=True)
    assert context.revocation_registry.get_by_tenant_idempotency(
        tenant_id=FOREIGN_TENANT,
        idempotency_key=str(_arguments()["idempotency_key"]),
    ) is None
    assert all(context.database[name].count_documents({}) == 0 for name in UNRELATED_COLLECTIONS)
    assert context.collections["principal_authorities"].count_documents({}) == 2
    assert context.collections["tenant_memberships"].count_documents({}) == 1
    assert context.collections["tenant_business_roles"].count_documents({}) == 1


# ARTIFACT: test_authorization_role_revocation_command_real_mongo.py
# VERSION: v1.0.1-P1-R3C-H2-RACE-HARNESS-REPAIR
# AUTHORITY BOUNDARY: real-Mongo IAM command certification only; no HTTP, Legal Operations, root, recovery, break-glass, JIT, session lifecycle, or finance
# TENANT POSTURE: exact real actor, target, business role, authorization role, assignment, and evidence tenant scope certified
# FAIL-CLOSED POSTURE: denial, target drift, root boundary, CAS race, evidence failure, and replay divergence reject atomically
# DATABASE POSTURE: UUID-isolated disposable database only; no production or customer database authority
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
