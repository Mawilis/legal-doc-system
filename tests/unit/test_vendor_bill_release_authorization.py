"""WILSY OS — VENDOR BILL RELEASE AUTHORIZATION UNIT CERTIFICATION
Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-UNIT-CERT
Authority: Wilsy OS Core Governance
Classification: Institutional Artifact — Production Certification
EPITOME: Pure-domain certification of immutable release evidence.
ABSOLUTE PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_vendor_bill_release_authorization.py
PRIMARY CONTRACT: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/vendor_bill_release_authorization.py
ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
KENNEL EOS: no execution here; it remains the exclusive financial authority.
COLLABORATION: Wilson Khanyezi — Founder / Chief Architect; AI Engineering (Codex)
Date: 2026-08-26
CHANGELOG: 2026-08-26 — initial sovereign pure-domain certification suite.
COMPLIANCE: POPIA §19 | GDPR §32 | SOC2 CC7.2
"""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.saas.domain.vendor_bill_release_authorization import (
    VendorBillReleaseAuthorization,
    VendorBillReleaseAuthorizationDomainError,
)


def make_valid_authorization() -> VendorBillReleaseAuthorization:
    """Description: create deterministic valid evidence.

    Collaboration: supplies the canonical fixture for the production contract.
    Institutional: fixed values make certification reproducible and pure.
    Returns: a valid immutable authorization.
    """
    moment = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    return VendorBillReleaseAuthorization(
        tenant_id="tenant-a",
        release_authorization_id="release-a",
        payable_id="payable-a",
        vendor_bill_revision=1,
        approval_effective_result_id="result-a",
        approval_effective_result_fingerprint="a" * 128,
        authorized_amount_minor=100,
        currency="ZAR",
        authorized_by_actor_id="actor-a",
        authorization_basis_reference="basis-a",
        authorized_at=moment,
        created_at=moment,
    )


def test_valid_construction_and_utc_normalization() -> None:
    """Description: valid evidence constructs and timestamps are UTC-aware.

    Institutional: the contract preserves scope while canonicalizing time.
    """
    offset = timezone(timedelta(hours=2))
    item = replace(
        make_valid_authorization(),
        authorized_at=datetime(2026, 1, 1, 14, tzinfo=offset),
        created_at=datetime(2026, 1, 1, 14, tzinfo=offset),
    )
    assert item.tenant_id == "tenant-a"
    assert item.authorized_at.tzinfo == timezone.utc
    assert item.created_at.tzinfo == timezone.utc


def test_frozen_immutability() -> None:
    """Description: certified evidence cannot be mutated after construction.

    Institutional: immutability prevents post-approval authority drift.
    """
    with pytest.raises(FrozenInstanceError):
        setattr(make_valid_authorization(), "payable_id", "other")


def test_persistence_round_trip_and_determinism() -> None:
    """Description: persistence serialization is exact and deterministic.

    Collaboration: future registries can hydrate the same evidence safely.
    Institutional: fixed keys prevent silent schema drift.
    """
    item = make_valid_authorization()
    first = item.to_persistence_dict()
    second = make_valid_authorization().to_persistence_dict()
    expected = {
        "schema", "tenant_id", "release_authorization_id", "payable_id",
        "vendor_bill_revision", "approval_effective_result_id",
        "approval_effective_result_fingerprint", "authorized_amount_minor",
        "currency", "authorized_by_actor_id", "authorization_basis_reference",
        "authorized_at", "created_at",
    }
    assert first == second
    assert set(first) == expected
    assert VendorBillReleaseAuthorization.from_persistence_dict(first) == item


@pytest.mark.parametrize("field_name", [
    "tenant_id", "release_authorization_id", "payable_id",
    "approval_effective_result_id", "authorized_by_actor_id",
    "authorization_basis_reference",
])
def test_required_text_rejects_empty_values(field_name: str) -> None:
    """Description: required identity text rejects empty and whitespace input.

    Institutional: blank bindings cannot establish financial authority.
    """
    for value in ("", "   "):
        with pytest.raises(VendorBillReleaseAuthorizationDomainError):
            replace(make_valid_authorization(), **{field_name: value})


