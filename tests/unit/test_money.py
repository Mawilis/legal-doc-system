"""WILSY OS canonical money precision certificate.
TITLE: Exact Currency Minor-Unit Conversion Certificate
VERSION: v1.0.0-WILSY-MONEY-PRECISION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove exact bounded currency representation without financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_money.py
AUTHORITY BOUNDARY: Representation only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from decimal import Decimal
import pytest
from tools.eos.saas.domain.money import MoneyPrecisionError, SUPPORTED_CURRENCY_EXPONENTS, currency_exponent, to_minor_units

def test_exponents_and_exact_conversion():
    assert currency_exponent("ZAR") == 2 and currency_exponent("JPY") == 0 and currency_exponent("KWD") == 3
    assert to_minor_units("10.25", "ZAR") == 1025 and to_minor_units(100, "JPY") == 100 and to_minor_units(Decimal("1.234"), "KWD") == 1234

@pytest.mark.parametrize("currency", ["", " zar", "XXX", "AUD"])
def test_unknown_currency_fails_closed(currency):
    with pytest.raises(MoneyPrecisionError): currency_exponent(currency)

@pytest.mark.parametrize("amount,currency", [("10.251", "ZAR"), ("100.1", "JPY"), ("1.2345", "KWD"), (float("nan"), "ZAR"), (float("inf"), "ZAR"), (True, "ZAR"), (-1, "ZAR")])
def test_inexact_or_invalid_amount_fails_closed(amount, currency):
    with pytest.raises(MoneyPrecisionError): to_minor_units(amount, currency)

def test_float_and_repeat_are_deterministic():
    assert to_minor_units(10.25, "ZAR") == 1025 == to_minor_units(10.25, "ZAR")
    with pytest.raises(TypeError): getattr(to_minor_units, "__call__")(10, "ZAR", 2)

def test_metadata_is_immutable_and_no_execution_authority():
    with pytest.raises((TypeError, AttributeError)): getattr(SUPPORTED_CURRENCY_EXPONENTS, "__setitem__")("ZAR", 9)
    assert not any(token in {"execute", "settled", "paid", "provider", "kenn el"} for token in dir(to_minor_units))

# ARTIFACT: test_money.py
# VERSION: v1.0.0-WILSY-MONEY-PRECISION-CERT
# AUTHORITY BOUNDARY: direct representation certification only
# TENANT POSTURE: none; generic domain primitive
# FAIL-CLOSED POSTURE: unsupported and inexact values reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
