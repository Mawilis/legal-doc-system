"""Host-backed certificate for C3C client-matter visibility provisioning.

TITLE: WILSY OS Legal Client Matter Visibility Provisioning Real-Mongo Certificate
VERSION: v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-RM-CERT
AUTHORITY: Host-backed certification of current-IAM/matter/visibility transaction composition.
EPITOME: Prove on the verified Mongo replica set that an authorized law-firm
         actor and independently ACTIVE same-tenant LEGAL_CLIENT target can
         grant/replay/revoke one canonical CaseMatter visibility relation in one
         caller-owned transaction, while abort and IAM denial write nothing.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_visibility_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for C3C composition using canonical
                            IAM repositories, L8-5/P1 matter evidence and L8-7B
                            persistence. HTTP/client projection remains separate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-RM-CERT
           establishes replica-set grant/replay/revoke, append-only visibility
           history, transaction-abort dominance, actor/target IAM denial, exact
           same-tenant matter scope and non-financial evidence proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant/principal/matter data.
TENANT BOUNDARY: Every IAM, matter and visibility record is exact-tenant scoped.
AUTHORITY BOUNDARY: Host provisioning certificate only; no client read authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Test owns Mongo transactions; C3C only receives active sessions.
FAIL-CLOSED DECLARATION: Runtime, actor/target IAM, matter, transaction or
                         visibility failure rejects without fabricated evidence.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentNotFoundError,
    RoleAssignmentRepository,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.orchestration.legal_client_matter_visibility_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    LegalClientMatterVisibilityProvisioningError,
    grant_client_matter_visibility,
    revoke_client_matter_visibility,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    COLLECTION as VISIBILITY_COLLECTION,
    LegalClientMatterVisibilityNotFoundError,
    LegalClientMatterVisibilityRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 20, 30, tzinfo=timezone.utc)


class _PrincipalReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> object:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> object:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _BusinessRoleReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        value = TenantBusinessRoleRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )
        if value.business_role != role_id:
            raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
        return value


class _AuthorizationRoleReader:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        role_id: str,
        *,
        session: Any = None,
    ) -> object:
        return RoleAssignmentRepository.resolve(
            principal_id,
            tenant_id,
            role_id,
            self.collection,
            session=session,
        )


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated replica-set database."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_7C3C_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_7C3C_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_7C3C_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_7c3c_{uuid.uuid4().hex}"]
        collections = {
            "lifecycle": database.get_collection(
                LIFECYCLE_COLLECTION,
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "visibility": database.get_collection(
                VISIBILITY_COLLECTION,
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "principal": database.get_collection(
                "principal_authorities",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "membership": database.get_collection(
                "tenant_memberships",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "business": database.get_collection(
                "tenant_business_roles",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "role": database.get_collection(
                "role_assignments",
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
        }
        LegalOperationsLifecycleRegistry.ensure_indexes(collections["lifecycle"])
        LegalClientMatterVisibilityRegistry.ensure_indexes(collections["visibility"])
        PrincipalAuthorityRepository.ensure_indexes(collections["principal"])
        TenantMembershipRepository.ensure_indexes(collections["membership"])
        TenantBusinessRoleRepository.ensure_indexes(collections["business"])
        RoleAssignmentRepository.ensure_indexes(collections["role"])
        yield {
            "client": client,
            "database": database,
            "collections": collections,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _seed_principal(
    collections: dict[str, Any],
    *,
    tenant: str,
    principal: str,
    business_role: str,
    authorization_role: str,
    authorization_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
) -> None:
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0),
        collections["principal"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal,
            tenant,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        collections["membership"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal,
            tenant,
            business_role,
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        collections["business"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(
            principal,
            tenant,
            authorization_role,
            authorization_status,
            0,
        ),
        collections["role"],
    )


def _seed_case(
    collections: dict[str, Any],
    *,
    tenant: str,
    matter_id: str,
) -> CaseMatter:
    value = CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"CASE-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"matter-{matter_id}",
    )
    LegalOperationsLifecycleRegistry.create(value, collections["lifecycle"])
    return value


def _readers(collections: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    return (
        _PrincipalReader(collections["principal"]),
        _MembershipReader(collections["membership"]),
        _BusinessRoleReader(collections["business"]),
        _AuthorizationRoleReader(collections["role"]),
    )


def _grant(
    collections: dict[str, Any],
    *,
    tenant: str,
    actor: str,
    client_principal: str,
    matter_id: str,
    session: Any,
):
    principal, membership, business, roles = _readers(collections)
    return grant_client_matter_visibility(
        tenant_id=tenant,
        actor_principal_id=actor,
        client_principal_id=client_principal,
        case_matter_id=matter_id,
        granted_at=NOW + timedelta(minutes=1),
        evidence_reference="visibility-grant",
        lifecycle_collection=collections["lifecycle"],
        visibility_collection=collections["visibility"],
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=roles,
        session=session,
    )


def _revoke(
    collections: dict[str, Any],
    *,
    tenant: str,
    actor: str,
    client_principal: str,
    matter_id: str,
    session: Any,
):
    principal, membership, business, roles = _readers(collections)
    return revoke_client_matter_visibility(
        tenant_id=tenant,
        actor_principal_id=actor,
        client_principal_id=client_principal,
        case_matter_id=matter_id,
        revoked_at=NOW + timedelta(minutes=2),
        evidence_reference="visibility-revoke",
        lifecycle_collection=collections["lifecycle"],
        visibility_collection=collections["visibility"],
        principal_repository=principal,
        membership_repository=membership,
        business_role_repository=business,
        role_assignment_repository=roles,
        session=session,
    )


def test_real_commit_replay_and_append_only_revoke(
    mongo_context: dict[str, Any],
) -> None:
    """Committed grant replays exactly; revoke appends and removes currentness."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    actor = f"actor-{uuid.uuid4().hex}"
    target = f"client-{uuid.uuid4().hex}"
    matter_id = f"matter-{uuid.uuid4().hex}"

    _seed_principal(
        collections,
        tenant=tenant,
        principal=actor,
        business_role="tenant_legal_partner",
        authorization_role="LEGAL_PARTNER",
    )
    _seed_principal(
        collections,
        tenant=tenant,
        principal=target,
        business_role="tenant_legal_client",
        authorization_role="LEGAL_CLIENT",
    )
    source = _seed_case(collections, tenant=tenant, matter_id=matter_id)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        created = _grant(
            collections,
            tenant=tenant,
            actor=actor,
            client_principal=target,
            matter_id=matter_id,
            session=session,
        )
        session.commit_transaction()

    assert created.source_case_matter_fingerprint == source.fingerprint
    assert created.granted_by_principal_id == actor
    assert collections["visibility"].count_documents(
        {"tenant_id": tenant, "status": "ACTIVE"}
    ) == 1

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        replay = _grant(
            collections,
            tenant=tenant,
            actor=actor,
            client_principal=target,
            matter_id=matter_id,
            session=session,
        )
        session.commit_transaction()
    assert replay == created
    assert collections["visibility"].count_documents({"tenant_id": tenant}) == 1

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        revoked = _revoke(
            collections,
            tenant=tenant,
            actor=actor,
            client_principal=target,
            matter_id=matter_id,
            session=session,
        )
        session.commit_transaction()

    assert revoked.status.value == "REVOKED"
    assert revoked.revoked_by_principal_id == actor
    assert collections["visibility"].count_documents({"tenant_id": tenant}) == 2
    with pytest.raises(LegalClientMatterVisibilityNotFoundError):
        LegalClientMatterVisibilityRegistry.resolve_current_active(
            tenant,
            target,
            matter_id,
            collections["visibility"],
        )


