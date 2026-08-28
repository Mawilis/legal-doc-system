"""Unit certification for the pure PayShap destination/evidence contract.

VERSION: v1.0.0-KENNEL-PAYSHAP-DESTINATION-EVIDENCE-CONTRACT-UNIT-CERT
"""
from datetime import datetime, timezone

# pyright: reportAttributeAccessIssue=false
import pytest

from tools.eos.kennel.orchestration.financial_execution_orchestrator import FinancialExecutionCommand
from tools.eos.kennel.domain.payment_destination import PaymentDestination, PaymentDestinationStatus, PaymentDestinationVerificationState
from tools.eos.kennel.providers.payshap_contract import PayShapConfig, PayShapContractError, PayShapProviderEvidence, PayShapProviderRequest, PayShapResolvedDestination, PayShapStatus, PayShapWebhookEvidence, map_status


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def destination() -> PaymentDestination:
    return PaymentDestination("pd", "tenant", "beneficiary", "opaque-ref", PaymentDestinationStatus.ACTIVE, PaymentDestinationVerificationState.VERIFIED, NOW, provider_metadata_reference="provider-meta")


def command() -> FinancialExecutionCommand:
    return FinancialExecutionCommand("tenant", "payable", "release", "execution-command", "idempotency", 100, "ZAR", "opaque-ref")


def config() -> PayShapConfig:
    return PayShapConfig("https://payshap.example", 10000, "https://return", "https://notify", "key-ref", "hook-ref")


def test_resolution_request_and_fingerprint_are_safe() -> None:
    resolved = PayShapResolvedDestination.from_destination(destination(), "merchant-ref")
    request = PayShapProviderRequest.from_command(command(), resolved, config())
    assert request.execution_command_id == command().execution_command_id and request.provider_reference != "payable"
    assert request.fingerprint == PayShapProviderRequest.from_command(command(), resolved, config()).fingerprint
    assert "api_key" not in request.evidence_payload()


def test_ineligible_destination_rejected() -> None:
    revoked = PaymentDestination("pd", "tenant", "beneficiary", "opaque-ref", PaymentDestinationStatus.REVOKED, PaymentDestinationVerificationState.VERIFIED, NOW, revoked_at=NOW, provider_metadata_reference="provider-meta")
    with pytest.raises(PayShapContractError): PayShapResolvedDestination.from_destination(revoked, "merchant-ref")


@pytest.mark.parametrize("value", ["bank_account", "card_number", "secret-token", "api_key"])
def test_raw_reference_rejected(value: str) -> None:
    with pytest.raises(PayShapContractError): PayShapResolvedDestination("pd", "tenant", "b", value, "meta", "merchant")


def test_config_validation() -> None:
    with pytest.raises(PayShapContractError): PayShapConfig("", 1, "return", "notify")
    with pytest.raises(PayShapContractError): PayShapConfig("base", 0, "return", "notify")


def test_ambiguous_status_is_not_failed_or_executed() -> None:
    for status in (PayShapStatus.REQUESTED, PayShapStatus.INITIATED, PayShapStatus.PENDING, PayShapStatus.ACCEPTED, PayShapStatus.UNKNOWN):
        with pytest.raises(PayShapContractError): map_status(status)
    assert map_status(PayShapStatus.FAILED) is not None
    with pytest.raises(PayShapContractError): map_status(PayShapStatus.EXECUTED)
    assert map_status(PayShapStatus.EXECUTED, NOW).value == "EXECUTED"


def test_evidence_is_immutable_and_payload_free() -> None:
    evidence = PayShapProviderEvidence("PayShap", "request", "execution", PayShapStatus.ACCEPTED, "a" * 128, "b" * 128, "event", NOW, NOW, "evidence-ref")
    assert evidence.to_dict()["evidence_reference"] == "evidence-ref" and "rawResponse" not in evidence.to_dict()
    with pytest.raises((AttributeError, TypeError)): evidence.provider_name = "other"


def test_webhook_evidence_has_no_business_mutation() -> None:
    event = PayShapWebhookEvidence("event", "provider-ref", PayShapStatus.ACCEPTED, 100, "ZAR", "tenant", NOW, NOW, "c" * 128, "evidence")
    assert event.status is PayShapStatus.ACCEPTED and not {"invoice", "paid", "settled", "outstandingAmount"}.intersection(event.__dict__)


def test_provider_metadata_and_secret_boundary() -> None:
    resolved = PayShapResolvedDestination.from_destination(destination(), "merchant-ref", "routing-ref")
    assert resolved.provider_metadata_reference == "provider-meta"
    with pytest.raises(PayShapContractError): PayShapConfig("base", 100, "return", "notify", "secret")


# ARTIFACT: test_payshap_contract.py
# VERSION: v1.0.0-KENNEL-PAYSHAP-DESTINATION-EVIDENCE-CONTRACT-UNIT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
