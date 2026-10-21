"""WILSY OS P12C-R4N physical practitioner HTTP IAM certificate.

VERSION: v1.0.0-P12C-R4N-P2B-DURABLE-IAM-HTTP
AUTHORITY: Existing canonical IAM repositories and authorization composer.
ISOLATION: Disposable random-port local MongoDB replica set, UUID database.
AUTHENTICATION: Controlled immutable identity, not a signed-token claim.
COMMAND: Transaction entry observed without performing a binding write.
TENANT POSTURE: Exact membership and current role authority are durable.
FINANCIAL AUTHORITY: None.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import runpy
from types import SimpleNamespace
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api import legal_practitioner_matter_binding_router as api
from tools.eos.api import tenant_authorization_http as iam
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
)
from tools.eos.auth.tenant_membership import (
    TenantMembershipAuthority,
    TenantMembershipStatus,
)
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository,
)
from tools.eos.auth.tenant_business_role import (
    TenantBusinessRoleAuthority,
    TenantBusinessRoleStatus,
)
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository,
)
from tools.eos.auth.role_assignment import (
    RoleAssignmentAuthority,
    RoleAssignmentStatus,
)
from tools.eos.auth.role_assignment_repository import (
    RoleAssignmentRepository,
)

ROOT = Path(__file__).resolve().parents[2]
PRE = runpy.run_path(
    str(
        ROOT
        / "tests/integration/"
        "test_legal_practitioner_matter_binding_provisioning_real_mongo.py"
    )
)

ACTOR = "partner-p12c-durable"
TENANT = "tenant-p12c-durable"
PERMISSION = "legal_operations:practitioner_matter_binding:provision"
OPERATION = "legal_practitioner_matter_binding_provision"
ENDPOINT = "/api/legal-operations/practitioner-bindings"
COMMANDS = (
    (
        ENDPOINT,
        {
            "case_matter_id": "matter-p12c",
            "practitioner_principal_id": "lawyer-p12c",
            "binding_id": "binding-p12c",
            "access_evidence_id": "evidence-p12c",
            "expected_access_evidence_fingerprint": "a" * 128,
        },
    ),
    (
        ENDPOINT + "/revocations",
        {
            "binding_id": "binding-p12c",
            "evidence_reference": "revocation-p12c",
        },
    ),
)


@pytest.fixture(scope="module")
def isolated_mongo():
    yield from PRE["isolated_mongo"].__wrapped__()


class BoundRepository:
    """Bind canonical repository methods to one isolated collection."""

    def __init__(self, repository, collection):
        self.repository = repository
        self.collection = collection

    def resolve(self, *args, session=None):
        return self.repository.resolve(
            *args, self.collection, session=session
        )


@pytest.mark.parametrize("endpoint,payload", COMMANDS)
@pytest.mark.parametrize(
    "scenario,expected",
    (
        ("eligible", 201),
        ("principal_inactive", 403),
        ("membership_inactive", 403),
        ("foreign_tenant", 403),
        ("wrong_business_role", 403),
        ("missing_permission_grant", 403),
        ("missing_principal", 403),
    ),
)
def test_physical_durable_iam_controls_binding_http(
    monkeypatch, isolated_mongo, endpoint, payload, scenario, expected
):
    assert api._PROVISION.permission_id == PERMISSION
    assert api._PROVISION.operation == OPERATION

    hello = isolated_mongo.admin.command("hello")
    assert hello["isWritablePrimary"] is True
    assert hello["setName"].startswith("wilsyP9Provision")

    database_name = "wilsy_p12c_durable_iam_" + uuid.uuid4().hex
    db = isolated_mongo[database_name]

    principals = db["principal_authorities"]
    memberships = db["tenant_memberships"]
    businesses = db["tenant_business_roles"]
    assignments = db["role_assignments"]
    bindings = db["legal_practitioner_matter_bindings"]

    try:
        PrincipalAuthorityRepository.ensure_indexes(principals)
        TenantMembershipRepository.ensure_indexes(memberships)
        TenantBusinessRoleRepository.ensure_indexes(businesses)
        RoleAssignmentRepository.ensure_indexes(assignments)

        if scenario != "missing_principal":
            PrincipalAuthorityRepository.create(
                PrincipalAuthority(
                    ACTOR,
                    (
                        next(
                            item for item in PrincipalStatus
                            if item is not PrincipalStatus.ACTIVE
                        )
                        if scenario == "principal_inactive"
                        else PrincipalStatus.ACTIVE
                    ),
                    0,
                ),
                principals,
            )

        TenantMembershipRepository.insert(
            TenantMembershipAuthority(
                ACTOR,
                TENANT,
                (
                    next(
                        item for item in TenantMembershipStatus
                        if item is not TenantMembershipStatus.ACTIVE
                    )
                    if scenario == "membership_inactive"
                    else TenantMembershipStatus.ACTIVE
                ),
                0,
            ),
            memberships,
        )

        TenantBusinessRoleRepository.insert(
            TenantBusinessRoleAuthority(
                principal_id=ACTOR,
                tenant_id=TENANT,
                business_role=(
                    "tenant_legal_attorney"
                    if scenario == "wrong_business_role"
                    else "tenant_legal_partner"
                ),
                status=TenantBusinessRoleStatus.ACTIVE,
                revision=0,
                effective_at=datetime.now(timezone.utc),
                revoked_at=None,
            ),
            businesses,
        )

        if scenario != "missing_permission_grant":
            RoleAssignmentRepository.insert(
                RoleAssignmentAuthority(
                    ACTOR,
                    TENANT,
                    "LEGAL_PARTNER",
                    RoleAssignmentStatus.ACTIVE,
                    0,
                ),
                assignments,
            )

        role_reader = iam._TenantAuthorityRoleReader(
            authorization_repository=BoundRepository(
                RoleAssignmentRepository, assignments
            ),
            business_repository=BoundRepository(
                TenantBusinessRoleRepository, businesses
            ),
        )

        identity = SovereignIdentity(
            identity_id=ACTOR,
            tenant_id="UNTRUSTED_TOKEN_TENANT",
            username="durable-iam-certificate",
            email="p12c@example.test",
            auth_method="test",
            status=PrincipalStatus.ACTIVE,
            roles=["ROOT"],
            permissions=["*"],
        )

        app = FastAPI()
        register_error_handlers(app, debug=False)
        app.include_router(api.router, prefix="/api")

        app.dependency_overrides[iam.get_current_identity] = (
            lambda: identity
        )
        app.dependency_overrides[
            iam.get_principal_authority_repository
        ] = lambda: BoundRepository(
            PrincipalAuthorityRepository, principals
        )
        app.dependency_overrides[
            iam.get_tenant_membership_repository
        ] = lambda: BoundRepository(
            TenantMembershipRepository, memberships
        )
        app.dependency_overrides[
            iam.get_role_assignment_repository
        ] = lambda: role_reader

        app.dependency_overrides[
            api.get_authorization_role_repository
        ] = lambda: BoundRepository(
            RoleAssignmentRepository, assignments
        )

        assert api._PROVISION not in app.dependency_overrides

        entries = []

        def observed_transaction(callback):
            entries.append("transaction")
            return {"durable_iam": "ADMITTED"}

        monkeypatch.setattr(
            api, "_transaction", observed_transaction
        )

        tenant_scope = (
            "foreign-p12c-tenant"
            if scenario == "foreign_tenant"
            else TENANT
        )

        response = TestClient(
            app, raise_server_exceptions=True
        ).post(
            endpoint,
            json=payload,
            headers={"X-Tenant-ID": tenant_scope},
        )

        assert response.status_code == expected, (
            scenario, endpoint, response.status_code, response.text
        )

        if scenario == "eligible":
            assert response.json() == {
                "durable_iam": "ADMITTED"
            }
            assert entries == ["transaction"]
        else:
            assert entries == []

        assert bindings.count_documents({}) == 0
        assert identity.tenant_id == "UNTRUSTED_TOKEN_TENANT"
        assert principals.count_documents({}) in (0, 1)
        assert memberships.count_documents({}) == 1
        assert businesses.count_documents({}) == 1
        assert assignments.count_documents({}) in (0, 1)

    finally:
        isolated_mongo.drop_database(database_name)
        assert database_name not in (
            isolated_mongo.list_database_names()
        )


# ARTIFACT: test_legal_practitioner_binding_http_durable_iam.py
# VERSION: v1.0.0-P12C-R4N-P2B-DURABLE-IAM-HTTP
# AUTHORITY: immutable physical IAM registry reads and canonical composer
# DATABASE: UUID-isolated disposable local replica set only
# AUTHENTICATION: controlled identity, not production signed-token proof
# BINDING WRITE: prohibited by transaction-observation fixture
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
