"""Direct certificate for the M12-P1 billing-intelligence evidence contract.

VERSION: v1.0.0-M12-P1
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Prove deterministic, tenant-scoped, non-financial evidence derivation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_billing_intelligence_engine.py
"""
from dataclasses import replace
from datetime import datetime, timezone

import pytest

import tools.eos.saas.billing.billing_intelligence_engine as engine
from tools.eos.saas.domain.commercial_receivable import (
    CommercialReceivable,
    ReceivableFamily,
    ReceivableStatus,
)
from tools.eos.saas.domain.commercial_receivable_aging import (
    CommercialReceivableAging,
)
from tools.eos.saas.domain.commercial_receivable_dunning import (
    CommercialReceivableDunning,
    DunningStage,
)


TENANT = "tenant-m12"
OTHER_TENANT = "tenant-other"
SOURCE_FP = "a" * 128
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)


def make_receivable(
    *, tenant_id: str = TENANT, receivable_id: str = "r-1", amount: int = 1250
) -> CommercialReceivable:
    return CommercialReceivable(
        tenant_id=tenant_id,
        receivable_family=ReceivableFamily.CLIENT,
        receivable_id=receivable_id,
        source_invoice_id=f"invoice-{receivable_id}",
        currency="ZAR",
        original_amount_minor=amount,
        adjustment_amount_minor=0,
        outstanding_amount_minor=amount,
        source_invoice_fingerprint=SOURCE_FP,
        status=ReceivableStatus.OPEN,
    )


def make_aging(receivable: CommercialReceivable) -> CommercialReceivableAging:
    return CommercialReceivableAging.from_receivable(
        receivable,
        due_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        as_of=AS_OF,
    )


def make_dunning(aging: CommercialReceivableAging) -> CommercialReceivableDunning:
    return CommercialReceivableDunning.from_aging(
        aging,
        effective_at=AS_OF,
        stage=DunningStage.REMINDER,
    )


def test_empty_input_is_explicit_and_deterministic() -> None:
    value = engine.derive_billing_intelligence(tenant_id=TENANT)
    assert value.receivable_count == 0
    assert value.receivable_outstanding_amount_minor == 0
    assert value.aging_evidence_count == 0
    assert value.dunning_evidence_count == 0
    assert value.source_provenance == ()
    assert value.evidence_fingerprint == value.compute_fingerprint()
    assert value.unsupported_outputs == engine.UNSUPPORTED_INTELLIGENCE_OUTPUTS


def test_derives_receivable_aging_and_dunning_summaries() -> None:
    receivable = make_receivable()
    aging = make_aging(receivable)
    dunning = make_dunning(aging)
    value = engine.derive_billing_intelligence(
        tenant_id=TENANT,
        receivables=(receivable,),
        aging=(aging,),
        dunning=(dunning,),
        as_of=AS_OF,
    )
    assert value.receivable_count == 1
    assert value.receivable_outstanding_amount_minor == 1250
    assert value.aging_evidence_count == 1
    assert dict(value.aging_by_bucket)[aging.bucket.value] == 1
    assert value.dunning_evidence_count == 1
    assert dict(value.dunning_by_stage)[DunningStage.REMINDER.value] == 1


def test_source_order_does_not_change_fingerprint() -> None:
    first = make_receivable(receivable_id="r-1")
    second = make_receivable(receivable_id="r-2", amount=2500)
    first_aging, second_aging = make_aging(first), make_aging(second)
    first_dunning, second_dunning = make_dunning(first_aging), make_dunning(second_aging)
    left = engine.derive_billing_intelligence(
        tenant_id=TENANT,
        receivables=(first, second),
        aging=(first_aging, second_aging),
        dunning=(first_dunning, second_dunning),
        as_of=AS_OF,
    )
    right = engine.derive_billing_intelligence(
        tenant_id=TENANT,
        receivables=(second, first),
        aging=(second_aging, first_aging),
        dunning=(second_dunning, first_dunning),
        as_of=AS_OF,
    )
    assert left.to_dict() == right.to_dict()


