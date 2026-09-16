"""WILSY AI C1B provider-neutral reasoning orchestrator.

TITLE: WILSY AI Authenticated Reasoning Runtime Orchestrator
VERSION: v1.0.0-C1B-R11
AUTHORITY: Wilsy OS Core Governance
EPITOME: Compose one durable usage admission with one server-owned model
         execution, then persist bounded invocation and usage evidence without
         allowing provider failures to become synthetic consumption.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/intelligence/wilsy_ai_reasoning_orchestrator.py
COLLABORATION / OWNERSHIP: C1B owns claim/execute/finalize composition;
                            admission, C1A invocation, and P5A observation
                            registries remain canonical persistence authorities.
CERTIFICATION / UPDATE DATE: 2026-09-16
CHANGELOG: v1.0.0-C1B-R11 establishes caller-transaction claim/finalization,
           one-use execution permits, bounded provider failure accounting,
           exact replay, and tenant/entitlement/provider binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Prompt and provider response remain transient;
                             exception details are never durable.
TENANT BOUNDARY: Every admission, invocation, observation, and replay lookup
                 is scoped to the supplied tenant identity.
AUTHORITY BOUNDARY: Model reasoning and usage evidence only; no legal-service,
                    execution, return, invoice, payment, or settlement truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: State, identity, result, metric, replay, and session
                         drift reject deterministically.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Final, NoReturn
import re

from tools.eos.intelligence.domain.ai_model_execution import (
    MODEL_EXECUTION_MODULE_ID,
    ModelExecutionInput,
    ModelExecutionOutcome,
    ModelInvocationEvidence,
    ModelProviderResult,
    ModelExecutionError,
    sanitize_provider_error,
)
from tools.eos.intelligence.domain.ai_model_provider_binding import AIModelProviderBindingError, ServerOwnedModelProviderBinding
from tools.eos.intelligence.registry.ai_model_invocation_registry import (
    AIModelInvocationRegistry,
)
from tools.eos.saas.domain.wilsy_ai_usage_admission import (
    WilsyAIUsageAdmission,
    WilsyAIUsageAdmissionState,
)
from tools.eos.saas.billing.wilsy_ai_usage_admission_registry import (
    WilsyAIUsageAdmissionRegistry,
    WilsyAIUsageAdmissionNotFoundError,
)
from tools.eos.saas.domain.wilsy_ai_usage_observation import WilsyAIUsageObservation
from tools.eos.saas.billing.wilsy_ai_usage_observation_registry import (
    WilsyAIUsageObservationRegistry,
    WilsyAIUsageObservationNotFoundError,
)


VERSION: Final[str] = "v1.0.0-C1B-R11"
_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_FORBIDDEN_TENANTS = frozenset({"default", "global", "global_root", "root", "master", "*"})


class WilsyAIReasoningOrchestratorError(RuntimeError):
    """Stable fail-closed C1B error carrying no provider material."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class WilsyAIReasoningInputError(WilsyAIReasoningOrchestratorError):
    """Invalid scope, permit, result, or derived evidence input."""


