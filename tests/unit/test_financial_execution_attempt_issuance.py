"""TITLE: Financial Execution Attempt Issuance Unit Certificate
VERSION: v2.1.0-M11-P5-R2D-R0-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Certify canonical command readback and immutable PREPARED attempt projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_attempt_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS attempt-boundary certification owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.1.0-M11-P5-R2D-R0-R1 certifies exact tenant/ID/fingerprint admission, canonical projection, AP/Platform compatibility, and provider non-reselection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no credentials or provider payloads.
TENANT BOUNDARY: Canonical command lookup is tenant-scoped and caller-session-bound.
AUTHORITY BOUNDARY: Tests cover preparation evidence only; no provider or execution authority is granted.
FINANCIAL AUTHORITY BOUNDARY: PREPARED is not transmitted, executed, settled, paid, or accounted.
TRANSACTION BOUNDARY: Unit mocks represent a caller-owned active transaction; no Mongo or I/O.
FAIL-CLOSED DECLARATION: Missing, divergent, cross-tenant, and provider-mismatched commands reject.
"""
from dataclasses import fields
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from typing import Any

import pytest

from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    PlatformBillingCommandSource,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttemptState
from tools.eos.kennel.orchestration.financial_execution_attempt_issuance import (
    FinancialExecutionAttemptIssuance,
    FinancialExecutionAttemptIssuanceError,
    issue_financial_execution_attempt,
)
from tools.eos.kennel.registry.financial_execution_command_registry import FinancialExecutionCommandNotFoundError

NOW = datetime(2026, 9, 8, 10, tzinfo=timezone.utc)
FP = "a" * 128
SEL_FP = "b" * 128
REL_FP = "c" * 128


def ap_command(**changes: object) -> FinancialExecutionCommand:
    source = AccountsPayableCommandSource(
        execution_request_id="request-ap",
        execution_request_fingerprint=FP,
        selection_decision_id="selection-ap",
        selection_decision_fingerprint=SEL_FP,
        payable_id="payable-ap",
        release_authorization_id="release-ap",
        authorized_provider_name="PAYSHAP",
    )
    values: dict[str, Any] = dict(
        tenant_id="tenant-ap",
        execution_command_id="command-ap",
        idempotency_key="idem-ap",
        amount_minor=1000,
        currency="ZAR",
        payment_destination_reference="destination-ap",
        source_authority=source,
        provider_name="PAYSHAP",
        created_at=NOW,
        provider_metadata_reference=None,
    )
    values.update(changes)
    return FinancialExecutionCommand(**values)


def platform_command(**changes: object) -> FinancialExecutionCommand:
    source = PlatformBillingCommandSource(
        execution_request_id="request-platform",
        execution_request_fingerprint=FP,
        routing_decision_id="routing-platform",
        routing_decision_fingerprint=SEL_FP,
        platform_invoice_id="platform-invoice",
        release_authorization_id="release-platform",
        release_authorization_fingerprint=REL_FP,
        authorized_provider_name="PAYSHAP",
    )
    values: dict[str, Any] = dict(
        tenant_id="tenant-platform",
        execution_command_id="command-platform",
        idempotency_key="idem-platform",
        amount_minor=2000,
        currency="ZAR",
        payment_destination_reference="destination-platform",
        source_authority=source,
        provider_name="PAYSHAP",
        created_at=NOW,
        provider_metadata_reference=None,
    )
    values.update(changes)
    return FinancialExecutionCommand(**values)


def issuance(**changes: object) -> FinancialExecutionAttemptIssuance:
    values: dict[str, Any] = dict(
        execution_attempt_id="attempt-1",
        provider_name="PAYSHAP",
        created_at=NOW,
        destination_fingerprint="d" * 128,
        request_evidence_reference="request-evidence",
    )
    values.update(changes)
    return FinancialExecutionAttemptIssuance(**values)


def issue(command: FinancialExecutionCommand, **changes: object):
    canonical = command if "canonical" not in changes else changes.pop("canonical")
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=canonical,
    ) as read:
        value = issue_financial_execution_attempt(
            command,
            issuance(**changes),
            command_collection=Mock(),
            session=Mock(in_transaction=True),
        )
    return value, read


