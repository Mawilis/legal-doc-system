from pathlib import Path

from tools.eos.api.owner_commercial_workspace_router import (
    _COMPLETE, _CREATE, _READ, router,
)
from tools.eos.api import server


def test_owner_commercial_workspace_routes_are_mounted_once():
    routes = {
        (route.path, tuple(sorted(route.methods or ())))
        for route in router.routes
    }
    assert ("/crm/owner-workspace", ("GET",)) in routes
    assert ("/crm/owner-workspace/work-items", ("POST",)) in routes
    assert ("/crm/owner-workspace/work-items/{work_item_id}/complete", ("POST",)) in routes
    app_routes = [
        route for route in server.app.routes
        if getattr(route, "path", "").startswith("/api/crm/owner-workspace")
    ]
    assert len(app_routes) == 3


def test_each_owner_workspace_command_has_its_exact_permission_binding():
    assert (_READ.permission_id, _READ.operation) == ("crm:work_item:read", "crm_work_item_read")
    assert (_CREATE.permission_id, _CREATE.operation) == ("crm:work_item:create", "crm_work_item_create")
    assert (_COMPLETE.permission_id, _COMPLETE.operation) == ("crm:work_item:complete", "crm_work_item_complete")
