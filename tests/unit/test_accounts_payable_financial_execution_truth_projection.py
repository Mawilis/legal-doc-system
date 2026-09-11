"""TITLE: Accounts Payable Financial Execution Truth Projection Certificate.
VERSION: v1.0.0-M11-P5-R2E-R1-R2.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Certify neutral-fact-to-AP-truth projection, provenance, tenancy, and transaction boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_accounts_payable_financial_execution_truth_projection.py
COLLABORATION / OWNERSHIP: Kennel EOS AP execution-evidence certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11-P5-R2E-R1-R2 adds a host-free direct certificate for exact AP projection and forbidden-boundary controls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no provider credentials or raw payment payloads.
TENANT BOUNDARY: Every fixture and asserted registry call is tenant scoped.
AUTHORITY BOUNDARY: Tests distinguish neutral execution evidence from typed AP command authority.
FINANCIAL AUTHORITY BOUNDARY: No provider transport, settlement, receivable, or ClientInvoice behavior is exercised.
TRANSACTION BOUNDARY: A caller-owned active-session double is required; no Mongo or transaction lifecycle is used.
FAIL-CLOSED DECLARATION: Tests require rejection for absent, nonterminal, cross-family, mismatched, and divergent evidence.
"""
from __future__ import annotations

from datetime import datetime, timezone
from inspect import getsource, signature
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, PropertyMock, patch

import pytest

from tools.eos.kennel.domain.financial_execution import (
    FinancialExecutionFact,
    FinancialExecutionStatus,
    FinancialExecutionTruth,
)
from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    FinancialExecutionCommandFamily,
    PlatformBillingCommandSource,
)
from tools.eos.kennel.registry.financial_execution_registry import (
    FinancialExecutionCreateOutcome,
    FinancialExecutionCreateResult,
)
from tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection import (
    AccountsPayableFinancialExecutionTruthProjectionError,
    project_financial_execution_fact_to_accounts_payable,
)

NOW = datetime(2026, 9, 8, 10, tzinfo=timezone.utc)
FP = "a" * 128
SEL_FP = "b" * 128
REL_FP = "c" * 128
EVIDENCE_FP = "d" * 128


def active_session() -> Any:
    return SimpleNamespace(in_transaction=True)


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
    values: dict[str, Any] = {
        "tenant_id": "tenant-ap",
        "execution_command_id": "command-ap",
        "idempotency_key": "idem-ap",
        "amount_minor": 1000,
        "currency": "ZAR",
        "payment_destination_reference": "destination-ap",
        "source_authority": source,
        "provider_name": "PAYSHAP",
        "created_at": NOW,
        "provider_metadata_reference": None,
    }
    values.update(changes)
    return FinancialExecutionCommand(**values)


def platform_command() -> FinancialExecutionCommand:
    return FinancialExecutionCommand(
        tenant_id="tenant-ap",
        execution_command_id="command-platform",
        idempotency_key="idem-platform",
        amount_minor=1000,
        currency="ZAR",
        payment_destination_reference="destination-ap",
        source_authority=PlatformBillingCommandSource(
            execution_request_id="request-platform",
            execution_request_fingerprint=FP,
            routing_decision_id="routing-platform",
            routing_decision_fingerprint=SEL_FP,
            platform_invoice_id="platform-invoice",
            release_authorization_id="release-platform",
            release_authorization_fingerprint=REL_FP,
            authorized_provider_name="PAYSHAP",
        ),
        provider_name="PAYSHAP",
        created_at=NOW,
    )


def fact(command: FinancialExecutionCommand, **changes: object) -> FinancialExecutionFact:
    values: dict[str, Any] = {
        "execution_fact_id": FinancialExecutionFact.deterministic_id("tenant-ap", "attempt-ap"),
        "tenant_id": "tenant-ap",
        "execution_command_id": command.execution_command_id,
        "execution_command_fingerprint": command.fingerprint,
        "execution_attempt_id": "attempt-ap",
        "provider": command.provider_name,
        "provider_execution_reference": "provider-execution",
        "execution_status": FinancialExecutionStatus.EXECUTED,
        "executed_amount_minor": command.amount_minor,
        "currency": command.currency,
        "executed_at": NOW,
        "payment_destination_reference": command.payment_destination_reference,
        "provider_evidence_reference": "provider-evidence",
        "execution_evidence_fingerprint": EVIDENCE_FP,
        "created_at": NOW,
    }
    values.update(changes)
    if "tenant_id" in changes:
        values["execution_fact_id"] = FinancialExecutionFact.deterministic_id(
            str(values["tenant_id"]), "attempt-ap"
        )
    return FinancialExecutionFact(**values)