@pytest.mark.parametrize("field_name, maximum", [
    ("tenant_id", 128), ("release_authorization_id", 80), ("payable_id", 80),
    ("approval_effective_result_id", 80), ("authorized_by_actor_id", 120),
    ("authorization_basis_reference", 240),
])
def test_text_length_boundaries(field_name: str, maximum: int) -> None:
    """Description: each institutional text limit is enforced exactly.

    Institutional: overflow is rejected rather than truncated.
    """
    replace(make_valid_authorization(), **{field_name: "x" * maximum})
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        replace(make_valid_authorization(), **{field_name: "x" * (maximum + 1)})


@pytest.mark.parametrize("field_name", ["vendor_bill_revision", "authorized_amount_minor"])
def test_numeric_invariants(field_name: str) -> None:
    """Description: financial integers reject bool, zero, and negatives.

    Institutional: bool is explicitly rejected because it subclasses int.
    """
    for value in (True, False, 0, -1):
        with pytest.raises(VendorBillReleaseAuthorizationDomainError):
            replace(make_valid_authorization(), **{field_name: value})
    replace(make_valid_authorization(), **{field_name: 1})


@pytest.mark.parametrize("currency", ["zar", "US", "ZARR", "Z1R", "12A", "", 1])
def test_currency_is_strict(currency: Any) -> None:
    """Description: currency requires exact uppercase three-letter ASCII.

    Institutional: caller input is never silently auto-uppercased.
    """
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        replace(make_valid_authorization(), currency=currency)
    replace(make_valid_authorization(), currency="ZAR")


@pytest.mark.parametrize("fingerprint", ["a" * 127, "a" * 129, "A" * 128, "g" * 128, "", 1])
def test_fingerprint_is_exact_sha3_512_hex(fingerprint: Any) -> None:
    """Description: approval evidence requires lowercase 128-character hex.

    Institutional: exact SHA3-512 shape prevents ambiguous evidence binding.
    """
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        replace(make_valid_authorization(), approval_effective_result_fingerprint=fingerprint)


def test_time_invariants() -> None:
    """Description: timestamps require awareness and chronological creation.

    Institutional: UTC normalization makes comparisons deterministic.
    """
    item = make_valid_authorization()
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        replace(item, authorized_at=datetime(2026, 1, 1))
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        replace(item, created_at=datetime(2026, 1, 1))
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        replace(item, created_at=item.authorized_at - timedelta(seconds=1))
    assert replace(item, created_at=item.authorized_at).created_at == item.authorized_at


def test_strict_persistence_and_execution_boundary() -> None:
    """Description: hydration rejects schema drift and execution-bearing fields.

    Collaboration: hydration reconstructs domain evidence only; no Kennel call occurs.
    Institutional: amount and currency are authorization scope, not settlement proof.
    """
    payload = make_valid_authorization().to_persistence_dict()
    missing = dict(payload)
    missing.pop("payable_id")
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        VendorBillReleaseAuthorization.from_persistence_dict(missing)
    for mutation in ({"extra": "x"}, {"schema": "wrong"}):
        candidate = {**payload, **mutation}
        with pytest.raises(VendorBillReleaseAuthorizationDomainError):
            VendorBillReleaseAuthorization.from_persistence_dict(candidate)
    with pytest.raises(VendorBillReleaseAuthorizationDomainError):
        non_mapping: Any = None
        VendorBillReleaseAuthorization.from_persistence_dict(non_mapping)
    forbidden = {
        "bank_account", "account_number", "payment_destination", "payment_rail",
        "execution_id", "execution_status", "settlement_id", "settlement_status",
        "paid_at", "settled_at", "provider_response", "transaction_reference",
    }
    assert forbidden.isdisjoint(payload)
    assert forbidden.isdisjoint(VendorBillReleaseAuthorization.__dataclass_fields__)
    assert make_valid_authorization().authorized_amount_minor == 100


# INSTITUTIONAL CERTIFICATION SEAL
# File: test_vendor_bill_release_authorization.py
# Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORIZATION-UNIT-CERT
# Status: SOVEREIGN UNIT CERTIFICATION — R2B-01
# Authority: Wilsy OS Core Governance | Primary contract: vendor_bill_release_authorization.py
# Architecture: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
# Runtime posture: PURE / NO DB / NO NETWORK / NO KENNEL EXECUTION
# Compliance: POPIA §19 | GDPR §32 | SOC2 CC7.2 | Certification date: 2026-08-26