def test_real_transaction_abort_leaves_no_visibility_evidence(
    mongo_context: dict[str, Any],
) -> None:
    """Caller abort dominates an otherwise valid C3C grant."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    actor = f"actor-{uuid.uuid4().hex}"
    target = f"client-{uuid.uuid4().hex}"
    matter_id = f"matter-{uuid.uuid4().hex}"

    _seed_principal(
        collections,
        tenant=tenant,
        principal=actor,
        business_role="tenant_legal_attorney",
        authorization_role="LEGAL_ATTORNEY",
    )
    _seed_principal(
        collections,
        tenant=tenant,
        principal=target,
        business_role="tenant_legal_client",
        authorization_role="LEGAL_CLIENT",
    )
    _seed_case(collections, tenant=tenant, matter_id=matter_id)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        value = _grant(
            collections,
            tenant=tenant,
            actor=actor,
            client_principal=target,
            matter_id=matter_id,
            session=session,
        )
        assert value.case_matter_id == matter_id
        session.abort_transaction()

    assert collections["visibility"].count_documents(
        {"tenant_id": tenant}
    ) == 0


def test_real_actor_or_target_iam_denial_writes_nothing(
    mongo_context: dict[str, Any],
) -> None:
    """Ineligible actor or revoked target LEGAL_CLIENT role rejects before write."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]

    tenant_a = f"tenant-{uuid.uuid4().hex}"
    actor_a = f"actor-{uuid.uuid4().hex}"
    target_a = f"client-{uuid.uuid4().hex}"
    matter_a = f"matter-{uuid.uuid4().hex}"
    _seed_principal(
        collections,
        tenant=tenant_a,
        principal=actor_a,
        business_role="tenant_sheriff",
        authorization_role="SHERIFF",
    )
    _seed_principal(
        collections,
        tenant=tenant_a,
        principal=target_a,
        business_role="tenant_legal_client",
        authorization_role="LEGAL_CLIENT",
    )
    _seed_case(collections, tenant=tenant_a, matter_id=matter_a)

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterVisibilityProvisioningError) as denied:
            _grant(
                collections,
                tenant=tenant_a,
                actor=actor_a,
                client_principal=target_a,
                matter_id=matter_a,
                session=session,
            )
        assert denied.value.code == (
            "L8_7C3C_ACTOR_AUTHORIZATION_DENIED_BUSINESS_ROLE_INELIGIBLE"
        )
        session.abort_transaction()

    tenant_b = f"tenant-{uuid.uuid4().hex}"
    actor_b = f"actor-{uuid.uuid4().hex}"
    target_b = f"client-{uuid.uuid4().hex}"
    matter_b = f"matter-{uuid.uuid4().hex}"
    _seed_principal(
        collections,
        tenant=tenant_b,
        principal=actor_b,
        business_role="tenant_legal_paralegal",
        authorization_role="LEGAL_PARALEGAL",
    )
    _seed_principal(
        collections,
        tenant=tenant_b,
        principal=target_b,
        business_role="tenant_legal_client",
        authorization_role="LEGAL_CLIENT",
        authorization_status=RoleAssignmentStatus.REVOKED,
    )
    _seed_case(collections, tenant=tenant_b, matter_id=matter_b)

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(LegalClientMatterVisibilityProvisioningError) as target:
            _grant(
                collections,
                tenant=tenant_b,
                actor=actor_b,
                client_principal=target_b,
                matter_id=matter_b,
                session=session,
            )
        assert target.value.code == (
            "L8_7C3C_CLIENT_AUTHORIZATION_ROLE_REQUIRED"
        )
        session.abort_transaction()

    assert collections["visibility"].count_documents({}) == 0
    assert PRODUCTION_VERSION == (
        "v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING"
    )


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_visibility_orchestrator_real_mongo.py
# VERSION: v1.0.0-L8-7C3C-CLIENT-MATTER-VISIBILITY-PROVISIONING-RM-CERT
# AUTHORITY BOUNDARY: real-Mongo C3C actor/target/matter/visibility transaction certificate only
# TENANT POSTURE: exact same tenant/session across IAM, CaseMatter and append-only visibility persistence
# FAIL-CLOSED POSTURE: denial, abort, matter or transaction failure writes no visibility evidence
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
