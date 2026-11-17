"""TITLE: WILSY EOS hiring list and command real-Mongo HTTP regressions.
VERSION: v1.6.0-STRUCTURED-HR-DENIAL-CERT
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies authenticated hiring commands and bounded candidate/offer reads
         against an isolated writable MongoDB replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_hiring_lifecycle_authenticated_real_http.py
COLLABORATION / OWNERSHIP: Direct HTTP integration coverage for hiring_lifecycle_router.py.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG:
  v1.6.0-STRUCTURED-HR-DENIAL-CERT — Asserts the standard structured 403 error code for an IAM-current but unentitled customer instead of assuming a FastAPI detail field.
  v1.5.0-EXPLICIT-HR-ENTITLEMENT-CERT — Seeds customer HR entitlement through D22B2, proves same-tenant customer access requires it, and adds an independently runnable employer route-pair contract.
  v1.4.0-ACCEPTANCE-IDENTITY-FAIL-CLOSED-HTTP — Verifies authenticated offer acceptance returns the governed identity-binding unavailable outcome and writes neither offer state nor lifecycle events.
  v1.3.0-EXPLICIT-WORKFORCE-AUTHORITY-FIXTURE — Seeds active synthetic workforce relationships through the canonical immutable registry so headcount HTTP tests satisfy currentness without bypassing authorization.
  v1.2.0-APPROVED-REQUISITION-CANDIDATE-GATE — Establishes a disposable requisition through independent approval and verifies unapproved candidate intake is denied.
  v1.1.0-AUTHENTICATED-HIRING-READ-PAGES — Verifies source readback, authoritative empty offers, pagination bounds, and tenant denial using durable disposable data.
  v1.0.0 — Certifies exact-tenant authenticated hiring commands with durable IAM.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Uses synthetic principals, tenants, and aggregates; each test drops its UUID-scoped database.
TENANT BOUNDARY: Every allowed read is bound to the authenticated tenant; mismatched tenant context is denied.
AUTHORITY BOUNDARY: Synthetic exact-tenant IAM, workforce and D22B2 HR entitlement fixtures only; test code proves customer HR entitlement is separate from employer capability and never provisions a production employee or IAM grant.
FINANCIAL AUTHORITY BOUNDARY: No payment, payroll execution, or settlement authority.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
os.environ.setdefault("WILSY_JWT_SECRET", "HIRING-HTTP-REPLICA-SET-CERT-ONLY-SECRET")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

import tools.eos.api.hiring_lifecycle_router as hiring_router
import tools.eos.api.tenant_authorization_http as http_subject
import tools.eos.kernel.db as kernel_db
import tools.eos.saas.auth.auth_registry as auth_registry_module
import tools.eos.saas.tenancy.tenant_registry as tenant_registry_module
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.tenant_authorization import _BINDINGS
import tools.eos.api.headcount_requisition_router as headcount_router
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
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlementState,
    create_tenant_product_entitlement,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
    derive_tenant_product_entitlement_id,
)
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    CURRENT_COLLECTION as PRODUCT_ENTITLEMENT_CURRENT_COLLECTION,
    HISTORY_COLLECTION as PRODUCT_ENTITLEMENT_HISTORY_COLLECTION,
    create_or_replay as create_product_entitlement_or_replay,
    ensure_indexes as ensure_product_entitlement_indexes,
    transition as transition_product_entitlement,
)
from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship, WorkforceRelationshipStatus, WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import workforce_relationship_registry

URI = os.getenv("HIRING_TEST_MONGODB_URI")
NOW = datetime.now(timezone.utc)


def _seed_user(db, principal_id, tenant_id):
    """Create a synthetic authentication fixture in the disposable database."""
    db["users"].insert_one({
        "user_id": principal_id, "email": f"{principal_id}@example.com",
        "firstName": "Hiring", "lastName": "Test", "role": "USER",
        "permissions": [], "tenantId": tenant_id, "passwordHash": "test-only",
        "credential_revision": 0, "mfaRegistered": False, "hasSignedCovenant": False,
    })


def _seed_iam(db, principal_id, tenant_id, business_role, authorization_role):
    """Seed one exact tenant membership and separated business/IAM role fixture."""
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


def _seed_active_workforce(client, db, tenant_id, principal_ids):
    """Append exact-tenant synthetic workforce facts in the disposable database."""
    collection = db[workforce_relationship_registry.COLLECTION_NAME]
    workforce_relationship_registry.ensure_indexes(collection)

    def persist(session):
        for principal_id in principal_ids:
            relationship = WorkforceRelationship(
                relationship_id=f"hiring-http-workforce-{principal_id}",
                revision=1,
                scope_kind=WorkforceScopeKind.TENANT,
                scope_id=tenant_id,
                principal_id=principal_id,
                relationship_type=WorkforceRelationshipType.EMPLOYEE,
                status=WorkforceRelationshipStatus.ACTIVE,
                effective_from=NOW,
                effective_until=None,
                status_effective_at=NOW,
                reason_reference="disposable-hiring-http-test-workforce-currentness",
                supersedes_fingerprint=None,
            )
            workforce_relationship_registry.persist_revision(
                relationship,
                collection=collection,
                session=session,
            )

    with client.start_session() as session:
        session.with_transaction(persist)



def _activate_test_hr_entitlement(client, db, tenant_id):
    """Persist an ACTIVE D22B2 HR entitlement in the disposable database."""
    history = db[PRODUCT_ENTITLEMENT_HISTORY_COLLECTION]
    current = db[PRODUCT_ENTITLEMENT_CURRENT_COLLECTION]
    ensure_product_entitlement_indexes(history, current)
    entitlement_id = derive_tenant_product_entitlement_id(
        tenant_id, TenantProductId.HR,
    )
    pending = create_tenant_product_entitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        product_id=TenantProductId.HR,
        source_evidence_reference="disposable-hiring-http-hr-source",
        source_evidence_fingerprint="a" * 128,
    )
    with client.start_session() as session:
        with session.start_transaction(
            read_concern=ReadConcern("snapshot"),
            write_concern=WriteConcern(w="majority", j=True),
            read_preference=ReadPreference.PRIMARY,
        ):
            create_product_entitlement_or_replay(
                pending, history, current, session=session,
            )
            transition_product_entitlement(
                tenant_id=tenant_id,
                entitlement_id=entitlement_id,
                target_state=TenantProductEntitlementState.ACTIVE,
                expected_revision=0,
                evidence_reference="disposable-hiring-http-hr-activation",
                evidence_fingerprint="b" * 128,
                occurred_at=NOW,
                history_collection=history,
                current_collection=current,
                session=session,
            )

def _token(principal_id, tenant_id):
    """Mint a test-only access token for the synthetic fixture principal."""
    return create_access_token(
        {"identity_id": principal_id, "tenant_id": tenant_id, "roles": [], "permissions": []},
        token_purpose=TokenPurpose.ACCESS, credential_revision=0,
    )


def _headers(principal_id, tenant_id):
    """Bind fixture credentials and explicit tenant transport context."""
    return {"Authorization": f"Bearer {_token(principal_id, tenant_id)}", "X-Tenant-ID": tenant_id}


def test_hiring_routes_keep_exact_employer_pairs_and_no_acceptance_override():
    """Certify employer route wiring independently of Mongo availability."""
    expected = (
        (hiring_router._CANDIDATE_READ, "platform_employer:hiring_candidate:read", "platform_employer_hiring_candidate_read"),
        (hiring_router._CANDIDATE_CREATE, "platform_employer:hiring_candidate:create", "platform_employer_hiring_candidate_create"),
        (hiring_router._CANDIDATE_TRANSITION, "platform_employer:hiring_candidate:transition", "platform_employer_hiring_candidate_transition"),
        (hiring_router._OFFER_READ, "platform_employer:hiring_offer:read", "platform_employer_hiring_offer_read"),
        (hiring_router._OFFER_CREATE, "platform_employer:hiring_offer:create", "platform_employer_hiring_offer_create"),
        (hiring_router._OFFER_SUBMIT, "platform_employer:hiring_offer:submit", "platform_employer_hiring_offer_submit"),
        (hiring_router._OFFER_DECIDE, "platform_employer:hiring_offer:decide", "platform_employer_hiring_offer_decide"),
        (hiring_router._OFFER_SEND, "platform_employer:hiring_offer:send", "platform_employer_hiring_offer_send"),
        (hiring_router._OFFER_SIGN, "platform_employer:hiring_offer:sign", "platform_employer_hiring_offer_sign"),
    )
    for dependency, permission_id, operation in expected:
        assert dependency.platform_employer_permission_id == permission_id
        assert dependency.platform_employer_operation == operation
        assert _BINDINGS[operation] == permission_id
    assert hiring_router._OFFER_ACCEPT.platform_employer_permission_id is None
    assert hiring_router._OFFER_ACCEPT.platform_employer_operation is None


@pytest.mark.skipif(not URI, reason="HIRING_TEST_MONGODB_URI is not configured")
def test_authenticated_hiring_http_uses_durable_iam_and_rejects_wrong_tenant_and_wrong_grant(monkeypatch):
    """Persist a candidate, read exact-tenant pages, and deny a mismatched scope."""
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
        workforce_relationship_registry.ensure_indexes(
            db[workforce_relationship_registry.COLLECTION_NAME]
        )

        tenant, other_tenant, unentitled_tenant = (
            f"tenant-{uuid.uuid4().hex}",
            f"other-{uuid.uuid4().hex}",
            f"unentitled-{uuid.uuid4().hex}",
        )
        manager, mismatch, director, unentitled_manager = (
            f"hr-manager-{uuid.uuid4().hex}", f"hr-mismatch-{uuid.uuid4().hex}",
            f"hr-director-{uuid.uuid4().hex}", f"hr-unentitled-{uuid.uuid4().hex}",
        )
        monkeypatch.setattr(tenant_registry_module, "tenants_collection", db["tenants"])
        TenantRegistry.create({"name": "Hiring HTTP certification", "tenant_id": tenant})
        TenantRegistry.create({"name": "Hiring HTTP other tenant", "tenant_id": other_tenant})
        TenantRegistry.create({"name": "Hiring HTTP unentitled tenant", "tenant_id": unentitled_tenant})
        _seed_user(db, manager, tenant)
        _seed_user(db, mismatch, tenant)
        _seed_user(db, director, tenant)
        _seed_user(db, unentitled_manager, unentitled_tenant)
        _seed_iam(db, manager, tenant, "tenant_hr_manager", "HR_MANAGER")
        _seed_iam(db, mismatch, tenant, "tenant_hr_manager", "HR_DIRECTOR")
        _seed_iam(db, director, tenant, "tenant_hr_director", "HR_DIRECTOR")
        _seed_iam(db, unentitled_manager, unentitled_tenant, "tenant_hr_manager", "HR_MANAGER")
        _seed_active_workforce(client, db, tenant, (manager, mismatch, director))
        _seed_active_workforce(client, db, unentitled_tenant, (unentitled_manager,))
        _activate_test_hr_entitlement(client, db, tenant)

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
        assert AuthRegistry().get_credential_revision(tenant, manager) == 0

        app = FastAPI()
        app.include_router(headcount_router.router, prefix="/api")
        app.include_router(hiring_router.router, prefix="/api")
        register_error_handlers(app, debug=False)
        with TestClient(app, raise_server_exceptions=False) as http:
            unentitled = http.get(
                "/api/hr/hiring/candidates",
                headers=_headers(unentitled_manager, unentitled_tenant),
            )
            assert unentitled.status_code == 403, unentitled.text
            assert unentitled.json()["error_code"] == "FORBIDDEN"
            assert unentitled.json()["http_status"] == 403

            draft_response = http.post(
                "/api/hr/headcount-requisitions",
                headers={**_headers(manager, tenant), "Idempotency-Key": "http-headcount-1"},
                json={
                    "department_id": "engineering", "position_title": "Platform Engineer",
                    "employment_type": "FULL_TIME", "work_location": "Remote", "headcount": 1,
                    "business_justification": "Disposable approved requisition for hiring route certification",
                },
            )
            assert draft_response.status_code == 201, draft_response.text
            requisition_id = draft_response.json()["requisition_id"]
            unapproved = http.post(
                "/api/hr/hiring/candidates",
                headers={**_headers(manager, tenant), "Idempotency-Key": "http-candidate-unapproved"},
                json={
                    "candidate_id": "CAN-HTTP-UNAPPROVED", "requisition_id": requisition_id,
                    "candidate_profile_reference": "candidate-profile://opaque/unapproved",
                    "source": "CAREERS_PORTAL",
                },
            )
            assert unapproved.status_code == 409, unapproved.text
            assert unapproved.json()["detail"] == "HIRING_APPROVED_REQUISITION_REQUIRED"

            submitted = http.post(
                f"/api/hr/headcount-requisitions/{requisition_id}/submit",
                headers={**_headers(manager, tenant), "Idempotency-Key": "http-headcount-submit-1"},
                json={"expected_revision": 1},
            )
            assert submitted.status_code == 200, submitted.text
            approved = http.post(
                f"/api/hr/headcount-requisitions/{requisition_id}/decision",
                headers={**_headers(director, tenant), "Idempotency-Key": "http-headcount-approve-1"},
                json={"expected_revision": 2, "decision": "APPROVE", "reason": "Independent disposable certification approval"},
            )
            assert approved.status_code == 200, approved.text
            assert approved.json()["status"] == "APPROVED"

            allowed = http.post(
                "/api/hr/hiring/candidates",
                headers={**_headers(manager, tenant), "Idempotency-Key": "http-candidate-1"},
                json={
                    "candidate_id": "CAN-HTTP-1", "requisition_id": requisition_id,
                    "candidate_profile_reference": "candidate-profile://opaque/http-1",
                    "source": "CAREERS_PORTAL",
                },
            )
            assert allowed.status_code == 201, allowed.text
            assert allowed.json()["tenant_id"] == tenant
            assert allowed.json()["requisition_id"] == requisition_id

            candidate_page = http.get(
                "/api/hr/hiring/candidates?limit=1&offset=0",
                headers=_headers(manager, tenant),
            )
            assert candidate_page.status_code == 200, candidate_page.text
            candidate_payload = candidate_page.json()
            assert candidate_payload["items"][0]["candidate_id"] == "CAN-HTTP-1"
            assert candidate_payload["total"] == 1
            assert candidate_payload["limit"] == 1
            assert candidate_payload["offset"] == 0
            assert candidate_payload["hasMore"] is False

            empty_offer_page = http.get(
                "/api/hr/hiring/offers?limit=5&offset=0",
                headers=_headers(manager, tenant),
            )
            assert empty_offer_page.status_code == 200, empty_offer_page.text
            assert empty_offer_page.json() == {
                "items": [], "total": 0, "limit": 5,
                "offset": 0, "hasMore": False,
            }

            offers_before_acceptance = db["wilsy_hr_employment_offers"].count_documents(
                {"tenant_id": tenant},
            )
            events_before_acceptance = db["wilsy_hr_hiring_lifecycle_events"].count_documents(
                {"tenant_id": tenant},
            )
            acceptance_disabled = http.post(
                "/api/hr/hiring/offers/OFFER-IDENTITY-PENDING/accept",
                headers={**_headers(director, tenant), "Idempotency-Key": "http-accept-identity-pending"},
                json={
                    "expected_revision": 1,
                    "evidence_reference": "EVD-IDENTITY-PENDING",
                    "evidence_fingerprint": "a" * 128,
                    "evidence_version_id": "VER-IDENTITY-PENDING",
                    "accepted_at": NOW.isoformat(),
                    "signer_certificate_pem_base64": "Y2VydA==",
                    "intermediate_certificate_pems_base64": ["aW50ZXJtZWRpYXRl"],
                    "detached_signature_base64": "c2ln",
                },
            )
            assert acceptance_disabled.status_code == 503, acceptance_disabled.text
            assert acceptance_disabled.json()["detail"] == "CANDIDATE_IDENTITY_BINDING_UNAVAILABLE"
            assert db["wilsy_hr_employment_offers"].count_documents(
                {"tenant_id": tenant},
            ) == offers_before_acceptance
            assert db["wilsy_hr_hiring_lifecycle_events"].count_documents(
                {"tenant_id": tenant},
            ) == events_before_acceptance

            invalid_page = http.get(
                "/api/hr/hiring/candidates?limit=101&offset=0",
                headers=_headers(manager, tenant),
            )
            assert invalid_page.status_code == 422

            wrong_tenant_page = http.get(
                "/api/hr/hiring/candidates?limit=1&offset=0",
                headers={"Authorization": f"Bearer {_token(manager, tenant)}", "X-Tenant-ID": other_tenant},
            )
            assert wrong_tenant_page.status_code == 403

            wrong_tenant = http.post(
                "/api/hr/hiring/candidates",
                headers={"Authorization": f"Bearer {_token(manager, tenant)}", "X-Tenant-ID": other_tenant, "Idempotency-Key": "http-candidate-wrong-tenant"},
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


# ARTIFACT: tests/integration/test_hiring_lifecycle_authenticated_real_http.py
# VERSION: v1.6.0-STRUCTURED-HR-DENIAL-CERT
# AUTHORITY BOUNDARY: Customer HTTP cases use durable synthetic active D22B2 HR entitlement plus exact IAM; platform-employer route contracts remain separately pinned.
# TENANT POSTURE: UUID-isolated replica-set database; mismatched scopes deny.
# FAIL-CLOSED POSTURE: Readback, authorization, or cleanup failures fail the test.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
