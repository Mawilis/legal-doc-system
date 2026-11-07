"""Authenticated hiring route and canonical IAM contract checks."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api.errors import register_error_handlers
from tools.eos.api.hiring_lifecycle_router import router
from tools.eos.api.institutional_signer_router import router as institutional_signer_router
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import ELIGIBLE, OPERATIONS, tenant_role_operation_eligibility


def _app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(router, prefix="/api")
    app.include_router(institutional_signer_router, prefix="/api")
    return app


def test_hiring_commands_require_authenticated_identity_and_tenant_scope():
    with TestClient(_app()) as client:
        response = client.post(
            "/api/hr/hiring/candidates",
            headers={"X-Tenant-ID": "WILSYTENANT-4CD2FZ4O", "Idempotency-Key": "candidate-1"},
            json={
                "candidate_id": "CAN-1", "requisition_id": "REQ-1",
                "candidate_profile_reference": "candidate-profile://opaque/1",
                "source": "CAREERS_PORTAL",
            },
        )
    assert response.status_code == 401


def test_hiring_permissions_are_canonical_tenant_scoped_and_non_self_authorizing():
    permissions = (
        "hr:hiring_candidate:read", "hr:hiring_candidate:create",
        "hr:hiring_candidate:transition", "hr:hiring_offer:read",
        "hr:hiring_offer:create", "hr:hiring_offer:submit",
        "hr:hiring_offer:decide", "hr:hiring_offer:send", "hr:hiring_offer:accept",
    )
    for permission in permissions:
        metadata = permission_metadata(permission)
        assert metadata.namespace == "TENANT"
        assert metadata.tenant_membership_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False

    assert "HR_MANAGER" in get_roles_granting_permission("hr:hiring_offer:create")
    assert "HR_MANAGER" in get_roles_granting_permission("hr:hiring_offer:submit")
    assert "HR_DIRECTOR" in get_roles_granting_permission("hr:hiring_offer:decide")
    assert "HR_MANAGER" not in get_roles_granting_permission("hr:hiring_offer:decide")
    assert "HR_DIRECTOR" not in get_roles_granting_permission("hr:hiring_offer:create")


def test_hiring_routes_do_not_accept_tenant_identity_or_permission_from_body():
    from tools.eos.api.hiring_lifecycle_router import CandidateCreate, OfferCreate
    assert "tenant_id" not in CandidateCreate.model_fields
    assert "principal_id" not in CandidateCreate.model_fields
    assert "permissions" not in CandidateCreate.model_fields
    assert "tenant_id" not in OfferCreate.model_fields
    assert "principal_id" not in OfferCreate.model_fields
    assert "permissions" not in OfferCreate.model_fields

def test_hiring_operations_are_known_and_business_role_eligibility_is_separate_from_iam():
    manager = {
        "hr_hiring_candidate_read", "hr_hiring_candidate_create",
        "hr_hiring_candidate_transition", "hr_hiring_offer_read",
        "hr_hiring_offer_create", "hr_hiring_offer_submit", "hr_hiring_offer_send",
    }
    director = {
        "hr_hiring_candidate_read", "hr_hiring_offer_read",
        "hr_hiring_offer_decide", "hr_hiring_offer_accept",
    }
    assert manager | director <= OPERATIONS
    for operation in manager:
        assert tenant_role_operation_eligibility("tenant_hr_manager", operation) == ELIGIBLE
    for operation in director:
        assert tenant_role_operation_eligibility("tenant_hr_director", operation) == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_hr_manager", "hr_hiring_offer_decide") != ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_hr_director", "hr_hiring_offer_create") != ELIGIBLE



def test_institutional_signer_governance_routes_require_authenticated_owner_context():
    with TestClient(_app()) as client:
        response = client.post(
            "/api/security/institutional-signers/enrollments",
            headers={"X-Tenant-ID": "WILSYTENANT-4CD2FZ4O", "Idempotency-Key": "signer-enroll-unauth"},
            json={
                "signer_certificate_pem_base64": "Y2VydA==",
                "intermediate_certificate_pems_base64": ["aW50ZXJtZWRpYXRl"],
                "identity_proofing_evidence_reference": "proofing://opaque/1",
                "signatory_mandate_evidence_reference": "mandate://opaque/1",
            },
        )
    assert response.status_code == 401