def test_canonical_readback_uses_tenant_command_id_and_session() -> None:
    command = ap_command()
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=command,
    ) as read:
        issue_financial_execution_attempt(
            command, issuance(), command_collection=Mock(), session=Mock(in_transaction=True)
        )
    assert read.call_args.args[:2] == ("tenant-ap", "command-ap")
    assert read.call_args.kwargs["session"].in_transaction is True


def test_exact_command_succeeds_and_canonical_projection_wins() -> None:
    command = ap_command()
    attempt, _ = issue(command)
    assert attempt.state is FinancialExecutionAttemptState.PREPARED
    assert attempt.tenant_id == command.tenant_id
    assert attempt.execution_command_id == command.execution_command_id
    assert attempt.provider_name == command.provider_name
    assert attempt.payment_destination_reference == command.payment_destination_reference
    assert attempt.request_fingerprint == command.fingerprint


def test_same_id_different_fingerprint_rejects() -> None:
    canonical = ap_command()
    caller = ap_command(payment_destination_reference="different-destination")
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=canonical,
    ), pytest.raises(FinancialExecutionAttemptIssuanceError, match="CANONICAL"):
        issue_financial_execution_attempt(caller, issuance(), command_collection=Mock(), session=Mock(in_transaction=True))


def test_same_fingerprint_different_id_rejects() -> None:
    canonical = ap_command()
    caller_base = ap_command(execution_command_id="other-command")

    class SameFingerprintCommand(FinancialExecutionCommand):
        @property
        def fingerprint(self) -> str:
            return canonical.fingerprint

    caller = SameFingerprintCommand(
        **{field.name: getattr(caller_base, field.name) for field in fields(FinancialExecutionCommand)}
    )
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=canonical,
    ), pytest.raises(FinancialExecutionAttemptIssuanceError):
        issue_financial_execution_attempt(caller, issuance(), command_collection=Mock(), session=Mock(in_transaction=True))


def test_tenant_mismatch_rejects() -> None:
    canonical = ap_command()
    caller = ap_command(tenant_id="other-tenant")
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=canonical,
    ), pytest.raises(FinancialExecutionAttemptIssuanceError):
        issue_financial_execution_attempt(caller, issuance(), command_collection=Mock(), session=Mock(in_transaction=True))


def test_missing_canonical_command_rejects() -> None:
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        side_effect=FinancialExecutionCommandNotFoundError("missing"),
    ), pytest.raises(FinancialExecutionAttemptIssuanceError, match="CANONICAL_COMMAND_REQUIRED"):
        issue_financial_execution_attempt(ap_command(), issuance(), command_collection=Mock(), session=Mock(in_transaction=True))


def test_cross_tenant_canonical_row_rejects() -> None:
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=ap_command(tenant_id="other-tenant"),
    ), pytest.raises(FinancialExecutionAttemptIssuanceError):
        issue_financial_execution_attempt(ap_command(), issuance(), command_collection=Mock(), session=Mock(in_transaction=True))


def test_caller_provider_is_correlation_only() -> None:
    command = ap_command()
    attempt, _ = issue(command, provider_name="PAYSHAP")
    assert attempt.provider_name == command.provider_name
    with pytest.raises(ValueError, match="provider"):
        issue(command, provider_name="ZAPPER")


def test_platform_command_canonicalizes_without_payable_access() -> None:
    command = platform_command()
    attempt, _ = issue(command)
    assert attempt.execution_command_id == command.execution_command_id
    assert attempt.request_fingerprint == command.fingerprint
    assert not hasattr(attempt, "payable_id")


def test_invalid_types_fail_before_canonical_read() -> None:
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get"
    ) as read:
        with pytest.raises(TypeError):
            issue_financial_execution_attempt(object(), issuance(), command_collection=Mock(), session=Mock(in_transaction=True))  # type: ignore[arg-type]
        assert not read.called


def test_issuance_requires_active_caller_session() -> None:
    with pytest.raises(FinancialExecutionAttemptIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        issue_financial_execution_attempt(ap_command(), issuance(), command_collection=Mock(), session=Mock(in_transaction=False))


def test_no_implicit_command_lookup_by_fingerprint() -> None:
    command = ap_command()
    _, read = issue(command)
    assert read.call_args.args[1] == command.execution_command_id
    assert command.fingerprint not in read.call_args.args[:2]


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "provider_name", "payment_destination_reference"])
def test_canonical_projected_fields_are_not_caller_rewritten(field: str) -> None:
    command = ap_command()
    attempt, _ = issue(command)
    assert getattr(attempt, field) == getattr(command, field)


