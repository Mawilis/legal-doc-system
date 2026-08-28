"""Unit certification for the provider-neutral Kennel EOS execution orchestrator.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-ORCHESTRATOR-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance
ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
SCOPE: deterministic orchestration contract; no Mongo, network, provider, or settlement.
"""
from datetime import datetime, timezone
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
import pytest

from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus, FinancialExecutionTruth
from tools.eos.kennel.orchestration.financial_execution_orchestrator import (
    FinancialExecutionCommand, FinancialExecutionCommandInvalidError,
    FinancialExecutionOrchestrator, FinancialExecutionOrchestratorError,
    FinancialExecutionPreInvocationIdempotencyConflictError,
    FinancialExecutionProviderContractError, FinancialExecutionProviderResult,
)
from tools.eos.kennel.registry.financial_execution_registry import FinancialExecutionCreateOutcome, FinancialExecutionIdempotencyKeyReuseError


def command(**changes):
    values = dict(tenant_id="tenant-a", payable_id="payable-a", release_authorization_id="release-a", execution_command_id="execution-a", idempotency_key="key-a", amount_minor=100, currency="ZAR", payment_destination_reference="destination-ref-a")
    values.update(changes)
    return FinancialExecutionCommand(**values)


def truth_for(c, status=FinancialExecutionStatus.EXECUTED):
    result = FinancialExecutionProviderResult("GENERIC", "provider-ref", status, "evidence-ref", datetime(2026, 1, 1, tzinfo=timezone.utc) if status is FinancialExecutionStatus.EXECUTED else None)
    fp = c.fingerprint
    return FinancialExecutionTruth(c.execution_command_id, c.tenant_id, c.payable_id, c.release_authorization_id, result.provider, result.provider_execution_reference, status, c.amount_minor, c.currency, result.executed_at, c.payment_destination_reference, result.provider_evidence_reference, fp, "b" * 128, datetime(2026, 1, 2, tzinfo=timezone.utc))


class SpyProvider:
    provider_name = "GENERIC"
    def __init__(self, result=None, error=None): self.result, self.error, self.invocation_count, self.commands = result, error, 0, []
    def execute(self, cmd):
        self.invocation_count += 1; self.commands.append(cmd)
        if self.error: raise self.error
        return self.result


class SpyRegistry:
    def __init__(self, existing=None, create_result=None, create_exception=None): self.existing, self.create_result, self.create_exception, self.read_count, self.create_count = existing, create_result, create_exception, 0, 0
    def get_by_idempotency_key(self, *args, **kwargs): self.read_count += 1; return self.existing
    def create(self, truth, *args, **kwargs):
        self.create_count += 1
        if self.create_exception: raise self.create_exception
        return self.create_result or type("Create", (), {"outcome": FinancialExecutionCreateOutcome.CREATED, "execution_truth": truth})()


def test_command_immutable_and_valid():
    c = command();
    with pytest.raises((AttributeError, TypeError)): c.amount_minor = 1


@pytest.mark.parametrize("field", ["tenant_id", "payable_id", "release_authorization_id", "execution_command_id", "idempotency_key", "payment_destination_reference"])
def test_required_identifiers_reject_blank(field):
    with pytest.raises(FinancialExecutionCommandInvalidError): command(**{field: " "})


@pytest.mark.parametrize("value", [0, -1, True, 1.0, "100", None])
def test_amount_rejects_invalid(value):
    with pytest.raises(FinancialExecutionCommandInvalidError): command(amount_minor=value)


@pytest.mark.parametrize("value", ["", "ZA", "ZARR", "123", "   "])
def test_currency_rejects_malformed(value):
    with pytest.raises(FinancialExecutionCommandInvalidError): command(currency=value)


def test_fingerprint_is_deterministic_and_changes_for_material_fields():
    base = command(); assert base.fingerprint == command().fingerprint; assert len(base.fingerprint) == 128; assert all(ch in "0123456789abcdef" for ch in base.fingerprint)
    for field, value in (("payable_id", "other"), ("release_authorization_id", "other"), ("execution_command_id", "other"), ("amount_minor", 101), ("currency", "USD"), ("payment_destination_reference", "other")):
        assert command(**{field: value}).fingerprint != base.fingerprint


def test_secret_patterns_rejected_and_opaque_reference_allowed():
    assert command(payment_destination_reference="destination-ref-a")
    for value in ("bank_account=1", "card_number=1", "access_token=secret"):
        with pytest.raises(FinancialExecutionCommandInvalidError): command(payment_destination_reference=value)


