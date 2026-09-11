"""Unit certificate for the closed generic financial command domain.

TITLE: Financial Execution Command Unit Certification
VERSION: v2.0.0-M11-P5-R2A
AUTHORITY: Certification evidence only; Kennel EOS owns execution truth.
EPITOME: Prove immutable AP and Platform Billing provenance without transport or settlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_command.py
COLLABORATION / OWNERSHIP: Kennel EOS command-domain certification.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v2.0.0-M11-P5-R2A certifies closed families, typed sources, strict hydration, provider correlation, and complete fingerprints.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Synthetic tenant-scoped fixtures only.
FINANCIAL TRUTH BOUNDARY: No provider execution, attempt, truth, settlement, or receivable mutation.
TRANSACTION BOUNDARY: Pure deterministic unit tests; no Mongo or clock.
"""
from dataclasses import fields
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

import pytest

from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    FinancialExecutionCommandError,
    FinancialExecutionCommandFamily,
    PlatformBillingCommandSource,
)

NOW = datetime(2026, 9, 7, 10, 0, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128
FP_C = "c" * 128


def ap_source(**changes: object) -> AccountsPayableCommandSource:
    values: dict[str, Any] = {"execution_request_id": "ap-request", "execution_request_fingerprint": FP_A, "selection_decision_id": "selection-1", "selection_decision_fingerprint": FP_B, "payable_id": "payable-1", "release_authorization_id": "release-1", "authorized_provider_name": "PAYSHAP"}
    values.update(changes)
    return AccountsPayableCommandSource(**values)


def platform_source(**changes: object) -> PlatformBillingCommandSource:
    values: dict[str, Any] = {"execution_request_id": "platform-request", "execution_request_fingerprint": FP_A, "routing_decision_id": "routing-1", "routing_decision_fingerprint": FP_B, "platform_invoice_id": "platform-invoice-1", "release_authorization_id": "platform-release-1", "release_authorization_fingerprint": FP_C, "authorized_provider_name": "STRIPE"}
    values.update(changes)
    return PlatformBillingCommandSource(**values)


def command(**changes: object) -> FinancialExecutionCommand:
    source: Any = changes.pop("source_authority", ap_source())
    values: dict[str, Any] = {"tenant_id": "tenant-1", "execution_command_id": "command-1", "idempotency_key": "idem-1", "amount_minor": 12500, "currency": "ZAR", "payment_destination_reference": "destination-ref", "source_authority": source, "provider_name": source.authorized_provider_name, "created_at": NOW, "provider_metadata_reference": "metadata-ref"}
    values.update(changes)
    return FinancialExecutionCommand(**values)


def test_valid_ap_command_projects_compatibility_subjects() -> None:
    item = command()
    assert item.family is FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE
    assert item.payable_id == "payable-1"
    assert item.release_authorization_id == "release-1"


def test_valid_platform_command_is_family_discriminated() -> None:
    item = command(source_authority=platform_source(), provider_name="STRIPE")
    assert item.family is FinancialExecutionCommandFamily.PLATFORM_BILLING
    assert item.source_authority_kind.value == "PLATFORM_BILLING"
    assert item.release_authorization_id == "platform-release-1"


def test_platform_payable_projection_fails_closed() -> None:
    with pytest.raises(FinancialExecutionCommandError):
        _ = command(source_authority=platform_source(), provider_name="STRIPE").payable_id


def test_family_enum_is_closed() -> None:
    assert {member.value for member in FinancialExecutionCommandFamily} == {"ACCOUNTS_PAYABLE", "PLATFORM_BILLING"}
    with pytest.raises(ValueError):
        FinancialExecutionCommandFamily("CLIENT_INVOICE")


@pytest.mark.parametrize("field", ["execution_request_id", "selection_decision_id", "payable_id", "release_authorization_id", "authorized_provider_name"])
def test_ap_source_text_fields_required(field: str) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        ap_source(**{field: " "})


@pytest.mark.parametrize("field", ["execution_request_fingerprint", "selection_decision_fingerprint"])
def test_ap_source_fingerprints_strict(field: str) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        ap_source(**{field: "not-a-fingerprint"})


@pytest.mark.parametrize("field", ["execution_request_id", "routing_decision_id", "platform_invoice_id", "release_authorization_id", "authorized_provider_name"])
def test_platform_source_text_fields_required(field: str) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        platform_source(**{field: " "})


@pytest.mark.parametrize("field", ["execution_request_fingerprint", "routing_decision_fingerprint", "release_authorization_fingerprint"])
def test_platform_source_fingerprints_strict(field: str) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        platform_source(**{field: "bad"})


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "idempotency_key", "payment_destination_reference"])
def test_common_text_fields_required(field: str) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        command(**{field: " "})


@pytest.mark.parametrize("value", [0, -1, True, 1.5, "12"])
def test_amount_positive_integer(value: object) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        command(amount_minor=value)


@pytest.mark.parametrize("value", ["", "zar", "ZA", "ZARR", 123])
def test_currency_closed(value: object) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        command(currency=value)


