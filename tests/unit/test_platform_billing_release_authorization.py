"""WILSY OS — PLATFORM BILLING RELEASE AUTHORIZATION DIRECT CERT

TITLE: Platform Billing Release Authorization Domain Direct Certificate
VERSION: v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN-CERT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify the immutable value and persistence-shape contract only.
EPITOME: Direct structural certification; no persistence, authorization
issuance, financial execution, or real-world settlement claim.
ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_release_authorization.py
CERTIFICATION / UPDATE DATE: 2026-09-04
FINANCIAL AUTHORITY BOUNDARY:
  APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED.
  Kennel EOS remains the exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from tools.eos.saas.domain.platform_billing_release_authorization import (
    SCHEMA,
    VERSION,
    PlatformBillingReleaseAuthorization,
    PlatformBillingReleaseAuthorizationDomainError,
)


TEST_VERSION = (
    "v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN-CERT"
)
EXPECTED_VERSION = (
    "v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN"
)

AUTHORIZED_AT = datetime(
    2026,
    9,
    4,
    4,
    0,
    tzinfo=timezone.utc,
)


def authorization(
    **changes: Any,
) -> PlatformBillingReleaseAuthorization:
    """Build deterministic valid immutable release evidence."""
    values: dict[str, Any] = {
        "tenant_id": "TENANT-R3C",
        "release_authorization_id": "PBRA-R3C-001",
        "platform_invoice_id": "WILSYINV-R3C-001",
        "platform_invoice_evidence_fingerprint":
            "a" * 128,
        "authorization_evidence_reference":
            "platform-collection-authority:R3C:001",
        "authorization_evidence_fingerprint":
            "b" * 128,
        "authorized_amount_minor": 12500,
        "currency": "ZAR",
        "authorized_by_principal_id":
            "PRINCIPAL-R3C",
        "authorization_basis_reference":
            "POLICY-R3C-001",
        "payment_destination_reference": "DESTINATION-R3C-001",
        "idempotency_key": "IDEMPOTENCY-R3C-001",
        "authorized_at": AUTHORIZED_AT,
        "created_at": AUTHORIZED_AT,
    }

    values.update(changes)

    return PlatformBillingReleaseAuthorization(
        **values
    )


def test_version_and_schema_contract() -> None:
    assert TEST_VERSION == "v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN-CERT"
    assert VERSION == EXPECTED_VERSION
    assert SCHEMA == (
        "WILSY-PLATFORM-BILLING-RELEASE-AUTHORIZATION/V2"
    )


def test_valid_authorization_preserves_exact_scope() -> None:
    evidence = authorization()

    assert evidence.tenant_id == "TENANT-R3C"
    assert evidence.platform_invoice_id == (
        "WILSYINV-R3C-001"
    )
    assert evidence.authorized_amount_minor == 12500
    assert evidence.currency == "ZAR"
    assert evidence.payment_destination_reference == "DESTINATION-R3C-001"
    assert evidence.idempotency_key == "IDEMPOTENCY-R3C-001"
    assert len(evidence.release_authorization_fingerprint) == 128
    assert evidence.release_authorization_fingerprint == evidence.fingerprint

def test_release_fingerprint_is_deterministic_and_semantic() -> None:
    baseline = authorization().fingerprint
    assert baseline == authorization().fingerprint
    assert baseline != authorization(authorized_amount_minor=12501).fingerprint
    assert baseline != authorization(payment_destination_reference="DESTINATION-R3C-002").fingerprint
    assert baseline != authorization(idempotency_key="IDEMPOTENCY-R3C-002").fingerprint


def test_persistence_shape_is_exact_and_round_trips() -> None:
    evidence = authorization()
    payload = evidence.to_persistence_dict()

    assert set(payload) == {
        "schema",
        "tenant_id",
        "release_authorization_id",
        "platform_invoice_id",
        "platform_invoice_evidence_fingerprint",
        "authorization_evidence_reference",
        "authorization_evidence_fingerprint",
        "authorized_amount_minor",
        "currency",
        "authorized_by_principal_id",
        "authorization_basis_reference",
        "authorized_at",
        "created_at",
        "payment_destination_reference",
        "idempotency_key",
        "release_authorization_fingerprint",
    }

    assert (
        PlatformBillingReleaseAuthorization
        .from_persistence_dict(payload)
        == evidence
    )


def test_contract_is_frozen() -> None:
    evidence = authorization()

    with pytest.raises(FrozenInstanceError):
        evidence.currency = "USD"  # type: ignore[misc]


@pytest.mark.parametrize(
    "field",
    (
        "tenant_id",
        "release_authorization_id",
        "platform_invoice_id",
        "authorization_evidence_reference",
        "authorized_by_principal_id",
        "authorization_basis_reference",
    ),
)
def test_required_text_fails_closed(
    field: str,
) -> None:
    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        authorization(
            **{field: "   "}
        )


@pytest.mark.parametrize(
    "field",
    (
        "platform_invoice_evidence_fingerprint",
        "authorization_evidence_fingerprint",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        "",
        "a" * 127,
        "A" * 128,
        "g" * 128,
    ),
)
def test_fingerprints_are_exact_lowercase_sha3_512(
    field: str,
    value: str,
) -> None:
    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        authorization(
            **{field: value}
        )


@pytest.mark.parametrize(
    "value",
    (
        0,
        -1,
        True,
        1.5,
    ),
)
def test_authorized_amount_minor_is_positive_integer(
    value: object,
) -> None:
    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        authorization(
            authorized_amount_minor=value
        )


@pytest.mark.parametrize(
    "value",
    (
        "zar",
        "US",
        "USDD",
        "12A",
        "",
    ),
)
def test_currency_is_strict_uppercase_iso_shape(
    value: str,
) -> None:
    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        authorization(
            currency=value
        )


def test_timestamps_require_timezone_awareness() -> None:
    naive = AUTHORIZED_AT.replace(
        tzinfo=None
    )

    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        authorization(
            authorized_at=naive
        )

    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        authorization(
            created_at=naive
        )


def test_creation_cannot_precede_authorization() -> None:
    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        authorization(
            created_at=(
                AUTHORIZED_AT
                - timedelta(seconds=1)
            )
        )


@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "extra",
        "schema",
    ),
)
def test_persistence_hydration_is_strict(
    mutation: str,
) -> None:
    payload = authorization().to_persistence_dict()

    if mutation == "missing":
        payload.pop(
            "authorization_basis_reference"
        )
    elif mutation == "extra":
        payload["execution_status"] = "succeeded"
    else:
        payload["schema"] = "WRONG"

    with pytest.raises(
        PlatformBillingReleaseAuthorizationDomainError
    ):
        PlatformBillingReleaseAuthorization.from_persistence_dict(
            payload
        )


def test_execution_and_destination_truth_are_absent() -> None:
    payload = authorization().to_persistence_dict()

    forbidden = {
        "provider",
        "provider_execution_reference",
        "execution_status",
        "executed_at",
        "settled_at",
        "settlement_id",
    }

    assert forbidden.isdisjoint(
        payload
    )

@pytest.mark.parametrize("value", ("BANK-001", "account-ref", "card-token", "secret-ref", "credential-x", "password-ref"))
def test_destination_rejects_sensitive_looking_reference(value: str) -> None:
    with pytest.raises(PlatformBillingReleaseAuthorizationDomainError):
        authorization(payment_destination_reference=value)


def test_source_has_no_io_or_kennel_dependency() -> None:
    path = Path(
        "tools/eos/saas/domain/"
        "platform_billing_release_authorization.py"
    )

    source = path.read_text(
        encoding="utf-8"
    ).lower()

    for token in (
        "pymongo",
        "requests",
        "httpx",
        "subprocess",
        "tools.eos.kennel",
    ):
        assert token not in source


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT:
#   test_platform_billing_release_authorization.py
# VERSION:
#   v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-DOMAIN-CERT
# CERTIFICATION:
#   Direct immutable-domain contract only.
# REAL-WORLD PERSISTENCE CLAIM:
#   NONE.
# FINANCIAL EXECUTION CLAIM:
#   NONE.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