class WilsyAIReasoningReplayError(WilsyAIReasoningOrchestratorError):
    """A pre-provider or durable replay would diverge or re-execute work."""


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable error while retaining technical context only as cause."""
    error = WilsyAIReasoningInputError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one opaque bounded identity."""
    if not isinstance(value, str) or _IDENTITY.fullmatch(value) is None:
        _fail(f"C1B_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    """Require explicit non-pseudo tenant scope."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("C1B_TENANT_INVALID")
    return tenant


def _when(value: object) -> datetime:
    """Normalize an aware timestamp to UTC."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        _fail("C1B_OCCURRED_AT_INVALID")
    return value.astimezone(timezone.utc)


def _caller_transaction(session: object) -> object:
    """Require an active caller transaction without taking its lifecycle."""
    if session is None:
        raise WilsyAIReasoningInputError("C1B_CALLER_SESSION_REQUIRED")
    marker = getattr(session, "in_transaction", False)
    try:
        active = marker() if callable(marker) else marker
    except Exception as error:
        raise WilsyAIReasoningInputError("C1B_CALLER_TRANSACTION_REQUIRED") from error
    if active is not True:
        raise WilsyAIReasoningInputError("C1B_CALLER_TRANSACTION_REQUIRED")
    return session


@dataclass(slots=True)
class WilsyAIReasoningExecutionPermit:
    """Transient one-use claim bound to admission and server model identity."""

    tenant_id: str
    principal_id: str
    admission_id: str
    invocation_id: str
    correlation_id: str
    entitlement_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    provider_id: str
    model_id: str
    request_fingerprint: str
    claimed_admission_fingerprint: str
    claimed_at: datetime
    request: ModelExecutionInput
    _token: object = field(repr=False, compare=False, default=None)
    _consumed: bool = field(repr=False, compare=False, default=False)


@dataclass(frozen=True, slots=True)
class WilsyAIReasoningProviderAttempt:
    """Transient result plus bounded C1A evidence; no persistence occurs here."""

    permit: WilsyAIReasoningExecutionPermit
    result: ModelProviderResult
    evidence: ModelInvocationEvidence


@dataclass(frozen=True, slots=True)
class WilsyAIReasoningFinalization:
    """Durable finalization outcome returned without exposing authority expansion."""

    admission: WilsyAIUsageAdmission
    invocation_evidence: ModelInvocationEvidence
    usage_observation: WilsyAIUsageObservation | None
    response_text: str | None
    replay: bool


class WilsyAIReasoningOrchestrator:
    """Coordinate C1B claim, out-of-transaction provider execution, and finalize."""

    __slots__ = ("_admissions", "_invocations", "_observations", "_binding", "_token", "_clock")

    def __init__(
        self,
        *,
        admission_registry: WilsyAIUsageAdmissionRegistry,
        invocation_registry: AIModelInvocationRegistry,
        observation_registry: WilsyAIUsageObservationRegistry,
        binding: ServerOwnedModelProviderBinding,
        clock: Any | None = None,
    ) -> None:
        """Bind canonical registries and one server-owned provider resolver."""
        if not isinstance(binding, ServerOwnedModelProviderBinding):
            raise WilsyAIReasoningInputError("C1B_PROVIDER_BINDING_RESOLVER_INVALID")
        self._admissions = admission_registry
        self._invocations = invocation_registry
        self._observations = observation_registry
        self._binding = binding
        self._token = object()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> datetime:
        """Return one aware UTC clock value."""
        return _when(self._clock())

    def claim(
        self,
        *,
        tenant_id: str,
        principal_id: str,
        admission_id: str,
        invocation_id: str,
        correlation_id: str,
        prompt: str,
        system_policy: str,
        session: object,
        occurred_at: datetime,
        entitlement_id: str,
        tool_invocation_evidence_references: tuple[str, ...] = (),
    ) -> WilsyAIReasoningExecutionPermit:
        """Claim one RESERVED admission inside the caller-owned transaction.

        Provider/model identity and request units are never caller-selected.
        The caller-proven legal attempt/instruction/document/deputy chain is
        represented by the supplied correlation_id; no caller may inject a
        second provenance source or provider identity.
        """
        tenant = _tenant(tenant_id)
        tx = _caller_transaction(session)
        for name, value in (("principal_id", principal_id), ("admission_id", admission_id), ("invocation_id", invocation_id), ("correlation_id", correlation_id), ("entitlement_id", entitlement_id)):
            _identity(name, value)
        occurred = _when(occurred_at)
        try:
            admission = self._admissions.get(tenant_id=tenant, admission_id=admission_id, session=tx)
        except WilsyAIUsageAdmissionNotFoundError as error:
            # A foreign tenant and an absent identity are intentionally
            # indistinguishable at this boundary.
            raise WilsyAIReasoningReplayError("C1B_TENANT_MISMATCH") from error
        if admission.tenant_id != tenant:
            raise WilsyAIReasoningReplayError("C1B_TENANT_MISMATCH")
        if admission.entitlement_id != entitlement_id:
            raise WilsyAIReasoningReplayError("C1B_ENTITLEMENT_MISMATCH")
        if admission.module_id != MODEL_EXECUTION_MODULE_ID:
            raise WilsyAIReasoningReplayError("C1B_MODULE_MISMATCH")
        if admission.state is not WilsyAIUsageAdmissionState.RESERVED:
            raise WilsyAIReasoningReplayError("C1B_REEXECUTION_FORBIDDEN")
        try:
            server_binding = self._binding.resolve()
        except AIModelProviderBindingError as error:
            _fail(error.args[0] if error.args else "C1B_PROVIDER_BINDING_INVALID", error)
        refs = tuple(tool_invocation_evidence_references)
        request = ModelExecutionInput(
            tenant_id=tenant,
            principal_id=principal_id,
            invocation_id=invocation_id,
            correlation_id=correlation_id,
            entitlement_id=entitlement_id,
            provider_id=server_binding.provider_id,
            model_id=server_binding.model_id,
            prompt=prompt,
            system_policy=system_policy,
            request_units=admission.reserved_request_units,
            tool_invocation_evidence_references=refs,
        )
        claimed = self._admissions.transition(
            tenant_id=tenant,
            admission_id=admission_id,
            target_state=WilsyAIUsageAdmissionState.CLAIMED,
            evidence_reference=invocation_id,
            occurred_at=occurred,
            session=tx,
        )
        if claimed.state is not WilsyAIUsageAdmissionState.CLAIMED or claimed.fingerprint == admission.fingerprint:
            raise WilsyAIReasoningReplayError("C1B_CLAIM_TRANSITION_INVALID")
        return WilsyAIReasoningExecutionPermit(
            tenant_id=tenant,
            principal_id=principal_id,
            admission_id=admission_id,
            invocation_id=invocation_id,
            correlation_id=correlation_id,
            entitlement_id=entitlement_id,
            entitlement_revision=admission.entitlement_revision,
            entitlement_fingerprint=admission.entitlement_fingerprint,
            provider_id=server_binding.provider_id,
            model_id=server_binding.model_id,
            request_fingerprint=request.request_fingerprint,
            claimed_admission_fingerprint=claimed.fingerprint,
            claimed_at=occurred,
            request=request,
            _token=self._token,
        )

    def execute(self, permit: WilsyAIReasoningExecutionPermit, *, completed_at: datetime | None = None) -> WilsyAIReasoningProviderAttempt:
        """Execute exactly once outside Mongo transaction scope."""
        if not isinstance(permit, WilsyAIReasoningExecutionPermit) or permit._token is not self._token:
            raise WilsyAIReasoningInputError("C1B_EXECUTION_PERMIT_INVALID")
        if permit._consumed:
            raise WilsyAIReasoningReplayError("C1B_PROVIDER_REEXECUTION_FORBIDDEN")
        permit._consumed = True
        finished = _when(completed_at if completed_at is not None else self._now())
        binding = self._binding.resolve()
        try:
            raw = binding.provider.execute(permit.request)
            if not isinstance(raw, ModelProviderResult):
                raise TypeError("provider result contract")
            if raw.provider_id != binding.provider_id or raw.model_id != binding.model_id:
                raise WilsyAIReasoningInputError("C1B_PROVIDER_RESULT_IDENTITY_DRIFT")
            result = raw
        except Exception as error:
            if isinstance(error, WilsyAIReasoningInputError):
                raise
            outcome = sanitize_provider_error(error)
            if isinstance(error, ModelExecutionError):
                outcome = ModelExecutionOutcome.INTERNAL_CONTRACT_VIOLATION
            result = ModelProviderResult(
                provider_id=binding.provider_id,
                model_id=binding.model_id,
                outcome=outcome,
                error_classification=outcome.value,
            )
        try:
            evidence = ModelInvocationEvidence.from_execution(
                permit.request,
                result,
                created_at=permit.claimed_at,
                completed_at=finished,
            )
        except Exception as error:
            _fail("C1B_INVOCATION_EVIDENCE_INVALID", error)
        return WilsyAIReasoningProviderAttempt(permit=permit, result=result, evidence=evidence)

    def finalize(
        self,
        attempt: WilsyAIReasoningProviderAttempt,
        *,
        session: object,
        occurred_at: datetime,
    ) -> WilsyAIReasoningFinalization:
        """Persist exact C1A/P5A evidence and close or reconcile the admission."""
        tx = _caller_transaction(session)
        if not isinstance(attempt, WilsyAIReasoningProviderAttempt):
            raise WilsyAIReasoningInputError("C1B_FINALIZATION_INPUT_INVALID")
        permit = attempt.permit
        evidence = attempt.evidence
        if (
            permit._token is not self._token
            or evidence.tenant_id != permit.tenant_id
            or evidence.invocation_id != permit.invocation_id
            or evidence.entitlement_id != permit.entitlement_id
            or evidence.provider_id != permit.provider_id
            or evidence.model_id != permit.model_id
            or evidence.request_fingerprint != permit.request_fingerprint
            or evidence.request_units != permit.request.request_units
            or evidence.outcome is not attempt.result.outcome
            or evidence.response_fingerprint != attempt.result.response_fingerprint
        ):
            raise WilsyAIReasoningInputError("C1B_FINALIZATION_PERMIT_INVALID")
        occurred = _when(occurred_at)
        if occurred < evidence.completed_at:
            raise WilsyAIReasoningInputError("C1B_FINALIZATION_CHRONOLOGY_INVALID")
        current = self._admissions.get(tenant_id=permit.tenant_id, admission_id=permit.admission_id, session=tx)
        if current.state in {WilsyAIUsageAdmissionState.COMPLETED, WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED}:
            persisted = self._invocations.get(tenant_id=permit.tenant_id, invocation_id=permit.invocation_id, session=tx)
            if persisted.to_dict() != evidence.to_dict():
                raise WilsyAIReasoningReplayError("C1B_INVOCATION_DIVERGENT_REPLAY")
            observation: WilsyAIUsageObservation | None = None
            metrics_available = attempt.result.input_tokens is not None and attempt.result.output_tokens is not None
            if attempt.result.outcome is ModelExecutionOutcome.SUCCESS and metrics_available:
                observation = self._observations.get(tenant_id=permit.tenant_id, usage_observation_id=f"usage-{permit.invocation_id}", session=tx)
                if (
                    observation.source_evidence_reference != persisted.invocation_id
                    or observation.source_evidence_fingerprint != persisted.fingerprint
                    or observation.request_units != persisted.request_units
                    or observation.input_tokens != persisted.input_tokens
                    or observation.output_tokens != persisted.output_tokens
                ):
                    raise WilsyAIReasoningReplayError("C1B_USAGE_DIVERGENT_REPLAY")
            elif attempt.result.outcome is ModelExecutionOutcome.SUCCESS:
                observation = None
            else:
                try:
                    self._observations.get(tenant_id=permit.tenant_id, usage_observation_id=f"usage-{permit.invocation_id}", session=tx)
                except WilsyAIUsageObservationNotFoundError:
                    observation = None
                else:
                    raise WilsyAIReasoningReplayError("C1B_FAILURE_USAGE_PRESENT")
            expected_state = WilsyAIUsageAdmissionState.COMPLETED if attempt.result.outcome is ModelExecutionOutcome.SUCCESS and metrics_available else WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED
            if current.state is not expected_state or current.evidence_reference != permit.invocation_id:
                raise WilsyAIReasoningReplayError("C1B_ADMISSION_REPLAY_DIVERGENCE")
            return WilsyAIReasoningFinalization(current, persisted, observation, attempt.result.response_text if attempt.result.outcome is ModelExecutionOutcome.SUCCESS else None, True)
        if current.state is not WilsyAIUsageAdmissionState.CLAIMED or current.tenant_id != permit.tenant_id or current.fingerprint != permit.claimed_admission_fingerprint:
            raise WilsyAIReasoningReplayError("C1B_FINALIZATION_STATE_INVALID")
        persisted = self._invocations.create_or_replay(attempt.evidence, session=tx)
        observation = None
        if attempt.result.outcome is ModelExecutionOutcome.SUCCESS:
            if attempt.result.input_tokens is None or attempt.result.output_tokens is None:
                final = self._admissions.transition(tenant_id=permit.tenant_id, admission_id=permit.admission_id, target_state=WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED, evidence_reference=permit.invocation_id, occurred_at=occurred, session=tx)
                return WilsyAIReasoningFinalization(final, persisted, None, None, False)
            input_tokens = attempt.result.input_tokens
            output_tokens = attempt.result.output_tokens
            observation = WilsyAIUsageObservation(
                tenant_id=permit.tenant_id,
                usage_observation_id=f"usage-{permit.invocation_id}",
                entitlement_id=permit.entitlement_id,
                entitlement_revision=permit.entitlement_revision,
                entitlement_fingerprint=permit.entitlement_fingerprint,
                module_id=MODEL_EXECUTION_MODULE_ID,
                request_units=attempt.evidence.request_units,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                automation_actions=0,
                occurred_at=occurred,
                source_evidence_reference=attempt.evidence.invocation_id,
                source_evidence_fingerprint=attempt.evidence.fingerprint,
            )
            observation = self._observations.create_or_replay(observation, idempotency_key=f"reasoning:{permit.invocation_id}", session=tx)
            final = self._admissions.transition(tenant_id=permit.tenant_id, admission_id=permit.admission_id, target_state=WilsyAIUsageAdmissionState.COMPLETED, evidence_reference=permit.invocation_id, occurred_at=occurred, session=tx)
            return WilsyAIReasoningFinalization(final, persisted, observation, attempt.result.response_text, False)
        final = self._admissions.transition(tenant_id=permit.tenant_id, admission_id=permit.admission_id, target_state=WilsyAIUsageAdmissionState.RECONCILIATION_REQUIRED, evidence_reference=permit.invocation_id, occurred_at=occurred, session=tx)
        return WilsyAIReasoningFinalization(final, persisted, None, None, False)


__all__ = ["VERSION", "WilsyAIReasoningOrchestratorError", "WilsyAIReasoningInputError", "WilsyAIReasoningReplayError", "WilsyAIReasoningExecutionPermit", "WilsyAIReasoningProviderAttempt", "WilsyAIReasoningFinalization", "WilsyAIReasoningOrchestrator"]

# ARTIFACT: wilsy_ai_reasoning_orchestrator.py
# VERSION: v1.0.0-C1B-R11
# AUTHORITY BOUNDARY: provider-neutral reasoning evidence and usage admission
# TENANT POSTURE: every durable lookup/write is explicitly tenant-scoped
# FAIL-CLOSED POSTURE: one-use permits, strict bindings, exact replay, no synthetic usage
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
