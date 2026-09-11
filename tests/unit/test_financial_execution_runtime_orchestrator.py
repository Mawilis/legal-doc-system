"""TITLE: Financial Execution Runtime Orchestrator Certificate.
VERSION: v1.0.0-M11-P5-R2E-R2.
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Certify one-session neutral-fact derivation and closed AP/Platform dispatch composition.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_runtime_orchestrator.py
COLLABORATION / OWNERSHIP: Kennel EOS runtime-composition certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.0.0-M11-P5-R2E-R2 adds a host-free certificate for exactly-once neutral derivation and closed family dispatch.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no credentials or provider transport.
TENANT BOUNDARY: Every runtime input and child call is tenant scoped.
AUTHORITY BOUNDARY: Runtime composition only; child owners retain derivation and family truth authority.
FINANCIAL AUTHORITY BOUNDARY: No command issuance, provider selection, settlement, receivable, or invoice authority.
TRANSACTION BOUNDARY: Caller-owned active-session double spans every child operation.
FAIL-CLOSED DECLARATION: Missing, uncorrelated, unsupported, and child-failure paths reject or propagate.
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
    FinancialExecutionFactCreateOutcome,
    FinancialExecutionFactCreateResult,
)
from tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator import (
    FinancialExecutionRuntimeOrchestratorError,
    orchestrate_terminal_execution_fact_and_projection,
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
        "tenant_id": "tenant-ap", "execution_command_id": "command-ap",
        "idempotency_key": "idem-ap", "amount_minor": 1000, "currency": "ZAR",
        "payment_destination_reference": "destination-ap", "source_authority": source,
        "provider_name": "PAYSHAP", "created_at": NOW,
        "provider_metadata_reference": None,
    }
    values.update(changes)
    return FinancialExecutionCommand(**values)


def platform_command(**changes: object) -> FinancialExecutionCommand:
    source = PlatformBillingCommandSource(
        execution_request_id="request-platform", execution_request_fingerprint=FP,
        routing_decision_id="routing-platform", routing_decision_fingerprint=SEL_FP,
        platform_invoice_id="platform-invoice", release_authorization_id="release-platform",
        release_authorization_fingerprint=REL_FP, authorized_provider_name="PAYSHAP",
    )
    values: dict[str, Any] = {
        "tenant_id": "tenant-ap", "execution_command_id": "command-platform",
        "idempotency_key": "idem-platform", "amount_minor": 1000, "currency": "ZAR",
        "payment_destination_reference": "destination-ap", "source_authority": source,
        "provider_name": "PAYSHAP", "created_at": NOW,
        "provider_metadata_reference": None,
    }
    values.update(changes)
    return FinancialExecutionCommand(**values)


def fact(command: FinancialExecutionCommand, *, tenant_id: str = "tenant-ap", **changes: object) -> FinancialExecutionFact:
    values: dict[str, Any] = {
        "execution_fact_id": FinancialExecutionFact.deterministic_id(tenant_id, "attempt-runtime"),
        "tenant_id": tenant_id, "execution_command_id": command.execution_command_id,
        "execution_command_fingerprint": command.fingerprint, "execution_attempt_id": "attempt-runtime",
        "provider": command.provider_name, "provider_execution_reference": "provider-execution",
        "execution_status": FinancialExecutionStatus.EXECUTED, "executed_amount_minor": command.amount_minor,
        "currency": command.currency, "executed_at": NOW,
        "payment_destination_reference": command.payment_destination_reference,
        "provider_evidence_reference": "provider-evidence", "execution_evidence_fingerprint": EVIDENCE_FP,
        "created_at": NOW,
    }
    values.update(changes)
    if "tenant_id" in changes:
        values["execution_fact_id"] = FinancialExecutionFact.deterministic_id(str(values["tenant_id"]), "attempt-runtime")
    return FinancialExecutionFact(**values)


def run_runtime(command: FinancialExecutionCommand, *, execution_fact: FinancialExecutionFact | None = None, session: Any = None, derive_result: object | None = None, ap_projection_side_effect: BaseException | None = None, platform_projection_side_effect: BaseException | None = None) -> tuple[object, Mock, Mock, Mock, Mock]:
    tx = session if session is not None else active_session()
    durable_fact = execution_fact or fact(command)
    derivation_result = derive_result or FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.IDEMPOTENT_REPLAY, durable_fact)
    ap_truth = (
        build_ap_truth(command, durable_fact)
        if isinstance(command.source_authority, AccountsPayableCommandSource)
        else None
    )
    platform_truth = SimpleNamespace(tenant_id=command.tenant_id, execution_truth_id=command.execution_command_id)
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.derive_financial_execution_fact", return_value=derivation_result) as derive,
        patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.FinancialExecutionCommandRegistry.get", return_value=command) as command_read,
        patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.project_financial_execution_fact_to_accounts_payable", side_effect=ap_projection_side_effect, return_value=ap_truth) as ap_projection,
        patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.bridge_financial_execution_fact_to_platform", side_effect=platform_projection_side_effect, return_value=platform_truth) as platform_projection,
    ):
        result = orchestrate_terminal_execution_fact_and_projection(
            "tenant-ap", "attempt-runtime", command_collection=Mock(), attempt_collection=Mock(),
            observation_collection=Mock(), fact_collection=Mock(), ap_truth_collection=Mock(),
            platform_truth_collection=Mock(), execution_time_evidence=Mock(), session=tx,
        )
    return result, derive, command_read, ap_projection, platform_projection


def build_ap_truth(command: FinancialExecutionCommand, execution_fact: FinancialExecutionFact) -> FinancialExecutionTruth:
    source = command.source_authority
    assert isinstance(source, AccountsPayableCommandSource)
    return FinancialExecutionTruth(
        command.execution_command_id, command.tenant_id, source.payable_id,
        source.release_authorization_id, execution_fact.provider,
        execution_fact.provider_execution_reference, execution_fact.execution_status,
        command.amount_minor, command.currency, execution_fact.executed_at,
        command.payment_destination_reference, execution_fact.provider_evidence_reference,
        command.fingerprint, execution_fact.execution_evidence_fingerprint, command.created_at,
    )


def test_public_api_has_only_canonical_caller_authority() -> None:
    params = signature(orchestrate_terminal_execution_fact_and_projection).parameters
    assert tuple(params) == ("tenant_id", "execution_attempt_id", "command_collection", "attempt_collection", "observation_collection", "fact_collection", "ap_truth_collection", "platform_truth_collection", "execution_time_evidence", "session")
    for forbidden in ("command_id", "fact_id", "provider", "family", "payable_id", "platform_invoice_id", "policy", "routing", "status", "amount_minor", "currency", "payment_destination_reference"):
        assert forbidden not in params


@pytest.mark.parametrize("session", [None, SimpleNamespace(in_transaction=False), SimpleNamespace(in_transaction=0)])
def test_active_transaction_required_before_derivation(session: object | None) -> None:
    with patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.derive_financial_execution_fact") as derive:
        with pytest.raises(FinancialExecutionRuntimeOrchestratorError, match="ACTIVE_TRANSACTION_REQUIRED"):
            orchestrate_terminal_execution_fact_and_projection("tenant-ap", "attempt-runtime", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), fact_collection=Mock(), ap_truth_collection=Mock(), platform_truth_collection=Mock(), execution_time_evidence=Mock(), session=session)  # type: ignore[arg-type]
    derive.assert_not_called()


def test_ap_dispatch_returns_ap_truth_and_calls_once() -> None:
    command = ap_command()
    result, derive, command_read, ap_projection, platform_projection = run_runtime(command)
    assert isinstance(result, FinancialExecutionTruth)
    derive.assert_called_once()
    ap_projection.assert_called_once()
    platform_projection.assert_not_called()
    assert command_read.call_count == 1


def test_platform_dispatch_returns_platform_truth_and_calls_once() -> None:
    command = platform_command()
    result, derive, command_read, ap_projection, platform_projection = run_runtime(command)
    assert isinstance(result, SimpleNamespace)
    assert result.execution_truth_id == "command-platform"
    derive.assert_called_once()
    platform_projection.assert_called_once()
    ap_projection.assert_not_called()
    assert command_read.call_count == 1


def test_derivation_receives_all_dependencies_and_same_session() -> None:
    command = ap_command()
    session = active_session()
    _, derive, _, _, _ = run_runtime(command, session=session)
    kwargs = derive.call_args.kwargs
    assert kwargs["session"] is session
    assert kwargs["command_collection"] is not None
    assert kwargs["attempt_collection"] is not None
    assert kwargs["observation_collection"] is not None
    assert kwargs["fact_collection"] is not None
    assert derive.call_args.args == ("tenant-ap", "attempt-runtime")


def test_command_read_uses_fact_command_id_and_same_session() -> None:
    command = ap_command()
    session = active_session()
    _, _, command_read, _, _ = run_runtime(command, session=session)
    assert command_read.call_args.args[:2] == ("tenant-ap", "command-ap")
    assert command_read.call_args.kwargs["session"] is session


def test_ap_projection_receives_fact_id_collection_and_session() -> None:
    command = ap_command()
    session = active_session()
    execution_fact = fact(command)
    _, _, _, ap_projection, _ = run_runtime(command, execution_fact=execution_fact, session=session)
    assert ap_projection.call_args.args[:2] == ("tenant-ap", execution_fact.execution_fact_id)
    assert ap_projection.call_args.kwargs["session"] is session
    assert "truth_collection" in ap_projection.call_args.kwargs


def test_platform_projection_receives_fact_id_collection_and_session() -> None:
    command = platform_command()
    session = active_session()
    execution_fact = fact(command)
    _, _, _, _, platform_projection = run_runtime(command, execution_fact=execution_fact, session=session)
    assert platform_projection.call_args.args[:2] == ("tenant-ap", execution_fact.execution_fact_id)
    assert platform_projection.call_args.kwargs["session"] is session
    assert "platform_truth_collection" in platform_projection.call_args.kwargs


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "execution_command_fingerprint", "provider", "executed_amount_minor", "currency", "payment_destination_reference"])
def test_uncorrelated_fact_command_material_rejects(field: str) -> None:
    command = ap_command()
    changes: dict[str, Any] = {"execution_command_fingerprint": "e" * 128}
    if field == "tenant_id":
        execution_fact = fact(command, tenant_id="other-tenant")
    else:
        values = {"execution_command_id": "other-command", "execution_command_fingerprint": "e" * 128, "provider": "OTHER", "executed_amount_minor": 999, "currency": "USD", "payment_destination_reference": "other-destination"}
        execution_fact = fact(command, **{field: values[field]})
    with pytest.raises(FinancialExecutionRuntimeOrchestratorError, match="CORRELATION"):
        run_runtime(command, execution_fact=execution_fact)


def test_missing_derivation_result_rejects() -> None:
    with pytest.raises(FinancialExecutionRuntimeOrchestratorError, match="NEUTRAL_FACT_DERIVATION_RESULT_REQUIRED"):
        run_runtime(ap_command(), derive_result=None if False else object())


def test_missing_canonical_command_propagates() -> None:
    command = ap_command()
    with patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.derive_financial_execution_fact", return_value=FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.CREATED, fact(command))), patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.FinancialExecutionCommandRegistry.get", side_effect=RuntimeError("missing")):
        with pytest.raises(RuntimeError, match="missing"):
            orchestrate_terminal_execution_fact_and_projection("tenant-ap", "attempt-runtime", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), fact_collection=Mock(), ap_truth_collection=Mock(), platform_truth_collection=Mock(), execution_time_evidence=Mock(), session=active_session())


def test_child_failure_propagates_without_conversion() -> None:
    command = ap_command()
    with pytest.raises(RuntimeError, match="AP_CHILD_FAILURE"):
        run_runtime(command, ap_projection_side_effect=RuntimeError("AP_CHILD_FAILURE"))


def test_platform_child_failure_propagates_without_conversion() -> None:
    command = platform_command()
    with pytest.raises(RuntimeError, match="PLATFORM_CHILD_FAILURE"):
        run_runtime(command, platform_projection_side_effect=RuntimeError("PLATFORM_CHILD_FAILURE"))


@pytest.mark.parametrize("family", ["UNKNOWN", "", "LEGACY"])
def test_unsupported_family_rejects_without_default(family: str) -> None:
    command = platform_command()
    execution_fact = fact(command)
    with patch.object(FinancialExecutionCommand, "source_authority_kind", new_callable=PropertyMock, return_value=family), patch.object(FinancialExecutionCommand, "fingerprint", new_callable=PropertyMock, return_value=execution_fact.execution_command_fingerprint):  # type: ignore[name-defined]
        with pytest.raises(FinancialExecutionRuntimeOrchestratorError):
            run_runtime(command, execution_fact=execution_fact)


def test_execution_time_evidence_is_forwarded_by_identity() -> None:
    command = ap_command()
    evidence = Mock()
    with patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.derive_financial_execution_fact", return_value=FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.IDEMPOTENT_REPLAY, fact(command)) ) as derive_call, patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.FinancialExecutionCommandRegistry.get", return_value=command), patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.project_financial_execution_fact_to_accounts_payable", return_value=build_ap_truth(command, fact(command))):
        orchestrate_terminal_execution_fact_and_projection("tenant-ap", "attempt-runtime", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), fact_collection=Mock(), ap_truth_collection=Mock(), platform_truth_collection=Mock(), execution_time_evidence=evidence, session=active_session())
    assert derive_call.call_count == 1
    assert derive_call.call_args.kwargs["execution_time_evidence"] is evidence


def test_caller_collections_are_forwarded_without_substitution() -> None:
    command = ap_command()
    execution_fact = fact(command)
    command_collection, attempt_collection, observation_collection = Mock(), Mock(), Mock()
    fact_collection, ap_truth_collection, platform_truth_collection = Mock(), Mock(), Mock()
    with patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.derive_financial_execution_fact", return_value=FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.IDEMPOTENT_REPLAY, execution_fact)) as derive_call, patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.FinancialExecutionCommandRegistry.get", return_value=command), patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.project_financial_execution_fact_to_accounts_payable", return_value=build_ap_truth(command, execution_fact)) as projection:
        orchestrate_terminal_execution_fact_and_projection("tenant-ap", "attempt-runtime", command_collection=command_collection, attempt_collection=attempt_collection, observation_collection=observation_collection, fact_collection=fact_collection, ap_truth_collection=ap_truth_collection, platform_truth_collection=platform_truth_collection, execution_time_evidence=Mock(), session=active_session())
    assert derive_call.call_args.kwargs["command_collection"] is command_collection
    assert derive_call.call_args.kwargs["attempt_collection"] is attempt_collection
    assert derive_call.call_args.kwargs["observation_collection"] is observation_collection
    assert derive_call.call_args.kwargs["fact_collection"] is fact_collection
    assert projection.call_args.kwargs["fact_collection"] is fact_collection
    assert projection.call_args.kwargs["command_collection"] is command_collection
    assert projection.call_args.kwargs["truth_collection"] is ap_truth_collection


def test_derivation_result_fact_id_is_the_only_child_identity() -> None:
    command = ap_command()
    execution_fact = fact(command)
    with patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.derive_financial_execution_fact", return_value=FinancialExecutionFactCreateResult(FinancialExecutionFactCreateOutcome.CREATED, execution_fact)), patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.FinancialExecutionCommandRegistry.get", return_value=command), patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.project_financial_execution_fact_to_accounts_payable", return_value=build_ap_truth(command, execution_fact)) as projection:
        orchestrate_terminal_execution_fact_and_projection("tenant-ap", "attempt-runtime", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), fact_collection=Mock(), ap_truth_collection=Mock(), platform_truth_collection=Mock(), execution_time_evidence=Mock(), session=active_session())
    assert projection.call_args.args[:2] == ("tenant-ap", execution_fact.execution_fact_id)


def test_unsupported_family_dispatches_to_no_child() -> None:
    command = platform_command()
    execution_fact = fact(command)
    with patch.object(FinancialExecutionCommand, "source_authority_kind", new_callable=PropertyMock, return_value="UNSUPPORTED"), patch.object(FinancialExecutionCommand, "fingerprint", new_callable=PropertyMock, return_value=execution_fact.execution_command_fingerprint), patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.project_financial_execution_fact_to_accounts_payable") as ap_projection, patch("tools.eos.kennel.orchestration.financial_execution_runtime_orchestrator.bridge_financial_execution_fact_to_platform") as platform_projection:
        with pytest.raises(FinancialExecutionRuntimeOrchestratorError, match="UNSUPPORTED_FINANCIAL_EXECUTION_COMMAND_FAMILY"):
            run_runtime(command, execution_fact=execution_fact)
    ap_projection.assert_not_called()
    platform_projection.assert_not_called()


def test_runtime_does_not_own_child_transaction_lifecycle() -> None:
    source = getsource(orchestrate_terminal_execution_fact_and_projection)
    for forbidden in ("start_session", "start_transaction", "commit_transaction", "abort_transaction", "with_transaction", "retry_transaction"):
        assert forbidden not in source


@pytest.mark.parametrize("forbidden", [
    "FinancialExecutionProviderObservationRegistry", "evaluate_terminalization", "FinancialExecutionTruthDerivation",
    "derive_financial_execution_truth", "FinancialExecutionAttemptRegistry", "provider_transport", "select_provider",
    "reselect_provider", "current_policy", "latest_policy", "AP_R3", "PlatformP4", "PlatformInvoice",
    "ClientInvoice", "CommercialReceivable", "Settlement", "settlement_registry", "mark_paid", "close_receivable",
    "insert_one", "update_one", "runtime_replay_registry", "runtime_durable_identity", "http_route", "BFF",
    "worker_mount", "cron_mount", "legacy_platform_command", "payable_platform_invoice", "customer_id",
])
def test_runtime_source_contains_no_business_or_mount_authority(forbidden: str) -> None:
    assert forbidden not in getsource(orchestrate_terminal_execution_fact_and_projection)


def test_runtime_has_no_durable_state_or_provider_transport() -> None:
    source = getsource(orchestrate_terminal_execution_fact_and_projection)
    assert "Collection" in source
    assert "FinancialExecutionTruthRegistry" not in source
    assert "FinancialExecutionFactRegistry" not in source


def test_reentry_uses_child_replay_without_runtime_second_fact() -> None:
    command = ap_command()
    first = run_runtime(command)
    second = run_runtime(command)
    assert first[1].call_count == 1 and second[1].call_count == 1
    assert first[3].call_count == 1 and second[3].call_count == 1


def test_platform_reentry_remains_platform_family() -> None:
    command = platform_command()
    result, _, _, ap_projection, platform_projection = run_runtime(command)
    assert isinstance(result, SimpleNamespace)
    assert result.execution_truth_id == "command-platform"
    ap_projection.assert_not_called()
    platform_projection.assert_called_once()


def test_return_annotation_is_closed_family_union() -> None:
    annotation = signature(orchestrate_terminal_execution_fact_and_projection).return_annotation
    assert "FinancialExecutionTruth" in str(annotation)
    assert "PlatformBillingFinancialExecutionTruth" in str(annotation)


def test_no_production_caller_is_mounted() -> None:
    from pathlib import Path
    root = Path(__file__).parents[2]
    callers = []
    for path in (root / "tools").rglob("*.py"):
        if path.name in {"financial_execution_runtime_orchestrator.py", "test_financial_execution_runtime_orchestrator.py"}:
            continue
        if "financial_execution_runtime_orchestrator" in path.read_text(encoding="utf-8"):
            callers.append(path)
    assert callers == []


# ARTIFACT: test_financial_execution_runtime_orchestrator.py
# VERSION: v1.0.0-M11-P5-R2E-R2
# AUTHORITY BOUNDARY: direct host-free composition certificate; no production mount or financial authority.
# TENANT POSTURE: all synthetic child calls are tenant-scoped and session-bound.
# FAIL-CLOSED POSTURE: family, lineage, transaction, child-failure, and forbidden-surface propositions reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; execution remains separate from settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
