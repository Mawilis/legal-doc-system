"""Tests for the Python EOS presentation-only PDF export boundary."""

import base64
import hashlib

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
    assert len(evidence["render_context_digest"]) == 128
    assert evidence["pdf_digest"] == hashlib.sha3_512(pdf).hexdigest()
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
    assert len(response.headers["x-wilsy-render-context-digest"]) == 128
    assert len(response.headers["x-wilsy-pdf-sha3-512"]) == 128


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


def test_pdf_route_fails_closed_for_enterprise_artifact_families_without_parity() -> None:
    import pytest

    enterprise_payloads = [
        {"type": "billing-invoice", "data": {"amount": 100}},
        {"artifactType": "crm-lead-proof-pack", "data": {"rows": []}},
        {"knowledgeBase": {"templateType": "PLAYBOOK_FG108"}},
        {"templateType": "nda"},
        {"payload": {"data": {"serviceType": "invoice"}}},
    ]
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_current_identity] = _identity

    for payload in enterprise_payloads:
        response = TestClient(app).post("/api/generate/pdf", json=payload)
        assert response.status_code == 503
        assert response.json()["detail"] == "ARTIFACT_PDF_ENTERPRISE_PARITY_UNAVAILABLE"


def test_pdf_route_keeps_generic_standard_presentation_export_available() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_current_identity] = _identity
    response = TestClient(app).post(
        "/api/generate/pdf",
        json={"type": "standard", "title": "Example", "data": {"value": "safe text"}},
    )
    assert response.status_code == 200
    assert response.headers["x-artifact-proof-status"] == "SOURCE_UNVERIFIED"


def test_render_artifact_pdf_preserves_bounded_user_signature_image_as_presentation_only() -> None:
    signature = (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADUlEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
    )
    pdf, evidence = render_artifact_pdf(
        {"type": "contract", "signature": signature, "metadata": {"jurisdiction": "ZA"}},
        _identity(),
        generated_at="2026-10-27T00:00:00+00:00",
    )
    assert pdf.startswith(b"%PDF-")
    assert len(evidence["pdf_digest"]) == 128


def test_render_artifact_pdf_rejects_untrusted_signature_image_format() -> None:
    from fastapi import HTTPException
    import pytest

    with pytest.raises(HTTPException) as raised:
        render_artifact_pdf(
            {"type": "contract", "signature": "data:image/svg+xml;base64,PHN2Zy8+"},
            _identity(),
        )
    assert raised.value.status_code == 422
    assert raised.value.detail == "ARTIFACT_PDF_SIGNATURE_IMAGE_FORMAT_INVALID"


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
