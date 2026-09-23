"""Host-backed certificate for canonical deputy-principal identity binding.

TITLE: WILSY OS Deputy Principal Binding Real-Mongo Certificate
VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-RM-CERT
AUTHORITY: Host-backed certification of L8-6B authority composition/persistence.
EPITOME: Prove on the verified Mongo replica set that one active principal with
         active tenant membership, tenant_deputy business role, active DEPUTY
         assignment, and canonical Deputy truth can create exactly one immutable
         one-to-one binding; replay, conflict, abort, corruption, and foreign
         scope remain fail closed.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_deputy_principal_binding_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for L8-6B core only; IAM, P1/P2/
                            L8-5, binding domain/registry remain independent.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-RM-CERT
           establishes replica-set index, commit/replay, both-key resolution,
           transaction-abort, wrong-role, foreign-scope, conflict, corruption,
           and non-financial evidence proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants/principals/deputies.
TENANT BOUNDARY: Every authority, lifecycle and binding record is exact-tenant.
AUTHORITY BOUNDARY: Host certificate only; binding is not IAM or service truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Test owns each Mongo transaction; production composer
                      only receives the already-active session.
FAIL-CLOSED DECLARATION: Runtime, IAM, Deputy, conflict, corruption, or tenant
                         failures reject without binding fabrication.
"""
from __future__ import annotations

