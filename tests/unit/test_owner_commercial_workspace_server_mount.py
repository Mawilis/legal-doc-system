"""WILSY OS owner commercial workspace composition certificate.

TITLE: Owner Commercial Workspace Route Mount and EOS Transport Certificate
VERSION: v1.1.0-TYPED-ROUTE-INSPECTION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verifies exact owner-workspace route composition, permission bindings,
    and the canonical Vite-to-Python EOS loopback target.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_owner_commercial_workspace_server_mount.py
COLLABORATION / OWNERSHIP: OwnerCommercialWorkspaceRouter, FastAPI composition,
    and Vite transport owners.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
  v1.1.0-TYPED-ROUTE-INSPECTION narrows FastAPI BaseRoute values to APIRoute
    before inspecting method/path metadata, preserving exact assertions under Pyright.
  v1.0.0-CANONICAL-EOS-LOOPBACK corrects the stale localhost assertion to the
    fixed 127.0.0.1:9095 EOS target without relaxing route or authorization checks.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Source and route metadata only; no request or tenant data.
TENANT BOUNDARY: Authorization is verified separately by exact dependency bindings.
AUTHORITY BOUNDARY: Composition regression evidence only; no business command runs.
FINANCIAL AUTHORITY BOUNDARY: No billing or financial execution authority.
"""
from __future__ import annotations

import inspect
from pathlib import Path

from fastapi.routing import APIRoute

from tools.eos.api import server
from tools.eos.api.owner_commercial_workspace_router import (
    _COMPLETE,
    _CREATE,
    _READ,
    router,
)

ROOT = Path(__file__).resolve().parents[2]


def test_owner_commercial_workspace_routes_are_mounted_once_and_directly() -> None:
    """Keep the exact Python route mount and canonical loopback transport."""
    routes = {
        (route.path, tuple(sorted(route.methods or ())))
        for route in router.routes
        if isinstance(route, APIRoute)
    }
    assert ("/crm/owner-workspace", ("GET",)) in routes
    assert ("/crm/owner-workspace/work-items", ("POST",)) in routes
    assert (
        "/crm/owner-workspace/work-items/{work_item_id}/complete",
        ("POST",),
    ) in routes

    source = inspect.getsource(server)
    assert source.count(
        'app.include_router(owner_commercial_workspace_router, prefix="/api")'
    ) == 1
    assert (
        "from .owner_commercial_workspace_router import router as "
        "owner_commercial_workspace_router"
    ) in source

    vite = (ROOT / "client/vite.config.js").read_text(encoding="utf-8")
    assert "'/api/crm/owner-workspace': {" in vite
    assert "http://127.0.0.1:9095" in vite
    assert not (ROOT / "server/server.js").exists()


def test_each_owner_workspace_command_has_its_exact_permission_binding() -> None:
    """Do not weaken the distinct read, create, and completion permissions."""
    assert (_READ.permission_id, _READ.operation) == (
        "crm:work_item:read",
        "crm_work_item_read",
    )
    assert (_CREATE.permission_id, _CREATE.operation) == (
        "crm:work_item:create",
        "crm_work_item_create",
    )
    assert (_COMPLETE.permission_id, _COMPLETE.operation) == (
        "crm:work_item:complete",
        "crm_work_item_complete",
    )


# ARTIFACT: Owner Commercial Workspace Route Mount and EOS Transport Certificate
# VERSION: v1.1.0-TYPED-ROUTE-INSPECTION
# AUTHORITY BOUNDARY: Composition regression evidence only.
# TENANT POSTURE: No tenant state or records are accessed.
# FAIL-CLOSED POSTURE: Route mount, transport, or permission drift fails tests.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
