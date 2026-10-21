"""Exact canonical partner-only practitioner binding provisioning IAM."""
import tools.eos.auth.tenant_authorization as composer
from tools.eos.auth.permission_namespace import (
    PermissionDisposition, permission_metadata,
)
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    DENY, ELIGIBLE, TENANT_ROLES, OPERATIONS,
    tenant_role_operation_eligibility,
)

P = "legal_operations:practitioner_matter_binding:provision"
O = "legal_practitioner_matter_binding_provision"

def test_exact_canonical_tenant_permission():
    item = permission_metadata(P)
    assert item.disposition is PermissionDisposition.CANONICAL
    assert item.namespace == "TENANT"
    assert item.tenant_membership_required is True
    assert item.cross_tenant_capable is False
    assert item.financial_execution_capable is False

def test_authorization_role_partner_only():
    assert get_roles_granting_permission(P) == ("LEGAL_PARTNER",)

def test_business_eligibility_partner_only():
    assert O in OPERATIONS
    for role in TENANT_ROLES:
        expected = ELIGIBLE if role == "tenant_legal_partner" else DENY
        assert tenant_role_operation_eligibility(role, O) == expected

def test_exact_operation_permission_composition():
    assert composer._BINDINGS.get(O) == P
    assert composer._BINDINGS.get(
        "legal_practitioner_matter_access_policy_issue"
    ) == "legal_operations:practitioner_matter_access_policy:issue"

def test_aliases_not_authorized():
    for alias in (
        "legal_practitioner_matter_binding_grant",
        "legal_practitioner_matter_binding_revoke",
        "legal_practitioner_matter_binding_write",
        O + " ",
    ):
        assert alias not in composer._BINDINGS
        assert tenant_role_operation_eligibility(
            "tenant_legal_partner",alias
        ) == DENY

def test_no_content_or_wall_clearance_authority():
    assert P != "legal_operations:matter_deadline:read"
    assert P != "legal_operations:practitioner_matter_access_policy:issue"
    assert "wall" not in P and "content" not in P

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P4-R3B-P1B-R1
# END OF WILSY OS SOVEREIGN ARTIFACT
