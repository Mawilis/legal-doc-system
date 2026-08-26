"""WILSY OS — VENDOR BILL RELEASE-AUTHORITY GUARD UNIT CERTIFICATION
Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORITY-GUARD-UNIT-CERT
Authority: Wilsy OS Core Governance
Classification: Institutional Unit Certification Artifact
Epitome: Certifies coordination-only VendorBill guard semantics.
Absolute path: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_vendor_bill_release_authority_guard.py
Collaboration: Wilson Khanyezi — Founder / Chief Architect; AI Engineering (Codex)
Date: 2026-08-27
CHANGELOG: v1.0.0 — initial release-authority guard certification matrix.
POPIA §19 | GDPR §32 | SOC2 CC7.2
APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
Kennel EOS remains the exclusive financial execution authority.
"""

from dataclasses import FrozenInstanceError, fields
from datetime import date, datetime, timezone
from typing import Any

import pytest

from tools.eos.saas.domain.vendor_bill import (
    VendorBill,
    VendorBillApprovalState,
    VendorBillDomainError,
    VendorBillObligationState,
)


def make_bill(**changes: Any) -> VendorBill:
    """Build a deterministic canonical VendorBill fixture."""
    values: dict[str, Any] = {
        "tenant_id": "tenant-a",
        "vendor_id": "vendor-a",
        "payable_id": "payable-a",
        "gross_amount_minor": 1000,
        "currency": "ZAR",
        "issue_date": date(2026, 1, 1),
        "due_date": date(2026, 1, 31),
        "received_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    values.update(changes)
    return VendorBill(**values)


def test_default_and_valid_guard_values() -> None:
    """Default and valid non-negative integer guard values are accepted."""
    assert make_bill().release_authority_guard_revision == 0
    for value in (0, 1, 2, 10**18):
        assert make_bill(release_authority_guard_revision=value).release_authority_guard_revision == value


@pytest.mark.parametrize("value", (-1, -100, True, False, 1.0, 1.5, "0", "1", None))
def test_invalid_guard_values_rejected(value: Any) -> None:
    """Guard input is strict integer metadata with no coercion."""
    with pytest.raises(VendorBillDomainError):
        make_bill(release_authority_guard_revision=value)


def test_guard_is_frozen_and_serialized() -> None:
    """The frozen guard is present in deterministic public serialization."""
    bill = make_bill(release_authority_guard_revision=7)
    with pytest.raises(FrozenInstanceError):
        bill.release_authority_guard_revision = 8  # type: ignore[misc]
    assert bill.to_dict()["release_authority_guard_revision"] == 7


def test_proof_boundary_excludes_guard_and_projection_fields() -> None:
    """Creation proof input excludes mutable projection and guard metadata."""
    first = make_bill(release_authority_guard_revision=0)
    second = make_bill(release_authority_guard_revision=9)
    assert "release_authority_guard_revision" not in first.evidence_payload()
    assert "approval_projection_revision" not in first.evidence_payload()
    assert "approval_effective_result_id" not in first.evidence_payload()
    assert first.evidence_payload() == second.evidence_payload()


def test_revision_dimensions_are_independent() -> None:
    """Obligation, approval, and release-authority revisions remain separate."""
    bill = make_bill(
        revision=7,
        approval_projection_revision=4,
        approval_effective_result_id="result-a",
        release_authority_guard_revision=9,
    )
    assert (bill.revision, bill.approval_projection_revision, bill.release_authority_guard_revision) == (7, 4, 9)


@pytest.mark.parametrize(
    "obligation_state,outstanding",
    [
        (VendorBillObligationState.DRAFT, 1000),
        (VendorBillObligationState.OPEN, 1000),
        (VendorBillObligationState.PARTIALLY_SETTLED, 400),
        (VendorBillObligationState.SETTLED, 0),
        (VendorBillObligationState.VOIDED, 0),
    ],
)
def test_guard_does_not_interfere_with_lifecycle(obligation_state: VendorBillObligationState, outstanding: int) -> None:
    """Changing only the guard cannot alter lifecycle or accounting dimensions."""
    bill = make_bill(obligation_state=obligation_state, outstanding_amount_minor=outstanding, release_authority_guard_revision=11)
    assert bill.obligation_state is obligation_state
    assert bill.approval_state is VendorBillApprovalState.NOT_REQUIRED
    assert bill.outstanding_amount_minor == outstanding
    assert bill.revision == 1
    assert bill.approval_projection_revision == 0
    assert bill.approval_effective_result_id is None


def test_guard_public_surface_has_no_execution_authority_fields() -> None:
    """Domain fields expose no reservation, payment, settlement, or execution controls."""
    names = {item.name for item in fields(VendorBill)}
    forbidden = {
        "reserved_amount_minor", "payment_destination", "provider_payment_id",
        "execution_status", "settlement_status", "paid", "kennel_invocation",
    }
    assert names.isdisjoint(forbidden)
    assert "release_authority_guard_revision" in names


# INSTITUTIONAL CERTIFICATION SEAL
# File: test_vendor_bill_release_authority_guard.py
# Version: v1.0.0-VENDOR-BILL-RELEASE-AUTHORITY-GUARD-UNIT-CERT
# Status: SOVEREIGN UNIT CERTIFICATION — R2B-03
# Authority: Wilsy OS Core Governance
# Architecture: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
# Kennel EOS: exclusive financial execution authority
# Runtime posture: PURE / NO DB / NO NETWORK / NO EXECUTION
# Compliance: POPIA §19 | GDPR §32 | SOC2 CC7.2
# Certification date: 2026-08-27
# Technical-control-only; no independent legal-compliance claim.
