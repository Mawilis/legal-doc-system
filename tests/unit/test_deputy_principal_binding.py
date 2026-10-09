"""Direct certificate for canonical deputy-principal identity binding.

TITLE: WILSY OS Deputy Principal Identity Binding Certificate
VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING-CERT
AUTHORITY: Direct adversarial certificate for the immutable L8-6B value.
EPITOME: Prove factory-only construction from exact canonical Deputy evidence,
         deterministic SHA3-512 provenance, strict input rejection, immutable
         value semantics, and absence of IAM, queue, service, AI, billing, or
         financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_deputy_principal_binding.py
COLLABORATION / OWNERSHIP: Certificate for deputy_principal_binding.py only;
                            P1 Deputy and IAM authorities remain independent.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING-CERT
           establishes exact provenance, direct-construction rejection,
           deterministic fingerprint, immutable behavior, malformed-input
           rejection, and authority-boundary proofs.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Binding tenant/deputy/office provenance is derived from P1.
AUTHORITY BOUNDARY: Certificate only; no IAM, queue, lifecycle mutation, AI,
                    billing, payment, execution, or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Any documentary construction or provenance/input drift
                         fails rather than producing binding truth.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tools.eos.legal_operations.domain.deputy_principal_binding import (
    VERSION as PRODUCTION_VERSION,
    DeputyPrincipalBinding,
    DeputyPrincipalBindingError,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy


VERSION = "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING-CERT"
NOW = datetime(2026, 9, 23, 15, 45, tzinfo=timezone.utc)


def _deputy(
    *,
    tenant_id: str = "tenant-a",
    deputy_id: str = "deputy-1",
    sheriff_office_id: str = "office-1",
) -> Deputy:
    """Build one canonical P1 Deputy for binding proofs."""
    return Deputy(
        tenant_id=tenant_id,
        deputy_id=deputy_id,
        sheriff_office_id=sheriff_office_id,
        display_name="Deputy One",
        badge_reference="badge-1",
        evidence_reference="deputy-directory-evidence",
    )


def _binding(
    *,
    principal_id: str = "principal-1",
    deputy: Deputy | None = None,
) -> DeputyPrincipalBinding:
    """Build one binding only through the public factory."""
    return DeputyPrincipalBinding.from_deputy(
        principal_id=principal_id,
        deputy=deputy or _deputy(),
        bound_at=NOW,
        evidence_reference="principal-deputy-binding-evidence",
    )


def _expect(code: str, operation: object) -> None:
    """Assert one stable binding validation code."""
    with pytest.raises(DeputyPrincipalBindingError) as caught:
        operation()  # type: ignore[operator]
    assert caught.value.code == code
    assert str(caught.value) == code


def test_factory_derives_all_deputy_provenance_and_fingerprint() -> None:
    """Caller supplies principal/evidence only; Deputy provenance is derived."""
    deputy = _deputy()
    value = _binding(deputy=deputy)

    assert value.tenant_id == deputy.tenant_id
    assert value.principal_id == "principal-1"
    assert value.deputy_id == deputy.deputy_id
    assert value.sheriff_office_id == deputy.sheriff_office_id
    assert value.deputy_fingerprint == deputy.fingerprint
    assert value.bound_at == NOW
    assert value.evidence_reference == "principal-deputy-binding-evidence"
    assert len(value.fingerprint) == 128
    int(value.fingerprint, 16)

    payload = value.to_dict()
    assert payload == {
        "schema": "WILSY-LEGAL-OPERATIONS-DEPUTY-PRINCIPAL-BINDING/V1",
        "version": PRODUCTION_VERSION,
        "tenant_id": "tenant-a",
        "principal_id": "principal-1",
        "deputy_id": "deputy-1",
        "sheriff_office_id": "office-1",
        "deputy_fingerprint": deputy.fingerprint,
        "bound_at": NOW.isoformat(),
        "evidence_reference": "principal-deputy-binding-evidence",
        "fingerprint": value.fingerprint,
    }


def test_direct_documentary_construction_is_rejected() -> None:
    """No caller can manufacture tenant/deputy provenance field-by-field."""
    _expect(
        "L8_6B_FACTORY_REQUIRED",
        lambda: DeputyPrincipalBinding(
            tenant_id="tenant-a",
            principal_id="principal-1",
            deputy_id="deputy-1",
            sheriff_office_id="office-1",
            deputy_fingerprint="a" * 128,
            bound_at=NOW,
            evidence_reference="evidence",
        ),
    )


def test_binding_is_frozen_and_deterministic() -> None:
    """Equal canonical inputs yield equal fingerprints and immutable values."""
    first = _binding()
    second = _binding()
    assert first == second
    assert first.fingerprint == second.fingerprint

    with pytest.raises(FrozenInstanceError):
        first.principal_id = "principal-2"  # type: ignore[misc]


def test_principal_timestamp_reference_and_runtime_type_fail_closed() -> None:
    """Malformed caller inputs and Deputy subclasses cannot become bindings."""
    for principal in ("", " principal-1", "principal 1", "*"):
        _expect(
            "L8_6B_PRINCIPAL_ID_INVALID",
            lambda principal=principal: DeputyPrincipalBinding.from_deputy(
                principal_id=principal,
                deputy=_deputy(),
                bound_at=NOW,
                evidence_reference="evidence",
            ),
        )

    _expect(
        "L8_6B_BOUND_AT_INVALID",
        lambda: DeputyPrincipalBinding.from_deputy(
            principal_id="principal-1",
            deputy=_deputy(),
            bound_at=datetime(2026, 9, 23, 15, 45),
            evidence_reference="evidence",
        ),
    )
    _expect(
        "L8_6B_EVIDENCE_REFERENCE_INVALID",
        lambda: DeputyPrincipalBinding.from_deputy(
            principal_id="principal-1",
            deputy=_deputy(),
            bound_at=NOW,
            evidence_reference=" evidence ",
        ),
    )

    class DeputyProxy(Deputy):
        pass

    proxy = DeputyProxy(
        tenant_id="tenant-a",
        deputy_id="deputy-1",
        sheriff_office_id="office-1",
        display_name="Deputy One",
        badge_reference="badge-1",
        evidence_reference="deputy-directory-evidence",
    )
    _expect(
        "L8_6B_DEPUTY_REQUIRED",
        lambda: DeputyPrincipalBinding.from_deputy(
            principal_id="principal-1",
            deputy=proxy,
            bound_at=NOW,
            evidence_reference="evidence",
        ),
    )


def test_fingerprint_changes_with_principal_deputy_or_binding_evidence() -> None:
    """Identity/evidence drift cannot preserve one binding fingerprint."""
    baseline = _binding()
    other_principal = _binding(principal_id="principal-2")
    other_deputy = _binding(
        deputy=_deputy(deputy_id="deputy-2"),
    )
    other_time = DeputyPrincipalBinding.from_deputy(
        principal_id="principal-1",
        deputy=_deputy(),
        bound_at=datetime(2026, 9, 23, 15, 46, tzinfo=timezone.utc),
        evidence_reference="principal-deputy-binding-evidence",
    )
    other_evidence = DeputyPrincipalBinding.from_deputy(
        principal_id="principal-1",
        deputy=_deputy(),
        bound_at=NOW,
        evidence_reference="different-binding-evidence",
    )

    fingerprints = {
        baseline.fingerprint,
        other_principal.fingerprint,
        other_deputy.fingerprint,
        other_time.fingerprint,
        other_evidence.fingerprint,
    }
    assert len(fingerprints) == 5


def test_binding_carries_no_iam_queue_service_ai_or_financial_authority() -> None:
    """Serialized identity evidence cannot masquerade as an access/command grant."""
    payload = _binding().to_dict()
    keys = {str(key).casefold() for key in payload}
    for forbidden in {
        "permission",
        "role_id",
        "business_role",
        "authorized",
        "queue",
        "attempt_id",
        "service_execution_id",
        "return_id",
        "client_id",
        "ai_score",
        "invoice_id",
        "payment",
        "settlement",
        "bank_execution",
        "provider_execution",
    }:
        assert forbidden not in keys

    assert PRODUCTION_VERSION == "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING"
    assert VERSION == "v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING-CERT"


# ARTIFACT: test_deputy_principal_binding.py
# VERSION: v1.0.0-L8-6B-DEPUTY-PRINCIPAL-IDENTITY-BINDING-CERT
# AUTHORITY BOUNDARY: direct immutable deputy-principal binding value certificate only
# TENANT POSTURE: provenance derives from exact canonical Deputy evidence
# FAIL-CLOSED POSTURE: direct construction, malformed input, type drift, and authority leakage fail
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
