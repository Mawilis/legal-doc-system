"""TITLE: WILSY EOS Signed-Offer Manifest and Hiring Authority Boundary Tests.
VERSION: v1.3.0-PLATFORM-EMPLOYEE-ADMISSION-AUTHORITY-BOUNDARY
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies deterministic signed-offer manifests, exact employer route
         pairs, centrally governed admission permission binding, and the
         fail-closed candidate-identity boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_hiring_signed_offer_manifest.py
COLLABORATION / OWNERSHIP: Regression tests for Python EOS hiring and authorization contracts.
CERTIFICATION / UPDATE DATE: 2026-11-12.
CHANGELOG:
  2026-11-12 v1.3.0-PLATFORM-EMPLOYEE-ADMISSION-AUTHORITY-BOUNDARY — Requires the centrally governed WILSY admission permission binding while proving no employee-admission route is mounted and offer acceptance remains identity-binding-disabled.
  2026-11-12 v1.2.0-PLATFORM-EMPLOYER-ROUTE-CONTRACT — Pins platform-employer pairs on candidate and offer routes and proves acceptance remains customer-HR-only and identity-binding-disabled.
  2026-11-12 v1.1.0-STRICT-TYPING-CERT — Uses explicit test-only type casts for deliberately minimal duck-typed manifest fixtures and the disabled route context.
  2026-11-12 v1.0.0-STRICT-TYPING-CERT — Requires authenticated acceptance to remain unavailable without governed candidate identity binding, before transaction or PKI dependencies are touched.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic offer and certificate inputs only; no persisted personal information.
TENANT BOUNDARY: Manifest tests use explicit synthetic tenant identifiers; disabled acceptance performs no persistence lookup.
AUTHORITY BOUNDARY: Tests verify central EOS permission mapping and mounted route boundaries; they do not assign roles or grant operational admission authority.
FINANCIAL AUTHORITY BOUNDARY: No payroll, payment, execution, or settlement authority.
"""

import hashlib
import json
from types import SimpleNamespace
from typing import cast

import pytest

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.saas.domain.hiring_lifecycle import EmploymentOffer

from tools.eos.api.hiring_lifecycle_router import _signed_offer_manifest
from tools.eos.auth.tenant_authorization import _BINDINGS


def test_signed_offer_manifest_is_canonical_and_commits_to_exact_offer_and_document():
    offer = SimpleNamespace(
        offer_id="OFFER-001",
        candidate_id="CAN-001",
        requisition_id="REQ-001",
        revision=7,
        fingerprint="f" * 64,
        terms=SimpleNamespace(
            to_dict=lambda: {"position_title": "Engineer", "currency": "ZAR"}
        ),
    )
    evidence = SimpleNamespace(
        evidence_id="EVD-001",
        evidence_version_id="VER-003",
        content_digest_sha3_512="a" * 128,
    )
    first = _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        offer=cast(EmploymentOffer, offer),
        evidence=evidence,
    )
    second = _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        offer=cast(EmploymentOffer, offer),
        evidence=evidence,
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
        offer_id="OFFER-001",
        candidate_id="CAN-001",
        requisition_id="REQ-001",
        revision=7,
        fingerprint="f" * 64,
        terms=SimpleNamespace(
            to_dict=lambda: {"position_title": "Engineer", "currency": "ZAR"}
        ),
    )
    evidence = SimpleNamespace(
        evidence_id="EVD-001",
        evidence_version_id="VER-003",
        content_digest_sha3_512="a" * 128,
    )
    baseline = _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        offer=cast(EmploymentOffer, offer),
        evidence=evidence,
    )
    changed_revision = SimpleNamespace(
        offer_id="OFFER-001",
        candidate_id="CAN-001",
        requisition_id="REQ-001",
        revision=8,
        fingerprint="e" * 64,
        terms=SimpleNamespace(
            to_dict=lambda: {"position_title": "Engineer", "currency": "ZAR"}
        ),
    )
    changed_terms = SimpleNamespace(
        offer_id="OFFER-001",
        candidate_id="CAN-001",
        requisition_id="REQ-001",
        revision=8,
        fingerprint="e" * 64,
        terms=SimpleNamespace(
            to_dict=lambda: {"position_title": "Director", "currency": "ZAR"}
        ),
    )
    changed_evidence = SimpleNamespace(
        evidence_id="EVD-001",
        evidence_version_id="VER-004",
        content_digest_sha3_512="b" * 128,
    )
    # Lifecycle revision changes on APPROVED -> SENT; it must not invalidate
    # a signature over unchanged, already-approved commercial terms.
    assert baseline == _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        offer=cast(EmploymentOffer, changed_revision),
        evidence=evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        offer=cast(EmploymentOffer, changed_terms),
        evidence=evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="WILSYTENANT-4CD2FZ4O",
        offer=cast(EmploymentOffer, offer),
        evidence=changed_evidence,
    )
    assert baseline != _signed_offer_manifest(
        tenant_id="CUSTOMER-TENANT-001",
        offer=cast(EmploymentOffer, offer),
        evidence=evidence,
    )


