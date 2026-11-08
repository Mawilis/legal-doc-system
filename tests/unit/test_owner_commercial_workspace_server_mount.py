import inspect
from pathlib import Path

from tools.eos.api import server
from tools.eos.api.owner_commercial_workspace_router import (
    _COMPLETE, _CREATE, _READ, router,
)


ROOT = Path(__file__).resolve().parents[2]


def test_owner_commercial_workspace_routes_are_mounted_once_and_directly():
    routes = {
        (route.path, tuple(sorted(route.methods or ())))
        for route in router.routes
    }
    assert ("/crm/owner-workspace", ("GET",)) in routes
    assert ("/crm/owner-workspace/work-items", ("POST",)) in routes
    assert ("/crm/owner-workspace/work-items/{work_item_id}/complete", ("POST",)) in routes
    source = inspect.getsource(server)
    assert source.count(
        "app.include_router(owner_commercial_workspace_router, prefix=\"/api\")"
    ) == 1
    assert "from .owner_commercial_workspace_router import router as owner_commercial_workspace_router" in source

    vite = (ROOT / "client/vite.config.js").read_text(encoding="utf-8")
    assert "'/api/crm/owner-workspace': {" in vite
    assert "http://localhost:9095" in vite
    assert not (ROOT / "server/server.js").exists()


def test_each_owner_workspace_command_has_its_exact_permission_binding():
    assert (_READ.permission_id, _READ.operation) == ("crm:work_item:read", "crm_work_item_read")
    assert (_CREATE.permission_id, _CREATE.operation) == ("crm:work_item:create", "crm_work_item_create")
    assert (_COMPLETE.permission_id, _COMPLETE.operation) == ("crm:work_item:complete", "crm_work_item_complete")
