"""Unit certificate for the retired untyped issuance boundary.

TITLE: Financial Execution Command Issuance Certification
VERSION: v2.0.0-M11-P5-R2A
AUTHORITY: Certification evidence only; no command or provider authority.
EPITOME: Ensure legacy caller-driven issuance fails explicitly before construction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_command_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS generic command boundary certification.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v2.0.0-M11-P5-R2A certifies stable legacy rejection and preserved public value shape.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: No persistence or lookup is performed.
FINANCIAL TRUTH BOUNDARY: No execution, attempt, truth, settlement, or receivable mutation.
TRANSACTION BOUNDARY: No transaction lifecycle is opened.
"""
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from tools.eos.kennel.orchestration.financial_execution_command_issuance import (
    FinancialExecutionCommandIssuance,
    FinancialExecutionCommandLegacyIssuanceError,
    issue_financial_execution_command,
)
from tools.eos.saas.domain.vendor_bill_financial_execution_request import VendorBillFinancialExecutionRequest

NOW = datetime(2026, 9, 7, 10, tzinfo=timezone.utc)


def request() -> VendorBillFinancialExecutionRequest:
    return VendorBillFinancialExecutionRequest(execution_command_id="request-command", tenant_id="tenant-1", payable_id="payable-1", release_authorization_id="release-1", idempotency_key="request-idem", amount_minor=1000, currency="ZAR", payment_destination_reference="destination-ref", requested_by_actor_id="actor-1", requested_at=NOW)


def issuance(**changes: object) -> FinancialExecutionCommandIssuance:
    values: dict[str, object] = {"execution_command_id": "command-1", "idempotency_key": "idem-1", "issued_at": NOW, "provider_name": "PAYSHAP", "provider_metadata_reference": "metadata-ref"}
    values.update(changes)
    return FinancialExecutionCommandIssuance(**cast(Any, values))


def test_legacy_issuer_fails_with_stable_authority_error() -> None:
    with pytest.raises(FinancialExecutionCommandLegacyIssuanceError) as error:
        issue_financial_execution_command(request(), issuance())
    assert error.value.code == "FINANCIAL_EXECUTION_COMMAND_LEGACY_ISSUANCE_DISABLED"
    assert not isinstance(error.value, TypeError)


@pytest.mark.parametrize("variant", [issuance(provider_name=None), issuance(provider_name="STRIPE"), issuance(provider_metadata_reference=None)])
def test_every_legacy_provider_shape_is_rejected(variant: FinancialExecutionCommandIssuance) -> None:
    with pytest.raises(FinancialExecutionCommandLegacyIssuanceError):
        issue_financial_execution_command(request(), variant)


def test_public_issuance_value_shape_remains_constructible() -> None:
    value = issuance()
    assert value.execution_command_id == "command-1"
    assert value.idempotency_key == "idem-1"
    assert value.issued_at == NOW


def test_invalid_legacy_inputs_fail_same_explicit_boundary() -> None:
    with pytest.raises(FinancialExecutionCommandLegacyIssuanceError):
        issue_financial_execution_command(cast(Any, object()), issuance())
    with pytest.raises(FinancialExecutionCommandLegacyIssuanceError):
        issue_financial_execution_command(request(), cast(Any, object()))


# ARTIFACT: test_financial_execution_command_issuance.py
# VERSION: v2.0.0-M11-P5-R2A
# AUTHORITY BOUNDARY: certification evidence only; legacy issuance must not construct commands.
# END OF WILSY OS SOVEREIGN ARTIFACT
