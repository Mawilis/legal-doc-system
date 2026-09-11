"""WILSY OS M10B1 domain certificate.
TITLE: Financial Movement Execution Unit Certificate
VERSION: v1.0.0-M10B1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable direction-aware execution contracts.
ABSOLUTE CANONICAL PATH: tests/unit/test_financial_movement_execution.py
COLLABORATION / OWNERSHIP: Kennel EOS unit certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M10B1 certifies command and truth invariants.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Sensitive bearer references are rejected.
TENANT BOUNDARY: Commands and truth are tenant-bound.
AUTHORITY BOUNDARY: Execution evidence only; no settlement or paid authority.
FINANCIAL AUTHORITY BOUNDARY: Execution is distinct from settlement.
TRANSACTION BOUNDARY: No database or transaction access.
FAIL-CLOSED DECLARATION: Invalid contracts reject deterministically.
"""
from datetime import datetime, timezone
import pytest
from typing import Any
from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.financial_movement_execution import (
    FinancialMovementDirection, FinancialMovementExecutionCommand,
    FinancialMovementExecutionError, FinancialMovementExecutionTruth,
)

FP = "a" * 128

def command(direction=FinancialMovementDirection.COLLECTION, **changes):
    data: dict[str, Any] = dict(tenant_id="t", execution_authorization_id="auth", execution_authorization_fingerprint=FP,
                authority_subject_kind="invoice", authority_subject_id="inv", authority_subject_fingerprint="b" * 128,
                direction=direction, execution_command_id="cmd", idempotency_key="idem", amount_minor=100,
                currency="ZAR", payment_instrument_reference="instrument-ref")
    data.update(changes)
    return FinancialMovementExecutionCommand(**data)

def test_d01_d02_d03_direction_contracts():
    a, b = command(), command(FinancialMovementDirection.DISBURSEMENT)
    assert a.direction is FinancialMovementDirection.COLLECTION
    assert b.direction is FinancialMovementDirection.DISBURSEMENT
    assert a.fingerprint != b.fingerprint

@pytest.mark.parametrize("field,value", [("direction", "BAD"), ("amount_minor", 0), ("amount_minor", -1), ("amount_minor", True), ("currency", "zar"), ("currency", "US"), ("execution_authorization_fingerprint", "x"), ("authority_subject_fingerprint", "x"), ("payment_instrument_reference", "card_number=4111")])
def test_d04_to_d11_invalid_contracts(field, value):
    with pytest.raises(FinancialMovementExecutionError): command(**{field: value})

def test_d05_d08_valid_money_and_currency():
    assert command(amount_minor=1, currency="USD").amount_minor == 1

def test_d12_to_d14_fingerprint_is_deterministic_and_provenance_bound():
    assert command().fingerprint == command().fingerprint
    assert command(execution_authorization_fingerprint="c" * 128).fingerprint != command().fingerprint

def test_d15_to_d18_truth_is_immutable_and_hydratable():
    now = datetime.now(timezone.utc)
    truth = FinancialMovementExecutionTruth("truth", "t", "auth", "invoice", "inv", FinancialMovementDirection.COLLECTION, "provider", "ref", FinancialExecutionStatus.EXECUTED, 100, "ZAR", now, "instrument-ref", "evidence", command().fingerprint, command().fingerprint, now)
    with pytest.raises(AttributeError): truth.provider = "other"  # type: ignore[misc]
    hydrated = FinancialMovementExecutionTruth.from_dict(truth.to_dict())
    assert hydrated == truth
    assert not hasattr(truth, "settled") and not hasattr(truth, "paid")

# ARTIFACT: test_financial_movement_execution.py
# VERSION: v1.0.0-M10B1
# AUTHORITY BOUNDARY: Unit evidence only.
# TENANT POSTURE: Synthetic tenant identifiers.
# FAIL-CLOSED POSTURE: Contract violations are asserted.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
