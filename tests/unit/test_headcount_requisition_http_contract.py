"""TITLE: WILSY headcount HTTP authority contract certification.
VERSION: v1.2.1-PLATFORM-EMPLOYER-SCOPE-CERT
AUTHORITY: Repository-owned regression certificate for Python EOS route composition.
EPITOME: Pins mounted route shape, customer HR and exact-WILSY employer IAM pairs,
         least-privilege grants, and the independent headcount maker/checker split.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_headcount_requisition_http_contract.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering; certifies headcount_requisition_router.py and existing shared authorization composition.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG:
  v1.2.1-PLATFORM-EMPLOYER-SCOPE-CERT — Corrects the release marker so the header, current changelog and end seal agree exactly; behavioral assertions are unchanged.
  v1.2.0-PLATFORM-EMPLOYER-SCOPE-CERT — Verifies exact employer and customer permission pairs are bound to the same headcount routes without changing command semantics.
  v1.1.0-HEADCOUNT-DECISION-ID-FIX-CERT — Certifies decision identifier and maker/checker route contract.
  v1.0.0-HEADCOUNT-HTTP-CERT — Pins authenticated headcount route mount and customer IAM binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: These tests assert policy wiring only; they create no principal, role assignment, membership, employee, entitlement, or business record.
TENANT BOUNDARY: Employer alternates are selected only by the shared adapter for canonical WILSY; customer HR permissions remain exact-tenant scoped and product-gated.
AUTHORITY BOUNDARY: Permission metadata and role eligibility do not self-authorize. Durable exact-tenant membership and assignment resolution remain required. Offer acceptance and employee admission remain outside this route contract.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution, settlement, or commercial entitlement grant.
"""

from tools.eos.api import server
from tools.eos.api.headcount_requisition_router import (
    _CREATE,
    _DECIDE,
    _READ,
    router,
)
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authorization import _BINDINGS


def test_authenticated_headcount_routes_are_mounted_once() -> None:
    """Keep all command routes mounted once beneath the canonical API prefix."""
    routes = {
        (route.path, tuple(sorted(route.methods or ())))
        for route in router.routes
    }
    assert ("/hr/headcount-requisitions", ("GET",)) in routes
    assert ("/hr/headcount-requisitions", ("POST",)) in routes
    assert (
        "/hr/headcount-requisitions/{requisition_id}/submit",
        ("POST",),
    ) in routes
    assert (
        "/hr/headcount-requisitions/{requisition_id}/decision",
        ("POST",),
    ) in routes
    source = __import__("inspect").getsource(server)
    assert source.count(
        'app.include_router(headcount_requisition_router, prefix="/api")'
    ) == 1


def test_customer_and_platform_employer_pairs_are_exact_and_nonfinancial() -> None:
    """Pin the paired route dependencies without creating cross-scope authority."""
    expected = {
        "read": (
            _READ,
            "hr:headcount_requisition:read",
            "hr_headcount_requisition_read",
            "platform_employer:headcount_requisition:read",
            "platform_employer_headcount_requisition_read",
        ),
        "create": (
            _CREATE,
            "hr:headcount_requisition:create",
            "hr_headcount_requisition_create",
            "platform_employer:headcount_requisition:create",
            "platform_employer_headcount_requisition_create",
        ),
        "decide": (
            _DECIDE,
            "hr:headcount_requisition:decide",
            "hr_headcount_requisition_decide",
            "platform_employer:headcount_requisition:decide",
            "platform_employer_headcount_requisition_decide",
        ),
    }
    for dependency, customer_permission, customer_operation, employer_permission, employer_operation in expected.values():
        assert dependency.permission_id == customer_permission
        assert dependency.operation == customer_operation
        assert _BINDINGS[customer_operation] == customer_permission
        assert dependency.platform_employer_permission_id == employer_permission
        assert dependency.platform_employer_operation == employer_operation
        assert _BINDINGS[employer_operation] == employer_permission
        for permission_id in (customer_permission, employer_permission):
            metadata = permission_metadata(permission_id)
            assert metadata.tenant_membership_required is True
            assert metadata.cross_tenant_capable is False
            assert metadata.financial_execution_capable is False
            assert metadata.authorizes_by_itself is False
    for permission_id in (
        "hr:headcount_requisition:read",
        "hr:headcount_requisition:create",
        "hr:headcount_requisition:decide",
    ):
        assert permission_metadata(permission_id).workforce_currentness_required is True


def test_headcount_maker_and_checker_roles_are_separate() -> None:
    """Keep customer HR and employer capability grants on the existing roles."""
    for permission in (
        "hr:headcount_requisition:create",
        "platform_employer:headcount_requisition:create",
    ):
        assert permission in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
        assert permission not in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]
    for permission in (
        "hr:headcount_requisition:decide",
        "platform_employer:headcount_requisition:decide",
    ):
        assert permission in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]
        assert permission not in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
    for permission in (
        "hr:headcount_requisition:read",
        "platform_employer:headcount_requisition:read",
    ):
        assert permission in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
        assert permission in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]


# ARTIFACT: test_headcount_requisition_http_contract.py
# VERSION: v1.2.1-PLATFORM-EMPLOYER-SCOPE-CERT
# AUTHORITY BOUNDARY: Regression evidence for existing EOS permission metadata, static grants, exact route pairs, and mounted surface only; it grants no runtime authority.
# TENANT POSTURE: Customer permissions are tenant-scoped; platform-employer pairs are canonical-WILSY-only through the shared authorization adapter.
# FAIL-CLOSED POSTURE: Route wiring, role-grant, binding, or scope-contract drift fails this certificate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
