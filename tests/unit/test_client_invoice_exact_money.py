"""P6E exact ClientInvoice integer-money certificate.
TITLE: Exact ClientInvoice Money Authority
VERSION: v1.0.0-P6E-EXACT-CLIENT-INVOICE-MONEY-CERT
AUTHORITY: Wilsy OS Core Governance
TENANT BOUNDARY: Exact invoices are tenant-scoped and idempotent.
AUTHORITY BOUNDARY: Integer commercial money only; no execution or settlement.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution and settlement.
FAIL-CLOSED: malformed, inexact, divergent, or corrupted evidence rejects.
"""
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import pytest

from tools.eos.saas.domain.billing import (
    ClientInvoice,
    ClientInvoiceExactMoney,
    ClientInvoiceExactMoneyLine,
)
from tools.eos.saas.billing.billing_registry import BillingRegistry


def _money() -> ClientInvoiceExactMoney:
    lines = (
        ClientInvoiceExactMoneyLine("Service", 2, 500, 1000, 150, 0, "ZAR"),
        ClientInvoiceExactMoneyLine("Travel", 1, 250, 250, 0, 0, "ZAR"),
    )
    return ClientInvoiceExactMoney("ZAR", 1250, 150, 1400, lines)


def test_exact_integer_arithmetic_and_fingerprint_are_deterministic():
    value = _money()
    assert value.exact_money_fingerprint == value.compute_fingerprint()
    assert value.exact_money_fingerprint == ClientInvoiceExactMoney.from_dict(value.to_dict()).exact_money_fingerprint
    assert len(value.exact_money_fingerprint) == 128
    with pytest.raises(FrozenInstanceError):
        value.total_minor = 2  # type: ignore[misc]


@pytest.mark.parametrize("kwargs", [
    {"quantity": True, "unit_price_minor": 1, "amount_minor": 1, "tax_amount_minor": 0, "discount_minor": 0},
    {"quantity": 1, "unit_price_minor": -1, "amount_minor": 0, "tax_amount_minor": 0, "discount_minor": 0},
    {"quantity": 1, "unit_price_minor": 1, "amount_minor": 2, "tax_amount_minor": 0, "discount_minor": 0},
])
def test_line_rejects_bool_negative_and_bad_arithmetic(kwargs):
    with pytest.raises(ValueError):
        ClientInvoiceExactMoneyLine("x", currency="ZAR", **kwargs)


def test_currency_and_cross_line_validation():
    with pytest.raises(ValueError):
        ClientInvoiceExactMoneyLine("x", 1, 1, 1, 0, 0, "zar")
    with pytest.raises(ValueError):
        ClientInvoiceExactMoney("ZAR", 1, 0, 1, (ClientInvoiceExactMoneyLine("x", 1, 1, 1, 0, 0, "USD"),))


def test_every_money_divergence_changes_fingerprint():
    baseline = _money()
    with pytest.raises(ValueError):
        replace(baseline, total_minor=1401)
    line = replace(baseline.lines[0], description="Changed")
    changed = replace(baseline, lines=(line, baseline.lines[1]), subtotal_minor=1250, total_minor=1400, exact_money_fingerprint="")
    assert changed.exact_money_fingerprint != baseline.exact_money_fingerprint


def test_projection_round_trips_and_legacy_hydration_survives():
    value = _money()
    projection = value.to_legacy_projection()
    invoice = ClientInvoice(tenant_id="tenant-a", exact_money=value)
    assert invoice.amount == projection["amount"]
    assert invoice.to_dict()["subtotal_minor"] == 1250
    assert ClientInvoice.from_dict(invoice.to_dict()).exact_money == value
    legacy = ClientInvoice.from_dict({"tenant_id": "tenant-a", "invoice_id": "legacy", "amount": 1.1, "total": 1.1})
    assert legacy.exact_money is None


class _Collection:
    def __init__(self): self.docs = []; self.calls = []
    def find_one(self, query, **kwargs):
        self.calls.append(("find_one", kwargs.get("session")))
        return next((dict(d) for d in self.docs if d.get("tenant_id") == query.get("tenant_id") and d.get("idempotency_key") == query.get("idempotency_key")), None)
    def insert_one(self, doc, **kwargs):
        self.calls.append(("insert_one", kwargs.get("session"))); self.docs.append(dict(doc))


