"""Workspace Bootstrap Projection isolated real-Mongo certificate.

TITLE: Workspace Bootstrap Projection Real-Mongo Certificate
VERSION: v1.0.0-WILSY-WORKSPACE-BOOTSTRAP-REAL-MONGO-CERT
AUTHORITY: Evidence-only certification of durable workspace-bootstrap composition.
EPITOME: Proves exact membership, dedicated business role, canonical tenant,
         current durable truth, shared-session visibility, and read-only behavior
         against an isolated certified Mongo replica-set database.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_workspace_bootstrap_projection_real_mongo.py

AUTHORITY BOUNDARY:
    Evidence only. Authentication/current-principal truth remains owned by the
    canonical authentication chain. JWT roles/permissions are deliberately forged
    here and must not influence workspace authority.

TENANT BOUNDARY:
    The identity tenant claim is candidate scope only. Exact ACTIVE membership,
    exact ACTIVE dedicated tenant-business-role evidence, and exact ACTIVE
    canonical tenant persistence must all agree before projection succeeds.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any, Iterator
from uuid import uuid4

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.auth.workspace_bootstrap_projection import (
    WorkspaceBootstrapProjectionError,
    build_workspace_bootstrap_projection,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry


VERSION = "v1.0.0-WILSY-WORKSPACE-BOOTSTRAP-REAL-MONGO-CERT"
URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 20, tzinfo=timezone.utc)


def _identity(principal_id: str, tenant_id: str) -> SovereignIdentity:
    """Return authenticated candidate scope with intentionally forged JWT authority."""
    return SovereignIdentity(
        identity_id=principal_id,
        tenant_id=tenant_id,
        username=principal_id,
        email=f"{principal_id}@example.invalid",
        roles=["SUPER_ADMIN"],
        permissions=["*"],
        auth_method="JWT",
        status=PrincipalStatus.ACTIVE,
    )


def _tenant_document(tenant_id: str) -> dict[str, Any]:
    """Return the canonical ACTIVE tenant document shape used by TenantRegistry."""
    created_at = datetime(2026, 9, 20, tzinfo=timezone.utc)
    return {
        "tenant_id": tenant_id,
        "name": "Workspace Bootstrap Tenant",
        "organization": {
            "organization_name": "Workspace Bootstrap Tenant",
            "industry": "Legal",
            "plan": "ENTERPRISE",
            "legal_name": "Workspace Bootstrap Tenant (Pty) Ltd",
            "tax_id": "workspace-bootstrap-tax",
            "contact_email": "workspace-bootstrap@example.invalid",
            "regions": ["Africa"],
            "created_at": created_at.isoformat(),
        },
        "industry": "Legal",
        "legal_name": "Workspace Bootstrap Tenant (Pty) Ltd",
        "tax_id": "workspace-bootstrap-tax",
        "contact_email": "workspace-bootstrap@example.invalid",
        "plan": "ENTERPRISE",
        "status": "ACTIVE",
        "created_at": created_at,
        "checksum": "workspace-bootstrap-cert",
        "alias": f"alias-{tenant_id}",
        "region": "ZA",
        "sector": "Law",
        "compliance_flags": {"certified": True},
        "proof_hash": "workspace-bootstrap-proof",
        "verified": True,
    }


def _snapshot(*collections: Any) -> tuple[tuple[int, str], ...]:
    """Return deterministic no-mutation evidence for all durable authority sources."""
    evidence: list[tuple[int, str]] = []
    for collection in collections:
        documents = [
            {key: value for key, value in row.items() if key != "_id"}
            for row in collection.find({})
        ]
        documents.sort(
            key=lambda row: json.dumps(row, sort_keys=True, default=str)
        )
        payload = json.dumps(
            documents,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode()
        evidence.append(
            (len(documents), hashlib.sha3_512(payload).hexdigest())
        )
    return tuple(evidence)


class _BoundMembershipRepository:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return TenantMembershipRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


class _BoundBusinessRoleRepository:
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def resolve(
        self,
        principal_id: str,
        tenant_id: str,
        *,
        session: Any = None,
    ) -> Any:
        return TenantBusinessRoleRepository.resolve(
            principal_id,
            tenant_id,
            self.collection,
            session=session,
        )


@pytest.fixture(scope="module")
def mongo_database() -> Iterator[tuple[Any, Any]]:
    """Bind one UUID-isolated database to the certified writable replica set."""
    client = MongoClient(
        URI,
        serverSelectionTimeoutMS=3000,
        replicaSet=REPLICA_SET,
        retryWrites=True,
    )
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.skip(
            "workspace-bootstrap Mongo runtime unavailable: "
            f"{type(error).__name__}"
        )

    if (
        hello.get("setName") != REPLICA_SET
        or not hello.get(
            "isWritablePrimary",
            hello.get("ismaster", False),
        )
    ):
        client.close()
        pytest.skip(
            "workspace-bootstrap certificate requires writable certified replica set"
        )

    database_name = "workspace_bootstrap_cert_" + uuid4().hex
    database = client.get_database(
        database_name,
        read_concern=ReadConcern("majority"),
        write_concern=WriteConcern(w="majority", j=True),
    )

    try:
        yield client, database
    finally:
        client.drop_database(database_name)
        assert database_name not in client.list_database_names()
        client.close()


@pytest.fixture()
def authority_collections(
    mongo_database: tuple[Any, Any],
) -> Iterator[tuple[Any, Any, Any, Any]]:
    """Create governed indexes and isolate every certificate assertion."""
    _, database = mongo_database
    memberships = database["tenant_memberships"]
    business_roles = database["tenant_business_roles"]
    tenants = database["tenants"]

    TenantMembershipRepository.ensure_indexes(memberships)
    TenantBusinessRoleRepository.ensure_indexes(business_roles)

    memberships.delete_many({})
    business_roles.delete_many({})
    tenants.delete_many({})

    try:
        yield database, memberships, business_roles, tenants
    finally:
        memberships.delete_many({})
        business_roles.delete_many({})
        tenants.delete_many({})


def _build(
    identity: SovereignIdentity,
    memberships: Any,
    business_roles: Any,
    tenants: Any,
    *,
    session: Any = None,
) -> Any:
    """Compose through the production function with only persistence bindings injected."""
    return build_workspace_bootstrap_projection(
        identity=identity,
        membership_repository=_BoundMembershipRepository(memberships),
        business_role_repository=_BoundBusinessRoleRepository(business_roles),
        tenant_resolver=lambda tenant_id, *, session=None: (
            TenantRegistry.resolve_canonical_tenant(
                tenant_id,
                collection=tenants,
                session=session,
            )
        ),
        session=session,
    )


def test_real_mongo_workspace_projection_uses_exact_current_durable_truth(
    authority_collections: tuple[Any, Any, Any, Any],
) -> None:
    """JWT claims cannot replace exact durable membership, role, or tenant truth."""
    _, memberships, business_roles, tenants = authority_collections
    principal_id = f"principal-{uuid4().hex}"
    tenant_id = f"tenant-{uuid4().hex}"
    identity = _identity(principal_id, tenant_id)

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            7,
        ),
        memberships,
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id,
            tenant_id,
            "tenant_auditor",
            TenantBusinessRoleStatus.ACTIVE,
            11,
            NOW,
            None,
        ),
        business_roles,
    )
    tenants.insert_one(_tenant_document(tenant_id))

    before = _snapshot(memberships, business_roles, tenants)
    projection = _build(
        identity,
        memberships,
        business_roles,
        tenants,
    )
    after = _snapshot(memberships, business_roles, tenants)

    assert projection.principal_id == principal_id
    assert projection.tenant_id == tenant_id
    assert projection.business_role == "tenant_auditor"
    assert projection.business_role != "SUPER_ADMIN"
    assert projection.membership_revision == 7
    assert projection.business_role_revision == 11
    assert projection.tenant.tenant_id == tenant_id
    assert before == after


def test_real_mongo_workspace_projection_fails_closed_on_inactive_durable_truth(
    authority_collections: tuple[Any, Any, Any, Any],
) -> None:
    """Inactive membership and dedicated business-role rows deny independently."""
    _, memberships, business_roles, tenants = authority_collections

    membership_principal = f"principal-{uuid4().hex}"
    membership_tenant = f"tenant-{uuid4().hex}"
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            membership_principal,
            membership_tenant,
            TenantMembershipStatus.SUSPENDED,
            0,
        ),
        memberships,
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            membership_principal,
            membership_tenant,
            "tenant_auditor",
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        business_roles,
    )
    tenants.insert_one(_tenant_document(membership_tenant))

    with pytest.raises(
        WorkspaceBootstrapProjectionError,
        match="WORKSPACE_BOOTSTRAP_MEMBERSHIP_INACTIVE",
    ):
        _build(
            _identity(membership_principal, membership_tenant),
            memberships,
            business_roles,
            tenants,
        )

    memberships.delete_many({})
    business_roles.delete_many({})
    tenants.delete_many({})

    role_principal = f"principal-{uuid4().hex}"
    role_tenant = f"tenant-{uuid4().hex}"
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            role_principal,
            role_tenant,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        memberships,
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            role_principal,
            role_tenant,
            "tenant_auditor",
            TenantBusinessRoleStatus.REVOKED,
            0,
            NOW,
            NOW,
        ),
        business_roles,
    )
    tenants.insert_one(_tenant_document(role_tenant))

    with pytest.raises(
        WorkspaceBootstrapProjectionError,
        match="WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_INACTIVE",
    ):
        _build(
            _identity(role_principal, role_tenant),
            memberships,
            business_roles,
            tenants,
        )


def test_real_mongo_workspace_projection_requires_canonical_tenant(
    authority_collections: tuple[Any, Any, Any, Any],
) -> None:
    """Membership and role evidence cannot fabricate an absent canonical tenant."""
    _, memberships, business_roles, tenants = authority_collections
    principal_id = f"principal-{uuid4().hex}"
    tenant_id = f"tenant-{uuid4().hex}"

    TenantMembershipRepository.insert(
        TenantMembershipAuthority(
            principal_id,
            tenant_id,
            TenantMembershipStatus.ACTIVE,
            0,
        ),
        memberships,
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id,
            tenant_id,
            "tenant_owner",
            TenantBusinessRoleStatus.ACTIVE,
            0,
            NOW,
            None,
        ),
        business_roles,
    )

    before = _snapshot(memberships, business_roles, tenants)

    with pytest.raises(
        WorkspaceBootstrapProjectionError,
        match="WORKSPACE_BOOTSTRAP_TENANT_UNAVAILABLE",
    ):
        _build(
            _identity(principal_id, tenant_id),
            memberships,
            business_roles,
            tenants,
        )

    assert before == _snapshot(memberships, business_roles, tenants)


def test_real_mongo_workspace_projection_forwards_one_shared_transaction_session(
    mongo_database: tuple[Any, Any],
    authority_collections: tuple[Any, Any, Any, Any],
) -> None:
    """All three durable sources are visible in one transaction and vanish on abort."""
    client, _ = mongo_database
    _, memberships, business_roles, tenants = authority_collections
    principal_id = f"principal-{uuid4().hex}"
    tenant_id = f"tenant-{uuid4().hex}"
    identity = _identity(principal_id, tenant_id)

    with client.start_session() as session:
        session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
        )

        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                principal_id,
                tenant_id,
                TenantMembershipStatus.ACTIVE,
                3,
            ),
            memberships,
            session=session,
        )
        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id,
                tenant_id,
                "tenant_admin",
                TenantBusinessRoleStatus.ACTIVE,
                5,
                NOW,
                None,
            ),
            business_roles,
            session=session,
        )
        tenants.insert_one(
            _tenant_document(tenant_id),
            session=session,
        )

        projection = _build(
            identity,
            memberships,
            business_roles,
            tenants,
            session=session,
        )

        assert projection.tenant_id == tenant_id
        assert projection.business_role == "tenant_admin"
        assert projection.membership_revision == 3
        assert projection.business_role_revision == 5

        session.abort_transaction()

    assert memberships.count_documents({}) == 0
    assert business_roles.count_documents({}) == 0
    assert tenants.count_documents({}) == 0


# ARTIFACT: test_workspace_bootstrap_projection_real_mongo.py
# VERSION: v1.0.0-WILSY-WORKSPACE-BOOTSTRAP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated real-Mongo workspace-bootstrap composition evidence only
# TENANT POSTURE: exact durable membership + dedicated business role + canonical tenant
# FAIL-CLOSED POSTURE: absent/inactive durable workspace truth denies
# JWT ROLE/PERMISSION AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
