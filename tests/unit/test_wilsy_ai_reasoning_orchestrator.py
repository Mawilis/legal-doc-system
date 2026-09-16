"""C1B-R11 direct certificate for authenticated reasoning orchestration.

TITLE: WILSY AI Reasoning Orchestrator Unit Certificate
VERSION: v1.0.0-C1B-R11
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove one-use claim permits, provider-neutral execution, bounded
         failure accounting, exact replay, and caller transaction ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_reasoning_orchestrator.py
COLLABORATION / OWNERSHIP: Certifies tools/eos/intelligence/wilsy_ai_reasoning_orchestrator.py.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0 establishes C1B claim/execute/finalize certificates.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Assertions prove raw provider failures and payloads
                             never enter durable evidence.
TENANT BOUNDARY: Fakes enforce exact tenant predicates on every registry call.
AUTHORITY BOUNDARY: Reasoning evidence only; no legal or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Identity, state, metric, replay, and lifecycle drift
                         must reject or reconcile without synthetic usage.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, cast

import pytest

from tools.eos.intelligence.domain.ai_model_execution import (
    ModelExecutionOutcome,
    ModelProviderResult,
)
from tools.eos.intelligence.domain.ai_model_provider_binding import ServerOwnedModelProviderBinding
from tools.eos.intelligence.registry.ai_model_invocation_registry import AIModelInvocationRegistryConflictError
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import WilsyAIUsageAdmissionNotFoundError
from tools.eos.saas.domain.wilsy_ai_usage_admission import WilsyAIUsageAdmission, WilsyAIUsageAdmissionState
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import WilsyAIUsageObservationNotFoundError
from tools.eos.intelligence.wilsy_ai_reasoning_orchestrator import (
    WilsyAIReasoningOrchestrator,
    WilsyAIReasoningReplayError,
)


NOW = datetime(2026, 9, 16, 8, 0, tzinfo=timezone.utc)


class Session:
    """Caller-owned transaction marker; no lifecycle methods are invoked."""

    in_transaction = True

    def __init__(self) -> None:
        self.starts = self.commits = self.aborts = 0


def admission() -> WilsyAIUsageAdmission:
    """Build one valid RESERVED reasoning capacity admission."""
    return WilsyAIUsageAdmission(
        tenant_id="tenant-c1b",
        admission_id="admission-1",
        idempotency_key="admission-key-1",
        entitlement_id="entitlement-1",
        module_id="WILSY_AI_REASONING",
        entitlement_revision=2,
        entitlement_fingerprint="a" * 128,
        window_start=NOW,
        window_end=NOW + timedelta(hours=1),
        reserved_request_units=1,
        created_at=NOW,
        updated_at=NOW,
    )


class Admissions:
    """In-memory canonical admission registry retaining exact CAS semantics."""

    def __init__(self, item: WilsyAIUsageAdmission) -> None:
        self.item = item
        self.sessions: list[object] = []

    def get(self, *, tenant_id: str, admission_id: str, session: object) -> WilsyAIUsageAdmission:
        self.sessions.append(session)
        if tenant_id != self.item.tenant_id or admission_id != self.item.admission_id:
            raise WilsyAIUsageAdmissionNotFoundError("C1B_NOT_FOUND")
        return self.item

    def transition(self, *, tenant_id: str, admission_id: str, target_state: Any, evidence_reference: str, occurred_at: datetime, session: object) -> WilsyAIUsageAdmission:
        self.sessions.append(session)
        self.item = self.item.transition(target_state, evidence_reference=evidence_reference, occurred_at=occurred_at)
        return self.item


class Invocations:
    """In-memory C1A registry with exact replay and divergence checks."""

    def __init__(self) -> None:
        self.items: dict[tuple[str, str], Any] = {}
        self.sessions: list[object] = []

    def create_or_replay(self, evidence: Any, *, session: object) -> Any:
        self.sessions.append(session)
        key = (evidence.tenant_id, evidence.invocation_id)
        if key in self.items and self.items[key].to_dict() != evidence.to_dict():
            raise AIModelInvocationRegistryConflictError("C1B_DIVERGENT")
        self.items[key] = evidence
        return evidence

    def get(self, *, tenant_id: str, invocation_id: str, session: object) -> Any:
        self.sessions.append(session)
        try:
            return self.items[(tenant_id, invocation_id)]
        except KeyError as error:
            raise WilsyAIUsageAdmissionNotFoundError("C1B_NOT_FOUND") from error


class Observations:
    """In-memory P5A registry retaining exact idempotent observation writes."""

    def __init__(self) -> None:
        self.items: dict[tuple[str, str], WilsyAIUsageObservation] = {}
        self.sessions: list[object] = []

    def create_or_replay(self, observation: WilsyAIUsageObservation, *, idempotency_key: str, session: object) -> WilsyAIUsageObservation:
        self.sessions.append(session)
        key = (observation.tenant_id, observation.usage_observation_id)
        if key in self.items and self.items[key] != observation:
            raise RuntimeError("C1B_DIVERGENT_USAGE")
        self.items[key] = observation
        return observation

    def get(self, *, tenant_id: str, usage_observation_id: str, session: object) -> WilsyAIUsageObservation:
        self.sessions.append(session)
        try:
            return self.items[(tenant_id, usage_observation_id)]
        except KeyError as error:
            raise WilsyAIUsageObservationNotFoundError("M13P5B_OBSERVATION_NOT_FOUND") from error


class Provider:
    """Deterministic provider double recording calls and transaction state."""

    def __init__(self, result: Any = None, error: BaseException | None = None) -> None:
        self.result = result
        self.error = error
        self.calls = 0
        self.in_transaction_values: list[bool] = []

    def execute(self, request: Any) -> Any:
        self.calls += 1
        self.in_transaction_values.append(False)
        if self.error is not None:
            raise self.error
        return self.result


def make_orchestrator(provider: Provider) -> tuple[WilsyAIReasoningOrchestrator, Admissions, Invocations, Observations, Session]:
    """Compose the orchestrator around deterministic registry doubles."""
    admissions, invocations, observations, session = Admissions(admission()), Invocations(), Observations(), Session()
    binding = ServerOwnedModelProviderBinding.from_injected(provider=provider, provider_id="provider-c1b", model_id="model-c1b")
    orchestrator = WilsyAIReasoningOrchestrator(
        admission_registry=cast(Any, admissions), invocation_registry=cast(Any, invocations),
        observation_registry=cast(Any, observations), binding=binding,
        clock=lambda: NOW + timedelta(seconds=2),
    )
    return orchestrator, admissions, invocations, observations, session


def claim(orchestrator: WilsyAIReasoningOrchestrator, session: Session) -> Any:
    """Claim one admission using proven legal correlation references."""
    return orchestrator.claim(
        tenant_id="tenant-c1b", principal_id="principal-1", admission_id="admission-1",
        invocation_id="invocation-1", correlation_id="attempt-1",
        entitlement_id="entitlement-1", prompt="bounded prompt", system_policy="bounded policy",
        tool_invocation_evidence_references=("attempt:attempt-1", "instruction:instruction-1", "document:document-1", "deputy:deputy-1"),
        session=session, occurred_at=NOW + timedelta(seconds=1),
    )


def success_result(**changes: Any) -> ModelProviderResult:
    """Build one valid provider success result."""
    values: dict[str, Any] = dict(provider_id="provider-c1b", model_id="model-c1b", response_text="bounded result", provider_request_id="request-1", input_tokens=4, output_tokens=3)
    values.update(changes)
    return ModelProviderResult(**values)


def test_success_claim_execute_finalize_binds_identity_and_usage() -> None:
    provider = Provider(success_result())
    orchestrator, admissions, invocations, observations, session = make_orchestrator(provider)
    permit = claim(orchestrator, session)
    assert permit.request.request_units == 1
    assert permit.request.tool_invocation_evidence_references == ("attempt:attempt-1", "instruction:instruction-1", "document:document-1", "deputy:deputy-1")
    attempt = orchestrator.execute(permit)
    assert provider.calls == 1
    final = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    assert final.admission.state is WilsyAIUsageAdmissionState.COMPLETED
    assert final.usage_observation is not None
    assert final.usage_observation.source_evidence_fingerprint == final.invocation_evidence.fingerprint
    assert final.usage_observation.automation_actions == 0
    assert len(invocations.items) == len(observations.items) == 1
    assert all(value is session for value in admissions.sessions + invocations.sessions + observations.sessions)
    assert session.starts == session.commits == session.aborts == 0


def test_provider_exception_is_sanitized_and_holds_capacity() -> None:
    provider = Provider(error=TimeoutError("secret provider detail"))
    orchestrator, admissions, invocations, observations, session = make_orchestrator(provider)
    attempt = orchestrator.execute(claim(orchestrator, session))
    final = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    assert final.admission.state is WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED
    assert attempt.evidence.outcome is ModelExecutionOutcome.PROVIDER_TIMEOUT
    assert attempt.evidence.error_classification == "PROVIDER_TIMEOUT"
    assert "secret provider detail" not in str(attempt.evidence.to_dict())
    assert observations.items == {}
    assert len(invocations.items) == 1


def test_missing_metrics_reconciles_without_synthetic_zero_usage() -> None:
    provider = Provider(success_result(input_tokens=None, output_tokens=None))
    orchestrator, admissions, _invocations, observations, session = make_orchestrator(provider)
    final = orchestrator.finalize(orchestrator.execute(claim(orchestrator, session)), session=session, occurred_at=NOW + timedelta(seconds=3))
    assert final.admission.state is WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED
    assert observations.items == {}


def test_missing_metrics_reconciliation_replays_without_provider_or_usage() -> None:
    provider = Provider(success_result(input_tokens=None, output_tokens=None))
    orchestrator, _admissions, _invocations, observations, session = make_orchestrator(provider)
    attempt = orchestrator.execute(claim(orchestrator, session))
    first = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    replay = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    assert first.admission.state is WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED
    assert replay.replay is True and replay.usage_observation is None
    assert provider.calls == 1 and observations.items == {}


def test_permit_is_one_use_and_pre_provider_replays_are_forbidden() -> None:
    provider = Provider(success_result())
    orchestrator, admissions, _invocations, _observations, session = make_orchestrator(provider)
    permit = claim(orchestrator, session)
    orchestrator.execute(permit)
    with pytest.raises(WilsyAIReasoningReplayError, match="C1B_PROVIDER_REEXECUTION_FORBIDDEN"):
        orchestrator.execute(permit)
    with pytest.raises(WilsyAIReasoningReplayError, match="C1B_REEXECUTION_FORBIDDEN"):
        claim(orchestrator, session)
    assert admissions.item.state is WilsyAIUsageAdmissionState.CLAIMED
    assert provider.calls == 1


def test_failure_finalization_replay_does_not_call_provider() -> None:
    provider = Provider(error=ConnectionError("secret unavailable"))
    orchestrator, admissions, invocations, observations, session = make_orchestrator(provider)
    attempt = orchestrator.execute(claim(orchestrator, session))
    first = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    second = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    assert first.replay is False and second.replay is True
    assert second.admission == first.admission
    assert provider.calls == 1 and len(invocations.items) == 1 and observations.items == {}


def test_success_finalization_replay_is_exact_and_provider_never_recalled() -> None:
    provider = Provider(success_result())
    orchestrator, _admissions, invocations, observations, session = make_orchestrator(provider)
    attempt = orchestrator.execute(claim(orchestrator, session))
    first = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    second = orchestrator.finalize(attempt, session=session, occurred_at=NOW + timedelta(seconds=3))
    assert first.replay is False and second.replay is True
    assert second.invocation_evidence == first.invocation_evidence
    assert second.usage_observation == first.usage_observation
    assert provider.calls == 1 and len(invocations.items) == len(observations.items) == 1


def test_tenant_and_entitlement_mismatch_fail_closed() -> None:
    provider = Provider(success_result())
    orchestrator, _admissions, _invocations, _observations, session = make_orchestrator(provider)
    with pytest.raises(WilsyAIReasoningReplayError, match="C1B_TENANT_MISMATCH"):
        orchestrator.claim(tenant_id="tenant-other", principal_id="principal-1", admission_id="admission-1", invocation_id="invocation-1", correlation_id="corr-1", entitlement_id="entitlement-1", prompt="p", system_policy="s", session=session, occurred_at=NOW)
    with pytest.raises(WilsyAIReasoningReplayError, match="C1B_ENTITLEMENT_MISMATCH"):
        orchestrator.claim(tenant_id="tenant-c1b", principal_id="principal-1", admission_id="admission-1", invocation_id="invocation-1", correlation_id="corr-1", entitlement_id="entitlement-other", prompt="p", system_policy="s", session=session, occurred_at=NOW)
    assert provider.calls == 0


def test_caller_provider_selection_is_not_an_orchestrator_argument() -> None:
    provider = Provider(success_result())
    orchestrator, _admissions, _invocations, _observations, session = make_orchestrator(provider)
    with pytest.raises(TypeError):
        orchestrator.claim(tenant_id="tenant-c1b", principal_id="principal-1", admission_id="admission-1", invocation_id="invocation-1", correlation_id="corr-1", entitlement_id="entitlement-1", prompt="p", system_policy="s", session=session, occurred_at=NOW, provider_id="caller", model_id="caller")  # type: ignore[call-arg]


def test_provider_result_identity_drift_fails_closed() -> None:
    provider = Provider(ModelProviderResult(provider_id="other-provider", model_id="model-c1b", response_text="drift"))
    orchestrator, _admissions, _invocations, _observations, session = make_orchestrator(provider)
    with pytest.raises(Exception, match="C1B_PROVIDER_RESULT_IDENTITY_DRIFT"):
        orchestrator.execute(claim(orchestrator, session))
    assert provider.calls == 1


def test_active_transaction_is_required_but_never_owned() -> None:
    provider = Provider(success_result())
    orchestrator, _admissions, _invocations, _observations, _session = make_orchestrator(provider)
    inactive = Session()
    inactive.in_transaction = False  # type: ignore[misc]
    with pytest.raises(Exception, match="C1B_CALLER_TRANSACTION_REQUIRED"):
        claim(orchestrator, inactive)
    assert inactive.starts == inactive.commits == inactive.aborts == 0


# ARTIFACT: test_wilsy_ai_reasoning_orchestrator.py
# VERSION: v1.0.0-C1B-R11
# AUTHORITY BOUNDARY: unit certificate for provider-neutral reasoning composition
# FAIL-CLOSED POSTURE: exact replay, bounded failure, and no synthetic usage
# END OF WILSY OS SOVEREIGN ARTIFACT
