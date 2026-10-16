"""
TITLE: WILSY OS Productive-Work Authenticated HTTP Read Certificate
VERSION: v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-HTTP-CERT
AUTHORITY: Focused transport certificate for the existing PW-P11A/PW-P4/PW-P7B chain.
TENANT BOUNDARY: Tenant and principal are derived only from authorized context.
AUTHORITY BOUNDARY: Read projection only; no assignment, supervision, workflow,
                    legal act, Sheriff, Deputy, billing or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.legal_operations.service.legal_profile_productive_work_read_service import (
    LegalProductiveWorkReadServiceError,
)


VERSION = (
    "v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-HTTP-CERT"
)


class _Session:
    in_transaction = True


class _Work:
    def __init__(
        self,
        identity: str,
    ) -> None:
        self.identity = identity

    def to_dict(
        self,
    ) -> dict[str, object]:
        return {
            "tenant_id": "tenant-a",
            "work_item_id": self.identity,
            "case_matter_id": "matter-a",
            "title": "Daily legal work",
            "status": "OPEN",
        }


class _Service:
    def __init__(
        self,
        captured: dict[str, object],
    ) -> None:
        self.captured = captured

    def project(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        as_of: datetime,
        session: Any,
        **_: object,
    ) -> Any:
        self.captured.update(
            {
                "tenant_id": tenant_id,
                "principal_id": principal_id,
                "as_of": as_of,
                "session": session,
            }
        )

        context = SimpleNamespace(
            operating_role_id="tenant-defined-lead",
            operating_role_revision=3,
            display_name="Lead Specialist",
            capability_ids=("PRACTICE_CORPORATE",),
            office_references=("office:jhb",),
            practice_references=("practice:corporate",),
            business_unit_references=(),
            jurisdiction_references=("jurisdiction:ZA",),
        )

        work = _Work(
            "work-1"
        )

        return SimpleNamespace(
            schema="WILSY-LEGAL-PROFILE-PRODUCTIVE-WORK/V1",
            version="v1.0.1-PW-P2-PROFILE-PRODUCTIVE-WORK-COMPOSITION",
            tenant_id=tenant_id,
            principal_id=principal_id,
            as_of=as_of,
            operating_contexts=(context,),
            capability_ids=("PRACTICE_CORPORATE",),
            assigned_work_items=(work,),
            supervised_work_items=(),
            overdue_work_items=(),
            due_soon_work_items=(work,),
        )


def _context() -> Any:
    return SimpleNamespace(
        tenant_id="tenant-a",
        identity=SimpleNamespace(
            identity_id="principal-a"
        ),
    )


def _app() -> FastAPI:
    app = FastAPI()

    app.dependency_overrides[
        legal_router._PRODUCTIVE_WORK_READ
    ] = _context

    app.include_router(
        legal_router.router,
        prefix="/api",
    )

    return app


def test_exact_pw_p11a_http_authority_and_route_shape() -> None:
    assert (
        legal_router._PRODUCTIVE_WORK_READ.permission_id
        == "legal_operations:productive_work:read"
    )
    assert (
        legal_router._PRODUCTIVE_WORK_READ.operation
        == "legal_productive_work_read"
    )

    matches = [
        route
        for route in legal_router.router.routes
        if getattr(
            route,
            "path",
            None,
        )
        == "/legal-operations/productive-work"
    ]

    assert len(matches) == 1
    assert getattr(matches[0], "methods", None) == {"GET"}


def test_route_uses_only_authenticated_context_scope(
    monkeypatch: Any,
) -> None:
    captured: dict[str, object] = {}
    session = _Session()

    monkeypatch.setattr(
        legal_router,
        "_productive_work_service",
        lambda database: _Service(
            captured
        ),
    )

    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(
            session,
            object(),
        ),
    )

    with TestClient(
        _app()
    ) as client:
        response = client.get(
            (
                "/api/legal-operations/productive-work"
                "?tenant_id=foreign-tenant"
                "&principal_id=foreign-principal"
            )
        )

    assert response.status_code == 200

    assert captured["tenant_id"] == "tenant-a"
    assert captured["principal_id"] == "principal-a"
    assert captured["session"] is session

    as_of = captured["as_of"]
    assert isinstance(
        as_of,
        datetime,
    )
    assert as_of.tzinfo is not None

    body = response.json()

    assert body["tenant_id"] == "tenant-a"
    assert body["principal_id"] == "principal-a"
    assert body["http_version"] == (
        "v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-READ-API"
    )

    assert body["capability_ids"] == [
        "PRACTICE_CORPORATE"
    ]

    assert body["operating_contexts"] == [
        {
            "operating_role_id": "tenant-defined-lead",
            "operating_role_revision": 3,
            "display_name": "Lead Specialist",
            "capability_ids": [
                "PRACTICE_CORPORATE"
            ],
            "office_references": [
                "office:jhb"
            ],
            "practice_references": [
                "practice:corporate"
            ],
            "business_unit_references": [],
            "jurisdiction_references": [
                "jurisdiction:ZA"
            ],
        }
    ]

    assert [
        value["work_item_id"]
        for value in body[
            "assigned_work_items"
        ]
    ] == ["work-1"]

    assert body[
        "supervised_work_items"
    ] == []

    assert body[
        "due_soon_work_items"
    ][0]["work_item_id"] == "work-1"

    serialized = response.text.casefold()

    for forbidden in (
        "foreign-tenant",
        "foreign-principal",
        "assigned_by_principal_id",
        "authorization_evidence",
        "supervision_plan",
        "payment",
        "settlement",
        "revenue",
        "sheriff_operational_queue",
        "deputy_personal_active_work",
    ):
        assert forbidden not in serialized


def test_productive_work_domain_failure_maps_to_bounded_503(
    monkeypatch: Any,
) -> None:
    class _FailingService:
        def project(
            self,
            **_: object,
        ) -> Any:
            raise LegalProductiveWorkReadServiceError(
                "PW_P4_CERTIFICATE_FAILURE"
            )

    monkeypatch.setattr(
        legal_router,
        "_productive_work_service",
        lambda database: _FailingService(),
    )

    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(
            _Session(),
            object(),
        ),
    )

    with TestClient(
        _app()
    ) as client:
        response = client.get(
            "/api/legal-operations/productive-work"
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "LEGAL_OPERATIONS_PRODUCTIVE_WORK_EVIDENCE_UNAVAILABLE"
    )


def test_existing_sheriff_and_deputy_dependencies_remain_distinct() -> None:
    assert (
        legal_router._QUEUE_READ.permission_id
        == "legal_operations:queue:read"
    )
    assert (
        legal_router._DEPUTY_QUEUE_READ.permission_id
        == "legal_operations:deputy_queue:read"
    )

    assert (
        legal_router._PRODUCTIVE_WORK_READ.permission_id
        not in {
            legal_router._QUEUE_READ.permission_id,
            legal_router._DEPUTY_QUEUE_READ.permission_id,
        }
    )


# ARTIFACT: test_legal_productive_work_http_router.py
# VERSION: v1.0.0-PW-P11B-AUTHENTICATED-PRODUCTIVE-WORK-HTTP-CERT
# AUTHORITY BOUNDARY: authenticated own-principal productive-work read transport only
# SHERIFF / DEPUTY: existing specialized authorities remain distinct and unchanged
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
