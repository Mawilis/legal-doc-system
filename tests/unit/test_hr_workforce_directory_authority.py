from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    tenant_role_operation_eligibility,
)
from tools.eos.auth.tenant_authorization import _BINDINGS


PERMISSION = "hr:employee_directory:read"
OPERATION = "hr_employee_directory_read"
APPROVED_ROLES = {
    "tenant_hr_director",
    "tenant_hr_manager",
    "tenant_employee_relations_director",
    "tenant_employee_relations_manager",
    "tenant_employee_relations_specialist",
}


def test_directory_permission_is_canonical_own_tenant_workforce_read() -> None:
    metadata = permission_metadata(PERMISSION)
    assert metadata.disposition.value == "CANONICAL"
    assert metadata.namespace == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.workforce_currentness_required is True
    assert _BINDINGS[OPERATION] == PERMISSION


def test_directory_read_is_eligible_only_for_formal_hr_roles() -> None:
    for role in APPROVED_ROLES:
        assert tenant_role_operation_eligibility(role, OPERATION) == ELIGIBLE
        assert PERMISSION in ROLE_PERMISSIONS_MAP[{
            "tenant_hr_director": "HR_DIRECTOR",
            "tenant_hr_manager": "HR_MANAGER",
            "tenant_employee_relations_director": "EMPLOYEE_RELATIONS_DIRECTOR",
            "tenant_employee_relations_manager": "EMPLOYEE_RELATIONS_MANAGER",
            "tenant_employee_relations_specialist": "EMPLOYEE_RELATIONS_SPECIALIST",
        }[role]]


def test_directory_read_denies_owner_legal_and_unknown_roles() -> None:
    for role in (
        "tenant_owner",
        "tenant_admin",
        "tenant_manager",
        "tenant_auditor",
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "unknown_role",
    ):
        assert tenant_role_operation_eligibility(role, OPERATION) == DENY
