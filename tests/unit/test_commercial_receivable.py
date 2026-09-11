"""WILSY OS M11A canonical commercial receivable unit certificate.
TITLE: Commercial Receivable Domain Certificate
VERSION: v1.0.0-M11A
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify typed platform/client balance truth and strict hydration.
ABSOLUTE CANONICAL PATH: tests/unit/test_commercial_receivable.py
COLLABORATION / OWNERSHIP: M11A domain certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11A certifies family, money, immutability, and integrity law.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers and no payment credentials.
TENANT BOUNDARY: Every fixture is tenant-scoped.
AUTHORITY BOUNDARY: Commercial truth only; no execution or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel owns execution and settlement evidence.
TRANSACTION BOUNDARY: Pure value-object certificate; no persistence.
FAIL-CLOSED DECLARATION: Invalid schema, money, family, and fingerprint reject.
"""
import dataclasses
import pytest
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, CommercialReceivableError, ReceivableFamily, ReceivableStatus

def make(family=ReceivableFamily.PLATFORM, outstanding=700):
    return CommercialReceivable("tenant", family, "recv-1", "invoice-1", "ZAR", 1000, 0, outstanding, "a" * 128, ReceivableStatus.OPEN)

def test_platform_and_client_families_are_explicit_and_distinct():
    assert make().receivable_family is ReceivableFamily.PLATFORM
    assert make(ReceivableFamily.CLIENT).receivable_family is ReceivableFamily.CLIENT
    assert make().to_dict()["receivable_family"] != make(ReceivableFamily.CLIENT).to_dict()["receivable_family"]

@pytest.mark.parametrize("value", [True, -1, 1.5])
def test_money_rejects_bool_negative_and_float(value):
    with pytest.raises(CommercialReceivableError): CommercialReceivable("t", ReceivableFamily.PLATFORM, "r", "i", "ZAR", value, 0, 0, "a"*128, ReceivableStatus.OPEN)

def test_balance_currency_tenant_and_identity_boundaries():
    with pytest.raises(CommercialReceivableError): make(outstanding=1001)
    with pytest.raises(CommercialReceivableError): CommercialReceivable("", ReceivableFamily.PLATFORM, "r", "i", "ZAR", 1, 0, 1, "a"*128, ReceivableStatus.OPEN)
    with pytest.raises(CommercialReceivableError): CommercialReceivable("t", ReceivableFamily.PLATFORM, "r", "i", "zar", 1, 0, 1, "a"*128, ReceivableStatus.OPEN)

def test_immutable_deterministic_round_trip_and_material_drift():
    value=make(); assert value.to_dict() == make().to_dict(); assert CommercialReceivable.from_dict(value.to_dict()) == value
    with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)): setattr(value, "outstanding_amount_minor", 0)
    assert make(outstanding=699).receivable_fingerprint != value.receivable_fingerprint

@pytest.mark.parametrize("mutation", [{"_id": "mongo"}, {"unknown": 1}, {"status": "PAID"}, {}])
def test_strict_hydration_rejects_transport_unknown_missing_and_forbidden_status(mutation):
    payload=make().to_dict(); payload.pop("receivable_fingerprint", None) if not mutation else payload.update(mutation)
    with pytest.raises(CommercialReceivableError): CommercialReceivable.from_dict(payload)

def test_forbidden_financial_authority_fields_and_fingerprint_corruption_reject():
    payload=make().to_dict(); payload["paid"] = True
    with pytest.raises(CommercialReceivableError): CommercialReceivable.from_dict(payload)
    payload=make().to_dict(); payload["receivable_fingerprint"]="b"*128
    with pytest.raises(CommercialReceivableError): CommercialReceivable.from_dict(payload)
    assert not any(name in make().to_dict() for name in ("settled", "executed", "provider", "payment_destination", "payable_id"))

def test_commercial_closure_is_balance_only_not_settlement_or_paid():
    closed=CommercialReceivable("tenant", ReceivableFamily.PLATFORM, "r", "i", "ZAR", 1000, 0, 0, "a"*128, ReceivableStatus.CLOSED_COMMERCIAL)
    assert closed.outstanding_amount_minor == 0 and closed.status is ReceivableStatus.CLOSED_COMMERCIAL

# ARTIFACT: test_commercial_receivable.py
# VERSION: v1.0.0-M11A
# AUTHORITY BOUNDARY: Commercial truth certificate only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Invalid commercial truth rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
