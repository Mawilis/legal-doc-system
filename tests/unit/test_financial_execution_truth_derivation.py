# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
"""TITLE: Financial Execution Truth Derivation Unit Certificate
VERSION: v1.1.0-M11-P5-R2D-R0-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS.
EPITOME: Certify exact attempt-to-command lineage before authenticated truth derivation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_financial_execution_truth_derivation.py
COLLABORATION / OWNERSHIP: Kennel EOS execution-truth certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v1.1.0-M11-P5-R2D-R0-R1 certifies tenant, command ID, command fingerprint, provider, destination, AP, and Platform lineage controls.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic external evidence only; no provider secrets.
TENANT BOUNDARY: Attempt, command, observation, and truth fixtures are tenant-scoped.
AUTHORITY BOUNDARY: Authenticated observation and canonical command facts only; no caller final truth.
FINANCIAL AUTHORITY BOUNDARY: No settlement, paid state, or receivable closure.
TRANSACTION BOUNDARY: Caller-owned active-session mocks; no Mongo or I/O.
FAIL-CLOSED DECLARATION: Divergent attempt projections and unsupported Platform subjects reject.
"""
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from typing import Any

import pytest

from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.financial_execution_command import (
    AccountsPayableCommandSource,
    FinancialExecutionCommand,
    PlatformBillingCommandSource,
)
from tools.eos.kennel.domain.financial_execution_execution_time_evidence import (
    ExecutionTimeAuthorityKind,
    FinancialExecutionTimeEvidence,
)
from tools.eos.kennel.domain.financial_execution_lifecycle import (
    FinancialExecutionAttempt,
    FinancialExecutionAttemptState,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
)
from tools.eos.kennel.domain.financial_execution_terminalization import (
    FinancialExecutionTerminalizationDecision,
    TerminalizationDecision,
)
from tools.eos.kennel.orchestration.financial_execution_truth_derivation import (
    FinancialExecutionTruthDerivationError,
    derive_financial_execution_fact,
    derive_financial_execution_truth,
)
from tools.eos.kennel.domain.financial_execution import FinancialExecutionFact

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


def platform_command() -> FinancialExecutionCommand:
    return FinancialExecutionCommand(
        tenant_id="tenant-platform",
        execution_command_id="command-platform",
        idempotency_key="idem-platform",
        amount_minor=2000,
        currency="ZAR",
        payment_destination_reference="destination-platform",
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


def attempt(command: FinancialExecutionCommand, **changes: object) -> FinancialExecutionAttempt:
    values: dict[str, Any] = dict(
        execution_attempt_id="attempt-1",
        tenant_id=command.tenant_id,
        execution_command_id=command.execution_command_id,
        provider_name=command.provider_name,
        payment_destination_reference=command.payment_destination_reference,
        request_fingerprint=command.fingerprint,
        created_at=NOW,
    )
    values.update(changes)
    return FinancialExecutionAttempt(**values)


def observation(tenant: str, attempt_id: str, provider: str) -> FinancialExecutionProviderObservation:
    return FinancialExecutionProviderObservation(
        "observation-1",
        tenant,
        attempt_id,
        provider,
        ObservationStatus.EXECUTED,
        NOW,
        provider_execution_reference="provider-execution",
        provider_evidence_reference="provider-evidence",
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
    )


def time_evidence(tenant: str, attempt_id: str, provider: str) -> FinancialExecutionTimeEvidence:
    return FinancialExecutionTimeEvidence(
        tenant,
        attempt_id,
        provider,
        "provider-execution",
        "provider-evidence",
        NOW,
        ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
        EvidenceStrength.AUTHENTICATED,
    )


def eligible() -> FinancialExecutionTerminalizationDecision:
    return FinancialExecutionTerminalizationDecision(
        TerminalizationDecision.ELIGIBLE_EXECUTED,
        FinancialExecutionStatus.EXECUTED,
        NOW,
        ("provider-evidence",),
        "explicit execution time",
    )


def derive(command: FinancialExecutionCommand, value: FinancialExecutionAttempt | None = None):
    value = value or attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    obs = observation(value.tenant_id, value.execution_attempt_id, value.provider_name)
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command) as command_read,
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=(obs,)),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.evaluate_terminalization", return_value=eligible()),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionTruthRegistry.create", return_value=Mock()) as create,
    ):
        result = derive_financial_execution_truth("tenant-ap", value.execution_attempt_id, command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=time_evidence(value.tenant_id, value.execution_attempt_id, value.provider_name), session=Mock(in_transaction=True))
    return result, command_read, create


def test_exact_attempt_and_command_reads_are_canonical() -> None:
    result, command_read, create = derive(ap_command())
    assert command_read.call_args.args[:2] == ("tenant-ap", "command-ap")
    assert create.call_args.args[0].execution_command_fingerprint == ap_command().fingerprint
    assert result is not None


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "provider_name", "payment_destination_reference"])
def test_projected_attempt_field_mismatch_rejects(field: str) -> None:
    command = ap_command()
    changed = {"tenant_id": "wrong-tenant", "execution_command_id": "wrong-command", "provider_name": "ZAPPER", "payment_destination_reference": "wrong-destination"}[field]
    with pytest.raises(FinancialExecutionTruthDerivationError, match="LINEAGE"):
        derive(command, attempt(command, **{field: changed}))


