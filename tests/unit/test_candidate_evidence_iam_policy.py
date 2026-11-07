from tools.eos.auth.tenant_authority_policy import (
    ELIGIBLE, DENY, BUSINESS_ROLE_OPERATION_PERMISSIONS,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authorization import _BINDINGS


def test_candidate_evidence_upload_and_read_are_distinct_canonical_operations():
    assert BUSINESS_ROLE_OPERATION_PERMISSIONS["hr_hiring_candidate_evidence_upload"] == "hr:hiring_candidate_evidence:upload"
    assert BUSINESS_ROLE_OPERATION_PERMISSIONS["hr_hiring_candidate_evidence_read"] == "hr:hiring_candidate_evidence:read"
    assert permission_metadata("hr:hiring_candidate_evidence:upload").tenant_membership_required is True
    assert permission_metadata("hr:hiring_candidate_evidence:read").tenant_membership_required is True
    for permission in ("hr:hiring_candidate_evidence:upload", "hr:hiring_candidate_evidence:read"):
        metadata = permission_metadata(permission)
        assert metadata.namespace == "TENANT"
        assert metadata.scope_kind == "TENANT"
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False


def test_candidate_evidence_business_eligibility_is_least_privilege():
    assert tenant_role_operation_eligibility("tenant_hr_manager", "hr_hiring_candidate_evidence_upload") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_hr_manager", "hr_hiring_candidate_evidence_read") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_hr_director", "hr_hiring_candidate_evidence_upload") == DENY
    assert tenant_role_operation_eligibility("tenant_hr_director", "hr_hiring_candidate_evidence_read") == ELIGIBLE
    assert tenant_role_operation_eligibility("tenant_owner", "hr_hiring_candidate_evidence_upload") == DENY
    assert tenant_role_operation_eligibility("tenant_legal_partner", "hr_hiring_candidate_evidence_read") == DENY



def test_candidate_evidence_static_role_grants_match_business_eligibility():
    assert "hr:hiring_candidate_evidence:upload" in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
    assert "hr:hiring_candidate_evidence:read" in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
    assert "hr:hiring_candidate_evidence:read" in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]
    assert "hr:hiring_candidate_evidence:upload" not in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]
    assert "hr:hiring_candidate_evidence:upload" not in ROLE_PERMISSIONS_MAP["TENANT_OWNER"]
    assert "hr:hiring_candidate_evidence:read" not in ROLE_PERMISSIONS_MAP["LEGAL_PARTNER"]



def test_candidate_evidence_operations_bind_exactly_to_canonical_permissions():
    assert _BINDINGS["hr_hiring_candidate_evidence_upload"] == "hr:hiring_candidate_evidence:upload"
    assert _BINDINGS["hr_hiring_candidate_evidence_read"] == "hr:hiring_candidate_evidence:read"