def test_tenant_isolation_rejects_mixed_sources() -> None:
    with pytest.raises(engine.BillingIntelligenceError, match="MIXED_TENANT"):
        engine.derive_billing_intelligence(
            tenant_id=TENANT,
            receivables=(make_receivable(), make_receivable(tenant_id=OTHER_TENANT, receivable_id="r-2")),
        )


def test_blank_tenant_rejects_before_derivation() -> None:
    with pytest.raises(engine.BillingIntelligenceError, match="INVALID_TENANT"):
        engine.derive_billing_intelligence(tenant_id=" ")


def test_duplicate_source_identity_fails_closed() -> None:
    first = make_receivable()
    conflicting = replace(first, outstanding_amount_minor=1000)
    with pytest.raises(engine.BillingIntelligenceError, match="DUPLICATE_SOURCE"):
        engine.derive_billing_intelligence(tenant_id=TENANT, receivables=(first, conflicting))


def test_aging_provenance_drift_fails_closed() -> None:
    receivable = make_receivable()
    aging = replace(make_aging(receivable), source_receivable_fingerprint="b" * 128)
    with pytest.raises(engine.BillingIntelligenceError, match="AGING_PROVENANCE_DRIFT"):
        engine.derive_billing_intelligence(tenant_id=TENANT, receivables=(receivable,), aging=(aging,))


def test_dunning_provenance_drift_fails_closed() -> None:
    receivable = make_receivable()
    aging = make_aging(receivable)
    dunning = replace( make_dunning(aging), aging_fingerprint="c" * 128)
    with pytest.raises(engine.BillingIntelligenceError, match="DUNNING_PROVENANCE_DRIFT"):
        engine.derive_billing_intelligence(
            tenant_id=TENANT, receivables=(receivable,), aging=(aging,), dunning=(dunning,)
        )


def test_provenance_preserves_each_source_fingerprint() -> None:
    receivable = make_receivable()
    aging = make_aging(receivable)
    dunning = make_dunning(aging)
    provenance = engine.derive_billing_intelligence(
        tenant_id=TENANT, receivables=(receivable,), aging=(aging,), dunning=(dunning,)
    ).source_provenance
    assert ("commercial_receivable", receivable.receivable_id, receivable.receivable_fingerprint) in provenance
    assert ("commercial_receivable_aging", aging.receivable_id, aging.aging_fingerprint) in provenance
    assert ("commercial_receivable_dunning", dunning.receivable_id, dunning.dunning_fingerprint) in provenance


def test_source_value_change_changes_final_fingerprint() -> None:
    original = make_receivable(amount=1250)
    changed = make_receivable(amount=1251)
    assert engine.derive_billing_intelligence(tenant_id=TENANT, receivables=(original,)).evidence_fingerprint != engine.derive_billing_intelligence(tenant_id=TENANT, receivables=(changed,)).evidence_fingerprint


def test_as_of_is_canonicalized_to_utc_and_bound() -> None:
    offset = datetime(2026, 9, 12, 14, tzinfo=timezone.utc)
    value = engine.derive_billing_intelligence(tenant_id=TENANT, as_of=offset)
    assert value.as_of == offset
    assert value.evidence_fingerprint != engine.derive_billing_intelligence(tenant_id=TENANT).evidence_fingerprint


def test_output_is_immutable_and_has_no_financial_authority() -> None:
    value = engine.derive_billing_intelligence(tenant_id=TENANT)
    with pytest.raises(AttributeError):
        value.receivable_count = 1  # type: ignore[misc]
    assert not hasattr(value, "settlement")
    assert not hasattr(value, "execution")
    assert not hasattr(value, "paid_state")


def test_unsupported_outputs_are_never_synthesized() -> None:
    value = engine.derive_billing_intelligence(tenant_id=TENANT)
    payload = value.to_dict()
    for name in engine.UNSUPPORTED_INTELLIGENCE_OUTPUTS:
        assert name not in payload
    assert value.unsupported_outputs == engine.UNSUPPORTED_INTELLIGENCE_OUTPUTS


def test_import_surface_has_no_external_client_or_persistence_owner() -> None:
    assert not hasattr(engine, "MongoClient")
    assert not hasattr(engine, "requests")
    assert not hasattr(engine, "httpx")
