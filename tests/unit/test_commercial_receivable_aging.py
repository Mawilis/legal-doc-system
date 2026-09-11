"""WILSY OS M11C commercial receivable aging certificate.
TITLE: Commercial Receivable Aging Unit Certificate
VERSION: v1.0.0-M11C
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic explicit-clock aging behavior and strict evidence hydration.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_commercial_receivable_aging.py
COLLABORATION / OWNERSHIP: M11C aging unit-certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11C certifies bucket boundaries, isolation, and fingerprints.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only.
TENANT BOUNDARY: Tests preserve tenant and family provenance.
AUTHORITY BOUNDARY: Projection evidence only.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, or settlement authority.
TRANSACTION BOUNDARY: Pure unit tests; no persistence.
FAIL-CLOSED DECLARATION: Invalid clocks, schema, and fingerprints must reject.
"""
from datetime import datetime, timezone, timedelta
import pytest
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.domain.commercial_receivable_aging import AgingBucket, CommercialReceivableAging, CommercialReceivableAgingError

def receivable(amount: int = 1000) -> CommercialReceivable:
    return CommercialReceivable("tenant-a", ReceivableFamily.CLIENT, "r-1", "invoice-1", "ZAR", amount, 0, amount, "a" * 128, ReceivableStatus.OPEN)

def test_a01_current_and_zero_balance_are_not_delinquent() -> None:
    now = datetime(2026, 1, 31, tzinfo=timezone.utc)
    current = CommercialReceivableAging.from_receivable(receivable(), now + timedelta(days=1), now)
    zero = CommercialReceivableAging.from_receivable(receivable(0), now - timedelta(days=90), now)
    assert current.bucket is AgingBucket.CURRENT and current.overdue_days == 0
    assert zero.bucket is AgingBucket.CURRENT and zero.overdue_days == 0

@pytest.mark.parametrize(("days", "bucket"), [(1, AgingBucket.DAYS_1_30), (30, AgingBucket.DAYS_1_30), (31, AgingBucket.DAYS_31_60), (60, AgingBucket.DAYS_31_60), (61, AgingBucket.DAYS_61_90), (90, AgingBucket.DAYS_61_90), (91, AgingBucket.DAYS_90_PLUS)])
def test_a02_bucket_boundaries(days: int, bucket: AgingBucket) -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    value = CommercialReceivableAging.from_receivable(receivable(), as_of - timedelta(days=days), as_of)
    assert value.overdue_days == days and value.bucket is bucket

def test_a03_deterministic_round_trip_and_no_mongo_id() -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    value = CommercialReceivableAging.from_receivable(receivable(), as_of - timedelta(days=31), as_of)
    payload = value.to_dict()
    assert CommercialReceivableAging.from_dict(payload) == value
    with pytest.raises(CommercialReceivableAgingError): CommercialReceivableAging.from_dict({**payload, "_id": "x"})

def test_a04_rejects_unknown_or_tampered_payload() -> None:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    payload = CommercialReceivableAging.from_receivable(receivable(), as_of - timedelta(days=1), as_of).to_dict()
    with pytest.raises(CommercialReceivableAgingError): CommercialReceivableAging.from_dict({**payload, "extra": 1})
    with pytest.raises(CommercialReceivableAgingError): CommercialReceivableAging.from_dict({**payload, "outstanding_amount_minor": 9})

def test_a05_naive_clock_rejected_and_tenant_isolation_preserved() -> None:
    with pytest.raises(CommercialReceivableAgingError): CommercialReceivableAging.from_receivable(receivable(), datetime(2026, 1, 1), datetime(2026, 1, 2, tzinfo=timezone.utc))
    other = CommercialReceivable("tenant-b", ReceivableFamily.PLATFORM, "r-2", "invoice-2", "ZAR", 1000, 0, 1000, "b" * 128, ReceivableStatus.OPEN)
    value = CommercialReceivableAging.from_receivable(other, datetime(2025, 12, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert value.tenant_id == "tenant-b" and value.receivable_family is ReceivableFamily.PLATFORM

# ARTIFACT: test_commercial_receivable_aging.py
# VERSION: v1.0.0-M11C
# AUTHORITY BOUNDARY: Projection evidence only.
# TENANT POSTURE: Synthetic tenant-scoped tests.
# FAIL-CLOSED POSTURE: Invalid evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