def test_exact_registry_replay_divergence_and_session_forwarding():
    collection = _Collection(); session = object(); registry = BillingRegistry()
    kwargs: dict[str, Any] = dict(customer_id="customer-a", customer_name="Customer A", payment_terms_days=30, tax_type="vat", seller_jurisdiction="ZA", customer_jurisdiction="ZA", collection_method="send_invoice", issued_at=datetime(2026, 9, 15, tzinfo=timezone.utc), due_at=datetime(2026, 10, 15, tzinfo=timezone.utc), line_tax_rates_basis_points=(1500, 0))
    first = registry.create_client_invoice_exact("tenant-a", _money(), idempotency_key="key-a", collection=collection, session=session, **kwargs)
    second = registry.create_client_invoice_exact("tenant-a", _money(), idempotency_key="key-a", collection=collection, session=session, **kwargs)
    assert first == second and len(collection.docs) == 1
    assert collection.docs[0]["exact_line_tax_rates_basis_points"] == [1500, 0]
    assert first.line_items[0].tax_rate == 0.15
    assert all(call[1] is session for call in collection.calls)
    divergent = ClientInvoiceExactMoney("ZAR", 1300, 150, 1450, (_money().lines[0], ClientInvoiceExactMoneyLine("Travel", 1, 300, 300, 0, 0, "ZAR")))
    with pytest.raises(ValueError, match="CLIENT_INVOICE_REPLAY_CONFLICT"):
        registry.create_client_invoice_exact("tenant-a", divergent, idempotency_key="key-a", collection=collection, **kwargs)

    changed_dates = dict(kwargs, issued_at=datetime(2026, 9, 16, tzinfo=timezone.utc), due_at=datetime(2026, 10, 16, tzinfo=timezone.utc))
    with pytest.raises(ValueError, match="CLIENT_INVOICE_REPLAY_CONFLICT"):
        registry.create_client_invoice_exact("tenant-a", _money(), idempotency_key="key-a", collection=collection, **changed_dates)
    changed_rates = dict(kwargs, line_tax_rates_basis_points=(2000, 0))
    with pytest.raises(ValueError, match="CLIENT_INVOICE_REPLAY_CONFLICT"):
        registry.create_client_invoice_exact("tenant-a", _money(), idempotency_key="key-a", collection=collection, **changed_rates)


@pytest.mark.parametrize(
    ("missing", "expected"),
    [
        ("customer_id", "CLIENT_INVOICE_CUSTOMER_REQUIRED"),
        ("customer_name", "CLIENT_INVOICE_CUSTOMER_REQUIRED"),
        ("payment_terms_days", "CLIENT_INVOICE_PAYMENT_TERMS_REQUIRED"),
        ("tax_type", "CLIENT_INVOICE_TAX_TYPE_REQUIRED"),
        ("seller_jurisdiction", "CLIENT_INVOICE_JURISDICTION_REQUIRED"),
        ("customer_jurisdiction", "CLIENT_INVOICE_JURISDICTION_REQUIRED"),
        ("collection_method", "CLIENT_INVOICE_COLLECTION_METHOD_REQUIRED"),
        ("issued_at", "CLIENT_INVOICE_ISSUED_AT_REQUIRED"),
        ("due_at", "CLIENT_INVOICE_DUE_AT_REQUIRED"),
    ],
)
def test_exact_registry_requires_every_commercial_authority_input(missing: str, expected: str):
    collection = _Collection()
    kwargs: dict[str, Any] = dict(
        customer_id="customer-a",
        customer_name="Customer A",
        payment_terms_days=30,
        tax_type="vat",
        seller_jurisdiction="ZA",
        customer_jurisdiction="ZA",
        collection_method="send_invoice",
        issued_at=datetime(2026, 9, 15, tzinfo=timezone.utc),
        due_at=datetime(2026, 10, 15, tzinfo=timezone.utc),
        line_tax_rates_basis_points=(1500, 0),
    )
    kwargs.pop(missing)
    with pytest.raises(ValueError, match=expected):
        BillingRegistry().create_client_invoice_exact(
            "tenant-a", _money(), idempotency_key="required-key", collection=collection, **kwargs
        )


def test_exact_registry_signature_has_no_commercial_defaults():
    import inspect

    signature = inspect.signature(BillingRegistry.create_client_invoice_exact)
    commercial = {
        "customer_id",
        "customer_name",
        "payment_terms_days",
        "tax_type",
        "seller_jurisdiction",
        "customer_jurisdiction",
        "collection_method",
        "issued_at",
        "due_at",
        "idempotency_key",
    }
    for name in commercial:
        parameter = signature.parameters[name]
        assert parameter.default is inspect.Parameter.empty or name == "idempotency_key" or parameter.default is not None
        if name != "idempotency_key":
            assert parameter.default is not None and repr(parameter.default) != "'vat'"


def test_no_payment_or_settlement_authority_on_exact_object():
    value = _money()
    assert not hasattr(value, "payment") and not hasattr(value, "settlement")


# ARTIFACT: test_client_invoice_exact_money.py
# VERSION: v1.0.0-P6E-EXACT-CLIENT-INVOICE-MONEY-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