from datetime import datetime, timezone
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
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
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
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy
from tools.eos.legal_operations.orchestration.deputy_principal_binding_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    DeputyPrincipalBindingOrchestrationError,
    bind_deputy_principal_identity,
)
from tools.eos.legal_operations.registry.deputy_principal_binding_registry import (
    COLLECTION as BINDING_COLLECTION,
    DeputyPrincipalBindingPersistedRecordInvalidError,
    DeputyPrincipalBindingRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 17, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database; runtime failure is fatal."""
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
                f"L8_6B_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_6B_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_6B_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_6b_binding_{uuid.uuid4().hex}"]
        collections = {
            "lifecycle": database.get_collection(
                LIFECYCLE_COLLECTION,
                write_concern=WriteConcern(w="majority", j=True),
                read_concern=ReadConcern("majority"),
            ),
            "binding": database.get_collection(
                BINDING_COLLECTION,
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
        DeputyPrincipalBindingRegistry.ensure_indexes(collections["binding"])
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


def _seed(
    collections: dict[str, Any],
    tenant: str,
    principal: str,
    deputy: str,
    *,
    business_role: str = "tenant_deputy",
    role_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
) -> Deputy:
    """Persist exact current IAM facts and one canonical Deputy."""
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
            "DEPUTY",
            role_status,
            0,
        ),
        collections["role"],
    )
    value = Deputy(
        tenant_id=tenant,
        deputy_id=deputy,
        sheriff_office_id="office-1",
        display_name="Deputy One",
        badge_reference="badge-1",
        evidence_reference="directory-deputy",
    )
    LegalOperationsLifecycleRegistry.create(value, collections["lifecycle"])
    return value


def _bind(
    collections: dict[str, Any],
    tenant: str,
    principal: str,
    deputy: str,
    session: Any,
    *,
    evidence_reference: str = "binding-evidence",
):
    return bind_deputy_principal_identity(
        tenant_id=tenant,
        principal_id=principal,
        deputy_id=deputy,
        bound_at=NOW,
        evidence_reference=evidence_reference,
        lifecycle_collection=collections["lifecycle"],
        binding_collection=collections["binding"],
        principal_collection=collections["principal"],
        membership_collection=collections["membership"],
        business_role_collection=collections["business"],
        role_assignment_collection=collections["role"],
        session=session,
    )


def test_real_indexes_commit_replay_and_two_way_resolution(
    mongo_context: dict[str, Any],
) -> None:
    """Certify one-to-one indexes, committed create, replay, and both resolvers."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy = f"deputy-{uuid.uuid4().hex}"
    source = _seed(collections, tenant, principal, deputy)

    indexes = {
        item["name"]: item
        for item in collections["binding"].list_indexes()
    }
    assert indexes["legal_operations_tenant_principal_deputy_binding_unique"]["unique"] is True
    assert indexes["legal_operations_tenant_deputy_principal_binding_unique"]["unique"] is True

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        created = _bind(collections, tenant, principal, deputy, session)
        session.commit_transaction()

    assert created.tenant_id == tenant
    assert created.principal_id == principal
    assert created.deputy_id == deputy
    assert created.deputy_fingerprint == source.fingerprint
    assert collections["binding"].count_documents({"tenant_id": tenant}) == 1

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        replay = _bind(collections, tenant, principal, deputy, session)
        by_principal = DeputyPrincipalBindingRegistry.resolve_by_principal(
            tenant,
            principal,
            collections["binding"],
            session=session,
        )
        by_deputy = DeputyPrincipalBindingRegistry.resolve_by_deputy(
            tenant,
            deputy,
            collections["binding"],
            session=session,
        )
        session.commit_transaction()

    assert replay == created
    assert by_principal == created
    assert by_deputy == created
    assert collections["binding"].count_documents({"tenant_id": tenant}) == 1


def test_real_transaction_abort_leaves_no_binding(
    mongo_context: dict[str, Any],
) -> None:
    """Caller abort dominates an otherwise valid binding composition."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy = f"deputy-{uuid.uuid4().hex}"
    _seed(collections, tenant, principal, deputy)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        value = _bind(collections, tenant, principal, deputy, session)
        assert value.deputy_id == deputy
        session.abort_transaction()

    assert collections["binding"].count_documents(
        {"tenant_id": tenant, "principal_id": principal}
    ) == 0


def test_real_wrong_business_role_and_revoked_deputy_role_write_nothing(
    mongo_context: dict[str, Any],
) -> None:
    """Wrong business role or revoked DEPUTY assignment rejects before binding."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]

    tenant_a = f"tenant-{uuid.uuid4().hex}"
    principal_a = f"principal-{uuid.uuid4().hex}"
    deputy_a = f"deputy-{uuid.uuid4().hex}"
    _seed(
        collections,
        tenant_a,
        principal_a,
        deputy_a,
        business_role="tenant_sheriff",
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(DeputyPrincipalBindingOrchestrationError) as wrong:
            _bind(collections, tenant_a, principal_a, deputy_a, session)
        assert wrong.value.code == "L8_6B_DEPUTY_BUSINESS_ROLE_REQUIRED"
        session.abort_transaction()

    tenant_b = f"tenant-{uuid.uuid4().hex}"
    principal_b = f"principal-{uuid.uuid4().hex}"
    deputy_b = f"deputy-{uuid.uuid4().hex}"
    _seed(
        collections,
        tenant_b,
        principal_b,
        deputy_b,
        role_status=RoleAssignmentStatus.REVOKED,
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(DeputyPrincipalBindingOrchestrationError) as revoked:
            _bind(collections, tenant_b, principal_b, deputy_b, session)
        assert revoked.value.code == "L8_6B_DEPUTY_AUTHORIZATION_ROLE_REQUIRED"
        session.abort_transaction()

    assert collections["binding"].count_documents({}) == 0


def test_real_foreign_deputy_scope_is_absence(
    mongo_context: dict[str, Any],
) -> None:
    """A foreign-tenant Deputy cannot satisfy a local principal binding."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy = f"deputy-{uuid.uuid4().hex}"

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
            "tenant_deputy",
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
            "DEPUTY",
            RoleAssignmentStatus.ACTIVE,
            0,
        ),
        collections["role"],
    )
    LegalOperationsLifecycleRegistry.create(
        Deputy(
            tenant_id=foreign,
            deputy_id=deputy,
            sheriff_office_id="office-foreign",
            display_name="Foreign Deputy",
            badge_reference="badge-foreign",
            evidence_reference="foreign-directory",
        ),
        collections["lifecycle"],
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(DeputyPrincipalBindingOrchestrationError) as caught:
            _bind(collections, tenant, principal, deputy, session)
        assert caught.value.code == "L8_6B_DEPUTY_NOT_FOUND"
        session.abort_transaction()

    assert collections["binding"].count_documents({}) == 0


def test_real_same_principal_or_deputy_conflicts_and_corruption_rejects(
    mongo_context: dict[str, Any],
) -> None:
    """Two-way identity conflicts and persisted fingerprint corruption fail closed."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy = f"deputy-{uuid.uuid4().hex}"
    _seed(collections, tenant, principal, deputy)

    with client.start_session() as session:
        session.start_transaction()
        first = _bind(collections, tenant, principal, deputy, session)
        session.commit_transaction()

    deputy_2 = f"deputy-{uuid.uuid4().hex}"
    LegalOperationsLifecycleRegistry.create(
        Deputy(
            tenant_id=tenant,
            deputy_id=deputy_2,
            sheriff_office_id="office-1",
            display_name="Deputy Two",
            badge_reference="badge-2",
            evidence_reference="directory-deputy-2",
        ),
        collections["lifecycle"],
    )

    with client.start_session() as session:
        session.start_transaction()
        with pytest.raises(DeputyPrincipalBindingOrchestrationError) as conflict:
            _bind(collections, tenant, principal, deputy_2, session)
        assert conflict.value.code == "L8_6B_BINDING_CONFLICT"
        session.abort_transaction()

    result = collections["binding"].update_one(
        {
            "tenant_id": tenant,
            "principal_id": principal,
        },
        {"$set": {"fingerprint": "f" * 128}},
    )
    assert result.matched_count == 1
    with pytest.raises(DeputyPrincipalBindingPersistedRecordInvalidError):
        DeputyPrincipalBindingRegistry.resolve_by_principal(
            tenant,
            principal,
            collections["binding"],
        )

    assert first.principal_id == principal
    assert collections["binding"].count_documents({"tenant_id": tenant}) == 1


def test_real_binding_payload_has_no_authorization_or_financial_truth(
    mongo_context: dict[str, Any],
) -> None:
    """Durable binding remains identity evidence only."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"principal-{uuid.uuid4().hex}"
    deputy = f"deputy-{uuid.uuid4().hex}"
    _seed(collections, tenant, principal, deputy)

    with client.start_session() as session:
        session.start_transaction()
        value = _bind(collections, tenant, principal, deputy, session)
        session.commit_transaction()

    keys = set(value.to_dict())
    for forbidden in {
        "permission",
        "role_id",
        "business_role",
        "authorized",
        "queue",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice",
        "payment",
        "settlement",
        "bank_execution",
        "provider_execution",
    }:
        assert forbidden not in keys

    assert PRODUCTION_VERSION == (
        "v1.0.1-L8-6B-DEPUTY-PRINCIPAL-BINDING-ORCHESTRATION"
    )
    assert VERSION == "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-RM-CERT"


# ARTIFACT: test_deputy_principal_binding_real_mongo.py
# VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-BINDING-RM-CERT
# AUTHORITY BOUNDARY: host-backed five-authority immutable identity-binding certificate only
# TENANT POSTURE: exact tenant across durable IAM, P1 Deputy, and binding registry
# FAIL-CLOSED POSTURE: runtime/IAM/Deputy/conflict/corruption/transaction failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
