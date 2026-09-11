"""WILSY OS canonical money precision authority.
TITLE: Exact Currency Minor-Unit Conversion
VERSION: v1.0.0-WILSY-MONEY-PRECISION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Bounded currency exponents and exact major-to-minor representation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/money.py
COLLABORATION / OWNERSHIP: Python EOS shared commercial domain
CERTIFICATION / UPDATE DATE: 2026-09-04
CHANGELOG: v1.0.0 establishes immutable locally evidenced currency precision.
COMPLIANCE: POPIA §19 | GDPR Article 32 | SOC2 CC7.2
AUTHORITY BOUNDARY: Representation only; no liability, authorization, execution, or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from types import MappingProxyType
from typing import Final
import math

SUPPORTED_CURRENCY_EXPONENTS: Final = MappingProxyType({"BHD": 3, "EUR": 2, "GBP": 2, "JPY": 0, "KWD": 3, "USD": 2, "ZAR": 2})
VERSION = "v1.0.0-WILSY-MONEY-PRECISION"

class MoneyPrecisionError(ValueError):
    """Raised when currency or amount cannot be represented exactly."""

def currency_exponent(currency: str) -> int:
    if not isinstance(currency, str) or currency != currency.strip() or currency not in SUPPORTED_CURRENCY_EXPONENTS:
        raise MoneyPrecisionError("unsupported currency")
    return SUPPORTED_CURRENCY_EXPONENTS[currency]

def to_minor_units(amount: Decimal | int | float | str, currency: str) -> int:
    exponent = currency_exponent(currency)
    if isinstance(amount, bool):
        raise MoneyPrecisionError("amount is invalid")
    if isinstance(amount, float) and not math.isfinite(amount):
        raise MoneyPrecisionError("amount is invalid")
    try:
        value = Decimal(str(amount))
    except (InvalidOperation, ValueError, TypeError):
        raise MoneyPrecisionError("amount is invalid") from None
    if not value.is_finite() or value < 0:
        raise MoneyPrecisionError("amount is invalid")
    scale = Decimal(10) ** exponent
    minor = value * scale
    if minor != minor.to_integral_value():
        raise MoneyPrecisionError("amount has excessive precision")
    return int(minor)

__all__ = ["SUPPORTED_CURRENCY_EXPONENTS", "MoneyPrecisionError", "currency_exponent", "to_minor_units", "VERSION"]
# ARTIFACT: money.py
# VERSION: v1.0.0-WILSY-MONEY-PRECISION
# AUTHORITY BOUNDARY: exact representation only; no execution or settlement
# TENANT POSTURE: none; generic domain primitive
# FAIL-CLOSED POSTURE: unsupported currencies and inexact values are rejected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
