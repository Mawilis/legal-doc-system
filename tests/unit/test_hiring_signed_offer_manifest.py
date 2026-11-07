import hashlib
import json
from types import SimpleNamespace

import pytest

from tools.eos.api.hiring_lifecycle_router import _signed_offer_manifest


def test_signed_offer_manifest_is_canonical_and_commits_to_exact_offer_and_document():
    offer = SimpleNamespace(
        offer_id="OFFER-001",
        candidate_id="CAN-001",
        requisition_id="REQ-001",
        revision=7,
        fingerprint="f" * 64,
        terms=SimpleNamespace(to_dict=lambda: {"position_title": "Engineer", "currency": "ZAR"}),
    )
    evidence = SimpleNamespace(
        evidence_id="EVD-001",
        evidence_version_id="VER-003",
        content_digest_sha3_512="a" * 128,
    )
    first = _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=offer, evidence=evidence,
    )
    second = _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=offer, evidence=evidence,
    )
    assert first == second
    manifest = json.loads(first)
    assert manifest == {
        "schema": "wilsy.hr.signed_offer_signature_manifest.v1",
        "tenant_id": "WILSYTENANT-4CD2FZ4O",
        "offer_id": "OFFER-001",
        "candidate_id": "CAN-001",
        "requisition_id": "REQ-001",
        "offer_terms_sha3_512": hashlib.sha3_512(
            b'{"currency":"ZAR","position_title":"Engineer"}'
        ).hexdigest(),
        "evidence_id": "EVD-001",
        "evidence_version_id": "VER-003",
        "evidence_kind": "SIGNED_OFFER",
        "evidence_digest_sha3_512": "a" * 128,
    }


def test_signed_offer_manifest_changes_when_offer_revision_terms_or_evidence_changes():
    offer = SimpleNamespace(
        offer_id="OFFER-001", candidate_id="CAN-001", requisition_id="REQ-001",
        revision=7, fingerprint="f" * 64,
        terms=SimpleNamespace(to_dict=lambda: {"position_title": "Engineer", "currency": "ZAR"}),
    )
    evidence = SimpleNamespace(
        evidence_id="EVD-001", evidence_version_id="VER-003",
        content_digest_sha3_512="a" * 128,
    )
    baseline = _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=offer, evidence=evidence,
    )
    changed_revision = SimpleNamespace(
        offer_id="OFFER-001", candidate_id="CAN-001", requisition_id="REQ-001",
        revision=8, fingerprint="e" * 64,
        terms=SimpleNamespace(to_dict=lambda: {"position_title": "Engineer", "currency": "ZAR"}),
    )
    changed_terms = SimpleNamespace(
        offer_id="OFFER-001", candidate_id="CAN-001", requisition_id="REQ-001",
        revision=8, fingerprint="e" * 64,
        terms=SimpleNamespace(to_dict=lambda: {"position_title": "Director", "currency": "ZAR"}),
    )
    changed_evidence = SimpleNamespace(
        evidence_id="EVD-001", evidence_version_id="VER-004",
        content_digest_sha3_512="b" * 128,
    )
    # Lifecycle revision changes on APPROVED -> SENT; it must not invalidate
    # a signature over unchanged, already-approved commercial terms.
    assert baseline == _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=changed_revision, evidence=evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=changed_terms, evidence=evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=offer, evidence=changed_evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="CUSTOMER-TENANT-001", offer=offer, evidence=evidence,
    )



def test_offer_acceptance_fails_closed_when_institutional_pki_is_not_ready(monkeypatch):
    import asyncio
    from datetime import datetime, timezone
    from types import SimpleNamespace

    from fastapi import FastAPI, HTTPException, Request

    import tools.eos.api.hiring_lifecycle_router as hiring
    from tools.eos.saas.domain.candidate_evidence import CandidateEvidenceKind
    from tools.eos.saas.domain.hiring_lifecycle import OfferStatus

    offer = SimpleNamespace(
        offer_id="OFFER-001", candidate_id="CAN-001", revision=1,
        fingerprint="f" * 64, status=OfferStatus.SENT,
    )
    evidence = SimpleNamespace(
        evidence_kind=CandidateEvidenceKind.SIGNED_OFFER,
        offer_id="OFFER-001", content_digest_sha3_512="a" * 128,
        fingerprint="e" * 64,
    )

    class FakeRegistry:
        def get_transition_replay(self, **kwargs):
            return None

        def get_offer(self, **kwargs):
            return offer

    class FakeDatabase:
        def __getitem__(self, key):
            return object()

    monkeypatch.setattr(hiring, "_transaction", lambda callback: callback(FakeRegistry(), object()))
    monkeypatch.setattr(hiring, "get_database", lambda: FakeDatabase())
    monkeypatch.setattr(hiring.CandidateEvidenceRegistry, "get", lambda self, **kwargs: evidence)

    app = FastAPI()
    app.state.institutional_pki_ready = False
    request = Request({
        "type": "http", "app": app, "headers": [], "query_string": b"",
        "path": "/api/hr/offers/OFFER-001/accept", "method": "POST",
        "server": ("testserver", 80), "scheme": "http", "client": ("test", 1),
    })
    body = hiring.OfferAcceptanceRequest(
        expected_revision=1,
        evidence_reference="EVD-001",
        evidence_fingerprint="a" * 128,
        evidence_version_id="VER-001",
        accepted_at=datetime(2026, 11, 7, tzinfo=timezone.utc),
        signer_certificate_pem_base64="Y2VydA==",
        intermediate_certificate_pems_base64=["aW50ZXJtZWRpYXRl"],
        detached_signature_base64="c2ln",
    )
    context = SimpleNamespace(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        identity=SimpleNamespace(identity_id="HR-PRINCIPAL-001"),
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(hiring.accept_offer(
            "OFFER-001", body, request, "accept-001", context,
        ))
    assert error.value.status_code == 503
    assert error.value.detail == "INSTITUTIONAL_PKI_NOT_READY"
