"""Host-backed certificate for bounded Legal client matter projection.

TITLE: WILSY OS Legal Client Matter Projection Real-Mongo Certificate
VERSION: v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-RM-CERT
AUTHORITY: Host-backed certification of current IAM + visibility + CaseMatter snapshot projection.
EPITOME: Prove on the verified Mongo replica set that one current LEGAL_CLIENT
         sees only ACTIVE explicitly-bound matters, receives current P1 state
         including legitimate OPEN->CLOSED progression, excludes revoked
         visibility despite durable ACTIVE history, and receives no internal
         lifecycle/service/financial evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_matter_projection_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for D5 using canonical IAM
                            repositories, L8-7B visibility and P2/L8-5 matter
                            history. HTTP transport and dashboard remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-RM-CERT
           establishes committed snapshot projection, current matter-state
           reflection, append-only revoked-visibility suppression, current IAM
           denial, deterministic safe payload shape and non-financial field
           exclusion against real MongoDB.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenant/client/matter data.
TENANT BOUNDARY: Every IAM, visibility and matter row is exact-tenant scoped.
AUTHORITY BOUNDARY: Host read-projection certificate only; no HTTP or mutation authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests own snapshot transactions; D5 receives active sessions.
FAIL-CLOSED DECLARATION: Runtime, IAM, visibility or matter evidence failure
                         rejects without tenant-wide or partial fallback.
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
from tools.eos.legal_operations.domain.legal_client_matter_projection import (
    VERSION as PRODUCTION_VERSION,
    LegalClientMatterProjectionError,
    get_legal_client_matter_projection,
)
from tools.eos.legal_operations.domain.legal_client_matter_visibility_binding import (
    LegalClientMatterVisibilityBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)
from tools.eos.legal_operations.registry.legal_client_matter_visibility_registry import (
    COLLECTION as VISIBILITY_COLLECTION,
    LegalClientMatterVisibilityRegistry,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION as LIFECYCLE_COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 23, 21, 30, tzinfo=timezone.utc)


class _PrincipalReader:
    """Adapt canonical principal persistence to the D5 read protocol."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(self, principal_id: str, *, session: Any = None) -> object:
        return PrincipalAuthorityRepository.get(
            principal_id,
            self.collection,
            session=session,
        )


class _MembershipReader:
    """Adapt canonical tenant membership persistence to D5."""

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
    """Adapt the one-current-business-role authority to the generic reader."""

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
    """Adapt canonical final-role persistence to the D5 read protocol."""

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
                f"L8_7D5_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_7D5_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_7D5_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_7d5_{uuid.uuid4().hex}"]
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


def _seed_client(
    collections: dict[str, Any],
    *,
    tenant: str,
    principal: str,
    role_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
) -> None:
    """Persist exact current LEGAL_CLIENT IAM for one synthetic principal."""
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
            "tenant_legal_client",
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
            "LEGAL_CLIENT",
            role_status,
            0,
        ),
        collections["role"],
    )


def _matter(
    *,
    tenant: str,
    matter_id: str,
) -> CaseMatter:
    """Build one canonical OPEN matter."""
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"CLIENT-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"matter-evidence-{matter_id}",
    )


def _grant_visibility(
    collections: dict[str, Any],
    *,
    principal: str,
    matter: CaseMatter,
) -> LegalClientMatterVisibilityBinding:
    """Persist one ACTIVE visibility relation for one canonical matter."""
    value = LegalClientMatterVisibilityBinding.grant(
        client_principal_id=principal,
        case_matter=matter,
        granted_by_principal_id="principal-provisioner",
        granted_at=NOW + timedelta(minutes=1),
        evidence_reference=f"visibility-{matter.case_matter_id}",
    )
    return LegalClientMatterVisibilityRegistry.grant(
        value,
        collections["visibility"],
    )


def _projection(
    collections: dict[str, Any],
    *,
    tenant: str,
    principal: str,
    session: Any,
):
    principal_reader = _PrincipalReader(collections["principal"])
    membership_reader = _MembershipReader(collections["membership"])
    business_reader = _BusinessRoleReader(collections["business"])
    role_reader = _AuthorizationRoleReader(collections["role"])
    return get_legal_client_matter_projection(
        tenant_id=tenant,
        principal_id=principal,
        visibility_collection=collections["visibility"],
        lifecycle_collection=collections["lifecycle"],
        principal_repository=principal_reader,
        membership_repository=membership_reader,
        business_role_repository=business_reader,
        role_assignment_repository=role_reader,
        session=session,
    )


