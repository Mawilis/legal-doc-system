"""Unit certification for the canonical AP-to-Kennel command issuance boundary.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND-ISSUANCE-UNIT-CERT
AUTHORITY: deterministic conversion evidence only; no persistence or provider authority.
"""
from datetime import datetime, timezone
from typing import Any, cast

import pytest

from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand
from tools.eos.kennel.orchestration.financial_execution_command_issuance import (
    FinancialExecutionCommandIssuance,
    issue_financial_execution_command,
)
from tools.eos.saas.domain.vendor_bill_financial_execution_request import VendorBillFinancialExecutionRequest


NOW = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)


def request() -> VendorBillFinancialExecutionRequest:
    return VendorBillFinancialExecutionRequest(
        execution_command_id="request-command",
        tenant_id="tenant-1",
        payable_id="payable-1",
        release_authorization_id="release-1",
        idempotency_key="request-idem",
        amount_minor=1000,
        currency="ZAR",
        payment_destination_reference="destination-ref",
        requested_by_actor_id="actor-1",
        requested_at=NOW,
    )


def issuance(**changes: object) -> FinancialExecutionCommandIssuance:
    values: dict[str, object] = {
        "execution_command_id": "command-1",
        "idempotency_key": "idem-1",
        "issued_at": NOW,
        "provider_name": "PAYSHAP",
        "provider_metadata_reference": "metadata-ref",
    }
    values.update(changes)
    return FinancialExecutionCommandIssuance(**cast(Any, values))


def test_returns_canonical_domain_command_with_explicit_authority() -> None:
    result = issue_financial_execution_command(request(), issuance())
    assert type(result) is FinancialExecutionCommand
    assert result.tenant_id == "tenant-1"
    assert result.execution_command_id == "command-1"
    assert result.idempotency_key == "idem-1"
    assert result.created_at == NOW
    assert result.provider_name == "PAYSHAP"
    assert result.provider_metadata_reference == "metadata-ref"


def test_request_fields_and_issuance_fields_remain_distinct() -> None:
    result = issue_financial_execution_command(
        request(), issuance(execution_command_id="issued-command", idempotency_key="issued-idem", issued_at=NOW)
    )
    assert result.payable_id == "payable-1"
    assert result.amount_minor == 1000
    assert result.execution_command_id == "issued-command"
    assert result.idempotency_key == "issued-idem"


def test_timezone_and_domain_validation_are_preserved() -> None:
    with pytest.raises(ValueError):
        issue_financial_execution_command(request(), issuance(issued_at=datetime(2026, 8, 28, 12, 0)))


def test_boundary_is_pure_and_requires_explicit_types() -> None:
    with pytest.raises(TypeError):
        issue_financial_execution_command(cast(Any, object()), issuance())
    with pytest.raises(TypeError):
        issue_financial_execution_command(request(), cast(Any, object()))


# ARTIFACT: test_financial_execution_command_issuance.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-COMMAND-ISSUANCE-UNIT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