def test_offer_acceptance_fails_closed_before_persistence_until_identity_binding_is_governed(
    monkeypatch,
):
    import asyncio
    from datetime import datetime, timezone
    from types import SimpleNamespace

    from fastapi import FastAPI, HTTPException, Request

    import tools.eos.api.hiring_lifecycle_router as hiring

    def forbidden_transaction(_callback):
        pytest.fail("disabled acceptance must not open a persistence transaction")

    def forbidden_database():
        pytest.fail("disabled acceptance must not resolve a database")

    monkeypatch.setattr(hiring, "_transaction", forbidden_transaction)
    monkeypatch.setattr(hiring, "get_database", forbidden_database)

    app = FastAPI()
    request = Request(
        {
            "type": "http",
            "app": app,
            "headers": [],
            "query_string": b"",
            "path": "/api/hr/hiring/offers/OFFER-001/accept",
            "method": "POST",
            "server": ("testserver", 80),
            "scheme": "http",
            "client": ("test", 1),
        }
    )
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
        asyncio.run(
            hiring.accept_offer(
                "OFFER-001",
                body,
                request,
                "accept-001",
                cast(TenantAuthorizationContext, context),
            )
        )
    assert error.value.status_code == 503
    assert error.value.detail == "CANDIDATE_IDENTITY_BINDING_UNAVAILABLE"


def test_hiring_routes_bind_employer_authority_but_keep_admission_unmounted():
    """Employer route pairs and admission authorization stay separate."""
    import tools.eos.api.hiring_lifecycle_router as hiring

    expected = (
        (
            hiring._CANDIDATE_READ,
            "platform_employer:hiring_candidate:read",
            "platform_employer_hiring_candidate_read",
        ),
        (
            hiring._CANDIDATE_CREATE,
            "platform_employer:hiring_candidate:create",
            "platform_employer_hiring_candidate_create",
        ),
        (
            hiring._CANDIDATE_TRANSITION,
            "platform_employer:hiring_candidate:transition",
            "platform_employer_hiring_candidate_transition",
        ),
        (
            hiring._OFFER_READ,
            "platform_employer:hiring_offer:read",
            "platform_employer_hiring_offer_read",
        ),
        (
            hiring._OFFER_CREATE,
            "platform_employer:hiring_offer:create",
            "platform_employer_hiring_offer_create",
        ),
        (
            hiring._OFFER_SUBMIT,
            "platform_employer:hiring_offer:submit",
            "platform_employer_hiring_offer_submit",
        ),
        (
            hiring._OFFER_DECIDE,
            "platform_employer:hiring_offer:decide",
            "platform_employer_hiring_offer_decide",
        ),
        (
            hiring._OFFER_SEND,
            "platform_employer:hiring_offer:send",
            "platform_employer_hiring_offer_send",
        ),
        (
            hiring._OFFER_SIGN,
            "platform_employer:hiring_offer:sign",
            "platform_employer_hiring_offer_sign",
        ),
    )
    for dependency, permission_id, operation in expected:
        assert dependency.platform_employer_permission_id == permission_id
        assert dependency.platform_employer_operation == operation
        assert _BINDINGS[operation] == permission_id

    assert hiring._OFFER_ACCEPT.platform_employer_permission_id is None
    assert hiring._OFFER_ACCEPT.platform_employer_operation is None
    assert hiring._OFFER_ACCEPT.permission_id == "hr:hiring_offer:accept"
    assert hiring._OFFER_ACCEPT.operation == "hr_hiring_offer_accept"
    assert "platform_employer:hiring_offer:accept" not in _BINDINGS.values()
    assert (
        _BINDINGS.get("platform_employer_employee_admission_create")
        == "platform_employer:employee_admission:create"
    )
    assert not any(
        "admission" in route.path.lower() or "admission" in route.name.lower()
        for route in hiring.router.routes
    )


# ARTIFACT: tests/unit/test_hiring_signed_offer_manifest.py
# VERSION: v1.3.0-PLATFORM-EMPLOYEE-ADMISSION-AUTHORITY-BOUNDARY
# AUTHORITY BOUNDARY: Deterministic offer-manifest checks, exact employer route-pair contract, central admission permission binding, and disabled acceptance behavior only.
# TENANT POSTURE: Synthetic tenant identifiers; the shared EOS resolver restricts platform-employer authority to the canonical WILSY company tenant.
# FAIL-CLOSED POSTURE: Missing candidate identity proofing cannot create accepted offer state; no employee-admission route is exposed.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
