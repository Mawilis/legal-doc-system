"""Unit certification for the AP-to-Kennel execution request boundary.

VERSION: v1.0.0-VENDOR-BILL-FINANCIAL-EXECUTION-REQUEST-UNIT-CERT
"""
from datetime import datetime, timezone
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
import pytest
from tools.eos.saas.domain.vendor_bill_financial_execution_request import VendorBillFinancialExecutionRequest, VendorBillFinancialExecutionRequestError
from tools.eos.saas.domain.vendor_bill_release_authorization import VendorBillReleaseAuthorization


def auth() -> VendorBillReleaseAuthorization:
    return VendorBillReleaseAuthorization("t", "ra", "p", 1, "r", "a" * 128, 100, "ZAR", "actor", "basis", datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2026, 1, 1, tzinfo=timezone.utc))


def request(**changes: object) -> VendorBillFinancialExecutionRequest:
    values: dict[str, object] = {"execution_command_id": "ec", "tenant_id": "t", "payable_id": "p", "release_authorization_id": "ra", "idempotency_key": "ik", "amount_minor": 100, "currency": "ZAR", "payment_destination_reference": "vault-ref", "requested_by_actor_id": "actor", "requested_at": datetime(2026, 1, 2, tzinfo=timezone.utc)}
    values.update(changes)
    return VendorBillFinancialExecutionRequest(**values)


def test_valid_mapping_is_immutable_and_side_effect_free() -> None:
    item = request(); command = item.to_financial_execution_command(auth())
    assert command.tenant_id == "t" and command.payable_id == "p" and command.release_authorization_id == "ra" and command.execution_command_id != command.release_authorization_id
    with pytest.raises((AttributeError, TypeError)): item.amount_minor = 1


@pytest.mark.parametrize("field", ["execution_command_id", "idempotency_key", "tenant_id", "payable_id", "release_authorization_id", "payment_destination_reference"])
def test_blank_identifiers_rejected(field: str) -> None:
    with pytest.raises(VendorBillFinancialExecutionRequestError): request(**{field: " "})


@pytest.mark.parametrize("value", [0, -1, True, 1.5, None])
def test_amount_rejected(value: object) -> None:
    with pytest.raises(VendorBillFinancialExecutionRequestError): request(amount_minor=value)


@pytest.mark.parametrize("value", ["zar", "US", "Z1R", ""])
def test_currency_rejected(value: str) -> None:
    with pytest.raises(VendorBillFinancialExecutionRequestError): request(currency=value)


def test_scope_and_destination_validation() -> None:
    for field, value in (("tenant_id", "x"), ("payable_id", "x"), ("release_authorization_id", "x"), ("currency", "USD"), ("amount_minor", 101)):
        with pytest.raises(VendorBillFinancialExecutionRequestError): request(**{field: value}).to_financial_execution_command(auth())
    for value in ("bank account 123", "card_number", "secret-token"):
        with pytest.raises(VendorBillFinancialExecutionRequestError): request(payment_destination_reference=value)


def test_fingerprint_is_deterministic() -> None:
    assert request().fingerprint == request().fingerprint and len(request().fingerprint) == 128


# END OF WILSY OS SOVEREIGN ARTIFACT
