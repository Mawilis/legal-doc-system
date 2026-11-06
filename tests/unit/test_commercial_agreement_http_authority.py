import inspect

import pytest
from pydantic import ValidationError

from tools.eos.api import server
from tools.eos.api.commercial_agreement_router import (
    _ACTIVATE, _DRAFT_CREATE, _EXECUTE, _READ,
    CommercialAgreementExecutionRequest, router,
)
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)


def test_commercial_agreement_routes_are_mounted_once_with_separate_authority_gates():
    routes = {
        (route.path, tuple(sorted(route.methods or ())))
        for route in router.routes
    }
    assert ("/commercial/agreements", ("POST",)) in routes
    assert ("/commercial/agreements/{agreement_id}", ("GET",)) in routes
    assert ("/commercial/agreements/{agreement_id}/history", ("GET",)) in routes
    assert ("/commercial/agreements/{agreement_id}/execute", ("POST",)) in routes
    assert ("/commercial/agreements/{agreement_id}/activate", ("POST",)) in routes
    assert ("/commercial/agreements/{agreement_id}/entitlements", ("GET",)) in routes
    source = inspect.getsource(server)
    assert source.count('app.include_router(commercial_agreement_router, prefix="/api")') == 1
    assert "from .commercial_agreement_router import router as commercial_agreement_router" in source


def test_route_dependencies_use_distinct_exact_permission_operation_pairs():
    assert (_READ.permission_id, _READ.operation) == (
        "tenant:commercial_agreement:read",
        "commercial_agreement_read",
    )
    assert (_DRAFT_CREATE.permission_id, _DRAFT_CREATE.operation) == (
        "tenant:commercial_agreement:draft:create",
        "commercial_agreement_draft_create",
    )
    assert (_EXECUTE.permission_id, _EXECUTE.operation) == (
        "tenant:commercial_agreement:execute", "commercial_agreement_execute"
    )
    assert (_ACTIVATE.permission_id, _ACTIVATE.operation) == (
        "tenant:commercial_agreement:activate", "commercial_agreement_activate"
    )


def test_permission_metadata_is_tenant_scoped_and_never_financial():
    read = permission_metadata("tenant:commercial_agreement:read")
    create = permission_metadata("tenant:commercial_agreement:draft:create")
    execute = permission_metadata("tenant:commercial_agreement:execute")
    activate = permission_metadata("tenant:commercial_agreement:activate")
    for item in (read, create, execute, activate):
        assert item.namespace == "TENANT"
        assert item.tenant_membership_required is True
        assert item.cross_tenant_capable is False
        assert item.financial_execution_capable is False
        assert item.authorizes_by_itself is False


def test_owner_admin_auditor_and_specialist_business_role_boundaries():
    assert permission_for_business_role_operation("commercial_agreement_read") == (
        "tenant:commercial_agreement:read"
    )
    assert permission_for_business_role_operation("commercial_agreement_draft_create") == (
        "tenant:commercial_agreement:draft:create"
    )
    assert permission_for_business_role_operation("commercial_agreement_execute") == (
        "tenant:commercial_agreement:execute"
    )
    assert permission_for_business_role_operation("commercial_agreement_activate") == (
        "tenant:commercial_agreement:activate"
    )
    assert tenant_role_operation_eligibility("tenant_owner", "commercial_agreement_read") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_owner", "commercial_agreement_draft_create") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_admin", "commercial_agreement_draft_create") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_owner", "commercial_agreement_execute") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_owner", "commercial_agreement_activate") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_admin", "commercial_agreement_execute") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_admin", "commercial_agreement_activate") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_auditor", "commercial_agreement_read") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_auditor", "commercial_agreement_draft_create") == DENY
    assert tenant_role_operation_eligibility("tenant_legal_partner", "commercial_agreement_read") == DENY
    assert tenant_role_operation_eligibility("tenant_legal_partner", "commercial_agreement_execute") == DENY
    assert tenant_role_operation_eligibility("tenant_legal_partner", "commercial_agreement_activate") == DENY
    assert "tenant:commercial_agreement:read" in ROLE_PERMISSIONS_MAP["TENANT_OWNER"]
    assert "tenant:commercial_agreement:draft:create" in ROLE_PERMISSIONS_MAP["TENANT_OWNER"]
    assert "tenant:commercial_agreement:read" in ROLE_PERMISSIONS_MAP["AUDITOR"]
    assert "tenant:commercial_agreement:draft:create" not in ROLE_PERMISSIONS_MAP["AUDITOR"]
    for role in ("TENANT_OWNER", "ENTERPRISE_ADMIN"):
        assert "tenant:commercial_agreement:execute" in ROLE_PERMISSIONS_MAP[role]
        assert "tenant:commercial_agreement:activate" in ROLE_PERMISSIONS_MAP[role]
    assert "tenant:commercial_agreement:execute" not in ROLE_PERMISSIONS_MAP["LEGAL_PARTNER"]
    assert "tenant:commercial_agreement:activate" not in ROLE_PERMISSIONS_MAP["LEGAL_PARTNER"]



def test_execution_request_accepts_only_server_evidence_reference():
    request = CommercialAgreementExecutionRequest(
        execution_evidence_reference="evidence:trusted-provider:123"
    )
    assert request.execution_evidence_reference == "evidence:trusted-provider:123"
    with pytest.raises(ValidationError):
        CommercialAgreementExecutionRequest.model_validate({
            "execution_evidence_reference": "evidence:trusted-provider:123",
            "signature": "browser-supplied-signature",
            "certificate_pem": "browser-supplied-certificate",
            "signatory_principal_id": "browser-supplied-principal",
        })
