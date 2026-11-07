from tools.eos.api import server
from tools.eos.api.headcount_requisition_router import (
    _CREATE, _DECIDE, _READ, router,
)
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP
from tools.eos.auth.tenant_authorization import _BINDINGS


def test_authenticated_headcount_routes_are_mounted_once():
    routes = {
        (route.path, tuple(sorted(route.methods or ())))
        for route in router.routes
    }
    assert ("/hr/headcount-requisitions", ("GET",)) in routes
    assert ("/hr/headcount-requisitions", ("POST",)) in routes
    assert ("/hr/headcount-requisitions/{requisition_id}/submit", ("POST",)) in routes
    assert ("/hr/headcount-requisitions/{requisition_id}/decision", ("POST",)) in routes
    source = __import__("inspect").getsource(server)
    assert source.count(
        'app.include_router(headcount_requisition_router, prefix="/api")'
    ) == 1


def test_each_command_has_exact_nonfinancial_workforce_iam_binding():
    expected = {
        "hr_headcount_requisition_read": "hr:headcount_requisition:read",
        "hr_headcount_requisition_create": "hr:headcount_requisition:create",
        "hr_headcount_requisition_decide": "hr:headcount_requisition:decide",
    }
    assert _BINDINGS["hr_headcount_requisition_read"] == expected["hr_headcount_requisition_read"]
    assert _BINDINGS["hr_headcount_requisition_create"] == expected["hr_headcount_requisition_create"]
    assert _BINDINGS["hr_headcount_requisition_decide"] == expected["hr_headcount_requisition_decide"]
    for permission_id in expected.values():
        metadata = permission_metadata(permission_id)
        assert metadata.tenant_membership_required is True
        assert metadata.workforce_currentness_required is True
        assert metadata.cross_tenant_capable is False
        assert metadata.financial_execution_capable is False
        assert metadata.authorizes_by_itself is False


def test_headcount_maker_and_checker_roles_are_separate():
    assert "hr:headcount_requisition:create" in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
    assert "hr:headcount_requisition:decide" not in ROLE_PERMISSIONS_MAP["HR_MANAGER"]
    assert "hr:headcount_requisition:decide" in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]
    assert "hr:headcount_requisition:create" not in ROLE_PERMISSIONS_MAP["HR_DIRECTOR"]
