"""
TITLE: WILSY OS Legal Specialist Workflow Authenticated HTTP Certificate
VERSION: v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP-CERT
AUTHORITY: Focused read-transport certificate for the P1 specialist workflow service.
EPITOME: Prove that one authenticated productive-work reader receives only
         deterministic workflow explanation for work admitted by the same
         tenant/principal productive-work projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_specialist_workflow_http_router.py
COLLABORATION / OWNERSHIP: Python EOS Legal Operations API certification.
CERTIFICATION / UPDATE DATE: 2026-10-18
CHANGELOG: v1.0.0 establishes route, scope, shared-session, serialization and
           bounded fail-closed transport expectations.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Only authenticated TenantAuthorizationContext scope is used.
AUTHORITY BOUNDARY: Read explanation only; no work or workflow mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute, _iter_routes_with_context

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.legal_operations.service.legal_specialist_workflow_read_service import (
    LegalSpecialistWorkflowReadServiceError,
)


class _Session:
    in_transaction = True


def _context() -> Any:
    return SimpleNamespace(
        tenant_id="tenant-a",
        identity=SimpleNamespace(identity_id="principal-a"),
    )


def _app() -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[legal_router._PRODUCTIVE_WORK_READ] = _context
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_specialist_route_reuses_productive_work_authority_and_is_get_only() -> None:
    matches = [
        route
        for route in legal_router.router.routes
        if getattr(route, "path", None)
        == "/legal-operations/specialist-workflow"
    ]
    assert len(matches) == 1
    assert getattr(matches[0], "methods", None) == {"GET"}
    assert legal_router._SPECIALIST_WORKFLOW_READ is legal_router._PRODUCTIVE_WORK_READ


def test_specialist_route_is_mounted_exactly_once_on_runtime_server() -> None:
    import tools.eos.api.server as server_api

    matches = []
    for route, context in _iter_routes_with_context(server_api.app.routes):
        if not isinstance(route, APIRoute):
            continue
        path = context.path if context is not None else route.path
        if path == "/api/legal-operations/specialist-workflow":
            methods = context.methods if context is not None else route.methods
            matches.append((path, tuple(sorted(methods or set()))))

    assert matches == [
        ("/api/legal-operations/specialist-workflow", ("GET",))
    ]


def test_specialist_route_composes_visibility_ceiling_and_workflow_in_one_session(
    monkeypatch: Any,
) -> None:
    session = _Session()
    captured: dict[str, Any] = {}
    now = datetime(2026, 10, 18, 10, 0, tzinfo=UTC)
    productive = SimpleNamespace(
        tenant_id="tenant-a",
        principal_id="principal-a",
        as_of=now,
    )
    row = SimpleNamespace(
        work_item_id="work-1",
        case_matter_id="matter-1",
        workflow_instance_id="workflow-1",
        workflow_definition_id="definition-1",
        stage_definition_id="stage-review",
        readiness="BLOCKED_DEPENDENCY_AND_GATE",
        blocking_dependency_work_item_ids=("work-0",),
        unsatisfied_gate_references=("PARTNER_REVIEW",),
        materialization_transition_id="transition-1",
        materialization_receipt_id="receipt-1",
    )

    class _ProductiveService:
        def project(self, **kwargs: object) -> object:
            captured["productive"] = kwargs
            productive.as_of = kwargs["as_of"]
            return productive

    class _SpecialistService:
        def project(self, **kwargs: object) -> object:
            captured["specialist"] = kwargs
            return SimpleNamespace(
                schema="WILSY-LEGAL-SPECIALIST-WORKFLOW-PROJECTION/V1",
                version="v1.0.0-P0-LEGAL-SPECIALIST-WORKFLOW-PROJECTION",
                tenant_id="tenant-a",
                principal_id="principal-a",
                as_of=productive.as_of,
                rows=(row,),
            )

    monkeypatch.setattr(
        legal_router,
        "_specialist_workflow_services",
        lambda database: (_ProductiveService(), _SpecialistService()),
    )
    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(session, object()),
    )

    with TestClient(_app()) as client:
        response = client.get(
            "/api/legal-operations/specialist-workflow"
            "?tenant_id=foreign&principal_id=foreign"
        )

    assert response.status_code == 200
    productive_call = captured["productive"]
    specialist_call = captured["specialist"]
    assert productive_call["tenant_id"] == "tenant-a"
    assert productive_call["principal_id"] == "principal-a"
    assert productive_call["session"] is session
    assert specialist_call["tenant_id"] == "tenant-a"
    assert specialist_call["principal_id"] == "principal-a"
    assert specialist_call["session"] is session
    assert specialist_call["productive_work"] is productive

    assert response.json() == {
        "schema": "WILSY-LEGAL-SPECIALIST-WORKFLOW-PROJECTION/V1",
        "version": "v1.0.0-P0-LEGAL-SPECIALIST-WORKFLOW-PROJECTION",
        "http_version": "v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP",
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "as_of": productive.as_of.isoformat(),
        "rows": [{
            "work_item_id": "work-1",
            "case_matter_id": "matter-1",
            "workflow_instance_id": "workflow-1",
            "workflow_definition_id": "definition-1",
            "stage_definition_id": "stage-review",
            "readiness": "BLOCKED_DEPENDENCY_AND_GATE",
            "blocking_dependency_work_item_ids": ["work-0"],
            "unsatisfied_gate_references": ["PARTNER_REVIEW"],
            "materialization_transition_id": "transition-1",
            "materialization_receipt_id": "receipt-1",
        }],
    }
    assert "foreign" not in response.text


def test_specialist_evidence_failure_maps_to_bounded_503(monkeypatch: Any) -> None:
    class _ProductiveService:
        def project(self, **_: object) -> object:
            return SimpleNamespace(
                tenant_id="tenant-a",
                principal_id="principal-a",
                as_of=datetime.now(UTC),
            )

    class _FailingSpecialistService:
        def project(self, **_: object) -> object:
            raise LegalSpecialistWorkflowReadServiceError("P1_CORRUPT_EVIDENCE")

    monkeypatch.setattr(
        legal_router,
        "_specialist_workflow_services",
        lambda database: (_ProductiveService(), _FailingSpecialistService()),
    )
    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(_Session(), object()),
    )

    with TestClient(_app()) as client:
        response = client.get("/api/legal-operations/specialist-workflow")

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "LEGAL_OPERATIONS_SPECIALIST_WORKFLOW_EVIDENCE_UNAVAILABLE"
    )


# ==============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ==============================================================================
# ARTIFACT: test_legal_specialist_workflow_http_router.py
# VERSION: v1.0.0-P2-LEGAL-SPECIALIST-WORKFLOW-HTTP-CERT
# AUTHORITY BOUNDARY: Authenticated read-transport evidence only
# TENANT POSTURE: Exact authorized tenant and principal only
# FAIL-CLOSED POSTURE: Missing, corrupt or divergent evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
