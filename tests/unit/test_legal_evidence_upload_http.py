"""Direct certificate for authenticated Legal Evidence multipart transport.

TITLE: Legal Evidence Upload HTTP Direct Certificate
VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_upload_http.py
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L10A4 proves exact route, one-file allow-list, server tenant,
           bounded media/size and canonical response projection.
TENANT BOUNDARY: Tenant comes from TenantAuthorizationContext only.
AUTHORITY BOUNDARY: Transport certificate only; no provider or financial truth.
"""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from tools.eos.api import legal_evidence_upload_router as subject
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.legal_operations.service.legal_evidence_upload_orchestrator import LegalEvidenceUploadResult


class _Orchestrator:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def upload(self, **values: Any) -> LegalEvidenceUploadResult:
        stream = values.pop("stream")
        content = stream.read()
        self.calls.append({**values, "content": content})
        return LegalEvidenceUploadResult(
            ingestion_reference="legal-evidence-ingestion:abc",
            document_id=values["document_id"], case_matter_id="matter-1",
            state="COMMITTED", content_reference="legal-evidence-content:abc",
            content_fingerprint="a" * 128, content_length=len(content),
        )


@pytest.fixture
def client_and_service() -> tuple[TestClient, _Orchestrator]:
    app = FastAPI()
    app.include_router(subject.router, prefix="/api")
    service = _Orchestrator()
    identity = SovereignIdentity(
        identity_id="principal-1", tenant_id="tenant-1",
        username=None, email=None, roles=["LEGAL_PARTNER"],
        auth_method="test", status=PrincipalStatus.ACTIVE,
    )
    context = TenantAuthorizationContext(identity=identity, tenant_id="tenant-1", decision=object())  # type: ignore[arg-type]
    app.dependency_overrides[subject._WRITE] = lambda: context
    app.dependency_overrides[subject.get_legal_evidence_upload_orchestrator] = lambda: service
    return TestClient(app), service


def test_transport_sends_only_file_and_server_context(client_and_service: tuple[TestClient, _Orchestrator]) -> None:
    client, service = client_and_service
    response = client.post(
        "/api/legal-operations/evidence/documents/document-1",
        headers={"Idempotency-Key": "upload-command-1"},
        files={"file": ("proof.pdf", b"%PDF-proof", "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["state"] == "COMMITTED"
    assert set(service.calls[0]) == {"tenant_id", "document_id", "filename", "media_type", "content_length", "idempotency_key", "content"}
    assert service.calls[0]["tenant_id"] == "tenant-1"
    assert service.calls[0]["content"] == b"%PDF-proof"


@pytest.mark.parametrize("field", ["tenant_id", "principal_id", "case_matter_id", "provider_reference"])
def test_authority_form_fields_reject(client_and_service: tuple[TestClient, _Orchestrator], field: str) -> None:
    client, service = client_and_service
    response = client.post(
        "/api/legal-operations/evidence/documents/document-1",
        headers={"Idempotency-Key": "upload-command-1"},
        files={"file": ("proof.pdf", b"%PDF-proof", "application/pdf")},
        data={field: "attacker-value"},
    )
    assert response.status_code == 422
    assert service.calls == []


def test_bad_media_and_missing_idempotency_reject(client_and_service: tuple[TestClient, _Orchestrator]) -> None:
    client, service = client_and_service
    media = client.post(
        "/api/legal-operations/evidence/documents/document-1",
        headers={"Idempotency-Key": "upload-command-1"},
        files={"file": ("proof.exe", b"binary", "application/octet-stream")},
    )
    missing = client.post(
        "/api/legal-operations/evidence/documents/document-1",
        files={"file": ("proof.pdf", b"%PDF-proof", "application/pdf")},
    )
    assert media.status_code == 422
    assert missing.status_code == 422
    assert service.calls == []


# ARTIFACT: test_legal_evidence_upload_http.py
# VERSION: v1.0.0-L10A4-LEGAL-EVIDENCE-UPLOAD-HTTP-CERT
# AUTHORITY BOUNDARY: direct multipart HTTP certificate only
# TENANT POSTURE: authorized server context exclusively supplies tenant scope
# FAIL-CLOSED POSTURE: extra fields, bad media and absent idempotency reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
