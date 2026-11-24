"""TITLE: WILSY EOS candidate evidence authenticated HTTP integration certificate.
VERSION: v1.4.0-PLATFORM-EMPLOYER-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies disposable tenant candidate evidence custody only after the
         existing independent headcount approval lifecycle authorizes intake.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_candidate_evidence_upload_authenticated_http.py
COLLABORATION / OWNERSHIP: Replica-set HTTP coverage for hiring_lifecycle_router.py and candidate_evidence_upload_router.py.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG:
  v1.4.0-PLATFORM-EMPLOYER-HTTP-CERT — Certifies exact-WILSY hiring/evidence HTTP operations in a disposable database without any HR product entitlement and pins both customer/employer dependency pairs.
  v1.3.0-EXPLICIT-WORKFORCE-CURRENTNESS — Seeds active synthetic HR manager/director workforce facts through the canonical immutable registry so customer headcount commands exercise, rather than bypass, currentness authorization.
  v1.2.0-CANDIDATE-TRANSITION-EVIDENCE-CUSTODY — Verifies stage changes require matching same-tenant candidate evidence custody and confirms the persisted transition by authenticated readback.
  v1.1.0-APPROVED-REQUISITION-CANDIDATE-GATE — Creates and independently approves an isolated requisition before candidate evidence custody tests.
  v1.0.0 — Certifies streamed evidence upload, immutable custody, authenticated readback, and role denial.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic disposable principal, tenant, candidate and byte payload only.
TENANT BOUNDARY: All reads/writes use exact canonical WILSY scope within an isolated UUID-named disposable replica-set database; no production tenant is contacted.
AUTHORITY BOUNDARY: Synthetic HR Manager/Director assignments only. This employer-path certificate proves no customer HR entitlement is required; it creates no acceptance, employee admission, production principal, membership, capacity or IAM state.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution or settlement authority.
"""
from __future__ import annotations

import hashlib
from io import BytesIO
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
import tools.eos.api.headcount_requisition_router as headcount_router
import tools.eos.api.tenant_authorization_http as http_subject
from tools.eos.auth.tenant_authorization import _BINDINGS
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as PRODUCT_ENTITLEMENT_CURRENT_COLLECTION,
)
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
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship, WorkforceRelationshipStatus, WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import workforce_relationship_registry
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

    def read_verified_object(self, metadata):
        return BytesIO(b"authenticated streamed evidence payload")

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


def _seed_active_workforce(client, db, tenant_id, principal_ids):
    """Append exact-tenant synthetic workforce facts in the disposable database."""
    collection = db[workforce_relationship_registry.COLLECTION_NAME]
    workforce_relationship_registry.ensure_indexes(collection)

    def persist(session):
        for principal_id in principal_ids:
            relationship = WorkforceRelationship(
                relationship_id=f"candidate-evidence-workforce-{principal_id}",
                revision=1,
                scope_kind=WorkforceScopeKind.TENANT,
                scope_id=tenant_id,
                principal_id=principal_id,
                relationship_type=WorkforceRelationshipType.EMPLOYEE,
                status=WorkforceRelationshipStatus.ACTIVE,
                effective_from=NOW,
                effective_until=None,
                status_effective_at=NOW,
                reason_reference="disposable-candidate-evidence-http-test-currentness",
                supersedes_fingerprint=None,
            )
            workforce_relationship_registry.persist_revision(
                relationship,
                collection=collection,
                session=session,
            )

    with client.start_session() as session:
        session.with_transaction(persist)


def _token(principal_id, tenant_id):
    return create_access_token(
        {"identity_id": principal_id, "tenant_id": tenant_id, "roles": [], "permissions": []},
        token_purpose=TokenPurpose.ACCESS, credential_revision=0,
    )


def _headers(principal_id, tenant_id):
    return {"Authorization": f"Bearer {_token(principal_id, tenant_id)}", "X-Tenant-ID": tenant_id}


