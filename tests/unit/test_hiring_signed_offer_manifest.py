import json
from types import SimpleNamespace

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
        "offer_terms_sha3_512": __import__("hashlib").sha3_512(
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
    changed_offer = SimpleNamespace(
        offer_id="OFFER-001", candidate_id="CAN-001",
        revision=8, fingerprint="e" * 64,
    )
    changed_evidence = SimpleNamespace(
        evidence_id="EVD-001", evidence_version_id="VER-004",
        content_digest_sha3_512="b" * 128,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=changed_offer, evidence=evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O", offer=offer, evidence=changed_evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="CUSTOMER-TENANT-001", offer=offer, evidence=evidence,
    )