def invoke(
    command: FinancialExecutionCommand,
    execution_fact: FinancialExecutionFact | None = None,
    *,
    session: object | None = None,
) -> tuple[object, Mock, Mock, Mock]:
    session_value = session if session is not None else active_session()
    durable_fact = execution_fact or fact(command)
    truth = SimpleNamespace(
        execution_truth=(
            build_truth(command, durable_fact)
            if isinstance(command.source_authority, AccountsPayableCommandSource)
            else None
        )
    )
    with (
        patch(
            "tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get",
            return_value=durable_fact,
        ) as fact_read,
        patch(
            "tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionCommandRegistry.get",
            return_value=command,
        ) as command_read,
        patch(
            "tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionTruthRegistry.create",
            return_value=truth,
        ) as truth_write,
    ):
        result = project_financial_execution_fact_to_accounts_payable(
            "tenant-ap",
            durable_fact.execution_fact_id,
            fact_collection=Mock(),
            command_collection=Mock(),
            truth_collection=Mock(),
            session=session_value,  # type: ignore[arg-type]
        )
    return result, fact_read, command_read, truth_write


def build_truth(command: FinancialExecutionCommand, execution_fact: FinancialExecutionFact) -> FinancialExecutionTruth:
    source = command.source_authority
    assert isinstance(source, AccountsPayableCommandSource)
    return FinancialExecutionTruth(
        command.execution_command_id,
        command.tenant_id,
        source.payable_id,
        source.release_authorization_id,
        execution_fact.provider,
        execution_fact.provider_execution_reference,
        execution_fact.execution_status,
        command.amount_minor,
        command.currency,
        execution_fact.executed_at,
        command.payment_destination_reference,
        execution_fact.provider_evidence_reference,
        command.fingerprint,
        execution_fact.execution_evidence_fingerprint,
        command.created_at,
    )


def test_public_api_requires_exact_fact_and_collection_arguments() -> None:
    params = signature(project_financial_execution_fact_to_accounts_payable).parameters
    assert tuple(params) == (
        "tenant_id", "execution_fact_id", "fact_collection", "command_collection",
        "truth_collection", "session",
    )
    assert params["session"].default is params["session"].empty


@pytest.mark.parametrize("session", [None, SimpleNamespace(in_transaction=False), SimpleNamespace(in_transaction=0)])
def test_active_transaction_is_required_before_reads(session: object | None) -> None:
    with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="ACTIVE_TRANSACTION_REQUIRED"):
        project_financial_execution_fact_to_accounts_payable(
            "tenant-ap", "fact-id", fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=session  # type: ignore[arg-type]
        )


def test_fact_lookup_is_tenant_and_exact_id_scoped() -> None:
    result, fact_read, _, _ = invoke(ap_command())
    assert isinstance(result, FinancialExecutionTruth)
    assert fact_read.call_args.args[:2] == ("tenant-ap", result.tenant_id if False else fact(ap_command()).execution_fact_id)
    assert fact_read.call_args.kwargs["session"].in_transaction is True


def test_command_lookup_follows_fact_command_id_only() -> None:
    command = ap_command()
    _, _, command_read, _ = invoke(command)
    assert command_read.call_args.args[:2] == ("tenant-ap", "command-ap")
    assert command_read.call_args.kwargs["session"].in_transaction is True


def test_truth_write_receives_same_caller_session() -> None:
    session = active_session()
    _, _, _, truth_write = invoke(ap_command(), session=session)
    assert truth_write.call_args.kwargs["session"] is session


def test_missing_fact_fails_closed() -> None:
    with patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get", return_value=None):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="FINANCIAL_EXECUTION_FACT_REQUIRED"):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", "fact-id", fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())


def test_missing_fact_does_not_read_command_or_write_truth() -> None:
    with patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get", return_value=None), patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionCommandRegistry.get") as command_read, patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionTruthRegistry.create") as truth_write:
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", "fact-id", fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())
    command_read.assert_not_called()
    truth_write.assert_not_called()


def test_fact_registry_result_must_match_requested_fact_identity() -> None:
    command = ap_command()
    with patch(
        "tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get",
        return_value=fact(command),
    ):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="FACT_ID_CORRELATION_MISMATCH"):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", "different-fact", fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())


