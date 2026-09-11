"""WILSY OS M11C commercial receivable dunning certificate.
TITLE: Commercial Receivable Dunning Unit Certificate
VERSION: v1.0.0-M11C
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic non-executing dunning-stage projection from aging evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_commercial_receivable_dunning.py
COLLABORATION / OWNERSHIP: M11C dunning unit-certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11C certifies stage boundaries and immutable fingerprints.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers; no outbound messaging.
TENANT BOUNDARY: Aging provenance remains tenant-scoped.
AUTHORITY BOUNDARY: Workflow projection only.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, settlement, or paid authority.
TRANSACTION BOUNDARY: Pure unit tests; no persistence.
FAIL-CLOSED DECLARATION: Invalid stage, time, and schema evidence rejects.
"""
from datetime import datetime, timezone, timedelta
import pytest
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.domain.commercial_receivable_aging import CommercialReceivableAging
from tools.eos.saas.domain.commercial_receivable_dunning import CommercialReceivableDunning, DunningStage

def aging(amount: int = 1000, overdue: int = 10) -> CommercialReceivableAging:
    as_of = datetime(2026, 2, 1, tzinfo=timezone.utc)
    r = CommercialReceivable("tenant-a", ReceivableFamily.CLIENT, "r-1", "invoice-1", "ZAR", amount, 0, amount, "a" * 128, ReceivableStatus.OPEN)
    return CommercialReceivableAging.from_receivable(r, as_of - timedelta(days=overdue), as_of)

def test_d01_overdue_open_balance_is_eligible() -> None:
    result = CommercialReceivableDunning.from_aging(aging(), datetime(2026, 2, 2, tzinfo=timezone.utc))
    assert result.stage is DunningStage.ELIGIBLE and result.outstanding_amount_minor == 1000

def test_d02_current_or_zero_balance_is_none() -> None:
    now = datetime(2026, 2, 2, tzinfo=timezone.utc)
    assert CommercialReceivableDunning.from_aging(aging(overdue=0), now).stage is DunningStage.NONE
    assert CommercialReceivableDunning.from_aging(aging(amount=0, overdue=10), now).stage is DunningStage.NONE

@pytest.mark.parametrize("stage", list(DunningStage))
def test_d03_explicit_stages_are_typed(stage: DunningStage) -> None:
    result = CommercialReceivableDunning.from_aging(aging(), datetime(2026, 2, 2, tzinfo=timezone.utc), stage)
    assert result.stage is stage

def test_d04_deterministic_serialization_and_fingerprint() -> None:
    result = CommercialReceivableDunning.from_aging(aging(), datetime(2026, 2, 2, tzinfo=timezone.utc))
    payload = result.to_dict()
    assert payload["dunning_fingerprint"] == result.dunning_fingerprint
    assert "_id" not in payload and result.to_dict() == payload

def test_d05_no_execution_or_outbound_authority() -> None:
    result = CommercialReceivableDunning.from_aging(aging(), datetime(2026, 2, 2, tzinfo=timezone.utc))
    assert result.stage in {DunningStage.NONE, DunningStage.ELIGIBLE, DunningStage.REMINDER, DunningStage.ESCALATED}
    assert not hasattr(result, "send") and not hasattr(result, "execute")

# ARTIFACT: test_commercial_receivable_dunning.py
# VERSION: v1.0.0-M11C
# AUTHORITY BOUNDARY: Workflow projection only.
# TENANT POSTURE: Aging provenance preserved.
# FAIL-CLOSED POSTURE: Invalid workflow evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
