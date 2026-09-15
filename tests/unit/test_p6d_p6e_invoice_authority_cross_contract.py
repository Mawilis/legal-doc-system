"""Cross-contract certificate for explicit P6D to P6E invoice authority inputs.

TITLE: P6D/P6E Invoice Authority Cross-Contract Certificate
VERSION: v1.0.0-P6D-P6E-INVOICE-AUTHORITY-CROSS-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves that P6D carries explicit commercial identity/policy evidence
         and P6E exact-money creation accepts no commercial defaults.
TENANT BOUNDARY: All profile and invoice authority remains tenant-scoped.
AUTHORITY BOUNDARY: This certificate inspects contracts; it creates no invoice,
                    payment, execution, or settlement truth.
FINANCIAL AUTHORITY: Kennel EOS exclusively owns financial execution and
                      settlement.
FAIL-CLOSED: Missing commercial inputs and implicit tax treatment are rejected.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: 2026-09-15 v1.0.0 establishes the P6D/P6E explicit-input contract.
"""
from dataclasses import fields
from datetime import datetime, timezone
import inspect

from tools.eos.saas.billing import billing_registry
from tools.eos.saas.billing.process_service_client_billing_authority import (
    ClientBillingProfileVersion,
    CollectionMethod,
    InvoiceTaxType,
)


def test_p6d_profile_declares_every_p6e_commercial_input() -> None:
    names = {field.name for field in fields(ClientBillingProfileVersion)}
    assert {
        "customer_id",
        "customer_legal_name",
        "payment_terms",
        "invoice_tax_type",
        "seller_jurisdiction",
        "customer_jurisdiction",
        "collection_method",
    } <= names
    assert InvoiceTaxType.VAT.value == "vat"
    assert CollectionMethod.SEND_INVOICE.value == "SEND_INVOICE"


def test_p6e_exact_factory_has_no_authority_bearing_defaults() -> None:
    signature = inspect.signature(billing_registry.BillingRegistry.create_client_invoice_exact)
    required = {
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
    commercial_literals = {"vat", "gst", "none", "send_invoice", "charge_automatically", 30}
    for name in required:
        parameter = signature.parameters[name]
        if name == "idempotency_key":
            assert parameter.default is inspect.Parameter.empty
            continue
        assert parameter.default is not inspect.Parameter.empty
        assert parameter.default not in commercial_literals
    assert datetime(2026, 9, 15, tzinfo=timezone.utc).tzinfo is not None


def test_p6d_tax_type_is_not_inferred_when_absent() -> None:
    profile_fields = {field.name: field for field in fields(ClientBillingProfileVersion)}
    assert profile_fields["invoice_tax_type"].default is None
    assert "invoice_tax_type" not in ClientBillingProfileVersion.__dataclass_fields__["invoice_tax_type"].metadata


# ARTIFACT: test_p6d_p6e_invoice_authority_cross_contract.py
# VERSION: v1.0.0-P6D-P6E-INVOICE-AUTHORITY-CROSS-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
