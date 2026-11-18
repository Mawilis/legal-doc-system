"""TITLE: WILSY workforce directory authority contract certification.
VERSION: v1.1.1-PLATFORM-EMPLOYER-DIRECTORY-SCOPE-CERT
AUTHORITY: Repository regression certificate for directory read permissions and route composition.
EPITOME: Pins customer HR workforce-currentness and the canonical WILSY
         platform-employer directory read pair without granting mutation rights.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hr_workforce_directory_authority.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering; certifies hr_workforce_directory_router.py and existing EOS permission governance.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG:
  v1.1.1-PLATFORM-EMPLOYER-DIRECTORY-SCOPE-CERT — Corrects the release marker so the header, current changelog and end seal agree exactly; behavioral assertions are unchanged.
  v1.1.0-PLATFORM-EMPLOYER-DIRECTORY-SCOPE-CERT — Verifies the exact-WILSY alternate pair and its least-privilege role eligibility while preserving customer HR currentness checks.
  v1.0.0-HR-WORKFORCE-DIRECTORY-CERT — Certifies canonical customer HR directory permission and role boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Static policy assertions only; no employee, principal, membership, entitlement, role assignment, or directory record is created.
TENANT BOUNDARY: Customer directory permission is tenant-scoped; platform-employer pair is selected only for canonical WILSY by the shared authorization dependency.
AUTHORITY BOUNDARY: Permission metadata and business-role eligibility are necessary policy facts, not self-authorizing grants. Exact membership and assigned IAM remain required.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution, settlement, or entitlement authority.
"""

from tools.eos.api.hr_workforce_directory_router import _DIRECTORY_AUTHORITY
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
PLATFORM_PERMISSION = "platform_employer:employee_directory:read"
PLATFORM_OPERATION = "platform_employer_employee_directory_read"
APPROVED_ROLES = {
    "tenant_hr_director",
    "tenant_hr_manager",
    "tenant_employee_relations_director",
    "tenant_employee_relations_manager",
    "tenant_employee_relations_specialist",
}


def test_directory_permission_is_canonical_own_tenant_workforce_read() -> None:
    """Customer HR directory access retains its existing workforce currentness gate."""
    metadata = permission_metadata(PERMISSION)
    assert metadata.disposition.value == "CANONICAL"
    assert metadata.namespace == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.workforce_currentness_required is True
    assert metadata.authorizes_by_itself is False
    assert _BINDINGS[OPERATION] == PERMISSION


def test_directory_route_pairs_customer_and_exact_wilsy_employer_authority() -> None:
    """The single read route keeps customer HR and WILSY employer authority separate."""
    assert (_DIRECTORY_AUTHORITY.permission_id, _DIRECTORY_AUTHORITY.operation) == (
        PERMISSION,
        OPERATION,
    )
    assert (
        _DIRECTORY_AUTHORITY.platform_employer_permission_id,
        _DIRECTORY_AUTHORITY.platform_employer_operation,
    ) == (PLATFORM_PERMISSION, PLATFORM_OPERATION)
    metadata = permission_metadata(PLATFORM_PERMISSION)
    assert metadata.disposition.value == "CANONICAL"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert _BINDINGS[PLATFORM_OPERATION] == PLATFORM_PERMISSION
    assert PLATFORM_PERMISSION in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
    assert PLATFORM_PERMISSION in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]


def test_customer_directory_read_is_eligible_only_for_formal_hr_roles() -> None:
    """Customer HR eligibility remains limited to existing formal HR roles."""
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
    """Customer HR directory access does not derive from owner or legal roles."""
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


def test_platform_employer_directory_is_limited_to_existing_hr_manager_roles() -> None:
    """Employer eligibility remains role-governed and excludes implicit founder access."""
    assert tenant_role_operation_eligibility(
        "tenant_hr_manager", PLATFORM_OPERATION,
    ) == ELIGIBLE
    assert tenant_role_operation_eligibility(
        "tenant_hr_director", PLATFORM_OPERATION,
    ) == ELIGIBLE
    for role in (
        "tenant_owner",
        "tenant_admin",
        "tenant_manager",
        "tenant_auditor",
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "unknown_role",
    ):
        assert tenant_role_operation_eligibility(role, PLATFORM_OPERATION) == DENY


# ARTIFACT: test_hr_workforce_directory_authority.py
# VERSION: v1.1.1-PLATFORM-EMPLOYER-DIRECTORY-SCOPE-CERT
# AUTHORITY BOUNDARY: Static permission metadata, route-pair and role-eligibility evidence only; this certificate grants no runtime capability.
# TENANT POSTURE: Customer HR and platform-employer directory reads are distinct exact-tenant authorization pairs.
# FAIL-CLOSED POSTURE: Any missing route pair, broad role eligibility, or customer currentness regression fails certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
