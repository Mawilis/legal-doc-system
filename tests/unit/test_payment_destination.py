"""Unit certification for the provider-independent PaymentDestination contract.

VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-AUTHORITY-UNIT-CERT
"""
from datetime import datetime, timezone

# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
import pytest

from tools.eos.kennel.domain.payment_destination import (
    PaymentDestination,
    PaymentDestinationError,
    PaymentDestinationStatus,
    PaymentDestinationVerificationState,
)


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def destination(**changes: object) -> PaymentDestination:
    values: dict[str, object] = {"payment_destination_id": "pd", "tenant_id": "tenant", "beneficiary_id": "beneficiary", "destination_reference": "opaque-ref", "status": PaymentDestinationStatus.ACTIVE, "verification_state": PaymentDestinationVerificationState.VERIFIED, "created_at": NOW}
    values.update(changes)
    return PaymentDestination(**values)


def test_valid_immutable_and_eligible() -> None:
    item = destination(provider_metadata_reference="metadata-ref")
    assert item.is_execution_eligible is True
    assert item.to_persistence_dict()["payment_destination_id"] == "pd"
    with pytest.raises((AttributeError, TypeError)):
        item.tenant_id = "other"


@pytest.mark.parametrize("field", ["payment_destination_id", "tenant_id", "beneficiary_id", "destination_reference"])
def test_required_identity_rejected(field: str) -> None:
    with pytest.raises(PaymentDestinationError):
        destination(**{field: " "})


@pytest.mark.parametrize("value", ["bank_account=1", "account-number", "card_number", "secret-token", "api_key=x"])
def test_raw_secret_patterns_rejected(value: str) -> None:
    with pytest.raises(PaymentDestinationError):
        destination(destination_reference=value)


@pytest.mark.parametrize("state", list(PaymentDestinationStatus))
def test_status_validation_and_revocation(state: PaymentDestinationStatus) -> None:
    item = destination(status=state, revoked_at=NOW if state is PaymentDestinationStatus.REVOKED else None)
    assert item.is_execution_eligible is (state is PaymentDestinationStatus.ACTIVE)


@pytest.mark.parametrize("state", list(PaymentDestinationVerificationState))
def test_verification_validation(state: PaymentDestinationVerificationState) -> None:
    item = destination(verification_state=state)
    assert item.is_execution_eligible is (state is PaymentDestinationVerificationState.VERIFIED)


def test_revoked_requires_timestamp_and_never_eligible() -> None:
    with pytest.raises(PaymentDestinationError):
        destination(status=PaymentDestinationStatus.REVOKED)
    assert destination(status=PaymentDestinationStatus.REVOKED, revoked_at=NOW).is_execution_eligible is False


def test_no_forbidden_states_or_fields() -> None:
    item = destination()
    assert not {"paid", "settled", "executed"}.intersection(item.to_persistence_dict())
    with pytest.raises(PaymentDestinationError):
        PaymentDestination.from_persistence_dict({**item.to_persistence_dict(), "bank_account": "redacted"})


def test_fingerprint_and_round_trip() -> None:
    item = destination()
    restored = PaymentDestination.from_persistence_dict(item.to_persistence_dict())
    assert restored == item
    assert item.fingerprint == restored.fingerprint and len(item.fingerprint) == 128
    assert item.fingerprint != destination(beneficiary_id="other").fingerprint


def test_provider_metadata_remains_opaque() -> None:
    with pytest.raises(PaymentDestinationError):
        destination(provider_metadata_reference="provider_secret")
    assert destination(provider_metadata_reference="provider-meta-ref").provider_metadata_reference == "provider-meta-ref"


# ARTIFACT: test_payment_destination.py
# VERSION: v1.0.0-KENNEL-PAYMENT-DESTINATION-AUTHORITY-UNIT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
