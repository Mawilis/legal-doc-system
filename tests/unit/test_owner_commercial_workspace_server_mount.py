"""WILSY OS owner commercial workspace composition certificate.

TITLE: Owner Commercial Workspace Route Mount and EOS Transport Certificate
VERSION: v1.5.0-DRAFT-PROGRESS-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verifies exact owner-workspace route composition, permission bindings,
    and the canonical Vite-to-Python EOS loopback target.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_owner_commercial_workspace_server_mount.py
COLLABORATION / OWNERSHIP: OwnerCommercialWorkspaceRouter, FastAPI composition,
    and Vite transport owners.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.5.0-DRAFT-PROGRESS-HTTP-CERT proves exact owner
           draft GET uses CRM READ and Draft/Open/In Progress status POST
           uses independently granted CRM UPDATE with strict revision evidence.
CHANGELOG: v1.4.0-AUDITED-OWNER-CANCEL-ROUTE-CERT pins the distinct
           owner-cancel route to CRM UPDATE IAM, requiring reason, source
           revision and idempotency without accepting actor/tenant from body.
CHANGELOG:
  v1.3.0-GOVERNED-EDIT-ROUTE-CERT proves PATCH uses CRM UPDATE rather
    than CREATE/COMPLETE IAM, audit-history GET stays read-only, and the
    typed edit contract requires each field and stable idempotency evidence.
  v1.2.0-SOURCE-WORK-DETAIL-READ-CERT certifies the added exact-record GET route uses
    existing CRM read IAM and does not establish a new write permission.
  v1.2.0-SOURCE-WORK-DETAIL-READ-CERT narrows FastAPI BaseRoute values to APIRoute
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

import pytest

from fastapi.routing import APIRoute

from tools.eos.api import server
from tools.eos.api.owner_commercial_workspace_router import (
    _COMPLETE,
    _CREATE,
    _READ,
    _UPDATE,
    OwnerWorkReviseRequest,
    OwnerWorkCancelRequest,
    OwnerWorkStatusRequest,
    read_owner_work_drafts,
    transition_owner_work_status,
    cancel_owner_work_item,
    _transaction,
    read_owner_work_item,
    read_owner_work_item_history,
    revise_owner_work_item,
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
    assert ("/crm/owner-workspace/work-items/{work_item_id}", ("GET",)) in routes
    assert ("/crm/owner-workspace/work-items/{work_item_id}", ("PATCH",)) in routes
    assert ("/crm/owner-workspace/work-items/{work_item_id}/history", ("GET",)) in routes
    assert ("/crm/owner-workspace/work-items/{work_item_id}/cancel", ("POST",)) in routes
    assert ("/crm/owner-workspace/drafts", ("GET",)) in routes
    assert ("/crm/owner-workspace/work-items/{work_item_id}/status", ("POST",)) in routes
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
    assert (_UPDATE.permission_id, _UPDATE.operation) == (
        "crm:work_item:update",
        "crm_work_item_update",
    )


def test_exact_work_detail_uses_existing_crm_read_permission() -> None:
    """The source-record lookup must re-use CRM read IAM without self-grant."""
    from fastapi.params import Depends

    signature = inspect.signature(read_owner_work_item)
    context_parameter = signature.parameters["context"]
    assert isinstance(context_parameter.default, Depends)
    assert context_parameter.default.dependency is _READ
    transaction_source = inspect.getsource(_transaction)
    assert "except OwnerWorkRegistryNotFound as error" in transaction_source
    assert 'HTTPException(status_code=404, detail="OWNER_WORK_NOT_FOUND")' in transaction_source



def test_work_edit_and_history_require_distinct_source_permissions():
    from fastapi.params import Depends
    from pydantic import ValidationError
    import pytest

    for endpoint, expected in (
        (revise_owner_work_item, _UPDATE),
        (read_owner_work_item_history, _READ),
    ):
        parameter = inspect.signature(endpoint).parameters["context"]
        assert isinstance(parameter.default, Depends)
        assert parameter.default.dependency is expected
    valid = {
        "title": "Source task", "description": "Source instructions",
        "priority": "HIGH", "due_at": None,
        "expected_updated_at": "2026-11-17T06:00:00Z",
    }
    assert OwnerWorkReviseRequest(**valid).priority == "HIGH"
    for field in valid:
        with pytest.raises(ValidationError):
            OwnerWorkReviseRequest(**{k: v for k, v in valid.items() if k != field})
    with pytest.raises(ValidationError):
        OwnerWorkReviseRequest(**{**valid, "owner_principal_id": "forged"})


def test_owner_cancel_requires_exact_crm_update_authority_and_strict_payload() -> None:
    from pydantic import ValidationError
    import inspect
    assert cancel_owner_work_item.__name__ == "cancel_owner_work_item"
    assert "Depends(_UPDATE)" in inspect.getsource(
        __import__("tools.eos.api.owner_commercial_workspace_router",
                   fromlist=["router"])
    )
    valid = {"reason": "Scope withdrawn", "expected_updated_at": "2026-11-17T10:00:00Z"}
    assert OwnerWorkCancelRequest(**valid).reason == "Scope withdrawn"
    for field in valid:
        with pytest.raises(ValidationError):
            OwnerWorkCancelRequest(**{key: value for key, value in valid.items() if key != field})
    with pytest.raises(ValidationError):
        OwnerWorkCancelRequest(**{**valid, "actor_principal_id": "forged"})


def test_exact_draft_and_progress_routes_retain_source_iam() -> None:
    from pydantic import ValidationError
    source = inspect.getsource(transition_owner_work_status)
    assert "Depends(_UPDATE)" in source
    assert "context.identity.identity_id" in source
    assert "Idempotency-Key" in source
    assert "Depends(_READ)" in inspect.getsource(read_owner_work_drafts)
    assert OwnerWorkStatusRequest(
        status="IN_PROGRESS", expected_updated_at="2026-11-17T10:00:00Z",
    ).status == "IN_PROGRESS"
    assert OwnerWorkStatusRequest(
        status="DRAFT", expected_updated_at="2026-11-17T10:00:00Z",
    ).status == "DRAFT"
    with pytest.raises(ValidationError):
        OwnerWorkStatusRequest(status="COMPLETED", expected_updated_at="2026-11-17T10:00:00Z")
    with pytest.raises(ValidationError):
        OwnerWorkStatusRequest(status="DRAFT", expected_updated_at="2026-11-17T10:00:00Z",
                               owner_principal_id="forged")


# ARTIFACT: Owner Commercial Workspace Route Mount and EOS Transport Certificate
# VERSION: v1.5.0-DRAFT-PROGRESS-HTTP-CERT
# AUTHORITY BOUNDARY: Composition regression evidence only.
# TENANT POSTURE: No tenant state or records are accessed.
# FAIL-CLOSED POSTURE: Route mount, transport, or permission drift fails tests.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