def test_real_authorized_projection_reflects_current_state_and_safe_shape(
    mongo_context: dict[str, Any],
) -> None:
    """Two active bindings project deterministic current OPEN/CLOSED cards."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    _seed_client(collections, tenant=tenant, principal=principal)

    open_matter = _matter(tenant=tenant, matter_id="matter-b")
    closing_matter = _matter(tenant=tenant, matter_id="matter-a")
    LegalOperationsLifecycleRegistry.create(
        open_matter,
        collections["lifecycle"],
    )
    LegalOperationsLifecycleRegistry.create(
        closing_matter,
        collections["lifecycle"],
    )
    _grant_visibility(
        collections,
        principal=principal,
        matter=open_matter,
    )
    closing_binding = _grant_visibility(
        collections,
        principal=principal,
        matter=closing_matter,
    )
    closed = closing_matter.transition_to(
        CaseMatterState.CLOSED,
        evidence_reference="matter-closed",
        occurred_at=NOW + timedelta(hours=1),
    )
    assert closed.fingerprint != closing_binding.source_case_matter_fingerprint
    LegalOperationsLifecycleRegistry.create(
        closed,
        collections["lifecycle"],
    )

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )
        result = _projection(
            collections,
            tenant=tenant,
            principal=principal,
            session=session,
        )
        session.commit_transaction()

    assert [value.case_matter_id for value in result.matters] == [
        "matter-a",
        "matter-b",
    ]
    assert [value.state for value in result.matters] == [
        CaseMatterState.CLOSED,
        CaseMatterState.OPEN,
    ]
    payload = result.to_dict()
    assert payload["visibility"] == "LEGAL_CLIENT_EXPLICIT_MATTERS"
    matters = payload["matters"]
    assert isinstance(matters, list)
    assert matters == [
        {
            "case_matter_id": "matter-a",
            "matter_reference": "CLIENT-matter-a",
            "opened_at": NOW.isoformat(),
            "state": "CLOSED",
        },
        {
            "case_matter_id": "matter-b",
            "matter_reference": "CLIENT-matter-b",
            "opened_at": NOW.isoformat(),
            "state": "OPEN",
        },
    ]
    forbidden = {
        "principal_id",
        "client_principal_id",
        "evidence_reference",
        "fingerprint",
        "transition_history",
        "instruction_id",
        "document_id",
        "deputy_id",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "invoice_id",
        "payment_id",
        "settlement_id",
    }
    assert forbidden.isdisjoint(payload)
    for item in matters:
        assert isinstance(item, dict)
        assert forbidden.isdisjoint(item)


def test_real_revoked_visibility_is_not_projected_despite_durable_active_history(
    mongo_context: dict[str, Any],
) -> None:
    """Append-only ACTIVE+REVOKED history yields no current client matter."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    _seed_client(collections, tenant=tenant, principal=principal)

    visible = _matter(tenant=tenant, matter_id="matter-visible")
    revoked_matter = _matter(tenant=tenant, matter_id="matter-revoked")
    for value in (visible, revoked_matter):
        LegalOperationsLifecycleRegistry.create(
            value,
            collections["lifecycle"],
        )
    _grant_visibility(collections, principal=principal, matter=visible)
    active = _grant_visibility(
        collections,
        principal=principal,
        matter=revoked_matter,
    )
    revoked = active.revoke(
        revoked_by_principal_id="principal-provisioner",
        revoked_at=NOW + timedelta(minutes=2),
        evidence_reference="visibility-revoked",
    )
    LegalClientMatterVisibilityRegistry.revoke(
        revoked,
        collections["visibility"],
    )

    assert collections["visibility"].count_documents(
        {
            "tenant_id": tenant,
            "case_matter_id": "matter-revoked",
        }
    ) == 2

    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"))
        result = _projection(
            collections,
            tenant=tenant,
            principal=principal,
            session=session,
        )
        session.commit_transaction()

    assert [value.case_matter_id for value in result.matters] == [
        "matter-visible"
    ]


def test_real_inactive_final_role_denies_before_client_projection(
    mongo_context: dict[str, Any],
) -> None:
    """Revoked LEGAL_CLIENT current truth cannot consume an ACTIVE visibility row."""
    client = mongo_context["client"]
    collections = mongo_context["collections"]
    tenant = f"tenant-{uuid.uuid4().hex}"
    principal = f"client-{uuid.uuid4().hex}"
    _seed_client(
        collections,
        tenant=tenant,
        principal=principal,
        role_status=RoleAssignmentStatus.REVOKED,
    )
    matter = _matter(tenant=tenant, matter_id="matter-denied")
    LegalOperationsLifecycleRegistry.create(
        matter,
        collections["lifecycle"],
    )
    _grant_visibility(collections, principal=principal, matter=matter)

    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"))
        with pytest.raises(LegalClientMatterProjectionError) as caught:
            _projection(
                collections,
                tenant=tenant,
                principal=principal,
                session=session,
            )
        assert caught.value.code == (
            "L8_7D5_CLIENT_AUTHORIZATION_DENIED_ROLE_ASSIGNMENT_INACTIVE"
        )
        session.abort_transaction()

    assert PRODUCTION_VERSION == "v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION"


# SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_client_matter_projection_real_mongo.py
# VERSION: v1.0.0-L8-7D5-CLIENT-MATTER-PROJECTION-RM-CERT
# AUTHORITY BOUNDARY: real-Mongo D5 current IAM + ACTIVE visibility + current CaseMatter safe projection certificate only
# TENANT POSTURE: exact tenant/principal and one active snapshot session span all durable projection reads
# FAIL-CLOSED POSTURE: revoked IAM/visibility or matter evidence failure cannot become client projection data
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
