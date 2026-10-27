"""Tests for the Python EOS presentation-only PDF export boundary."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tools.eos.api.artifact_pdf_router import render_artifact_pdf, router
from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus


def _identity() -> SovereignIdentity:
    return SovereignIdentity(
        identity_id="principal-test-1",
        tenant_id="tenant-test-1",
        username="Test Operator",
        email="operator@example.invalid",
        auth_method="test-dependency-override",
        status=PrincipalStatus.ACTIVE,
    )


def test_render_artifact_pdf_returns_pdf_and_hashes_without_claiming_source_verification() -> None:
    pdf, evidence = render_artifact_pdf(
        {"type": "generic-artifact", "title": "Example", "data": {"value": "safe text"}},
        _identity(),
        generated_at="2026-10-27T00:00:00+00:00",
    )
    assert pdf.startswith(b"%PDF-")
    assert b"%%EOF" in pdf
    assert len(evidence["request_digest"]) == 128
    assert len(evidence["integrity_digest"]) == 128
    assert evidence["artifact_type"] == "generic-artifact"


def test_pdf_route_requires_authenticated_identity_and_returns_presentation_headers() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_current_identity] = _identity
    response = TestClient(app).post(
        "/api/generate/pdf",
        json={"type": "generic-artifact", "title": "Example", "data": {"value": "safe text"}},
    )
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-")
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.headers["x-artifact-proof-status"] == "SOURCE_UNVERIFIED"
    assert response.headers["cache-control"] == "no-store"
    assert len(response.headers["x-request-proof"]) == 128
    assert len(response.headers["x-wilsy-server-integrity-digest"]) == 128


def test_pdf_route_rejects_caller_selected_tenant_context() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_current_identity] = _identity
    response = TestClient(app).post(
        "/api/generate/pdf",
        json={"tenantId": "other-tenant", "type": "generic-artifact", "data": {"value": "x"}},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "ARTIFACT_PDF_TENANT_CONTEXT_MISMATCH"


def test_pdf_route_rejects_non_object_payload() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_current_identity] = _identity
    response = TestClient(app).post("/api/generate/pdf", json=["not", "an", "object"])
    assert response.status_code == 422
    assert response.json()["detail"] == "ARTIFACT_PDF_OBJECT_REQUIRED"


# ARTIFACT: test_artifact_pdf_router.py
# AUTHORITY BOUNDARY: Test-only assertions; no production identity or financial authority.
# FAIL-CLOSED POSTURE: Tenant-context mismatch must remain denied.
# END OF WILSY OS TEST ARTIFACT
