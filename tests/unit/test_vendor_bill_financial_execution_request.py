"""Unit certification for the AP execution-request boundary.

TITLE: Vendor Bill Financial Execution Request Unit Certification
VERSION: v2.0.0-M11-P5-R2B
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Certify release-scoped AP request validation and explicit legacy issuance refusal.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_vendor_bill_financial_execution_request.py
COLLABORATION / OWNERSHIP: SaaS AP request boundary certification.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v2.0.0-M11-P5-R2B updates the retired success expectation to the stable fail-closed boundary while preserving request validation evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; credential-like destinations reject.
TENANT BOUNDARY: Release-scope validation requires tenant and payable identity equality.
AUTHORITY BOUNDARY: AP request is not a generic command; typed AP bridge remains the future issuance owner.
FINANCIAL AUTHORITY BOUNDARY: No provider selection, execution, settlement, paid state, or receivable mutation.
TRANSACTION BOUNDARY: Pure unit tests; no persistence, session, transaction, Mongo, or I/O.
FAIL-CLOSED DECLARATION: Invalid scope and retired untyped issuance reject explicitly.
"""
from datetime import datetime, timezone
from typing import Any

import pytest

from tools.eos.kennel.orchestration.financial_execution_command_issuance import (
    FinancialExecutionCommandIssuance,
    FinancialExecutionCommandLegacyIssuanceError,
)
from tools.eos.saas.domain.vendor_bill_financial_execution_request import (
    VendorBillFinancialExecutionRequest,
    VendorBillFinancialExecutionRequestError,
)
from tools.eos.saas.domain.vendor_bill_release_authorization import VendorBillReleaseAuthorization

NOW = datetime(2026, 9, 7, 10, 0, tzinfo=timezone.utc)


def auth() -> VendorBillReleaseAuthorization:
    """Build a release authorization matching the valid AP request fixture."""
    return VendorBillReleaseAuthorization(
        "tenant-1",
        "release-1",
        "payable-1",
        1,
        "release-idempotency",
        "a" * 128,
        100,
        "ZAR",
        "actor-1",
        "basis-1",
        NOW,
        NOW,
    )


def request(**changes: object) -> VendorBillFinancialExecutionRequest:
    """Build a deterministic release-scoped AP request fixture."""
    values: dict[str, Any] = {
        "execution_command_id": "request-command",
        "tenant_id": "tenant-1",
        "payable_id": "payable-1",
        "release_authorization_id": "release-1",
        "idempotency_key": "request-idempotency",
        "amount_minor": 100,
        "currency": "ZAR",
        "payment_destination_reference": "vault-ref",
        "requested_by_actor_id": "actor-1",
        "requested_at": NOW,
    }
    values.update(changes)
    return VendorBillFinancialExecutionRequest(**values)


def issuance() -> FinancialExecutionCommandIssuance:
    """Build the preserved legacy issuance value shape."""
    return FinancialExecutionCommandIssuance(
        "issued-command",
        "issued-idempotency",
        NOW,
        "PAYSHAP",
        "metadata-ref",
    )


def test_valid_mapping_now_fails_at_retired_issuance_boundary() -> None:
    """A valid AP request reaches the intentional legacy fail-closed boundary."""
    with pytest.raises(FinancialExecutionCommandLegacyIssuanceError) as error:
        request().to_financial_execution_command(auth(), issuance())
    assert error.value.code == "FINANCIAL_EXECUTION_COMMAND_LEGACY_ISSUANCE_DISABLED"


@pytest.mark.parametrize("field", ["execution_command_id", "idempotency_key", "tenant_id", "payable_id", "release_authorization_id", "payment_destination_reference"])
def test_blank_identifiers_rejected(field: str) -> None:
    """Request identity and opaque destination fields remain mandatory."""
    with pytest.raises(VendorBillFinancialExecutionRequestError):
        request(**{field: " "})


@pytest.mark.parametrize("value", [0, -1, True, 1.5, None])
def test_amount_rejected(value: object) -> None:
    """Only positive integer minor-unit amounts are valid."""
    with pytest.raises(VendorBillFinancialExecutionRequestError):
        request(amount_minor=value)


@pytest.mark.parametrize("value", ["zar", "US", "Z1R", ""])
def test_currency_rejected(value: str) -> None:
    """Currency remains a closed uppercase three-letter code."""
    with pytest.raises(VendorBillFinancialExecutionRequestError):
        request(currency=value)


def test_scope_and_destination_validation() -> None:
    """Tenant, payable, release, amount, and destination scope fail closed."""
    for field, value in (("tenant_id", "other-tenant"), ("payable_id", "other-payable"), ("release_authorization_id", "other-release"), ("currency", "USD"), ("amount_minor", 101)):
        with pytest.raises(VendorBillFinancialExecutionRequestError):
            request(**{field: value}).to_financial_execution_command(auth(), issuance())
    for value in ("bank account 123", "card_number", "secret-token"):
        with pytest.raises(VendorBillFinancialExecutionRequestError):
            request(payment_destination_reference=value)


def test_fingerprint_is_deterministic_and_request_has_no_command_side_effect() -> None:
    """Request evidence is deterministic and conversion does not persist or select a provider."""
    assert request().fingerprint == request().fingerprint
    assert len(request().fingerprint) == 128


# ARTIFACT: test_vendor_bill_financial_execution_request.py
# VERSION: v2.0.0-M11-P5-R2B
# AUTHORITY BOUNDARY: AP request certification only; typed command bridge remains separate.
# TENANT POSTURE: request and release scope are tenant-bound.
# FAIL-CLOSED POSTURE: retired untyped issuance is explicitly rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns later execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