@pytest.mark.parametrize("value", ["", "bank-account-secret", "card-token"])
def test_destination_never_accepts_credentials(value: str) -> None:
    with pytest.raises(FinancialExecutionCommandError):
        command(payment_destination_reference=value)


def test_provider_is_mandatory_and_correlated() -> None:
    with pytest.raises(FinancialExecutionCommandError):
        command(provider_name="OTHER")


def test_provider_metadata_is_optional_and_opaque() -> None:
    assert command(provider_metadata_reference=None).provider_metadata_reference is None
    with pytest.raises(FinancialExecutionCommandError):
        command(provider_metadata_reference="credential-token")


def test_created_at_requires_aware_datetime() -> None:
    assert command().created_at == NOW
    with pytest.raises(FinancialExecutionCommandError):
        command(created_at=datetime(2026, 9, 7, 10, 0))


def test_command_id_is_explicit_and_preserved() -> None:
    assert command(execution_command_id="caller-command").execution_command_id == "caller-command"


def test_source_objects_are_immutable() -> None:
    with pytest.raises(AttributeError):
        ap_source().payable_id = "other"  # type: ignore[misc]


def test_command_is_immutable() -> None:
    with pytest.raises(AttributeError):
        command().amount_minor = 1  # type: ignore[misc]


def test_source_fingerprints_are_deterministic_and_family_bound() -> None:
    assert ap_source().fingerprint == ap_source().fingerprint
    assert ap_source().fingerprint != platform_source().fingerprint


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "idempotency_key", "amount_minor", "currency", "payment_destination_reference", "provider_name", "provider_metadata_reference", "created_at"])
def test_command_fingerprint_binds_common_fields(field: str) -> None:
    replacement: dict[str, object] = {"amount_minor": 12501, "currency": "USD", "provider_name": "OTHER", "provider_metadata_reference": "metadata-other", "created_at": datetime(2026, 9, 8, 10, tzinfo=timezone.utc)}
    value = replacement.get(field, f"changed-{field}")
    if field == "provider_name":
        with pytest.raises(FinancialExecutionCommandError):
            command(**{field: value})
    else:
        assert command().fingerprint != command(**{field: value}).fingerprint


def test_command_fingerprint_binds_source_fields() -> None:
    assert command().fingerprint != command(source_authority=ap_source(payable_id="payable-2")).fingerprint


def test_fingerprint_is_sha3_512_of_complete_payload() -> None:
    item = command()
    expected = hashlib.sha3_512(json.dumps(item.evidence_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    assert item.fingerprint == expected
    assert len(item.fingerprint) == 128


def test_persisted_projection_contains_common_and_typed_source() -> None:
    row = command().to_persisted()
    assert row["source_authority_kind"] == "ACCOUNTS_PAYABLE"
    assert row["source_authority"]["payable_id"] == "payable-1"  # type: ignore[index]
    assert row["command_fingerprint"] == command().fingerprint


def test_strict_round_trip() -> None:
    assert FinancialExecutionCommand.from_persisted(command().to_persisted()) == command()
    assert FinancialExecutionCommand.from_persisted(command(source_authority=platform_source(), provider_name="STRIPE").to_persisted()).family is FinancialExecutionCommandFamily.PLATFORM_BILLING


@pytest.mark.parametrize("mutator", [lambda row: row.pop("source_authority_kind"), lambda row: row.__setitem__("source_authority_kind", "UNKNOWN"), lambda row: row.__setitem__("requested_provider", "PAYSHAP"), lambda row: row.__setitem__("extra", 1), lambda row: row.pop("source_authority"), lambda row: row["source_authority"].pop("selection_decision_id"), lambda row: row["source_authority"].__setitem__("source_authority_kind", "PLATFORM_BILLING"), lambda row: row.__setitem__("command_fingerprint", "f" * 128)])
def test_strict_hydration_rejects_corrupt_or_legacy_rows(mutator: object) -> None:
    row = command().to_persisted()
    mutator(row)  # type: ignore[operator]
    with pytest.raises((FinancialExecutionCommandError, TypeError, KeyError)):
        FinancialExecutionCommand.from_persisted(row)


def test_platform_row_rejects_ap_source_mixing() -> None:
    row = command(source_authority=platform_source(), provider_name="STRIPE").to_persisted()
    row["source_authority"]["payable_id"] = "forged"  # type: ignore[index]
    with pytest.raises((FinancialExecutionCommandError, TypeError)):
        FinancialExecutionCommand.from_persisted(row)


def test_no_execution_or_settlement_surface() -> None:
    names = {field.name for field in fields(FinancialExecutionCommand)}
    assert {"execution_status", "provider_execution_reference", "settlement_state", "paid"}.isdisjoint(names)
    assert not hasattr(command(), "settle")


# ARTIFACT: test_financial_execution_command.py
# VERSION: v2.0.0-M11-P5-R2A
# AUTHORITY BOUNDARY: certification evidence only; no execution or settlement authority.
# END OF WILSY OS SOVEREIGN ARTIFACT