def test_provider_result_immutable_and_status_contract():
    result = FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.EXECUTED, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc))
    with pytest.raises((AttributeError, TypeError)): result.provider = "x"
    assert FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.EXECUTED, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc)).execution_status is FinancialExecutionStatus.EXECUTED
    assert FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.FAILED, "evidence", None).executed_at is None
    for status in (FinancialExecutionStatus.SUBMITTED, FinancialExecutionStatus.ACCEPTED, "PAID", "SETTLED", "CLEARED", "COMPLETED", "executed"):
        with pytest.raises(FinancialExecutionProviderContractError): FinancialExecutionProviderResult("GENERIC", "ref", status, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc))
    with pytest.raises(FinancialExecutionProviderContractError): FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.EXECUTED, "evidence", None)
    with pytest.raises(FinancialExecutionProviderContractError): FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.EXECUTED, "evidence", datetime(2026, 1, 1))
    with pytest.raises(FinancialExecutionProviderContractError): FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.FAILED, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc))


def test_provider_required_fields_and_consistency():
    c = command(requested_provider="GENERIC"); provider = SpyProvider(FinancialExecutionProviderResult("OTHER", "ref", FinancialExecutionStatus.EXECUTED, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc))); registry = SpyRegistry();
    with pytest.raises(FinancialExecutionProviderContractError): FinancialExecutionOrchestrator(provider, registry).authorize(c)
    assert provider.invocation_count == 1 and registry.create_count == 0
    for field in ("provider", "provider_execution_reference", "provider_evidence_reference"):
        with pytest.raises(FinancialExecutionProviderContractError): FinancialExecutionProviderResult(" " if field == "provider" else "GENERIC", " " if field == "provider_execution_reference" else "ref", FinancialExecutionStatus.EXECUTED, " " if field == "provider_evidence_reference" else "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc))


def test_exact_replay_suppresses_provider():
    c = command(); existing = truth_for(c); provider = SpyProvider(); registry = SpyRegistry(existing); result = FinancialExecutionOrchestrator(provider, registry).authorize(c)
    assert registry.read_count == 1 and registry.create_count == 0 and provider.invocation_count == 0 and not result.provider_invoked and result.registry_outcome is FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY and result.execution_truth == existing


def test_divergent_replay_fails_before_provider():
    c = command(); existing = truth_for(command(amount_minor=99)); provider = SpyProvider(); registry = SpyRegistry(existing)
    with pytest.raises(FinancialExecutionPreInvocationIdempotencyConflictError): FinancialExecutionOrchestrator(provider, registry).authorize(c)
    assert provider.invocation_count == 0 and registry.create_count == 0


def test_fresh_execution_maps_truth_and_persists_once():
    c = command(); provider = SpyProvider(FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.EXECUTED, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc))); registry = SpyRegistry(); result = FinancialExecutionOrchestrator(provider, registry).authorize(c)
    assert provider.invocation_count == 1 and registry.read_count == 1 and registry.create_count == 1 and result.provider_invoked and result.registry_outcome is FinancialExecutionCreateOutcome.CREATED
    assert isinstance(result.execution_truth, FinancialExecutionTruth) and result.execution_truth.execution_status is FinancialExecutionStatus.EXECUTED and result.execution_truth.payable_id == c.payable_id


def test_failed_execution_maps_truth_without_timestamp():
    c = command(); provider = SpyProvider(FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.FAILED, "evidence", None)); registry = SpyRegistry(); result = FinancialExecutionOrchestrator(provider, registry).authorize(c)
    assert result.execution_truth.execution_status is FinancialExecutionStatus.FAILED and result.execution_truth.executed_at is None and provider.invocation_count == 1


def test_provider_and_registry_errors_propagate():
    c = command(); provider = SpyProvider(error=RuntimeError("provider"));
    with pytest.raises(RuntimeError): FinancialExecutionOrchestrator(provider, SpyRegistry()).authorize(c)
    registry = SpyRegistry(create_exception=FinancialExecutionIdempotencyKeyReuseError("reuse")); provider = SpyProvider(FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.EXECUTED, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc)))
    with pytest.raises(FinancialExecutionIdempotencyKeyReuseError): FinancialExecutionOrchestrator(provider, registry).authorize(c)


def test_active_transaction_blocks_fresh_provider_call():
    class Session: in_transaction = True
    c = command(); provider = SpyProvider(FinancialExecutionProviderResult("GENERIC", "ref", FinancialExecutionStatus.EXECUTED, "evidence", datetime(2026, 1, 1, tzinfo=timezone.utc))); registry = SpyRegistry()
    with pytest.raises(FinancialExecutionOrchestratorError): FinancialExecutionOrchestrator(provider, registry).authorize(c, session=Session())
    assert provider.invocation_count == 0 and registry.create_count == 0


# ARTIFACT: test_vendor_bill_release_orchestrator.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-ORCHESTRATOR-UNIT-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