def test_candidate_evidence_authority_pairs_keep_customer_and_wilsy_employer_separate():
    """Pin the two exact IAM paths before any disposable HTTP infrastructure runs."""
    expected = (
        (
            upload_router._UPLOAD,
            "hr:hiring_candidate_evidence:upload",
            "hr_hiring_candidate_evidence_upload",
            "platform_employer:hiring_candidate_evidence:upload",
            "platform_employer_hiring_candidate_evidence_upload",
        ),
        (
            upload_router._READ,
            "hr:hiring_candidate_evidence:read",
            "hr_hiring_candidate_evidence_read",
            "platform_employer:hiring_candidate_evidence:read",
            "platform_employer_hiring_candidate_evidence_read",
        ),
    )
    for dependency, customer_permission, customer_operation, employer_permission, employer_operation in expected:
        assert dependency.permission_id == customer_permission
        assert dependency.operation == customer_operation
        assert dependency.platform_employer_permission_id == employer_permission
        assert dependency.platform_employer_operation == employer_operation
        assert _BINDINGS[customer_operation] == customer_permission
        assert _BINDINGS[employer_operation] == employer_permission


@pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")
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
        workforce_relationship_registry.ensure_indexes(
            db[workforce_relationship_registry.COLLECTION_NAME]
        )

        tenant = http_subject.WILSY_COMPANY_TENANT_ID
        manager, director = f"hr-manager-{uuid.uuid4().hex}", f"hr-director-{uuid.uuid4().hex}"
        monkeypatch.setattr(tenant_registry_module, "tenants_collection", db["tenants"])
        TenantRegistry.create({"name": "Disposable WILSY employer certification", "tenant_id": tenant})
        assert db[PRODUCT_ENTITLEMENT_CURRENT_COLLECTION].count_documents(
            {"tenant_id": tenant},
        ) == 0
        _seed_user(db, manager, tenant)
        _seed_user(db, director, tenant)
        _seed_iam(db, manager, tenant, "tenant_hr_manager", "HR_MANAGER")
        _seed_iam(db, director, tenant, "tenant_hr_director", "HR_DIRECTOR")
        _seed_active_workforce(client, db, tenant, (manager, director))

        monkeypatch.setattr(kernel_db, "get_client", lambda: client)
        monkeypatch.setattr(kernel_db, "get_database", lambda: db)
        monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: db)
        monkeypatch.setattr(tenant_registry_module, "tenants_collection", db["tenants"])
        monkeypatch.setattr(http_subject, "get_client", lambda: client)
        monkeypatch.setattr(http_subject, "get_database", lambda: db)
        monkeypatch.setattr(hiring_router, "get_client", lambda: client)
        monkeypatch.setattr(hiring_router, "get_database", lambda: db)
        monkeypatch.setattr(headcount_router, "get_client", lambda: client)
        monkeypatch.setattr(headcount_router, "get_database", lambda: db)
        monkeypatch.setattr(upload_router, "get_client", lambda: client)
        monkeypatch.setattr(upload_router, "get_database", lambda: db)
        monkeypatch.setattr(upload_router, "_storage", lambda: FakeStorage())
        assert AuthRegistry().get_credential_revision(tenant, manager) == 0

        app = FastAPI()
        app.include_router(headcount_router.router, prefix="/api")
        app.include_router(hiring_router.router, prefix="/api")
        app.include_router(upload_router.router, prefix="/api")
        register_error_handlers(app, debug=False)

        with TestClient(app, raise_server_exceptions=False) as http:
            requisition = http.post(
                "/api/hr/headcount-requisitions",
                headers={**_headers(manager, tenant), "Idempotency-Key": "evidence-headcount-create"},
                json={
                    "department_id": "engineering", "position_title": "Platform Engineer",
                    "employment_type": "FULL_TIME", "work_location": "Remote", "headcount": 1,
                    "business_justification": "Disposable evidence custody certification",
                },
            )
            assert requisition.status_code == 201, requisition.text
            requisition_id = requisition.json()["requisition_id"]
            submitted = http.post(
                f"/api/hr/headcount-requisitions/{requisition_id}/submit",
                headers={**_headers(manager, tenant), "Idempotency-Key": "evidence-headcount-submit"},
                json={"expected_revision": 1},
            )
            assert submitted.status_code == 200, submitted.text
            approved = http.post(
                f"/api/hr/headcount-requisitions/{requisition_id}/decision",
                headers={**_headers(director, tenant), "Idempotency-Key": "evidence-headcount-approve"},
                json={"expected_revision": 2, "decision": "APPROVE", "reason": "Independent evidence-test approval"},
            )
            assert approved.status_code == 200, approved.text
            assert approved.json()["status"] == "APPROVED"

            created = http.post(
                "/api/hr/hiring/candidates",
                headers={**_headers(manager, tenant), "Idempotency-Key": "evidence-candidate-create"},
                json={
                    "candidate_id": "CAN-EVIDENCE-HTTP-1",
                    "requisition_id": requisition_id,
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

            evidence_reference = "candidate-evidence://EVD-HTTP-1/VER-HTTP-1"
            content_digest = hashlib.sha3_512(body).hexdigest()
            missing_evidence = http.post(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/transition",
                headers={**_headers(manager, tenant), "Idempotency-Key": "candidate-transition-missing-evidence"},
                json={
                    "expected_revision": 1, "target_stage": "SCREENING",
                    "reason": "Verify source custody before stage change",
                    "evidence_reference": "candidate-evidence://EVD-MISSING/VER-MISSING",
                    "evidence_fingerprint": content_digest,
                },
            )
            assert missing_evidence.status_code == 409, missing_evidence.text
            assert missing_evidence.json()["detail"] == "CANDIDATE_TRANSITION_VERIFIED_EVIDENCE_REQUIRED"

            transitioned = http.post(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/transition",
                headers={**_headers(manager, tenant), "Idempotency-Key": "candidate-transition-verified-evidence"},
                json={
                    "expected_revision": 1, "target_stage": "SCREENING",
                    "reason": "Verified candidate profile reviewed",
                    "evidence_reference": evidence_reference,
                    "evidence_fingerprint": content_digest,
                },
            )
            assert transitioned.status_code == 200, transitioned.text
            assert transitioned.json()["stage"] == "SCREENING"
            assert transitioned.json()["revision"] == 2
            assert transitioned.json()["history"][-1]["evidence_reference"] == evidence_reference
            assert transitioned.json()["history"][-1]["evidence_fingerprint"] == content_digest

            tampered_evidence = http.post(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/transition",
                headers={**_headers(manager, tenant), "Idempotency-Key": "candidate-transition-tampered-digest"},
                json={
                    "expected_revision": 2, "target_stage": "INTERVIEW",
                    "reason": "Digest mismatch must not advance stage",
                    "evidence_reference": evidence_reference,
                    "evidence_fingerprint": "0" * 128,
                },
            )
            assert tampered_evidence.status_code == 409, tampered_evidence.text
            assert tampered_evidence.json()["detail"] == "CANDIDATE_TRANSITION_VERIFIED_EVIDENCE_REQUIRED"
            read_candidate = http.get(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1",
                headers=_headers(manager, tenant),
            )
            assert read_candidate.status_code == 200, read_candidate.text
            assert read_candidate.json()["stage"] == "SCREENING"
            assert read_candidate.json()["revision"] == 2

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

            read_manager = http.get(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/evidence/EVD-HTTP-1/VER-HTTP-1",
                headers=_headers(manager, tenant),
            )
            assert read_manager.status_code == 200, read_manager.text
            assert read_manager.content == body
            assert read_manager.headers["cache-control"] == "no-store"

            read_director = http.get(
                "/api/hr/hiring/candidates/CAN-EVIDENCE-HTTP-1/evidence/EVD-HTTP-1/VER-HTTP-1",
                headers=_headers(director, tenant),
            )
            assert read_director.status_code == 200, read_director.text
            assert read_director.content == body

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


# ARTIFACT: tests/integration/test_candidate_evidence_upload_authenticated_http.py
# VERSION: v1.4.0-PLATFORM-EMPLOYER-HTTP-CERT
# AUTHORITY BOUNDARY: Synthetic authenticated test evidence only; source routes own authorization and custody. Exact-WILSY employer path has no HR entitlement; acceptance/admission remain disabled.
# TENANT POSTURE: Canonical WILSY tenant identifier exists only in a UUID-named disposable database; cleanup is mandatory.
# FAIL-CLOSED POSTURE: Missing approval, absent or mismatched evidence custody, denied upload, failed readback or failed cleanup fails certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