def test_attempt_fingerprint_mismatch_rejects() -> None:
    command = ap_command()
    with pytest.raises(FinancialExecutionTruthDerivationError, match="LINEAGE"):
        derive(command, attempt(command, request_fingerprint="f" * 128))


def test_missing_attempt_fingerprint_rejects() -> None:
    command = ap_command()
    with pytest.raises(FinancialExecutionTruthDerivationError, match="LINEAGE"):
        derive(command, attempt(command, request_fingerprint=None))


def test_canonical_command_fingerprint_is_retained_in_ap_truth() -> None:
    command = ap_command()
    _, _, create = derive(command)
    assert create.call_args.args[0].execution_command_fingerprint == command.fingerprint
    assert create.call_args.args[0].payable_id == getattr(command.source_authority, "payable_id", None)


def test_platform_lineage_is_validated_without_payable_access() -> None:
    command = platform_command()
    value = attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    with pytest.raises(FinancialExecutionTruthDerivationError, match="PLATFORM_TRUTH_SUBJECT_UNSUPPORTED"):
        derive(command, value)


def test_platform_fingerprint_mismatch_rejects_before_subject_gate() -> None:
    command = platform_command()
    value = attempt(command, request_fingerprint="f" * 128)
    with pytest.raises(FinancialExecutionTruthDerivationError, match="LINEAGE"):
        derive(command, value)


def test_noneligible_terminalization_rejects() -> None:
    command = ap_command()
    value = attempt(command)
    with patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=()), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.evaluate_terminalization", return_value=Mock(decision=TerminalizationDecision.NOT_ELIGIBLE)):
        with pytest.raises(FinancialExecutionTruthDerivationError, match="TERMINALIZATION"):
            derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=time_evidence("tenant-ap", "attempt-1", "PAYSHAP"), session=Mock(in_transaction=True))


def test_active_transaction_is_required() -> None:
    with pytest.raises(FinancialExecutionTruthDerivationError, match="ACTIVE_SESSION"):
        derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=Mock(), session=Mock(in_transaction=False))


@pytest.mark.parametrize("status", ["NOT_ELIGIBLE", "RECONCILIATION_REQUIRED", "CONFLICT"])
def test_nonexecuted_or_invalid_observation_outcomes_never_create_truth(status: str) -> None:
    command = ap_command()
    with patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=attempt(command)), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=()), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.evaluate_terminalization", return_value=Mock(decision=TerminalizationDecision[status])):
        with pytest.raises(FinancialExecutionTruthDerivationError):
            derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=Mock(), session=Mock(in_transaction=True))


def test_attempt_read_is_tenant_scoped_and_session_bound() -> None:
    command = ap_command()
    value = attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    session = Mock(in_transaction=True)
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value) as attempt_read,
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=()),
    ):
        with pytest.raises(FinancialExecutionTruthDerivationError):
            derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=Mock(), session=session)
    assert attempt_read.call_args.args[:2] == ("tenant-ap", "attempt-1")
    assert attempt_read.call_args.kwargs["session"] is session


def test_command_read_uses_attempt_command_id_and_same_session() -> None:
    command = ap_command()
    value = attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    session = Mock(in_transaction=True)
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command) as command_read,
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=()),
    ):
        with pytest.raises(FinancialExecutionTruthDerivationError):
            derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=Mock(), session=session)
    assert command_read.call_args.args[:2] == ("tenant-ap", "command-ap")
    assert command_read.call_args.kwargs["session"] is session


def test_observation_read_is_attempt_scoped_and_session_bound() -> None:
    command = ap_command()
    value = attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    session = Mock(in_transaction=True)
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=()) as observation_read,
    ):
        with pytest.raises(FinancialExecutionTruthDerivationError):
            derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=Mock(), session=session)
    assert observation_read.call_args.args[:2] == ("tenant-ap", "attempt-1")
    assert observation_read.call_args.kwargs["session"] is session


def test_lineage_rejection_precedes_truth_persistence() -> None:
    command = ap_command()
    value = attempt(command, request_fingerprint="f" * 128)
    create = Mock()
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionTruthRegistry.create", create),
    ):
        with pytest.raises(FinancialExecutionTruthDerivationError, match="LINEAGE"):
            derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=Mock(), session=Mock(in_transaction=True))
    create.assert_not_called()


def test_provider_observation_mismatch_is_rejected_after_lineage() -> None:
    command = ap_command()
    value = attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    bad_observation = observation(value.tenant_id, value.execution_attempt_id, "ZAPPER")
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=(bad_observation,)),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.evaluate_terminalization", return_value=eligible()),
    ):
        with pytest.raises(FinancialExecutionTruthDerivationError, match="PROVIDER_CORRELATION"):
            derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=time_evidence(value.tenant_id, value.execution_attempt_id, value.provider_name), session=Mock(in_transaction=True))