def test_attempt_is_immutable_and_subject_neutral() -> None:
    command = ap_command()
    attempt, _ = issue(command)
    with pytest.raises(AttributeError):
        attempt.provider_name = "ZAPPER"  # type: ignore[misc]
    assert not hasattr(attempt, "family")
    assert not hasattr(attempt, "payable_id")
    assert not hasattr(attempt, "platform_invoice_id")


def test_no_provider_transport_settlement_or_client_invoice_surface() -> None:
    attempt, _ = issue(ap_command())
    assert attempt.state is FinancialExecutionAttemptState.PREPARED
    assert not {"settled", "paid", "settlement_id", "client_invoice_id"}.intersection(attempt.to_dict())


def test_none_session_is_rejected_before_command_read() -> None:
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get"
    ) as read, pytest.raises(FinancialExecutionAttemptIssuanceError, match="ACTIVE_TRANSACTION_REQUIRED"):
        issue_financial_execution_attempt(ap_command(), issuance(), command_collection=Mock(), session=None)  # type: ignore[arg-type]
    assert not read.called


def test_issuer_never_starts_commits_or_aborts_transaction() -> None:
    session = Mock(in_transaction=True)
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=ap_command(),
    ):
        issue_financial_execution_attempt(ap_command(), issuance(), command_collection=Mock(), session=session)
    session.start_transaction.assert_not_called()
    session.commit_transaction.assert_not_called()
    session.abort_transaction.assert_not_called()


def test_canonical_registry_receives_the_supplied_collection() -> None:
    command = ap_command()
    collection = Mock()
    session = Mock(in_transaction=True)
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get",
        return_value=command,
    ) as read:
        issue_financial_execution_attempt(command, issuance(), command_collection=collection, session=session)
    assert read.call_args.args[2] is collection


def test_attempt_identity_and_evidence_are_issuance_only() -> None:
    command = ap_command()
    attempt, _ = issue(
        command,
        execution_attempt_id="attempt-custom",
        destination_fingerprint="e" * 128,
        request_evidence_reference="evidence-custom",
    )
    assert attempt.execution_attempt_id == "attempt-custom"
    assert attempt.destination_fingerprint == "e" * 128
    assert attempt.request_evidence_reference == "evidence-custom"
    assert attempt.execution_command_id == command.execution_command_id


def test_platform_provider_is_asserted_not_selected() -> None:
    command = platform_command()
    with pytest.raises(ValueError, match="provider"):
        issue(command, provider_name="ZAPPER")


def test_missing_issuance_type_rejects_before_command_read() -> None:
    with patch(
        "tools.eos.kennel.orchestration.financial_execution_attempt_issuance.FinancialExecutionCommandRegistry.get"
    ) as read, pytest.raises(TypeError, match="issuance"):
        issue_financial_execution_attempt(ap_command(), object(), command_collection=Mock(), session=Mock(in_transaction=True))  # type: ignore[arg-type]
    assert not read.called


def test_canonical_command_is_the_only_source_of_destination() -> None:
    canonical = ap_command(payment_destination_reference="canonical-destination")
    caller = ap_command(payment_destination_reference="caller-destination")
    with pytest.raises(FinancialExecutionAttemptIssuanceError, match="CANONICAL"):
        issue_financial_execution_attempt(caller, issuance(), command_collection=Mock(), session=Mock(in_transaction=True))
    assert canonical.payment_destination_reference == "canonical-destination"


def test_canonical_command_is_the_only_source_of_provider() -> None:
    canonical = ap_command()
    with pytest.raises(ValueError, match="provider"):
        issue(canonical, provider_name="ZAPPER")


# ARTIFACT: test_financial_execution_attempt_issuance.py
# VERSION: v2.1.0-M11-P5-R2D-R0-R1
# AUTHORITY BOUNDARY: canonical-attempt certificate only; no provider, truth, or settlement authority.
# TENANT POSTURE: synthetic tenant-scoped fixtures and caller-owned session mocks.
# FAIL-CLOSED POSTURE: divergent, missing, cross-tenant, and provider-mismatched commands reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns later execution truth.
# END OF WILSY OS SOVEREIGN ARTIFACT
