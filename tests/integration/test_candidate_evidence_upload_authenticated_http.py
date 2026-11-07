"""Replica-set authenticated HTTP certification for streamed HR evidence uploads."""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timezone

import pytest

os.environ.setdefault("WILSY_JWT_SECRET", "CANDIDATE-EVIDENCE-HTTP-REPLICA-SET-TEST-SECRET")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient

import tools.eos.api.candidate_evidence_upload_router as upload_router
import tools.eos.api.hiring_lifecycle_router as hiring_router
import tools.eos.api.tenant_authorization_http as http_subject
import tools.eos.kernel.db as kernel_db
import tools.eos.saas.auth.auth_registry as auth_registry_module
import tools.eos.saas.tenancy.tenant_registry as tenant_registry_module
from tools.eos.api.errors import register_error_handlers
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
from tools.eos.saas.auth.auth_registry import AuthRegistry
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry
from tools.eos.saas.hr.candidate_evidence_storage import (
    CandidateEvidenceBinaryObjectEvidence, CandidateEvidenceWriteSession,
)
from tools.eos.saas.hr.candidate_evidence_upload_attempt_registry import (
    COLLECTION as ATTEMPT_COLLECTION, EVENT_COLLECTION as ATTEMPT_EVENT_COLLECTION,
)
from tools.eos.saas.hr.candidate_evidence_registry import (
    COLLECTION as EVIDENCE_COLLECTION, EVENT_COLLECTION as EVIDENCE_EVENT_COLLECTION,
)

URI = os.getenv("HIRING_TEST_MONGODB_URI")
pytestmark = pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")
NOW = datetime.now(timezone.utc)


class FakeStorage:
    def begin(self, intent):
        return CandidateEvidenceWriteSession(
            intent=intent, provider_upload_id="opaque-provider-upload-token",
            provider_object_key="hashed/object/key",
            storage_object_reference="hashed-object-reference", created_at=NOW,
        )

    def write_chunk(self, session, chunk):
        number = len(session.parts) + 1
        session.parts.append({
            "PartNumber": number, "ETag": hashlib.sha3_256(chunk).hexdigest(),
            "length": len(chunk),
        })
        session.bytes_written += len(chunk)
        session.hasher.update(chunk)
        return session.bytes_written

    def complete(self, session):
        return CandidateEvidenceBinaryObjectEvidence(
            intent_fingerprint=session.intent.fingerprint,
            storage_object_reference=session.storage_object_reference,
            object_version_reference="opaque-object-version",
            provider_integrity_reference="opaque-provider-etag",
            byte_length=session.bytes_written,
            content_digest_sha3_512=session.hasher.hexdigest(),
            completed_at=NOW,
        )

    def inspect(self, intent, evidence):
        assert evidence.intent_fingerprint == intent.fingerprint
        return evidence

    def abort(self, session):
        session.closed = True


