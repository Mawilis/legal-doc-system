"""Real replica-set authenticated HTTP certification for hiring commands."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
os.environ.setdefault("WILSY_JWT_SECRET", "HIRING-HTTP-REPLICA-SET-CERT-ONLY-SECRET")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

import tools.eos.api.hiring_lifecycle_router as hiring_router
import tools.eos.api.tenant_authorization_http as http_subject
import tools.eos.kernel.db as kernel_db
import tools.eos.saas.auth.auth_registry as auth_registry_module
import tools.eos.saas.tenancy.tenant_registry as tenant_registry_module
from tools.eos.api.errors import register_error_handlers
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.auth.jwt_provider import TokenPurpose, create_access_token
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentRepository
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import TenantBusinessRoleRepository
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipRepository
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry

URI = os.getenv("HIRING_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")
NOW = datetime.now(timezone.utc)


def _seed_user(db, principal_id, tenant_id):
    db["users"].insert_one({
        "user_id": principal_id, "email": f"{principal_id}@example.invalid",
        "firstName": "Hiring", "lastName": "Test", "role": "USER",
        "permissions": [], "tenantId": tenant_id, "passwordHash": "test-only",
        "credential_revision": 0, "mfaRegistered": False, "hasSignedCovenant": False,
    })


def _seed_iam(db, principal_id, tenant_id, business_role, authorization_role):
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
        db["principal_authorities"],
    )
    TenantMembershipRepository.insert(
        TenantMembershipAuthority(principal_id, tenant_id, TenantMembershipStatus.ACTIVE, 0),
        db["tenant_memberships"],
    )
    TenantBusinessRoleRepository.insert(
        TenantBusinessRoleAuthority(
            principal_id=principal_id, tenant_id=tenant_id,
            business_role=business_role, status=TenantBusinessRoleStatus.ACTIVE,
            revision=0, effective_at=NOW, revoked_at=None,
        ),
        db["tenant_business_roles"],
    )
    RoleAssignmentRepository.insert(
        RoleAssignmentAuthority(principal_id, tenant_id, authorization_role, RoleAssignmentStatus.ACTIVE, 0),
        db["role_assignments"],
    )


def _token(principal_id, tenant_id):
    return create_access_token(
        {"identity_id": principal_id, "tenant_id": tenant_id, "roles": [], "permissions": []},
        token_purpose=TokenPurpose.ACCESS, credential_revision=0,
    )


def _headers(principal_id, tenant_id):
    return {"Authorization": f"Bearer {_token(principal_id, tenant_id)}", "X-Tenant-ID": tenant_id}


def test_authenticated_hiring_http_uses_durable_iam_and_rejects_wrong_tenant_and_wrong_grant(monkeypatch):
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    db_name = f"hiring_http_iam_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        PrincipalAuthorityRepository.ensure_indexes(db["principal_authorities"])
        TenantMembershipRepository.ensure_indexes(db["tenant_memberships"])
        TenantBusinessRoleRepository.ensure_indexes(db["tenant_business_roles"])
        RoleAssignmentRepository.ensure_indexes(db["role_assignments"])

        tenant, other_tenant = f"tenant-{uuid.uuid4().hex}", f"other-{uuid.uuid4().hex}"
        manager, mismatch = f"hr-manager-{uuid.uuid4().hex}", f"hr-mismatch-{uuid.uuid4().hex}"
        monkeypatch.setattr(tenant_registry_module, "tenants_collection", db["tenants"])
        TenantRegistry.create({"name": "Hiring HTTP certification", "tenant_id": tenant})
        TenantRegistry.create({"name": "Hiring HTTP other tenant", "tenant_id": other_tenant})
        _seed_user(db, manager, tenant)
        _seed_user(db, mismatch, tenant)
        _seed_iam(db, manager, tenant, "tenant_hr_manager", "HR_MANAGER")
        _seed_iam(db, mismatch, tenant, "tenant_hr_manager", "HR_DIRECTOR")

        monkeypatch.setattr(kernel_db, "get_client", lambda: client)
        monkeypatch.setattr(kernel_db, "get_database", lambda: db)
        monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: db)
        monkeypatch.setattr(tenant_registry_module, "tenants_collection", db["tenants"])
        monkeypatch.setattr(http_subject, "get_client", lambda: client)
        monkeypatch.setattr(http_subject, "get_database", lambda: db)
        monkeypatch.setattr(hiring_router, "get_client", lambda: client)
        monkeypatch.setattr(hiring_router, "get_database", lambda: db)
        assert AuthRegistry().get_credential_revision(tenant, manager) == 0

        app = FastAPI()
        app.include_router(hiring_router.router, prefix="/api")
        register_error_handlers(app, debug=False)
        with TestClient(app, raise_server_exceptions=False) as http:
            allowed = http.post(
                "/api/hr/hiring/candidates",
                headers={**_headers(manager, tenant), "Idempotency-Key": "http-candidate-1"},
                json={
                    "candidate_id": "CAN-HTTP-1", "requisition_id": "REQ-HTTP-1",
                    "candidate_profile_reference": "candidate-profile://opaque/http-1",
                    "source": "CAREERS_PORTAL",
                },
            )
            assert allowed.status_code == 201, allowed.text
            assert allowed.json()["tenant_id"] == tenant

            wrong_tenant = http.post(
                "/api/hr/hiring/candidates",
                headers={**_headers(manager, other_tenant), "Idempotency-Key": "http-candidate-wrong-tenant"},
                json={
                    "candidate_id": "CAN-HTTP-OTHER", "requisition_id": "REQ-HTTP-1",
                    "candidate_profile_reference": "candidate-profile://opaque/http-other",
                    "source": "CAREERS_PORTAL",
                },
            )
            assert wrong_tenant.status_code == 403

            wrong_grant = http.post(
                "/api/hr/hiring/candidates",
                headers={**_headers(mismatch, tenant), "Idempotency-Key": "http-candidate-wrong-role"},
                json={
                    "candidate_id": "CAN-HTTP-DENIED", "requisition_id": "REQ-HTTP-1",
                    "candidate_profile_reference": "candidate-profile://opaque/http-denied",
                    "source": "CAREERS_PORTAL",
                },
            )
            assert wrong_grant.status_code == 403

        assert db["wilsy_hr_candidate_applications"].count_documents({"tenant_id": tenant}) == 1
        assert db["wilsy_hr_hiring_lifecycle_events"].count_documents({"tenant_id": tenant}) == 1
    finally:
        client.drop_database(db_name)
        assert db_name not in client.list_database_names()
        client.close()