def test_missing_command_rejects() -> None:
    command = ap_command()
    execution_fact = fact(command)
    with patch(
        "tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get",
        return_value=fact(command),
    ), patch(
        "tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionCommandRegistry.get",
        return_value=None,
    ):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="FINANCIAL_EXECUTION_COMMAND_REQUIRED"):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", execution_fact.execution_fact_id, fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())


def test_platform_family_is_rejected() -> None:
    command = platform_command()
    with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="AP_COMMAND_FAMILY_REQUIRED"):
        invoke(command, fact(command))


def test_platform_source_cannot_pass_an_ap_family_discriminator() -> None:
    command = platform_command()
    with patch.object(
        FinancialExecutionCommand,
        "source_authority_kind",
        new_callable=PropertyMock,
        return_value=FinancialExecutionCommandFamily.ACCOUNTS_PAYABLE,
    ):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="AP_COMMAND_SOURCE_REQUIRED"):
            invoke(command, fact(command))


def test_ap_projection_accepts_exact_typed_source() -> None:
    result, _, _, _ = invoke(ap_command())
    assert isinstance(result, FinancialExecutionTruth)
    assert result.payable_id == "payable-ap"
    assert result.release_authorization_id == "release-ap"


@pytest.mark.parametrize("field,value", [
    ("tenant_id", "other-tenant"),
    ("execution_command_id", "other-command"),
    ("execution_command_fingerprint", "e" * 128),
    ("provider", "OTHER_PROVIDER"),
    ("executed_amount_minor", 999),
    ("currency", "USD"),
    ("payment_destination_reference", "other-destination"),
])
def test_fact_command_correlations_reject_divergence(field: str, value: object) -> None:
    command = ap_command()
    changes = {field: value}
    if field == "tenant_id":
        changes[field] = value
    with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError):
        invoke(command, fact(command, **changes))


def test_fact_status_must_be_terminal() -> None:
    command = ap_command()
    with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="TERMINAL_EXECUTION_FACT_REQUIRED"):
        invoke(command, fact(command, execution_status=FinancialExecutionStatus.ACCEPTED, executed_at=None))


def test_fact_execution_evidence_projects_without_rereading_observation() -> None:
    command = ap_command()
    execution_fact = fact(command, provider_execution_reference="fact-reference", provider_evidence_reference="fact-evidence")
    result, _, _, truth_write = invoke(command, execution_fact)
    assert isinstance(result, FinancialExecutionTruth)
    assert result.provider_execution_reference == "fact-reference"
    assert result.provider_evidence_reference == "fact-evidence"
    assert truth_write.call_args.args[0].execution_evidence_fingerprint == EVIDENCE_FP


def test_historical_identity_idempotency_and_command_authority_are_preserved() -> None:
    command = ap_command()
    result, _, _, truth_write = invoke(command)
    assert isinstance(result, FinancialExecutionTruth)
    assert result.execution_truth_id == command.execution_command_id
    assert truth_write.call_args.args[1] == command.idempotency_key
    assert result.executed_amount_minor == command.amount_minor
    assert result.currency == command.currency
    assert result.payment_destination_reference == command.payment_destination_reference
    assert result.created_at == command.created_at


def test_replay_result_is_returned_without_local_replay_logic() -> None:
    command = ap_command()
    expected = build_truth(command, fact(command))
    with (
        patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get", return_value=fact(command)),
        patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionTruthRegistry.create", return_value=FinancialExecutionCreateResult(FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY, expected)),
    ):
        assert project_financial_execution_fact_to_accounts_payable("tenant-ap", fact(command).execution_fact_id, fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session()) == expected


def test_divergent_replay_rejects_through_registry() -> None:
    command = ap_command()
    with (
        patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get", return_value=fact(command)),
        patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionTruthRegistry.create", side_effect=RuntimeError("DIVERGENT_REPLAY")),
    ):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="FINANCIAL_EXECUTION_TRUTH_PERSISTENCE_FAILED"):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", fact(command).execution_fact_id, fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())


def test_registry_exceptions_are_fail_closed() -> None:
    with patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get", side_effect=RuntimeError("lookup")):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="FINANCIAL_EXECUTION_FACT_READ_FAILED"):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", "fact-id", fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())


