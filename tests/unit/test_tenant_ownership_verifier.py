"""Unit contract for deny-only Issue #300 ownership verification.

TITLE: Tenant Ownership Verifier Contract Certificate
VERSION: v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CERT
AUTHORITY: Validate verifier shape only; no ownership or issuer authority.
EPITOME: Prove malformed scope and unavailable issuer authority cannot yield a
         successful tenant-ownership evidence result.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_ownership_verifier.py
COLLABORATION / OWNERSHIP: Certificate for tools/eos/auth/tenant_ownership_verifier.py.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG: v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CERT verifies exact request validation, unavailable-only verifier behavior, and rejection of public positive-result construction.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers; no issuer or trust-root fixture.
TENANT BOUNDARY: Exact synthetic tenant, legal entity and principal only.
AUTHORITY BOUNDARY: Unit evidence only; no ownership, IAM or tenant lifecycle grant.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools.eos.auth.tenant_ownership_verifier import (
    TenantOwnershipEvidenceVerifier,
    TenantOwnershipOperation,
    TenantOwnershipVerificationError,
    TenantOwnershipVerificationRequest,
    UnavailableTenantOwnershipEvidenceVerifier,
    VerifiedTenantOwnershipEvidence,
)


VERSION = "v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CERT"


def _request(**overrides: object) -> TenantOwnershipVerificationRequest:
    """Construct one synthetic exact-scope verification request."""
    values: dict[str, object] = {
        "tenant_id": "tenant-synthetic",
        "legal_entity_reference": "entity-synthetic",
        "principal_id": "principal-synthetic",
        "operation": TenantOwnershipOperation.TENANT_GENESIS,
        "evaluated_at": datetime(2026, 11, 2, tzinfo=timezone.utc),
    }
    values.update(overrides)
    return TenantOwnershipVerificationRequest(**values)  # type: ignore[arg-type]


def test_request_binds_exact_identifiers_and_normalizes_aware_time() -> None:
    """The request is immutable scope only and normalizes its explicit instant."""
    request = _request(
        evaluated_at=datetime(2026, 11, 2, 2, tzinfo=timezone.utc)
    )

    assert request.tenant_id == "tenant-synthetic"
    assert request.legal_entity_reference == "entity-synthetic"
    assert request.principal_id == "principal-synthetic"
    assert request.evaluated_at == datetime(2026, 11, 2, 2, tzinfo=timezone.utc)
    with pytest.raises((AttributeError, TypeError)):
        request.tenant_id = "tenant-other"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("tenant_id", "global", "TENANT_OWNERSHIP_TENANT_ID_INVALID"),
        ("principal_id", "", "TENANT_OWNERSHIP_PRINCIPAL_ID_INVALID"),
        (
            "evaluated_at",
            datetime(2026, 11, 2),
            "TENANT_OWNERSHIP_EVALUATED_AT_INVALID",
        ),
        (
            "operation",
            "TENANT_GENESIS",
            "TENANT_OWNERSHIP_OPERATION_INVALID",
        ),
    ],
)
def test_malformed_or_ambiguous_scope_is_rejected(
    field: str,
    value: object,
    code: str,
) -> None:
    """Caller input cannot widen tenant scope or substitute enum/time types."""
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        _request(**{field: value})

    assert raised.value.code == code


def test_unavailable_verifier_denies_even_well_formed_request() -> None:
    """No configured issuer means no positive result for any operation."""
    verifier = UnavailableTenantOwnershipEvidenceVerifier()
    request = _request(operation=TenantOwnershipOperation.OWNERSHIP_TRANSFER)

    assert isinstance(verifier, TenantOwnershipEvidenceVerifier)
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        verifier.verify(request)

    assert raised.value.code == "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"


def test_successful_result_has_no_public_constructor() -> None:
    """Protocol-shaped values and caller documents cannot self-issue success."""
    with pytest.raises(TenantOwnershipVerificationError) as raised:
        VerifiedTenantOwnershipEvidence()

    assert raised.value.code == "OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE"


# ARTIFACT: test_tenant_ownership_verifier.py
# VERSION: v1.0.0-ISSUE-300-OWNERSHIP-VERIFIER-CERT
# AUTHORITY BOUNDARY: typed-contract evidence only; no trust root
# TENANT POSTURE: synthetic scope only
# FAIL-CLOSED POSTURE: missing issuer authority and public success construction deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
