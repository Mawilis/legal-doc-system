# -*- coding: utf-8 -*-
# pyright: reportArgumentType=false
"""Unit certification for the PayShap ambiguous-outcome reconciliation contract.

VERSION: v1.0.0-KENNEL-PAYSHAP-AMBIGUOUS-OUTCOME-RECONCILIATION-UNIT-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic evidence classification; no provider, persistence, or settlement authority.
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI Engineering)
CHANGELOG: v1.0.0 certifies immutable identity, fail-closed classification, and retry/operator boundaries.
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
"""
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tools.eos.kennel.providers.payshap_contract import PayShapStatus
from tools.eos.kennel.providers.payshap_reconciliation import (
    PayShapObservationSource,
    PayShapProviderObservation,
    PayShapReconciliationContext,
    PayShapReconciliationError,
    PayShapReconciliationOutcome,
    reconcile,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def context() -> PayShapReconciliationContext:
    return PayShapReconciliationContext("tenant", "command", "provider-ref", "destination-ref", "f" * 128, ("evidence-1",), NOW)


def observation(status: PayShapStatus, *, source: PayShapObservationSource = PayShapObservationSource.WEBHOOK_EVIDENCE, reference: str = "provider-ref", tenant: str = "tenant", authenticated: bool = True, evidence: str | None = "evidence-1", timestamp: datetime | None = NOW, command: str | None = "command", amount: int | None = None, currency: str | None = None) -> PayShapProviderObservation:
    return PayShapProviderObservation(source, tenant, command, reference, status, timestamp, NOW, evidence, "a" * 128, authenticated, amount, currency)


def test_context_and_observation_are_immutable_and_safe() -> None:
    value = context()
    with pytest.raises(FrozenInstanceError):
        value.tenant_id = "other"  # type: ignore[misc]
    assert not {"raw_payload", "credential", "invoice", "settlement"}.intersection(value.__dict__)
    assert not {"raw_payload", "credential", "invoice", "settlement"}.intersection(observation(PayShapStatus.PENDING).__dict__)


@pytest.mark.parametrize("field", ["tenant_id", "execution_command_id", "provider_reference", "destination_reference", "request_fingerprint"])
def test_blank_context_identity_rejected(field: str) -> None:
    values = {"tenant_id": "tenant", "execution_command_id": "command", "provider_reference": "provider-ref", "destination_reference": "destination-ref", "request_fingerprint": "fingerprint"}
    values[field] = ""
    with pytest.raises(PayShapReconciliationError):
        PayShapReconciliationContext(**values)


def test_blank_observation_identity_rejected() -> None:
    with pytest.raises(PayShapReconciliationError):
        observation(PayShapStatus.PENDING, tenant="")


def test_no_evidence_is_unknown_and_requires_review() -> None:
    result = reconcile(context(), [])
    assert result.outcome is PayShapReconciliationOutcome.UNKNOWN and not result.may_retry and result.requires_operator_review


@pytest.mark.parametrize("status", [PayShapStatus.REQUESTED, PayShapStatus.INITIATED, PayShapStatus.PENDING, PayShapStatus.ACCEPTED])
def test_non_final_status_remains_pending(status: PayShapStatus) -> None:
    result = reconcile(context(), [observation(status)])
    assert result.outcome is PayShapReconciliationOutcome.STILL_PENDING and not result.may_retry


@pytest.mark.parametrize("status", [PayShapStatus.UNKNOWN])
def test_unknown_status_never_becomes_failure(status: PayShapStatus) -> None:
    result = reconcile(context(), [observation(status)])
    assert result.outcome is PayShapReconciliationOutcome.UNKNOWN and not result.may_retry


def test_timeout_and_connection_reset_are_not_provider_failure() -> None:
    for observations in ([], [observation(PayShapStatus.UNKNOWN)]):
        result = reconcile(context(), observations)
        assert result.outcome is PayShapReconciliationOutcome.UNKNOWN and result.outcome is not PayShapReconciliationOutcome.CONFIRMED_FAILED


def test_initiation_success_does_not_finalize_execution() -> None:
    result = reconcile(context(), [observation(PayShapStatus.ACCEPTED, source=PayShapObservationSource.INITIATION_RESPONSE, evidence=None)])
    assert result.outcome is PayShapReconciliationOutcome.STILL_PENDING


def test_authenticated_failure_is_retryable() -> None:
    result = reconcile(context(), [observation(PayShapStatus.FAILED)])
    assert result.outcome is PayShapReconciliationOutcome.CONFIRMED_FAILED and result.may_retry and not result.requires_operator_review


def test_unauthenticated_failure_remains_unknown() -> None:
    result = reconcile(context(), [observation(PayShapStatus.FAILED, authenticated=False)])
    assert result.outcome is PayShapReconciliationOutcome.UNKNOWN and not result.may_retry


def test_execution_requires_authenticated_evidence_and_provider_timestamp() -> None:
    result = reconcile(context(), [observation(PayShapStatus.EXECUTED)])
    assert result.outcome is PayShapReconciliationOutcome.CONFIRMED_EXECUTED and not result.may_retry
    for kwargs in ({"authenticated": False}, {"timestamp": None}):
        assert reconcile(context(), [observation(PayShapStatus.EXECUTED, **kwargs)]).outcome is PayShapReconciliationOutcome.UNKNOWN
    with pytest.raises(PayShapReconciliationError):
        observation(PayShapStatus.EXECUTED, evidence=None)


def test_conflicting_execution_and_failure_is_conflict() -> None:
    result = reconcile(context(), [observation(PayShapStatus.EXECUTED), observation(PayShapStatus.FAILED)])
    assert result.outcome is PayShapReconciliationOutcome.CONFLICT and result.requires_operator_review and not result.may_retry


@pytest.mark.parametrize("kwargs", [{"reference": "other"}, {"tenant": "other"}, {"command": "other"}])
def test_identity_mismatch_fails_closed(kwargs: dict[str, str]) -> None:
    result = reconcile(context(), [observation(PayShapStatus.EXECUTED, **kwargs)])
    assert result.outcome is PayShapReconciliationOutcome.CONFLICT and result.requires_operator_review


@pytest.mark.parametrize("kwargs", [{"amount": 100}, {"currency": "ZAR"}])
def test_partial_amount_currency_binding_conflicts(kwargs: dict[str, object]) -> None:
    result = reconcile(context(), [observation(PayShapStatus.PENDING, **kwargs)])
    assert result.outcome is PayShapReconciliationOutcome.CONFLICT


def test_complete_amount_currency_binding_is_deterministic() -> None:
    first = reconcile(context(), [observation(PayShapStatus.PENDING, amount=100, currency="ZAR")])
    second = reconcile(context(), [observation(PayShapStatus.PENDING, amount=100, currency="ZAR")])
    assert first == second


def test_retry_and_review_semantics_are_explicit() -> None:
    unknown = reconcile(context(), [observation(PayShapStatus.UNKNOWN)])
    conflict = reconcile(context(), [observation(PayShapStatus.EXECUTED, reference="other")])
    assert not unknown.may_retry and unknown.requires_operator_review
    assert not conflict.may_retry and conflict.requires_operator_review


def test_result_carries_only_evidence_references() -> None:
    result = reconcile(context(), [observation(PayShapStatus.EXECUTED)])
    assert result.evidence_references == ("evidence-1",)
    assert "SETTLED" not in {member.value for member in PayShapReconciliationOutcome}


# ARTIFACT: test_payshap_reconciliation.py
# VERSION: v1.0.0-KENNEL-PAYSHAP-AMBIGUOUS-OUTCOME-RECONCILIATION-UNIT-CERT
# AUTHORITY BOUNDARY: deterministic provider-evidence classification only; no HTTP, persistence, execution, or settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