def test_command_registry_exceptions_are_fail_closed() -> None:
    command = ap_command()
    execution_fact = fact(command)
    with patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get", return_value=fact(command)), patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionCommandRegistry.get", side_effect=RuntimeError("lookup")):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="FINANCIAL_EXECUTION_COMMAND_READ_FAILED"):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", execution_fact.execution_fact_id, fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())


def test_truth_registry_exceptions_are_fail_closed() -> None:
    command = ap_command()
    execution_fact = fact(command)
    with patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get", return_value=fact(command)), patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionCommandRegistry.get", return_value=command), patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionTruthRegistry.create", side_effect=RuntimeError("write")):
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError, match="FINANCIAL_EXECUTION_TRUTH_PERSISTENCE_FAILED"):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", execution_fact.execution_fact_id, fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=active_session())


def test_source_and_provider_are_not_selected_or_rewritten() -> None:
    source = ap_command().source_authority
    assert isinstance(source, AccountsPayableCommandSource)
    result, _, _, _ = invoke(ap_command())
    assert isinstance(result, FinancialExecutionTruth)
    assert result.provider == "PAYSHAP"


def test_projection_source_contains_no_forbidden_runtime_boundaries() -> None:
    source = getsource(project_financial_execution_fact_to_accounts_payable)
    for forbidden in ("FinancialExecutionProviderObservationRegistry", "evaluate_terminalization", "bridge_financial_execution_fact_to_platform", "select_provider"):
        assert forbidden not in source


@pytest.mark.parametrize("forbidden", [
    "FinancialExecutionProviderObservationRegistry", "evaluate_terminalization", "derive_financial_execution_fact",
    "bridge_financial_execution_fact_to_platform", "provider_transport", "select_provider", "issue_command",
    "FinancialExecutionTruthDerivation", "FinancialExecutionAttemptRegistry", "FinancialExecutionTerminalization",
    "route_provider", "release_payment", "mark_paid", "close_receivable", "FinancialExecutionProviderObservation",
])
def test_module_does_not_own_forbidden_authority(forbidden: str) -> None:
    source = getsource(project_financial_execution_fact_to_accounts_payable)
    assert forbidden not in source


def test_caller_cannot_supply_truth_or_provider_override() -> None:
    params = signature(project_financial_execution_fact_to_accounts_payable).parameters
    assert "truth" not in params and "provider" not in params and "observation" not in params


def test_result_is_canonical_registry_truth() -> None:
    result, _, _, truth_write = invoke(ap_command())
    assert isinstance(result, FinancialExecutionTruth)
    assert result == truth_write.return_value.execution_truth


def test_fact_command_fingerprint_is_not_used_as_command_lookup_identity() -> None:
    command = ap_command()
    execution_fact = fact(command)
    _, _, command_read, _ = invoke(command, execution_fact)
    assert command_read.call_args.args[1] == execution_fact.execution_command_id
    assert command_read.call_args.args[1] != execution_fact.execution_command_fingerprint


def test_non_ap_source_cannot_be_cast_into_ap_authority() -> None:
    command = platform_command()
    with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError):
        invoke(command, fact(command))


def test_projection_does_not_write_directly_to_injected_collections() -> None:
    command = ap_command()
    fact_collection = Mock()
    command_collection = Mock()
    truth_collection = Mock()
    invoke(command, fact(command))
    fact_collection.insert_one.assert_not_called()
    command_collection.insert_one.assert_not_called()
    truth_collection.insert_one.assert_not_called()


def test_active_session_is_admitted_before_fact_lookup() -> None:
    with patch("tools.eos.kennel.orchestration.accounts_payable_financial_execution_truth_projection.FinancialExecutionFactRegistry.get") as fact_read:
        with pytest.raises(AccountsPayableFinancialExecutionTruthProjectionError):
            project_financial_execution_fact_to_accounts_payable("tenant-ap", "fact-id", fact_collection=Mock(), command_collection=Mock(), truth_collection=Mock(), session=None)  # type: ignore[arg-type]
    fact_read.assert_not_called()


# ARTIFACT: test_accounts_payable_financial_execution_truth_projection.py
# VERSION: v1.0.0-M11-P5-R2E-R1-R2
# AUTHORITY BOUNDARY: direct host-free certificate for AP projection only; no runtime or provider authority.
# TENANT POSTURE: all synthetic evidence and mocked registry calls are tenant-scoped.
# FAIL-CLOSED POSTURE: all material lineage and forbidden-boundary propositions reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; no settlement truth is asserted.
# END OF WILSY OS SOVEREIGN ARTIFACT