def test_ap_truth_projection_has_no_settlement_or_client_invoice_fields() -> None:
    command = ap_command()
    result, _, create = derive(command)
    truth = create.call_args.args[0]
    assert result is not None
    assert not {"settled", "paid", "settlement_id", "client_invoice_id"}.intersection(truth.to_dict())


def test_truth_domain_does_not_claim_command_or_attempt_identity() -> None:
    _, _, create = derive(ap_command())
    persisted = create.call_args.args[0].to_dict()
    assert "execution_command_id" not in persisted
    assert "execution_attempt_id" not in persisted


def test_truth_persistence_receives_the_caller_owned_session() -> None:
    command = ap_command()
    session = Mock(in_transaction=True)
    value = attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    obs = observation(value.tenant_id, value.execution_attempt_id, value.provider_name)
    create = Mock(return_value=Mock())
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=(obs,)),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.evaluate_terminalization", return_value=eligible()),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionTruthRegistry.create", create),
    ):
        derive_financial_execution_truth("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), truth_collection=Mock(), execution_time_evidence=time_evidence(value.tenant_id, value.execution_attempt_id, value.provider_name), session=session)
    assert create.call_args.kwargs["session"] is session


def derive_fact(command: FinancialExecutionCommand, value: FinancialExecutionAttempt | None = None):
    value = value or attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW)
    obs = observation(value.tenant_id, value.execution_attempt_id, value.provider_name)
    result = Mock(return_value=Mock())
    with (
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=(obs,)),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.evaluate_terminalization", return_value=eligible()),
        patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionFactRegistry.create", result),
    ):
        output = derive_financial_execution_fact(value.tenant_id, value.execution_attempt_id, command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), fact_collection=Mock(), execution_time_evidence=time_evidence(value.tenant_id, value.execution_attempt_id, value.provider_name), session=Mock(in_transaction=True))
    return output, result


def test_neutral_fact_derivation_is_additive():
    output, create = derive_fact(ap_command())
    assert output is not None
    assert isinstance(create.call_args.args[0], FinancialExecutionFact)


def test_neutral_fact_derivation_retains_command_and_attempt_lineage():
    _, create = derive_fact(ap_command())
    value = create.call_args.args[0]
    assert (value.execution_command_id, value.execution_attempt_id) == ("command-ap", "attempt-1")


def test_neutral_fact_has_no_subject_fields():
    _, create = derive_fact(ap_command())
    assert not {"payable_id", "platform_invoice_id"}.intersection(create.call_args.args[0].to_dict())


def test_neutral_fact_uses_canonical_command_fingerprint():
    command = ap_command(); _, create = derive_fact(command)
    assert create.call_args.args[0].execution_command_fingerprint == command.fingerprint


def test_neutral_fact_uses_caller_session():
    command = ap_command(); value = attempt(command, state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW); obs = observation(value.tenant_id, value.execution_attempt_id, value.provider_name); session = Mock(in_transaction=True); create = Mock(return_value=Mock())
    with patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionAttemptRegistry.get", return_value=value), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionCommandRegistry.get", return_value=command), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionProviderObservationRegistry.list_for_attempt", return_value=(obs,)), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.evaluate_terminalization", return_value=eligible()), patch("tools.eos.kennel.orchestration.financial_execution_truth_derivation.FinancialExecutionFactRegistry.create", create):
        derive_financial_execution_fact("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), fact_collection=Mock(), execution_time_evidence=time_evidence("tenant-ap", "attempt-1", "PAYSHAP"), session=session)
    assert create.call_args.kwargs["session"] is session


def test_neutral_fact_platform_family_is_allowed():
    output, create = derive_fact(platform_command(), attempt(platform_command(), state=FinancialExecutionAttemptState.CONFIRMED_EXECUTED, confirmed_at=NOW, execution_attempt_id="attempt-platform"))
    assert output is not None and create.call_args.args[0].tenant_id == "tenant-platform"


def test_neutral_fact_requires_active_transaction():
    with pytest.raises(FinancialExecutionTruthDerivationError, match="ACTIVE_SESSION"):
        derive_financial_execution_fact("tenant-ap", "attempt-1", command_collection=Mock(), attempt_collection=Mock(), observation_collection=Mock(), fact_collection=Mock(), execution_time_evidence=Mock(), session=Mock(in_transaction=False))


def test_neutral_fact_never_reads_payable_projection():
    _, create = derive_fact(ap_command())
    assert "payable_id" not in create.call_args.args[0].to_dict()


# ARTIFACT: test_financial_execution_truth_derivation.py
# VERSION: v1.1.0-M11-P5-R2D-R0-R1
# AUTHORITY BOUNDARY: lineage and observation certificate only; no settlement authority.
# TENANT POSTURE: synthetic tenant-scoped fixtures and caller-owned session mocks.
# FAIL-CLOSED POSTURE: divergent projected fields and unsupported Platform subjects reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
