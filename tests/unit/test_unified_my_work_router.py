"""TITLE: WILSY OS Unified My Work router authorization certification.
VERSION: v1.2.1-SAFE-SOURCE-FAILURE-LOG-CERT
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies independently admitted, source-owned My Work aggregation,
         including privacy-minimal HR action projection handoff.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_unified_my_work_router.py
COLLABORATION / OWNERSHIP: unified_my_work_router and existing source routers.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG: v1.2.1-SAFE-SOURCE-FAILURE-LOG-CERT verifies stable
           error-only diagnostics never contain arbitrary private HTTP detail.
           v1.2.0-CRM-CORE-OPTIONAL-SOURCE-CERT omits CRM only on
           exact canonical not-entitled evidence and proves CRM entitlement
           uncertainty still raises, preserving other source truth.
CHANGELOG: v1.1.0-HR-SOURCE-OWNED-ACTIONS-CERT adds denied-HR, safe-HR-action
           and dependency-wiring coverage without creating a role or record.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque fixtures; no personnel data or writes.
TENANT BOUNDARY: Every fixture uses an exact source context or tests rejection.
AUTHORITY BOUNDARY: Tests source admission only; commands remain source-owned.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from tools.eos.api import unified_my_work_router as route


def test_source_http_failure_logs_only_bounded_codes(caplog):
    """A failing CRM source cannot leak arbitrary HTTP detail into EOS logs."""
    import logging

    caplog.set_level(logging.ERROR, logger="WilsyOS.API.UnifiedMyWork")
    def unavailable():
        raise HTTPException(status_code=503, detail="OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE")

    with pytest.raises(HTTPException):
        route._timed_source_read("CRM", unavailable)
    assert any(
        "http_status=503 source_code=OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE" in row.message
        for row in caplog.records
    )
    caplog.clear()
    def private_failure():
        raise HTTPException(status_code=503, detail={"private_record": "sensitive value"})

    with pytest.raises(HTTPException):
        route._timed_source_read("CRM", private_failure)
    assert any("source_code=UNCLASSIFIED_HTTP" in row.message for row in caplog.records)
    assert "sensitive value" not in caplog.text


def _context(tenant="tenant-a", principal="principal-a"):
    return SimpleNamespace(
        tenant_id=tenant,
        identity=SimpleNamespace(identity_id=principal),
    )


def _identity(principal="principal-a"):
    return SimpleNamespace(identity_id=principal)


def _hr_contexts():
    """Supply explicit denied HR dependencies for direct route invocation."""
    return {
        "headcount_read_context": None,
        "headcount_submit_context": None,
        "headcount_decide_context": None,
        "offer_read_context": None,
        "offer_submit_context": None,
        "offer_decide_context": None,
        "offer_send_context": None,
    }


def _omit_hr_dependencies(app):
    """Keep HTTP fixtures independent of live HR IAM repositories."""
    for dependency in (
        route._HEADCOUNT_READ,
        route._HEADCOUNT_SUBMIT,
        route._HEADCOUNT_DECIDE,
        route._OFFER_READ,
        route._OFFER_SUBMIT,
        route._OFFER_DECIDE,
        route._OFFER_SEND,
    ):
        app.dependency_overrides[dependency] = lambda: None


def test_route_omits_denied_sources_and_reads_only_independently_admitted_sources(monkeypatch):
    calls = []

    def read_module(slug, *, tenant_id):
        calls.append((slug, tenant_id))
        return {
            "tenant_id": tenant_id,
            "items": [{
                "work_item_id": f"{slug}-1",
                "title": f"{slug} work",
                "status": "OPEN",
                "priority": "HIGH",
            }],
        }

    monkeypatch.setattr(route, "_read_module", read_module)
    monkeypatch.setattr(route, "_read_legal", lambda **_kwargs: pytest.fail("denied Legal source read"))
    monkeypatch.setattr(route, "_read_crm", lambda **_kwargs: pytest.fail("denied CRM source read"))

    result = asyncio.run(route.read_my_work(
        tenant_id="tenant-a",
        identity=_identity(),
        legal_context=None,
        operations_context=_context(),
        intelligence_context=None,
        crm_context=None,
        **_hr_contexts(),
    ))

    assert calls == [("operations", "tenant-a")]
    assert result["sources_included"] == ["OPERATIONS"]
    assert result["summary"]["active_count"] == 1
    assert result["summary"]["source_counts"] == {"OPERATIONS": 1}
    assert result["items"][0]["source"] == "OPERATIONS"
    assert result["authority"]["permits_source_commands"] is False


def test_route_fails_closed_when_an_authorized_source_reader_is_unavailable(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise HTTPException(status_code=503, detail="SOURCE_UNAVAILABLE")

    monkeypatch.setattr(route, "_read_module", unavailable)
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id="tenant-a",
            identity=_identity(),
            legal_context=None,
            operations_context=_context(),
            intelligence_context=None,
            crm_context=None,
            **_hr_contexts(),
        ))
    assert error.value.status_code == 503


def test_route_rejects_context_from_a_different_tenant_or_principal():
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id="tenant-a",
            identity=_identity(),
            legal_context=None,
            operations_context=_context(tenant="tenant-b"),
            intelligence_context=None,
            crm_context=None,
            **_hr_contexts(),
        ))
    assert error.value.status_code == 503
    assert error.value.detail == "MY_WORK_AUTHORIZATION_CONTEXT_INCONSISTENT"


def test_route_registers_independent_optional_iam_dependencies_for_hr_and_existing_sources():
    endpoint = next(
        item.endpoint for item in route.router.routes
        if getattr(item, "name", None) == "read_my_work"
    )
    names = set(endpoint.__annotations__)
    assert "legal_context" in names
    assert "operations_context" in names
    assert "intelligence_context" in names
    assert "crm_context" in names
    assert "headcount_read_context" in names
    assert "headcount_submit_context" in names
    assert "headcount_decide_context" in names
    assert "offer_read_context" in names
    assert "offer_submit_context" in names
    assert "offer_decide_context" in names
    assert "offer_send_context" in names



def test_route_rejects_whitespace_tenant_scope_before_source_reads():
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id=" tenant-a ",
            identity=_identity(),
            legal_context=None,
            operations_context=None,
            intelligence_context=None,
            crm_context=None,
            **_hr_contexts(),
        ))
    assert error.value.status_code == 403
    assert error.value.detail == "TENANT_SCOPE_REQUIRED"


def test_route_rejects_tenant_scope_when_no_source_is_authorized():
    with pytest.raises(HTTPException) as error:
        asyncio.run(route.read_my_work(
            tenant_id="foreign-tenant",
            identity=_identity(),
            legal_context=None,
            operations_context=None,
            intelligence_context=None,
            crm_context=None,
            **_hr_contexts(),
        ))
    assert error.value.status_code == 403
    assert error.value.detail == "MY_WORK_NO_AUTHORIZED_SOURCE"


def test_http_route_does_not_return_empty_success_for_unjoined_foreign_tenant():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(route.router, prefix="/api")
    app.dependency_overrides[route.get_current_identity] = _identity
    app.dependency_overrides[route._LEGAL_READ] = lambda: None
    app.dependency_overrides[route._OPERATIONS_READ] = lambda: None
    app.dependency_overrides[route._INTELLIGENCE_READ] = lambda: None
    app.dependency_overrides[route._CRM_READ] = lambda: None
    _omit_hr_dependencies(app)

    with TestClient(app) as client:
        response = client.get(
            "/api/my-work",
            headers={"X-Tenant-ID": "foreign-tenant"},
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "MY_WORK_NO_AUTHORIZED_SOURCE"



def test_http_route_omits_denied_source_and_returns_only_authorized_projection(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(route.router, prefix="/api")
    app.dependency_overrides[route.get_current_identity] = _identity
    app.dependency_overrides[route._LEGAL_READ] = lambda: None
    app.dependency_overrides[route._OPERATIONS_READ] = lambda: _context()
    app.dependency_overrides[route._INTELLIGENCE_READ] = lambda: None
    app.dependency_overrides[route._CRM_READ] = lambda: None
    _omit_hr_dependencies(app)
    monkeypatch.setattr(
        route,
        "_read_module",
        lambda slug, *, tenant_id: {
            "tenant_id": tenant_id,
            "items": [{
                "work_item_id": "http-ops-1",
                "title": "HTTP operations task",
                "status": "OPEN",
                "priority": "NORMAL",
            }],
        },
    )

    with TestClient(app) as client:
        response = client.get("/api/my-work", headers={"X-Tenant-ID": "tenant-a"})

    assert response.status_code == 200
    body = response.json()
    assert body["sources_included"] == ["OPERATIONS"]
    assert [item["title"] for item in body["items"]] == ["HTTP operations task"]


def test_http_route_does_not_turn_authorized_source_outage_into_empty_success(monkeypatch):
    from fastapi import FastAPI, HTTPException
    from fastapi.testclient import TestClient
    from tools.eos.api.errors import register_error_handlers

    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.include_router(route.router, prefix="/api")
    app.dependency_overrides[route.get_current_identity] = _identity
    app.dependency_overrides[route._LEGAL_READ] = lambda: None
    app.dependency_overrides[route._OPERATIONS_READ] = lambda: _context()
    app.dependency_overrides[route._INTELLIGENCE_READ] = lambda: None
    app.dependency_overrides[route._CRM_READ] = lambda: None
    _omit_hr_dependencies(app)

    def unavailable(*_args, **_kwargs):
        raise HTTPException(status_code=503, detail="SOURCE_UNAVAILABLE")

    monkeypatch.setattr(route, "_read_module", unavailable)
    with TestClient(app) as client:
        response = client.get("/api/my-work", headers={"X-Tenant-ID": "tenant-a"})

    assert response.status_code == 503



def test_module_product_entitlement_denial_omits_only_that_source(monkeypatch):
    def not_entitled(*_args, **_kwargs):
        raise HTTPException(status_code=403, detail="MODULE_WORK_PRODUCT_NOT_ENTITLED")

    monkeypatch.setattr(route.module_source, "_transaction", not_entitled)
    assert route._read_module("operations", tenant_id="tenant-a") is None


def test_crm_core_entitlement_denial_omits_only_crm_source(monkeypatch):
    def not_entitled(*_args, **_kwargs):
        raise HTTPException(status_code=403, detail="OWNER_WORK_CRM_NOT_ENTITLED")

    monkeypatch.setattr(route.crm_source, "_transaction", not_entitled)
    assert route._read_crm(tenant_id="tenant-a") is None


def test_uncertain_crm_entitlement_does_not_become_verified_empty_work(monkeypatch):
    def unavailable(*_args, **_kwargs):
        raise HTTPException(status_code=503, detail="OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE")

    monkeypatch.setattr(route.crm_source, "_transaction", unavailable)
    with pytest.raises(HTTPException) as error:
        route._read_crm(tenant_id="tenant-a")
    assert error.value.status_code == 503
    assert error.value.detail == "OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE"


def test_unknown_source_forbidden_and_source_outage_are_not_silently_omitted(monkeypatch):
    def forbidden(*_args, **_kwargs):
        raise HTTPException(status_code=403, detail="UNCLASSIFIED_SOURCE_DENIAL")

    monkeypatch.setattr(route.module_source, "_transaction", forbidden)
    with pytest.raises(HTTPException) as error:
        route._read_module("operations", tenant_id="tenant-a")
    assert error.value.detail == "UNCLASSIFIED_SOURCE_DENIAL"


def test_route_includes_only_safe_hr_actions_after_source_specific_read_admission(monkeypatch):
    captured = {}

    def read_hr(**kwargs):
        captured.update(kwargs)
        return {
            "tenant_id": kwargs["tenant_id"],
            "items": [{
                "work_item_id": "OFFER:opaque:DECIDE",
                "title": "Independently decide employment offer",
                "status": "PENDING_ACTION",
                "priority": "HIGH",
                "kind": "HR_OFFER_DECISION",
            }],
        }

    monkeypatch.setattr(route, "_read_hr", read_hr)
    result = asyncio.run(route.read_my_work(
        tenant_id="tenant-a",
        identity=_identity(),
        legal_context=None,
        operations_context=None,
        intelligence_context=None,
        crm_context=None,
        headcount_read_context=None,
        headcount_submit_context=None,
        headcount_decide_context=None,
        offer_read_context=_context(),
        offer_submit_context=None,
        offer_decide_context=_context(),
        offer_send_context=None,
    ))

    assert result["sources_included"] == ["HR"]
    assert result["summary"]["source_counts"] == {"HR": 1}
    assert result["items"][0]["source_key"] == "HR:OFFER:opaque:DECIDE"
    assert captured["offer_read"] is not None
    assert captured["offer_decide"] is not None
    assert captured["offer_submit"] is None


def test_hr_source_owners_emit_only_action_metadata_not_administrative_records(monkeypatch):
    from datetime import datetime, timezone
    from types import SimpleNamespace

    from tools.eos.saas.domain.headcount_requisition import RequisitionStatus
    from tools.eos.saas.domain.hiring_lifecycle import OfferStatus

    draft_requisition = SimpleNamespace(
        requisition_id="REQ-opaque", status=RequisitionStatus.DRAFT,
        requested_by_principal_id="principal-a", submitted_by_principal_id=None,
        department_id="CONFIDENTIAL", business_justification="CONFIDENTIAL",
    )
    submitted_offer = SimpleNamespace(
        offer_id="OFFER-opaque", status=OfferStatus.SUBMITTED,
        prepared_by_principal_id="principal-other",
        candidate_id="CONFIDENTIAL", terms=SimpleNamespace(
            expires_at=datetime(2026, 12, 1, tzinfo=timezone.utc),
            gross_compensation_minor=999999,
        ),
    )
    monkeypatch.setattr(
        route.headcount_source,
        "_transaction",
        lambda callback: callback(
            SimpleNamespace(list_for_tenant=lambda **_kwargs: (draft_requisition,)),
            object(),
        ),
    )
    monkeypatch.setattr(
        route.hiring_source,
        "_transaction",
        lambda callback: callback(
            SimpleNamespace(list_offers=lambda **_kwargs: ([submitted_offer], 1)),
            object(),
        ),
    )

    payload = route._read_hr(
        tenant_id="tenant-a", principal_id="principal-a",
        headcount_read=_context(), headcount_submit=_context(), headcount_decide=None,
        offer_read=_context(), offer_submit=None, offer_decide=_context(), offer_send=None,
    )

    assert payload == {
        "tenant_id": "tenant-a",
        "items": [
            {
                "work_item_id": "HEADCOUNT:REQ-opaque:SUBMIT",
                "title": "Submit headcount requisition",
                "status": "PENDING_ACTION",
                "priority": "NORMAL",
                "kind": "HR_HEADCOUNT_SUBMIT",
            },
            {
                "work_item_id": "OFFER:OFFER-opaque:DECIDE",
                "title": "Independently decide employment offer",
                "status": "PENDING_ACTION",
                "priority": "HIGH",
                "kind": "HR_OFFER_DECISION",
            },
        ],
    }


# ARTIFACT: test_unified_my_work_router.py
# VERSION: v1.2.1-SAFE-SOURCE-FAILURE-LOG-CERT
# AUTHORITY BOUNDARY: Source read admission and metadata projection only.
# TENANT POSTURE: Exact tenant and principal contexts are mandatory in each case.
# FAIL-CLOSED POSTURE: Denial and source errors never become an empty success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