def _seed_user(db, principal_id, tenant_id):
    db["users"].insert_one({
        "user_id": principal_id, "email": f"{principal_id}@example.com",
        "firstName": "Evidence", "lastName": "Test", "role": "USER",
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
        RoleAssignmentAuthority(
            principal_id, tenant_id, authorization_role, RoleAssignmentStatus.ACTIVE, 0,
        ),
        db["role_assignments"],
    )


def _token(principal_id, tenant_id):
    return create_access_token(
        {"identity_id": principal_id, "tenant_id": tenant_id, "roles": [], "permissions": []},
        token_purpose=TokenPurpose.ACCESS, credential_revision=0,
    )


def _headers(principal_id, tenant_id):
    return {"Authorization": f"Bearer {_token(principal_id, tenant_id)}", "X-Tenant-ID": tenant_id}


def test_authenticated_stream_upload_registers_verified_custody_and_denies_director_upload(monkeypatch):
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    db_name = f"candidate_evidence_http_{uuid.uuid4().hex}"
    db = client[db_name]
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") and hello.get("isWritablePrimary") is True
        for collection, repository in (
            ("principal_authorities", PrincipalAuthorityRepository),
            ("tenant_memberships", TenantMembershipRepository),
            ("tenant_business_roles", TenantBusinessRoleRepository),
            ("role_assignments", RoleAssignmentRepository),
        ):
            repository.ensure_indexes(db[collection])

        tenant = f"tenant-{uuid.uuid4().hex}"
        manager, director = f"hr-manager-{uuid.uuid4().hex}", f"hr-director-{uuid.uuid4().hex}"
        monkeypatch.setattr(tenant_registry_module, "tenants_collection", db["tenants"])
        TenantRegistry.create({"name": "Evidence upload certification", "tenant_id": tenant})
        _seed_user(db, manager, tenant)
        _seed_user(db, director, tenant)
        _seed_iam(db, manager, tenant, "tenant_hr_manager", "HR_MANAGER")
        _seed_iam(db, director, tenant, "tenant_hr_director", "HR_DIRECTOR")

        monkeypatch.setattr(kernel_db, "get_client", lambda: client)
        monkeypatch.setattr(kernel_db, "get_database", lambda: db)
        monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: db)
        monkeypatch.setattr(tenant_registry_module, "tenants_collection", db["tenants"])
        monkeypatch.setattr(http_subject, "get_client", lambda: client)
        monkeypatch.setattr(http_subject, "get_database", lambda: db)
        monkeypatch.setattr(hiring_router, "get_client", lambda: client)
        monkeypatch.setattr(hiring_router, "get_database", lambda: db)
        monkeypatch.setattr(upload_router, "get_client", lambda: client)
        monkeypatch.setattr(upload_router, "get_database", lambda: db)
        monkeypatch.setattr(upload_router, "_storage", lambda: FakeStorage())
        assert AuthRegistry().get_credential_revision(tenant, manager) == 0

        app = FastAPI()
        app.include_router(hiring_router.router, prefix="/api")
        app.include_router(upload_router.router, prefix="/api")
        register_error_handlers(app, debug=False)

        with TestClient(app, raise_server_exceptions=False) as http:
            created = http.post(
                "/api/hr/hiring/candidates",
                headers={**_headers(manager, tenant), "Idempotency-Key": "evidence-candidate-create"},
                json={
                    "candidate_id": "CAN-EVIDENCE-HTTP-1",
                    "requisition_id": "REQ-EVIDENCE-HTTP-1",
                    "candidate_profile_reference": "candidate-profile://opaque/evidence-http-1",
                    "source": "CAREERS_PORTAL",
                },
            )
            assert created.status_code == 201, created.text

            body = b"authenticated streamed evidence payload"
            uploaded = http.put(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/evidence/EVD-HTTP-1/VER-HTTP-1",
                headers={
                    **_headers(manager, tenant),
                    "X-Evidence-Media-Type": "application/pdf",
                    "X-Evidence-Filename": "profile.pdf",
                    "X-Evidence-Kind": "CANDIDATE_PROFILE",
                },
                content=body,
            )
            assert uploaded.status_code == 201, uploaded.text
            result = uploaded.json()
            assert result["status"] == "CUSTODY_REGISTERED"
            assert result["custody_registered"] is True
            assert result["byte_length"] == len(body)

            duplicate = http.put(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/evidence/EVD-HTTP-1/VER-HTTP-1",
                headers={
                    **_headers(manager, tenant),
                    "X-Evidence-Media-Type": "application/pdf",
                    "X-Evidence-Filename": "profile.pdf",
                    "X-Evidence-Kind": "CANDIDATE_PROFILE",
                },
                content=body,
            )
            assert duplicate.status_code == 409

            denied = http.put(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/evidence/EVD-DENIED/VER-1",
                headers={
                    **_headers(director, tenant),
                    "X-Evidence-Media-Type": "application/pdf",
                    "X-Evidence-Filename": "profile.pdf",
                    "X-Evidence-Kind": "CANDIDATE_PROFILE",
                },
                content=body,
            )
            assert denied.status_code == 403

        assert db[ATTEMPT_COLLECTION].count_documents({
            "tenant_id": tenant, "status": "CUSTODY_REGISTERED",
        }) == 1
        assert db[EVIDENCE_COLLECTION].count_documents({
            "tenant_id": tenant, "candidate_id": "CAN-EVIDENCE-HTTP-1",
        }) == 1
        assert db[ATTEMPT_EVENT_COLLECTION].count_documents({"tenant_id": tenant}) >= 4
        assert db[EVIDENCE_EVENT_COLLECTION].count_documents({"tenant_id": tenant}) == 1
    finally:
        client.drop_database(db_name)
        assert db_name not in client.list_database_names()
        client.close()
