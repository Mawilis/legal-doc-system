"""Authenticated hiring route and canonical IAM contract checks."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api.errors import register_error_handlers
from tools.eos.api.hiring_lifecycle_router import router
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import get_roles_granting_permission


def _app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(router, prefix="/api")
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
